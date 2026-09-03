# Session 2 handoff (auto-DV setup, branch `fzhang/auto-dv-setup`) — RUNNING LOG

**Date:** 2026-09-02 (session 2, in progress — this file is updated as state changes; the git log
is authoritative between updates).

## Status ledger (delta from session-1 handoff)

| Item | State | Evidence |
|---|---|---|
| Handoff items 3, 4.1, 5 | VERIFIED (were done in session 1) | CLAUDE.md; `.claude/settings.json` |
| Handoff item 4.2 (dv_principles DUT scoping) | **DONE** | 208a84aa; codex APPROVE `docs/dv/reviews/2026-09-02-codex-diff-c77f02da-208a84aa.md` |
| WS5 MCP servers | **DONE** (gate item 3 closed against the amendment's replacement criterion in WS7 T4) | `docs/dv/process-logs/ws5/progress.md`; `ws7-gate/check-e-no-remote-mcp.txt` |
| WS4 Jenkins+LSF | **DONE** (closed after review rounds) | 248cdb83; `...ws4-jenkins-lsf-review-log.md` |
| WS7 / WS6 | **COMPLETE** (T1–T5; mex on both trees; invariant 2 lifted) | `docs/dv/process-logs/ws7/progress.md`; `docs/dv/evidence/ws7-gate/`, `ws6-mex/` |
| playbook | done earlier this session | 1e3d4f47, 625eff54 |

## WS7+WS6 close-out (end of session 2)

- **Generation sessions are now PERMITTED** — Critical Invariant 2 lifted in CLAUDE.md/AGENTS.md:
  permitted ONLY inside a verified cleanroom export (`ci/make-cleanroom.sh`, self-verify green);
  `docs/dv/FENCE.md` is the fence rulebook (full tree) with a Zone A variant shipped by the
  overlay. Infra sessions stay contaminated-by-design and never do generation.
- **The single remaining launch blocker is the owner signature**: `DV_prompt.txt`'s
  `Owner sign-off:` line is still the unsigned template (Section 12 item 8). Everything else
  passes: final Section-12 run vs export SHA `32084c74` = 10 PASS / 1 BLOCKED / 0 FAIL
  (`docs/dv/evidence/ws7-gate/section12-final.txt`).
- **Export path decision** (owner directive 2026-09-02, plan v2): re-exports instead of the v1
  snapshot branch. Deferred machinery is listed with authorities in `docs/dv/FENCE.md`
  §"Deferred machinery" (snapshot branch + sync, fence.yaml, escape harness, zoneb-run referee
  attachment, Zone A permission rules, full spec:139 triage-on-add); v1 design at 86eba26e.
- **Post-T5 fence state:** owner final-check fix set folded (deny `ci/vars.env`,
  `ci/install-build-deps.sh`, `ci/cleanroom-overlay`, `ci/lint-commits.sh`; `ibex-cosim`/
  `ibex_cosim` scan strings; consequential `flake.nix` deny). Full-mode selftest green
  (`ws7-selftest-tdd/t5-fixes-green.txt`). Live export at `/localdev/fzhang/ws/ibex-cleanroom`
  (source `ebf47c1a`); its spike needs a rebuild per SIM_RECIPE (the --force rebuild discarded
  the T4 build; the site attestation stands).
- Remaining process step: WS7+WS6 post-execution cross-model review (controller; opus fallback if
  codex is still capped), then ledgers to DONE and SDD workspace cleanup.

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

## Final state (end of session 2)
ALL WORKSTREAMS DONE: WS1-WS3 (session 1), WS4 (Jenkins+LSF, incl. dual-suite plumbing + spike-pin
fix), WS5 (MCP, DONE after WS7 closed its gate item), WS6 (mex, both trees), WS7 (export-path
cleanroom fence — owner-directed re-cut from the snapshot design; v1 design preserved at 86eba26e
and in FENCE.md §Deferred). Setup playbook committed. Fence amendment v2.1 BINDING.
Generation sessions are PERMITTED (CLAUDE.md Critical Invariant 2 lifted) inside a verified export.
THE ONE REMAINING LAUNCH BLOCKER: owner signature on DV_prompt.txt:375 (Section 12 item 8).
Open owner call: shared IBEX_TOOLS_DIR holds the cosim ISS (visible to Zone A ls; advisory layer).
Post-merge note: first full TEST=all against the bumped spike pin confirms the ZIHPM fix at scale.
codex remains spend-capped; opus fallback authorized and used for all reviews after the cap.
