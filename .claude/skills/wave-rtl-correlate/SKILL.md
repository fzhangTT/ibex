---
name: wave-rtl-correlate
description: Root-cause a signal misbehavior at a specific waveform time by combining RTL structure, fan-in dataflow, and timing values in one round-trip (parallel tool calls), instead of 10 sequential lookups. Use when both an FSDB and the RTL are available and a failure time is known; not for a signal with no FSDB yet (waveform-querying first) or a log with no localized time (sim-debug first).
---

Adapted from ChipSmart (riscv/ChipSmart) wave-rtl-correlate.

# Waveform + RTL Correlation (one-shot context pull)

A single waveform query tells you *what* a signal did. A single fan-in walk tells you *who* drives it. A single hierarchy elaboration tells you *where* it lives. Chasing these sequentially costs 10+ tool calls and a stale context. This skill collapses the discovery into ONE round-trip so reasoning can start immediately.

## When to apply

- "Why is signal X stuck/wrong at time T?" with both an FSDB and an RTL workspace available.
- An assertion fired at a known time and the user wants the cause.
- A scoreboard mismatch is localized to a specific cycle and you need to find the driver chain.

Not for:
- A signal name only, no FSDB → use `waveform-querying` to discover the file first.
- A regression log with no localized time → use `sim-debug` to extract the failure time first.
- A formal counterexample with no FSDB — not applicable in this repo (no formal-FV flow).

## Required capabilities

Declare these to the host before invoking. If any is unavailable, fall back as noted.

| capability | purpose | fallback if missing |
|---|---|---|
| **AST-elaboration tool** | Resolve module hierarchy and locate where the failing signal lives. | Read top-level RTL files manually; flag as best-effort. |
| **fan-in / cone-of-influence tool** | Enumerate the signals that drive the failing signal. | Regex-grep for direct drivers; expect lower precision. |
| **waveform-query tool** | Return value transitions for named signals in a time window (Python OR SQL). | Skip step 3; ask the user for the values. |

## Workflow

> **Run steps 1–3 as parallel tool calls in a single assistant turn.** Don't wait for results between them. The point of this skill is parallelism — sequential execution sacrifices its main value.

### 1. Locate the signal structurally

Elaborate the RTL workspace to confirm which module the failing signal lives in and what instantiates it. Pass the workspace glob and the inferred top module. If the top module is unknown, do ONE listing of the RTL root and pick the obvious top — do not iterate globs.

### 2. Walk the fan-in cone

From the failing signal, enumerate everything that drives it. Treat as root-cause candidates only the leaves that are **NOT registers** and **NOT external inputs** — these are the combinational drivers whose latest transition could have caused the failure.

### 3. Pull the timeline

Query the waveform for transitions of the candidate signals in a window around the failure time. Default window: `[t - 100, t + 10]` in the file's native time units. If the cone signals aren't known yet (first pass without waiting on step 2), use a scope-derived LIKE pattern as a coarse filter:

```
# Illustrative shape — adapt to the host's waveform-query surface:
SELECT t, name, value FROM changes
WHERE name LIKE '<signal_scope>%'
  AND t BETWEEN <failure_time - 100> AND <failure_time + 10>
ORDER BY t, name;
```

After step 2 lands, narrow to the precise cone signal list.

### 4. Synthesize root cause

After all three results are in context, reason in this order:

1. **Structure** — from step 1, name the module and its parent. State what the signal is supposed to do.
2. **Fan-in** — from step 2, list the candidate drivers (omit registers and tied inputs).
3. **Timeline** — from step 3, list the last 5–10 transitions before `<failure_time>` of the candidate signals.
4. **Diagnosis** — the candidate that transitioned latest before the failure AND disagrees with its expected value is the root cause. State it in one sentence with the cycle.

## Decision rules

WHEN no failure time is given:
  DO refuse and route the user to `sim-debug` to extract the time from the log first.
  EVIDENCE a single sentence: "I need a failure time — typically from $fatal, an assertion fire, or a scoreboard mismatch line in the run log."

WHEN the fan-in cone returns >50 candidates:
  DO filter to the subset that transitioned within the window from step 3, then re-run step 4 with the filtered list.
  EVIDENCE explicit mention of "n candidates pre-filter, m post-filter".

WHEN the waveform tool reports no data in the window:
  DO widen the window to `[t - 1000, t + 100]` once, and report the new bounds. Do not widen further automatically — ask the user.
  EVIDENCE a note that the original window was empty.

WHEN the candidate driver is a register (DFF leaf):
  DO recurse step 2 from that register's data-input expression as the new "failing signal."
  EVIDENCE explicit mention of the recursion and the new target signal.

## Compatible tools

| capability used | concrete tools (any one suffices) |
|---|---|
| AST-elaboration | siliconpilot MCP `slang_hierarchy`, manual `read` of RTL |
| fan-in / cone-of-influence | siliconpilot MCP `cone_of_influence`, `slang_xref` + manual walk |
| waveform-query | siliconpilot MCP `queryWaveform`, or fsdb-mcp-server's `get_signal_drivers`/`sample_signals_at_time`/`count_signal_transitions` |

## Output format

Report under exactly these headings, in order:

```
## Structure
<module path · file:line where the signal is declared · parent that instantiates it>

## Fan-in (candidate drivers)
- <signal_1>  (kind: comb / register / input)
- <signal_2>  ...

## Timeline (last N transitions before <failure_time>)
| time  | signal     | prev → new |
|-------|------------|------------|
| ...   | ...        | ...        |

## Diagnosis
<one sentence naming the root-cause signal and the cycle it went wrong, e.g.
"`top.dut.u_arb.grant_int` deasserted at t=4998 due to `req_mask[2]` going X
at t=4997; the arbiter's combinational grant path then produced the failure
at t=5000.">
```

## What success looks like

- Three tool calls fire in one assistant turn, not three.
- The diagnosis names a specific signal and cycle, not a general area.
- The user does not need to ask a follow-up "which signal?" question.
- Total round-trips from prompt to diagnosis: 1 (this turn) + 1 (the diagnosis turn) = 2.

## Anti-patterns

- ✗ Calling the three tools sequentially across multiple turns.
- ✗ Reading RTL files with `view`/`read` before step 1 returns — the elaboration already gives you the structural picture.
- ✗ Grepping for instantiation or driver patterns when an AST-elaboration tool is available — the cone tool will fail downstream if you skip elaboration.
- ✗ Widening the time window without bound. If `[t-100, t+10]` is empty, ask the user — don't sweep.
- ✗ Treating registers as root causes. They are intermediate state; the bug is on their data input.

## Optional: illustrate with a diagram

Optional, only when it sharpens the diagnosis — don't add one by default. See
the `diagram-builder` skill for format syntax.

- **The timeline (step 3)** → a ` ```wavedrom ` block of the last N transitions
  before `<failure_time>`, drawn from the values you pulled. It renders INLINE
  as a waveform card and makes the "stuck/wrong at cycle T" obvious at a glance.
- **The fan-in cone (step 2)** → a small ` ```mermaid ` `flowchart` of
  driver → … → signal when the causal chain has several hops worth showing.
