# Classification Edge Cases (from live sweep, May 13 2026)

Real replies that didn't fit neatly into the original schema — documenting the correct label for each.

## Pricing Inquiries = positive_soft

```
"Whats the cost"
"Please share fees."
"How much does this cost?"
```

These are **buying signals**, not neutral questions. A prospect asking about price has moved past curiosity into evaluation. Classify as `positive_soft`.

## Person-Left-With-Referral = positive_referral

```
"Cuong Nguyen is no longer with Synaptics. Please contact Gene Chen (Gene.Chen@synaptics.com)"
"Jessica is no longer working at BlackPine. For marketing inquiries, please contact Mike Paris mparis@blackpinecommunities.com"
```

The original contact is gone but the auto-reply names a specific replacement. This is a referral — classify as `positive_referral`. Add the referred contact to future outreach lists.

## Dead Email / Email Not Monitored = bounce

```
"This email no longer exists."
"This email address is no longer monitored. For any inquiries, please email t.patton@victors.com."
"Rick is no longer working for Thermal Concepts. His emails are being reviewed."
```

These are effectively bounces — the target inbox can't receive mail. The "contact X instead" variant could be a referral if a specific name is given, but "emails are being reviewed" or "no longer monitored" with no named replacement = `bounce`.

## Spam Challenge-Response = bounce

```
"The message you sent requires that you verify that you are a real live human being and not a spam source. To complete this verification, simply reply to this message..."
```

This is an automated challenge-response system (BoxTrapper/BXD, etc.). It's a spam filter, not a hostile human. Classify as `bounce`.

## Message Blocked by Server = bounce

```
"Message blocked. Your message to X has been blocked. The response was: Message rejected."
```

Server-level rejection. Classify as `bounce`.

## Domain Migration Notice = neutral

```
"We are currently migrating our email to a new domain. Please start using ethan@anchorent.co"
```

Not hostile, not interested, not a bounce. Informational. Classify as `neutral_question`.

## Classification Ordering Pitfall: Person-Left-With-Referral vs. Dead-Email Bounce

**The ordering of classification checks matters.** If "dead email" bounce checks run before "person-left-with-referral," you'll misclassify leads that left but named a replacement.

```
WRONG ORDER:
  "X is no longer with [company]. Please contact Y" → caught by "no longer" → bounce ❌

CORRECT ORDER:
  Check person-left-with-referral FIRST: "no longer with" + "please contact/reach out/email" → positive_referral ✅
  Then check dead-email: "no longer exists" / "no longer monitored" with no named replacement → bounce
```

**Implementation**: Before any dead-email pattern, check for the combination of `person-left` language AND referral language in the same body. "I am no longer with X. Please contact Y" is a referral. "This email no longer exists" (with no contact) is a bounce.

## "no thank you" ≠ "no thanks" (Pattern Gap)

The pattern `'no thanks'` won't match `'no thank you'` in substring search. Both must be in the negative_notfit patterns:
- `'no thanks'` ✓
- `'no thank you'` ✓
- `'no, thanks'` ✓
- `'no. thanks'` ✓

Also: `'we're good'` and `'we are good'` are common rejection signals in conversational replies.

## Single-Word "Stop" Reply (Unsubscribe Signal)

Some replies contain just "Stop" (or "Stop.") at the top with the quoted email below. These are opt-out signals per CAN-SPAM norms. Checking `body_clean == 'stop'` fails because the quoted email text is present.

**Fix**: Check if the body starts with "stop" (case-insensitive) as the first word before any quoted text. Alternatively, check if the first non-quoted line is "stop":
- `body_clean.startswith('stop ')` or `body_clean == 'stop'` or `body_clean.startswith('stop.')`

## "STOP MAIL" / "STOP EMAIL" as Unsubscribe Signal (June 10, 2026)

```
"BUSINESS SOLD - STOP MAIL TKS"
```

This contains "STOP MAIL" which is an explicit unsubscribe command. The word "STOP" alone is already covered by the single-word check, but "STOP MAIL" mid-body (e.g., in all-caps subject-style lines) was NOT caught because "stop mail" wasn't in the unsubscribe pattern list.

