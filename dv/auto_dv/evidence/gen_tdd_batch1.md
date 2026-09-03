# TDD transcript: Phase 1 batch 1 (eight directed self-checking tests)

Test Writer, 2026-09-03. Tests, program generators and manifests landed as cb3d7eb. Every run below was
made by the batch-1 subagent of that group through `dv/auto_dv/gen_tb/gen_tb_local.sh run` against the local
gen_tb build `dv/auto_dv/work/test-writer/out_head` (working tree at 07d5b3a plus TB Infra's T-068 edits,
compiled 08:40 UTC); the Test Writer re-read every log named here before writing this file (10:53 UTC).
Ordering statement: for each test the red program is `plan(seed, red=True)` of the same generator, so the
red fixture deviates from the plan by construction and its verdict does not depend on run order; red and
green runs of one test were made in the same harness invocation (same minute in the table). Acceptance
through Runtime (3 seeds, purpose 1) is requested separately; the four comparator-blocked tests wait for T-102.

## 1. Summary table (local harness, seed = program seed = simulator seed)

| Test | Run | Time UTC | Seed | Image crc32 | Marker line (stdout.log) | UVM_ERROR | Harness verdict and reason |
|---|---|---|---|---|---|---|---|
| gen_test_rst_boot | red1 | 10:26 | 1 | 714621e8 | 109: GEN_TEST_FAIL (fire-check) | n/a (sim ended at the Python assert) | FAIL: uvm_error at sim.log:30 |
| gen_test_rst_boot | s1 | 10:26 | 1 | 0d22037e | 110: GEN_TEST_PASS | 8 | FAIL: uvm_error at sim.log:30 |
| gen_test_rst_boot | s2 | 10:26 | 2 | cdf7aae9 | 110: GEN_TEST_PASS | 8 | FAIL: uvm_error at sim.log:30 |
| gen_test_csr_reset | red1 | 10:31 | 1 | 1bdf5179 | 195: GEN_TEST_FAIL (fire-check) | n/a (sim ended at the Python assert) | FAIL: uvm_error at sim.log:29 |
| gen_test_csr_reset | s1 | 10:31 | 1 | ddd2890e | 196: GEN_TEST_PASS | 42 | FAIL: uvm_error at sim.log:29 |
| gen_test_csr_reset | s2 | 10:31 | 2 | f7797d6b | 196: GEN_TEST_PASS | 42 | FAIL: uvm_error at sim.log:29 |
| gen_test_csr_access | red1 | 10:41 | 1 | 56a3e90c | 990: GEN_TEST_FAIL (fire-check) | n/a (sim ended at the Python assert) | FAIL: gen_fail_marker at stdout.log:990 |
| gen_test_csr_access | s1 | 10:40 | 1 | ac324d96 | 991: GEN_TEST_PASS | 0 | PASS: no collected failure mechanism; end marker and config banner present |
| gen_test_csr_access | s2 | 10:40 | 2 | 7aed62fc | 991: GEN_TEST_PASS | 0 | PASS: no collected failure mechanism; end marker and config banner present |
| gen_test_csr_trap_setup | red1 | 10:32 | 1 | c03ef73f | 1251: GEN_TEST_FAIL (fire-check) | n/a (sim ended at the Python assert) | FAIL: uvm_error at sim.log:30 |
| gen_test_csr_trap_setup | s1 | 10:32 | 1 | c36050a7 | 1252: GEN_TEST_PASS | 407 | FAIL: uvm_error at sim.log:30 |
| gen_test_csr_trap_setup | s2 | 10:32 | 2 | cd0c166b | 1318: GEN_TEST_PASS | 477 | FAIL: uvm_error at sim.log:30 |
| gen_test_cmp_zcb | red1 | 10:18 | 1 | 6883d708 | 182: GEN_TEST_FAIL (fire-check) | n/a (sim ended at the Python assert) | FAIL: gen_fail_marker at stdout.log:182 |
| gen_test_cmp_zcb | s1 | 10:18 | 1 | 3ca3fb56 | 183: GEN_TEST_PASS | 0 | FAIL: end-of-test marker 'GEN_TEST_CMP_ZCB_PASS' not found |
| gen_test_cmp_zcb | s2 | 10:18 | 2 | a9ae41ef | 203: GEN_TEST_PASS | 0 | FAIL: end-of-test marker 'GEN_TEST_CMP_ZCB_PASS' not found |
| gen_test_cmp_zcmp_basic | red1 | 10:32 | 1 | 44313c36 | 2641: GEN_TEST_FAIL (fire-check) | n/a (sim ended at the Python assert) | FAIL: gen_fail_marker at stdout.log:2641 |
| gen_test_cmp_zcmp_basic | s1 | 10:32 | 1 | 4119149f | 2642: GEN_TEST_PASS | 0 | PASS: no collected failure mechanism; end marker and config banner present |
| gen_test_cmp_zcmp_basic | s2 | 10:32 | 2 | bd5e521f | 2646: GEN_TEST_PASS | 0 | PASS: no collected failure mechanism; end marker and config banner present |
| gen_test_bit_draft | red1 | 10:17 | 1 | 539d1b44 | 107: GEN_TEST_FAIL (fire-check) | n/a (sim ended at the Python assert) | FAIL: gen_fail_marker at stdout.log:107 |
| gen_test_bit_draft | s1 | 10:17 | 1 | b0c98906 | 108: GEN_TEST_PASS | 0 | FAIL: end-of-test marker 'GEN_TEST_BIT_DRAFT_PASS' not found |
| gen_test_bit_draft | s2 | 10:17 | 2 | de1aef4b | 113: GEN_TEST_PASS | 0 | FAIL: end-of-test marker 'GEN_TEST_BIT_DRAFT_PASS' not found |
| gen_test_pmp_csr_warl | red1 | 10:49 | 1 | 77992a1f | 1383: GEN_TEST_FAIL (fire-check) | n/a (sim ended at the Python assert) | FAIL: uvm_error at sim.log:30 |
| gen_test_pmp_csr_warl | s1 | 10:48 | 1 | 99ad8745 | 1384: GEN_TEST_PASS | 532 | FAIL: uvm_error at sim.log:30 |
| gen_test_pmp_csr_warl | s2 | 10:48 | 2 | ade3339e | 1406: GEN_TEST_PASS | 556 | FAIL: uvm_error at sim.log:30 |

Reading the table:
- Every green run (s1, s2) ends in the module's own `<name> GEN_TEST_PASS` line and cocotb reports 1 passed / 0 failed;
  every red run ends in the Python `AssertionError: GEN_TEST_FAIL <name>: N fire-check failure(s)` line and cocotb
  reports 0 passed / 1 failed. Image checksums differ between seeds and between red and green: the programs are
  per-seed generator output, not one static walk.
- Harness verdict `end-of-test marker 'GEN_TEST_<MODULE>_PASS' not found` (gen_cmp_zcb, gen_bit_draft greens) is the
  local harness deriving its marker from the module name; the flow uses the testlist `pass_marker: GEN_TEST_PASS`.
- Harness verdict `uvm_error at sim.log:NN` (gen_rst_boot, gen_csr_reset, gen_csr_trap_setup, gen_pmp_csr_warl, all
  three runs each) is the lock-step ISA comparator (uvm_test_top.env.sb rows isa_rd, isa_mem, isa_pc_next, isa_prv)
  disagreeing with the DUT on conventions the RTL and the plan define differently (mret pc_wdata = pc + 4 per C-1,
  isa_prv against the executing privilege, shim CSR legalization); assigned to TB Infra as T-102 (LOG-018). For these
  four the first collected evidence line is the comparator's, so their red fixtures cannot reach RED-OK and their
  greens cannot reach PASS in the flow until T-102 lands. The DUT matched every program-level expectation in all 24 runs.
- gen_pmp_csr_warl isolation: with `+gen_chk_isa_pc_next=0 +gen_chk_isa_prv=0` the s1 run has UVM_ERROR 0 and the red
  fixture's first evidence line is the fire-check (dirs pmp_csr_warl_s1_norows, pmp_csr_warl_red1_norows).

## 2. Per test: items, red fixture, first failing line

### gen_test_rst_boot
- Files: dv/auto_dv/tests/gen_test_rst_boot.py, dv/auto_dv/tests/gen_programs/gen_rst_boot_prog.py,
  dv/auto_dv/fcov_expectations/gen_test_rst_boot.fcov.yaml (unwired); notes dv/auto_dv/work/test-writer/batch1/rst_boot/.
- Items built: TP-RST-003, TP-RST-006, TP-RST-007. Not built: TP-SEC-031, TP-RST-001/002/004/005/008/027, TP-RVFI-036 (pin, bus and RVFI channels: asks 4 and 5).
- Red fixture (`--red`): the program stores the mstatus reset read-back with MPIE toggled (fire_tp_rst_006); expectation unchanged.
- Red first failing line, out_head/rst_boot_red1/stdout.log:109:

      AssertionError: GEN_TEST_FAIL gen_test_rst_boot: 1 fire-check failure(s): fire_tp_rst_006: 6/7 report words match: mstatus=0x00000000 (expected 0x00000080) [reports 1..37: mstatus=0x00000000 (expected 0x00000080) mie=0x00000000 trap_mcause=0x00000002 trap_mstatus=0x00000080 trap_mepc=0x80000294 pad_result=0xe2e0b258 unexpected_traps=0x00000000]

- Green seed 1: out_head/rst_boot_s1/stdout.log:110: `cocotb.gen_tb_top                  gen_test_rst_boot GEN_TEST_PASS`; UVM_ERROR 8.
- Green seed 2: out_head/rst_boot_s2/stdout.log:110: `cocotb.gen_tb_top                  gen_test_rst_boot GEN_TEST_PASS`; UVM_ERROR 8.
- red_expect `GEN_TEST_FAIL gen_test_rst_boot: [0-9]+ fire-check failure` against the harness's first evidence line: NO MATCH (first evidence line is the comparator UVM_ERROR; RED-OK waits for T-102).

### gen_test_csr_reset
- Files: dv/auto_dv/tests/gen_test_csr_reset.py, dv/auto_dv/tests/gen_programs/gen_csr_reset_prog.py,
  dv/auto_dv/fcov_expectations/gen_test_csr_reset.fcov.yaml (unwired); notes dv/auto_dv/work/test-writer/batch1/csr_reset/.
- Items built: TP-CSR-037, TP-CSR-105..109 (all 6). Not built: none.
- Red fixture (`--red`): the program writes mscratch before its reset value is read (fire_tp_csr_106); expectation unchanged.
- Red first failing line, out_head/csr_reset_red1/stdout.log:195:

      AssertionError: GEN_TEST_FAIL gen_test_csr_reset: 1 fire-check failure(s): fire_tp_csr_106: 4/5 read-backs in bounds, 0/0 relations hold; mscratch got 0x409d4000 expected 0x00000000

- Green seed 1: out_head/csr_reset_s1/stdout.log:196: `cocotb.gen_tb_top                  gen_test_csr_reset GEN_TEST_PASS`; UVM_ERROR 42.
- Green seed 2: out_head/csr_reset_s2/stdout.log:196: `cocotb.gen_tb_top                  gen_test_csr_reset GEN_TEST_PASS`; UVM_ERROR 42.
- red_expect `GEN_TEST_FAIL gen_test_csr_reset: [0-9]+ fire-check failure` against the harness's first evidence line: NO MATCH (first evidence line is the comparator UVM_ERROR; RED-OK waits for T-102).
- T-249 (2026-09-03, joint landing with the DV Lead under LOG-036b, committed 9596727): the CG-CSR-011, CG-CSR-016 and CG-CSR-009 Sample lines' anti-vacuity
  clause now states the sampler's own observation and attributes the prediction comparison to the comparator's isa_rd row until
  gen_chk_csr_readback is built, so gen_test_csr_reset's manifest was re-rendered by --test-module on an archive of 1bf0295 with the new plan:
  68 declared bins unchanged, 60 anti_vacuity strings carry the new clause, header and every other line unchanged; nothing in
  the test or its program changed.

