---
name: uvm-test-generation
description: Author a single new UVM sequence/sequence_item/test end-to-end — pick the base class, declare rand fields, write constraints, pre-validate the constraint set (SMT solver where available) before the build-sim cycle, wire into the env, run a smoke. Use for "write me a sequence that…" with one concrete artefact in scope and the TB already existing; compose with the `ibex-test-generator` agent for the trust-triad evidence (fcov-expectation, mutation-check) the agent adds on top.
---

Adapted from ChipSmart (riscv/ChipSmart) uvm-test-generation.

# UVM test generation

Author one new UVM artefact (sequence, sequence_item, or test) end-to-end. The unique value of this skill is the **constraint pre-validation step** that catches `randomize()` failures and over-constraint at edit time, before paying the build-sim-fail cycle. Sister skills handle other intents: `create-tb` for whole-TB scaffold, `coverage-closure` for closing a specific covergroup hole; the `ibex-test-generator` agent wraps this same author-validate-smoke loop with the repo's trust-triad evidence requirements.

## When to apply

- "Write me a sequence that …" / "add a test for …" with one concrete artefact in scope.
- The user has the intent in plain English; the testbench, agents, sequencer, and config are already in place.
- The artefact must compile, randomize successfully, and run to at least one transaction before being declared done.

Not for:
- Building the testbench itself or adding an agent → `create-tb`.
- A stub aimed at one missing covergroup bin → `coverage-closure`.
- Translating a spec into a multi-test plan → `verification-planning-test-generation`.

## Workflow

### 1. Pin the intent

Capture one sentence: *what stimulus does the new artefact produce, and how will we know it worked?* Without this the rest of the workflow has no target. Anchor it to a coverpoint, an assertion, a VP row, or a known bug — anything checkable.

EVIDENCE: a one-line "goal" + the checkable signal/cover the smoke step will inspect.

### 2. Pick the closest existing artefact and the right base class

Use a **testbench catalogue** to find an existing sequence / sequence_item / test whose name or payload class signal-matches the intent (shared protocol, shared agent, shared transaction). That one becomes the parent class (`extends …`) — almost never start from `uvm_sequence`/`uvm_test` directly. If nothing close exists, fall back to the project's documented base (`<block>_base_vseq`, `<block>_base_test`).

EVIDENCE: name of the chosen base class + the file/line where it's defined.

### 3. Declare rand fields with explicit widths

Every `rand` / `randc` field needs a width-pinned type (`rand bit [N-1:0] f;`). Unsized `int` is allowed but discourages width checks downstream. If the field is an array, prefer fixed-size `[K]` so the SMT step can unroll `foreach`.

WHEN a field's allowable range is known from the spec (e.g. "instance ∈ 0..N-1"):
  DO declare it `inside { [0:N-1] }` as a constraint, not as a literal type cast.
  EVIDENCE the constraint block names the spec-side range.

### 4. Author constraints

Write each clause one at a time. The pattern matters more than the syntax — prefer **declarative** (`inside`, `dist`, `==`, `->`, `&&`) over procedural (functions in constraints). Use `solve … before …` only when ordering matters for distribution, not for feasibility.

### 5. Pre-validate the constraint set with the SMT solver (the load-bearing step)

Before compiling the testbench, run the **constraint-validation** capability against the bare constraint set (no missing-bin predicate — just "does this seq's `randomize()` have any solution?"). Four outcomes:

| Verdict | Meaning | Action |
|---|---|---|
| **SAT (with witness)** | The constraint set is satisfiable; the witness shows one admissible assignment. | Sanity-check the witness — does it look like a useful stimulus? Tiny admissible region (1-2 witness combinations across many runs) means the seq is over-constrained even though it solves. |
| **UNSAT (with core)** | The constraint set has no solution; `randomize()` would always fail. The core names the contradictory clauses. | Edit the clauses in the core. Re-run the check. Do NOT compile until SAT. |
| **UNKNOWN (timeout)** | Solver couldn't decide in the timeout. Often signals genuinely-hard constraints (large bit-widths × nonlinear arithmetic). | Increase timeout once; if still UNKNOWN, simplify the offending arithmetic or accept that this seq's pre-validation is a manual-eye step. |
| **UNTRANSLATABLE** | The constraint uses constructs outside the solver's reach (function calls, inter-object refs, soft constraints, `pre/post_randomize`). | Read the constraint by eye. The solver doesn't help here; rely on the smoke step in §7 instead. |

EVIDENCE: solver output captured (verdict + witness / core / reason). Tag the SV file with a brief comment if the verdict was relied on.

