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
architectural behaviour; their flow verdicts FAIL through uvm_error until the TB rows are fixed or ruled.

## 2. Runs (out_head3/<dir>; committed copies gen_tdd_logs/test_writer/gen_<dir>_stdout.log for s1, s2 and the default red, gen_<dir>_stdout_excerpt.log (decisive lines) for the per-item reds)

| Run | Result | GEN_TEST_BINS | UVM_ERROR | md5 of the retained copy (stdout.log; stdout_excerpt.log for the per-item reds) |
|---|---|---|---|---|
| b2_cmp_zca_red1 | FAIL 1: fire_tp_cmp_005 first | 337 | - | 215d863b984c9e32cd59f31c2bfd9514 |
| b2_cmp_zca_red_001 | FAIL 1: fire_tp_cmp_001 first | 337 | - | 63bca0fb7283e8d98df47c1e0367fb9f |
| b2_cmp_zca_red_002 | FAIL 1: fire_tp_cmp_002 first | 337 | - | 6cb93d57847314383b829cfd501de009 |
| b2_cmp_zca_red_004 | FAIL 1: fire_tp_cmp_004 first | 337 | - | b5836dea5792b6cbdd471d79bdc47b7f |
| b2_cmp_zca_red_005 | FAIL 1: fire_tp_cmp_005 first | 337 | - | 26a615e2d07f29fa82b39742f73ca1c4 |
| b2_cmp_zca_red_008 | FAIL 1: fire_tp_cmp_008 first | 337 | - | fd9cc78990d69d0ece5aae67f4b68619 |
| b2_cmp_zca_red_010 | FAIL 1: fire_tp_cmp_010 first | 337 | - | 3fa65ce2c2674fb7b0d53bf31a58e790 |
| b2_cmp_zca_red_011 | FAIL 1: fire_tp_cmp_011 first | 337 | - | 3d535b94e2bb0de06f7af310467d3ad7 |
| b2_cmp_zca_red_012 | FAIL 1: fire_tp_cmp_012 first | 337 | - | aac5c0dfdaf110aff36d0e0d5dea834f |
| b2_cmp_zca_red_014 | FAIL 1: fire_tp_cmp_014 first | 337 | - | e73202db8bcdc1bd1bc199d11077ac94 |
| b2_cmp_zca_red_016 | FAIL 1: fire_tp_cmp_016 first | 337 | - | 274f97f90e36b4374d8d7d55fc2bd37c |
| b2_cmp_zca_red_017 | FAIL 1: fire_tp_cmp_017 first | 337 | - | 2dd51d21d80703286b33fa28c874318b |
| b2_cmp_zca_red_018 | FAIL 1: fire_tp_cmp_018 first | 337 | - | 02123591bbd28577679c64ec99ceb600 |
| b2_cmp_zca_red_020 | FAIL 1: fire_tp_cmp_020 first | 337 | - | b0b7dbb31a0f28c16150a4ca3239f940 |
| b2_cmp_zca_red_021 | FAIL 1: fire_tp_cmp_021 first | 337 | - | 74b5f9b7fc35ae948e146323103a48a6 |
| b2_cmp_zca_red_023 | FAIL 1: fire_tp_cmp_023 first | 337 | - | 414623c118f4d94589da1181d340c76a |
| b2_cmp_zca_red_024 | FAIL 1: fire_tp_cmp_024 first | 337 | - | a68c49bccfb3d5ba011218108b56baad |
| b2_cmp_zca_red_026 | FAIL 1: fire_tp_cmp_026 first | 337 | - | 1c3192e02d01aa790a357565e81eb446 |
| b2_cmp_zca_red_028 | FAIL 1: fire_tp_cmp_028 first | 337 | - | bd19fc16435b512ceec70429f367ddcb |
| b2_cmp_zca_red_030 | FAIL 1: fire_tp_cmp_030 first | 337 | - | 300218e4e7d58791da58370915e0e03f |
| b2_cmp_zca_red_032 | FAIL 1: fire_tp_cmp_032 first | 337 | - | ac11d47420ec38fd9b8a7a73fd89c3a5 |
| b2_cmp_zca_red_033 | FAIL 1: fire_tp_cmp_033 first | 337 | - | 1c40b93f99c74b7e23bd8f6d3a135a5f |
| b2_cmp_zca_s1 | PASS | 337 | 6 | abb4b727256d3d8d5416c088ba3a3ee3 |
| b2_cmp_zca_s2 | PASS | 337 | 8 | 8670e6cea43723186e4c6c31c56806de |
| b2_bit_ratified_red1 | FAIL 2: fire_tp_bit_014_ops first | 830 | - | ccc7db4ecf9a34c7735821119873acd9 |
| b2_bit_ratified_red_002 | FAIL 2: fire_tp_bit_002_ops first | 830 | - | fd5f6ba4ca0c024fa6e4a4afb0fe886a |
| b2_bit_ratified_red_003 | FAIL 2: fire_tp_bit_003_ops first | 830 | - | c91092f10f9e6749b4b891a8cd3dca1f |
| b2_bit_ratified_red_004 | FAIL 2: fire_tp_bit_004_ops first | 830 | - | 2e2c4302e4b6b889f864a1ceff77c453 |
| b2_bit_ratified_red_005 | FAIL 2: fire_tp_bit_005_ops first | 830 | - | b6e2b4187d756b33739c519cef528087 |
| b2_bit_ratified_red_006 | FAIL 2: fire_tp_bit_006_ops first | 830 | - | 103cd06b1e702f4e649ebe6108a27df3 |
| b2_bit_ratified_red_007 | FAIL 2: fire_tp_bit_007_ops first | 830 | - | 9c9c4b9091055eabb23569cf14b216f6 |
| b2_bit_ratified_red_008 | FAIL 2: fire_tp_bit_008_ops first | 830 | - | d76e14c7bf8b1e2959ca5ceae86ecec6 |
| b2_bit_ratified_red_009 | FAIL 2: fire_tp_bit_009_ops first | 830 | - | a2fb77129b4ef471710de917e0280181 |
| b2_bit_ratified_red_010 | FAIL 2: fire_tp_bit_010_ops first | 830 | - | 38d4d48c36b6a00585e69e8fb3807554 |
| b2_bit_ratified_red_014 | FAIL 2: fire_tp_bit_014_ops first | 830 | - | c62ab78674e8e9daeccd6700adad37f7 |
| b2_bit_ratified_red_015 | FAIL 1: fire_tp_bit_015_ops first | 830 | - | 5124cc5057392f060aa37d22a245d405 |
| b2_bit_ratified_red_017 | FAIL 2: fire_tp_bit_017_ops first | 830 | - | c7bf939c54ae830956fa23b2d1e408ff |
| b2_bit_ratified_red_018 | FAIL 1: fire_tp_bit_018_ops first | 830 | - | ff4bbfcba18c900ce3ae41df200f2461 |
| b2_bit_ratified_red_019 | FAIL 2: fire_tp_bit_019_ops first | 830 | - | 94d45ed85df1259d43c933c20e2b4eef |
| b2_bit_ratified_red_020 | FAIL 3: fire_tp_bit_020_ops first | 830 | - | 30aeb3badc94103547cf41d118759302 |
| b2_bit_ratified_red_021 | FAIL 1: fire_tp_bit_021_ops first | 830 | - | b840c2bc34419a53206195d46f3fa1a8 |
| b2_bit_ratified_red_038 | FAIL 2: fire_tp_bit_038_ops first | 830 | - | 67f9106030550f66717ff4d66f1a5b43 |
| b2_bit_ratified_red_040 | FAIL 2: fire_tp_bit_040_ops first | 830 | - | c327040808fd90a63d6e7d8c058c3428 |
| b2_bit_ratified_s1 | PASS | 830 | 0 | 9403c86595cb24721296f3a6799270a2 |
| b2_bit_ratified_s2 | PASS | 830 | 0 | 9858eabe33ac66aec898c38b78ba5699 |
| b2_isa_alu_red1 | FAIL 1: fire_tp_isa_002 first | 604 | - | 297aa9b767e31d72205f507ed3dbbb8f |
| b2_isa_alu_red1_001 | FAIL 1: fire_tp_isa_001 first | 604 | - | 94a9b7e880659d695af8beb389fb56e3 |
| b2_isa_alu_red1_002 | FAIL 1: fire_tp_isa_002 first | 604 | - | 6e5faff257e75ad94dfbcdea58058181 |
| b2_isa_alu_red1_003 | FAIL 1: fire_tp_isa_003 first | 604 | - | 351620e730ba097da604dfad9b91bddc |
| b2_isa_alu_red1_004 | FAIL 2: fire_tp_isa_004 first | 604 | - | 222007c817a3cea641bcdbbe61539f61 |
| b2_isa_alu_red1_005 | FAIL 1: fire_tp_isa_005 first | 604 | - | 903e734f921bdf569851978255845713 |
| b2_isa_alu_red1_006 | FAIL 2: fire_tp_isa_006 first | 604 | - | 7dc0f3fcf96a59aa60216c35a1d98591 |
| b2_isa_alu_red1_007 | FAIL 1: fire_tp_isa_007 first | 604 | - | 4c16f934661fadfd8abff2d74fb96287 |
| b2_isa_alu_red1_008 | FAIL 1: fire_tp_isa_008 first | 604 | - | 1a101e8d4452e273f1af04bb63db9556 |
| b2_isa_alu_red1_009 | FAIL 1: fire_tp_isa_009 first | 604 | - | 3182a820c7c520899ab4ce4d062a9f2f |
| b2_isa_alu_red1_052 | FAIL 2: fire_tp_isa_052 first | 604 | - | bc8b666eb01bb8460562c3684ea98763 |
| b2_isa_alu_s1 | PASS | 604 | 0 | a7be2241f39983537a5e77221a18f0ad |
| b2_isa_alu_s2 | PASS | 604 | 0 | 6fc4cd85c4782d3fdf58852070bf32c9 |
| b2_isa_shift_red1 | FAIL 1: fire_tp_isa_010 first | 120 | - | 041ba5811a774db96f03fbde0eeb4ed4 |
| b2_isa_shift_red1_011 | FAIL 1: fire_tp_isa_011 first | 120 | - | 7dfa15f168919bc462eaf52c2f14707a |
| b2_isa_shift_red1_013 | FAIL 1: fire_tp_isa_013 first | 120 | - | 18716cb21cf5e92750766d1d00649d3c |
| b2_isa_shift_red1_014 | FAIL 1: fire_tp_isa_014 first | 120 | - | a7ce7c2f88dd9134d9aa7032bcf898a4 |
| b2_isa_shift_s1 | PASS | 120 | 0 | a1c922fc9fa4a3ce3a035c2b1ef0c1ff |
| b2_isa_shift_s2 | PASS | 120 | 0 | a4aaff55b858f312cbd0881bb286b500 |
| b2_isa_cti_red1 | FAIL 1: fire_tp_isa_017 first | 200 | - | 51a0da9355acc1ce81445a525d48f10c |
| b2_isa_cti_red1_015 | FAIL 1: fire_tp_isa_015 first | 200 | - | 5a44a78d84e930381877da94be810040 |
| b2_isa_cti_red1_017 | FAIL 1: fire_tp_isa_017 first | 200 | - | 64c1fd64823c5d3b94bad3f95e000e9b |
| b2_isa_cti_red1_018 | FAIL 1: fire_tp_isa_018 first | 200 | - | a1bc7897e63a8a80ecb4b223eda6497d |
| b2_isa_cti_red1_019 | FAIL 1: fire_tp_isa_019 first | 200 | - | 4dd2fc7ffe1b686f37645211af4b726c |
| b2_isa_cti_red1_020 | FAIL 1: fire_tp_isa_020 first | 200 | - | 92927a810b1f6d96dabb8a506ca8caf0 |
| b2_isa_cti_red1_023 | FAIL 1: fire_tp_isa_023 first | 200 | - | 8ee4b2f61acea418428ff448bd22333a |
| b2_isa_cti_red1_027 | FAIL 1: fire_tp_isa_027 first | 200 | - | 10ed279d7722d66d0927388ae6a0c191 |
| b2_isa_cti_red1_053 | FAIL 1: fire_tp_isa_053 first | 200 | - | d69f687ab95c70050c2fd7482e32fa56 |
| b2_isa_cti_s1 | PASS | 200 | 64 | c978e7edbf782f0fcce8268704badfc4 |
| b2_isa_cti_s2 | PASS | 200 | 64 | 55186e35c37a50ff689462936f6dafec |
| b2_mul_mul_red1 | FAIL 1: fire_tp_mul_002 first | 338 | - | 7c9d2c6b54ed28153d0f23f8554777e2 |
| b2_mul_mul_red_001 | FAIL 1: fire_tp_mul_001 first | 338 | - | ea6196f47be8641ef8734ac0bf0c3c35 |
| b2_mul_mul_red_004 | FAIL 1: fire_tp_mul_004 first | 338 | - | f2e589e99648c024de81d475ab624fe8 |
| b2_mul_mul_red_005 | FAIL 1: fire_tp_mul_005 first | 338 | - | 0372e411c44d93118a0547442a57d909 |
| b2_mul_mul_red_006 | FAIL 1: fire_tp_mul_006 first | 338 | - | d3f9219852228b97b68072aaed5e23f5 |
| b2_mul_mul_red_007 | FAIL 1: fire_tp_mul_007 first | 338 | - | 997576ccac47778ae5c1f139d1df397e |
| b2_mul_mul_red_008 | FAIL 1: fire_tp_mul_008 first | 338 | - | 57f5163f92be4402cf6f7d3000004506 |
| b2_mul_mul_red_027 | FAIL 1: fire_tp_mul_027 first | 338 | - | a14167444939a82893808da627694c55 |
| b2_mul_mul_s1 | PASS | 338 | 0 | 1f2ff7183c70bd48b72a7ba3779058ae |
| b2_mul_mul_s2 | PASS | 338 | 0 | 1d0a47bae41be2406953029feb7330cc |
| b2_mul_div_red1 | FAIL 1: fire_tp_mul_014 first | 224 | - | d3ac6386f9225ae8125d16d56cb46075 |
| b2_mul_div_red_013 | FAIL 1: fire_tp_mul_013 first | 224 | - | a64d155e319eef5772ad2a9487c5c54b |
| b2_mul_div_red_015 | FAIL 1: fire_tp_mul_015 first | 224 | - | 8c313f1bf370afe6f5f4176189391982 |
| b2_mul_div_red_016 | FAIL 2: fire_tp_mul_016 first | 224 | - | b5bb2c1104b865715569ee76cc8d530e |
| b2_mul_div_red_017 | FAIL 2: fire_tp_mul_017 first | 224 | - | ecf5228a384b5eb5df1c867fffdb5268 |
| b2_mul_div_red_018 | FAIL 1: fire_tp_mul_018 first | 224 | - | 5be0ad944024d69a80297b2059608b82 |
| b2_mul_div_red_019 | FAIL 1: fire_tp_mul_019 first | 224 | - | 679f0978c57bdd32b9577a4769bb3f89 |
| b2_mul_div_red_020 | FAIL 1: fire_tp_mul_020 first | 224 | - | 5de6e6f68f3fd63301e59653dccd75e8 |
| b2_mul_div_red_021 | FAIL 1: fire_tp_mul_021 first | 224 | - | 21d14d0d43aa8d1c530f234c5705f52a |
| b2_mul_div_red_026 | FAIL 1: fire_tp_mul_026 first | 224 | - | 5a198e759b5b4c2a6c067a7fd5905f8b |
| b2_mul_div_s1 | PASS | 224 | 0 | a47a954a78cfe798f8476dd52bcfd238 |
| b2_mul_div_s2 | PASS | 224 | 0 | e016aabf38cf1644100b0e3303e738df |

