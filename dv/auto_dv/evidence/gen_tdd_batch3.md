# TDD transcript: Phase 1 batch 3, group gen_pmp_mseccfg (the second PMP WARL group; gen_pmp_lock follows in its own section when it lands)

Test Writer, 2026-09-03. One unnamed subagent (dispatched by the previous Test Writer instance, brief
dv/auto_dv/work/test-writer/batch3/gen_pmp_mseccfg/BRIEF.md over gen_subagent_brief.md v3) wrote dv/auto_dv/tests/gen_test_pmp_mseccfg.py,
dv/auto_dv/tests/gen_programs/gen_pmp_mseccfg_prog.py and rendered dv/auto_dv/fcov_expectations/gen_test_pmp_mseccfg.fcov.yaml from the
module; its own runs (out_head7, an export of 1cbbcfc, on the pre-3h template) are superseded by the runs below and not retained. The Test
Writer changed the delivery in one respect, the Orchestrator's ruling for batch 3: TP-PMP-108 stays not_built (the plan's state-machine walk
restarts from a wrapper reset to revisit the low states and asserts all 8 states per seed; the bridge has no reset command), so the
delivered reduced walk with nine bins_not_hit transitions became `not_built = {"TP-PMP-108": ...}`, fire_tp_pmp_108 and the bins_not_hit
entries were removed, and the manifest was re-rendered (112 bins with 9 not_hit -> 77 bins, 0 not_hit, the not_built header line). The
program keeps the per-seed walk as stimulus: its mseccfg read-backs are checked in lock-step by gen_isa_compare but credit no item. The TB
ask (a mid-run reset command on the bridge) is filed with tb-infra (Section 3).

