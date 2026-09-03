# T-045 evidence: fcov-expectation wiring in the flow (trust triad rule 3)

Owner: runtime. Date: 2026-09-03 (06:34 to 06:38 UTC for the first two proving regressions; the cited LSF job 10931279 was submitted 06:37:22 UTC, dispatched to soc-c-22 the same second and finished 06:37:32 UTC per `bhist -l`; a third regression at 06:56 UTC, below, retains its inputs by construction). Build configuration: `opentitan`. Checker:
`ci/check_fcov_expectations.py` (allowlisted; `--self-test` PASS on this host). Flow module:
`dv/auto_dv/flow/gen_fcov.py`; wiring in `gen_run.py` (`apply_fcov_check`, `--fcov-check`) and
`gen_regress.py` (`post_fcov_checks`, `fcov_summary`, `fcov_policy_failures`); API document
`dv/auto_dv/docs/gen_runtime_api.md` Section 7c (manifest schema, flow step, policy).

## 1. What is proven today, and how

| Piece | Proof | Result |
|---|---|---|
| Manifest schema (`dv/auto_dv/fcov_expectations/<test>.fcov.yaml`: test == stem, owner slug, gen_ bins `cg.cp.bin`, one anti-vacuity note per bin) | `python3 gen_fcov.py --self-test`, cases 1-2 | a well-formed manifest passes; stem, owner, namespace and missing-note violations are each reported |
| Checker verdict on real bin rows | `gen_fcov.py --self-test`, cases 3-6: a fabricated urg text report (`grpinfo.txt` in the exact shape the checker's parser documents: `Group : <path>::<cg>`, `Summary for Variable <cp>`, `Covered bins` / `Uncovered bins` tables) driven through the REAL checker with `--report-dir` | all-hit: PASS, 2/2 bins; one bin with count 0: exit 2, `unmet_bins == [gen_selftest_cg.cp_mode.bin_b]`, flow reason `fcov expectation unmet: 1 declared bin(s) not hit [...]`; a declared bin absent from the report: `MISSING-FROM-REPORT`, unmet; no report dir: exit 1, `fcov expectation unverifiable` (unverifiable is not a pass) |
| Per-test slice selection on a REAL vdb (`urg -tests <vdb minus .vdb>/<cm_name>`), shown by the retained urg work dir, NOT by the checker's own assertion (see Section 2, item 0) | `gen_regress.py --testlist <temp testlist> --tests gen_smoke --tag t045_fcov_wiring2` with a working-file manifest for gen_smoke declaring one bin no covergroup provides (`dv/auto_dv/work/runtime/selftest/gen_smoke.fcov.yaml`); LSF job 10931279 on soc-c-22 (a first pass, tag t045_fcov_wiring, job 10931237, gave the same result but left the checker's work dir in /tmp; not cited) | the run itself PASSes (marker, banner, finish); the post-run check ran the checker on `cov_unmeasured/gen_smoke.vdb` with `--cm-name test_gen_smoke_330815564`; the retained checker work dir `<out root>/regress_t045_fcov_wiring2/runs/gen_smoke_330815564/fcovexp_03ur6ex8/` holds `test_selection.txt` = `<out root>/regress_t045_fcov_wiring2/cov_unmeasured/gen_smoke/test_gen_smoke_330815564` and `urgReport/tests.txt`: `Total tests in report: 1` with exactly that identifier, so the slice URG produced is the single test record of this run; the retained `urgReport/` listing is `asserts.txt dashboard.txt hierarchy.txt modinfo.txt modlist.txt session.xml tests.txt` (no `grpinfo.txt`, no covergroup), so the checker raises `urg per-test report failed` (its message quotes urg's tail, not the missing file) and exits 1; the flow recorded FAIL `fcov expectation unverifiable: checker exit 1 (see fcov_check.log)`; since T-049 the flow names the cause itself: `per-test urg report has no grpinfo.txt (no covergroup in this vdb)`. The temporary testlist and manifest of this run were working files; copies now sit in `<out root>/regress_t045_fcov_wiring2/inputs/` (sha256 2eb15b7fca3658a2..., 438ec68d64c23a30...), and every later regression retains `testlist_used.yaml` and `runs/<run>/fcov_manifest_used.yaml` by construction (regress_t045_fcov_wiring3, Section 4) |
| Collected mechanism and summaries | same regression manifest | `runs[0].verdict: FAIL`, `fcov_check.status: PROTOCOL_ERROR`, `anti_vacuity` note carried verbatim, `fcov.totals: {checked: 1, pass: 0, unmet: 0, unverifiable: 1}`, `fcov.per_test.gen_smoke`, `fcov.covergroups_exist: false`; one-line summary `fcov expectations checked 1 (unmet 0, unverifiable 1)`; dashboard columns "fcov expectation" (per test) and "fcov checked/unmet/unverifiable" (per regression) |
| Manifest-required policy | code path `fcov_policy_failures` | live for the tiers in the testlist header now (empty), and for every measured tier automatically once URG reports a GROUP total in any merge of the regression; tier check exempt; not exercisable until a covergroup exists |

## 2. What remains to be proven at the first covergroup

0. The checker's OWN per-test isolation assertion (ci/check_fcov_expectations.py, the
   "Total tests in report: 1" and exact-identifier check after the urg call) is still unexercised:
   with no `grpinfo.txt` the checker raises `urg per-test report failed` before it reads tests.txt.
   Today's isolation evidence is the flow's reading of the retained tests.txt, not the checker's
   verdict; the first covergroup run exercises the assertion itself.
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

