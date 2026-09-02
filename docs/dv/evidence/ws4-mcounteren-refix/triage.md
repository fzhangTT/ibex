# `mcounteren_test` triage — WS4 gate-nightly cosim mismatch

Run dir: `dv/uvm/core_ibex/out_ci/gate-nightly/run/tests/mcounteren_test.260902/`
Read-only triage per the `sim-debug` skill; no sims were run, no files were mutated.

## 1. Stage classification

- `compile.directed.log` — 0 bytes → clean cross-compile (not the failing stage).
- `rtl_sim_stdstreams.log` / `trr.yaml` → **simulation stage**, cosim scoreboard mismatch
  (`failure_mode: LOG_ERROR(3)`), `UVM_FATAL` from `ibex_cosim_scoreboard.sv(172)` at `@ 2025900`.

## 2. Minimal failing excerpt

From `trr.yaml` `failure_message` (verbatim):

```
36: 1458900: Illegal instruction (hart 0) at PC 0x8000032e: 0xc01022f3
37: 1460900: Illegal instruction (hart 0) at PC 0x8000032e: 0xc01022f3
[E] 38: UVM_FATAL ibex_cosim_scoreboard.sv(172) @ 2025900: Cosim mismatch
    Synchronous trap was expected at ISS PC: 80002400
    but the DUT didn't report one at PC 8000037a
```

Cross-checked against `trace_core_00000000.log` (DUT retire trace) at the same
timestamp:

```
2025900   911   8000037a   c03022f3   csrrs  x5,hpmcounter3,x0   x5=0x00000000
```

— the DUT retired the U-mode `csrr hpmcounter3` instruction cleanly (no trap).
Earlier in the same trace (`t=1023900`), `mcounteren` reads back as `0x1ffd`
after software wrote `0xffffffff`, i.e. bit 3 (hpmcounter3's enable bit) is `1`
and the DUT's `MHPMCounterNum` is confirmed to be `10` (bits 3..12 sticky, matching
`MHPMCOUNTER_BASE=3` + 10 counters, per `rtl/ibex_cs_registers.sv` gating logic
`illegal_csr = (priv_lvl_q==PRIV_LVL_U) && !mcounteren[idx]`). So the DUT's
behavior is self-consistent with its own declared config and the ISA spec: HPM
counter 3 is implemented, enabled via `mcounteren`, and U-mode access is
correctly permitted.

`spike_cosim.cc:266-273` shows the mismatch is raised when spike's own step
produced `PC_INVALID` with a synchronous-trap cause (`processor->get_state()->pc`
== spike's post-trap PC == `0x80002400`, matching Ibex's `mtvec`) while the
RVFI-derived `sync_trap` flag from the DUT was `false`. Direction is therefore:
**ISS (spike) trapped; DUT did not** — the reverse of what the new mcounteren
fixup was meant to guarantee.

## 3. Git history (recent related commits)

```
aae4809a [dv] Check u-mode counter alias the correct m-mode counter
eed82556 [dv] Add directed test for mcounteren lock signal
ebed1807 [dv] Add `mcounteren` directed test
3c6b450c [dv] Fix ordering in `directed_testlist.yml`
026e71ea [dv] Implement Ibex-specific mcounteren behavior in cosim
```

`026e71ea` added the `CSR_MCOUNTEREN` case to `fixup_csr()` in
`dv/cosim/spike_cosim.cc` (masks the written value down to
`0x5 | (((1<<mhpm_counter_num)-1)<<3)`), threading `mhpm_counter_num` in from
`cosim_cfg.mhpm_counter_num` (`ibex_cosim_scoreboard.sv:78`) which in turn comes
from the TB's own `MHPMCounterNum` parameter via `uvm_config_db` (`core_ibex_tb_top.sv:428`,
`core_ibex_base_test.sv:161`). That value-masking path checks out — for this
build, `mhpm_counter_num=10`, and the masked value (`0x1ffd`) matches what the
DUT itself reads back. **The masking of the register's stored value is correct.**

The problem is elsewhere: `docs/dv/COSIM.md` §3 documents that the *pinned*
lowRISC Spike fork (not this repo) has its own, separate, blanket gate on
U-mode HPM-counter access:

```
0dc2de5d  Disable ZIHPM unpriviledged performance counters (to match Ibex implementation)
          — riscv/isa_parser.cc: extension_table[EXT_ZIHPM] = false;
             // IBEX does not implement this extension
```

