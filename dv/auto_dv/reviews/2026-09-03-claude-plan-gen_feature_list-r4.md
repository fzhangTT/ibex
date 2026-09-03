# Cross-model review - plan/spec file(s): dv/auto_dv/docs/gen_feature_list.md dv/auto_dv/docs/gen_test_plan.md dv/auto_dv/docs/gen_fcov_plan.md dv/auto_dv/docs/gen_bug_log.md

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 8344c9dd-1569-42c0-a3ab-e0e7ad7e2ee3; sandbox: bubblewrap, filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Date:** 2026-09-03
**Target:** plan/spec file(s): dv/auto_dv/docs/gen_feature_list.md dv/auto_dv/docs/gen_test_plan.md dv/auto_dv/docs/gen_fcov_plan.md dv/auto_dv/docs/gen_bug_log.md (echo at raw line 1)

---

TARGET: dv/auto_dv/docs/gen_feature_list.md@e0fb716d
TARGET: dv/auto_dv/docs/gen_test_plan.md@16b8e465
TARGET: dv/auto_dv/docs/gen_fcov_plan.md@a757ab81
TARGET: dv/auto_dv/docs/gen_bug_log.md@be28fd9d

Reviewer identity: Claude Fable 5.1 (claude-fable-5-1), Claude Agent SDK session, fresh session, default reasoning, read-only; codex not used (owner ruling A-001 fallback, as in rounds 1 to 3). Review target: plan set v2c at efe1c91, scoped to the two round-3 mediums and the eight lows of dv/auto_dv/reviews/2026-09-03-claude-plan-gen_feature_list-r3.md, answered by Section 6 (CM-r3) of dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md. The four TARGET hashes are the sha256 prefixes of the efe1c91 blobs; I extracted those blobs and every line number below refers to them. The branch advanced during the review (efe1c91 to 2ca9deb: v2d in 0dcd796 and 0d27718, a Critic verdict, an intervention-log entry). Those commits are not reviewed here. The exclusion file dv/auto_dv/excl/gen_exclusions.el is unchanged since 9ebf2d9 (md5 9b642ef57393d8b3af8de9485a8f6f88 reproduced).

Method. Ran `python3 dv/auto_dv/tools/gen_trace_check.py` myself: features 1017 (ACTIVE 705, ALIAS 122, FOLDED 190); TP items 1203; covergroups 207; bins referenced 15825 (adopted 49, spec-derived 15776); ACTIVE->TP 705/705, ACTIVE->bin 705/705, bins->feature 207/207, CSV bins declared 15825/15825; coverpoints 2278, owned 2204, regression-level 74; PASS, exit 0. Matches the commit message. Own derivations over the pinned test plan: 1203 items, 1092 Phase 1, 29 expected-fail, 11 informational, 226 distinct test groups, 0 groups mixing kinds, 0 `_info` groups holding a pass item, 2 items with `Knobs: none` (both `none (elaboration-only: ...)`), 220 items whose Fire-check carries a `[cycle-level clause: ...]` (191 of them Phase 1), all 220 with an `RVFI-only fallback:` sub-clause. Parsed the .el into 492 annotation groups and 1421 entries (186 Block, 83 Branch, 667 Condition, 463 Toggle, 2 Fsm, 5 State, 12 Transition, 3 Assert; 487 class T, 2 class P, 3 class D; 41 (module, metric) scopes over 13 modules) and queried it per table row.

## 1. Medium 1: F-CHERI-001 versus gen_exclusions.el at 9ebf2d9

Verdict on the row-for-row claim: holds for every row I sampled (31 rows) and for every aggregate in the closing note.

