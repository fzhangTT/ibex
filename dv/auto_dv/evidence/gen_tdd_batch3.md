# TDD transcript: Phase 1 batch 3, groups gen_pmp_mseccfg (Sections 1-3) and gen_pmp_lock (Section 4)

Test Writer, 2026-09-03. One unnamed subagent (dispatched by the previous Test Writer instance, brief
dv/auto_dv/work/test-writer/batch3/gen_pmp_mseccfg/BRIEF.md over gen_subagent_brief.md v3) wrote dv/auto_dv/tests/gen_test_pmp_mseccfg.py,
dv/auto_dv/tests/gen_programs/gen_pmp_mseccfg_prog.py and rendered dv/auto_dv/fcov_expectations/gen_test_pmp_mseccfg.fcov.yaml from the
module; its own runs (out_head7, an export of 1cbbcfc, on the pre-3h template) are superseded by the runs below and not retained. The Test
Writer changed the delivery in one respect, the Orchestrator's ruling for batch 3: TP-PMP-108 stays not_built (the plan's state-machine walk
restarts from a wrapper reset to revisit the low states and asserts all 8 states per seed; the bridge has no reset command), so the
delivered reduced walk with nine bins_not_hit transitions became `not_built = {"TP-PMP-108": ...}`, fire_tp_pmp_108 and the bins_not_hit
entries were removed, and the manifest was re-rendered (112 bins with 9 not_hit -> 77 bins, 0 not_hit, the not_built header line). The
program keeps the per-seed walk as stimulus; since the cross-model review of e7a0941 (2026-09-03-claude-diff-37c7ecb6-e7a0941b.md,
APPROVE-WITH-CHANGES) its read-backs are compared with the PmpModel prediction by fire_program_verdict as uncredited program integrity (the
review's Minor), the seed-drawn red draws from the built items only (RED_ITEMS; the Major: a `--red` draw of TP-PMP-108 deviated a word no
fire method consulted, an inert red, reproduced by the reviewer at seed 8), an explicit `--red-item TP-PMP-108` stays and now fails loud through
fire_program_verdict (red_108 below), and the .data placeholder is the named PH_DATA (the Nit). The green and pinned-red programs are
byte-identical before and after those changes (seeds 1..3 and --red-item TP-PMP-011 regenerated and compared; the 30-seed sweep from the
export: 450 runs, 0 failures, the seed-drawn red never picks TP-PMP-108); every run below is from the review-fixed test. The TB ask (a
mid-run reset command on the bridge) is filed with tb-infra (Section 3).

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
| gen_test_pmp_mseccfg | 12 of 13 (TP-PMP-108 not built: wrapper-reset walk, no reset command on the bridge) | 77 | PASS (reports 175) | PASS (reports 193) | PASS (reports 191) | 0/0/0 | TP-PMP-011 | 12, each tripping its item alone; plus the TP-PMP-108 red tripping fire_program_verdict |

Knobs: the items name knob:instr_mix csr_heavy and (031) knob:pmp_regime mml_on, both program-side (gen_tb_knobs.yaml
regime_set_consumer: program): the program is CSR-heavy and sets MML itself; the test declares `schedulable = lib.TIMING_ONLY_KNOBS`. Seed 3's
schedule reached 12 of 12 entries with 6 mid-run phases applied (k=3 at seeds 2 and 3; seed 2's nine later entries fall after the end of
test at cycle 7390), so the group has run under mid-run regime changes on the fixed runner. Checkers: gen_chk_csr_readback and gen_chk_pmp
are UNBUILT (plan Section 0a), so every read-back and every U-mode probe outcome is a report word compared by the fire_tp method against the
generator's PmpModel (the single source), as in gen_test_pmp_csr_warl; gen_isa_compare is the always-on cross-check (UVM_ERROR 0).

## 2. Runs (out_head8/b3_mseccfg_<run>; committed copies gen_tdd_logs/test_writer/gen_b3_pmp_mseccfg_<run>_stdout.log and _sim.log for s1..s3, gen_pmp_mseccfg_red1_stdout.log and _sim.log for the pinned red, gen_b3_pmp_mseccfg_red_<nnn>_stdout_excerpt.log for the other reds; run header first, with the build's sources sha)

