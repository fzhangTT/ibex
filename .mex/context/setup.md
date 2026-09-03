---
name: setup
description: Dev environment setup and commands. Load when setting up the project for the first time or when environment issues arise.
triggers:
  - "setup"
  - "install"
  - "environment"
  - "getting started"
  - "how do I run"
  - "local development"
edges:
  - target: context/stack.md
    condition: when specific technology versions or library details are needed
  - target: context/architecture.md
    condition: when understanding how components connect during setup
# Ground only setup behavior implemented by specific code symbols.
# Entry shape: { node: "function:<tier-1-id>", fingerprint: "mh:64:<hex>" }
grounds_to: []
last_updated: 2026-09-02
mex:
  id: mx_01M1JCXQBDVRQW2R5TGK5ZX25E
  type: guide
  status: promoted
  revision: 3
  title: setup
  relations:
    - type: related_to
      target: mx_01M1JCXQBPCM765G4N0BY59R7C
      note: when specific technology versions or library details are needed
    - type: related_to
      target: mx_01M1JCXQ816BT342PE3PRTJZAV
      note: when understanding how components connect during setup
---

# Setup

<!-- mex:entity
id: mx_01M1JCXQB5F2J2EM0GP3BHNXS2
type: guide
status: promoted
revision: 1
-->
## Prerequisites

- The site `module` system, loaded via `source ci/env.sh` (login shell /
  `bash -lc`; see its header for the supported-shell contract).
- Node.js ≥22.5 with SQLite's `fts5` extension, only if working on this `.mex/`
  scaffold — see "Common Issues" below.
- `npm-global` bin directory on `PATH` (site default) for `mex` and any other
  globally-installed Node CLI.

<!-- mex:entity
id: mx_01M1JCXQAYNPKHJWPH8R527G6R
type: guide
status: promoted
revision: 1
-->
## First-time Setup

1. `source ci/env.sh` — every session, every shell, before anything else.
2. For the RTL/DV build and simulation flow: follow `docs/dv/BUILD_AND_SIM.md`
   directly (fenced from this wiki — it names existing tests and the flow in
   detail; this scaffold does not summarize it).
3. For this `.mex/` scaffold specifically: `npm install -g mex-agent`, then
   `mex setup` from the repo root.

## Environment Variables

No plaintext secrets or `.env` values are required in this repo — all
toolchain/license configuration is managed by the site `module` system through
`ci/env.sh`.

<!-- mex:entity
id: mx_01M1JCXQAPH9KFR4QEGW3GWTSC
type: guide
status: promoted
revision: 1
-->
## Common Commands

- `source ci/env.sh` — load the environment (do every session).
- `make lint-core-tracing` / `make python-lint` — the reference-build lint
  targets in the top-level `Makefile`.
- `mex check` — detect drift between this scaffold and the codebase.
- `mex graph scope "<task>"` — bounded, source-backed context for a task
  (Python/TypeScript/JavaScript/Rust only — see `context/stack.md`).

<!-- mex:entity
id: mx_01M1JCXQAE1NNG2SQSXJB7D9KN
type: guide
status: promoted
revision: 1
-->
## Common Issues

**`module` command "fails" with exit 1:** This is expected even on success —
never `&&`-chain it; `ci/env.sh` already handles this.

**Node 22.14 (site default) cannot build the `.mex/` code graph or wiki:**
`Code graph setup failed: no such module: fts5` — that Node build's embedded
SQLite omits the `fts5` extension both the graph and wiki require. Prepend a
build that has it, e.g. `/tools_soc/opensrc/node.js/v24.14.0/bin`, to `PATH`
before running `mex` commands. Full repro:
`docs/dv/evidence/ws6-mex/summary.txt`.

**Stale `metadata.pickle` in the DV flow:** run the flow's own clean target
(defined in `dv/uvm/core_ibex`'s Makefile, fenced from this wiki — not the
repo-root `Makefile`) or use a fresh `OUT=` after editing testlists/configs —
see `CLAUDE.md` Site gotchas.
