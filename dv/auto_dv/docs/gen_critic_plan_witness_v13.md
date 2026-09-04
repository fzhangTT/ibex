# Critic plan witness v13: the plan set at 9fdef64 (plan commits since 624fdea: 3240963 v3b, 9596727 T-249, a1fd231 v3c, 252ec36 v3d, 9506119 v3e, 9fdef64 v3f)

Base verdict re-reviewed here: gen_critic_plan_witness_v12.md (54f2516a5090c81c, REQUEST-CHANGES on M-1) M-1, L-1..L-9, I-1..I-3.

Artifacts reviewed (committed blobs at 9fdef64; sha256 first 16 hex):

- dv/auto_dv/docs/gen_test_plan.md  2c45c934947c2586
- dv/auto_dv/docs/gen_fcov_plan.md  182da8e6f05fa06b
- dv/auto_dv/docs/gen_feature_list.md  b0517807605c0aef
- dv/auto_dv/docs/gen_trace_tp_bin.csv  4168125e50331105
- dv/auto_dv/docs/gen_trace_witness_ids.csv  fef8b72324452b71
- dv/auto_dv/docs/gen_bug_log.md  4432529347328422
- dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md  59f6f4900fff084b
- dv/auto_dv/evidence/gen_round0_credit/gen_round0_credit.md  75ff6d454c07f8bf
- dv/auto_dv/evidence/gen_round0_credit/gen_round0_credit.csv  e17bc5bd3259e30a
- dv/auto_dv/evidence/gen_round0_credit/gen_round0_credit_summary.md  bd77b20d3c39de0f
- dv/auto_dv/evidence/gen_round0_promotion_table.md  5dba231ba424d0db
- dv/auto_dv/evidence/gen_round0_covergroup_set.md  629fa1a5907f180b
- dv/auto_dv/evidence/gen_round0_covergroup_set.csv  ea5957cf4f5d4ded
- dv/auto_dv/tools/gen_round_credit.py  c49582c2a17e6548
- dv/auto_dv/tools/gen_plan_holds.py  dd4987fe407ddc5e
- dv/auto_dv/flow/gen_testlist.yaml  87ed798c77d2bba0
- dv/auto_dv/fcov_expectations/gen_test_csr_access.fcov.yaml  20499a7dcb9b1d12
- dv/auto_dv/fcov_expectations/gen_test_csr_reset.fcov.yaml  e8b5e0358d3e2aa9
- dv/auto_dv/fcov_expectations/gen_test_csr_trap_setup.fcov.yaml  e3cb6a2392f8144e
- dv/auto_dv/fcov_expectations/gen_test_pmp_csr_warl.fcov.yaml  5db25507653f86ca
- dv/auto_dv/fcov_expectations/gen_test_pmp_lock.fcov.yaml  99d698867df766d2
- dv/auto_dv/fcov_expectations/gen_test_pmp_mseccfg.fcov.yaml  acbdd63ac1cea333

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411, LOG-051, LOG-055,
LOG-074, DV_prompt.txt Section 9 (crediting), rtl/ibex_cs_registers.sv:377-391 and :452 (misa), rtl/ibex_id_stage.sv:1059-1062 and :1117-1118 (the retired hazard path).
Method: detached git worktree of 9fdef64 (the crediting tool digests its inputs from the tree and the flow self-test reads history). The three
generated artifacts were regenerated with the invocations their headers print (gen_round_credit.py with the byte-for-byte line, gen_promotion_table.py
and gen_covergroup_set.py --plan-sha v3f-on-1fc4ffa): the worktree stayed clean, so every committed generated file is byte-identical to a fresh render;
gen_round_credit.py --self-test 5 of 5 including the two new carve-out cases; gen_plan_holds.carveout_items on the plan returns the two Section 1.8 rows
and no hold section; the promotion table's input shas 2c45c934947c / 87ed798c77d2 recomputed equal; the credit digest 1118ca7a5769 and the covergroup
set digest df988df592b6 recomputed equal by the audit subagent. One unnamed subagent (trace and response-row audit over the worktree, told the fence, kept out
of dv/auto_dv/reviews/), its residuals re-checked by me in the blobs. EXPOSURE: the Orchestrator's target message carried no artifact content; the git log
subjects of the plan review artifacts name their levels; the T-235 statements in v3e / v3f cite the CM123 artifact's two majors, whose content I read for
gen_critic_tb_l9.md's reconciliation after finding the same two defects from the RTL (tb_l9 M-1 / M-2), so their agreement here is not adopted from the
artifact. The plan review artifacts for these six commits were not read before Sections 1-5; Section 6 reconciles.

