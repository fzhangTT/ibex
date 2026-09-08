# Bug log - Ibex core, opentitan configuration

Part-file names in this document (tp_<area>.md, fcov_<area>.md, gen_part_<area>.md, trace_*_<area>.csv and the README_*_BRIEF.md briefs) are this plan set's own gitignored sources, named as provenance: the content they hold is in the corresponding area of gen_test_plan.md, gen_fcov_plan.md or gen_feature_list.md, and the bug and doc-defect number series they define are in gen_bug_log.md. No claim in this document rests on opening one. Three rtl-arch notes this plan set cites are committed references, not work files: dv/auto_dv/evidence/gen_multdiv_bound_props.md (the MD-n bound properties and covers), dv/auto_dv/evidence/gen_bug_reproducer_specs.md (the reproducer recipes behind the bug log) and dv/auto_dv/evidence/gen_interface_inventory.md (the numbered driver and protocol rules); citations name them by basename and resolve there.

Deliverable 7 (DV_prompt.txt Section 11). Owner: dv-lead. Version 2, 2026-09-08 01:25 UTC (version 1 was
2026-09-03 06:58 UTC; the change log is Section 4). This document lists every place where the Ibex core, as
built in the opentitan configuration, behaves differently from the RISC-V specifications or from its own
documentation. Entries were opened by the DV Lead from the feature list, the reading report and rtl-arch's
behaviour summaries (the Part A ids BUG-01..BUG-11 are kept as aliases). Rules that apply to every entry:

- An entry is a CANDIDATE until a committed reproducer log exists. A reproduced entry says so and names the
  retained log.
- DV never modifies the RTL. A candidate leaves the pass gate only through a recorded owner ruling
  (DV_prompt.txt Section 10; owner questions Q-004 and Q-005 in dv/auto_dv/docs/gen_intervention_log.md).
  The owner's standing answer on handling is LOG-097 addendum (2026-09-05): the tests for bug candidates
  should fail, and the flow expects them to fail (the expected_fail mechanism).
- Defects of the verification environment itself (testbench, tests, harness) are NOT in this file. They are
  in dv/auto_dv/evidence/gen_tb_defects.md. A reader who finds no testbench entries here should look there.

## 0. How to read this document

### 0.1 Glossary

Each term is expanded once here and then used freely.

- CSR: control and status register, read and written with the csrr / csrw / csrs instructions.
- M-mode, U-mode: machine mode (the most privileged mode) and user mode. This core has no S-mode
  (supervisor mode).
- mstatus.MPRV, mstatus.MPP: two fields of the mstatus CSR. MPP holds the privilege mode to return to on
  mret. When MPRV is 1, loads and stores are checked with the privilege named by MPP instead of the current
  privilege.
- PMP: physical memory protection. Up to 16 regions (pmpcfg / pmpaddr CSRs) allow or deny fetches, loads
  and stores per privilege mode.
- Debug mode: the mode a debugger puts the core into. Entered by the debug_req_i pin, by ebreak when
  dcsr.ebreakm or dcsr.ebreaku is set, by a trigger match, or by single step. The core then runs code at
  DmHaltAddr (the debug ROM); exceptions inside debug mode go to DmExceptionAddr. dret leaves debug mode.
- dcsr, dpc: the debug control CSR (fields: cause, prv, ebreakm, ebreaku, ebreaks, nmip, mprven, step) and
  the debug program counter (where dret resumes).
- Trigger CSRs: tselect, tdata1, tdata2, tdata3, mcontext, scontext, mscontext. tdata1 / tdata2 arm an
  execute-address breakpoint that enters debug mode.
- mcause, mtval, mepc: the CSRs written on a trap: the cause code, the trap value (for example the faulting
  address or the illegal encoding), and the return address.
- minstret: the CSR counting retired instructions. mcycle counts cycles.
- HPM counters: the hardware performance monitor counters mhpmcounter3..12. Ibex assigns a fixed event to
  each (doc/03_reference/performance_counters.rst): 5 NumLoads, 6 NumStores, 7 NumJumps, 8 NumBranches,
  9 NumBranchesTaken, 11 NumCyclesMulWait, 12 NumCyclesDivWait.
- mcountinhibit: the CSR whose bits stop individual counters.
- cpuctrlsts: Ibex's custom CSR (0x7C0) holding the security controls: dummy_instr_en, dummy_instr_mask,
  data_ind_timing, sync_exc_seen, double_fault_seen and the icache enable.
- Dummy instructions: a SecureIbex feature (cpuctrlsts.dummy_instr_en). The fetch stage inserts random
  instructions that write no register, to hide timing. They are not part of the program.
- DIT: data-independent timing (cpuctrlsts.data_ind_timing). When set, branches always take the same time
  whether taken or not.
- Zcmp: the compressed push / pop instructions (cm.push, cm.pop, cm.popret, cm.popretz, cm.mvsa01,
  cm.mva01s). Ibex expands each one into a sequence of micro-ops (several stores or loads plus a stack
  pointer update).
- NMI: non-maskable interrupt (the irq_nm_i pin). Internal NMI: the NMI the core raises itself on a bus
  integrity error.
- WFI: the wait-for-interrupt instruction.
- Bus integrity: with MemECC the data and instruction buses carry 7 check bits beside the 32 data bits. A
  corrupted response raises alert_major_bus_o and an internal NMI.
- Misaligned access, beats: a load or store whose address is not a multiple of its size. Ibex splits it into
  two bus transactions (two beats).
- LSU: the load-store unit (rtl/ibex_load_store_unit.sv). ID and WB: the decode stage and the writeback stage
  of the pipeline. IF: the fetch stage.
- RVFI: the RISC-V formal interface. A per-instruction trace port the core exposes (rvfi_valid, rvfi_pc_wdata,
  rvfi_trap, rvfi_mem_rmask and so on). The testbench compares it with the ISA model. RVFI-only means the
  trace is wrong but the core's real state is right.
- Spike, the reference model (also called the ISA model): upstream riscv-isa-sim, the clone's own copy under
  tools/riscv-isa-sim/ (an allowed upstream project, not the fenced cosim fork). The lock-step comparator runs
  it instruction by instruction beside the core and compares every retired instruction (the gen_isa_compare rows isa_pc,
  isa_insn, isa_trap, isa_rd, isa_mem, isa_prv, isa_pc_next, isa_csr in dv/auto_dv/env/gen_rvfi_pkg.sv).
  A mismatch is a collected UVM_ERROR tagged with the row name, for example [isa_trap].
- TB: the testbench. Checker: a testbench component that predicts a value and raises a collected error on a
  mismatch. A checker "follows the specification" when it predicts what the specification says; it "follows
  the RTL" when it predicts what the RTL does.
- Expected-fail, XFAIL: a test whose testlist entry carries expected_fail: true. The flow reports its failure
  as XFAIL (the verdict for a known bug) and reports an unexpected PASS as FAIL (dv/auto_dv/flow/gen_verdict.py).
- TP item: a test-plan item in dv/auto_dv/docs/gen_test_plan.md (TP-<AREA>-<nnn>). Feature: an entry of
  dv/auto_dv/docs/gen_feature_list.md (F-<AREA>-<nnn>).
- D entry: a documentation defect (Section 3). S entry: a security-relevant RTL-defined behaviour that the
  owner decides on (Section 2). Retained ID: a B number that turned out not to be a bug but is kept so old
  references resolve (Section 1b).
