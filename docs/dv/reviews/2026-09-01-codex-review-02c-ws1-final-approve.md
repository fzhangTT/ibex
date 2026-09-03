| Open item | Verdict | Basis |
|---|---|---|
| F1 — environment bootstrap/tool checks | **ADDRESSED-UNDER-RULING** | [ci/env.sh](/localdev/fzhang/ws/ibex/ci/env.sh:6) documents the supported-shell contract and adds WARN-only `verdi`/`dtc` checks. Supported login-shell sourcing and re-sourcing passed; sanitized-shell failure remains intentionally out of WS1 scope. |
| F3 — venv lock enforcement | **ADDRESSED-UNDER-RULING** | [ci/setup-venv.sh](/localdev/fzhang/ws/ibex/ci/setup-venv.sh:4) clears `PYTHONPATH` before all pip operations and performs an exact freeze-versus-lock check. The siliconpilot leak reproduced with ambient `PYTHONPATH` and disappeared when cleared; clean freeze matched the lock exactly, 110/110. |

The [BUILD_AND_SIM.md](/localdev/fzhang/ws/ibex/docs/dv/BUILD_AND_SIM.md:27) contradiction is fixed.

Fresh verification passed: shell syntax, repeated `set -euo pipefail` sourcing, exact lock comparison, `git diff --check`, and clean worktree.

**Final verdict: APPROVE**
