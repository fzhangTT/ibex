# Fence-Integrity Check

**Severity:** Critical
**Context:** both
**Filters:** dv/auto_dv/**, docs/dv/TB_CONTRACT.md, docs/dv/FENCE.md

**Fence note (binding):** this rubric evaluates generated-DV artifacts in Zone B / evaluator
context; findings go to humans, never back into a generation session (spec WS7).

You are reviewing a generated-DV artifact (or its landing diff) for knowledge-fence violations:
- References to fenced collateral: paths, test names, covergroup/bin names, or distinctive
  identifiers from existing DV (`dv/uvm/core_ibex/tests|riscv_dv_extension|directed_tests|fcov`,
  `dv/cosim`, verification docs) appearing in generated files, comments, or commit messages.
- Paraphrase leakage: prose that summarizes fenced content (an existing testplan's structure, the
  human coverage model's dimensions, cosim internals) beyond what `TB_CONTRACT.md`/`FENCE.md`
  state.
- Landing-shape violations: changes outside `dv/auto_dv/**` in a cleanroom-originated diff;
  symlinks/renames/deletes outside the namespace; ancestry not from an approved cleanroom snapshot
  (flag for the landing validator when not verifiable here).

**Do NOT flag:** references to allowed collateral (`TB_CONTRACT.md`, `FENCE.md`, `rtl/`, upstream
riscv-dv/spike, `ibex_pkg`), or similarity of *behavior* alone — overlap-of-substance belongs to
the test-overlap rubric in evaluator context, not here.
Respond `{"status": "PASS"}` or the FAIL JSON per `GUIDE.md`.
