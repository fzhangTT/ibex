---
name: lint-check
description: Run the repo's RTL lint (verilator via fusesoc) and report findings against the known baseline. Use before committing RTL/TB SV changes.
---

# lint-check

Entry point (fixed in this fork — the old `ibex_core_tracing` core name is gone):
`bash -lc 'source ci/env.sh && make lint-core-tracing'` (wraps
`fusesoc --cores-root . run --target=lint lowrisc:ibex:ibex_top_tracing` + small-config opts).

Current baseline (verified 2026-09-01): the target exits nonzero with exactly 3 pre-existing
`%Warning-UNOPTFLAT` circular-comb warnings (`ibex_id_stage.sv` `instr_executing_spec`/
`instr_done`, `ibex_controller.sv`) — a known upstream waiver case; `lint/verilator_waiver.vlt`
exists but is not wired into the lint target (follow-up, not yet done). Judge a lint run against
this baseline: NEW warnings/errors beyond the 3 are findings on your change; the 3 themselves are
not yours. Update this baseline note when the waiver wiring lands. `fusesoc` writes a `build/`
dir at repo root — remove it after linting; never commit it. Python lint: `make python-lint`.
