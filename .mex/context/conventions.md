---
name: conventions
description: How code is written in this project — naming, structure, patterns, and style. Load when writing new code or reviewing existing code.
triggers:
  - "convention"
  - "pattern"
  - "naming"
  - "style"
  - "how should I"
  - "what's the right way"
edges:
  - target: context/architecture.md
    condition: when a convention depends on understanding the system structure
  - target: context/decisions.md
    condition: when a convention exists because of a documented decision
# Add only nodes that embody the documented convention; do not ground examples broadly.
# grounds_to:
#   - node: "function:<tier-1-id>"
#     fingerprint: "mh:64:<hex>"
grounds_to: []
last_updated: 2026-09-02
mex:
  id: mx_01M1JCXQ9BS63RWRR6ZXZK0EVJ
  type: convention
  status: promoted
  revision: 2
  title: conventions
  relations:
    - type: related_to
      target: mx_01M1JCXQ816BT342PE3PRTJZAV
      note: when a convention depends on understanding the system structure
---

# Conventions

<!-- mex:entity
id: mx_01M1JCXQ93SN31Q6VEJTY2F4D5
type: convention
status: promoted
revision: 1
-->
## Naming

- RTL files: `ibex_<unit>.sv` (e.g. `ibex_alu.sv`, `ibex_load_store_unit.sv`), one
  primary module per file.
- RTL packages: `ibex_*_pkg.sv` (e.g. `ibex_pkg.sv`, `ibex_tracer_pkg.sv`) for
  shared types/parameters, never inlined into a unit file.
- Skill directories: `.claude/skills/<name>/SKILL.md`, and the frontmatter `name:`
  must equal `<name>` exactly — `.codex/compat/validator.py` fails the build
  otherwise.
- Review artifacts: `docs/dv/reviews/<date>-<who>-<what>.md`, one file per review.

<!-- mex:entity
id: mx_01M1JCXQ8V0E5GM4XNKX2A427A
type: convention
status: promoted
revision: 1
-->
## Structure

- `source ci/env.sh` first, always, before any build/lint/sim command (login
  shell / `bash -lc`); the site `module` command exits 1 even on success, so it
  is never `&&`-chained.
- The top-level `Makefile` is the reference-build entry point; the DV flow's own
  build/run commands live under `dv/uvm/core_ibex` and are fenced from this
  wiki — see `docs/dv/BUILD_AND_SIM.md` directly, not a summary here.
- Skills live in `.claude/skills/`; codex discovers the same files through the
  `.agents/skills/shared` symlink (must resolve to `../../.claude/skills`).

<!-- mex:entity
id: mx_01M1JCXQ8K3JSS7E9ERR3YCDNB
type: convention
status: promoted
revision: 1
-->
## Patterns

Cross-model review (binding, from `CLAUDE.md`): the executing model never
self-approves. Every plan/spec/testplan gets a pre-execution review by the other
model (Claude executes ⇒ codex reviews; codex executes ⇒ `claude -p` reviews),
and every diff gets the same post-execution. Verdicts are machine-readable
(`APPROVE` / `APPROVE-WITH-CHANGES` / `REQUEST-CHANGES`) and gating — no progress
past `REQUEST-CHANGES` without a recorded re-review. Review artifacts are
committed under `docs/dv/reviews/` with a reviewer-identity header and an
explicit review target. The `cross-review` skill executes this; do not invoke
the reviewer CLIs ad hoc.

Knowledge fence (binding, from `CLAUDE.md` Critical Invariants): generation
sessions must not read fenced DV collateral, and infra sessions never paste
fenced content into allowed files — including this `.mex/` scaffold. See the
Fence section in `.mex/AGENTS.md` for the concrete deny list.

<!-- mex:entity
id: mx_01M1JCXQ8CWA6G66BA63N5QG03
type: convention
status: promoted
revision: 1
-->
## Verify Checklist

Before presenting any change in this repo:
- [ ] `source ci/env.sh` was run this session before any build/lint/sim command.
- [ ] RTL changes pass `lint-check` (verilator via fusesoc) against the known
      baseline before committing.
- [ ] No content from a fenced path (see `.mex/AGENTS.md` Fence section) was
      paraphrased into a `.mex/context/`, `.mex/patterns/`, or `.mex/ROUTER.md`
      entry.
- [ ] A new or edited `.claude/skills/<dir>/SKILL.md` has frontmatter `name:
      <dir>` and a non-empty `description:` (validator-checked).
- [ ] Any plan/diff this session authored has, or will get, the cross-model
      review the Cross-model review policy requires before it lands.
