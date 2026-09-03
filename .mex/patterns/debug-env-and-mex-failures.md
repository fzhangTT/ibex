---
name: debug-env-and-mex-failures
description: Diagnosing the recurring environment failure boundary — module/env.sh, PYTHONPATH-in-pip, and mex's fts5 requirement.
triggers:
  - "module command failed"
  - "pip freeze"
  - "fts5"
  - "mex setup failed"
edges:
  - target: context/setup.md
    condition: for the full prerequisite and common-issues list this pattern debugs
grounds_to: []
last_updated: 2026-09-02
mex:
  id: mx_01M1JCXQC5RM332KF08K25T6KH
  type: pattern
  status: promoted
  revision: 2
  title: debug-env-and-mex-failures
  relations:
    - type: related_to
      target: mx_01M1JCXQBDVRQW2R5TGK5ZX25E
      note: for the full prerequisite and common-issues list this pattern debugs
---

# Debug env and mex failures

## Context
Three recurring, non-obvious failure modes at the environment boundary, load
`context/setup.md` "Common Issues" alongside this pattern.

## Debug: "module" command exits 1
This is expected even on success. Never `&&`-chain a `module` load; `ci/env.sh`
already handles this correctly. If a script you're editing chains it, that is
the bug, not the module system.

## Debug: `pip freeze` lists unrelated packages
`~/.bashrc` leaks `PYTHONPATH` (site tooling) into any `pip` invocation,
polluting `pip freeze`/`pip list` with unrelated package metadata. Clear
`PYTHONPATH` around pip operations.

## Debug: `mex setup` / `mex graph rebuild` fails with `no such module: fts5`
The site's default Node 22.14 build's embedded SQLite omits the `fts5`
extension, which both mex's code graph and wiki index require as a hard
dependency (`CREATE VIRTUAL TABLE ... USING fts5(...)` in both). Fix: prepend
a Node build that has `fts5` to `PATH`, e.g.
`export PATH=/tools_soc/opensrc/node.js/v24.14.0/bin:$PATH` (confirmed present
at the site and ≥22.5 per spec), then rerun the `mex` command. Full repro and
the exact error text: `docs/dv/evidence/ws6-mex/summary.txt`.

## Verify
- [ ] `node --version` on the active `PATH` is a build with `fts5` before any
      `mex setup`/`mex graph rebuild` invocation:
      `node -e "require('node:sqlite')"` then a `CREATE VIRTUAL TABLE ...
      USING fts5(x)` succeeds.
- [ ] `PYTHONPATH` is unset (or scoped to the venv only) before any `pip`
      command whose output you intend to trust.

## Update Scaffold
- [ ] Update `.mex/context/setup.md` "Common Issues" if a new recurring
      failure is found
- [ ] If this is a new task type without a pattern, create one in
      `.mex/patterns/` and add it to `INDEX.md`
