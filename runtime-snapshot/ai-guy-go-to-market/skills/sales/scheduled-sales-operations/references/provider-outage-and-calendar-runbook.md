# Provider Outage and Calendar Runbook

## Tested sequence

1. Read `Instantly_API_KEY` and call:
   `https://server.Instantly/api/v1/campaigns?api_key=KEY`
2. Parse the full response. Classify `Plan expired!`, `Invalid API Key`, authentication failures, and non-2xx responses as **DOWN**. Never interpret `Scanned: 0` as a healthy empty inbox without this check.
3. If DOWN, skip Instantly inbox calls and state mutations. Report whether recovery requires billing/plan renewal (`Plan expired!`) or key rotation (`Invalid API Key`).
4. Run `/opt/data/skills/sales/pre-call-report/scripts/cal_triple_endpoint_check.py` regardless of Instantly status. It successfully returned eight prospect-facing upcoming bookings in the Aug 3, 2026 run while Instantly was unavailable.
5. Check all `clients/*/pre-call-report.md` paths against attendee email/domain. Generate only genuinely missing reports; refresh existing reports in place.
6. After writes, use filesystem search/read to verify every new report and update stale time-relative language.

## Cal.com observations from the validated run

- Live triple-endpoint output contained `upcoming`, `cancelled`, and `past` sections.
- Upcoming records included `start` timestamps with `Z`; convert them before writing local/ET times.
- A booking can have an attendee timezone different from ET; report both the operator's ET time and the attendee's local time.
- Prospect-facing event types observed: `aiintegraterz` and `speaker-agent-beta`. SpeakerAgent Beta must not be silently reframed as the AI-operator offer.
- Existing reports may be stored under company-domain slugs rather than attendee names. Search report contents before assuming a report is missing.

## Artifact checklist

- [ ] Report path is `clients/{slug}/pre-call-report.md`.
- [ ] Header date/time matches the live booking.
- [ ] Correct booking-specific Zoom/meeting URL is present.
- [ ] Section 7 contains game-plan status, morning-of confirmation, and open items.
- [ ] Unknown Instantly/thread facts are explicitly marked unavailable or unknown.
- [ ] Exclusivity/competitor conflicts are prominent and include the partner/competitor/client decision tree.
