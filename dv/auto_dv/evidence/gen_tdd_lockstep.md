# TDD transcript: RVFI monitor + scoreboard with the Spike lock-step comparator (build step 2a)

Components: `dv/auto_dv/tb/gen_rvfi_if.sv`, `dv/auto_dv/env/gen_rvfi_pkg.sv` (gen_rvfi_txn, gen_rvfi_monitor,
gen_scoreboard), `dv/auto_dv/isa/gen_isa_dpi_pkg.sv` + the shim library (`gen_tdd_isa_shim.md`), the
`evt_isa_records` / `evt_isa_mismatch` bridge fields, `+gen_sb_trace`, `+gen_ut_lockstep_min_ratio_pct`.
Test: `dv/auto_dv/gen_tb/gen_tests/gen_ut_lockstep.py` (written first): the boot flow plus "every retired
record was consumed by the comparator with zero mismatches". Out-trees `dv/auto_dv/work/tb-infra/out_2a_red/`
(red), `out_2a/` (green attempts). Owner: tb-infra.

## 1. Red (the test on the step-1c top: no RVFI monitor, no scoreboard)

```
# RED run (lock-step test on the step-1c top: no RVFI monitor, no scoreboard; compile out_2a_red vcs exit 0)
Command: /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_2a_red/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build
0.00ns INFO     cocotb.regression                  pytest not found, install it to enable better AssertionError messages
5190.00ns INFO     cocotb.gen_tb_top                  GEN_UT_LOCKSTEP retired 169 compared 0 mismatches 0 tohost 0x00000001
assert compared * 100 >= retired * min_ratio, f"GEN_UT_LOCKSTEP: compared {compared} of {retired} retired records (< {min_ratio}%)"
AssertionError: GEN_UT_LOCKSTEP: compared 0 of 169 retired records (< 90%)
** TESTS=1 PASS=0 FAIL=1 SKIP=0                                              5190.01           0.06      90266.84  **
Time: 5190010 ps
```

## 2. Attempt 1 (comparator wired; 136 collected `uvm_error`s on the Zc program, all TB-side interpretation)

- `isa_mem` on every non-store record: `rvfi_mem_rmask` is 1111 on records that read nothing, with
  `rvfi_mem_addr` = the ALU result. RTL: `rvfi_stage_mem_rmask[i] <= data_we_o ? 4'b0000 :
  rvfi_mem_mask_int` (rtl/ibex_core.sv:2085) with the mask following `lsu_type` alone (:2253-2260); no
  LSU-request qualifier. An RVFI-port deviation reported to rtl-arch and the DV Lead as a bug candidate;
  the scoreboard now infers a DUT read from the model's own access, compares `wmask` directly (it is
  gated), and counts the observation (`rvfi_rmask_on_nonload` in the GEN_SB report).
- `isa_insn` once per Zcmp sequence: the micro-op records carry the EXPANDED 32-bit instruction in
  `rvfi_insn`; the encoding the model executes as one instruction is `rvfi_ext_expanded_insn` (16 bits).
  The fold now compares that.

## 3. Attempt 2 (0 mismatches on Zc; the riscv-dv program exposed a model gap)

- Zc: retired 169, compared 148 + 21 micro-op records folded, mismatches 0; the TEST's ratio metric
  compared `compared` alone against retirements and failed at 148/169: `evt_isa_records` now counts
  records CONSUMED (compared once each, Zcmp micro-ops through their fold).
- riscv-dv seed 7: 8516 mismatches, all downstream of order 17: `csrs mseccfg, x4` (0x74725073)
  retired on the DUT but trapped (cause 2) in the model: Spike implements mseccfg only with the
  `smepmp` extension, which Ibex implements (MML/MMWP/RLB). The ISA string (single source
  `gen_tb_knobs.yaml`) gained `_smepmp`; standalone Spike (`gen_program.py --spike-check`) accepts it.
- Forced red of the compare path (TB_CONTRACT Section 3): `+gen_isa_string=rv32imc_zicsr_zifencei`
  (a model without Zc/Zb) against the Zc program: 637 collected mismatches, cocotb FAIL. The compare fires.

## 4. Green (attempt 3: `smepmp` in the model, records-consumed metric; compile `out_2a`, vcs exit 0)

Directed Zc program:

