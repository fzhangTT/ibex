# Critic verdict: test template, second review (commit 98c2ade, Test Writer answers to the 746af6f reviews)

Artifacts at commit 98c2ade (sha256 first 16 hex, lines):
- dv/auto_dv/tests/gen_test_template.py        ee94d1be4a8e1cd8  310
- dv/auto_dv/tests/gen_test_lib.py             148eb01dd272d7bf  284
- dv/auto_dv/tests/gen_fcov_manifest.py        afe6e40d2d97f0c7  287
- dv/auto_dv/tests/gen_test_boot_retire.py     0c0edf458ce75f99   42
- dv/auto_dv/docs/gen_test_template_api.md     fadde4668e4ec0bd  161
- dv/auto_dv/evidence/gen_tdd_test_template.md 87847cbad2522046  219 (Section 6 = the fix runs)
- dv/auto_dv/evidence/gen_critic_response_test_template.md  a53cbb8dec553ced  27 (11 cross-model rows; no Critic row yet)
Date: 2026-09-03T09:57Z   Role: Critic   Previous: gen_critic_test_template_v1.md (746af6f, REQUEST-CHANGES, M-1..M-5, L-1..L-6).
The cross-model artifact for 746af6f was not read before v1; its findings reached me only through the response file.

CRITIC VERDICT: REQUEST-CHANGES

Two of my mediums are closed with real red-then-green fixtures, one is closed by removal, one is downgraded. One
medium (M-3, the layer gating) is untouched at this commit, and the fixture sources and logs that prove the fixes
are not committed anywhere (new N-1). The working tree already shows both being worked on (section 4); this verdict
is on the commit.

## 1. My v1 findings at 98c2ade

| v1 | Status | Verified |
|---|---|---|
| M-1 vacuous fire_schedule_applied | FIXED | wait_eot records eot_cycle / eot_retired; phase_reached() derives "reached" from those counts, not from the runner; missed and early lists; check fails on either. Fixture runs (work/test-writer/out_head, md5 and mtime as the transcript states): prefix_sched_vacuous 8f4f7bf1.. 05:21:35.18 `ok=True applied 1 of 2` (defect shown), postfix_sched_vacuous 6cf265c2.. 05:23:06.83 `ok=False reached 2 of 2 ... applied 1, missed [...]`, postfix_sched_sound 4168f472.. 05:23:10.29 `ok=True reached 2 of 2 ... applied 2`. Closed. |
| M-2 zero recorded checks pass | FIXED | check() counts calls; finish() raises `fire_check() recorded no check` before the handshake. prefix_zero_check c7b630c6.. PASS with no GEN_TEST_FIRE line (defect shown); postfix_zero_check 90f37742.. AssertionError with that message. Closed. |
| M-3 hand-typed layer gating; not_applied passes | OPEN | gen_test_lib.py:25-33 unchanged (both tuples empty, hand-maintained); `GEN_TEST_LAYERS not_applied` still a logged no-op that passes. Only the wording changed (row 7: docstring, API row, testlist description). Blocking. |
| M-4 generator depends on uncommitted inputs | PARTLY, downgraded to L-5 | Both inputs now fail loud with `GEN_FCOV_MANIFEST_INPUT_VERSION` (gen_fcov_manifest.py:92-94, :127-133) and the self-test prints the tree state it ran on. The dependency itself stays until the DV Lead's plan set lands (SHA to be recorded, as the response says). Still wrong: gen_test_writer_plan.md:66 records "122 excluded coverpoints"; today's working tree prints 86 and the committed tree prints nothing. |
| M-5 re-typed bridge encodings | FIXED | IRQ_LINE_BIT, IRQ_FAST_BIT0, IRQ_HOLD, DBG_HOLD, MEM_ERR_BUS, MEM_ERR_KIND and irq_mask() removed; comment names the codegen ask (gen_test_lib.py:39-41). Closed. |
| L-1 forked-task failure path unexercised | OPEN | no row; the working tree has a postfix2_stim_raises run (section 4), not judged. |
| L-2 EOT_PASS_CODE literal | OPEN | gen_test_boot_retire.py:22 unchanged. |
| L-3 +instr_cnt floor is heuristic | OPEN | docstring unchanged. |
| L-4 transcript log labelling and ordering | ADDRESSED | ordering statement under the title; stdout.log named. |
| L-5 (Runtime) "sv_fatal at log line 100" | not the Test Writer's | Runtime added red_fixture handling (984b99d); the reason label stays with Runtime. |
| L-6 wait_* return semantics in the API | carried | not checked further here. |

## 2. New findings

- N-1 (medium) [S6 committed evidence]: every fixture source and every Section 6 log lives under the gitignored
  dv/auto_dv/work/test-writer/ (fixtures/gen_ut_sched_vacuous.py, gen_ut_sched_sound.py, gen_ut_zero_check.py,
  gen_ut_report_channel.py, gen_ut_report_channel_red.py, gen_report_channel.S, gen_report_fixture_map.h;
  out_head/prefix_* and postfix_* runs). Commit 98c2ade adds no file under dv/auto_dv/tests/ and nothing under
  evidence/gen_tdd_logs/. The reds that close M-1 and M-2 cannot be re-run or re-read from the repository.
  Required: commit the fixture sources (gen_ prefix, e.g. dv/auto_dv/tests/gen_fixtures/) and byte copies of the
  Section 6 logs under dv/auto_dv/evidence/gen_tdd_logs/test_writer/ with a manifest (path, source, bytes, md5),
  the pattern TB Infra used in T-068.
- N-2 (low) [S6 TDD]: the report channel (expected_reports, the per-store edge collection and the skip assert in
  wait_eot, gen_test_template.py:217-242) is new template logic. Its retained red (out_head/report_red_s1,
  05:15:08 local, fixture gen_ut_report_channel_red, `fire_report_1` mismatch) is not cited in Section 6, and the
  skip-detection assert (`report channel skipped a store`) and the per-store timeout have no red at all. Cite the
  red; add one for the skip path.
- N-3 (low): row 9 makes a schedule single-kind (c or r). Schedule.derive only ever emits c, so the restriction is
  harmless today, but the +gen_regime_sched syntax section of the API must state it (not verified here).

## 3. Conformance of the fix set (dv_principles, read fresh)

S2 place the check where the failure lands: the schedule check now compares against counts captured at the
end-of-test edge, and the zero-check guard runs before the handshake. S4 honesty: the ordering statement and the
self-test's tree-state line are the right kind of correction. S5 single source: the mirrored encodings are gone;
the literal pass code (L-2) remains. S6 triad: red-then-green shown for M-1 and M-2 with the defect visible in the
pre-fix runs; the evidence is not committed (N-1).

## 4. Working tree ahead of the commit (not judged)

dv/auto_dv/tests/gen_test_template.py differs from 98c2ade (+40 lines across 6 files) and the work tree holds
fixtures/gen_ut_layers_required.py (09:45Z) with run postfix2_layers_required (09:47Z: setup fails loud
"declared regime knobs ... no REGIME_SET consumer"), postfix2_stim_raises, postfix2_race_c1924 and a second
postfix2 set. By their names they address M-3 and L-1; I judge them at their commit.

## 5. What closes this verdict

M-3 closed by a mechanism (a `layers_required` guard that fails setup when a test declares knobs the build cannot
consume, or the consumed set rendered from the TB's single source), with its red committed; N-1 closed by
committing the fixtures and logs; the Critic rows added to the response file. L-1, L-2, L-3, L-5, N-2, N-3 may ride
along.
