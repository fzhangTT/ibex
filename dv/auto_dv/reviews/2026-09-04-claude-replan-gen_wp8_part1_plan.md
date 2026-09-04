# Cross-model review - scoped re-review: dv/auto_dv/docs/gen_wp8_part1_plan.md (delta since 2098158b) against findings in dv/auto_dv/reviews/2026-09-04-claude-plan-gen_wp8_part1_plan.md, reviewed text at commit fa3fb77a

**Reviewer:** claude CLI 2.1.260 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 9d08cf10-0c1e-4f34-a116-48ad3d0f6889; sandbox: bubblewrap, working directory = detached read-only checkout of commit fa3fb77aee8934a75fc3ba9ceb91d2d9c3f186c3 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit fa3fb77aee8934a75fc3ba9ceb91d2d9c3f186c3
**Date:** 2026-09-04
**Target:** scoped re-review: dv/auto_dv/docs/gen_wp8_part1_plan.md (delta since 2098158b) against findings in dv/auto_dv/reviews/2026-09-04-claude-plan-gen_wp8_part1_plan.md, reviewed text at commit fa3fb77a (echo at raw line 1)

---

TARGET: dv/auto_dv/docs/gen_wp8_part1_plan.md@91fd41db
TARGET: dv/auto_dv/reviews/2026-09-04-claude-plan-gen_wp8_part1_plan.md@dd44a935

Reviewer identity: claude-fable-5-1 (Claude Code CLI, fresh session, default reasoning), reviewing commit fa3fb77 read-only from a detached checkout. Scope: (1) each finding of the 2098158 review verdicted against the plan at HEAD (300 lines, ASCII confirmed, unchanged since b88b270); (2) the diff `git diff 2098158..HEAD -- dv/auto_dv/docs/gen_wp8_part1_plan.md` (249 insertions, 48 deletions; the retained lines are the Section 2 table rows, Section 3 and the ETA paragraph). Unchanged content not re-reviewed.

**What I verified against the repository (not taken from the plan)**

- Renderer dry run in a temp root from `git archive HEAD` of the four files: `--check` reports up to date; with `"CG-IC-006"` appended to IMPLEMENTED the render succeeds, rc=0, and reports `// CG-IC-006 (gen_ic_ecc_cg), 24 coverpoint bins, 16 cross bins`; the HEAD-rendered 4591 lines are a byte-exact prefix of the 4657-line result; cp_alert_pulses renders `bins one= {0}`, cp_knob renders none/rare/frequent, cp_no_alert_case renders the five bins in plan order. The C-1 prerequisite is met at HEAD (gen_fcov_plan.md:4849-4850 parenthetical after the iff guard, :4859 cross line with `: bins`, :4856 `cp_knob ... : bins`).
- CSV: 44 CG-IC-006 rows reduce to 37 distinct coverpoint-and-bin pairs, per-coverpoint counts matching the Section 2 table exactly; part 1 = 29, part 2 = 8 (cp_inval_ways 2, cp_refetch 1, cp_lookups_blocked_next 1, cp_multiway_mismatch 2, cr_ram_x_inval 2).
- Every line anchor in the revised text resolves: gen_fcov_codegen.py:148; gen_checkers_pkg.sv:408 write_state, :471-474 unconditional alert_internal error, :482 alert_bus expectation, :511 close_owed(0), :592-600 judge_data form selection, :634 attribute_pulse (nobody error at :660), :674-678 close_owed with `closed = 1` at :678, :705 close_owed(1); gen_tb_pkg.sv:246 window=2, :248 retire window=64, :560 tag_shadow, :575 `q.size() > 256` pop, :577-581 qualified_at; gen_icache_ram.sv:28 mem, :34 initial, :76 write branch inside `if (req)`; gen_tb_top.sv:156; gen_rvfi_pkg.sv:69, :207; gen_env_pkg.sv:123, :232, :241; gen_fcov_pkg.sv:1667 GEN_FCOV_UT; gen_export_event_lines.svh:84-91 (plan says 83-91, fine); gen_test_plan.md:434; rtl/ibex_icache.sv:262, :266, :274-283, :580-585; rtl/ibex_core.sv:1830.
- Written-ness claim: the needles `written|wr_seen|initialised|uninit` yield zero identifier-shaped uses in the three files; the word "written" occurs exactly at gen_tb_pkg.sv:38, :271, :560, :562, :602, all in comments. gen_icache_ram.sv contains no export reference. 203 `ignore_bins na = {-1}` clauses at HEAD.
- Buildability of the Section 4 wiring: gen_fcov_pkg.sv (gen_tb.f:25) compiles before gen_checkers_pkg.sv (:26) and neither imports the other, so a `gen_isa_cov` handle in gen_misc_monitor needs only an `import gen_fcov_pkg::*` in gen_checkers_pkg; no cycle, no unbuildable constraint. The plan omits the import (nit, not a finding).
- Plan vs fcov plan at HEAD say the same thing on the four contested points: Sample (plan:118-119, 165-168 vs gen_fcov_plan.md:4791-4794, 4807-4808: checked lookup, first read per line of a way, at most 512); flag (plan:129-147 vs :4798-4806: per LINE of a way, set on every write including sweep and ECC-correction writes, never cleared by reset or invalidation); windows (plan:202-213 vs :4809-4814, 4828-4830: levels over the injection window with a persistent level not quiet, NMI flag over GEN_ICACHE_RETIRE_WINDOW); precedence (plan:180-184 vs :4837-4848: disabled_cache, during_invalidation, then the injection pair, then uninitialised_data_ram, classifier reading qualified_at). The plan's -1 rule for a closure before any retirement (plan:214-217) is not in the fcov plan but does not contradict it.