CRITIC VERDICT: APPROVE. The v12 medium is closed by a machine-readable carve-out record the crediting tool reads and applies, proven by self-test and
by regeneration; the nine lows are closed with the residuals below, all lows; the plan's statements about the tree hold, with one state written two
ways inside one group and carve-out prose that lags the lift.

## 1. Honesty against the tree (LOG-055)

| statement class | checked | result |
|---|---|---|
| T-183 lift (v3d, LOG-074) | the T-137 LIFTED record (gen_test_plan.md:173) credits the twelve items and TP-IRQ-073 / 075 from the next measured regression, keeps TP-IRQ-079 / TP-SEC-025 COUNTED ONLY until the NMI-pre-empted fix, and records the spanning-load gate gap (CM117-M-1, tb_l7 L-1) as owed by tb-infra | consistent with LOG-074 and with gen_critic_tb_l7.md; the item-level prose lags (L-1) |
| T-235 as built (v3e, v3f) | the Section 0a gen_isa_compare row and eleven gen_pmc_ctrl Pass criteria say BUILT by tb-infra at 158f5be, cite the two write-corner defects (the written half inferred from the value at gen_isa_shim.cc:238-240; the gap rule after an uncounted writer, rtl/ibex_id_stage.sv:1213-1216), say the group runs unmeasured and uncounted until the fix and the review, and "the Critic has not witnessed it" | true of the tree at 158f5be and equal to tb_l9 M-1 / M-2 found independently; "not witnessed" is one commit stale (I-1); three items in the group still say NOT BUILT (L-2) |
| gen_chk_csr_readback UNBUILT | the eight T-249 Sample lines and the three v3c lines attribute the comparison to the lock-step comparator's isa_rd row until the checker is built; the eleven bin-note phrases are covered by the Section 0 bullet; TP-PMC-022 / 032 and nine more items carry the marker | conforming; the bullet's list (nine bin notes and the CG-IRQ-013 preamble) checked: the CG-IRQ-013 block carries the one mention it says |
| the T-249 manifests (9596727) | six manifests: bins identical as sets and in order (80 / 68 / 168 / 266 / 50 / 77), 239 anti_vacuity strings rewritten, every declared bin in gen_trace_tp_bin.csv, no string names the checker as built | conforming |
| tier rule (v12 I-1) | gen_testlist.yaml lists gen_test_pmp_mseccfg and gen_test_pmp_lock at targeted (:1426, :1476); the promotion table shows no "TESTLIST SAYS" flag | LOG-069 fix landed; closed |
| B4-R1, path B, WP-10 / WP-11 | cr_insn_equal.cm_mvsa01_yes "measured by no committed test" (gen_fcov_plan.md:756); the three wrap bins "measured by nothing until gen_isa_lui_auipc_cg renders" (gen_test_plan.md:962); WP-10 NOT BUILT with the record-time deviation; WP-11 NOT BUILT, the mid-run bins owned by an unbuilt group and declared by no manifest | conforming |
| misa legal / illegal (tb_l5 L-4) | the two CSV rows removed (252ec36), the ignore clause in gen_fcov_plan.md:1239 with the RTL anchors (:452, :377-391 verified), the rendered covergroup still carries the bins (response :571: tb-infra follows) | conforming, pending tb-infra |
| Slice A inputs (v3f) | 1371 declared / 3 ignore_bins recomputed over the five Part 3.1 areas (ISA 349, MUL 149, CMP 354, BIT 447, BTALU 72); the retired popret_ra_fwd note with rtl/ibex_id_stage.sv:1059-1062 and :1117-1118 (verified); the = expression form on CG-RST-001 | conforming; the "ISA area" label of the subject and the response row is the five-area count (L-3) |

## 2. Generated evidence, crediting and holds

- Regenerations identical (Method). Headers: promotion table inputs 2c45c934947c / 87ed798c77d2 (the 9fdef64 plan and testlist, the label
  v3f-on-1fc4ffa declared a label only); credit digest 1118ca7a5769; covergroup set df988df592b6; "carve-out rows read 2 (0 hosted in this round)".
- Credit: 162 items hosted, credited 0, uncredited 0, counted-only 0, held 0, 162 NOT-RUN-CLEAN; the new columns exist and are zero because
  neither carved item is hosted by a round-0 test. Rule sentence (gen_test_plan.md:206-209) names Section 1.8 as the record gen_plan_holds.py
  reads and gen_round_credit.py applies, "the two tags being report states only, and the lift is a hand step" with an owner.
