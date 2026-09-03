# TB contract note (Zone A): cocotb-on-VCS-with-UVM mechanics

<!-- FENCE-ZONE: A -->
fence-integrity: PASS — 2026-09-02

A working cocotb + UVM + VCS integration exists on this site. This note records the mechanics
that were hard-won — seeding, the master-handshake pattern, the failure path, and logging rules —
so your from-scratch TB does not rediscover them. It is a mechanics reference, NOT an interface:
you design your own TB's interfaces yourself (seed prompt, Section 9). The wiring flags live in
`docs/dv/SIM_RECIPE.md` §4.

## 1. Seeding

One run seed drives every source of randomness. For a cocotb + SV run that means the SAME value
in two places, recorded together:

- `+ntb_random_seed=<seed>` — the SV/UVM side.
- `RANDOM_SEED=<seed>` — the environment variable cocotb reads for Python-side seeding.

Your run script sets both from one variable and logs the seed from BOTH sides at time zero. A
run where the two can differ is not reproducible; every failure must reproduce from test name
plus seed alone (seed prompt, Section 6).

## 2. The cocotb-master handshake pattern

When cocotb (not UVM) owns the end of simulation, three mechanisms keep a dead or slow Python
side from producing a silent false PASS. Build all three:

1. **Alive-bit watchdog — fails loud, in hardware.** The Python side sets an "alive" bit on an
   SV interface as its very first action; an SV initial block `$fatal`s if the bit is still
   clear after a fixed startup window. This catches total VPI/libpython load failure — the case
   where no Python code runs at all, so nothing on the Python side can report anything. (A
   Python import error of the test module is a different failure class: cocotb's own regression
   manager logs it CRITICAL with a traceback and ends the simulation at time 0. Both paths are
   loud, but they log differently — budget for both when triaging.)
2. **Objection holder / active flag.** The Python side raises "stimulus active" before driving
   and drops it only after its own checks have completed, so the SV side's end-of-test logic
   cannot conclude while Python work is outstanding.
3. **Finish polling with a caller-sized timeout.** The Python side ends the run by polling for
   the SV side's completion signal and raising a timeout error if it does not arrive within the
   budget. Size the default for the smallest program only; a heavier test passes its own budget —
   nothing scales it automatically, and an undersized budget fails an otherwise-passing run.

Order your end-of-test strictly: run ALL Python-side checks and assertions BEFORE the
finish/completion handshake. Once the UVM side reaches its own completion point it prints its
report, and anything raised after that point may no longer fail the run; the simulation also
keeps clocking between the UVM report and the actual `$finish`, so a DUT assertion can still
fire in that window on an unlucky seed. Assert first, then finish promptly.

## 3. Failure path

- A Python `assert` or raised exception inside a cocotb test fails the cocotb test, which fails
  the run. That is the ONLY Python-side mechanism that fails anything.
- A bare log line (`log.error(...)`, `print(...)`) fails NOTHING, in either language. On the SV
  side, fail through `uvm_error`/`uvm_fatal`.
- Prove each failure path once with a forced red run before trusting it (`dv_principles.md`
  §2, §6), and decide pass/fail from collected mechanisms, never from the simulator's process
  exit code (`SIM_RECIPE.md` §5).

## 4. ASCII-only logging (hard rule)

Every string that may be logged or raised on the Python side must be pure ASCII. cocotb's
failure-logging path uses an ASCII-only stream encoder: one non-ASCII character (an em-dash, a
unicode arrow) crashes the log call itself instead of reporting the real error — swallowing your
failure text and potentially turning a real failure into a silent false PASS.

## 5. Python-to-SV event handshakes (pattern)

If Python triggers named SV-side events through your own bridge, build in:

- a "listener armed" bit the Python side awaits before its first trigger — closes the startup
  race between the test and the SV side arming its listener;
- accounting counters on both sides (triggers sent vs. triggers observed), compared before
  finishing — a trigger that arrives while the listener is mid-response to a previous one is
  otherwise silently dropped; spacing heuristics alone are not a check, the counter comparison
  is;
- expected counts derived from your test's intent, never assumed from a counter's name (a
  counter that counts "events taken" may count them regardless of source, and may reset on DUT
  reset when your sent-count does not).

## 6. Testlist hygiene for cocotb-driven tests

- **Vacuous-pass guard.** If a test is meaningful only when the cocotb overlay is compiled in,
  the non-cocotb build of the same test name must `uvm_fatal` on seeing that test's cocotb
  plusargs — otherwise the same entry built without cocotb silently runs as a plain test under a
  name that claims cocotb-driven coverage it never exercised.
- **Choose iterations consciously.** If a test's timing (event spacing, hold times, settle
  waits) was tuned and verified against specific seeds only, pin those seeds rather than
  implying a full multi-seed sweep is safe — an untuned timing corner on another seed can
  false-FAIL a test whose stimulus logic is correct.

## 7. Checking obligation

Every generated test/TB deliverable carries its own checking strategy (self-checking stimulus,
generated SVA, and/or its own reference-model integration built from upstream open-source
imports) and declared functional-coverage expectations; it may not assume any hidden referee
catches what its own checks miss (seed prompt, Sections 7 and 8; `dv_principles.md` §6).
