# Critic verdict: plan set v1 (feature list v2, test plan, functional-coverage plan, bug log, traceability) - T-007 part 2

Artifacts under review (committed under dv/auto_dv/docs/ unless stated; sha256 first 16 hex at review time):
- gen_feature_list.md (v2, 12910 lines)                        d924dadf0e80d28e   (commit 7356277)
- gen_test_plan.md (20414 lines)                               2d99607783afb09c   (commit 7356277)
- gen_fcov_plan.md (5469 lines)                                967411cdf07460bd   (commit 7356277)
- gen_bug_log.md                                               b0a8f9b17ea91f53 at 7356277 (217 lines, read first);
                                                               1a31f0f1423e791c at 5d598bb (v1a: B12 and B14 reclassified,
                                                               landed by a4795a7 2026-09-03 03:06:35 -0400 auto_dv: TB architecture document adopted by the DV Lead (TB Infra draft verbatim + rulings: coverage scope = u_ibex_core + u_register_file, -cm_glitch 0 for measured builds; DV Lead notes); bug log v1a; feature-list Critic response promoted to evidence)
- gen_trace_feature_tp.csv (2003 lines)                        cf19ab64e666fac2
- gen_trace_tp_bin.csv (13989 lines)                           8f76a6efbdad4b69
- dv/auto_dv/tools/gen_trace_check.py (53 lines)               56428759533fee7f
- DV Lead response to my v1 (committed): dv/auto_dv/evidence/gen_critic_response_feature_list_v1.md, sha256 fd9712d25e4ff216
  (promoted in a4795a7); the same content was read as dv/auto_dv/work/dv-lead/gen_reading_report.md Section 6b
  (sha256 85f4a8ac2b6ad6a9, gitignored). The response to THIS verdict goes to dv/auto_dv/evidence/ as
  gen_critic_response_plan_set_v1.md (standing rule: verdicts cite committed response paths).
Date: 2026-09-03 (UTC)
Role: Critic (reviewer other than the author: traceability confirmation, checker-direction and anti-vacuity approvals,
DV_prompt.txt Section 4 and dv_principles.md Section 6)
Supersedes: dv/auto_dv/work/critic/gen_critic_feature_list_v1.md (T-007 part 1, REQUEST-CHANGES) and folds in the
advisory dv/auto_dv/work/critic/gen_critic_fcov_drafts_prereview_v1.md (T-034).

CRITIC VERDICT: REQUEST-CHANGES

What stands. The mechanical traceability (completeness rules 1-3) holds: I re-derived it from the CSVs and the three
documents with my own script, independently of gen_trace_check.py, and every relation the DV Lead claims is true
(Section 1). All highs and mediums of my v1 on the feature list are closed or reduced to bookkeeping (Section 2); the
F-CHERI-001 table now agrees with rtl-arch's exclusion draft and even finds three gaps in it (Section 6). The plan set
is a serious, traceable body of work.

What blocks. Two highs and eleven mediums, all of them things a Test Writer or TB Infra would code wrongly tomorrow:
six debug/trigger items and one covergroup still require rvfi_trap = 1 on an ebreak that enters debug mode, which the
RTL never produces, so those fire-checks can never fire (H-1); a quarter of the covergroups, including every regime
group that is supposed to prove the three randomization layers, credit bins without the behaviour they name having
occurred (H-2); seven of the thirty expected-fail items contradict the committed bug log, four pass-marked items follow
the RTL on open bug candidates, thirteen requested checkers exist in no architecture document, and 221 coverpoints
belong to no test-plan item so no run will ever be held to them. One of the remaining feature errors (F-DBG-044) comes
from a premise my own v1 finding C-06 stated wrongly; Section 5 records that.

## 1. Traceability confirmation (my own derivation, dv/auto_dv/tools/gen_trace_check.py re-run in the flow environment)

| Relation | Result | Note |
|---|---|---|
| Features parsed from the list | 1014 = 765 ACTIVE + 95 ALIAS + 154 FOLDED; 0 without a Status field | matches the Section 1 table and the CSV status column (0 mismatches) |
| ACTIVE feature -> at least one TP item | 765/765 | |
| ACTIVE feature -> at least one bin (through its TP items) | 765/765 | |
| TP items in the plan vs CSV | 1181 in the plan; 1181 referenced; 0 unknown, 0 orphan, 0 without bins | |
| Covergroups in the plan vs CSV | 204 = 204; 0 unknown either way | |
| Bins referenced (distinct) | 10234; 55 adopted (Section ADOPT) | every referenced bin traces to a feature through its TP item |
| ALIAS canonical is ACTIVE; FOLDED parent is ACTIVE | 95/95; 154/154 | |
| Section 3.1/3.2 references resolve | 398/398 | v1 C-15 closed |
| Bin tokens present in their covergroup text | 10203/10234 | the 31 misses are fast_N array bins declared as `fast[15]{[16:30]}` (L-1) |
| Plan coverpoints with no CSV row (no TP item declares any bin of them) | 221 of 2185 | PMP 56, EXC 36, CMP 32, BIT 31, ISA 25, MUL 15, IRQ 13, BTALU 10, IMEM 2, REG 1 (M-6) |
| gen_trace_check.py | PASS, same counts | its rule 2 is evaluated at covergroup level (Features field), not per bin |

