# Ibex DV principles

Recurring verification best-practices for this repo — the centralized "how we verify" reference
for humans and agents. It binds hand-written and generated DV equally: tests, TB components,
checkers, coverage, and the tooling around them. Flow commands live in
[`BUILD_AND_SIM.md`](BUILD_AND_SIM.md); cosim architecture in [`COSIM.md`](COSIM.md); the
generated-test interface contract in `TB_CONTRACT.md` (once WS2 lands).

Boundary rules scope to **the chosen DUT** — the module a TB instantiates as its device under
test. In the core-level TB that is the ibex core (the examples below assume it); a sub-module TB
applies the same rules at that sub-module's port boundary — realistic drive (§1) and
interface-boundary checking (§2) are judged against its interface, not the core's.

## 1. Stimulus & drive

- **Realistic drive at the DUT boundary.** Drive ibex the way a real system does: instructions
  through generated programs (riscv-dv or directed assembly) fetched over the instruction bus,
  data through the memory interface agents, interrupts through the irq lines. A backdoor or
  force is acceptable only where the boundary itself is the thing being modeled (e.g. memory
  model contents) — never as a shortcut around a DUT input you could drive for real. A forced
  internal net can silently no-op under VCS visibility rules; if a backdoor is unavoidable,
  verify it took (write → clock → read back → error on mismatch).
- **If it's a config, program it.** CSR-controlled behavior is set through real CSR-writing
  instructions in the test program, not by poking DUT state. TB-parameter behavior is set
  through the config system (`IBEX_CONFIG`, `+define+IBEX_CFG_*`) — and the `TB-CONFIG:` banner
  exists so every log proves which configuration actually elaborated.
- **Randomize, don't walk.** A test explores its state space to catch corners, not to confirm
  one path. Randomly select stimulus per iteration with distribution weights; pin a directed
  iteration inside the random stream only to guarantee a specific corner. Never reduce a test
  to a single directed case "because the answer is known".
- **Future-proof every count.** Derive counts and ranges from their canonical parameter
  (`ibex_pkg` enums/parameters, config fields), never a re-typed literal — when the design
  parameter changes, the stimulus must follow with no edit.
- **Cover the transition, not just the steady state.** Interleave alternative modes (e.g.
  interrupt on/off phases, debug entries, PMP region reconfiguration) so the switch itself is
  exercised, not just each mode in isolation.
- **Own your preconditions.** A test programs the machine state its behavior depends on
  (privilege mode, MIE/MSTATUS, PMP setup) explicitly at entry and assumes nothing about
  incoming state; on observing unexpected state, error rather than adapt silently.
- **Sensitizing operands.** Distinct, non-degenerate data; interpretation-distinct values so a
  wrong interpretation is observable. No all-zeros or identity values that mask a fault.

## 2. Checking & correctness

- **Check at the interface boundary; internal signals only when unavoidable.** Prefer checks at
  module/bus boundaries and architectural state (the cosim comparison is the model: retired
  instructions, RF writes, PC). An internal-signal check is fragile to design change and does
  not show end-to-end behavior — when one is unavoidable, make its failure message identify
  itself ("checked signal moved/renamed", not a phantom bug) and pair it with an end-to-end
  check.
- **Deterministic ⇒ derive from intent.** A reference model computes expected values from the
  ISA/spec and the driven stimulus — never by copying an RTL decode net. A model mirrored from
  the RTL only proves the RTL matches itself. Reach for an internal anchor only when the
  quantity's starting state is genuinely unknowable from intent, and document it.
- **End-to-end round-trip.** Use data again through the consumer's output (store then load
  back; CSR write then read). Handing data off correctly does not prove it was applied.
- **Place the check where the failure lands — never before it.** A check that passes before
  full propagation is a false pass waiting to happen; gate on the commit/settle event.
- **Verify the result of every transaction — including the "harmless" ones.** A read issued
  only to observe state must still assert both that it landed and that the value matches; a
  dropped or perturbing read otherwise passes unnoticed.
- **Fail through a mechanism the flow actually collects.** In the SV-UVM flow, that is
  `uvm_error`/`uvm_fatal` (scanned by `scripts/check_logs.py` into `trr.yaml`/`regr.log`); in
  cocotb tests, a Python `assert`/raised exception fails the cocotb test which fails the run. A
  bare `$display`/log line fails nothing. Know your failure path and prove it once (see §6).
- **Predict-and-check.** Per-feature expectations computed from randomized stimulus + sampled
  config, compared against observation. Keep predictors pure and host-testable where possible.
- **Ground-truth at the waveform for new checkers.** Confirm a new monitor/checker against the
  actual wave at the cycles of interest at least once — it catches mis-reads (wrong hierarchical
  handle, packed-signal misinterpretation, silent-idle None handle) that a green test hides.

## 3. Scoreboard & infrastructure

- **Passive, always-on checking is the default.** The best check is one a test author cannot
  forget: derived automatically, applied on every transaction in every test (the cosim referee
  is the archetype). Active in-test checks exist for (a) "did the targeted scenario actually
  fire" — the reason the test exists — and (b) checks unique or too costly to run passively.
  Both layers are needed; a passive floor does not remove a test's duty to check its own
  driven data and effects.
