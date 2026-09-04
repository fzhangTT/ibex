# gen_bug_reproducer_specs.md -- reproducer specifications for the bug candidates (T-041)

Committed reference (promoted 2026-09-04 from the rtl-arch working file
dv/auto_dv/work/rtl-arch/gen_bug_reproducer_specs.md, same content apart from this paragraph); when the working
copy changes, this copy is re-promoted, and the working copy is never copied over this one without carrying this
paragraph. The working-file names below (gen_cover_props_draft.sv) are this role's own gitignored sources, named
as provenance: no claim here rests on opening one, and every RTL fact is cited to its rtl/ file and line.

Owner: rtl-arch. Date: 2026-09-03. Consumers: the DV Lead (bug log, test plan) and the Test Writer
(directed programs through dv/auto_dv/stim/gen_program.py --directed <file.S>, Zc macros from
dv/auto_dv/stim/gen_zc_insn.h). Build: opentitan configuration, DUT gen_dut_top (cheriot off),
SecureIbex=1, PMPNumRegions=16, DbgTriggerEn=1 with one trigger, WritebackStage=1.
Specs: tools/specs/riscv-debug-spec (Sdext.adoc, Sdtrig.adoc, xml/core_registers.xml),
tools/specs/riscv-isa-manual/src/priv/machine.adoc, tools/specs/riscv-isa-manual/src/unpriv/zcmp.adoc,
tools/specs/riscv-formal/docs/source/rvfi.rst. Every RTL line below was re-read on 2026-09-03.
No RTL edits, no LSF. ASCII only.

Classification policy applied (dv/auto_dv/docs/gen_intervention_log.md):
- Q-004 default (debug/MPRV items): checkers implement the debug spec, the tests are marked
  expected-fail, both are logged as bug candidates with reproducers.
- Q-005 default (dummy instructions and counters): exact-count checks run with dummy_instr_en=0; a
  directed test with dummies enabled asserts minstret_delta >= retired count and records the RTL
  count.
- Q-006 default (doc-vs-RTL where the RTL is spec-legal): the checker follows the RTL and the doc
  mismatch is logged (dv_principles.md Section 4).
- Q-007 default: debug_req_i is driven as a level held until debug-mode entry, plus one directed
  pulse-drop test for the dcsr.cause=0 window (B9).

Common mechanics for the Test Writer:
- Directed programs: `gen_program.py --directed <file.S> --seed <s> --out <dir> [--spike-check]`;
  the program starts at boot_addr_i + 0x80 through gen_boot_stub.S (gen_riscv_dv_target); end of test
  is the riscv-dv tohost convention (store 1 = pass, 3 = fail) as in gen_directed/gen_zc_directed.S.
- Debug mode: the DUT enters debug mode on debug_req_i (TB input, Q-007 level), on ebreak with
  dcsr.ebreakm/ebreaku set, on a trigger match, or on single step. Debug code is the program's own
  `.debug_rom` section (overrides gen_debug_rom_stub.S; linked at DmHaltAddr 0x1A110800, exception
  entry at +8, `.option norvc`, gen_link.ld). The "debugger" is therefore assembly in that section:
  it reads/writes dcsr/dpc/mstatus with csrr/csrw and ends with dret. Spike (standalone, no
  debugger) cannot run the debug-mode sections; for those the reference is the spec text quoted
  in the section and the check is self-checking assembly or a TB checker on CSR/RVFI state.
- Spike-runnable means: the sequence runs on tools/spike with the ISA string in gen_program.py
  (rv32imc_zicsr_zifencei_zba_zbb_zbc_zbs_zcb_zcmp_zicntr_zihpm_zicclsm, --priv=mu, --pmpregions=16,
  --triggers=1) and the spec behaviour is what Spike shows; DUT-only mechanisms (debug_req_i, dummy
  instructions, RVFI) are flagged per section.
- Zc macros take register NUMBERS and raw field values (gen_zc_insn.h header): cm_push rlist, spimm;
  cm_pop rlist, spimm; cm_popret / cm_popretz; cm_mvsa01 / cm_mva01s r1s, r2s.
- Observation points at the DUT boundary: RVFI fields (rvfi_valid, rvfi_order, rvfi_trap, rvfi_insn,
  rvfi_pc_rdata, rvfi_rd_*, rvfi_mem_*, rvfi_ext_* under +define+RVFI), the data bus (data_req_o,
  data_addr_o, data_we_o, data_wdata_o), debug_mode_o, priv_mode observable through PMP behaviour,
  and CSR reads made by the program itself and stored to a result buffer the TB compares.

Severity is the DV Lead's call; rtl-arch gives its reading in each section.

## BUG-01 MPRV honoured for data PMP checks in debug mode although dcsr.mprven reads 0

Spec expectation. dcsr.mprven (xml/core_registers.xml:281-287): value 0 "mprv in mstatus is
ignored in Debug Mode"; Sdext.adoc:33-34 "mprv in mstatus may be ignored according to dcsr.mprven";
Sdext.adoc:76-78: if hardware ties mprven to 0 "the external debugger is expected to simulate all
the effects of MPRV". MPRV itself: machine.adoc:588 "modifies the effective privilege mode" of loads
and stores to MPP. The RTL ties mprven to 0 (rtl/ibex_cs_registers.sv:826), so in debug mode the
load/store privilege for PMP must be M (debug mode executes with M privilege, Sdext.adoc:30-34), not
MPP.

RTL behaviour. priv_mode_lsu_o = mstatus_q.mprv ? mstatus_q.mpp : priv_lvl_q
(rtl/ibex_cs_registers.sv:998) has no debug_mode term; the PMP data channel uses it
(rtl/ibex_core.sv:1604 pmp_priv_lvl[PMP_D] = priv_mode_lsu). priv_lvl_q is forced to M on debug
entry (:908) but MPRV=1 with MPP=U makes the debug-mode load/store a U-mode access for PMP.

