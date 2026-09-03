# Critic verdict: test template, third review (commit 566a601, Test Writer second fix set)

Artifacts at commit 566a601 (sha256 first 16 hex, lines):
- dv/auto_dv/tests/gen_test_template.py        e6f6f2e802fbd581  334
- dv/auto_dv/tests/gen_test_lib.py             ddaafd04f4fcf78b  382
- dv/auto_dv/tests/gen_fcov_manifest.py        3fdc4dc089868108  289
- dv/auto_dv/tests/gen_test_boot_retire.py     2bc25e4fba58c2e6   45
- dv/auto_dv/docs/gen_test_template_api.md     7bf340a75011651f  163
- dv/auto_dv/docs/gen_test_writer_plan.md      98c1f32c87b2013d  223
- dv/auto_dv/evidence/gen_tdd_test_template.md 3058aedb9b02d5e9  260 (Section 7 = the second-round runs)
- dv/auto_dv/evidence/gen_critic_response_test_template.md  23f89d6dc6a7123d  57 (rows for my v1 M-1..M-5, L-1..L-6)
Date: 2026-09-03T10:09Z   Role: Critic   Previous: gen_critic_test_template_v1.md (746af6f) and _v2.md (98c2ade), both
REQUEST-CHANGES. The round-2 cross-model artifact was not read before this verdict.

CRITIC VERDICT: REQUEST-CHANGES (one medium left: the fixtures and logs that prove the fixes are not committed)

Every finding of my v1 is closed in the committed code and proven by retained runs; the layer-gating medium is
closed by a derived consumed-knob set and a loud setup failure with its own red. What remains is my v2 N-1: the eight
fixture sources and the twenty fix-run logs that are the TDD evidence for M-1, M-2, M-3 and L-1 live only under the
gitignored work tree. One retention commit closes this verdict.

## 1. My findings at 566a601

| Finding | Status | Verified |
|---|---|---|
| v1 M-1 vacuous schedule check | CLOSED | reached from the counts at the end-of-test edge; R2-4 race fix (`hit or count <= self.cycle()`, the runner drained before the check). Runs: prefix_race_c1924 shows the spurious FAIL (`reached 2 of 2, applied 1`), postfix2_race_c1924 PASS with the phase applied at cycle 1924; postfix2_sched_vacuous FAIL / postfix2_sched_sound PASS. |
| v1 M-2 zero recorded checks | CLOSED | `self.checks` guard in finish() plus the host AST structure check (gen_test_lib.py check_test_source: hooks only, at least one self.check, no literal ok); postfix2_zero_check FAIL with the named message; the self-test refuses three red sources. |
| v1 M-3 hand-typed layer gating | CLOSED | REGIME_KNOBS = every yaml knob; CONSUMED_KNOBS from the rendered constant when present, else parsed from apply_knob in gen_env_pkg.sv (self-test on a fixture and a negative file; () on the committed tree, which has no apply_knob); `layers_required = True` by default fails setup when a declared knob has no consumer (gen_test_template.py:184-186), red postfix2_layers_required; the API row (:61) and Section 8 agree. Residual L-1 below. |
| v1 M-4 generator inputs uncommitted | CLOSED | with bc9dba9 landed the manifest self-test passes from a clean archive of 566a601 (`67 bins, 0 dropped; 86 excluded coverpoints`); the docstring says the generator validates, never expands; the "122" sentence is gone from the writer plan. |
| v1 M-5 re-typed encodings | CLOSED | removed at 98c2ade, unchanged. |
| v1 L-1 forked-task failure path | CLOSED | postfix2_stim_raises: `AssertionError: GEN_TEST_FAIL gen_ut_stim_raises: deliberate failure inside the forked stimulus()`, TESTS=1 PASS=0 FAIL=1. |
| v1 L-2 pass-code literal | CLOSED | lib.TOHOST_PASS / TOHOST_FAIL, imported by the test. |
| v1 L-3 heuristic floor | CLOSED | stated in the docstring with the observed range. |
| v1 L-4 log labelling | CLOSED | Section 7 header states where every quoted line lives. |
| v1 L-6 wait_* return | CLOSED | API :74. |
| v2 N-1 fixtures and logs not committed | OPEN (medium) | see section 2. |
| v2 N-2 report-channel red uncited; no red for the skip path | PARTLY | report_red is cited once in the evidence; the skip-detection assert (`report channel skipped a store`) still has no red. Low. |
| v2 N-3 single trigger kind in the API | CLOSED | API section 7 names the mixed-trigger-kind refusal. |

## 2. The remaining medium

N-1 [dv_principles S6, committed evidence]: at 566a601 no file exists under dv/auto_dv/tests/ or dv/auto_dv/evidence/
for gen_ut_sched_vacuous.py, gen_ut_sched_sound.py, gen_ut_zero_check.py, gen_ut_layers_required.py,
gen_ut_stim_raises.py, gen_ut_report_channel.py, gen_ut_report_channel_red.py, gen_report_channel.S, nor for any
of the Section 6 / Section 7 run logs; all of them are working files under dv/auto_dv/work/test-writer/ (gitignored).
The response file has no row for it (its Critic section answers v1 only). The reds that closed four findings cannot
be re-run or re-read from the repository. Required: commit the fixture sources with the gen_ prefix (a fixtures
directory under dv/auto_dv/tests/ is fine) and byte copies of the cited stdout.log / sim.log files under
dv/auto_dv/evidence/gen_tdd_logs/test_writer/ with a manifest row per file (path, source, bytes, md5), as TB Infra did
in T-068; add the Critic v2 rows to the response file.

## 3. Lows

- L-1 `layers_required = False` is a class attribute any test may set; only a comment restricts it to bring-up tests.
  The structure check or the acceptance step should refuse it for entries that are `measured: true`, or the flow
  should treat `GEN_TEST_LAYERS not_applied` as a bad verdict on measured runs (my v1 M-3 alternative b).
- L-2 The consumed-knob parse is a regex over the dispatcher idiom; acceptable as the stated fallback, and it goes
  away when TB Infra renders REGIME_SET_CONSUMED (asked 09:50Z). Keep the self-test's fixture case when that lands so
  the rendered set is still cross-checked against the SV source once.
- L-3 N-2 skip-path red (above).

## 4. Evidence audit (four-point rule) of Section 7

All twelve runs exist under work/test-writer/out_head with the stated stdout.log md5 and mtime (05:45:09.46 to
05:48:14.02 local) and carry the quoted decisive lines: the three race probes (c1923 PASS, c1924 FAIL pre-fix, c1925
PASS), postfix2_race_c1924 PASS, layers_required FAIL, stim_raises FAIL, sched_vacuous FAIL, sched_sound PASS,
zero_check FAIL, boot green PASS with `not_applied ... layers_required=False`, boot red FAIL, report_s1 PASS with
`fire_report_count ok=True reports 3`. Host side, run by me from a clean archive of the commit: gen_test_lib
--self-test PASS (consumed knobs none; gen_test_boot_retire.py passes the structure check), gen_fcov_manifest
--self-test PASS. Nothing in Section 7 is unretained in the work tree; nothing in it is committed (N-1).

## 5. What closes this verdict

The N-1 retention commit with the manifest and the v2 rows in the response file. I verify the md5 of every committed
copy against the work-tree originals and the fixture sources against the runs' module names; nothing else is re-opened.
