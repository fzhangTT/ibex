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

- Two seeds locally; the third seed and the flow verdict come from Runtime's acceptance runs (requests test-writer-009/011/012/013 and reds 017/019/020/021 filed 11:0x UTC; the comparator-blocked eight staged under work/test-writer/batch1/requests_staged/).
- `layers_required = False` on every batch-1 test (no REGIME_SET consumer at HEAD): layers 2 and 3 are drawn and logged, not applied; entries are `tier: check, measured: false` until step 2b re-lands.
- Mutation evidence per checker id (plan Section 5) is not part of this transcript; it needs Runtime's `--rtl-root` mutation copies and comes with the mutation batch.
- No subagent reported a fence event; the Test Writer re-verified compile, the AST structure check, ASCII and the log lines, not every expectation derivation.
