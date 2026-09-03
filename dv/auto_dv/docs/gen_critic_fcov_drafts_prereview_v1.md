# Critic pre-review v1: DV Lead coverage-plan / test-plan drafts (T-034, advisory)

- Artifacts (working drafts, dv/auto_dv/work/dv-lead/parts6/, state at 2026-09-03 06:08-06:25 UTC):
  fcov_{csr,dbg_trg_pmc,exc_irq,isa,mem_fetch_icache,pmp,sec_rst_rvfi_cheri,xcut}.md,
  tp_<same>.md, trace_feat_tp_<same>.csv, trace_tp_bin_<same>.csv, README_T006_BRIEF.md.
  exc_irq landed during the review (fcov 02:08, tp 02:07 local time; CSVs 02:08).
- Nature: ADVISORY input to the DV Lead's T-006 consolidation. No verdict line; the gate is the
  T-007 part 2 review of the promoted documents.
- Standard: DV_prompt.txt Sections 3 (adopted bins marked), 4 (completeness: every feature ->
  item -> bin, every bin -> feature, reviewer confirms), 5 step 2 (edge cases as own items/bins),
  6 (three randomization layers, regime pinnable, cross-interface crosses, counts from
  parameters), 8 (anti-vacuity of every sampling condition); docs/dv/dv_principles.md Section 4
  (prune impossible bins, never `illegal_bins = default sequence`, no duplicate coverpoints) and
  Section 6 rule 3; the Critic's earlier rulings gen_critic_feature_list_v1.md (C-20 B6 is
  RTL-defined, C-21 dcsr.ebreaks is a spec violation) and gen_critic_tb_arch_components_v1.md
  (C8 probe rulings: P1 accepted coverage-only, P4 conditional coverage-only, P2/P3/P5 rejected,
  P6 debug-only).
- Date (UTC): 2026-09-03 06:30. Reviewer: critic (Claude Fable 5.1). Method: one mechanical
  cross-area traceability script (mine) plus eight per-area unnamed subagents (anti-vacuity,
  observability, literals, transitions, crosses, layers, bug-candidate Expected lines,
  fire-checks, CSV shape); every high finding and the systemic mediums below were re-verified by
  me at the cited draft line and, where an RTL fact decides, at the cited RTL line. Fence: parts6,
  the brief, the feature list, rtl-arch/tb-infra work files, docs/dv, rtl/, doc/, tools/specs,
  and vendor/google_riscv-dv/src/riscv_instr_cover_group.sv as reference only (adoption check).
  One subagent grep touched five lines of ibex_configs.yaml (allowed path). No fence event.

## 1. Mechanical traceability shape (all eight areas, after exc_irq landed)

| Area | TP items | Features mapped | Bin rows | Adopted rows | TP without bin / without feature |
|---|---|---|---|---|---|
| csr | 158 | 138 | 3564 | 0 | 0 / 0 |
| dbg_trg_pmc | 156 | 149 | 2398 | 0 | 0 / 0 |
| exc_irq | 151 | 134 | 1498 | 0 | 0 / 0 |
| isa | 215 | 202 | 1128 | 0 | 0 / 0 |
| mem_fetch_icache | 179 | 149 | 884 | 0 | 0 / 0 |
| pmp | 110 | 100 | 2045 | 0 | 0 / 0 |
| sec_rst_rvfi_cheri | 142 | 127 | 1092 | 0 | 0 / 0 |
| xcut | 53 | 284 (cross-area) | 1218 | 55 | 0 / 0 |
| total | 1164 | 999 of 999 | 13827 | 55 | 0 / 0 |

- Every one of the 999 features has at least one TP item; every TP item has at least one feature
  row and one bin row; every TP-ID in a CSV exists in its tp file. Good shape.
- M-01 (medium) CSV `covergroup` column convention differs: trace_tp_bin_isa.csv uses the SV type
  name (gen_cg_isa_alu_imm) while every other area uses the CG id (CG-PMP-001). The fold-in and
  gen_check_trace.py need one convention (the brief's completeness rule uses the CG id and derives
  the URG key from the gen_cg name).
- M-02 (medium) Bin naming versus the fcov text: 4298 of 13827 rows have no literal `name{...}`
  on the coverpoint line. Causes, verified per area: cross bins and many value bins are written as
  bare names (brief template), coverpoint lines wrap, and range shorthand (`fast_0 .. fast_14`,
  fcov_sec_rst_rvfi_cheri.md:665) is expanded only in the CSV (fast_1..fast_13 appear nowhere in
  the fcov). Every other CSV bin is findable by name inside its CG block. Required for the
  checker: match `\bname\b` within the CG block after joining wrapped lines, and expand every
  shorthand in the fcov text so the plan, not the CSV, is the source.
- M-03 (high) CSV rows that require bins the fcov itself ignores or that are impossible: PMP 12
  rows on explicitly ignored bins (trace_tp_bin_pmp.csv:411, 414-415, 418-419, 562, 564, 1637-1640,
  1690) plus 13 rows on impossible bins (298-299, 488-492, 513-517, 1182-1183, 1442, 1448, 1692);
  DBG cr_stepped_retired.ebreakdbg_trap (tp_dbg_trg_pmc.md:859); exc_irq
  cr_pulse_change_outcome.one_stable_taken (tp_exc_irq.md:1367); SEC CG-DIT-004.cp_context.
  fetch_stalled (tp_sec_rst_rvfi_cheri.md:684); PMP dret_u_cleared_spec bins on the expected-fail
  item TP-PMP-073 (trace_tp_bin_pmp.csv:1182-1183). Under trust-triad rule 3 a declared-but-unhit
  bin fails the run, so these items are unpassable as written. Regenerate the CSVs from the
  post-ignore bin set and fix the impossible bins (Section 3).