Confirmation: I confirm rules 1 and 3 of the completeness measure and rule 2 at the granularity the script implements.
Rule 2 as written in gen_fcov_plan.md Section 1 ("every bin maps back to a feature") is satisfied only through the
covergroup's Features line; the 221 coverpoints of M-6 show the gap that granularity hides. The mapping is confirmed;
the plan set is not yet approvable for the reasons in Section 4.

## 2. Closure of the v1 findings on the feature list

| v1 | Sev | Status | Evidence (checked by me or re-verified from the sample) |
|---|---|---|---|
| C-16 six "no" rows sweep live RV32I logic | high | CLOSED | all eight blocks now "yes (live RV32I, never excluded)" or condition-only (rows at 12734, 12761-12764, 12797-12800, 12826-12843, 12858); the 165-row table mirrors the exclusion draft's A.3/A.5/A.6/A.7 and Part C class-T rows |
| C-17 / C-18 / C-19 table verdicts, missing entries, bookkeeping | medium/low | CLOSED | decoder rows split dead arms from live else arms; :707-715, depc/dscratch combi, rvfi_id_done, rvfi_rd_cap_d rows added; 165 rows counted |
| C-02 F-EXC-009 trigger CSRs trap | medium | CLOSED | 4371: M-mode legal, writes dropped, D12 cited; F-DBG-050 canonical, F-CSR-017 alias |
| C-05 six factual errors | medium | CLOSED 6/6 | F-ISA-012 fsri decode, F-MUL-022 rem sign, F-FE-017 three-buffer throttle, F-IC-006 two codewords, F-DIT-025 lockup reload, F-SEC-032 bits 6/7 RW; each re-read against the cited RTL |
| C-06 wrong RTL facts (F-DBG-044/059, F-RST-008) | medium | PARTIAL | F-RST-008 fixed (FIRST_FETCH one cycle); F-DBG-059 and F-DBG-044 wrong for a different reason (M-1, Section 5) |
| C-07 87 observables naming no port | medium | CLOSED | 759/765 name a port, RVFI field or read-back; residual soft cases F-CMP-009 (1299), F-IC-001/046 (port group), F-RST-009/020, F-SEC-036 (elaboration checks) are acceptable |
| C-08 internal nets as observables | low | CLOSED with one phrasing gap | F-CSR-001 (2707) names P6 directly; F-CSR-101, F-SEC-004, F-SEC-011 name internal witnesses without the probe phrase (L-2) |
| C-09 / C-10 uncovered arcs and rules | medium | CLOSED | 15 new features (F-MUL-028, F-CMP-069/070, F-BIT-041, F-IRQ-066, F-DBG-068, F-DIT-030, F-RVFI-034, F-IMEM-031/032, F-DMEM-048..051, F-IC-048) plus the F-IC-022 amendment; RTL spot-checks HIT |
| C-12 edge restatements (23 percent) | medium | PARTIAL | 154 folds done; 53-edge sample still 13 percent clear restatements plus borderline cases (M-9) |
| C-13 edge bookkeeping | low | PARTIAL | 9 edges point at an ALIAS, 24 folds hang on an edge parent, 38 Edge pointers disagree with the fold target (L-3) |
| C-14 about 60 duplicate clusters | medium | PARTIAL | 95 aliases acknowledge all but four clusters; a fresh scan finds about 12 duplicated behaviours across about 25 ACTIVE features (M-10) |
| C-15 Section 3 references | low | CLOSED | 0 unresolved |
| C-20 B6 misclassified | medium | CLOSED | bug log B6 "not a bug"; TP-EXC-046 / TP-DBG-034 expect pass (verified 6637, 10476) |
| C-21 dcsr.ebreaks belongs in 5.1 | medium | CLOSED | B15 in the bug log; TP-CSR-076 / TP-DBG-018 expected-fail; but see M-3 |
| C-22 / C-23 / C-26 | low | CLOSED | B5 cited to core_registers.xml:292-298; D1..D19 single table; counts corrected (one residual: the response says 341 ACTIVE edges, the file says 368, I-1) |
| Citation quality | - | 30/30 HIT in a fresh random sample; v1 had 71 HIT / 13 PARTIAL / 2 MISS in 86 | |

## 3. Fold-in of the T-034 advisory (M-01..M-03, S-1..S-14)