Rows checked against the file (row: claim -> .el evidence):
- 8: `MODULE ibex_core Branch 3` on the :1000 select plus A.4 vectors -> Branch 3 `(instr_valid_id & instr_is_cheriot_id)` (.el:1265), Conditions 82/83 (.el:1287, :1290).
- 17: `Block 60 rvfi_mem_rdata_d = rf_wdata_lsu;` -> present (.el:1259).
- 23: no Branch object for if_stage :222-228, A.4 vectors only -> if_stage has 0 Branch entries; Conditions 1, 4, 5 on :222/:225.
- 24 and 31: no scope for ibex_prefetch_buffer / ibex_fetch_fifo -> neither module appears among the 13 MODULE scopes.
- 35 and 37: id_stage single Branch (Branch 5, :578); :747 two Condition groups (38, 40), no Branch for :746-749 -> confirmed; id_stage holds exactly 1 Branch.
- 38: Blocks 62 / 64 `id_fsm_d = MULTI_CYCLE;` -> present (.el:1899).
- 47: decoder Branch 7 / 8 / 9 -> present (.el:1751).
- 50, 56: decoder :351, :824, :856, :873 `illegal_insn = 1'b1` NOT in the file (carve-back) -> 0 groups name those lines.
- 54: :778 Condition 47 present; no Toggle for csr_cheriot_always_ok_o; decoder Toggle count 38 -> confirmed (38 Toggle entries in ibex_decoder).
- 61: 11 Blocks and 10 Condition vectors in the compressed decoder -> Block 11, Condition 10 (plus the one Toggle of row 60).
- 65, 80: LSU Branch 0 (:131), Branch 4 / 5 (:702-709) -> present (.el:2094, :2219-2227).
- 73, 74: Fsm ls_fsm_cs with 3 CTX states and 7 transitions, cap_rx_fsm_q with 2 states and 5 transitions -> Fsm 2, State 5, Transition 12 (.el:2277, :2290).
- 85: cheriot_ex 75 Block / 66 Branch / 246 Condition / 144 Toggle in 218 groups -> exact.
- 97, 99: wb Branch 1 / 2 in one group for :182/:183/:215 -> present (.el:2439).
- 107: 3 Blocks `*_err_prio = 1'b1;` -> Blocks 9, 19, 21 (cheriot_wb/ex/asr_err_prio).
- 115, 116: controller :850/:854 groups present; :866/:868 two Condition groups, no Branch -> controller has 0 Branch entries.
- 128: Blocks 21 / 24 `illegal_csr = 1'b1;`, :473 / :482 live -> both Blocks present; 0 groups name :473 or :482 (README 5b lists them live).
- 129: no Block for :510-512 / :519-521, only A.4 vectors of the :504 / :516 guards -> four Condition groups (15, 18, 20, 23), no Block.
- 130: Blocks 75 / 78 / 81 `csr_rdata_int = mshwm_q / mshwmb_q / cdbg_ctrl_q;`, :682/:690/:698 live -> present; 0 groups name :682/:690/:698 (README 5b).
- 131: Block 86 -> present.
- 146: SCR read mux :2014-2056 live, Toggle covers cheriot_csr_rdata_o -> 0 groups in that range; Toggle group at .el:1625 names cheriot_csr_rdata_o (README 5b).
- 148, 150: Block 277 `pcc_cap_q <= pcc_cap_d;` plus 10 update-arm Blocks; reset arms :2114/:2136/:2155/:2170/:2185/:2203 live -> Blocks 294, 304, 308, 313, 318, 323, 325, 330, 332 and 337 present (with 277 and the six above that is exactly the 17 cs_registers Blocks); 0 groups name the reset lines.
- 151: mstack_epc_cap_q has no entry -> 0 matches for `mstack` anywhere in the file (README 5b, Critic CR-M-1).
- 156, 160: one RF Branch (Branch 0 `g_cheriot_rf.cheriot_enabled`) whose annotation names both :113 and :227-230; RF Condition vectors 67 / 70 / 74 removed -> confirmed (.el:2309); no Condition 67, 70 or 74 exists in the RF scope.
- 157: :136-137 Condition vectors -> 16 groups.
- 161: 3 Asserts -> present (.el:2431).
- 166, 167: class P Block 67 `nt_branch_mispredict_o = 1'b1;`, decoder Blocks 414 / 417 (ALU_BDECOMPRESS / ALU_BCOMPRESS) -> present with `Class P` annotations.
- 169: class D 2b default arms (controller :990-993, LSU :605-607, multdiv :522-524) HELD OUT -> 0 groups name those lines; .el header line 5 and README section 2 say held out; README section 7 gives the fill procedure.
- 170: class D 2a Blocks id_stage 83, multdiv 11, icache 265 -> present, each with a `Class D (enum default arm, no spare encoding)` annotation.
- 176: four glitch-covered tie conditions -> cheriot_ex :970 two groups (.el:820, :823), cs_registers :377 two groups (.el:1526, :1529), :1020 two groups (.el:1532, :1535), core :1343 (.el:1294).