## 4. Addendum: retained P6 refusal run and self-tests (T-038 review minors), third proving run (T-045 review minors)

- `regress_t045_fcov_wiring3` (06:57 UTC, LSF job 10931649 on soc-c-13): the same proof rerun after the T-045 review; the outdir
  retains `testlist_used.yaml` and `runs/gen_smoke_330815564/fcov_manifest_used.yaml` (copies made by
  the flow), `manifest.yaml` carries `testlist: {path, sha256, copy}`, and the run's `fcov_check`
  carries `cause: per-test urg report has no grpinfo.txt (no covergroup in this vdb)`, `declared: 1`
  (from the validated manifest, not from the checker's output), `manifest_copy`, `manifest_sha256`.

- `regress_t045_p6_refusal` (06:42 UTC): a temporary testlist declares `debug_only_plusargs:
  [gen_smoke_intg_flip]` and a measured smoke-tier twin of gen_smoke with `+gen_smoke_intg_flip=5`.
  `gen_run.py` refused the run before any LSF submission: `result.yaml` `verdict: NOT_RUN`, reason
  `debug-only plusarg(s) ['gen_smoke_intg_flip'] enabled in a measured coverage run (P6); run it
  unmeasured (measured: false or --measured no)`, `lsf: null`; the regression records 1 not_run and
  exits 3 (`coverage merge status 'no_vdb'`). Out-tree
  `<out root>/regress_t045_p6_refusal/runs/gen_p6_probe_323273637/result.yaml`. The temporary testlist
  of that run was a working file at the time; a copy now sits in
  `<out root>/regress_t045_p6_refusal/inputs/testlist_p6.yaml` (sha256 52452481b4fabfb4...), and every
  later regression retains `testlist_used.yaml` by construction.
- `python3 gen_regress.py --self-test`: fcov_policy_failures (no covergroup: null manifests pass;
  covergroups exist: smoke null manifest FAILs, tier check exempt; header tier FAILs), fcov_summary
  totals and per-test, summarize counts. `python3 gen_flow_util.py --self-test`: plusarg_enabled
  (`+k`, `+k=1` enabled; `+k=0`, `+k=` not), vcs+ names keep their inner `+`.
- `regress_t045_check3` (06:42 UTC, after the banner-from-sim.log and mandatory-banner edits):
  gen_smoke (LSF 10931376) and gen_cocotb_probe (10931375) PASS with `banner_seen: true`,
  `out_root_fs: wekafs`.

## 5. LSF accounting

Jobs 10931237 (t045_fcov_wiring, first pass), 10931279 (t045_fcov_wiring2, the cited pass), 10931375 and 10931376 (t045_check3), 10931649 (t045_fcov_wiring3); the P6 refusal submitted none. `bjobs -w` after the runs: no unfinished job.
