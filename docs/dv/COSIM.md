# Ibex Instruction-Level Co-simulation (Spike)

This document covers `core_ibex`'s instruction-level co-simulation: how the
UVM testbench, the DPI boundary, and the linked-in Spike reference model fit
together, what a mismatch looks like on disk, what this fork changed versus
upstream lowRISC Spike, and where the model's coverage stops (CHERIoT).

This is **not** the generic riscv-dv "run an ISS as a subprocess and diff
commit logs" flow (`vendor/google_riscv-dv/yaml/iss.yaml:15-18` still defines
that `spike --log-commits ...` invocation, but nothing in `core_ibex` calls
it). Instead, Spike is linked directly into the VCS testbench binary and
stepped one retired instruction at a time from SystemVerilog via DPI-C.

## 1. Architecture: TB <-> DPI <-> `SpikeCosim`

```
ibex_cosim_scoreboard.sv (UVM, per-instr/per-txn)
        |  cosim_dpi.svh / spike_cosim_dpi.svh (DPI-C imports)
        v
cosim_dpi.cc, spike_cosim_dpi.cc (extern "C" glue)
        |  dispatches through the abstract Cosim* handle
        v
SpikeCosim : simif_t, Cosim   (dv/cosim/spike_cosim.{h,cc})
        |  wraps a spike processor_t
        v
lowRISC riscv-isa-sim fork (linked library)
```

`ibex_cosim_scoreboard.sv` (`dv/uvm/core_ibex/common/ibex_cosim_agent/`) is
the only consumer of the DPI interface. `spike_cosim_init()`
(`.../ibex_cosim_agent/spike_cosim_dpi.cc:13-36`) is called once per reset
(`ibex_cosim_scoreboard.sv:70-84`, `init_cosim()`); it builds a `SpikeCosim`
with the config's ISA string, PMP/HPM/secure/icache/debug-module parameters
(`core_ibex_cosim_cfg`, `.../ibex_cosim_agent/ibex_cosim_cfg.sv`) and adds a
single memory device spanning almost the whole 32-bit address space
(`cosim->add_memory(0x00000000, 0xFFFF0000)`), returned to SV as an opaque
`chandle` (`Cosim*` upcast). Everything after that goes through the generic
`Cosim` DPI surface in `dv/cosim/cosim.h`/`cosim_dpi.svh`, not through any
`SpikeCosim`-specific entry point.

### Per-instruction step-and-compare

