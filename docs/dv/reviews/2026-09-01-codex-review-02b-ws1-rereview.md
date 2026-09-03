# Final verdict: REQUEST-CHANGES

| Finding | Verdict | Evidence |
|---|---|---|
| 1. `ci/env.sh` is not self-contained | **NOT-ADDRESSED** | Commit `56acf9c8` adds GCC 11 loading and failure reporting, but a sanitized non-login shell still returns `1` with `vcs`, `verdi`, and `dtc` missing. The validation tail checks only `vcs`, `RISCV_GCC`, and `python3`; it does not validate `verdi`, `dtc`, or the host GCC version ([ci/env.sh:70](/localdev/fzhang/ws/ibex/ci/env.sh:70)). Site module paths remain inherited rather than initialized by the script. |
| 2. `set -u` abort | **ADDRESSED** | Both variables now use nounset-safe expansion ([ci/env.sh:36](/localdev/fzhang/ws/ibex/ci/env.sh:36)). With site module metadata available, fresh sourcing and repeated sourcing under `set -euo pipefail` both completed successfully with the variables initially unset. |
| 3. Lock enforcement/clean venv | **NOT-ADDRESSED** | The script still reuses an existing `.venv`, upgrades pip in place, permits an unpinned fallback, and performs no exact-freeze verification ([ci/setup-venv.sh:7](/localdev/fzhang/ws/ibex/ci/setup-venv.sh:7)). A current `pip freeze` comparison has 111 packages versus 110 locked packages, with `siliconpilot==0.18.1` still exposed through the inherited `PYTHONPATH`. Thus the lock does not define the executed Python environment. |
| 4. Final-HEAD raw gate evidence | **ADDRESSED** | The manifest identifies functional commit `56acf9c8`, tool versions, exact commands, and the deleted VDB’s aggregate hash ([ws1-manifest.txt:4](/localdev/fzhang/ws/ibex/docs/dv/evidence/ws1-manifest.txt:4)). Raw smoke/small results and banners, coverage regression output, URG dashboard, and functional-coverage output are committed. Commit `3f381447` contains documentation/evidence only and directly follows `56acf9c8`. |

New breakage found:

- **Minor:** documentation now contradicts the modified setup script. [BUILD_AND_SIM.md:27](/localdev/fzhang/ws/ibex/docs/dv/BUILD_AND_SIM.md:27) says `setup-venv.sh` installs `python-requirements.txt`, while the script prefers `ci/requirements.lock`.

No new RTL/TB functional breakage was introduced by these two commits. Both shell scripts pass `bash -n`, and the tracked worktree remains clean. Findings 1 and 3 remain major blockers.
