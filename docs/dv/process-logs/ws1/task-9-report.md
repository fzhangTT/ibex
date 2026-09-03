# Task 9 Report: `docs/dv/COSIM.md`

## Summary

Wrote `docs/dv/COSIM.md`, a cosim architecture reference covering the
step-and-compare mechanism between the UVM TB and the linked-in Spike model,
how mismatches surface on disk, what the lowRISC Spike fork vs. this repo's
`dv/cosim` layer each contribute, and the CHERIoT augmentation gap.

## Process

1. Read the interface-first order specified in the brief:
   `dv/cosim/cosim.h` -> `spike_cosim.h` -> `spike_cosim.cc` ->
   `cosim_dpi.svh`. Also read `dv/cosim/cosim_dpi.cc` (the generic DPI glue
   that dispatches through `Cosim*`) and
   `dv/uvm/core_ibex/common/ibex_cosim_agent/spike_cosim_dpi.cc` (the
   Ibex-DV-specific glue that actually constructs a `SpikeCosim` and hands
   it back as a `Cosim*` handle) to close the loop from SV all the way to
   the concrete model, and `ibex_cosim_scoreboard.sv` to see how the
   per-instruction/per-transaction DPI calls are actually driven.

2. **Artifacts from Task 6 no longer existed on disk** — `out/` is
   gitignored and had been cleaned since that task ran, so
   `dv/uvm/core_ibex/out/run/tests/riscv_arithmetic_basic_test.1/` (and any
   `trr.yaml`/`spike_cosim_trace_core_00000000.log`) were gone. Rather than
   fabricate excerpts, I re-ran the exact smoke command from
   `docs/dv/BUILD_AND_SIM.md` (`make SIMULATOR=vcs IBEX_CONFIG=opentitan
   ISS=spike TEST=riscv_arithmetic_basic_test ITERATIONS=1 SEED=1`), which
   passed (10448 instructions matched) and regenerated real `rtl_sim.log`,
   `trr.yaml`, and `spike_cosim_trace_core_00000000.log` files that the doc
   quotes verbatim. This directory stayed untracked/gitignored throughout
   (confirmed via `git status`/`git check-ignore` before committing).

3. Diffed the pinned Spike fork's history
   (`$IBEX_TOOLS_DIR/src/riscv-isa-sim-lowrisc`, i.e.
   `/localdev/fzhang/ws/tools/src/riscv-isa-sim-lowrisc`): ran
   `git log --oneline --no-merges -30` and classified each commit as
   cosim/commitlog-load-bearing vs. plain Zc*-decode support, listing only
   the former in a table with what in `spike_cosim.cc` each one backs.

