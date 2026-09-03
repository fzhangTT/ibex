# TDD transcript: Phase 1 batch 2 (seven M-mode, trap-free groups)

Test Writer, 2026-09-03. Seven subagents (one per group, dispatched 12:45 UTC on the Orchestrator's ruling after the Critic's batch-1 v2)
wrote gen_test_<g>.py, gen_programs/gen_<g>_prog.py and rendered gen_test_<g>.fcov.yaml from the module (--test-module, per built
items, not_built in the header) for g in cmp_zca, bit_ratified, isa_alu, isa_shift, isa_cti, mul_mul, mul_div. Every run below was made
through dv/auto_dv/tests/gen_fixtures/gen_run_fixture.sh against the HEAD-20a66cf build out_head3 (T-102 comparator in, step 2b not
yet) with GEN_TB_PYROOT = the export (rendered knobs matching the simv) and GEN_TEST_STAGED_ENTRIES (entries measured: false). The
Test Writer re-verified (13:5x UTC) in the working tree: py_compile, the library self-test (structure check with the not_built two-sided rule, the
fire_tp-called and item-naming rules, flow-style generator runs) over all 16 tests, ASCII, no hierarchical access, every manifest
unchanged by a --test-module re-render, and every run directory below re-read. At the batch-2 commit itself the committed tree's
self-test was red on gen_test_bit_draft.py (held back without its not_built attribute while the guard already required it); landing
3c commits that file; on the committed tree the self-test is green from e83614c on (the testlist commit that carries the batch-2
entries the layers_required rule needs), with no environment variable. Ordering: each red is `plan(seed, red=True, red_item)`
of the same generator (expectations asserted equal to the green plan), so red-ness does not depend on run order.

## 1. Summary