```
lockstep_zc:
Command: /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_2a/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan +gen_mem_image=/
UVM_INFO dv/auto_dv/env/gen_rvfi_pkg.sv(167) @ 0: uvm_test_top.env.sb [GEN_SB] ISA model ready: pc=80000080 mtvec=80000001
UVM_INFO dv/auto_dv/env/gen_env_pkg.sv(251) @ 519000: uvm_test_top [GEN_BASE_TEST] finish_req seen at cycle 514, commands consumed 65, retired 169
UVM_INFO dv/auto_dv/env/gen_agents_pkg.sv(321) @ 519000: uvm_test_top.env.dbus_agent [gen_bus_agent] dbus gnt=1..3(short) rvalid=1..3(short) cap=2(cap2) err=0/1000(none) intg=0/1000(none)x1: grants=29 responses=28 injected_err=0 injected_intg=0
UVM_INFO dv/auto_dv/env/gen_agents_pkg.sv(321) @ 519000: uvm_test_top.env.ibus_agent [gen_bus_agent] ibus gnt=1..3(short) rvalid=1..3(short) cap=8(cap8) err=0/1000(none) intg=0/1000(none)x1: grants=140 responses=139 injected_err=0 injected_intg=0
UVM_INFO dv/auto_dv/env/gen_rvfi_pkg.sv(121) @ 519000: uvm_test_top.env.rvfi_mon [GEN_RVFI_MON] records=169 irq_markers=0
UVM_INFO dv/auto_dv/env/gen_rvfi_pkg.sv(292) @ 519000: uvm_test_top.env.sb [GEN_SB] ISA compare: records=148 mismatches=0 folded=31 draft_b=0 traps=0 irq_entries=0 dbg_entries=0 rvfi_rmask_on_nonload=126
UVM_ERROR :    0
UVM_FATAL :    0
[GEN_RVFI_MON]     1
0.00ns INFO     cocotb.regression                  pytest not found, install it to enable better AssertionError messages
5190.00ns INFO     cocotb.gen_tb_top                  GEN_UT_LOCKSTEP retired 169 compared 179 mismatches 0 tohost 0x00000001
** TESTS=1 PASS=1 FAIL=0 SKIP=0                                              5190.01           0.07      73549.86  **
Time: 5190010 ps
```

riscv-dv seed-7 program (debug section, 29375 words), 2000 records in lock-step:

```
lockstep_s7:
Command: /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_2a/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan +gen_mem_image=/
UVM_INFO dv/auto_dv/env/gen_rvfi_pkg.sv(167) @ 0: uvm_test_top.env.sb [GEN_SB] ISA model ready: pc=80000080 mtvec=80000001
UVM_INFO dv/auto_dv/env/gen_env_pkg.sv(251) @ 9407500: uvm_test_top [GEN_BASE_TEST] finish_req seen at cycle 9403, commands consumed 65, retired 2000
UVM_INFO dv/auto_dv/env/gen_agents_pkg.sv(321) @ 9407500: uvm_test_top.env.dbus_agent [gen_bus_agent] dbus gnt=1..3(short) rvalid=1..3(short) cap=2(cap2) err=0/1000(none) intg=0/1000(none)x1: grants=547 responses=547 injected_err=0 injected_intg=0
UVM_INFO dv/auto_dv/env/gen_agents_pkg.sv(321) @ 9407500: uvm_test_top.env.ibus_agent [gen_bus_agent] ibus gnt=1..3(short) rvalid=1..3(short) cap=8(cap8) err=0/1000(none) intg=0/1000(none)x1: grants=2955 responses=2955 injected_err=0 injected_intg=0
UVM_INFO dv/auto_dv/env/gen_rvfi_pkg.sv(121) @ 9407500: uvm_test_top.env.rvfi_mon [GEN_RVFI_MON] records=2000 irq_markers=0
UVM_INFO dv/auto_dv/env/gen_rvfi_pkg.sv(292) @ 9407500: uvm_test_top.env.sb [GEN_SB] ISA compare: records=2000 mismatches=0 folded=0 draft_b=0 traps=1 irq_entries=0 dbg_entries=0 rvfi_rmask_on_nonload=1452
UVM_ERROR :    0
UVM_FATAL :    0
[GEN_RVFI_MON]     1
0.00ns INFO     cocotb.regression                  pytest not found, install it to enable better AssertionError messages
94075.00ns INFO     cocotb.gen_tb_top                  GEN_UT_LOCKSTEP retired 2000 compared 2000 mismatches 0 tohost 0x00000001
** TESTS=1 PASS=1 FAIL=0 SKIP=0                                             94075.01           0.34     275645.95  **
Time: 94075010 ps
```

