---
name: mex-fence-aware-wiki-edit
description: Editing this .mex/ scaffold (context/, patterns/, ROUTER.md, AGENTS.md) without letting fenced DV content leak into a tracked file.
triggers:
  - "update the wiki"
  - "edit .mex"
  - "mex context"
  - "mex pattern"
edges:
  - target: context/architecture.md
    condition: for what this wiki is allowed to describe about the DV layer
grounds_to: []
last_updated: 2026-09-02
mex:
  id: mx_01M1JCXQCCB397Y6V8BAD88T81
  type: pattern
  status: promoted
  revision: 2
  title: mex-fence-aware-wiki-edit
  relations:
    - type: related_to
      target: mx_01M1JCXQ816BT342PE3PRTJZAV
      note: for what this wiki is allowed to describe about the DV layer
---

# mex fence-aware wiki edit

## Context
This is the most dangerous edit surface in the repo for accidental
contamination: `.mex/context/`, `.mex/patterns/`, `.mex/ROUTER.md`, and
`.mex/AGENTS.md` are all git-tracked, full-tree documents, but mex-agent 0.8.0
has no ignore-glob configuration to stop fenced content from being typed into
them — the control is entirely in the author (you). See the Fence section in
`.mex/AGENTS.md` for the deny list.

## Steps
1. Before writing a wiki edit that touches anything DV-related, check the path
   you're about to describe against the deny list in `.mex/AGENTS.md`.
2. If the thing you want to describe lives under a fenced path: say it exists
   and point at it by path (e.g. "the DV flow's build commands are documented
   in `docs/dv/BUILD_AND_SIM.md`"), never paraphrase its content (test names,
   testbench structure, cosim internals, coverage bins).
3. Write the edit; keep `grounds_to` empty unless the claim is embodied by a
   specific graph node in a non-fenced, graph-supported file (TypeScript/
   JavaScript/Python/Rust — SystemVerilog is never parsed).
4. Bump `last_updated` on every file you touched.

## Gotchas
- `mex graph scope`/`query` will happily return Python files under fenced
  roots (e.g. `dv/formal/*.py`, `vendor/google_riscv-dv/scripts/*.py`) since
  the graph has no ignore config either — treat any such hit as off-limits for
  wiki prose even though the tool surfaced it.
- `.mex/graph.db`/`.mex/wiki.db` are untracked (`.mex/.gitignore`) — that
  protects commits, not this session's own reasoning. Do not paste graph query
  output that names fenced content into a tracked file.

## Verify
- [ ] `git diff --stat -- .mex` before committing, then read the full diff:
      no fenced test/checker/cosim name or testlist detail appears.
- [ ] `mex check` still reports no new drift from this edit.

## Debug
If unsure whether a fact is fenced, check `ci/make-cleanroom.sh`'s `DENY=(...)`
array (the single source of truth) rather than guessing from this file's
list, which mirrors it but is not authoritative.

## Update Scaffold
- [ ] Update `.mex/ROUTER.md` "Current Project State" if what's working/not
      built has changed
- [ ] If this is a new task type without a pattern, create one in
      `.mex/patterns/` and add it to `INDEX.md`
