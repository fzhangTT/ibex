# Critic verdict: test template, fourth review (commit b0d6a3f, Test Writer retention landing), N-1 closure

Artifacts at commit b0d6a3f (sha256 first 16 hex, lines):
- dv/auto_dv/tests/gen_test_template.py                     4eefff151cd87b83  374 (CheckResult, witness_epilogue, plan_bins default)
- dv/auto_dv/tests/gen_test_lib.py                          b2fffce3b7a9d960  533 (structure check rewrite, plan_bins, testlist_entry)
- dv/auto_dv/tests/gen_test_boot_retire.py                  c5afb06821af451f   42
- dv/auto_dv/tests/gen_fixtures/ (15 files: 11 gen_ut_*.py, gen_report_channel.S, gen_report_fixture_map.h, gen_run_fixture.sh, gen_ut_manifest_stale.fcov.yaml)
- dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_manifest.md  7b485e1015427d5f  165 (154 rows)
- dv/auto_dv/evidence/gen_tdd_test_template.md              2af43f4b87a79123  289 (Section 8 added)
- dv/auto_dv/evidence/gen_critic_response_test_template.md  692c1813f70f1b0d   94 (rows CM3-1..7, CR2-N-1..3, CR3-N-1, CR3-L-1..3)
- dv/auto_dv/docs/gen_test_template_api.md                  664bd34d41088e65  193 (Section 9 structure rules and witness epilogue)
Also in scope because they decide my open findings: commit 38d1262 (T-109, 11:15Z) and dv/auto_dv/flow/gen_testlist.yaml at b0d6a3f.
Date: 2026-09-03T11:31Z   Role: Critic   Previous: v3 at 566a601 (REQUEST-CHANGES on N-1 alone; L-1..L-3). The cross-model review of
this commit was not read.

CRITIC VERDICT: APPROVE (N-1 closed; v3 L-1..L-3 closed; two new lows)

## 1. N-1: retention

- Logs: the manifest has 154 rows; every committed copy matches its md5 and byte count, and every row's source under
  dv/auto_dv/work/test-writer/ still exists and has the same md5 (154 of 154), so the copies are byte copies of the
  runs I audited in v2, v3 and the batch-1 verdict. No committed file under gen_tdd_logs/test_writer/ is missing from
  the manifest; every name carries the gen_ prefix.