**Fix**: Add `'stop mail'` and `'stop email'` to the unsubscribe patterns. Also check for `'stop mail'` / `'stop email'` as substring matches (case-insensitive) before the notfit checks.

## One-Word Agreement with Trailing Quoted Email (June 10, 2026)

```
"Sure    On Wed, Jun 3, 2026, 10:42 AM Soren Marlow <...> wrote: ..."
```

A "Sure" reply followed by the quoted original email was classified as `positive_soft` instead of `positive_interested`. The one-word check `stripped_lower in one_word_positives` failed because the stripped body isn't exactly "sure" — it includes whitespace and the full quoted email thread.

**Fix**: Extract only the NEW content before the quoted email marker. Split on common quote separators (`'On ... wrote:'`, `'-----Original Message-----'`, `'---Original---'`, `'From:'`) and classify only the first segment. Then `'sure' in one_word_positives` matches correctly. This is the same fix as the "Single-Word Stop" edge case above — both need first-segment extraction before classification.

## Abbreviated Negatives (June 11, 2026)

```
"No thx"
"no thx"
```

Abbreviated rejections like "no thx" won't match the full-word pattern `'no thanks'` in substring search. The substring `'no thanks'` is NOT inside `'no thx'`.

**Fix**: Add `'no thx'` to the negative_notfit patterns explicitly. This must be a standalone check — don't rely on `'no thanks'` to catch it.

Dead-email pattern `'address no longer monitored'` won't match `'address is no longer being monitored'` because of the extra words "is" and "being" between "address" and "no longer".

**Fix**: Use broader patterns for dead email detection:
- `'no longer being monitored'` 
- `'no longer monitored'`
- `'is no longer'` combined with email/address context

## Borderline: Dead Email Redirecting to info@

```
"Please note that this email address is no longer being monitored. 
Please resend your email to info@nspra.org and a staff member will respond."
```

This is NOT a real positive_soft. It's a dead email with a generic catch-all redirect. The info@ address is not a decision-maker referral. Classify as `bounce` (dead email) — do NOT flag as positive_referral or positive_soft. Only count named-person referrals as positive.

## "Please do not email us back" = negative_notfit (June 16, 2026)

```
"Please do not email us back thanks!"
```

Soft rejection. The phrase "do not email" is a clear request to stop contacting — equivalent to "not interested." Classify as `negative_notfit`. Current patterns missed this because "do not email" isn't in the notfit list.

**Fix**: Add `'do not email'`, `'do not contact'` to negative_notfit patterns.

## "Remove our email address" = unsubscribe (June 16, 2026)

```
"Remove our email address from this list. No solicitation."
```

Currently the unsubscribe patterns include `"remove me"` and `"remove from"` but NOT `"remove our email address"`. This is an explicit opt-out — classify as `unsubscribe`.

**Fix**: Add `'remove our email'` to unsubscribe patterns.

## "Please stop not intrested" — Typo = negative_notfit (June 16, 2026)

```
"Please stop not intrested"
```

Contains two signals: "please stop" (unsubscribe) and "not intrested" (typo for "not interested"). The pattern `'not interested'` won't match `'not intrested'` — one-letter typo breaks the substring check. "Please stop" alone should trigger unsubscribe classification, but this was missed entirely.

**Fix**: Add `'not intrested'` to negative_notfit patterns. Add `'please stop'` to unsubscribe patterns. Consider fuzzy matching for common typos in rejection signals.

## Auto-Responder False Positive — "We will contact you" (June 16, 2026)

```
"Thank you for contacting Accu-Temp Air Conditioning & Heating. We will contact you within one business day."
```

This is a **form auto-responder** (contact form acknowledgment), NOT a referral. The classifier's referral pattern `re.search(r'(try|contact) (\w+)', body)` matched `"contact you"` → flagged as `positive_referral`. This is a false positive.

**Fix**: The referral regex must exclude `"you"` and `"me"` as the target of "contact" / "try":
```python
referral_match = re.search(r'(?:try|contact)\s+(\w+)', body_first_lower)
if referral_match and referral_match.group(1) not in ('you', 'me', 'us'):
    # real referral to a named person
```

