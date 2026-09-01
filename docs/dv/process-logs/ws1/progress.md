# SDD ledger — plan: docs/superpowers/plans/2026-09-01-ws1-vcs-bringup.md

Spec: docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md (read; binding authority)
Branch: fzhang/auto-dv-setup (dedicated setup branch; not master)

Ruling: execute in the existing checkout on branch fzhang/auto-dv-setup, no separate worktree — the user created this branch for exactly this work and WS1 builds tools outside the repo at absolute paths; cost if wrong: dirty-tree interference with the user's own edits.

## Pre-flight conflict scan

| Pair / task | Produces vs consumes | Finding |
|---|---|---|
| T1 env.sh ↔ T2 venv | env.sh sources `.venv/bin/activate` if present; T2 creates it | consistent (guarded) |
| T1 env.sh ↔ T3 spike | env.sh exports `SPIKE_INSTALL=$IBEX_TOOLS_DIR/spike-ibex-cosim`; T3 defaults to same | consistent |
| T1 env.sh ↔ T4 toolchain | env.sh prefers `$IBEX_TOOLS_DIR/lowrisc-toolchain-gcc-rv32imcb`, falls back to site riscv64; T4 installs to that exact path | consistent |
| T4 ↔ T6 | T4 must validate the exact opentitan march (bitmanip); T6 smoke uses opentitan | consistent after codex-review amendment |
| T5 ↔ T6/T8 | banner strings: opentitan `BaseIsaRV32IorCHERIoT`/`RV32ZcaZcbZcmp`; small `BaseIsaRV32I`/`RV32Zca` | consistent |
| T6 ↔ T7 | separate OUT trees (out vs out_cov) avoid metadata.pickle conflicts | consistent |
| T6/T7/T8 evidence | docs/dv/evidence created by T6 (mkdir -p) before T7/T8 write | consistent |
| T5 self | plan constraint "stock flow unchanged except define fix" vs added TB-CONFIG banner | Ruling: banner is additive log output mandated by the spec as permanent evidence — allowed; cost if wrong: one extra log line in every sim |
| T4 self | `python3 -c "import scripts.ibex_cmd"` probe may fail outside the flow's PYTHONPATH bootstrap | Ruling: implementer may adapt probe mechanics (any method that captures the exact ISA strings emitted for opentitan); cost if wrong: none — probe is diagnostic |

Scan otherwise clean. Rubric conflicts: none (no assert-nothing tests or duplication mandated).