### 6. Write the procedural body

`function new`, optional `pre_start` / `pre_body`, then `task body()`. Use the project's transaction-send macros (`uvm_send`, `uvm_do_with`, `start_item/finish_item`) — do not invent a new pattern. Wire the rand fields into the transaction via `randomize() with { … }` only when the call-site needs additional constraints beyond what the class already has.

WHEN the seq sends multiple transactions:
  DO either declare the rand fields *inside* the loop (re-randomise each iteration) or use `randomize()` again per iteration.
  EVIDENCE the body shows where the next set of rand values is drawn.

### 7. Wire into the env / test list

For a new sequence: register with `uvm_object_utils` and put it in `<block>_sequences_pkg.sv`'s include list. For a new test: register with `uvm_component_utils`, add to `<block>_tests_pkg.sv`, and add a row to the regression list so the smoke step can `+UVM_TESTNAME=` it.

### 8. Smoke step — compile, elaborate, one-shot run

Compile + elaborate. Run the testbench with the new test/seq + a seed; require at least:
- One successful `randomize()` call.
- One transaction observed at the monitor's analysis port (or at the DUT pin in a waveform).
- No `UVM_FATAL` / `UVM_ERROR` in the first 1k ns.

WHEN the smoke fails despite SMT verdict SAT:
  DO triage as either (a) a constraint solver corner case (the SMT translator missed a construct → bug for §5), (b) a procedural body bug, or (c) a TB wiring bug (sequencer mismatch, missing config_db key).
  EVIDENCE the triage names which of (a/b/c) and points at the specific file/line.

## Decision rules

WHEN the closest existing seq differs only by a constraint clause:
  DO emit a derived class that calls `super.new` and adds the diff, not a from-scratch class.
  EVIDENCE the new class is < 50 LoC and inherits the rand surface.

WHEN no testbench catalogue exists yet:
  DO bring up the catalogue (rebuild the UVM index) before authoring; the closest-base lookup is the load-bearing input.
  EVIDENCE the index is fresh (timestamp newer than any recent SV edit under `dv/**`).

WHEN the SMT verdict is UNSAT:
  DO NOT compile. Fix the constraint, re-run the SMT check, and only then proceed to §7.
  EVIDENCE the second SMT run returns SAT and the unsat-core from the first run is referenced in the fix's commit message or comment.

WHEN the SMT verdict is UNTRANSLATABLE (function call / inter-object / soft / pre-post-randomize):
  DO skip pre-validation, document the skip in a one-line `// SMT-skip: <reason>` comment above the constraint block, and rely on the smoke step to catch errors.
  EVIDENCE the comment names the un-supported construct so a later reader knows why pre-validation was skipped.

WHEN the project uses parameterised base classes (`#(NUM_X, NUM_Y, …)`):
  DO match the parameter list of the closest existing seq; do not introduce a new parameterisation.
  EVIDENCE the new class's `extends` clause names the same parameters in the same order.

## Compatible tools

| capability | concrete tools |
|---|---|
| testbench catalogue (UVM) | UVM analyser → sqlite DB, `sv-parser` + indexer, Verible AST + grep |
| constraint validation (SMT) | Z3 or CVC5 driven by SMT-LIB stdin; a SV → SMT-LIB translator sits between the constraint AST and the solver |
| static lint | `verilator --lint-only`, `slang --lint-only`, project-native |
| AST cross-reference | `slang_xref`, Verible LSP |
| file edit / pattern search | host-native; `grep`, `rg` |

## Output format

A unified diff (or list of new files) plus a markdown report with these sections, in order:

1. **Goal** — one sentence + the checkable signal/coverpoint from §1.
2. **Base class** — name, file, why-chosen, parameter list match.
3. **Rand surface** — table: `field | type | range from spec`.
4. **Constraints** — the new constraint block verbatim.
5. **SMT verdict** — SAT / UNSAT / UNKNOWN / UNTRANSLATABLE; if SAT show the witness, if UNSAT show the core + how it was fixed.
6. **Wiring** — files touched to register the new artefact.
7. **Smoke result** — randomize succeeded? transaction count at monitor? duration to first transaction?

## What success looks like

- The new artefact compiles cleanly under project lint.
- The SMT pre-validation either returned SAT (with a sensible-looking witness) OR an explicit `// SMT-skip:` comment names the unsupported construct.
- The smoke run produces at least one observed transaction and zero fatal errors.
- The report names the next concrete extension (more bins to hit, follow-up coverage, regression-list entry) — not "good luck."
