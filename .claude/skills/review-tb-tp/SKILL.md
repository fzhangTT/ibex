---
name: review-tb-tp
description: Audit a UVM testbench AND its companion verification testplan against the spec, methodology, and coding standards, producing a gap-and-quality report with file:line citations. Use for a TB/TP sign-off review before merge, or onboarding a TB to find its weakest spots; distinct from dv-principles-check (dv_principles.md conformance only) and cross-review (the diff-review policy gate) — this checks TB-structure-vs-testplan-vs-spec traceability.
---

Adapted from ChipSmart (riscv/ChipSmart) review-tb-tp.

# Review Testbench + Testplan

Audit an existing UVM testbench AND its associated testplan against the verification methodology, the spec, and the project's coding standards. Returns a report that lists `file:line` evidence for every finding so the verification engineer can act without re-reading the source.

## When to apply

- A TB / TP just landed and needs a sign-off review before merge.
- A pre-tape-out audit covering both the TB structure and the testplan coverage.
- A team is onboarding a TB and wants to know where its weakest spots are.
- The testplan is being reviewed for gaps before regression sign-off.

Not for:
- Writing a new TB from scratch → use `create-tb`.
- Triaging which TB tests failed in a regression → use the `regression-triage` specialist.

## Workflow

### 1. Gather inputs (mandatory first step)

Confirm with the user:

| Input | Default if unspecified |
|---|---|
| TB location (path) | required — do not guess |
| Testplan location (path or doc system) | required |
| Spec / VP reference | required — used as ground truth |
| Verification methodology / VM template | host or project default |
| Coding-standards doc | host or project default |
| Review scope | full = structure + functional + coverage + TP gaps |
| Output location | `dv/<block>/docs/review-<YYYY-MM-DD>.md` |

### 2. Read reference materials

- Spec / VP → ground truth for what must be covered.
- VM template → gold standard for naming, packaging, agent/env shape.
- Coding standards → style + safety rules (clocking, reset, SVA discipline).

### 3. Audit the testbench

Categories (skip those not in scope):

| Category | What to check |
|---|---|
| Structure | dir layout, file naming, package import order, agent → env → test layering |
| Conventions | clk/reset signals, interface params, `uvm_config_db` keys |
| Components | every required agent/sequencer/driver/monitor/scoreboard is present |
| Sequences | base / virtual / feature sequences exist for every TP entry |
| Coverage | every TP coverpoint has a coverage element, every bin reachable |
| Checkers | every SVA has a matching cover; assertions name the property |
| Methodology | phase ordering, `connect_phase` correctness, `objection` lifecycle |

### 3b. Adversarial pass — verification that silently doesn't verify

The table above finds what's missing. This pass finds what's *present but defeated* —
the highest-value TB findings. For each, report `file:line`, the failure mode it hides,
and a concrete fix:

- **Dead / unbound checker** — an assertion or checker module defined but never
  instantiated or bound (grep its instantiation/bind; absent = dead code that reads as
  a live checker).
- **Computed-but-unchecked** — an expected/predicted value computed but only fed to a
  `uvm_info`/log, never compared against the DUT.
- **Defeated checks** — global severity overrides (`set_report_severity_override`
  UVM_ERROR→UVM_INFO), `disable_*check` plusargs, holdoff/blind windows that never
  adjudicate, or a waiver/exclusion file a flag points at that does not exist.
- **Structurally-impossible coverage** — a needed cross whose coverpoints live in
  different covergroups/modules; `default`-binned multi-way points that collapse
  combinations; value coverpoints that only sample booleans.
- **Stimulus that never runs where it counts** — tests in no testlist, or run only in a
  build where `--cov` is stripped, so they add zero functional coverage.
- **Dangling / tied ports** feeding coverage or error injection (hardcoded 0, `//FIXME`).

Tie every coverage gap to the RTL fact that makes it reachable and important (reset
value, tick increment, comparator depth, remap/fuse logic) — never a generic "add more
bins".

### 4. Audit the testplan

| Aspect | Check |
|---|---|
| Spec coverage | every spec section maps to ≥ 1 TP entry |
| Edge cases | boundary, error, reset, concurrency for every interface |
| Physical validity | constraints reflect post-PD reality (no fictional timing) |
| Automation | every test entry is automatable or marked manual with reason |
| Regression class | each entry tagged `smoke / nightly / weekly / one-off` |
| Owner / status | every entry has an owner; status is `planned / in-progress / done / retired` |

### 5. Decision rules

WHEN a TB component is missing for a TP entry:
  DO record under `Gaps`, severity = `BLOCKER` if smoke-class entry
  EVIDENCE `<tp-entry-id>` ↔ `<tb-component-not-found>`

WHEN a spec section has no TP entry:
  DO record under `TP Gaps`, severity = `MAJOR`
  EVIDENCE `<spec section>:<line-range>` ↔ `<no matching TP entry>`

WHEN a sequence exists but no test invokes it:
  DO record under `Dead code`, severity = `MINOR`
  EVIDENCE `<sequence file:line>`

WHEN an SVA exists without a cover:
  DO record under `Methodology violation`, severity = `MAJOR`
  EVIDENCE `<sva-file:line>`

## Output format

```
## TB + TP Review — <block> — <YYYY-MM-DD>

### Summary
| Category | Findings | Blockers | Major | Minor |
|---|---|---|---|---|
| TB structure | 3 | 0 | 1 | 2 |
| TB components | 8 | 2 | 3 | 3 |
| TP gaps | 12 | 1 | 5 | 6 |
| Methodology | 4 | 0 | 2 | 2 |

### Blockers
- [BLOCKER] <one-line> — evidence: <file:line> ↔ <tp-entry>

### Major
- [MAJOR] <one-line> — evidence: <file:line>

### Minor
- [MINOR] <one-line>

### Open questions
- <one-line>

### Recommended next steps
1. <one concrete action, ordered by severity>
2. ...
```

## Compatible tools

| capability | concrete tools |
|---|---|
| pattern search | `grep`, `rg` |
| file glob | `glob`, `find` |
| AST cross-reference | `slang_xref` (SP), Verible LSP |
| testplan reader | host's TP / Excel reader, or markdown TP |

## What success looks like

- Every finding has a `file:line` (TB) or testplan entry id (TP) citation.
- Severity ladder is consistent: BLOCKER blocks merge, MAJOR blocks sign-off, MINOR tracks.
- Recommended next steps are ordered by severity and small enough to act on individually.
- No motherhood statements — every line is an observable finding.
