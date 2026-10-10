#!/usr/bin/env python3
"""
Owned Audiences Reply Monitor Pipeline
======================================
Sweeps Instantly inbox pages 0-N for campaign #3617053, pre-filters auto-responders
by email prefix, pulls message history for real leads, classifies replies, and
checks our_replies_after to determine whether a lead still needs a case study reply.

Usage:
  python3 scripts/monitor_pipeline.py [--pages N] [--campaign-id ID]

Output:
  /tmp/monitor_results.json — {positives, negatives, auto_responders, already_handled, ...}

State files read:
  /tmp/owned_audiences_followups.json — known message IDs + lead statuses
  /opt/data/scripts/auto_reply_state.json — hostile/unsub senders (daemon state)

RATE LIMITS: runs ~1 API call per real lead (message history) + 1 per inbox page.
With 41 auto-reply prefixes filtered out of 60 entries, only ~19 API calls for a 3-page sweep.
"""

import json, sys, os, re, subprocess, time, argparse, urllib.request
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CAMPAIGN_ID = 3617053
STATE_PATH = '/tmp/owned_audiences_followups.json'
DAEMON_STATE_PATH = '/opt/data/scripts/auto_reply_state.json'
ENV_PATH = '/opt/data/.env'
Instantly_BIN = '/opt/data/home/.local/bin/Instantly'