- Fixture sources: 15 files under dv/auto_dv/tests/gen_fixtures/. Ten of the eleven Python fixtures are byte-identical to
  the work copies that produced the Section 6 and 7 runs or differ only in the first docstring line ("committed
  fixture, never a testlist entry" for "working file": 2 diff lines each, checked for all five); gen_ut_drain_probe,
  gen_ut_report_skip, gen_ut_manifest_missing and gen_ut_manifest_stale are new. gen_run_fixture.sh puts the clone root
  and dv/auto_dv/tests/gen_fixtures on PYTHONPATH, and the Section 8 runs import exactly those module names
  ("Found test gen_ut_drain_probe.gen_ut_drain_probe", "... gen_ut_sched_vacuous ..."), so the retained runs are
  reproducible from the committed sources.
- Section 8 runs, decisive lines found in the committed copies: ret2_drain_probe GEN_TEST_DRAIN waited cycles=40 and
  fire_schedule_applied PASS (the R2-4 drain wait exercised); ret2_report_skip "report channel skipped a store
  (0 -> 2)" FAIL as designed (my N-2 / v3 L-3 red); ret_sched_vacuous still red; ret_boot_green_s1 and ret_cmp_zcb_s1
  PASS with the new check() / finish(); declbins_cmp_zcb_s1 and declbins_bit_draft_s1 PASS with GEN_TEST_BINS n=110 /
  n=480 and the manifest check satisfied; declbins_manifest_missing fails "declares 110 bins but has no manifest";
  declbins_manifest_stale fails "109 in the manifest, 110 declared". The manifest check now has a green, a missing red
  and a stale red.
- Host side, run by me from a clean archive of b0d6a3f: gen_test_lib --self-test PASS over the nine committed tests
  (with the refused sources: alias base, module-level assignment, setattr, nested class, direct COV_WITNESS,
  cycle_clause_true outside fire_*, layers_required = False without a measured: false entry; parser fixtures with the
  automatic form and comments); gen_fcov_manifest --self-test PASS (68 bins for gen_reg_schedule, 86 excluded).
N-1 CLOSED.

## 2. My v3 lows

- L-1 layers_required = False unrestricted: CLOSED. check_test_source refuses it unless the class's name has a testlist
  entry with measured: false (the committed flow testlist first, the staged entries second) or an allowlisted reason
  (LAYERS_OPTOUT_ALLOWLIST, empty). At b0d6a3f all eight batch tests and both boot entries are in the committed flow
  testlist with measured: false, so the refusal rests on the committed file today. See L-2 below for the fallback.
- L-2 parser fallback fixture: KEPT with a reason (both parser fixtures stay; when REGIME_SET_CONSUMED exists the
  rendered set is additionally checked to name known knobs; equality against the parse is deliberately not asserted).
  Accepted.
- L-3 skip-path red: CLOSED (gen_ut_report_skip, ret2_report_skip).

## 3. The witness protocol as landed (plan v2f, my C-1 / C-2 on the Python side)

- check() records a CheckResult with cycle_clause_true, allowed only on the TRUE branch of a fire_tp_* clause; finish()
  runs witness_epilogue() before the handshake and issues COV_WITNESS for exactly the passed results with
  cycle_clause_true, ids restricted to the entry's witness_ids, codes from the rendered WITNESS_IDS; a foreign id, a
  missing table or a missing command fails loud. The structure check refuses the COV_WITNESS token anywhere in a test
  and cycle_clause_true outside a fire_* self.check. This is C-1 as I asked. C-2's dispatcher side is TB Infra's.
- Not yet exercised: no batch-1 item carries the cycle-clause marker, WITNESS_IDS is {} until TB Infra renders it, so
  no run issues a COV_WITNESS and the epilogue's fail-loud paths are code only (the transcript says so). Low L-4.

## 4. Effect on the batch-1 verdict

Commit 38d1262 (T-109) removed the empty declare_bins() override from all eight batch tests; they now inherit
plan_bins(), the manifest generator's own derivation, and finish() compares it with the rendered manifest (green on
bit_draft and cmp_zcb above). My batch-1 H-1 is therefore closed at 38d1262 (to be recorded in the batch-1 re-review).
Batch-1 M-1 stays open: the default declares the WHOLE group's bins, unbuilt items included, so each test must declare
its built subset (or the groups split) before the covergroups land. The template supports it (a test "hitting a subset
declares that subset"); the plan_group attribute and the declare_bins hook are the places.

## 5. New lows

- L-4 The witness epilogue's fail-loud paths (foreign id, missing WITNESS_IDS, missing command) and one green witness
  have no run yet; a red and a green are owed when TB Infra renders WITNESS_IDS and the dispatcher row (first marked
  item, plan Section 1.3).
- L-5 [S5 no hardcoded paths] gen_test_lib.testlist_entry() reads dv/auto_dv/work/test-writer/gen_testlist_entries.yaml as
  its second source, a gitignored file, so the structure check's layers_required decision can differ between a clean
  tree and the Test Writer's working tree. Acceptable as a bring-up convenience only while Runtime copies entries by
  hand; drop the fallback when entries land with the tests.

## 6. Principle walk of the new code

S2 place the check where the failure lands: the witness epilogue runs after fire_check() and before the handshake;
check_manifest_matches names the missing and extra bins. S4 honesty: Section 8 states what was not exercised. S5 single
source: plan_bins reuses the manifest generator's code; WITNESS_IDS and the command come from the rendered package.
S6 triad: reds for the drain wait, the skip path, the missing and the stale manifest; the vacuous runner kept red.
Conformance PASS apart from L-5.
