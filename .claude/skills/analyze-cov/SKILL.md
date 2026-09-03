---
name: analyze-cov
description: Analyze a spec + RTL + DV to identify the functional coverpoints, crosses, and code-coverage gaps a coverage plan needs, or name the gaps in an existing urg/vdb report. Use when a block needs its coverage plan written, coverage is below target, or a spec change invalidated existing coverpoints — not for authoring the covergroup SV (use covergroup-authoring) or the testplan rows (use verification-planning-test-generation).
---

Adapted from ChipSmart (riscv/ChipSmart) analyze-cov.

# Analyse Coverage

Read the spec, the RTL, and the existing testbench (if any), and produce a coverage plan: what to cover, why each item matters, and how it maps to the DV's covergroup structure. When existing coverage data is supplied, also identify gaps.

## When to apply

- A new IP / block needs its coverage plan written.
- Coverage from a regression run is below target and the team needs to know what to add.
- A spec change has invalidated existing coverpoints.
- The user supplied a UCDB / VDB / coverage report and wants the gaps named.

Not for:
- Writing the SV covergroup code itself → that's part of `create-tb`.
- Identifying which test failed → `regression-triage` or `sim-debug`.
- Choosing the testplan rows that drive the coverage → `verification-planning-test-generation`.

## Workflow

### 1. Gather inputs

| Input | Default |
|---|---|
| Spec / VP | required |
| RTL root | required |
| Existing TB / coverage code (if any) | discovered from path |
| Existing coverage data (UCDB / VDB / merged) | optional |
| Target coverage % | project default (90% / 95% / 100%) |

### 2. Enumerate the verification surface

For each interface and capability, identify the dimensions that need to be covered:

| Dimension | What it captures |
|---|---|
| Transaction kind | every legal protocol transaction |
| Data values | boundary (0, 1, max, max+1) + a handful of mid-range |
| Address ranges | every spec'd address region + boundary |
| Modes | reset, idle, active, debug, low-power transitions |
| Errors | every spec-stated illegal-input case |
| Concurrency | (interface × interface) crosses for shared resources |
| Sequence ordering | back-to-back, gapped, interleaved transactions |

For each, decide: covergroup, single coverpoint, or cross.

### 3. Decide the bin strategy

For every coverpoint, choose bins deliberately:

| Pattern | When to use |
|---|---|
| `bins zero = {0}; bins one = {1}; bins max = {[MAX-1:MAX]};` | Boundary coverage on integer fields |
| `bins valid_codes[] = {[0:7]};` | Enum-style fields with finite valid range |
| `bins error_codes = {SLVERR, DECERR};` | Error-class fields |
| `ignore_bins reserved = {[X:Y]};` | Spec-reserved values |

Avoid: trivial coverpoints that bin every value (`bins all[] = {[0:$]}`) — these inflate "coverage" without proving anything was exercised.

### 4. Plan crosses

Crosses are the most expensive coverage element. Plan them deliberately:

| Cross | When |
|---|---|
| (transaction × mode) | mode-dependent behaviour exists in spec |
| (transaction × error) | error injection per transaction type |
| (interface_A × interface_B) | shared-resource arbitration |
| (param × scenario) | parameterised RTL with multiple legal values |

Avoid: Cartesian-product crosses that explode bin counts past what regression can hit.

### 5. Identify code-coverage gaps (if data supplied)

When the user provides a UCDB / VDB / coverage report:

| Gap kind | How to read it |
|---|---|
| Unhit lines | RTL lines reached zero times |
| Unhit branches | conditional taken zero times |
| Unhit toggles | signals that never changed |
| Unhit FSM states | states the testbench never reached |
| Unhit FSM transitions | edges the testbench never exercised |

For each unhit element, propose a stimulus that would reach it. Cite the RTL `file:line`.

### 6. Output the coverage plan

```
## Coverage Plan — <block>

### Inputs
- Spec: <path>
- RTL: <path>
- TB: <path or none>
- Coverage data: <path or none>

### Covergroups
| cg name | dimension | bins | crosses |
|---|---|---|---|
| cg_axi_xact | type × len × strb | per-type, boundary lens | none |
| cg_axi_err | resp code | per-error | with mode |

### Crosses
| cross | rationale | size (bins) |
|---|---|---|
| (xact × mode) | mode-dependent path in spec §4.2 | 24 |

### Gaps (if data supplied)
| Element | RTL location | Why unhit | Proposed stimulus |
|---|---|---|---|
| <fsm_state> | <file:line> | error path never reached | inject SLVERR on read |

### Sign-off bars
- Functional coverage target: <target>%
- Code coverage target: <target>% line, <target>% branch
- Specifically required 100%: list (e.g. error covergroups, reset state)

### Open questions
- <one-line>
```

## Decision rules

WHEN a coverpoint would have > 1000 bins:
  DO redesign it. Bins that regression can't realistically hit are theatre.

WHEN a cross would produce > 100 bins:
  DO add `ignore_bins` for impossible combinations OR redesign.

WHEN code coverage is < 80% but functional coverage is at target:
  DO surface this as a finding — the testplan is missing entries.

WHEN functional coverage is 100% but code coverage is < target:
  DO surface this as a finding — the testplan covers the spec but misses RTL paths.

## Compatible tools

| capability | concrete tools |
|---|---|
| coverage database | verdi-cov MCP (`vdb_find`/`vdb_functional`/`vdb_lines`/`vdb_toggles`), `urg -format text` |
| AST cross-reference | siliconpilot MCP `slang_xref` |
| pattern search | `grep`, `rg` |
| FSM extraction | siliconpilot MCP `fsm_extract` |
| structural reachability triage | siliconpilot MCP `cone_of_influence` over the elaborated AST (whole-design, conservative const-tie / const-function waivers) |
| bounded formal escalation (residual only) | [not applicable in this repo — no formal/BMC tooling in the ibex flow (formal-FV is out of scope); treat an unresolved reachability cone as a manual judgment call and cite it in the report rather than auto-escalating] |

## What success looks like

- Every covergroup has a one-line rationale that names the spec section it derives from.
- Every cross is deliberate; no Cartesian explosions.
- Every gap (when data is supplied) names a `file:line` and a proposed stimulus.
- Sign-off bars are explicit so the next agent knows when the plan is done.
