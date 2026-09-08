# Bug-candidate test records (P2 entries of gen_bug_log.md version 2)

Owner: test-writer. Evidence bar: LOG-103 (owner directive of 2026-09-08). Each section is one expected-fail test and
carries what ran, the seed, the verdict with its failure signature, the passing control, and the waveform reading with
the FSDB location. The mutation proof, the seed sweep, the fcov-expectation manifest and the full record template of
gen_tdd_test_template.md are not required for this work and are not here.

Common to every section below unless a section says otherwise:

- Builds: two, both compiled by dv/auto_dv/tb/gen_tb_local.sh from an export of the commit named, into a gitignored work
  directory. Build A, Sections 1 and 2: export of 14c2f481730f028c24d34af449eb1d157b4c97b9, sources sha256 prefix
  d9a0553bd4e0b326, dv/auto_dv/work/test-writer/head_export20/dv/auto_dv/work/test-writer/out_tw20. Those two tests were
  handed on the later base d04ada46f1688ec8ab7314c9f2943cacb2b30121, and the range 14c2f48..d04ada4 changes plan
  documents, two evidence documents and four files under dv/auto_dv/tools only, so no file the build is made of. Build B,
  Sections 3 to 5: export of 2f46b1d69f7074be51696e86218b754c36536c1d, sources sha256 prefix 047718cec02eec6a,
  dv/auto_dv/work/test-writer/head_export21/dv/auto_dv/work/test-writer/out_tw21. Build B carries TB Infra's landing 64,
  so the arming-count knob Section 4 needs is in it. Build C, Sections 6 to 8: export of
  c74662939ccd763c67f87a37842dad980ef68030, sources sha256 prefix b60a9b31cee9f9e7,
  dv/auto_dv/work/test-writer/head_export22/dv/auto_dv/work/test-writer/out_tw22. Build C carries TB Infra's landing 65,
  the counter model, whose rules are the collected failure of those three sections; its sources digest equals the identity
  TB Infra's own landing message quotes, b60a9b31cee9f9e7.
- Runner: dv/auto_dv/tests/gen_fixtures/gen_run_fixture.sh with GEN_TB_PYROOT set to the export root, SEED=1.
- Images: built by dv/auto_dv/stim/gen_program.py --directed <source> --seed 1 from the committed program named in the
  section. The run headers name the image under a session scratch directory; the flow's own reproduction command
  rebuilds the image from the committed source, so nothing in a record depends on that directory surviving.
- Verdicts: dv/auto_dv/flow/gen_verdict.py, the flow's pass/fail authority, with --expected-fail for a red and without
  it for a control (the flag is what turns the FAIL into XFAIL, as the testlist entry does in a flow run).
- Waves: the red was re-run with -ucli -do on a rendering of dv/auto_dv/flow/gen_dump.tcl; the FSDB values below were
  read with the fsdb-mcp-server tools on the file the section names.

## 1. B2: mstatus.MPRV applied to debug-mode loads although dcsr.mprven is 0 (TP-PRV-035)

Test: gen_prv_debug_b2_xfail (tier check, measured: false, expected_fail: true, owner test-writer), cocotb module
dv/auto_dv/gen_tb/gen_tests/gen_ut_dbg.py, program dv/auto_dv/stim/gen_directed/gen_prv_debug_b2_directed.S.

Program shape. All PMP regions stay OFF, so a data access checked as U-mode is denied by the no-match rule
(rtl/ibex_pmp.sv access_fault_check). The program clears mstatus.MPP to U, sets mstatus.MPRV and parks in a register-only
loop; no load or store follows the MPRV write, because with MPP = U every data access of the parked program would be
denied as well. The program carries its own .debug_rom (gen_program.py links it in place of gen_debug_rom_stub.S): the
halt entry jumps to a body that loads one word from the program window, outside the debug-module window, and drets; the
exception entry at DmHaltAddr + 8 drets too, which is where the core lands when the load is denied.

Red. Retained: gen_tdd_logs/test_writer/gen_bug_b2_dbg_mprv_red1_{stdout.log,sim.log,verdict.txt}. Seed 1. Verdict XFAIL,
reason "expected-fail: uvm_error at sim.log:33 (isa_trap)". Signature, the first of four scoreboard rows:

    UVM_ERROR dv/auto_dv/env/gen_rvfi_pkg.sv(260) @ 1157500: uvm_test_top.env.sb [isa_trap] dut trapped, model retired 1
    trap=0 cause=00000000 (order=304 pc=1a110814 insn=000e2e83 trap=1 intr=0 rd=x0/00000000 mem=800002e8 w0000 r0000
    mode=3 cyc=1152)

