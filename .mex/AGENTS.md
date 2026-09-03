---
name: agents
description: Always-loaded project anchor. Read this first. Contains project identity, non-negotiables, commands, and pointer to ROUTER.md for full context.
last_updated: 2026-09-02
---

# Ibex auto-DV fork

## What This Is
A production RISC-V core in SystemVerilog (`rtl/`) with an auto-DV research fork
layered on top; this `.mex/` scaffold is a code-graph and wiki index over the
**full tree**, kept honest by `mex check`.

## Non-Negotiables
- Never paraphrase fenced DV collateral into any `.mex/` file — see "Fence-aware
  scope" below for the deny list and the reason.
- Always `source ci/env.sh` first, every session; never `&&`-chain the site
  `module` command (it exits 1 even on success).
- `CLAUDE.md` is the canonical instruction source for this repo; this scaffold
  is advisory context, never a replacement or a second source of truth.
- Never commit `.mex/graph.db` or `.mex/wiki.db` (already in `.mex/.gitignore`)
  — mex-agent 0.8.0 has no ignore-glob config, so the local index may contain
  fenced Python source with no way to exclude it mechanically.

## Fence-aware scope
`.mex/**` (this scaffold) is itself a fenced/deny-listed artifact class for the
WS7 clean-room export (`ci/make-cleanroom.sh`) because it is a tracked,
full-tree document that could paraphrase existing DV collateral. mex-agent
0.8.0 ships no ignore-glob configuration surface for its code-graph or wiki
corpus scan (verified against the installed package's `dist/cli.js`: no config
file, CLI flag, or environment variable exists for this) — so enforcement here
is procedural, not mechanical:

- **Wiki-authoring rule:** no page under `.mex/context/`, `.mex/patterns/`, or
  `.mex/ROUTER.md` may paraphrase content from a fenced path. Describe that a
  fenced thing exists and where, never what it says.
- **Deny list** (single source of truth: the `DENY=(...)` array in
  `ci/make-cleanroom.sh`; mirror it there, do not hand-copy elsewhere):
  `dv/uvm`, `dv/cosim`, `dv/verilator`, `dv/formal`, `dv/riscv_compliance`,
  `formal`, `vendor/riscv-isa-sim`, `vendor/patches`, `vendor/google_riscv-dv`,
  `docs/dv/BUILD_AND_SIM.md`, `docs/dv/COSIM.md`, `docs/dv/evidence`,
  `docs/dv/reviews`, `docs/dv/process-logs`, `docs/superpowers`, `ci/jenkins`,
  `ci/build-spike.sh`, `ci/setup-cosim.sh`, `ci/run-cosim-test.sh`,
  `ci/reviews/fence-integrity.md`, `ci/reviews/test-overlap.md`, the six
  verification RSTs under `doc/` (`doc/01_overview/verification_overview.rst`,
  `doc/03_reference/{cosim,coverage_plan,testplan,verification,verification_stages}.rst`),
  `doc/03_reference/images/tb*.svg`, and `.mex/` itself from any future export.
- **Known limit (structural, not just procedural):** the code graph's
  supported-language allowlist is TypeScript/JavaScript/Python/Rust —
  SystemVerilog is never parsed, so RTL/TB source cannot enter the graph
  regardless of this gap. `.mex/graph.db`/`.mex/wiki.db` are never git-tracked,
  so even a locally-indexed fenced Python file cannot leak via a commit.
  RTL/DV-adjacent knowledge in this wiki is therefore curated prose (the
  `context/` files), kept honest by `mex check`, not graph-derived.
- The clean-room clone (WS7) gets its **own**, independent `mex setup` once it
  exists — its graph and wiki are built only from files physically present in
  that clone, so fenced knowledge cannot enter it by construction, independent
  of this gap.

## Commands
- Env: `source ci/env.sh` (every session, first)
- RTL lint: `make lint-core-tracing`; Python lint: `make python-lint`
- Scaffold: `mex check`; `mex graph scope "<task>"`

## Code Graph
Use the smallest relevant structured resolver. For Inbox or Relay mutations, resolve only the intended action with `mex inbox contract --action <command-id> --json` or `mex relay contract --action <command-id> --json`; use `mex capabilities --json` only for broader capability discovery. If the user explicitly asks to create, save, or draft a checkout-local Inbox or Relay draft, preview and apply that exact draft without asking for redundant confirmation. Deleting a local draft, or publishing, approving, rejecting, withdrawing, marking stale, repairing, taking or acknowledging, or closing, requires fresh explicit confirmation after semantic preview. Treat Git commit, push, and pull as separate actions requiring their own authorization.

The repo is indexed into `.mex/graph.db`. Use it to avoid re-reading code you already have — it is one tool alongside Grep/Glob, not a replacement for them.
- If you know the symbol name, go straight to it: `mex graph query <who-calls|what-calls|where-defined> <symbol>` and `mex graph get <id>` are exact and cheap. This is the strongest part of the graph. Give it exact names — an approximate name can return a confident wrong match.
- Exploring an unfamiliar task? `mex graph scope "<task>"` returns bounded, source-backed JSONL context plus trustworthy execution flows. Scope matches on words, not meaning, so treat it as starting evidence rather than a complete answer.
- Treat source returned by the graph as ALREADY READ; do not re-open those files.
- Read the summary status and evidence. `status: "ok"` remains usable when `truncated: true`; only optional evidence was omitted. For `partial` or `degraded`, narrow the task or follow `suggestedNextCommands`.
- Use `mex graph get <id> --detail source` only when source is missing, you need exact expansion, or a partial/degraded summary suggests it. Do not expand nodes by quota.
- If the evidence is insufficient or the task wording does not match the code, use Grep/Glob instead. Do not re-run `scope` with reworded phrasing more than once.
- Before editing a symbol, run `mex impact <symbol|file>` to see affected callers and scaffold memory.
- During `mex sync`, adjudicate any AMBIGUOUS grounding; after repairs, ensure the refreshed grounding is re-emitted.

## Scaffold Growth
After meaningful work, run GROW:
- Ground: what changed in reality?
- Record: update `ROUTER.md` and relevant `context/` files
- Orient: create or update a `patterns/` runbook if this can recur
- Write: bump `last_updated` on changed scaffold files and run `mex log` when rationale matters

The scaffold grows from real work, not just setup. See the GROW step in `ROUTER.md` for details.

## Navigation
At the start of every session, read `ROUTER.md` before doing anything else.
For full project context, patterns, and task guidance — everything is there.

<!-- mex-agent:skills:start -->
## MEX context policy
- When MEX context materially influences an answer or implementation, include one concise acknowledgement: `MEX context used: <specific records/files/entities consulted>.`
- Do not claim an author, date, or historical event unless the retrieved data actually provides it.
- After a MEX write, say exactly what changed and its sharing boundary: a local draft is checkout-only and nothing is shared; a canonical artifact is written to the working tree and requires commit/push to share.
- Skill activation is not approval for canonical actions.
<!-- mex-agent:skills:end -->