- FSDB: the waveform file (Verdi format) a run with --waves writes. URG: the coverage report tool.
- WARL: write-any-read-legal, a CSR field that turns an illegal written value into a legal one.
- Spec cites: tools/specs/ holds the RISC-V unprivileged and privileged manuals, the debug specification
  (Sdext.adoc, Sdtrig.adoc, xml/core_registers.xml) and the RVFI definition (riscv-formal rvfi.rst).
  doc/03_reference/*.rst is the Ibex documentation.

### 0.2 Impact rating (owner definitions of 2026-09-07)

- P1: an actual bug that will cause an issue with functionality. Applied as: wrong architectural state or a
  wrong execution path that software cannot avoid without giving up a feature, or cannot detect.
- P2: an actual bug that can be avoided with a workaround, such as adding a delay, using another instruction
  sequence, writing a CSR first, or turning an optional mode off while measuring.
- P3: undefined or no-impact behaviour. Applied as: the specification leaves the case undefined or
  implementation-defined; or only a trace field or a status field is wrong and execution and state are
  right; or the Ibex documentation is what is wrong.

Every B, S and D entry carries a rating with one line of justification. Two ratings are marked "pending
rtl-arch confirmation" (B10, B16) because the committed RTL facts records do not settle the point the rating
rests on; rtl-arch was not running when this version was written.

### 0.3 Effort classes for a quick test (item 5 of the owner request)

Given for every entry that has no test yet. They rest on what the testbench has today: the lock-step ISA
comparator (built), the debug-request and NMI stimulus through the cocotb bridge (built: DBG_REQ, NMI_PULSE,
MEM_ERR_ARM commands, dv/auto_dv/docs/gen_component_api_bridge.md), directed programs that may carry their
own debug ROM (dv/auto_dv/stim/gen_program.py links a program's .debug_rom section in place of the stub), the
irq and debug checkers (built: dbg_entry, dbg_dret, dbg_masked, nmi_entry, nmi_internal in
dv/auto_dv/env/gen_checkers_pkg.sv). NOT built at HEAD: the counter model (gen_chk_counters / ctr_*), the CSR
read-back predictor (gen_chk_csr_readback), the PMP model (gen_chk_pmp) and the bus-integrity response checker
(gen_chk_bus_intg_rsp) that several plan items name; their API documents describe the plan, not code.

- S: under half a day. An existing test module (gen_ut_lockstep, gen_ut_dbg or gen_ut_intg_span) plus one
  directed program and one testlist entry with expected_fail: true; the built ISA comparator is the checker.
- M: one to two days. A new checker rule in the testbench, or a new stimulus, or a directed program with
  several cooperating parts (PMP setup, a debug ROM, U-mode code, a trap handler) that must run under
  lock-step with the model.
- L: more than two days. A new testbench capability, such as the whole counter model.

Each scoping names (a) what must exist, (b) what it extends, (c) who builds it (test-writer or tb-infra),
(d) the class and why. Evidence bar for these tests (owner directive LOG-103, 2026-09-08): a retained red run
(for an expected-fail bug test, the XFAIL verdict on the RTL with its failure signature) and a retained green
control run, plus a waveform confirmation with the FSDB path recorded; no mutation proof, seed sweep or
fcov-expectation manifest is required for them.

### 0.4 Test commands

The flow's reproduction form (dv/auto_dv/docs/gen_runtime_api.md Section 3; docs/dv/SIM_RECIPE.md Section 6
for waves) is

    python3 dv/auto_dv/flow/gen_regress.py --repro <test> <seed> --waves --tag <tag>

It compiles a waves build if needed, runs the one test and seed on LSF (add --local to run on this host),
and writes the run under <out root>/regress_<tag>/runs/<test>_<seed>/. The out root is GEN_DV_OUT_ROOT, else
out_root in dv/auto_dv/work/runtime/gen_site.yaml (the team's was /proj_soc/user_dev/fzhang/ibex_dv_out), else
dv/auto_dv/work/runtime/out. In that run directory: sim.log (the simulator log with the UVM_ERROR lines),
verdict.txt (PASS / FAIL / XFAIL and the first collected failure line), and waves.fsdb (waves.vpd when
VERDI_HOME is not set). The regression summary is <out root>/regress_<tag>/manifest.yaml.

"Fail loud" means: the run's verdict is decided by a collected mechanism, a UVM_ERROR from a checker or a
Python assertion in the cocotb test, quoted in verdict.txt. For a bug candidate with expected_fail: true the
verdict reads XFAIL; that is the designed outcome, and a PASS would mean the behaviour changed. Every test
name in a command below exists in dv/auto_dv/flow/gen_testlist.yaml. A test the plan names but the testlist
does not carry is written "proposed test to build: <plan test group>".

### 0.5 Summary table

Status: "candidate" means not yet reproduced in simulation; "reproduced" means a retained log shows it.
Effort is the class of Section 0.3 for the entries with no test yet; "-" where a test exists or none is owed.
Citing into this document: cite an entry by its heading text ("### B4:") or, for a Section 2 or Section 3 row, by the
section and the row label ("Section 3, row | D20 |"); a bare row label matches this summary table too, so it is never
a citation target on its own. Anchor text does not move when lines do; a line number does.

| Id | Short name | Rating | Status | Test | Effort |
|---|---|---|---|---|---|
| B1 | dret to U-mode leaves mstatus.MPRV set | P2 | candidate | no test yet | M |
| B2 | MPRV applied to debug-mode loads and stores although dcsr.mprven is 0 | P2 | reproduced | gen_prv_debug_b2_xfail seed 1 (XFAIL) | - |
| B3 | unimplemented trigger CSRs read 0 instead of trapping | P3 | candidate | no test yet | S (two CSRs) / M (all four) |
| B4 | reserved cm.mvsa01 encoding (r1s' == r2s') executes | P3 | reproduced | gen_ut_lockstep_zcmp_mv_reserved seed 1 (XFAIL) | - |
| B5 | dcsr.nmip never reports a pending NMI | P3 | candidate | no test yet | M |
| B7 | dummy instructions are counted in minstret and the wait counters | P2 | reproduced | gen_pmc_minstret_xfail seed 1 (XFAIL) | - |
| B8 | a dummy instruction inside a Zcmp push / pop corrupts registers or the stack | P1 | reproduced, cause stated | gen_ut_lockstep_zcmp_dummy seed 1 (XFAIL) | - |
| B10 | ebreak entry records cause 2 when the next instruction matches the trigger | P2 (pending rtl-arch) | candidate | no test yet | M |
| B11 | NumBranchesTaken counts not-taken branches under DIT | P2 | candidate | no test yet | M |
| B13 | RVFI next-PC keeps bit 0 on jalr to an odd target | P3 | observed (retained logs) | gen_test_isa_cti passes by policy; raw-rule red retained | - |
| B14 | RVFI drops the ID trap record when a WB error coincides (downgraded) | P3 | downgraded, confirmation pending | no test yet | S |
| B15 | dcsr.ebreaks is writable although there is no S-mode | P3 | candidate | no test yet | S |
| B16 | misaligned load with a bad first beat still writes rd | P2 (pending rtl-arch) | candidate, measured by tb-infra | no test yet | S (program and knob) / M (the suppression rule) |
| B17 | counters 8, 11, 12 over-count while a load or store is outstanding | P2 | candidate | no test yet | M |
| B18 | RVFI read mask and address set on every non-store record | P3 | observed (retained logs) | passes by policy | - |
| B19 | RVFI trap flag cleared on an illegal ebreak variant | P3 | candidate | no test yet | S |
| B20 | fence.i is counted as a jump | P2 | candidate | no test yet | M |
| B6 | exception in debug mode forces M privilege | P3 | not a bug (RTL-defined) | TP-EXC-046, TP-DBG-034 pass | - |
| B9 | a debug request that drops in the FLUSH cycle records cause 0 | P3 | RTL-defined corner, out-of-spec stimulus | record only | - |
| B12 | mret clears cpuctrlsts.sync_exc_seen | P3 | documented behaviour, design note | items pass with the note | - |
| B21 | fetch address is combinational from the interrupt inputs | P3 | RTL-defined property (S6); the observed divergence was TB defect T3 | recorded only | - |
| S1 | second half of a misaligned access issued after a first-half PMP fault | P3 | owner decision (Q-DL-7) | covered as RTL-defined | - |
| S2 | trap and debug entry proceed while fetch_enable_i is not On | P3 | owner decision (Q-DL-8) | checked as-is | - |
| S3 | no defence against unsolicited rvalid | P3 | owner decision (Q-DL-9) | informational test | - |
| S4 | mret clears sync_exc_seen (B12) | P3 | documented | items pass with the note | - |
| S5 | a masked duplicate-copy icache corruption reports nothing | P3 | documented gap (D22) | covered as a no-alert case | - |
| S6 | fetch address combinational from interrupt inputs (B21) | P3 | recorded, unguarded | none | - |
| D1 | mip reads the raw pins | P3 | doc defect | checker follows the RTL | - |
| D2 | illegal MPP legalises to U, doc says M | P3 | doc defect | checker follows the RTL | - |
| D3 | mcause is software-writable | P3 | doc defect | checker follows the RTL | - |
| D4 | tdata1 reset value 0x2800_1048 | P3 | doc defect | checker follows the RTL | - |
| D5 | retired (became B15) | - | retired | - | - |
| D6 | misaligned accesses counted once | P3 | doc defect | checker follows the RTL | - |
| D7 | divide latency wording | P3 | doc defect | checker follows the RTL | - |
| D8 | bfp is single-cycle | P3 | doc defect | checker follows the RTL | - |
| D9 | icache.rst port and RAM width text stale | P3 | doc defect | checker follows the RTL | - |
| D10 | mtval on an instruction access fault | P3 | doc defect | checker follows the RTL | - |
| D11 | early multiplier completion text stale | P3 | doc defect | checker follows the RTL | - |
| D12 | trigger CSR access outside debug mode | P3 | doc defect | checker follows the RTL | - |
| D13 | fence.i and a pending scramble key request | P3 | doc defect | checker follows the RTL | - |
| D14 | instruction-side integrity error gives no NMI | P3 | doc defect | checker follows the RTL | - |
| D15 | CSR table omits implemented CSRs | P3 | doc defect | checker follows the RTL | - |
| D16 | counter parameter text stale | P3 | doc defect | checker follows the RTL | - |
| D17 | separate integrity ports do not exist | P3 | doc defect | checker follows the RTL | - |
| D18 | tselect parameter name and scontext address | P3 | doc defect | checker follows the RTL | - |
| D19 | dummy_instr_mask table incomplete | P3 | doc defect | checker follows the RTL | - |
| D20 | mhpmeventN encoding | P3 | doc defect | checker follows the RTL | - |
| D21 | up to two instructions retire before the internal NMI | P3 | doc defect, to be confirmed | checker follows the RTL | - |
| D22 | icache duplicate-way text | P3 | doc defect | checker follows the RTL | - |

### 0.6 Policies (rulings, kept from version 1)

Checker direction (docs/dv/dv_principles.md Section 4). Where the RTL contradicts a RISC-V specification, the
checker follows the specification and the carrying test-plan items are `expected-fail (Bn)`. Where the RTL is
legal under the specification and only the Ibex documentation disagrees, the checker follows the RTL and the
item is `pass (doc mismatch Dn)`.

B-versus-D criterion, for a discrepancy between the RTL and the Ibex documentation only (no RISC-V
specification text applies). It is a doc defect (D) when the RTL behaviour is a self-consistent,
timing-independent convention that the documentation mis-describes: a value, an encoding, a count
convention, a latency bound (D6 misaligned accesses counted once, D20 mhpmevent encoding, D21 NMI latency).
It is a bug candidate (B) when the RTL behaviour depends on pipeline timing, so the same program yields
different architectural results (B17: the branch count depends on whether a WB access is outstanding), or
when it violates a documented functional or security intent (B7 dummies in minstret; B16 rd written on a
bad first beat; B11: NumBranchesTaken counts a not-taken branch under one configuration, which is a wrong
event and not a convention, unlike D6 where the doc merely mis-states the RTL's uniform counting convention
for misaligned accesses). The checker follows the RTL for a D and the documentation for a B.

How a checker carries a known candidate without failing every ordinary run (the B13 convention, LOG-032, applied to
the counter rules by the DV Lead's ruling of 2026-09-08 on tb-infra's counter cut, dv/auto_dv/work/tb-infra/
gen_counter_cut_2026-09-08.md Section 2). "The checker follows the documentation for a B" states the rule the bug's
expected-fail test enforces, not the default of every run. Where the candidate occurs in ordinary traffic (B17: counter 8
over-counts in every run with realistic bus latency; B11 under DIT; B20 on every fence.i; B13 on every odd jalr target)
the checker's default follows the RTL, COUNTS each accommodated interval or record per bug and reports the counts at
the end of the run so nothing is silent, and a knob selects the documentation rule; the bug's expected-fail test alone
runs with that knob set, and that run is the loud failure. The knobs of one family share one sense (the same value
selects the documentation rule on all of them) and are named in the component's API document. A run whose accommodation
count is nonzero met the candidate; a run whose count is zero did not exercise it.

## 1. Bug candidates (RTL against a specification or against documented intent)

Entry layout: rating; status; the feature by name with its id; the plan items that expect the failure; the RTL
and specification cites (the evidence chain, unchanged from version 1); what happens; steps to reproduce; the
test command or the scoping of a quick test; evidence; notes.

### B1: dret to U-mode leaves mstatus.MPRV set
- Rating: P2. The behaviour breaks the debug specification and is security-relevant (U-mode code then runs its
  loads and stores with the MPP privilege, possibly M), but the debugger controls the state: clearing
  mstatus.MPRV before dret avoids it.
- Status: candidate, reproducer pending
- Feature: dret to U-mode does not clear mstatus.MPRV, so U-mode loads/stores can run with MPP (possibly M)
  privilege (F-PRV-015, canonical); aliases F-DBG-033, F-PMP-075
- Plan items (expected-fail): TP-PRV-014, TP-DBG-038, TP-PMP-073
- rtl-arch alias: BUG-06 (rtl-arch T-017; static confirmation against Sdext.adoc:202; reproducer recipe in
  gen_bug_reproducer_specs.md BUG-06)
- RTL: rtl/ibex_cs_registers.sv:949-951 (csr_restore_dret_i restores priv_lvl only; compare mret :953-959 which clears MPRV when MPP != M)
- Specification / intent: riscv-debug-spec Sdext.adoc:202 (Resume: "If the new privilege mode is less privileged than M-mode, MPRV in mstatus is cleared")
- What happens: when the debugger resumes the core into U-mode with dret, the RTL restores only the privilege
  level and leaves mstatus.MPRV as it was. If MPRV was 1 with MPP = M, the U-mode program's loads and stores
  are checked by the PMP with M privilege. The specification says dret must clear MPRV when it resumes to a
  less privileged mode. mret does this; dret does not.
- Steps to reproduce:
  1. Set up (M-mode): program one PMP region that denies U-mode and does not check M-mode for a data word X
     (L = 0, R = W = X = 0). Set mstatus.MPRV = 1 and MPP = M. Park in a loop.
  2. Do: assert debug_req_i (held until the core halts). In the debug ROM set dcsr.prv = U and dpc to a U-mode
     routine, then dret. The U-mode routine loads X.
  3. RTL: MPRV is still 1 with MPP = M, so the load is checked with M privilege and completes without a fault.
  4. Specification: MPRV is cleared by the resume to U, the load is checked with U privilege and raises a load
     access fault (mcause 5).
  5. Control: the same sequence with MPRV = 0 faults on both.
- Test: No test yet. Proposed test to build: plan test group gen_prv_debug_b1_xfail (TP-PRV-014), with
  expected_fail: true. Scoping: (a) a directed program with four cooperating parts (the PMP setup, its own
  .debug_rom section that writes dcsr.prv and dpc, the U-mode probe, an M-mode trap handler that records
  mcause and ends the test) and a cocotb module that sends DBG_REQ once the program is parked; (b) extends
  gen_ut_dbg (dv/auto_dv/gen_tb/gen_tests/gen_ut_dbg.py already sends DBG_REQ through the bridge and asserts
  zero ISA mismatches) and the directed-program flow (gen_program.py links a program's own .debug_rom in place
  of the stub); (c) test-writer; (d) M: no new testbench capability is needed, because the ISA model clears
  MPRV on a dret to a lower privilege (tools/riscv-isa-sim/riscv/insns/dret.h), so the model faults the U-mode
  load while the core does not and the comparator raises [isa_trap]; but the program has four parts that must
  agree with the model under lock-step, and the model's debug-entry step must be shown to carry the dcsr.prv
  change (gen_ut_dbg only runs a ROM that drets at once).
- Evidence: none yet.
- Notes: security-relevant (U-mode loads and stores use the MPP privilege for PMP checks until the next trap
  or mret). Pair with B2 in one program: the same PMP region serves both probes (gen_bug_reproducer_specs.md).

### B2: mstatus.MPRV is applied to debug-mode loads and stores although dcsr.mprven is hardwired 0
- Rating: P2. A specification violation with a security angle (a debugger cannot rely on M privilege while
  MPRV is set), but the debugger can clear MPRV before its memory accesses and restore it before dret.
- Status: REPRODUCED by test-writer (dv/auto_dv/evidence/gen_tdd_bug_tests.md Section 1: retained red and green runs and a waveform confirmation, LOG-103); still a candidate for the owner ruling
- Feature: mstatus.MPRV is honoured for data accesses in debug mode although dcsr.mprven=0 (F-DBG-055,
  canonical); alias F-PMP-076
- Plan items (expected-fail): TP-PRV-035, TP-DBG-060, TP-PMP-074
- rtl-arch alias: BUG-01 (recipe gen_bug_reproducer_specs.md BUG-01)
- RTL: rtl/ibex_cs_registers.sv:826 (dcsr_d.mprven = 0), :998 (priv_mode_lsu_o = mprv ? mpp : priv_lvl_q, no debug_mode term); consumer rtl/ibex_core.sv:1603-1604
- Specification / intent: riscv-debug-spec core_registers.xml dcsr.mprven: 0 = MPRV in mstatus is ignored in Debug Mode
- What happens: dcsr.mprven reads 0, which tells the debugger that MPRV is ignored in debug mode. The RTL
  still applies MPRV: the privilege used for the PMP check of a load or store has no debug-mode term. With
  MPRV = 1 and MPP = U, a debug-mode load is checked as a U-mode access.
- Steps to reproduce:
  1. Set up (M-mode): all PMP regions OFF (M-mode accesses allowed; U-mode denied by the no-match rule with
     mseccfg.MMWP = 0). Set mstatus.MPRV = 1 and MPP = U. Park in a loop.
  2. Do: assert debug_req_i. In the debug ROM execute lw from an address outside the debug-module window.
  3. RTL: the access is checked as U and denied: no data_req_o appears and the core jumps to DmExceptionAddr
     (an exception inside debug mode).
  4. Specification: MPRV is ignored in debug mode, the load runs with M privilege and completes.
  5. Control: MPRV = 0, the load completes on both.
- Test (exists; expected_fail: true; verdict XFAIL):

      python3 dv/auto_dv/flow/gen_regress.py --repro gen_prv_debug_b2_xfail 1 --waves --tag b2_repro

  Seed 1 is the retained run's seed (dv/auto_dv/evidence/gen_tdd_bug_tests.md Section 1). The collected failure is the scoreboard UVM_ERROR [isa_trap] "dut trapped, model retired 1 trap=0 cause=00000000" on the debug ROM's load record (order 304, pc 1a110814, insn 000e2e83), then [isa_pc] pc model=1a110818 dut=1a110808 (the model drets from the ROM body, the core from DmExceptionAddr), the pair repeating on the second debug entry, and the module assertion "GEN_UT_DBG: 4 ISA mismatches across the debug entries"; the flow reason string is "expected-fail: uvm_error at sim.log:33 (isa_trap)". The control program gen_prv_debug_b2_ctrl_directed.S (MPRV cleared) PASSES. Program dv/auto_dv/stim/gen_directed/gen_prv_debug_b2_directed.S with its own .debug_rom, cocotb module gen_ut_dbg, tier check, measured false; retained logs dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_bug_b2_dbg_mprv_red1_{stdout.log,sim.log,verdict.txt}. The flow reports XFAIL for the
  expected_fail entry; an unexpected PASS means the behaviour changed. The retained FSDB is test-writer's out tree out_tw20/bug_b2_dbg_mprv_red1_waves/waves.fsdb, its run header retained as dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_bug_b2_dbg_mprv_red1_waves_run_header.txt (at 11575 ns debug_mode = 1, priv_mode_id = 3 (M) while priv_mode_lsu = 0 (U), the ROM's load record carries rvfi_trap = 1 and data_req_o never asserts between 11500 and 11620 ns); a fresh run lands its
  waves at <out root>/regress_b2_repro/runs/gen_prv_debug_b2_xfail_1/waves.fsdb.
- Evidence: dv/auto_dv/evidence/gen_tdd_bug_tests.md Section 1 (the retained red run with its signature, the green control, the FSDB path); an owner ruling on the RTL is the open item.
- Notes: security-relevant. B1 and B2 share one program and one PMP region.
  Scoping before the test landed: Proposed test to build: plan test group gen_prv_debug_b2_xfail (TP-PRV-035), with expected_fail: true. Scoping: (a) a directed program (PMP off, MPRV = 1 with MPP = U, a .debug_rom that performs the load and stores a result word) and a testlist entry; (b) extends gen_ut_dbg (DBG_REQ through the bridge, zero-mismatch assertion) with the directed program; (c) test-writer; (d) S: the ISA model ignores MPRV in debug mode when mprven is 0 (tools/riscv-isa-sim/riscv/mmu.h:572), so the model completes the load while the core traps to DmExceptionAddr and the comparator raises [isa_trap] on that record; the program has two parts and the debug-entry shape is the one gen_ut_dbg already runs.

### B3: tdata3, mcontext, scontext and mscontext read 0 and ignore writes instead of trapping
- Rating: P3. Reading 0 instead of trapping changes no execution and no state; only software that probes for
  the trigger module by expecting a trap would be misled. The Ibex documentation states the read-0 behaviour.
- Status: candidate, reproducer pending
- Feature: tdata3, mcontext, scontext, mscontext read zero; writes are ignored; accessible in M/debug
  (F-TRG-008, canonical); alias tdata3 (0x7A3), mcontext (0x7A8), mscontext (0x7AA), scontext (0x5A8) read 0
  and ignore writes (F-CSR-083)
- Plan items (expected-fail): TP-CSR-083, TP-TRG-008
- rtl-arch alias: -
- RTL: rtl/ibex_cs_registers.sv:648-663
- Specification / intent: riscv-isa-manual / riscv-debug-spec Sdtrig.adoc:370 ("Attempts to access an unimplemented Trigger Module Register raise an illegal instruction exception")
- What happens: the core does not implement these four trigger CSRs. The debug specification says an access
  to an unimplemented trigger CSR raises an illegal-instruction exception. The RTL returns 0 on a read and
  drops a write, with no trap.
- Steps to reproduce:
  1. Set up: M-mode, nothing else.
  2. Do: csrr t0, 0x7A3 (tdata3). Repeat for 0x7A8 (mcontext), 0x5A8 (scontext) and 0x7AA (mscontext).
  3. RTL: each read returns 0 and takes no trap.
  4. Specification: each read raises an illegal-instruction exception (mcause 2, mtval = the encoding).
- Test: No test yet. Proposed tests to build: plan test groups gen_csr_trigger_csr_xfail (TP-CSR-083) and
  gen_trg_csr_xfail (TP-TRG-008), with expected_fail: true. Scoping: (a) a directed program that reads the
  four CSR numbers in M-mode under lock-step; (b) extends gen_ut_lockstep with a directed program;
  (c) test-writer; (d) S for two of the four CSRs and M for all four: the ISA model traps on scontext (Spike
  registers it only when S-mode exists, tools/riscv-isa-sim/riscv/csr_init.cc:315) and on mscontext (not in
  the model), so those two reads raise [isa_trap] "model trapped, dut retired" today; the model implements
  tdata3 (with one trigger) and mcontext (tools/riscv-isa-sim/riscv/csr_init.cc:303, :319) and returns 0 like the
  core, so those two
  numbers need the CSR read-back predictor the plan names (gen_chk_csr_readback, not built) with a rule that
  they trap: M, tb-infra.
- Evidence: none yet.
- Notes: the Ibex documentation (cs_registers.rst) documents read-0.

### B4: cm.mvsa01 with r1s' == r2s' (a reserved encoding) executes as two moves
- Rating: P3. The encoding is reserved; the specification defines no behaviour for it (the general rule
  leaves it unspecified, and a platform may or may not trap). The RTL's choice, execute with the second
  write winning, affects only programs that emit an encoding no assembler produces.
- Status: REPRODUCED by tb-infra (landing 5, slice 3, committed a9b63ae). The RTL cause is stated by rtl-arch
  in dv/auto_dv/evidence/gen_b4_rtl_facts.md (T-237; at 3c3a96f, sha256 3b0f7aed4462; first landed ab3cb31,
  reviewed APPROVE-WITH-CHANGES at 5e05ad7): the cm.mvsa01 arm raises no illegal instruction, the only Zcmp
  encoding the decoder accepts that the specification reserves. Owner item: does Ibex's non-trapping
  execution of the reserved cm.mvsa01 encoding stand.
- Feature: cm.mvsa01 with r1s' == r2s' is reserved but executed by the RTL (F-CMP-051)
- Plan items (expected-fail): TP-CMP-051
- rtl-arch alias: T-237 (gen_b4_rtl_facts.md)
- RTL: rtl/ibex_compressed_decoder.sv:779-806; rtl-arch T-237, dv/auto_dv/evidence/gen_b4_rtl_facts.md at 3c3a96f (sha256 3b0f7aed4462; first landed ab3cb31, reviewed APPROVE-WITH-CHANGES at 5e05ad7): the cm.mvsa01 arm (:788-800) carries no illegal_instr_o term (the funct3-101 group's encoding-level illegal_instr_o assignments are the defaults :835, :839 and the push/pop reserved-rlist assignments :637 under the test :635 and :705 under :703; its configuration-level assignments :620, CHERIoT enable, and :843, RV32ZC without Zcmp, do not apply to this build); the first micro-op carries the COMMIT tag (:790), so the pair is atomic and the second write wins
- Specification / intent: tools/specs/riscv-isa-manual/src/unpriv/zcmp.adoc:1163 (norm:cm-mvsa01_res) "For the encoding to be legal r1s' != r2s'." and :1174 (norm:cm-mvsa01_op) "r1s' and r2s' must be different."; the reserved encoding has no defined behaviour, Ibex's choice is to execute it; the general reserved-encoding rule (rv32.adoc:124-130: behaviour UNSPECIFIED, a platform may require a trap) and Spike's require (tools/riscv-isa-sim/riscv/insns/cm_mvsa01.h:1-4) are quoted in the facts note Section 5
- What happens: cm.mvsa01 copies a0 and a1 into two registers r1s' and r2s'. The encoding with r1s' equal to
  r2s' is reserved. The ISA model (Spike) refuses it with an illegal-instruction exception. Ibex executes it
  as two moves into the same register, and the second move (from a1) wins.
- Steps to reproduce:
  1. Set up: M-mode; assemble one cm.mvsa01 with r1s' = r2s' through .insn or .2byte
     (dv/auto_dv/stim/gen_directed/gen_zcmp_mv_reserved_directed.S does this).
  2. Do: execute it under the lock-step comparator.
  3. RTL: two moves retire; the destination register ends with the value of a1; no trap.
  4. Specification: no defined behaviour; the model traps (mcause 2, mtval 0xac22 in the retained run).
- Test (exists; expected_fail: true; verdict XFAIL):

      python3 dv/auto_dv/flow/gen_regress.py --repro gen_ut_lockstep_zcmp_mv_reserved 1 --waves --tag b4_repro

  Seed 1 is the retained run's seed (dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l5_lockstep_zcmp_mv_res_run_header.txt).
  The collected failure is the scoreboard UVM_ERROR from dv/auto_dv/env/gen_rvfi_pkg.sv tagged [isa_trap]:
  "dut retired, model retired 0 trap=1 cause=00000002 tval=0000ac22" at order 8, pc 80000094
  (gen_fu_l5_lockstep_zcmp_mv_res_verdict.txt), followed by [isa_rd] "Zcmp union:" register rows. A FAIL
  through any other mechanism is not the B4 red and needs triage (the testlist entry's notes say the same).
  The FSDB lands at <out root>/regress_b4_repro/runs/gen_ut_lockstep_zcmp_mv_reserved_1/waves.fsdb.
- Evidence: tb-infra landing 5, slice 3, committed a9b63ae (its review f2320ca is REQUEST-CHANGES on the mv
  sampler's sreg mapping, ablation and red-log retention, none of it touching these files; the re-review sha
  follows landing 6): program dv/auto_dv/stim/gen_directed/gen_zcmp_mv_reserved_directed.S and the retained
  logs dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l5_lockstep_zcmp_mv_res_{run_header.txt,verdict.txt,stdout_excerpt.log,export.txt};
  the verdict's first comparator row is the [isa_trap] line quoted above (model illegal instruction, DUT two
  retiring moves).
- Notes: low severity. DV Lead ruling B4-R1 (2026-09-03): the TB does not adopt the RTL behaviour as its
  reference before the owner rules (a shim modelling Ibex's execution of the reserved encoding refused);
  running the encoding with the comparators off refused; the witness bin CG-CMP-007.cr_insn_equal.cm_mvsa01_yes
  is TP-CMP-051's alone (expected-fail, own test): only the reserved encoding hits it and a pass test never
  executes that encoding under lock-step, so the TP-CMP-053 row of the trace CSV and the bin in
  gen_test_cmp_zcmp_basic's manifest (473 declared bins, gen_cmp_zcmp_mv_cg.cr_insn_equal.cm_mvsa01_yes) left
  together with the Test Writer's re-render (joint landing T-239 at 4a71798, LOG-036b).

### B5: dcsr.nmip is hardwired 0 while an NMI can be pending in debug mode
- Rating: P3. nmip is a read-only status bit for the debugger. The NMI itself is taken correctly after dret;
  only the report is missing.
- Status: candidate, reproducer pending
- Feature: NMI while in debug mode is ignored; dcsr.nmip reads 0 (F-IRQ-037, canonical)
- Plan items (expected-fail): TP-DBG-021
- rtl-arch alias: -
- RTL: rtl/ibex_cs_registers.sv:825
- Specification / intent: tools/specs/riscv-debug-spec/xml/core_registers.xml:292-298 (nmip, access R: set when an NMI is pending; reliability implementation-dependent). The generated field table is absent from the clone but the XML source is on disk.
- What happens: while the core is in debug mode an NMI is held pending. The debug specification says
  dcsr.nmip reports a pending NMI. The RTL ties the bit to 0, so a debugger never learns of it.
- Steps to reproduce:
  1. Set up: any M-mode program; assert debug_req_i and wait for debug mode.
  2. Do: assert irq_nm_i (NMI_PULSE through the bridge). In the debug ROM read dcsr.
  3. RTL: bit 3 (nmip) reads 0.
  4. Specification: bit 3 reads 1 while the NMI is pending.
- Test: No test yet. Proposed test to build: plan test group gen_dbg_irq_mask_xfail (TP-DBG-021), with
  expected_fail: true. Scoping: (a) a directed program with a .debug_rom that reads dcsr and stores the value,
  a cocotb module that sends DBG_REQ and then NMI_PULSE while debug mode is on, and a checker rule that
  predicts nmip = 1 for a dcsr read while an NMI is pending; (b) extends gen_ut_dbg (DBG_REQ) and
  gen_ut_irq_nmi_long (NMI through the bridge) for the stimulus, and gen_dbg_checker in
  dv/auto_dv/env/gen_checkers_pkg.sv for the rule; (c) tb-infra for the rule, test-writer for the program;
  (d) M: the ISA model also reads nmip as 0 (the field is absent from the dcsr model in
  tools/riscv-isa-sim/riscv/csrs.cc), so the comparator cannot see the bug and a new checker rule is required.
- Evidence: none yet.
- Notes: low; a read-only status field that never reports.

### B7: dummy instructions are counted in minstret and in mhpmcounter11 / 12 (the multiply and divide wait counters)
- Rating: P2. minstret and the wait counters are wrong whenever dummy instructions are enabled; the
  workaround is to measure with dummy_instr_en = 0 (the Q-005 default already does this) or to accept that
  the counts include the dummies.
- Status: REPRODUCED by test-writer (dv/auto_dv/evidence/gen_tdd_bug_tests.md Section 2: retained red and green runs and a waveform confirmation, LOG-103); still a candidate for the owner ruling
- Feature: SecureIbex dummy instructions increment minstret and the div-wait counter (bug candidate); the
  dummy mul adds no mul-wait cycles (F-PMC-011, canonical); alias Dummy instructions are counted by minstret
  and the mul/div wait events (F-DIT-018)
- Plan items (expected-fail): TP-PMC-013, TP-DIT-019
- rtl-arch alias: BUG-02 (recipe gen_bug_reproducer_specs.md BUG-02)
- RTL: rtl/ibex_id_stage.sv:1218-1220 (instr_perf_count_id_o has no dummy term), rtl/ibex_wb_stage.sv:150,169,208-209, rtl/ibex_cs_registers.sv:1588
- Specification / intent: doc/03_reference/security.rst:45 (dummies have no functional impact on processor state); priv spec: minstret counts retired instructions
- What happens: dummy instructions are inserted by the fetch stage and are not part of the program. The
  privileged specification says minstret counts the program's retired instructions, and the Ibex
  documentation says dummies have no functional impact on processor state. The RTL counts every dummy in
  minstret, and a dummy multiply or divide also advances the wait counters. RVFI shows no record for a dummy
  (correct), so RVFI and minstret disagree.
- Steps to reproduce:
  1. Set up (M-mode): csrw cpuctrlsts, 0x4 (dummy_instr_en = 1, mask 0 for the highest insertion rate).
  2. Do: csrr t0, minstret; 64 nops; csrr t1, minstret.
  3. RTL: t1 - t0 = 65 plus the number of dummies inserted (an LFSR decides where; the RVFI order delta is
     exactly 65).
  4. Specification: t1 - t0 = 65.
  5. Control: dummy_instr_en = 0 gives 65.
- Test (exists; expected_fail: true; verdict XFAIL):

      python3 dv/auto_dv/flow/gen_regress.py --repro gen_pmc_minstret_xfail 1 --waves --tag b7_repro

  Seed 1 is the retained run's seed (dv/auto_dv/evidence/gen_tdd_bug_tests.md Section 2). The collected failure is the scoreboard UVM_ERROR [isa_rd] rd model=x7/00000048 dut=x7/0000006f on the second minstret read (order 73, pc 8000019a, insn b02023f3) and [isa_rd] rd model=x29/00000041 dut=x29/00000068 on the program's own subtraction: the model measures the specification's 65, the core 104, so 39 dummy instructions were counted at seed 1 (the count is seed-dependent: an LFSR places the dummies, so another seed gives other values and another mismatch count); the module assertion "GEN_UT_LOCKSTEP: 2 ISA mismatches" is the collected failure and the flow reason string is "expected-fail: uvm_error at sim.log:32 (isa_rd)". The control program gen_pmc_minstret_dummy_ctrl_directed.S (cpuctrlsts written 0) PASSES. Program dv/auto_dv/stim/gen_directed/gen_pmc_minstret_dummy_directed.S, cocotb module gen_ut_lockstep, +gen_ut_boot_retire=20, tier check, measured false; retained logs dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_bug_b7_minstret_red1_{stdout.log,sim.log,verdict.txt}. Not covered by this test: the mhpmcounter11 / 12 half of B7 (the shim holds the core's HPM values, so the comparator cannot see it; it needs tb-infra's counter rule like B11, B17 and B20). The flow reports XFAIL for the
  expected_fail entry; an unexpected PASS means the behaviour changed. The retained FSDB is test-writer's out tree out_tw20/bug_b7_minstret_red1_waves/waves.fsdb, its run header retained as dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_bug_b7_minstret_red1_waves_run_header.txt (dummy_instr_wb high from 1025 to 1055 ns and rvfi_valid low from 1035 to 1065 ns while cs_registers_i.minstret_raw steps 0x8 to 0x9 at 1035 ns and 0x9 to 0xa at 1045 ns: the counter advances over instructions the trace never reports); a fresh run lands its
  waves at <out root>/regress_b7_repro/runs/gen_pmc_minstret_xfail_1/waves.fsdb.
- Evidence: dv/auto_dv/evidence/gen_tdd_bug_tests.md Section 2 (the retained red run with its signature, the green control, the FSDB path); an owner ruling on the RTL is the open item.
- Notes: needs one directed simulation (static reading so far). The counter model the plan names
  (ctr_minstret) is designed to run a bound check while dummies are on, so it would not fire on B7 by itself;
  the lock-step comparator is the witness.
  Scoping before the test landed: Proposed tests to build: plan test groups gen_pmc_minstret_xfail (TP-PMC-013) and gen_dit_dummy_xfail (TP-DIT-019), with expected_fail: true. Scoping: (a) a directed program that enables dummies and reads minstret around a block of nops, run under lock-step; (b) extends gen_ut_lockstep with a directed program (gen_zcmp_dummy_directed.S already enables dummies the same way); (c) test-writer; (d) S: the ISA shim serves minstret from the model's own retirement count and does not model dummies (dv/auto_dv/docs/gen_component_api_isa_shim.md, section Counter CSRs), so the second csrr differs and the comparator raises [isa_rd] on that record.

### B8: a dummy instruction inserted inside a Zcmp push / pop sequence drops a micro-op or replays the whole expansion
- Rating: P1. Silent corruption of architectural state (a register not saved or not restored, registers
  reloaded from above the stack frame, the stack pointer incremented twice, a ret with a stale stack pointer)
  in a shipped configuration (SecureIbex dummy instructions with Zcmp). Software cannot detect it, and the
  only avoidance is to give up dummy instructions or Zcmp.
- Status: REPRODUCED deterministically by tb-infra (landing 4, T-205 slice 2, committed 5b8a0fb) and
  EXPLAINED by rtl-arch (dv/auto_dv/evidence/gen_b8_rtl_facts.md: rtl-arch T-225: 1eb2ede, CM59 fixes
  53e8468, CM64 fixes 7d7be39, tb-infra's 27-row mapping folded 76cd2e5, CM68 / CM69 fixes ae5e58a = the
  explained record, sha256 b33a133f519f; cross-model APPROVE-WITH-CHANGES 68b9af3 on the CM59 copy). An
  architectural bug, not an RVFI export bug. The RTL fix is an owner item.
- Feature: Dummy instruction insertion during a Zcmp sequence (bug candidate) (F-CMP-064); cross-reference
  plan item TP-DIT-032 (the DIT area's item for the same case)
- Plan items (expected-fail): TP-CMP-065, TP-DIT-032, TP-CMP-074 (the interrupt / debug exposure; a second
  reproducer for the owner)
- rtl-arch alias: BUG-07 (rtl-arch T-017: CONFIRMED reachable by static analysis; highest-value finding:
  architectural-state corruption with dummy instructions enabled, a shipped-configuration feature)
- RTL: rtl/ibex_if_stage.sv:492-493 (the compressed decoder's valid_i and id_in_ready_i carry no dummy-insertion term) while :526-528 put the dummy into the IF/ID register with the INSTR_NOT_EXPANDED tag and :535, :808-809 hold the prefetch buffer, so the cm.* halfword stays at the decoder input; the expansion FSM takes its id_in_ready_i branches (rtl/ibex_compressed_decoder.sv:641, :653, :661, :676 for cm.push; :709, :718, :726, :745, :761, :767 for the pop family) and the micro-op on instr_o is discarded; the only FSM reset is flush_expanded on PC_EXC (rtl/ibex_if_stage.sv:483; rtl/ibex_compressed_decoder.sv:889); insertion decision rtl/ibex_dummy_instr.sv:115 with the counter advancing once per accepted micro-op (:103-104); debug gate rtl/ibex_controller.sv:474-477 (EXPANDED or COMMIT) and interrupt gate :498-500 (COMMIT tag only), both keyed on the ID tag the dummy does not carry
- Specification / intent: Zcmp atomicity intent (zc.adoc push/pop sequences); Ibex doc silent
- What happens: Ibex expands cm.push / cm.pop into micro-ops (one store or load per register, then the stack
  pointer update). The dummy inserter can place a dummy instruction between two micro-ops. The expansion
  state machine then advances as if its micro-op had been accepted, while the decode stage receives the
  dummy instead. That micro-op never executes: a lost store leaves one register unsaved, a lost load leaves
  one register unrestored. When the dummy lands on the LAST micro-op the state machine returns to idle with
  the cm.* halfword still in the fetch buffer, and the whole expansion runs again: cm.push doubles every store
  (memory and the stack pointer end correct); cm.popret / cm.popretz replay after the stack pointer was
  already incremented, reloading every register from above the frame and incrementing the stack pointer a
  second time; a dummy on the stack-pointer increment of cm.popret / cm.popretz makes the ret execute with a
  stale stack pointer.
- Steps to reproduce:
  1. Set up (M-mode): csrs cpuctrlsts, 0x4 (dummy_instr_en = 1, mask 0). Load known patterns into ra and
     s0..s11. Pre-fill the stack area with a marker.
  2. Do: run cm.push / cm.pop pairs (the retained program uses rlist 4, 8, 12 and 15 with spimm 2), or
     cm.popret / cm.popretz functions (gen_zcmp_dummy_popret_directed.S).
  3. RTL: micro-ops are lost or the expansion replays. In the retained run x18 (s2) reads 00000000 after the
     pop instead of 33333333; a pop emits load records for only 8 of its 13 registers; a push stores twice at
     the same addresses.
  4. Specification: every register in the list is stored or loaded exactly once, the stack pointer moves
     once, and the registers hold their values after the pair (zcmp.adoc: a push / pop sequence executes as
     a whole).
  5. Control: the same program without the cpuctrlsts write is clean under all four data-bus response
     regimes, and so is a misaligned-stack variant; the trigger is the dummy insertion inside a Zcmp expansion.
- Test (exists; expected_fail: true; verdict XFAIL):

      python3 dv/auto_dv/flow/gen_regress.py --repro gen_ut_lockstep_zcmp_dummy 1 --waves --tag b8_repro

  Seed 1 is the retained run's seed (gen_fu_l4_lockstep_zcmp_dummy_run_header.txt: module gen_ut_lockstep,
  seed 1, build_sources_sha256 893384b8eec4e6d5). The collected failure is the scoreboard UVM_ERROR from
  dv/auto_dv/env/gen_rvfi_pkg.sv: [isa_mem] rows "Zcmp stores:" or "Zcmp loads:" with a model / dut count
  mismatch (first row in the retained verdict: "Zcmp stores: model 1, dut 2" at order 34, pc 800000fa, insn
  fd010113), then [isa_rd] "Zcmp union:" register rows. The testlist entry sits in the check tier with
  expected_fail: true (Runtime touch ac5f4ab), so the flow reports XFAIL; an unexpected PASS means the
  behaviour changed and the finding must be re-examined. A FAIL through any other mechanism is not the B8 red
  and needs triage. The FSDB lands at <out root>/regress_b8_repro/runs/gen_ut_lockstep_zcmp_dummy_1/waves.fsdb.
  The popret / popretz replay has no testlist entry: its retained runs (Evidence, item 5) were made with the
  local fixture; adding gen_zcmp_dummy_popret_directed.S as a second expected-fail entry of gen_ut_lockstep is
  an S item for test-writer.
- Evidence (reproduction), kept from version 1 with its figures:
  1. Program dv/auto_dv/stim/gen_directed/gen_zcmp_dummy_directed.S; retained logs
     dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l4_lockstep_zcmp_dummy_{run_header.txt,verdict.txt,stdout_excerpt.log,export.txt}.
     After csrs 0x7C0, 4 four cm.push / cm.pop pairs (rlist 4, 8, 12, 15; spimm 2) diverge from the lock-step
     model on 27 rows: isa_mem Zcmp stores model 1 dut 2 on the first push's sp-adjust micro-op (fd010113),
     loads model 1 dut 2 on its pop, stores 5/6 and loads 5/7 on the rlist-8 pair, and isa_rd Zcmp union x18
     model 33333333 dut 00000000 after the pop.
  2. Symptom (a), architectural: x18 is wrong after the pop (00000000 in the retained run: the s2 store of
     push rlist 8 lost in CmPushStoreReg, the slot stale, the pop's load faithful).
  3. Symptom (b), the export: the rlist-15 pop (pc 80000108, insn 06010113, orders 0x50-0x58) emits load
     micro-op records for x27, x26, x24, x22, x21, x20, x18, x8 only (x25, x23, x19, x9, x1 absent), every
     micro-op still carrying rvfi_ext_expanded_insn_valid and the sp-adjust carrying _last: loads that did not
     happen. The rlist-12 pop (pc 80000104, insn 05010113, orders 0x3c-0x47) shows the replay case: a first
     pass x22, x21, x20, x18, x9, a second pass x23, x22, x20, x18, x9, x1, then the sp adjust, x8 never loaded
     (comparator row: model wrote 10 registers, dut 8, order 71). Symptoms (a) and (b) have one cause (Notes).
     The rlist-12 attribution of the 8-record list in tb-infra's gen_tdd_fcov.md:79 was the same
     mis-attribution, corrected by tb-infra in landing 6 at 61c97c1.
  4. Row mapping: dv/auto_dv/evidence/gen_b8_row_mapping.md (committed a9b63ae with landing 5, whose review
     f2320ca is REQUEST-CHANGES with no finding on the mapping file, the re-review being the cross-model
     APPROVE-WITH-CHANGES for landing 6 at 4947718; facts file Section 3, reproduction status): all 27
     comparator rows map to a lost micro-op or a full replay, 33 lost micro-ops in all (CmIdle first store
     lost 2, CmPushStoreReg store lost 11, CmPushDecrSp addi lost with replay 2, CmIdle first load lost 2,
     CmPopLoadReg load lost 13, CmPopIncrSp addi lost with replay 3).
  5. Replay corruption (the CmPopRetRa reload from above the frame): gen_zcmp_dummy_directed.S defines only
     PUSH and POP and has no popret / popretz, so this case is not reachable from that run. The variant that
     reaches it is dv/auto_dv/stim/gen_directed/gen_zcmp_dummy_popret_directed.S (six cm.popret and six
     cm.popretz functions over rlist 4, 7, 9, 12, 14 and 15), with retained runs at landings 7, 10 and 12
     (for example gen_fu_l12_b8_zcmp_dummy_popret_off_1000_{run_header.txt,verdict.txt,stdout_excerpt.log}),
     whose excerpts each carry "isa_mem Zcmp load 0: model addr 800003ac dut 800003cc" at order 46, pc
     8000016c, insn 00008067 (a ret), with the push counterpart "Zcmp store 0: model 800003ac<=800000fa
     (4 bytes) dut 800003cc<=800000fa" at order 41 and an x2 divergence of exactly 0x20 on the ret record.
  6. Withdrawn citation: the earlier figure x18 = 800003ff came from an unretained gen_zcmp_directed.S run
     and occurs in NO retained log (counted across the 12 retained popret LOG files, the thirteenth tracked
     path being the stimulus program rather than a log, with "popret" itself as the positive control at 12
     line hits over 8 of those files, the four verdict files carrying the token nowhere).
  7. Not yet run: the mv-pair symptom (the first move of cm.mvsa01 / cm.mva01s lost, destination unwritten)
     has no run (TP-CMP-065 reproducer clause).
  8. Control: the same program without the csrs (every rlist and spimm, push/pop pairs, popret/popretz, 290
     sequences) is clean under all four dmem rvalid regimes, and a misaligned-sp variant is clean.
- Notes (mechanism, from the B8 facts record Sections 2-5): the FSM advances as if its micro-op had been
  accepted while ID receives the dummy, so that micro-op never executes (no LSU request, no register-file
  write, no RVFI record). Dummies increment minstret (Section 4 as corrected by the review; B7). The two
  symptoms of the reproduction have one cause (Section 4): the missing RVFI records are faithful records of
  loads that did not happen and the extra records are the replayed micro-ops, so no RVFI-only candidate
  splits off. Consecutive micro-ops can be lost: dummy_cnt_threshold = lfsr cnt & {dummy_instr_mask, ones}
  (rtl/ibex_dummy_instr.sv:97), so with mask 0 the threshold is 0..3. Secondary exposure (Section 5, stated
  from the RTL, not reproduced): the dummy in ID carries INSTR_NOT_EXPANDED, so the controller admits an
  interrupt inside the COMMIT window of the pop family (after the sp increment: the ret of cm.popret, the
  li a0, 0 or ret of cm.popretz; an interrupt between other micro-ops is by design and its restart is
  idempotent; the third COMMIT site, the first move of cm.mvsa01 / cm.mva01s, opens a benign window because
  the replay re-reads unchanged operands) and a debug request at any position of an expansion, and the PC_EXC
  flush restarts the expansion after mret / dret with partially applied state (TP-CMP-074). cm.mvsa01 /
  cm.mva01s (Section 3): a dummy on the first move leaves its destination permanently unwritten. The existing
  IbexPushPopFSMStable assertion (rtl/ibex_compressed_decoder.sv:937) cannot catch it because valid_i stays
  high; rtl-arch's TB-side assertion form (Section 6): if_id_pipe_reg_we && insert_dummy_instr |->
  cm_state_d == cm_state_q && cm_rlist_d == cm_rlist_q && cm_sp_offset_d == cm_sp_offset_q (internal nets:
  probe P1 territory, coverage-only). Fix direction for the RTL owner (DV Lead reading; rtl-arch proposes
  none): qualify the expander's id_in_ready_i with ~insert_dummy_instr, or block insertion while the decoder
  is mid-expansion.

### B10: an ebreak that enters debug mode records dcsr.cause = 2 (trigger) when the next instruction's address matches tdata2
- Rating: P2 (pending rtl-arch confirmation). The cause field is wrong while the entry itself and dpc are
  right; a debugger can tell the two apart from dpc (dpc is the ebreak's address, tdata2 the next address)
  or avoid arming a trigger on the instruction after an ebreak. Whether a second-order effect exists beyond
  the wrong field is not stated in the committed facts, so the rating waits for rtl-arch.
- Status: candidate, reproducer pending
- Feature: ebreak entering debug mode while the following instruction's address matches tdata2: cause
  misreported as 2 (bug candidate) (F-TRG-020)
- Plan items (expected-fail): TP-TRG-020
- rtl-arch alias: - (recipe gen_bug_reproducer_specs.md B10; rtl-arch T-017 static confirmation)
- RTL: rtl/ibex_controller.sv:519-523
- Specification / intent: riscv-debug-spec Sdext (cause 1 for ebreak) / Sdtrig (trigger fires on the matched instruction, not on the instruction before it)
- What happens: the trigger match is evaluated on the fetch-stage PC every cycle. While an ebreak that enters
  debug mode is in the decode stage, the fetch-stage PC already holds the next address. If that address
  equals tdata2, the cause field is written 2 (trigger) instead of 1 (ebreak), although dpc points at the
  ebreak. After dret the trigger fires again, correctly, on the matched instruction.
- Steps to reproduce:
  1. Set up: the trigger CSRs are writable only in debug mode, so the program first halts by debug_req_i and
     its debug ROM arms tdata1 (execute) with tdata2 = A, sets dcsr.ebreakm = 1, points dpc at the test
     sequence and drets.
  2. Do: execute ebreak at address A - 4 (A - 2 with c.ebreak). On the second debug entry the debug ROM
     records dcsr.cause and dpc.
  3. RTL: (cause, dpc) = (2, A - 4).
  4. Specification: (cause, dpc) = (1, A - 4); the trigger then fires on the instruction at A after dret,
     giving (2, A) on the third entry, where both agree.
- Test: No test yet. Proposed test to build: plan test group gen_trg_fire_xfail (TP-TRG-020), with
  expected_fail: true. Scoping: (a) a directed program with a multi-entry debug ROM (an entry counter in
  memory: arm on the first entry, record cause and dpc on the later ones) and a cocotb module that sends the
  first DBG_REQ; (b) extends gen_ut_dbg (DBG_REQ through the bridge, zero ISA mismatches) with the directed
  program; (c) test-writer for the program, tb-infra if a cause rule in gen_dbg_checker is needed (its
  dbg_entry rule as built checks the entry within a bound, not the cause value); (d) M: the ISA model enters
  debug mode on an ebreak with ebreakm set and records cause 1, so a dcsr read in the ROM should raise
  [isa_rd] against the core's 2, but the model's trigger arming through tdata1 / tdata2 in debug mode and its
  re-fire after dret must be confirmed in the run, and the ROM logic has several parts.
- Evidence: none yet.
- Notes: rtl-arch T-017: confirmed statically (trigger_match evaluated on pc_if every cycle; during the FLUSH
  cycle of an ebreak-into-debug pc_if holds the next address). Arming happens inside the debug ROM (trigger
  CSRs writable only in debug mode); T-041 reproducer spec.

### B11: NumBranchesTaken (mhpmcounter9) counts not-taken branches when cpuctrlsts.data_ind_timing = 1
- Rating: P2. The counter reports a wrong event under one configuration; the workaround is to read
  NumBranchesTaken with DIT off, or to use NumBranches (counter 8) instead.
- Status: candidate, reproducer pending
- Feature: mhpmcounter9 over-counts with cpuctrlsts.data_ind_timing=1: not-taken branches also count (bug
  candidate) (F-PMC-041)
- Plan items (expected-fail): TP-PMC-043, TP-BTALU-016
- rtl-arch alias: -
- RTL: rtl/ibex_id_stage.sv:790-791,815,831,928 (branch_set forced for all branches under DIT)
- Specification / intent: doc/03_reference/performance_counters.rst (NumBranchesTaken: taken branches)
- What happens: with DIT on, the core treats every branch as taken for timing purposes (it redirects, then
  continues at the fall-through address for a not-taken branch). The taken-branch counter is driven from the
  same signal, so it also counts branches that were not taken.
- Steps to reproduce:
  1. Set up (M-mode): csrs cpuctrlsts with data_ind_timing = 1; mcountinhibit = 0.
  2. Do: csrr t0, mhpmcounter9; 100 branches that are never taken; csrr t1, mhpmcounter9.
  3. RTL: t1 - t0 = 100.
  4. Documentation: t1 - t0 = 0.
  5. Control: data_ind_timing = 0 gives 0.
- Test: No test yet. Proposed tests to build: plan test groups gen_pmc_hpm_event_xfail (TP-PMC-043) and
  gen_btalu_dit_xfail (TP-BTALU-016), with expected_fail: true. Scoping: (a) a directed program (DIT on,
  never-taken branches around two counter reads) and a checker rule that predicts NumBranchesTaken from the
  RVFI records (a branch record whose next PC is not the fall-through); (b) extends gen_ut_lockstep with the
  directed program, and the counter model the plan names (dv/auto_dv/docs/gen_component_api_counter_model.md,
  ctr_hpm_exact for counters 5..10) for the rule; (c) test-writer for the program, tb-infra for the rule;
  (d) M: the ISA shim keeps the core's HPM counter values in holders synced from the core
  (gen_component_api_isa_shim.md, Counter CSRs), so the lock-step comparator cannot see a wrong HPM count and
  one new predicted-count rule is needed. Building the whole counter model (the four ctr_* checkers behind
  B11, B17 and B20 together) is L.
- Evidence: none yet.
- Notes: rtl-arch T-017 confirmed statically (perf_tbranch_o = branch_set_i; branch_set_raw_d =
  branch_decision_i | data_ind_timing_i). Decision requested from the DV Lead (T-017 Section 6): treated as a
  counter bug candidate (the doc defines the event as taken branches); items TP-PMC-043 / TP-BTALU-016 stay
  expected-fail. Classified B, not D, by the criterion in Section 0.6 (wrong event under a configuration, not
  a mis-described convention; contrast D6).

### B13: rvfi_pc_wdata keeps bit 0 for a jalr to an odd target while the fetch clears it (RVFI-only)
- Rating: P3. Trace-only: the core executes jalr per the specification (the fetch address and every
  architectural register see the even address); only the RVFI next-PC field carries the raw odd sum.
- Status: observed and explained (rtl-arch R11, dv/auto_dv/evidence/gen_t102_rtl_facts.md; Test Writer batch
  2: gen_test_isa_cti reports 64 of 64 comparator rows per seed of isa_pc_next dut == model | 1 on jalr /
  c.jr / c.jalr with an odd rs1 + imm, dv/auto_dv/evidence/gen_tdd_batch2.md; Orchestrator ruling LOG-032).
  Promoted from an RVFI-cosmetic note to a DUT bug candidate of the RVFI-only class.
- Feature: rvfi_pc_wdata keeps bit 0 for jalr to an odd target (RVFI bug candidate) (F-BTALU-008,
  canonical); cross-reference Record of a load/store that faults (bus error or PMP) in WB (F-RVFI-013)
- Plan items (expected-fail): TP-BTALU-008, TP-RVFI-013
- rtl-arch alias: R11 (gen_t102_rtl_facts.md)
- RTL: the branch-target ALU adds rs1 and the immediate without masking (rtl/ibex_ex_block.sv:95-101), so branch_target_ex carries bit 0; the fetch drops it (rtl/ibex_if_stage.sv:244, :288 prefetch_addr = {fetch_addr_n[31:1], 1'b0}, :416; rtl/ibex_fetch_fifo.sv:62-63) and pc_if / pc_id are even; the jalr record's rvfi_pc_wdata = pc_set ? branch_target_ex : pc_if (rtl/ibex_core.sv:2084) takes the RAW target, so RVFI reports an odd next-pc while no architectural register or fetch address ever shows bit 0
- Specification / intent: RVFI (riscv-formal docs/source/rvfi.rst, Program counter): pc_wdata is the address of the next instruction; the ISA execution is per spec (JALR clears the target LSB), the RVFI definition is violated
- What happens: jalr computes rs1 + imm and must clear bit 0 of the result. The branch-target adder does not
  mask the bit; the fetch stage drops it, so execution is right. The RVFI record of the jalr takes the raw
  adder result as its next-PC field, so the trace reports an odd address while the next record's PC is even.
- Steps to reproduce:
  1. Set up: M-mode; a jalr (or c.jr / c.jalr) whose rs1 + imm is odd
     (dv/auto_dv/stim/gen_directed/gen_jalr_odd_directed.S).
  2. Do: execute it under the lock-step comparator with the raw next-PC rule (+gen_isa_pc_next_mask_b13=0).
  3. RTL: rvfi_pc_wdata[0] = 1 on the jalr record; the next record's rvfi_pc_rdata[0] = 0.
  4. Specification: rvfi_pc_wdata is the address of the next instruction, so bit 0 is 0.
- Test: gen_test_isa_cti (smoke tier, measured, 3 seeds) hits the case on every seed and PASSES by policy:
  the comparator masks bit 0 on jump records and counts them (b13_odd_jalr in the GEN_SB "ISA compare"
  summary line; 64 in the retained seed-1 log
  dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_l9_isa_cti_s1_stdout.log). The plan item that records the
  expected-fail is TP-BTALU-008 (proposed test to build: gen_btalu_hazard_xfail, which alone runs the raw
  rule). To see the loud failure today, run the raw rule by hand (gen_regress.py --repro cannot pass a
  plusarg):

      python3 dv/auto_dv/flow/gen_build.py --build gen_tb --outdir <out>/build/gen_tb --waves
      python3 dv/auto_dv/flow/gen_run.py --build-dir <out>/build/gen_tb --test gen_test_isa_cti --seed 1 --run-dir <out>/runs/gen_test_isa_cti_1 --waves --plusarg +gen_isa_pc_next_mask_b13=0

  The collected failure is the scoreboard UVM_ERROR [isa_pc_next] "pc_next model=<even> dut=<odd>" on each
  odd-target jalr record (64 per seed); the FSDB is <out>/runs/gen_test_isa_cti_1/waves.fsdb. The same
  signature is retained from tb-infra's directed red of the raw rule:
  dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_a_red_jalr_odd_r11_v2_verdict.txt, "[isa_pc_next] pc_next
  model=80000124 dut=80000125 (order=11 pc=8000011e insn=00030067)", module gen_ut_lockstep, seed 1, program
  gen_jalr_odd_directed.S.
- Evidence: dv/auto_dv/evidence/gen_tdd_batch2.md (gen_test_isa_cti comparator rows, Sections 1 and 2b);
  dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_l9_isa_cti_s1_stdout.log (b13_odd_jalr=64);
  dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_a_red_jalr_odd_r11_v2_{run_header.txt,verdict.txt,stdout_excerpt.log}
  (the raw-rule red); rtl-arch R11.
- Notes: RVFI-only class (like BUG-10 / B18): no architectural effect. One-line fix the RTL owner would make:
  mask bit 0 at rtl/ibex_core.sv:2084 ({branch_target_ex[31:1], 1'b0} when pc_set). Comparator convention
  (T-144): the unmask knob landed at ffa9127 (TB Infra delta 1b on ce33b4f) as +gen_isa_pc_next_mask_b13,
  default 1: isa_pc_next masks bit 0 of rvfi_pc_wdata on jalr / c.jr / c.jalr records and counts them as
  b13_odd_jalr in the GEN_SB report (gen_rvfi_pkg.sv:494-500 at ffa9127); 0 runs the raw RVFI rule; proof
  pair on TB Infra's build: 80 records counted with the mask, exactly 80 isa_pc_next misses without it. Caveat
  (delta 1b review): with the mask on the comparator does not fail on B13, so gen_btalu_hazard_xfail /
  TP-BTALU-008 / TP-RVFI-013 must run with +gen_isa_pc_next_mask_b13=0 to witness the defect; TB Infra's 1c
  (9e912bb) passed both reviewers (LOG-051), so the plan's Section 0a records the comparator as built with the
  mask. TP-ISA-019's verdict relies on that convention and stays not_built for the odd-target clause until
  then; the expected-fail test gen_btalu_hazard_xfail (TP-BTALU-008) alone runs the unmasked rule and records
  the bit.

### B14: RVFI drops the ID-stage trap record when a WB load / store error coincides (downgraded to a convention note)
- Rating: P3. RVFI-only and, after rtl-arch's re-analysis, correct: the instruction in ID did not trap in that
  cycle; it is killed and re-executed after the handler, and its own record appears then.
- Status: downgraded to an RVFI convention note pending the confirmation simulation (rtl-arch T-041,
  fact-check row 48): the WB error has priority in FLUSH, the killed ID instruction re-executes after the
  handler and then produces its own record, so suppressing its record is correct; the confirmation program
  must show two trap records in order; one record re-opens it
- Feature: ID exception while WB is already faulting (single trap record) (F-RVFI-015, canonical);
  cross-references mtval is written to zero for ECALL, EBREAK and interrupts (F-EXC-065), Outputs may change
  the cycle after grant (F-DMEM-034), Writes to x0 are discarded for every instruction class (F-ISA-051)
- Plan items: none as gate items (downgraded); confirmation items, informational: TP-EXC-065, TP-ISA-051,
  TP-DMEM-063, TP-RVFI-039
- rtl-arch alias: BUG-04 (recipe gen_bug_reproducer_specs.md BUG-04)
- RTL: rtl/ibex_core.sv:1851-1853 (rvfi_id_done suppresses when wb_exception_o); rtl/ibex_controller.sv:336-337
- Specification / intent: RVFI convention: every trapping instruction is reported (rtl/ibex_core.sv:1843-1849 comment; rvfi.rst rvfi_trap)
- What happens: when a store in the writeback stage reports a bus or PMP error in the same cycle an
  instruction in the decode stage would trap (for example an illegal instruction), the core takes the
  writeback error first and kills the decode-stage instruction without executing it. RVFI emits no record for
  the killed instruction in that cycle. After the handler returns, the killed instruction runs again and gets
  its record then. That is the expected trace; the original reading (a trap lost from the trace) assumed the
  decode-stage trap was taken.
- Steps (a confirmation, not a bug reproduction):
  1. Set up (M-mode): a PMP region that denies a word bad_word for M as well (L = 1, no permissions); a
     handler that records mcause and mepc and, on the store fault, advances mepc past the store.
  2. Do: sw zero, 0(bad_word); .word 0x00000000 (an illegal instruction) right after it, with the memory
     response timed so the store's error arrives while the illegal instruction is in decode (vary
     knob_dmem_rvalid_delay).
  3. RTL and specification: record 1 is the store with rvfi_trap = 1 (store access fault); record 2 is the
     illegal instruction with rvfi_trap = 1 after the handler returned. Two trap records, no gap in rvfi_order.
  4. If only ONE trap record appears, B14 re-opens as a bug candidate with the trace attached.
- Test: No test yet. Proposed test to build: the informational item's test group gen_isa_illegal_info
  (TP-ISA-051) and the RVFI / DMEM confirmation items. Scoping: (a) a directed program as in the steps, run
  under lock-step; (b) extends gen_ut_lockstep with a directed program (gen_pmp_deny_directed.S already sets
  a denying region); (c) test-writer; (d) S: the comparator checks both trap records against the model
  (isa_trap rows), and a pass is the expected outcome.
- Evidence: none yet (the confirmation run is the owed step).
- Notes: RVFI-only; affects the comparator, not architectural state; unverified in simulation.

### B15: dcsr.ebreaks (bit 13) is writable although the hart has no S-mode
- Rating: P3. Nothing reads the bit (rtl/ibex_controller.sv:481-483 never consults it) and no S-mode ebreak
  can occur, so there is no functional effect; only the read-back value is wrong.
- Status: candidate, reproducer pending
- Feature: dcsr bit 13 (ebreaks) is writable and readable although S-mode is absent (bug candidate B15)
  (F-DBG-016, canonical); alias dcsr.ebreaks (bit 13) is writable and readable although S-mode does not
  exist (F-CSR-076)
- Plan items (expected-fail): TP-CSR-075, TP-CSR-076, TP-DBG-018
- rtl-arch alias: BUG-03 (recipe gen_bug_reproducer_specs.md BUG-03)
- RTL: rtl/ibex_cs_registers.sv:810-836 (every other field forced; bit 13 not forced)
- Specification / intent: riscv-debug-spec xml/core_registers.xml:163-172 (ebreaks hardwired to 0 if the hart does not support S-mode); misa = 0x40901104 has no S
- What happens: the dcsr write path forces every unimplemented field to 0 except ebreaks. A write of bit 13
  is stored and read back as 1. The debug specification hardwires the bit to 0 on a hart without S-mode.
- Steps to reproduce:
  1. Set up: enter debug mode (debug_req_i, or ebreak with ebreakm set).
  2. Do (in the debug ROM): li t0, 0x2000; csrs dcsr, t0; csrr t1, dcsr.
  3. RTL: t1[13] = 1.
  4. Specification: t1[13] = 0.
- Test: No test yet. Proposed tests to build: plan test groups gen_csr_debug_csr_b15a_xfail (TP-CSR-075),
  gen_csr_debug_csr_b15b_xfail (TP-CSR-076) and gen_dbg_csr_xfail (TP-DBG-018), with expected_fail: true.
  Scoping: (a) a directed program whose .debug_rom sets bit 13 and reads dcsr back; (b) extends gen_ut_dbg
  (DBG_REQ, zero-mismatch assertion) with the directed program; (c) test-writer; (d) S: the ISA model forces
  ebreaks to 0 when S-mode is absent (tools/riscv-isa-sim/riscv/csrs.cc:1625), so the csrr result differs and
  the comparator raises [isa_rd] on that record.
- Evidence: none yet.
- Notes: functional impact nil: rtl/ibex_controller.sv:481-483 never reads it.

### B16: a misaligned load with a bus-integrity error on the FIRST beat still writes rd
- Rating: P2 (pending rtl-arch confirmation). The documented security intent (no register write on bad check
  bits) is violated for one access class, but the alert and the internal NMI still fire, so the corruption is
  detected, and aligned accesses avoid the class. The rating rests on the merged word not being usable
  before the NMI is taken; rtl-arch X-11 states the alert and NMI path but not how many instructions can
  consume the register first (D21 says up to two ordinary instructions retire before the internal NMI), so
  rtl-arch's confirmation is asked.
- Status: candidate, reproducer pending (rtl-arch T-053 X-11; security-relevant; owner question Q-015 filed
  2026-09-03 in dv/auto_dv/docs/gen_intervention_log.md, unanswered; default while pending: bug candidate,
  expected-fail for the first-beat class, not excluded from the gate)
- Feature: Load data write suppressed on a bus integrity error (rf_wr_suppress) (F-SEC-015, canonical:
  security.rst:88); cross-references Bus integrity on the data interface (MemECC only) (F-DMEM-041), Dummy
  instructions produce no record (cross-reference) (F-RVFI-024), Integrity error on an unexpected (spurious)
  data response (F-SEC-017)
- Plan items (expected-fail): TP-DMEM-064, TP-SEC-040, TP-RVFI-040
- rtl-arch alias: BUG-08 (gen_bug_reproducer_specs.md)
- RTL: rtl/ibex_load_store_unit.sv:514 (first-half status lsu_err_d = data_bus_err_i | pmp_err_q, no integrity term), :697-698 (RF write gated only by the completing beat's data_intg_err), :756 (alert); rtl/ibex_controller.sv:402-438 (internal NMI)
- Specification / intent: doc/03_reference/security.rst:88 ("Where load data has bad checkbits the write to the load's destination register will be suppressed"); the RISC-V specification is silent (Ibex feature). RTL less complete than the documented intent (dv_principles.md Section 4): checker follows the documented intent, expected-fail for the first-beat class.
- What happens: a misaligned load takes two bus beats. The register write is suppressed only when the beat
  that completes the load (the second) has bad check bits. When only the first beat is corrupted, the core
  still writes the destination register with the merged word. The alert and the internal NMI fire in both
  cases; only the register write leaks.
- Steps to reproduce:
  1. Set up (M-mode, MemECC on): x6 word-aligned; the data agent armed to corrupt the integrity bits of the
     FIRST response beat inside the buffer only (MEM_ERR_ARM, kind integrity, count 1); data_err_i = 0 on
     both beats.
  2. Do: lw x5, 2(x6) (effective address 4n + 2, two beats).
  3. RTL: rvfi_rd_addr = 5, rvfi_ext_rf_wr_suppress = 0, x5 = the merged data; one alert_major_bus_o pulse;
     internal NMI with mcause 0xFFFF_FFE0.
  4. Documentation: rvfi_rd_addr = 0, rvfi_ext_rf_wr_suppress = 1, x5 unchanged; the same alert and NMI.
  5. Control: the SECOND beat corrupted suppresses the write (both agree).
- Test: No test yet. Proposed tests to build: plan test groups gen_dmem_intg_xfail (TP-DMEM-064),
  gen_sec_alert_inject_dbus_first_beat_xfail (TP-SEC-040) and gen_rvfi_ext_rf_wr_suppress_xfail
  (TP-RVFI-040), with expected_fail: true. Scoping: (a) a directed program variant of
  gen_intg_span_directed.S with the corruption armed on the first word only, and a count knob for the arming
  in the cocotb module; (b) extends gen_ut_intg_span (dv/auto_dv/gen_tb/gen_tests/gen_ut_intg_span.py arms
  two corruptions on the buffer with MEM_ERR_ARM; count 1 arms the first access only) and its testlist
  entry; (c) test-writer, with tb-infra for the module knob; (d) S: the scoreboard's T-183 gate expects no
  register write for a load whose corruption the driver announced and compares the core's rd fields against
  no write, so the core's write raises [isa_rd], and the module's own assertion that a suppressed record
  exists fails too. CORRECTED by tb-infra's knob landing (dv/auto_dv/evidence/gen_tdd_b16_knob.md Section 8): the
  T-183 gate as built is entered only when the core asserts rvfi_ext_rf_wr_suppress, so in B16's case it checks
  nothing; the module's own assertion that a suppressed record exists fires on 8 of 8 seeds and is the
  seed-independent collected failure, while the isa_rd miss appears only when the flip lands in the merged
  half-word (16 of the 39 bit positions; 2 of 8 seeds in its sweep, Section 6). The doc-direction rule "an
  announced corruption of a load's word obliges a suppressed write" is not built: M, tb-infra; until it exists the
  expected-fail test's loud failure is the module assertion.
- Evidence: MEASURED by tb-infra with the arming-count knob at count 1 (dv/auto_dv/evidence/gen_tdd_b16_knob.md Sections
  3, 5, 6 and 9; retained logs dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l64_b16_c1_seed1_{run_header.txt,sim.log,
  stdout_excerpt.log,verdict.txt} and gen_fu_l64_b16_sweep16.log): the core writes rd with the merged word,
  rvfi_ext_rf_wr_suppress stays 0, the alert fires once and the internal NMI arrives with mtval = the load's own
  unaligned address 0x800002e2 (its Section 7); the module assertion fires on 8 of 8 seeds while the isa_rd miss appears
  on 2 of 8 (Section 6: the flip lands in the merged half-word on 16 of the 39 encoded bit positions, so on six of the
  eight seeds the merged word is clean and only the missing suppression remains, which is the constant part of the
  defect; a wrong VALUE in rd needs the injection in the data bits). Waveform
  confirmation (Section 9): beat 1 data_rdata_i 0x0101111111 (bit 28 flipped) against the clean beat 2, bus request
  phase identical to the count-2 control. The expected-fail test itself is test-writer's, not yet landed.
- Notes: the alert and the internal NMI do fire; only the rd write leaks the merged data. Security-relevant:
  owner question Q-015 (filed 2026-09-03, unanswered).

### B17: HPM counters 8, 11 and 12 over-count an instruction waiting in ID behind an outstanding WB memory access
- Rating: P2. The counts depend on memory latency; the workaround is to put independent instructions (a
  delay) between a load or store and the following branch, multiply or divide, so the response has arrived
  before that instruction reaches decode.
- Status: candidate, reproducer pending (rtl-arch T-053 X-13)
- Feature: HPM counters 8 (NumBranches), 11 (NumCyclesMulWait) and 12 (NumCyclesDivWait) over-count an
  instruction waiting in ID behind an outstanding WB memory access (bug candidate B17) (F-PMC-053,
  canonical); counter features mhpmcounter8 (NumBranches) counts every conditional branch, taken or not
  (F-PMC-039), mhpmcounter11 (NumCyclesMulWait) counts multiplier stall cycles (F-PMC-043), mhpmcounter12
  (NumCyclesDivWait) counts iterative divider stall cycles (F-PMC-044); cross-reference F-PMC-041 (B11)
- Plan items (expected-fail): TP-PMC-058, TP-PMC-059, TP-PMC-060, TP-BTALU-018
- rtl-arch alias: BUG-09 (gen_bug_reproducer_specs.md)
- RTL: rtl/ibex_id_stage.sv:886-934 (perf_branch_o in FIRST_CYCLE under instr_executing_spec), :1054-1057 (instr_executing_spec lacks ~outstanding_memory_access), :866-869 (state advances only under instr_executing), :1226-1227 (perf_mul_wait_o / perf_div_wait_o count deferred-start cycles)
- Specification / intent: doc/03_reference/performance_counters.rst:41 ("Number of branches (conditional)"): one count per branch; the RTL counts once per waiting cycle. Counters 7 (jumps) and 9 (taken) are exact (deduped by branch_jump_set_done_q). Direction (DV Lead): bug candidate, checker follows the doc for the waiting class; RTL-defined otherwise.
- What happens: a branch that reaches decode while the previous load or store still waits for its bus
  response asserts the branch event in every waiting cycle, so NumBranches gains one count per cycle instead
  of one per branch. The multiply and divide wait counters count the same waiting cycles for a multiply or
  divide in that position.
- Steps to reproduce:
  1. Set up (M-mode): mcountinhibit = 0; dummy_instr_en = 0; a data response delay K >= 4 cycles (regime knob
     knob_dmem_rvalid_delay = long, or the dbus_rvalid_min / dbus_rvalid_max plusargs); x9 != x10.
  2. Do: csrr t0, mhpmcounter8; lw x7, 0(x8); beq x9, x10, +8; nop; csrr t1, mhpmcounter8.
  3. RTL: t1 - t0 is about K (one count per cycle the beq waited in decode).
  4. Documentation: t1 - t0 = 1.
  5. Control: enough independent instructions between the lw and the beq (or a one-cycle response) gives 1.
- Test: No test yet. Proposed tests to build: plan test groups gen_pmc_hpm_b17_br_xfail (TP-PMC-058),
  gen_pmc_hpm_b17_mul_xfail (TP-PMC-059), gen_pmc_hpm_b17_div_xfail (TP-PMC-060) and gen_btalu_perf_b17_xfail
  (TP-BTALU-018), with expected_fail: true. Scoping: (a) a directed program as in the steps with the long
  data-response regime pinned from the command line, and a checker rule that predicts counter 8 as one per
  retired conditional branch (and counters 11 / 12 from the multiply and divide records); (b) extends
  gen_ut_lockstep with the directed program, and the counter model the plan names (ctr_hpm_exact,
  ctr_hpm_bound) for the rule; (c) test-writer for the program, tb-infra for the rule; (d) M: the shim holds
  the core's HPM values (synced), so the comparator cannot see the over-count; the counter-8 rule is simple
  (count branch records) but the bound rule for 11 / 12 needs the bus timing from the export; the whole
  counter model is L.
- Evidence: none yet.

### B18: rvfi_mem_rmask is non-zero and rvfi_mem_addr is the ALU result on every record that is not a store (RVFI-only)
- Rating: P3. Trace-only: the fields are wrong on records of instructions that access no memory; the memory
  accesses themselves are right.
- Status: observed in TB Infra's first lock-step run and counted in every lock-step run since; RVFI-port
  deviation; no architectural effect; the comparator classifies records by decoded opcode
- Feature: mem_addr / rmask / wmask for loads and stores (single record, unshifted mask) (F-RVFI-011,
  canonical); cross-reference the rvfi_proto checker row
- Plan items: none (no architectural item; the RVFI protocol item TP-RVFI-014 records the deviation in its
  caveat and applies mask rules only to decoded load / store records)
- rtl-arch alias: BUG-10
- RTL: rtl/ibex_core.sv:2085 and :2253-2260 (mask derived from lsu_type without an LSU-request qualifier; wmask clean because data_we_o is decode-qualified)
- Specification / intent: tools/specs/riscv-formal/docs/source/rvfi.rst:135-136, 143-144 (rmask non-zero only for memory operations; addr holds the accessed location)
- What happens: RVFI's read mask should be non-zero only on records of instructions that read memory. Ibex
  derives the mask from the decoded size field without checking that a memory request happened, so every
  record that is not a store carries rmask 1111 (or the mask of whatever size the bits decode to) and
  rvfi_mem_addr holds the ALU result of that instruction. The write mask is right, because the store enable
  is decode-qualified.
- Steps to reproduce:
  1. Set up: any program.
  2. Do: look at the RVFI record of a non-memory instruction, for example addi or lui.
  3. RTL: rvfi_mem_rmask = 4'b1111, rvfi_mem_addr = the ALU result.
  4. Specification: rvfi_mem_rmask = 0.
- Test: every lock-step test observes it and PASSES by policy: the scoreboard infers a read from the model's
  own access instead of the mask and counts the records (rvfi_rmask_on_nonload in the GEN_SB "ISA compare"
  summary line; 23002 in dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_l9_isa_cti_s1_stdout.log, seed 1
  of gen_test_isa_cti). No test fails on it: the RVFI protocol checker the plan names (rvfi_proto,
  TP-RVFI-014's caveat) is not built. No effort item is owed, because the deviation is fully observed; a loud
  test would need that checker with the rmask rule (M, tb-infra) and is worth building only if the owner
  wants an XFAIL entry for the RVFI-only class.
- Evidence: the GEN_SB counter in the retained lock-step logs (above); TB Infra's first lock-step
  observation (out_2a run, order 5, pc 0x8000008e, gen_bug_reproducer_specs.md BUG-10).
- Notes: same fact as fact-check X-15 / the TP-RVFI-014 checker caveat; ID-stage trap records also carry the
  garbage decode.

### B19: rvfi_trap is cleared on an illegal ebreak encoding variant when dcsr.ebreakm / ebreaku is set (RVFI-only)
- Rating: P3. Trace-only: the trap is taken correctly (mcause 2, mtval = the encoding, PC to mtvec); only the
  RVFI trap flag on that record is wrong.
- Status: candidate, reproducer spec available (rtl-arch confirmed at the RTL, T-053 follow-up; RVFI-only,
  BUG-04 / BUG-10 family; no architectural effect; informational item TP-ISA-057)
- Feature: ebreak that enters debug mode is not reported as a trap (F-RVFI-025, canonical: the
  illegal-variant case is its B19 note); ebreak (and c.ebreak) (F-ISA-034, the rs1 / rd != 0 illegal
  variants)
- Plan items: none as gate items (informational: TP-ISA-057)
- rtl-arch alias: BUG-11 (gen_bug_reproducer_specs.md)
- RTL: rtl/ibex_decoder.sv:739-740 sets ebrk_insn_o for funct12 0x001 regardless of rs1/rd and :757-759 raises illegal_insn when rs1 or rd != 0 (the illegal block :912-920 does not clear ebrk_insn_o); rtl/ibex_controller.sv:312-332 gives illegal_insn_q priority over ebrk_insn (mcause 2, mtval = encoding, PC to mtvec); rtl/ibex_core.sv:1885-1886 masks rvfi_trap with ~(ebrk_insn & ebreak_into_debug), ebreak_into_debug = dcsr.ebreakm/u per mode (:481)
- Specification / intent: rvfi.rst: rvfi_trap must be set for an instruction that cannot be decoded as legal
- What happens: an ebreak encoding with rs1 or rd not equal to zero is illegal. The decoder marks it both as
  an ebreak and as illegal; the controller correctly takes the illegal-instruction trap. The RVFI trap flag is
  masked for ebreak-into-debug records, and that mask still applies to the illegal variant when the matching
  dcsr bit is set, so the record shows no trap although a trap was taken.
- Steps to reproduce:
  1. Set up: enter debug mode (debug_req_i), set dcsr.ebreakm = 1 in the debug ROM, dret; an M-mode handler
     that records mcause and mtval and skips the instruction.
  2. Do: execute .word 0x00100173 (an ebreak encoding with rd = x2).
  3. RTL: the record has rvfi_trap = 0; mcause reads 2, mtval 0x00100173, execution continues at mtvec.
  4. Specification: the record has rvfi_trap = 1.
  5. Control: with the dcsr bit clear the record has rvfi_trap = 1; a legal ebreak with ebreakm set enters
     debug mode with rvfi_trap = 0 (known behaviour, F-RVFI-025).
- Test: No test yet. Proposed test to build: plan test group gen_isa_illegal_ebreak_info (TP-ISA-057,
  informational). Scoping: (a) a directed program with a .debug_rom that sets ebreakm and drets, then the
  illegal ebreak word and a handler; (b) extends gen_ut_dbg (DBG_REQ) with the directed program;
  (c) test-writer; (d) S: the ISA model traps on the illegal encoding, the core's record says no trap, and
  the comparator raises [isa_trap] ("model trapped, dut retired") on that record, which is the B19 signature
  the plan predicts.
- Evidence: none yet.
- Notes: no architectural effect; the comparator treats the record per the decoded illegal-instruction
  class. TB Infra's rule of deriving the trap from the PC flow for these encodings is not built.

### B20: fence.i increments mhpmcounter7 (NumJumps), which the documentation defines as unconditional jumps only
- Rating: P2. One extra count per fence.i in a counter the documentation defines precisely; software can
  subtract its fence.i count, or the owner can re-document (then B20 becomes a D entry).
- Status: candidate, reproducer spec available (rtl-arch reading, dv/auto_dv/evidence/gen_hpm_event_defs.md
  Section 3, D-NUMJUMPS-FENCEI; no run yet)
- Feature: mhpmcounter7 (NumJumps) counts jal/jalr (including c.j, c.jal, c.jr, c.jalr, cm.popret's return
  jump); the RTL also counts fence.i against the doc (B20) (F-PMC-038); item TP-PMC-061 (expected-fail);
  TP-PMC-040 keeps fence.i out of its windows
- Plan items (expected-fail): TP-PMC-061 (gen_pmc_hpm_b20_fencei_xfail)
- rtl-arch alias: D-NUMJUMPS-FENCEI (gen_hpm_event_defs.md); rtl-arch recommends following the doc
- RTL: rtl/ibex_decoder.sv:704-720 implements FENCE.I as a jump to the next PC (jump_in_dec_o, and jump_set_o in the first cycle, to flush the prefetch buffer and the icache); rtl/ibex_id_stage.sv:941 and rtl/ibex_controller.sv:687 count jump_set as perf_jump, so NumJumps moves by one per fence.i
- Specification / intent: performance_counters.rst:39 "NumJumps: Number of unconditional jumps (j, jal, jr, jalr)"; the privileged spec leaves hpm events implementation-defined, so the Ibex doc is the only definition of this counter; B by the B-versus-D criterion because the counter records an event the doc excludes (the B11 class: a wrong event, not a mis-stated convention like D6/D20)
- What happens: Ibex implements fence.i as a jump to the next instruction, which is how it flushes the
  prefetch buffer and the instruction cache. The jump counter counts that internal jump, so every fence.i
  adds one to NumJumps.
- Steps to reproduce:
  1. Set up (M-mode): mcountinhibit bit 7 = 0.
  2. Do: csrr t0, mhpmcounter7; fence.i; csrr t1, mhpmcounter7.
  3. RTL: t1 - t0 = 1.
  4. Documentation: t1 - t0 = 0.
- Test: No test yet. Proposed test to build: plan test group gen_pmc_hpm_b20_fencei_xfail (TP-PMC-061), with
  expected_fail: true. Scoping: (a) a directed program as in the steps and a checker rule that predicts
  NumJumps from the RVFI records (jal / jalr and their compressed forms, cm.popret's return; not fence.i);
  (b) extends gen_ut_lockstep with the directed program and the counter model the plan names (ctr_hpm_exact,
  counter 7) for the rule; (c) test-writer for the program, tb-infra for the rule; (d) M: the shim holds the
  core's HPM values (synced), so the comparator cannot see the extra count; the rule itself is simple, and
  the plan's bin CG-PMC-003.cr_variant_rel.fencei_gt is its witness.
- Evidence: none yet.
- Notes: severity low; the RTL fix is a one-term gate on perf_jump or a separate flush request; the owner may
  instead accept the RTL and re-document, in which case B20 becomes a doc defect and TP-PMC-061 a pass item
  (owner question Q-016, filed 2026-09-03 in dv/auto_dv/docs/gen_intervention_log.md, unanswered; default while
  pending: the checker follows the doc, TP-PMC-061 expected-fail); the independent counter model
  follows the doc and treats fence.i windows as the B20 witness (CG-PMC-003.cr_variant_rel.fencei_gt).

## 1b. Retained IDs that are not bug candidates (kept so plan and review references resolve)

B6 (RTL-defined: debug mode runs at M privilege, Sdext.adoc:32/:51), B9 (RTL-defined corner reachable only
under out-of-spec debug_req_i stimulus; record-only, informational item), B12 (documented behaviour,
exception_interrupts.rst:191 and cs_registers.rst:556; design-weakness note S4 in Section 2) and B21
(RTL-defined: the fetch address is combinational from top-level interrupt inputs, so the presented and booked
addresses can differ inside a request cycle; design property S6 in Section 2, and the observed divergence was
a TB modelling defect, gen_tb_defects.md T3). None carries an expected-fail item. All four are rated P3.

### B6: RECLASSIFIED (Critic C-20): an exception taken in debug mode forces priv_lvl to M
- Rating: P3. RTL-defined: the debug specification says debug mode runs with M privilege and leaves
  privilege-changing instructions in debug mode unspecified.
- Status: not a bug (RTL-defined, retained ID)
- Feature: Exception while in debug mode jumps to DmExceptionAddr; privilege forced to M (RTL-defined)
  (F-EXC-046)
- Plan items: none expected-fail (TP-EXC-046, TP-DBG-034 expect pass)
- rtl-arch alias: -
- RTL: rtl/ibex_cs_registers.sv:908
- Specification / intent: Sdext.adoc:32 (debug mode runs with machine-mode privilege), :51 (privilege-changing instructions in debug mode are UNSPECIFIED)
- What happens: a synchronous exception inside debug mode jumps to DmExceptionAddr and sets the privilege to
  M. The specification allows it.
- Test: none owed; TP-EXC-046 and TP-DBG-034 expect pass.
- Notes: NOT A BUG: RTL-defined; retained ID only so earlier references resolve.

### B9: dcsr.cause is written 0 if debug_req_i deasserts in the FLUSH cycle before DBG_TAKEN_IF
- Rating: P3. The stimulus is outside the specification (the debug module holds haltreq until the hart
  halts), so the value has no defined expectation; recorded as a robustness note.
- Status: RTL-defined corner under out-of-spec stimulus (a debug_req_i pulse shorter than the DECODE->FLUSH
  span; the debug spec holds haltreq until the hart halts): record only, not a gate item (rtl-arch T-041,
  Q-007 default); B-id retained
- Feature: debug_req_i deasserting in the FLUSH cycle records dcsr.cause = 0 (bug candidate) (F-DBG-006)
- Plan items: none expected-fail (record-only; informational item: TP-DBG-011)
- rtl-arch alias: - (recipe gen_bug_reproducer_specs.md B9)
- RTL: rtl/ibex_controller.sv:451-533 (debug_cause_d priority and one-cycle skew)
- Specification / intent: riscv-debug-spec Sdext.adoc (cause field must identify the entry reason)
- What happens: when a CSR access, fence or WFI is in decode, a debug request goes DECODE, FLUSH, DBG_TAKEN_IF.
  The cause value is registered one cycle earlier. If debug_req_i is already low in the FLUSH cycle the
  registered cause is 0 (none) although the core still enters debug mode. A held request (the specification's
  shape) records 3.
- Steps (out-of-spec stimulus, record only):
  1. Set up: a loop of csrr / fence instructions.
  2. Do: pulse debug_req_i high for one cycle so that it ends exactly in the FLUSH cycle of one of them; read
     dcsr in the debug ROM.
  3. RTL: cause reads 0.
  4. Specification: no defined value for a withdrawn request; a held request reads 3.
- Test: none owed (record only). TP-DBG-011 is the informational item; it would need a pulsed debug_req_i
  knob (the bridge's DBG_REQ hold policy 0, CYCLES, gives a bounded pulse: gen_ut_dbg.py) and a directed
  program: S, test-writer, only if the owner wants the corner recorded by a run.
- Notes: rtl-arch T-017: confirmed statically for the special-request path only (DECODE -> FLUSH ->
  DBG_TAKEN_IF); requires a debug_req_i pulse shorter than the DECODE->FLUSH span, which the debug spec
  forbids (haltreq is held until the hart halts). Classification: RTL-defined corner under out-of-spec
  stimulus, low severity; the RTL comment at rtl/ibex_controller.sv:515-518 acknowledges the window.

### B12: mret from an interrupt handler clears cpuctrlsts.sync_exc_seen, weakening double-fault detection
- Rating: P3. Documented Ibex behaviour with no RISC-V specification covering double-fault detection;
  carried as a design-weakness note for the security owner (S4), not as a bug.
- Status: documented behaviour, not a bug candidate: design-weakness note for the security owner
  (exception_interrupts.rst:191 and cs_registers.rst:556 say sync_exc_seen is cleared when mret is executed;
  no RISC-V specification covers double-fault detection). Carrying items expect pass with the note (Critic
  pre-review S-1; rtl-arch T-017 agrees)
- Feature: Software-written sync_exc_seen / double_fault_seen (F-SEC-025, canonical); aliases Software writes
  to cpuctrlsts.sync_exc_seen / double_fault_seen (F-EXC-057), F-CSR-091
- Plan items: none expected-fail (TP-EXC-056, TP-CSR-094, TP-SEC-025 expect pass with a design note)
- rtl-arch alias: -
- RTL: rtl/ibex_cs_registers.sv:964-965
- Specification / intent: documented Ibex behaviour: exception_interrupts.rst:191 and cs_registers.rst:556 ("cleared when mret is executed"); no RISC-V specification covers double-fault detection. No owner question is needed (no specification contradiction; the design-weakness note is carried to the closure report and Section 2 row S4)
- What happens: sync_exc_seen is set by a synchronous exception and cleared by any mret. If an interrupt
  handler runs inside an exception handler, its mret clears the flag, so a second synchronous exception in
  the original handler is not reported as a double fault.
- Steps (documented behaviour):
  1. Set up: take a synchronous exception (ecall); sync_exc_seen = 1.
  2. Do: in the handler enable interrupts and take one; its mret clears sync_exc_seen; then raise a second
     synchronous exception in the original handler.
  3. RTL: double_fault_seen_o does not rise.
  4. Intent: a double fault would be reported; the documentation states the RTL's behaviour.
- Test: none owed; the items pass with the design note.
- Notes: design weakness for the security owner (a second synchronous exception in the original handler is
  not detected after an interrupt handler's mret); not a bug candidate; items pass with the note.

### B21: RETAINED: the instruction-fetch address is combinational from the top-level interrupt inputs
- Rating: P3. An RTL-defined property, harmless against a slave that samples at the accepting clock edge; the
  divergence that raised the id was a testbench modelling defect (gen_tb_defects.md T3).
- Status: retained ID; not a bug candidate (design property S6 in Section 2)
- Feature: none assigned (recorded as design property S6)
- Plan items: none
- rtl-arch alias: -
- RTL: rtl/ibex_controller.sv:503-511, :539, :751; rtl/ibex_if_stage.sv:213, :214, :225-228; registered counterpart rtl/ibex_cs_registers.sv:262-264, :130
- Specification / intent: none settled (Section 2 row S6 states the two readings of the data-interface figure)
- What happens: within one request cycle the fetch address the core presents can change with an asynchronous
  interrupt input, so the address a slave sees mid-cycle can differ from the one the core books at the
  accepting clock edge. The core is self-consistent at every rising edge.
- Test: none; recorded only (the retained rtl-arch-010 block and export, Section 2 row S6).
- Notes: opened and closed in the same touch (change log v1i of 2026-09-05): the observed divergence was the
  memory agent sampling at the falling edge (TB defect T3, fixed at e6eb3a2).

## 2. Security-relevant RTL-defined behaviours (owner decision requested, not bugs)

All six rows are rated P3: the RTL is specification-legal or the specification is silent, and the owner
decides whether the behaviour stands.

| Ref | Behaviour | RTL | Owner question | Default applied | Rating |
|---|---|---|---|---|---|
| S1 (MEM-13) | Second half of a misaligned data access is issued after a first-half PMP fault; a faulting misaligned store performs its second-word write | rtl/ibex_load_store_unit.sv:489-531; rtl/ibex_core.sv:1063 | Q-DL-7 | modelled as RTL-defined, covered (F-PMP-087, TP-PMP-085) | P3 (spec-legal: a misaligned access may be split and partially performed) |
| S2 (CTRL-04) | Trap/debug entry updates CSRs and PC while fetch_enable_i is not On; invalid MuBi encodings act as Off with no alert | rtl/ibex_core.sv:644-649,1350-1351 | Q-DL-8 | checked as-is (F-RST-015, F-IMEM-023) | P3 (no specification covers fetch_enable_i) |
| S4 (B12) | mret from an interrupt handler clears cpuctrlsts.sync_exc_seen, so a second synchronous exception in the original handler is not detected (documented behaviour) | rtl/ibex_cs_registers.sv:962-965 | none needed (documented); noted for the closure report | items pass with the design note | P3 (documented) |
| S3 (MEM-05/19) | No defence against unsolicited or grant-cycle rvalid on either bus; integrity check runs on such responses | rtl/ibex_load_store_unit.sv:756-757; rtl/ibex_icache.sv:721 | Q-DL-9 | never driven in passing tests; one informational test per bus (TP-IMEM-040) | P3 (out-of-protocol stimulus) |
| S5 (WP12-F2) | A data-RAM corruption in one copy of a line held valid in two ways reports nothing when the flip clears a bit of the un-tweaked word the mux ORs: the hit-data mux ORs the matching ways, so the other copy restores the bit, the fetched word is correct and no minor alert is signalled; a flip that sets a bit stays visible | rtl/ibex_icache.sv:506-514, :585, :591-592 | none needed: the alert sentences (icache.rst:218, security.rst:107) are conditioned on an error being seen or detected and the ORed word is a correct codeword, so neither is breached; icache.rst:214 is phrased on RAM state and IS contradicted here, and it is written for one copy and corrected by D22; noted for the closure report | covered as a no-alert case (CG-IC-006.cp_no_alert_case.masked_duplicate_copy, F-IC-042 Notes); the duplicate is self-limiting by capacity and self-clearing on the next data error at that index | P3 (the fetched word is correct; a documentation gap, D22) |
| S6 (B21) | The core presents its instruction-fetch address combinationally from asynchronous top-level interrupt inputs, with no register in the path, so within one request cycle the address presented externally can differ from the address the core books at the accepting clock edge. Harmless against a slave that samples at that edge, and within the contract the instruction interface inherits from the data interface. NOT what made the rtl-arch-010 run fail: the core is self-consistent at every rising edge (pin, icache output pairing, fetch address, pc_if, pc_id, mcause) and the divergence there came from the TB agent latching a mid-cycle value (gen_tb_defects.md T3) | rtl/ibex_controller.sv:503-511, :539, :751; rtl/ibex_if_stage.sv:213, :214, :225-228; registered counterpart rtl/ibex_cs_registers.sv:262-264, :130 | Guard the property with an assertion that the address is stable while a request is outstanding? The document does not settle it. No address rule appears in PROSE in the instruction reference, the data interface or the integration document (a prose-keyword search, which by construction cannot match a timing figure). The data interface's transaction figure (doc/03_reference/load_store_unit.rst:100-118) does depict one address held across the request and grant cycles, but WaveDrom carries one value per signal per cycle, so it cannot express a sub-cycle requirement in either direction: read strictly as one address value per request cycle the core did not comply, having two within the cycle; read as a requirement at the accepting edge it did. Which reading governs is the question | Recorded only; no assertion adopted and no stimulus-shape reproducer built. Evidence: the retained rtl-arch-010 block and export at 07653dd, committed at dv/auto_dv/evidence/gen_irq_triage/gen_rtl_arch_010_served.yaml with its acceptance conditions in dv/auto_dv/evidence/gen_irq_triage/gen_rtl_arch_010_request.yaml and the export at dv/auto_dv/evidence/gen_irq_triage/gen_export.txt.gz, indexed by dv/auto_dv/evidence/gen_irq_triage/gen_index.md, which carries the 10 ps tick convention of the UVM timestamps and the export's original size, sha256 and line count. The rerun on a commit carrying both TB fixes, dv/auto_dv/evidence/gen_irq_triage/gen_irq_req2_rerun.yaml, does not bear on this property either way: it is quiet for a PRE-REGISTERED reason (0 UVM_ERROR, that seed running quiet at default bus timing once the schedule defect is gone), so rtl-arch's wave at 07653dd remains the only run that places the divergence | P3 (RTL-defined; the question is which reading of the interface figure governs) |

## 3. Doc defects (RTL is specification-legal or internally consistent; the Ibex doc is wrong or stale)

Merged list: reading report Section 5.3 plus rtl-arch A.2 (Critic C-23). The checker follows the RTL for
every row. Every row is rated P3 (the documentation is what is wrong); D2 carries a note because trusting the
documentation there changes the privilege an mret lands in.

| ID | Defect | Doc location | RTL | Features | Rating |
|---|---|---|---|---|---|
| D1 | mip reads the raw irq pins, not qualified by mie | cs_registers.rst:246 | rtl/ibex_cs_registers.sv:408-412,495-501 | F-CSR-032 | P3 |
| D2 | Illegal mstatus.MPP value (01/10) legalises to U; doc says M | cs_registers.rst:138 | rtl/ibex_cs_registers.sv:783-786 | F-CSR-024 (BUG-05 alias) | P3 (spec-legal WARL choice; software that trusts the doc lands in U-mode after mret instead of M) |
| D3 | mcause is software-writable; doc marks the fields read-only | cs_registers.rst:213-217 | rtl/ibex_cs_registers.sv:730-733,803 | F-CSR-046 | P3 |
| D4 | tdata1 reset/constant value is 0x2800_1048 (m=1,u=1), doc says 0x2800_1000 | cs_registers.rst:360 | rtl/ibex_cs_registers.sv:1848-1866 | F-TRG-003 / F-CSR-081; the doc's own field table at cs_registers.rst:362-404 (m = 1 at bit 6, u = 1 at bit 3) already yields 0x2800_1048; RTL composition rtl/ibex_cs_registers.sv:1848-1864 with execute = tmatch_control_q reset 0 at :1806-1812 (rtl-arch R5, gen_t102_rtl_facts.md); read as 28001048 in the Test Writer's rst_boot_s1 log; reproducer csrr t0, tdata1 in M-mode after reset | P3 |
| D5 | RETIRED: dcsr.ebreaks writable is bug candidate B15 | - | - | - | - |
| D6 | NumLoads/NumStores count a misaligned access once; doc says twice | performance_counters.rst | rtl/ibex_load_store_unit.sv:468-475 | F-PMC-034/036 | P3 |
| D7 | Divide latency: RTL 37 cycles total (36 stall); docs say 37 (instruction_decode_execute.rst) and 37 stall (pipeline_details.rst:63) | instruction_decode_execute.rst, pipeline_details.rst:63 | rtl/ibex_multdiv_fast.sv:412-526 | F-MUL-012 | P3 |
| D8 | bfp executes in one cycle; doc table lists Zbf as multi-cycle | instruction_decode_execute.rst:95 | rtl/ibex_alu.sv:266-275, rtl/ibex_decoder.sv:1302 | F-BIT-030 | P3 |
| D9 | icache.rst describes instr_pmp_err_i and branch_spec_i ports that do not exist and a 72-bit data RAM (RTL: 2 x 39-bit codewords, LineSizeECC 78) | icache.rst:202-208,236-241,271-274 | rtl/ibex_icache.sv:13-69,305-310; rtl/ibex_core.sv:557 | F-IC-006, F-IMEM-028, F-IC-036 | P3 |
| D10 | mtval on an instruction access fault is the faulting fetch address (pc or pc+2), not 0 | cs_registers.rst:235 | rtl/ibex_controller.sv:859-861 | F-EXC fetch-fault entries | P3 |
| D11 | security.rst claims early completion of multiplication by zero/one is removed under DIT; the single-cycle multiplier has no such path | security.rst:27 | rtl/ibex_multdiv_fast.sv:140-260 | F-DIT-005 | P3 |
| D12 | debug.rst says trigger CSRs trap outside debug mode; RTL and cs_registers.rst:345 allow M-mode reads and silently drop M-mode writes | debug.rst:54-55 | rtl/ibex_cs_registers.sv:636-662,1775-1780 | F-DBG-050, F-TRG-007 | P3 |
| D13 | cs_registers.rst says fence.i is guaranteed to fetch a new scramble key; icache.rst:113-116 and RTL ignore fence.i while a key request is pending | cs_registers.rst:544-545 | rtl/ibex_icache.sv:1229-1240 | F-IC key-request entries | P3 |
| D14 | security.rst implies an internal NMI for any bus-integrity mismatch; instruction-side errors give the major alert plus a fetch fault, no NMI | security.rst:85-87 | rtl/ibex_id_stage.sv:613 | F-IMEM-027, F-SEC integrity entries | P3 |
| D15 | cs_registers.rst CSR table omits implemented mcounteren, mstatush, menvcfg/menvcfgh, mconfigptr and the cycle/instret/hpmcounter aliases | cs_registers.rst table | rtl/ibex_cs_registers.sv read mux | F-CSR-0xx (machine info / trap setup) | P3 |
| D16 | performance_counters.rst parameter text stale (NumMHPMCounters 1..8, WidthMHPMCounters); MHPMCounterNum=10 gives mhpmcounter3..12 | performance_counters.rst | rtl/ibex_cs_registers.sv:1667-1707 | F-PMC-020 | P3 |
| D17 | load_store_unit.rst / instruction_fetch.rst list separate 7-bit intg ports; at ibex_core they are bits [38:32] of the 39-bit ports | load_store_unit.rst:34-36,52-54; instruction_fetch.rst:68 | rtl/ibex_core.sv:74,84,86 | F-IMEM/F-DMEM width entries | P3 |
| D18 | cs_registers.rst tselect text names parameter DbgHwNumLen (it is DbgHwBreakNum); scontext heading gives 0x7AA (table and RTL: 0x5A8) | cs_registers.rst tselect/scontext | rtl/ibex_pkg.sv:511,518 | F-TRG-002, F-CSR trigger entries | P3 |
| D20 | mhpmeventN reads 1 << (N - 3) (mhpmevent3 = 0x1 .. mhpmevent12 = 0x200); doc says 1 << N | performance_counters.rst:133-147 | rtl/ibex_cs_registers.sv:185, 1602-1619 | F-PMC-020, F-CSR-061 (fact-check X-3) | P3 |
| D21 | up to two ordinary instructions can retire between a corrupted data response and the internal NMI; doc says at most one (to be confirmed by the first directed integrity-error sim, inventory UNVERIFIED-4) | exception_interrupts.rst:87-88 | rtl/ibex_controller.sv:402-438 | F-IRQ-04x internal-NMI entries (fact-check X-10) | P3 |
| D19 | security.rst dummy_instr_mask table lists 4 of the 8 legal values | security.rst | rtl/ibex_dummy_instr.sv:33-148 | F-DIT-012 | P3 |
| D22 | icache.rst gives one cause for a line allocated in several ways, a branch into an address being prefetched, and calls the consequence a minor performance inefficiency; an ECC-correction refetch is a second, undocumented cause, and with one copy corrupted the consequence extends to a corruption that reports nothing (S5). Second stale sentence: :214, "Any error (single or double bit) in any RAM will effectively cancel a cache hit in IC1", is phrased on RAM state and holds only for a line in one way; in the masked duplicate case the error is in the RAM and the hit is not cancelled | icache.rst:73-74, :214 | rtl/ibex_icache.sv:506-514, :534-535, :591-592 | F-IC-042, F-IC-021 | P3 |

## 4. Change log
- v1i (2026-09-05 UTC): S6 (B21) added to Section 2, the fetch-address combinational property, recorded not guarded; B21 retained in Section 1b and NOT opened as a bug candidate (the observed divergence is a TB modelling defect, gen_tb_defects.md T3); scope note now names the TB defect register.
- v1h (2026-09-03 UTC): B11 cites the B-versus-D criterion (round-4 low); criterion text names B11 and D6.
- v1g (2026-09-03 10:20 UTC): round-3 lows: B17 feature IDs (F-PMC-053/039/043/044), B19 canonical F-RVFI-025, B9 note aligned to record-only, B6/B9/B12 moved to Section 1b (retained IDs, not bug candidates), B-versus-D criterion stated.
- v1f (2026-09-03 09:39 UTC): B19 confirmed by rtl-arch as BUG-11 (RTL chain and reproducer spec).
- v1e (2026-09-03 09:30 UTC): item lists refreshed after plan v2b (B16 items TP-DMEM-064/TP-SEC-040/TP-RVFI-040; B17 items TP-PMC-058/059/060, TP-BTALU-018); B16 canonical feature F-SEC-015; B19 (RVFI-only, OQ-10) added pending rtl-arch confirmation.
- v1d (2026-09-03 08:52 UTC): B16 (BUG-08, security-relevant, Q-015), B17 (BUG-09), B18 (BUG-10) added from rtl-arch T-053 / TB Infra; D20, D21 added; B12 citation corrected and moved to a Section 2 note (S4).
- v1c (2026-09-03): B9 reclassified record-only (informational item); B14 feature corrected to F-RVFI-015; expected-fail lists refreshed after the plan v2a fold.
- v1b (2026-09-03): expected-fail item lists refreshed from the plan parts after the Critic pre-review fold-in (B6/B12/B14 carry no expected-fail items; B15 items TP-CSR-075, TP-DBG-018).
- v1a (2026-09-03): folded rtl-arch T-017 (BUG-06 = B1, BUG-07 = B8 confirmed reachable, B9 out-of-spec stimulus, B10/B11 confirmed) and T-041 (BUG-04/B14 downgraded pending sim); B12 reclassified as documented behaviour with a design note (Critic pre-review S-1).
- v1 (2026-09-03): opened with B1..B15 (B6 reclassified per Critic C-20; B15 added per C-21; B5 re-cited per C-22), S1..S3, D1..D19 (D5 retired).
- v1i (2026-09-03 12:43 UTC): B20 added from rtl-arch's HPM event definitions (fence.i counted by NumJumps; doc followed, expected-fail TP-PMC-061); rtl-arch's second candidate (illegal branch/JALR encodings counted before the trap) was withdrawn by rtl-arch (rtl/ibex_decoder.sv:905-918 clears jump/branch on illegal_insn) and gets no row; the counter model's expected deviations are D6, B7, B11, B17 and B20.
- v1j (2026-09-03 13:59 UTC): B13 promoted from RVFI-cosmetic note to a DUT bug candidate of the RVFI-only class per rtl-arch R11 and the batch-2 observation (64 of 64 rows per seed); one-line fix at rtl/ibex_core.sv:2084 and the comparator convention recorded (Orchestrator ruling). R10 (mtval = 0 on a breakpoint exception is spec-legal; the pc arm is CHERIoT-only) is a shim convention, not a bug: cited in the plan where the cause-3 mtval expectation is stated.
- v1k (2026-09-03 14:49 UTC): B13 reworded per the v2i diff review (CM12-M-2, L-3): the comparator mask is TB Infra's T-144 to encode, not a present fact (gen_rvfi_pkg.sv:452 at b8332f9 has no mask); the ruling is cited as LOG-032.
- v1l (2026-09-04 06:36 UTC): S5 and D22 added for tb-infra's finding WP12-F2 with rtl-arch's traced mechanism. Classified RTL-defined behaviour with a documentation gap, NOT a bug candidate: multi-way allocation of one line is documented (icache.rst:73), the ECC-correction refetch is an undocumented second cause of it, and the masked case never detects an error at all, so neither alert sentence (icache.rst:218, security.rst:107, both conditioned on detection) is triggered. F-IC-042's What and Notes carry the corrected consequence and both causes.
- v1m (2026-09-04 07:04 UTC): S5's rationale narrowed and D22 given its second stale sentence (icache.rst:214, phrased on RAM state, contradicted in the masked case) per the v3z review; S5 and F-IC-042 name the domain of the clearing flip, the un-tweaked word the hit-data mux ORs.
- v2 (2026-09-08 01:25 UTC): owner request of 2026-09-07: plain language, numbered steps, feature names, test commands, effort scoping, P-ratings. Section 0 added (glossary, rating and effort definitions, the test-command form and where the FSDB lands, the summary table, the policies moved here and shortened). Every B entry rewritten in the Section 1 layout with its feature named first, its steps as a numbered list, its test command (B4, B8 exist; B13 and B18 pass by policy with the raw-rule witness given) or "No test yet" with the item-5 scoping, and its rating (P1: B8; P2: B1, B2, B7, B10, B11, B16, B17, B20; P3: the rest, S1-S6 and D1-D22); B10 and B16 marked pending rtl-arch confirmation. B21 given its own Section 1b entry. Section 2 and Section 3 tables gained a Rating column. No plan item id, RTL cite or specification cite was dropped and every feature id is kept, with one correction: version 1's B8 cross-reference "F-DIT-032 item" named an id that has no feature heading (the case is the plan item TP-DIT-032), so it is now written as the plan item; the B-versus-D criterion, ruling B4-R1 and the B8 mechanism text are kept with their wording. Two rtl-arch records cite version-1 line numbers of this file (gen_b4_rtl_facts.md:6 "gen_bug_log.md:60", gen_t102_rtl_facts.md:8 "gen_bug_log.md:274"); they resolve by id (B4, D20) and are rtl-arch's to re-point at their next touch.
- v2a (2026-09-08 01:32 UTC): Orchestrator citation instruction of 2026-09-08: every Spike source cite carries the clone-relative path tools/riscv-isa-sim/... (the clone's own copy of the allowed upstream project, not the fenced cosim fork); the glossary names Spike as the reference model in those words.
- v2b (2026-09-08 01:59 UTC): B16 and B20 said their owner questions were still to be filed; Q-015 and Q-016 were filed on 2026-09-03 and are unanswered, so both entries now say so with the default applied while pending; Section 0.3 states the LOG-103 evidence bar (red and green retained runs plus a waveform confirmation) for the proposed quick tests.
- v2c (2026-09-08 02:24 UTC): B2 and B7 have tests: their Test, Status and Evidence read the landed expected-fail entries
  gen_prv_debug_b2_xfail and gen_pmc_minstret_xfail (seed 1, XFAIL, signatures, controls, FSDB locations) from
  dv/auto_dv/evidence/gen_tdd_bug_tests.md, the earlier scoping kept under Notes; the summary table follows. Section
  0.6 records the counter-rule direction ruling of 2026-09-08 (the B13 convention applied to the B11, B17 and B20
  checker rules: RTL default with counted accommodation, knob to the documentation rule for the expected-fail run).
- v2d (2026-09-08 02:45 UTC): B16 measured by tb-infra's arming-count knob (gen_tdd_b16_knob.md at e7e7a94): the Evidence field, the
  corrected scoping clause (the suppressed-write gate is never entered in B16's case; the module assertion is the
  seed-independent mechanism; the suppression rule itself is an M item for tb-infra) and the qualified effort cell;
  Section 0.5 states the citation-anchor convention (a bare row label such as | D20 | matches twice); the B16 and B10
  ratings wait for rtl-arch's record. The TB defect T11 (the scoreboard's internal-NMI mtval correction inside the
  suppress-flag block) is opened in gen_tb_defects.md from the same landing.