- Trace: 1205 TP headings = 1205 CSV items, 207 covergroups all in the fcov plan, CG-IRQ-012 RETIRED with no bins by design; witness ids unchanged.

## 3. Closure of gen_critic_plan_witness_v12.md

- M-1 CLOSED: Section 1.8 is a table the tool parses (CARVE_HDR / CARVE_ROW, gen_plan_holds.py:22-35), gen_round_credit.py applies UNCREDITED
  (never credits) and COUNTED-ONLY (counts without crediting) with a self-test case for each tag and a load_plan wiring case (5 of 5 pass); the
  digest covers the record; the rule sentence is corrected; the hand step of the lift has an owner. v3c generated 16 rows, v3d removed 14 on
  LOG-074, 2 remain, equal to the LIFTED record's prose.
- L-1 CLOSED (gen_bug_log.md:102 corrected; "71-entry testlist" at 3240963). L-2 CLOSED (HINT "since landing 4, already at f660470"; mtvec low
  without a landing-6 attribution; the seven remaining "built in landing 6" attributions are the rd = x0 guards and cp_mcen_gate, correct).
  L-3 CLOSED in the plan (8ddd7f6; three historical markers), one response residual (L-3 below). L-4 CLOSED (gen_fcov_plan.md:756). L-5 CLOSED
  (:1220 "when it is itself a write, reopens"). L-6 CLOSED (the eleven Pass criteria carry UNBUILT). L-7 CLOSED in substance (gen_test_plan.md:962;
  the row's attribution imprecise, L-3). L-8 CLOSED (response :495, WP-10 row, gen_fcov_plan.md:1235, the knob value 2). L-9 CLOSED (csr_trap_setup
  among the six). I-1 CLOSED (tiers). I-2, I-3 stand.

## 4. Findings

### L-1 (low) [S4 record] Carve-out prose that lags LOG-074

The record and the LIFTED record are right; five places still describe the pre-lift state: TP-IRQ-073 / 075 Notes "COUNTED ONLY until T-183 (2c)
lands" (gen_test_plan.md:8895, :8924); the Section 0a gen_isa_compare row's "items resting on it stay uncredited (the twelve)" and "the
NMI-pre-empted rule writes intr into the shared record until 2c" (:238; 2c moved the flag off the shared record and the fix's red is still owed,
so the carve-out outlives 2c, as :173 says); the "Integrity runs are consistency-only until then" Notes of TP-DMEM-039 / 041 / 064 and TP-RVFI-024
(:16020, :16060, :16562, :21595); the Section 0 comparator paragraph (:160-165) in its 2a-era wording without a re-date. Nothing is credited
yet, so no figure is wrong today; a reader of 0a is told the opposite of the record.

### L-2 (low) [S4 consistency] One group's as-built state written two ways

12 lines say the T-235 shim gaps are "BUILT by tb-infra at 158f5be" (the 0a row and eleven gen_pmc_ctrl Pass criteria); 3 gen_pmc_ctrl Notes
(TP-PMC-023 :13409, TP-PMC-025 :13447, TP-PMC-056 :14036) still say "T-235 shim gaps (NOT BUILT; listed in TP-PMC-022 and Section 0a)". Make
the three Notes point at the Pass-criteria statement.

### L-3 (low) [S4 record] Response-file and label residuals

gen_critic_response_plan_set_v1.md:484 (CM84-L-1) still reads "revised through 1bccc58" without the historical marker the other three rows got
(v12 L-3); :560 says the CM92-M-1 row carries the "measured by nothing" sentence, which is in TP-ISA-006's Notes and in row 560 itself; :584 places
the WP table in "Section 0" (it is Section 2a, as TP-PMC-057 says); the v3f subject and row :582 call the 1371 / 3 count "the ISA area" where the
Part 3.1 count spans five areas.

### L-4 (low) [S4 figures] Figures without a committed artifact

Response :512 "17 TP-IC items stay marked coverage-only" (the plan has 57 TP-IC headings and no marking that yields 17); :580 the gen_pmc_ctrl joint
landing row's "204 declared bins", "13 handed files", "four checks PASS", "18 of 18 manifests" and digest for a manifest that is not in the tree
(held out by design). Say the figures are the Test Writer's unretained delivery, or retain the manifest render they describe.

### Informational