followed by [isa_pc] pc model=1a110818 dut=1a110808 (the model drets from the ROM body, the core from DmExceptionAddr),
the pair repeating on the module's second debug entry, and the collected module assertion "GEN_UT_DBG: 4 ISA mismatches
across the debug entries". A FAIL through any other mechanism is not the B2 red.

Green control. gen_prv_debug_b2_ctrl_directed.S is the same program with mstatus.MPRV cleared instead of set, so the
ROM's load is checked with the core's own M privilege on both sides. Retained: gen_bug_b2_dbg_mprv_ctrl1_*; verdict PASS,
UVM_ERROR 0, GEN_UT_DBG_PASS. The control has no testlist entry of its own (the pattern of gen_zcmp_dummy_popret_directed.S).

Waveform. out_tw20/bug_b2_dbg_mprv_red1_waves/waves.fsdb (run header retained as
gen_bug_b2_dbg_mprv_red1_waves_run_header.txt). At 11575 ns the core is in debug mode (debug_mode = 1) with
priv_mode_id = 3, that is M, while priv_mode_lsu = 0, that is U: the MPP privilege is what checks the data access. The
record of that instruction is the ROM's load (rvfi_pc_rdata = 1a110814) with rvfi_trap = 1, and data_req_o has no
transition between 11500 ns and 11620 ns, so the denied load never reached the data bus.

Reproduction once the entry is committed:

    python3 dv/auto_dv/flow/gen_regress.py --repro gen_prv_debug_b2_xfail 1 --waves --tag b2_repro

## 2. B7: dummy instructions counted in minstret (TP-PMC-013, TP-DIT-019)

Test: gen_pmc_minstret_xfail (tier check, measured: false, expected_fail: true, owner test-writer), cocotb module
dv/auto_dv/gen_tb/gen_tests/gen_ut_lockstep.py, program
dv/auto_dv/stim/gen_directed/gen_pmc_minstret_dummy_directed.S, plusarg +gen_ut_boot_retire=20.

Program shape. cpuctrlsts (0x7C0) is written with 4: dummy_instr_en set, dummy_instr_mask 0, the highest insertion rate,
as gen_zcmp_dummy_directed.S does. minstret is read into t1, 64 nops run, minstret is read into t2, the dummies are
turned off again and the program computes t4 = t2 - t1, the delta the privileged specification fixes at 65 (the 64 nops
and the first csrr). The program then stores 1 to tohost and spins.

Red. Retained: gen_bug_b7_minstret_red1_{stdout.log,sim.log,verdict.txt}. Seed 1. Verdict XFAIL, reason "expected-fail:
uvm_error at sim.log:32 (isa_rd)". Signature, the two scoreboard rows:

    [isa_rd] rd model=x7/00000048 dut=x7/0000006f (order=73 pc=8000019a insn=b02023f3 ... cyc=208)
    [isa_rd] rd model=x29/00000041 dut=x29/00000068 (order=76 pc=800001a4 insn=40638eb3 ... cyc=217)

The first is the second minstret read (0x48 = 72 in the model, 0x6f = 111 in the core); the second is the program's own
subtraction, where the model measures 0x41 = 65, the specification's value, and the core 0x68 = 104, so 39 dummy
instructions were counted at this seed. The module reports "retired 79 consumed 79 mismatches 2" and its assertion
"GEN_UT_LOCKSTEP: 2 ISA mismatches" is the collected failure. How many dummies an LFSR inserts is decided by the seed, so
another seed gives other values and another mismatch count; the mechanism is the same and a FAIL through any other
mechanism is not the B7 red.

Green control. gen_pmc_minstret_dummy_ctrl_directed.S is the same instruction stream, the cpuctrlsts write included, with
the written value 0, so no dummy is inserted. Retained: gen_bug_b7_minstret_ctrl1_*; verdict PASS, UVM_ERROR 0,
GEN_UT_LOCKSTEP_PASS. No testlist entry of its own.

Waveform. out_tw20/bug_b7_minstret_red1_waves/waves.fsdb (header retained as
gen_bug_b7_minstret_red1_waves_run_header.txt). dummy_instr_wb is high from 1025 ns to 1055 ns and rvfi_valid is low from
1035 ns to 1065 ns, yet cs_registers_i.minstret_raw still steps from 0x8 to 0x9 at 1035 ns and from 0x9 to 0xa at 1045 ns:
the counter advances twice over instructions the trace never reports, which is the bug in one picture.

Reproduction once the entry is committed:

    python3 dv/auto_dv/flow/gen_regress.py --repro gen_pmc_minstret_xfail 1 --waves --tag b7_repro