Minimal sequence (M-mode program, debug ROM section, TB asserts debug_req_i):
```
# main (M-mode): a PMP region that denies U but not M, MPRV=1, MPP=U, then wait for the halt.
  la   t0, probe_word          # a word inside region 0
  srli t1, t0, 2
  csrw pmpaddr0, t1            # NA4 region on probe_word (PMPGranularity=0 allows NA4)
  li   t2, 0x10                # pmp0cfg: L=0, A=NA4 (10), R=W=X=0 -> denied for U, not checked for M
  csrw pmpcfg0, t2
  li   t3, 0x00020000          # mstatus.MPRV (bit 17) = 1, MPP (bits 12:11) = 00 (U)
  csrw mstatus, t3
1: wfi                         # TB asserts debug_req_i here (level, Q-007)
  j 1b
.section .debug_rom            # debugger code at DmHaltAddr
  lw   a0, probe_word          # THE probe: a debug-mode load of the U-denied, M-allowed word
  li   a1, 0x600D
  sw   a1, result0             # reached only if the load did not fault
  dret
# DmExceptionAddr (DmHaltAddr + 8) is the debug exception entry: record 0xBAD in result0, dret
```
Spec: the load is an M-mode access (mprven=0 -> MPRV ignored), region 0 has L=0 so M is not
checked, the load succeeds, result0 = 0x600D. RTL: PMP checks with privilege U (MPRV/MPP), R=0 ->
load access fault inside debug mode -> the core jumps to DmExceptionAddr (rtl/ibex_controller.sv
exception entry in debug mode), result0 = 0xBAD.

Discriminating observation. result0 written by the program (TB reads the result buffer), or the
data bus: with the spec behaviour data_req_o for probe_word is issued while debug_mode_o=1; the RTL
suppresses the request (rtl/ibex_core.sv:1063 PMP gate) and takes the debug exception entry; on
RVFI the load appears with rvfi_trap=1 and rvfi_ext_debug_mode=1.

Classification. Spec violation (Q-004 default): checker follows the debug spec (in debug mode with
mprven=0 the effective data privilege is M); test expected_fail until the owner rules. Security
relevant: a debugger cannot rely on M privilege while MPRV is set. Severity: medium (rtl-arch).

Prerequisites. PMPEnable=1, one NA4 region; debug_req_i level from the TB after the program parks
in the wfi loop; the program's own .debug_rom section; no Spike reference for the debug part (the
main part up to the halt is Spike-runnable).

## BUG-02 Dummy instructions increment minstret (and the mul/div wait HPM counters)

Spec expectation. machine.adoc:1521 "The minstret CSR counts the number of instructions the hart
has retired." Dummy instructions are not instructions of the program; Ibex's own doc says they have
"no functional impact on processor state" (doc/03_reference/security.rst:45).

RTL behaviour. instr_perf_count_id_o (rtl/ibex_id_stage.sv:1218-1220) excludes ebreak/ecall/
illegal/fetch-error/minstret-write/expanded micro-ops but has no dummy term; wb_count_q carries it
to perf_instr_ret_wb_o (rtl/ibex_wb_stage.sv:150, :169, :208-209) and minstret increments
(rtl/ibex_cs_registers.sv:1588). RVFI excludes dummies (rtl/ibex_core.sv:1864 `rvfi_id_done &
~dummy_instr_id`, :1905 rvfi_stage_order_d not incremented), so RVFI and minstret disagree.

Minimal sequence (M-mode, Spike-runnable for the spec value; the RTL delta needs the DUT):
```
  li   t0, 0x4                 # cpuctrlsts.dummy_instr_en = 1 (mask 000: dummy every instruction slot allowed)
  csrw 0x7c0, t0               # cpuctrlsts
  csrr t1, minstret
  .rept 64
  nop
  .endr
  csrr t2, minstret
  sub  t3, t2, t1              # spec: 65 (64 nops + the first csrr); RTL: 65 + number of dummies inserted
  sw   t3, result0
  csrw 0x7c0, zero
```
Spike has no cpuctrlsts (custom CSR 0x7c0): for the Spike run guard the csrw with a TB-provided
plusarg or place it in a section the Spike variant omits; the spec reference value 65 is
independent of the CSR.

Discriminating observation. result0 > 65 on the DUT (the exact excess equals the number of dummy
retirements, which the TB can count as instructions retired in WB with no RVFI record, or as
rvfi_order gaps: none, because RVFI skips them). A second signal: mhpmcounter11/12 (mul/div wait)
advance when the inserted dummy is a MUL/DIV.

Classification. Spec violation of minstret semantics; Q-005 default: exact-count checks run with
dummy_instr_en=0; this directed test runs with dummies on, asserts minstret_delta >= 65 and records
the RTL count; logged pending ruling. Severity: low (counters only), but it breaks any
minstret-based comparator when dummies are on.

Prerequisites. SecureIbex=1 (dummy instructions available); no debug; deterministic dummy count is
not possible (LFSR), so record rather than predict.

## BUG-03 dcsr.ebreaks is writable and reads back although S-mode is absent

Spec expectation. xml/core_registers.xml:163-174: ebreaks (bit 13) is WARL and "This bit is
hardwired to 0 if the hart does not support S-mode." Ibex has M and U only. Ibex doc
doc/03_reference/cs_registers.rst:465-467 also says the other dcsr bit fields read as zero.

RTL behaviour. The dcsr write path (rtl/ibex_cs_registers.sv:811-836) forces xdebugver, prv, cause,
stepie, nmip, mprven, stopcount, stoptime, zero0/1/2, but not bit 13 (ebreaks); the read returns
dcsr_q (:551).

