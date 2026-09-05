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
byte-identical before and after those changes (seeds 1..3 and --red-item TP-PMP-011 regenerated and compared); every run below is from
the review-fixed test. The generator sweep is retained since the batch-3 touch (Section 5): gen_b3_pmp_mseccfg_sweep30.log
(md5 0d982f539cea70dc1ca716254adc26ea) names the generator's sha256 in its header (672078f2f97512f8, the touch's generator, whose programs for
seeds 1..3, the drawn red and all 13 item reds at seed 1 are byte-identical to 36e2694's): 30 seeds x (plain, --red, 13 --red-item) =
450 runs, 0 failures, the seed-drawn red never picks TP-PMP-108. Both docstrings now state the red rule precisely (CR-B3-M-1): the
seed-drawn item comes from RED_ITEMS, an explicit TP-PMP-108 red fails through fire_program_verdict. Two reachable transitions the walk never
generates (CR-B3-L-2, 60 seeds): s001->s111 (MML and MMWP set in one write) and s101->s110 (MMWP set and RLB cleared in one write); every walk
write toggles one bit by construction (rlb_op and the single-bit MML / MMWP set writes), so two-bit transitions do not occur; they are legal,
belong to TP-PMP-108's walk when the item is built with the reset command, and are not declared until then (the item is not_built). The TB ask (a
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
- T-249 (2026-09-03, joint landing with the DV Lead under LOG-036b, committed 9596727): the CG-PMP-001 Sample line's anti-vacuity
  clause now states the sampler's own observation and attributes the prediction comparison to the comparator's isa_rd row until
  gen_chk_csr_readback is built, so gen_test_pmp_mseccfg's manifest was re-rendered by --test-module on an archive of 1bf0295 with the new plan:
  77 declared bins unchanged, 19 anti_vacuity strings carry the new clause, header and every other line unchanged; nothing in
  the test or its program changed.

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

## 4. Group gen_pmp_lock (the first PMP WARL group of batch 3; verified after gen_pmp_mseccfg; runs re-made by the batch-3 touch, Section 5)

One unnamed subagent (dispatched by the previous Test Writer instance at 16:08Z, brief dv/auto_dv/work/test-writer/batch3/gen_pmp_lock/BRIEF.md)
wrote dv/auto_dv/tests/gen_test_pmp_lock.py, dv/auto_dv/tests/gen_programs/gen_pmp_lock_prog.py and rendered
dv/auto_dv/fcov_expectations/gen_test_pmp_lock.fcov.yaml from the module; its own runs (out_head7, an export of 1cbbcfc, the pre-3h template) and
the Test Writer's first verification runs on out_head8 (36e2694) are superseded by the runs below, made on out_head14 after the batch-3 touch
(Section 5) and retained under the same names. All 10 items built (TP-PMP-013..021, 112), no not_built; the structure self-test PASSes with the
module present and the manifest equals a --test-module re-render (50 bins, four bins_not_hit header lines). Every run below was made through the
export's gen_run_fixture.sh against out_head14 (export of 2ea81ac, HEAD when the export was made; TB paths unchanged through d4b5933: no path under dv/auto_dv/env, tb, isa, gen_tb, tests, fcov_expectations, stim or rtl/ changed; sources sha 893384b8eec4e6d5; template
sha abbe6fcb78e53a27 in the run headers) with the export as the one Python root carrying the touch's files, no GEN_TEST_STAGED_ENTRIES; the library
self-test with GEN_TEST_STAGED_ENTRIES naming the staged entries PASSes (the red entry's red_expect against the retained pinned red through the
flow's red_signature_check). Generator sweep: Section 5 (seeds 1..400, 200 draws meant as random seeds that were one seed (CM99-M-1, re-swept in Section 8) and 200 flow-derived seeds, every red item at seeds 1..60,
retained as gen_b3_pmp_lock_sweep800.log).

bins_not_hit (rule (g), from the module; the precondition each names is one this test does not apply):
- gen_pmp_mseccfg_cg.cr_state_trans.s011_to_s010: MMWP is never set: M-mode default deny needs a full rule set for code, data and the MMIO page
- gen_pmp_mseccfg_cg.cr_state_trans.s101_to_s100: MML is 0 at the run's one RLB clear: the MML=0 items 013/019/020 follow it
- gen_pmp_mseccfg_cg.cr_state_trans.s111_to_s110: MMWP is never set: M-mode default deny needs a full rule set for code, data and the MMIO page
- gen_pmp_recfg_cg.cp_bb.rlbclr_then_addr: the write adjacent to the run's one RLB clear is a pmpcfg write here (RLB stays 0 once a lock exists, so
  one clear per power-on); the pmpaddr variant is not applied by this test (gen_pmp_recfg_cg.cp_bb.rlbclr_then_cfg is declared and hit every seed)

| Test | Items built | Bins | Seed 1 | Seed 2 | Seed 3 | UVM_ERROR (s1/s2/s3) | Pinned red | Per-item reds |
|---|---|---|---|---|---|---|---|---|
| gen_test_pmp_lock | 10 of 10 | 50 | PASS (reports 92) | PASS (reports 94) | PASS (reports 90) | 0/0/0 | TP-PMP-013 | 10, each tripping its item alone; 40 seeds of the pinned red and 40 green seeds in Section 5 |

Knobs: the items name knob:instr_mix csr_heavy, program-side; the test declares `schedulable = lib.TIMING_ONLY_KNOBS`. Seed 3's schedule reached
12 of 12 entries with 6 mid-run phases applied (seeds 1 and 2: ok=True reached 6 of 6, applied 6; ok=True reached 6 of 15, applied 6, the later entries
after the end of test at cycles 3159 and 3448). Checkers as for gen_pmp_mseccfg: gen_chk_csr_readback and
gen_chk_pmp UNBUILT, every read-back a report word compared against the shared PmpModel; TP-PMP-019's "blocks RLB" clause is a read-back
(mseccfg.RLB stays 0 after the set attempt), no probe episode; gen_isa_compare always on (UVM_ERROR 0).

Runs (out_head14/b3l14_pmplock_<run>; committed copies gen_tdd_logs/test_writer/gen_b3_pmp_lock_<run>_stdout.log and _sim.log for s1..s3,
gen_pmp_lock_red1_stdout.log and _sim.log for the pinned red, gen_b3_pmp_lock_red_<nnn>_stdout_excerpt.log for the other reds; run header first):

| Run | Result | GEN_TEST_BINS | UVM_ERROR | reports | retired | EOT cycle | fire_schedule_applied | md5 (gen_b3_pmp_lock_<run>_stdout.log) |
|---|---|---|---|---|---|---|---|---|
| b3l14_pmplock_s1 | PASS | 50 | 0 | 92 | 462 | 3159 | ok=True reached 6 of 6, applied 6 (0 idx>0 phases) | e5f3d614b8db6dff1deac143d851fc88 |
| b3l14_pmplock_s2 | PASS | 50 | 0 | 94 | 457 | 3448 | ok=True reached 6 of 15, applied 6 (0 idx>0 phases) | d7e5fee5a4e9b9ca6ce7ad2474e09920 |
| b3l14_pmplock_s3 | PASS | 50 | 0 | 90 | 450 | 5637 | ok=True reached 12 of 12, applied 12 (6 idx>0 phases) | c4ee09d32d3842b61df3db8f125ca802 |