That command is verified, not assumed. Run with the out root pointed at a scratch tree it synced the mirror, compiled a
waves build, built the program from the committed source and reported "gen_pmc_minstret_xfail seed=1: XFAIL
(expected-fail: uvm_error at sim.log:50 (isa_rd))", one xfail of one, with the waveform at
runs/gen_pmc_minstret_xfail_1/waves.fsdb. The flow's own sim.log puts that first collected line at :50 where the local
fixture puts it at :32, because the flow's log carries more preamble; the row and the mechanism are the same.

## 3. B1: dret to U-mode leaves mstatus.MPRV set (TP-PRV-014)

Test: gen_prv_debug_b1_xfail (tier check, measured: false, expected_fail: true, owner test-writer), cocotb module
dv/auto_dv/gen_tb/gen_tests/gen_ut_dbg.py, program dv/auto_dv/stim/gen_directed/gen_prv_debug_b1_directed.S. Build B.

Program shape, four cooperating parts. The M-mode setup programs one execute-only PMP region (NAPOT, 64 bytes) over the
U-mode probe and leaves every other region OFF, so a U-mode instruction fetch of the probe is allowed while a U-mode data
access to the probe word is denied by the no-match rule; it loads the probe word's address into a register and parks in a
register-only loop. The program's own .debug_rom arms mstatus itself before every resume (MPP = M, MPRV = 1), writes
dcsr.prv = U and dpc = the probe, and drets. The probe loads the word and then executes ecall. The vector table's entry 0
jumps to one M-mode loop. That last part is what bounds the run: the core that completed the load reaches the same handler
the faulting model already took, and both settle in the same loop, so the comparator's rows are the divergence itself plus
the three records it takes to rejoin, not an unbounded drift. The debug ROM arms mstatus on every entry because the probe's
ecall leaves MPP = U behind and the module's second debug entry must resume into the same state.

Red. Retained: gen_tdd_logs/test_writer/gen_bug_b1_dret_mprv_red1_{stdout.log,sim.log,verdict.txt}. Seed 1. Verdict XFAIL,
reason "expected-fail: uvm_error at sim.log:32 (isa_trap)". Signature, the first two rows:

    [isa_trap] dut retired, model retired 0 trap=1 cause=00000005 tval=80000298 (order=315 pc=80000140 insn=00082783
    trap=0 intr=0 rd=x15/b1b1b1b1 mem=80000298 w0000 r1111 mode=3 cyc=1290)
    [isa_rd] dut wrote x15/b1b1b1b1, model wrote nothing (same record)

pc 80000140 is gen_u_probe and 80000298 is gen_b1_probe. The model takes a load access fault, cause 5, with the probe
address in mtval, as the debug specification requires of a resume below M; the core completes the load and leaves the
probe word in x15. The module reports "GEN_UT_DBG: 18 ISA mismatches across the debug entries", nine per debug entry over
three records. A FAIL through any other mechanism is not the B1 red.

The run also carries 145 [crash_dump] rows. That checker compares the core's crash_dump exception_pc / exception_addr
mirror with the model's mepc / mtval, and the two sides took different traps by construction (the model the load fault at
the probe, the core the ecall after it), so it cannot agree once they diverge. The rows are a consequence of the designed
divergence, not a second finding, and the checker is left on rather than silenced with +gen_chk_crash_dump.

Green control. gen_prv_debug_b1_ctrl_directed.S is the same four parts with mstatus.MPRV cleared instead of set before
each dret, so the probe's load is checked with U privilege on both sides and both take the fault at the same record.
Retained: gen_bug_b1_dret_mprv_ctrl1_*; verdict PASS, UVM_ERROR 0, GEN_UT_DBG_PASS. No entry of its own.

Waveform. out_tw21/bug_b1_dret_mprv_red1_waves/waves.fsdb. At 12905 ns the core is out of debug mode (debug_mode = 0)
with priv_mode_id = 0, that is U, while priv_mode_lsu = 3, that is M, and mstatus_q.mprv = 1 with mstatus_q.mpp = 3: the
resume to U-mode left MPRV set. In the same cycle data_req_o = 1 with data_addr_o = 80000298, so the load reached the data
bus with M privilege, which is the leak (contrast Section 1, where a U-checked access never reaches the bus).

Reproduction:

    python3 dv/auto_dv/flow/gen_regress.py --repro gen_prv_debug_b1_xfail 1 --waves --tag b1_repro

## 4. B16: a misaligned load with a corrupted first beat still writes rd (TP-DMEM-064)

Test: gen_dmem_intg_xfail (tier check, measured: false, expected_fail: true, owner test-writer), cocotb module
dv/auto_dv/gen_tb/gen_tests/gen_ut_intg_span.py, program dv/auto_dv/stim/gen_directed/gen_intg_span_directed.S with
+gen_ut_intg_span_arm_count=1. Build B.