| Run | Result | GEN_TEST_BINS | UVM_ERROR | reports | retired | EOT cycle | walk path | fire_schedule_applied | md5 (gen_b3_pmp_mseccfg_<run>_stdout.log) |
|---|---|---|---|---|---|---|---|---|---|
| b3_mseccfg_s1 | PASS | 77 | 0 | 175 | 840 | 6216 | mml_first_rlb | ok=True reached 6 of 6, applied 6 (0 idx>0 phases) | dd554a4e853e5d5b4d6a1bea8e1a7f30 |
| b3_mseccfg_s2 | PASS | 77 | 0 | 193 | 935 | 7390 | mmwp_first | ok=True reached 6 of 15, applied 6 (0 idx>0 phases) | 03e27feca82f1a22f1786d853316a308 |
| b3_mseccfg_s3 | PASS | 77 | 0 | 191 | 930 | 9709 | mmwp_first | ok=True reached 12 of 12, applied 12 (6 idx>0 phases) | 9db6a4410afd7615e12a277a239290df |

| Run | Result | GEN_TEST_BINS | UVM_ERROR | md5 of the retained copy (stdout.log for the pinned red; stdout_excerpt.log for the others) |
|---|---|---|---|---|
| b3_mseccfg_red_011 (pinned; retained in full as gen_pmp_mseccfg_red1_stdout.log / _sim.log) | FAIL 1: fire_tp_pmp_011 first (1 ok=False line) | 77 | - | 8d2fbb66d6fe4265b874e26036ff96c3 |
| b3_mseccfg_red1 (seed-drawn red, --red without --red-item: drew TP-PMP-012) | FAIL 1: fire_tp_pmp_012 first (1 ok=False line) | 77 | - | 2d16421c8fc50940713cfb0e486fa624 |
| b3_mseccfg_red_012 | FAIL 1: fire_tp_pmp_012 first (1 ok=False line) | 77 | - | eaf7b885df4c1740327ad4eb4dda73a6 |
| b3_mseccfg_red_022 | FAIL 1: fire_tp_pmp_022 first (1 ok=False line) | 77 | - | 6ce2ca8e0e7bde4e872e502dce6d25a4 |
| b3_mseccfg_red_023 | FAIL 1: fire_tp_pmp_023 first (1 ok=False line) | 77 | - | 399685a89056469d2285cb9fb9a8ff4c |
| b3_mseccfg_red_024 | FAIL 1: fire_tp_pmp_024 first (1 ok=False line) | 77 | - | b46b699a0df674b0684705adc1a75623 |
| b3_mseccfg_red_025 | FAIL 1: fire_tp_pmp_025 first (1 ok=False line) | 77 | - | d029b87e7c7f786422ea67894e3f1546 |
| b3_mseccfg_red_026 | FAIL 1: fire_tp_pmp_026 first (1 ok=False line) | 77 | - | f4c8c9cb553fd29e3fb04b8ea8d72297 |
| b3_mseccfg_red_027 | FAIL 1: fire_tp_pmp_027 first (1 ok=False line) | 77 | - | aff4f3de9b99b9517b5c2af828414335 |
| b3_mseccfg_red_028 | FAIL 1: fire_tp_pmp_028 first (1 ok=False line) | 77 | - | a46a6a2333ea8cf4c1139a6e253a24ab |
| b3_mseccfg_red_029 | FAIL 1: fire_tp_pmp_029 first (1 ok=False line) | 77 | - | c65612c9294877f26c69daf155414a2f |
| b3_mseccfg_red_030 | FAIL 1: fire_tp_pmp_030 first (1 ok=False line) | 77 | - | 829d28b3256f5b4269206c21ba131d34 |
| b3_mseccfg_red_031 | FAIL 1: fire_tp_pmp_031 first (1 ok=False line) | 77 | - | 187ecdbd1a8074c29190e960acb7627e |
| b3_mseccfg_red_108 (explicit --red-item TP-PMP-108: the not-built item's walk word deviated; caught by fire_program_verdict's integrity compare) | FAIL 1: fire_program_verdict first (1 ok=False line) | 77 | - | 5d242a31280fc348400a4a72f4088a23 |