- M-04 (medium) Orphan fcov bins (no TP item owns them): csr 5, dbg 4, mem 13, pmp 73, sec 2;
  isa 674 of about 1600 are reached only through `cr_*.auto` references (2 true orphans:
  CG-ISA-001.cp_rs1_eq_rd, CG-ISA-008.cp_delta). The ISA convention (items list `auto` crosses)
  and the other areas' convention (every bin enumerated) must be unified, and the manifest
  expansion of `auto` must exclude the impossible auto-cross bins of Section 2 S-7.
- M-05 (info) 284 features are mapped from two area files (xcut cross-maps); the completeness
  script must count each feature once.

## 2. Systemic findings (cross-area; examples with file:line)

### S-1 (high) Checker direction for bug candidates does not follow the recorded rulings
- dcsr.ebreaks: the Critic ruled it a spec violation (hardwired 0 without S-mode;
  gen_critic_feature_list_v1.md C-21). tp_csr.md:1088 TP-CSR-076 "pass (doc mismatch D-EBREAKS)",
  tp_csr.md:1058/1072 TP-CSR-074/075 bake bit 13 into pass predictions (masks 0xB004 /
  0x4000_B007), tp_dbg_trg_pmc.md:359 TP-DBG-018 "pass (doc mismatch D5)" with mask 0xB007
  (tp:356); fcov_csr.md:183 cp_dcsr_ro_w and fcov_dbg_trg_pmc.md:176 must treat ebreaks as a
  forced-0 field. All must become `expected-fail (BUG-03)` with the checker predicting 0.
- B6 (exception in debug mode forces priv M): the Critic ruled it RTL-defined, not a spec
  violation (C-20). tp_exc_irq.md:677 TP-EXC-046 `expected-fail (B6)` must become `pass`; the
  brief's B-list (README_T006_BRIEF.md) still names B6 as expected-fail and tp_csr.md TP-PRV-004/
  026 and TP-CSR-018 touch it without citing the ruling.
- B12 (mret clears sync_exc_seen): doc/03_reference/cs_registers.rst:556 states "cleared when
  mret is executed", so the RTL matches its documentation and no RISC-V specification covers
  double-fault detection; tp_exc_irq.md:817 TP-EXC-056 `expected-fail (B12)` and tp_csr.md:1340
  TP-CSR-094 should be `pass` with a design-weakness note for the security owner (an owner
  question, not a bug candidate).
- B14 (RVFI drops the ID trap on a WB error): tp_isa.md:738-751 TP-ISA-051 and
  tp_mem_fetch_icache.md:1296-1314 TP-DMEM-034 mark the whole scenario expected-fail, which masks
  a regression in the correct priority behaviour (WB error outranks the ID exception, the ID
  instruction is killed and re-executed). Split into the priority item (pass) and the RVFI-record
  item (expected-fail B14, unverified in simulation); the ISA subagent argues the model shows the
  same trap order so B14 may not be observable at all: route to the owner (both files already
  raise it in Open questions).
- B5 (dcsr.nmip): no CSR item exists (tp_csr.md:1055-1074 treat nmip as RO-0 with Expected: pass)
  while tp_dbg_trg_pmc.md:411 TP-DBG-021 and tp_exc_irq.md:1645 TP-IRQ-041 are expected-fail
  (B5). Reconcile: one owner item, the others exclude the bit from their compare.
- B3 contradiction inside tp_csr.md: TP-CSR-108 (tp:1535-1536) predicts tdata3/mcontext/
  scontext/mscontext read 0 in M-mode with "pass", while TP-CSR-083 (tp:1185-1186) makes the
  checker follow Sdtrig (trap, expected-fail B3). Move the four reads out of 108.