No new program was needed. The bug log's scoping asks for a variant of the intg-span program with the corruption armed on
the first word only, but TB Infra's arming-count knob (landing 64, record dv/auto_dv/evidence/gen_tdd_b16_knob.md) keeps
the armed address range spanning both words of the misaligned load at every count, so the count alone selects the first
bus access and the committed program is the stimulus.

Red. Retained: gen_bug_b16_first_beat_{stdout.log,sim.log,verdict.txt} under the red1 name. Seed 1. Verdict XFAIL, reason
"expected-fail: uvm_error at sim.log:34 (isa_rd)". The seed-independent designed failure is the module's own assertion,

    GEN_UT_INTG_SPAN: no record with rf_wr_suppress (the spanning load's corrupted halves should suppress its write)

which TB Infra measured on 8 of 8 seeds at this count. At seed 1 the first collected line is the scoreboard row

    [isa_rd] rd model=x11/22221111 dut=x11/22220111 (order=8 pc=80000118 insn=00252583 mem=800002e2 cyc=50)

the merged word the core wrote, differing from the model's in one bit of the upper half-word; that row appears on 2 of 8
seeds because the injected flip reaches the merged half-word only sometimes (gen_tdd_b16_knob.md Section 6). The run also
carries 21 [crash_dump] rows from the TB gap TB Infra reported in that record's Section 7; they are not part of the B16
red.

Green control. The same program at the default arming count 2, which is the committed gen_ut_intg_span entry's own
configuration: both words are corrupted, the core suppresses the write, and the module finds its suppressed record.
Retained: gen_bug_b16_first_beat_ctrl1_*; verdict PASS, UVM_ERROR 0, GEN_UT_INTG_SPAN_PASS.

Waveform. out_tw21/bug_b16_first_beat_red1_waves/waves.fsdb. The bus alert pulses for one cycle at 490 ns, so the
corruption was detected. The load's own record is valid at 550 ns and reads rvfi_pc_rdata = 80000118, rvfi_mem_addr =
800002e2, rvfi_rd_addr = 0b (x11), rvfi_rd_wdata = 22220111 and rvfi_ext_rf_wr_suppress = 0: the write was not suppressed
and the merged word, including the corrupted bit, went to the register file while the alert was already out.

Reproduction:

    python3 dv/auto_dv/flow/gen_regress.py --repro gen_dmem_intg_xfail 1 --waves --tag b16_repro

## 5. B10: an ebreak entry records cause 2 when the next address matches tdata2 (TP-TRG-020), NO ENTRY YET

The program and its control are committed with this hand, gen_trg_ebreak_cause_directed.S and
gen_trg_ebreak_cause_ctrl_directed.S, but there is NO testlist entry, because the checking mechanism the bug log expects
does not witness the bug and a passing control does not exist yet. The finding is recorded here so the next owner of the
question starts from measurements.

Program shape. The trigger CSRs are writable in debug mode only, so the program parks until a debug request arrives and
its multi-entry debug ROM does the arming: it counts entries in memory, and on the first it writes tdata1 (the execute bit
is the only writable one, rtl/ibex_cs_registers.sv:1789) and tdata2 = gen_b10_target, sets dcsr.ebreakm, points dpc at a
sequence whose ebreak sits four bytes before that address, and drets. On every later entry it reads dcsr and dpc, stores
both, and then resumes past an ebreak, disarms on a trigger, or resumes in place on a halt request.

What the core does, from the ROM's own dcsr read (order 330, pc 1a110828, insn 7b002e73) in two runs that differ only in
whether tdata1 is armed:

    trigger armed:      dut dcsr = 40008083, cause 2 (trigger)
    trigger not armed:  dut dcsr = 40008043, cause 1 (ebreak)

so the cause is 2 where the debug specification says 1, and the control run shows the field is right when nothing is armed
on the following address. dpc agrees with the model in both runs: the ROM's dpc read raises no row, so only the cause field
is wrong.

Why there is no entry. The model reads dcsr = 400080c3, cause 3 (halt request), in BOTH runs, so the comparator raises
[isa_rd] on the ROM's dcsr read either way and cannot tell the bug from the correct behaviour; the control fails too
(153 mismatches against the red's 417). The reason is the comparator, not the model's CSR modelling:
dv/auto_dv/env/gen_rvfi_pkg.sv:377-379 arms the model's debug entry through halt_request for every entry, and Spike maps
halt_request to DCSR_CAUSE_DEBUGINT = 3 (tools/riscv-isa-sim/riscv/execute.cc:211-212) while its own ebreak path would
record DCSR_CAUSE_SWBP = 1 (insns/ebreak.h with dcsr.ebreakm, execute.cc:347-349). TB Infra has the measurement and the
recommendation: let the model take its own trap_debug_mode when the entry follows an ebreak, and the comparator becomes
the witness with no new checker; a cause rule in gen_dbg_checker is the alternative the bug log names. The entry is one
testlist entry away once either lands, on this same program.

Waveform, the RTL-level picture. out_tw21/bug_b10_cause_red1_waves/waves.fsdb. At 15705 ns the decode stage holds the
ebreak (pc_id = 80000140) while the fetch stage already holds the armed address (pc_if = 80000144 = gen_b10_target); in
that same cycle trigger_match_i = 1 and the controller's debug_cause_d = 2, and three cycles later pc_if becomes 1a110800,
the debug ROM entry. So the trigger match, evaluated on the fetch-stage PC, wins over the ebreak that is actually entering
debug mode.

A second observation from the same runs, reported to tb-infra and rtl-arch and NOT part of B10 (it is present in the
control too): rvfi_order skips one value at each debug entry an instruction causes. The red's export
(out_tw21/bug_b10_cause_red1/gen_export.txt) has orders 318, 319, 320, 322 and later 343, 345; the missing 321 and 344 sit
where the ebreak at gen_b10_seq and the trigger-matched instruction at gen_b10_target would be, and neither emits a
record. The testbench's rvfi_proto rule (gen_rvfi_pkg.sv:143) and sva_rvfi_order_incr flag it twice per run, which is why
both B10 runs' verdicts name rvfi_order as their first collected line. rtl-arch answered the classification question from
these runs in dv/auto_dv/evidence/gen_rvfi_order_debug_entry_rtl_facts.md: the index advances under a condition that
catches instructions flushed in decode while emission needs writeback or the trap bit, both of which are absent for a
retained ebreak, the interface definition forbids the gap, and the deviation is of the B13 and B18 trace-only class with
P3 recommended, while the comparator's contiguity rule is correct as it stands. No RTL mechanism is stated here on my own
authority.

## 6. B20: fence.i counted as a jump (TP-PMC-061), and how B20, B11 and B17 are tested

Sections 6, 7 and 8 share one design, so it is stated once here. Each bug has a directed program of mine with two or
three read windows on the counter under test, and each program compares every window with the value
doc/03_reference/performance_counters.rst defines for the event, sets a bit of a verdict word per violation, stores the
window differences and the verdict to memory, and stores the end-of-test code 1 when nothing was violated or 0x100 plus
the bits when something was. The counter rules of TB Infra's landing 65 (dv/auto_dv/env/gen_counter_model.sv, record
dv/auto_dv/evidence/gen_tdd_counters.md) are the collected failure: each of the four direction knobs follows the RTL at
its default 1 and the documentation at 0, so the pair of entries per bug differs in exactly one knob. The cocotb module
gen_ut_counters is the fire-check: it reads the program's own differences back through +gen_ut_ctr_delta_sym and
+gen_ut_ctr_delta_expect and refuses a run whose numbers are not the ones the RTL is known to produce, which is what
makes a green rule mean the rule judged this behaviour rather than nothing. The six entries are TB Infra's, folded into
the testlist by me with one correction recorded at the end of Section 8.

The lock-step comparator sees none of it, and that is measured, not assumed: every one of the six runs reports
"mismatches 0" and the default-direction runs report UVM_ERROR 0. The ISA shim mirrors the core's HPM values, so a
counter bug cannot reach the comparator, which is why these three bugs needed a checker of their own.

B20. Entries gen_ut_counters_b20_jumps (default, PASS) and gen_ut_counters_b20_jumps_xfail (documentation,
+gen_ctr_rtl_jumps_fencei=0, expected_fail: true), program gen_pmc_fencei_jump_directed.S, seed 1, Build C. The three
windows read mhpmcounter7 around a fence.i, around two nops and around a call with its return; the differences are
1, 0 and 2 with the verdict word 1, and the program's end-of-test code is 0x00000101, bit 0 for the fence.i window.

Red, retained gen_bug_b20_fencei_doc1_*: verdict XFAIL, reason "expected-fail: uvm_error at sim.log:32
(ctr_hpm_exact)", signature

    [ctr_hpm_exact] mhpmcounter7 advanced 1, 0 predicted: read 00000001 -> 00000002, cycles 40..56, order 10

one firing, and the nop and call windows raise nothing, so the rule accuses only the fence.i.

Green, two of them. The default-direction entry is the paired green: the same program and run with the knob at 1, where
the rule accepts the count and reports it as one B20 accommodation (retained gen_bug_b20_fencei_default1_*, PASS,
UVM_ERROR 0). The second green is my control program gen_pmc_fencei_jump_ctrl_directed.S, the same three windows with
the fence.i replaced by a nop, which stores the pass code 1 and passes on gen_ut_lockstep (retained
gen_bug_b20_fencei_ctrl1_*): it shows the program's own comparison against the documentation can pass, which the paired
green does not show because the knob, not the program, is what changes there.

Waveform. out_tw21/bug_b20_fencei_red1_waves/waves.fsdb, Build B. At 1035 ns the decode stage holds pc_id 8000011a with
instr_rdata 0000100f, the fence.i, and in that cycle cs_registers_i.mhpmcounter_incr is 00000081, so bit 7, the NumJumps
event, is asserted for it (bit 0 is mcycle). The counters the record quotes are Build C's; this reading is the event
pulse itself, which Build B and Build C share.

Reproduction:

    python3 dv/auto_dv/flow/gen_regress.py --repro gen_ut_counters_b20_jumps_xfail 1 --waves --tag b20_repro

## 7. B11: not-taken branches counted as taken under data-independent timing (TP-PMC-043, TP-BTALU-016)

Entries gen_ut_counters_b11_taken (default, PASS) and gen_ut_counters_b11_taken_xfail (documentation,
+gen_ctr_rtl_taken_dit=0, expected_fail: true), program gen_pmc_dit_branch_directed.S, seed 1, Build C. Two windows read
mhpmcounter9 around the same sixteen never-taken branches, the first with cpuctrlsts.data_ind_timing set and the second
with it clear; the differences are 16 and 0 with the verdict word 1, and the end-of-test code is 0x00000101.

Red, retained gen_bug_b11_dit_doc1_*: verdict XFAIL, reason "expected-fail: uvm_error at sim.log:32 (ctr_hpm_exact)",
two firings:

    [ctr_hpm_exact] mhpmcounter9 advanced 16, 0 predicted: read 00000000 -> 00000010, cycles 48..176, order 29
    [ctr_hpm_exact] mhpmcounter9 advanced 1, 0 predicted: read 00000010 -> 00000011, cycles 176..200, order 34

The first is the sixteen never-taken branches of the armed window. The second is the program's own check branch, which
runs while the mode is still set and is counted for the same reason, so it is the same finding, not a second one; the
mode-off window raises nothing.

Green, two of them: the default-direction entry, where the rule accepts both windows and reports two B11 accommodations
(retained gen_bug_b11_dit_default1_*, PASS, UVM_ERROR 0), and my control program gen_pmc_dit_branch_ctrl_directed.S,
which leaves data_ind_timing clear and passes with the code 1 on gen_ut_lockstep (retained gen_bug_b11_dit_ctrl1_*).

Waveform. out_tw21/bug_b11_dit_red1_waves/waves.fsdb, Build B. data_ind_timing is high, and at 1085 ns the decode stage
holds the first never-taken beq (pc_id 80000124) while mhpmcounter_incr is 00000201, so bit 9, the taken-branch event, is
asserted; the record's next PC is the fall-through 80000128, so the branch was not taken. At 1075 ns the same branch
raises bit 8, the conditional-branch event, which is correct and stays correct in both directions.

Reproduction:

    python3 dv/auto_dv/flow/gen_regress.py --repro gen_ut_counters_b11_taken_xfail 1 --waves --tag b11_repro

## 8. B17: counters 8, 11 and 12 over-count behind an outstanding memory access (TP-PMC-058, 059, 060, TP-BTALU-018)

Entries gen_ut_counters_b17_wait (default, PASS) and gen_ut_counters_b17_wait_xfail (documentation,
+gen_ctr_rtl_branches_wait=0 +gen_ctr_rtl_wait_cycles=0, expected_fail: true), program gen_pmc_wb_wait_directed.S, seed
1, Build C, with the data response pinned by +gen_dbus_rvalid_min=8 +gen_dbus_rvalid_max=8. Six windows in three pairs:
counter 8 around a branch that decodes behind an outstanding load and then around the same branch with eight independent
instructions after the load, and the same shape for counter 11 with a multiply and counter 12 with a divide. The
differences are 8, 1, 6, 0, 43 and 36 with the verdict word 21, and the end-of-test code is 0x00000115, bits 0, 2 and 4.

Red, retained gen_bug_b17_wbwait_doc1_*: verdict XFAIL, reason "expected-fail: uvm_error at sim.log:32
(ctr_hpm_exact)", three firings:

    [ctr_hpm_exact] mhpmcounter8 advanced 8, 1 predicted: read 00000000 -> 00000008, cycles 49..66, order 17
    [ctr_hpm_bound] mhpmcounter11 advanced 6, at most 1 documented (1 multiply record(s) at 1 cycles each, ...)
    [ctr_hpm_bound] mhpmcounter12 advanced 43, at most 36 documented (1 divide record(s) at 36 cycles each, ...)

one per counter, and all three calibration windows of the program raise nothing: counter 8 counts 1 for the separated
branch, counter 11 does not move for the separated multiply, and counter 12 moves by exactly the divider's own 36 cycles.
That pairing is what makes the three firings attributable to the outstanding access rather than to the instructions.

Green, two of them: the default-direction entry, where the rule accepts the counts and reports the B17 accommodations
(retained gen_bug_b17_wbwait_default1_*, PASS, UVM_ERROR 0), and my control program gen_pmc_wb_wait_ctrl_directed.S,
which applies the workaround the bug log names (eight independent instructions between the load and the event in every
window) and passes with the code 1 on gen_ut_lockstep (retained gen_bug_b17_wbwait_ctrl1_*).

Waveform. out_tw21/bug_b17_wbwait_red1_waves/waves.fsdb, Build B. From 1155 ns to 1230 ns mhpmcounter_incr holds
00000109 with bit 8, the conditional-branch event, asserted while pc_id stays 8000012a, the window's branch, and
data_rvalid_i is low the whole time; the response arrives at 1230 ns and the branch leaves decode in the next cycle. So
the event is held for every cycle the branch waits, which is where a count of one branch per window becomes a count per
cycle.

RETRACTED, and replaced by measurement. An earlier version of this section said the three load-shadowed differences were
build-sensitive, quoting 6, 1, 7, 0, 41, 36 on one build against 8, 1, 6, 0, 43, 36 on another. That was wrong: the two
figures came from two different PROGRAMS, not two builds. The first belonged to the image crc32 0x454f07f9 with 184
words, which is this program before its documented-expectation self-check was added; the committed program is crc32
0xf75e1215 with 237 words. Measured afterwards, the committed program gives

    export of 2f46b1d, gen_ut_lockstep    [8, 1, 6, 0, 43, 36]
    export of c746629, gen_ut_lockstep    [8, 1, 6, 0, 43, 36]
    export of c746629, gen_ut_counters    [8, 1, 6, 0, 43, 36, 21]

byte-identical across both builds and both modules, so there is no build sensitivity and no module sensitivity, which is
what TB Infra measured independently. The retained runs of that check are gen_bug_b17_head_build{B,C}_*.

What IS variable, from TB Infra's grant-delay probe (gen_fu_l66_b17_gnt_probe.log in its landing 66): words 2 and 4, the
counter 11 and 12 windows behind the load, take 5, 6 and 7 and 42 and 43 across two seeds and three grant-delay
settings, because the fetch side moves when the multiply or divide reaches decode relative to the load's response;
pinning the grant delay does not stabilise them. Words 0, 1, 3 and 5 and the verdict word are stable in all six of its
runs. Both B17 entries therefore carry ranges rather than exact values on those two words,
+gen_ut_ctr_delta_expect=8,1,4:10,0,40:46,36,21, TB Infra's tight bounds.

The programs' own checks pin no measured value at all, only documented ones: B20 requires 0 for the fence.i window, 0
for the nop window and 2 for the call window; B11 requires 0 for both branch windows; B17 requires 1 for each counter-8
window, 0 for each counter-11 window and EQUALITY between the two counter-12 windows, because the divider's own stall
count is not a documented constant.

THE ONE CORRECTION I MADE TO TB INFRA'S SIX ENTRIES. Its file wrote each expect value unquoted inside a YAML flow list,
for example `plusargs: [..., +gen_ut_ctr_delta_expect=1,0,2,1]`. YAML splits a flow list on those commas, so the value
became `+gen_ut_ctr_delta_expect=1` followed by three bare integers, which the flow's own testlist loader refuses
(gen_flow_util plusarg_name on an int). I quoted the value in the fold, changed nothing else, asserted that every folded
entry parses to the author's object with that one field corrected, and told TB Infra. The six runs above used the full
expect string on the command line, so the measurements are of the intended configuration.

## 9. B7 again: the wait-counter half (TP-DIT-019)

Test: gen_dit_dummy_xfail (tier check, measured: false, expected_fail: true, owner test-writer), cocotb module
dv/auto_dv/gen_tb/gen_tests/gen_ut_lockstep.py, program dv/auto_dv/stim/gen_directed/gen_pmc_dummy_wait_directed.S,
seed 1, Build C. Section 2 covers B7's minstret half; this is the half the lock-step comparator cannot reach, because
the shim mirrors the core's HPM values.

Program shape. Four windows in two pairs. The first pair reads mhpmcounter12 (NumCyclesDivWait) around eight divides
with cpuctrlsts.dummy_instr_en clear and then around the same eight divides with it set; the second pair does the same
for mhpmcounter11 (NumCyclesMulWait) around eight multiplies. Each cpuctrlsts write sits OUTSIDE both windows of its
pair, so the interval a counter rule judges holds nothing but the program's own arithmetic. The documented intent is that
a dummy instruction has no functional impact on processor state (doc/03_reference/security.rst), so each pair's two
windows must read the same; the program compares them and sets a verdict bit per disagreeing pair. The fetch stage's
dummy types include MUL and DIV (rtl/ibex_dummy_instr.sv), which is what makes the divide pair the interesting one.

Red. Retained: gen_bug_b7w_dummywait_red1_{stdout.log,sim.log,verdict.txt}. Verdict XFAIL. The collected failure is the
module's assertion "GEN_UT_LOCKSTEP: program did not report pass" with the end-of-test code in the log line:

    GEN_UT_LOCKSTEP retired 106 consumed 106 mismatches 0 tohost 0x00000101

Bit 0 is the divide pair. The windows measure 288 divide-wait cycles with dummies off, which is exactly the eight
divides' own 36 cycles each, and 289 with them on; the multiply pair reads 0 and 0, so bit 1 stays clear, which is the
documented behaviour for a one-cycle multiplier and is this program's internal control. The figures are identical at
seeds 1, 2 and 7, because the dummy insertion pattern comes from a build-time LFSR seed rather than the run seed.

The excess is small and I state it as measured rather than as the bug log's wording implies: over eight divides it is one
cycle, and over thirty-two divides (a probe, not the committed program) two. So the observable is not a dummy divide's
whole 36-cycle stall being added; it is the divide-wait counter advancing in a cycle a dummy occupies.

Green control. gen_pmc_dummy_wait_ctrl_directed.S is the same instruction stream with the cpuctrlsts value 0, so no
dummy is inserted, each pair's windows agree and the program stores the pass code. Retained:
gen_bug_b7w_dummywait_ctrl1_*; verdict PASS, UVM_ERROR 0, GEN_UT_LOCKSTEP_PASS.

Why this entry is NOT on gen_ut_counters, measured. I ran the program under TB Infra's counter module with
+gen_ctr_rtl_wait_cycles=0, the documentation direction for counters 11 and 12, and the rule does NOT fire: both
directions report UVM_ERROR 0, the model's own summary reads "windows exact=0 bound=6 misses exact=0 bound=0" and its
accommodation line reports "B7 dummy=0". Its counter-11 and 12 bound is a per-instruction latency ceiling, and a
one-cycle excess sits inside it. The module also does not judge the end-of-test code by design, so on that module the
program's own finding is invisible and the run passes. Hence gen_ut_lockstep, where the end-of-test code is asserted.
TB Infra has the measurement; if it wants the rule to witness this half, the tighter form is the paired-window equality
this program already computes.

Waveform. out_tw22/bug_b7w_dummywait_red1_waves/waves.fsdb. Inside the dummies-on divide window (cycles 411 to 716)
three dummy instructions reach decode. At 5285 ns the second of them is in decode (dummy_instr_id = 1) while
cs_registers_i.mhpmcounter_incr reads 0x00001005: bit 12, the divide-wait event, is asserted in that cycle, and bit 2,
minstret, with it. So one picture carries both halves of B7: a dummy instruction is counted by minstret and, in the same
cycle, by the divide-wait counter.

Reproduction:

    python3 dv/auto_dv/flow/gen_regress.py --repro gen_dit_dummy_xfail 1 --waves --tag b7wait_repro

## Record log

- 2026-09-08T02:13:23Z: sections 1 and 2 written from the runs of the same date on out_tw20.
- 2026-09-08T02:57:18Z: sections 3 (B1), 4 (B16) and 5 (B10, recorded without a testlist entry) written from the
  runs of the same date on build B; handed on base dab298859cca07e8e4a86e01d9af3b665b955bc0.
- 2026-09-08T03:16:38Z: sections 6, 7 and 8 (B20, B11, B17) written from the runs of the same date on build C, on
  TB Infra's six folded entries; handed on base 5a64b1e989cfd4e08275f93e72c556ade9748a1e.
- 2026-09-08T03:40:42Z: Section 8's build-sensitivity claim retracted and replaced by the four-run measurement of the
  committed program; Section 2 gained the verified flow reproduction; Section 9 (B7's wait-counter half) written from the
  runs of the same date on build C; handed on base f77ac6ee7c9cfd638086401b8c1e424b7669b15e.
