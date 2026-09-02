# Cross-model review — plan/spec file(s): docs/superpowers/plans/2026-09-02-ws4-jenkins-lsf.md

**Reviewer:** codex-cli 0.149.1; run-reported: model: gpt-5.6-sol; reasoning effort: high
**Date:** 2026-09-02
**Target:** plan/spec file(s): docs/superpowers/plans/2026-09-02-ws4-jenkins-lsf.md

---

TARGET: docs/superpowers/plans/2026-09-02-ws4-jenkins-lsf.md@e2f56e1c
[critical][docs/superpowers/plans/2026-09-02-ws4-jenkins-lsf.md:18] The proposed testlist variables are currently unused: `metadata.py` hardcodes both stock testlists, and the Makefile does not pass these variables into metadata. Dry-run checks would pass while real runs silently use stock suites, defeating the dual-suite requirement — add Makefile/metadata plumbing, path-resolution tests, and an actual alternate-testlist gate run.
[high][docs/superpowers/plans/2026-09-02-ws4-jenkins-lsf.md:134] The smoke script duplicates test names and an iteration count outside the authoritative testlist YAMLs, contrary to the Magic-Numbers rubric and `dv_principles.md` single-source-of-truth rule — derive the smoke selection from authoritative YAML or record an explicit policy exemption before implementation.
[high][docs/superpowers/plans/2026-09-02-ws4-jenkins-lsf.md:329] Jenkins parameters are interpolated unquoted into shell commands; this permits shell injection and breaks legitimate values containing whitespace, with the same defect repeated in the Nightly and Coverage stages — pass parameters through environment variables, quote every expansion, construct suite arguments as a shell array, and validate numeric/token inputs.
[high][docs/superpowers/plans/2026-09-02-ws4-jenkins-lsf.md:46] A seconds-resolution timestamp does not guarantee a fresh output directory, and caller-supplied `--out` values can reuse stale metadata — atomically reserve a unique output location and reject any location containing prior metadata or results.
[high][docs/superpowers/plans/2026-09-02-ws4-jenkins-lsf.md:47] LSF must open `<out_abs>/lsf.log` before the submitted script runs, but the plan never creates its parent directory — create the log directory before `bsub`, while preserving the fresh-output invariant for the inner invocation.
[high][docs/superpowers/plans/2026-09-02-ws4-jenkins-lsf.md:97] Because the scripts intentionally omit `set -e`, a failing `source ci/env.sh` will not stop execution unless its status is checked explicitly — require and test an explicit nonzero return when environment setup fails.
[medium][docs/superpowers/plans/2026-09-02-ws4-jenkins-lsf.md:357] Standard Jenkins cron triggers cannot assign `RUN_NIGHTLY` or `RUN_COVERAGE`; with these defaults, the proposed scheduled invocations run Smoke instead — specify a parameterized-scheduler mechanism, API trigger, or separate job configuration that supplies the required parameters.
[medium][docs/superpowers/plans/2026-09-02-ws4-jenkins-lsf.md:358] The LSF execution host must access the Jenkins workspace and output path at the same absolute location, but this requirement is absent — document shared-workspace visibility and verify it during the LSF gate.
Final verdict: REQUEST-CHANGES