- I-1: the T-235 statements say "the Critic has not witnessed it"; gen_critic_tb_l9.md at d5134d1 (REQUEST-CHANGES on the same two corners) is
  the witness now. Cite it in the next touch; the statements' substance stands.
- I-2: TP-CSR-021's misa legal / illegal bins left the CSV while gen_fcov_groups.svh:2947-2948 still renders them; response :571 assigns the
  removal to tb-infra's next landing. Consistent, pending.
- I-3: WP-11 (mid-run reset regime) is a new NOT BUILT request whose bins are owned, undeclared and not ignored: the honest form.

## 5. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S4 honesty: crediting is machine-applied from a record the plan carries and the
tool digests (conforming); the as-built statements true of the tree (conforming); stale item prose (L-1, L-2). S6: the crediting tool's new
paths have self-test cases (conforming). One-line verdict: PASS with the lows.

CRITIC VERDICT: APPROVE. Lows L-1..L-4 to the DV Lead's next plan touch, with I-1's citation.

## 6. Reconciliation with the six plan review artifacts (read after Sections 1-5 were written)

dv/auto_dv/reviews/2026-09-03-claude-diff-986771a5-32409636.md (v3b), -94629025-95967273.md (T-249), -e931e2a3-a1fd231b.md (v3c),
-b72e0c2d-252ec36d.md (v3d), -d9f66c64-9506119e.md (v3e), -1fc4ffa2-9fdef648.md (v3f): all six APPROVE-WITH-CHANGES. Their items were judged
against the tree at 9fdef64, where most of the earlier ones are already fixed by the later commits:

- Closed by later commits, verified here: the wrong "landing 4, f660470" sha (now "landing 4, 5b8a0fb, and already at f660470"); the T-249 row's
  future tense and the CM102-M-1 row's HINT clause (:518, :522 rewritten); the three further Sample lines CG-CSR-015 / CG-PRV-002 / CG-PRV-007
  and the three present-tense definitions (all in the L5R-3 form now); the CG-CSR-004 consistency-compare qualifier (the v3c bullet and the cp_fam
  line); the CM96-I-1 status; the T-136 record's pointer to Section 1.8 (:171); the credit header's parenthetical now names the carve-out
  sections and rows; the rule sentence names the tags as report states and the lift as a hand step with an owner; the fifth self-test case and
  the "carve-out rows read" count in the header; the "review CM123 is running" clause (now "is APPROVE-WITH-CHANGES with two write-corner
  majors owed"); the tb_l6:225 corrigendum (gen_critic_tb_l7.md's header).
- Adopted and verified, added to L-3 / L-4: the v3f medium in part: gen_trace_tp_bin.csv:23579 traces CG-RST-001.cp_reset_kind.mid_run to
  TP-RVFI-036 (Test group gen_rst_boot) as well as to TP-RST-017, so "the mid_run bins belong to gen_rst_midrun_reset, a group with no test" is
  incomplete; the promoted gen_test_rst_boot manifest declares no mid_run bin (0 matches), so "declared by no promoted manifest" holds and
  TP-RVFI-036 cannot credit until a mid-run reset exists, which the plan should say (Low here: the record is honest, the sentence incomplete);
  WP-11 and the cp_reset_kind note cite TP-RST-017 / 018 / 019 while only TP-RST-017 traces CG-RST-001 bins (5 / 0 / 0, verified); the v3f
  subject's "the covergroup set CSV changed with the retired bin" where the 30 changed CSV lines are line-anchor shifts and the CG-CMP-009 row is
  unchanged (verified); the 0a row maps both write corners onto "(gap 3)" while its own sizing list separates the low-write carry corner (verified);
  the CM116-L-2 row's claim that gen_test_csr_access quotes both the CG-CSR-003 and CG-CSR-004 anti-vacuity strings is false for CG-CSR-004
  (no manifest names it, 0 matches; the row at :567 still carries the sentence (verified)); the "six gen_pmc_ctrl programs all contain the M-1 case" statement (response :585) is unverifiable from
  the tree, the class of my L-4.
- Routed, not this file's: gen_component_api_fcov.md:198's stale misa sentence (tb-infra, with the gen_fcov_groups.svh:2947-2948 follow-up);
  tb-infra's CR-4-L-6 row.
- Not in the artifacts: L-1 (the carve-out prose lagging LOG-074 in the item Notes and the 0a row), L-2 (the three NOT BUILT Notes), the :484
  and :560 residuals, I-1.
- Verdict levels agree: no medium open on the plan set; the artifacts' changes and my lows are the same next touch. The v3f medium is held at Low
  here for the reason given.
