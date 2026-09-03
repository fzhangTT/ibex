---
name: verification-planning-test-generation
description: Produce a comprehensive verification testplan from a spec — concrete stimulus, measurable criteria, coverage plan, simulation-checked SVA properties, and regression classes, each row traceable to a spec section — then optionally generate the matching test/sequence/coverage stubs. Use when a block has a spec but no testplan, or an existing TP needs refreshing against a spec change; not for reviewing a TB against a TP (use review-tb-tp) or generating just the scaffold (use create-tb).
---

Adapted from ChipSmart (riscv/ChipSmart) verification-planning-test-generation.

# Verification Planning + Test Generation

Take a spec (architecture doc, IP datasheet, microarchitecture spec) and produce a testplan: structured rows of `id / scenario / stimulus / expected / coverage / regression-class / spec-traceback / owner`. Then optionally generate the matching SystemVerilog test/sequence/coverage stubs.

## When to apply

- A new IP / block has a spec but no testplan.
- An existing testplan has gaps and needs to be refreshed against the latest spec.
- A spec change needs to be propagated into the TP.
- The user has a TP and wants the test stubs / coverage / formal properties auto-generated.

Not for:
- Reviewing a testbench against an existing TP → `review-tb-tp`.
- Generating just the TB scaffold → `create-tb`.
- Authoring the spec itself — not a DV task.

## Workflow

### 1. Gather inputs

| Input | Default |
|---|---|
| Spec / VP document (PDF / md / xlsx) | required |
| Block / IP name | required |
| Existing TP (if any) | discover via path; merge instead of replacing |
| Reference TP for style (sibling block) | project's TP template |
| Output location | `dv/<block>/docs/tp.md` (or project default) |
| Scope | full / coverage-only / formal-only / regression-classes-only |

If the spec is a PDF or Excel, dispatch the `spec-extraction` skill first to lift the source material into structured form.

### 2. Discover the verification surface

For each interface and capability in the spec, identify:

| Aspect | What to enumerate |
|---|---|
| Interfaces | every protocol port (AXI, APB, JTAG, custom) |
| Modes | every operating mode (reset, idle, active, debug, low-power) |
| Configurations | every parameter sweep that's user-visible |
| Transactions | every legal transaction type |
| Errors | every error / illegal-input the spec says is detected |
| Performance | every measurable spec'd metric (throughput, latency, jitter) |

### 3. Build the testplan rows

For every (interface × mode × scenario) combination, emit one row. Aim for **concrete stimulus** and **measurable criteria**:

| field | example |
|---|---|
| id | `TP-AXI-001` |
| scenario | `Write burst of length 16, byte enables all-asserted` |
| stimulus | `axi_wr_seq#(LEN=16, BEN=16'hFFFF)` |
| expected | `RRESP == OKAY, data echoed on response port, no SVA fires` |
| coverage | `cp_burst_len[16]` |
| regression | `smoke` |
| spec | `<doc>#p12 §3.4.1` |
| owner | `<engineer or TBD>` |

WHEN the spec entry says "may be X or Y":
  DO emit one TP row per possible value.
  EVIDENCE cite the spec ambiguity in an Open Question.

WHEN the spec says "shall not happen":
  DO emit a TP row for the illegal stimulus AND the expected error behaviour.

WHEN a spec'd metric is measurable:
  DO emit a perf-class TP row with the threshold from the spec.

### 4. Plan coverage

For each TP entry, the coverage column names a covergroup / coverpoint that proves the test was actually run. Avoid the trap of covergroups that bin trivial values.

| covergroup type | when to use |
|---|---|
| transaction covergroup | per protocol transaction kind |
| cross | combinations the spec calls out as risky |
| mode-cross | (mode × stimulus) for mode-dependent behaviour |
| error covergroup | every spec'd illegal input |

### 5. Plan formal properties (where applicable)

[In this repo: these SVA properties are checked under simulation (VCS), not a
formal-proof tool — formal-FV flows are out of scope here.] For protocol
interfaces, every spec-stated invariant becomes an SVA property:

| property kind | shape |
|---|---|
| handshake | `assert property (req |-> ##[1:LATENCY] ack)` |
| ordering | `assert property (done |-> $past(start))` |
| stability | `assert property (valid && !ready |=> $stable(data))` |

Each `assert property` must have a matching `cover property` so coverage can confirm the antecedent was exercised.

### 6. Classify the regression

Each TP row gets a class:

| class | runs |
|---|---|
| `smoke` | every PR / nightly head; < 10 entries total per block |
| `nightly` | every night on main |
| `weekly` | once per week or on demand |
| `one-off` | bring-up / sign-off / not part of regression |

### 7. Generate stubs (optional)

WHEN the user asks for stubs:
  DO emit, for each TP row, a sequence skeleton + a coverage element + (where formal-applicable) an SVA property.
  Place them at the paths a downstream `create-tb` call would expect.

## Decision rules

WHEN a TP row has no measurable expected outcome:
  DO REJECT it. "Verify correct operation" is not a test — rewrite or drop.

WHEN two TP rows have the same coverage element:
  DO consolidate into one row OR split the covergroup so each test has a unique covenant.

WHEN the spec is silent on an interface's behaviour:
  DO emit an Open Question. Do not invent a TP entry from imagination.

WHEN a TP row's regression class is `weekly` or `one-off`:
  DO state the reason it isn't smoke/nightly (cost, simulation time, infra dependency).

## Output format

```
## Verification Testplan — <block> — <YYYY-MM-DD>

### Inputs
- Spec: <path>
- Existing TP: <path or none>

### Summary
| Interface | Modes | Entries | Smoke | Nightly | Weekly |
|---|---|---|---|---|---|
| AXI | 3 | 42 | 5 | 30 | 7 |
| JTAG | 1 | 12 | 2 | 8 | 2 |

### TP rows
| ID | Scenario | Stimulus | Expected | Coverage | Class | Spec | Owner |
|---|---|---|---|---|---|---|---|
| TP-AXI-001 | … | … | … | … | smoke | <doc>#p12 | … |
| TP-AXI-002 | … | … | … | … | nightly | <doc>#p12 | … |

### Coverage plan
- cg_axi_transactions: type × len × strb-pattern
- cg_axi_errors: every spec'd error code
- cross: (mode × transaction_type)

### Formal properties (if in scope)
| Property | File | Cover |
|---|---|---|
| axi_wr_handshake | <path>:<line> | ✓ matching cover |

### Open questions
- <one-line — e.g. "spec §4.2 says 'may be X or Y'; one TP row per value emitted; confirm intent">

### Generated stubs (if requested)
- <list of files written>
```

## Compatible tools

| capability | concrete tools |
|---|---|
| spec read | `pdfMarkdown` (SP), `pdftotext`, host PDF reader |
| Excel read | `ViewSpreadsheetRange` (SP), `openpyxl`, `pandas` |
| pattern search | `grep`, `rg` |
| AST cross-reference | `slang_xref` (SP), Verible LSP |

## What success looks like

- Every TP row has a measurable expected outcome (no "verify correct operation").
- Every TP row traces back to a spec page/section.
- Regression classification is intentional, with reasons for non-smoke entries.
- Coverage and formal plans are written, not hand-waved.
- Open questions enumerate every ambiguity in the source spec.