AUTO_REPLY_PREFIXES = [
    'support@', 'info@', 'privacy@', 'contact@', 'hello@',
    'admin@', 'help@', 'noreply@', 'no-reply@', 'team@',
    'connect@', 'ask@', 'consult@', 'trt@', 'orders@',
    'staff@', 'frontdesk@', 'notifications@', 'mailer-daemon@',
    'care@', 'press@', 'media@', 'podcast@', 'podcasts@', 'contactus@',
    'compliance@', 'partnerships@', 'moreinfo@', 'concierge@',
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_Instantly_key():
    with open(ENV_PATH) as f:
        for line in f:
            if line.startswith('Instantly_API_KEY='):
                return line.split('=', 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("Instantly_API_KEY not found in .env")


def check_api_health(key, timeout=10):
    """Verify Instantly API is accessible before running the sweep.
    
    Returns (ok, message). If ok=False, the pipeline must abort immediately —
    continuing would produce a false all-clear: zero inbox entries, exit code 0,
    indistinguishable from a genuinely empty inbox. (Jul 2026: plan expiry twice
    produced silent false-negatives because this check didn't exist.)
    """
    url = f"https://server.Instantly/api/v1/campaigns?api_key={key}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
        if isinstance(data, dict) and data.get('message') == 'Plan expired!':
            return False, "PLAN_EXPIRED"
        if isinstance(data, dict) and data.get('ok') is False:
            return False, f"API_ERROR: {data.get('message', 'unknown')}"
        # Any valid JSON response that isn't an error = API is healthy
        return True, "OK"
    except urllib.error.HTTPError as e:
        return False, f"HTTP_{e.code}"
    except Exception as e:
        return False, f"CONNECTION_ERROR: {e}"


def run_Instantly(cmd, timeout=60):
    env = {
        **os.environ,
        'Instantly_API_KEY': Instantly_KEY,
        'PATH': f'{os.path.dirname(Instantly_BIN)}:' + os.environ.get('PATH', ''),
    }
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, env=env)
    return result


def is_auto_reply_email(email):
    if not email:
        return True
    el = email.lower()
    return any(el.startswith(p) for p in AUTO_REPLY_PREFIXES)


def extract_reply_body(full_body):
    """Strip HTML, decode entities, normalize line endings, then strip quoted original message."""
    # CRITICAL: normalize \r\n → \n FIRST — Outlook/iOS/Windows replies use CRLF.
    # Without normalization, \n-based quote patterns fail silently and the entire
    # quoted original email contaminates classification. (Jul 20, 2026: Jeff Dillon)
    body = full_body.replace('\r\n', '\n').replace('\r', '\n')
    body = re.sub(r'<[^>]+>', ' ', body)
    body = __import__('html').unescape(body)
    quote_patterns = [
        r'\n>',
        r'\nOn .* wrote:',
        r'\nOn .* at .* wrote:',
        r'\nFrom:.*\n(?:Sent|Date):.*\nTo:',  # Outlook forward
        # Inline quote delimiters (when HTML stripping collapses newlines)
        r'On .* at .* wrote:',
        r'On .*, .* wrote:',
    ]
    for pat in quote_patterns:
        m = re.search(pat, body)
        if m:
            body = body[:m.start()]
            break
    return body.strip()


def classify_reply(body_text):
    """Classify a stripped reply body. Returns one of:
    positive_interested, negative_notfit, hostile, auto_responder, neutral
    """
    body_lower = body_text.lower()

    # One-word messages override
    body_words = body_text.strip().split()
    if len(body_words) <= 2:
        word = body_text.strip().lower().rstrip('.!?,;')
        if word in ('sure', 'ok', 'okay', 'yes', 'yep', 'yeah', 'absolutely', 'definitely', 'indeed', 'please'):
            return 'positive_interested'
        if word in ('stop', 'unsubscribe', 'remove'):
            return 'hostile'

    # First-word positive override — catches "Yes, I'd be open to see what you have"
    # and similar multi-word replies where the first word alone signals interest.
    # (Jul 20, 2026: Jeff Dillon — "Yes, I'd be open..." classified as neutral
    #  because len(body_words) > 2 and no positive regex matched.)
    first_word = body_words[0].lower().rstrip('.!?,;:')
    if first_word in ('yes', 'yeah', 'yep', 'yup', 'absolutely', 'definitely', 'indeed', 'sure'):
        # Only fire if body doesn't contain rejection signals
        if not re.search(r'\b(?:not interested|decline|pass|don.t need|no thanks|remove me|unsubscribe)\b', body_text.lower()):
            return 'positive_interested'

    # Hostile patterns (MUST run before negative)
    hostile_patterns = [
        r'\bstop\b.*(?:email|contact|messag|text)',
        r'(?:email|contact|messag|text).*\bstop\b',
        r'\bremove\b.*(?:list|email|contact)',
        r'(?:list|email|contact).*\bremove\b',
        r'\bunsubscribe\b',
        r'\btake me off\b',
        r'\bdo not (?:contact|email|reach)\b',
        r'\breport\b.*(?:spam|you)',
        r'^stop\s*$',
    ]
    if any(re.search(p, body_lower) for p in hostile_patterns):
        return 'hostile'

    # Ticket system / challenge-response
    ticket_patterns = [
        r'\bticket\b.*\bcreated\b', r'\bsupport ticket\b',
        r'\bplease verify\b', r'\bverify you are\b', r'\bconfirm.*human\b',
        r'\breal live human\b', r'\bchallenge.?response\b',
    ]
    if any(re.search(p, body_lower) for p in ticket_patterns):
        return 'auto_responder'

    # OOO / customer-service auto-responders (72 business hours, etc.)
    cs_auto_patterns = [
        r'\baddressed within\b', r'\bbusiness hours\b', r'\bbusiness days\b',
        r'\bwe will respond\b', r'\bwe.ll get back\b',
    ]
    if any(re.search(p, body_lower) for p in cs_auto_patterns):
        return 'auto_responder'

    # CSS-only / HTML-cruft bodies (broken auto-replies)
    if len(body_text.strip()) < 20 or re.match(r'^[\\s{};:#.\\-\\w]+$', body_text.strip()):
        return 'auto_responder'

    # OOO patterns
    ooo_patterns = [
        r'\bout of (?:the )?office\b', r'\baway from\b', r'\breturning\b',
        r'\bvacation\b', r'\bout of town\b', r'\bnot in the office\b',
        r'\bauto.?reply\b', r'\bautomated response\b',
        r'\bretired\b', r'\bno longer (?:in |with |at )',
        r'\bpermanently\b.*(?:close|vacation|retire)',
        r'\bwill be out\b', r"\bi (?:am|'m) out\b",
        r'\bout of the country\b', r'\blimited access to email\b',
        r'\bwell deserved break\b', r'\btaking a break\b',
        r'\bwill respond to your message\b',
    ]
    if any(re.search(p, body_lower) for p in ooo_patterns):
        return 'auto_responder'

# Negative patterns — check BEFORE positive to avoid "not interested" matching "interested"
    # First, strip "Thank you / Thanks" prefix to avoid false-positives
    stripped = re.sub(r'^(?:thank you|thanks)[,.\\s]*', '', body_lower, flags=re.IGNORECASE)

    # "Not sure I understand" / "Not sure what" — genuine questions, not rejections.
    # Skip negative check entirely for these; they're positive_interested.
    if re.search(r'\bnot sure\b', stripped):
        # Unless followed by rejection signals
        if not re.search(r'\bnot interested\b|\bdon\'t need\b|\bno thanks\b', stripped):
            return 'positive_interested'

    negative_patterns = [
        r'\bnot interested\b', r'\bno thanks?\b', r'\bno thx\b',
        r'\bnot a fit\b', r'\bnot (?:currently|right now)\b',
        r"\bdon't need\b", r'\bi must decline\b', r'\bpass\b',
        r"\bi'm good\b", r"\bi am good\b", r"\bwe'?re good\b",
        r'\bnot looking\b', r'\bnot currently\b',
        # Polite decline variants that don't use "not/interested"
        r'\btoo late\b',                 # "it's too late"
        r'\balready\b.*\b(?:own|have)\b',  # "already developed my own/have my own"
    ]
    if any(re.search(p, stripped) for p in negative_patterns):
        return 'negative_notfit'

    # Positive patterns
    positive_patterns = [
        r'\b(?:yes|sure|ok|okay|yep|yeah|absolutely|definitely|indeed|please do|go ahead|send|love to|would love|interested|tell me more|learn more|hear more|how does it work|works for me)\b',
        r'\bsend (?:me )?(?:more|some)?\s*(?:info|information|details|pricing)',
        r"\bwhat.?(?:do you|are you|'?s)\b",
        r'\bcan you send\b', r'\bmeeting link\b',
        r'\bopen to\b.*(?:see|hear|learn|chat|discuss|talk)',  # "open to see what you have" (Jul 20: Jeff Dillon)
    ]
    if any(re.search(p, body_lower) for p in positive_patterns):
        return 'positive_interested'

    return 'neutral'


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitor Owned Audiences replies')
    parser.add_argument('--pages', type=int, default=3, help='Inbox pages to sweep (default: 3)')
    parser.add_argument('--campaign-id', type=int, default=CAMPAIGN_ID)
    parser.add_argument('--timeout', type=int, default=60, help='API timeout per call (default: 60s)')
    args = parser.parse_args()

    CAMPAIGN_ID = args.campaign_id
    Instantly_KEY = load_Instantly_key()

    # -------------------------------------------------------------------
    # PRE-CHECK: Instantly API health (prevents false all-clear on expiry)
    # -------------------------------------------------------------------
    api_ok, api_msg = check_api_health(Instantly_KEY)
    if not api_ok:
        msg = (
            f"FATAL: Instantly API is DOWN ({api_msg}).\n"
            f"Pipeline cannot monitor inbox — all campaigns are blind.\n"
            f"Recovery: renew at app.Instantly (Instantly@usingaitoscale.com)\n"
            f"then run a full inbox sweep to catch missed replies.\n"
            f"See: Instantly-cold-email → references/plan-expiry-recovery.md"
        )
        print(msg, file=sys.stderr)
        print(msg)
        sys.exit(2)  # exit code 2 = API down (distinct from 0=clear and 1=positives)
    print(f"Instantly API: {api_msg}")

    # Load state files
    with open(STATE_PATH) as f:
        state = json.load(f)
    known_ids = set(state.get('known_reply_message_ids', []))

    hostile_senders = set()
    unsub_senders = set()
    daemon_replied = set()
    try:
        with open(DAEMON_STATE_PATH) as f:
            daemon_state = json.load(f)
        hostile_senders = set(daemon_state.get('hostile_senders', []))
        unsub_senders = set(daemon_state.get('unsub_senders', []))
        for mid in daemon_state.get('replied_message_ids', []):
            daemon_replied.add(mid.strip('<>'))
    except FileNotFoundError:
        pass

    # -----------------------------------------------------------------------
    # Phase 1: Collect inbox entries
    # -----------------------------------------------------------------------
    all_entries = []
    for page in range(args.pages):
        offset = page * 20
        payload = json.dumps({"offset": offset, "limit": 20})
        payload_path = f'/tmp/iq_monitor_p{page}.json'
        with open(payload_path, 'w') as f:
            f.write(payload)

        result = run_Instantly(
            f'{Instantly_BIN} inbox replies --from-json {payload_path} --format json',
            timeout=args.timeout
        )
        if result.returncode != 0:
            print(f"Page {page} API error: {result.stderr[:200]}", file=sys.stderr)
            if page == 0:
                continue
            break
        try:
            raw = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"Page {page} JSON parse error", file=sys.stderr)
            break
        entries = raw.get('data', [])
        if not entries:
            break
        all_entries.extend(entries)
        print(f"Page {page}: {len(entries)} entries")

    print(f"\nTotal entries: {len(all_entries)}")

    # Filter to target campaign
    campaign_entries = [e for e in all_entries if e.get('email_campaign_id') == CAMPAIGN_ID]
    other_entries = [e for e in all_entries if e.get('email_campaign_id') != CAMPAIGN_ID]
    print(f"Campaign #{CAMPAIGN_ID}: {len(campaign_entries)} entries")
    if other_entries:
        print(f"Other campaigns: {len(other_entries)} entries")
        for e in other_entries:
            print(f"  #{e.get('email_campaign_id')} — {e.get('lead_first_name')} ({e.get('lead_email')})")

    # -----------------------------------------------------------------------
    # Phase 2: Split auto-reply emails vs real leads
    # -----------------------------------------------------------------------
    auto_reply_entries = []
    real_entries = []
    for e in campaign_entries:
        email = e.get('lead_email', '')
        if is_auto_reply_email(email):
            auto_reply_entries.append(e)
        else:
            real_entries.append(e)

    print(f"\nAuto-reply (by email prefix): {len(auto_reply_entries)}")
    print(f"Real leads (need message history): {len(real_entries)}")

    # -----------------------------------------------------------------------
    # Phase 3: Pull message history + classify
    # -----------------------------------------------------------------------
    new_positives = []
    new_negatives = []
    already_handled = []
    auto_responders_confirmed = []
    vestigial = []
    skipped_hostile = []

    for entry in real_entries:
        lead_id = entry.get('email_lead_id')
        lead_email = entry.get('lead_email', '')
        lead_name = entry.get('lead_first_name', '')

        # Check hostile/unsub
        if lead_email in hostile_senders or lead_email in unsub_senders:
            skipped_hostile.append({'name': lead_name, 'email': lead_email})
            continue

        print(f"\n--- {lead_name} ({lead_email}) lead_id={lead_id} ---")

        result = run_Instantly(
            f'{Instantly_BIN} leads messages --campaign-id {CAMPAIGN_ID} --lead-id {lead_id} --format json',
            timeout=args.timeout
        )
        if result.returncode != 0:
            print(f"  ERROR: {result.stderr[:100]}", file=sys.stderr)
            continue

        try:
            history_raw = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"  JSON parse error")
            continue

        history = history_raw.get('history', [])
        if not history:
            print(f"  Empty history — vestigial (lead deleted)")
            vestigial.append({'name': lead_name, 'email': lead_email})
            continue

        # Get latest REPLY
        replies = [m for m in history if m.get('type') == 'REPLY']
        if not replies:
            print(f"  No REPLY in history")
            continue

        latest_reply = replies[-1]
        reply_msg_id = latest_reply.get('message_id', '')
        reply_body = latest_reply.get('email_body', '')
        reply_time = latest_reply.get('time', '')

        msg_id_norm = reply_msg_id.strip('<>')

        # Check our_replies_after
        reply_dt = None
        try:
            reply_dt = datetime.fromisoformat(reply_time.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            pass

        our_replies = []
        if reply_dt:
            for m in history:
                if m.get('type') == 'SENT' and m.get('time'):
                    try:
                        sent_dt = datetime.fromisoformat(m['time'].replace('Z', '+00:00'))
                        if sent_dt > reply_dt:
                            seq = str(m.get('email_seq_number', ''))
                            body = str(m.get('email_body', ''))
                            # Exclude sequence auto-emails (seq 1/2/3) unless they contain reply patterns
                            if seq not in ('1', '2', '3') or 'case study' in body.lower() or 'here it is' in body.lower() or 'thanks for the reply' in body.lower():
                                our_replies.append(m)
                    except (ValueError, AttributeError):
                        pass

        print(f"  Reply: {reply_time} | our_replies_after: {len(our_replies)}")

        if our_replies:
            print(f"  ALREADY HANDLED")
            already_handled.append({'name': lead_name, 'email': lead_email, 'lead_id': lead_id})
            continue

        # Classify
        body_text = extract_reply_body(reply_body)
        classification = classify_reply(body_text)
        print(f"  Class: {classification} | body: {body_text[:120]}")

        result_obj = {
            'name': lead_name,
            'email': lead_email,
            'lead_id': lead_id,
            'msg_id': reply_msg_id,
            'body': body_text[:300],
            'classification': classification,
            'entry': entry,
        }

        if classification == 'positive_interested':
            new_positives.append(result_obj)
        elif classification in ('hostile', 'negative_notfit'):
            new_negatives.append(result_obj)
        elif classification == 'auto_responder':
            auto_responders_confirmed.append(result_obj)

        time.sleep(0.3)  # gentle rate limit

    # -----------------------------------------------------------------------
    # Phase 4: Summary
    # -----------------------------------------------------------------------
    print(f"\n{'='*60}")
    print(f"SUMMARY — Campaign #{CAMPAIGN_ID}")
    print(f"{'='*60}")
    print(f"Auto-reply (prefix):   {len(auto_reply_entries)}")
    print(f"Auto-responder (body): {len(auto_responders_confirmed)}")
    print(f"Hostile/unsub skipped: {len(skipped_hostile)}")
    print(f"Vestigial (deleted):   {len(vestigial)}")
    print(f"Already handled:       {len(already_handled)}")
    print(f"New negatives/hostile: {len(new_negatives)}")
    print(f"New positives:         {len(new_positives)}")
    print(f"{'='*60}")

    for p in new_positives:
        print(f"  ➕ {p['name']} ({p['email']}) — {p['body'][:100]}")
    for n in new_negatives:
        print(f"  ➖ {n['name']} ({n['email']}) — {n['classification']}: {n['body'][:80]}")

    # Save results
    output = {
        'campaign_id': CAMPAIGN_ID,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'positives': new_positives,
        'negatives': new_negatives,
        'auto_responders': auto_responders_confirmed,
        'already_handled': already_handled,
        'vestigial': vestigial,
        'skipped_hostile': skipped_hostile,
        'auto_reply_prefix_count': len(auto_reply_entries),
        'total_inbox_entries': len(all_entries),
    }
    with open('/tmp/monitor_results.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults → /tmp/monitor_results.json")

    # Exit code: 0 if no new positives, 1 if positives found (for cron alerting)
    sys.exit(1 if new_positives else 0)