76 per-item red runs in total (one per built item: 21 + 18 + 10 + 4 + 8 + 8 + 10; earlier reports said 66 by mistake).

gen_test_mul_div was re-generated after the Critic's L-8 (filler registers x29..x31 outside the operand set, asserted disjoint) and
re-run on the step-2b build out_head4 with the final template; these runs supersede the b2_mul_div_* rows as proof of the program
(30-seed generator sweep clean):

| Run | Result | GEN_TEST_BINS | UVM_ERROR | md5 (stdout.log) |
|---|---|---|---|---|
| l7_mul_div_s1 | PASS | 224 | 0 | 7675a70562d7803a1464c19eaaa21a6c |
| l7_mul_div_s2 | PASS | 224 | 0 | c24f1353ccf39a08ca52d595391133dd |
| l7_mul_div_red_014 | FAIL: fire_tp_mul_014 first | 224 | - | e670e6f4b0ba049cda8485dbcbebe16c | After the
WP-9 bins_not_hit change gen_test_isa_alu was re-run at seed 1 on the step-2b build with the committed 602-bin manifest:
out_head4/l5_isa_alu_s1 GEN_TEST_PASS, GEN_TEST_BINS n=602, UVM_ERROR 0 (retained in landing 3d as gen_l5_isa_alu_s1_stdout.log and _sim.log
with manifest rows; not in 69be96b; the 604-bin greens predate the change and are
superseded as proof of the manifest). Red runs print no UVM summary (the cocotb assertion ends the simulation before the UVM report); their sim.log copies are not
retained (decisive-log rule). Per-test details (clauses not asserted, dropped clauses with owners, assembler lessons such as GAS
widening compressed jumps, program sizes) are in each subagent's NOTES under dv/auto_dv/work/test-writer/batch2/<g>/ and in the
test docstrings.

## 3. Findings for other roles

- TB Infra: shim mtval after c.ebreak (model = pc, Ibex 0); comparator isa_pc_next bit 0 on odd jalr/c.jr/c.jalr targets (B13 mask per TP-BTALU-008).
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
