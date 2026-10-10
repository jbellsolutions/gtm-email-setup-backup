# Cross-Step Component Collapse & Track Leakage (multi-framework sequence QA)

Defect classes found live in the 30,331-lead Fitness Affiliate Program build (2026-09-03).
Both survive per-body machine QA (word counts, banned words, tokens, structure all green)
and only appear when the checker reads ONE lead's entire 22-step sequence.

## 1. Component collapse across steps

A combo-search composer (opener x pain x offer x close per email) without per-lead memory
always converges to the same opener in every framework email and the same short close line
in most of them. Bodies stay unique by hash — the lead still sees the same sentence 10x.

Observed: one lead's 10 framework emails shared 1 opener (10x) and one 6-word close line
appeared in 6 of 10 emails. Follow-up opener phrases repeated 4-5x per lead even when all
leads' copy was unique (separate defect: fixed by rotating opening connectives per slot
index — Quick one. / Circling back. / One more. / Bumping this. / Following up. — with the
greeting stripped before rotation).

Detection (per lead, across all framework-email steps):
- distinct first-paragraph (opener) count vs step count
- distinct close/CTA line count; flag any close line repeated > 2x
- flag any first-4-words phrase repeated across follow-ups within a lead

Fix (in the composer, not the QA):
- keep per-lead `used_openers` / `used_closes` sets, threaded through the build call
- rotate the pool start index per framework (base_shift) so different emails start at
  different pool offsets
- keep the variant pool comfortably LARGER than the step count (16 openers for 10 emails);
  a 6-variant pool with a 10-step sequence forces repeats even with rotation
- escape hatch `if op in used: continue` must still allow the LAST pool item, or long
  sequences crash; prefer "used" checks as preference order, not hard filters

## 2. Track-language leakage through shared templates

Campaigns with offer tracks ("grow what you already sell" vs "we set it up for you") leak
the wrong track's language through shared follow-up/closer templates. Framework emails were
track-adapted; follow-ups 7/8/10 still said "We set it up" / "no charge for the setup" to
grow-track leads who ALREADY run the program (78 leads flagged).

Key lesson: QA that greps only framework emails for track language reports 0. Scan ALL
steps — every follow-up and closer — against EVERY setup-phrasing variant that exists in
the component pools:
`we set (it|the whole thing) up for you | setup costs you nothing | we set it up, we only
get paid | setup is done for you | setup done for you, no charge for it | no charge for the
setup | we don.t charge for the setup | we set up an actual`

Fix: make shared follow-up templates track-neutral ("we handle it", "done for you, no
charge", "nothing to carry" instead of "the setup"), keep the grow CTA ("reply grow")
distinct from the setup CTA ("reply setup"), and re-run the FULL rebuild + both QA passes
after ANY pool edit — a pool edit invalidates every earlier green run.

## 3. Salvaging a timed-out second-agent sweep

A delegate subagent running a full-corpus sweep over ~30k leads died on its 10-minute cap
mid-script (its sweep script hit the foreground terminal 300s timeout, then the delegation
600s cap). The script it wrote IS the deliverable:
- recover it from the subagent's live transcript `cache/delegation/live/<deleg_id>/task-0.log`
  (every write_file/terminal call is logged with paths)
- run it yourself in a background shell: `timeout 900 python3 sweep.py > out.txt 2>&1 &`
- poll the result file; total wall cost ~5 min vs re-delegating and re-paying discovery

Also: backgrounded terminal processes that produce zero output while threads stay alive
mean a stall (catastrophic regex under GIL — see resumable-research-crawler.md), not slow
network. Diagnose with `ps` + `/proc/<pid>/status` Threads + a small foreground batch before
killing.

## 4. Banned-word QA exceptions (lead identity fields)

Company names ("Synergy Fitness", "Price's Academy") and cities ("Price, UT") legitimately
inject banned tokens into copy. Exception rule: strip possessives (`'` and curly `'`) from
both token and identity fields, then match the token against company + City + State before
flagging. Without the city check, a lead in Price, Utah fails 11 steps on "price".

Company-name scrub before interpolation (raw names leaked 17 exclamation-mark and 14 dash
failures and inflated word counts past the band): strip `!`, map `$`->S, split on
en/em-dash/hyphen and keep the first clause, strip trailing `dba|LLC|Inc|the`, drop
`&`-clauses and ` of ` tails, cap at 4-5 words. Result: machine QA 30,331 leads / 0 issues.