- Missing doc-mismatch tags (consistency): tp_csr.md:345 (D-MPP), :472 (D-MIP), :602-656
  (D-MCAUSE), :1198 (D-TDATA1). D-numbering differs per area (D1..D10 in exc_irq and mem,
  D-EBREAKS/D-MIP names in csr, rtl-arch's D1/D2/D3 for icache.rst); one table in the folded plan.

### S-2 (high) rvfi_trap is 0 on an ebreak that enters debug mode
rtl/ibex_core.sv:1885-1886: `rvfi_trap_id = id_exception & ~(ebrk_insn & ebreak_into_debug)`.
The DBG part assumes rvfi_trap = 1: fire-checks tp_dbg_trg_pmc.md:424-425 (TP-DBG-022), :508-509
(027), :524-525 (028), :854-855 (046), :1240-1242 (067), :1632-1633 (TRG-020) can never pass on
correct RTL; CG-DBG-003 sample premise (fcov_dbg_trg_pmc.md:70-75) and the bin
cr_stepped_retired.ebreakdbg_trap (fcov:156) are wrong; the accepted feature list carries the same
error (gen_feature_list_draft.md:6174, F-DBG-017 Observable at). Fix: `is_ebreak(rvfi_insn) &&
!rvfi_trap && next fetch == DmHaltAddr` identifies the debug path; rvfi_trap = 1 identifies the
exception path. The counter model also needs the rule "ebreak-into-debug: RVFI record with
rvfi_trap = 0 that is NOT counted in minstret" (rtl/ibex_id_stage.sv:1218).

### S-3 (high) Vacuous and near-vacuous sampling conditions
The brief asks for an anti-vacuity note per covergroup; most notes exist, but the conditions
themselves are weak in these patterns:
- Tautological conditions: fcov_isa.md:283 CG-MUL-002, :322 CG-MUL-004, :713 CG-BIT-010
  ("a previous retirement exists"), :755 CG-BTALU-001, :781 CG-BTALU-002; fcov_pmp.md:105
  CG-PMP-005 ("every PMP check performed by the model", i.e. every retirement: cp_match.nomatch and
  the reset-table cr_nomatch bins hit on every instruction of every test), :273 CG-PMP-012;
  fcov_dbg_trg_pmc.md:273-280 CG-DBG-012 and :521-527 CG-PMC-008 (`rvfi_valid`); fcov_csr.md:411
  CG-PRV-001 samples only on mode changes yet declares same-mode transition bins (cr_trans
  m_m_mret/ecall/ebreak/illegal/fetch_fault/ls_fault/irq/nmi, dbg_dbg_exc, cp_seq3 m_m_u/u_m_m:
  11 bins unreachable as written, declared by TP-PRV-002/004/005/010/036/038).
- Always-true witness bins that a manifest would count as coverage: fcov_mem_fetch_icache.md has
  15 `never{0}/none{0}/zero{0}` bins (:90, :150, :155, :180, :421, :454, :504, :548, :552, :604,
  :636-641, :743, :770) and 17 `ok{1}` checker-mirror bins; fcov_sec_rst_rvfi_cheri.md:203-204
  cp_internal_total.zero and :200-202 cp_minor_count_per_inject.zero (one end-of-test sample with
  no activity qualifier), :763-765 CHERI quiet bins not tied to store activity; fcov_csr.md:389-395
  CG-CSR-017 cp_alert_int.none, :540-542 CG-PRV-007 *_no bins; fcov_dbg_trg_pmc.md:521-527
  cp_hpm_hi.all_zero / cp_mcycle_rel.inc, :508-513 cycle_tick bins. Rule for the fold-in: a
  negative or "check passed" bin is either qualified by the stimulus that could have produced the
  effect (sampled per consumed fetch/response/retirement with a count threshold) or removed from
  closure bins and left to the checker.
- Multi-event covergroups without per-coverpoint `iff` guards, so coverpoints sample on events for
  which they are undefined: fcov_mem_fetch_icache.md:106-110 CG-IMEM-004, :139-141 CG-IMEM-005,
  :395-398 CG-DMEM-008 ("condition: as per coverpoint"), :622-625 CG-IC-002, :731-733 CG-IC-005,
  :791-793 CG-IC-007; fcov_dbg_trg_pmc.md:249-252 CG-DBG-011, :355-364 CG-PMC-001;
  fcov_csr.md:67-75 CG-CSR-002, :98-100 CG-CSR-003, :177-184 CG-CSR-007, :208-211 CG-CSR-008,
  :229-240 CG-CSR-009, :285-288 CG-CSR-011, :429-438 CG-PRV-002, :534-541 CG-PRV-007;
  fcov_isa.md:350-356 CG-CMP-001 (cp_insn32_straddle can never sample under the 16-bit condition),
  :488 CG-CMP-008 ("condition: as stated"); fcov_sec_rst_rvfi_cheri.md:30-40 CG-DIT-001.
- Unreachable-by-definition bins: fcov_sec_rst_rvfi_cheri.md:125-131 CG-DIT-004.cp_context.
  fetch_stalled (the file's own note says insertion cannot happen while fetch is stalled; required
  by TP-DIT-030); fcov_mem_fetch_icache.md:540-554 CG-FE-005 three coverpoints sampled on a trap
  event that cannot produce them, :494-506 CG-FE-003 cp_branch_not_taken_no_redirect sampled on
  redirects; fcov_exc_irq.md:290/299 CG-IRQ-001 exc_handler_first_intr0 (rvfi_intr is set for
  interrupt vectors only, rtl/ibex_core.sv:2403-2413), :467/475 CG-IRQ-011 none_pending_while_off,
  :356 cr_pulse_change_outcome.one_stable_taken (a one-cycle pulse is never taken: the controller
  re-evaluates the live pins in IRQ_TAKEN, CTRL-09).

### S-4 (medium) Timing-derived bins: direction, qualifiers and the icache
- rvfi_ext_mcycle is captured when the instruction leaves ID (rtl/ibex_core.sv:2102), so a
  retire-to-retire delta measures the LATER instruction's ID residency. fcov_isa.md:577, :656,
  :679, :702 define cp_delta "to the next retirement" for rotates/crc/ternary/bfp: d1 is hit by
  any single-cycle follower and d2 is unreachable; CG-MUL-002/004 and CG-BIT-010 use "from the
  previous retirement" (correct). The D8 witness CG-BIT-009.cp_delta.d1 (tp_isa.md:2651) is
  therefore vacuous. Same care in fcov_sec_rst_rvfi_cheri.md:93 cp_latency.full{37} (gap equals
  latency only after a measured pipeline offset, as tp_sec:117-119 admits).
- Every delta bin needs three qualifiers the drafts state inconsistently: no fetch stall (and for
  redirects the target fetch is by construction late: fcov_isa.md:16-17, :290, :765 define
  fetch_stall so that `no` is never true after a taken CTI), no dummy instruction in the gap
  (dummy_instr_en = 0 from the CSR model), and no mcycle/mcountinhibit write in between.
- ICache is on in this build. Bins and fire-checks that infer "in ID" from an ibus delivery, or
  assert "no ibus request to the target" (tp_isa.md:2892 TP-BTALU-005, :2976 TP-BTALU-011, :242,
  :732; tp_exc_irq.md:241, :507, :521, :591, :899, :1363, :1433, :1965; fcov_pmp.md:257/264
  bus_prefetched bins; fcov_xcut.md:70-71 S19) are blind when the line hits in the cache. Pin
  cpuctrlsts.icache_enable = 0 for those items (and exclude it from random cpuctrlsts writes,
  tp_exc_irq.md:993, :825) or derive the redirect from RVFI (pc_wdata != pc + len).
- fcov_xcut.md:64-69 S18 "same cycle" window semantics rest on the premise that RVFI is two
  stages late; rtl/ibex_core.sv:1868 makes rvfi_valid exactly one flop after WB exit, so
  retirement-anchored events can be back-dated by one cycle and read cycle-exactly at the pins.
  Consequences: CG-XIF-007 cp_enable_effect (fcov_xcut.md:301, the irq_pending_o edge precedes the
  RVFI record of the mie write, so "within 2 cycles AFTER" never samples), TP-XIF-014
  (tp_xcut.md:723), and the exc_irq decision-cycle definition (fcov_exc_irq.md:311/316: pre_mip is
  captured when ID empties, before the WB drain, rtl/ibex_core.sv:1948-1957).

### S-5 (medium) Regime layers (layers 2 and 3)
- fcov_xcut.md:83-167 CG-REG-001..006: every `_tr` transition bin samples on the phase-START
  record (fcov:85 "TB-side phase start"), so a transition is credited before any transaction ran
  under the new value (asleep phase, quiet irq regime, cache disabled). Sample `_tr` on the first
  event under the new regime or gate on per-phase activity counters.
- fcov_xcut.md:148-153 CG-REG-005 icache_ecc_err_rate bins credited with the cache disabled
  (tp_xcut.md:124 admits); add `iff icache_en_q`.
- fcov_xcut.md:168 cp_pmp_regime_tr lists mml_on_to_off/sparse/dense both as bins and as
  ignore_bins (an SV error) with the reason "schedule never spans a reset", contradicted by
  tp_xcut.md:173-175 (gen_xif_reset continues the schedule across resets, where MML clears).
- fcov_xcut.md:177-187 CG-REG-007 mixes three sample instants (banner, per-phase, end-of-run) in
  one covergroup with crosses across them; carry the run-constant values into every per-phase
  sample and drop the end-of-run sample. CG-REG-008 (fcov:193-200) samples per group, not per
  knob, so two knobs of one group changing together lose one transition.
- Knob-state coverpoints duplicated inside area files against the file's own rule
  (fcov_mem_fetch_icache.md:14-15 versus :35, :62, :175, :213-214, :632, :777, :819-823;
  fcov_sec_rst_rvfi_cheri.md:353 cp_key_delay): keep knob values only as cross operands outside
  xcut (dv_principles Section 4, no duplicate coverpoints).
- Positive: all 17 knobs and every value of the brief are covered (fcov_xcut.md:87-167); 187
  enumerated transition bins, no `default sequence` anywhere (grep clean in all eight files);
  `+gen_regime_pin` covered (cp_pinned_count fcov_xcut.md:183, TP-REG-019); every Phase 2 item in
  every area names knobs (0 `Knobs: none` on Phase 2); all knob names used are in the brief's list
  (the three new intg-rate knobs appear only as proposals).

### S-6 (medium) Layer 1: per-transaction distribution weights are mostly absent
Stimulus lines enumerate classes or ranges without weights: tp_csr.md 22 items (:397, :411, :481,
...), tp_dbg_trg_pmc.md 89 of 156 items (list in the DBG section), tp_isa.md about 200 Stimulus
lines (weights only at :12-17 convention and six items), tp_pmp.md all Phase 2 items (:1404-1530),
tp_exc_irq.md all 11 Phase 2 items ("Randomized: everything per seed"), tp_sec_rst_rvfi_cheri.md
5 items, tp_mem_fetch_icache.md most Phase 1 latency items (weights only in TP-IMEM-001/TP-DMEM-001).
One weight table per agent/operand class in the folded plan, referenced by items, satisfies
DV_prompt Section 6 layer 1 without repeating it 1164 times.
Also: 134 Phase 1 items carry `Knobs: none` (csr 33, isa 60, dbg 21, sec 14, mem 5, pmp 1) while
tp_isa.md:15-17 claims every Phase 1 item randomizes the memory-response regime through knobs;
either add a latency knob or drop the sentence.

### S-7 (medium) Crosses: impossible combinations without ignore, and duplicate coverage
- Impossible combinations left in `auto` or product crosses: fcov_isa.md:274-277 (c_mul with
  rd_x0/same-register bins, funct3 f4..f7 excluded by the sample), :209 cr_op_priv_outcome (nine
  impossible triples), :251, :363, :547, :815, :790/796 (about 30 unreachable bins);
  fcov_mem_fetch_icache.md:252-254 cr_be_x_beat (8), :219-220, :39-40 and nine more crosses (about
  40 combos); fcov_csr.md:80 cr_mpp_op.mpp_h_csrrsi (old MPP is never 10); fcov_pmp.md:30
  cr_prelock_wrl setlock_c1010/c1011 (RW=01 under MML=0 is legalised to w_dropped, contradicting
  the ignore at fcov_pmp.md:22), :170 cr_hi_mode base_hi30/hi31 and :169 cr_tor_empty unsamplable
  under CG-PMP-007's own condition, :167 k30/k31/k32_inside_high, :312 cr_phase.halt_fetch_deny
  (DmHaltAddr is inside the bypassed DM window, CTRL-34), :335 cr_locked_regime self-contradictory
  ignore, :262-263 mseccfg_*_now_allowed impossible; fcov_exc_irq.md:302, :305, :336, :338, :353,
  :354, :400-401, :438, :478, :66, :87, :150-151, :168, :183, :200; fcov_sec_rst_rvfi_cheri.md:75-77
  cr_dit_gap (DIT on forces gap >= 2), :98-102 cr_latency, :437-441, :642-644, :730-732, :774-778
  (U-mode id reads: marchid/misa trap in U, so id_*_u_no is unreachable and the ignore is inverted);
  fcov_xcut.md:256 CG-XIF-004 none_needed_trap_taken/debug_entered, :234/241 nmi_int outstanding
  bins (both rules cannot hold), :281/285 CG-XIF-006 step bins (zcmp_inflight is 0 at a dret).
  VCS reports every auto-cross bin; unignored impossible bins dilute the 80 percent gate and, when
  listed in a manifest, fail the run.
- Duplicate coverpoints across groups: fcov_isa.md CG-ISA-007 vs CG-BTALU-001 (cp_taken,
  cp_target_align, cp_wrap, cp_delta, cp_dit), CG-ISA-006 vs CG-BTALU-002, CG-ISA-011 vs
  CG-BTALU-003, CG-BIT-003/007/008 cp_delta vs CG-BIT-010, plus nine crosses that reduce to a
  coverpoint (:191-192, :212, :249, :585-586, :683-684, :686, :744-745, :773, :775, :795);
  fcov_exc_irq.md "exception commit x interrupt pending" in four groups (:141/152, :163/167,
  :273/279-280, :492) and pc[1]/mepc[1] alignment in six; fcov_sec_rst_rvfi_cheri.md cp_trap in
  five groups, cp_rf_wr_suppress in three; fcov_dbg_trg_pmc.md rvfi_mode-in-debug and dcsr.cause
  read-back each sampled three times; fcov_csr.md :142-147, :163, :247, :272-273, :330, :566
  single-bin or identity crosses; fcov_pmp.md:266 cr_bb, :337 cr_all_off_u, :79 cr_op_trans
  (a cross of a cross, not legal SV).

### S-8 (low) Literals where a parameter exists
MHPMCounterNum (13-bit masks 0x1FFD, "3..12", "13..31", 0xB0D..0xB1F, "12 counters":
tp_dbg_trg_pmc.md:2188-2330, tp_csr.md:722, :775, :806, fcov_csr.md:76, :115, :120, :133, :374,
fcov_dbg_trg_pmc.md:261); PMPNumRegions ("pmpaddr0..15", "16 regions", entry 15: fcov_pmp.md:36,
:85, tp_pmp.md:6, :73, :143, :254-258, :632-636, :759, :1482, :1490); PMPGranularity granule
(fcov_pmp.md:153, :159); NUM_FB*IC_LINE_BEATS / NUM_FB / IC_NUM_LINES (fcov_mem_fetch_icache.md:58,
:114, :148-149, :500, :529, :628, :644, :705-707, :736, :802; tp_mem:2198, :2357-2417, :2636,
:3031, :3047); $bits(irq_fast_i) (fcov_exc_irq.md:313-317, :334, tp_exc:1181, :1285, :1289,
fcov_csr.md:74, tp_csr.md:384, :467); IbexMuBiOn/Off and $bits(ibex_mubi_t)
(fcov_sec_rst_rvfi_cheri.md:348-349, :381, :508-509); CSR addresses and marchid value
(fcov_sec:21, :155, :744-759: use ibex_pkg names); mhpmevent selectors programmed although they
are hardwired (tp_isa.md:350, :3028, fcov_isa.md:766-767: counters 7/8/9 are jumps/branches/
taken, rtl/ibex_cs_registers.sv:1606-1617). The conventions blocks name the parameters; the bin
expressions and tp text must too.

### S-9 (medium) Adopted bins
- fcov_xcut.md CG-ADOPT-001..006 (55 CSV rows, all adopted = 1, each naming its riscv-dv source
  covergroup and the reduction applied; every ADOPT group cites real F-IDs): correct marking.
  Two refinements: CG-ADOPT-004 cp_ras enumerates 9 bins where riscv-dv's cross has effectively 4
  (`non_link = default` is excluded from crosses), so it extends rather than adopts; CG-ADOPT-006
  r0{0} duplicates F-BIT-006's boundary bin.
- fcov_isa.md declares "Adopted: none" without having read riscv-dv, yet six of its partitions are
  identical to riscv-dv coverpoints: cp_sign_pair {pp,pn,np,nn} (:66, :265, :307 = cp_sign_cross),
  cp_taken (:162, :757 = cp_branch_hit), cp_eq_operands for min/max (:534 = cp_rs1_eq_rs2),
  cp_reg3 r8..r15 (:357 = the compressed gpr[] bins), cp_grev_ctrl c0..c31 and cp_shfl_ctrl
  (:596-597 = reverse_mode/shuffle_mode ranges). Same-partition-independently-derived is a policy
  question for the DV Lead: DV_prompt Section 3 counts adopted bins separately, so either mark them
  adopted with the source, or record in the plan that identical partitions derived from the ISA
  text are spec-derived (HINT and illegal-compressed classes and div-by-zero results clearly are).
  The riscv-dv partitions the plan does NOT have (rotate/bit-location/bfp 0..31 value ranges,
  cp_logical similarity, instr_trans sequences) are listed in the ISA section for the DV Lead.

### S-10 (medium) Cross-interface crosses
- DV_prompt Section 6's example (fetch stalled while a data error returns while an interrupt is
  pending) exists as fcov_xcut.md:213 CG-XIF-001.cr_fetch_x_async.stalled_irq_pending with a
  genuinely same-cycle pin fire-check (tp_xcut.md:541), and from the fault side in fcov_exc_irq.md
  CG-EXC-013/CG-EXC-006. fcov_mem_fetch_icache.md has no three-way (TP-DMEM-054 lists three single
  bins) and fcov_exc_irq.md:486-492 CG-IRQ-012 samples the triple on the irq decision cycle, not
  on the coincidence. Assign one owner (CG-EXC-013 for the exception side, XIF-001 for the
  boundary triple) and remove the other copies.
