#!/usr/bin/env python3
"""
Quick daily inbox sweep — checks only page 0 for TODAY's replies.

Lightweight alternative to monitor_inbox.py for daily cron runs.
Faster because it skips pagination and only fetches message history
for leads whose last_reply_time is today. For the full deep-scan
(including legacy campaigns on deep pages), use monitor_inbox.py.

Usage:
    python3 quick_check.py

Output:
    Prints NEW positive replies with full body for draft generation.
    Silently adds all new message IDs to state.
    Returns exit code 1 if actionables found.

Requires:
    Instantly_API_KEY from /opt/data/.env
    Instantly CLI at /opt/data/home/.local/bin/Instantly
    State file at /opt/data/scripts/auto_reply_state.json
"""

import json, os, re, subprocess, sys
from datetime import datetime, timezone


def load_state(path='/opt/data/scripts/auto_reply_state.json'):
    with open(path) as f:
        return json.load(f)


def save_state(state, path='/opt/data/scripts/auto_reply_state.json'):
    with open(path, 'w') as f:
        json.dump(state, f, indent=2)


def get_api_key():
    with open('/opt/data/.env') as f:
        for line in f:
            if line.startswith('Instantly_API_KEY='):
                return line.split('=', 1)[1].strip()
    raise RuntimeError("Instantly_API_KEY not found")


def Instantly_cli(*args, timeout=30):
    env = {
        **os.environ,
        'Instantly_API_KEY': get_api_key(),
        'PATH': '/opt/data/home/.local/bin:' + os.environ.get('PATH', ''),
    }
    cmd = ['Instantly'] + list(args)
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"CLI failed: {r.stderr[:200]}")
    return json.loads(r.stdout)


def normalize(msg_id):
    return (msg_id or '').strip('<>')


def classify(body_text):
    """Lightweight classifier for reporting."""
    lower = body_text.lower().strip()

    # Hostile
    if lower in ('stop', 'stop.', 'unsubscribe'):
        return 'hostile'
    hostile = ['remove me', 'take me off', 'do not contact', 'stop emailing', 'fuck off']
    if any(p in lower for p in hostile):
        return 'hostile'

    # Unsub
    if any(p in lower for p in ('unsubscribe', 'opt out', 'opt-out', 'do not email')):
        return 'unsubscribe'

    # Positive
    one_word = {'sure', 'ok', 'okay', 'yep', 'yes', 'absolutely', 'definitely', 'indeed', 'interested'}
    first = lower.split()[0] if lower.split() else ''
    if first.strip('.,!?') in one_word and len(lower) < 60:
        return 'positive_interested'

    pos = ['happy to chat', 'would love to learn', 'tell me more',
           'send me more info', 'send me info', 'send me some info',
           'can you send', 'meeting link', 'suggest times', 'piqued',
           'set up a call', 'schedule a call', 'hop on a call',
           'worth.*conversation', 'open to hearing',
           'learn more about', 'be happy to', 'i\'d be happy',
           'looking forward to', 'available for a', 'sounds interesting']
    if any(re.search(p, lower) for p in pos):
        return 'positive_interested'

    # Negative
    neg = ['not interested', 'no thanks', 'no thx', 'not a fit', 'not looking']
    if any(p in lower for p in neg):
        return 'negative_notfit'

    # OOO
    ooo = ['out of office', 'out of the office', 'on vacation', 'on leave',
           'away from', 'will respond when', 'limited access']
    if any(p in lower for p in ooo):
        return 'ooo'

    return 'neutral'


