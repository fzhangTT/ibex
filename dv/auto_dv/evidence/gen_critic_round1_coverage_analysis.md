# Critic verdict: the round-1 coverage analysis (owner directive LOG-093), dv/auto_dv/evidence/gen_round_0_coverage_analysis.md at b176587

Scope (the Orchestrator's, from the owner directive of 22:25Z): a fast verdict on the analysis file alone, checking every figure against the record files
it cites, the scope on every number, the three group quantities with no group-gate pass claim, the cause class on each gap, and whether the ranked list is
honest about what round 2 can reach. The owner reads the analysis after this verdict; the team pauses after it.

Artifacts reviewed (sha256 first 16 hex): dv/auto_dv/evidence/gen_round_0_coverage_analysis.md @b176587 76bddfb41ec0ff2c (221 lines); its inputs
dv/auto_dv/evidence/gen_round_0_coverage_tables.md @702d3ba e63e10a93cf1b313 (244 lines, runtime-2), the committed record d29d5db (gen_regress_manifest.yaml,
gen_groups.txt, gen_grpinfo.txt, gen_asserts.txt, gen_hierarchy.txt, gen_dashboard.txt), rtl-arch's pass 14 at 98b643e (gen_exclusions_README.md,
gen_precheck/gen_precheck_dashboard_round_0.txt), and the round's out-tree URG report (modlist.txt, modinfo.txt) which the analysis and the tables cite.

Date: 2026-09-04 (UTC). Role: Critic. Method: every figure re-derived by me from the file the analysis names for it: the gate row and the report-wide and
info rows from the record's manifest, dashboard and hierarchy; the three group quantities from gen_groups.txt (26 rows summed to 3477/4268 = 81.47; the
25 non-ledger scores averaged to 78.2932; 3477/4048 = 85.89); the module table from modlist.txt row by row; the FSM figures from modinfo.txt's six FSM
blocks; the two controller line blocks from modinfo.txt (ALWAYS :504 4 lines 0 covered, :541 171 lines 78 covered); the 13 unhit assertions from
gen_asserts.txt (18 report-wide, 13 distinct in the gated trees) and their cause classes against the build configuration and the rulings; the covergroup
table and zero-hit coverpoints from gen_groups.txt and gen_grpinfo.txt; 182 unbuilt covergroups and 758 declarations from the verifier's population line
and the re-scope record; the 41 uncovered re-scoped bins from my own gen_read_keyed run over the record's grpinfo; the exclusion-adjusted gated row from
gen_exclusions_README.md:149-154 and the report-wide adjusted row from the precheck dashboard; the tables' self-check (the 102 gated instance rows of
modinfo.txt sum to the gate row on all six metrics) re-derived; the plan-credit figures from my own gen_round_credit.py run in the round verdict.
EXPOSURE: the Orchestrator's directive message; the DV Lead's and runtime-2's files; the out-tree report. No subagent used. Written within the twenty
minutes the directive allows, so the depth is one re-derivation per figure and no simulation.

CRITIC VERDICT: APPROVE. Every figure in the analysis reproduces from the file it names, every number carries its scope, the three group quantities are
stated with their rules and the group gate is claimed for none, each gap carries a cause class that holds against the configuration and the rulings, and
the ranked list says where it has not modelled a delta. Three Lows on the ranked list's honesty and two on wording, none of which changes a figure the
owner will read; one of them (the PMP row) should be corrected before the owner reads the list, because it names a round-2 target that a standing rule
blocks.

## 1. What was verified

| section | claim | evidence (re-derived by me) |
|---|---|---|
| 1 | the gate row line 83.83 (3654/4359), cond 67.17, toggle 67.39, fsm 44.19, branch 75.41, assert 92.74 (166/179), each marked against 80; the three group quantities; report-wide 72.64 / 83.91 / 67.18 / 67.15 / 44.19 / 75.49 / 89.11 / 81.47; info u_dut 71.25 | the record's manifest gate_row, totals and info_scope; gen_groups.txt summed and averaged; the arithmetic of 3477/4048 |
| 1 | the exclusion-adjusted gated row (pass 14, 98b643e): denominators 4158 / 9375 / 21102 / 74 / 2363 / 176 with covered counts unchanged; the precheck dashboard's report-wide adjusted row 3688/4194 ... score 76.47; not applied to the recorded round; the strict load is the author's own | gen_exclusions_README.md:149-154 at 98b643e reads exactly those pairs; gen_precheck_dashboard_round_0.txt reads that row with -elfile gen_exclusions.el; the round manifest's elfiles is empty; README:186 states the owed independent re-load |
| 2 | the twelve module rows ranked by missed objects (2211 / 1833 / 1815 / 1214 / 915 / 555 / 524 / 488 / 414 / 392 / 325 / 224) with their metric pairs; the top four hold 7073; ibex_pmp misses 1433 of 3966 conditions; gen_dut_top's 915 are toggle on the wrapper | modlist.txt rows read token by token, all twelve equal; 2211 + 1833 + 1815 + 1214 = 7073; 3966 - 2533 = 1433; gen_dut_top carries only a toggle pair |
| 2 | FSM: five modules, controller 5/26, LSU 6/22, icache 5/8, compressed decoder 14/17, multdiv 8/13, summing to 38/86; the controller's ALWAYS :504 at 0 of 4 and :541 at 78 of 171 | modinfo.txt's six FSM blocks: transitions 26/5, 17/6 + 5/0, 8/5, 17/14, 13/8 (states 10/5, 8/4, 3/1, 4/4, 8/8, 7/7); the two line blocks read as stated |
| 2 | the 13 unhit assertions in the gated trees, in four cause classes: 5 configuration (dummy instructions never enabled), 2 structurally absent (BranchPredictor=0), 1 probe off by LOG-067, 5 genuine | gen_asserts.txt's Uncovered table: 18 report-wide, 13 distinct gated, the same 13 names as the tables; BranchPredictor=0 in the run banners and the plan's configuration header; the B8 knob off by LOG-067; the dummy-instruction set's attempts absent (see I-1) |
| 3 | 26 covergroups, ten at or above 80, the ledger, nine gaps with cause classes; gen_ic_ecc_cg 1/40 with the knob never set; 182 unbuilt covergroups carrying 758 declarations; 41 re-scoped bins uncovered by anything | gen_groups.txt: the ten below-80 rows equal; no round entry carries an icache_ecc plusarg (0 of 19) and the knob is not regime-drawn (regime_set_consumer none); the verifier's population line 182 and the class-A sum 758; my gen_read_keyed run 25 / 41 |
| 4b | the plan-credit figures 66 / 185 / 50 / 18 / 51, PMP 31 of 31, and the acceptance regeneration owned by the DV Lead | my round-verdict probe (gen_critic_round1_record.md Section 1) |
| 5 | pass 14's block structure: 1424 entries, 531 the CHERIoT carve-out, guard-proven dead lines by module, 105 no-ops and 84 effective, so the entry count is not an impact; the 36-run scope; the group cell disputed | the 98b643e commit message and README; the record |
| tables | runtime-2's self-check: the 102 gated instance rows sum to the gate row on all six metrics | re-derived from modinfo.txt: 102 rows, 3654/4359, 6464/9624, 16877/25044, 38/86, 1831/2428, 166/179 |

