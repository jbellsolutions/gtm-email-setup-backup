#!/usr/bin/env python3
"""
Classify Instantly reply bodies using the positive-reply-scoring schema.

Usage: python3 classify.py <message_history.json> [message_history2.json ...]

Reads Instantly `leads messages` output, extracts the first human REPLY,
classifies it, and prints the result.

Edge cases handled:
- One-word agreements ("Sure") with trailing quoted email
- "STOP MAIL" / "STOP EMAIL" unsubscribe signals
- Person-left-with-referral before dead-email bounce
- Single-word "Stop" before quoted email
- Pricing inquiries = positive_soft
- July 2026: "away from my email" OOO patterns, "psycho"/"slop" hostile patterns,
  "no interested" typo, hostile pre-check before unsubscribe, "I will reply" OOO patterns
"""

import json, re, sys

ONE_WORD_POSITIVES = {"sure", "ok", "yep", "absolutely", "definitely", "indeed", "yes", "yeah"}

def strip_html(text):
    if not text:
        return ""
    return re.sub(r'<[^>]+>', ' ', text).strip()

def extract_reply_content(body):
    """
    Extract only the NEW reply content, stripping the quoted original email.
    Email clients typically separate the reply from the quote with markers like:
    'On ... wrote:', '-----Original Message-----', '---Original---', 'From:'

    FIXED (June 24, 2026): The original regex required a newline before quote markers,
    missing cases where "Sure" and the quoted email are on the same line (HTML-stripped).
    Now uses re.split() with non-anchored patterns, then takes segment[0].strip().
    """
    if not body:
        return ""

    # Split on common quote separators using re.split (no newline anchor needed)
    # This catches "Sure    On Wed, Jun 3, 2026, 10:42 AM ..." where everything is one line
    quote_markers = [
        r'On\s+.+\s+wrote\s*:',
        r'-{3,}\s*Original\s+Message\s*-{3,}',
        r'From\s*:\s*\S+.*?Sent\s*:',
        r'-{3,}\s*Original\s*-{3,}',
    ]

    earliest_split = len(body)
    for marker in quote_markers:
        match = re.search(marker, body, re.IGNORECASE)
        if match and match.start() < earliest_split and match.start() > 0:
            earliest_split = match.start()

    if earliest_split < len(body):
        return body[:earliest_split].strip()

    return body.strip()


