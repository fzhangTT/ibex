# TB Contract: cocotb (Python) stimulus on the `core_ibex` UVM TB

This document describes the **interfaces** a test may use to drive stimulus from Python
via cocotb, running alongside the existing UVM testbench. It does not describe TB
internals or any specific existing test — only the API surface, its semantics, and the
rules a caller must follow to use it correctly.

## 1. Two-level selection

- `COCOTB=1` (make knob, default `0`) compiles the cocotb coexistence overlay into the
  TB build. `COCOTB=0` compiles none of it in — every interface in this document simply
  does not exist in that build.
- `COCOTB_MODULE=<dotted.module>` (make knob, default `dv.cocotb.ibex_cocotb`) selects
  which Python module cocotb imports at run time, resolved on `PYTHONPATH` from the repo
  root. Point it at your own test module's dotted path to select which test runs.
- `+cocotb_*` plusargs, added to a testlist entry's `sim_opts`, parameterize stimulus at
  run time. Read them in test code via `cocotb.plusargs.get("name", "default")` — values
  arrive as strings; cast to the type you need.

## 2. Handshake API (`dv.cocotb.common.handshake`)

- `await start(dut)` — call once, first, in every test. Signals the cocotb process is
  alive and stimulus is active (in that order), and logs the run's seed.
- `await finish(dut, timeout_ms=2)` — call once, last, after all of your own checks have
  already run and asserted (see the checking-obligation and Hard Rule 1 below). Clears
  the active flag, then polls for the UVM side's completion signal, raising `TimeoutError`
  if it does not arrive within `timeout_ms`.

**Hard rule 1 — assert before `finish()`, never after.** The flow's log scanner stops
treating `Error` lines as failures once it has seen the UVM PASS banner, which only
prints once the whole run reaches its own completion handshake — at or after the point
`finish()` would return. A check placed after `finish()` can never fail the flow.

**Hard rule 2 — ASCII only in every string that may be logged or raised.** cocotb's
failure-logging path uses an ASCII-only stream encoder; a non-ASCII character (e.g. an
em-dash) crashes that log call instead of reporting the real error, which swallows your
failure text and can turn a real failure into a silent false PASS.

**Hard rule 3 — mind the post-report assertion window.** The TB runs with UVM's
own `finish_on_completion` cleared, since cocotb (not UVM) owns ending the simulation —
so the simulation keeps clocking between UVM's own summary/report and the point `finish()`
observes completion and returns. Any DUT assertion can still fire in that window on an
unlucky seed. Call `finish()` promptly once your own checks are done; don't add
unnecessary delay before it.

**`timeout_ms` sizing:** the default (`2`) is sized for a minimal program. A test that
generates a substantially larger program, and/or drives multiple rounds of stimulus
through a TB agent, must pass a `timeout_ms` sized to how long *that* program actually
takes to reach its own completion handshake — nothing scales this automatically, and an
undersized budget raises `TimeoutError` on an otherwise-passing run.

## 3. uvm_bridge API (`dv.cocotb.common.uvm_bridge`)

- `trigger(ev_name: str)` — triggers a named global TB event synchronously. No setup
  or scope handling is required by the caller; the module handles that internally.
- Available event names:
  - `"cocotb_irq_raise"` — one `trigger()` call drives one full external-irq raise/drop pulse
    (the TB side owns both the raise and the drop timing; the caller does not trigger a
    separate drop event).
- `cocotb_if.uvm_ready` — a bit set once the TB-side listener for a given event is armed.
  Await it before your first `trigger()` call to close the startup race between your test
  and the TB arming its listener.
- Accounting counters exposed on `cocotb_if` (integers, monotonic for the run):
  `cocotb_if.trigger_received_count` increments once per triggered event the TB side
  actually observes, and `cocotb_if.handler_entry_count` increments once per unit of
  stimulus the TB agent actually services. Compare your own triggers-sent count against
  `trigger_received_count` (equal ⇒ nothing was dropped) and check `handler_entry_count`
  against what your stimulus should have produced, before calling `finish()`.

**Hard rule 4 — event triggers are not queued.** A `trigger()` call that arrives while
the TB-side listener is still mid-response to a previous trigger is silently dropped —
`uvm_ready` only closes the *startup* race, not this one. Space consecutive triggers by
more than the listener's own response hold time plus whatever latency the agent's
sequence takes to start and complete, and use the accounting counters above to detect a
drop rather than assuming delivery.

## 4. Seeds

- `RANDOM_SEED` (Python-side environment variable, read at `start()`) and
  `+ntb_random_seed` (SV-side plusarg) must carry the same value for a reproducible run.
  The run flow sets both from the same seed automatically; a test invoked outside that
  flow must set both itself to stay reproducible.

## 5. Testlist-entry rules for any test using this contract

**Hard rule 5a — vacuous-pass guard.** If a testlist entry's `sim_opts` include a
`+cocotb_*` plusarg, the non-cocotb (`COCOTB=0`) build path for that same `rtl_test` must
`uvm_fatal` if that plusarg is present. Without this guard, building the same entry
without `COCOTB=1` silently runs as a plain test under a name that claims cocotb-driven
coverage it never exercised.

**Hard rule 5b — choose `iterations` consciously.** If a test's timing (event spacing,
hold times, settle waits) was tuned and verified against specific seed(s) only, pin
`iterations` to those seeds rather than implying a full multi-seed sweep is safe — an
untuned timing corner on a different seed can false-FAIL a test whose stimulus logic is
otherwise correct.

## 6. Checking obligation

Verbatim from the design spec's WS2 amendment
(`docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md`):

> a generated test/TB deliverable must carry its own checking strategy (self-checking
> stimulus, generated SVA, and/or its own reference-model integration built from
> *upstream* open-source imports) and declared functional-coverage expectations; it may
> not assume any hidden referee catches what its own checks miss.

## 7. Functional-coverage expectation duty

Every new test declares the functional-coverage bins it intends to hit, and a
declared-but-unhit bin fails the run. This is enforced, not aspirational — see the
`fcov-expectation` skill (`.claude/skills/fcov-expectation/SKILL.md`) for the manifest
format, the anti-vacuity review each declared bin's sampling condition must pass, and the
namespace rule for generated covergroups.