| T-034 | Status in the committed plan set |
|---|---|
| M-01..M-03 document shape, bin syntax, CSV form | DONE: uniform CG blocks, `name{values}` bins, machine-readable CSVs |
| S-1 checker direction | PARTIAL: B6 and dcsr.ebreaks handled in most items; B12/B14 still expected-fail in the plan while the bug log reclassified them (M-2); TP-CSR-074/075/108/066 follow the RTL on B15/B3/B7 (M-3) |
| S-2 rvfi_trap = 0 on ebreak-into-debug | PARTIAL: ISA, EXC, RVFI items and CG-EXC-004 correct; six DBG/TRG items and CG-DBG-003/006 still wrong (H-1) |
| S-3 vacuous sampling | PARTIAL: 175 of 204 groups event-driven with a stated guard; 25 groups still vacuous or near-vacuous, 4 depend on unregistered internal nets (H-2, M-7) |
| S-4 timing-derived bins | DONE in shape (delta, fetch_stall, wb_busy defined per area) |
| S-5 regime bins credited at phase start | NOT DONE for CG-REG-001..007/009/010 (H-2) |
| S-6 layer-1 weights | NOT DONE in the fcov plan (two mentions of "weight" in prose); the test plan carries operand-mix prose per area but no weight table (M-8) |
| S-7 impossible cross combinations | PARTIAL: many ignore clauses added (CG-DMEM-002, CG-ISA-009/011, CG-PRV-004/006 ...); residuals CG-CSR-002 mpp_h_csrrsi, CG-PRV-001 m_m_* under a mode-change-only sample, CG-XIF-004 none_needed_trap_taken, CG-XIF-006 step bins, CG-PMP-001/007/013/014 contradictions (M-7) |
| S-8 literals | PARTIAL: xcut and PMC honour the rule; CSR/PMP/PRV/IRQ/IC groups still enumerate hpm3..hpm12, addr0..15, f0..f14, way0/way1 (L-4) |
| S-9 adoption marks | NOT DONE for the ISA file: it still states "Adopted bins: none ... vendor/google_riscv-dv was not read by this subagent"; at least eight partitions mirror riscv_instr_cover_group.sv unmarked (M-5) |
| S-10 cross-interface crosses | DONE: Section XIF samples monitor-derived state with stated events |
| S-11 completeness measure | PARTIAL: denominator 765 stated; reviewer step reduced to "confirms the mapping"; the 80 percent gate lives only in the 3.8 proposal; per-bin rule 2 not implemented (M-6, L-5) |
| S-12 edges with no item or bin | DONE mechanically (rule 1 holds for every ACTIVE entry) |
| S-13 fire-check quality | NOT DONE: 27 items still use coverage as the fire-check, 14 of them regression-level (M-4) |
| S-14 document shape for the fold-in | DONE |

## 4. Findings

### High