### gen_test_csr_access
- Files: dv/auto_dv/tests/gen_test_csr_access.py, dv/auto_dv/tests/gen_programs/gen_csr_access_prog.py,
  dv/auto_dv/fcov_expectations/gen_test_csr_access.fcov.yaml (unwired); notes dv/auto_dv/work/test-writer/batch1/csr_access/.
- Items built: TP-CSR-001..004, TP-CSR-012. Not built: TP-CSR-005 (parked on the comparator's mret isa_pc_next row, T-102).
- Red fixture (`--red`): the first TP-CSR-001 sequence is forced to csrrw with one writable operand bit flipped (fire_tp_csr_001); expectation unchanged.
- Red first failing line, out_head/csr_access_red1/stdout.log:990:

      AssertionError: GEN_TEST_FAIL gen_test_csr_access: 1 fire-check failure(s): fire_tp_csr_001: 400/401 report words as planned over 200 RMW sequences (rd = pre-op value, read-back = legalised op result, trap count 0); first mismatch [202] seq0 mcountinhibit read-back after csrrc: expected 0x00000560, got 0x00001a99

- Green seed 1: out_head/csr_access_s1/stdout.log:991: `cocotb.gen_tb_top                  gen_test_csr_access GEN_TEST_PASS`; UVM_ERROR 0.
- Green seed 2: out_head/csr_access_s2/stdout.log:991: `cocotb.gen_tb_top                  gen_test_csr_access GEN_TEST_PASS`; UVM_ERROR 0.
- red_expect `GEN_TEST_FAIL gen_test_csr_access: [0-9]+ fire-check failure` against the harness's first evidence line: MATCH.
- L5R-3 (2026-09-03, joint landing with the DV Lead under LOG-036b, committed 812ed54): the CG-CSR-002 Sample line's anti-vacuity
  clause now claims only that a hit proves a read-back record exists for the write pattern and attributes the legalised-prediction
  comparison to the comparator's isa_rd row until gen_chk_csr_readback is built, so this test's manifest was re-rendered by
  --test-module on an archive of 5c0b0c0 with the new plan: 80 declared bins unchanged, the four CG-CSR-002 anti_vacuity
  strings carry the new clause, header and every other line unchanged; nothing in the test or its program changed.
- T-249 (2026-09-03, joint landing with the DV Lead under LOG-036b, committed 9596727): the CG-CSR-003 Sample line's anti-vacuity
  clause now states the sampler's own observation and attributes the prediction comparison to the comparator's isa_rd row until
  gen_chk_csr_readback is built, so gen_test_csr_access's manifest was re-rendered by --test-module on an archive of 1bf0295 with the new plan:
  80 declared bins unchanged, 20 anti_vacuity strings carry the new clause, header and every other line unchanged; nothing in
  the test or its program changed.

### gen_test_csr_trap_setup
- Files: dv/auto_dv/tests/gen_test_csr_trap_setup.py, dv/auto_dv/tests/gen_programs/gen_csr_trap_setup_prog.py,
  dv/auto_dv/fcov_expectations/gen_test_csr_trap_setup.fcov.yaml (unwired); notes dv/auto_dv/work/test-writer/batch1/csr_trap_setup/.
- Items built: TP-CSR-023/024/025/027/028/029/030/035/036. Not built: TP-CSR-026, TP-CSR-031 (irq agent, step 2b).
- Red fixture (`--red`): one TP-CSR-036 mtvec operand is written with bit 8 flipped (fire_tp_csr_036); expectation unchanged.
- Red first failing line, out_head/csr_trap_setup_red1/stdout.log:1251:

      AssertionError: GEN_TEST_FAIL gen_test_csr_trap_setup: 1 fire-check failure(s): fire_tp_csr_036: 41 mtvec read-backs vs (w & 0xFFFFFF00) | 1 for MODE 00/01/10/11 x bits 7:2 zero/nonzero and the clear attempts: 1 mismatch(es); first [342] pair 0 csrrw mtvec operand 0x00000000: expected 0x00000001 got 0x00000101

- Green seed 1: out_head/csr_trap_setup_s1/stdout.log:1252: `cocotb.gen_tb_top                  gen_test_csr_trap_setup GEN_TEST_PASS`; UVM_ERROR 407.
- Green seed 2: out_head/csr_trap_setup_s2/stdout.log:1318: `cocotb.gen_tb_top                  gen_test_csr_trap_setup GEN_TEST_PASS`; UVM_ERROR 477.
- red_expect `GEN_TEST_FAIL gen_test_csr_trap_setup: [0-9]+ fire-check failure` against the harness's first evidence line: NO MATCH (first evidence line is the comparator UVM_ERROR; RED-OK waits for T-102).
- L5R-3 (2026-09-03, joint landing with the DV Lead under LOG-036b, committed 812ed54): the CG-CSR-002 Sample line's anti-vacuity
  clause now claims only that a hit proves a read-back record exists for the write pattern and attributes the legalised-prediction
  comparison to the comparator's isa_rd row until gen_chk_csr_readback is built, so this test's manifest was re-rendered by
  --test-module on an archive of 5c0b0c0 with the new plan: 168 declared bins unchanged, the 151 CG-CSR-002 anti_vacuity
  strings carry the new clause, header and every other line unchanged; nothing in the test or its program changed.
- T-249 (2026-09-03, joint landing with the DV Lead under LOG-036b, committed 9596727): the CG-CSR-016 Sample line's anti-vacuity
  clause now states the sampler's own observation and attributes the prediction comparison to the comparator's isa_rd row until
  gen_chk_csr_readback is built, so gen_test_csr_trap_setup's manifest was re-rendered by --test-module on an archive of 1bf0295 with the new plan:
  168 declared bins unchanged, 3 anti_vacuity strings carry the new clause, header and every other line unchanged; nothing in
  the test or its program changed.

### gen_test_cmp_zcb
- Files: dv/auto_dv/tests/gen_test_cmp_zcb.py, dv/auto_dv/tests/gen_programs/gen_cmp_zcb_prog.py,
  dv/auto_dv/fcov_expectations/gen_test_cmp_zcb.fcov.yaml (unwired); notes dv/auto_dv/work/test-writer/batch1/cmp_zcb/.
- Items built: TP-CMP-034, TP-CMP-036, TP-CMP-038 (all 3). Not built: none.
- Red fixture (`--red`): one Zcb ALU form is emitted as a different form (fire_tp_cmp_036); expectation unchanged.
- Red first failing line, out_head/cmp_zcb_red1/stdout.log:182:

      AssertionError: GEN_TEST_FAIL gen_test_cmp_zcb: 1 fire-check failure(s): fire_tp_cmp_036: 32 report words (c_zext_b 6 c_sext_b 6 c_zext_h 7 c_sext_h 6 c_not 7, operand mix): 1 mismatch(es), first idx=0 c_not x11 operand=0x2ac9e8f7 expected 0xd5361708 got 0xffffe8f7

- Green seed 1: out_head/cmp_zcb_s1/stdout.log:183: `cocotb.gen_tb_top                  gen_test_cmp_zcb GEN_TEST_PASS`; UVM_ERROR 0.
- Green seed 2: out_head/cmp_zcb_s2/stdout.log:203: `cocotb.gen_tb_top                  gen_test_cmp_zcb GEN_TEST_PASS`; UVM_ERROR 0.
- red_expect `GEN_TEST_FAIL gen_test_cmp_zcb: [0-9]+ fire-check failure` against the harness's first evidence line: MATCH.

### gen_test_cmp_zcmp_basic
- Files: dv/auto_dv/tests/gen_test_cmp_zcmp_basic.py, dv/auto_dv/tests/gen_programs/gen_cmp_zcmp_basic_prog.py,
  dv/auto_dv/fcov_expectations/gen_test_cmp_zcmp_basic.fcov.yaml (unwired); notes dv/auto_dv/work/test-writer/batch1/cmp_zcmp_basic/.
- Items built: TP-CMP-039..043, 045..050, 052, 053, 055, 066, 069, 073 (17). Not built: TP-CMP-068 (writable low addresses and bus records).
- Red fixture (`--red`): one plain cm.push is emitted with the other spimm bit, sp_new off by 16 (fire_tp_cmp_039 and the two checks reading that frame); expectation unchanged.
- Red first failing line, out_head/cmp_zcmp_basic_red1/stdout.log:2641:

      AssertionError: GEN_TEST_FAIL gen_test_cmp_zcmp_basic: 3 fire-check failure(s): fire_tp_cmp_039: 51 scenarios, 826 report words checked, 1 mismatches; cm.push over 48/48 (rlist, spimm); expected frame words == the predicted registers, poison slots untouched, sp_new == sp_old - stack_adj; first: report 1024 (push#98 rlist=12 spimm=1 plain sp_new): expected 0x8000c070 got 0x8000c080 | fire_tp_cmp_04

- Green seed 1: out_head/cmp_zcmp_basic_s1/stdout.log:2642: `cocotb.gen_tb_top                  gen_test_cmp_zcmp_basic GEN_TEST_PASS`; UVM_ERROR 0.
- Green seed 2: out_head/cmp_zcmp_basic_s2/stdout.log:2646: `cocotb.gen_tb_top                  gen_test_cmp_zcmp_basic GEN_TEST_PASS`; UVM_ERROR 0.
- red_expect `GEN_TEST_FAIL gen_test_cmp_zcmp_basic: [0-9]+ fire-check failure` against the harness's first evidence line: MATCH.
- B4-R1 (2026-09-03, joint landing with the DV Lead under LOG-036b): the bin gen_cmp_zcmp_mv_cg.cr_insn_equal.cm_mvsa01_yes left this
  test's manifest (473 -> 472 declared, re-rendered by --test-module on an archive of a9b63ae with the TP-CMP-053 row removed from the
  trace CSV, header and anti_vacuity lines otherwise unchanged): Ibex executes the reserved cm.mvsa01 encoding with equal sources while
  the ISA model traps it (gen_bug_log.md B4), so the bin cannot be proven under the comparator and stays TP-CMP-051's expected-fail
  witness; nothing in the test or its program changes.

### gen_test_bit_draft
- Files: dv/auto_dv/tests/gen_test_bit_draft.py, dv/auto_dv/tests/gen_programs/gen_bit_draft_prog.py,
  dv/auto_dv/fcov_expectations/gen_test_bit_draft.fcov.yaml (unwired); notes dv/auto_dv/work/test-writer/batch1/bit_draft/.
- Items built: TP-BIT-016 (grev/gorc family plus rev8/orc.b/brev8). Not built: TP-BIT-011, TP-BIT-022..033 (shim C5.5 references beyond grev/gorc, T-102 item 4).
- Red fixture (`--red`): one grevi/gorci immediate deviates (fire_tp_bit_016_gorci); expectation unchanged.
- Red first failing line, out_head/bit_draft_red1/stdout.log:107:

      AssertionError: GEN_TEST_FAIL gen_test_bit_draft: 1 fire-check failure(s): fire_tp_bit_016_gorci: 9 ops, 1 mismatches; first op 0 gorci ctrl=28 rs1=0xf227fe72 expected 0xffffffff got 0xf227fe72

- Green seed 1: out_head/bit_draft_s1/stdout.log:108: `cocotb.gen_tb_top                  gen_test_bit_draft GEN_TEST_PASS`; UVM_ERROR 0.
- Green seed 2: out_head/bit_draft_s2/stdout.log:113: `cocotb.gen_tb_top                  gen_test_bit_draft GEN_TEST_PASS`; UVM_ERROR 0.
- red_expect `GEN_TEST_FAIL gen_test_bit_draft: [0-9]+ fire-check failure` against the harness's first evidence line: MATCH.

### gen_test_pmp_csr_warl
- Files: dv/auto_dv/tests/gen_test_pmp_csr_warl.py, dv/auto_dv/tests/gen_programs/gen_pmp_csr_warl_prog.py,
  dv/auto_dv/fcov_expectations/gen_test_pmp_csr_warl.fcov.yaml (unwired); notes dv/auto_dv/work/test-writer/batch1/pmp_csr_warl/.
- Items built: TP-PMP-001..008 (all 8). Not built: none.
- Red fixture (`--red`): one TP-PMP-001 pmpcfg byte is written with a flipped A field (fire_tp_pmp_001); expectation unchanged.
- Red first failing line, out_head/pmp_csr_warl_red1/stdout.log:1383:

      AssertionError: GEN_TEST_FAIL gen_test_pmp_csr_warl: 1 fire-check failure(s): fire_tp_pmp_001: 124 words compared, 1 mismatches (first: idx 132 [w2 readback pmpcfg3] expected 0x191f0908 got 0x191f0900); pmpcfg CSRs written [0, 1, 2, 3]; byte lanes with a non-zero A read back [0, 1, 2, 3]; 83 csrrw/csrr pairs

- Green seed 1: out_head/pmp_csr_warl_s1/stdout.log:1384: `cocotb.gen_tb_top                  gen_test_pmp_csr_warl GEN_TEST_PASS`; UVM_ERROR 532.
- Green seed 2: out_head/pmp_csr_warl_s2/stdout.log:1406: `cocotb.gen_tb_top                  gen_test_pmp_csr_warl GEN_TEST_PASS`; UVM_ERROR 556.
- red_expect `GEN_TEST_FAIL gen_test_pmp_csr_warl: [0-9]+ fire-check failure` against the harness's first evidence line: NO MATCH (first evidence line is the comparator UVM_ERROR; RED-OK waits for T-102).
- T-249 (2026-09-03, joint landing with the DV Lead under LOG-036b, committed 9596727): the CG-PMP-001 Sample line's anti-vacuity
  clause now states the sampler's own observation and attributes the prediction comparison to the comparator's isa_rd row until
  gen_chk_csr_readback is built, so gen_test_pmp_csr_warl's manifest was re-rendered by --test-module on an archive of 1bf0295 with the new plan:
  266 declared bins unchanged, 117 anti_vacuity strings carry the new clause, header and every other line unchanged; nothing in
  the test or its program changed.

## 3. Manifests

Rendered from the committed plan by `python3 dv/auto_dv/tests/gen_fcov_manifest.py --group gen_<g> --test gen_test_<g> --write`
(0 dropped bins each) and validated: `python3 dv/auto_dv/flow/gen_fcov.py --validate dv/auto_dv/fcov_expectations/gen_test_*.fcov.yaml`
prints OK for all eight (10:54 UTC, after the anti-vacuity note quoting fix in render()). Bins: rst_boot 42, csr_reset 81,
csr_access 83, csr_trap_setup 206, cmp_zcb 110, cmp_zcmp_basic 479, bit_draft 480, pmp_csr_warl 266. Entries keep
`fcov_expectation_file: null` until the first covergroup exists (the manifests are expectations, not measurements).

## 4. Reproduction

    bash -lc 'source ci/env.sh && python3 dv/auto_dv/tests/gen_programs/gen_<g>_prog.py --seed 1 --out /path/red.S --red'
    bash -lc 'source ci/env.sh && python3 dv/auto_dv/stim/gen_program.py --directed /path/red.S --seed 1 --out /path/prog --gcc-opts=-Idv/auto_dv/tests/gen_programs'
    then gen_tb_local.sh run with module dv.auto_dv.tests.gen_test_<g>, seed 1, the image plusargs from prog/, and +gen_fetch_en_at_reset=0

Through the flow: testlist entries gen_test_<g> (seeds 3) and gen_test_<g>_red (`red_fixture: true`, `red_expect`) in
dv/auto_dv/work/test-writer/gen_testlist_entries.yaml use `program.generator` (Runtime API Section 7e).

## 5. Limitations

- Two seeds locally; the third seed and the flow verdict come from Runtime's acceptance runs (requests test-writer-009/011/012/013 and reds 017/019/020/021 filed 11:02 UTC; the comparator-blocked eight staged under work/test-writer/batch1/requests_staged/).
- `layers_required = False` on every batch-1 test (no REGIME_SET consumer at HEAD): layers 2 and 3 are drawn and logged, not applied; entries are `tier: check, measured: false` until step 2b re-lands.
- Mutation evidence per checker id (plan Section 5) is not part of this transcript; it needs Runtime's `--rtl-root` mutation copies and comes with the mutation batch.
- No subagent reported a fence event; the Test Writer re-verified compile, the AST structure check, ASCII and the log lines, not every expectation derivation.

## 6. Acceptance wave 1 (Runtime, head mode at d58bdeb, 11:05-11:06 UTC) and the declare_bins defect

Requests test-writer-009/011/012/013 (greens, 3 seeds) and 017/019/020/021 (red fixtures) were served together.
Manifests: dv/auto_dv/work/runtime/results/test-writer-<seq>/manifest.yaml (run trees under
/proj_soc/user_dev/fzhang/ibex_dv_out/regress_req_test-writer-<seq>/). None reached PASS or RED-OK:

| Request | Test | Seed | Verdict | Reason (manifest) | Whose |
|---|---|---|---|---|---|
| test-writer-009 | gen_test_csr_access | 86614566 | NOT_RUN | build gen_tb failed | Runtime flow (head-mode stage race / HEAD moved between waves) |
| test-writer-009 | gen_test_csr_access | 945071090 | NOT_RUN | build gen_tb failed | Runtime flow (head-mode stage race / HEAD moved between waves) |
| test-writer-009 | gen_test_csr_access | 1610721211 | NOT_RUN | build gen_tb failed | Runtime flow (head-mode stage race / HEAD moved between waves) |
| test-writer-011 | gen_test_cmp_zcb | 198464629 | FAIL | cocotb_summary at sim_stdout.log:201 | Test Writer (declare_bins) |
| test-writer-011 | gen_test_cmp_zcb | 1669651236 | FAIL | cocotb_summary at sim_stdout.log:207 | Test Writer (declare_bins) |
| test-writer-011 | gen_test_cmp_zcb | 2083413616 | FAIL | cocotb_summary at sim_stdout.log:197 | Test Writer (declare_bins) |
| test-writer-012 | gen_test_cmp_zcmp_basic | 14603651 | NOT_RUN | build gen_tb failed | Runtime flow (head-mode stage race / HEAD moved between waves) |
| test-writer-012 | gen_test_cmp_zcmp_basic | 708897507 | NOT_RUN | build gen_tb failed | Runtime flow (head-mode stage race / HEAD moved between waves) |
| test-writer-012 | gen_test_cmp_zcmp_basic | 883583994 | NOT_RUN | build gen_tb failed | Runtime flow (head-mode stage race / HEAD moved between waves) |
| test-writer-013 | gen_test_bit_draft | 513633256 | FAIL | cocotb_summary at sim_stdout.log:117 | Test Writer (declare_bins) |
| test-writer-013 | gen_test_bit_draft | 762156845 | FAIL | cocotb_summary at sim_stdout.log:119 | Test Writer (declare_bins) |
| test-writer-013 | gen_test_bit_draft | 912937852 | FAIL | cocotb_summary at sim_stdout.log:122 | Test Writer (declare_bins) |
| test-writer-017 | gen_test_csr_access_red | 1 | NOT_RUN | build gen_tb failed | Runtime flow (head-mode stage race / HEAD moved between waves) |
| test-writer-019 | gen_test_cmp_zcb_red | 1 | NOT_RUN | build gen_tb failed | Runtime flow (head-mode stage race / HEAD moved between waves) |
| test-writer-020 | gen_test_cmp_zcmp_basic_red | - | no run | regress_rc 1: mirror is not a head-mode mirror of HEAD 6b3301d (manifest head d58bdeb) | Runtime flow (head-mode stage race / HEAD moved between waves) |
| test-writer-021 | gen_test_bit_draft_red | - | no run | regress_rc 1: mirror is not a head-mode mirror of HEAD 6b3301d (manifest head d58bdeb) | Runtime flow (head-mode stage race / HEAD moved between waves) |

- Runtime's two: `build gen_tb failed` is gen_mirror.py tree_hash raising FileNotFoundError on
  head_stage_status/dv/auto_dv/excl/gen_excl_select.py while another wave rewrote the shared stage (regress.log);
  the two red requests were refused before any run because HEAD moved to 6b3301d between waves (serve.log).
  Reported to Runtime 11:09 UTC; not a property of the tests.
- Mine: gen_test_cmp_zcb and gen_test_bit_draft fail on every seed with
  `AssertionError: GEN_TEST_LIB: manifest of gen_test_cmp_zcb differs from declare_bins()` (run
  gen_test_cmp_zcb_198464629, sim_stdout.log:195). Cause: every batch-1 test overrode declare_bins() to return [],
  while the committed manifests carry the plan's bins, and finish() compares the two whenever the manifest file
  exists. The Section 1 local runs passed because the manifests were rendered (10:53 UTC) after those runs
  (10:17-10:49 UTC) and no test was re-run afterwards: a verification gap of the Test Writer, recorded here.
  The program.generator path worked in the same runs (result.yaml: generator_command, generator_source_sha256,
  seed_source run).

### 6.1 Fix (this landing)

- gen_test_template.py: `declare_bins()` defaults to `lib.plan_bins(self.name, self.plan_group)`, the plan's bins for
  the test's group (new class attribute `plan_group`, None = gen_<x> for gen_test_<x>), derived by
  gen_fcov_manifest.plan_bins (the generator's own bins_of_items + bin_tokens; one implementation for the file and
  the declaration). finish() therefore proves at every run that the rendered manifest is current against the plan.
- gen_test_lib.check_manifest_matches: a test that declares bins but has no manifest file FAILS (was: silent skip);
  a mismatch names the counts and the first differing tokens each way.
- The nine `declare_bins(): return []` overrides (eight batch-1 tests, gen_test_boot_retire) are removed; their
  docstrings say so. API doc Sections 2, 3 (`plan_group`), 6 and 8 updated.
- Host check (11:10 UTC): lib.plan_bins(name) equals the committed manifest for all eight batch-1 tests
  (42/81/83/206/110/479/480/266 tokens, about 0.15 s each); gen_test_boot_retire declares 0 and has no manifest
  (skip); the two negative calls raise with the new messages. `gen_test_lib.py --self-test` PASS over nine tests;
  `gen_fcov_manifest.py --self-test` PASS (68 bins, 86 excluded coverpoints).

### 6.2 Red and green, local harness (build out_head, seed 1, gen_cmp_zcb / gen_bit_draft seed-1 images)

Red 1 is the flow itself: the FAIL lines above (test-writer-011/-013). Red 2 and 3 are committed fixtures under
dv/auto_dv/tests/gen_fixtures/ (never testlist entries): gen_ut_manifest_missing (gen_cmp_zcb's test under a name
with no manifest) and gen_ut_manifest_stale (its manifest home is the fixture directory, whose
gen_ut_manifest_stale.fcov.yaml is the gen_cmp_zcb manifest minus its last bin).

| Run (out_head/<dir>/stdout.log) | Decisive line (line no.) | cocotb | md5 | bytes |
|---|---|---|---|---|
| declbins_cmp_zcb_s1 | 183: 21240.00ns INFO     cocotb.gen_tb_top                  gen_test_cmp_zcb GEN_TEST_PASS | ** TESTS=1 PASS=1 FAIL=0 SKIP=0 21240.01 0.34 62783.75 ** | bdc42f0a4c77e2aa1edf2a75b0c3dbc3 | 27249 |
| declbins_bit_draft_s1 | 108: 10530.00ns INFO     cocotb.gen_tb_top                  gen_test_bit_draft GEN_TEST_PASS | ** TESTS=1 PASS=1 FAIL=0 SKIP=0 10530.01 0.35 30364.03 ** | 41d2a3dc3b2c809fdf1bcb6e3ff42926 | 35511 |
| declbins_manifest_missing | 185: AssertionError: GEN_TEST_LIB: gen_ut_manifest_missing declares 110 bins but has no manifest fcov_expectations/gen_ut_manifest_missing.fcov.yaml (rende | ** TESTS=1 PASS=0 FAIL=1 SKIP=0 21240.01 0.32 67192.77 ** | c998bc3d28c90748429a4d0648885f0a | 26584 |
| declbins_manifest_stale | 185: AssertionError: GEN_TEST_LIB: manifest of gen_ut_manifest_stale differs from declare_bins(): 109 in the manifest, 110 declared; not in the manifest [' | ** TESTS=1 PASS=0 FAIL=1 SKIP=0 21240.01 0.33 64400.16 ** | 51bb61e3657e672e8387948f07ff00cc | 26561 |

GEN_TEST_BINS lines: cmp_zcb `21240.00ns INFO cocotb.gen_tb_top GEN_TEST_BINS n=110 gen_cm`, bit_draft `10530.00ns INFO cocotb.gen_tb_top GEN_TEST_BINS n=480 gen_bi`.
UVM_ERROR 0 on both greens. The ordering is honest: the flow's red came first (11:06 UTC), the fix and the two fixture
reds and the two greens followed (11:10-11:12 UTC, all in one harness invocation).

Wave 2: the same eight requests are re-filed against the commit that carries this fix (Section 7 when the manifests
arrive).

## 7. Acceptance wave 2 (Runtime, head mode at 38d1262 or later, 11:2x-11:3x UTC)

Requests test-writer-023/024/025/026 (greens, 3 seeds) and 027/028/029/030 (red fixtures), filed 11:21 UTC against the
declare_bins fix. Manifests dv/auto_dv/work/runtime/results/test-writer-<seq>/manifest.yaml.

| Request | Test | Seed | Verdict | Reason | head_sha |
|---|---|---|---|---|---|
| test-writer-023 | gen_test_csr_access | 115015914 | PASS | no collected failure mechanism; end marker and config banner present | 7fa426282957 |
| test-writer-023 | gen_test_csr_access | 134006003 | PASS | no collected failure mechanism; end marker and config banner present | 7fa426282957 |
| test-writer-023 | gen_test_csr_access | 1905524115 | PASS | no collected failure mechanism; end marker and config banner present | 7fa426282957 |
| test-writer-024 | gen_test_cmp_zcb | 866812001 | NOT_RUN | gen_run.py wrote no result.yaml (see driver.log) | 7fa426282957 |
| test-writer-024 | gen_test_cmp_zcb | 1589399401 | PASS | no collected failure mechanism; end marker and config banner present | 7fa426282957 |
| test-writer-024 | gen_test_cmp_zcb | 1803095304 | PASS | no collected failure mechanism; end marker and config banner present | 7fa426282957 |
| test-writer-025 | gen_test_cmp_zcmp_basic | 180641635 | PASS | no collected failure mechanism; end marker and config banner present | 7fa426282957 |
| test-writer-025 | gen_test_cmp_zcmp_basic | 1413406531 | PASS | no collected failure mechanism; end marker and config banner present | 7fa426282957 |
| test-writer-025 | gen_test_cmp_zcmp_basic | 1484830938 | PASS | no collected failure mechanism; end marker and config banner present | 7fa426282957 |
| test-writer-026 | gen_test_bit_draft | 81770765 | PASS | no collected failure mechanism; end marker and config banner present | 7fa426282957 |
| test-writer-026 | gen_test_bit_draft | 1268056028 | PASS | no collected failure mechanism; end marker and config banner present | 7fa426282957 |
| test-writer-026 | gen_test_bit_draft | 1418596552 | PASS | no collected failure mechanism; end marker and config banner present | 7fa426282957 |
| test-writer-027 | gen_test_csr_access_red | 1 | RED-OK | red fixture failed as designed (red_expect matched): gen_fail_marker at sim_stdout.log:992 | 7fa426282957 |
| test-writer-028 | gen_test_cmp_zcb_red | 1 | RED-OK | red fixture failed as designed (red_expect matched): gen_fail_marker at sim_stdout.log:184 | 7fa426282957 |
| test-writer-029 | gen_test_cmp_zcmp_basic_red | 1 | RED-OK | red fixture failed as designed (red_expect matched): gen_fail_marker at sim_stdout.log:2643 | 7fa426282957 |
| test-writer-030 | gen_test_bit_draft_red | 1 | RED-OK | red fixture failed as designed (red_expect matched): gen_fail_marker at sim_stdout.log:109 | 7fa426282957 |

Totals: {'PASS': 11, 'RED-OK': 4, 'NOT_RUN': 1, 'FAIL': 0}. Eleven of twelve green runs PASS with UVM_ERROR 0 and GEN_TEST_BINS equal to the committed manifest; all four red
fixtures RED-OK (red_expect matched on the first collected evidence line). The one NOT_RUN (gen_test_cmp_zcb, seed 866812001) is a
generator defect of the Test Writer's batch, not the flow's: gen_cmp_zcb_prog.py's own must-cover self-check
(`AssertionError: load form x uimm not covered`, program/generator.log) trips for about 5 percent of seeds (a 41-seed host
sweep of all eight generators, 11:40 UTC, found it on 2 of 41 seeds for cmp_zcb and no crash in the other seven). The flow
stopped the run before the simulator as designed (NOT_RUN with the generator log retained). Fix and re-run follow in the
batch-1 remediation round (Critic verdict dv/auto_dv/docs/gen_critic_batch1_v1.md).

## 8. Batch-1 remediation (Critic verdict dv/auto_dv/docs/gen_critic_batch1_v1.md; cross-model review of the batch)

Shared changes by the Test Writer (11:40-12:05 UTC): a test's declared bins are the plan bins of the items its fire_tp_<area>_<nnn>
methods name (lib.fire_items / lib.plan_bins) and gen_fcov_manifest.py --test-module renders the same set, so every manifest now covers
the built items only (M-1: rst_boot 42 -> 9 bins, csr_access 83 -> 80, csr_trap_setup 206 -> 172, cmp_zcmp_basic 479 -> 473, bit_draft
480 -> 15); the `[CYCLE-CLAUSE ...]` marker token keeps a marked item's CG-WIT-001 witness bin out (M-2, rule f; the csr_trap_setup
manifest has no gen_wit bin); one dv/auto_dv/tests/gen_programs/gen_prog_const.py holds CSR addresses, reset values, tohost codes and
the configuration name (L-2); the cmp_zcb generator emits every load form x uimm as its own unit (the wave-2 NOT_RUN crash; 404
generator runs clean); the eight red entries pin one item (`--red --red-item <TP>`) and their red_expect names the fire id (cross-model
Major). Eight per-test remediation subagents (one per test, editing only their two files) implemented M-3 (per-item red:
`--red-item <TP>`, the seed draws the item otherwise, expectations unchanged), M-4 (no observation avoided: the csr_access rd = x0 reads
are gone and the clause is declared blocked on T-102; the pmp LRWX = 1111 refusal is gone and the pattern is programmed, no shim gap
seen), the Section 3 items and L-3; dispositions per finding in dv/auto_dv/evidence/gen_critic_response_batch1.md. The Test Writer
re-verified: py_compile, the lib self-test (structure check over nine tests), ASCII, no hierarchical access, the seed-1 source of every
generator byte-identical to the one its proven runs used, every manifest unchanged by a --test-module re-render, every --red-item id
accepted by its generator, and every run directory below re-read (12:10 UTC).

### 8.1 Greens on the committed template with the per-item manifests present (H-1), seed 1 and 2

| Run (out_head/<dir>) | Result | GEN_TEST_BINS | UVM_ERROR | md5 (stdout.log) |
|---|---|---|---|---|
| rem_rst_boot_s1 | PASS | 9 | 8 | eddc1049d88f3f5af7f1e97e8e196c72 |
| rem_rst_boot_s2 | PASS | 9 | 8 | 345b6f29096c74195d18aaa0f0df5459 |
| rem_csr_reset_s1 | PASS | 81 | 42 | 0a8723edf2c698a97a5a5165fd1a22ea |
| rem_csr_reset_s2 | PASS | 81 | 42 | 5699923cf3458294d98714bba1391f12 |
| rem_csr_access_v2_s1 | PASS | 80 | 0 | c6121064c76e45c7bfec91aa525c5db7 |
| rem_csr_access_v2_s2 | PASS | 80 | 0 | 08a9f10d9b449991fa19b72375e65f1c |
| rem_csr_trap_setup_s1 | PASS | 172 | 408 | af7ca6deed50e0ec6dfd12f28173ff59 |
| rem_csr_trap_setup_s2 | PASS | 172 | 479 | 681fd69b32be12c31be402b43d9640b9 |
| rem_cmp_zcb_v3_s1 | PASS | 110 | 0 | 8feaefbbbf5f23e34667646678eab3a2 |
| rem_cmp_zcb_v3_s2 | PASS | 110 | 0 | a3873381fc3ee8a39296ee8e1d9476bf |
| rem_cmp_zcb_s866812001 | PASS | 110 | 0 | 34b41a4899b536945e07e9875d8a25c1 |
| rem_cmp_zcmp_basic_s1 | PASS | 473 | 0 | 7705757b3efb389d50574445d1cd44aa |
| rem_cmp_zcmp_basic_s2 | PASS | 473 | 0 | b1e49d6c2b7e748f9a7d605785df7f10 |
| rem_bit_draft_s1 | PASS | 15 | 0 | 111db61e89316720766da6450d9152ec |
| rem_bit_draft_s2 | PASS | 15 | 0 | 86b7abbb31e8228959427d512995bba8 |
| rem_pmp_csr_warl_s1 | PASS | 266 | 532 | d334150d4a3b5cfc957b3dfd7451565e |
| rem_pmp_csr_warl_s2 | PASS | 266 | 556 | 6ea366ea5e0f7751bb920e82e4755bf2 |
| rem_pmp_csr_warl_s25 | PASS | 266 | 556 | 90aca50cbdee9ae6a8f6cf74d4867c2d |

UVM_ERROR counts above 0 are the T-102 comparator rows (rst_boot 8, csr_reset 42, csr_trap_setup 408/479, pmp_csr_warl 532/556; first
lines in the retained sim.log copies); the DUT matched every program-level expectation. rem_cmp_zcb_s866812001 is the wave-2 crash seed,
green after the generator fix; rem_pmp_csr_warl_s25 is the seed that draws LRWX = 1111 (0 isa_csr rows: no shim gap on that pattern).

### 8.2 One red per fire_tp item (M-3), seed 1, program deviation only

| Run (out_head/<dir>) | Result (first failing fire-check) | md5 (stdout.log) |
|---|---|---|
| rem_bit_draft_red1 | FAIL 1: fire_tp_bit_016_gorci first | 98222c538a687ae79018094f0d5493f3 |
| rem_bit_draft_red2 | FAIL 2: fire_tp_bit_016_gorci first | 0aeebc27f9ecb4c5dc7223c353b2ce08 |
| rem_cmp_zcb_red_034 | FAIL 1: fire_tp_cmp_034 first | a503671df7a8f7b5319f7aeee93f1f79 |
| rem_cmp_zcb_red_036 | FAIL 1: fire_tp_cmp_036 first | d833ead8adfed9fa531abc75971eae58 |
| rem_cmp_zcb_red_038 | FAIL 1: fire_tp_cmp_038 first | f1317cb75882bd6006463cb37d9d4970 |
| rem_cmp_zcmp_basic_red_039 | FAIL 3: fire_tp_cmp_039 first | a4eaa7a5af46588bbc183dd0b5318cc1 |
| rem_cmp_zcmp_basic_red_040 | FAIL 2: fire_tp_cmp_039 first | 84d89d5610f23e72b749826f36a57e6f |
| rem_cmp_zcmp_basic_red_041 | FAIL 2: fire_tp_cmp_039 first | 2831577938994c2b4e58364f1840114f |
| rem_cmp_zcmp_basic_red_042 | FAIL 2: fire_tp_cmp_039 first | ea592c1fb86b3441bd315efae5ef01b8 |
| rem_cmp_zcmp_basic_red_043 | FAIL 2: fire_tp_cmp_043 first | d7d35617a9b40acf401fe23492e60282 |
| rem_cmp_zcmp_basic_red_045 | FAIL 1: fire_tp_cmp_045 first | bc57f9a1d079a720096ab1612fe07d8e |
| rem_cmp_zcmp_basic_red_046 | FAIL 2: fire_tp_cmp_045 first | bec79187391f8ad390ed6803d1b28a1b |
| rem_cmp_zcmp_basic_red_047 | FAIL 1: fire_tp_cmp_047 first | f46b47e6a44e1f9d8f985fe35b063a3a |
| rem_cmp_zcmp_basic_red_048 | FAIL 1: fire_tp_cmp_048 first | 628e797fc65c19f23fa568c0a033fff0 |
| rem_cmp_zcmp_basic_red_049 | FAIL 2: fire_tp_cmp_047 first | a5e2ef34c075e187670a56065283ca75 |
| rem_cmp_zcmp_basic_red_050 | FAIL 1: fire_tp_cmp_050 first | 328ad1e0079ee1acc89837cac9f1cdc4 |
| rem_cmp_zcmp_basic_red_052 | FAIL 1: fire_tp_cmp_052 first | 15879a4b6ea1f1ab1a586937f7530b46 |
| rem_cmp_zcmp_basic_red_053 | FAIL 1: fire_tp_cmp_053 first | 6b7bbf63bab282d7dd55e89276349d50 |
| rem_cmp_zcmp_basic_red_055 | FAIL 1: fire_tp_cmp_055 first | a297f98f3866e2e11a1591459b98c446 |
| rem_cmp_zcmp_basic_red_066 | FAIL 1: fire_tp_cmp_066 first | e6f4faae011f1880c4b3a866b37efbd8 |
| rem_cmp_zcmp_basic_red_069 | FAIL 2: fire_tp_cmp_052 first | fcc1a231422e4a75b471dea05c45a016 |
| rem_cmp_zcmp_basic_red_073 | FAIL 2: fire_tp_cmp_047 first | 511458f249e44a1bbfb96a6fbd6b10f2 |
| rem_csr_access_v2_red1_001 | FAIL 1: fire_tp_csr_001 first | 2a089ee29ca7f728db793b44df96dfb0 |
| rem_csr_access_v2_red1_002 | FAIL 1: fire_tp_csr_002 first | d7ea3c65798c3aa280db4ba6d90a4181 |
| rem_csr_access_v2_red1_003 | FAIL 1: fire_tp_csr_003 first | 9a10b18095a078d5c76c0a497af61648 |
| rem_csr_access_v2_red1_004 | FAIL 1: fire_tp_csr_004 first | ebc798929a07536bb8ed10b3224962ca |
| rem_csr_access_v2_red1_012 | FAIL 1: fire_tp_csr_012 first | 41001e5623014303dd3cbc24622d0f85 |
| rem_csr_reset_red_037 | FAIL 1: fire_tp_csr_037 first | 25b5b1ebd8c2c69709d96cc5c41969b3 |
| rem_csr_reset_red_105 | FAIL 1: fire_tp_csr_105 first | d8b907ae715cba759f15738de4115cbb |
| rem_csr_reset_red_106 | FAIL 1: fire_tp_csr_106 first | 9edf8f3505c096dabf74096c9aa90c59 |
| rem_csr_reset_red_107 | FAIL 1: fire_tp_csr_107 first | 40968a44d39c95cc47741afb6bf43fcc |
| rem_csr_reset_red_108 | FAIL 1: fire_tp_csr_108 first | 1a5f4768d7d88bfe537fd24abeb19702 |
| rem_csr_reset_red_109 | FAIL 1: fire_tp_csr_109 first | e69f82feb7418fa53107a0536b8f0524 |
| rem_csr_trap_setup_red023 | FAIL 1: fire_tp_csr_023 first | 0f976ddf9f5f7110ec6b5a1ece9ca343 |
| rem_csr_trap_setup_red024 | FAIL 1: fire_tp_csr_024 first | 9c809f36845a5ac4c365db271c0938e5 |
| rem_csr_trap_setup_red025 | FAIL 1: fire_tp_csr_025 first | bab81d9a214c91932afb9913b8df3d2d |
| rem_csr_trap_setup_red027 | FAIL 1: fire_tp_csr_027 first | 84561fc66bcce671726c623280f7d10e |
| rem_csr_trap_setup_red028 | FAIL 1: fire_tp_csr_028 first | 685e198c4e605bc68b63b451d0b234f9 |
| rem_csr_trap_setup_red029 | FAIL 1: fire_tp_csr_029 first | 1e54f148ec9e094a47e6ca9dcc56cdb6 |
| rem_csr_trap_setup_red030 | FAIL 1: fire_tp_csr_030 first | 3291035daa8a29c9ea05c1461f26c602 |
| rem_csr_trap_setup_red035 | FAIL 1: fire_tp_csr_035 first | 7fe46b312adbb7513ffcc5479f75230f |
| rem_csr_trap_setup_red036 | FAIL 1: fire_tp_csr_036 first | 743335dd679a122df8465294f8194429 |
| rem_pmp_csr_warl_red1 | FAIL 1: fire_tp_pmp_001 first | f10dbc11d29384bfe41254973fb81efa |
| rem_pmp_csr_warl_red2 | FAIL 1: fire_tp_pmp_002 first | c13698f7b4f49d1a2047acdcca959e78 |
| rem_pmp_csr_warl_red3 | FAIL 1: fire_tp_pmp_003 first | b381e546be80bbe3c86f41c708306614 |
| rem_pmp_csr_warl_red4 | FAIL 1: fire_tp_pmp_004 first | 4aaae61ec7dcf931c19e020bfff921c6 |
| rem_pmp_csr_warl_red5 | FAIL 1: fire_tp_pmp_005 first | e71a2879312154cc1a5584b2b26b557a |
| rem_pmp_csr_warl_red6 | FAIL 1: fire_tp_pmp_006 first | 7651f6a5cdc1f5d6fb7d79f57fc1f166 |
| rem_pmp_csr_warl_red7 | FAIL 1: fire_tp_pmp_007 first | 4d0bacb59a23a16f59a18cad82fc65f7 |
| rem_pmp_csr_warl_red8 | FAIL 1: fire_tp_pmp_008 first | cd6b0267924ef1fc2a8f67fd56589de9 |
| rem_rst_boot_red003 | FAIL 1: fire_tp_rst_003 first | 478240b7ec6443f060e669611dd7cf19 |
| rem_rst_boot_red006 | FAIL 1: fire_tp_rst_006 first | a57fd66fdf73111e26b20dc6c6c3ece0 |
| rem_rst_boot_red007 | FAIL 1: fire_tp_rst_007 first | 09d9e146965e9771d5c24cdef793870d |

Every red trips the intended item; where a superset check audits the same records it precedes the intended one in fire_check order
(cmp_zcmp_basic 039 for any push, 045 for any pop, 047 for the popret's words, 052 for the hazard mva01s; bit_draft red2 trips the gorci
compare and the new control-coverage check). The first csr_access remediation runs (rem_csr_access_s1/s2/red1_*) were overwritten by a
shared-scratchpad collision between two subagents and are superseded by the rem_csr_access_v2_* runs; the rem_cmp_zcb_s1 and
rem_manifest_stale runs of 11:37 UTC failed on a stale image (old generator) and are superseded by rem2_*; the retention pass of landing 3 dropped these superseded runs from gen_tdd_logs/test_writer (named in the manifest header), none was cited as proof.

### 8.3 Reproduction

    python3 dv/auto_dv/tests/gen_programs/gen_<g>_prog.py --seed 1 --out <w>/gen_source.S --red --red-item <TP-ID>
    python3 dv/auto_dv/stim/gen_program.py --directed <w>/gen_source.S --seed 1 --out <w>/prog --gcc-opts=-Idv/auto_dv/tests/gen_programs
    SEED=1 dv/auto_dv/tests/gen_fixtures/gen_run_fixture.sh <OUT> <name> dv.auto_dv.tests.gen_test_<g> <w>/prog/prog.vmem

Flow: the red entries in gen_testlist_entries.yaml pin one item each; acceptance wave 3 re-runs the four comparator-clean tests.

Incident recorded (cross-model review of 2d72b4a): the bit_draft generator's --red-item help string used Python 3.12-only nested
f-string quoting; the Test Writer's py_compile under the system Python 3.9 caught it before the landing and the string was
de-nested (seed-1 program byte-identical). The flow's interpreter is 3.12, so no run was affected.

## 9. Acceptance wave 3 (2d72b4a), the T-102 build, and landing 3

Wave 3 (test-writer-031..038, head mode at 2d72b4a, 12:2x UTC): gen_test_csr_access, gen_test_cmp_zcb and gen_test_bit_draft PASS on all
three seeds (UVM_ERROR 0); their pinned reds -035/-036/-038 RED-OK on the named fire id. gen_test_cmp_zcmp_basic (-033, -037) NOT_RUN:
its generator imported gen_prog_const without the sys.path guard the flow's script invocation needs (`ModuleNotFoundError: No module
named 'dv'`, program/generator.log); the guard is added (seed-1 source byte-identical) and the library self-test now runs every
generator as a flow-style script, so this class of defect is caught before a commit. Re-filed as test-writer-047/048 after landing 3.

TB Infra's T-102 (d0c0d15, 50256f0) on a build of HEAD 20a66cf (out_head3, see the template transcript Section 9): the four tests
that failed the flow verdict on comparator rows now PASS with UVM_ERROR 0 and their per-item manifests:

| Run (out_head3/<dir>) | Result | GEN_TEST_BINS | UVM_ERROR | md5 (stdout.log) |
|---|---|---|---|---|
| l3_rst_boot_s1 | PASS | 9 | 0 | 2f08de3777a44b7c42d84445c8afcc89 |
| l3_csr_reset_s1 | PASS | 81 | 0 | 424ab59b6f0f750e12ccf618fca3abd2 |
| l3_csr_trap_setup_s1 | PASS | 172 | 0 | c9d7fd261c83d32286fe34953405df18 |
| l3_pmp_csr_warl_s1 | PASS | 266 | 0 | b977c9904e5901f35716216cc5df990b |

Wave 4 (test-writer-039..046) requests those four tests and their pinned reds from Runtime. Landing 3 also labels the irq-agent
preconditions not applied (TP-CSR-023/029, TP-RST-006: docstring and GEN_TEST_INFO), replaces the T-102 wording with the status
citing d0c0d15/50256f0 and the consistency-compare caveat, and deduplicates the layers_required explanation.

### 9.1 Acceptance wave 4 (test-writer-039..046, head mode, the four tests T-102 held back)

| Request | Test | Seed | Verdict | Reason | head_sha |
|---|---|---|---|---|---|
| test-writer-039 | gen_test_rst_boot | 161973274 | PASS | no collected failure mechanism; end marker and config banner present | d22ac19103b4 |
| test-writer-039 | gen_test_rst_boot | 227699301 | PASS | no collected failure mechanism; end marker and config banner present | d22ac19103b4 |
| test-writer-039 | gen_test_rst_boot | 767411510 | PASS | no collected failure mechanism; end marker and config banner present | d22ac19103b4 |
| test-writer-040 | gen_test_csr_reset | 356330330 | PASS | no collected failure mechanism; end marker and config banner present | d22ac19103b4 |
| test-writer-040 | gen_test_csr_reset | 1901869263 | PASS | no collected failure mechanism; end marker and config banner present | d22ac19103b4 |
| test-writer-040 | gen_test_csr_reset | 2106622326 | PASS | no collected failure mechanism; end marker and config banner present | d22ac19103b4 |
| test-writer-041 | gen_test_csr_trap_setup | 75672323 | PASS | no collected failure mechanism; end marker and config banner present | d22ac19103b4 |
| test-writer-041 | gen_test_csr_trap_setup | 256705059 | PASS | no collected failure mechanism; end marker and config banner present | d22ac19103b4 |
| test-writer-041 | gen_test_csr_trap_setup | 1306446864 | PASS | no collected failure mechanism; end marker and config banner present | d22ac19103b4 |
| test-writer-042 | gen_test_pmp_csr_warl | 670590772 | PASS | no collected failure mechanism; end marker and config banner present | d22ac19103b4 |
| test-writer-042 | gen_test_pmp_csr_warl | 1428092103 | PASS | no collected failure mechanism; end marker and config banner present | d22ac19103b4 |
| test-writer-042 | gen_test_pmp_csr_warl | 1532037239 | PASS | no collected failure mechanism; end marker and config banner present | d22ac19103b4 |
| test-writer-043 | gen_test_rst_boot_red | 1 | RED-OK | red fixture failed as designed (red_expect matched): gen_fail_marker at sim_stdout.log:103 | d22ac19103b4 |
| test-writer-044 | gen_test_csr_reset_red | 1 | RED-OK | red fixture failed as designed (red_expect matched): gen_fail_marker at sim_stdout.log:158 | d22ac19103b4 |
| test-writer-045 | gen_test_csr_trap_setup_red | 1 | RED-OK | red fixture failed as designed (red_expect matched): gen_fail_marker at sim_stdout.log:847 | d22ac19103b4 |
| test-writer-046 | gen_test_pmp_csr_warl_red | 1 | RED-OK | red fixture failed as designed (red_expect matched): gen_fail_marker at sim_stdout.log:853 | d22ac19103b4 |

Totals: {'PASS': 12, 'RED-OK': 4}. With waves 3 and 4, seven of the eight batch-1 tests PASS in the flow on three seeds each with UVM_ERROR 0 and their
pinned red fixtures reach RED-OK on the named fire id; gen_test_cmp_zcmp_basic follows as wave 3b (test-writer-047/048) once the
import-guard fix is committed.

### 9.2 Acceptance wave 5 (test-writer-047/048, head mode with the step-2b layers live) and its diagnosis

gen_test_cmp_zcmp_basic: seeds 110100884 and 1156253223 PASS (UVM_ERROR 0, GEN_TEST_BINS n=473, 528k and 654k cycles under long bus
regimes); seed 421987159 and the red (seed 1) FAIL with `end-of-test store 1 of 4133 not seen within 300000 cycles`. Cause: the
template's fixed per-store budget, not the program and not the testbench; under the drawn regimes (dmem_gnt long, imem_rvalid
long or random, imem_gnt random) the program's prologue reaches its first report store at cycle 327k to 430k while the core keeps
retiring (12272 instruction fetches in the 300k cycles of the failing run). Deterministic: the local reproductions with the same
source hash, plusargs, seed-derived schedule and testbench revision reach the same first-store cycles. Landing 3c makes the wait
progress-based (template transcript Section 9.2): the failing seed then PASSes at 968492 cycles and the red FAILs on its designed
item. Recorded by the Orchestrator as LOG-030 (a template defect found by acceptance under live layers). Wave 5 re-files against 3c.

## 10. Landing 3e: pinned reds re-run on the build out_head5 (TB sources equal to b95d6d2's), csr_trap_setup at plan v2k, the fixed self-test from a clean archive

Why: Runtime's loader applies every red entry's red_expect to its retained pinned-red log with gen_verdict.decide_lines (the
reviewer's method, CM11). The retained reds of rst_boot, csr_reset, csr_trap_setup and pmp_csr_warl predated the T-102 comparator
fixes and carried isa_rd / isa_pc_next UVM_ERROR rows ahead of the harness line, so they decided FAIL on the log itself although the
same fixtures were RED-OK live in waves 3 and 4; gen_test_boot_retire_red had no retained log. Plan v2k (5f530a8) moved TP-CSR-026,
TP-CSR-029 and TP-CSR-031 into the new group gen_csr_trap_setup_irq, which left the committed library self-test red (built + not_built
outside the group). The ruling (LOG-036) keeps TP-CSR-029 built here and moves only 026 and 031 (plan v2l, landed jointly with this
module): fire_tp_csr_029 stays as at HEAD, not_built is empty, and the manifest is re-rendered against the nine-item group (168 bins;
the only delta to HEAD is the two removed not_built header lines; the four TP-CSR-035 interrupt bins stay excluded). The two-sided
guard was checked with that group list (against the committed v2k plan it fails on 029, as LOG-036 records). A 144-bin intermediate
state (029 removed against v2k) existed in this tree for half an hour and was undone; its runs were not retained.

Build: out_head5 (export of a8dfec4; `git diff --stat a8dfec4 HEAD -- dv/auto_dv/gen_tb dv/auto_dv/tb dv/auto_dv/env dv/auto_dv/isa`
is empty, so its TB sources equal HEAD), Python root head_export4 (export of HEAD b95d6d2 without dv/auto_dv/tests, so the test modules
come from this tree). A first attempt with the older Python root head_export3 (a8dfec4) failed to import: the library now reads the flow
marker from gen_flow_const.JOB_ENV_SET, which that export lacks; those runs were discarded before retention. Programs: the committed
generators at seed 1 with `--red --red-item <pinned item>` (gen_boot_retire_red.S directed), built by gen_program.py; the csr_trap_setup
green reuses the seed-1 image of Section 8 (generator unchanged).

| Run (out_head5) | Retained as | Result | GEN_TEST_BINS | UVM_ERROR lines | Verdict (gen_verdict.py --red-fixture, entry red_expect) | md5 (stdout copy) |
|---|---|---|---|---|---|---|
| l8_boot_retire_red1 | gen_boot_retire_red1_stdout.log | FAIL: fire_eot_pass_code (and fire_retired_floor) | 0 | 0 | RED-OK | b9efa679b50aa87e37da7ea4fdd547d7 |
| l8_rst_boot_red1 | gen_rst_boot_red1_stdout.log | FAIL: fire_tp_rst_006 | 8 | 0 | RED-OK | 1ada13feaa1308c7c9346a24701f58e4 |
| l8_csr_reset_red1 | gen_csr_reset_red1_stdout.log | FAIL: fire_tp_csr_106 | 81 | 0 | RED-OK | ea60016680541abf17557122aaf47125 |
| l8_csr_trap_setup_red1 | gen_csr_trap_setup_red1_stdout.log | FAIL: fire_tp_csr_036 | 168 | 0 | RED-OK | 6888ee6bb14b4e416fc66433b1ad6f45 |
| l8_pmp_csr_warl_red1 | gen_pmp_csr_warl_red1_stdout.log | FAIL: fire_tp_pmp_001 | 266 | 0 | RED-OK | 218bd8002efc393f88cdb3dce0034abf |
| l8_csr_trap_setup_s1 | gen_l8_csr_trap_setup_s1_stdout.log, _sim.log | PASS | 168 | 0 | PASS | 5ad7d0d6de50cda9393627b90f481b68 |

Each run's verdict.txt is retained beside its log (gen_<name>_verdict.txt). `python3 dv/auto_dv/flow/gen_flow_util.py
--check-red-signatures dv/auto_dv/work/test-writer/gen_testlist_entries.yaml` reads PASS with every row RED-OK and no STALE row (16 red entries; the cmp_zca and isa_cti reds
were replaced by the l9_* runs on out_head6, UVM_ERROR-free; re-run at landing 3h from an export of HEAD). The same command against
the committed testlist, `--check-red-signatures dv/auto_dv/flow/gen_testlist.yaml`, from a detached archive of 8fff875 reads the same:
RED-CHECK PASS, 16 rows RED-OK, no STALE row (the staged file is git-ignored; the committed one is what a reviewer runs). The T-102-era copies
were removed under the retention rule (LOG-024; the manifest header names them); the per-item red excerpts now start with the run
header line (LOG-034), and the md5 cells of gen_tdd_batch2.md follow the excerpt copies.

Library self-test from a clean archive: `git archive 7f78c41` extracted to a scratch directory (gen_test_lib.py, gen_test_template.py,
gen_test_bit_draft.py, gen_fcov_manifest.py and gen_testlist.yaml byte-equal to that commit's blobs), `PYTHONPATH=<archive> python3
dv/auto_dv/tests/gen_test_lib.py --self-test` without the developer variable: PASS (Critic v4 Section 6's closure condition for H-1: the
working loops refuse every listed red source, the aliased-parameter helper included). On this tree after the 3e edits: PASS in both
forms (committed entries only; staged entries), with two stale-evidence notices (cmp_zca, isa_cti). Negative check of the new
red_expect rule: a staged copy of the bit_ratified and bit_draft red entries with the boundary form (`\bfire_tp_bit_014\b`,
`\bfire_tp_bit_016\b`) fails the self-test on the synthesized harness line (the recorded names are fire_tp_bit_014_ops /
_pattern and fire_tp_bit_016_gorci).

## 11. Landing 3e: promotion and the layers_required opt-out dropped

The DV Lead's per-entry tier table (dv/auto_dv/work/dv-lead/gen_round0_promotion_table.md) promotes 15 entries (14 smoke, gen_test_bit_draft
targeted; gen_test_boot_retire stays check) with measured: true, seeds 3 and fcov_expectation_file wired to each class's per-item
manifest; the red entries stay check / measured: false. The bring-up opt-out `layers_required = False` (class attribute, its comment and the
docstring sentence) is removed from all 16 built tests, so a declared knob without a REGIME_SET consumer now fails setup as the template
default demands. Proof that no test trips it: every test at seed 1 on out_head6 (export of ce33b4f) with the modules of this tree and the
layers applied (one GEN_TEST_PHASE idx=0 line per drawn knob and fire_schedule_applied ok=True in every log; no log carries a
GEN_TEST_LAYERS applied marker):

| Run (out_head6) | Result | GEN_TEST_BINS | UVM_ERROR | EOT cycle | phases applied / fire_schedule_applied | SLOW rounds | md5 (gen_<run>_stdout.log) | Note |
|---|---|---|---|---|---|---|---|---|
| l9g_boot_retire | PASS | 0 | 0 | 4263 | 6 / yes | 0 | 4a04c574d6191f922cb7d89b4ce4582a |  |
| l9g_rst_boot | PASS | 8 | 0 | 778 | 4 / yes | 0 | 00eb7e460622ed85482b656a9580e12b |  |
| l9g_csr_reset | PASS | 81 | 0 | 1438 | 5 / yes | 0 | 8edfec244253785e1a50ba3bb4e82b37 |  |
| l9g_csr_access | PASS | 80 | 0 | 21090 | 2 / yes | 0 | 102aa761219b7aa74d59c77ae23e14f5 | knob_instr_mix removed from schedulable (program-side knob, no TB consumer) |
| l9g_csr_trap_setup | PASS | 168 | 0 | 28926 | 2 / yes | 0 | f0031b04ada78331e4152680f5902e28 |  |
| l9g_cmp_zcb | PASS | 110 | 0 | 6424 | 3 / yes | 0 | 428cf64a931b948f3bae1e894d70ae40 | image rebuilt (the 07:5x image ran away after store 122 under the current image loader; fresh image identical run to l4) |
| l9g_cmp_zcmp_basic | PASS | 473 | 0 | 755229 | 4 / yes | 3 | afba20a866b9e4e2560bd5f8c7d859fc |  |
| l9g_bit_draft | PASS | 15 | 0 | 4573 | 1 / yes | 0 | 8f58452679d1cd1d566eb2ad5545d585 | image rebuilt (same stale-image runaway at store 42) |
| l9g_pmp_csr_warl | PASS | 266 | 0 | 63243 | 6 / yes | 0 | 0bc43991656a2b1de295343c2519fc6d | image rebuilt (the 07:5x image predates the link layout change: no gen_probe_pool symbol) |
| l9g_cmp_zca | PASS | 337 | 0 | 29797 | 6 / yes | 0 | bec9704b05a3157737f621d394a69d58 |  |
| l9g_bit_ratified | PASS | 830 | 0 | 23163 | 6 / yes | 0 | 8b95c174d030fc6d960de7c925da3d5a |  |
| l9g_isa_alu | PASS | 602 | 0 | 212028 | 6 / yes | 0 | 700711cc0d34d9781c21ec2d09824dcc |  |
| l9g_isa_shift | PASS | 120 | 0 | 9361 | 6 / yes | 0 | abc45fce9977597e3d29f32f6b723054 |  |
| l9g_isa_cti | PASS | 200 | 0 | 379708 | 6 / yes | 0 | c5d0628495001a10e0ce615ab99db650 |  |
| l9g_mul_mul | PASS | 338 | 0 | 11191 | 6 / yes | 0 | 58d44699bf138d61b6f866df722d34f0 |  |
| l9g_mul_div | PASS | 224 | 0 | 11076 | 6 / yes | 0 | 9d5f7807b837a09bd2c0c7db44562b20 | v3 image (filler fix) |

All 16 PASS with every declared knob consumed (phase 0 applies each drawn knob; fire_schedule_applied ok). This proof covers the
initial phase only: every schedule here had its mid-run triggers unapplied by the runner defect of Section 12, and the check passed
because no trigger fell before the end of test at seed 1 (LOG-042a). Two findings from the sweep,
both fixed in this landing: gen_test_csr_access declared knob_instr_mix, a program-side knob (gen_tb_knobs.yaml: regime_set_consumer
program) the TB cannot schedule, so the template's consumer check failed it once the opt-out was gone; the knob is no longer declared
(the docstring says why). Three seed-1 images built at 07:5x UTC (pmp_csr_warl, cmp_zcb, bit_draft) predate the image layout change of
the program builder and ran away or lacked symbols under the current image loader; rebuilt from the committed generators they pass
(cmp_zcb: the same 132 stores / 862 retired / cycle 6424 as the l4 run). The flow builds every image fresh per run, so this is a
local-harness artefact: the older images under batch1/<group>/s1 are not evidence any more. Logs retained as gen_l9g_<group>_stdout.log
and _sim.log (LOG-034: greens in full).

## 12. Landing 3h: the schedule runner applies mid-run phases (LOG-042a)

Why: the batch-2 acceptance wave (Runtime test-writer-049..055, head mode at d3c6ca8) failed 13 of its 24 greens on
fire_schedule_applied alone ("reached N of M scheduled entries by EOT ..., applied 6, missed [...]"; no other ok=False line in any
of the 13 logs), and Runtime's bisect probes at 7ef16a0 and d3c6ca8 (probe_t181_bit_ratified_7ef16a0 / _d3c6ca8, gen_test_bit_ratified
seed 288888690) are identical: six GEN_TEST_PHASE idx=0 lines at cycles 60-65 and none with idx>0.

Cause, in the template and not in the TB: GenTest._edge_or_eot, the wait behind wait_cycles / wait_retired / wait_event, abandoned
its wait at the first EOT-register store: it returned False as soon as evt_eot_count was above zero and on any edge of evt_eot_seen.
The bridge toggles evt_eot_seen on every store to the EOT register (gen_bridge_if.sv), and the report channel stores its words through
that register, so in every test with report words the runner's wait for the first mid-run trigger ended at report 0: in the probe,
report 0 lands at cycle 289 and the first mid-run trigger is c709, run_schedule took the False return for the end of the program and
returned, and the six idx=0 phases stayed the only ones. The dispatcher was never called for the later entries: the probe log carries
exactly six "[GEN_PHASE] phase N" dispatch lines (gen_env_pkg.sv) and no REGIME_SET after cycle 65, so this is not a silent refusal
and nothing is open on the TB side. The wave's 11 greens are the seeds whose mid-run triggers all fall after the end of test
(reached 6 = applied 6). The same False return would have ended any stimulus-body wait after the first report store; no committed test
calls wait_cycles / wait_retired / wait_event outside the template.

Fix: _edge_or_eot ends a wait only at the final store (store number expected_reports + 1, the rule wait_eot already applies); a
report-store edge re-arms the wait within the remaining budget, and a hit landing in the same cycle as a store is not lost (the
awaited signal is sampled before and after the edge). The docstring, the run-order comment and gen_test_template_api.md (step 3 and the
wait_* row) state the rule. gen_run_fixture.sh's run header now carries the sources sha the compile step records (`sources_sha=`), so a
retained run names its build; since landing 3i it also carries `template_sha=`, the sha256 prefix of the python root's gen_test_template.py,
so a run from an out-of-tree pyroot names the template it executed (CM30-I-1).

Runs: build out_head8, the export of HEAD 9e7c440 with the fixed template (sources sha 156eb9357b79552e; the TB sources equal d3c6ca8's,
the wave's tree: `git diff --stat d3c6ca8 HEAD -- dv/auto_dv/tb dv/auto_dv/env` is empty). The images are the wave's own prog.vmem files
(one per failing seed, crc32 as in the wave's run_cmd.sh), and the HEAD generators reproduce them byte for byte (bit_ratified seed
288888690 regenerated from dv/auto_dv/tests/gen_programs/gen_bit_ratified_prog.py + gen_program.py: sha256 b9a697debab0 both).

- 3h_red_prefix_bit_ratified_288888690: HEAD's template before this landing (pyroot head_export7, an archive of 9e7c440; that template's
  sha256 prefix 89fc45e20f827180, the fixed template's abbe6fcb78e53a27) on out_head8:
  FAIL fire_schedule_applied, applied 6, missed 5, the probe's numbers; GEN_TEST_FAIL harness line (RED-OK). The failing path a reviewer
  re-runs: the same fixture command with a pyroot whose gen_test_template.py is 9e7c440's.
- 3h_red_mut_bit_ratified_288888690: the fixed template with mutation 3h-M1 (run_schedule skips the idx=1 entries of a reached boundary;
  gen_3h_mutation_M1.diff, 3 lines): GEN_TEST_PHASE idx=2 at cycle 11564 (the runner now reaches later boundaries), fire_schedule_applied
  ok=False applied 7, missed 4 (the four c709 entries), GEN_TEST_FAIL harness line (RED-OK): a reached but unapplied c-triggered entry
  fails loud after the fix.
- 3h_acc_*: the 13 seeds that failed the wave, all PASS, 1 to 17 idx>0 phases each, every reached entry applied (ok=True, applied ==
  reached), GEN_TEST_BINS equal to the committed manifests, UVM_ERROR 0. The end-of-test cycles differ from the wave's because the mid-run
  regimes now change the bus delays (bit_ratified 288888690: 66382 in the wave, 35276 here).

| Run (out_head8) | Result | GEN_TEST_BINS | UVM_ERROR | EOT cycle (wave) | EOT cycle | fire_schedule_applied | phases idx=0 + idx>0 (max idx) | md5 (gen_<run>_stdout.log) |
|---|---|---|---|---|---|---|---|---|
| 3h_red_prefix_bit_ratified_288888690 | FAIL: fire_schedule_applied | 830 | no UVM summary (the failing cocotb test ends the sim before the report) | 66382 (probe) | 66382 | ok=False reached 11 of 14, applied 6, missed 5 entries | 6 + 0 (max idx 0) | d90f869a6eb917853de7fc8513f6a7f3 |
| 3h_red_mut_bit_ratified_288888690 | FAIL: fire_schedule_applied | 830 | no UVM summary (the failing cocotb test ends the sim before the report) | 66382 (probe) | 66382 | ok=False reached 11 of 14, applied 7, missed 4 entries | 6 + 1 (max idx 2) | ce12abf01274daf0649678703814b969 |
| 3h_acc_bit_ratified_1400867381 | PASS | 830 | 0 | 16293 | 16699 | ok=True reached 10 of 10, applied 10 | 6 + 4 (max idx 1) | b05b7f9073e5b988b5dd8458c107dd16 |
| 3h_acc_bit_ratified_288888690 | PASS | 830 | 0 | 66382 | 35276 | ok=True reached 11 of 14, applied 11 | 6 + 5 (max idx 2) | ab200817357725d0b046b6320031ae3d |
| 3h_acc_bit_ratified_555087581 | PASS | 830 | 0 | 17215 | 16934 | ok=True reached 7 of 20, applied 7 | 6 + 1 (max idx 1) | bb3af561a42dd172deedb1dc4d5d7f7e |
| 3h_acc_cmp_zca_1539293166 | PASS | 337 | 0 | 63784 | 8641 | ok=True reached 15 of 16, applied 15 | 6 + 9 (max idx 2) | a2b8be0655e9dcd38a017c4d7e0a2de9 |
| 3h_acc_cmp_zca_2115402665 | PASS | 337 | 0 | 29520 | 25546 | ok=True reached 13 of 13, applied 13 | 6 + 7 (max idx 2) | 6f5d63f8d16beda5134015423406f346 |
| 3h_acc_isa_alu_1711178164 | PASS | 602 | 0 | 319829 | 546858 | ok=True reached 12 of 12, applied 12 | 6 + 6 (max idx 2) | 547fa8250a8f9d00c7ad61a492060f3d |
| 3h_acc_isa_alu_1730556152 | PASS | 602 | 0 | 277317 | 606317 | ok=True reached 16 of 16, applied 16 | 6 + 10 (max idx 2) | a1504c1c955f662b2c5b287d931c21ad |
| 3h_acc_isa_cti_1038415940 | PASS | 200 | 0 | 372800 | 679451 | ok=True reached 23 of 23, applied 23 | 6 + 17 (max idx 4) | 777e1b7ee5fa86102b1889e2dce3a33e |
| 3h_acc_isa_cti_777966141 | PASS | 200 | 0 | 319530 | 880839 | ok=True reached 16 of 16, applied 16 | 6 + 10 (max idx 3) | 3a5834cb5d8384feee35da7e3cb4e8c1 |
| 3h_acc_isa_shift_1401504676 | PASS | 120 | 0 | 28022 | 25006 | ok=True reached 17 of 17, applied 17 | 6 + 11 (max idx 3) | ceb1cda45ace9524eb1f55b58ecf07c9 |
| 3h_acc_mul_div_1465513474 | PASS | 224 | 0 | 9901 | 9511 | ok=True reached 13 of 13, applied 13 | 6 + 7 (max idx 2) | 2ece980cd4c168804fe919c06888f580 |
| 3h_acc_mul_div_1640919798 | PASS | 224 | 0 | 17761 | 11603 | ok=True reached 13 of 13, applied 13 | 6 + 7 (max idx 2) | e2c804510a284214c39b789b80eef6c8 |
| 3h_acc_mul_div_754956299 | PASS | 224 | 0 | 21200 | 9000 | ok=True reached 14 of 14, applied 14 | 6 + 8 (max idx 3) | 63d829bacebff833e525c80b13a78c51 |

Logs retained in full (stdout.log with the run header prepended, and sim.log) for the two template reds and the 13 greens, plus the
mutation diff, as gen_3h_<run>_stdout.log / _sim.log and gen_3h_mutation_M1.diff (gen_manifest.md, LOG-034: greens and the landing's
decisive reds in full). The red runs' sim.log carries no UVM summary: the failing cocotb test ends the simulation before the report,
and the harness line is in stdout.log (the flow's gen_fail_marker).

Scope correction for Section 11 (LOG-042a): the l9g proof "the layers are live" exercised the idx=0 batch only, each drawn knob applied
once at start-up before FETCH_EN; no mid-run phase had run in any test before this landing, so that proof supports the promotion (the
declared knobs are consumed) and nothing about mid-run regime changes; plan items whose stimulus needs one are held by LOG-042b until
this landing is reviewed.

Reproduction (from a clean archive of the landing commit; the images from the flow's run directories or regenerated as above):

    bash -lc 'source ci/env.sh && FORCE=1 bash dv/auto_dv/tb/gen_tb_local.sh compile <OUT>'
    GEN_TB_PYROOT=<archive> SEED=288888690 bash dv/auto_dv/tests/gen_fixtures/gen_run_fixture.sh <OUT> 3h_acc_bit_ratified_288888690 \
        dv.auto_dv.tests.gen_test_bit_ratified <abs path>/prog.vmem
    # the red: the same command with a pyroot whose dv/auto_dv/tests/gen_test_template.py is 9e7c440's (applied 6, missed 5);
    # the mutation red: the pyroot with gen_3h_mutation_M1.diff applied to the fixed template (applied 7, missed 4)

## 13. T-206: gen_test_csr_reset seed 1028791296 ran away in round 0 (a debug request storm on a program without debug handling)

Why: round 0 (Runtime, head mode on 37c7ecb, LOG-046) had one test-side failure, gen_test_csr_reset seed 1028791296: "end-of-test store 1 of 89
not seen within 16 x 100000 cycles (cycle 1600065, retired 32890) although the core keeps retiring (runaway program)"; the run's layer-2 draw
was debug_req_regime=storm, imem_gnt_delay=random, imem_rvalid_delay=short, irq_line_mix=single, scr_key_delay=withheld_then_valid, its
schedule applied a mid-run phase at c19746 (debug_req_regime none, irq_line_mix multi, imem_rvalid_delay long, scr_key_delay delayed), and the
debug agent logged the storm from cycle 65 (sim.log "[GEN_DBG] knob_debug_req_regime <= storm"). The other two round-0 seeds of the test
(debug_req_regime none and sparse) passed at cycles 769 and 779. UVM_ERROR was 0 in the failing run: the ISA comparator followed the DUT.

Cause: gen_test_csr_reset declared knob_debug_req_regime schedulable (with irq_line_mix, imem delays and scr_key_delay, the items' Knobs lines)
while its generated program has no debug handling and the memory model's DM window (GEN_MM_DM_BASE 0x1a110000, halt 0x1a110800, exception
0x1a110808) carries no program code. A debug request storm drawn at start-up halts the core into that window before the program's first report
store; it never returns to the program (retirement continued at about 2050 per 100000 cycles, the exception path in the DM window), and the
storm's end at c19746 did not recover it. A debug request is taken regardless of mstatus.MIE, unlike an interrupt (gen_test_rst_boot's
irq_regime=storm draw in the same round passed: interrupts stay untaken with MIE=0). Not a DUT defect: the comparator saw no mismatch.

Reproduction and control, out_head8 (export of 9e7c440 with the 3h template, sources sha 156eb9357b79552e), the round-0 image of the seed:
- t206_csr_reset_1028791296_asis: the committed test as is: the same runaway, store 1 of 89 not seen (excerpt md5 df3e87f00448f28e26bc178ec086c768).
- t206_csr_reset_1028791296_dbgnone: the same run with +gen_knob_debug_req_regime=none (the knob pinned, so the template leaves it to the
  command line and draws the rest): PASS, 88 reports, 81 bins (excerpt md5 45be0c9836440179817f8fe483b89e0a). The knob is the whole difference.

Fix (landing 3k): knob_debug_req_regime is removed from the test's schedulable set; the docstring says why and that the items' debug-mode clauses
stay the not-built clauses already stated. The manifest is unchanged by a --test-module re-render (bins derive from the items, not the knobs);
the structure self-test PASSes. Re-runs on out_head8 with the fixed test (the three round-0 images, and the pinned red TP-CSR-106 at seed 1):

| Run | Result | GEN_TEST_BINS | UVM_ERROR | reports | retired | EOT cycle | fire_schedule_applied | knobs drawn | md5 (gen_<run>_stdout.log) |
|---|---|---|---|---|---|---|---|---|---|
| t206fix_csr_reset_1028791296 | PASS | 81 | 0 | 88 | 243 | 4203 | ok=True reached 4 of 8, applied 4 | imem_gnt_delay=random imem_rvalid_delay=short irq_line_mix=single scr_key_delay=withheld_then_valid | 32b0c2f68f1ba73a42443fc363033d52 |
| t206fix_csr_reset_1118950644 | PASS | 81 | 0 | 88 | 258 | 768 | ok=True reached 4 of 17, applied 4 | imem_gnt_delay=same_cycle imem_rvalid_delay=min1 irq_line_mix=with_nmi scr_key_delay=immediate | d56dd55e1c9904053e07a817b958b6f6 |
| t206fix_csr_reset_1228198789 | PASS | 81 | 0 | 88 | 261 | 778 | ok=True reached 4 of 10, applied 4 | imem_gnt_delay=same_cycle imem_rvalid_delay=min1 irq_line_mix=single scr_key_delay=delayed | 2ab43a633df38e57c9008ddb271fd510 |
| t206fix_csr_reset_red_106_s1 | FAIL 1: fire_tp_csr_106 first (RED-OK) | 81 | no UVM summary | 88 | - | - | - | imem_gnt_delay=same_cycle imem_rvalid_delay=long irq_line_mix=fast_only scr_key_delay=delayed | ab8b50cae4a635420cb23b466d45c22a |

The pinned red's committed retained log (gen_csr_reset_red1_stdout.log, the l8 run of Section 10) keeps its harness line and RED-OK verdict
under the fixed test (the knob set does not touch the red's deviation); the new red run is retained beside it as gen_t206fix_csr_reset_red_106_s1
so the fixed test's red is on record too. Logs: gen_t206_* (two excerpts) and gen_t206fix_* (four runs in full), gen_manifest.md.

Lesson for every test (recorded for the Orchestrator and the DV Lead): a program without a debug ROM must not schedule knob_debug_req_regime,
and a program without an interrupt handler must not schedule knob_irq_regime unless it keeps MIE=0 throughout; the template has no guard for
this today (the lint's red-source list is frozen, LOG-024d (a)), so the rule lives in the briefs and the reviews until a ruling adds one. The
declared debug-mode bins of this test at 56e37d7 are thirteen, not two: gen_csr_reset_read_cg cp_dbg.dbg, cr_dbg_reset.dcsr_dbg,
cr_dbg_reset.dpc_dbg, cr_dbg_reset.dscratch0_dbg, cr_dbg_reset.dscratch1_dbg, cp_csr.dcsr, cp_csr.dpc, cp_csr.dscratch0, cp_csr.dscratch1 and
gen_csr_debug_csr_cg cp_csr.dcsr, cp_trap.ok, cp_dbg.dbg, cr_csr_dbg_trap.dcsr_dbg_ok; none can be hit without a debug entry. Their disposition
is the DV Lead's rule (g) decision in TP-CSR-108's Notes (plan v2r part 4c), landed as T-222 (Section 14).

## 14. T-222: the thirteen debug-mode bins of TP-CSR-108 under bins_not_hit (rule (g))

Why: the 3k review (dv/auto_dv/reviews/2026-09-03-claude-diff-e4cbdd8b-56e37d75.md, rows CM42-*) found the closing sentence of Section 13
naming two of the thirteen debug-mode bins the committed manifest still declared as expected-hit, a docstring silent about them, and a history
breadcrumb. The DV Lead decided (TP-CSR-108 Notes, plan v2r part 4c) that the thirteen go under bins_not_hit with the reason (no debug handling
in the program, the debug regime not scheduled) pending a debug-ROM program, the four gen_csr_debug_csr_cg bins co-owned with TP-CSR-017
(gen_csr_debug_csr, a debug-capable group); LOG-055 ordered the re-render as a small landing ahead of the consolidated batch-3 touch.

Change: gen_test_csr_reset.py declares `bins_not_hit` with the thirteen tokens (gen_csr_reset_read_cg cp_dbg.dbg, cr_dbg_reset.dcsr_dbg,
cr_dbg_reset.dpc_dbg, cr_dbg_reset.dscratch0_dbg, cr_dbg_reset.dscratch1_dbg, cp_csr.dcsr, cp_csr.dpc, cp_csr.dscratch0, cp_csr.dscratch1;
gen_csr_debug_csr_cg cp_csr.dcsr, cp_trap.ok, cp_dbg.dbg, cr_csr_dbg_trap.dcsr_dbg_ok), each with the reason naming TP-CSR-108's Notes and
rule (g); the docstring names the set, says why, and drops the breadcrumb and the stale clause about gen_fcov_pkg (the package exists at HEAD;
this test's covergroups are not in it yet). The manifest was re-rendered with `python3 dv/auto_dv/tests/gen_fcov_manifest.py --test-module
dv/auto_dv/tests/gen_test_csr_reset.py --test gen_test_csr_reset --write` ("68 bins, 0 dropped by the manifest rule, 13 not_hit"): 81 declared
at 56e37d7, 68 now, thirteen `# not_hit` header lines; the 68 are exactly the 81 minus the thirteen (set compare in the retention script).
Nothing else changed: fire checks, program generator, schedulable set and the pinned red (TP-CSR-106) are as at 56e37d7, so the committed red
logs keep their verdicts.

Green run on a fresh export of HEAD: head_export13 = `git archive` of f6b42ea (HEAD when the export was made; between f6b42ea and 705edb8, the
HEAD at hand-off, no path under dv/auto_dv/env, tb, isa, gen_tb, tests, fcov_expectations, stim or rtl/ changed), tools/spike linked from the
clone, compiled to out_head13 (sources sha 8452b39617094289), the two T-222 files overlaid (template sha abbe6fcb78e53a27, the committed template). Program: the
generator at seed 1028791296 through dv/auto_dv/stim/gen_program.py with the testlist entry's --gcc-opts, from the export (266 words, crc32
0x27ec99e6, md5 6edabe4a45450ad667929468e15799b6, byte-identical to the round-0 image of Section 13). Run: seed 1028791296, module
dv.auto_dv.tests.gen_test_csr_reset, the export's fixture from the export root, no plusarg beyond the image set; the run header is the first
line of the retained stdout.

| Run | Result | GEN_TEST_BINS | equals the manifest | UVM_ERROR | reports | retired | EOT cycle | fire_schedule_applied | knobs | md5 (gen_<run>_stdout.log) |
|---|---|---|---|---|---|---|---|---|---|---|
| t222_csr_reset_1028791296 | PASS | 68 | yes (set compare) | 0 | 88 | 243 | 4203 | ok=True reached 4 of 8, applied 4 | pinned=- drawn=imem_gnt_delay=random imem_rvalid_delay=short irq_line_mix=single scr_key_delay=withheld_then_valid | bdcd77cc3871997c2114ddba27f1759a |

Retained in full (LOG-034: greens in full): gen_t222_csr_reset_1028791296_stdout.log (run header first) and gen_t222_csr_reset_1028791296_sim.log,
rows in gen_manifest.md. Self-tests from the detached archive with the overlay, PYTHONPATH and GEN_TEST_STAGED_ENTRIES unset:
dv/auto_dv/work/test-writer/head_export13_selftest_t222.log (18:57:00Z-18:57:09Z) reads "GEN_TEST_LIB self-test PASS" and "GEN_FCOV_MANIFEST
self-test PASS (67 bins for gen_reg_schedule, 1 dropped; 86 excluded coverpoints)", both rc=0, and the committed manifest equals a fresh
`--test-module` render (diff empty). The library self-test also PASSes in the shared tree at 18:57:20Z.

## 15. Follow-ups folded into the batch-3 touch: the Critic's batch-1 v8 lows on 3k and the T-222 review's info

- v8 L-2 (the run header stamps the template but not the test module): gen_run_fixture.sh now writes `test_sha=` beside `sources_sha=` and
  `template_sha=`, the sha256 prefix of the test module file Python resolves for MODULE (the first PYROOTS entry carrying it, then the fixtures
  directory), so a landing whose whole change is one test file is identified in every retained run header. First carried by the batch-3 touch's
  runs on out_head14 (gen_tdd_batch3.md Section 4: test_sha=29c1be4e19212597 is gen_test_pmp_lock.py of that landing).
- v8 L-3 (the Knobs sentence claimed the items' Knobs lines name debug_req_regime): gen_test_csr_reset.py says debug_req_regime is TP-CSR-108's
  alone, the item's debug half not built here. Docstring only; the manifest equals a fresh render.
- v8 L-1 (a structural guard for regime knobs without handlers, LOG-050): not in this touch; it is the template touch's item (the library refuses
  a schedulable dbg-consumer knob for a program without debug handling, and an irq-consumer knob for a program without a handler unless MIE is
  pinned 0; a red fixture proves the refusal), as LOG-050 places it.
- T-222 review (595fbf5, APPROVE, one info): the reason string is repeated thirteen times because gen_fcov_manifest.py's extractor accepts
  ast.Constant values only; no change, recorded so a shared constant is not attempted without extending the extractor first.