Minimal sequence (debug ROM section; halt by debug_req_i or by ebreak with ebreakm set):
```
.section .debug_rom
  csrr t0, dcsr
  li   t1, 0x2000              # ebreaks
  or   t0, t0, t1
  csrw dcsr, t0
  csrr t2, dcsr
  andi t2, t2, 0x2000          # spec: 0 (hardwired); RTL: 0x2000
  sw   t2, result0
  dret
```
Discriminating observation. result0 (program-visible) or a TB CSR checker on the dcsr read value
while debug_mode_o=1. Functionally invisible otherwise (no S-mode ebreak can occur).

Classification. Spec violation (WARL field that must read 0); Q-006 does not apply (the RTL is not
spec-legal). Checker follows the spec; test expected_fail. Severity: low.

Prerequisites. Debug-mode entry (debug_req_i level or ebreakm); own .debug_rom section; DUT only.

## BUG-04 RVFI trap record suppressed when an ID-stage exception coincides with a WB load/store error -- DOWNGRADED by this re-analysis

Spec expectation. rvfi.rst:35-39: when the core retires an instruction it asserts rvfi_valid;
:53-58: rvfi_trap must be set for an instruction that traps; :41-43: rvfi_order has no gaps. RVFI is
the trace contract of the ISA-model comparator, not a RISC-V ISA specification.

RTL behaviour (re-read for T-041). rvfi_id_done = instr_id_done | (rvfi_flush_next &
id_exception_o & ~wb_exception_o) (rtl/ibex_core.sv:1851-1853); rvfi_flush_next = (ctrl_fsm_ns ==
FLUSH) (rtl/ibex_controller.sv:1122); id_exception_o = exc_req_d (:278); wb_exception_o =
load_err_q | store_err_q | load_err_i | store_err_i | (On & cheriot_wb_err_i) (:336-337). In the
coincidence cycle the controller goes to FLUSH for BOTH exceptions; in FLUSH the writeback error has
priority: csr_save_wb_o = store_err_q | load_err_q (:833-840), the cause is the access fault, mepc =
the WB instruction's PC, and the ID instruction is killed (instr_kill via wb_exception,
rtl/ibex_id_stage.sv:1033-1036) WITHOUT having executed. After the handler returns, the killed
instruction is fetched and executed (or traps) again, and RVFI records it then. Suppressing its
record in the coincidence cycle is therefore architecturally CORRECT: the instruction did not trap
in that cycle; only the WB instruction did, and that one has its own rvfi_trap record from the WB
path. The T-003/T-017 statement "the RVFI stream then lacks the trapped instruction" (A.1 row
BUG-04, DV Lead B14) assumed the ID exception was taken; it is not. No case was found in which
wb_exception_o is high in the coincidence cycle and the WB exception is then NOT taken in FLUSH
(the _i terms are registered into the _q terms for the FLUSH cycle).

Minimal sequence (M-mode; Spike-runnable; this is now a CONFIRMATION test of consistent behaviour):
```
  # PMP: region 0 NA4 on bad_word with L=1, RWX=000 (denied for M as well)
  la   t0, bad_word
  srli t1, t0, 2
  csrw pmpaddr0, t1
  li   t2, 0x90
  csrw pmpcfg0, t2
  sw   zero, 0(t0)             # faults in WB (PMP error at response time)
  .word 0x00000000             # illegal instruction in ID in that cycle
  # handler: record (mcause, mepc) in the result buffer; on the store fault set mepc = mepc + 4
```
Expected on RVFI (spec and, per this re-analysis, RTL): record 1 = the store with rvfi_trap=1
(StoreAccessFault, mepc = store); record 2 = the illegal instruction with rvfi_trap=1 AFTER the
handler returns (it executes then, because the handler skipped the store). The ISA model (Spike)
produces the same two traps in the same order. Two records with rvfi_trap, no gap in rvfi_order.

Discriminating observation. If the RTL ever emitted only ONE trap record for this program (the
illegal instruction missing although it re-executed), BUG-04 is real; the expected outcome is two.
Timing: the illegal instruction must be in ID when the store's error is reported (WritebackStage=1:
the instruction right after the store); vary the memory latency so the response arrives in the
DECODE cycle of the illegal instruction.

Classification. DOWNGRADED from bug candidate to "RVFI convention note, confirmation pending"
(rtl-arch re-analysis 2026-09-03; the id BUG-04 stays reserved so the log history is stable). The
comparator follows the RVFI convention; the test is a normal pass/fail test (no expected_fail): pass
= two trap records in program order. If the sim shows one record, re-open as a bug candidate with
the trace attached. The DV Lead's B14 sim remains the evidence step.

Prerequisites. +define+RVFI build; PMP region for the WB fault; a trap handler that skips the store.

## BUG-05 Illegal mstatus.MPP encodings are mapped to U, the Ibex doc says M

Spec expectation. machine.adoc:433 "xPP fields are WARL fields that can hold only privilege mode x
and any implemented privilege mode lower than x", :392 "The xPP fields can only hold privilege
modes up to x": with M and U implemented, writing 01 (S) or 10 (reserved) may legally map to any of
the supported values. Ibex doc doc/03_reference/cs_registers.rst:138 says such writes "will be
interpreted as Machine Mode".

RTL behaviour. rtl/ibex_cs_registers.sv:783-786: `if ((mstatus_d.mpp != PRIV_LVL_M) &&
(mstatus_d.mpp != PRIV_LVL_U)) mstatus_d.mpp = PRIV_LVL_U;` (same rule for dcsr.prv :813-816).

