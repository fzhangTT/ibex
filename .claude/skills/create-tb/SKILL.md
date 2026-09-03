---
name: create-tb
description: Create a UVM testbench — a standalone scaffold from a DUT port list (quickstart), a whole TB from a verification plan, or a single new component (agent/sequence/test/coverage/checker/interface) added to an existing TB. Use when the challenge phase's from-scratch ibex-core DUT-wrapper TB needs scaffolding, or an existing TB needs one new component; not for reviewing a TB (review-tb-tp) or authoring one sequence end-to-end (uvm-test-generation).
---

Adapted from ChipSmart (riscv/ChipSmart) create-tb. [The bundled `vm-template/`
reference tree was NOT imported with this skill — no bundled template exists in
this repo. For Mode A/B, derive file naming, layering, and import order from
`dv/uvm/core_ibex`'s existing `env/`/`tests/`/`tb/` structure instead of a
prototype template.]

# Create Testbench (quickstart, whole TB, or per-component)

Generate UVM testbench code following the project's own TB conventions (in this
repo: `dv/uvm/core_ibex/{env,tests,tb}`) in place of a bundled reference template.
A project may point at its own template path if one exists. Three modes:

- **Mode A — Quickstart from a DUT port list:** a self-contained single-agent TB
  derived purely from the DUT's ports, droppable into a regression.
- **Mode B — Plan-driven whole TB:** a full methodology scaffold from a verification
  plan + interface list.
- **Mode C — Per-component add:** one new agent / sequence / test / coverage / checker
  / interface placed into an existing TB.

## When to apply

- A DUT module exists and you need a working TB fast, with no VP yet → **Mode A**.
- A new IP / block has a VP + methodology doc and wants matching boilerplate → **Mode B**.
- An existing TB needs an additional component for a new interface or sequence → **Mode C**.

Not for:
- Reviewing an existing TB → `review-tb-tp`.
- Debugging a failing TB → the `sim-debug` skill / `ibex-debug-analyzer` agent.
- Writing the testplan itself → not a DV-coding task.
- Authoring a single new sequence with the full author-validate-smoke loop →
  `uvm-test-generation`.

## Mode A — Quickstart from a DUT port list

### A1. Discover the DUT interface

Extract the port list from the DUT top module (hierarchy/AST capability; fall back to
reading the RTL source). From the ports, classify each signal:

| Category | Detection pattern |
|---|---|
| Clock | port named `clk`, `clock`, `clk_i`, or matching `*clk*` |
| Synchronous reset | port named `rst_n`, `rstn`, `reset_n`, `rst` |
| Asynchronous reset | same naming but driven async in RTL |
| Data inputs | `input logic [W-1:0] <name>` — width W drives field size |
| Data outputs | `output logic [W-1:0] <name>` — monitored, not driven |
| Enable / valid | single-bit inputs named `*en*`, `*valid*`, `*start*` |
| Ready / done | single-bit outputs named `*ready*`, `*done*`, `*ack*` |

Record module name, parameters, and the full port table (name, direction, width). All
file and class names derive from the DUT name in snake_case.

### A2. Generate the single-agent file set

Produce a flat TB under `tb/<dut>/`, one file per component, in dependency order:

```
tb/<dut>/  →  tb_if → tb_transaction → tb_driver → tb_monitor → tb_scoreboard
              → tb_agent → tb_env → tb_base_seq → tb_test → tb_pkg → tb_top
```

Shape each file from the equivalent existing component in `dv/uvm/core_ibex/`
(interface, transaction, driver, monitor, agent, env, base test, tb_pkg, tb_top —
find the closest analog under `dv/uvm/core_ibex/{env,tests,tb}` and follow its
naming/layering), parameterised on the discovered ports:

- Clock/reset are plain interface signals — not inside a clocking block.
- TB-driven (`input`) ports → `driver_cb` (output skew `#1step`); DUT-driven (`output`)
  ports → `monitor_cb` (sampled `@(posedge clk)`). Provide `driver_mp` / `monitor_mp`.
- Driver pulls items via `seq_item_port`; monitor broadcasts on an analysis port; the
  scoreboard is a placeholder check the user fills in.

Then go to **§ Verify the generated code compiles**.

## Mode B / C — Plan-driven whole TB or per-component

### 1. Gather inputs

For a **whole TB** (Mode B):

| Input | Default |
|---|---|
| Block / IP name (e.g. `dfd`, `aplic`) | required |
| Spec / VP reference | required |
| Methodology / VM doc | project default |
| Reference template path | no bundled template in this repo — nearest existing TB under `dv/uvm/` |
| Output root (e.g. `dv/<block>/`) | required |
| Interfaces to instantiate | from the spec |

