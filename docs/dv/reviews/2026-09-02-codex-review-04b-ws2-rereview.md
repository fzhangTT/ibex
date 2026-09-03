VERDICT: REQUEST-CHANGES

The five original findings are substantively remediated, but the fix wave introduces blocking knowledge-fence violations.

| # | Disposition | Evidence |
|---|---|---|
| 1 | ADDRESSED | [`cocotb: 1`](/localdev/fzhang/ws/ibex/dv/uvm/core_ibex/riscv_dv_extension/testlist.yaml:584) is filtered for wildcard `COCOTB=0` selection by [ibex_cmd.py](/localdev/fzhang/ws/ibex/dv/uvm/core_ibex/scripts/ibex_cmd.py:193), wired through [metadata.py](/localdev/fzhang/ws/ibex/dv/uvm/core_ibex/scripts/metadata.py:279). Direct assertions over the real testlist found 58 entries, removed exactly `cocotb_irq_python_test` for stock selection, and retained it for exact or mixed explicit selection. |
| 2 | ADDRESSED-UNDER-RULING | MUT-002 records the mutation, named detector, `+disable_cosim=1`, attributed failure, passing ablation, and reverted-green run in the [transcript](/localdev/fzhang/ws/ibex/docs/dv/process-logs/ws2/mut-002-transcript.txt:18). Historical red→green evidence remains absent; the explicit exception is recorded in the [mutation record](/localdev/fzhang/ws/ibex/dv/auto_dv/mutations/README.md:50) under the controller’s [Round-2 ruling](/localdev/fzhang/ws/ibex/docs/dv/process-logs/ws2/progress.md:90). |
| 3 | ADDRESSED | Over-count now fails through [`count == triggers_sent`](/localdev/fzhang/ws/ibex/dv/cocotb/tests/test_irq_from_python.py:84), while [TB_CONTRACT.md](/localdev/fzhang/ws/ibex/docs/dv/TB_CONTRACT.md:90) accurately documents broad-source and reset semantics. The zero-trigger evidence records `count=0`; therefore equality passes and the independent `0 >= 3` floor fails. An unrelated interrupt causing equality to fail would be test contamination, not a false failure. |
| 4 | ADDRESSED | The contract now contains the manifest location, YAML schema, `COV=1` requirement, per-test/pre-merge behavior, anti-vacuity rule, and namespace rule at [TB_CONTRACT.md](/localdev/fzhang/ws/ibex/docs/dv/TB_CONTRACT.md:138). |
| 5 | ADDRESSED | Generic normal and coverage commands include cwd, simulator, test, module, seed, output, and coverage settings at [TB_CONTRACT.md](/localdev/fzhang/ws/ibex/docs/dv/TB_CONTRACT.md:20). |

Blocking new breakage:

- [CRITICAL][fence-integrity] [dv/auto_dv/mutations/README.md](/localdev/fzhang/ws/ibex/dv/auto_dv/mutations/README.md:27) now exposes fenced TB paths, an existing test/checker name, execution details, and an infra transcript path inside a generation-visible file. This directly contradicts that file’s own no-infra-reference rule at [line 23](/localdev/fzhang/ws/ibex/dv/auto_dv/mutations/README.md:23) and the fail-closed invariant in [CLAUDE.md](/localdev/fzhang/ws/ibex/CLAUDE.md:38). Keep detailed MUT-002 evidence solely in infra-owned collateral and reconcile the mutation-record location with the fence policy.

- [CRITICAL][fence-integrity] The allowlisted contract leaks a real human-authored coverage bin, `uarch_cg.cp_controller_fsm.out_of_decode0`, at [TB_CONTRACT.md:148](/localdev/fzhang/ws/ibex/docs/dv/TB_CONTRACT.md:148). That identifier comes from existing DV coverage and also conflicts with the generated-covergroup isolation rule later in the same contract. Replace it with a synthetic generated-namespace example.

Nonblocking cleanup:

- [BUILD_AND_SIM.md:84](/localdev/fzhang/ws/ibex/docs/dv/BUILD_AND_SIM.md:84) still says default `TEST=all` selects “every” test, which is no longer true after the intentional cocotb-only exclusion.
- [test_irq_from_python.py:82](/localdev/fzhang/ws/ibex/dv/cocotb/tests/test_irq_from_python.py:82) says the failure is “now” hard rather than a warning—history narration contrary to DV principles §5.

All four commits passed `git show --check`; their ancestry and the complete range passed `git diff --check`. Python syntax and read-only selector assertions passed. No simulation was rerun. No files were modified; the pre-existing untracked swap file remains.
