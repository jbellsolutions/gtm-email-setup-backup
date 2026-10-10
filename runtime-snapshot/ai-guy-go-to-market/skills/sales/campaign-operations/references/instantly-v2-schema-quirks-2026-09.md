# Instantly v2 schema quirks (verified live 2026-09-03)

Request shapes for `POST /api/v2/campaigns` discovered by iterating 400-error messages — the API reveals **one missing required property at a time**, so converge by patching the payload after each rejection. None of this is in Instantly's docs; all shapes below were accepted by the live API on this workspace.

## campaign_schedule (accepted shape)

```json
"campaign_schedule": {
  "schedules": [
    {
      "name": "Mon-Fri business hours",
      "days": {"0": true, "1": true, "2": true, "3": true, "4": true, "5": false, "6": false},
      "timing": {"from": "07:00", "to": "17:00"},
      "timezone": "Australia/Brisbane"
    }
  ]
}
```

- `timing.from` / `to` must be **HH:MM strings** matching `^([01][0-9]|2[0-3]):([0-5][0-9])$` — integers like `7`/`17` are rejected.
- `timing` must be an **object** (a string like `"specific_hours"` is rejected).
- `Etc/GMT-10` (accepted on a different org per the 2026-08 build notes) was **rejected here** — the timezone enum is **org-specific**. `Australia/Brisbane` was accepted. If a timezone is rejected, try the org's local IANA name next, and record which org accepts what.

## sequences (accepted shape)

```json
"sequences": [
  {"steps": [
    {"type": "email", "delay": 0,
     "variants": [{"subject": "{{email_1_subject}}", "body": "<div>{{email_1_body}}</div>"}]},
    {"type": "email", "delay": 3,
     "variants": [{"subject": "{{email_2_subject}}", "body": "<div>{{email_2_body}}</div>"}]}
  ]}
]
```

- Each step requires `type: "email"`, `delay` (integer days; 0 for step 1), and `variants` (array of `{subject, body}`). Flat `subject`/`body` on the step object is rejected.
- A **single sequence containing 12 steps** is accepted for long per-lead sequences; per-lead variables resolve as `{{email_N_subject}}` / `{{email_N_body}}` and are auto-registered on the campaign when leads carry them (24 custom variables appeared in the campaign object after upload).

## Workspace lead-limit cap (plan-level)

- `POST /leads/add` returns **403** `{"message": "Lead limit reached. Reamining uploads: N."}` (typo "Reamining" in the live response). This is a **hard stop, not transient** — do not retry the same batch; it will 403 again until slots free up.
- **Partial upload down to the exact remaining count works**: with N=5 remaining, submitting a 5-lead slice of the next 50-lead batch succeeded (`leads_uploaded: 5`). The response includes `remaining_in_plan: 0` and `blocklist_used`.
- The cap is **workspace-wide across all campaigns**, not per-campaign — an account with many paused campaigns can exhaust it even when the new campaign is empty.
- Checkpoint each accepted batch (batch index + partial counts) so a blocked run resumes exactly at the next un-uploaded lead.

## Verified end-to-end pattern (2026-09-03, 5,729-lead build)

Create → explicit `POST /campaigns/{id}/pause` → re-fetch (status 2) → 12 variable-only steps in one sequence → `POST /leads/add` in 50-lead batches with per-lead `custom_variables` (returned later under each lead's `payload`) → per-batch checkpoint file → cursor reconciliation via `POST /leads/list` with filter key `campaign`. Every batch accepted 50/50 with 0 duplicates/invalid/incomplete; reconciled count matched submitted count exactly.