- All boundary-derived state S1..S17 in fcov_xcut.md is genuinely boundary-derived; S11 (mode
  attribution during entry windows) and S19 (redirect confirmed by a bus request) are approximations
  that the S18 back-dating fix and an RVFI-derived redirect remove.

### S-11 (medium) Completeness measure (fcov_xcut.md:440-486)
- The proposal matches DV_prompt Section 4 in structure (feature -> item -> bin through the two
  CSVs; bin -> feature through CG Features; adopted counted separately; per-test manifests
  pre-merge with `urg -tests`). Gaps: (a) the 80 percent denominator is undefined: DV_prompt
  Section 4 says the URG summary number is the number, and URG's functional score is a weighted
  average of per-group scores, not the flat declared-bin ratio the script computes; define the
  gate as the URG group score with equal weights (or the flat ratio over post-ignore expanded
  bins, documented), after ignore_bins, counting cross bins per expanded bin; (b) rule 6 reduces
  "a reviewer other than the author confirms the mapping" to attaching the script output; add a
  sampled semantic confirmation (N feature-bin pairs per area) in the Critic's review; (c) bin ->
  feature resolves only at CG granularity (CG-XIF-005 cites 26 F-IDs over 62 bins); require per-
  coverpoint F-ID tags (fcov_xcut.md:87 already does it); (d) the ">= 1 bin from every coverpoint
  of every owned CG" manifest rule breaks for probe-gated (CG-XIF-012) and conditional coverpoints;
  (e) CG Features not claimed by any owning item: CG-REG-004 {F-DBG-006, F-DBG-008, F-RST-014,
  F-RST-015, F-SEC-012}, CG-REG-005 {F-IC-009, F-IC-010, F-IC-025}, CG-XIF-003 {F-DMEM-031};
  (f) "passes only if both totals pass" is stricter than DV_prompt (record it as a team policy).

