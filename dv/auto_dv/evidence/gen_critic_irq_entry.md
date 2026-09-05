# Critic verdict: irq-entry (gen_test_irq_basic, the library rules it forced, the agent fixes it found)

Range 0203c6e..b6b1bbe, named by the Orchestrator. Group commits: a488878 (the entry's first landing: test module,
program generator, manifest), 3b18a50 (runtime-2's testlist merge of gen_test_irq_basic and gen_test_irq_basic_red),
d08955f (the cocotb entry point and the library rule refusing a module with no registered test), 92d6ea2 (the poll fixed
to an absolute cycle), 2d87642 (the cycle-slot timer service, lib.CycleWaiters), e6eb3a2 (tb-infra-2's agent fixes:
ack_seen per line, bus capture at the accepting posedge), 298642c (the TB-defect register T1-T3 and design property S6),
2b16c55 (the report-edge poll, the held final entry, the nearer-target re-arm), 00c80d7 (the first RED-OK rerun
retained), 0b16018 (the retirement-floor identity with its self-test case; the irq red transcript), b6b1bbe (Section 15).
Everything else in the range belongs to other groups (pmp-step1 at 2897920, irq-step1-samplers at its own verdict) or is
records.
Artifacts at b6b1bbe (sha256 first 16 / lines): dv/auto_dv/tests/gen_test_irq_basic.py eb679c23f44517a4 / 206;
dv/auto_dv/tests/gen_programs/gen_irq_basic_prog.py 5ea57e739acb7b7e / 315; dv/auto_dv/fcov_expectations/
gen_test_irq_basic.fcov.yaml 25cf8b1faf56456b / 146; dv/auto_dv/tests/gen_test_lib.py cdc0036ce618459c / 1399;
dv/auto_dv/tests/gen_test_template.py 71776612b32365cd / 482; dv/auto_dv/env/gen_agents_pkg.sv 7f9e7d6cb8b6efa2 / 835;
dv/auto_dv/flow/gen_testlist.yaml 63c0c74cc5bc76be / 2507; dv/auto_dv/evidence/gen_tdd_batch3.md 1c85771b0c5737fd / 708
(Sections 11, 13, 15); gen_tb_defects.md 28b57a150f6bb1b0 / 20; gen_tdd_logs/test_writer/gen_irq_basic_red1_stdout.log
and _sim.log, gen_fu_cycle_slot_service.log with gen_fu_cycle_slot_service_script.md, gen_fu_floor_identity.log;
gen_tdd_logs/lockstep/gen_fu_l41_irq_ack_target.log and gen_fu_l41_bus_latch_instant.log with the mutant diffs
MUT-ACKALL1 and MUT-LATCHNEG1; dv/auto_dv/gen_tb/gen_tests/gen_ut_irq_ack.py, dv/auto_dv/stim/gen_directed/
gen_irq_ack_directed.S, dv/auto_dv/tb/unit/gen_ut_bus_latch_top.sv.
Judged against: the trust triad (dv_principles.md Section 6) for the entry, the library rules and the agent fixes;
gen_test_plan.md TP-IRQ-001..004 pass criteria (:7944 and siblings); the RTL for the S6 class ruling (my trace in
dv/auto_dv/work/critic/gen_irq_entry_prep_notes.md); LOG-096/097; docs/dv/dv_principles.md d9c27db18f511411 (read
fresh; skill dv-principles-check).
Date: 2026-09-05T07:32:30Z   Role: Critic
Method: detached worktree of b6b1bbe in my scratchpad (removed after the logs were retained under
dv/auto_dv/work/critic/irqe/); the retained transcript read line by line against Section 15's claims; the cycle-slot
red reproduced by running the companion script (five lines byte-identical); gen_test_lib --self-test run at the range
end; the generator run by me at 40 seeds and in its red form (no simulation); every fire check read against the plan's
pass criteria; the S6 chain traced in the RTL with every gating term (prep note). The range review 274a89a was NOT read
before Sections 1-5; Section 6 follows. EXPOSURE, stated: the Orchestrator's messages summarised that review's headline
rows (mepc uniformity, the fifteen-entries count, the report-edge wait, the "own words" block, the fcov leg, the
hand-encoded hold, the narration) before I wrote these sections; each of those points below was then checked by me
against the code and the logs, and the two I rate Medium I would have to rate the same had I found them alone.

## 1. The entry and its trust triad
gen_test_irq_basic drives each armed line alone (quiet regime, line_mix single) through the bridge IRQ_SET command with
the until-ack hold; the per-seed program (gen_irq_basic_prog.py) spins on one instruction under a vectored mtvec table
whose armed stubs store five words per entry (vector index, mcause, mepc, mtval, mstatus) and acknowledge; the test's
fire checks read the tuples. Testlist at b6b1bbe: gen_test_irq_basic tier smoke, seeds 3, measured false, no manifest
referenced; gen_test_irq_basic_red tier check, red_fixture, red_expect naming fire_tp_irq_002, generator_args --red
--red-item TP-IRQ-002 (the vector's stub deviates by design, RED_VECTOR).
- TDD RED, retained and read: gen_irq_basic_red1_stdout.log, run irq_group_close2 red1, pinned git_head 1bd7439, seed
  694904681, verdict RED-OK; exactly one ok=False line ("fire_tp_irq_002 ok=False timer interrupt entry: vector 7
  carried mcause 0x00000007, expected 0x80000007"), 0 UVM_ERROR mentions, GEN_TEST_EOT stores=93 reports=92
  retired=1670, 18 "drove ... entry N of 18" lines, 14 GEN_PHASE lines, fire_schedule_applied ok=True 14 of 14. Section
  15's figures (92 report words, 18 lines driven, 14 phases, one fire failure) are the log's own; the entry's history at
  this seed (run 3: 173 UVM_ERROR and 14 phases applied at cycle 77; first rerun: 8 phases; now: 14 at their own
  boundaries) is stated with the pinned commit of each.
- The fire checks (line_facts, :50-67): per entry, mcause == MCAUSE_INTERRUPT | cause, mstatus.MIE == 0, MPIE != 0,
  mtval == 0; fire_tp_irq_002 adds that all entries share one pc; fire_tp_irq_003 the unexpected-trap count is 0;
  fire_tp_irq_004 the fast sweep enters every armed vector. Against the plan (gen_test_plan.md:7944, TP-IRQ-001, and its
  siblings): "gen_chk_csr_readback (mcause, mepc == interrupted pc, mtval 0, MPIE/MIE/MPP)". mepc is checked only for
  uniformity across entries and MPP is not read back (M-1).
- Mutation leg: the red fixture is a program-side deviation caught by the named check (the designed red); no mutant of
  the checker itself is retained for the entry. For the class M-1 names (a wrong mepc recorded consistently) the check as
  written cannot catch it, so the leg is open there.
- fcov leg: the manifest declares 71 bins, 38 on gen_irq_entry_cg (rendered at 4b5730e), 29 on gen_irq_vector_cg and 4
  on gen_exc_trap_csrs_cg, neither rendered; it is unreferenced by the testlist, so the unbuilt-mark DECL leg does not
  judge it today (L-3). The entry is unmeasured, so nothing in round 2 rests on it.
- Generator robustness: my own generator-level sweep at b6b1bbe runs gen_irq_basic_prog.py at 40 seeds (rc 0 each) and
  in its red form at three seeds (rc 0); the team's rule also wants the simulated 40-seed green sweep and the
  model-level red-observability assertion before the generator is handed, and a488878's message promised the sweep;
  none is retained in the group (L-6).

## 2. The library rules and the service (d08955f, 2d87642, 2b16c55, 0b16018)
- The registered-test rule: check_test_module parses the file and requires exactly one @cocotb.test() whose name equals
  the class's name attribute (gen_test_lib.py); the commit records four directions on a real file (committed shape
  passes; decorator removed, renamed entry point, two entry points fail). gen_test_lib --self-test at b6b1bbe: PASS,
  rc 0 (my run; the case the cycle-slot log recorded as failing, the red entry without a retained pinned-red log, is
  cleared by 0b16018's transcript).
- The cycle-slot service (lib.CycleWaiters): the retained red gen_fu_cycle_slot_service.log claims the policy only
  (one bridge slot, gen_bridge_if.sv:24-25, :77-80; the naive shared slot fails "far_asleep_at_near_hit" and
  "far_woke_at_own", CycleWaiters passes all three); its COMMAND 1 script was not kept, so 2b16c55 adds the companion
  gen_fu_cycle_slot_service_script.md as a stated reconstruction. I extracted that script and ran it from the range end
  with PYTHONPATH unset: rc 0 and the five result lines byte-identical to the log (irqe/cycle_slot_out.txt). The log's
  "NOT CLAIMED HERE: the cocotb layer" is answered by the transcript: 14 of 14 phases applied at their own boundaries.
- The floor identity: program_min_retired asserts equality with the plan's value when given; the retained red
  gen_fu_floor_identity.log shows on one real image (gen_min_retired 3332) and two plan values (3332 matched, 3065 stale)
  that the committed >= lets the mismatched pair through and the identity refuses it, the no-plan path unchanged; the
  library self-test carries the four arms. The record's "the fifteen directed entries pass it" counts callers: 15 test
  modules call program_min_retired; gen_test_irq_basic, gen_test_rst_boot, gen_test_csr_access and gen_test_csr_reset do
  not (my grep), so the identity does not run for them (M-2).
- The report-edge poll (2b16c55): await_reports waits on the report edge with the collector's retirement rule; it
  re-implements wait_eot's rule with its own rounds counter and does not count self._slow_rounds (L-1).

## 3. The agent fixes (e6eb3a2) and the class ruling (298642c)
- ack_seen releases only the line the acknowledging store's cause names: gen_fu_l41_irq_ack_target.log carries RED
  (committed driver, the named test FAIL), GREEN (fix, PASS), GREEN with referees inert, MUT-ACKALL1 caught by the named
  check with referees inert (FAIL), and the ablation control (the named check removed, PASS, "entry 2 = None (the named
  check is ablated)").
- Bus capture at the accepting posedge: gen_fu_l41_bus_latch_instant.log carries RED, GREEN, MUT-LATCHNEG1 caught by the
  named driver test on both checks and the ablation control (0 failures with the two checks removed), plus a whole-TB
  storm regression (ackgreen, irqlines, boot, lockstorm: 0 UVM_ERRORs each).
- The class ruling: the order-548 divergence was a TB modelling defect (register row T3: the memory agent sampled a
  combinational DUT output at the falling edge, gen_agents_pkg.sv:264 with the design note at :194); the core is
  self-consistent at every rising edge; the combinational path from the interrupt inputs to the fetch address is
  recorded as design property S6 (B21), not a bug candidate, with the interface-contract question put to the owner. My
  RTL trace (prep note, restated): rtl/ibex_cs_registers.sv:1044 irqs_o = mip & mie_q with mip the raw pins;
  rtl/ibex_controller.sv:490 irq_enabled, :498-500 handle_irq = ~debug_mode_q & ~debug_single_step_i & ~nmi_mode_q &
  (irq_nm | (irq_pending_i & irq_enabled)) & !(instr_gets_expanded_i == INSTR_EXPANDED_COMMIT); IRQ_TAKEN (:725 ff.)
  sets pc_set_o, exc_pc_mux_o = EXC_PC_IRQ and exc_cause_o from the LIVE irqs_i through mfip_id (:503-511, :746-751);
  rtl/ibex_if_stage.sv:418 branch_req = pc_set_i | predict_branch_taken, :213-228 exc_pc = {mtvec[31:8], 1'b0, irq_vec,
  2'b00}; rtl/ibex_icache.sv:251 lookup_addr_ic0 = branch_i ? addr_i : prefetch_addr_q, :1030-1037 instr_addr =
  |fill_ext_req ? fill_ext_req_addr : lookup_addr_ic0. So in the IRQ_TAKEN cycle with no external fill pending the
  presented address follows the pins with no register between, while mcause (csr_save_cause_o) and the pc are booked at
  the edge: S6 holds as written, and the classification rests on the contract question the record puts to the owner.
  The retained rerun (00c80d7, and 0b16018's transcript) with both agent fixes is clean at the failing seed, and Section
  15 says plainly that this zero is not the divergence resolved.

## 4. Conformance (dv_principles.md, read fresh)
Section 2: the fire checks fail through the collected mechanism (self.check) and the verdict is the flow's; Section 4:
Section 15 names its three defects, the dropped change and the pre-registered null, and the class ruling records the
corrected readings; Section 5: one history-narrating comment (L-5); Section 6: the entry's red is retained and named,
the library rules and the agent fixes carry red, green and (for the agents) mutant and ablation; the entry's own mutation
leg is open for the class M-1 names.

## 5. Rows
- M-1 (Medium, test; Test Writer). fire_tp_irq_001..004 verify mcause, MIE, MPIE and mtval per entry but mepc only as
  "all entries share one pc" (fire_tp_irq_002) and MPP not at all, where the plan's pass criteria (gen_test_plan.md:7944
  and the TP-IRQ-002..004 siblings) state mepc == interrupted pc and MPIE/MIE/MPP. A program that recorded a consistent
  wrong mepc (or an MPP other than M) would pass. Required: check mepc against the spin loop's pc per entry (the program
  knows its own symbol; the run shows 0x80000154) and MPP == M from the stored mstatus, with a red mutant that records a
  consistent wrong mepc caught by the named check.
- M-2 (Medium, library and records; Test Writer). The floor identity runs only where program_min_retired is called: 15
  modules call it, gen_test_irq_basic, gen_test_rst_boot, gen_test_csr_access and gen_test_csr_reset do not, so a floor
  drift there is invisible, while Section 13 says "the fifteen directed entries pass it" as if it covered the directed
  set. Required: the source checker requires the identity for every module whose program carries gen_min_retired (or the
  module states its exemption, as gen_test_boot_retire does through its sidecar), and the count is corrected.
- L-1 (Low, test). await_reports re-implements wait_eot's retirement-progress rule with its own rounds counter and
  never increments self._slow_rounds, so the slow-store count under-reports.
- L-2 (Low, records). Section 15's "in the run's own words" block includes "red_expect matched", which appears in
  neither retained log (my grep: 0 in both); the log's words are verdict=RED-OK and the fire line.
- L-3 (Low, records; DV Lead sizes). The entry's fcov leg: gen_test_irq_basic.fcov.yaml declares 33 bins on
  gen_irq_vector_cg and gen_exc_trap_csrs_cg, which no landing renders; unreferenced today, it fails the DECL leg at the
  flip. Owner and step unstated in the record.
- L-4 (Low, code). HOLD_UNTIL_ACK = 1 is hand-encoded in gen_test_irq_basic.py:29 against gen_irq_hold_e
  (gen_agents_pkg.sv:489) with no rendered Python home for the enum.
- L-5 (Low, comment rule). gen_test_lib.py:1030 narrates the incident ("used to destroy a pending far one ... stole the
  schedule runner's c11664"); state the intent.
- L-6 (Low, owed). No simulated 40-seed green sweep or model-level red-observability assertion of gen_irq_basic_prog.py
  is retained (a488878 promised the sweep); my generator-level run is green at 40 seeds. Owed before the entry's
  measured flip, when its manifest is measured anyway.
- Info. The UNTIL_ACK hold change is disclosed as dropped (Section 15) and the program stays byte-identical to the
  run-3 source; the retained companion script is a stated reconstruction whose output I reproduced.

CRITIC VERDICT: REQUEST-CHANGES, confined to the entry's fire checks (M-1) and the floor identity's coverage (M-2).
APPROVED within the group: the registered-test rule and the cycle-slot service with their reds (the latter reproduced by
me from the retained script), the floor identity's mechanism and its red, the report-edge poll and the held final entry
(their effect measured in the transcript: 14 of 14 phases at their own boundaries), both agent fixes with red, mutant
and ablation, the TB-defect register and the S6 class ruling (the RTL chain confirmed term by term), and the retained
RED-OK transcript, which is the first run of this entry with nothing but the designed failure in it. The entry stays
unmeasured, so round 2 does not rest on the open rows.

## 6. Reconciliation with the cross-model range review
dv/auto_dv/reviews/2026-09-05-claude-diff-0203c6e5-b6b1bbea.md at 274a89a (de9c34fc50e94499, APPROVE-WITH-CHANGES; two
Medium, five Low, one Info), read at 2026-09-05T07:33:17Z after Sections 1-5 were written (its headline rows had reached me through the
Orchestrator's messages, as the method line states). The reviewer verified what Sections 1-3 verified: collected
checking through finish(), the designed red with exactly one ok=False line, Section 15's counts from the log, one writer
to the cycle slot, the agent fixes bounded by their reds and mutants, the floor identity's four arms and the sidecar
exemption.
- Its Medium 1 = my M-1 (mepc uniformity only; MPP not read back); its remedy (export the spin label, compare every mepc
  to the sidecar's symbol address; MPP == M in line_facts) is the one I state.
- Its Medium 2 = my M-2 (the identity opt-in per test; four directed modules never call it; the count).
- Its Lows are my L-1 (the report-edge wait re-implementing wait_eot's rule), L-2 (the "own words" block), L-3 (the fcov
  leg open with the owner unstated), L-4 (HOLD_UNTIL_ACK hand-encoded; the review finds the second copy at
  gen_ut_irq_ack.py:24), L-5 (incident narration in gen_test_lib.py, also at :1056 and the two docstrings). Its Info is
  mine.
- Not in the review: my L-6 (no simulated 40-seed sweep or red-observability assertion of the new generator retained; my
  generator-level sweep is green).
- The verdict words differ on the same facts: the review's APPROVE-WITH-CHANGES and my REQUEST-CHANGES confined to M-1
  and M-2 rest on my rule that a plan-stated pass criterion absent from the check is blocking for that check.
- After the range: 721bab8 (Test Writer) says the entry compares every mepc against the exported spin label and the four
  directed modules call the floor identity; that touch is judged at its own range, and it is the shape M-1 and M-2 ask for.

## Section 7. Recorded re-review of 721bab8, the disposition of M-1 and M-2 (written 2026-09-05T07:46:10Z)

Artifact: commit 721bab8 (parent 4cd3ff6), eleven files: gen_test_lib.py, gen_test_template.py,
gen_test_irq_basic.py, gen_test_rst_boot.py, gen_test_csr_access.py, gen_test_csr_reset.py,
gen_programs/gen_irq_basic_prog.py, gen_tdd_logs/test_writer/gen_fu_mepc_identity.log (new, 5426 bytes,
md5 7931b0e0a7b70819d955831bc0b5756e, its gen_manifest.md row matches), gen_tdd_batch3.md and
gen_critic_response_batch3.md. All eleven are ASCII-clean. Method: the diff read in full; every claim of
the retained log re-derived on a detached worktree of 721bab8 (scratch critic_irqr; my logs retained
under dv/auto_dv/work/critic/irqr/); the landing claims no simulation and I ran none. Exposure: the
Orchestrator's messages summarised the landing's commit message and the rows' dispositions before I
read the diff; every statement below is my own measurement.

7.1 M-1 (mepc checked for uniformity only; MPP unread): ADDRESSED.
- The check. fire_tp_irq_002 now asserts pcs == {spin} with spin = lib.program_symbol_addr(self.image,
  "gen_irq_wait"); line_facts adds (mstatus & MSTATUS_MPP) == MSTATUS_MPP_M, so all four line classes
  check MPP. The generator exports the label (.globl gen_irq_wait); program_symbol_addr reads the
  sidecar's symbols block and asserts the symbol exists.
- The RTL fact behind the MPP predicate. On exception entry mstatus_d.mpp = priv_lvl_q
  (rtl/ibex_cs_registers.sv:927); mret restores priv_lvl_d = mstatus_q.mpp and sets mpp to PRIV_LVL_U
  (:954, :978), so MPP reads U between entries and M again at each entry; the handler reads mstatus after
  entry; the program never leaves M-mode (its only privilege instruction is the handler's mret).
  PRIV_LVL_M = 2'b11 (rtl/ibex_pkg.sv:225), so (mstatus & 3<<11) == 3<<11 is the right predicate.
- The retained red, reproduced. The log names its inputs by digest: the retained run log 70722f03779f
  equals the committed blob of gen_irq_basic_red1_stdout.log; the generator a350edcbb6d0 equals the
  committed blob of gen_irq_basic_prog.py at 721bab8 (so the log's "working tree" is the committed file);
  the proof script 5b303d27eb96 equals the script embedded in the log (extracted and hashed). I built the
  program at seed 694904681 from the 721bab8 worktree: gen_irq_wait = 0x80000154, the value all eighteen
  recorded mepc words carry. I ran the extracted script against the committed run log and my sidecar:
  exit 0, result block byte-identical to the log's (control True/True; the three mutants committed True,
  fixed False; RED/GREEN HOLDS True). One mutant the script omits, the mixed set {spin, spin+4}: committed
  False, fixed False, so the fixed check is nowhere weaker than the committed one.
- Info: pcs == {spin} is False for an empty entry set, where len(pcs) <= 1 passed vacuously.

7.2 M-2 (floor identity opt-in; four modules skipped it): ADDRESSED.
- The four modules call lib.program_min_retired(self.image, <plan>.min_retired) in fire_check:
  gen_test_irq_basic and gen_test_rst_boot with prog.plan(self.seed), gen_test_csr_access with self.plan
  (:64 plan_for), gen_test_csr_reset with self._plan (:168). py_compile of the seven Python files passes;
  gen_test_lib.py --self-test PASS at 721bab8.
- The condition, re-derived by me: 19 generators under gen_programs/*.py declare gen_min_retired (the
  twentieth grep match is gen_boot_retire_red.S, a red fixture); 19 test modules import one of them and
  each of the 19 calls program_min_retired with its plan value (census over dv/auto_dv/tests/gen_test_*.py:
  every module with a generator import has exactly one call). gen_test_boot_retire calls it without a
  plan value, the stated riscv-dv exemption. Section 13's corrigendum, nineteen rather than fifteen, is
  the count I get.

7.3 The Lows of Section 5 in this landing.
- L-1 (the report-edge wait duplicated wait_eot's rule): one template step, next_report_edge, carries the
  lateness rule; wait_eot and await_reports both call it, and _slow_rounds increments in that one place,
  so GEN_TEST_SLOW_TOTAL now counts stimulus waits too. The GEN_TEST_SLOW info line's wording changed;
  the flow parses only GEN_TEST_SLOW_TOTAL (dv/auto_dv/flow/gen_flow_const.py:32), so no consumer
  breaks. The template imports Edge and with_timeout (:48); the entry's now-unused import is removed
  and no use remains. CLOSED.
- L-2 ("red_expect matched" in neither retained file): Section 15 now separates QUOTED lines from
  COUNTED figures. The two quoted lines are verbatim substrings of gen_irq_basic_red1_stdout.log lines
  282 and 195 (fixed-string grep); the counted figures are the ones I measured in Section 3 (92 report
  words, 0 UVM_ERROR, 14 phases). CLOSED.
- L-5 (incident narrations in code): four docstrings and comments trimmed; the gen_test_lib.py diff and
  the CycleWaiters docstring change are comment-only. CLOSED.
- L-3 (fcov leg), L-4 (HOLD_UNTIL_ACK literal), L-6 (no retained 40-seed sweep): routed in the response
  file to the DV Lead, tb-infra-2 and runtime-2; not this landing's to close. My generator-level control
  re-run at 721bab8: 40 of 40 seeds generate, each program carries the .globl line, and the three
  --red --red-item TP-IRQ-002 builds return 0 (dv/auto_dv/work/critic/irqr/).

7.4 New findings on 721bab8.
- L-7 (low). The retained log names "sidecar of a program built at the same seed 60326dfb0989".
  prog.sym.json embeds absolute paths (the directed .S path, the tool paths), so its digest is not
  reproducible by anyone else: my build at the same seed gives 461101d27f33 with an identical symbols
  block. The load-bearing fact, gen_irq_wait = 0x80000154, is reproduced; a path-free identity (the
  symbols block, sha256 over json.dumps(symbols, sort_keys=True), 70f98779d358 in my build, or prog.nm)
  would make the line checkable. A corrigendum beside the log, or the manifest row, at the next touch.
- L-8 (low). gen_tdd_batch3.md's Section 14 corrigendum and the response file cite the Runtime Manager's
  measurement "against forty simulated runs" (40 of 40 against 28 of 40 for cr_op_rs1.zext_h_pos_rand;
  6 of 40 against 40 of 40 for cp_single_pos.p16) and name no retained artifact; git grep at HEAD over
  dv/auto_dv/evidence, work, reviews and docs finds the figures only in those two prose passages. The
  passage decides nothing (the mapper stays withdrawn), so this is a records defect: name the run set or
  manifest the figures come from.
- Build identity: 721bab8 touches no file of gen_rtl.f or gen_tb.f; gate key 449f0e66969bd42b at 721bab8
  and at its parent 4cd3ff6, both computed with gen_build_identity.py on detached worktrees.

7.5 Verdict on 721bab8. Both Mediums of Section 5 are addressed with evidence I reproduced; L-1, L-2
and L-5 are closed; L-3, L-4 and L-6 are routed; L-7 and L-8 are new Lows on the record.
CRITIC VERDICT: APPROVE for 721bab8. The REQUEST-CHANGES of Section 5 on 0203c6e..b6b1bbe is LIFTED on
this record: the irq-entry group stands approved, with L-3, L-4, L-6, L-7 and L-8 owed as disclosed.
Sections 1-6 above are byte-identical to the d355f7f commit (69a2f14b24f9a5f0).
