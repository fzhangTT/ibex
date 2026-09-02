# New-Test Overlap Check

**Severity:** Error
**Context:** both
**Filters:** dv/uvm/core_ibex/riscv_dv_extension/testlist.yaml, dv/uvm/core_ibex/directed_tests/**, dv/cocotb/tests/**/*.py, dv/auto_dv/**

**Fence note (binding):** against generated DV this rubric runs in Zone B / evaluator context ONLY —
its findings go to humans, never back to a generation session (spec WS7).

You are reviewing one changed/added test (a testlist entry, a directed test, or a cocotb test
file). Goal: stop test bloat — catch a new or substantially-rewritten test that duplicates an
existing one. Only report findings about the artifact under review; siblings you read for
comparison are never flagged. Cosmetic/comment-only changes are PASS.

Procedure: summarize the scenario under review (stimulus shape, config axes, what it asserts);
compare against plausibly-similar siblings you can name (same testlist section, same tests dir).
**FAIL only when** you can name a concrete near-duplicate by path/entry — same stimulus/assertion
shape differing only trivially (seed, count, constant); say what to do (merge / parameterize /
drop). A different seed alone does not make tests distinct — but never FAIL on suspicion: name the
duplicate or PASS. Respond `{"status": "PASS"}` or the FAIL JSON per `GUIDE.md`.