Closing-note aggregates (gen_feature_list.md:13604-13617): A.3 Blocks / Branch per module core 1/7, id_stage 2/1, decoder 36/3, compressed_decoder 11/0, controller 14/0, LSU 24/3, cs_registers 17/0, wb 0/2, RF 0/1 (105 Blocks, 17 Branch) reproduce from my per-module census after subtracting the 2 class P and 3 class D Blocks; A.4 = 667 - 246 = 421; A.5 = 319 shared + 144 cheriot_ex = 463; 41 scopes; 492 groups (487/2/3). The README section 4 "10 entries dropped" versus the generated COUNTS "0" is a real inconsistency in the README, correctly flagged for rtl-arch in the response row.

Residuals (findings below): gen_feature_list.md:81 still names dv/auto_dv/work/rtl-arch/gen_exclusions_draft.md as "the authoritative exclusion list" (the r3 medium asked for the .el to be the single named authority); the Source field at :13346 has a parenthetical spliced into the README filename; :37 still says B1..B15.

## 2. Medium 2: Section 0 rule for cycle-level fire-checks

Rule (gen_test_plan.md:43-50): cycle-level fire-checks depend on the bus/pin event export as a Phase-1 prerequisite; until it lands an item is implemented against its RVFI-only fallback and the cycle-level clause is marked; dropping the clause without the marker fails acceptance item 5.

Soundness. The rule closes the silent-weakening hole the r3 review named: the fallback is now written per item, and the marker is a visible debt. All 220 marked items carry a fallback sub-clause. Fallback facts reference only exported record fields: the rvfi_ext_* names used (mcycle 60 items, debug_req 11, nmi_int 9, nmi 8, pre_mip 6, debug_mode 4, post_mip 2, rf_wr_suppress 2, expanded_insn_last 1, mhpmcounters 1) are all ibex_core ports and all appear in the addendum's R-line field list (`ext_exp_last`, `ext_mcycle`, the counter words under the counters knob).

Path to a green Phase 1 without the cycle-level facts: yes, one exists. The rule says the export is a Phase-1 prerequisite, but nothing requires a marked test to be upgraded once its source lands, no artefact counts marked tests, and the fcov manifest is SV-side so no bin depends on the Python clause. A Test Writer can ship all 191 Phase-1 marked items on fallback, the export can land, and Phase 1 can be signed off with no cycle-level fact ever asserted. The addendum's own build order (Section 8: bus events in step 2, pin/alert/misc/regime in step 3) gives the natural sunset per source; the plan does not use it.

Event-name consistency with addendum v4 Section 8. The fallbacks are RVFI-only and name no events, so they are consistent by construction. The cycle-level clauses themselves are not fully covered by the v4 table: 26 marked items assert irq_pending_o in a named cycle (TP-CSR-029 :4429, TP-CSR-031 :4457, TP-PRV-018 :5957, TP-PRV-019 :5971, TP-IRQ-011 :7701, TP-DBG-003 :10624, TP-TRG-025, the XIF items and 16 more) and 33 assert an instruction or data request cycle or its absence (TP-PMP-082 :9972 "zero data_req_o", TP-REG-012 :22621 "every instr_req_o inside an Off window", TP-IMEM-039 :15018 "instr_req_o sampled high in the same cycle", TP-EXC-037/038, TP-IRQ-049/051/052, 11 IMEM, 8 DMEM, 3 FE, 4 IC items). The v4 table has no misc `irq_pending` row and no bus `req` row (only `gnt` and `rvalid`), so these clauses cannot be built from the export as designed even after it lands. Also the plan names the knob `+gen_bus_export` (221 occurrences) while v4 renamed the family to `+gen_export_file` / `+gen_export_sources` and names the lines `E`; at efe1c91 the committed addendum is v3a (no Event channel section) and v4 existed only as an uncommitted working-tree edit, so the rule cites a design not yet in the tree.

