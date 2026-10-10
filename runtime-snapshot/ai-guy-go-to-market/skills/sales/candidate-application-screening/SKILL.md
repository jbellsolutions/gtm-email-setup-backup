---
name: candidate-application-screening
description: "Use when screening job applications from Gmail."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [recruiting, hiring, candidate-screening, Gmail, resumes, PDF, ranking]
---

# Candidate Application Screening

Use this class-level workflow when the user wants applications reviewed, shortlisted, ranked, or labeled in Gmail. The deliverable is a defensible shortlist for human review, not an autonomous hiring decision.

## Operating principles

1. Scope precisely before reading: identify the exact Gmail label/query, expected population, role post, shortlist size, and requested destination label. Do not scan the whole mailbox.
2. Use job-related evidence: score demonstrated experience, tools, work samples, availability, communication, and role responsibilities. Do not infer protected characteristics or use them as criteria.
3. Treat education preferences as explicit user criteria, not a substitute for fit. Verify the actual education entry and distinguish graduation/degree from a workshop, certificate, school mention, or unrelated name match.
4. Be skeptical of keyword stuffing: repeating job-post terms is not proof. Prefer concrete responsibilities, duration, outcomes, named systems, certifications, and internally consistent dates. Flag claims for skills-test verification rather than declaring fraud from a resume alone.
5. Never reject applicants, send candidate messages, or make a final hiring decision without explicit approval. Labeling a shortlist is a reversible organizational action when explicitly requested.

## Gmail workflow

1. Confirm the mailbox identity before acting. A hiring address may be an alias or forwarding address rather than a separately connected Gmail account; do not assume that messages routed to/from the alias prove access to its labels.
2. List labels in the specified mailbox/account and resolve the exact label ID by name. Never guess a label ID. If the requested mailbox is not among connected accounts, report that limitation and request connection/access rather than substituting another inbox.
3. Search only the requested label, e.g. `label:"Hermes to check"`. Record the returned message count and note that Gmail counts messages, while the user may be counting conversations or unique applicants.
4. If the label is not visible, an alias-address search may be used for discovery only. Treat those results as potentially unrelated hiring notifications, calendar messages, marketing, or applications for other roles. Do not reply, draft, or bulk-process them unless the exact role label or otherwise unambiguous role-specific scope is verified.
5. Before creating drafts, show/confirm the target population and use in-thread drafts addressed to each applicant. Never send messages without explicit approval.
3. If the count differs from the user’s estimate, investigate duplicates, follow-ups, and multiple emails from the same applicant before reporting the population size.
4. Fetch full messages, not metadata only. Extract body text and attachment metadata.
5. Download candidate PDF attachments using Gmail message attachment IDs. Extract text with PyMuPDF (`fitz`); use OCR for image-only PDFs when available. Preserve message IDs and filenames for traceability.
6. Build one candidate record per applicant, deduplicating by person/email while retaining all relevant messages. Store name, email, message IDs, body, resume text, attachments, education evidence, experience, tools, availability, concerns, and source excerpts.
7. Rank against a written rubric derived from the job post. Use two-pass review: broad extraction, then detailed review of strongest and borderline candidates.
8. Resolve the destination label, create it only if explicitly requested and absent, then add exact shortlist message IDs with Gmail modify.
9. Verify by searching the destination label and confirming the exact number and identities.

## Ranking rubric

Adapt weights to the role:

- Must-have responsibility fit: executive/admin support, inbox/calendar, travel, records, bookkeeping, meetings, events, project/content work.
- Technical adaptability: AI tools, spreadsheets, Airtable/CRM, WordPress, Xero or equivalent bookkeeping, automation, light coding where relevant.
- Evidence quality: concrete work history and outcomes over generic self-description.
- Schedule/work readiness: required timezone/hours, reliable setup, communication, and availability when explicitly evidenced.
- **Education preference:** treat the user's explicit university hierarchy as a primary ranking dimension when provided, not merely a tie-breaker. For this hiring workflow, rank in this order: (1) confirmed graduate of UP, UST, De La Salle, or Ateneo **plus** strong job compatibility; (2) confirmed graduate of one of those four preferred university groups with weaker job compatibility; (3) strong job compatibility without confirmed preferred-university graduation. Keep separate fields for preferred-university attended, preferred-university graduated, and education ambiguous. Verify the actual education section and degree/graduation context; do not award preference for certificates, workshops, affiliations, references, or incidental mentions.
- Flags: missing application steps, unsupported/contradictory claims, unclear dates, material gaps, or apparent job-post copying. These are verification flags, not automatic disqualifiers unless instructed.

Do not use naive substring scoring. `UP`, `Ateneo`, `La Salle`, or `University of the Philippines` can appear in certifications, references, employer descriptions, or unrelated text. Inspect the education section and nearby degree/date context before assigning an education preference.

## Output format

Give a concise method note and population count; a ranked shortlist with name, email, source message ID, evidence, strengths, concerns, and suggested skills-test focus; a separate note for ambiguous claims; destination-label update and independent verification; and a clear statement that the shortlist supports human review rather than final hiring.

## Support reference

See `references/gmail-resume-screening-runbook.md` for the tested native Hermes Gmail/PDF extraction pattern, label operations, and verification checklist.