Forced red kept as the proof that the compare fires (model without Zc/Zb):

```
lockstep_forced_red:
Command: /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_2a/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan +gen_mem_image=/
UVM_INFO dv/auto_dv/env/gen_rvfi_pkg.sv(167) @ 0: uvm_test_top.env.sb [GEN_SB] ISA model ready: pc=80000080 mtvec=80000001
0.00ns INFO     cocotb.regression                  pytest not found, install it to enable better AssertionError messages
5190.00ns INFO     cocotb.gen_tb_top                  GEN_UT_LOCKSTEP retired 169 compared 179 mismatches 637 tohost 0x00000001
AssertionError: GEN_UT_LOCKSTEP: 637 ISA mismatches
** TESTS=1 PASS=0 FAIL=1 SKIP=0                                              5190.01           0.09      59807.62  **
Time: 5190010 ps
```

What green proves: every retired record of both programs was consumed by the comparator (Zcmp micro-ops
through their fold), the model stepped once per record with matching pc, instruction, retirement/trap
status, rd address and value, memory access presence, address and full-word store data, privilege and
next pc; UVM_ERROR 0, cocotb PASS. The forced red shows the same path producing 637 collected
`uvm_error`s (isa_pc, isa_insn, isa_rd, isa_pc_next) when the model diverges, so a silent comparator is
excluded. The three fixes on the way (Zcmp insn source, rmask-independent memory compare, `smepmp`) are
disclosed in Sections 2 and 3; none touched the DUT.

Bookkeeping note (found in the GEN_SB report of the green runs, fixed after them, re-verified with the
next compile): the report showed `folded=31` for the Zc program although only 21 micro-op records precede
their sequences' last records; the last record of each of the 10 sequences was counted both as compared
and as folded, so `evt_isa_records` read 179 for 169 retirements (the ratio check passed on `>=`). The
fold counter now excludes the last record; the compare itself was unaffected.

## 5. T-068 (2026-09-03): corrections, the committed comparator's green runs, per-field evidence

Retained logs: `dv/auto_dv/evidence/gen_tdd_logs/lockstep/` (manifest `gen_tdd_logs/gen_manifest.md`).

Corrections to Sections 2-4 (cross-model 2a mediums 2-4, low 1):

- Attempt 1 (136 collected errors) and attempt 2 (8516 mismatches) have no retained artifact: UNRETAINED.
- The Section 4 green logs were produced by the pre-fix fold counter (`folded=31`, `compared 179` of 169
  retirements); they are retained for the record as `gen_lockstep_zc_2a_prefix_sim.log`,
  `gen_lockstep_s7_2a_prefix_sim.log`, `gen_lockstep_forced_red_2a_prefix_sim.log` and are NOT the green run of the
  committed comparator. The ratio check `compared * 100 >= retired * min_ratio` passed on that over-count; the
  test now asserts `consumed == retired` exactly and the knob `+gen_ut_lockstep_min_ratio_pct` is gone.
- "What green proves" (Section 4) claimed that rd and memory matched for every retired record. At 3be5a34 the
  Zcmp fold compared pc and the 16-bit encoding only; the 31 micro-op records of the 10 cm.* sequences had no
  rd or memory compare. That sentence was wrong for those records. T-068 implements the C5.2 union compare:
  the set of GPR writes over the sequence against the model's logged register writes (`gen_isa_reg_write`),
  the ordered store list (address, data) against the model's logged data writes (`gen_isa_mem_write`), the
  ordered load addresses against the model's logged reads (`gen_isa_mem_read`); ids isa_rd / isa_mem.
- The forced red of Section 3/4 listed four ids; six fired (isa_trap and isa_mem were omitted). The T-068
  forced red below lists all of them.
- The draft-B path took its operands (`rs1_rdata`, `rs2_rdata`) and the next pc from the DUT record. It now
  takes pc, the fetched instruction and the operands from the MODEL (`gen_isa_get_pc`, `gen_isa_fetch_insn`,
  `gen_isa_read_gpr` at the indices decoded from the instruction), compares `pc_rdata`, `insn`, the operands,
  `rd` and `pc_wdata` (= model pc + 4) and writes the reference result and pc + 4 into the model. Both retained
  programs have `draft_b=0`, so this path is implemented but UNEXERCISED; its first exercise is owed with a
  directed grevi/gorci program. The model's minstret does not advance on a draft-B op (known limitation until
  the counter model lands).