Minimal sequence (M-mode, Spike-runnable; Spike's own WARL choice may differ from both, so the
reference is the spec text, not Spike):
```
  li   t0, 0x00000800          # MPP = 01 (S)
  csrw mstatus, t0
  csrr t1, mstatus
  srli t1, t1, 11
  andi t1, t1, 3               # doc: 3 (M); RTL: 0 (U)
  sw   t1, result0
  li   t0, 0x00001000          # MPP = 10
  csrw mstatus, t0
  csrr t1, mstatus
  srli t1, t1, 11
  andi t1, t1, 3
  sw   t1, result1
  # consequence check: mret target privilege
  la   t2, after_mret
  csrw mepc, t2
  li   t0, 0x00000800
  csrw mstatus, t0
  mret                         # RTL: enters U-mode; doc: stays M
after_mret:
  csrr t3, mhartid             # U-mode read of an M-only CSR traps in the RTL case
```
Discriminating observation. result0/result1 (0 vs 3) and the privilege after mret (an M-only CSR
read after mret traps with IllegalInstruction when the RTL choice is in effect; the trap handler
records mcause). On RVFI: rvfi_ext_priv (if exposed) or the trap record.

Classification. RTL-defined (spec-legal WARL choice); Q-006 default: the checker follows the RTL
(MPP illegal -> U), the doc mismatch is logged as a doc defect. Not expected_fail. Severity: doc
only; note for the DV Lead that the choice decides the mret target privilege, so the ISA model's
WARL choice must be aligned with the RTL (Spike maps illegal MPP writes to its own legal value).

Prerequisites. None beyond M-mode; Spike-runnable.

## BUG-06 dret into U-mode leaves mstatus.MPRV set

Spec expectation. Sdext.adoc:202 (Resume): "If the new privilege mode is less privileged than
M-mode, MPRV in mstatus is cleared." (MPRV semantics: machine.adoc:588.) Compare mret, which the RTL handles (rtl/ibex_cs_registers.sv:
957-959 clears MPRV when MPP != M).

RTL behaviour. csr_restore_dret_i (rtl/ibex_cs_registers.sv:949-951) restores only priv_lvl from
dcsr.prv; no mstatus write.

Minimal sequence (debug ROM section; halt from M-mode by debug_req_i):
```
# main (M): MPRV=1 with MPP=M, then park
  li   t0, 0x00021800          # MPRV=1, MPP=11 (M)
  csrw mstatus, t0
1: wfi
  j 1b
.section .debug_rom
  csrr t1, dcsr
  andi t1, t1, ~3              # dcsr.prv = 00 (U)
  csrw dcsr, t1
  la   t2, u_code
  csrw dpc, t2
  dret                         # resume into U-mode
u_code:                        # U-mode
  lw   a0, m_only_word         # word in a PMP region that allows M (L=0, RWX=000): denied for U
  # spec: MPRV cleared on resume -> U access, PMP denies -> LoadAccessFault (handler records 0xF1)
  # RTL:  MPRV still 1 with MPP=M -> load performed with M privilege -> no fault (record 0x600D)
```
Discriminating observation. Whether the U-mode load faults (mcause 5 recorded by the M-mode
handler) or completes; on the data bus, whether data_req_o is issued for m_only_word while the
core is in U-mode; a CSR read of mstatus is not possible from U-mode, so the PMP behaviour is the
observable. Note the debugger must NOT have cleared MPRV itself (the point of the test).

Classification. Spec violation (Q-004 default): checker follows the debug spec (MPRV=0 after a dret
to U), test expected_fail. Security relevant (U-mode code runs with M data privilege until the next
mret/trap). Severity: medium-high (rtl-arch).

Prerequisites. debug_req_i level; PMP region with M-only access; own .debug_rom; DUT only (no Spike
debugger). Also pair with BUG-01 in one program: the same region serves both probes.

## BUG-07 Dummy instruction inserted mid-Zcmp sequence skips one micro-op

Spec expectation. zcmp.adoc:151-163 (software view of push): "A sequence of stores writing the
bytes required by the pseudocode ... A stack pointer adjustment"; :543 "The final section of
pseudocode executes atomically, and only executes if the section above completes without any
exceptions or interrupts"; :141-144 a trapped sequence is re-executed as a whole. cm.pop likewise
(:205-215, :735). Every register in the list must be stored/loaded exactly once per execution.

RTL behaviour. The expander FSM advances on its id_in_ready_i port = id_in_ready_i & ~pc_set_i
(rtl/ibex_if_stage.sv:493) with no insert_dummy_instr qualifier, while the IF/ID register takes the
dummy instead of the micro-op (instr_out mux :526-530). The dummy inserter counts every accepted
slot including micro-ops (rtl/ibex_dummy_instr.sv:102-103, threshold :115); fetch_valid stays high
during expansion (:808-809), so a dummy can be inserted after 0..3 micro-ops of a sequence. The FSM
then moves on (cm_state_d/cm_rlist_d updates rtl/ibex_compressed_decoder.sv:640-670, pop :723-753):
one store, one load, or the sp adjustment is never executed.

Minimal sequence (M-mode; Spike-runnable for the spec values, dummies are DUT-only):
```
  .include "gen_zc_insn.h"
  la   sp, stack_top
  mv   t0, sp
  li   t1, 0x4                 # cpuctrlsts.dummy_instr_en=1, mask 000 (highest insertion rate)
  csrw 0x7c0, t1
  # known patterns in ra, s0..s11
  li   ra, 0x01010101
  li   s0, 0x02020202
  ...                           # s1..s11 = 0x03030303 .. 0x0d0d0d0d
  .rept 32                      # many iterations so the LFSR threshold lands mid-sequence
  cm_push 15, 3                 # rlist 15 = {ra, s0-s11}; spimm field 3 -> stack_adj = 64 + 3*16 = 112 (zcmp.adoc:408, :447-450)
  cm_pop  15, 3
  .endr
  csrw 0x7c0, zero
  # check 1: sp == t0
  # check 2: every register still holds its pattern (a skipped store followed by a pop reloads
  #          stale stack memory into that register; a skipped load leaves the register untouched
  #          but a skipped sp adjustment breaks the frame for the next iteration)
  # check 3 (memory): pre-fill the stack area with 0xDEAD; after the loop every pushed slot of the
  #          LAST push must hold the register pattern, never 0xDEAD
```
Because the LFSR decides where the dummy lands, use many iterations and also a pop-only variant
(pre-filled stack, single cm.pop) and a push-only variant (single cm.push into 0xDEAD memory).