def main():
    state = load_state()
    replied = {normalize(m) for m in state.get('replied_message_ids', [])}

    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    # Step 1: Pull inbox page 0
    inbox = Instantly_cli('inbox', 'replies', '--format', 'json')
    entries = inbox.get('data', inbox)
    if isinstance(entries, dict) and 'data' in entries:
        entries = entries['data']

    # Step 2: Filter to today's leads
    today_entries = [e for e in entries if (e.get('last_reply_time', '') or '').startswith(today)]
    print(f"Inbox page 0: {len(entries)} total, {len(today_entries)} from today")

    new_replies = []

    for entry in today_entries:
        cid = entry['email_campaign_id']
        lid = entry['email_lead_id']
        email = entry.get('lead_email', '')
        name = entry.get('lead_first_name', '')

        try:
            history = Instantly_cli('leads', 'messages',
                                    '--campaign-id', str(cid),
                                    '--lead-id', str(lid),
                                    '--format', 'json')
            msgs = history.get('history', [])
        except Exception as e:
            print(f"  FAIL: {name} <{email}>: {e}")
            continue

        # Find REPLY messages
        for msg in msgs:
            if msg.get('type') != 'REPLY':
                continue
            from_field = str(msg.get('from', '')).lower()
            if 'mailer-daemon' in from_field:
                continue

            mid = msg.get('message_id', '')
            if not mid:
                continue
            if normalize(mid) in replied:
                continue

            # New reply
            body_html = msg.get('email_body', '')
            body_text = re.sub(r'<[^>]+>', ' ', body_html)
            body_text = re.sub(r'\s+', ' ', body_text).strip()

            # Skip our own domain replies (operator replies showing as REPLY type)
            our_domains = ('speakeragent.ai', 'progressdeskks.info', 'successcrestco.info',
                          'growthmapar.info', 'horizonedgenv.info', 'advancesteptn.info',
                          'successliftia.info', 'prosperaxisma.info', 'strategyvistaaz.info',
                          'visiondesknj.info', 'meetaiintegraterz.com', 'useaiintegraterz.com',
                          'joinaiintegraterz.com')
            if any(d in from_field for d in our_domains):
                print(f"  SKIP (our domain): {name} <{email}> from={from_field}")
                state['replied_message_ids'].append(mid)
                replied.add(normalize(mid))
                continue

            cl = classify(body_text)
            new_replies.append({
                'email': email, 'name': name, 'campaign_id': cid,
                'msg_id': mid, 'body': body_text[:500],
                'time': msg.get('time', ''), 'classification': cl,
                'from': from_field, 'lead_id': lid,
            })

            print(f"  NEW [{cl}] {name} <{email}> | {msg.get('time', '')[:19]}")
            print(f"    {body_text[:150]}")

            state['replied_message_ids'].append(mid)
            replied.add(normalize(mid))

        # Also scan for operator reply message IDs (from our domains that appear as REPLY)
        for msg in msgs:
            if msg.get('type') != 'REPLY':
                continue
            from_field = str(msg.get('from', '')).lower()
            our_domains = ('speakeragent.ai', 'progressdeskks.info', 'successcrestco.info',
                          'growthmapar.info', 'horizonedgenv.info', 'advancesteptn.info',
                          'successliftia.info', 'prosperaxisma.info', 'strategyvistaaz.info',
                          'visiondesknj.info', 'meetaiintegraterz.com', 'useaiintegraterz.com',
                          'joinaiintegraterz.com')
            if any(d in from_field for d in our_domains):
                mid = msg.get('message_id', '')
                if mid and normalize(mid) not in replied:
                    state['replied_message_ids'].append(mid)
                    replied.add(normalize(mid))

    save_state(state)

    # Summary
    if not new_replies:
        print("NO new customer replies today.")

    actionables = [r for r in new_replies if r['classification'] in
                   ('positive_interested', 'positive_soft')]
    non_actionables = [r for r in new_replies if r not in actionables]

    if non_actionables:
        print(f"\nNon-actionable ({len(non_actionables)}):")
        for r in non_actionables:
            print(f"  [{r['classification']}] {r['name']} <{r['email']}>")

    if actionables:
        print(f"\n*** {len(actionables)} ACTIONABLE ***")
        for r in actionables:
            print(f"  [{r['classification']}] {r['name']} <{r['email']}>")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())