**Part 1: verdict per finding of the 2098158 artifact**

| row | verdict | evidence in the current plan |
|---|---|---|
| C-1 Critical, unbuildable pair (:45/:89) | ADDRESSED, resolved | :12-17 the three refusals reproduced; :27-31 both sentences WITHDRAWN and appear only inside the withdrawal; :33-36 prerequisite stated as the plan owner's touch, build gated on its commit; :38-48 render reproduced with 24/16. Prerequisite is committed at HEAD (fa3fb77), so the gate is open. |
| H-1 High, queue flooding (:55) | ADDRESSED, resolved | :149-159: no `announce()`, never enters `q`, separate bounded static queue; the five functions named iterate `q` only (confirmed: attribute_pulse :636, close_owed :675, judge_data :595, resolve_held/pending via held, report_phase :700). See new finding 1 on what the bypass leaves unstated. |
| H-2 High, anti-vacuity (:59) | ADDRESSED, resolved | :161-178 three qualifications (first checked read per line, `qualified_at`, injection-free with alert low over 1..GEN_ICACHE_ECC_WINDOW); :180-184 total precedence; :137-142 sweep writes counted (write branch inside `if (req)`, gen_icache_ram.sv:74-76). Equivalent to the recommended hit-way formulation by observation. |
| M-1 Medium, cleared on reset (:54) | ADDRESSED, resolved | :142-147 "Cleared never", initial block only (gen_icache_ram.sv:34), not on reset, not on invalidation. |
| M-2 Medium, window semantics (:64) | ADDRESSED, resolved | :202-205 alert levels over 1..2 with persistent high not quiet; :206-213 NMI over the retire window via `gen_model_state.nmi_int_pend` (gen_rvfi_pkg.sv:69, :207) reaching write_state (:408); "referenced ZERO times" withdrawn at :211-213. |
| M-3 Medium, unnamed detectors (:76) | ADDRESSED, resolved | :225-230 rule and GEN_FCOV_UT via GEN_CMD_FCOV_SELFTEST; :232-237 manifest check on the declared bin plus UT cases for precedence; :238-247 forced alert WITHDRAWN, bus-integrity corruption named (gen_checkers_pkg.sv:482 confirms it is legal); :248-255 mutation detectors named. See new finding 3 on the second mutation's determinism. |
| M-4 Medium, sample timing (:21) | ADDRESSED, resolved for injections | :98-101 closure point at :678 from :511 and :705; :103-109 sampler never reads probe_on/lk_cyc/lk_tag, form (b) in measured runs, -1 when unjudged. See new finding 1: the non-injection sample has no stated site. |
| L-1 Low, zero-hits sentence (:50) | ADDRESSED, resolved | :120-126 identifier claim with the measurement and its control; the five comment occurrences match the repository exactly. |
| L-2 Low, cp_knob bins (:24) | ADDRESSED, resolved | :66 table row; :71-76 render total 24+16 vs manifest total 29 stated separately and correctly. |
| L-3 Low, WP-8 export rows (:3) | ADDRESSED, resolved | :271-277 the three export rows and digest guard placed outside the part-1/part-2 split, formatters exist, RAM model has none. |