Discriminating observation. Architectural: a register or stack slot with a wrong value after a
push/pop pair (checks 1-3), i.e. a Spike-vs-DUT register/memory mismatch at the end of the loop.
Micro-architectural (RVFI, +define+RVFI): the number of rvfi_ext_expanded_insn micro-op records per
cm.push/cm.pop is rlist+1 (stores plus sp update; pop adds the ret for popret) on the spec side and
one fewer on the RTL side when a dummy landed inside; the data bus shows rlist stores for a correct
push and rlist-1 for a broken one.

Classification. Spec violation (Q-004/Q-006 do not cover it directly; Zcmp semantics are
normative): checker follows the spec (all list registers stored/loaded, sp adjusted), test
expected_fail while dummies are on; with dummy_instr_en=0 the same program must pass (control).
Severity: high (silent data corruption on the stack with SecureIbex dummies enabled). Also the
BUG-07 witness cover T022_COVER_bug07_dummy_midseq in gen_cover_props_draft.sv marks the cycle.

Prerequisites. SecureIbex=1, cpuctrlsts.dummy_instr_en=1 with mask 000; RV32ZC=RV32ZcaZcbZcmp
(Zc macros); a stack area the TB can inspect; control run with dummies off.

## B9 dcsr.cause = 0 when debug_req_i drops during the FLUSH cycle (corner, out-of-spec stimulus)

Spec expectation. dcsr.cause (xml/core_registers.xml:236-242) "Explains why Debug Mode was
entered", encodings 1..6 with the priority table (haltreq = 3); 0 is not a defined cause. The debug
module holds haltreq until the hart halts (debug_module.adoc, haltreq semantics), so a request
that disappears before entry is out-of-spec stimulus.

RTL behaviour. debug_cause_d (rtl/ibex_controller.sv:519-523) is recomputed every cycle from
trigger_match_i, ebreak-into-debug, debug_req_i and do_single_step_d; the value written to dcsr is
the registered copy debug_cause_q (debug_cause_o = debug_cause_q, :533) consumed when the FSM
reaches DBG_TAKEN_IF (:764, debug_csr_save_o :774) or DBG_TAKEN_ID (:785, :806), written by
rtl/ibex_cs_registers.sv:914 dcsr_d.cause = debug_cause_i. When a special request (CSR access, fence, wfi, ...) is in ID the path is DECODE ->
FLUSH -> DBG_TAKEN_IF (:985-987), and if debug_req_i is low in the FLUSH cycle the cause written is
DBG_CAUSE_NONE (0). The RTL comment :515-518 acknowledges the window.

Minimal sequence (TB stimulus, Q-007 pulse-drop test):
```
# main (M): a loop of special-request instructions so a halt request is likely to land on one
1: csrr t0, mcycle
   fence
   j 1b
# TB: pulse debug_req_i high for exactly 1 cycle while a csrr/fence is in ID (gen_dut_top port,
#     TB knob), instead of the Q-007 level.
.section .debug_rom
  csrr t1, dcsr
  srli t1, t1, 6
  andi t1, t1, 7               # spec (level stimulus): 3; RTL with the 1-cycle pulse: 0
  sw   t1, result0
  dret
```
Discriminating observation. result0 = 0 (RTL) against 3; debug_mode_o rises although the request
was withdrawn. With the compliant level stimulus the RTL writes 3 (no bug).

Classification. RTL-defined corner under out-of-spec stimulus: no spec violation because the
stimulus is illegal; the test RECORDS the value (no expected_fail, no pass/fail on cause) and the
DV Lead decides whether the corner is logged as a robustness note. Severity: low.

Prerequisites. A TB knob for a pulsed debug_req_i (TB Infra); own .debug_rom; DUT only.

## B10 dcsr.cause = 2 (trigger) recorded on an ebreak entry when the NEXT instruction matches tdata2

Spec expectation. xml/core_registers.xml:236-242 and the dcsr cause priority table: trigger (2)
outranks ebreak (1) only when a trigger actually fires for that entry; the note in the same
register text: "an execute trigger with timing=after on an ebreak instruction is lower priority
than the ebreak itself because the trigger will fire after the ebreak instruction". An
execute-address trigger on the instruction AFTER the ebreak has not fired when the ebreak halts the
hart (Sdtrig.adoc:107 "Instruction address breakpoint ... execute address before" applies to the
instruction being executed, not to a prefetched one). Expected cause = 1 (ebreak), dpc = the
ebreak's address; the trigger fires later, after dret, when that instruction is about to execute.

RTL behaviour. debug_cause_d gives trigger_match_i top priority (rtl/ibex_controller.sv:519);
trigger_match = tmatch_control & (pc_if == tdata2) is evaluated on the IF-stage PC every cycle
(rtl/ibex_cs_registers.sv:1871-1874, "match against the next address"). While the ebreak is in ID
(ebrk_insn_prio & ebreak_into_debug -> DBG_TAKEN_ID, :875-883) pc_if holds the address of the
following instruction; if that equals tdata2, debug_cause_d = TRIGGER in that DECODE cycle, the
registered debug_cause_q (:533) is written in DBG_TAKEN_ID (:785, :806; rtl/ibex_cs_registers.sv:914)
as cause 2 while dpc = pc_id (the ebreak).
After dret the trigger fires again (cause 2, correctly).