### S-12 (medium) Edge cases with no item or bin (DV_prompt Section 5 step 2)
- exc_irq: an NMI or debug request arriving between IRQ_TAKEN and the handler's first retirement
  (rtl/ibex_core.sv:1949-1957 recaptures; the NMI's mepc is the interrupt vector); mstatus.MIE
  global 0->1 / 1->0 with a line pending as bins (fcov_exc_irq.md:330-334 covers mie-CSR edges
  only; TP-IRQ-070 demands MIE toggles but lists none); debug_req during nmi_mode (dret returns
  with nmi_mode still set).
- pmp: per-region mode transitions on a live entry (OFF->TOR->NA4->NAPOT) have no bins
  (fcov_pmp.md:13 records only cp_wr_mode); "RLB cleared then locked write ignored" sequence.
- mem: the security-relevant second-half store landing after a first-half PMP fault (MEM-13,
  Q-DL-7) has no bin and TP-DMEM-048's fire-check (tp_mem:1557-1559) does not assert it; the two
  informational unsolicited-rvalid tests (Q-DL-9) are in Open questions only, not in the test
  groups.
- dbg/pmc: step on->off free-run resume, mcountinhibit set mid-window, mcounteren_writable_i pin
  transition, trigger disarm after fire, ebreakm/ebreaku toggles across windows exist as stimulus
  but not as bins.

### S-13 (medium) Fire-check quality
- Coverage-as-fire-check ("every bin of cross X hit over the regression"): tp_csr.md:1590, :1646,
  :1660, :1674, :1688, :1702, :2208, :2222, :2236, :1436; tp_pmp.md:762, :1406, :1420;
  tp_exc_irq.md:717, :997; tp_mem:689, :1696 (agent generator verified, not the DUT). Rule 3 is
  per test and pre-merge; a fire-check is a per-seed assertion on an observable.
- Wrong or unsatisfiable: tp_mem_fetch_icache.md:160-161 TP-IMEM-008 "instr_req_o low while depth
  == cap" holds only for cap 8 (the DUT does not know the agent's cap; for smaller caps it holds
  req high while gnt is withheld); tp_mem:1973 TP-FE-015 ">= 50 redirects with spacing 1 cycle"
  (pipeline_details.rst:67-77: a taken branch costs 2, a jump >= 1); tp_sec_rst_rvfi_cheri.md:
  1713-1722 TP-RST-007 expects dcsr {prv M, rest 0} and dpc 0 after a debug_req entry, but entry
  writes dcsr.cause = 3 and depc = the boot vector (rtl/ibex_cs_registers.sv:910-917);
  tp_exc_irq.md:1489 TP-IRQ-030 width-2 pulse rule (a two-cycle pulse whose first cycle is the
  decision cycle IS taken); tp_xcut.md:189, :203, :245, :259, :427, :441 regime fire-checks are
  echo-versus-echo (add a measured per-phase statistic).
