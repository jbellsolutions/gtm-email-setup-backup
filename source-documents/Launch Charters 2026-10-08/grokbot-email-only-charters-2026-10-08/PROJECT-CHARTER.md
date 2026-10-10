# GrokBot email and replies project charter

Owner: Justin Bellware. Coordinator: Head of Operations. Timezone: America/New_York. This charter replaces the broad fleet mandate for the reduced project once Justin adopts it. It does not activate any sender or routine merely by being loaded.

## Mission and scope

Run existing and newly approved Instantly cold campaigns, separate SMTP newsletters and their replies, plus Justin's LinkedIn DMs/comment replies. Preserve campaign assets, history, source provenance and suppression records. Provide reliable replies and delivery controls with fewer agents and fewer recurring wakes.

Nine core agents: Head of Operations, Campaign Manager, List Manager, Custom Email Writer, Editorial, ESP & Deliverability, Instantly Operator, SMTP Newsletter Operator and Reply Agent. Keep Attio CRM Operator only if Attio remains the prospect CRM. Keep one read-only LinkedIn Inbox Bridge only if direct Reply Agent tool access cannot cover a required inbox.

Databox/Bops is the external lead source. There is no required GrokBot Data Agent, Lead Radar, Prospecting Agent, Dream 100, content/podcast bot, affiliate recruiter, Call Prep, social-growth bot, or separate manager for each brand. Existing cold campaign offers survive as files under one Campaign Manager. Beehiiv publishing and general client operations are out of scope. Keep any brand-specific lane that falls within cold email or SMTP campaigns, including Connect Med if applicable; verify its actual purpose before deciding. LinkedIn new connection/DM campaigns, engagement hunting, posts and reactivation blasts are also out of scope; existing LinkedIn campaigns stay paused unless Justin separately retains one.

## Ownership and workflow

Campaign Manager owns portfolio, brief, readiness and campaign folders. List Manager owns eligibility and suppressions. Custom Email Writer produces the researched sequences and newsletter drafts. Editorial independently signs off the exact version. ESP clears infrastructure and capacity. Instantly Operator changes Instantly; SMTP Newsletter Operator changes Listmonk/SMTP. Reply Agent owns all conversational wording and sends through verified connectors under its activated playbook. Attio is the sole CRM writer when retained. HoOps coordinates and records decisions; it does not duplicate every agent's work.

Brief → eligible list → source-backed copy → Editorial PASS → ESP clearance → platform readback → Justin's launch GO. Campaign-specific approved daily operations can then run within their recorded limits. A copy/list/settings change that invalidates those gates returns the campaign to HOLD. First launch, resume after the fleet stop, ramp, new offer, new sender identity or materially increased spend requires the applicable explicit decision. Never invent terms, proof, dates or links.

## Channel rules

Keep Instantly inboxes/domains separate from SMTP newsletter delivery. Deduplicate exposure across both channels using historical sends, active conversation and suppression state. Do not turn a newsletter membership flag into proof of consent. Sender/Reply-To must be the intended account, and replies must reach a monitored mailbox.

Reply Agent uses one dedupe ledger and one playbook with campaign/channel overrides. Covered routine replies may SEND only after Justin activates the specific standing playbook. A global pause freezes that standing permission until its scope is reconciled. Draft/escalate anything outside approved facts, sender identities, money/contract terms or booking authority. Stops/unsubscribes suppress promptly even if CRM logging is blocked. Do not ask for permission again when a valid active playbook already covers the action.

DMs and LinkedIn comments are distinct channels. The old dashboard was comment-only; DM capability must be independently verified. No automated engagement, new posts or first-connection reactivation is implied by replies-only permission.

## Delivery and credit rules

Use current ESP evidence, not historic target volume. Confirm placement, blocklists, authentication, domain sharing and actual allocation. Unknown bounce/complaint telemetry is not zero. Preserve lane-specific stricter thresholds; restore their current stop conditions before launch. ESP can order a documented protective pause, with the relevant operator applying it and telling HoOps.

The October 7 facts in CURRENT-STATE.md are dated recovery evidence, not a current delivery certification. Restore exact sequence, sender identity, footer, suppression and stop-on-reply settings. Never mail the burned localaffiliatepro.com CTA. No default 2,000 gym/day or 10,000 newsletter/day target becomes a standing requirement.

Historical credit ceiling: no more than 10% of weekly GrokBot usage in a day unless Justin explicitly raises it. Use events, platform-native reporting and shared snapshots. No broad helper fleet, duplicate polling or unconditional “send daily even when blocked” rule. External Databox pulls retain their source-side plan/budget authorization; publishing a skill is not a spending approval.

## Reset invariants

Reset the GrokBot team and its owned automation, not the external sender accounts. Preserve Instantly/Listmonk campaigns, contacts, inboxes, billing, DNS, unsubscribe history, warmup settings and calendar state. Export retained and excluded agent prompts, chats, routines, files, IDs and dependencies before archiving. Do not assume app uninstall safely preserves state.

Inventory app routines AND their bridge/webhook/one-time-job routes. Stop old triggers and verify their state before staging replacements. All new/replacement routines start disabled. Use existing verified agent IDs when slimming in place; use actual new IDs when rebuilding. Never paste old UUIDs blindly into new profiles.

Use FILES-AND-RESTORE.md and templates/ for the project state. Keep secret values in supported secret storage, referenced by name. Missing exports and source CSVs remain unresolved, with owners and required retrieval paths. Agents with unknown dependencies remain inactive until resolved rather than being deleted.

## Acceptance and activation

A reduced team is ready when the preserved backup has hashes and a restore check; the keep/archive map and dependency graph are complete; exact routine text and trigger routes are recorded; every required inbox channel has a verified read route; the two sending infrastructures are separate; current suppression history is imported; and the platform campaign/list readbacks match the file registry.

Use read-only connector checks, offline render/QC fixtures and recorded event-replay fixtures for setup validation. Actual seed emails, invites or test replies require their existing or new send permission. Present the remaining activation decisions together: reply playbook and channels, specific routine enablement, seed tests and campaign GOs. A partially missing old transcript need not block an independently verified lane; it does block unsupported deletion or claims of exact restoration.