Minimal sequence. The trigger CSRs are writable only in debug mode (rtl/ibex_cs_registers.sv:
1775-1780: tselect/tdata1/tdata2 write enables include debug_mode_i) and tdata1 has one writable
bit, execute (bit 2); type=2, dmode=1, action=1 (enter debug), m=1, u=1, match=equal are fixed
(:1847-1863). So the arming and the ebreakm bit are set by the debug ROM on a first debug_req_i
halt; Spike (no debugger) cannot run this part; the program is self-checking:
```
# main (M):
1: wfi                         # halt 1: TB asserts debug_req_i (level)
  j 1b                         # the debug ROM redirects dpc to seq on the first entry
seq:
  ebreak                       # halt 2: cause must be 1 (ebreak), dpc = seq
target:                        # = seq + 4 (or seq + 2 with c.ebreak); tdata2 points here
  nop                          # halt 3: trigger fires here: cause 2, dpc = target
  # ... store the recorded results to tohost, end
.section .debug_rom
  csrr t0, dcsr
  # entry counter kept in a scratch memory word; on entry 1: arm and configure
  #   csrw tselect, zero ; la t1, target ; csrw tdata2, t1 ; li t2, 0x4 ; csrw tdata1, t2
  #   li t3, 0x8000 ; or t0, t0, t3 ; csrw dcsr, t0   (ebreakm = 1)
  #   la t4, seq ; csrw dpc, t4
  # on entries 2 and 3: record (dcsr.cause = (t0 >> 6) & 7, dpc) into result slots
  dret
```
Discriminating observation. The sequence of (cause, dpc) pairs recorded by the debug ROM: spec
(1, ebreak_pc) then (2, target); RTL (2, ebreak_pc) then (2, target). Also rvfi_ext_debug_req /
debug_mode_o timing is identical, so the CSR value is the only discriminator.

Classification. Spec violation (cause misattribution; Q-004 default: checker follows the debug
spec, test expected_fail). Severity: low (debugger UX, no state corruption).

Prerequisites. DbgTriggerEn=1 (one trigger); ebreakm set by debug code on a prior halt (the
program cannot write dcsr outside debug mode); own .debug_rom; DUT only for the debug part.

## Summary table

| ID | Spec cite | RTL cite | Discriminator | Classification / policy | Prerequisite |
|---|---|---|---|---|---|
| BUG-01 | core_registers.xml:281-287 (mprven=0: MPRV ignored); Sdext.adoc:30-34, :76-78 | cs_registers.sv:826, :998; core.sv:1604 | debug-mode load of a U-denied/M-allowed word faults (RTL) vs succeeds (spec) | spec violation, Q-004: checker=spec, expected_fail | PMP region, debug_req_i level, .debug_rom |
| BUG-02 | machine.adoc:1521; security.rst:45 | id_stage.sv:1218-1220; wb_stage.sv:208-209; cs_registers.sv:1588; core.sv:1864, :1905 | minstret delta 65 (spec) vs 65 + dummies (RTL) | spec violation, Q-005: record, delta >= 65 | dummy_instr_en=1 |
| BUG-03 | core_registers.xml:163-174 (ebreaks hardwired 0 without S) | cs_registers.sv:811-836 (no ebreaks force), :551 | dcsr bit 13 reads back 1 | spec violation: checker=spec, expected_fail | debug entry, .debug_rom |
| BUG-04 | rvfi.rst:35-43, :53-58 | core.sv:1851-1853; controller.sv:278, :336-337, :833-840, :1122 | two trap records expected (store, then the re-executed illegal instruction); one record would re-open the bug | DOWNGRADED to RVFI convention note, confirmation test (normal pass/fail) | +define+RVFI, PMP-denied store, handler skips the store |
| BUG-05 | machine.adoc:392, :433 (WARL); cs_registers.rst:138 (doc) | cs_registers.sv:783-786 | MPP reads 0 (RTL) vs doc 3; mret target privilege | RTL-defined (spec-legal), Q-006: checker=RTL, doc defect logged | none |
| BUG-06 | Sdext.adoc:202 | cs_registers.sv:949-951 (compare :957-959) | U-mode load after dret succeeds with M privilege (RTL) vs faults (spec) | spec violation, Q-004: checker=spec, expected_fail | debug_req_i, PMP region, .debug_rom |
| BUG-07 | zcmp.adoc:151-163, :543, :735 | if_stage.sv:493, :526-530, :808-809; dummy_instr.sv:102-103, :115; compressed_decoder.sv:640-670, :723-753 | wrong register/stack value after push/pop with dummies on; rlist-1 stores on the bus | spec violation: checker=spec, expected_fail (control with dummies off passes) | dummy_instr_en=1, Zc macros |
| B9 | core_registers.xml:236-242 (cause encodings); haltreq held until halt | controller.sv:515-531, :985-987; cs_registers.sv:914 | dcsr.cause 0 after a 1-cycle debug_req_i pulse on a special-request instruction | RTL-defined corner under illegal stimulus: record only | pulsed debug_req_i knob |
| B10 | core_registers.xml:236-242 + timing note; Sdtrig.adoc:107 | controller.sv:519, :875-883; cs_registers.sv:1871-1874 | (cause, dpc) = (2, ebreak_pc) instead of (1, ebreak_pc) | spec violation: checker=spec, expected_fail (low) | trigger armed on ebreak+4, ebreakm via debug code |

What the DV Lead needs: the classification column above feeds the bug log and the expected_fail
marks; BUG-01/06 share one program and one PMP region; BUG-07 needs its control run (dummies off)
in the same test entry. What the Test Writer needs: the .debug_rom override mechanism and a TB knob
for the B9 pulse (TB Infra); the cpuctrlsts guard for Spike runs (custom CSR 0x7c0 is unknown to
Spike); the result-buffer convention the TB compares.

