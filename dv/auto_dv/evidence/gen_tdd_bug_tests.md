# Bug-candidate test records (P2 entries of gen_bug_log.md version 2)

Owner: test-writer. Evidence bar: LOG-103 (owner directive of 2026-09-08). Each section is one expected-fail test and
carries what ran, the seed, the verdict with its failure signature, the passing control, and the waveform reading with
the FSDB location. The mutation proof, the seed sweep, the fcov-expectation manifest and the full record template of
gen_tdd_test_template.md are not required for this work and are not here.

Common to every section below unless a section says otherwise:

- Build: gen_tb compiled by dv/auto_dv/tb/gen_tb_local.sh from an export of commit
  14c2f481730f028c24d34af449eb1d157b4c97b9, sources sha256 prefix d9a0553bd4e0b326, into
  dv/auto_dv/work/test-writer/head_export20/dv/auto_dv/work/test-writer/out_tw20 (the work directory is gitignored).
  The tests were handed on the later base d04ada46f1688ec8ab7314c9f2943cacb2b30121; the range
  14c2f48..d04ada4 changes plan documents, two evidence documents and four files under dv/auto_dv/tools only, and no
  RTL, testbench, environment, flow, isa-shim or stimulus file, so the build is the current one for the handed tree.
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

## Record log

- 2026-09-08T02:13:23Z: sections 1 and 2 written from the runs of the same date on out_tw20.