def classify(body, sender_email=""):
    """
    Classify reply body using the positive-reply-scoring schema.
    Rules applied in order — first match wins.
    """
    if not body:
        return "unknown"

    b = body.lower().strip()
    sender_lower = sender_email.lower() if sender_email else ""

    # Pre-processing: extract only the NEW content (before quoted email)
    b_new = extract_reply_content(body).lower().strip()
    b_trim = b_new.replace('.', '').replace(',', '').replace('!', '').replace('?', '').strip()

    # Rule 1: OOO auto-replies
    ooo_patterns = [
        "out of office", "out of the office", "on vacation", "away from my desk",
        "return on", "will be out", "i am out", "i'm out", "auto-reply", "autoreply",
        "automatic reply", "vacation responder", "on annual leave", "on leave",
        "on maternity leave", "on paternity leave", "on sick leave",
        "auto-generated reply", "auto generated reply",
        "closed in observance", "office is closed", "will be closed on",
        "we will reopen on", "i am currently out", "away from my email",
        "taking some time off", "taking time off", "i will reply to your email",
        "i'll reply to your email", "i will reply as soon as i can",
        "will be back in the office", "be back in the office",
        # Retirement/dead-company auto-replies (Jul 8 sweep)
        "i've officially retired", "i have officially retired",
        "officially retired", "i've retired", "i have retired",
        "after four decades", "it's been a great ride",
    ]
    for p in ooo_patterns:
        if p in b:
            return "ooo"

    # Rule 2: Bounce (technical)
    if "mailer-daemon" in sender_lower:
        return "bounce"
    bounce_patterns = [
        "mail delivery failed", "undeliverable", "address not found",
        "mailbox full", "delivery status notification", "could not be delivered",
        "returned to sender", "failed permanently"
    ]
    for p in bounce_patterns:
        if p in b:
            return "bounce"

    # Rule 3: Person-left-with-referral (BEFORE dead-email bounce)
    # EXCLUDED: "no longer active", "no longer valid", "no longer in use" = dead-email,
    # NOT person-left. These should fall through to bounce, not referral.
    person_left = any(p in b for p in [
        "no longer with", "no longer at", "no longer works", "no longer employed",
        "left the company", "has left", "no longer here"
    ])
    # "is no longer" is too greedy — matches "is no longer active" (dead email).
    # Only treat as person-left when followed by person-context words.
    if "is no longer" in b and not any(dead in b for dead in [
        "no longer active", "no longer valid", "no longer in use", "no longer monitored"
    ]):
        person_left = True
    if person_left:
        has_referral = any(ind in b for ind in [
            "contact ", "reach out to ", "try ", "talk to ",
            "speak with ", "speak to ", "connect with "
        ])
        # "email " is too greedy — "email account" is the dead email itself, not a referral.
        # Only count "email " when followed by a name or address pattern.
        if "email " in b and "email account" not in b and "email address" not in b:
            has_referral = True
        if has_referral:
            return "positive_referral"
        # Person left but no named referral
        return "bounce"

    # Rule 3b: Dead-email (no referral given)
    dead_patterns = [
        "email no longer exists", "address no longer monitored",
        "message blocked", "no longer monitored", "no longer in use",
        "email address is no longer", "mailbox not found",
        "recipient address rejected", "user unknown", "no such user",
        "does not exist", "no longer being monitored"
    ]
    for p in dead_patterns:
        if p in b:
            return "bounce"

    # Rule 4: Spam challenge-response
    spam_challenge = [
        "verify you are a real live human", "verify you are human",
        "confirm you are a real person", "click here to verify",
        "prove you are human", "confirm your email address",
        "complete this verification"
    ]
    for p in spam_challenge:
        if p in b:
            return "bounce"

    # Rule 4: Form auto-responders / contact acknowledgments (FIXED June 24, 2026)
    # "Thank you for contacting... we will contact you within" is NOT a referral.
    # These are auto-replies — exclude from denominator like OOO.
    #
    # PATCHED July 8, 2026: "thanks for reaching out" / "thank you for reaching out"
    # were swallowing real human replies that start politely then express interest
    # (e.g., "Thanks for reaching out. This sounds interesting. Please give me more info."
    #  or "Thank you for reaching out. Can you send me some info about SpeakerAgent?").
    # Now gate: only classify as OOO if NO interest signals follow the form language.
    form_auto_patterns = [
        "thank you for contacting", "we will respond within",
        "we'll get back to you", "we will contact you within",
        "we have received your", "your message has been received",
        "this is an automated response", "this is an automatic reply",
        "auto-response", "auto response",
        "ticket has been created", "your email has been received",
        "due to a high volume of emails",
        # NOTE: "thank you for reaching out" and "thanks for reaching out" are
        # gated below — they only count as OOO if no interest signals follow.
    ]
    triggered_form = False
    for p in form_auto_patterns:
        if p in b:
            triggered_form = True
            break
    # Gated patterns: only auto if no interest follows
    gated_form = ["thanks for reaching out", "thank you for reaching out"]
    for p in gated_form:
        if p in b:
            triggered_form = True
            break
    if triggered_form:
        # Check for interest signals AFTER the form language
        interest_signals = [
            "send me", "tell me", "more info", "how does it work",
            "what's your", "what is your", "how much", "pricing",
            "fees", "rates", "cost", "interested", "let's talk",
            "let's chat", "happy to chat", "set up a call",
            "suggest some times", "sounds interesting", "piqued",
            "website", "send over", "send details", "forward me",
            "please give me", "link", "calendar", "book a call",
            "learn more", "would love", "i'd love", "sounds great",
            "check it out", "what do you", "referral", "speakeragent",
        ]
        has_interest = any(sig in b for sig in interest_signals)
        if not has_interest:
            return "ooo"
        # Interest signal found — fall through to further classification

    # Rule 5: Unsubscribe (check new content only for single-word signals)
    # PRE-CHECK: if body contains personal insults, classify as hostile BEFORE unsubscribe.
    # "Stop contacting me psycho!" = hostile, not unsubscribe.
    insult_precheck = ["psycho", "fuck you", "fuck off", "shithead", "dick", "bastard", "creep"]
    for insult in insult_precheck:
        if insult in b:
            return "negative_hostile"

    unsub_patterns = [
        "unsubscribe", "remove me", "take me off your list",
        "remove from", "opt out", "opt-out", "do not email",
        "do not contact", "stop emailing", "stop contacting",
        "please remove", "don't email me", "stop mail", "stop email",
        "take me off", "remove my email", "remove our email",
        "remove this email", "remove email", "no solicitation"
    ]
    for p in unsub_patterns:
        if p in b:
            return "unsubscribe"
    # Single-word STOP (check extracted content before quoted email)
    if b_trim in ["stop", "remove", "unsubscribe"]:
        return "unsubscribe"
    # STOP as first word in new content (e.g. STOP MAIL TKS, STOP  please remove,
    # Stop Ann Pitcher Pitcher Communications... - FIXED Jul 8: was failing on proper nouns)
    if b_trim.startswith("stop ") or b_trim.split()[0] == "stop":
        return "unsubscribe"

    # Rule 6: Not a fit
    notfit_patterns = [
        "not interested", "not a fit", "don't need this", "no thank you",
        "no thanks", "we're good", "we are good", "we are all set",
        "all set", "we're all set", "not looking", "don't need",
        "do not need", "we don't need", "no thx", "pass",
        "not something we", "doesn't interest", "not for us",
        "not for me", "thanks but no", "thank you but no",
        "appreciate it but", "appreciate the offer but",
        "not at this time", "we are fine", "we're fine",
        "not intrested", "not intersted", "no interested",
        "no money", "can't afford", "no budget", "not a prospect",
    ]
    for p in notfit_patterns:
        if p in b:
            return "negative_notfit"
    # Very short negative replies (on new content only)
    if len(b_trim) < 30 and b_trim in ["no", "nope", "nah", "no thanks", "no thx", "pass", "not interested"]:
        return "negative_notfit"

    # Rule 7: Not right now
    notnow_patterns = [
        "not right now", "circle back", "reach back out",
        "maybe later", "next quarter", "next year", "not now",
        "bad timing", "wrong timing", "timing isn't right",
        "timing is off", "try again", "check back"
    ]
    for p in notnow_patterns:
        if p in b:
            return "negative_notnow"

    # Rule 8: Pricing inquiries (interest signal)
    pricing_patterns = [
        "what's the cost", "what is the cost", "please share fees",
        "how much", "what are your rates", "what do you charge",
        "pricing", "price?", "cost?", "rates?", "fee?",
        "what's your pricing", "how much does it cost",
        "what's the price", "cost structure"
    ]
    for p in pricing_patterns:
        if p in b:
            return "positive_soft"

    # Rule 9-10: Referral
    referral_patterns = [
        "try ", "contact ", "talk to ", "reach out to ",
        "not me but", "not the right person", "speak to ",
        "you should reach", "you should contact", "you should talk",
        "better to contact", "better suited", "connect with "
    ]
    for p in referral_patterns:
        if p in b:
            return "positive_referral"

    # Rule 11: Positive soft (send more info)
    soft_patterns = [
        "send more info", "tell me more", "how does it work",
        "send me info", "more information", "send details",
        "i'd like to learn", "would like to learn", "tell me about",
        "share more", "send it over", "send over", "what's this about",
        "what is this about", "what's this regarding",
        "i'm interested in learning", "interested in learning",
        "can you send", "could you send", "please send",
        "send me the", "forward me", "email me"
    ]
    for p in soft_patterns:
        if p in b:
            return "positive_soft"

    # Rule 12: Positive interested — one-word agreements FIRST (on extracted new content)
    if b_trim in ONE_WORD_POSITIVES:
        return "positive_interested"
    # One-word agreement as first word in new content (e.g., "Sure" then quoted email)
    for w in ONE_WORD_POSITIVES:
        if b_trim.startswith(w + " "):
            return "positive_interested"

    interested_patterns = [
        "let's book a call", "let's talk", "let's connect",
        "would love to", "i'd love to", "sounds interesting",
        "sounds great", "interested", "let's do this",
        "let's set up", "set up a call", "schedule a call",
        "let's chat", "happy to chat", "glad to chat",
        "count me in", "i'm in", "let's go", "i'd like to",
        "would like to set", "love to hear", "love to learn",
        "tell me more", "how do i sign", "where do i sign",
        "what's the next step", "next steps"
    ]
    for p in interested_patterns:
        if p in b:
            return "positive_interested"

    # Rule 13: Hostile
    hostile_patterns = [
        "fuck", "shit", "asshole", "idiot", "moron", "scam",
        "spam", "report you", "reporting you", "lawsuit",
        "legal action", "harassment", "stop harassing",
        "cease and desist", "lawyer", "attorney",
        "how dare you", "are you kidding", "joke", "slop",
        "psycho", "delete whatever", "work on your own writing",
        "do not contact me", "do not email me",
    ]
    for p in hostile_patterns:
        if p in b:
            return "negative_hostile"

    # Rule 14: Everything else = neutral
    return "neutral_question"


def main():
    if len(sys.argv) < 2:
        print("Usage: classify.py <message_history.json> [message_history2.json ...]", file=sys.stderr)
        sys.exit(1)

    for path in sys.argv[1:]:
        try:
            with open(path) as f:
                data = json.load(f)
        except Exception as e:
            print(f"ERROR: {path}: {e}")
            continue

        history = data.get("history", [])
        reply_body = None
        reply_from = None

        # Find first human REPLY
        for msg in history:
            if msg.get("type") == "REPLY":
                sender = msg.get("from", "")
                if "mailer-daemon" not in sender.lower():
                    reply_body = strip_html(msg.get("email_body", ""))
                    reply_from = sender
                    break

        if reply_body is None:
            # Check for bounce-only replies
            for msg in history:
                if msg.get("type") == "REPLY":
                    print(f"{path}: bounce (mailer-daemon)")
                    break
            else:
                print(f"{path}: no_reply_found")
            continue

        label = classify(reply_body, reply_from or "")
        preview = reply_body[:120].replace("\n", " ").replace("\r", "")
        print(f"{path}: {label} | {preview}")


if __name__ == "__main__":
    main()