## BUG-08 (candidate, added 2026-09-03 by T-053) Misaligned load with an integrity error on the first beat still writes rd

- Class: RTL less complete than the documented intent (security feature). Security-relevant:
  owner question recommended (same shape as Q-008).
- Spec / doc: the RISC-V specifications do not define bus integrity; doc/03_reference/security.rst:88
  "Where load data has bad checkbits the write to the load's destination register will be
  suppressed."
- RTL: rtl/ibex_load_store_unit.sv:514 `lsu_err_d = data_bus_err_i | pmp_err_q` (the first-half
  status has no integrity term); :697-698 `lsu_rdata_valid_o = (ls_fsm_cs == IDLE) & data_rvalid_i &
  ~data_or_pmp_err & ~data_we_q & ~data_intg_err` (the RF write is gated only by the integrity of
  the beat that completes the access); :756 load_resp_intg_err_o (alert on every corrupt beat);
  rtl/ibex_controller.sv:402-438 (internal NMI pending flag); rtl/ibex_core.sv:2384-2385
  (rvfi_ext_rf_wr_suppress = instr_done_wb & lsu_load_resp_intg_err, i.e. only for the completing
  beat).
- Instruction sequence (M-mode, mtvec handler records mcause/mtval, MemECC = 1):
  1. `la x6, buf` with buf word-aligned; `lw x5, 2(x6)` (EA = buf + 2, two bus beats: word(buf) with
     be 1100 then word(buf + 4) with be 0011).
  2. The data agent corrupts the integrity bits [38:32] of the FIRST rvalid beat only; data_err_i =
     0 on both beats.
  3. `sw x5, 0(x7)` to a signature location; the handler at the NMI vector (mtvec + 0x7C) records
     mcause and mtval.
- Expected per doc: rvfi_rd_addr = 0 and rvfi_ext_rf_wr_suppress = 1 on the lw record (x5
  unchanged), alert_major_bus_o one pulse in the corrupted rvalid cycle, internal NMI with mcause
  0xFFFF_FFE0.
- RTL: rvfi_rd_addr = 5, rvfi_ext_rf_wr_suppress = 0, x5 = the merged (corrupted-half) data; the
  alert and the NMI fire as expected. The signature store carries the corrupt data.
- Control (both agree): the same sequence with the SECOND beat corrupted -> rd write suppressed,
  rvfi_ext_rf_wr_suppress = 1. Aligned loads: the single beat is the completing beat, suppression
  works.
- Observation point: the lw RVFI record (rvfi_rd_addr, rvfi_ext_rf_wr_suppress), alert_major_bus_o,
  the NMI handler's mcause/mtval read-backs.
- Spike: no integrity model; the comparator must be told the beat class (TB-side prediction).
- Marking: expected-fail for the first-beat class only (TP-DMEM-041, TP-SEC-008, TP-RVFI-024
  variants), pass for the aligned and second-beat classes. Unverified in simulation.

## BUG-09 (candidate, added 2026-09-03 by T-053) NumBranches / mul-wait / div-wait over-count while a WB memory access is outstanding

- Class: RTL-defined counter semantics that contradict the documented meaning; the DV Lead decides
  between D-tag (Q-006) and bug candidate.
- Doc: doc/03_reference/performance_counters.rst:41 "NumBranches: Number of branches
  (conditional)"; :45-47 mul/div wait cycles.
- RTL: rtl/ibex_id_stage.sv:886-934 perf_branch_o = 1 in the FIRST_CYCLE arm under
  instr_executing_spec; :1054-1057 instr_executing_spec has no ~outstanding_memory_access term;
  :866-869 id_fsm_q advances only under instr_executing (which has the term, :1059-1062); so a
  branch that is valid in ID while the WB load/store still awaits its response asserts perf_branch_o
  in every waiting cycle. branch_set / jump_set are deduped by branch_jump_set_done_q (:806-815), so
  counters 7 and 9 are exact. :1226-1227 perf_mul_wait_o / perf_div_wait_o = stall_multdiv &
  *_en_dec count every cycle a mul/div waits to start behind the outstanding access (mult_en_id /
  div_en_id are 0 while not executing, :733-734).
- Instruction sequence (M-mode, mcountinhibit = 0, dummy_instr_en = 0):
  `csrr t0, mhpmcounter8 ; lw x7, 0(x8) ; beq x9, x10, skip ; nop ; skip: csrr t1, mhpmcounter8`
  with x9 != x10 and the data agent holding data_rvalid_i for K >= 4 cycles after the grant
  (knob dmem_rvalid_delay = K).
- Expected per doc: t1 - t0 = 1.
- RTL: t1 - t0 = 1 + (number of cycles the beq was valid in ID while the lw was outstanding),
  about K - 1.
- Control: insert enough independent ALU instructions between the lw and the beq (or use
  dmem_rvalid_delay = 1) so the response has arrived before the beq enters ID -> delta = 1.
- Observation point: csrr read-backs on rvfi_rd_wdata; rvfi_ext_mhpmcounters[5] on the beq record.
- Spike: counts 1; the comparator must use the bound class for counters 8/11/12 whenever a
  branch/mul/div follows an outstanding WB access.
- Marking: DV Lead decision (D-tag pass or expected-fail). Unverified in simulation.

## BUG-10 (RVFI-only candidate, added 2026-09-03 from TB Infra's first lock-step run) rvfi_mem_rmask is non-zero and rvfi_mem_addr is the ALU result on every record that is not a store

- Class: RVFI convention defect (no architectural effect; affects the comparator and the RVFI
  protocol checker). B15-class like the other RVFI-only entries.