Sampled fallbacks (pinned lines). Sound: TP-ISA-024 :934, TP-MUL-024 :1735, TP-BTALU-018 :3710 (mcycle gap from the access record plus the counter delta), TP-CSR-034 :4499 (pre/post_mip versus rd_wdata), TP-PRV-018 :5957, TP-EXC-062 :7377 (one handler-first record per trap; distances honestly "coverage-only"), TP-IRQ-039 :8093, TP-IRQ-044 :8163 (C-7 record count between the suppressed load and the nmi_int entry, read-backs), TP-PMP-082 :9972, TP-DBG-003 :10624, TP-DBG-021 :11036, TP-TRG-026 :12587, TP-PMC-058 :13826, TP-DMEM-064 :16402, TP-FE-022 :16871 ("the bypass fact stays coverage-only"), TP-REG-001 :22463, TP-REG-012 :22617. Vacuous or count-only: TP-IMEM-006 :14295 and TP-DMEM-007 :15185 ("no rvfi_trap and no nmi_int over the run": a pure negative that cannot show the non-rvalid garbage was driven), TP-IC-045 :17877 ("gen_chk_icache zero-violation count and records retiring with rvfi_insn == image over the run": nothing evidences a port collision), TP-DMEM-051 :16096 (computes the modelled addr_last but compares it with nothing), TP-PMP-077 :9902 (negative only; the prefetched denied word is invisible to RVFI), TP-IC-003 :17054 ("each hit" is not identifiable from RVFI without the shadow model), and the zero-violation halves of TP-IMEM-039 :15018 and TP-CSR-100 :5423. These should be labelled coverage-only outright rather than presented as fallbacks.

Counts: Section 0 :50 says "216 items after v2c" and the response row CM-r3-M2 gives csr 8, mem 75, dbg 35, pmp 5, isa 14, xcut 27, exc_irq 52; the file carries 220 (mem 79, the other six as stated), which is also the commit message's number. The rule's literal marker `coverage-only until the bus/pin event export lands` (:48) occurs in no item; every item carries the longer form with the knob parenthesis inside it, so a mechanical check for the literal finds zero marked items.

## 3. Lows

- CM-r3-L1 informational: FIXED. Section 1 rows "Informational items 11" and "Items outside the Phase 1 pass gate 40" (:107-108); Section 1.2 (:133-146) lists the 11 IDs with group and reason class; my census finds the same 11 and 29 expected-fail.
- CM-r3-L2 gen_csr_machine_ids: FIXED. Six occurrences, zero of the old `_info` name; no `_info` group holds a pass item.
- CM-r3-L3 knobs: FIXED. Only TP-SEC-037 :20109 and TP-RST-020 :20703 carry `Knobs: none`, both in the `none (elaboration-only: ...)` form; the exception sentence is in the pmp (:8806), dbg (:10465), mem (:14050) and sec (:18293) headers.
- CM-r3-L4 fcov gate: FIXED. Section 1 opens with the gate sentence (gen_fcov_plan.md:74-75); the xcut heading :6856 reads "adopted".
- CM-r3-L5 fast[15]: FIXED. CG-FE-001.cp_irq_vec_id declares `fast[15]{[16:30]}` (:4494); the efe1c91 CSV has 19 cp_irq_vec_id rows in `fast[N]` form and 0 in `fast_N` form; the 27 remaining `fast_N_*` CSV rows are named cross bins.
- CM-r3-L6 bug log: FIXED in the bug log (B17 Features F-PMC-053/039/043/044 :171; B19 F-RVFI-025 + F-ISA-034 :192; B9 note record-only :221; B6/B9/B12 under Section 1b :200; v1g change-log :277). The feature-list half (:37 "B1..B15") is not done.
- CM-r3-L7 B-versus-D criterion: stated (gen_bug_log.md:15-21) and cited from D6, D20, D21, B17, B7, B16. It does not separate B11 from D6: B11 (mhpmcounter9 counts not-taken branches under DIT) is a timing-independent count convention, which the paragraph's own D clause covers, and B11's Notes (:120) rest on "treated as a counter bug candidate" without citing the criterion; the B clause "violates a documented functional intent" would apply equally to D6.
- CM-r3-L8 C-15: FIXED. :51-54 says checkers stay ON, verdicts recorded, `measured: false`; consistent with TP-ISA-057 :1397.

