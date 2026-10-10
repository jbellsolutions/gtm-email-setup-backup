#!/usr/bin/env python3
"""
Instantly inbox monitor - cron companion script.

Fetches message history for every lead in the inbox, compares RFC 5322
message IDs against the daemon state file, and reports NEW (unprocessed)
replies. Auto-responders (OOO, ticket systems) are added to state but
classified as non-actionable. Genuine human replies are output for the
caller to draft responses.

Usage:
    python3 monitor_inbox.py [--full] [--state /path/to/auto_reply_state.json]

    --full: paginate through ALL inbox pages (for deep sweeps). Default: page 0 only.

Output:
    Prints classification summary to stdout.
    Prints JSON of any new POSITIVE replies to stderr for pipeline consumption.
    Updates state file in-place.

Requires:
    Instantly_API_KEY from /opt/data/.env
    Instantly CLI at /opt/data/home/.local/bin/Instantly
"""

import json
import os
import re
import subprocess
import sys
import time


def load_state(state_path):
    with open(state_path) as f:
        return json.load(f)


def save_state(state, state_path):
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)


def get_api_key():
    with open('/opt/data/.env') as f:
        for line in f:
            if line.startswith('Instantly_API_KEY='):
                return line.split('=', 1)[1].strip()
    raise RuntimeError("Instantly_API_KEY not found in /opt/data/.env")


def Instantly_cli(*args, timeout=30):
    """Run Instantly CLI, return parsed JSON."""
    env = {
        **os.environ,
        'Instantly_API_KEY': get_api_key(),
        'PATH': '/opt/data/home/.local/bin:' + os.environ.get('PATH', ''),
    }
    cmd = ['Instantly'] + list(args)
    result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"Instantly {' '.join(args[:2])} failed: {result.stderr[:200]}")
    return json.loads(result.stdout)


def fetch_inbox(full=False):
    """Pull inbox entries. Page 0 only by default (for --once cron).
    Set full=True to paginate through all pages (for monitoring sweeps)."""
    all_entries = []
    offset = 0
    while True:
        payload = {'offset': offset, 'limit': 20}
        payload_path = f'/tmp/inbox_payload_{offset}.json'
        with open(payload_path, 'w') as f:
            json.dump(payload, f)
        try:
            raw = Instantly_cli('inbox', 'replies', '--from-json', payload_path, '--format', 'json')
        finally:
            try:
                os.remove(payload_path)
            except OSError:
                pass
        data = raw.get('data', raw)
        if isinstance(data, dict) and 'data' in data:
            data = data['data']
        if isinstance(data, list):
            all_entries.extend(data)
        if not data or len(data) < 20 or not full:
            break
        offset += 20
        time.sleep(0.5)
    return all_entries


def fetch_message_history(campaign_id, lead_id):
    """Fetch full message history for a lead."""
    raw = Instantly_cli(
        'leads', 'messages',
        '--campaign-id', str(campaign_id),
        '--lead-id', str(lead_id),
        '--format', 'json',
    )
    history = raw.get('history', raw)
    if isinstance(history, dict):
        history = history.get('history', [])
    return history


def normalize_msg_id(msg_id):
    """Strip angle brackets for comparison."""
    if not msg_id:
        return ''
    return msg_id.strip().strip('<>')


def is_auto_responder(body_clean, from_field=''):
    """Classify a reply as auto-responder (OOO, ticket, auto-reply)."""
    lower = body_clean.lower()

    # OOO indicators
    ooo_patterns = [
        r'out of (the )?office',
        r'out of town',
        r'on vacation',
        r'on leave',
        r'away from.*email',
        r'will respond.*(when|upon|after).*return',
        r'limited.*access.*email',
        r'out of pocket',
    ]
    for pat in ooo_patterns:
        if re.search(pat, lower):
            return True

    # Ticket system auto-responders
    ticket_patterns = [
        r'ticket has been created',
        r'thank you for contacting',
        r'we have received your',
        r'support representative',
        r'auto.?reply',
        r'auto.?response',
        r'automated response',
    ]
    for pat in ticket_patterns:
        if re.search(pat, lower):
            return True

    # Generic auto-responders (no personal touch)
    if ('thank you so much for your email' in lower and 'influencer' in lower):
        return True
    if 'thank you for your email' in lower and len(body_clean) < 300:
        return True

    return False


def classify_reply(body_clean):
    """Classify a human reply (not auto-responder)."""
    lower = body_clean.lower()

    # Hostile
    hostile_patterns = ['remove me', 'take me off', 'do not contact', 'stop emailing', 'fuck off']
    for pat in hostile_patterns:
        if pat in lower:
            return 'hostile'

    # Bare "Stop" (1-word hostile from Outlook for iOS)
    stripped = body_clean.strip()
    if stripped.lower() in ('stop', 'stop.', 'unsubscribe'):
        return 'hostile'

    # Unsubscribe
    unsub_patterns = ['unsubscribe', 'opt out', 'opt-out', 'do not email']
    for pat in unsub_patterns:
        if pat in lower:
            return 'unsubscribe'

    # Positive: one-word agreements
    one_word_positives = {'sure', 'ok', 'okay', 'yep', 'yes', 'absolutely', 'definitely',
                          'indeed', 'interested', 'interested.', 'please', 'yes please'}
    first_word = stripped.split()[0] if stripped else ''
    if first_word.strip('.,!?').lower() in one_word_positives and len(stripped) < 60:
        return 'positive_interested'

    # Positive: engagement signals
    positive_signals = [
        'happy to chat', 'would love to learn', 'tell me more',
        'send me more info', 'send me information', 'send more info',
        'send me some info', 'send me info', 'can you send', 'meeting link',
        'book an appointment', 'suggest times', 'piqued.*interest',
        'set up a call', 'schedule a call', 'hop on a call',
        'worth.*conversation', 'open to hearing', 'interested in learning',
        'send links', 'send the link', 'would like to know',
    ]
    for pat in positive_signals:
        if re.search(pat, lower):
            return 'positive_interested'

    # Positive: soft interest
    soft_signals = [
        'what do you', 'how does it work', 'how does this work',
        'what is speakeragent', 'more details', 'learn more',
        'sounds interesting', 'sounds good',
    ]
    for pat in soft_signals:
        if re.search(pat, lower):
            return 'positive_soft'

    # Negative
    negative_patterns = [
        'not interested', 'no thanks', 'no thx', 'not a fit',
        'no money', 'not a prospect', 'not at this time',
    ]
    for pat in negative_patterns:
        if re.search(pat, lower):
            return 'negative_notfit'

    # Greeting-only
    greeting_only = stripped.lower() in ('hi', 'hello', 'hey', 'hi there', 'hello there', 'hey there')
    if greeting_only:
        return 'neutral'

    return 'neutral'


