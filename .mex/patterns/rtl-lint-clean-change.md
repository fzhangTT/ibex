---
name: rtl-lint-clean-change
description: Making an RTL change under rtl/ and keeping it lint-clean against the known baseline.
triggers:
  - "change rtl"
  - "edit rtl"
  - "add a signal"
  - "lint"
edges:
  - target: context/conventions.md
    condition: for the RTL naming/structure conventions this pattern assumes
  - target: context/architecture.md
    condition: for where the changed module sits in the overall RTL
grounds_to: []
last_updated: 2026-09-02
mex:
  id: mx_01M1JCXQCKJ3Q69GF6ATE5E21V
  type: pattern
  status: promoted
  revision: 3
  title: rtl-lint-clean-change
  relations:
    - type: related_to
      target: mx_01M1JCXQ9BS63RWRR6ZXZK0EVJ
      note: for the RTL naming/structure conventions this pattern assumes
    - type: related_to
      target: mx_01M1JCXQ816BT342PE3PRTJZAV
      note: for where the changed module sits in the overall RTL
---

# RTL lint-clean change

## Context
Load `context/conventions.md` (RTL naming: `ibex_<unit>.sv`, `ibex_*_pkg.sv` for
shared types) and `context/architecture.md` (Key Components) before editing
`rtl/`. `source ci/env.sh` first, every session.

## Steps
1. `source ci/env.sh`.
2. Make the RTL edit in `rtl/`, keeping one primary module per file and shared
   types in the relevant `ibex_*_pkg.sv`.
3. Run the `lint-check` skill (verilator via fusesoc) against the known
   baseline.
4. If the lint run touches simulation behavior, note that the UVM DV flow that
   would exercise it lives under `dv/uvm/core_ibex` and is fenced from this
   wiki — follow `docs/dv/BUILD_AND_SIM.md` directly for the verified
   build/run commands, do not ask this scaffold to summarize them.

## Gotchas
- The site `module` command exits 1 even on success — never `&&`-chain it.
- `make build-all`/`lint-core-tracing` at the repo root only cover the
  reference builds (`simple_system`, `riscv-compliance`); it is not the DV
  flow's own build.

## Verify
- [ ] `lint-check` shows no new findings against the known baseline.
- [ ] `python-lint` still passes if any Python tooling under `ci/` changed.
- [ ] The change did not touch a fenced path (see `.mex/AGENTS.md` Fence
      section) as a side effect (e.g. a generated file landing under `dv/uvm`).

## Debug
If lint reports something unexpected, check whether the baseline itself is
stale (`lint-check` skill documents how the baseline is refreshed) before
assuming the new finding is real.

## Update Scaffold
- [ ] Update `.mex/ROUTER.md` "Current Project State" if what's working/not
      built has changed
- [ ] Update `.mex/context/architecture.md` if a new RTL component was added
- [ ] If this is a new task type without a pattern, create one in
      `.mex/patterns/` and add it to `INDEX.md`
