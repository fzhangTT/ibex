---
name: stack
description: Technology stack, library choices, and the reasoning behind them. Load when working with specific technologies or making decisions about libraries and tools.
triggers:
  - "library"
  - "package"
  - "dependency"
  - "which tool"
  - "technology"
edges:
  - target: context/decisions.md
    condition: when the reasoning behind a tech choice is needed
  - target: context/conventions.md
    condition: when understanding how to use a technology in this codebase
# Broad inventory: ground only claims embodied by a small number of symbols.
# Entry shape: { node: "function:<tier-1-id>", fingerprint: "mh:64:<hex>" }
grounds_to: []
last_updated: 2026-09-02
mex:
  id: mx_01M1JCXQBPCM765G4N0BY59R7C
  type: architecture
  status: promoted
  revision: 2
  title: stack
  relations:
    - type: related_to
      target: mx_01M1JCXQ9BS63RWRR6ZXZK0EVJ
      note: when understanding how to use a technology in this codebase
---

# Stack

## Core Technologies

- **SystemVerilog** — the RTL implementation language (`rtl/`); the only
  synthesizable-design source in the repo.
- **Python 3.9** (site-managed via the `module` system, loaded by `ci/env.sh`) —
  tooling scripts (`ci/*.py`, e.g. `ci/check_fcov_expectations.py`) and the
  `python-lint` Make target.
- **Node.js ≥22.5** — runs `mex-agent` (this scaffold). The site's default 22.14
  build's embedded SQLite lacks the `fts5` extension that both the code graph and
  the wiki index require as a hard dependency; the site's v24.14.0 build does have
  it. See "Version Constraints" below.
- **Make** — the top-level build entry point (`Makefile`): `build-all`,
  `build-riscv-compliance`, `build-simple-system`, `lint-core-tracing`,
  `python-lint`, `test-cfg`.

## Key Libraries

- **Verilator** (not a paid tool) — RTL lint and the `simple_system` reference
  build; the `lint-check` skill runs it via fusesoc and compares against a known
  baseline.
- **Synopsys VCS** — the DV flow's UVM simulator (`SIMULATOR=vcs`); site-licensed,
  fenced from this wiki's content (used, not described, here).
- **Yosys** — the `syn/` synthesis flow's backend for area/reporting.
- **mex-agent** (npm, global install) — this scaffold's own engine: a local code
  graph (`.mex/graph.db`, tree-sitter based) and wiki index (`.mex/wiki.db`),
  neither of which is git-tracked (`.mex/.gitignore`).

## What We Deliberately Do NOT Use

- No containerized build — the toolchain is the site `module` system via
  `ci/env.sh`, not Docker.
- No project-committed IDE configuration or editor state.
- No ORM/database layer of any kind — this is an RTL/DV repo, not a service.

## Version Constraints

Node 22.14 (the site's default, loaded by `ci/env.sh`) cannot build this
scaffold's code graph or wiki: SQLite's `fts5` extension is a hard dependency of
both, and this build's embedded SQLite omits it (`Code graph setup failed: no
such module: fts5`). The site's `/tools_soc/opensrc/node.js/v24.14.0/bin` build
does include `fts5` and was used to build this scaffold; prepend it to `PATH`
before running `mex` commands until this is resolved upstream or a site Node
build adds `fts5`. Full repro in `docs/dv/evidence/ws6-mex/summary.txt`.
