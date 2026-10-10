# Grammar & Localization Merge-Rendering Defects

A second defect family the structural checks miss. These arise in **deterministic generators**
that fill fixed template strings with merge tags and a region column: the template slot
renders *ungrammatically* or in the *wrong regional column* even though every structural rule
(subject casing, word count, banned words, signoff, no doubled words) passes. They are
per-lead editorial errors, so machine QA (which checks structure, not prose) reports
"0 hard failures" while the copy is still not production-ready.

## Defect table

| Class | Example rendered | Detection | Why machine QA misses it |
|---|---|---|---|
| **Number agreement** — singular template noun slot filled with a plural tag | "each have a **preferred plumbers**" (template `a preferred {trade_noun}` + tag `plumbers`) | `a preferred [a-z ]+` then confirm the tail is singular; or `\ba (plumbers\|sparkies\|chippies\|solar installers)\b` | no banned word, no doubled word, within word count |
| **Article a/an** — "a" before a vowel-initial label | "need **a air con** company" | `\ba (air con\|aircon\|electrician\|insulation\|extension\|enquiry\|estimate)\b` | a/an is a pure prose error; no structural rule fires |
| **Lowercase-after-period fragment** — partner-list appended after a full stop | "…need a builder. **sparkies**, plumbers and roofers." | `\. [a-z][a-z]+s?\b` then confirm it's a list fragment, not an acronym | reads as a stray fragment; no rule catches capitalization |
| **Regional swap missed** — region column not applied to a term/platform | NZ aircon lead says "air con" not "heat pump"; AU lead "is on **Trade Me**" | count term/platform mentions per `country` column, cross-check the doc's swap table | the word isn't banned; the mismatch is semantic |
| **Empty merge tag** — dangling punctuation | "Saw Elemek Electrical works around **.**" | `around \.|near \.|in \.|for \.` | merge tag emptied by bad lead data; structure intact |
| **Sanitization fallback leak** — company name replaced by a placeholder | "Saw **your place** works around Nunawading" | grep the fallback literal; read the relevance line for genuineness | fallback is grammatical ("your place" ≈ "your outfit") but reads templated |
| **De-contraction drift** — generator expands contractions | "who **is** sending" / "does **not** go" vs the doc's native "who's"/"doesn't" | `\b(who is\|what is\|does not\|do not\|is not\|they are\|it is)\b` | no rule bans full forms; it's a tone/voice miss |
| **Trade noun ≠ recipient trade** — cross-field off-by-one mapping | builder lead → "each have a preferred **plumber**"; electrician → "a preferred **chippy**"; aircon → "a preferred **sparky**"; roofer → "a preferred **solar installer**" | extract the merged noun with `each have a preferred (.+?)[,.]` and assert it is in the row's own `trade` allowed set: builder→builder/chippy, electrician→sparky, plumber→plumber, aircon→air con/heat pump, roofer→roofer | a "is the tail singular?" check PASSES this — the fix de-pluralized ("plumbers"→"plumber") but left the wrong trade, so every one of N leads still reads wrong. Singularity ≠ correctness; the noun must match the recipient's own `trade` column |
| **Greeting inconsistency across the sequence** | same lead: "Kia ora Alex," (s1) → "Hey Alex," (s3) → "Hi Alex," (s7) | collect `body.split('<br>')[0]` per step per lead; flag a lead whose 12 greetings mix `Kia ora`/`Hey`/`Hi` (NZ localization) or `Hey`/`Hi` (AU), and flag lowercase first names ("Kia ora amy,") | structural pass; only a per-lead full-sequence read catches it |

## Method

1. **Stratified manual sample first** (confirm the class is real), then **quantify cohort-wide**
   with targeted regex so the report can say "100% of aircon leads" instead of "a lot".
2. **Stratification dimensions** (pick ≥2 each, ≥1 per step read fully):
   - per `country` column (AU / NZ)
   - named-contact greeting vs generic "Hi there,"
   - the regional-greeting variant (e.g. "Kia ora" for NZ)
   - any sanitized-company fallback (e.g. company == "your place")
   - at least one lead from every step in the sequence
3. **Read every sampled email word-by-word.** Grammar/agreement/article/localization errors
   are invisible to regex-first passes — you catch them by reading aloud.
4. **Evidence of variation**: count *distinct opener strings* (first body paragraph after the
   greeting) for step 1. High distinct count (≈ total leads) proves openers vary by research;
   mask company name + town to classify the *template shapes* ("Saw {CO} works around {TOWN}.",
   "Saw {CO} is hiring.", "Had a look at {CO}.") and spot the weak generic shape.
5. **Verify partner/type mapping by reading the map row**, not the prose: for each sampled
   trade, confirm the named partner types match the doc's partner map and name *types only*
   (never specific businesses).

## Reporting

List every defect as `(email, step, quoted fragment, why it breaks the doc)`. A systematic
defect (present in 100% of leads in one step) is a **FAIL** even if every structural rule
passed — "a preferred plumbers" in a Day-3 follow-up is exactly what a recipient clocks as a
bot. Do not rewrite the copy; report only, with exact counts.
