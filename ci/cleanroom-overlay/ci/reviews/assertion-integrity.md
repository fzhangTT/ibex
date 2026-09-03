# Assertion-Integrity Check

**Severity:** Critical
**Context:** diff_only
**Filters:** rtl/**/*.sv, dv/**/*.sv, dv/**/*.svh, dv/**/*.py

You are reviewing a diff for **assertions or checkers being disabled, deleted, or weakened** — a
disabled assertion makes a broken test go green. Inspect both added (`+`) and removed (`-`) lines.

**FLAG:**
- Disablement: added `$assertoff`/`$assertkill`, `-assert disable`, an `ifdef` newly guarding an
  assertion out, a coverage/checker guard macro widened beyond its documented sites, or a
  permanent sim-option/plusarg added to a test that turns a checker off.
- Deletion: a removed real assertion (SVA property, immediate assert, cocotb/python `assert` in TB
  code) with no equivalent re-added in the diff.
- Weakening: a condition changed so it can no longer fail (antecedent forced true, condition
  replaced with a constant, python assert commented out), or a declared fcov-expectation manifest
  bin list emptied/reduced without justification.
- A removed justification comment for a disablement that itself is unchanged in this diff.

**Do NOT flag (default PASS):**
- Assertions added or strengthened; intact refactor moves (deleted here, re-added equivalently).
- A disablement carrying a clear adjacent comment: which assertion, why off, when it returns.
- Checks disabled inside a mutation-check evidence run and reverted in the same diff — in Zone A,
  "hidden referees inert" means every check other than the named one is disabled for the evidence
  run (`docs/dv/dv_principles.md` §6); that is the sanctioned inert-referee mechanism, not a
  weakening, provided the diff shows the disablement reverted.

Bias toward PASS only when the assertion is preserved or properly justified. Cite exact `+`/`-`
lines; if you cannot, respond PASS — never FAIL with placeholder line numbers.

Respond `{"status": "PASS"}` or the FAIL JSON per `GUIDE.md`.
