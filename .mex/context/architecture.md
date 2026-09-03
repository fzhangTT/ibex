---
name: architecture
description: How the major pieces of this project connect and flow. Load when working on system design, integrations, or understanding how components interact.
triggers:
  - "architecture"
  - "system design"
  - "how does X connect to Y"
  - "integration"
  - "flow"
edges:
  - target: context/stack.md
    condition: when specific technology details are needed
  - target: context/decisions.md
    condition: when understanding why the architecture is structured this way
# Broad overview: keep this empty unless a claim depends on a few specific symbols.
# Entry shape: { node: "function:<tier-1-id>", fingerprint: "mh:64:<hex>" }
grounds_to: []
last_updated: 2026-09-02
mex:
  id: mx_01M1JCXQ816BT342PE3PRTJZAV
  type: architecture
  status: promoted
  revision: 2
  title: architecture
  relations:
    - type: related_to
      target: mx_01M1JCXQBPCM765G4N0BY59R7C
      note: when specific technology details are needed
---

# Architecture

<!-- mex:entity
id: mx_01M1JCXQ7PKYJT80YGNPZKMHSB
type: component
status: promoted
revision: 1
-->
## System Overview

Ibex is a production RISC-V core implemented in SystemVerilog under `rtl/` — the
repo's only synthesizable-design tree. Everything else is tooling wrapped around
that RTL: `ci/env.sh` loads the site module toolchain (must be sourced first, every
session), the top-level `Makefile` drives reference builds (`build-simple-system`,
`build-riscv-compliance`, `lint-core-tracing`, `python-lint`), `syn/` runs the Yosys
synthesis flow, and `doc/` is the Sphinx documentation source. Layered on top of that
is an agent-tooling surface (`.claude/skills/`, `.claude/agents/`, `CLAUDE.md`/`AGENTS.md`)
that governs how both Claude and codex sessions work in this repo, including a
mandatory cross-model review policy for plans and diffs.

A separate, actively-verified DV layer exists under `dv/` (UVM testbench, cosim,
riscv-dv-derived tests) but it is **knowledge-fenced from this wiki by design** — see
"What Does NOT Exist Here" below.

<!-- mex:entity
id: mx_01M1JCXQ7DF983JKV3FG4FXYCS
type: component
status: promoted
revision: 1
-->
## Key Components

- **`rtl/`** — the Ibex core RTL: `ibex_top.sv` (top level), `ibex_core.sv` (pipeline
  glue), `ibex_pkg.sv` (shared types/parameters), plus one file per functional unit
  (`ibex_alu.sv`, `ibex_decoder.sv`, `ibex_load_store_unit.sv`, `ibex_pmp.sv`, …).
  Parametrized for RV32E/I, M, C, B, and PMP configurations.
- **`ci/env.sh`** — the one-time environment loader for every session; site `module`
  commands exit 1 even on success, so it is never `&&`-chained. All verified
  build/run/coverage commands live in `docs/dv/BUILD_AND_SIM.md` (fenced from this
  wiki — read it directly, do not ask this scaffold to summarize it).
- **`.claude/skills/` and `.claude/agents/`** — the agent-tooling layer: `CLAUDE.md`
  is the canonical instruction source, `AGENTS.md` is the codex delegator that
  mirrors only the Critical Invariants block (hash-checked by
  `.codex/compat/validator.py`). Skills are discovered by codex through the
  `.agents/skills/shared` symlink.
- **`examples/`, `syn/`, `util/`, `doc/`** — reference software (`simple_system`),
  the Yosys synthesis flow, misc utilities, and the Sphinx documentation tree.
- **`.mex/`** (this scaffold) — a code-graph + wiki index over the full tree, built
  with `mex-agent`. It deliberately stays at a structural level: no fenced DV
  content is paraphrased into it (see the Fence section in `.mex/AGENTS.md`).

<!-- mex:entity
id: mx_01M1JCXQ74CR29JGZ8QHTRSXCZ
type: component
status: promoted
revision: 1
-->
## External Dependencies

- **Synopsys VCS** — the primary UVM simulator for the (fenced) DV flow; site-licensed,
  loaded via `ci/env.sh`.
- **Verilator** (open-source) — used for RTL lint (`lint-check` skill) and the
  `simple_system` reference build.
- **Node.js ≥22.5** (site default 22.14; a build with SQLite's `fts5` extension is
  required — see `context/stack.md` "Version Constraints") — runs `mex-agent`
  itself, this scaffold's code graph and wiki engine.
- **Yosys** — the `syn/` synthesis flow's area/reporting backend.

<!-- mex:entity
id: mx_01M1JCXQ5S5ZMY1XE3ZH1YB9R5
type: component
status: promoted
revision: 1
-->
## What Does NOT Exist Here

- No description of the existing DV testbench, cosim architecture, or generated-test
  collateral in this wiki. That knowledge is fenced (`docs/dv/dv_principles.md`
  binds both hand-written and generated DV work without itself being fenced;
  `docs/dv/FENCE.md` is the authoritative fence document once WS7 lands). This
  scaffold intentionally does not summarize or index it.
- No CI/regression orchestration detail (Jenkins, LSF fan-out) — out of scope for
  this wiki under the same fence; `ci/jenkins` and the cosim-runner scripts are
  denied paths for `.mex/` content.
- No secrets, credentials, or license-server configuration — those live in the
  site module system loaded by `ci/env.sh`, never in this repo.
