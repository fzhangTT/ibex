# SDD ledger — plan: docs/superpowers/plans/2026-09-01-ws2-cocotb.md

Spec: docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md WS2 (binding; amended: watchdog = $fatal by ruling)
Branch: fzhang/auto-dv-setup (this checkout). WS3 executes in parallel in worktree ../ibex-ws3 (branch fzhang/ws3-skills, fork-controller) — paths disjoint by design.

## Pre-flight conflict scan

| Pair / task | Produces vs consumes | Finding |
|---|---|---|
| T1 cocotb in venv ↔ T4 `-load` resolution | T4 shells `cocotb-config` at command-construction | consistent (T1 first) |
| T2 interface (5 bits incl uvm_ready + flag bit) ↔ T3 handshake ↔ T7 uvm_ready/counter | one interface contract, stated in T2 Produces | consistent |
| T4 COCOTB_MODULE knob ↔ T5 watchdog negative + T7 module select | T5/T7 use the knob, no ad-hoc env | consistent |
| T4 ibex_sim.mk dep vars ↔ T5/T6/T7 fresh-OUT usage | transition test in T4; fresh OUT elsewhere | consistent |
| T7 testlist edit ↔ metadata staleness | fresh OUT mandated in T7 Step 3/4 | consistent |
| T2 Step 4 manual define vs T4 knob | guarded fallback ("defer to Task 4 Step 4") stated | consistent |
| Cross-plan WS3 (parallel worktree) | WS2 touches dv/cocotb, dv/uvm/core_ibex/{tb,common,tests,scripts,yaml,Makefile,riscv_dv_extension}, ci/{env.sh,setup-venv.sh,requirements*}, docs/dv/{TB_CONTRACT,BUILD_AND_SIM,evidence/ws2-*}; WS3 touches .claude/, .codex/, .agents/, AGENTS.md, CLAUDE.md, ci/reviews/, ci/check_fcov_expectations.py, docs/dv/{dv_principles,evidence/ws3-*} | disjoint; merge risk low. Ruling: if WS3 needs a WS2 file it must message, not edit |
| T1 regenerates ci/requirements.lock ↔ WS3 venv use | WS3 sims use the same .venv (worktree shares it? No — .venv lives in main checkout; worktree has no .venv → WS3's env.sh venv-activate silently skips!) | FINDING: WS3 worktree lacks .venv; ci/env.sh guards on existence so python falls back to system 3.9. Ruling: acceptable risk — WS3's live sim (Task 5) requires the venv; instructed controller to run ci/setup-venv.sh in its worktree if needed (its fork context knows the script is idempotent). Cost if wrong: WS3 Task 5 stalls and messages me. |

Rubric conflicts: none.

## Task status
BASE for T1: bfd74d7c
Task 1: dispatched (implementer=sonnet)
Task 1: implementer DONE (3b033ae7). cocotb 1.9.2 + find_libpython in lock; LIBPYTHON_LOC guarded. Concern carried to T4: site cocotb-config 1.7.1 behind venv on PATH — T4 must assert the resolved vpi .so comes from the venv 1.9.2.
Task 1: task review dispatched (sonnet)
Task 1: review Approved (1 Important deferred-by-reviewer: bogus LIBPYTHON_LOC window pre-venv w/ stray 1.7.1 shadow. Ruling: neutralized in T4 — resolve cocotb-config via $IBEX_CI_ROOT/.venv/bin absolute path, assert 1.9.2; cost if wrong: T4 review catches it). Minor deferred: empty-string LIBPYTHON_LOC export on no-output failure.
Task 1: complete (commits bfd74d7c..3b033ae7, review approved)
BASE for T2: 3b033ae7
Task 2: dispatched (implementer=sonnet)
Task 2: implementer DONE (234432c0; commit landed ~20s after report — timing race noted). New pkg core_ibex_cocotb_pkg + incdir; ifdef-guarded import in test_pkg; concerns: monitor handshake is single-cycle monotonic (loop needed if future tests toggle active repeatedly) — acceptable for A/B, noted for TB_CONTRACT. Task review dispatched (sonnet).
Task 2: review Needs fixes — 1 Critical: core_ibex_cocotb_pkg.sv package shell unguarded (empty pkg present in stock builds). Minors deferred: uvm_ready forward scaffolding (intentional); single-pass handshake (disclosed, revisit at T7).
Task 2: fix round 1 dispatched (resume implementer).
Task 2: fix round 1/5 (fix 30d5842f — package shell guarded; module count 104→103 stock proof; scoped re-review dispatched, haiku)
Task 2: fix round 1/5 (1 addressed, 0 open; commit 30d5842f)
Task 2: complete (commits 3b033ae7..30d5842f, review clean after 1 fix round)
BASE for T3: 30d5842f
Task 3: dispatched (implementer=haiku — mechanical, contract fully specified)
Task 3: implementer DONE (d5ab596a). Task review dispatched (haiku — small python diff).
Task 3: review Needs fixes — 2 Critical (async-generator yield bug: protocol never executes; BinaryValue bit-string log) + 1 Important (dut.hart_id_i likely needs dut.dut.hart_id_i under TOPLEVEL=core_ibex_tb_top — the SV instance is literally named 'dut'). Minors deferred: unrequested 1ns settle Timer; truthiness vs ==1. Haiku implementer produced plausible-but-dead code — model-selection lesson: python-cocotb protocol code gets sonnet-floor implementers next time.
Task 3: fix round 1 dispatched (resume implementer).
Task 3: fix round 1/5 (fix b70cca43; scoped re-review dispatched, haiku)
Task 3: fix round 1/5 (3 addressed, 0 open; commit b70cca43)
Task 3: complete (commits 30d5842f..b70cca43, review clean after 1 fix round)
BASE for T4: b70cca43
Task 4: dispatched (implementer=sonnet)
Task 4: implementer DONE after stall+ultimatum (fa9de86e). Real finding: metadata create-once defeats knob flips in persisted OUT (affects WAVES/COV too) — carry to T8 doc. Run-stage env prereq not exercised end-to-end (T5's job, disclosed). Task review dispatched (sonnet).
Task 4: review Approved, zero C/I. Minors deferred: pickle-schema forward-compat gap (pre-existing, fold into T8 caveat), redundant per-test dump-vars writes, COCOTB in run-deps redundant-but-harmless.
Task 4: complete (commits b70cca43..fa9de86e, review approved)
BASE for T5: fa9de86e
Task 5: dispatched (implementer=sonnet — Milestone A live run + triage loop)
Task 5: implementer DONE (8acfe309 handshake race fix, aa667d39 log-scanner fix, 809b45bc evidence; SEED=2). Ruling 1: SEED=1 post-report assertion window (NoMemResponseWithoutPendingAccess after UVM summary, exposed by finish_on_completion=0) = structural coexistence consequence — document in TB_CONTRACT (T8) + surface at final review; seed change acceptable for Milestone A; cost if wrong: latent flake class undertreated. Ruling 2: WS2 gate wording amended — import failure fails fast via cocotb's own 0ns self-report (demonstrated); SV watchdog covers VPI/libpython-never-loaded class, verified by review not live-fire (not reachable via COCOTB_MODULE); cost if wrong: watchdog has a bug we never see until that failure class occurs.
Task 5: task review dispatched (sonnet).
Task 5 extra finding (pre-existing): flow never checks vcs_simv exit code — pass/fail is log-scan only (check_logs). Carry to: WS4 jenkins scripts (propagate exit codes), T8 gotchas, and the trust-evidence story (a $fatal nonzero exit is invisible to the flow except via log absence).
Task 5: review Needs fixes — 2 Critical (PY_EXCEPTION_RE \b can't match compound exceptions; regression vs Error-[FCIBH] format already-seen in-repo), 1 Important (watchdog run's flow-level FAIL argued not quoted). Ruling: reviewer's Minor #5 (pinned classifier unit test) is REQUIRED in the fix — the classifier is a checker; triad mandates prove-it-fires; manual checking demonstrably failed. Minor deferred: ReadWrite() vs Timer flush style.
Task 5: fix round 1 dispatched (resume implementer).
Task 5: fix round 1/5 (fix 3d393446 — scanner restored + pinned classifier test + FAIL quote; scoped re-review dispatched, sonnet)
Task 5: fix round 1/5 (3 addressed, 0 open; commit 3d393446 — re-reviewer independently reproduced RED/GREEN)
Task 5: complete (commits fa9de86e..3d393446, review clean after 1 fix round). Milestone A green.
BASE for T6: 3d393446
Task 6: dispatched (implementer=haiku — mechanical identity evidence)
Task 6: implementer DONE (5c2500b7). Task review dispatched (haiku).
Task 6: review Needs fixes. Ruling on Critical 1 (plan-vs-finding conflict): the plan's literal "zero hits for cocotb|COCOTB|vpi" is unachievable by accepted design (cocotb .sv filenames are unconditionally parsed; contents ifdef away — T2's module-count proof). Identity is BEHAVIORAL: evidence must show zero hits for `COCOTB_SIM|\+vpi|cocotb_pli|libcocotbvpi|MODULE=` on compile+run surfaces, with the two filename parse-lines annotated as expected. Criticals 2/Important 3 accepted as-is: raw grep transcripts required, not summaries. Cost if wrong: identity evidence overstates cleanliness.
Task 6: fix round 1 dispatched.
Task 6: fix round 1/5 (fix d8223f35 — raw behavioral transcripts; scoped re-review dispatched, haiku)
Task 6: fix round 1/5 (all addressed; commit d8223f35)
Task 6: complete (commits 3d393446..d8223f35, review clean after 1 fix round)
BASE for T7: d8223f35
Task 7: dispatched (implementer=sonnet, 60-min watchdog — Milestone B)
CROSS-TRACK: WS3 fork controller complete (fzhang/ws3-skills, bfd74d7c..25d19075, 10 commits, unmerged). Fork disclosed missing per-task Claude review seats → compensating whole-branch review dispatched (fable) before merge. Its codex loop closed at cap REQUEST-CHANGES-ADJUDICATED with 3 parked items for the user. 4 dv-principles-check findings vs BUILD_AND_SIM.md → fold into WS2 T8 dispatch: hardcoded tools path :13, config-table retyping, "silently excluded" wording, FCIBH follow-up untracked. WS7 carries: dv_principles+trust skills fence-allowlisted; manifest-location + skill-split decisions.
WS3 whole-branch review (fable): With fixes — 1 Critical (dangling evidence pointers incl. a spec exit-gate on prose), 4 Important (simple-english beowulf trigger description; plan-mode \n bug; no codex timeout; shared-VDB concurrency to record). Rulings: fix 1-4 + debris cleanup; 5 recorded to the parked WS7 item; reviewer minors 6-10 deferred to WS3 ledger. Fix wave sent to ws3-controller; scoped re-review then merge.
WS3 fix-wave re-review: 1/3/5/6 addressed; 2 (simple-english YAML now INVALID — regression, validator's regex check blind) and 4 (timeout dead code under set -e) NOT addressed. Round 2 sent: fix both + ruled addition (validator YAML-parse upgrade w/ mutation proof) + correct uncorroborated bwrap narrative in ledger. Caveat on finding 1 (embellished retry story) folded into item 4.
WS3 round 2 re-review: all items addressed. Residual parked with Ruling: validator's no-pyyaml regex fallback is weaker than pre-round (drops name==dir + description checks) — deferred to WS7's validator work (same file); cost if wrong: weaker validation only on pyyaml-less interpreters. WS3 loop CLOSED. Merging fzhang/ws3-skills.
Task 7: implementer DONE (c7a5089d, on top of WS3 merge). Counter = IRQ_TAKEN state entry (structural); ablation proper (fixed expectation, zeroed stimulus); 2 in-task bugs found/fixed (finish timeout scaling; em-dash breaking the negative control). Concerns to T8: timeout_ms callout; assert-before-finish contract rule; single-seed tuning disclosed. Task review dispatched (sonnet).
Task 7: review Needs fixes (fable) — 3 Important: vacuous-pass in stock regressions (10 iters, COCOTB=0); no-lost-triggers overstated (mid-pulse window, un-queued uvm_event); 1:1 unenforced (>= passes double-counts). Rulings: fix all 3 (fatal-guard + iterations=1; listener trigger-counter + equality check instead of prose contract; count bounded max(n,3) + over-count warning). Ruled-in minor: trim the 11-line comment (violates user's global comment rules). Deferred: evidence header OUT name, CDLL no-op, fork-order wording, em-dash comment footgun, spurious-IRQ_TAKEN caveat.
Task 7: fix round 1 dispatched.
Task 7: fix round 1/5 (fix 26ff5fe1 — fatal guard + trigger accounting + max(n,3) floor + comment trim; all three proofs quoted in evidence appendix; scoped re-review dispatched, sonnet)
Task 7: fix round 1/5 (3+style addressed, 0 open; commit 26ff5fe1)
Task 7: complete (commits 668c85b7..26ff5fe1, review clean after 1 fix round). Milestone B green with enforced accounting.
BASE for T8: 26ff5fe1
Task 8: dispatched (implementer=sonnet — TB_CONTRACT + docs + codex-findings disposition)
Task 8: implementer DONE (76e196c9). New docs/dv/known-followups.md convention (1 entry). Task review dispatched (sonnet).
Task 8: review Needs fixes — 1 Important (counter accessor names omitted from TB_CONTRACT §3). Ruling: results.xml placement in BUILD_AND_SIM signed off (harness artifact, not interface). Minor deferred: trigger() param-name prose mismatch.
Task 8: fix round 1 dispatched.
Task 8: fix round 1/5 (1 addressed; commit aea3d6f9)
Task 8: complete (commits 26ff5fe1..aea3d6f9, review clean after 1 fix round)
ALL WS2 TASKS COMPLETE. Final whole-branch review dispatching (fable), WS2 scope over bfd74d7c..aea3d6f9 (contains WS3 merge — separately reviewed).
WS2 final review (fable): With fixes — 1 Critical (evidence chain cites uncommitted .superpowers paths; commit reports to docs/dv/process-logs/ws2/ + repoint), 5 Important. Rulings: fix 1-4+6 as prescribed (event name+param word; $fatal em-dash; non-VCS COCOTB guard; SV end-of-test zero-trigger uvm_error); #5 fcov manifest — attempt the real manifest (bin verified via one COV=1 run of the test; full-triad flagship) with exemption-ruling fallback if bin identification is murky; ride-along: COCOTB_MODULE named in the knob-flip gotcha (minor 9). Recorded: WS3's out-of-path root-Makefile lint fix (minor 8) — correct but violated the declared-paths claim. All other minors: triaged defer by the reviewer, stands.
Final fix wave dispatched (sonnet, fresh).
WS2 final fix wave: 3 commits (2932699c evidence chain, 839646db code+contract fixes incl. REAL fcov manifest for the flagship test, 83847d0d report archived). Scoped re-review dispatched (sonnet).
Codex post-execution review 04: REQUEST-CHANGES — 2 Critical (default TEST=all COCOTB=0 regression now FAILS on the vacuous-pass guard — stock-neutrality broken, missed by every Claude seat; Milestone B negative control is not full mutation-check procedure), 3 Important (over-count only warns + counter semantics contradict contract; contract lacks inline manifest schema/COV=1; contract lacks runnable command). Rulings: fix all — testlist cocotb-marker filtering when COCOTB=0 (explicit selection keeps the fatal); full MUT-002 mutation-check on the flagship checker (named record, +disable_cosim, ablation-survives, revert); over-count becomes FAILURE via count==triggers_sent alongside the floor (ablation math still fails at 0>=3); contract gains actual counter semantics + inline fcov schema/knob + generic runnable command. Artifact committed.
Codex re-review 04b: originals 5/5 ADDRESSED (MUT-002 under-ruling), 2 NEW Critical fence-integrity leaks from round 2 (generation-visible mutation README detail; real human bin in the contract's fcov example) + 2 nonblocking cleanups. Round 3 dispatched: strip README to MUT-001 shape, synthetic-namespace example, both one-liners ruled in.