| Test | Items built | Bins | Seed 1 | Seed 2 | UVM_ERROR (s1/s2) | Default red pins | Per-item reds |
|---|---|---|---|---|---|---|---|
| gen_test_cmp_zca | 21 of 21 | 337 | PASS (reports 762) | PASS (reports 765) | 6/8 | TP-CMP-005 | 21, each tripping its item first |
| gen_test_bit_ratified | 18 of 19 (TP-BIT-001 not built: per-retirement rvfi_trap over the encoding table is an RVFI record fact; its U-mode leg leaves M-mode) | 830 | PASS (reports 685) | PASS (reports 679) | 0/0 | TP-BIT-014 | 18, each tripping its item first |
| gen_test_isa_alu | 10 of 10 | 602 (604 before the WP-9 bins_not_hit; retained 602-bin green l5_isa_alu_s1) | PASS (reports 6073) | PASS (reports 6069) | 0/0 | TP-ISA-002 | 10, each tripping its item first |
| gen_test_isa_shift | 4 of 4 | 120 | PASS (reports 338) | PASS (reports 356) | 0/0 | TP-ISA-010 | 3, each tripping its item first |
| gen_test_isa_cti | 8 of 12 (016, 022: memory map, no text near 0 or in the top 2 KiB, and the self-loop exit needs IRQ_SET codes; 024: timing clause; 026: self-loop exit and wrap text) | 200 | PASS (reports 2626) | PASS (reports 2528) | 64/64 | TP-ISA-017 | 8, each tripping its item first |
| gen_test_mul_mul | 8 of 9 (003: latency clause is the item's subject) | 338 | PASS (reports 367) | PASS (reports 379) | 0/0 | TP-MUL-002 | 7, each tripping its item first |
| gen_test_mul_div | 10 of 12 (012, 022: latency and cycle clauses are the items' subjects) | 224 | PASS (reports 184) | PASS (reports 200) | 0/0 | TP-MUL-014 | 9, each tripping its item first |

UVM_ERROR above 0 is not explained away: gen_test_cmp_zca carries 2 comparator rows per c.ebreak unit (isa_rd on the handler's `csrr mtval`:
Ibex 0 per the documentation and the plan, the Spike model the faulting pc; plus the isa_mem row of that report store), a shim mtval
legalization gap of the T-102 class, reported to TB Infra; gen_test_isa_cti carries 64 isa_pc_next rows per seed, every one `dut ==
model | 1` on a jalr/c.jr/c.jalr with an odd rs1 + imm: rvfi_pc_wdata bit 0 (bug candidate B13); TP-ISA-019 says the comparator masks
bit 0 per TP-BTALU-008 and the HEAD build does not; reported to TB Infra and the DV Lead. Both tests' fire-checks pass on the DUT's
architectural behaviour; their flow verdicts FAILed through uvm_error until the TB rows landed at ce33b4f (Section 2b: both tests UVM_ERROR-free there).

## 2. Runs (out_head3/<dir>; committed copies gen_tdd_logs/test_writer/gen_<dir>_stdout.log for s1, s2 and the default red, gen_<dir>_stdout_excerpt.log (decisive lines) for the per-item reds)

| Run | Result | GEN_TEST_BINS | UVM_ERROR | md5 of the retained copy (stdout.log; stdout_excerpt.log for the per-item reds) |
|---|---|---|---|---|
| b2_cmp_zca_red1 | retained copy replaced by l9_cmp_zca_red1 on out_head6 (Section 2b): FAIL: fire_tp_cmp_005 first | 337 | 0 | 8cca2bee47b3b402b274aa956852e8df |
| b2_cmp_zca_red_001 | FAIL 1: fire_tp_cmp_001 first | 337 | - | 82bfa27abdf94ac3296ef614e655b2c5 |
| b2_cmp_zca_red_002 | FAIL 1: fire_tp_cmp_002 first | 337 | - | d7bdce8647f067a39341aad4ea0dd4e6 |
| b2_cmp_zca_red_004 | FAIL 1: fire_tp_cmp_004 first | 337 | - | ae97796cab04ef408c991673e05e10be |
| b2_cmp_zca_red_005 | FAIL 1: fire_tp_cmp_005 first | 337 | - | 3784d0aadf31783512968a7b0b0be7ce |
| b2_cmp_zca_red_008 | FAIL 1: fire_tp_cmp_008 first | 337 | - | 2bc7bf46e5e1c853575b01d935894a5a |
| b2_cmp_zca_red_010 | FAIL 1: fire_tp_cmp_010 first | 337 | - | dc75d8284db4226f1f34b09def0395ed |
| b2_cmp_zca_red_011 | FAIL 1: fire_tp_cmp_011 first | 337 | - | 59fe9f788f842baff6d7e3c7fc0b4e00 |
| b2_cmp_zca_red_012 | FAIL 1: fire_tp_cmp_012 first | 337 | - | 371ee8d88cb22364746e7af603c48542 |
| b2_cmp_zca_red_014 | FAIL 1: fire_tp_cmp_014 first | 337 | - | 76c85ad3735d6c098e0d095b63936541 |
| b2_cmp_zca_red_016 | FAIL 1: fire_tp_cmp_016 first | 337 | - | 454f49b81f670940ad09aa8b281b80b0 |
| b2_cmp_zca_red_017 | FAIL 1: fire_tp_cmp_017 first | 337 | - | 570f3453986f7d6d99a900c52170eab7 |
| b2_cmp_zca_red_018 | FAIL 1: fire_tp_cmp_018 first | 337 | - | 3eff943c4754efdd779ba3c6c9533c96 |
| b2_cmp_zca_red_020 | FAIL 1: fire_tp_cmp_020 first | 337 | - | 710a635460f3ad5f44f055450a248834 |
| b2_cmp_zca_red_021 | FAIL 1: fire_tp_cmp_021 first | 337 | - | fe8c87ea64838abf545d069bfc280256 |
| b2_cmp_zca_red_023 | FAIL 1: fire_tp_cmp_023 first | 337 | - | dbf12ffbde36399d1762ac3aac0d10d9 |
| b2_cmp_zca_red_024 | FAIL 1: fire_tp_cmp_024 first | 337 | - | 75f191514ed7957d4d6c73ef6b8dee06 |
| b2_cmp_zca_red_026 | FAIL 1: fire_tp_cmp_026 first | 337 | - | ea79628c2cc51eca2c401b4bcb28dc8a |
| b2_cmp_zca_red_028 | FAIL 1: fire_tp_cmp_028 first | 337 | - | 4027184f2bb1dbf79086a4883be56a76 |
| b2_cmp_zca_red_030 | FAIL 1: fire_tp_cmp_030 first | 337 | - | c607ae26fc2083bd9217da5fb751498a |
| b2_cmp_zca_red_032 | FAIL 1: fire_tp_cmp_032 first | 337 | - | b16b2affb34acaa795082ce974a92e8a |
| b2_cmp_zca_red_033 | FAIL 1: fire_tp_cmp_033 first | 337 | - | 6afbfb3044545173bc5ee44eb7d7bf07 |
| b2_cmp_zca_s1 | PASS | 337 | 6 | abb4b727256d3d8d5416c088ba3a3ee3 |
| b2_cmp_zca_s2 | PASS | 337 | 8 | 8670e6cea43723186e4c6c31c56806de |
| b2_bit_ratified_red1 | FAIL 2: fire_tp_bit_014_ops first | 830 | - | ccc7db4ecf9a34c7735821119873acd9 |
| b2_bit_ratified_red_002 | FAIL 2: fire_tp_bit_002_ops first | 830 | - | 0bd1ad88ec09bd848ec99832b929f104 |
| b2_bit_ratified_red_003 | FAIL 2: fire_tp_bit_003_ops first | 830 | - | 993a6a907ecc12fd25f729bb734d069f |
| b2_bit_ratified_red_004 | FAIL 2: fire_tp_bit_004_ops first | 830 | - | b52f7ce96b70583c976cd5bdbe30e0e9 |
| b2_bit_ratified_red_005 | FAIL 2: fire_tp_bit_005_ops first | 830 | - | a98abaf4f86cf5a56c84f6fc1dad1c2d |
| b2_bit_ratified_red_006 | FAIL 2: fire_tp_bit_006_ops first | 830 | - | 2bf9012bc03673cdf99d07ba1dfd24b5 |
| b2_bit_ratified_red_007 | FAIL 2: fire_tp_bit_007_ops first | 830 | - | 4ba0f4c55148c3359e75ebe0bf2ad867 |
| b2_bit_ratified_red_008 | FAIL 2: fire_tp_bit_008_ops first | 830 | - | 74d7a8877bdfe6142a2a882c5bd14a31 |
| b2_bit_ratified_red_009 | FAIL 2: fire_tp_bit_009_ops first | 830 | - | 5d616f2d118a3de2e1951467c4676156 |
| b2_bit_ratified_red_010 | FAIL 2: fire_tp_bit_010_ops first | 830 | - | ba1121b0a8f8c8f63908faa30ce1dccb |
| b2_bit_ratified_red_014 | FAIL 2: fire_tp_bit_014_ops first | 830 | - | b3f8ac415f6d0c87c143011b8293eeed |
| b2_bit_ratified_red_015 | FAIL 1: fire_tp_bit_015_ops first | 830 | - | 07272b83e9888e505096f1ed724d1702 |
| b2_bit_ratified_red_017 | FAIL 2: fire_tp_bit_017_ops first | 830 | - | 56384ce6f95826ec8545df570d28f99a |
| b2_bit_ratified_red_018 | FAIL 1: fire_tp_bit_018_ops first | 830 | - | 6f0fd8f1aa7c555075d2a2e1500e75fc |
| b2_bit_ratified_red_019 | FAIL 2: fire_tp_bit_019_ops first | 830 | - | 0618f53391da277522dd73408f4d8339 |
| b2_bit_ratified_red_020 | FAIL 3: fire_tp_bit_020_ops first | 830 | - | b372f85a5f16ee1d76de23eea725d71e |
| b2_bit_ratified_red_021 | FAIL 1: fire_tp_bit_021_ops first | 830 | - | e3a6d4fb242d1059bedde59a1b69a775 |
| b2_bit_ratified_red_038 | FAIL 2: fire_tp_bit_038_ops first | 830 | - | 06af4a6a137cdaed25b3db2d169e2222 |
| b2_bit_ratified_red_040 | FAIL 2: fire_tp_bit_040_ops first | 830 | - | d4c8851f9d578a810ea4ee45ba2d557c |
| b2_bit_ratified_s1 | PASS | 830 | 0 | 9403c86595cb24721296f3a6799270a2 |
| b2_bit_ratified_s2 | PASS | 830 | 0 | 9858eabe33ac66aec898c38b78ba5699 |
| b2_isa_alu_red1 | FAIL 1: fire_tp_isa_002 first | 604 | - | 297aa9b767e31d72205f507ed3dbbb8f |
| b2_isa_alu_red1_001 | FAIL 1: fire_tp_isa_001 first | 604 | - | 8bb63232c61fdd5009c7edbe62c969d9 |
| b2_isa_alu_red1_002 | FAIL 1: fire_tp_isa_002 first | 604 | - | a2e29c1bf8b9669e79336cabe519430e |
| b2_isa_alu_red1_003 | FAIL 1: fire_tp_isa_003 first | 604 | - | b7ab608f27b14ab1c4000f39553d4145 |
| b2_isa_alu_red1_004 | FAIL 2: fire_tp_isa_004 first | 604 | - | 0c16bd33c56d31408fb9ca0f10da9131 |
| b2_isa_alu_red1_005 | FAIL 1: fire_tp_isa_005 first | 604 | - | fb7111e48d5ff7c53bdf609b533b040c |
| b2_isa_alu_red1_006 | FAIL 2: fire_tp_isa_006 first | 604 | - | 8a2f098f6268002e021630a10fe1d574 |
| b2_isa_alu_red1_007 | FAIL 1: fire_tp_isa_007 first | 604 | - | 7e6def9495e3e0df0c34e5856138acd3 |
| b2_isa_alu_red1_008 | FAIL 1: fire_tp_isa_008 first | 604 | - | 6b4aad5a5af74f4aed23a57917b6b4d2 |
| b2_isa_alu_red1_009 | FAIL 1: fire_tp_isa_009 first | 604 | - | e9eceb15ec12f50330faf8c3bfebdc65 |
| b2_isa_alu_red1_052 | FAIL 2: fire_tp_isa_052 first | 604 | - | ce7db23bdcf11fe7a411383e70f2e742 |
| b2_isa_alu_s1 | PASS | 604 | 0 | a7be2241f39983537a5e77221a18f0ad |
| b2_isa_alu_s2 | PASS | 604 | 0 | 6fc4cd85c4782d3fdf58852070bf32c9 |
| b2_isa_shift_red1 | FAIL 1: fire_tp_isa_010 first | 120 | - | 041ba5811a774db96f03fbde0eeb4ed4 |
| b2_isa_shift_red1_011 | FAIL 1: fire_tp_isa_011 first | 120 | - | 1e2456ea2a870b7e6226da46ce4bac12 |
| b2_isa_shift_red1_013 | FAIL 1: fire_tp_isa_013 first | 120 | - | cceb4658391bf9d5dc9b2da182dff1fc |
| b2_isa_shift_red1_014 | FAIL 1: fire_tp_isa_014 first | 120 | - | 60562b1fed204b6b9093d530b9feb5e1 |
| b2_isa_shift_s1 | PASS | 120 | 0 | a1c922fc9fa4a3ce3a035c2b1ef0c1ff |
| b2_isa_shift_s2 | PASS | 120 | 0 | a4aaff55b858f312cbd0881bb286b500 |
| b2_isa_cti_red1 | retained copy replaced by l9_isa_cti_red1 on out_head6 (Section 2b): FAIL: fire_tp_isa_017 first | 200 | 0 | 1ef859389b54b80494fa16afb569189e |
| b2_isa_cti_red1_015 | FAIL 1: fire_tp_isa_015 first | 200 | - | dd96eb649d8569abf842b4792dd9a781 |
| b2_isa_cti_red1_017 | FAIL 1: fire_tp_isa_017 first | 200 | - | ff81ba6f6e45733717b797c141fac442 |
| b2_isa_cti_red1_018 | FAIL 1: fire_tp_isa_018 first | 200 | - | 63cea270fa225f6c7d781a0dc8bb5f19 |
| b2_isa_cti_red1_019 | FAIL 1: fire_tp_isa_019 first | 200 | - | 3cee0a65b72ed1a0762b07633446b013 |
| b2_isa_cti_red1_020 | FAIL 1: fire_tp_isa_020 first | 200 | - | 1db4c55c837f3bf9a34f1b76ce5ec21f |
| b2_isa_cti_red1_023 | FAIL 1: fire_tp_isa_023 first | 200 | - | 90af28bb08a9aba88eaf854b1f5198d2 |
| b2_isa_cti_red1_027 | FAIL 1: fire_tp_isa_027 first | 200 | - | 3a0227ec4d7346de7798a2a31b86afe8 |
| b2_isa_cti_red1_053 | FAIL 1: fire_tp_isa_053 first | 200 | - | e81c3639b86ff603b11b1c66269bc00b |
| b2_isa_cti_s1 | PASS | 200 | 64 | c978e7edbf782f0fcce8268704badfc4 |
| b2_isa_cti_s2 | PASS | 200 | 64 | 55186e35c37a50ff689462936f6dafec |
| b2_mul_mul_red1 | FAIL 1: fire_tp_mul_002 first | 338 | - | 7c9d2c6b54ed28153d0f23f8554777e2 |
| b2_mul_mul_red_001 | FAIL 1: fire_tp_mul_001 first | 338 | - | 1e0a33ef0f2dfd5e6c651593da53c4c4 |
| b2_mul_mul_red_004 | FAIL 1: fire_tp_mul_004 first | 338 | - | d0400c893b92c966af94eee395c58feb |
| b2_mul_mul_red_005 | FAIL 1: fire_tp_mul_005 first | 338 | - | 76e8575fd055359c6d54e0ebe77d636c |
| b2_mul_mul_red_006 | FAIL 1: fire_tp_mul_006 first | 338 | - | 3e63cbe8765db6b834ac3b4ca9254501 |
| b2_mul_mul_red_007 | FAIL 1: fire_tp_mul_007 first | 338 | - | b10f3775a1bb8dddba32e1891209bded |
| b2_mul_mul_red_008 | FAIL 1: fire_tp_mul_008 first | 338 | - | 0a6094c46e87b8f238df1a1e5fe0e1e8 |
| b2_mul_mul_red_027 | FAIL 1: fire_tp_mul_027 first | 338 | - | 3a28285a7a8d1fa6bf6ab3e255cfccc3 |
| b2_mul_mul_s1 | PASS | 338 | 0 | 1f2ff7183c70bd48b72a7ba3779058ae |
| b2_mul_mul_s2 | PASS | 338 | 0 | 1d0a47bae41be2406953029feb7330cc |
| b2_mul_div_red1 | FAIL 1: fire_tp_mul_014 first | 224 | - | d3ac6386f9225ae8125d16d56cb46075 |
| b2_mul_div_red_013 | FAIL 1: fire_tp_mul_013 first | 224 | - | 253bab1f082334c864c836845de63b0d |
| b2_mul_div_red_015 | FAIL 1: fire_tp_mul_015 first | 224 | - | 7c51a9233f15713262bcc2f70f713418 |
| b2_mul_div_red_016 | FAIL 2: fire_tp_mul_016 first | 224 | - | 5266e89cdb265a273e0b61b2ae447d64 |
| b2_mul_div_red_017 | FAIL 2: fire_tp_mul_017 first | 224 | - | f63ab4a3aa8c2295d9038cf960a56862 |
| b2_mul_div_red_018 | FAIL 1: fire_tp_mul_018 first | 224 | - | 3d96337da45a21a4d3c1f7b2dde3b219 |
| b2_mul_div_red_019 | FAIL 1: fire_tp_mul_019 first | 224 | - | d2b719e4f7c62712aaabafbd53afdbca |
| b2_mul_div_red_020 | FAIL 1: fire_tp_mul_020 first | 224 | - | 57dbd9fdcc2a18731d9c374eb197a55f |
| b2_mul_div_red_021 | FAIL 1: fire_tp_mul_021 first | 224 | - | 6639e0e0780131cefdb181c52b710bb4 |
| b2_mul_div_red_026 | FAIL 1: fire_tp_mul_026 first | 224 | - | 2f9b5f5b8c21c6cc265fc799da9b976c |
| b2_mul_div_s1 | PASS | 224 | 0 | a47a954a78cfe798f8476dd52bcfd238 |
| b2_mul_div_s2 | PASS | 224 | 0 | e016aabf38cf1644100b0e3303e738df |

76 per-item red runs in total (one per built item: 21 + 18 + 10 + 4 + 8 + 8 + 10; earlier reports said 66 by mistake).
The excerpt copies start with the run header line (build, seed, module, image; LOG-034) followed by the decisive lines; the md5
cells above are of the excerpt copies as retained in landing 3e.

gen_test_mul_div's filler registers: landing 3d moved FILLER_REGS to x29..x31 and asserted them disjoint from OP_REGS, but the
filler templates still named x5..x7 (operand registers), so that fix did not touch the failing path (3d review high; the l7_mul_div_*
runs proved nothing about it and are dropped). Landing 3e derives the templates from FILLER_REGS and asserts at import that no filler
template names a register outside FILLER_REGS; the seed-1 and seed-2 programs carry 141 and 99 filler lines on x29..x31 and none on
x5..x7 (grep over gen_source.S for the filler forms); 30-seed generator sweep (plain, default red, every --red-item, flow-style without
PYTHONPATH): 660 of 660 OK. Re-run on out_head5 (TB sources equal HEAD; Python root head_export4) with the final template; these runs
supersede the b2_mul_div_* rows as proof of the program:

| Run | Result | GEN_TEST_BINS | UVM_ERROR | Verdict | md5 (stdout.log copy) |
|---|---|---|---|---|---|
| l8_mul_div_s1 | PASS | 224 | 0 | PASS | 2a036a5efe1de030dfd9f8156928e1d1 |
| l8_mul_div_s2 | PASS | 224 | 0 | PASS | 109873c80080823b75eb658e98504fb8 |
| l8_mul_div_red_014 | FAIL: fire_tp_mul_014 first | 224 | - | RED-OK | 84543ddfecec56d715361478e2a46a20 |

After the
WP-9 bins_not_hit change gen_test_isa_alu was re-run at seed 1 on the step-2b build with the committed 602-bin manifest:
out_head4/l5_isa_alu_s1 GEN_TEST_PASS, GEN_TEST_BINS n=602, UVM_ERROR 0 (retained in landing 3d as gen_l5_isa_alu_s1_stdout.log and _sim.log
with manifest rows; not in 69be96b; the 604-bin greens predate the change and are
superseded as proof of the manifest). Red runs print no UVM summary (the cocotb assertion ends the simulation before the UVM report); their sim.log copies are not
retained (decisive-log rule). Per-test details (clauses not asserted, dropped clauses with owners, assembler lessons such as GAS
widening compressed jumps, program sizes) are in each subagent's NOTES under dv/auto_dv/work/test-writer/batch2/<g>/ and in the
test docstrings.

## 2b. cmp_zca and isa_cti on the ce33b4f build (TB Infra follow-up landing 1: R10 shim mtval, R11 isa_pc_next bit-0 exception)

Build out_head6 (export of ce33b4f compiled locally; Python root the same export without dv/auto_dv/tests; a gen_test_boot_retire
green as canary), seed-1 images of Section 2 and the pinned reds regenerated from the committed generators (`--red --red-item`).
Both tests are UVM_ERROR-free now; the two retained pinned-red logs are replaced by these runs (same names, gen_b2_<group>_red1_*), so
`gen_flow_util.py --check-red-signatures` reads RED-OK for every red entry; the l9 greens are retained in full beside the Section 2 greens.

| Run (out_head6) | Retained as | Result | GEN_TEST_BINS | UVM_ERROR | Verdict | md5 (stdout copy) |
|---|---|---|---|---|---|---|
| l9_boot_green_s1 | gen_l9_boot_green_s1_stdout.log, _sim.log | PASS | 0 | 0 | PASS | 8462bc8578b193ea33615fc3a1ccfb1e |
| l9_cmp_zca_s1 | gen_l9_cmp_zca_s1_stdout.log, _sim.log | PASS | 337 | 0 | PASS | b892aae794fa1aac95b2663a2f2ffa36 |
| l9_cmp_zca_red1 | gen_b2_cmp_zca_red1_stdout.log, _verdict.txt | FAIL: fire_tp_cmp_005 first, no UVM_ERROR line | 337 | 0 | RED-OK | 8cca2bee47b3b402b274aa956852e8df |
| l9_isa_cti_s1 | gen_l9_isa_cti_s1_stdout.log, _sim.log | PASS | 200 | 0 | PASS | e5be6d61808d15a74ebc2059dec75842 |
| l9_isa_cti_red1 | gen_b2_isa_cti_red1_stdout.log, _verdict.txt | FAIL: fire_tp_isa_017 first, no UVM_ERROR line | 200 | 0 | RED-OK | 1ef859389b54b80494fa16afb569189e |

The gen_test_cmp_zca docstring now states both resolutions (the comparator counts rvfi_pc_wdata bit 0 as its documented exception,
B13's xfail item owns the bug; the model reports mtval 0 after c.ebreak like the DUT); the staged red entries read (RED-OK) again.

## 3. Findings for other roles

- TB Infra: shim mtval after c.ebreak (model = pc, Ibex 0); comparator isa_pc_next bit 0 on odd jalr/c.jr/c.jalr targets (B13 mask per TP-BTALU-008). Landed at ce33b4f (R10, R11): Section 2b.
- Rulings received (rtl-arch facts, DV Lead, Orchestrator): the cmp_zca expectation (mtval 0, mepc = pc on c.ebreak) is the RTL's
  behaviour and spec-legal, so the shim takes the Ibex view (TB Infra follow-up); the odd-jalr bit 0 is a real DUT defect of the
  RVFI-only class (rvfi_pc_wdata carries the raw odd target while the architectural state is even), bug candidate B13 owned by the
  expected-fail test gen_btalu_hazard_xfail, and the comparator masks bit 0 on jump-class records as a counted, documented exception;
  both tests stay as written (no masking on the test side) and are expected to pass once those rows land. Plan rulings folded in:
  TP-ISA-016/022/026 and TP-ISA-006's pc-region bins cite the plan request WP-9 (code windows at address 0 and the top page, a
  self-loop break command) as their not_built / bins_not_hit reason; TP-CMP-001's floor is >= 3000 retired per seed with the
  per-form floors governing.
- DV Lead: B13 ruling for the comparator; TP-ISA-016/022/026 need text near address 0 and in the top 2 KiB (gen_link.ld PROG window) and IRQ_SET codes; TP-ISA-006's cp_pc_region.high/low bins are unreachable in the memory map; TP-CMP-001's floor is >= 3000 retired per seed (about 3800 seen), the per-form floors governing.
- Subagent fence slips, recorded: the mul_mul subagent ran one read-only `git log -1` and a `find` that listed path names under dv/auto_dv/work/orchestrator and work/runtime (nothing read); the mul_div subagent listed the shared OUT directory and read 3 lines of a sibling run's sim.log (Test Writer work files).