| Run | Result | GEN_TEST_BINS | UVM_ERROR | md5 of the retained copy (stdout.log for the pinned red; stdout_excerpt.log for the others) |
|---|---|---|---|---|
| b3l14_pmplock_red_013 (pinned; retained in full as gen_pmp_lock_red1_stdout.log / _sim.log) | FAIL 1: fire_tp_pmp_013 first (1 ok=False line) | 50 | - | c89fcd0b5db210cb680aa0d089e60be4 |
| b3l14_pmplock_red1 (seed-drawn red, --red without --red-item: drew TP-PMP-014) | FAIL 1: fire_tp_pmp_014 first (1 ok=False line) | 50 | - | 7f426cc7c8f8244f4e4b41510bd66f6a |
| b3l14_pmplock_red_014 | FAIL 1: fire_tp_pmp_014 first (1 ok=False line) | 50 | - | f04ea5a9287e4bccfd446d0d2da9a4d1 |
| b3l14_pmplock_red_015 | FAIL 1: fire_tp_pmp_015 first (1 ok=False line) | 50 | - | cadfdb2dd00b63ccc8db5a5f9a44fdbc |
| b3l14_pmplock_red_016 | FAIL 1: fire_tp_pmp_016 first (1 ok=False line) | 50 | - | a8f311139ef1a7c0b7cf6c89c93e3713 |
| b3l14_pmplock_red_017 | FAIL 1: fire_tp_pmp_017 first (1 ok=False line) | 50 | - | bcd6a5679820599e120430a49ddb41e5 |
| b3l14_pmplock_red_018 | FAIL 1: fire_tp_pmp_018 first (1 ok=False line) | 50 | - | 45e84756d2d60494b8699e3341ea665c |
| b3l14_pmplock_red_019 | FAIL 1: fire_tp_pmp_019 first (1 ok=False line) | 50 | - | 272e6c33078e6e64c1ac04787a68807c |
| b3l14_pmplock_red_020 | FAIL 1: fire_tp_pmp_020 first (1 ok=False line) | 50 | - | 8d06541561444a11880018129b4ac94f |
| b3l14_pmplock_red_021 | FAIL 1: fire_tp_pmp_021 first (1 ok=False line) | 50 | - | 708188ad210d66a1fba7df3707653ec3 |
| b3l14_pmplock_red_112 | FAIL 1: fire_tp_pmp_112 first (1 ok=False line) | 50 | - | 43a91137d4b996306d431af564e3a991 |

Every red fails through the collected mechanism (one GEN_TEST_FIRE ok=False line, the GEN_TEST_FAIL harness line naming exactly that item, no
GEN_TEST_PASS); the red runs' sim.log carries no UVM summary. Every red site is one the model says is observable (Section 5).

Staged entries (dv/auto_dv/work/test-writer/gen_testlist_entries.yaml): gen_test_pmp_lock at tier check, measured false, seeds 3, the fcov
file wired; gen_test_pmp_lock_red pinned to TP-PMP-013 (a lock-mix pmpcfg word write that changes an unlocked lane replaced by a read).
- T-249 (2026-09-03, joint landing with the DV Lead under LOG-036b, committed 9596727): the CG-PMP-001 Sample line's anti-vacuity
  clause now states the sampler's own observation and attributes the prediction comparison to the comparator's isa_rd row until
  gen_chk_csr_readback is built, so gen_test_pmp_lock's manifest was re-rendered by --test-module on an archive of 1bf0295 with the new plan:
  50 declared bins unchanged, 20 anti_vacuity strings carry the new clause, header and every other line unchanged; nothing in
  the test or its program changed.

## 5. The batch-3 touch: red-site observability, three green generator defects, the retained sweeps (the CM32/CM38/CR-B3/CR-B3v2 rows are in gen_critic_response_batch3.md)

Why: the Critic's batch3 v2 (M-1) found the TP-PMP-013 red vacuous on about half the seeds (the replaced write hit an all-locked word, or was a
csrrc no-op, so the read-back equalled the green expectation) and asked for the same audit of every red site of both generators; the 3j review
(CM38-MAJ-1) found plan() aborting on about 7 percent of seeds (the reserved non-TOR neighbour itself a kept lock). The touch answers both with
mechanism, not enumeration:
- gen_pmp_lock_prog.py: a TP-PMP-013 site is eligible only where the write changes an unlocked lane of the word (a write to an all-locked word or an
  RMW that changes nothing is never a site); csr_op asserts for every skipped write that the modelled read-back moves, so any vacuous site of any
  item fails plan() loud; the CM38-MAJ-1 role draw (ntor only from kept locks whose lower neighbour is not the other kept lock) with the assert.
- gen_pmp_mseccfg_prog.py: a TP-PMP-027/028/029 red lane is eligible only where the deviated write reads back differently from the planned one
  (the model runs both), and the TP-PMP-030 skip asserts the skipped write changes the word; the RLB-flip sites already carried that check
  (msec_flip_dev). Before the gating, the assertion alone caught a vacuous TP-PMP-028 red at seed 18 (lane 0 of pmpcfg2, A=OFF, L=0 stored equal to
  the suppressed byte): gen_b3_pmp_mseccfg_red028_s18_ungated_probe.log (md5 7f355c281a1e2bfe31b4f5442cb32e70); the
  gated generator draws lane 2 of pmpcfg3 there. The programs (seeds 1..3, the drawn red and all 13 item reds at seed 1) are byte-identical to
  36e2694's, so the 21 retained mseccfg logs stay valid.
- TP-PMP-112's adjacent write is the pmpcfg variant on every seed (one RLB clear per power-on, so one variant per test): rlbclr_then_cfg is
  declared, rlbclr_then_addr is a rule (g) entry (CR-B3v2 L-4); 49 bins with five not_hit became 50 with four.

Three green defects of gen_pmp_lock_prog.py found by the touch's sweeps (each a green run failing on its own fire check, none a DUT finding):
- seeds 29 and 35 (first seen by the TP-PMP-013 red sweep, confirmed by green probes): a TP-PMP-021 csrrs rewrite of a locked entry under RLB=1
  set only W without R, which legalisation strips, so the rewrite changed nothing and fire_tp_pmp_021's "every rewrite changed" relation failed
  (7 of 8, 8 of 9); the RMW forms now fall back to csrrw whenever the legalised byte would not change. The sweep on the generator before this fix
  (gen_b3_pmp_lock_sweep800_before_fix.log, md5 b216db32a7104eddb014a0a276b8f922; its stderr
  gen_b3_pmp_lock_sweep800_before_fix_err.log) shows the new csr_op assertion catching the same site as a vacuous red: 2200 runs,
  1 failure, failed_seeds=[r35] ("red TP-PMP-021 rlb1 rewrite cfg csrrs: the skipped write changes nothing").