- **Always-true invariants live in shared infrastructure; "did it fire" lives in the test.**
- **No-modify reuse of shared/vendored infra.** riscv-dv and lowrisc_ip are vendored: extend
  through the extension points (`riscv_dv_extension/`, TB hooks), don't patch vendored code
  ad-hoc. When a genuine vendor patch is required it goes through `vendor/patches/` with the
  vendoring flow, never a direct edit.

## 4. RTL truth & honesty

- **Ground in intent, log divergence.** Models and testplans derive from the ISA spec and
  documented intent. When RTL and intent disagree: if the RTL is more complete/correct, RTL
  wins and the disagreement is logged; if the RTL is less complete than the documented intent,
  that is a latent-bug candidate — write the test to the intended behavior, mark it as a known
  expected-fail, and drive the fix. DV does not modify RTL to make tests pass.
- **Don't hide failures.** Never fake-pass, silently down-scope, or paper over something that
  cannot be driven or checked; surface limitations explicitly (the FCIBH workaround in
  `BUILD_AND_SIM.md` is the pattern: documented, scoped, with the follow-up named).
- **Evidence over inference.** If a question is answerable from waves, RTL, docs, git history,
  or a quick experiment — check it. State unverified claims as unverified. A mechanism you
  explained but did not observe is a guess.
- **FCOV: build samplable, prune impossible.** A coverpoint may be built before stimulus can
  hit it (0% marks intent), but genuinely unhittable bins are pruned/`ignore_bins`'d so
  coverage isn't diluted. No duplicate coverpoints — extend, don't re-cover. Beware simulator
  semantics: `illegal_bins = default sequence` is not portable (see the FCIBH gotcha).

## 5. Tooling & hygiene

- **Toggleable debug, never unconditional prints.** Debug output gates behind a plusarg;
  plusarg names are declared once (test/TB constants), not scattered string literals — a
  mistyped gate silently no-ops.
- **Concise diagnostics.** A failure message states its triggering condition — id plus
  expected-vs-actual — nothing more. Root-cause narration belongs in docs, not runtime messages.
- **Self-sufficient docs and code.** Every doc, commit message, comment, and identifier is
  resolvable on its own: expand a tag/ID on first use or link the defining doc. Code never
  depends on a bare cross-file positional index or opaque tag; bind by named import or stable
  key that fails loud on reorder.
- **Concise code comments — intent only.** What and why, never history ("moved from X",
  "previously Y") — that lives in git.
- **Single source of truth.** A value meaning the same thing in two places is defined once and
  imported: `ibex_pkg` parameters, config fields, one constants home per language domain.
- **No hardcoded paths — filesystem or hierarchy.** Filesystem paths anchor to the repo root
  or `ci/env.sh`-exported variables. Hierarchical RTL references (SV bind paths, cocotb
  handles) resolve through one central place per domain (the fcov binds; the cocotb common
  package), so a rename fails loudly there instead of silently per call-site.
- **Site realities** (see `BUILD_AND_SIM.md` gotchas): the module command exits nonzero on
  success; background notifications are unreliable — poll artifacts with deadlines and watchdog
  long-running work; clear `PYTHONPATH` around pip operations.

## 6. Trust & evidence

Every claim about verification is backed by committed evidence — logs, reports, banners — not
prose. The `TB-CONFIG:` banner, the evidence files under `docs/dv/evidence/`, and the review
artifacts under `docs/dv/reviews/` are the standing examples.

<!-- TRUST-TRIAD-CANONICAL-BEGIN -->
**The trust triad** — required for every new test, checker, assertion, or covergroup, whether
human-written or generated:

1. **TDD** — the behavior is specified by a failing check before the implementation that makes
   it pass; the red→green transcript is part of the evidence.
2. **Mutation-proof** — a new checker or assertion counts only when a named mutation (recorded
   as id, file:line, original, mutated, expected detector) is caught by the NAMED checker with
   hidden referees inert, plus a checker-ablation negative control (checker disabled ⇒ the
   mutation survives). "Hidden referees inert" operationally: run with `+disable_cosim=1` (cosim
   mismatches become informational and cannot fail the test) and verify the failure signature in
   the log belongs to the named checker.
3. **fcov-expectation** — every new test declares the functional-coverage bins it intends to
   hit; declared-but-unhit bins FAIL the run. Verification is per-test and pre-merge (merged
   databases let one test claim another's bins), generated covergroups live in an isolated
   namespace, and every sampling condition gets an anti-vacuity review (a bin hit by an
   always-true sample proves nothing).
<!-- TRUST-TRIAD-CANONICAL-END -->

- **Self-proving checks.** The triad's rules 2 and 3 generalize: a check never exercised to
  fail is not trusted; a stimulus never proven to arrive is not trusted.
- **Reviewer independence.** The executing model never self-approves — the cross-model review
  policy in `CLAUDE.md` governs; artifacts live under `docs/dv/reviews/`.
- **No hidden-referee reliance.** Generated DV must carry its own checking and may not lean on
  referees it cannot see (the cosim demotion rules and the checking obligation live in the
  spec's fence workstream and `TB_CONTRACT.md` once WS2 lands).