4. No failing cosim run was available to quote a real `UVM_FATAL` block
   from, so the doc is explicit that the mismatch-string examples are
   verbatim error-message formats taken from `spike_cosim.cc`'s source (not
   a captured failure), while the log-processing mechanics (how
   `check_logs.py`/`ibex_log_to_trace_csv.py` turn a `UVM_FATAL` into
   `trr.yaml`'s `failure_mode`/`failure_message`) are described from the
   real script code with file:line citations.

5. Verified `git status` was clean before and after `git add
   docs/dv/COSIM.md`, then committed on `fzhang/auto-dv-setup`.

## Doc section structure

1. Architecture (TB -> DPI -> `SpikeCosim`, with a diagram, the per-instruction
   check list, memory/iside error checking, and error-string plumbing)
2. How failures surface (`rtl_sim.log` UVM_FATAL, `check_logs.py`/
   `ibex_log_to_trace_csv.py` log-extraction into `trr.yaml`, and the Spike
   commit-log trace format — all with real excerpts from the regenerated
   passing run)
3. What lowRISC patched in Spike (commit table) vs. what this fork added in
   `dv/cosim` (the `Cosim`/`SpikeCosim` adapter itself, `fixup_csr()`, and
   commit `026e71ea`'s mcounteren behavior)
4. Augmentation gaps (Spike has no CHERIoT knowledge; safe today because
   `cheriot_enable_i` is tied off at `tb/core_ibex_tb_top.sv:194`; a
   CHERIoT-aware Sail-based reference model would be needed to close it,
   out of scope)

## Commit

`08255d8b` `[docs] Add cosim architecture reference` on
`fzhang/auto-dv-setup` (verified branch before committing). Working tree is
clean; no `out*/` paths were staged (confirmed gitignored).

## Fix round 1

Review found the Section 3 commit survey was incomplete and contained a
misattributed row. Re-ran `git log --oneline --no-merges -30` in
`riscv-isa-sim-lowrisc` and reclassified all 30 commits, verifying with a
scripted set-diff (sorted list of the 30 real hashes vs. every hash used in
the doc's buckets — empty diff) that each commit now appears in exactly one
bucket.

- **Finding 1 (Critical) — incomplete/false survey.** `ef10d395`,
  `15fbd568`, and `0e306ce7` were missing from both the load-bearing table
  and the "remaining" list, and the doc's closing sentence ("the remaining
  commits are all Zc*") was therefore false. Read each commit's message and
  diff:
  - `0e306ce7` "Allow hardware triggers to go off without using the mmu
    tlb" — its own message says "For our cosimulation env, the Spike mmu
    TLB functionality is not used" — added to the load-bearing table.
  - `15fbd568` "Move ebreak* logic from take_trap into instructions.
    (#1006)" — read its diff (`riscv/execute.cc`, `riscv/insns/c_ebreak.h`):
    it makes `c.ebreak`/`ebreak` throw `trap_debug_mode` and enter debug
    mode directly (gated on `dcsr.ebreakm/s/u`) instead of taking a normal
    trap. That is exactly the path `SpikeCosim::pc_is_debug_ebreak()` /
    `check_debug_ebreak()` (`spike_cosim.cc:1065-1120`) special-case before
    any other retire/trap logic runs — genuinely load-bearing, added to the
    table.
  - `ef10d395` "fesvr: fix compilation with gcc 13" — a generic upstream
    portability fix (missing `<cstdint>` include), unrelated to cosim hooks
    *and* unrelated to Zc*. Called out as its own sentence rather than
    folded into either bucket, and the false "remaining commits are all
    Zc*" claim was corrected to state the Zc*-bucket count is 9, not "the
    remaining" (which had implicitly included `ef10d395`).
  - Also pulled `2ee11169` ("Add CI to build ibex_cosim") out of the
    load-bearing table into the same one-line callout as `ef10d395` — it's
    cosim-adjacent but is build infrastructure, not a runtime-behavior
    commit, so it doesn't belong in a table whose "Backs" column cites
    specific `SpikeCosim` checks.

- **Finding 2 (Important) — invented paraphrase under "Subject."** The row
  `c9a893a3, a5692fb0 | pmp/CPUCTRL CSR fixes | ...` put a made-up summary
  in the column headed "Subject." Split it into two rows, one per commit,
  each with its actual verbatim `git log --format=%s` subject line
  (`Revert "Revert "pmp: mstatus.mprv should be clear if mpp is not
  M-mode""` and `Fix CPUCTRL CSR`), and moved the paraphrased explanation
  into the "Backs" column where it belongs — for `a5692fb0` sourced from
  its own commit message (CPUCTRL/CPUCTRLSTS was being fixed to read
  `secure_ibex`/`icache_en` live off the processor instance rather than a
  stale copy, since `SpikeCosim`'s constructor sets those parameters via
  `set_ibex_flags()`, `spike_cosim.cc:73`, after `processor_t`'s own
  constructor already ran).

The deferred Minor (`check_logs.py` cited as 27-79 vs. actual 27-81) was
left as-is per instruction.

Verified before committing: table + two callout commits + Zc* list = 19 + 2
+ 9 = 30, and a sorted-hash diff against the real `git log` output for all
30 commits was empty.

**Commit:** `68667d51` `[docs] Fix incomplete/inaccurate spike commit
survey in COSIM.md` on `fzhang/auto-dv-setup`. Working tree clean after
commit; no `out*/` paths staged.