- seed 7: a TP-PMP-020 episode locked the entry right above TP-PMP-015's TOR entry as TOR before P6, freezing that entry's pmpaddr, so lock_entry
  fell back to A=OFF and fire_tp_pmp_015 failed ("entry 10 read back locked TOR: False"); P5 now never draws TOR right above the 015/017 entries
  and p6_tor_lock asserts the pmpaddr is writable.
- seed 17 (found by the green sweep after the two fixes): TP-PMP-015's TOR entry drawn at PMPNumRegions-2 under TP-PMP-018's top-entry lock, which
  may be a TOR; the TOR roles now stay below the top entry.
What 36e2694's generator carried: the TP-PMP-021 no-op rewrite (its seeds 29 and 35 fail the same way, and seed 36 aborts in plan()) and the
latent hazard of a TOR lock above the 015/017 entries; that hazard surfaced at seed 7 only after the TP-PMP-112 variant pin shifted every
post-P2 draw (at 36e2694's seed 7 the P5 episode on entry 11 draws NA4, and over seeds 1..200 it never falls 015 back to A=OFF), and the
before-fix sweep's r35 red belongs to that intermediate generator too. The acceptance wave on 36e2694 would still have shown the 021 failures
at about 2 of 40 seeds.

Sweeps on the final generator (sha256 56ef5fe5f695106b), from head_export13 with the touch overlaid:
- gen_b3_pmp_lock_sweep800.log (md5 74999fde11c68c749b373cd8569f1aac): plan() green and seed-drawn red for seeds 1..400, 200 draws meant as
  random 31-bit seeds (in fact the single seed 255808012 repeated, the script re-seeding random.Random(2026) per draw; CM99-M-1, the random
  part re-swept over 200 distinct seeds in Section 8) and 200 flow-derived seeds, every --red-item at seeds 1..60: 2200 runs over 601 distinct
  seeds, 0 failures (the observability
  assertion included); 013 red sites over seeds 1..60 (lock mix of the replaced write): 8 none, 52 some.
- Simulation sweeps on out_head14 (gen_b3_pmp_lock_h13_run_summary.log, md5 8585166c074f75a00580b32cb9d55cc0, one DONE line per
  run; per-run decisive-line excerpts gen_b3_pmp_lock_r013_s<N>_stdout_excerpt.log and gen_b3_pmp_lock_g<N>_stdout_excerpt.log): the TP-PMP-013 red
  at seeds 1..40 fails on fire_tp_pmp_013 alone on 40 of 40 seeds (replaced-write
  lock mix: 4 none, 36 some); the green program at seeds 1..40 passes on 40 of 40
  (GEN_TEST_BINS n=50 equal to the manifest, UVM_ERROR 0 on every seed).

Note for the covergroup author (CM72-I-3): rlbclr_then_cfg is a per-seed must-hit bin whose hit assumes the cp_bb pair predicate counts
consecutive PMP CSR writes (the `li t0` between the mseccfg clear and the pmpcfg write is not a PMP CSR write), the assumption the declared
lock_then_* bins already make; a predicate on consecutive rvfi_order would miss both.

## 6. Group gen_pmc_ctrl: a complete draft held out of the tree, blocked on the ISA model's counter set

Status: the dependency below is met by tb-infra's T-235 landing (158f5be); the group is re-verified on that shim and staged in Section 9. The
text of this section stays as the record of the held state and of the ask.

One unnamed subagent (dispatched by the previous Test Writer instance at 18:1x Z against 56e37d7, brief
dv/auto_dv/work/test-writer/batch3/gen_pmc_ctrl/BRIEF.md) wrote gen_test_pmc_ctrl.py, gen_programs/gen_pmc_ctrl_prog.py and the rendered
manifest into its export (last edit 18:54Z; the instance was stopped at 18:46Z, LOG-056, and the subagent's report never arrived). The
respawned Test Writer verified the delivery from the snapshot batch3/gen_pmc_ctrl/draft_18_54Z/ on head_export14 (an export of 2ea81ac, the
TB of tb-infra landing 4) with one docstring paragraph added (quoted at the end of this section): 13 of 14 items built (TP-PMC-057 not_built: the mcounteren_writable pin is
a static plusarg knob with no mid-run driver, TB ask), 204 bins declared with 18 bins_not_hit (debug window, the pin's off / invalid values,
024's export-row clause), the manifest equal to a --test-module render, the library self-test PASS with the module present (the LOG-050
regime-handler rule included: schedulable = lib.TIMING_ONLY_KNOBS). Files as verified: gen_test_pmc_ctrl.py sha256
5a03a61a4ecf6370, gen_pmc_ctrl_prog.py e7893d97218c421e,
gen_test_pmc_ctrl.fcov.yaml 193caa85e484aecb (kept under the work directory, not in the tree).

Runs on out_head14 (programs rebuilt from the draft generator, batch3/gen_pmc_ctrl/h14/; the s1 green retained as
gen_b3_pmc_ctrl_s1_stdout_excerpt.log with the comparator's first mismatches and summary): the fire checks and the reds do what the plan
asks, the ISA comparator does not follow the program.

| Run | fire checks | GEN_TEST_BINS | gen_isa_compare |
|---|---|---|---|
| b3_pmc_ctrl_s1 | PASS | 204 | UVM_ERROR 654; ISA compare: records=6056 mismatches=654 |
| b3_pmc_ctrl_s2 | PASS | 204 | UVM_ERROR 572; ISA compare: records=6999 mismatches=572 |
| b3_pmc_ctrl_s3 | PASS | 204 | UVM_ERROR 643; ISA compare: records=6539 mismatches=643 |
| b3_pmc_ctrl_red_022 | FAIL on fire_tp_pmc_022 alone | 204 | (red run: no UVM summary) |
| b3_pmc_ctrl_red_023 | FAIL on fire_tp_pmc_023 alone | 204 | (red run: no UVM summary) |
| b3_pmc_ctrl_red_024 | FAIL on fire_tp_pmc_024 alone | 204 | (red run: no UVM summary) |
| b3_pmc_ctrl_red_025 | FAIL on fire_tp_pmc_025 alone | 204 | (red run: no UVM summary) |
| b3_pmc_ctrl_red_026 | FAIL on fire_tp_pmc_026 alone | 204 | (red run: no UVM summary) |
| b3_pmc_ctrl_red_027 | FAIL on fire_tp_pmc_027 alone | 204 | (red run: no UVM summary) |
| b3_pmc_ctrl_red_028 | FAIL on fire_tp_pmc_028 alone | 204 | (red run: no UVM summary) |
| b3_pmc_ctrl_red_029 | FAIL on fire_tp_pmc_029 alone | 204 | (red run: no UVM summary) |
| b3_pmc_ctrl_red_030 | FAIL on fire_tp_pmc_030 alone | 204 | (red run: no UVM summary) |
| b3_pmc_ctrl_red_031 | FAIL on fire_tp_pmc_031 alone | 204 | (red run: no UVM summary) |
| b3_pmc_ctrl_red_032 | FAIL on fire_tp_pmc_032 alone | 204 | (red run: no UVM summary) |
| b3_pmc_ctrl_red_033 | FAIL on fire_tp_pmc_033 alone | 204 | (red run: no UVM summary) |
| b3_pmc_ctrl_red_056 | FAIL on fire_tp_pmc_056 alone | 204 | (red run: no UVM summary) |
| b3_pmc_ctrl_red1 (seed-drawn) | FAIL on fire_tp_pmc_023 alone | 204 | (red run: no UVM summary) |

Blocker (TB), diagnosed against the committed shim (LOG-063; the 04cf523 review's High): dv/auto_dv/isa/gen_isa_shim.cc, unchanged since
9e912bb (before 2ea81ac) and so identical in the 2ea81ac export out_head14 ran (its retirement derivation dates from 3be5a34), derives each step's retirement from Spike's minstret delta (minstret0 at :431,
`retired = minstret1 - minstret0` at :465-466) and, when the delta is 0, synthesises trap = 1 with the current mcause and mtval (:474-477).
The program holds mcountinhibit.IR = 1 through TP-PMC-023/024/025/033/056, so Spike's minstret stops (the pinned Spike passes 0 to the
bump while IR is inhibited) and every record executed under the inhibit is reported as a trap with the stale cause 8 of the last ecall while
pc, insn and rd match: the model stays in lock-step, the row is the synthesised trap. The same constraint is already written into
tests/gen_programs/gen_csr_access_prog.py:35-36 ("mcountinhibit.IR is never set"). The second mechanism is the mcountinhibit mask the shim
defers (gen_component_api_isa_shim.md:104, DEFERRED; Spike keeps bits 13..31, Ibex reads 0), and the third is Spike's minstret under the
inhibit and after a write (gen_counter_csr_anchors.md section 10: the writer's +1 lands in the low word, a read includes the instruction
retiring in WB). Classification of the retained seed-1 run (gen_b3_pmc_ctrl_s1_mismatch_classes.log; 6056 records, 654 rows): isa_trap
501, of which 500 are `dut retired, model retired 0 trap=1 cause=00000008` (the synthesised trap) and one is the csrw minstret record whose
delta is the written value (model retired 1375117292); isa_rd 109, of which 62 are mcountinhibit read-backs (csrr / csrrw / csrrs /
csrrc / csrrwi), 31 minstret / instret read-backs, and 16 are loads and ALU results over stored counter values; isa_mem 44 are stores of
report words whose value the model computed differently. Not gaps, contrary to the first report (retracted; LOG-063): the shim already
masks mcounteren to 0x1FFD with TM 0 (:43, :273-277), traps time / timeh in every mode (:142-149, :228-229) and gates mcounteren writes on
the mcounteren_writable pin (:208, :274); the reading "a U-mode alias access traps in Ibex and not in the model, after which the model's
ecall lands one record late" is superseded by the classification above (no isa_pc / isa_insn / isa_rd row precedes the first isa_trap).
The ask, restated from the tree (T-235, tb-infra): (1) derive retirement independently of minstret, or model the inhibit so a step under
IR = 1 still counts as retired, the blocking part (this group's programs cannot avoid IR = 1); (2) legalise mcountinhibit to Ibex's 13-bit
set (bits 0, 2..12 writable; bit 1 and 31:13 read 0), the DEFERRED row; (3) the minstret rows of gen_counter_csr_anchors.md section 10
(the writer's +1 in the low word, the WB-inclusive read), which this group's counter writes must respect once the comparator follows the
program. The DV Lead's plan note stands in the narrower form: TP-PMC-032's criterion "gen_isa_compare (mcause 2)" is satisfiable (the shim
traps time / timeh), the WARL items' read-backs wait on (2) and (3). Consequence: no testlist entry (the flow verdict would FAIL on the
comparator); the draft's docstring states the dependency in these sentences (the draft is held under the work directory, so the quote is the
record until it lands): "gen_isa_compare cannot follow this program yet: the shim derives a retirement from Spike's minstret delta and synthesises
a trap record when the delta is 0, so every record executed while mcountinhibit.IR = 1 (023/024/025/033/056 hold it) is an isa_trap mismatch,
and the mcountinhibit mask the shim defers (Spike keeps bits 13..31) plus Spike's minstret under inhibit and after writes make the counter
read-backs isa_rd mismatches; until the shim derives retirement independently of minstret (or models the inhibit) and legalises
mcountinhibit, this test has no testlist entry: its fire checks and reds are verified locally (gen_tdd_batch3.md Section 6) and the flow
does not run it."
The three files stay under dv/auto_dv/work/test-writer/batch3/gen_pmc_ctrl/verified_h14/ (the subagent's snapshot beside them in
draft_18_54Z/) until the shim lands, when the group is re-verified and staged with its pin-off entry.

## 7. Evidence for the Critic's batch3 v2 final lows: the pre-fix defects and the intermediate generators

The two intermediate generators of the batch-3 touch (never committed) are reconstructed from the committed gen_pmp_lock_prog.py by reverting
the later edits, and their sha256 prefixes equal the ones the retained logs name: 7fead94e4693c62a (the before-fix sweep's header) and
429fa9897e7236fa (the header of the second-pass sweep that ran beside the h13 second-pass build, retained as
gen_cm99_pmp_lock_h13_prefix2_sweep_header.log); both are retained as text, and gen_cm99_pmp_lock_attribution_crc.log ties each to its
build by image checksum: the 7fead94e text rebuilds seeds 7, 29 and 35 to the words and crc32 of the images the pre-fix greens loaded, and
the 429fa989 text rebuilds seeds 1..6 to those of the second-pass build log (CM99-L-3). gen_b3_pmp_lock_intermediate_reproduction.log (md5
1331eb924a455d3586db666ee9ce2e59) runs them from a detached archive: 7fead94e asserts "red TP-PMP-021 rlb1 rewrite cfg
csrrs: the skipped write changes nothing" at --seed 35 --red (the before-fix sweep's one failure) and builds seeds 7, 17 and 29; 429fa989 aborts
at seed 17 with "TP-PMP-015: pmpaddr14 is frozen by a locked TOR above it" and builds the others. The pre-fix green failures of seeds 7, 29 and
35 (out_head13, the 7fead94e generator) are retained as gen_b3_pmp_lock_prefix_green_s7/s29/s35_stdout_excerpt.log (fire_tp_pmp_015 at seed 7,
fire_tp_pmp_021 at 29 and 35, one ok=False line each), with the first-pass run summary gen_b3_pmp_lock_prefix_run_summary.log. The 800 seeds of
the sweep are gen_b3_pmp_lock_sweep800_seeds.txt (md5 39d6e98749ba6b847d7ca762c8bd7694), whose random_31bit line is the single seed
255808012 repeated 200 times (CM99-M-1): the two 800-seed sweeps covered 601 distinct seeds, and Section 8 re-sweeps the random part.

## 8. The closure-touch review (CM99): the random part of the 800-seed sweeps re-run, the intermediate generators tied to their builds

CM99-M-1: sweep_lock_800.sh built its 200 "random 31-bit seeds" as `random.Random(2026).getrandbits(31)` inside the comprehension, a new
generator per draw, so every draw was 255808012; the retained seed list shows it, and both 800-seed sweeps (the before-fix one and the final
one) covered 601 distinct seeds (400 sequential, 1 random, 200 flow-derived). The random part is re-swept here, generator-only as before:
gen_cm99_pmp_lock_random200_seeds.txt (md5 e49d726a7760c3902bcf71eae8b84b8c) holds 200 distinct seeds from one random.Random(2026)
instance (Random(2026)'s first draw is the old single value 255808012, so it is the first of the 200), and gen_cm99_pmp_lock_random200_sweep.log (md5 e8ae9adb30e8b15e950ee757459a2ca3)
runs plan() green and seed-drawn red for each on HEAD's gen_pmp_lock_prog.py (sha256 862ad214f482a2e6, the committed sweeps' 56ef5fe5f695106b
with the docstring 674d026 edited) from a detached archive: 400 runs, 0 failures. The retained sweep logs and seed list are not edited; their
manifest rows and the Section 5 sentences name the defect.
CM99-L-3: the attribution of the pre-fix greens to 7fead94e and of the h13 second-pass build to 429fa989 rested on run timing and on a
sweep header that lived under work/. gen_cm99_pmp_lock_h13_prefix2_sweep_header.log (md5 77e10c7ea0a3678afb6f4de651ab1fdd)
retains that header, and gen_cm99_pmp_lock_attribution_crc.log (md5 f3371c3dffd0fb024d030ebe52c847cb) makes the attribution
mechanical: rebuilt from a detached archive, the 7fead94e text reproduces the images the pre-fix greens of seeds 7, 29 and 35 loaded
(words 589 / 557 / 557, crc32 0x66b42d50 / 0x90aa26f5 / 0x420b00bd, equal to probe_greens/g<N>/build.log), and the 429fa989 text reproduces
the second-pass build's seeds 1..6 (equal to build_all_prefix2.log); the final generator's images of the same seeds differ, so the checksums
discriminate.

## 9. Group gen_pmc_ctrl re-verified on the T-235 shim and staged

The ISA shim landed with the counter model this group waited for (158f5be, tb-infra's T-235; the shim's API doc names it: a step under
mcountinhibit.IR = 1 retires instead of being synthesised as a trap, minstret is served as Spike's count minus what Ibex did not count with
the inhibit rule an instruction leaves behind, mcountinhibit is masked, mhpmcounter13..31 and mhpmevent13..31 read as zero). Its own
measurement of this group's seed-1 image is tb-infra's (gen_fu_l9_lockstep_pmc_s1_on_* under evidence/gen_tdd_logs/lockstep: 8000 records,
0 mismatches). This section is the Test Writer's re-verification: export head_export18 of bf61843 (T-235 in, with the 73ff075
write-corner fixes of its review, CM123), build out_head18, the held
draft's test and generator copied in, the docstring's dependency paragraph replaced by the statement of what the shim models and what it
leaves unmodelled (the hazard variant of the high-word write corner, dummy instructions under the counters knob, neither relied on here),
the manifest re-rendered on HEAD's plan (204 declared bins, one not_built header for TP-PMC-057, eighteen not_hit; gen_test_pmc_ctrl.fcov.yaml
193caa85e484 and test 388b15850e47 as landed at aa43c5b, c3f77460af5d and 0383702cd933 after the CM141 corrections below, whose runs the Runs
paragraph retains); generator e7893d97218c. Images built
from that export with gen_program.py --directed --gcc-opts=-Idv/auto_dv/tests/gen_programs: seed 1 words 6581 crc32 0xe4448e4a, seed 2
6517 / 0x9ee34d68, seed 3 6533 / 0xbe52ad89 (the pin-off program is the same text, the pin changes only the expectations).
Runs: seeds 1, 2, 3 PASS with UVM_ERROR 0 and GEN_TEST_BINS n=204, all 13 fire checks ok (gen_pmc_ctrl_t235_s1_stdout.log md5
217aab71155a4760c7f6c5985c683c48 and _sim.log c19578b386bdefde37a51fb1b96f4b8f in full; s2 / s3 excerpts); the pin-off variant (generator --pin off,
+gen_knob_mcounteren_writable=off) PASS with UVM_ERROR 0, fire_tp_pmc_028 on its dropped branch, the banner naming the pin
(gen_pmc_ctrl_t235_pin_off_s1_stdout_excerpt.log md5 b0a3a0f4d011b43b341bef9f3265d7db); the pinned red --red-item TP-PMC-022 fails exactly
fire_tp_pmc_022 (gen_pmc_ctrl_red1_stdout.log md5 499328cc3bc15065f644524bb2ccc786, _sim.log 9275e94424ea376335f1d2381a89c3aa, the entry's pinned red, in full) and the
seed-drawn red (seed 1 draws TP-PMC-023) fails exactly fire_tp_pmc_023 (gen_pmc_ctrl_t235_red_drawn_s1_stdout_excerpt.log md5
a171385f78f4d4ffe5e812fcf51cbf59). So the three asks of Section 6 are answered on the shim's side: the 501 trap rows (retirement under IR = 1), the 62
mcountinhibit read-backs (the mask) and the 31 minstret rows all compare clean in these runs. The reds of the other eleven items were
verified in Section 6 on out_head14 and are not re-run here; the fire checks are unchanged: the held draft's test (sha256 29d9b8c79e2b, the file
under work/test-writer/batch3/gen_pmc_ctrl/verified_h14/) and the committed test differ only in the docstring (the dependency paragraph replaced
here, the pin-off manifest statement and the plan anchor's commit id corrected under CM141), one comment and the two not_hit reason strings of
bins_not_hit (which feed the rendered header); no fire-check or expectation code differs. The committed test is 0383702cd933 and its runs above
were re-done against the out_head18 build with that text as the Python root (a scratchpad copy of a detached archive of HEAD with the corrected test),
so their headers name it.
Staged entries (dv/auto_dv/work/test-writer/gen_testlist_entries.yaml, sha256 9c8aed00c141 as handed, 32fd0a2d0b3f after the pin-off argument
was quoted for YAML and its description corrected under CM141; merged into the testlist at c0d12f4 and bb3a0a6): gen_test_pmc_ctrl (tier check, 3 seeds,
measured false until the PMC covergroups are built), gen_test_pmc_ctrl_pin_off (tier check, 1 seed, --pin off with the pin plusarg) and
gen_test_pmc_ctrl_red (pinned to TP-PMC-022, red_expect on fire_tp_pmc_022, matched against the retained pinned red's harness line); the
library self-test passes in the staged form. Verified from a detached archive of HEAD with the group overlaid
(dv/auto_dv/work/test-writer/head_final_selftest_pmc.log names the HEAD).
Write corners (the T-235 landing review, CM123): every program here carries the review's corner (1), a minstreth write that leaves the high
word unchanged (`csrrc t1, minstreth, t5` with the high word 0: seed 1 pc 0x8000509c, seed 2 0x800052b0, seed 3 0x80005008), and none carries
corner (2), a minstret write followed at gap 1 by a minstreth write (other counters do pair up back to back). The runs above are on the shim
with those two corners fixed (73ff075); the same programs on the pre-fix shim (out_head17, an export of 5cf028e) also passed with 0
comparator mismatches, and why the misclassified write produced no visible difference there is tb-infra's to state in its record. Of the
five CM123 minors owed to landing 11: no program has a counter write right after a Zcmp or Zcb op; every program has two minstret low-word
writes after ended inhibit episodes (seed 1 at 0x80001c48 with IR = 1 and 0x8000506c with IR = 0, seed 2 at 0x80001e40 and 0x80005288,
seed 3 at 0x800022ac and 0x80005018), none within reach of a wrap into the high word (the largest low word written is 0x51f6abb0 with under
8000 retirements to follow), so the writes-after-inhibit path is exercised and the low-word carry corner is not; no program has a TB-side
counter write (the test issues no bridge CSR write). Scan: dv/auto_dv/work/test-writer/pmc_t235/counter_write_scan.log.
Review of the landing (CM141): the pin-off entry names the group manifest, which is keyed by test name and declares the pin-on bins, so the
dropped-branch bins (cp_pin.off, cr_en_pin_effect.en_off_drop and their kin) are declared by no manifest; under measured false that is latent,
and the docstring, the two not_hit reasons and the staged entry's description now say so instead of claiming the pin-off entry carries them.
The own pin-off manifest (a pin-aware declare_bins() and a second manifest under fcov_expectations, a joint landing since the covergroup set
reads every manifest) comes with the group's promotion to measured. The manifest is re-rendered for the reason text (header lines only, 204 bins
unchanged; gen_test_pmc_ctrl.fcov.yaml c3f77460af5d), and the docstring's plan anchor drops its commit id.

## 10. Retained-log integrity: the ugrep -I hazard and the retention-completeness check

In this session's Claude Code tool shell, and there only, `grep` is an injected function that re-execs the Claude Code binary as
ugrep with `--ignore-files -I` (measured with `type grep` on 2026-09-04; `bash -lc` and `bash -ic` for the same account both
resolve grep to /usr/bin/grep, no ugrep sits on PATH because it lives inside the CLI, and no tracked doc records the wrapper, so a
reader in another shell cannot reproduce it). The flow's own commands run under `bash -lc`, so every grep inside the checked-in
scripts is GNU grep and none of this reaches them. Under that wrapper a recursive grep rooted at or above dv/auto_dv silently
skips the ignored work/ tree, and `-I` drops a file it deems binary even when that file is named explicitly, returning rc 1 with
no output, which is indistinguishable from the pattern being absent. Either would let a count read low and look clean. Audited
over this batch's records at the Orchestrator's request; the full measurement is under
work/test-writer/gen_watch_answer_grep_I.md.

No count in these records could have come from a suppressed grep, for two independent reasons. First the suppression cannot reach
the files: every file in gen_tdd_logs/test_writer (701, the manifest's 700 subjects plus gen_manifest.md) holds no NUL byte and
decodes as ASCII, as do gen_tdd_batch1/2/3.md and gen_critic_response_batch3.md, so -I cannot drop any of them named or recursive;
on a named retained log the wrapper, `command grep` and `command grep -a` return the same count at rc 0. Second the numbers were
not grep-derived: the manifest's bytes and md5 columns and its row count come from stat, md5sum and a row loop, re-derived as 700
rows and 0 bad, and the log-derived figures re-derive from the retained logs by byte-based match, giving GEN_TEST_BINS n=204 and
UVM_ERROR : 0 in all four green gen_pmc_ctrl logs and fire_schedule_applied ok=True reaching 6 of 6, 15 of 15, 12 of 12 and 6 of
6. Both reds fail exactly one item and it is the item the record names: fire_tp_pmc_022 at 46 words compared with 1 mismatch, and
fire_tp_pmc_023 at 170 words with 1 mismatch. Neither red log contains the string UVM_ERROR anywhere, which is correct rather
than suppressed: these tests fail through a python AssertionError on the cocotb path, so a red carries no UVM_ERROR summary line
and no record here claims one.

Retention completeness is the gap shape the row-verify check cannot see, because a log owed a manifest row and missing one never
appears as a bad row. Measured in both directions: 700 manifest rows against 701 files on disk, 0 subject files with no row,
0 rows pointing outside the directory, and 0 rows failing size or md5, so no retention gap exists in these records. No
trace_core_*-shaped file exists anywhere under committed dv/auto_dv/evidence either; the nested-.gitignore case measured under the
export copies reaches only the working copies under work/, which are never the retained record.

## 11. Bridge cycle-slot service (library; the irq-entry group's first landing)

WHAT WAS WRONG. The bridge carries one cycle-threshold slot (gen_bridge_if.sv:24-25, :35, :77-80) and every
GenTest.wait_cycles caller wrote it directly. run() runs the schedule runner and stimulus() as concurrent tasks, so
a stimulus that waits on cycles overwrites a pending target: in the irq red at seed 694904681 an eight-cycle poll
took the runner's c11664 boundary, the whole phase group applied at cycles 77-82 (sim_stdout.log:44, :68), and the
run carried the storm interrupt regime from cycle 77 to the end. The check reported it honestly at :367.

THE FIX. lib.CycleWaiters holds every pending target; GenTest arms the slot only with the earliest, re-arms after
each hit, and wakes only the waiters a hit reaches. wait_cycles registers and awaits its own event, so the slot has
exactly one writer. run_schedule needs no change and got none: it reaches the fix by calling wait_cycles.

WHAT IS PROVEN HERE, and it is deliberately less than the fix.
  - The waking POLICY, red before green. Against a stand-in that behaves as the bridge did (one target, last writer
    wins), the far waiter wakes at the near waiter's hit and never wakes at its own: two assertions fail, which is
    the defect in nine lines. Against CycleWaiters all pass, plus a hit past several targets waking all of them, a
    dropped waiter leaving the others armed, and each waiter keeping its own budget. Retained at
    gen_tdd_logs/test_writer/gen_fu_cycle_slot_service.log with its commands and the filter on its self-test line.
  - The SINGLE-WRITER property, measured: one occurrence of evt_cycle_target.value in the whole tests tree.

WHAT IS NOT PROVEN HERE. The cocotb layer: the service task, the Event handshake, the _edge_or_eot interaction
when the program ends mid-wait, and the re-arm when a nearer target arrives while the service waits. Those are
simulator behaviours and the log says so itself. Two head-mode runs after this commit prove them: a scheduled entry
with the runner as sole waiter, expected every phase at its own cycle; and the irq red at 694904681, expected the
idx=1 group not applied at cycle 77. A defect found there is fixed inside this group before GROUP COMPLETE.

WHY THE POLICY IS A SEPARATE CLASS. So the red could run without a simulator. Splitting the waking rule from the
cocotb plumbing is what let the defect be reproduced and the fix demonstrated at all; a service written as one
piece would have had no red until a wave was free.

WORDS OVER READINGS. On the fault this entry exposed, three of my inferences were corrected while the evidence I
gathered was right each time: I called a record internally inconsistent when the fetch was wrong and the record
faithful; I said the wrong stub ran under the wrong cause when the cause was correct; and I made a point of "three
slots" when the third address was a pc+4 link value. The finding survived because the three slot words and the two
record lines were quoted. Quote the words; label the reading as one.

## 12. PMP step 1 promoted to measured: three manifests shaped by a 40-seed block

WHAT THE MANIFESTS REST ON. runtime-2's PMP block (dv/auto_dv/work/runtime/done/gen_pmp_40seed.yaml
and gen_pmp_40seed_bins.txt), pinned to 218e9f3, coverage on, unmeasured, base seed 218090305, 407 bins
of the four gen_pmp covergroups, per-bin per-seed counts from one urg report per test rather than a
merged one, because a merged report's per-bin test column caps at ten tests with no marker.

THE DENOMINATOR IS 39 FOR THE WARL ENTRY, NOT 40, and the manifest renderer emits no header, so every
WARL reason line carries "of the entry's 39 measured seeds" instead. The missing run is a defect in a
committed generator, not in the flow: at seed 230969025 gen_pmp_csr_warl_prog.py asserts on its own
draw, "TP-PMP-003 mml0: no reserved-bit write drawn" (gen_pmp_csr_warl_prog.py:615, reached from
build() at :1066 through the tp003 block at :1062), so no program was generated and no result was
written. The fix joins the generator-fixes group; a measured entry whose generator asserts on a seed
refuses a round.

WHAT EACH ENTRY DECLARES AFTER THE FLIP, by the rule that only a bin hit at EVERY seed of its entry
may leave that entry's manifest:

  entry                    seeds   declared   stays   bins_not_hit
  gen_test_pmp_csr_warl       39        260     179             81
  gen_test_pmp_mseccfg        40         26      26              0
  gen_test_pmp_lock           40         41      39              2

The two coverpoints called out before the wave came back asymmetric, which is what the every-seed rule
exists to catch: cp_mml.mml1 is every-seed for csr_warl (39/39) and mseccfg (40/40) but 18/40 for lock,
and cp_rlb.rlb1 is every-seed for lock and mseccfg but 32/39 for csr_warl. Neither is safe to declare
from all three, and the two entries that are safe differ between them.

THREE BINS ARE DECLARATION-CLASS, NOT STIMULUS GAPS, and each names the mechanism read out of the
committed source rather than a label:
  - gen_pmp_cfg_write_cg.cr_res_op.nonzero_csrrc. The cross samples the ATTEMPTED word, and a
    clear-type write presents the read-back value with its mask cleared. This implementation stores no
    reserved pmpcfg field (ibex_pkg pmp_cfg_t carries lock, mode, exec, write and read only), so bits
    6:5 read zero and no csrrc can present them non-zero. csrrs and csrrw reach their legs of the same
    cross at every one of the 39 seeds, which is the control that makes this a property of the op
    rather than of the draw.
  - gen_pmp_addr_write_cg.cr_self_lock.locked_rlb1_written and cr_tor_lock.nl_tor_rlb1_written. The
    sampler sets self_locked as the entry's lock bit AND NOT mseccfg.RLB, and next_locked the same way
    for the next entry (gen_fcov_pkg.sv). So cp_self_lock.locked and cp_rlb.rlb1 are mutually exclusive
    by construction, as are cp_next_cfg.next_locked_tor and cp_rlb.rlb1, and no stimulus can reach
    either cross bin. The lock entry DOES rewrite locked entries under RLB=1 in its RLB phase; the
    classifier does not label those samples locked. This is reported to the covergroup and plan owners.

CG-PMP-014 (gen_pmp_table_state_cg) IS DECLARED BY NONE of the three, on the DV Lead's ruling that it
is an expected-from-random-tests covergroup: its items include Phase 2 random-stimulus work, its
coverpoints are whole-table shape properties no targeted test drives through, and locking is sticky so
a run that reaches all-locked cannot return. Its bins are credited from the merged report.

measured_seeds is stated ABSENT: the field does not exist at this HEAD and the manifests render
without it.

WHAT IS NOT CLAIMED HERE. Every one of the 119 runs in the block reads FAIL, on the rule that an entry
declaring bins must have a manifest. That rule fires in finish(), after sampling, so the coverage the
counts come from is real; the positive control's own database carries all four covergroups with
non-zero counts where the identical control at the previous commit carried none. The flip is what makes
these entries pass again, and until it lands the three entries fail at HEAD.

## 13. The retirement floor becomes an identity: a check that could not catch what it was for

WHAT WAS WRONG. Every directed entry ends its verdict with the program's own retirement floor read out
of the IMAGE and the same number recomputed by the imported module:

    floor = lib.program_min_retired(self.image)
    self.check("...", retired >= floor >= p.min_retired, f"retired {retired} (program floor {floor}, plan {p.min_retired})")

Those two numbers are equal BY CONSTRUCTION for a matched pair: the generator writes gen_min_retired
into the image and the plan recomputes it. Compared with ">=", a mismatched pair passes whenever the
newer program is longer. So the one check positioned to notice that a program and its checker came
from different generator versions could not notice it.

HOW IT SURFACED, and the attribution is not mine to soften. A generator sweep built its images from
edited generators in one root while importing its Python from a mirror synced two days earlier; the
Runtime Manager found and reported that, and retracted three blocks of results. Before that, the same
runs read as 57 fire-check failures against one edited generator, which looked like a design bug in
it. The verdict line above printed both numbers in every one of those runs. Neither the run's owner
nor I read them.

THE CHANGE. program_min_retired takes the plan's value as an optional second argument and asserts
equality when it is given; the fifteen directed entries pass it, each with the expression that names
its plan in its own scope. gen_test_boot_retire is deliberately exempt: it is a riscv-dv entry whose
floor is an instruction count rather than a plan value, and the library skips the identity for any
entry whose sidecar names a riscv-dv test. Two verdicts that repeated the comparison the identity now
owns are simplified to "retired >= floor".

THE RED AND THE GREEN, on one real image and two real plan values, retained at
gen_tdd_logs/test_writer/gen_fu_floor_identity.log with the proof script folded in:
  the image's gen_min_retired word          3332   (built from the pre-fix generator)
  the plan of the generator it came from    3332
  the plan of the COMMITTED generator       3065   (what a stale import hands the checker)
  committed library, mismatched pair        3332 >= 3065 is True, the fault escapes
  changed library, no plan given            3332, unchanged
  changed library, matched plan             3332, passes
  changed library, mismatched plan          AssertionError naming both numbers and the mechanism

THE SELF-TEST PASSES, exit 0, and it now carries this policy as a case of its own: a stub image with
a gen_min_retired symbol asserting all four arms, no plan given returning the image's word, a matched
plan passing, a mismatched plan raising, and a riscv-dv sidecar exempt because its floor is an
instruction count. The self-test had been exiting 1 on one pre-existing case unrelated to this
change, the irq red entry having no retained pinned-red log; that log is retained in this touch and
the case is satisfied. An earlier draft of this section and of the retained log said the self-test
exits 1 either way, which was true when written and is not true now.

WHAT THIS IS NOT. It is not the stronger check. Two plans can coincide on a number, and one of the
retracted runs did exactly that, printing "reports 761 (k 761)" while the floor disagreed at 3862
against 3802; two files cannot coincide on a digest. The Runtime Manager owns that half as a flow
item, threading the generator path and its recorded sha256 into the simulation, and the library will
grow the digest arm beside this identity rather than a second check. This identity is the cheap
always-on half that needs no plumbing at all.

ONE THING NOT PROVEN, recorded because it would be easy to imply otherwise. While chasing the same
failure I found and fixed a real defect in gen_bit_ratified_prog.py, where the derived x0 probe set
held three mnemonics that the draft probe set already covered, so each was probed twice. That fix
stands on having read the source. Whether the duplicate could ever have changed a result is untested,
because the failure it was proposed to explain never existed.

## 14. Declared bins against the every-seed bar: twelve entries, three instruments, one withdrawal

WHY THIS EXISTS. A DECLARED bin is a per-run guarantee: the entry promises it on every run, and the
functional-coverage check fails a run that misses one. Round 1 selected its entries at three seeds
from one base seed. Round 2 changes the base by design, so a declared set calibrated on the old base
is not evidence for the new one. A bin produced at 6 of 40 seeds passes a fresh three-seed draw with
probability 0.0034; its three-of-three in round 1 was the selection criterion, not evidence for it.

THREE INSTRUMENTS, and this record says per entry which one decided it, because they are not
interchangeable:
  HAND MAPPER   a reader written against one generator's actual semantics, calibrated so that any
                bin the committed round report says was hit must resolve and be non-zero.
  SIMULATION    runtime-2's 40-seed unmeasured sweep with per-test attribution. Decides any bin,
                needs no mapper, and is authoritative where the two disagree.
  (WITHDRAWN)   a generic mapper. See the withdrawal below; it decided nothing.

TWO COUNTS PER ENTRY, NEVER ONE. The count of declared bins found under the every-seed bar, and the
count of declared bins the reader could NOT examine. A line reading "0 under the bar" is read as
clearance for the whole declared set; for an entry whose reader examined a quarter of it, that
sentence would mislead while every word of it stayed true. The DV Lead required this after
runtime-2's classification showed the case concretely, and runtime-2's sweep blocks carry the same
pair.

    entry                     declared  instrument   under the bar   not examined
    gen_test_bit_ratified          617  hand mapper   0 (was 8)                543
    gen_test_cmp_zca               300  hand mapper   0 (was 3) + 12 unproven  217
    gen_test_isa_alu               563  simulation    pending                  563
    gen_test_mul_mul               338  simulation    pending                  338
    gen_test_cmp_zcmp_basic        325  simulation    pending                  325
    gen_test_mul_div               196  simulation    pending                  196
    gen_test_isa_cti               184  simulation    pending                  184
    gen_test_csr_trap_setup        146  simulation    pending                  146
    gen_test_isa_shift             120  simulation    pending                  120
    gen_test_cmp_zcb                96  simulation    pending                   96
    gen_test_rst_boot                6  simulation    pending                    6
    gen_test_csr_access              4  simulation    pending                    4

WHAT THE HAND MAPPERS FOUND, and it is the whole case for the precondition. Eleven bins that these
two entries DECLARE hit are produced at fewer than 40 of 40 seeds by the committed generators: three
pack equal-operand legs (cr_op_eq.pack_no, packh_no, packu_no), five rs1_eq_rs2 legs (cr_op_same for
max, minu, sh1add, sh2add, sh3add) and three next-length legs (cr_insn_next.c_addi_n16, c_j_n16,
c_slli_n16). The thinnest, c_j_n16, stands at 6 of 40. Both entries run at three seeds, so they were
passing by coincidence. The generator work in this group takes that eleven to zero; the twelve
"unproven" on cmp_zca are memory-form alignment legs whose addresses the reader refuses to place
after a line the assembler may compress, and the simulation decides those.

A GENERIC MAPPER WAS ATTEMPTED AND IS WITHDRAWN, recorded because the withdrawal is the finding. It
resolved a declared bin by matching the bin's class token against tag VALUES in the generator's plan,
with no link to the coverpoint the bin belongs to. Two facts killed it:
  - Its one positive finding was gen_bit_count_cg.cp_single_pos.p16 at 6 of 40 seeds. Checked against
    the generator before it was reported: the string p16 in that plan belongs to orc.b operations
    tagged cls=p16, while the declared bin is a single-bit POSITION in a bit-count covergroup. The
    match was spelling, not semantics.
  - Adding one rule, refusing any value carried by more than one tag key, moved gen_test_isa_alu from
    367 resolved to 172. A number that halves when one guess is removed was never a measurement, and
    the survivors have no better claim than the ones that went.
Its calibration could not catch either: the control flags a resolved bin at zero that the report says
was hit, and a mis-resolution landing at 6 of 40 passes that test. So the ten entries have no
emit-level reading at all, and the cost of a real one is one hand mapper per generator, which is what
the two above took.

WHAT THE SIMULATION HAS DECIDED SO FAR:
  gen_test_cmp_zca   25 of 40 clean; the other 15 each miss exactly ONE declared bin, nine on
                     cr_insn_rdfull.c_swsp_x8_15 and six on c_swsp_x3_7, with no fire-check failure
                     in the forty. Both bins are in the 217 the hand mapper does not examine, which
                     is the concrete case for the second count.
  gen_test_pmp_csr_warl  its declared set is PROVISIONAL, not cleared: the shaping block ran 39 of 40
                     seeds and the missing one is a generator-class miss, seed 230969025, where the
                     committed generator asserted on its own draw. That makes the sample biased
                     rather than merely smaller. The generator fix in this group produces a program
                     at that seed and at three others it also refused, and a 40-seed re-sweep clears
                     it.

WHAT IS NOT CLAIMED. No entry in the simulation rows is cleared or condemned by this record; those
rows are pending and the sweep decides them. And a hand mapper's "0 under the bar" clears only the
bins it examined, which is why the fourth column is beside it rather than in a footnote.