`run_cosim_rvfi()` (`ibex_cosim_scoreboard.sv:116-176`) drains the RVFI
monitor port one retired-instruction item at a time. For each item it first
pushes side-band state that must be visible *before* the step — debug
request, NMI/internal-NMI, MIP pre/post values, mcycle, the ten
MHPMCOUNTER/MHPMCOUNTERH CSRs (driven as a pseudo-backdoor write since Ibex's
perf counters aren't otherwise observable to Spike), and the ICache
scramble-key-valid bit — then calls the actual check:

```systemverilog
// ibex_cosim_scoreboard.sv:165-174
if (!riscv_cosim_step(cosim_handle, rvfi_instr.rd_addr, rvfi_instr.rd_wdata, rvfi_instr.pc,
                      rvfi_instr.trap, rvfi_instr.rf_wr_suppress)) begin
  if (cfg.relax_cosim_check) begin
    `uvm_info(`gfn, get_cosim_error_str(), UVM_LOW)
  end else begin
    `uvm_fatal(`gfn, get_cosim_error_str())
  end
end
```

`SpikeCosim::step()` (`dv/cosim/spike_cosim.cc:175-322`) does the work:

- Debug `ebreak` is special-cased first (`pc_is_debug_ebreak`/
  `check_debug_ebreak`) since Spike treats entry to debug mode as "no
  instruction retired, immediately execute the next one."
- Otherwise it calls Spike's own `processor->step(1)` and uses the
  `last_inst_pc == PC_INVALID` sentinel plus the top bit of `mcause` to tell
  apart three cases: a retired instruction, a synchronous trap (checked by
  `check_sync_trap`, `spike_cosim.cc:392-436` — PC match and *no* side
  effects, since a trapping instruction is presented on RVFI but never
  retires), and an asynchronous trap (steps once more to reach the first
  handler instruction).
- For a retired instruction, `check_retired_instr()`
  (`spike_cosim.cc:324-390`) checks, per instruction:
  - **PC**: DUT's reported `pc` vs Spike's `last_inst_pc`.
  - **GPR write**: index and data (`check_gpr_write`,
    `spike_cosim.cc:438-476`) against the DUT's `write_reg`/`write_reg_data`;
    `write_reg == 0` means "no write expected," and a write index mismatch
    or data mismatch is a distinct error string.
  - **CSR writes**: every CSR write Spike's commit log records is replayed
    into Spike's own state through `on_csr_write()` ->
    `fixup_csr()` (`spike_cosim.cc:503-514`, `787-855`) — not diffed against
    the DUT, but *masked to Ibex's WARL behavior* (MSTATUS, MCAUSE, MTVEC,
    MISA, MCOUNTEREN) so later steps don't diverge because Spike's own CSR
    write semantics are looser than Ibex's hardware.
  - **Suppressed writes**: `suppress_reg_write` (Ibex dropping a GPR write
    because a load returned bad-integrity data) is checked against
    `pc_is_load()` before the step, and Spike's destination register is
    restored to its pre-step value afterward so cosim state stays in sync.

### Memory checking

DUT-side dside transactions are queued as they retire off the memory monitor
(`run_cosim_dmem()`, `ibex_cosim_scoreboard.sv:178-188`, ->
`notify_dside_access()`, `cosim.h:145`, `spike_cosim.cc:767-773`, into a
`pending_dside_accesses` FIFO). Spike's own `mmio_load`/`mmio_store`
callbacks (`spike_cosim.cc:87-123`) fire as Spike executes the matching
instruction and call `check_mem_access()` (`spike_cosim.cc:857-1053`), which
checks address, store-vs-load, byte-enable, and data against the head of
that FIFO. Misaligned accesses get extra handling since Ibex splits them
into two bus transactions while Spike checks PMP byte-by-byte and can abort
partway through — `misaligned_pmp_fixup()` (`spike_cosim.cc:651-686`)
detects the resulting benign divergence (second half of a misaligned access
that Ibex issued but Spike didn't reach) and cross-checks it against Spike's
MMU (`mmu->pmp_ok()`) rather than flagging a false mismatch.

Instruction-side (fetch) errors follow a separate path since RVFI has no
per-fetch signal: `run_cosim_imem`/`run_cosim_ifetch`/`run_cosim_ifetch_pmp`
track which fetch addresses saw an error, `run_cosim_imem_errors`
correlates a failing address with the RVFI order of the instruction that
was fetched from it (`ibex_cosim_scoreboard.sv:190-307`), and
`run_cosim_prune_imem_errors` drops queued errors for instructions that get
flushed before they'd otherwise reach RVFI. A matched error is pushed via
`riscv_cosim_set_iside_error()` before the corresponding `step()`, so Spike
is told in advance to expect an instruction fault at that address.

### Error reporting out of the model

`Cosim::get_errors()` returns a `vector<string>` accumulated during `step()`
and `check_mem_access()`. `get_cosim_error_str()`
(`ibex_cosim_scoreboard.sv:333-341`) concatenates all pending error strings
under one `"Cosim mismatch "` prefix and clears them
(`riscv_cosim_clear_errors`) — that string is what reaches `uvm_fatal`.

## 2. How failures surface

**In `rtl_sim.log`**, a mismatch is a `UVM_FATAL` from
`ibex_cosim_scoreboard.sv(172)` whose body is the `"Cosim mismatch "` string
above. The individual error strings are built in `spike_cosim.cc` and are
specific about what didn't match, e.g. (verbatim formats from the source,
not from a captured failure — no failing run exists to quote from):

```
PC mismatch, DUT retired : 80000090 , but the ISS retired: 8000008c
DUT wrote register x10 but a write was not expected
Register write data mismatch to x12 DUT: deadbeef expected: 12345678
DUT generated store at address 80001000 with BE 3 but BE f was expected
```

On a passing run there is no such block; instead `final_phase()`
(`ibex_cosim_scoreboard.sv:343-350`) logs one line per test and the run ends
in `--- RISC-V UVM TEST PASSED ---`. From the real
`riscv_arithmetic_basic_test.1` run used for this doc
(`dv/uvm/core_ibex/out/run/tests/riscv_arithmetic_basic_test.1/rtl_sim.log`,
lines 27, 38, 40):

```
TB-CONFIG: BaseIsa=BaseIsaRV32IorCHERIoT RegFile=RegFileFF RV32ZC=RV32ZcaZcbZcmp
...
UVM_INFO .../ibex_cosim_scoreboard.sv(346) @ 164878400: uvm_test_top.env.cosim_agent.scoreboard [uvm_test_top.env.cosim_agent.scoreboard] Co-simulation matched      10448 instructions

--- RISC-V UVM TEST PASSED ---
```

**Post-processing** turns that log into pass/fail metadata.
`check_logs.py:compare_test_run()` (`dv/uvm/core_ibex/scripts/check_logs.py:27-79`)
calls `check_ibex_uvm_log()`
(`dv/uvm/core_ibex/riscv_dv_extension/ibex_log_to_trace_csv.py:177-251`),
which scans `rtl_sim.log` line by line for `UVM_ERROR`/`UVM_FATAL`/`Error`
before a `RISC-V UVM TEST PASSED` line is seen. On a hit it records the
first offending line, then re-scans to pull a ±5-line window around it
(`ibex_log_to_trace_csv.py:239-243`) tagging the exact line with `[E]`, and
classifies the failure as `Failure_Modes.TIMEOUT` (wall-clock) or
`Failure_Modes.LOG_ERROR` (everything else, including a cosim mismatch) —
`test_run_result.py:26-36`. `check_logs.py` writes that into
`trr.failure_message` wrapped in `---------------*LOG-EXTRACT*----------------`
markers and sets `trr.passed = False`, then `trr.export(write_yaml=True)`
serializes the whole `TestRunResult` dataclass to `trr.yaml`.

**In `trr.yaml`**, the pass-relevant fields on the real passing run above
(`dv/uvm/core_ibex/out/run/tests/riscv_arithmetic_basic_test.1/trr.yaml`)
read:

```yaml
passed:                   True
failure_mode:
failure_message:
...
rtl_log:                  rtl_sim_stdstreams.log
rtl_trace:                trace_core_00000000.log
iss_cosim_trace:          spike_cosim_trace_core_00000000.log
```

On a cosim mismatch, `passed: False`, `failure_mode: LOG_ERROR(3)`, and
`failure_message` carries `[FAILED]: error seen in 'rtl_sim.log'` followed
by the log-extract block described above — i.e. the `uvm_fatal` line plus
its `"Cosim mismatch "` payload, in context.

**The Spike reference trace** (`spike_cosim_trace_core_00000000.log`,
enabled by handing `SpikeCosim`'s constructor a non-empty `trace_log_path`,
which turns on `processor->enable_log_commits()` — `spike_cosim.cc:78-81`)
is Spike's own two-line-per-retired-instruction commit log: a disassembly
line, then the register/CSR write line. Real excerpt from the same run
(lines 1-8):

```
core   0: 0x80000080 (0x40001537) lui     a0, 0x40001
core   0: 3 0x80000080 (0x40001537) x10 0x40001000
core   0: 0x80000084 (0x10650513) addi    a0, a0, 262
core   0: 3 0x80000084 (0x10650513) x10 0x40001106
core   0: 0x80000088 (0x30151073) csrw    misa, a0
core   0: 3 0x80000088 (0x30151073) c769_misa 0x40901104
core   0: 0x8000008c (0x00015617) auipc   a2, 0x15
core   0: 3 0x8000008c (0x00015617) x12 0x8001508c
```

When debugging a mismatch, this file is the ground truth to line up against
the DUT's own `trace_core_00000000.log` (the `ibex_tracer` output) around
the reported PC/order — the `uvm_fatal` string tells you *which* check
failed and at which PC; these two trace files tell you what each side
actually did around that point.

## 3. What lowRISC patched in Spike vs. what this fork added

The linked Spike is a pinned lowRISC fork
(`$IBEX_TOOLS_DIR/src/riscv-isa-sim-lowrisc`, built by `ci/build-spike.sh` —
see `docs/dv/BUILD_AND_SIM.md`). Skimming
`git log --oneline --no-merges -30` in that checkout, the load-bearing
commits for cosim/commitlog behavior (as opposed to plain ISA/decode
additions) are:

| Commit | Subject (verbatim) | Backs |
|---|---|---|
| `394ce314` | Add configurable debug_module address range to the processor type | `dm_start_addr`/`dm_end_addr` ctor args, `set_debug_module_range` |
| `6d5b6608` | PMP should always allow accesses to the debug_module in debug mode. | debug-mode PMP exception used by the above |
| `39612f93` | Introduce pre_val MIP concept. | `set_mip(pre_mip, post_mip)`'s two-value interface |
| `f7c682a5` | DEBUG_ROM_TVEC -> 0x80000008 | matches Ibex's fixed debug ROM entry |
| `1f89c527` | Remove debug memory access check | lets `backdoor_read_mem`/cosim reach debug-module addresses |
| `c0926fc3` | Move mmu_t::pmp_ok to public | used directly by `misaligned_pmp_fixup()` |
| `15fbd568` | Move ebreak* logic from take_trap into instructions. (#1006) | makes ebreak enter debug mode directly (via `dcsr.ebreakm/s/u`) instead of a normal trap — the path `pc_is_debug_ebreak()`/`check_debug_ebreak()` (`spike_cosim.cc:1065-1120`) special-case |
| `0e306ce7` | Allow hardware triggers to go off without using the mmu tlb | commit message states this explicitly: "For our cosimulation env, the Spike mmu TLB functionality is not used" — without it, hardware triggers (used by the debug-trigger CSR setup in `initial_proc_setup()`) would never fire |
| `6272327d` | Add Internal NMI field in Spike | `set_nmi_int()` |
| `ce7a9be2` | Hardcode TDATA1 fields to match implemented ibex features | matches `initial_proc_setup()`'s `TM.tdata1_write` hardcoding |
| `0dc2de5d` | Disable ZIHPM unpriviledged performance counters (to match Ibex implementation) | superseded by `aadf648d` below — see there for the current behavior |
| `f125d93a` | Hardcode MHPM event register wrt. MHPMCounterNum | `mhpm_counter_num`-sized event CSRs |
| `aadf648d` | Enable ZIHPM unpriviledged performance counters | re-enables ZIHPM (reverses `0dc2de5d`); Ibex supports mcounteren-gated U-mode HPM access, not a blanket disable |
| `9a6f786a` | Change ebreak instructions to not save pc to mtval | matches Ibex's ebreak behavior |
| `68edd179` | Rename CPUCTRL to CPUCTRLSTS and add ic_scr_key_valid field | `set_ic_scr_key_valid()`, CPUCTRLSTS double-fault tracking |
| `9b68f2f9` | Add MCONFIGPTR CSR | Ibex exposes this CSR |
| `2806109f` | Add (M/S)CONTEXT as read-only-0 csr's to match Ibex implementation | Ibex hardwires these to 0 |
| `eccdcb15` | Unify PMPCFGx behaviour with PMPADDRx where PMP is disabled | matches Ibex PMP-disabled read-back |
| `c9a893a3` | Revert "Revert "pmp: mstatus.mprv should be clear if mpp is not M-mode"" | Ibex-specific fix: clears `mstatus.MPRV` on `mret`/`sret` when `mstatus.MPP` isn't M-mode |
| `a5692fb0` | Fix CPUCTRL CSR | commit message: fixes CPUCTRL (now CPUCTRLSTS) to read the icache/secure-Ibex parameters live off the processor instance rather than a stale copy — needed because `SpikeCosim`'s constructor sets those parameters (`set_ibex_flags`, `spike_cosim.cc:73`) after `processor_t`'s own constructor has already run |

Two more of the 30 are cosim-adjacent but don't back a specific runtime
check, so they're kept out of the table above: `2ee11169` "Add CI to build
ibex_cosim" is build infrastructure, not runtime behavior, and `ef10d395`
"fesvr: fix compilation with gcc 13" is a generic upstream portability fix
(missing `<cstdint>` include) unrelated to cosim or to any ISA extension.

The remaining 9 of the 30
(`4b973966`, `69471d63`, `d691e19e`, `0a171692`, `5ab7b312`, `f58aa591`,
`5643be11`, `bb9a10f8`, `46902f0b`) add Zc*-extension decode/disassembly
support (plus the `encoding.h` regeneration and cherry-pick compatibility
fixes that support it) — they matter for running compressed-extension tests
but aren't cosim-hook or commitlog changes.

**What this fork added on top, in `dv/cosim`:** the entire `Cosim`/
`SpikeCosim` DPI adapter (`cosim.h`, `cosim_dpi.{h,cc,svh}`,
`spike_cosim.{h,cc}`) is Ibex-repo-specific — it is not part of Spike
upstream or the lowRISC fork; it is this repo's step-and-compare harness
built *over* the linked Spike library. Within that adapter, the `fixup_csr()`
switch (`spike_cosim.cc:787-855`) exists purely because Spike's own CSR
write semantics don't match Ibex's WARL behavior; each case is a
fork-local correction, not something lowRISC's Spike commits provide. The
most recent example is commit `026e71ea` "[dv] Implement Ibex-specific
mcounteren behavior in cosim": it added the `mhpm_counter_num` field to
`SpikeCosim` and a `CSR_MCOUNTEREN` case to `fixup_csr()`
(`spike_cosim.cc:841-853`) that masks MCOUNTEREN down to bit 0/bit 2
(mcycle/minstret, always implemented) plus exactly the bits for the
configured number of HPM counters — matching Ibex's hardwired-zero behavior
for unimplemented counters instead of Spike's more permissive default.

## 4. Augmentation gaps

Spike — including the lowRISC fork above — has **no CHERIoT knowledge**:
none of the sampled commits touch capability registers, tag bits, or
CHERIoT-mode decode/execution semantics.

This is not currently a problem because the testbench hard-ties CHERIoT off
regardless of `IBEX_CONFIG`:

```systemverilog
// dv/uvm/core_ibex/tb/core_ibex_tb_top.sv:194
.cheriot_enable_i          (ibex_pkg::IbexMuBiOff      ),
```

So the DUT never actually runs in CHERIoT mode under this DV flow today —
`opentitan`'s `BaseIsa=BaseIsaRV32IorCHERIoT` selects CHERIoT-*capable*
hardware, but `cheriot_enable_i` keeps it running as plain RV32I at runtime
(confirmed by the `TB-CONFIG` banner in section 2, and by
`docs/dv/BUILD_AND_SIM.md`'s Gotchas section).

If `cheriot_enable_i` is ever driven to `IbexMuBiOn` through this TB, this
cosim setup cannot verify it as-is: Spike would keep executing/decoding the
plain integer ISA and diverge immediately on the first capability-affecting
instruction or tag-bit side effect (a GPR/memory "mismatch" that isn't a
real DUT bug — it's a reference-model gap). Closing this gap needs a
CHERIoT-aware reference model swapped in for (or run alongside) `SpikeCosim`
— the CHERIoT ecosystem's own Sail model is the natural candidate, since
Spike upstream has no CHERIoT support to pull in. That work is out of scope
for WS1; this section exists to track it as a known limitation of the
current cosim, not a defect in it.
