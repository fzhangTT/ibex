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
flow's red_signature_check). Generator sweep: Section 5 (seeds 1..400, 200 random and 200 flow-derived seeds, every red item at seeds 1..60,
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
The generator at 36e2694 carried the first two (its role draws are unchanged by the fixes up to seed 17's), so the acceptance wave would have
shown them as green failures at about 3 of 40 seeds.

Sweeps on the final generator (sha256 56ef5fe5f695106b), from head_export13 with the touch overlaid:
- gen_b3_pmp_lock_sweep800.log (md5 74999fde11c68c749b373cd8569f1aac): plan() green and seed-drawn red for seeds 1..400, 200 random
  31-bit seeds and 200 flow-derived seeds, every --red-item at seeds 1..60: 2200 runs, 0 failures (the observability
  assertion included); 013 red sites over seeds 1..60 (lock mix of the replaced write): 8 none, 52 some.
- Simulation sweeps on out_head14 (gen_b3_pmp_lock_h13_run_summary.log, md5 8585166c074f75a00580b32cb9d55cc0, one DONE line per
  run; per-run decisive-line excerpts gen_b3_pmp_lock_r013_s<N>_stdout_excerpt.log and gen_b3_pmp_lock_g<N>_stdout_excerpt.log): the TP-PMP-013 red
  at seeds 1..40 fails on fire_tp_pmp_013 alone on 40 of 40 seeds (replaced-write
  lock mix: 4 none, 36 some); the green program at seeds 1..40 passes on 40 of 40
  (GEN_TEST_BINS n=50 equal to the manifest, UVM_ERROR 0 on every seed).