Every run below was made through dv/auto_dv/tests/gen_fixtures/gen_run_fixture.sh against out_head8 (export of HEAD 9e7c440 with the landing-3h
template; sources sha 156eb9357b79552e; the TB sources equal HEAD's) with GEN_TB_PYROOT = the export carrying the patched test and the
re-rendered manifest, no GEN_TEST_STAGED_ENTRIES. Verified by the Test Writer on the export: py_compile, the library self-test (structure
check: not_built two-sided against the 13-item group, fire_tp-called and item-naming rules, flow-style generator runs) with the new module
present, the same self-test with GEN_TEST_STAGED_ENTRIES naming the staged entries (the red entry's red_expect against the retained pinned
red through the flow's red_signature_check), ASCII, the manifest unchanged by a --test-module re-render, every run directory re-read.
Generator sweep by the subagent: 30 seeds x (plain, --red, 13 --red-item) = 450 runs, 0 failures (batch3/gen_pmp_mseccfg/sweep.log).
Ordering: each red is `plan(seed, red=True, red_item)` of the same generator with the green expectations kept, so red-ness does not depend
on run order; the seed-drawn red (`--red` alone) drew TP-PMP-012 at seed 1.

## 1. Summary

| Test | Items built | Bins | Seed 1 | Seed 2 | Seed 3 | UVM_ERROR (s1/s2/s3) | Pinned red | Per-item reds |
|---|---|---|---|---|---|---|---|---|
| gen_test_pmp_mseccfg | 12 of 13 (TP-PMP-108 not built: wrapper-reset walk, no reset command on the bridge) | 77 | PASS (reports 175) | PASS (reports 193) | PASS (reports 191) | 0/0/0 | TP-PMP-011 | 12, each tripping its item alone |

Knobs: the items name knob:instr_mix csr_heavy and (031) knob:pmp_regime mml_on, both program-side (gen_tb_knobs.yaml
regime_set_consumer: program): the program is CSR-heavy and sets MML itself; the test declares `schedulable = lib.TIMING_ONLY_KNOBS`. Seed 3's
schedule reached 12 of 12 entries with 6 mid-run phases applied (k=3 at seeds 2 and 3; seed 2's nine later entries fall after the end of
test at cycle 7390), so the group has run under mid-run regime changes on the fixed runner. Checkers: gen_chk_csr_readback and gen_chk_pmp
are UNBUILT (plan Section 0a), so every read-back and every U-mode probe outcome is a report word compared by the fire_tp method against the
generator's PmpModel (the single source), as in gen_test_pmp_csr_warl; gen_isa_compare is the always-on cross-check (UVM_ERROR 0).

## 2. Runs (out_head8/b3_mseccfg_<run>; committed copies gen_tdd_logs/test_writer/gen_b3_pmp_mseccfg_<run>_stdout.log and _sim.log for s1..s3, gen_pmp_mseccfg_red1_stdout.log and _sim.log for the pinned red, gen_b3_pmp_mseccfg_red_<nnn>_stdout_excerpt.log for the other reds; run header first, with the build's sources sha)

| Run | Result | GEN_TEST_BINS | UVM_ERROR | reports | retired | EOT cycle | walk path | fire_schedule_applied | md5 (gen_b3_pmp_mseccfg_<run>_stdout.log) |
|---|---|---|---|---|---|---|---|---|---|
| b3_mseccfg_s1 | PASS | 77 | 0 | 175 | 840 | 6216 | mml_first_rlb | ok=True reached 6 of 6, applied 6 (0 idx>0 phases) | 6e27ff305d07f35fb360a78fc6cf92f8 |
| b3_mseccfg_s2 | PASS | 77 | 0 | 193 | 935 | 7390 | mmwp_first | ok=True reached 6 of 15, applied 6 (0 idx>0 phases) | e1907e26f763ae942e9eb3f2e43b4f57 |
| b3_mseccfg_s3 | PASS | 77 | 0 | 191 | 930 | 9709 | mmwp_first | ok=True reached 12 of 12, applied 12 (6 idx>0 phases) | e5c44338149f58842c8377ca1e224d01 |

| Run | Result | GEN_TEST_BINS | UVM_ERROR | md5 of the retained copy (stdout.log for the pinned red; stdout_excerpt.log for the others) |
|---|---|---|---|---|
| b3_mseccfg_red_011 (pinned; retained in full as gen_pmp_mseccfg_red1_stdout.log / _sim.log) | FAIL 1: fire_tp_pmp_011 first (1 ok=False line) | 77 | - | 48735d58eb49d1576eef055ed774f3d5 |
| b3_mseccfg_red1 (seed-drawn red, --red without --red-item: drew TP-PMP-012) | FAIL 1: fire_tp_pmp_012 first (1 ok=False line) | 77 | - | 16c2fde21f16fba0c59e47fa76a7af90 |
| b3_mseccfg_red_012 | FAIL 1: fire_tp_pmp_012 first (1 ok=False line) | 77 | - | 8b447c887c0debed52946207befc4e70 |
| b3_mseccfg_red_022 | FAIL 1: fire_tp_pmp_022 first (1 ok=False line) | 77 | - | 3cedc86eb26788719dee6ac1610c9ec7 |
| b3_mseccfg_red_023 | FAIL 1: fire_tp_pmp_023 first (1 ok=False line) | 77 | - | 6fdbbe7af9f372ca1456162e96a0e506 |
| b3_mseccfg_red_024 | FAIL 1: fire_tp_pmp_024 first (1 ok=False line) | 77 | - | b82d30d5299b4715ba6bf5f2a9409af6 |
| b3_mseccfg_red_025 | FAIL 1: fire_tp_pmp_025 first (1 ok=False line) | 77 | - | 371e0b39eff3072134be3c00a94cb6a7 |
| b3_mseccfg_red_026 | FAIL 1: fire_tp_pmp_026 first (1 ok=False line) | 77 | - | 62c34ef6d0d0dd97d00bb5c07f5f0a32 |
| b3_mseccfg_red_027 | FAIL 1: fire_tp_pmp_027 first (1 ok=False line) | 77 | - | e642e06d2662a092c11fd64da1d88690 |
| b3_mseccfg_red_028 | FAIL 1: fire_tp_pmp_028 first (1 ok=False line) | 77 | - | 0c0b88cafecf8a21b3b3fd86db1781e8 |
| b3_mseccfg_red_029 | FAIL 1: fire_tp_pmp_029 first (1 ok=False line) | 77 | - | 6f021b12edb3f8d09b75d35d62d53aaf |
| b3_mseccfg_red_030 | FAIL 1: fire_tp_pmp_030 first (1 ok=False line) | 77 | - | f2b55ec26b4ea1876816257f044c1ad4 |
| b3_mseccfg_red_031 | FAIL 1: fire_tp_pmp_031 first (1 ok=False line) | 77 | - | 5933069aac3b2870d542ff05c455a5e3 |

Every red fails through the collected mechanism (one GEN_TEST_FIRE ok=False line, the GEN_TEST_FAIL harness line naming exactly that item, no
GEN_TEST_PASS); the red runs' sim.log carries no UVM summary (the failing cocotb test ends the simulation before the report). The pinned
red's retained log passes the flow's red_signature_check with the staged entry's red_expect (RED-OK; the self-test run above).

## 3. Findings for other roles

- tb-infra (TB ask, TP-PMP-108): a mid-run reset command on the bridge (a wrapper reset of the core with the program image kept, the
  bridge counts continuing or restarting as the design decides) is what the plan's mseccfg walk needs to revisit the low {MML, MMWP, RLB}
  states; the CMD kinds at HEAD (DBG_REQ, EXPORT_FLUSH, FETCH_EN, ICACHE_ECC_ARM, IRQ_CLR, IRQ_SET, KEY_MODE, MEM_ERR_ARM, MEM_PEEK, MISC,
  NMI_PULSE, REGIME_SET) have none. Until it exists TP-PMP-108 is not_built and its CG-PMP-003 cr_state_trans / cp_pre / cp_post bins are
  declared by no test. The item's own ignore_bins cover the three (1,x,0)->(1,x,1) arcs only (OQ-PMP-10); the six MML-with-RLB=0 entries
  are reachable from M-mode code but leave no (1,x,1) state for TP-PMP-030 in the same power-on, which a reset would also resolve.
- DV Lead: TP-PMP-109 (gen_pmp_random_regime, Phase 2) co-owns the nine transition bins that TP-PMP-108 cannot reach in one power-on; its
  planning should assume the same constraint until the reset command lands.
- Orchestrator: the staged entries (dv/auto_dv/work/test-writer/gen_testlist_entries.yaml: gen_test_pmp_mseccfg at tier check, measured
  false, seeds 3; gen_test_pmp_mseccfg_red pinned to TP-PMP-011) await the batch-3 acceptance wave through Runtime after the commit.