- Spec: tools/specs/riscv-formal/docs/source/rvfi.rst:135-136 "For memory operations
  (rvfi_mem_rmask and/or rvfi_mem_wmask are non-zero), rvfi_mem_addr holds the accessed memory
  location" and :143-144 "rvfi_mem_rmask is a bitmask that specifies which bytes in
  rvfi_mem_rdata contain valid read data from rvfi_mem_addr": a non-zero rmask declares a memory
  read, so it must be zero on instructions that read no memory.
- RTL: rtl/ibex_core.sv:2085 `rvfi_stage_mem_rmask[i] <= data_we_o ? 4'b0000 : rvfi_mem_mask_int`
  and :2253-2260 `rvfi_mem_mask_int` decoded from lsu_type alone (default 2'b00 -> 4'b1111), with
  no qualifier on an LSU request; :2086 `rvfi_stage_mem_wmask[i] <= data_we_o ? rvfi_mem_mask_int
  : 4'b0000`; rvfi_mem_addr = alu_adder_result_ex on every record (:2207-2209, gen_tp_parts_rtl_
  factcheck.md X-15 / TP-RVFI-014 caveat / TP-RVFI-029). data_we_o = lsu_we_i
  (rtl/ibex_load_store_unit.sv:723) = the decoder's data_we_o, which is 1 only for store opcodes
  (rtl/ibex_decoder.sv:284 default 0, :397 store arm): it is DECODE-qualified, not
  request-qualified, so wmask is clean on every non-store record because no other opcode decodes
  data_we = 1, while rmask is 4'b1111 (or 0011 / 0001 for whatever lsu_type the word happens to
  decode to) on every non-store, non-load record. Masks are zeroed only for WB traps (:2156-2157).
- Instruction sequence: any non-memory instruction, e.g. `lui x1, 0x80000` at a known pc; observe
  its RVFI record.
- Expected per RVFI: rvfi_mem_rmask = 0, rvfi_mem_wmask = 0 (rvfi_mem_addr then unconstrained).
- RTL: rvfi_mem_rmask = 4'b1111, rvfi_mem_wmask = 0, rvfi_mem_addr = the ALU adder result of that
  instruction, rvfi_mem_rdata = the last load's data (held register).
- Observation point: the RVFI record (TB Infra's GEN_SB counter rvfi_rmask_on_nonload already
  counts it; out_2a run, order 5 pc 0x8000008e).
- Marking: RVFI-only bug candidate; the comparator infers reads from the model's own access and
  applies the mask rules only to decoded load/store records (as the scoreboard now does); the
  rvfi_proto row cites this id. No expected-fail on any architectural item.


## BUG-11 (RVFI-only candidate, added 2026-09-03 from the T-053 isa_a note and the DV Lead's B19) rvfi_trap is masked on an ILLEGAL ebreak variant when dcsr.ebreakm/ebreaku is set

- Class: RVFI convention defect, same family as BUG-04 / BUG-10 (no architectural effect: the trap is
  taken correctly; only the trace field is wrong). DV Lead id B19; plan item TP-ISA-057 (informational).
- Spec: riscv-formal rvfi.rst: rvfi_trap marks an instruction that trapped; an illegal-instruction
  exception (mcause 2) is a trap.
- RTL: rtl/ibex_decoder.sv:739-740 sets ebrk_insn_o = 1 for funct12 0x001 whatever rs1/rd hold, and
  :757-759 sets illegal_insn = 1 when instr_rs1 != 0 or instr_rd != 0 (the illegal block :912-920
  clears rf_we/data_req/jump/branch/csr_access but not ebrk_insn_o). rtl/ibex_controller.sv:312-332:
  illegal_insn_q takes priority over ebrk_insn, so the exception is ExcCauseIllegalInsn (mcause 2,
  mtval = the encoding, :864-868) and the PC goes to mtvec, not to the debug ROM. rtl/ibex_core.sv:
  1885-1886: rvfi_trap_id = id_exception & ~(id_stage_i.ebrk_insn & ebreak_into_debug), and
  ebreak_into_debug = dcsr.ebreakm in M / dcsr.ebreaku in U (rtl/ibex_controller.sv:481): with the
  matching dcsr bit set, the record of the illegal ebreak variant carries rvfi_trap = 0 although it
  trapped with mcause 2. With the dcsr bit clear rvfi_trap = 1 (correct).
- Instruction sequence (M-mode, mtvec handler records mcause/mtval and returns past the instruction):
  1. csrw dcsr is not writable outside debug mode; enter debug mode (debug_req_i), set dcsr.ebreakm = 1
     in the debug ROM, dret.
  2. `.word 0x00100173` (ebreak encoding with rd = x2: funct12 0x001, rs1 = 0, rd = 2) at a known pc.
  3. The handler reads mcause (expect 2) and mtval (expect 0x00100173) and skips the instruction.
- Expected per RVFI: the record of the .word has rvfi_trap = 1, rvfi_insn = 0x00100173, next record at
  mtvec base.
- RTL: same record with rvfi_trap = 0; mcause 2 and mtval as expected; execution continues at mtvec.
- Control (both agree): the same .word with dcsr.ebreakm = 0 gives rvfi_trap = 1; a legal ebreak
  (0x00100073) with ebreakm = 1 enters debug mode with rvfi_trap = 0 (known S-2 behaviour) and no mcause
  update.
- Observation point: the RVFI record and the handler's csrr read-backs on rvfi_rd_wdata.
- Spike: traps with cause 2; the comparator must not use rvfi_trap alone to detect the trap for
  ebreak encodings with rs1/rd != 0 when ebreakm/u is set (derive from the pc discontinuity / next
  record at mtvec, as for S-2).
- Marking: RVFI-only bug candidate (checker classifies the record by pc flow); no expected-fail on an
  architectural item. Unverified in simulation.
