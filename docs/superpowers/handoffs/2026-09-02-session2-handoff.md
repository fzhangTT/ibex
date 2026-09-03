# Session 2 handoff (auto-DV setup, branch `fzhang/auto-dv-setup`) — RUNNING LOG

**Date:** 2026-09-02 (session 2, in progress — this file is updated as state changes; the git log
is authoritative between updates).

## Status ledger (delta from session-1 handoff)

| Item | State | Evidence |
|---|---|---|
| Handoff items 3, 4.1, 5 | VERIFIED (were done in session 1) | CLAUDE.md; `.claude/settings.json` |
| Handoff item 4.2 (dv_principles DUT scoping) | **DONE** | 208a84aa; codex APPROVE `docs/dv/reviews/2026-09-02-codex-diff-c77f02da-208a84aa.md` |
| WS5 MCP servers | **CLOSED — PARTIAL pending WS7** | `docs/dv/process-logs/ws5/progress.md`; codex APPROVE `...codex-diff-d04e5bba-9f2f6c39.md` (3 fix rounds, superseded artifacts suffixed) |
| WS4 Jenkins+LSF | plan rev 6 in codex pre-review (round 6; rounds 1–5 all REQUEST-CHANGES, all findings real) | plan + `...ws4-jenkins-lsf-review-log.md`; artifacts `-round1..5` |
| WS7 / WS6 / playbook | not started | order per session-1 handoff |

## Infra events this session (owner aware; durable arrangements)

- **/home quota incident:** weka `/home` rejected all writes (user/dir quota + hourly snapshots in
  `/home/.snapshots` pinning deletions). ~1.3G freed (caches, old codex packages, 2 old Claude Code
  versions). IT-side issue; resolved during the session (writes work again).
- **codex relocation (permanent):** `CODEX_HOME=/proj_soc/user_dev/fzhang/home-storage/codex-home`
  (700, tokens 600) holds state + the live package store; `~/.local/bin/codex` symlinks into it;
  `~/.bashrc` exports CODEX_HOME (BEGIN-codex-projsoc block). `codex update` installs there.
  `~/.codex` on /home is stale leftovers. Memory: `codex-projsoc-relocation`.
- **codex upgraded 0.149.1 → 0.152.1** during WS5 T3 (fixed codex's MCP tool-registry exposure).
  Artifacts record per-run identity.
- **cross-review wrapper timeout now 150 min** (`run_codex_review.sh`): the grown WS4 plan blew
  60/90-min budgets three times. If round 6 also times out at 150, next step is a scoped
  re-review mode (verify prior findings + diff-since-last-rev instead of whole-plan re-reads).
- **`ci/env.sh` gained `IBEX_ENV_TOOLCHECK=off`** (narrow opt-out of the fail-loud tool check; used
  by MCP wrappers whose servers need no simulator) and the `IBEX_MCP_*` pinned exports +
  `$VERDI_HOME/bin` PATH prepend.

## WS5 outcomes worth knowing

- All three local MCP servers work natively from BOTH clients; `ci/mcp/README.md` §Client setup
  documents the codex `trust_level` prerequisite and Claude `enabledMcpjsonServers` knob.
- Root cause that mattered: env.sh's fail-loud vcs check killed wrappers under codex's stripped
  MCP-spawn env — fixed via the toolcheck opt-out + per-wrapper prereq guards.
- Re-runnable gate probes live in `ci/mcp/probes/` (fail-loud validated).
- WS7 plan inputs recorded: (a) WS5's cleanroom no-MCP gate item lands there; (b) the fence manifest
  must triage `ci/mcp/**` + env.sh `IBEX_MCP_*` as Zone A-visible pointers to Zone B equipment.

## Operating notes (session-2 additions)

- SDD with unnamed subagents works well under agent-teams; one T3 stall was recovered by
  nudge-then-reassign per the watchdog rule (the nudged agent finished; the reassigned one was
  TaskStop'd before mutating — check tree state before letting a reassignment run).
- Codex plan reviews of large plans are the loop bottleneck; keep plans lean and move round
  dispositions to sidecar logs.
- Disk-cleanup lesson: `~/.codex/packages` IS the codex install, not a cache — deleting it removed
  the binary (restored from weka snapshots). Don't clean it or `codex-home/packages`.

## Owner decisions (2026-09-02, later session)
- **Fence-scope amendment** `docs/superpowers/specs/2026-09-02-zone-a-fence-scope-amendment.md`:
  fence the collateral, not the tools — Zone A gets the same MCP servers and skills pointed at its
  own out-tree; Zone A builds its own TB and runs its own sims; Zone A variants of tool-adjacent
  files; fence-line triage tables; DUT = gen_dut_top wrapper, CHERIoT out of scope. Cross-model
  review in flight (opus fallback). Feeds WS7 planning directly.
- **codex spend cap hit** — codex unavailable until the owner raises the cap. Owner authorized the
  CLAUDE.md fallback (opus fresh-session reviewer, identity recorded) "for now".
- **ChipSmart** (`riscv/ChipSmart`, clone at /localdev/fzhang/ws/ChipSmart) is the siliconpilot
  skill library; a curated selective import into .claude/skills/ is in flight — only skills that
  serve the ibex stack (VCS/UVM/riscv-dv/cocotb; no bazel/bzsim/simscope/DFT/fault).