H-1 rvfi_trap on ebreak-into-debug, DBG/TRG area (S-2 residual). RTL: rvfi_trap_id = id_exception & ~(ebrk_insn &
ebreak_into_debug) (rtl/ibex_core.sv:1885-1886), so an ebreak that enters debug mode retires with rvfi_trap = 0. Items
whose fire-check requires rvfi_trap = 1 on that record can never fire: TP-DBG-022 (gen_test_plan.md:10254 "RVFI item
for the ebreak (rvfi_trap==1)"), TP-DBG-027 (:10338 "rvfi_insn[15:0]==16'h9002 and rvfi_trap==1", debug variant),
TP-DBG-028 (:10355), TP-DBG-046 (:10687 "stepped ebreak RVFI item (rvfi_trap)"), TP-DBG-067 (:11080), TP-TRG-020
(:11499; an expected-fail item, so the wrong-reason failure would be masked as XFAIL). Coverage: CG-DBG-003 sample
premise (gen_fcov_plan.md:2640-2641 "both the trap-recorded and the into-debug case carry rvfi_trap") and CG-DBG-006
bin cr_stepped_retired.ebreakdbg_trap (:2726) are unreachable. Required: rewrite the six fire-checks to "ebreak record
with rvfi_trap = 0 and rvfi_ext_debug_mode = 0 followed by the DmHaltAddr fetch / the next record with
rvfi_ext_debug_mode = 1" (as TP-EXC-064:6887 and TP-RVFI-028:18962 already do), fix the CG-DBG-003 premise, remove or
re-target the ebreakdbg_trap bin.

H-2 Vacuous and pre-credited sampling (anti-vacuity duty, dv_principles Section 6; S-3 and S-5 residual). 25 of 204
covergroups credit bins without the named behaviour having occurred. (a) Every regime group is credited at the phase
boundary, not on an event under the regime: CG-REG-001 (:5013 "imem agent phase-log record (TB-side phase start)"),
CG-REG-002/003/004/005 (same pattern; :5076 "this group only proves the regime ran"), CG-REG-006 (:5089 credited at the
region marker store, before any instruction of the mix retires), CG-REG-007 (:5105 banner at time 0), CG-REG-009 (:5370
"condition: MemECC=1 build", a constant), CG-REG-010 (:5383 "condition: always"). These groups are the evidence for
DV_prompt Section 6's three randomization layers; as written they prove the schedule ran, not that the DUT saw the
regime. Required: a regime value or transition bin is credited on the first DUT-visible transaction or event that
completes under that regime (grant/response for the bus agents, a taken or masked interrupt for the irq agent, a
retirement inside the region for the program mix), as CG-PMP-014:2490 already does ("at least one PMP-checked access
retires before the next table change (otherwise the sample is discarded)"); drop the constant-condition group or make
it a property. (b) Tautological conditions: CG-MUL-002 (:348 "condition: a previous retirement exists in the same run"),
CG-MUL-004, CG-BIT-010, CG-BTALU-001 (:862), CG-BTALU-002: state the real guard (fetch_stall == no and wb_busy == no
for the delta bins). (c) Always-true witness bins credited on every sample: CG-CSR-017 cp_alert_int.none (:1377,
sampled every 256 retirements), CG-PMP-005 cr_nomatch and CG-PMP-012 mprv0 bins (:2275 every retirement), CG-DBG-012
req0_mode0 (:2845 "every rvfi_valid"), CG-PMC-008 relation bins (:3093), CG-RVFI-001 continuity ok bins (:4660),
CG-RST-004 register-bank bins (:4627), CG-SEC-001 and CG-CHERI-001 end-of-test zero bins (:4279, :4849; credited in any
clean run). Required: remove the witness bins or gate them on the scenario they witness; a checker's pass is not a
coverage event. (d) CG-PRV-001 samples only on a mode change (:1392) while cr_trans requires eight m_m_* bins (:1400):
unreachable as written.

### Medium

M-1 F-DBG-044, F-IRQ-051, F-DBG-059 state the step-over-WFI and WFI-in-debug cases wrongly. With dcsr.step = 1
outside debug mode, do_single_step_d = 1 for the wfi in DECODE (rtl/ibex_controller.sv:462), enter_debug_mode_prio_d
= 1 (:474-475), wfi is a special_req (:287-293) so DECODE goes to FLUSH (:664-677), and in FLUSH the `else if (wfi_insn)
ctrl_fsm_ns = WAIT_SLEEP` (:966-967) is overridden by `if (enter_debug_mode_prio_q ...) ctrl_fsm_ns = DBG_TAKEN_IF`
(:985-987, flop :1046). WAIT_SLEEP is never reached and core_busy_o never drops; dpc = wfi + 4 and cause 4 stay right.
F-DBG-044 (7758) and F-IRQ-051 (5769) say "core_busy_o low for exactly one cycle" through WAIT_SLEEP -> SLEEP. For WFI
inside debug mode (F-DBG-059, 7953) WAIT_SLEEP is reached, but the ctrl_busy dip reaches core_busy_o only when no
fetch beat is outstanding, no invalidation is active and the LSU is idle (core_busy_o = ctrl_busy | if_busy | lsu_busy,
rtl/ibex_core.sv:496-522; rtl-arch T-051 row 29). Required: F-DBG-044/F-IRQ-051: FLUSH -> DBG_TAKEN_IF, core_busy_o
stays On; F-DBG-059: port-level wording. The corresponding TP items and bins (TP-DBG-044/059 family, CG-DBG-006 wfi
rows) follow. See Section 5 for my share.

M-2 Seven expected-fail items contradict the committed bug log. gen_bug_log.md v1a (hash 1a31f0f1423e791c) reclassifies
B12 ("documented behaviour, not a bug candidate ... TP-EXC-056, TP-CSR-094, TP-SEC-025 expect pass with a design note",
:139-142) and downgrades B14 ("none as gate items after the downgrade; the carrying items ... are split into the
priority behaviour (pass) and the RVFI-record confirmation (informational)", :161-164), consistent with my S-1. The test
plan (unchanged since 7356277) still has TP-CSR-094:4955, TP-EXC-056:6777, TP-SEC-025:17465 "expected-fail (B12)" and
TP-ISA-051:1103, TP-EXC-065:6903, TP-DMEM-034:14096, TP-RVFI-018:18768 "expected-fail (B14)", and Section 1.1 counts
them in the 30. On today's RTL these items pass, and the flow reports an expected-fail test that passes as FAIL
("unexpected PASS"). Required: B12 items to pass with the design note; B14 items split as the bug log says; Section 1.1
and the count (23 remaining) updated; TP-DMEM-034's priority/kill/re-execute checks must not sit under expected-fail.

M-3 Pass-marked items that follow the RTL on open bug candidates (S-1 residual). TP-CSR-074 (:4673-4675 "bit 13 is
compared under the RTL-as-is expectation in this item") and TP-CSR-075 (:4687 "0x4000_B007 ... RTL-as-is value") pass
today and fail after the B15 fix; TP-CSR-108 (:5149-5151 "M-mode trigger reads retire without trap ... others 0",
Expected pass) reads tdata3/mcontext/mscontext/scontext, the B3 behaviour, with an RTL expectation; TP-CSR-066 (:4561)
counts dummies "if enabled" under Expected pass (B7). No owner ruling accepts these RTL behaviours (Q-004/Q-005 open).
Required: exclude bit 13 from the TP-CSR-074/075 compares (or mark them expected-fail B15), move the four unimplemented
trigger-CSR reads out of TP-CSR-108 into TP-CSR-083/TP-TRG-008, run TP-CSR-066 with dummies off.

M-4 Coverage as the fire-check (S-13 residual). 27 items name a bin set as their fire-check; 14 are regression-level
("hit over the regression", "across the seed set", "over the run set"), which cannot be a per-seed fire-check at all:
TP-CSR-112:5205, TP-CSR-116:5261, TP-CSR-120:5317, TP-PRV-036:5823, TP-PRV-038:5851, TP-PMP-054:8985 ("the
covergroup is the fire-check"), TP-PMP-109:9755, TP-RST-029:18372, TP-RVFI-037:19117 and five more; TP-IMEM-040:13508
and TP-IC-038:15707-15708 have no gating criterion ("gen_chk_icache in informational mode ... gen_chk_alerts suppressed"
under Expected pass); TP-SEC-013:17196-17197 forces a wrapper-internal RF flop in a pass-gate item. Required: every item
names a per-seed assertion that proves the scenario happened (DV_prompt Section 5 step 4); regression-level coverage
goals move to the fcov-expectation manifests of the group's tests; TP-SEC-013 becomes a mutation-evidence item
(measured: false) or drops the force.

M-5 Adoption marks (S-9; DV_prompt honesty rule). gen_fcov_plan.md:97-98 and :1010 still say "Adopted bins: none in
this file. vendor/google_riscv-dv/** was not read by this subagent"; that is a statement of not having checked, not of
"none". Partitions that mirror riscv_instr_cover_group.sv without the mark: CG-ISA-002 cp_sign_pair (:131, also
duplicating adopted CG-ADOPT-003), CG-MUL-001 cp_sign_pair (:330), CG-MUL-003 cp_sign_pair (:372), CG-ISA-007 cp_taken
(:227), CG-CMP-001 cp_reg3 (:436, duplicating CG-ADOPT-005), CG-CMP-003 cp_hint (:474), CG-CMP-004 cp_class (:486),
CG-BIT-001 cp_eq_operands (:637). Required: one pass over the ISA/MUL/CMP/BIT/BTALU partitions against the riscv-dv
model (reference-only reading is allowed); mark each mirror "adopted" or record the S-9 "spec-derived, coincides"
ruling per coverpoint; correct the two sentences and the 55 count if it changes.

M-6 221 coverpoints that no test-plan item declares. gen_trace_tp_bin.csv references 2033 of the plan's 2185
coverpoints; the 221 others (PMP 56, EXC 36, CMP 32, BIT 31, ISA 25, MUL 15, IRQ 13, BTALU 10, IMEM 2, REG 1; e.g.
CG-BIT-001 cp_eq_operands/cp_rd_x0/cp_same_regs/cp_sign_pair/cp_wrap, CG-BIT-004 cp_bit25/cp_rs2_upper) will never
appear in an fcov-expectation manifest, so no run is held to them and the per-test check (completeness rule 5) cannot
fail on them. The completeness measure hides this because rule 2 is evaluated per covergroup. Required: every
coverpoint is owned by at least one TP item (add the bins to the items that exercise them, or mark the coverpoint
"regression-level, owner <group>" and have gen_trace_check.py report the count); gen_trace_check.py reports plan
coverpoints without CSV rows and fails when the count is not zero or not explicitly allow-listed.

M-7 Probe-register and unreachable-bin discipline in the coverage plan. (a) Four groups sample internal nets that are
not in gen_probe_register.md: CG-MUL-005 (:412, gen_sva_multdiv bound on div_en_i / md_state_q inside
ibex_multdiv_fast), CG-CSR-010 (:1240, "probe candidate P7 ... P1-P6 are taken"), CG-DIT-004 (:4198, :4204,
fcov_dummy_instr_type and the IF/ID write enable, not among P1's registered nets), CG-XIF-012 (:5299, same). Required:
a probe-register entry with a boundary alternative for each, submitted for my ruling before any bind; until then these
coverpoints are marked "pending probe ruling" and excluded from manifests. (b) Bins unhit by construction under the
opentitan configuration or the plan's own sampling rule: CG-TRG-001 tsel_dbg_app ok_applied (:2881; tselect always
reads 0 with DbgHwBreakNum = 1), CG-CSR-002 cr_mpp_op.mpp_h_csrrsi (:1061; csrrsi touches bits 4:0), CG-PRV-001 m_m_*
(H-2 d), CG-DIT-004 cp_context.fetch_stalled (:4213, the plan itself says impossible), CG-XIF-004
none_needed_trap_taken (:5186), CG-XIF-006 step bins under a zcmp_inflight sample (:5216-5217), CG-REG-006
cp_pmp_regime_tr bins listed both as bins and ignore_bins (:5098), CG-REG-007 all{17} with 19-20 knobs (:5111).
Bins that credit a bug-candidate RTL behaviour as "ok" without a bug tie: CG-DBG-007 nmip_0 (:2746, B5), CG-CSR-008
tdata3/mcontext/scontext *_wr/*_rd (m, ok) (:1194, B3), CG-CSR-001 m_s_lvl_ok (:1032, B3). Required: ignore_bins with
reason, or the "(Bn evidence)" mark, per case.

M-8 Layer-1 distribution weights (S-6). The fcov plan carries no per-bin weights or operand-class weights; the test plan's
"operand mix" prose (e.g. gen_test_plan.md area 4.1 conventions) gives a few ratios (rd = x0 about 1/16) but no table
the Test Writer can implement or the coverage can be checked against. Required: one weight table per agent/operand
class in the test plan (or gen_tb_knobs.yaml when it exists) that the fcov plan references; a "default random" entry is
acceptable where uniform is intended, but it must be stated.

M-9 Edge restatements (C-12 residual). In a systematic 53-edge sample 7 are clear restatements and 4 borderline (13 to
21 percent of 368): F-PRV-014:3977 ("priv_mode_lsu = M either way", the parent's formula at MPP = M; its twin F-PMP-073
was folded), F-IRQ-046:5718, F-RST-017:12122, F-TRG-013:8233, F-IRQ-019:5355 (also duplicates F-MUL-023 and F-BIT-036),
F-PMC-037:8864, F-DIT-007:11087, F-CSR-093:3679, F-IMEM-023:9339, F-CSR-077:3503 (duplicates ACTIVE F-DBG-013). Required:
fold these ten and apply the v2 edge rule to the remainder of the 368 with the same rigour as the 154 folds; report the
count.

M-10 Duplicates (C-14 residual). Unacknowledged clusters with more than one ACTIVE member: F-PRV-014 / F-PMP-072;
F-EXC-026 / F-PMP-082 / F-DMEM-033 (all three ACTIVE, `Edge: no`, the same PMP-denied data access statement);
F-EXC-031 / F-DMEM-022 (the latter calls itself "Bus-side view of F-EXC-031"); F-EXC-032 / F-PMP-088. Fresh scan of the
ACTIVE set: F-EXC-003 / F-IMEM-011, F-EXC-023 / F-PRV-021, F-CSR-077 / F-DBG-013, F-DBG-059 / F-IRQ-051, F-PRV-023 vs
F-IRQ-007/008, F-CSR-061 / F-PMC-018(+019), F-CSR-083 / F-TRG-008, F-DBG-057 / F-IRQ-037, F-CSR-011 / F-PMC-029
(subset), F-BIT-036 / F-MUL-023 / F-IRQ-019, F-DBG-020 / F-EXC-017 (subset). About 12 behaviours, 25 features.
Required: alias or fold each; one over-merge to undo: F-CSR-060 -> F-PMC-020 (3345) loses "with mcountinhibit[2] = 1 an
ID-stage minstret read returns the raw flop value without the speculative +1", which now exists only as a bin
(CG-CSR-013.cr_minstret_rd_wb.minstret_inh_retiring) with no ACTIVE What.

M-11 Checkers requested that no architecture defines, and a knob-name split. gen_test_plan.md Section 2 requests 62
checkers; 13 appear nowhere in dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md (grep count 0):
gen_chk_bitmanip_ref, gen_chk_timing_isa, gen_chk_zcmp_seq, gen_sva_multdiv, gen_chk_csr_flush, gen_sva_csr_excl,
gen_chk_trap_timing, gen_chk_exc_flush, gen_chk_regime, gen_chk_reset, gen_chk_sleep, gen_sva_ibus, gen_sva_dbus. The
plan's knob form `+gen_chk_<name>_en=0` (:42) differs from the architecture's `+gen_chk_<id>=0|1`, and the plan's coarse
ids (gen_chk_pmp, gen_chk_irq, gen_chk_debug ...) map to several fine architecture ids each, so the mutation-evidence
procedure ("+gen_chk_all=0 +gen_chk_<id>=1") cannot be executed from the plan's names. The architecture's C5.3b carries
spec-direction rows only for B1, B2, B3 and B15; B4, B5, B7, B9, B10, B11, B13 have no spec-direction checker anywhere,
so their expected-fail items would pass for want of a checker (B7 in particular: the architecture's ctr_minstret is a
bound check whenever dummies are on and cannot fail on B7; TP-PMC-013 needs its own rvfi_order-delta compare).
Required: a checker-id concordance (plan id -> architecture id(s) -> knob) owned by the DV Lead and agreed by TB Infra;
each of the 13 either gets an architecture row or is re-expressed as a test-level compare; C5.3b or the test plan names
the compare for each remaining bug candidate.

M-12 Expected-fail items share tests with pass items. The flow's expected_fail is a per-test attribute (gen_testlist.yaml:
FAIL is reported as XFAIL); every one of the 30 expected-fail items sits in a group that also hosts pass items (29
groups, e.g. gen_cmp_zcmp_basic 18 pass items with TP-CMP-051, gen_trg_fire 18 with TP-TRG-020, gen_csr_debug_csr 7
with TP-CSR-076 including the RTL-direction TP-CSR-074/075). If a group becomes one test, XFAIL masks every pass item's
failure. The conventions let the Test Writer split a group but do not require it. Required: a convention that every
expected-fail item is its own test (or its own xfail-only group), stated in Section 0 and applied to Section 3.

### Low

L-1 Array-bin naming. The plan declares `fast[15]{[16:30]}` while the CSV names the bins fast_0..fast_14; URG reports
array bins as fast[0]..fast[14]. The fcov-expectation manifests are generated from the CSV, so the names must match
what ci/check_fcov_expectations.py will find in the vdb. Decide the convention once (gen_fcov_plan.md Section 0) and
apply it to the 45 fast_N rows (CG-IRQ-001, CG-IRQ-006, CG-RVFI-003) and to F-IRQ-061/062's fold bins.

L-2 Probe phrasing. F-CSR-001 (2707), F-CSR-101 (3794), F-SEC-004 (11470), F-SEC-011 (11564), F-DIT-017 (11225) name
internal nets or RTL assertions as observables or expectations without the "probe candidate P<n> (probe register entry
needed)" phrase; F-SEC-011 names RTL-internal assertions as the observable.

L-3 Fold and edge bookkeeping. 9 ACTIVE edges point at an ALIAS instead of the canonical (F-CSR-065/068/077,
F-EXC-055/056/059, F-IRQ-005, F-DBG-053/054); 24 folds hang on a parent that is itself an edge (depth 2 through the
fold; e.g. F-DBG-027..030 -> F-PRV-005 -> F-PRV-002); 38 folds keep an Edge pointer naming a different ID than the
Status target (e.g. F-CMP-066:1869, F-DBG-046:7792); 22 folds name a bin in a covergroup that lists the fold, not the
parent (Section 0 promises the parent's covergroup); F-DBG-019 (7508) is FOLDED with `Edge: no`; F-SEC-032 (11814)
disagrees across What/Edge/Status; Section 3.2 rows for F-IRQ-022 and F-IRQ-038 say "(see parent covergroup)" while
the Status fields name bins; F-IC-033 (10756) names a cross, not a bin; F-EXC-058 and F-PMP-046 fold bins exist in the
plan but not in the CSV.

L-4 Literals where a parameter exists (S-8): CG-CSR-004 :1096-1097, CG-CSR-002 :1055/1057, CG-CSR-005 :1114-1124,
CG-CSR-016 :1355 (MHPMCounterNum); CG-CSR-011 :1262, CG-CSR-001 :1026, CG-PMP-005 :2283 (PMPNumRegions); CG-PRV-008
:1538/1547, CG-IRQ-002 :1932/1934 ($bits(irq_fast_i)); CG-IC-001/003/006 way0/way1 (IC_NUM_WAYS).

L-5 Completeness measure text. The reviewer step (rule 4) should state what the reviewer confirms (mechanical mapping
plus a sampled semantic check, as this file does); the 80 percent gate should be stated in Section 1, not only in the
3.8 proposal; rule 6 of 3.8 ("must contain >= 1 bin from every coverpoint of every CG its items own") breaks for
probe-gated coverpoints and needs the M-7 exclusion.

L-6 Test-group bookkeeping: TP-DMEM-001 (13520) sits in gen_imem_proto_basic "(informational entry)", 188 labels
against 187 in Section 3; TP-DBG-011 (10061, B9) drives a one-cycle debug_req_i pulse that the bug log calls
out-of-spec stimulus and "not a gate item" while the plan marks it expected-fail; TP-CMP-065 (2507) makes P1 the
fire-check beyond P1's permitted use.

L-7 Feature-list residuals: F-BTALU-001's alias F-ISA-024 ("not taken vs taken timing") has no ACTIVE What for the
not-taken case (it survives only as fold F-BTALU-005's bin); F-CMP-038's What defers to its own alias F-MUL-027
("see F-MUL-027"); F-BTALU-015 -> F-PMC-040 cluster is mis-sized.

L-8 gen_trace_check.py improvements implied above: per-bin rule 2, plan coverpoints without CSV rows, array-bin name
check, Section 3.2 consistency with Status fields, Edge pointer vs fold target.

### Info

I-1 The response (Section 6b) says 341 ACTIVE edge entries; the file has 368. I-2 The bug log v1a landed after the test
plan was generated; the plan set was reviewed as the committed pair (hashes above). I-3 B4: the architecture's C5.3b has
no row, and whether the pinned Spike traps on cm.mvsa01 with r1s' == r2s' is unverified; the shim or a test-level
compare must implement the spec check, else TP-CMP-051 XPASSes. I-4 The test plan's inventory names gen_isa_compare
while the architecture's rows are isa_*; fine once M-11's concordance exists.

## 5. Corrections to my own earlier findings

C-06 (v1) said of F-DBG-044 "the dip is exactly one cycle (WAIT_SLEEP)". That premise was wrong: under dcsr.step the
controller leaves FLUSH for DBG_TAKEN_IF (rtl/ibex_controller.sv:985-987) and never enters WAIT_SLEEP. The DV Lead
implemented my wording faithfully; the error is mine first. Likewise my A-10 (TB architecture v1) asked for a
core_busy_o rule from a ctrl_busy fact; rtl-arch's T-051 corrected it and F-DBG-059 needs the same port-level wording.
Both corrections are in M-1. Method note: I verified the WAIT_SLEEP line and not the FLUSH override two screens below
it; from now on any statement of the form "state X is entered" is checked against every assignment to ctrl_fsm_ns in
the enclosing state, not the first one found.

## 6. Cross-area items to relay

- rtl-arch (exclusion draft v2, my T-040 conditions F-6/F-7 depend on these): the F-CHERI-001 table finds (a) the A.3
  Block rtl/ibex_cs_registers.sv:2108-2209 contains the live flop mstack_epc_cap_q (:2126-2132, written on NMI in RV32I
  mode; the draft's own A.8 lists it as not excluded): carve it out of the Block by object; (b) the MSECCFG/MSECCFGH else
  arms rtl/ibex_cs_registers.sv:504-512, :516-522 are unreachable under PMPEnable = 1 and absent from A.3; (c) A.5 has no
  toggle lists for ibex_prefetch_buffer / ibex_fetch_fifo constant ports (feature list rows 24, 31). Also Part C rows 29
  and 24-28 carry off-by-one ranges (:901-909 vs :901-908; :615-624 vs :616-623) against A.3.
- TB Infra: M-11 (checker-id concordance; C5.3b rows or named compares for B4/B5/B7/B9/B10/B11/B13); M-7(a) probe
  requests; the ctr_minstret bound-check versus B7 note.
- Runtime: none new; the expected-fail granularity (M-12) is solved on the plan side.

## 7. Required before re-review (in this order)

1. H-1 rewrite (six items, CG-DBG-003 premise, CG-DBG-006 bin).
2. H-2 sampling rules: regime groups credited on a DUT-visible event; tautological guards replaced; witness bins removed
   or gated; CG-PRV-001 sample or bins fixed.
3. M-2 and M-3: expected-fail set reconciled with the bug log (23 items) and the four RTL-direction items corrected.
4. M-1: F-DBG-044, F-IRQ-051, F-DBG-059 and their items/bins.
5. M-6 and L-8: coverpoint ownership; gen_trace_check.py extended; re-run attached.
6. M-11 concordance; M-12 convention; M-5 adoption pass; M-7 ignore/mark/probe entries; M-4 fire-checks; M-8 weights;
   M-9/M-10 folds and aliases; the lows as time allows.
7. Write the response as dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md with one row per finding above.

The re-review will re-run my derivation script and the extended gen_trace_check.py, re-read every H and M location, and
re-sample 30 sampling conditions and 30 items; it will not re-open the closed v1 items.

## 8. Fence and method record

Inputs: the seven committed files, the response section, my v1 and T-034 files, gen_probe_register.md, the TB
architecture component sections v2, rtl-arch's exclusion draft v2 and T-051 fact-check, rtl/ (controller, core,
cs_registers, id_stage, load_store_unit, icache, multdiv_fast, if_stage), tools/specs (riscv-debug-spec
core_registers.xml, Sdext.adoc, Sdtrig.adoc), vendor/google_riscv-dv/src/riscv_instr_cover_group.sv (reference only,
by the coverage subagent, for adoption marks; no text copied). Four unnamed subagents sampled the four risk areas; every
high and medium above was re-verified by me against the cited lines before it was written. gen_trace_check.py was run
under ci/env.sh (PASS) and my own derivation script under the system python3. No LSF command. No fence event.
