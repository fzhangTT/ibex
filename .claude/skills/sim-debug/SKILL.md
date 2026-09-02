---
name: sim-debug
description: Triage a failing ibex DV simulation from its out-tree artifacts — classify the failing stage, extract the minimal excerpt, and propose the next probe. Use on any sim/regression failure before proposing fixes.
---

# sim-debug

Input: a test name (and optionally the OUT dir; default newest `out*/` under `dv/uvm/core_ibex`).

1. Locate the run dir: `out*/run/tests/<test>.<seed>/`; read `trr.yaml` first — `passed`,
   `failure_mode`, `failure_message` classify most failures outright.
2. Classify by stage, using these verified log names (0-byte `compile.riscvdv.log` = clean compile,
   not a failure):
   - riscv-dv generator build → `out*/build/instr_gen/build_stdout.log`
   - test generation → gen logs in the run dir
   - cross-compile → `compile.riscvdv.log`
   - TB compile → `out*/build/tb/compile_tb_stdstreams.log` (spike pkg-config/link errors land here)
   - simulation → `rtl_sim_stdstreams.log` / `rtl_sim.log`
3. Known signatures to check before deep-diving (grep the sim log):
   - cosim mismatch → `docs/dv/COSIM.md` §"How failures surface" (architectural state quoted;
     compare against `spike_cosim_trace_core_00000000.log`)
   - `Error-[FCIBH]` → the `default sequence` illegal-bins gotcha (`BUILD_AND_SIM.md`); should not
     appear under VCS builds (guarded) — if it does, the guard regressed
   - `cocotb failed to start (cctb_alive still 0 at 100ns)` → Python import error; the traceback is
     earlier in the same log
   - `TB-CONFIG:` banner absent → the sim never reached time 0; look at elaboration
4. Output contract: failing stage, minimal excerpt (≤15 lines), one hypothesis, one next probe
   (a rerun knob, a wave, or a file to read). Never propose a fix before the stage is classified.

Site rules: poll logs directly with deadlines (notifications unreliable); fresh `OUT=` after
editing testlists/configs (stale `metadata.pickle`).