For a **per-component** add (Mode C):

| Input | Default |
|---|---|
| Component type | agent / sequence / test / coverage / checker / interface / env-update |
| Component name (e.g. `apb`, `cla_match_event`) | required |
| Existing TB path | required — defines where the new file lands |
| VP section driving this component | required for coverage / tests |

### 2. Read the reference template

Extract conventions from the nearest existing TB under `dv/uvm/` (or the project
template path, if one is supplied):

| Concern | What to extract from the template |
|---|---|
| Directory layout | top-level dirs (`agents/`, `tests/`, `sequences/`, ...) |
| File naming | `<proto>_pkg.sv`, `<proto>_if.sv`, `<block>_base_test.sv`, ... |
| Package import order | transaction → config → sequencer typedef → driver → monitor → agent → base_sequence |
| Clocking / reset | `clk`, `rst_n` interface params; `uvm_config_db` keys |
| Agent shape | conditional sqr/drv on `is_active`, analysis-port pass-through |
| Sequence shape | `uvm_sequence` base, `body()` with `start_item`/`finish_item` |
| Test shape | `uvm_test` base, `build_phase` instantiates env, `run_phase` raises objection |
| Coverage shape | module bind, covergroup with `coverpoint` + `cross` |
| Checker shape | SVA module with `bind`, every `assert property` has matching `cover property` |

### 3. Generate

WHEN scope = whole TB:
  DO produce the full directory tree from the template, parameterised on block name and interface list.
  EVIDENCE diff with all new files + a one-line readme at the TB root.

WHEN scope = component:
  DO produce only the new file(s), placed at the right path in the existing TB.
  EVIDENCE diff containing the new file(s) + any minimal edits to `<block>_env.sv` / `<block>_test_pkg.sv` to wire it in.

## Verify the generated code compiles

Run the project's lint / elaborate step on the new code before reporting success.

```
WHEN lint passes:
  REPORT success with the file list and the next steps (write sequences, run smoke test).

WHEN lint fails:
  REPORT the diagnostics with `file:line` and the recommended fix — do NOT silently mark the TB as ready.
```

## Decision rules

WHEN the spec mentions ≥ 2 distinct protocol interfaces:
  DO generate one agent per interface, not a multi-protocol mega-agent.

WHEN coverage is in scope:
  DO place coverage in a separate `<block>_coverage.sv` bound module, not inside agents.

WHEN the component is a checker:
  DO ensure every `assert property` has a matching `cover property` in the same file.

WHEN the user asks for a "minimal TB":
  DO generate one passive monitor + one passive agent + a smoke test only. Skip coverage and checkers unless explicitly requested.

WHEN the scope is component = sequence (a `constraint`-bearing artefact):
  DO pre-validate the constraint set with the SMT-solver capability before lint/compile — catch over-constraint and contradictions at edit time, not at sim time.
  EVIDENCE verdict captured in the output report; UNSAT blocks lint until the constraint is fixed. Hand off to `uvm-test-generation` if the user wants the full author-validate-smoke loop.

## Output format

```
## TB Scaffold Generated — <block>

### Files created
- dv/<block>/<files>   (or tb/<dut>/<files> for Mode A)

### Files modified (per-component case only)
- <file>: <one-line>

### Compiles?
- ✓ lint clean    OR    ✗ <n> diagnostics — see below

### Next steps
1. <smallest concrete next action — e.g. "write the first sequence at dv/<block>/sequences/...">
2. ...
```

## Compatible tools

| capability | concrete tools |
|---|---|
| DUT port / hierarchy discovery | siliconpilot MCP `slang_hierarchy`/`rtl_analyze`, read RTL source |
| static lint | the repo's `lint-check` skill (verilator via fusesoc) |
| AST cross-reference | siliconpilot MCP `slang_xref` |
| constraint pre-validation | [no SMT-solver MCP tool in this repo — fall back to by-eye constraint review, per uvm-test-generation's UNTRANSLATABLE path] |
| pattern search | `grep`, `rg` |
| file glob | `glob`, `find` |

## What success looks like

- Mode A produces a compile-clean single-agent TB derived from the DUT's actual ports.
- The new files match the bundled template's naming, layering, and import order.
- Compile / lint passes on the generated code.
- Every required component named in the VP exists in the generated tree (Mode B).
- The output report names a small concrete next step (not "good luck, write tests").