Also: auto-responders that are form acknowledgments ("Thank you for contacting... We will respond within...") should be classified as `ooo` (automated reply) or `neutral_question`, never as `positive_referral` or `positive_interested`.

## Auto-Reply Daemon State File Bloat

The daemon's `auto_reply_state.json` can accumulate massive duplication in the `replied_ids` list (thousands of entries for the same 6 IDs). The `replied_ids` key was supposed to be removed in the May 18, 2026 fix but may persist.

**Symptom**: State file grows to 100KB+ with repeated entries.  
**Fix**: Reset the state file to use only `replied_message_ids` (message-level dedup is sufficient):
```python
state = {"replied_message_ids": [], "hostile_senders": [], "unsub_senders": []}
```

## Empty Reply — Blank Body, Only Quoted Email (June 17, 2026)

```html
<div><br></div><div><br>
<div class="gmail_quote">On Mon, Jun 15, 2026 at 7:10 AM Zayden Marlow wrote:
<blockquote>Hey there, did that last note land?...</blockquote>
</div></div>
```

After HTML stripping, the body contains only the quoted original email with no new content from the sender. This is likely an **accidental reply** (fat-fingered "Reply" in Gmail mobile app).

**Classification**: `neutral_question` (rule 14 fallthrough — no positive or negative signal). Do NOT flag as `positive_interested` just because the reply exists. The absence of original content means no intent.

**Detection**: If the body after HTML stripping and quote-marker splitting has an empty first segment (only whitespace), classify as `neutral_question`.

## "Slop" = Hostile Signal (July 3, 2026)

```
"You either need to work on your own writing skills or delete whatever AI agent you're using for this slop"
```

The word "slop" is a contemptuous dismissal commonly used to insult AI-generated content. It belongs in the hostile pattern list alongside "spam" and "scam" — it signals the recipient is angry about receiving AI-written email.

**Fix**: Add `"slop"` to hostile_patterns.

## "No not really" — Short Rejection = negative_notfit (July 8, 2026)

```
"No not really"
```

Two-word rejection. "No" alone is ambiguous but "no not really" is a clear dismissal. The pattern `'not interested'` won't catch this — it's a conversational brush-off. Same pattern: "Nah not really", "No I'm good", "No, I don't think so."

**Fix**: Add `'not really'` to negative_notfit patterns. Also add `"no not"` as a combined signal — when "no" is immediately followed by a negation ("no not", "no I'm", "no we're"), it's a rejection.

## "I don't think I fit your target profile" — Soft Rejection = negative_notfit (July 8, 2026)

```
"I don't think i fit your target profile. I'm just about as busy as I want to be. If that changes I'll let you know!"
```

"Don't think I fit" is polite rejection language. This doesn't match any existing notfit pattern. The lead is declining but not hostile.

**Fix**: Add `"don't think i fit"` and `"don't think we fit"` to negative_notfit patterns.

## Snarky Rhetorical Rejection = negative_notfit (July 8, 2026)

```
"Read over what you wrote. Would you hire you?"
```

Rhetorical questions dismissing the outreach quality. Not hostile (no profanity, no threats) but clearly negative — the person is not interested. This is between NOT_FIT and HOSTILE on the spectrum. Classify as `negative_notfit` — it's a rejection without escalation.

**Fix**: Add `"would you hire"` to negative_notfit patterns as a snarky-dismissal signal.

## "Stop [Outlook Mobile Signature]" = unsubscribe (July 8, 2026)

```
"Stop Get Outlook for iOS"
```

The user typed "Stop" and their Outlook mobile app auto-appended "Get Outlook for iOS" as a signature on the same line. The result is a single-line body `"Stop Get Outlook for iOS"` which is NOT "Stop" or "Stop." — the `startswith('stop')` check catches it but a full-body equality check fails. This also fails `split()[0] == 'stop' and len(split()) <= 3` because the sentence has 5 words.

**Fix**: When the body starts with "Stop" and contains "Get Outlook for iOS" or "Sent from my iPhone" or similar mobile signatures, strip the signature before classification. Alternatively, check if `body.split()[0].lower() == 'stop'` and the FIRST non-signature word after splitting on common mobile signature markers is "stop".

