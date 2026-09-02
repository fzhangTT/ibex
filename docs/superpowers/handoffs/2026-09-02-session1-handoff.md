# Session 1 → Session 2 handoff (auto-DV setup, branch `fzhang/auto-dv-setup`)

**Date:** 2026-09-02. **Branch state:** 80+ commits over `master` (34b07057), pushed to `origin/fzhang/auto-dv-setup`, clean tree. **All work reviewed via SDD loops + cross-model policy; every workstream below closed with codex APPROVE.**

## Status ledger

| Workstream | State | Evidence / ledger |
|---|---|---|
| WS1 VCS bring-up | **DONE** | `docs/dv/process-logs/ws1/progress.md`; smoke+COV green, define fix (54e01775), FCIBH guard (dbba358f); `docs/dv/BUILD_AND_SIM.md`, `COSIM.md` |
| WS2 cocotb | **DONE** | `docs/dv/process-logs/ws2/progress.md`; Milestones A+B green, TB_CONTRACT.md, MUT-002, codex APPROVE (reviews 04–04d) |
| WS3 skills/cross-model | **DONE** (merged 668c85b7) | `docs/dv/process-logs/ws3/progress.md`; validator + 8 skills + 2 agents live; codex cycle closed REQUEST-CHANGES-ADJUDICATED then compensating Claude review + fix rounds |
| WS4 Jenkins+LSF | **NOT STARTED** (spec §WS4) | needs plan + codex pre-review |
| WS5 MCP servers | **NOT STARTED** (spec §WS5; zone-scoped per amendment) | siliconpilot/fsdb/verdi-cov launch lines recon'd in spec |
| WS6 mex | **NOT STARTED** (spec §WS6; runs last) | |
| WS7 knowledge fence | **NOT STARTED** (spec §WS7, heavily amended) | absorbs the parked items below |

**Spec:** `docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md` (authoritative, amended through codex reviews). **Plans:** `docs/superpowers/plans/`. **Review artifacts:** `docs/dv/reviews/` (01–04d). **Env:** `source ci/env.sh`; venv lock-enforced; spike + rv32imcb toolchain under `/localdev/fzhang/ws/tools/`.

## Open decisions parked for the owner (fzhang)
1. Generated-test fcov-manifest location vs `dv/auto_dv` namespace + discovery path + shared-VDB concurrency fix (WS3/WS2 ledgers).
2. Generation-safe vs infra-only skill split (fail-closed until fence authority exists).
3. Commit-message fence-scope ruling (codex accepted; owner may tighten).
4. Validator no-pyyaml fallback weaker than main path (rides WS7 validator work).
5. `ci/fence.yaml` must allowlist `docs/dv/dv_principles.md` + trust skills + `TB_CONTRACT.md` + `FENCE.md` (rulings recorded, not yet encoded).

## NEXT SESSION — owner's six items (with context)

1. **Cleanroom sim capability.** Verify cocotb/VCS sims work from a cleanroom: agents there must know how to set up a TB and run sims (same compile args/flow mechanics) — they just can't see existing DV collateral. Today the flow's compile depends on fenced files (`ibex_dv.f` lists the whole TB; cosim links `dv/cosim`). Needed: a fence-allowlisted **SIM_RECIPE** (VCS args, +vpi/cocotb wiring, how to hook a new TB top, run/env contract — distilled from `rtl_simulation.yaml`/`BUILD_AND_SIM.md` without collateral references), plus decide what of the flow scripts is allowlisted vs recipe-only. Gate: an actual compile+run of a minimal new TB from a cleanroom prototype.
2. **Cleanroom authoring + namespaces + regressions.** New tests/FCOV/TBs must be addable from the cleanroom. Adopt a common prefix (contract already uses `gen_*` for covergroups; extend convention to tests/TB modules/files, e.g. `gen_` or `adv_`) and check worktree/branch namespace collisions (cleanroom is a separate clone — collisions are merge-time; the landing validator (spec WS7) enforces `dv/auto_dv/**`). Regression scripts (WS4) must support BOTH: the existing suite as reference AND new suites/testlists for the challenge (a `--testlist`/suite knob in `ci/jenkins/*.sh`; note `TEST=all` now excludes `cocotb: 1`-marked entries when `COCOTB=0` — 0498fbea).
3. **Watchdog rule in CLAUDE.md** — DONE this session (CLAUDE.md §Site gotchas, mandatory watchdog rule; validator PASS).
4. **Rule refinements** — 4.1 DONE this session (CLAUDE.md cross-model policy: codex `sol`-class high effort preferred; equivalent Claude fallback OK; record identity). 4.2 TODO: `docs/dv/dv_principles.md` boundary-condition rules apply to **the chosen DUT** — correct as written for ibex core-level, but agents may build sub-module TBs where the DUT boundary differs; add that scoping clarification. CAREFUL: the file carries the hash-anchored TRUST-TRIAD block (edit outside the markers) and semantic checks — run `.codex/compat/validator.py` after, and mirror-check `dv-principles-check` skill citations (§ numbers must not shift).
5. **Agent teams** — enabled this session (`.claude/settings.json` env var; offline reference at `docs/superpowers/references/agent-teams.md`). NOTE the caution in that reference: with teams on, NAMED subagent dispatches become teammates (no background subagents, different idle behavior) — validate the SDD controller pattern still works or spawn unnamed subagents; TeammateIdle/TaskCompleted hooks are a candidate for mechanically enforcing review gates.
6. **Reproducible setup playbook.** Write `docs/superpowers/SETUP_PLAYBOOK.md`: repo-agnostic steps to recreate this whole setup on a new repo — env entry-point pattern (module quirks, fail-loud tail), venv+lock (PYTHONPATH-clean), toolchain/ISS builds, config-propagation audit (the IBEX_CFG class of bug), cocotb overlay recipe (coexistence pattern + flag discipline + hard rules), skills topology + validator, cross-model review policy + gating, trust triad mechanics, SDD/watchdog orchestration practice, fence design. Sources: the spec, ws1–ws3 ledgers, TB_CONTRACT, this handoff.

## Suggested session-2 order
(1) items 3–5 verify/finish (mostly done) → (2) WS4 plan+execute with item-2's dual-suite requirement folded in → (3) WS5 → (4) WS7 with items 1+2 folded into its plan (they are fence-design questions) → (5) WS6 mex → (6) item 6 playbook → then the challenge phase (test-plan generation + closure loops) on the finished platform.

## Operating notes for the next controller
- SDD skill + per-task reviews + fix loops; fresh sonnet implementers (haiku only for pure transcription — it shipped dead async code once); fable for final/whole-branch reviews; codex closes every workstream. Budget 25–45 min per codex full-range review.
- Watchdog EVERYTHING (CLAUDE.md rule); poll artifacts, never trust notifications; PYTHONPATH-clean pip; fresh OUT per knob change.
- Memories on this machine: `watchdog-stalled-agents`, `pythonpath-freeze-contamination` (in the project memory dir).
