---
name: sim-debug
description: Triage a failing ibex DV simulation from its out-tree artifacts — classify the failing stage, extract the minimal excerpt, and propose the next probe. Use on any sim/regression failure before proposing fixes.
---

# sim-debug

Input: a test name (and optionally the output dir; default the newest out-tree the team's runner
wrote under `dv/auto_dv/`).

1. Locate the failing run's artifacts; if the team's flow writes a per-test verdict record, read
   it first — it classifies most failures outright.
2. Classify by stage, in pipeline order: program/stimulus generation → cross-compile → TB compile
   (`SIM_RECIPE.md` §2 log) → elaboration → simulation (§5 log) → post-run checks (fcov
   expectations, log scan). A 0-byte sub-step log usually means a clean step, not a failure —
   confirm against the runner before treating it as one.
3. Known signatures to check before deep-diving (grep the sim log):
   - `Error-[FCIBH]` → VCS `default sequence` transition-bin gotcha (`SIM_RECIPE.md` §9);
     enumerate legal transitions instead.
   - Python side dead at start → either the TB's alive-bit watchdog `$fatal` (no Python ran at
     all) or cocotb's own CRITICAL import traceback at time 0; the first real error is earlier in
     the same log (`TB_CONTRACT.md` §2).
   - Timeout from the finish-polling handshake → undersized budget on an otherwise-passing run
     vs. a genuinely hung program — check whether the program reached its completion handshake
     (`TB_CONTRACT.md` §2).
   - License-wait messages (`-licqueue`/`+vcs+lic+wait`) → waits, not failures.
   - The TB's time-0 config banner absent → the sim never reached time 0; look at elaboration.
4. Output contract: failing stage, minimal excerpt (≤15 lines), one hypothesis, one next probe
   (a rerun knob, a wave, or a file to read). Never propose a fix before the stage is classified.

Site rules: poll logs directly with deadlines (notifications unreliable); fresh output directory
after editing testlists/knobs (`SIM_RECIPE.md` §9).