## "Please give me [timeframe]" — False Positive for POSITIVE_SOFT (July 8, 2026)

```
"This is an auto-generated reply. Thanks for reaching out. Due to the volume of emails I receive, please give me 2 - 3 business days to get back to you."
```

The pattern `"please give me"` matches → classified as `positive_soft`. But this is an auto-responder asking for PATIENCE, not info. The full phrase is "please give me [timeframe] to get back to you", NOT "please give me more info."

**Fix**: Gate the `"please give me"` positive_soft pattern: if followed by time-related words ("days", "business days", "hours", "weeks", "to get back"), do NOT classify as positive. The distinction: "please give me more info" = positive; "please give me 2-3 business days" = auto-responder.

## "Demo video", "Case Studies", "Examples" = positive_soft Signals (July 8, 2026)

```
"we do pretty well on our own, but do you have a demo video of how it works? Some examples or case studies?"
```

Asking for demos, case studies, or examples is pre-purchase behavior — the same class as pricing inquiries. Even when the opener has a mild pushback ("we do pretty well on our own"), the follow-up request for materials is a genuine interest signal.

**Fix**: Add to positive_soft patterns: `"demo video"`, `"case studies"`, `"examples or"`, `"some examples"`.

## "Auto-generated reply" = Auto-Responder (July 8, 2026)

```
"This is an auto-generated reply. Thanks for reaching out. Due to the volume of emails I receive, please give me 2 - 3 business days to get back to you."
```

Explicitly declares itself as auto-generated. This should be classified as OOO (automated reply, exclude from denominator). The phrase "auto-generated reply" is a stronger signal than "thank you for contacting" — it should gate ALL positive checks.

**Fix**: Add `"auto-generated reply"` and `"auto generated reply"` to the auto-responder pre-check (before any positive pattern matching).

```
"Mad 4 Marketing will be closed on Friday, July 3rd in observance of Independence Day."
"The O'Keeffe PR office is closed for July 3 in recognition of the July 4/Independence Day holiday."
"This is an auto-generated reply. Thanks for reaching out."
"I will be out of the office traveling from 6/30 to 7/8."
```

Holiday closures use language like "closed in observance" and "will be closed on" that doesn't match standard OOO patterns ("out of office", "away from my desk"). These are still OOO — classify as such.

**Fix**: Add to OOO patterns: `"closed in observance"`, `"office is closed"`, `"will be closed on"`, `"we will reopen on"`, `"i am currently out"`, `"auto-generated reply"`, `"auto generated reply"`.

Also add to form auto-responder patterns: `"ticket has been created"`, `"your email has been received"`, `"due to a high volume of emails"`.

## Legitimacy-Concern / Skepticism = NOT Positive (July 20, 2026)

```
"Unfortunately, the link is still not working, which raises some concerns for me about the legitimacy and professionalism of this opportunity. Before moving forward, could you please send me some case studies, client success stories..."
```

This is a **legitimacy-concern reply** — the prospect is questioning whether the business is real, not expressing interest. The phrase "raises some concerns… about the legitimacy" is a clear skepticism signal. Even though the body contains "send me case studies" (which normally flags as `positive_soft`), the CONTEXT makes this a demand for proof, not a buying signal. A person who thinks you might be a scam and demands evidence is NOT a positive lead.

**Classification**: `neutral_question` (skeptical). Kill the "send me" positive_soft match when the body also contains legitimacy/professionalism concern language.

**Fix**: Add a pre-check before any positive_soft keyword matching: if the body contains `\braises (?:some )?concerns?\b` AND `\blegitimacy\b` OR `\bprofessionalism\b`, classify as `neutral_question` (skeptical) and skip all positive pattern matching. Also gate on standalone skepticism signals: `\bnot sure (?:this|if|about) (?:is )?legit\b`, `\bconcerns? (?:about|for|with) (?:the )?(?:legitimacy|professionalism)\b`.

**Related pattern — broken link / failed tech = suspicion**: A broken Calendly/booking link followed by a legitimacy concern is a red flag. The operational failure created the suspicion. Fix the link, don't treat this as a positive reply.

