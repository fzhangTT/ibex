VERDICT: REQUEST-CHANGES

- Critical 1 — **ADDRESSED.** MUT-002 is now a bare abstract record in [README.md](/localdev/fzhang/ws/ibex/dv/auto_dv/mutations/README.md:27). The cited fenced identifiers and infra path return zero matches.
- Critical 2 — **ADDRESSED.** `uarch_cg` returns zero matches in [TB_CONTRACT.md](/localdev/fzhang/ws/ibex/docs/dv/TB_CONTRACT.md:148); the replacement uses the synthetic `gen_myfeature_cg` namespace.

New blocking breakage:

- **[CRITICAL][fence-integrity]** Commit `31979136`’s message itself repeats `core_ibex_tb_top.sv`, `test_irq_from_python.py`, the infra transcript path, and `uarch_cg.cp_controller_fsm.out_of_decode0`. The binding fence rubric explicitly covers commit messages. Reword the commit message using abstract descriptions without fenced identifiers, then re-review.

The two nonblocking cleanups are correct. `git show --check` and `git diff --check` pass. There is no disagreement with a recorded WS2 ruling. No files were modified.