## 2. Findings

- L-1 (section 4, row 2, "reachable in round 2: yes: two PMP entries exist, unmeasured"): gen_test_pmp_lock and gen_test_pmp_mseccfg are targeted-tier,
  measured false, with no manifest, and every bin their items own sits on a covergroup that is not rendered (0 gen_pmp_* covergroups in
  gen_fcov_groups.svh; their manifests were removed at 04a4808 because the generator refuses to render them). Under P-07 as LOG-090 and LOG-091 hold it, a
  measured entry needs a manifest with a non-empty per-run guaranteed set, so neither entry can be measured in round 2 until its covergroups are built
  (tb-infra) or its items are re-planned onto built ones (DV Lead). The row names the right code-coverage target and the wrong precondition; it should
  read "yes, once a PMP covergroup is built or the entries' items are planned onto built covergroups", with the dependency on row 1 stated. This is the
  one row the owner should not read as written.
- L-2 (section 2, FSM table header "states+transitions covered"): the figures in that column are transitions only (5/26, 6/22, 5/8, 14/17, 8/13), which
  is what URG scores and what 38/86 counts; states (29/40 over the six FSMs) are listed by URG and not scored. Relabel the column "transitions covered"
  or add the states column.
- L-3 (section 4, row 9): "20 in cmp_zca" should read 17 (gen_cmp_zca_cg 279/296); "55 in isa_branch" is right (153/208). Row 8's "12+5 bins" names no
  source from which 12 and 5 derive; state the two sets (the cross bins by name or the covergroup and coverpoint) so the 17 can be re-derived.
- L-4 (sections 2 and 5, sources): modlist.txt and modinfo.txt, which the module table, the FSM detail, the controller line blocks and the tables'
  self-check rest on, are in the round's out-tree URG report and not in the committed record (gen_round_0 holds dashboard, hierarchy, tests, groups,
  grpinfo and asserts). The analysis says it read the out-tree, which is honest; the record should retain modlist.txt and modinfo.txt (gzipped, as the
  exclusion files are) so the analysis re-derives from the repository alone.
- L-5 (section 1, the exclusion-adjusted row): the row is presented with the caveat that its strict load is the author's own and the Runtime Manager's
  independent re-load is owed; keep that caveat beside the row wherever the row is quoted, including in section 5 where the adjusted row is called "what
  the same merge reads with pass 14's file" without the caveat.

### Informational

- I-1: the "configuration, not stimulus" class for the five dummy-instruction assertions rests on the feature never being enabled in the round; gen_asserts.txt
  supports it in its columns rather than by absent attempts: every uncovered assertion shows ATTEMPTS 5408327 (one per cycle of the merge), REAL SUCCESSES 0
  and INCOMPLETE 0, except NextStateCheck_A with INCOMPLETE 36; the analysis's "no attempts that could succeed" is right in substance and should quote the
  columns (attempted every cycle, never satisfied) so the owner does not read "no attempts" literally; gen_grpinfo.txt's gen_sec_ctrl_inputs_cg
  cp_dummy_en shows one of its two bins hit, consistent with the enable never being set.
- I-2: section 4b's plan-credit figures are mine and are labelled as a probe with my heading argument; when the DV Lead regenerates the credit report at
  the round's commit the figures become the record's and the section should cite that file instead.
- I-3: row 3's "n/a" for ibex_cheriot_ex is right after pass 14 (531 of the 1424 entries carve the CHERIoT paths out by owner ruling); the sentence in
  section 5 that "most of ibex_cheriot_ex's 2211 missed objects are ruled out of scope" is a claim about entries, and the analysis itself says entries
  are not impact; the carve-out's object count per metric is in the README's pass-14 table if the owner wants it.

## 3. Verdict

CRITIC VERDICT: APPROVE on dv/auto_dv/evidence/gen_round_0_coverage_analysis.md at b176587: the numbers are the record's, every one carries its scope, the group
gate is not claimed, and the gaps are classified by cause with the reachability stated honestly except for the PMP row (L-1), which names a target a
standing rule blocks until covergroups are built. Rows CR-41 L-1..L-5, all Low, for the DV Lead's next touch; L-1 before the owner reads the ranked list
if the schedule allows. The pause follows this verdict.