## 4. Rubrics (Zone A set, diff_only)

The four files are markdown under dv/auto_dv/docs/ and match no rubric filter; the delta adds no code, code comments, forces, literals in code or assertion changes. ai-slop-comments `{"status": "PASS"}`; rtl-purity `{"status": "PASS"}`; magic-numbers `{"status": "PASS"}`; forces-and-hier-access `{"status": "PASS"}`; assertion-integrity `{"status": "PASS"}`.

## Findings

[medium][dv/auto_dv/docs/gen_test_plan.md:43] The cycle-level rule has no sunset: nothing requires a marked test to implement its cycle-level clause once its event source lands, no artefact counts marked tests, and no manifest bin depends on the clause, so Phase 1 can be signed off with all 191 Phase-1 marked items on their RVFI-only fallback and no cycle-level fact ever asserted. - Add to Section 0: the test template emits one tag per fallback in use (e.g. GEN_FALLBACK <id> <source>), the flow reports the count per run, and Phase-1 sign-off requires zero tags for every source whose writer has landed per the addendum's build order (bus and ctrl events in step 2; pin, alert, misc and regime in step 3); a tag after its source landed fails acceptance item 5.

[medium][dv/auto_dv/docs/gen_test_plan.md:44] The rule makes the addendum v4 event export the Phase-1 prerequisite for the cycle-level clauses, but 26 marked items assert irq_pending_o in a named cycle (TP-CSR-029 :4429, TP-PRV-018 :5957, TP-IRQ-011 :7701, TP-DBG-003 :10624 and 22 more) and 33 assert a bus request cycle or its absence (TP-PMP-082 :9972, TP-REG-012 :22621, TP-IMEM-039 :15018 and 30 more) while the v4 event table (addendum Section 8) has no `irq_pending` row and no `req` row (only gnt and rvalid), so those clauses cannot be built from the export as designed. The plan also names the knob `+gen_bus_export` (221 occurrences) where v4 uses `+gen_export_file` / `+gen_export_sources` and `E` lines, and at efe1c91 the committed addendum is v3a without an event channel. - Ask TB Infra for a `misc irq_pending` row (value on change) and `ibus, dbus req` rows (addr, the cycle req rises and falls) or reformulate the 59 clauses against gnt/rvalid; rename the knob to the v4 name once v4 is committed; cite the committed addendum revision in the rule.

[low][dv/auto_dv/docs/gen_test_plan.md:48] The marker text the rule fixes (`coverage-only until the bus/pin event export lands`) appears in zero items (all 220 carry the form with the knob parenthesis inside), and :50 says 216 marked items (response row: mem 75) while the file has 220 (mem 79). - Make the marker one exact token with the knob outside it, and regenerate the count in Section 0 and the response row.

[low][dv/auto_dv/docs/gen_test_plan.md:14295] Some fallbacks are vacuous as fire evidence: TP-IMEM-006 :14295 and TP-DMEM-007 :15185 (negative only over the run), TP-IC-045 :17877 (zero-violation count plus any retirements), TP-DMEM-051 :16096 (a model with no compare), TP-PMP-077 :9902 (negative only), TP-IC-003 :17054 ("each hit" not identifiable from RVFI), and the zero-violation halves of TP-IMEM-039 :15018 and TP-CSR-100 :5423. - Label these clauses coverage-only outright (as TP-FE-022 and TP-EXC-062 do) instead of claiming a fallback, or add one positive RVFI fact (e.g. the retirement count per non-rvalid-garbage window from the bridge count).