## Task status
BASE for T1+T2: a273ede0
Task 1+2: dispatched as one batch (same-shape script tasks), implementer=sonnet
Task 1+2: implementer DONE_WITH_CONCERNS (02404601, 3c0e5d80). Concerns: licenses module prereq (picked synopsys/licenses/2.3, documented inline), -full64 needed at invocation (not in env.sh), metadata.py needs setup_imports PYTHONPATH — carry into T4/T6 dispatches.
Task 1+2: task review dispatched (sonnet), package review-a273ede0..3c0e5d80.diff
Task 1+2: review spec ❌ — 1 Important (plan-mandated): setup-venv.sh:5 hardcodes python path outside env.sh. Ruling: constraint wins over the plan's verbatim script — env.sh exports IBEX_PYTHON default; setup-venv.sh consumes it with no private default; cost if wrong: an extra env indirection.
Task 1+2: minor (deferred): module-hide site noise on env.sh sourcing undocumented; synopsys/licenses/2.3 hardcoded without override (inconsistent with other overrides); requirements.lock round-trip sanity check on a fresh venv not yet run (odd names httpcore2/httpx2 flagged).
Task 1+2: fix round 1/5 (fix f5a726be, IBEX_PYTHON centralized; scoped re-review dispatched, haiku)
Task 1+2: fix round 1/5 (1 addressed, 0 open; commit f5a726be)
Task 1: complete (commits a273ede0..f5a726be, review clean after 1 fix round)
Task 2: complete (same range, batched with Task 1)
BASE for T3: f5a726be
Task 3: dispatched (implementer=sonnet)
Task 3: implementer DONE (70b50e53); build 51s, no source patches. Concerns: dtc/1.7.2 module load not automated; site module cmd exits 1 despite success (never chain with &&) — carry both to T8 gotchas; watchdog rule now in force (user-mandated, saved to memory).
Task 3: task review dispatched (sonnet)
Task 3: review — 2 Important (both plan-mandated). (1) dtc module load un-automated: Ruling — fold `module load dtc/1.7.2 2>/dev/null || true` into ci/env.sh (central authority precedent; || true because site module cmd exits 1 on success); cost if wrong: an unneeded module in non-build shells. (2) -static-libstdc++ doesn't remove DT_NEEDED (shared Boost 1.66 re-introduces it): Ruling — do NOT chase static Boost/old-GCC now; DTS gcc-11 on RHEL8 keeps the symbol floor at the system libstdc++, so practical risk is low; fix the untruthful comment and make Task 6 the definitive check (simv links+loads DPI or we fall back to flake's low-floor approach); cost if wrong: Task 6 fails at sim load and we rebuild spike differently then.
Task 3: minor (deferred): unconditional refetch on re-run; partial-clone edge case.
Task 3: fix round 1/5 (fix 16886efb — dtc in env.sh + truthful LDFLAGS comment; scoped re-review dispatched, haiku)
Task 3: fix round 1/5 (2 addressed, 0 open; commit 16886efb)
Task 3: complete (commits f5a726be..16886efb, review clean after 1 fix round)
BASE for T4: 16886efb
Task 4: dispatched (implementer=sonnet)
Task 4: implementer DONE (78f07202). lowRISC toolchain path won; exact opentitan march validated (rv32imcb / ISS rv32imc_Zba_Zbb_Zbc_Zbs_XZbf_XZbp_XZbr_XZbt). Brief snippet signature drift noted (get_isas_for_config needs Config obj) — covered by preflight probe-mechanics ruling.
Task 4: task review dispatched (sonnet)
Task 4: review Approved but 2 Important. (1) plan-mandated: partial-download cache not crash-safe. Ruling: amend script beyond brief verbatim — curl to $NAME.tar.xz.part then mv (atomic cache); cost if wrong: none material. (2) evidence gap: march compile not provably run with lowRISC gcc. Ruling: re-run validation as one transcript echoing resolved $RISCV_GCC; no code change needed.
Task 4: minor (deferred): no tarball checksum; kept-tarball tradeoff uncommented; rm -rf/mv failure window.
Task 4: fix round 1/5 (fix 462c2e11 — atomic download + continuous gcc transcript; scoped re-review dispatched, haiku)
Task 4: fix round 1/5 (2 addressed, 0 open; commit 462c2e11)
Task 4: complete (commits 16886efb..462c2e11, review clean after 1 fix round)
BASE for T5: 462c2e11
Task 5: dispatched (implementer=sonnet). Note: T5's rtl_tb_compile is first exercise of spike pkg-config/DPI link — early test of the T3 libstdc++ ruling.
Task 5: red-state compile done (spike cosim DPI link SUCCEEDED — T3 libstdc++ concern retired at link level; simv runtime load still pending in T6). Implementer stalled on lost notification again; nudged with poll-the-log instruction. 45-min report watchdog still armed.
Task 5: implementer DONE (54e01775). Audit: only the 3 known gaps; RV32ZC param+forward added; banner in; red/green proven at compile level; runtime banner check deferred to T6/T8 by design. Pre-existing PCWM-W (trvk_revbm_rdata_intg_i) and SIOB warnings noted — untouched.
Task 5: task review dispatched (sonnet)
Task 5: complete (commits 462c2e11..54e01775, review clean, zero findings). Runtime banner check rides on T6/T8 by design.
BASE for T6: 54e01775
Task 6: dispatched (implementer=sonnet; 60-min watchdog; poll-logs-directly instruction)
Task 6: implementer DONE (2e184fd7). E2E PASS first try, <60s total, banner exact, no fixes needed. Task review dispatched (sonnet).
Task 6: review Approved; 1 Important (wall-time claim "under 60s" is ~72.2s by out/ artifact timestamps). Ruling: finding accepted; deliverable (evidence+commit) unaffected; authoritative figure = ~72s launch→regr.log, recorded here and passed to Task 8's dispatch as the number for BUILD_AND_SIM.md; no fix round — the claim lives only in the uncommitted scratch report. Cost if wrong: a doc timing off by seconds.
Task 6: minor (deferred): grep-order nit in report transcript; compile.riscvdv.log is 0 bytes on clean compile (benign, note for sim-debug skill).
Task 6: complete (commits 54e01775..2e184fd7, review approved)
BASE for T7: 2e184fd7
Task 7: dispatched (implementer=sonnet, 30-min watchdog)
Task 7: implementer DONE_WITH_CONCERNS (2afc18be). COV=1 machinery works (merged.vdb, urg, fcov) but sim dies at ~2us: Error-[FCIBH] on fcov illegal_bins `default sequence` (core_ibex_fcov_if.sv:606-613 + sleep variant) — VCS X-2025.06 half-implements the construct and false-fatals legal FSM self-loops. Upstream TODO says the checker was expected EMPTY under VCS (never functional there).
Task 7: Ruling — guard the two `illegal_bins ... = default sequence` lines with `ifndef FCOV_NO_DEFAULT_SEQUENCE` and add +define+FCOV_NO_DEFAULT_SEQUENCE to the vcs compile opts only (yaml/rtl_simulation.yaml). Preserves upstream's intended VCS behavior (no illegal-transition checking there), xlm unchanged, targeted macro name avoids collision with any generic VCS define. Follow-up flagged for later: explicit enumeration if FSM illegal-transition checking is wanted under VCS. Cost if wrong: we lose a checker VCS never had.
Task 7: fix round 1/5 (fix dbba358f — FCOV_NO_DEFAULT_SEQUENCE guard + vcs-only define + passing COV=1 rerun in out_cov2, honest evidence; scoped re-review dispatched, sonnet)
Task 7: fix round 1/5 (1 addressed, 0 open; commit dbba358f). urg overall 52.13 (LINE 70.46 TOGGLE 39.37 FSM 20.93 BRANCH 62.52 ASSERT 85.63 GROUP 33.86).
Task 7: complete (commits 2e184fd7..dbba358f, review clean after 1 fix round)
BASE for T8: dbba358f
Task 8: dispatched (implementer=sonnet)
Task 8: implementer DONE (d71e486c). small banner proved (BaseIsaRV32I/RV32Zca, PASSED); doc re-verified fresh-shell (~156s run noted as variance). Task review dispatched (sonnet).
Task 8: minor (deferred): out_cov2 numeral unexplained inline; "silently excluded" wording (filter logs a warning); gotcha count said ten, list is nine (bundled item).
Task 8: complete (commits dbba358f..d71e486c, review approved, zero Important)
BASE for T9: d71e486c
Task 9: dispatched (implementer=sonnet)
Task 9: implementer done (08255d8b). Task review dispatched (sonnet).
Task 9: review Needs fixes — 1 Critical (spike commit survey omits ef10d395/15fbd568/0e306ce7; 0e306ce7 is a cosim-hook commit that belongs in the load-bearing table; "remaining are all Zc*" claim false), 1 Important (paraphrased subjects presented under a "Subject" header for c9a893a3/a5692fb0).
Task 9: minor (deferred): check_logs.py range cited 27-79, actual 27-81.
Task 9: fix round 1 dispatched (resume implementer).
Task 9: fix round 1/5 (fix 68667d51 — commit survey completed/corrected; scoped re-review dispatched, haiku)
Task 9: fix round 1/5 (2 addressed, 0 open; commit 68667d51)
Task 9: complete (commits d71e486c..68667d51, review clean after 1 fix round)
ALL TASKS COMPLETE. Final whole-branch review: dispatching (fable), MERGE_BASE=34b07057.
Final review (fable): With fixes. 3 Important: (1) env.sh dies under set -e (licenses/vcs module loads unguarded); (2) toolchain fallback exports RISCV_TOOLCHAIN and sticks across re-source; (3) requirements.lock contaminated (siliconpilot + orphan deps; dependency-confusion vector; escalates deferred T2 minor). Ruling: fix wave = Importants 1-3 + minors 4/5/6 (gitignore out*/, IBEX_TOOLS_DIR doc line, stray backtick) — one-liners that hit the first newcomer; all other minors stay deferred per reviewer triage. Cost if wrong: slightly larger fix diff.
FIX_BASE for final wave: 68667d51. Fix wave dispatched (sonnet).
Final fix wave: commit 915ff926 (all 6 findings claimed fixed); scoped re-review dispatched (haiku) with adjudication of the lock-contamination-scope claim.
CORRECTION: fix wave = 3 commits (915ff926, a689bbfb, 607f98e0); re-review redirected to full package review-68667d51..607f98e0.diff. Fixer's finding-3 claim sharpened: suspected orphans are pyucis transitive deps (MCP-server feature); only siliconpilot removed.
Final fix wave: re-review clean (6/6 addressed, no new breakage; lock "orphans" adjudicated as genuine pyucis transitive deps via pyvsc chain).
WS1 COMPLETE pending post-execution codex review (cross-model policy).
Codex post-execution review (gpt-5.6-sol, codex-cli 0.149.1, range 34b07057..25fba310): REQUEST-CHANGES, 4 major. Ruling: all accepted with scoping — (1) env.sh gains nounset-safety, gcc-toolset-11 enable, and a fail-loud required-tools tail (keeps per-load guards from Claude final review; the two reviews are complementary: tolerate load noise, verify outcomes); (2) venv recreated FROM the lock and setup-venv.sh enforces the lock when present; (3) gates rerun at final HEAD with raw artifacts committed. Cost if wrong: ~10 min of reruns.