All ten rows ADDRESSED; none open. The prior REQUEST-CHANGES is cleared.

**Part 2: rubrics on the diff** (one markdown file; no code lines qualify)
- ai-slop-comments: `{"status": "PASS"}`
- rtl-purity: `{"status": "PASS"}`
- magic-numbers: `{"status": "PASS"}`
- forces-and-hier-access: `{"status": "PASS"}` (the forced-alert red is withdrawn at :240-242; no force remains anywhere in the plan)
- assertion-integrity: `{"status": "PASS"}`

**Part 2: new defects introduced by the remediation**

[Medium][dv/auto_dv/docs/gen_wp8_part1_plan.md:98] The H-1 remediation created a second event queue but Section 4 still says the sample fires at "the single existing closure point" in close_owed, which iterates `q` only (gen_checkers_pkg.sv:675) and so never sees the uninitialised-read events of :156-159. Their classification needs the read cycle plus GEN_ICACHE_ECC_WINDOW to elapse (:176-178), so it cannot fire at the read either. The plan names no drain point, no end-of-run pass for events still inside their window, no bound for the "bounded" queue and no rule for an event evicted before classification (a silent lost sample). - Add to Section 4 a second sample site: the misc monitor's per-cycle pass beside `close_owed(0)` (:511) drains events whose window has closed, judging alert_minor_o from the levels it already records, and the final pass beside `close_owed(1)` (:705) drains the rest; state the bound (at most 512 first-reads per run, so a bound of 512 makes eviction impossible) or count evictions as a GEN_MISC statistic.

[Low][dv/auto_dv/docs/gen_wp8_part1_plan.md:24] "nine plan lines used `: values`" and :36 "eight `: values` lines remain" are miscounts: `git show 6457c71:dv/auto_dv/docs/gen_fcov_plan.md` has 11 such lines (the four CG-IC-008 lines at 4891-4895 included) and HEAD has 10 (3670, 3898, 3938, 3940, 4291, 4613, 4938, 4940, 4941, 4942), none in an IMPLEMENTED group so the render is unaffected. - Correct to eleven and ten, or drop the counts.

[Low][dv/auto_dv/docs/gen_wp8_part1_plan.md:248] The second written-flag mutation's detector (pushing uninitialised events into `q` so pending injections are evicted and attribute_pulse raises the :660 error) fires only if more than 256 events arrive while an injection awaits its form-(b) verdict; with the once-per-line rule of :166-168 capping events at 512 per run and at most two per lookup cycle, eviction inside a 64-cycle window is stimulus-dependent, not guaranteed, and the :149-156 flood rationale is likewise overstated once the cap exists. - Name the run that makes eviction certain (frequent data-injection rate in the first checked lookups after enable) or use a deterministic detector (a GEN_FCOV_UT or directed check that `q.size()` is unchanged across an uninitialised event).

[Low][dv/auto_dv/docs/gen_wp8_part1_plan.md:33] Section 1 Status and :268-269 describe the prerequisite as an uncommitted touch and the word-versus-line granularity as still owed; at the reviewed HEAD (fa3fb77) both are committed (gen_fcov_plan.md:4798 reads "per data-RAM LINE of a way"). Also :44 "appends 65 lines (4591 to 4657)": HEAD's 4591 lines are an exact prefix of the 4657-line render, so 66 lines are appended. - Cite fa3fb77 as the commit that met the prerequisite, drop the "owed" sentence, correct the line count.

No new unbuildable constraint: the render succeeds against the committed fcov plan, the handle wiring respects the package compile order, and every named detector exists in the tree.

Final verdict: APPROVE-WITH-CHANGES
