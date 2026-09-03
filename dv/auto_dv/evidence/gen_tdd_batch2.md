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
3c commits that file and the self-test is green on the committed tree from 3c on. Ordering: each red is `plan(seed, red=True, red_item)`
of the same generator (expectations asserted equal to the green plan), so red-ness does not depend on run order.

## 1. Summary

| Test | Items built | Bins | Seed 1 | Seed 2 | UVM_ERROR (s1/s2) | Default red pins | Per-item reds |
|---|---|---|---|---|---|---|---|
| gen_test_cmp_zca | 21 of 21 | 337 | PASS (reports 762) | PASS (reports 765) | 6/8 | TP-CMP-005 | 21, each tripping its item first |
| gen_test_bit_ratified | 18 of 19 (TP-BIT-001 not built: per-retirement rvfi_trap over the encoding table is an RVFI record fact; its U-mode leg leaves M-mode) | 830 | PASS (reports 685) | PASS (reports 679) | 0/0 | TP-BIT-014 | 18, each tripping its item first |
| gen_test_isa_alu | 10 of 10 | 604 | PASS (reports 6073) | PASS (reports 6069) | 0/0 | TP-ISA-002 | 10, each tripping its item first |
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

| Run | Result | GEN_TEST_BINS | UVM_ERROR | md5 (stdout.log) |
|---|---|---|---|---|
| b2_cmp_zca_red1 | FAIL 1: fire_tp_cmp_005 first | 337 | - | 215d863b984c9e32cd59f31c2bfd9514 |
| b2_cmp_zca_red_001 | FAIL 1: fire_tp_cmp_001 first | 337 | - | 835c1cbd14f8a8cd7ee503a0e79619b8 |
| b2_cmp_zca_red_002 | FAIL 1: fire_tp_cmp_002 first | 337 | - | 194bf709a6136243698503ec6ad279d7 |
| b2_cmp_zca_red_004 | FAIL 1: fire_tp_cmp_004 first | 337 | - | e741d783039bf0aee4e8fd07da07b32b |
| b2_cmp_zca_red_005 | FAIL 1: fire_tp_cmp_005 first | 337 | - | 8560271a2faa363ee781e3a1f9a532b1 |
| b2_cmp_zca_red_008 | FAIL 1: fire_tp_cmp_008 first | 337 | - | 7334563e97f3f96f50f6c198ca8b80ff |
| b2_cmp_zca_red_010 | FAIL 1: fire_tp_cmp_010 first | 337 | - | 9d071343bb73cd3b58843becec0f2bce |
| b2_cmp_zca_red_011 | FAIL 1: fire_tp_cmp_011 first | 337 | - | 15254317364fc3829dfaa60365af3ce6 |
| b2_cmp_zca_red_012 | FAIL 1: fire_tp_cmp_012 first | 337 | - | fea5acb0257b47f18f27b0b05e9c9496 |
| b2_cmp_zca_red_014 | FAIL 1: fire_tp_cmp_014 first | 337 | - | 803c529fa73f85363796a3abbdb845c8 |
| b2_cmp_zca_red_016 | FAIL 1: fire_tp_cmp_016 first | 337 | - | 96b3146f9999f7316e2383833b42a34d |
| b2_cmp_zca_red_017 | FAIL 1: fire_tp_cmp_017 first | 337 | - | 50a43ec80e85483edad313a5df713d38 |
| b2_cmp_zca_red_018 | FAIL 1: fire_tp_cmp_018 first | 337 | - | b3eed6401ab702260f3f017435e63d7d |
| b2_cmp_zca_red_020 | FAIL 1: fire_tp_cmp_020 first | 337 | - | a6e3d4cdd1fe2066cbfb533f2b032099 |
| b2_cmp_zca_red_021 | FAIL 1: fire_tp_cmp_021 first | 337 | - | 0045d6b509165bac9167bda22f914372 |
| b2_cmp_zca_red_023 | FAIL 1: fire_tp_cmp_023 first | 337 | - | 148fa684e17f83fc05fff6dec301241f |
| b2_cmp_zca_red_024 | FAIL 1: fire_tp_cmp_024 first | 337 | - | b347218a91c7fe809b2a7486a221e2cf |
| b2_cmp_zca_red_026 | FAIL 1: fire_tp_cmp_026 first | 337 | - | d619a7d99f3f700cf7ff3049024eaf19 |
| b2_cmp_zca_red_028 | FAIL 1: fire_tp_cmp_028 first | 337 | - | 82c8b00ba70ccec48547288acc01bbc5 |
| b2_cmp_zca_red_030 | FAIL 1: fire_tp_cmp_030 first | 337 | - | 91551c188ecea5131069b2963add8a8d |
| b2_cmp_zca_red_032 | FAIL 1: fire_tp_cmp_032 first | 337 | - | b90d4c7de6ca020c80d8877dffdba844 |
| b2_cmp_zca_red_033 | FAIL 1: fire_tp_cmp_033 first | 337 | - | 3694fecddcb971ab95a0ad631a6d64d6 |
| b2_cmp_zca_s1 | PASS | 337 | 6 | abb4b727256d3d8d5416c088ba3a3ee3 |
| b2_cmp_zca_s2 | PASS | 337 | 8 | 8670e6cea43723186e4c6c31c56806de |
| b2_bit_ratified_red1 | FAIL 2: fire_tp_bit_014_ops first | 830 | - | ccc7db4ecf9a34c7735821119873acd9 |
| b2_bit_ratified_red_002 | FAIL 2: fire_tp_bit_002_ops first | 830 | - | 62e420b22ceea36d4030100a42f8239a |
| b2_bit_ratified_red_003 | FAIL 2: fire_tp_bit_003_ops first | 830 | - | 6f70799ba7d64f38c4629fc2ca727857 |
| b2_bit_ratified_red_004 | FAIL 2: fire_tp_bit_004_ops first | 830 | - | 7dcd4c57e157b1587ad4d159ebf5129f |
| b2_bit_ratified_red_005 | FAIL 2: fire_tp_bit_005_ops first | 830 | - | 1b1c18e7a1c222dd6000c1f9df662ade |
| b2_bit_ratified_red_006 | FAIL 2: fire_tp_bit_006_ops first | 830 | - | cb48ef2a12e568ce4e474a136f2b4811 |
| b2_bit_ratified_red_007 | FAIL 2: fire_tp_bit_007_ops first | 830 | - | 381b0e42845fcf594a12af6c391f259e |
| b2_bit_ratified_red_008 | FAIL 2: fire_tp_bit_008_ops first | 830 | - | a11b5e69d3674c36098e7805df8c4335 |
| b2_bit_ratified_red_009 | FAIL 2: fire_tp_bit_009_ops first | 830 | - | b4af7a52d473a8c4a60e4964c335893d |
| b2_bit_ratified_red_010 | FAIL 2: fire_tp_bit_010_ops first | 830 | - | 08cc3ea7ab7e96bc56dd27ec00e37556 |
| b2_bit_ratified_red_014 | FAIL 2: fire_tp_bit_014_ops first | 830 | - | 054869b1071cd51b9496700ee52ef6b7 |
| b2_bit_ratified_red_015 | FAIL 1: fire_tp_bit_015_ops first | 830 | - | 6f70bc9581f0670f7128d9b83bcd2fb5 |
| b2_bit_ratified_red_017 | FAIL 2: fire_tp_bit_017_ops first | 830 | - | 8d104fd356b8dbfed62898aa257701c3 |
| b2_bit_ratified_red_018 | FAIL 1: fire_tp_bit_018_ops first | 830 | - | 7db0b7a3976e504221e468802fbcb2e3 |
| b2_bit_ratified_red_019 | FAIL 2: fire_tp_bit_019_ops first | 830 | - | b20822c4d3d8f37df365d15cd1c88b8c |
| b2_bit_ratified_red_020 | FAIL 3: fire_tp_bit_020_ops first | 830 | - | 88a20152edac4077ea744ca711d7b1ec |
| b2_bit_ratified_red_021 | FAIL 1: fire_tp_bit_021_ops first | 830 | - | 97fa6586e31cc9e821a5fd2bc9bedce2 |
| b2_bit_ratified_red_038 | FAIL 2: fire_tp_bit_038_ops first | 830 | - | 27ae89c171d74a0b0888d3facf8223c8 |
| b2_bit_ratified_red_040 | FAIL 2: fire_tp_bit_040_ops first | 830 | - | bfd2e600f47295dea9508a0c4fc9e5c8 |
| b2_bit_ratified_s1 | PASS | 830 | 0 | 9403c86595cb24721296f3a6799270a2 |
| b2_bit_ratified_s2 | PASS | 830 | 0 | 9858eabe33ac66aec898c38b78ba5699 |
| b2_isa_alu_red1 | FAIL 1: fire_tp_isa_002 first | 604 | - | 297aa9b767e31d72205f507ed3dbbb8f |
| b2_isa_alu_red1_001 | FAIL 1: fire_tp_isa_001 first | 604 | - | dfb3a93caca3c14a74ae4c40e20cb9ec |
| b2_isa_alu_red1_002 | FAIL 1: fire_tp_isa_002 first | 604 | - | 8c505dc90e3c31356b978074ce4479b3 |
| b2_isa_alu_red1_003 | FAIL 1: fire_tp_isa_003 first | 604 | - | d4b0b54b4044f290ecd9909c7aac47e7 |
| b2_isa_alu_red1_004 | FAIL 2: fire_tp_isa_004 first | 604 | - | abb0587ed46f6925080aeff12116ed46 |
| b2_isa_alu_red1_005 | FAIL 1: fire_tp_isa_005 first | 604 | - | 2a67df66df548943dd7c71e6801d2320 |
| b2_isa_alu_red1_006 | FAIL 2: fire_tp_isa_006 first | 604 | - | cce054c58ea0d905e5a71352b5096de6 |
| b2_isa_alu_red1_007 | FAIL 1: fire_tp_isa_007 first | 604 | - | 7279297b27790fd9b8236148f67f783d |
| b2_isa_alu_red1_008 | FAIL 1: fire_tp_isa_008 first | 604 | - | 2c58b9ed570bb37fd1de3a4dd6a3f537 |
| b2_isa_alu_red1_009 | FAIL 1: fire_tp_isa_009 first | 604 | - | 49ccbac2d32dfc4f86cce74fb6d4aa1f |
| b2_isa_alu_red1_052 | FAIL 2: fire_tp_isa_052 first | 604 | - | 205f4dd4a8187b830e6e13dfd13d5a9a |
| b2_isa_alu_s1 | PASS | 604 | 0 | a7be2241f39983537a5e77221a18f0ad |
| b2_isa_alu_s2 | PASS | 604 | 0 | 6fc4cd85c4782d3fdf58852070bf32c9 |
| b2_isa_shift_red1 | FAIL 1: fire_tp_isa_010 first | 120 | - | 041ba5811a774db96f03fbde0eeb4ed4 |
| b2_isa_shift_red1_011 | FAIL 1: fire_tp_isa_011 first | 120 | - | c044cc2806d8ba39812a890678f0edb6 |
| b2_isa_shift_red1_013 | FAIL 1: fire_tp_isa_013 first | 120 | - | aa825f385989d87a1a2f6ea168dfde3d |
| b2_isa_shift_red1_014 | FAIL 1: fire_tp_isa_014 first | 120 | - | 41b50dadc8b82090c5c97999a0576b2d |
| b2_isa_shift_s1 | PASS | 120 | 0 | a1c922fc9fa4a3ce3a035c2b1ef0c1ff |
| b2_isa_shift_s2 | PASS | 120 | 0 | a4aaff55b858f312cbd0881bb286b500 |
| b2_isa_cti_red1 | FAIL 1: fire_tp_isa_017 first | 200 | - | 51a0da9355acc1ce81445a525d48f10c |
| b2_isa_cti_red1_015 | FAIL 1: fire_tp_isa_015 first | 200 | - | d24d412352c16ab6ff24bfdd23fd56b9 |
| b2_isa_cti_red1_017 | FAIL 1: fire_tp_isa_017 first | 200 | - | 72d3f313371f5555bc8b006feb13fe58 |
| b2_isa_cti_red1_018 | FAIL 1: fire_tp_isa_018 first | 200 | - | d7f52a16c57a9cac1fd62c6b5edf71f6 |
| b2_isa_cti_red1_019 | FAIL 1: fire_tp_isa_019 first | 200 | - | 1dac1a12e48529aeddacf4861d661d7e |
| b2_isa_cti_red1_020 | FAIL 1: fire_tp_isa_020 first | 200 | - | 61b7375e6d3d7499d59a291186344b0b |
| b2_isa_cti_red1_023 | FAIL 1: fire_tp_isa_023 first | 200 | - | 328b7990c0c905a5020c510b8a8ac54f |
| b2_isa_cti_red1_027 | FAIL 1: fire_tp_isa_027 first | 200 | - | 6f91e1a075c030bfedf38f6fabab4408 |
| b2_isa_cti_red1_053 | FAIL 1: fire_tp_isa_053 first | 200 | - | ae1422dd4e6284672a932ec823fdaad0 |
| b2_isa_cti_s1 | PASS | 200 | 64 | c978e7edbf782f0fcce8268704badfc4 |
| b2_isa_cti_s2 | PASS | 200 | 64 | 55186e35c37a50ff689462936f6dafec |
| b2_mul_mul_red1 | FAIL 1: fire_tp_mul_002 first | 338 | - | 7c9d2c6b54ed28153d0f23f8554777e2 |
| b2_mul_mul_red_001 | FAIL 1: fire_tp_mul_001 first | 338 | - | 9934c46861bfaeba2f5e95240d4976cb |
| b2_mul_mul_red_004 | FAIL 1: fire_tp_mul_004 first | 338 | - | cc3bda4d79ae6dee05b3f44bedf7d9f4 |
| b2_mul_mul_red_005 | FAIL 1: fire_tp_mul_005 first | 338 | - | e5f1c1cb80112d4a363d58258ff60ce5 |
| b2_mul_mul_red_006 | FAIL 1: fire_tp_mul_006 first | 338 | - | 28f77e55df1579ea68ce13611497a78e |
| b2_mul_mul_red_007 | FAIL 1: fire_tp_mul_007 first | 338 | - | d8aca92182f027fbab15db13f22059b2 |
| b2_mul_mul_red_008 | FAIL 1: fire_tp_mul_008 first | 338 | - | 12d1d972ffbc58e322ac526f3be22bb2 |
| b2_mul_mul_red_027 | FAIL 1: fire_tp_mul_027 first | 338 | - | ad16a5b23df916a462b75755d8df968a |
| b2_mul_mul_s1 | PASS | 338 | 0 | 1f2ff7183c70bd48b72a7ba3779058ae |
| b2_mul_mul_s2 | PASS | 338 | 0 | 1d0a47bae41be2406953029feb7330cc |
| b2_mul_div_red1 | FAIL 1: fire_tp_mul_014 first | 224 | - | d3ac6386f9225ae8125d16d56cb46075 |
| b2_mul_div_red_013 | FAIL 1: fire_tp_mul_013 first | 224 | - | 7b2289dece9b53d8d0e273eaaf70f35d |
| b2_mul_div_red_015 | FAIL 1: fire_tp_mul_015 first | 224 | - | a2fa148d995f9466a9e019dc2527e9f8 |
| b2_mul_div_red_016 | FAIL 2: fire_tp_mul_016 first | 224 | - | 3f8c41673642a4f279c49d29bc0055a3 |
| b2_mul_div_red_017 | FAIL 2: fire_tp_mul_017 first | 224 | - | a8f711354a116a8a38316750bddbf7fb |
| b2_mul_div_red_018 | FAIL 1: fire_tp_mul_018 first | 224 | - | 2feed800a764f5c48938ef9f8962f35b |
| b2_mul_div_red_019 | FAIL 1: fire_tp_mul_019 first | 224 | - | dc40d726295c52f323dac59dad2628a3 |
| b2_mul_div_red_020 | FAIL 1: fire_tp_mul_020 first | 224 | - | faaae5a8c193514684fb725a848458d5 |
| b2_mul_div_red_021 | FAIL 1: fire_tp_mul_021 first | 224 | - | c75e66ce316c395fa210bfd968030b85 |
| b2_mul_div_red_026 | FAIL 1: fire_tp_mul_026 first | 224 | - | 6e67b910e60ba891f6d1ef4fbf764104 |
| b2_mul_div_s1 | PASS | 224 | 0 | a47a954a78cfe798f8476dd52bcfd238 |
| b2_mul_div_s2 | PASS | 224 | 0 | e016aabf38cf1644100b0e3303e738df |

76 per-item red runs in total (one per built item: 21 + 18 + 10 + 4 + 8 + 8 + 10; earlier reports said 66 by mistake). After the
WP-9 bins_not_hit change gen_test_isa_alu was re-run at seed 1 on the step-2b build with the committed 602-bin manifest:
out_head4/l5_isa_alu_s1 GEN_TEST_PASS, GEN_TEST_BINS n=602, UVM_ERROR 0 (retained; the 604-bin greens predate the change and are
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
- DV Lead: B13 ruling for the comparator; TP-ISA-016/022/026 need text near address 0 and in the top 2 KiB (gen_link.ld PROG window) and IRQ_SET codes; TP-ISA-006's cp_pc_region.high/low bins are unreachable in the memory map; TP-CMP-001's >= 5000-instruction stimulus not met (about 3800 retired).
- Subagent fence slips, recorded: the mul_mul subagent ran one read-only `git log -1` and a `find` that listed path names under dv/auto_dv/work/orchestrator and work/runtime (nothing read); the mul_div subagent listed the shared OUT directory and read 3 lines of a sibling run's sim.log (Test Writer work files).
