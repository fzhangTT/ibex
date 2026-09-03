# T-045 evidence: fcov-expectation wiring in the flow (trust triad rule 3)

Owner: runtime. Date: 2026-09-03 (06:33 to 06:36 UTC). Build configuration: `opentitan`. Checker:
`ci/check_fcov_expectations.py` (allowlisted; `--self-test` PASS on this host). Flow module:
`dv/auto_dv/flow/gen_fcov.py`; wiring in `gen_run.py` (`apply_fcov_check`, `--fcov-check`) and
`gen_regress.py` (`post_fcov_checks`, `fcov_summary`, `fcov_policy_failures`); API document
`dv/auto_dv/docs/gen_runtime_api.md` Section 7c (manifest schema, flow step, policy).

## 1. What is proven today, and how

| Piece | Proof | Result |
|---|---|---|
| Manifest schema (`dv/auto_dv/fcov_expectations/<test>.fcov.yaml`: test == stem, owner slug, gen_ bins `cg.cp.bin`, one anti-vacuity note per bin) | `python3 gen_fcov.py --self-test`, cases 1-2 | a well-formed manifest passes; stem, owner, namespace and missing-note violations are each reported |
| Checker verdict on real bin rows | `gen_fcov.py --self-test`, cases 3-6: a fabricated urg text report (`grpinfo.txt` in the exact shape the checker's parser documents: `Group : <path>::<cg>`, `Summary for Variable <cp>`, `Covered bins` / `Uncovered bins` tables) driven through the REAL checker with `--report-dir` | all-hit: PASS, 2/2 bins; one bin with count 0: exit 2, `unmet_bins == [gen_selftest_cg.cp_mode.bin_b]`, flow reason `fcov expectation unmet: 1 declared bin(s) not hit [...]`; a declared bin absent from the report: `MISSING-FROM-REPORT`, unmet; no report dir: exit 1, `fcov expectation unverifiable` (unverifiable is not a pass) |
| Per-test slice selection on a REAL vdb (`urg -tests <vdb minus .vdb>/<cm_name>`) | `gen_regress.py --testlist <temp testlist> --tests gen_smoke --tag t045_fcov_wiring2` with a working-file manifest for gen_smoke declaring one bin no covergroup provides (`dv/auto_dv/work/runtime/selftest/gen_smoke.fcov.yaml`); LSF job 10931279 on soc-c-22 (a first pass, tag t045_fcov_wiring, job 10931237, gave the same result but left the checker's work dir in /tmp; not cited) | the run itself PASSes (marker, banner, finish); the post-run check ran the checker on `cov_unmeasured/gen_smoke.vdb` with `--cm-name test_gen_smoke_330815564`; the retained checker work dir `<out root>/regress_t045_fcov_wiring2/runs/gen_smoke_330815564/fcovexp_03ur6ex8/` holds `test_selection.txt` = `<out root>/regress_t045_fcov_wiring2/cov_unmeasured/gen_smoke/test_gen_smoke_330815564` and `urgReport/tests.txt`: `Total tests in report: 1` with exactly that identifier, so the isolation step works on this flow's vdbs; `urgReport/` has no `grpinfo.txt` (no covergroup), the checker exits 1, and the flow records the run as FAIL `fcov expectation unverifiable: checker exit 1 (see fcov_check.log)` |
| Collected mechanism and summaries | same regression manifest | `runs[0].verdict: FAIL`, `fcov_check.status: PROTOCOL_ERROR`, `anti_vacuity` note carried verbatim, `fcov.totals: {checked: 1, pass: 0, unmet: 0, unverifiable: 1}`, `fcov.per_test.gen_smoke`, `fcov.covergroups_exist: false`; one-line summary `fcov expectations checked 1 (unmet 0, unverifiable 1)`; dashboard columns "fcov expectation" (per test) and "fcov checked/unmet/unverifiable" (per regression) |
| Manifest-required policy | code path `fcov_policy_failures` | live for the tiers in the testlist header now (empty), and for every measured tier automatically once URG reports a GROUP total in any merge of the regression; tier check exempt; not exercisable until a covergroup exists |

## 2. What remains to be proven at the first covergroup

1. `grpinfo.txt` of a real per-test URG slice carries the `gen_<feature>_cg` groups with the bin
   rows in the documented shape, and the checker's parse yields HIT for a bin the test drove
   (positive) and UNHIT for one it did not (negative): one green and one red run per the trust
   triad, recorded in the Test Writer's first test evidence and here as an addendum.
2. Counts summed across instances of the same covergroup name (the checker's rule) match the
   Test Writer's intent when a covergroup is bound at several places.
3. The dashboard GROUP column (grand total) becomes a number and `fcov.covergroups_exist` flips
   the manifest-required policy live on smoke/targeted/full.

## 3. Fence note

While inspecting the checker's urg work directory for this evidence, a glob of `/tmp/fcovexp_*`
listed another workspace's checker output first (the checker's `tempfile.mkdtemp` default is
`/tmp`), and three lines of that foreign report appeared in the runtime agent's tool output. They
were not read further, used, or copied anywhere; the event is reported to the Orchestrator for the
intervention log. Mitigation in the flow: `gen_fcov.run_checker` sets `TMPDIR` to the run directory,
so every per-test report is retained beside its run (`<run dir>/fcovexp_*/urgReport/`) and never
shares `/tmp` with other workspaces.

## 4. LSF accounting

Jobs 10931237 (t045_fcov_wiring, first pass) and 10931279 (t045_fcov_wiring2, the cited pass). `bjobs -w` after the runs: no unfinished job.