- Internal force in a pass-gate item: tp_sec_rst_rvfi_cheri.md:1028-1038 TP-SEC-013 forces a bit
  in the register file and filters the comparator; classify as mutation evidence (like
  TP-SEC-004) or drop.
- Probe-gated fire-checks presented as boundary: tp_sec:534-536 TP-DIT-023, :675-678 TP-DIT-030
  (rf_we_wb_o is P1-class), tp_dbg:1740-1742 TP-TRG-026, :2051-2052 TP-PMC-013 (proves only the
  enable read-back), tp_isa.md:2138 TP-CMP-065 (fires only via P1).

### S-14 (low) Document shape for the fold-in
- fcov_mem_fetch_icache.md ends at CG-IC-008 with no `## Counts` and no `## Probe candidates`
  (the header at :6 promises them); it also labels the RAM-model shadow-tag derivation "P2" (:6,
  :477, :664) although P2 was rejected and the derivation is boundary-based (correct approach,
  wrong label).
- fcov_isa.md and fcov_exc_irq.md CG blocks occasionally omit `condition:` (fcov_isa.md:468,
  fcov_exc_irq.md:311) or write "condition: as stated" (:488).
- Bare-name bins carry no value expression (fcov_mem:81-82, :112, :234, :339-342; 361 bins); the
  SV author must invent the encoding: give each symbolic bin its predicate.