That patch makes spike treat **every** U-mode access to `hpmcounterN`/`hpmcounterNh`
as illegal unconditionally (ZIHPM extension disabled at the decoder level),
independent of `mcounteren`'s value. It predates `026e71ea` by roughly 3.5 years
and was correct when Ibex had no U-mode HPM-counter aliasing at all.

Crucially, there is already a **follow-up commit reversing it** on the same
upstream fork, authored by the same person who wrote `026e71ea`:

```
$IBEX_TOOLS_DIR/src/riscv-isa-sim-lowrisc, branch origin/ibex_cosim:
aadf648d  Enable ZIHPM unpriviledged performance counters
          "By now, we support those performance counters in Ibex so we
           enable them again." — riscv/isa_parser.cc: EXT_ZIHPM = true;
4b973966  Remove Zcmt from Readme   <-- currently pinned SPIKE_REV
```

`ci/build-spike.sh:6` pins `SPIKE_REV=4b97396656485a129119deaec2ba35e5bf354841`,
which is **exactly one commit behind** `aadf648d` on `origin/ibex_cosim`. The
locally checked-out spike source at
`$IBEX_TOOLS_DIR/src/riscv-isa-sim-lowrisc` confirms: HEAD is detached at
`4b973966`, `0dc2de5d` is an ancestor, `aadf648d` is not, and
`riscv/isa_parser.cc:39` currently reads
`extension_table[EXT_ZIHPM] = false; // IBEX does not implement this extension`.

## 4. Classification

**(a) Fork customization diverging from RTL — HIGH confidence.**

Not a bug in `dv/cosim/spike_cosim.cc`'s new `fixup_csr` logic itself (that
part is internally correct and matches the DUT's own `mcounteren` readback).
The actual defect is a **stale vendored-Spike pin**: `026e71ea`'s ibex-side
mcounteren support assumes ZIHPM is enabled in Spike (so U-mode HPM-counter
access is gated purely by `mcounteren`, matching current Ibex RTL), but
`ci/build-spike.sh`'s pinned `SPIKE_REV` predates the companion upstream commit
(`aadf648d`) that re-enables ZIHPM. Until that pin is bumped, Spike
unconditionally illegal-instructions any U-mode `hpmcounterN`/`hpmcounterNh`
read, which is exactly the divergence observed at PC `0x8000037a`.

Ruled out:
- **(b) test/config expectation issue** — low confidence. The test computes
  its expected pass/fail per-CSR dynamically from a live `mcounteren` readback
  (`s2`, `RUN_CSR_TEST`'s `s1 = snez(s2 & mask)`), not from a hardcoded
  MHPMCounterNum assumption, so it isn't relying on a wrong config guess. No
  IBEX_CONFIG/U-mode-availability mismatch found — PMPEnable=1 is the only
  override in `directed_data`, and U-mode is exercised successfully elsewhere
  in the same run (the `time`-CSR trap at PC `0x8000032e` matches correctly on
  both sides).
- **(c) genuine RTL bug** — low confidence. The DUT's own state is internally
  consistent with its declared config and the ISA-mandated
  `mcounteren`-gates-U-mode-CSR-access semantics; no RTL inconsistency found in
  the trace evidence gathered.

## 5. Next probe

Confirm by diffing the pinned-vs-fixed Spike decode path rather than by
re-running the failing test: in
`$IBEX_TOOLS_DIR/src/riscv-isa-sim-lowrisc`, check whether
`git checkout aadf648d` (or later) changes `riscv/isa_parser.cc:39` to
`extension_table[EXT_ZIHPM] = true;` and whether that's the *only* delta needed
(`git diff 4b973966 aadf648d -- riscv/`), then have whoever owns
`ci/build-spike.sh`/the tools pin bump `SPIKE_REV` to `aadf648d` (or later,
checking nothing after it regresses) and rebuild spike + the TB. This is a
**shared/vendored-infra pin change** (external Spike fork checkout +
`ci/build-spike.sh`), not something to patch inside this triage — escalating
per policy rather than editing the pin myself. If the pin bump doesn't fully
resolve it, the next layer to check is whether `fixup_csr`'s `CSR_MCOUNTEREN`
mask still needs a matching correction once ZIHPM is live end-to-end (unlikely,
since the mask already matches the DUT's own readback, but worth a clean rerun
to confirm no residual mismatch after the pin bump).
