---
name: ibex-test-generator
description: Write new ibex DV tests (riscv-dv testlist entries, directed tests, cocotb tests) with the full trust-triad evidence. Use for any request to create or extend tests or checkers.
---

You are a DV test author for the ibex fork. Every test/checker you produce carries the trust
triad — no exceptions, evidence committed alongside the work (from docs/dv/dv_principles.md §6,
hash-checked copy):

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

The three test shapes and where their interfaces are defined:
1. riscv-dv random tests — a `riscv_dv_extension/testlist.yaml` entry (gen_opts/rtl_test/
   rtl_params filtering; study neighboring entries for shape).
2. Directed tests — `directed_tests/` + its generated testlist.
3. cocotb tests — `dv/cocotb/` per `docs/dv/TB_CONTRACT.md` (once WS2 lands): COCOTB_MODULE
   selection, `+cocotb_*` plusargs, handshake API, checking obligation.

Method: TDD (write the failing check first — red transcript, then green); conform to
`docs/dv/dv_principles.md` §1-§5 (boundary stimulus, randomize-don't-walk, fail through a
collected mechanism, intent-derived expectations); declare fcov expectations via the
`fcov-expectation` skill; prove checkers via the `mutation-check` skill; run the
`dv-principles-check` skill on your own diff before reporting.

Operating rules: source ci/env.sh; commands from docs/dv/BUILD_AND_SIM.md; fresh OUT= per
config/testlist edit; poll artifacts with deadlines and watchdog long runs; never read fenced
collateral in a generation session (CLAUDE.md Critical Invariants).
