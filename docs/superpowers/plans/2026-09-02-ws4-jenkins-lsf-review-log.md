# WS4 plan — codex pre-review disposition log

Plan: 2026-09-02-ws4-jenkins-lsf.md. Artifacts: docs/dv/reviews/.

## Review disposition (codex pre-review round 1 — REQUEST-CHANGES)

Findings from `docs/dv/reviews/2026-09-02-codex-plan-2026-09-02-ws4-jenkins-lsf-round1.md`, each addressed in rev 2:
1. **[critical] testlist vars unused** — CONFIRMED against `metadata.py:138,141`; new Task 2 plumbs args-list → metadata fields with a red→green check (`check_testlist_knob.sh`) and Task 4 Step 7 adds the alternate-testlist gate run.
2. **[high] smoke selection duplication** — explicit policy exemption recorded (Task 3 header + smoke.sh comment + README §Smoke policy).
3. **[high] Jenkins parameter injection** — parameters now flow through `environment {}` into single-quoted `sh` blocks, quoted at use, suite args built as a bash array; script-side value validation added (Global Constraints + Task 3 selftest checks).
4. **[high] stale/colliding OUT** — `ci_reserve_out`: prior-results rejection + noclobber sentinel ownership; selftest fixtures cover fresh/poisoned/owned/inner-LSF cases.
5. **[high] lsf.log parent missing** — reservation (mkdir -p) happens before `bsub`; inner invocation accepts the reserved dir via the `LSB_JOBID` carve-out.
6. **[high] unchecked env.sh source** — explicit `|| exit 1` with message; fault-injection selftest via `CI_ENV_SH` + `testdata/env_fail.sh`.
7. **[medium] cron cannot set params** — README documents `parameterizedCron` and the three-job-defaults alternative; neither assumed.
8. **[medium] LSF workspace visibility** — Task 4 Step 5 probe before the LSF gate; README §Storage requirement.

## Review disposition (codex pre-review round 2 — REQUEST-CHANGES)

Findings from `docs/dv/reviews/2026-09-02-codex-plan-2026-09-02-ws4-jenkins-lsf-round2.md`, each addressed in this revision:
1. **[high] second injection boundary in the make `--args-list` recipe** — strict value validation chosen (the offered alternative to structured transport): charset rules for `--config`/`--test`/testlist paths (no whitespace or shell metacharacters), with injection and whitespace-path selftest checks added in Task 3.
2. **[high] stdlib pathlib vs runtime-typechecked pathlib3x** — the check script now uses `import pathlib3x as pathlib`.
3. **[medium] unit check bypasses the Make boundary** — Task 2 Step 5 adds a `make -n` recipe check proving both variables reach `--args-list`; the Task 4 alternate-testlist run stays as the end-to-end proof.
4. **[medium] zero permitted for `--jobs`/`--iterations`** — both now require positive integers (`-j0` rejected by make; iterations ≤ 0 rejected by metadata); `--seed` stays nonnegative; selftest checks added.

## Review disposition (codex pre-review round 3 — REQUEST-CHANGES)

Findings from `docs/dv/reviews/2026-09-02-codex-plan-2026-09-02-ws4-jenkins-lsf-round3.md`, each addressed in this revision:
1. **[high] `--test` rejects hyphenated names** — charset now `^[A-Za-z0-9_,-]+$`; positive selftest uses real tests `lh-misaligned,div-01`.
2. **[high] `--out` unvalidated (recursive make expansion)** — resolved `CI_OUT_ABS` validated against the safe-path charset, make receives the absolute path only; metacharacter and whitespace rejection selftests added.
3. **[high] summary-only evidence** — gate evidence is now a directory per gate with raw `regr.log`/`lsf.log`/`dashboard.txt`, reproducibility metadata (commit SHA, VCS version, invocation, wall-clock), and sha256 for uncommitted binaries (dv_principles §6).
4. **[medium] no pipeline timeouts** — pipeline-level 14h + per-stage 2h/10h/12h timeouts; common.sh LSF mode runs `bsub -K` as a trapped child that `bkill`s the job on INT/TERM so aborts do not orphan LSF work.

## Review disposition (codex pre-review round 4 — REQUEST-CHANGES)

Findings from `docs/dv/reviews/2026-09-02-codex-plan-2026-09-02-ws4-jenkins-lsf-round4.md`, each addressed in this revision:
1. **[high] no `--cocotb-module`** — option added (implies `--cocotb`, validated `^[A-Za-z0-9_.]+$`, passed as `COCOTB_MODULE=` and through LSF reinvocation), Jenkins `COCOTB_MODULE` parameter wired into all three stages, selftest checks added.
2. **[high] `bkill -J` on a non-unique name** — the wrapper now parses the exact job ID from bsub's submission line (`Job <NNNN>`) and traps with `bkill "$jid"`; the name stays for observability only.
3. **[high] red→green transcripts not committed** — every task saves its failing and passing selftest/check transcripts to `docs/dv/evidence/ws4-selftest-tdd/t<N>-{red,green}.txt`, committed with the task (Global Constraints rule + per-task steps).
4. **[high] evidence SHA recorded before the code is committed** — Tasks 3–5 now commit the implementation first, run the gate from that immutable commit, record its SHA, and commit evidence separately.
5. **[medium] `allowEmpty*` lets publication silently no-op** — publication moved into per-stage strict `post { always }` blocks scoped to each stage's OUT glob; the global post keeps only workspace cleanup.

## Review disposition (codex pre-review round 5 — REQUEST-CHANGES)

Findings from `docs/dv/reviews/2026-09-02-codex-plan-2026-09-02-ws4-jenkins-lsf-round5.md`, each addressed in this revision:
1. **[high] trap armed after submission parsing (orphan window)** — trap armed before `bsub`; handler kills the child, resolves the job ID from `$jid` or a trap-time `bsub.log` scan, `bkill`s if found; submission-line polling bounded at 120s; mocked-LSF cancellation selftest added (`testdata/lsf-stub/`).
2. **[high] `tee` masks the tested command's exit status** — all four transcript commands run under `bash -o pipefail` and echo the real exit status into the transcript.
3. **[high] blanket `LSB_JOBID` sentinel bypass** — replaced with a random `CI_OWNER_TOKEN` written into the sentinel and exported through bsub; the inner run must present the matching token; match/mismatch selftests added.
4. **[medium] `@` rejected in Jenkins workspace paths** — out-path charset admits `@`; positive `ws@2` selftest added (concurrent builds stay enabled).
