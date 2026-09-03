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