[low][dv/auto_dv/docs/gen_feature_list.md:81] Section 1 still says the F-CHERI-001 table "mirrors dv/auto_dv/work/rtl-arch/gen_exclusions_draft.md, which is the authoritative exclusion list", contradicting the table's own authority statement (:13375-13383: the .el at 9ebf2d9 is what urg loads) and the README header ("mirrors THIS file"); the r3 medium asked for the .el to be the single named authority. - Replace the sentence with "mirrors dv/auto_dv/excl/gen_exclusions.el at 9ebf2d9 row for row; the draft is the file's source, never the authority".

[low][dv/auto_dv/docs/gen_feature_list.md:13346] The Source field splices a parenthetical into the README filename ("gen_exclusions_README (md5 9b642ef5...; Critic verdict APPROVE in draft form ...; rtl-arch sends the delta).md"), attaches the .el's md5 to the README name, and says both "Critic approval of the file pending" and "Critic verdict APPROVE in draft form" in one field. - Rewrite as: the .el (md5 ...) with its README; Critic verdict APPROVE in draft form (gen_critic_exclusions_v3.md:15), F-1 and F-3 open until the first measured regression.

[low][dv/auto_dv/docs/gen_feature_list.md:37] "bug candidates as B1..B15" is stale (the bug log runs B1..B19 with B6/B9/B12 in Section 1b); r3 L6 asked for this and the response row does not cover it. - Update to B1..B19 and mention Section 1b.

[low][dv/auto_dv/docs/gen_bug_log.md:15] The B-versus-D criterion does not separate B11 from D6: B11 (mhpmcounter9 counts not-taken branches under DIT) is a timing-independent count convention, which the D clause covers, and B11's Notes (:120) do not cite the criterion; the B clause "violates a documented functional intent" applies equally to D6. - Either cite the criterion from B11 with the clause that makes it a B (the doc defines the event, so counting a not-taken branch is a wrong count, not a convention) and say why D6 is not the same, or reclassify B11 as a D.

[info][dv/auto_dv/docs/gen_feature_list.md:13375] F-CHERI-001 verified as a row-for-row mirror of the .el at 9ebf2d9 on 31 sampled rows including 169 (class D 2b held out: no entry for controller :990-993, LSU :605-607, multdiv :522-524), 128, 130, 146, 150, 151, 160 (live objects: no entry, README 5b lists them), and all closing-note aggregates (1421 entries, 492 groups, 41 scopes, per-module A.3 counts, 487/2/3 classes). The README section 4 "10 entries dropped" versus COUNTS 0 is correctly flagged for rtl-arch. Trace check PASS reproduced. Rubrics all PASS.

[info] HEAD moved from efe1c91 to 2ca9deb during this review (v2d, a Critic APPROVE, LOG-016a). Commit 0dcd796's message claims to rename the export knobs to the v4 names, cite the mirrored file at 9ebf2d9 with its md5 in F-CHERI-001, and tag 40 marked items for boundary reformulation; none of that is reviewed here and the findings above stand against efe1c91.

Summary. Both round-3 mediums are substantively closed: the F-CHERI-001 table is now the mirror it claims to be, verified row by row against the committed file, and the cycle-level rule with per-item fallbacks removes the silent-weakening path. What remains is that the rule has no sunset and the export it depends on lacks two event rows that 59 of the marked clauses need, plus bookkeeping lows (two unclosed halves of r3 items in the feature list, the 216/220 count, the marker literal, a handful of vacuous fallbacks, and a B-versus-D criterion that does not yet explain B11). None blocks Phase 1 test writing provided the sunset rule and the event-table additions are folded in the next revision.

Final verdict: APPROVE-WITH-CHANGES