- Probe usage is consistent with the C8 rulings: P1 for dummy-insertion bins (fcov_xcut CG-XIF-012,
  fcov_sec CG-DIT-004/005, CG-RST-002/004; declared as probe-gated), P4 named only as a fallback
  for coverage crosses (fcov_exc_irq.md:511-546, fcov_dbg:42), no checker consumes a probe. Items
  whose bins are P1-gated must not list those bins as must-hit until the probe register carries
  P1 (tp_dbg_trg_pmc.md:1747, :2058 versus its OQ-6).

## 3. Per-area top findings (highs and the mediums not already in Section 2)

### csr (fcov_csr.md, tp_csr.md)
- [high] tp:1088, :1058, :1072, :2273, :2288 ebreaks direction (S-1); [high] fcov:411/416/419
  CG-PRV-001 11 unreachable transition bins (S-3); [high] fcov:80 cr_mpp_op.mpp_h_csrrsi
  unreachable, declared by TP-CSR-024 (tp:362).
- [medium] fcov:382 cr_dbg_reset.tdata1_dbg cannot be hit by TP-CSR-081 (its preconditions read
  tdata1 in M-mode first, tp:1152); fcov:322 CG-CSR-013 cp_coincide "mcycle: always" tautology
  declared by TP-CSR-063; B5 item missing, B6 items uncited, TP-CSR-108 vs 083 (S-1).
- [low] fcov:265 cp_seed_val named after the internal csr_wdata_int (derivable from RVFI: say
  so); fcov:325, :563 pipeline-state inferences not listed as probe candidates; core_busy_o
  compared as a bit in prose (fcov:497, tp:1914-1970: it is ibex_mubi_t); tp:456, :1886, :1998
  fire-checks need a csrr the stimulus does not issue.

### dbg_trg_pmc (fcov_dbg_trg_pmc.md, tp_dbg_trg_pmc.md)
- [high] rvfi_trap on ebreak-into-debug (S-2): fcov:70-75, :156; tp:424, :508, :524, :854,
  :1240, :1632. [high] tp:359 ebreaks direction (S-1).
- [medium] fcov:139-143 step_armed derived from write data instead of the post-op dcsr.step;
  fcov:163-177 and :453-472 per-set-bit sampling makes zero-pattern bins unsamplable and misreads
  csrrc; fcov:302/309 tsel_dbg_app unreachable with DbgHwBreakNum = 1; fcov:420 div_wait one/few
  unreachable (one divide adds about 36 wait cycles); manifests declare bins their stimulus
  cannot hit (dcsr write-only bins on read-only items tp:413, :897, :1153, :1116, :1229; minstret
  bins on debug programs that read only dcsr/dpc tp:431, :448, :681, :791-948); counter exactness
  class per index missing from fcov:412-421 and TP-PMC-046's exact div_wait from RVFI gaps
  (tp:2599-2604); TP-TRG-026 runs dummies on with a passive exact counter checker (tp:1734).
- [medium] observability: FLUSH / IRQ_TAKEN cycle references (fcov:59, :83, :214, :336; tp:227)
  need the window definition or the P4 listing; tp:1074-1075 names pc_if inside a checker rule.

### exc_irq (fcov_exc_irq.md, tp_exc_irq.md)
- [high] fcov:356 / tp:1367 one_stable_taken unreachable (S-3); [high] tp:677 B6 direction (S-1).
- [medium] tp:817 B12 direction; fcov:413 cp_taken_after two_plus ignored although reachable in
  debug/NMI contexts (fcov:414-415); ICache=1 blindness in eight fire-checks (S-4); MIE edge bins
  and the IRQ_TAKEN-window NMI/debug edge (S-12); Phase 2 weights (S-6); tp:1489 TP-IRQ-030
  (S-13); tp:591 TP-EXC-040 same-cycle claim through the icache.
- Positives: 151 items, 134/134 features, all bins resolve; CG-EXC-007/009 sample on the
  coincidence itself; every interrupt-taken fire-check uses rvfi_intr / rvfi_ext_irq_valid / the
  vector fetch; NMI x MIE and U-mode x MIE=0 ignores are right.

### isa (fcov_isa.md, tp_isa.md, trace_tp_bin_isa.csv)
- [high] fcov:283, :322, :713 tautological sample conditions; fcov:577, :656, :679, :702 delta
  direction (S-4).
- [medium] fcov:16-17/:290/:765 fetch_stall definition versus taken CTIs; redirect fire-checks
  blind under icache hits (tp:2892, :2976, :242, :732); mcycle/inhibit/dummy qualifiers missing
  for every delta bin; tp:350/:3028 and fcov:766-767 program hardwired mhpmevent selectors;
  seven auto-cross defects (about 30 unreachable bins) and seven cross-CG duplicate families
  (S-7); six riscv-dv-identical partitions unmarked (S-9); TP-ISA-051 B14 expected-fail likely
  wrong (S-1); TP-CMP-051 records instead of asserting (tp:1944); 60 Phase 1 `Knobs: none`.
- CSV: 929 distinct bins referenced, all exist; 105 of 285 coverpoints reached only via
  `cr_*.auto`; 2 orphans (fcov:47, :188).

### mem_fetch_icache (fcov_mem_fetch_icache.md, tp_mem_fetch_icache.md)
- [high] missing `## Counts` / `## Probe candidates` (S-14); [high] tp:160-161 TP-IMEM-008
  fire-check wrong for cap < 8 (S-13).
- [medium] eleven multi-event covergroups without iff (S-3); three unreachable-as-written
  coverpoints (fcov:540-554, :494-506); knob-state coverpoints duplicated (S-5); TB-agent
  behaviour covered as DUT coverage (fcov:36-37 cp_gnt_comb, :323 cp_store_rdata_random, :62/:65-66
  cap crosses); fcov:378-379 cp_nmi_latency l2p ignored although reachable in debug/NMI context;
  tp:1973 TP-FE-015 spacing-1 unsatisfiable; MEM-13 second-half-store bin missing (S-12);
  TP-DMEM-034 bundles priority with B14 (S-1); no three-way stall x error x irq cross (S-10).