- `32'h305` and `2'b11` are gone (`ibex_pkg::CSR_MTVEC`; the privilege compare uses the RISC-V encoding on both
  sides).

### 5.1 Green runs of the committed comparator (build `gen_compile_t068.log`, vcs exit 0)

```
lockstep_zc (gen_lockstep_zc_t068_*; run header 2026-09-03T09:11:00Z, seed 1):
UVM_INFO ... [GEN_RVFI_MON] records=169 irq_markers=0
UVM_INFO ... [GEN_SB] ISA compare: records=148 mismatches=0 folded=21 draft_b=0 traps=0 irq_entries=0 dbg_entries=0 rvfi_rmask_on_nonload=126
GEN_UT_LOCKSTEP retired 169 consumed 169 mismatches 0 tohost 0x00000001
GEN_UT_LOCKSTEP_PASS | UVM_ERROR : 0 | TESTS=1 PASS=1 FAIL=0 | verdict: PASS

lockstep_s7 (gen_lockstep_s7_t068_*; 2026-09-03T09:11:08Z, riscv-dv seed-7 program, 29375 words):
UVM_INFO ... [GEN_RVFI_MON] records=2002 irq_markers=0
UVM_INFO ... [GEN_SB] ISA compare: records=2002 mismatches=0 folded=0 draft_b=0 traps=1 irq_entries=0 dbg_entries=0 rvfi_rmask_on_nonload=1453
GEN_UT_LOCKSTEP retired 2002 consumed 2002 mismatches 0 tohost 0x00000001
GEN_UT_LOCKSTEP_PASS | UVM_ERROR : 0 | TESTS=1 PASS=1 FAIL=0 | verdict: PASS
```
148 compared + 21 folded = 169 = every retirement of the Zc program; the union compare ran on its 10 cm.*
sequences with 0 mismatches (MUT-005 below shows the store part of that compare firing). The s7 program
retires 2002 records by the time the test samples (four settle cycles after the retirement threshold and the
tohost store), all consumed.

### 5.2 Forced red (model without Zc/Zb) with the flow's verdict

```
lockstep_forced_red (gen_lockstep_forced_red_t068_*; +gen_isa_string=rv32imc_zicsr_zifencei):
GEN_UT_LOCKSTEP retired 169 consumed 169 mismatches 676 tohost 0x00000001
AssertionError: GEN_UT_LOCKSTEP: 676 ISA mismatches | TESTS=1 PASS=0 FAIL=1
verdict: FAIL | reason: uvm_error at log line 31
ids: isa_insn 135, isa_mem 11, isa_pc 135, isa_pc_next 136, isa_rd 123, isa_trap 136 (isa_prv: never)
```
This run proves the collected path and the model dependence, not per-field discrimination; that evidence is
Section 5.3. `gen_ut_lockstep` is registered in Runtime's testlist (commit 280b4e9); `gen_ut_lockstep_forced_red` landed
there with `red_fixture: true` (its FAIL is recorded as RED-OK, kept out of the pass rate and coverage; Runtime's
check-tier proof `dv/auto_dv/work/runtime/out/t_red_fixture_check_0925/manifest.yaml`, reason `uvm_error at log line 31`).

### 5.3 Per-field discrimination and ablation (MUT-004..MUT-007)

`dv/auto_dv/mutations/gen_mut_isa_fields.md`: one monitor-side mutation per field, each run three ways on the
Zc program (isolated with every other check off, default, ablation with the field knob off). isa_rd 124 errors
(only that id) and 0 with `+gen_chk_isa_rd=0`; isa_mem 8 / 0 (`Zcmp store 0: model 8000039c<=44444444 (4
bytes) dut 8000039c<=44444445` is the union compare firing); isa_trap 148 / 0; isa_pc_next 148 / 0. Every
default run shows no other id, every ablation run has verdict PASS. Logs `gen_tdd_logs/mutations/mut00[4-7]_*`.
isa_pc and isa_insn fire in the forced red; isa_prv has never fired (no privilege change in either program).
