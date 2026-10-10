# Deterministic Copy QA — full recipe

For auditing per-lead copy produced by a deterministic generator (hash-on-email framework
assignment + fixed template strings + `{company}`/`{city}` merge tags). Confirms fidelity
and catches defect classes a human spot-check misses. Run *before* the manual editorial read.

## 1. Reproduce the generator byte-for-byte (cheap fidelity proof)

Don't hand-copy template strings into the QA script — that re-encoding drifts. Load the
generator's source, redirect its output path to /tmp, exec it, and diff against the shipped
artifact:

```python
from pathlib import Path
src = Path('generate_campaign.py').read_text()
src2 = src.replace("Path('/data/copy.jsonl')", "Path('/tmp/repro.jsonl')")
exec(compile(src2, 'generate_campaign.py', 'exec'), {})
assert Path('/tmp/repro.jsonl').read_text() == Path('/data/copy.jsonl').read_text()
```

Byte-identical ⇒ subjects/cores/follows/closes, framework assignment, and step depth are
exactly as authored. Any diff is the real defect; no diff means fidelity checks are done.

## 2. Template-merge collision defects (the "the The gym" class)

Merge tags render inside fixed phrases; when the **lead data** starts with a word the
template also ends/prepends with, you get doubled words — the same defect family as
"personal training training":

| Template phrase | Lead name | Renders |
|---|---|---|
| `the {c} site mentions` | "The GYM" | "the The GYM site mentions" |
| `…landed on {c}` | "On Point Fitness" | "…landed on On Point Fitness" |
| `I found {c}` | "Found Development" | "I found Found Development" |

**Detection — word-token adjacent-duplicate scan per line, case-insensitive:**

```python
import re
for line in body.split('\n'):
    w = re.findall(r"[A-Za-z][A-Za-z'\-]*", line)
    for a, b in zip(w, w[1:]):
        if a.lower() == b.lower():
            # candidate — READ it before flagging
```

Most hits are innocent real names ("Walla Walla", "Yoga Yoga", "R&R"). But `the The`,
`on On`, `found Found`, `in in` are **template bugs, not data** — the template didn't guard
against leading-article/word collisions.

**Separator trap:** the token scan above drops non-letter chars, so it also matches across
separators — "Pro Cheer Training & Training Center" yields a false "training training" hit
(the `&` is dropped from the token list). For the named defect class, prefer
whitespace-adjacency so `&`, `/`, and punctuation act as boundaries:

```python
DUP_WORD_RE = re.compile(r'\b([A-Za-z]+)\s+\1\b', re.IGNORECASE)  # whitespace-adjacent only
for m in DUP_WORD_RE.finditer(body):
    w = m.group(1).lower()          # read the context; real names are innocent
```

This still catches "found Found" (`I found Found Development`) while ignoring
"Training & Training Center". Classify hits: the task's four named patterns
(`the The` / `on On` / `found Found` / `training training`) are hard failures; other
adjacent duplicates (`for For`, `in in`, `gym gym`) are same-family and worth reporting,
but real names and `&`-separated terms are not.

## 3. Regex false positives that will mis-flag clean copy

Banned-claim / spam regexes fire on innocent merges. **Adjudicate, don't auto-fail:**

- `\bwill (make|earn|generate|profit)\b` → matches `I will make this brief.` (opener). Not an income promise.
- `\b(every member|all members|always|never)\b` → fires on lead names ("Never Give Up Fitness", "Always Reddy Athletics").
- `\$\d[\d,]*` → fires on "$3" inside a lead name ("PURPO$3").
- ALL-CAPS run `[A-Z]{3,}` → fires on real names/abbrevs ("YMCA", "BJJ", "LLC"), not copy defects.

**Doubled-word substring trap:** never scan doubled words as substrings — `"the the" in
body` matches "the theater", and `"is is" in body` matches "this is" (lowercased). Always
use the word-token scan in §2 with same-line adjacency. Same for the claim word-boundary
regexes: verify the *context* before counting a hit as a failure.

## 4. Fallback-detail redundancy

When the research detail falls back to a meta string ("the supplied listing places it in
{City}") and the opener **already** states name+location, the render is redundant and
machine-sounding: "I found The Foundry in Harvard, MA. I checked the site and noted the
supplied listing places it in Harvard, MA." Fix by making the fallback a noun phrase ("its
Harvard location") or dropping the location clause when the opener already carries it.
The fallback must also be traceable (page text, or explicitly-marked fallback) — never invented.

## 4b. Traceability: match the generator's KEY, not its LABEL

A `research_detail` generator commonly emits a human-friendly **label** derived from a
matched **key** in the page text — e.g. `("personal training", "personal training")` emits
`"personal training sessions"`, `("climbing", "climb")` emits `"climbing"`, `("24/7 access",
"24/7")` emits `"24/7 access"`. A naive `detail.lower() in research_text` then flags thousands
of genuinely-traceable details as invented, because the *label* isn't literally in the text
even though the *key* is.

Fix: re-map label→key before the substring match, and search the same text pool the generator
used (page `text` + `title` + `description` + any `social_research` entries with `status=="ok"`):

```python
KEY_MAP = {'climbing': 'climb', 'personal training sessions': 'personal training',
           'strength training sessions': 'strength training', '24/7 access': '24/7'}
d = step0['research_detail']
if d.startswith('its listed location') or d.startswith('the supplied listing'):
    trace = 'fallback'          # explicitly-labeled listing fallback — allowed
else:
    key = KEY_MAP.get(d, d.lower())
    trace = 'OK' if key in combined_text.lower() else 'INVENTED'   # key absent + not fallback
```

A detail is only "invented" when its *key* is absent from the stored research AND it isn't an
explicitly-labeled fallback.

## 5. Stratified sample for the manual editorial read

Deterministic seed; e.g. 4 leads/framework × research-status classes (ok-discipline /
ok-fallback / unreachable) = 40. Read first-touch + follow-up aloud for grammar, tone, and
reasonableness. The machine pass proves structure; the sample read proves it sounds human.
