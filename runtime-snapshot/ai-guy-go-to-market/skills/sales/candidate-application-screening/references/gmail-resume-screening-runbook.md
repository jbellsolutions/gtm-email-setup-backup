# Native Hermes Gmail Resume-Screening Runbook

## Verified extraction pattern

- Native Google Workspace setup script: `skills/productivity/google-workspace/scripts/setup.py`
- Native Gmail wrapper: `skills/productivity/google-workspace/scripts/google_api.py`
- Authenticate with the stored Hermes token, then resolve label IDs using `gmail labels`.
- Search a label with Gmail query syntax: `gmail search 'label:"Hermes to check"' --max 500`.
- Fetch full messages with `gmail get MESSAGE_ID`; for attachments, use the Gmail API `users.messages.attachments.get` endpoint with the message attachment ID.
- Decode Gmail URL-safe base64 attachment data. Extract PDF text with PyMuPDF (`fitz`). Keep original message ID, sender, subject, filename, and extracted text together.

## Important verification lessons

1. Gmail returned 295 messages for a label the user described as 291 applicants. Treat this as a message count, not a unique-applicant count. Follow-ups and duplicates can inflate it; deduplicate before claiming the applicant total.
2. A simple keyword scorer over-ranks resumes that repeat job-post language and can misread university names. Education claims must be checked in the education section with degree and date context.
3. A candidate may mention a preferred school in a certificate, event, reference, or employer description without graduating there. Record `education_ambiguous` and do not award the full preference.
4. The Gmail `modify` operation is reversible and appropriate for an explicitly requested shortlist label. Resolve the exact destination label ID first, add labels to the selected message IDs, then search the destination label and confirm exact count/identities.
5. Report source message IDs and concise evidence so the user can audit each recommendation. Recommend a skills test for claims that resumes alone cannot validate.

## Browser OAuth callback quirk

The native flow uses `http://localhost:1` for a manual redirect. Browsers may show `ERR_UNSAFE_PORT`; this is expected. Copy the complete URL from the browser address bar, including `state`, `code`, and `scope`, and pass it to `setup.py --auth-code`. Verify with `setup.py --check` before Gmail operations.

## Screening guardrails

Use only job-related criteria. Do not infer or rank protected characteristics. University preference is a user-specified education preference, but it must not replace evidence of minimum role fit. Do not call a claim fake solely because it is ambitious; mark it for verification through the skills test or interview.
