# Ibex auto-DV fork — canonical agent instructions

This file is the single source of truth for AI agents in this repo. `AGENTS.md` (codex) delegates
here and mirrors only the Critical Invariants block below.

## Environment & flow

- `source ci/env.sh` first, always (login shell / `bash -lc`; see its header for the supported-shell
  contract). One-time setup and every verified build/run/coverage command: `docs/dv/BUILD_AND_SIM.md`.
- The UVM DV flow lives in `dv/uvm/core_ibex` (Makefile-driven; VCS via `SIMULATOR=vcs`); cosim
  architecture: `docs/dv/COSIM.md`; generated-test interface: `docs/dv/TB_CONTRACT.md` (once WS2 lands).

## DV principles

`docs/dv/dv_principles.md` binds all DV work, hand-written or generated. In one line: realistic
boundary stimulus, intent-derived checking that fails through a collected mechanism, honesty over
green, and the trust triad — TDD, mutation-proof, fcov-expectation — for every new test or checker.

## Cross-model review policy

- The executing model never self-approves.
- Before execution: the plan/spec/testplan is reviewed by the other model (Claude executes ⇒ codex
  reviews; codex executes ⇒ `claude -p` reviews). After execution: the diff is reviewed by the other
  model the same way.
- Review artifacts are committed under `docs/dv/reviews/`, each with a reviewer-identity header (CLI
  version, model ID, reasoning setting) and an explicit review target (commit SHAs / diff scope).
- Verdicts are machine-readable — `APPROVE` / `APPROVE-WITH-CHANGES` / `REQUEST-CHANGES` — and
  gating: no progress past `REQUEST-CHANGES` without a recorded re-review.
- Disagreements with a recorded controller ruling go to the human owner, not back into the loop.
- The `cross-review` skill executes this policy; use it rather than ad-hoc invocations.

## Critical invariants

<!-- CRITICAL-INVARIANTS-BEGIN -->
1. The executing model never self-approves: plans get a pre-execution review and diffs get a
   post-execution review by the other model; a `REQUEST-CHANGES` verdict blocks progress until a
   recorded re-review reaches `APPROVE`/`APPROVE-WITH-CHANGES`.
2. Knowledge-fence: generation sessions must not read fenced DV collateral. Fence rules live in
   `docs/dv/FENCE.md` once WS7 lands; until a fence authority exists, generation sessions are
   NOT permitted at all (fail closed), and infra sessions never paste fenced content into
   allowed files.
<!-- CRITICAL-INVARIANTS-END -->

## Site gotchas

- The `module` command exits 1 even on success — never `&&`-chain it (`ci/env.sh` handles loads).
- Background/completion notifications are unreliable: poll log files and artifacts directly with
  deadlines, and put a watchdog timer on any dispatched work longer than ~5 minutes.
- Clear `PYTHONPATH` around pip operations (`~/.bashrc` leaks package metadata into `pip freeze`).
- Stale `metadata.pickle`: use `make clean` or a fresh `OUT=` after editing testlists/configs.
- Full gotcha list with evidence: `docs/dv/BUILD_AND_SIM.md`.

## Skills index

Skills live in `.claude/skills/` (codex discovers them via `.agents/skills/shared`). Agents live in
`.claude/agents/`. Index (updated as skills land): `cross-review`, `sim-debug`, `regress`,
`lint-check`, `dv-principles-check`, `mutation-check`, `fcov-expectation`, `simple-english`.
Review rubrics (model-neutral prompt files): `ci/reviews/`.