- Positives: protocol bins agree with the inventory (rvalid d0 and outstanding-cap bins ignored
  with Q-DL-9 reasons, byte-enable table complete, 256 sweep writes, one-cycle key pulse); hit/
  miss and occupancy are boundary-derived as the Critic required; every CSV row resolves.

### pmp (fcov_pmp.md, tp_pmp.md, trace_tp_bin_pmp.csv)
- [high] fcov:105 CG-PMP-005 samples every retirement (S-3); [high] fcov:30 setlock_c1010/c1011
  impossible (contradicts fcov:22); [high] fcov:169-170 cr_tor_empty / base_hi30/hi31 unsamplable
  under the group's condition; [high] 25 CSV rows on ignored or impossible bins (M-03).
- [medium] fcov:257/264 bus_prefetched bins and TP-PMP-091 (tp:1272-1285): every PMP CSR write
  flushes the pipeline (rtl/ibex_id_stage.sv:595-597), so the pre-fetched word is discarded;
  fcov:237 CG-PMP-010 privilege-at-grant mis-modelled during mret/trap in flight; fcov:167
  k30-k32_inside_high unreachable; fcov:312 halt_fetch_deny impossible; fcov:335 self-contradictory
  ignore; fcov:262-263 mseccfg_*_now_allowed impossible; fcov:283/287 dret_u_cleared_spec bins
  required by the expected-fail item TP-PMP-073 (a manifest can never pass); B1/B2 leak into pass
  items TP-PMP-094/098/104 (MPRV not pinned to 0 in debug episodes); per-region mode transitions
  missing (S-12); Phase 2 weights (S-6).
- Positives: Smepmp truth table cr_truth_mml1 = 96 bins verified row by row against smepmp.adoc
  and rtl/ibex_pmp.sv:59-97; MML/MMWP/RLB state walk (36 transitions) complete; MEM-13 bins match
  the Q-DL-7 shape; the 0x1FFFFFFF trailing-ones count is right (k29).

### sec_rst_rvfi_cheri (fcov_sec_rst_rvfi_cheri.md, tp_sec_rst_rvfi_cheri.md)
- [high] fcov:125-131 / tp:684 CG-DIT-004 fetch_stalled unhittable and required (M-03).
- [medium] negative eot bins without activity qualifiers (fcov:200-204, :763-765) and reset-window
  bins with no reset sample (fcov:185-189, :214-217); DIT gap bins without a stall-in-gap
  qualifier (fcov:65-93); tp:1713-1722 TP-RST-007 dcsr/dpc expectations (S-13); tp:1028-1038
  TP-SEC-013 internal force; tp:604-623 TP-DIT-027 must state the SIMULATION-define dependence
  of the LFSR reload (Critic C-05); cr_dit_gap / cr_latency impossible combos (S-7).
- Positives: B7/B13/B14/F-SEC-032/CTRL-04/ShadowCSR Expected lines conform; CG-CHERI-001 covers
  off-behaviour only (0x5b/0x7b and 0xBC1/2/4 traps, data_tag_o = 0, cap fields constant,
  marchid 22); P1 bins are listed as probe candidates; no `rvfi_csr_*` assumption.

### xcut (fcov_xcut.md, tp_xcut.md)
- [medium] `_tr` bins credited at phase start (S-5); S18 window premise (S-4); CG-REG-005 with
  cache off, CG-REG-007 multi-instant, CG-REG-008 per-group sampling, fcov:168 duplicate bin/
  ignore (S-5); CG-XIF-003 nmi_int outstanding rule, CG-XIF-004 none_needed bins, CG-XIF-006
  step bins, CG-XIF-007 cp_enable_effect (S-3/S-4); completeness denominator and reviewer rule
  (S-11); regime fire-checks echo-versus-echo (S-13).
- Positives: all knobs/values/transitions enumerated (187 `_tr` bins, 3 ignored with reasons);
  adopted bins correctly marked and sourced (55); the DV_prompt cross-interface example is present
  with a same-cycle pin fire-check; every CSV row resolves and every declared legal bin is owned.

## 4. What the consolidation should settle first (ranked)
1. Checker direction: ebreaks -> expected-fail (BUG-03); B6 and B12 -> pass with notes; B14 split
   and routed to the owner; B5 one owner item; B3 contradiction in tp_csr (S-1).
2. rvfi_trap = 0 on ebreak-into-debug: fix the six DBG fire-checks, CG-DBG-003, the
   ebreakdbg_trap bin, F-DBG-017, and the counter-model rule (S-2).
3. Remove or qualify the tautological samples and always-true witness bins; add per-coverpoint
   iff guards to multi-event groups; fix the unreachable-as-written bins (S-3) and regenerate the
   CSVs from the post-ignore bin set so no manifest can fail by construction (M-03).
4. Timing bins: delta from the previous retirement only, with the three qualifiers; icache_enable
   pinned for ibus-inferred items; back-date RVFI-anchored events by one cycle (S-4).
5. Regime transition bins sampled on the first event under the new regime; single owner for knob
   coverpoints (S-5); one weight table per agent for layer 1 (S-6).
6. Prune impossible cross combinations and de-duplicate coverpoints across groups (S-7).
7. Adoption policy for the six ISA partitions identical to riscv-dv (S-9); completeness
   denominator and reviewer-confirmation rule (S-11); one D-number table (S-1).
8. Add the missing edge items/bins (S-12); fix the wrong fire-checks (S-13); MEM Counts/Probe
   sections and the P2 wording (S-14).
