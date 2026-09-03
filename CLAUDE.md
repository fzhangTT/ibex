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
- Reviewer model preference: codex with the `sol`-class model at high reasoning effort when
  available (`gpt-5.6-sol` today); if codex is unavailable, an equivalent-tier Claude model
  (Opus-class or above) reviewing from a fresh session is an acceptable substitute — record which
  was used in the artifact's identity header either way.

## Critical invariants

<!-- CRITICAL-INVARIANTS-BEGIN -->
1. The executing model never self-approves: plans get a pre-execution review and diffs get a
   post-execution review by the other model; a `REQUEST-CHANGES` verdict blocks progress until a
   recorded re-review reaches `APPROVE`/`APPROVE-WITH-CHANGES`.
2. Knowledge-fence: generation sessions are permitted ONLY inside a verified cleanroom export —
   built by `ci/make-cleanroom.sh`, self-verify green. `docs/dv/FENCE.md` is the fence rule file.
   Infra sessions in this full tree are contaminated by design: they never do generation, and
   they never paste fenced content into allowed files.
<!-- CRITICAL-INVARIANTS-END -->

## Site gotchas

- The `module` command exits 1 even on success — never `&&`-chain it (`ci/env.sh` handles loads).
- Background/completion notifications are unreliable: poll log files and artifacts directly with
  deadlines, and put a watchdog timer on any dispatched work longer than ~5 minutes.
- **Watchdog rule (mandatory):** every dispatched agent, background shell, or long tool run gets a
  bounded timer sized to the work (~10 min default; 45-60 min for full sims/regressions). On firing,
  verify progress from the filesystem/process table — never from agent status alone — then nudge
  once with concrete state, and reassign against the working-tree state if still dead after one
  nudge window. An idle agent with finished work is a stall, not a success.
- Clear `PYTHONPATH` around pip operations (`~/.bashrc` leaks package metadata into `pip freeze`).
- Stale `metadata.pickle`: use `make clean` or a fresh `OUT=` after editing testlists/configs.
- Full gotcha list with evidence: `docs/dv/BUILD_AND_SIM.md`.

## mex — code graph & wiki

A full-tree `mex-agent` scaffold lives at `.mex/` (code graph + curated wiki,
built with `mex setup`; read `.mex/ROUTER.md` first each session for full
context). Use `mex graph query <who-calls|what-calls|where-defined> <symbol>`
for exact lookups and `mex graph scope "<task>"` for bounded, source-backed
context; treat what it returns as already read. Gate: `mex check` stays green.

Known limit: the code graph parses Python/TypeScript/JavaScript/Rust only — no
SystemVerilog — so it covers the DV/python side; RTL/TB knowledge is curated
wiki prose (`.mex/context/`), kept honest by `mex check`, not graph-derived.
mex-agent 0.8.0 has no ignore-glob config for its graph/wiki scan, so fence
enforcement for this scaffold is procedural: see `.mex/AGENTS.md`'s
"Fence-aware scope" for the deny list (mirrored from `ci/make-cleanroom.sh`'s
`DENY=(...)` array) and the wiki-authoring rule — no `.mex/` page may
paraphrase fenced content. The clean-room clone (WS7) gets its own,
independent `mex setup` once it exists, fence-safe by construction.

## Skills index

Skills live in `.claude/skills/` (codex discovers them via `.agents/skills/shared`). Agents live in
`.claude/agents/`. Index (updated as skills land): `cross-review`, `sim-debug`, `regress`,
`lint-check`, `dv-principles-check`, `mutation-check`, `fcov-expectation`, `simple-english`,
`analyze-cov`, `covergroup-authoring`, `coverage-closure`, `coverage-regression-triage`,
`regression-optimization`, `create-tb`, `uvm-test-generation`,
`verification-planning-test-generation`, `review-tb-tp`, `vcs-rtl-compat`,
`waveform-querying`, `wave-rtl-correlate`, `diagram-builder`, `rtl-workspace-exploration`.
Review rubrics (model-neutral prompt files): `ci/reviews/`.
