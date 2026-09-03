# Ibex auto-DV cleanroom — canonical agent instructions

<!-- FENCE-ZONE: A -->
This clone is the Zone A cleanroom. This file is the single source of truth for AI agents in it;
`AGENTS.md` (codex) delegates here and mirrors only the Critical Invariants block below. The
mission is the seed prompt (`DV_prompt.txt`); the fence authority is `docs/dv/FENCE.md`.

## Environment & flow

- `source ci/env.sh` first, always (login shell / `bash -lc`; see its header for the supported-shell
  contract). Compile, run, coverage, LSF, and Zone B submission mechanics: `docs/dv/SIM_RECIPE.md`.
- You build your own TB and flow from scratch. Everything you produce lands under `dv/auto_dv/**`
  with the `gen_` prefix (`dv/auto_dv/contract/README.md`). The cocotb-on-VCS mechanics note is
  `docs/dv/TB_CONTRACT.md` — mechanics to reuse, not an interface to build against.

## DV principles

`docs/dv/dv_principles.md` binds all DV work, hand-written or generated. In one line: realistic
boundary stimulus, intent-derived checking that fails through a collected mechanism, honesty over
green, and the trust triad — TDD, mutation-proof, fcov-expectation — for every new test or checker.

## Cross-model review policy

- The executing model never self-approves.
- Before execution: the plan/spec/testplan is reviewed by the other model (Claude executes ⇒ codex
  reviews; codex executes ⇒ `claude -p` reviews). After execution: the diff is reviewed by the
  other model the same way.
- Review artifacts are committed under `dv/auto_dv/reviews/`, each with a reviewer-identity header
  (CLI version, model ID, reasoning setting) and an explicit review target (commit SHAs / diff
  scope).
- Verdicts are machine-readable — `APPROVE` / `APPROVE-WITH-CHANGES` / `REQUEST-CHANGES` — and
  gating: no progress past `REQUEST-CHANGES` without a recorded re-review.
- Disagreements with a recorded controller ruling go to the human owner, not back into the loop.
- The `cross-review` skill executes this policy; use it rather than ad-hoc invocations. Its wrapper
  asserts the Zone A rubric set in `ci/reviews/` (GUIDE.md plus exactly five rubrics) and fails
  loud on a missing or extra rubric.
- Reviewer model preference: codex with the `sol`-class model at high reasoning effort when
  available; if codex is unavailable, an equivalent-tier Claude model (Opus-class or above)
  reviewing from a fresh session is an acceptable substitute — record which was used in the
  artifact's identity header either way.

## Critical invariants

<!-- CRITICAL-INVARIANTS-BEGIN -->
1. The executing model never self-approves: plans get a pre-execution review and diffs get a
   post-execution review by the other model; a `REQUEST-CHANGES` verdict blocks progress until a
   recorded re-review reaches `APPROVE`/`APPROVE-WITH-CHANGES`.
2. Knowledge-fence: generation is permitted in this clone only, and only on what this clone
   contains or `docs/dv/FENCE.md` allows. Never fetch other branches or remotes, never read
   sibling clones, never pull Ibex DV collateral from the network; where `FENCE.md` and any other
   document disagree, `FENCE.md` wins — stop and report.
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
- Use a fresh output directory after changing build knobs, lists, or configuration inputs.
- Full gotcha list: `docs/dv/SIM_RECIPE.md` §Site gotchas.

## Skills index

Skills live in `.claude/skills/` (codex discovers them via `.agents/skills/shared`). Agents live in
`.claude/agents/`. The skills and agents in this clone are Zone A variants where the full-tree
versions pointed at documents that do not ship here — trust the copies in this clone. Index:
`cross-review`, `sim-debug`, `regress`, `lint-check`, `dv-principles-check`, `mutation-check`,
`fcov-expectation`, `simple-english`, `analyze-cov`, `covergroup-authoring`, `coverage-closure`,
`coverage-regression-triage`, `regression-optimization`, `create-tb`, `uvm-test-generation`,
`verification-planning-test-generation`, `review-tb-tp`, `vcs-rtl-compat`, `waveform-querying`,
`wave-rtl-correlate`, `diagram-builder`, `rtl-workspace-exploration`.
Review rubrics (model-neutral prompt files): `ci/reviews/`.