Every red fails through the collected mechanism (one GEN_TEST_FIRE ok=False line, the GEN_TEST_FAIL harness line naming exactly that item, or fire_program_verdict for
the TP-PMP-108 red, no GEN_TEST_PASS); the red runs' sim.log carries no UVM summary (the failing cocotb test ends the simulation before the
report). The pinned
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

## 4. Group gen_pmp_lock (the first PMP WARL group of batch 3; verified after gen_pmp_mseccfg)

One unnamed subagent (dispatched by the previous Test Writer instance at 16:08Z, brief dv/auto_dv/work/test-writer/batch3/gen_pmp_lock/BRIEF.md)
wrote dv/auto_dv/tests/gen_test_pmp_lock.py, dv/auto_dv/tests/gen_programs/gen_pmp_lock_prog.py and rendered
dv/auto_dv/fcov_expectations/gen_test_pmp_lock.fcov.yaml from the module (49 bins; five bins_not_hit with the reason in the header, below); it
ran s1..s4 and eleven reds on out_head7 (an export of 1cbbcfc, the pre-3h template; its summary is batch3/gen_pmp_lock/gen_run_summary.md), all
superseded by the runs below and not retained. The Test Writer took the delivery unchanged: all 10 items built (TP-PMP-013..021, 112), no
not_built; the structure self-test PASSes with the module present and the manifest equals a --test-module re-render. Every run below was made
through gen_run_fixture.sh against out_head8 (export of 9e7c440 with the landing-3h template; sources sha 156eb9357b79552e; template sha
abbe6fcb78e53a27 in the run headers) with GEN_TB_PYROOT = the export carrying copies of the three files, no GEN_TEST_STAGED_ENTRIES; the
library self-test with GEN_TEST_STAGED_ENTRIES naming the staged entries PASSes (the red entry's red_expect against the retained pinned red
through the flow's red_signature_check). Generator sweep by the subagent: 30 seeds x (plain, --red, 10 --red-item), 0 failures
(batch3/gen_pmp_lock/gen_sweep30.log).

bins_not_hit (per-seed unreachable, from the module):
- gen_pmp_mseccfg_cg.cr_state_trans.s011_to_s010: MMWP is never set: M-mode default deny needs a full rule set for code, data and the MMIO page
- gen_pmp_mseccfg_cg.cr_state_trans.s101_to_s100: MML is 0 at the run's one RLB clear: the MML=0 items 013/019/020 follow it
- gen_pmp_mseccfg_cg.cr_state_trans.s111_to_s110: MMWP is never set: M-mode default deny needs a full rule set for code, data and the MMIO page
- gen_pmp_recfg_cg.cp_bb.rlbclr_then_addr: one RLB clear per run; the adjacent-write variant is drawn per seed, so neither rlbclr bin is per-seed must-hit
- gen_pmp_recfg_cg.cp_bb.rlbclr_then_cfg: one RLB clear per run; the adjacent-write variant is drawn per seed, so neither rlbclr bin is per-seed must-hit

| Test | Items built | Bins | Seed 1 | Seed 2 | Seed 3 | UVM_ERROR (s1/s2/s3) | Pinned red | Per-item reds |
|---|---|---|---|---|---|---|---|---|
| gen_test_pmp_lock | 10 of 10 | 49 | PASS (reports 84) | PASS (reports 94) | PASS (reports 90) | 0/0/0 | TP-PMP-013 | 10, each tripping its item alone |

Knobs: the items name knob:instr_mix csr_heavy, program-side; the test declares `schedulable = lib.TIMING_ONLY_KNOBS`. Seed 3's schedule reached
12 of 12 entries with 6 mid-run phases applied (seeds 1 and 2: k=1 and k=3 with the later entries after the end of test at cycles 2897 and
3460). Checkers as for gen_pmp_mseccfg: gen_chk_csr_readback and gen_chk_pmp UNBUILT, every read-back a report word compared against the
shared PmpModel; TP-PMP-019's "blocks RLB" clause is a read-back (mseccfg.RLB stays 0 after the set attempt), no probe episode; gen_isa_compare
always on (UVM_ERROR 0).

Runs (out_head8/b3_pmplock_<run>; committed copies gen_tdd_logs/test_writer/gen_b3_pmp_lock_<run>_stdout.log and _sim.log for s1..s3,
gen_pmp_lock_red1_stdout.log and _sim.log for the pinned red, gen_b3_pmp_lock_red_<nnn>_stdout_excerpt.log for the other reds; run header first):

| Run | Result | GEN_TEST_BINS | UVM_ERROR | reports | retired | EOT cycle | fire_schedule_applied | md5 (gen_b3_pmp_lock_<run>_stdout.log) |
|---|---|---|---|---|---|---|---|---|
| b3_pmplock_s1 | PASS | 49 | 0 | 84 | 424 | 2897 | ok=True reached 6 of 6, applied 6 (0 idx>0 phases) | 15e0305fb57aee7384a6e132d09f6473 |
| b3_pmplock_s2 | PASS | 49 | 0 | 94 | 456 | 3460 | ok=True reached 6 of 15, applied 6 (0 idx>0 phases) | ea82d846a7fc92a11dca988b7d6b0bc0 |
| b3_pmplock_s3 | PASS | 49 | 0 | 90 | 451 | 5634 | ok=True reached 12 of 12, applied 12 (6 idx>0 phases) | 82b1ad5bd654b73399258b367597072b |

| Run | Result | GEN_TEST_BINS | UVM_ERROR | md5 of the retained copy (stdout.log for the pinned red; stdout_excerpt.log for the others) |
|---|---|---|---|---|
| b3_pmplock_red_013 (pinned; retained in full as gen_pmp_lock_red1_stdout.log / _sim.log) | FAIL 1: fire_tp_pmp_013 first (1 ok=False line) | 49 | - | 764a0617aabf3770c1808741114cb945 |
| b3_pmplock_red1 (seed-drawn red, --red without --red-item: drew TP-PMP-014) | FAIL 1: fire_tp_pmp_014 first (1 ok=False line) | 49 | - | 0f1b70a61d6f023e9c64ea5a04b31447 |
| b3_pmplock_red_014 | FAIL 1: fire_tp_pmp_014 first (1 ok=False line) | 49 | - | c8af4c3154f8b8886757e49f2c9c27aa |
| b3_pmplock_red_015 | FAIL 1: fire_tp_pmp_015 first (1 ok=False line) | 49 | - | 3e49646c75ee542911a5237df73b7a92 |
| b3_pmplock_red_016 | FAIL 1: fire_tp_pmp_016 first (1 ok=False line) | 49 | - | 4ec25d1196323b7bd8230160fa6876df |
| b3_pmplock_red_017 | FAIL 1: fire_tp_pmp_017 first (1 ok=False line) | 49 | - | f4870561d0e60dd448bc771d84183dd5 |
| b3_pmplock_red_018 | FAIL 1: fire_tp_pmp_018 first (1 ok=False line) | 49 | - | 032775333403e1571ee6602c0f88e326 |
| b3_pmplock_red_019 | FAIL 1: fire_tp_pmp_019 first (1 ok=False line) | 49 | - | 84aada8a8f68ddf89bb6370ecd1c2e4e |
| b3_pmplock_red_020 | FAIL 1: fire_tp_pmp_020 first (1 ok=False line) | 49 | - | 0875d147df6ab4669f6f8f0f81bc7c11 |
| b3_pmplock_red_021 | FAIL 1: fire_tp_pmp_021 first (1 ok=False line) | 49 | - | 4edfa224ee751847578b802296ab38d8 |
| b3_pmplock_red_112 | FAIL 1: fire_tp_pmp_112 first (1 ok=False line) | 49 | - | 637c2a7a8ff587d201928862fc1cb7ec |

Every red fails through the collected mechanism (one GEN_TEST_FIRE ok=False line, the GEN_TEST_FAIL harness line naming exactly that item, no
GEN_TEST_PASS); the red runs' sim.log carries no UVM summary. A first local pass at 17:33Z ran the wrong module (the Test Writer's run script
kept gen_test_pmp_mseccfg after a name substitution) and was discarded; the runs above are the 17:36Z pass.

Staged entries (dv/auto_dv/work/test-writer/gen_testlist_entries.yaml): gen_test_pmp_lock at tier check, measured false, seeds 3, the fcov
file wired; gen_test_pmp_lock_red pinned to TP-PMP-013 (the csrrc to a lock-mix pmpcfg word replaced by a read).