def main():
    state_path = '/opt/data/scripts/auto_reply_state.json'
    full_sweep = '--full' in sys.argv
    if '--state' in sys.argv:
        idx = sys.argv.index('--state')
        state_path = sys.argv[idx + 1]

    state = load_state(state_path)
    replied_ids = set(state.get('replied_message_ids', []))
    replied_normalized = {normalize_msg_id(mid) for mid in replied_ids}

    print(f"State file: {len(replied_ids)} replied IDs ({len(replied_normalized)} normalized)")

    # Step 1: Pull inbox
    inbox = fetch_inbox(full=full_sweep)
    print(f"Inbox: {len(inbox)} entries (full_sweep={full_sweep})")

    # Step 2: Collect unique leads (dedup by lead_id within inbox)
    seen_leads = set()
    inbox_entries = []
    for entry in inbox:
        lid = entry.get('email_lead_id')
        if lid and lid not in seen_leads:
            seen_leads.add(lid)
            inbox_entries.append(entry)

    print(f"Unique leads: {len(inbox_entries)}")

    # Step 3: Fetch message history for each lead
    new_replies = []
    checked = 0

    for entry in inbox_entries:
        campaign_id = entry.get('email_campaign_id')
        lead_id = entry.get('email_lead_id')
        lead_name = entry.get('lead_first_name', 'Unknown')
        lead_email = entry.get('lead_email', 'Unknown')

        try:
            history = fetch_message_history(campaign_id, lead_id)
        except Exception as e:
            print(f"  FAIL: {lead_name} <{lead_email}>: {e}")
            continue

        for msg in history:
            if msg.get('type') != 'REPLY':
                continue

            from_field = str(msg.get('from', '')).lower()
            if 'mailer-daemon' in from_field:
                continue
            if 'mail delivery' in str(msg.get('email_body', '')).lower()[:200]:
                continue

            msg_id = msg.get('message_id', '')
            body = msg.get('email_body', '')
            msg_time = msg.get('time', '')

            normalized = normalize_msg_id(msg_id)

            # Skip if already in state
            if normalized in replied_normalized:
                continue

            # New reply!
            body_clean = re.sub(r'<[^>]+>', ' ', body).strip()

            # Count our SENT messages after this reply's time (for our_replies_after check)
            our_replies_after = 0
            for m in history:
                if m.get('type') == 'SENT' and int(m.get('email_seq_number', 0) or 0) > 3:
                    if m.get('time', '') > msg_time:
                        our_replies_after += 1

            classification = classify_reply(body_clean)
            is_auto = is_auto_responder(body_clean, from_field)

            if is_auto:
                classification = 'ooo' if 'office' in body_clean.lower() or 'vacation' in body_clean.lower() or 'beach' in body_clean.lower() else 'auto'

            new_replies.append({
                'lead_id': lead_id,
                'campaign_id': campaign_id,
                'name': lead_name,
                'email': lead_email,
                'message_id': msg_id,
                'body': body,
                'body_clean': body_clean[:300],
                'time': msg_time,
                'classification': classification,
                'is_auto': is_auto,
                'our_replies_after': our_replies_after,
            })

            checked += 1
            print(f"  NEW [{classification}] {lead_name} <{lead_email}> | {msg_time[:19]}")
            print(f"    body: {body_clean[:120]}")

        time.sleep(0.3)  # Rate-limit respect

    print(f"\n=== SUMMARY: {len(new_replies)} new replies ({checked} total new messages) ===")

    # Step 4: Add all new message IDs to state
    for nr in new_replies:
        if nr['message_id'] not in state['replied_message_ids']:
            state['replied_message_ids'].append(nr['message_id'])

    save_state(state, state_path)
    print(f"State updated: {len(state['replied_message_ids'])} total IDs")

    # Step 5: Report actionables
    actionables = [nr for nr in new_replies if nr['classification'] in ('positive_interested', 'positive_soft')]
    non_actionables = [nr for nr in new_replies if nr['classification'] not in ('positive_interested', 'positive_soft')]

    if non_actionables:
        print(f"\nNon-actionable (silently added to state):")
        for nr in non_actionables:
            print(f"  [{nr['classification']}] {nr['name']} <{nr['email']}>")

    if actionables:
        print(f"\n*** ACTION REQUIRED: {len(actionables)} positive replies ***")
        for nr in actionables:
            print(f"  [{nr['classification']}] {nr['name']} <{nr['email']}>")
            print(f"    {nr['body_clean'][:200]}")
        # Output actionables as JSON to stderr for pipeline
        print(json.dumps(actionables, indent=2), file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
