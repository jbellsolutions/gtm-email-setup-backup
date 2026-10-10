# Research and personalization gates

Use this reference when a campaign requires per-lead research and unique copy.

## Evidence tiers

- **Tier A:** A business-relevant service, program, discipline, or facility detail appears in fetched homepage or an entity-verified business social profile. Quote only the observed detail.
- **Tier B:** A non-generic page title or metadata signal supports a narrow relevance line. Do not turn a slogan into a service claim.
- **Tier C:** Only supplied company/location data is available. Label it as a listing fallback, never as website research, and consider holding the record when the brief requires meaningful research.

## Social-source rules

Classify every URL before use. Skip personal profiles, platform placeholders, app-store pages, tracking-only URLs, and unrelated accounts. Store the URL, fetch status, evidence text, and whether it was used in the copy. A fetched social URL is not automatically an entity-verified business source.

## Uniqueness rules

Measure uniqueness on final rendered bodies, not source rows or merge-field payloads. Also measure structural diversity: opening, sentence rhythm, pain framing, offer presentation, and close. A different company name in one shared template is technical uniqueness, not genuinely personalized writing.

## Fallback handling

When a site is unreachable or contains no defensible service detail, use an explicitly labeled listing fallback only if the campaign owner authorizes it. Avoid awkward constructions such as `the {company} site` when the company begins with `The`, and avoid bare noun insertion into slots such as `stood out because {detail}`. Render every opener variant against fallback and observed-detail cohorts.

## Required pre-upload report

Report total leads, website-success count, social-success count, Tier A/B/C counts, held count, unique final-body count, structural-diversity measures, and machine/editorial QA verdict. A timeout or a machine-only pass is not a second-agent editorial pass.
