# Ibex auto-DV testbench architecture

## 0. Header

| Field | Value |
|---|---|
| Build configuration | `opentitan` (`util/ibex_config.py opentitan vcs_opts`; every report states it) |
| DUT | `gen_dut_top` = `ibex_core` + `ibex_register_file_ff` per the DV_prompt Section 2 ruling and Q-002 (revised); instances `u_ibex_core`, `u_register_file`; `cheriot_enable_i` tied `IbexMuBiOff`, register-file `test_en_i` tied 0; bus data ports literal 39 bits (integrity in [38:32]); `+define+RVFI` |
| Document owner | DV Lead (adopts, edits, rules, signs off) |
| Component sections owner | TB Infra (Section 6, `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` v2) |
| Status | adopted by DV Lead 2026-09-03 07:04 UTC (T-006e / T-011); TB Infra draft T-048 taken as-is, Section 5 rulings filled and Section 8 DV Lead notes added by the DV Lead. Section 6 has passed the Critic's v1 review with changes applied and the cross-model pre-execution review (APPROVE-WITH-CHANGES, changes applied); its v2 re-review is in progress. Document as a whole: pending Critic T-007 part 2 and the cross-model delta review |
| Governing documents | `DV_prompt.txt`, `docs/dv/FENCE.md` (wins), `docs/dv/SIM_RECIPE.md`, `docs/dv/TB_CONTRACT.md`, `docs/dv/dv_principles.md` |
| Inputs | `dv/auto_dv/work/tb-infra/gen_tb_scoping_notes.md` (Phase 0 step 3, superseded passages marked inline), `dv/auto_dv/work/rtl-arch/gen_answers_tb_infra.md`, `dv/auto_dv/docs/gen_probe_register.md` v2, `dv/auto_dv/docs/gen_intervention_log.md`, `dv/auto_dv/work/critic/gen_critic_tb_arch_components_v1.md`, `dv/auto_dv/reviews/2026-09-03-claude-plan-gen_tb_arch_component_sections.md` |

Conventions: every generated file carries the `gen_` prefix and lives under `dv/auto_dv/`; DV never
edits `rtl/` or `vendor/`; ASCII only; one run seed; pass/fail comes from collected failure
mechanisms, never from the simulator exit code (SIM_RECIPE Section 5).

## 1. Phase 0 step 3 scoping answers (condensed; superseded passages resolved)

### 1.1 Interfaces that must be driven or observed

Each paragraph names the boundary signals, the protocol the test equipment must honour, and the
component section that specifies the agent. All stimulus enters at the `gen_dut_top` boundary; no
internal signal is driven.

**Instruction bus (`instr_req_o/gnt_i/addr_o/rvalid_i/rdata_i[38:0]/err_i`).** Request-grant then a
one-cycle response, in grant order, up to `GEN_IBUS_MAX_OUTSTANDING` = `GEN_ICACHE_NUM_FB *
IC_LINE_BEATS` (4 x 2) grants in flight. Hard rule (rtl-arch T-022 evidence 5.2): `rvalid` only for a
granted request, never in the grant cycle, never without an outstanding grant; the icache does not
defend against either, so a passing test never violates it (Q-010 default) and a TB self-check
asserts it. `rdata[38:32]` is the `prim_secded_inv_39_32` integrity of the word unless an injection
corrupts it; PMP-denied and speculative fetches are served like any other. Section C3.1.

**Data bus (`data_req_o/gnt_i/addr_o/we_o/be_o/wdata_o[38:0]/rvalid_i/rdata_i[38:0]/err_i`).** Same
handshake, at most `GEN_DBUS_MAX_OUTSTANDING` = 2 in flight (the LSU split rule); a misaligned access
appears as two word transactions and a PMP-denied half never reaches the bus while the permitted
half does (Q-008 default, BS MEM-13). Errors and integrity corruption are injected per response and
published with `injected = 1` so the checkers arm their expectations. Section C3.2.

**Memory model behind both buses.** One sparse word-addressed model loaded once at time 0 from the
program image (`.vmem` plus `.sym.json` sidecar, CRC-32 over (index, word) pairs verified by
`gen_mem_model::crc32_index_word()` and by a seeded MEM_PEEK read-back from Python); MMIO windows
for the riscv-dv signature, the interrupt acknowledge register, the end-of-test register and
`tohost`; every other change comes from bus stores. The boot entry (`{boot_addr[31:8], 8'h80}`) and
the debug ROM at `DmHaltAddr` are linked into the image, so the TB serves no stub. Section C3.3.

**Instruction-cache RAMs (`ic_tag_req_o/write_o/addr_o/wdata_o/rdata_i`, `ic_data_*`, per way).**
Synchronous RAM models as test equipment (`ICache=1`, `ICacheECC=1`, `ICacheScramble=1`): write
in the request cycle, read data the next cycle, ECC bits stored as written; ECC error injection
by flipping stored bits (`ICACHE_ECC_ARM`); initial contents random by default. Section C3.4.

**Scramble-key responder (`ic_scr_key_req_o` -> `ic_scr_key_valid_i`, `scramble_key_i`,
`scramble_nonce_i`).** `ic_scr_key_req_o` is a one-cycle pulse; the responder answers after a
randomized latency with a fresh key and nonce and drops `valid` per the request-response rule;
key modes (fixed, random, delayed) are a regime. Section C3.5.

**Interrupts (`irq_software_i`, `irq_timer_i`, `irq_external_i`, `irq_fast_i[14:0]`, `irq_nm_i`).**
Level pins; `mip` reads the raw pins (rtl-arch CTRL-08) and `irq_pending_o` is combinational
`|(pins & mie_q)`. The driver sets and clears pins on bridge commands (IRQ_SET, IRQ_CLR,
NMI_PULSE) and implements deassert policies (on the handler's MMIO acknowledge store, after a
count of cycles, or never for livelock tests) because software cannot clear `mip`. Section C3.6.

**Debug request (`debug_req_i`).** Level; asserted and released on bridge command (DBG_REQ); entry
lands in the image-linked debug ROM at `DmHaltAddr` 0x1A110800 (exception entry +8, ROM budget
0x800). Section C3.7.

**Static and slow controls.** `fetch_enable_i` (MuBi, FETCH_EN command, Q-009 default: RTL behaviour
as-is), `boot_addr_i` (must match the image entry page, checked at time 0), `hart_id_i`,
`ram_cfg_i`, `cheriot_enable_i` (tied Off), `test_en_i` (tied 0), `rst_ni` (reset sequence from
the TB top, ResetAll = 1). Sections C1 and C9.

**Observed outputs.** `alert_minor_o`, `alert_major_internal_o`, `alert_major_bus_o`, `crash_dump_o`,
`double_fault_seen_o`, `irq_pending_o`, `core_busy_o`, and the RVFI record (`rvfi_valid`, `rvfi_order`,
`rvfi_insn`, `rvfi_trap`, `rvfi_intr`, `rvfi_pc_*`, `rvfi_rs*/rd*`, `rvfi_mem_*`, the `rvfi_ext_*` fields
including `pre/post_mip` raw, `irq_valid`, `debug_mode`, `rf_wr_suppress`, `expanded_insn_*`). RVFI is a
define-gated DUT interface at the boundary (probe register ruling). Sections C4.1 to C4.7.

### 1.2 Internal probes

The probe register is `dv/auto_dv/docs/gen_probe_register.md` (v2, rulings recorded). The target
is zero checker probes and it is met: RVFI is classified as a boundary interface; P1 (dummy
instruction visibility) is accepted for coverage and the BUG-02 quantification reproducer only,
never as a checker input (`ctr_minstret` is a bound check while dummy instructions are enabled);
P2 and P3 rejected; P4 conditionally accepted for coverage only; P5 rejected; P6 debug-only,
default off, never in a measured regression. "No checker depends on any probe" (Section C8).

### 1.3 Constants centralized

One source per fact, three consumers: `gen_tb_pkg.sv` (SV constants and the derived `opentitan`
parameter set with `ifndef` defaults for the config macros), the codegen output
`gen_isa_shim_map.h` plus `gen_knobs.py` (memory map, `GEN_ISA_STRING`, knob names and defaults
generated from the same table), and the Python handles module `gen_handles.py` (hierarchical
paths of the bridge fields; nothing inside the DUT). The memory map has one origin
(`gen_link.ld` and the SV parameters `DmBaseAddr`, `DmAddrMask`, `GEN_BOOT_ADDR_DEFAULT`), which
`gen_program.py` already derives its Spike windows from. Section C11.

### 1.4 Simulation-only features via binds

`dv/auto_dv/tb/gen_binds.sv` is the single home for everything that attaches to the DUT without
editing it: error-injection binds on the bus interfaces, bound coverage modules, rtl-arch's cover
properties (`gen_cover_props_draft.sv`, `$error` collected, knob `+gen_chk_t022_never`), and the
protocol self-check `sva_rvalid_legal`. Mutation runs need an RTL-root/filelist override, relayed
to Runtime. Section C10.

## 2. Checking strategy

### 2.1 The ISA-model decision

Upstream Spike at the pinned commit 4ffd6ba860f4190ceac2716fa3c2cf139e85538f, built in
`tools/spike` (`dv/auto_dv/evidence/gen_t019_spike_build.md`), used as a step-locked library: one
`processor_t` without `sim_t` over the shim's own `simif_t`, stepped per RVFI record class from a
C++ DPI shim (`gen_isa_shim.cc`, `gen_isa_dpi.sv`). Feasibility is proven by two link tests
(`gen_t019_spike_build.md` Section 5; `dv/auto_dv/evidence/gen_t046_spike_linktest2.md`, 98/98).
Standalone `spike --log-commits` runs serve only bring-up and the per-program sanity check in
`gen_program.py`.

What it covers: architectural state per retired or trapping instruction: pc, instruction bits,
register write, memory access, privilege, next pc, CSR writes (rows `isa_pc`, `isa_insn`,
`isa_trap`, `isa_rd`, `isa_mem`, `isa_prv`, `isa_pc_next`, `isa_csr`, Section C4.7), with Ibex's
WARL and platform rules applied by the legalization layer: RTL-defined rows (C5.3a, the model
follows the RTL under the Q-006 and Q-008 defaults) and spec-violation rows (C5.3b: B1, B2/BUG-01,
BUG-03, B3, B5; the model follows the specification and the tests carry `expected_fail: true`
until the owner rules).

What it does not cover, and which own checker does (Section C4): interrupt pin to `irq_pending_o`
and entry latency (`irq_pending`, `irq_entry`), alerts and their timing (`alert_bus` split by
source, `alert_internal`, `alert_minor`, `icache_ecc`), bus protocol and outstanding rules
(`ibus_proto`, `ibus_outstanding`, `dbus_*`), PMP effects on the bus (`pmp_data`, `pmp_fetch`),
counters (`ctr_mcycle` windowed, `ctr_minstret` exact or bound, `ctr_hpm_*`), `crash_dump`,
`core_busy` (including the WAIT_SLEEP one-cycle dip), `double_fault_seen`, the internal NMI
(`nmi_internal`), the scramble-key handshake (`scrkey_*`), debug entry and ROM behaviour
(`dbg_*`), and the CSR observability plan (Section C6). Dummy instructions never reach RVFI and
leave residue only in the counters.

### 2.2 Passive by default, failure paths, exactness

Checkers observe monitors and never drive; every checker has an id, a disable knob
`+gen_chk_<id>=0` and an isolation mode (`+gen_chk_all=0 +gen_chk_<id>=1`), and every row names
the RTL locus and the mutation class that proves it (trust triad). TB self-checks
(`bridge_accounting`, `sva_rvalid_legal`) are listed but not counted as DUT checkers; agent-internal
consistency asserts (`ibus_order`, `dbus_queue`) have no row. Failure paths: SV raises `uvm_error`
(checker id, cycle, expected versus actual) or `uvm_fatal` for TB integrity events (`MEM_LOAD`,
`ISA_INIT`, `GEN_UNKNOWN_PLUSARG` at time 0, the alive watchdog `$fatal`); Python raises an `assert`
that fails the cocotb test; the regression script scans the log for these mechanisms (SIM_RECIPE
Section 5). Exactness classes (Section C4.8): `exact` per cycle or per record; `windowed(constant)`
around a `gen_tb_pkg` constant with a predicted value that bring-up confirms and a directed test
pins (`GEN_CSR_WRITE_TO_RVFI_OFFSET` = 2, `GEN_TRAP_TO_RVFI_OFFSET` = 1, `GEN_RVFI_ID_EXIT_OFFSET` = 2
plus the WB wait, `GEN_ICACHE_ECC_WINDOW`; `alert_bus` is exact for both sources after the RTL
fact-check, Section 6.13); `bound` (`GEN_IRQ_ENTRY_BOUND_RECORDS` = 17 worst case, `ctr_minstret`
with dummies on).

## 3. Language split (DV_prompt Section 9)

- **SystemVerilog / UVM** owns everything that needs cycle fidelity: the interface agents (drivers,
  monitors, sequencers), the memory and RAM models, the scoreboard and checkers, the covergroups
  and the binds. Per-transaction randomization (layer 1: grant and response latencies, error and
  integrity decisions inside a regime) is drawn in SV because each draw is a per-cycle decision that
  Python could not make without polling; the regime that bounds the draws is Python's choice.
- **Python / cocotb** owns test orchestration: the test class, program selection and seeding,
  regime selection and scheduling (layers 2 and 3), the bridge commands, the end-of-test verdict
  and the report. It never touches a DUT signal; `gen_handles.py` exposes only bridge fields.
- **C++** owns the Spike shim behind DPI-C (library API, own `.so` with its own flags, loaded via
  `-LDFLAGS`; C++20 headers from `tools/spike/include` only).
- **The bridge** (Section C2) is a small register block in the TB top: Python writes a command
  (`cmd_kind`, `cmd_arg[3:0]`, `cmd_seq`) and toggles `cmd_valid`; SV acks by an edge the next
  cycle; events (`evt_thresh_hit`, `evt_irq_taken`, `evt_dbg_entered`, `evt_eot_seen`) are single-bit
  toggles Python awaits by edge; thresholds are written (`evt_retired_target`, `evt_cycle_target`)
  and the counts are read once at finish. **No per-cycle Python polling exists anywhere in the TB**
  (Critic A-01); MEM_PEEK is the only data-return command (image read-back).

## 4. Stimulus architecture

### 4.1 Program generation path

`dv/auto_dv/stim/gen_program.py` is the single driver for one (test, seed): it materializes the
riscv-dv target (`gen_riscv_dv_target/`, `gen_`-prefixed sources copied to the tool-mandated fixed
names out of tree, Q-013 default) into a private per-run directory, runs the compiled generator
with the run seed and cross-checks riscv-dv's `seed.yaml`, or takes a directed program
(`gen_directed/*.S`, Zc encodings via the `.2byte` macros of `gen_zc_insn.h` because binutils 2.35
lacks Zcb/Zcmp), assembles with the lowRISC gcc 10.2 `-march=rv32imcb` toolchain (`ci/env.sh`),
relocates the debug ROM into `.debug_rom` at `DmHaltAddr` (`gen_relocate_debug_rom.py`, budget
checked), links with `gen_link.ld` (`-Wl,-N`, `.gen_boot` entry at boot + 0x80), converts to the
image (`gen_elf2mem.py`: word-addressed `.vmem`, `.sym.json` with entry, segments, symbols,
CRC-32, seed, memory map, ROM size), and sanity-runs the ELF on standalone Spike with
`GEN_ISA_STRING` and memory windows derived from the SV parameters. Evidence:
`dv/auto_dv/evidence/gen_t023_stimulus_toolchain.md`, `gen_t025_stim_tooling.md`.

### 4.2 Three randomization layers and the one-seed rule

1. **Layer 1, SV per transaction**: latencies, error and integrity decisions, key delays, drawn from
   the active regime's distributions by each agent's driver (constraints in `gen_<agent>_item`).
2. **Layer 2, Python per test**: the regime per agent (`+gen_<agent>_regime=<name>`, pinnable with
   `+gen_regime_pin`), the program and its knobs, the interrupt and debug scenario.
3. **Layer 3, Python schedule**: regime changes at retirement or cycle thresholds
   (`+gen_regime_sched=<agent>:<regime>@r<N>|c<N>,...`), derived from the seed and echoed in the
   banner, or consumed as input when supplied on the command line so a specific schedule is
   reproducible; each trigger is one written threshold and one awaited `evt_thresh_hit` edge.

One seed drives everything: `+ntb_random_seed` (SV), `RANDOM_SEED` (Python) and the program seed
are the same value, recorded in the log and in the image sidecar (`seed_used`), so every failure
reproduces from test name plus seed (SIM_RECIPE Section 5). Section C9.

## 5. Coverage architecture

- **Code coverage scope (`-cm_hier`)**: the tree under `gen_tb_top.<dut instance>` so TB and test
  equipment stay out of the numbers. DV Lead ruling P-04/A-21 (run scope, 2026-09-03 07:04 UTC): the measured code-coverage scope is the
  two instances inside the wrapper, `gen_tb_top.u_dut.u_ibex_core` and `gen_tb_top.u_dut.u_register_file`
  (two `+tree` lines in `gen_cm_hier.cfg`). Reason: `gen_dut_top` is DV-authored pure wiring whose every
  coverage object duplicates an `ibex_core` port (312 of 2420 wrapper toggle objects, about 9 percent of
  the toggle denominator); counting them would either inflate the denominator with duplicates or force
  about 312 exclusions of ports that carry control (req, gnt, irq, debug_req) and therefore cannot be
  justified as data-path exclusions under DV_prompt Section 4. The DV_prompt Section 2 ruling fixes the
  wrapper as the DUT boundary for stimulus and checking, which is unchanged; the RTL under test is
  exactly `ibex_core` plus `ibex_register_file_ff`, so the two-instance scope measures the whole DUT
  logic and nothing else. The wrapper's own objects are reported informationally (a third `+tree` in a
  separate, non-gated report) so a wiring defect stays visible. Runtime applies this as the single
  `cov_trees` source; the coverage plan (gen_fcov_plan.md Section 0) references this ruling. Both candidate scopes differ only by wrapper wiring (C7).
- **Glitch and metric flags (`-cm_glitch`, condition coverage)**: DV Lead ruling LOG-007/008 (2026-09-03 07:04 UTC): every
  measured build uses `-cm_glitch 0`. Reason: the same-seed control (rtl-arch-002) showed the
  numerator drop of the trial (LINE 55.09 to 38.93, COND 37.41 to 26.63, BRANCH 41.03 to 33.00 on the
  NOP smoke) is the glitch filter removing zero-time hits, not a seed effect; hits recorded only through
  zero-time glitch events are not exercised logic (DV_prompt Section 10 honesty), and the flag removes
  every coverage-status-mismatch warning from the URG merge. Consequences: Runtime makes it the default
  in `gen_flow_const.py`; the round-0 baseline is re-measured under the flag so round-over-round gains
  compare like with like; every URG report header states `-cm_glitch 0`; FSM coverage is not
  glitch-filtered (VCS warning VCM-OPTIGN) and is recorded as such in the closure report. Condition
  coverage (`cond`) is a gated metric and is included in the measured `-cm` set (Runtime T-010 proved
  it). Compile and run flags otherwise per SIM_RECIPE Section 3 (`line+tgl+assert+fsm+branch`,
  `-cm_name test_<test>_<seed>` per run).
- **Covergroup namespace**: every group is `gen_<feature>_cg` in `gen_fcov_pkg.sv`, class-based and
  sampled by the scoreboard and monitors on named events (`gen_smp_<name>`), never on a free-running
  clock; bound signal-level coverage modules live in `gen_*_cov.sv` via `gen_binds.sv`; bin ranges
  derive from `ibex_pkg` parameters; `gen_regime_cg` covers layer 3; `gen_csr_cg` carries the CSR
  observability bins (C6, C7). No RTL covergroups exist to collide with.
- **fcov-expectation duty**: each test declares the bins it intends to hit in
  `dv/auto_dv/fcov_expectations/<test>.fcov.yaml`; `ci/check_fcov_expectations.py --vdb <vdb>
  --cm-name test_<test>_<seed>` fails the run on declared-but-unhit bins; Runtime wires the check
  into the regression flow (T-045).
- **Reporting**: URG merge per SIM_RECIPE Section 8; `dashboard.txt` is the number.

## 6. Component API sections (TB Infra, v2, included verbatim)

The text below is `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` (version 2) in
full; only the heading depth is shifted by one level to nest under this section. Per-finding
dispositions of the Critic's review and the cross-model review are in
`dv/auto_dv/work/tb-infra/gen_critic_response_tb_arch_v1.md`.

### 6.0 Embedded document: TB architecture component sections (tb-infra, T-018), version 2

Version 2, 2026-09-03: revised after the Critic's REQUEST-CHANGES
(`dv/auto_dv/work/critic/gen_critic_tb_arch_components_v1.md`, A-01..A-25 and the C8 rulings), the
cross-model pre-execution review (`dv/auto_dv/reviews/2026-09-03-claude-plan-gen_tb_arch_component_
sections.md`, five mediums and the lows, marked "(v2, XM-n)") and rtl-arch's T-022 inputs
(`gen_cover_props_draft.sv`, `gen_unreachability_evidence.md` 5.2). The per-finding disposition of
both reviews is `dv/auto_dv/work/tb-infra/gen_critic_response_tb_arch_v1.md`. Changes against v1
are marked "(v2)" in the text.

For the DV Lead to fold into `dv/auto_dv/docs/gen_tb_architecture.md` (DV Lead owns the document;
tb-infra owns these sections). Written for the Critic and the cross-model reviewer to judge
feasibility: interfaces, timing, failure paths. Sources: `dv/auto_dv/work/rtl-arch/
gen_answers_tb_infra.md` (AN), `gen_interface_inventory.md` (II), `gen_behaviour_summaries.md`
(BS), `gen_rv32b_otearlgrey_encodings.md` (ENC); `dv/auto_dv/work/dv-lead/gen_reading_report.md`
Section 7 (RR); `dv/auto_dv/work/tb-infra/gen_tb_scoping_notes.md` (SN, with the T-014
corrections folded in); as-built wrapper `dv/auto_dv/tb/gen_dut_top.sv` and
`dv/auto_dv/docs/gen_component_api_dut_top.md`. Build configuration: `opentitan`. ASCII only.
UNVERIFIED marks a claim from RTL or tool-source reading that bring-up must confirm.

Conventions used by every component below:

- Names: SV components `gen_<name>` in package `gen_env_pkg` (UVM), interfaces `gen_<name>_if`,
  covergroups `gen_<feature>_cg` in `gen_fcov_pkg`, binds in `gen_binds.sv`, constants in
  `gen_tb_pkg`. Python: `gen_tb/` package (`gen_handles.py`, `gen_knobs.py` generated,
  `gen_bridge.py`, tests under `gen_tests/`).
- Knobs: every runtime knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg`
  (`PLUSARG_*`) and a generated Python constant of the same value; the env reads each once at
  build time into a config object placed in `uvm_config_db`. Checker knobs are
  `+gen_chk_<id>=0|1` (default 1). Debug prints gate behind `+gen_dbg_<component>=1`.
- Failure path: checkers fail with `uvm_error` (id = the checker id below) and the env's
  `report_server` counts them; a protocol state that makes further checking meaningless fails
  with `uvm_fatal`; Python-side checks are `assert`s in the cocotb test. The regression script
  decides pass/fail from the UVM error/fatal counts and the cocotb result, never from the exit
  code (SIM_RECIPE Section 5). Every failure message carries the checker id, the cycle, and
  expected-versus-actual, nothing else.
- Mutation evidence (DV_prompt Section 8): each checker row names the mutation classes it is
  meant to catch with an example RTL locus; the Test Writer picks one mutation per checker,
  disables every other check (`+gen_chk_all=0 +gen_chk_<id>=1` is supported: `gen_chk_all` is the
  master, the per-id knob re-enables one), shows the named id in the log, and runs the ablation
  (`+gen_chk_<id>=0`, mutation survives).
- "Cycle" means posedge `clk_i`; all DUT flops are async-reset on `rst_ni`.
- (v2, A-02) Every Python-side string that may be logged or raised (cocotb test, bridge, handles,
  regimes) is pure ASCII; the gen_tests template enforces it with a unit check, because a non-ASCII
  character in a failure message crashes cocotb's log path (TB_CONTRACT Section 4).
- (v2, A-23) An unknown `+gen_*` plusarg on the command line is a `uvm_fatal GEN_UNKNOWN_PLUSARG`
  at time 0 (a mistyped regime pin or checker knob must fail the run, not silently run defaults).
- (v2, A-13, XM-L3) TB self-checks (`bridge_accounting`, `sva_rvalid_legal`) are listed with their
  components for completeness but are NOT counted as DUT checkers in the trust-triad evidence
  table; their mutation column says "TB self-check". Purely internal consistency assertions of a
  driver (`ibus_order`, `dbus_queue`) are agent-internal `assert`s without a checker row or knob.
- (v2, A-09) Every checker states its exactness class: `exact` (compared every cycle or per record
  with no tolerance), `windowed(<constant>)` (compared after a pipeline offset or inside a window
  named by a `gen_tb_pkg` constant that bring-up measures and a directed test pins), or `bound`
  (monotonic and within limits). The classes and constants are collected in C4.8.

Proposed section headings (numbering left to the DV Lead): C1 DUT wrapper as built; C2 TB top,
language split and the cocotb/UVM bridge; C3 interface agents and test-equipment models; C4
monitors and checkers; C5 ISA-model integration, shim and comparator policy; C6 CSR observability
plan; C7 covergroup implementation strategy; C8 probe register candidates; C9 environment
configuration, knobs and regimes; C10 binds home; C11 constants home and Python handles module.

### C1. DUT wrapper gen_dut_top as built (RR ask 1)

Compiled, elaborated and smoke-run 2026-09-03 (evidence `dv/auto_dv/evidence/
gen_t005_compile_log_excerpt.md`; commit accepted; diff review APPROVE).

| Parameter | Value (opentitan) | How it is set |
|---|---|---|
| BaseIsa | BaseIsaRV32IorCHERIoT | `+define+BaseIsa` (enum) via the wrapper's macro default |
| RV32M / RV32B / RV32ZC / RegFile | RV32MSingleCycle / RV32BOTEarlGrey / RV32ZcaZcbZcmp / RegFileFF | `+define+` (enum) via macro defaults |
| RV32E, BranchTargetALU, WritebackStage, ICache, ICacheECC, BranchPredictor, DbgTriggerEn, SecureIbex, PMPEnable | 0, 1, 1, 1, 1, 0, 1, 1, 1 | `-pvalue+` on the TB top, forwarded |
| PMPGranularity, PMPNumRegions, MHPMCounterNum, MHPMCounterWidth | 0, 16, 10, 32 | `-pvalue+`, forwarded |
| ICacheScramble | 1 | `-pvalue+`, accepted, forwarded nowhere (not an ibex_core parameter) |
| RegFileECC | 0 | wrapper parameter (Q-DL-1 default: ibex_top main core) |
| ResetAll | SecureIbex = 1 | wrapper parameter (Q-DL-1 default) |
| MemECC / MemDataWidth | 1 / 39 | derived `= SecureIbex`, `MemECC ? 39 : 32` |
| DummyInstructions, ICacheTweakInfection | 1, 1 | derived `= SecureIbex` |
| BusSizeECC / LineSizeECC / TagSizeECC | 39 / 78 / 28 | derived with ibex_top's ICacheECC conditionals |
| RegFileDataWidth / RegFileCapEccWidth | 32 / 35 | derived from RegFileECC |
| DbgHwBreakNum | 1 | wrapper parameter, ibex_core default |
| DmBaseAddr / DmAddrMask / DmHaltAddr / DmExceptionAddr | 0x1A110000 / 0x00000FFF / 0x1A110800 / 0x1A110808 | wrapper parameters, ibex_core defaults |
| RndCnstLfsrSeed / RndCnstLfsrPerm | ibex_pkg defaults | wrapper parameters |
| CsrMvendorId / CsrMimpId | 0 / 0 | wrapper parameters |
| PMPRstCfg / PMPRstAddr / PMPRstMsecCfg | ibex_pkg reset values (all OFF / 0) | ibex_core defaults, not exposed |
| RVFI | on | `+define+RVFI` in the compile command (Q-DL-1 default) |
| GEN_DUT_SPLIT_INTG | off | compile define; off = ports literal to the ruling (39-bit, integrity in [38:32]) |

Tie list inside the wrapper: `cheriot_enable_i = IbexMuBiOff` on the core and the register file;
register-file `test_en_i = 1'b0` (unused by the FF file). Not present (ibex_top / ibex_top_tracing
ports only): `scan_rst_ni`, `ram_cfg_icache_*`, `scramble_key_i/nonce_i/req_o`, `trvk_*`,
`core_sleep_o`, lockstep/shadow outputs. Exposed cap residue because ibex_core has it: `data_tag_o`
(constant 0 with the tie, AN s2), `data_tag_i` (TB drives 0), RVFI `*_rcap` / `rvfi_mem_is_cap`
(constant NULL_CAP / 0). The register-file cap seam is internal. TB-side static inputs: `hart_id_i`
(knob, default 0), `boot_addr_i` (knob, default 0x8000_0000, low byte 0), `fetch_enable_i`
(knob/driver, default IbexMuBiOn), `mcounteren_writable_i` (knob, default IbexMuBiOn; RR candidate
Q4), `ic_scr_key_valid_i` (responder), `debug_req_i`, `irq_*` (drivers). Instance names for
`-cm_hier`: `u_ibex_core`, `u_register_file`.

### C2. TB top, language split and the cocotb/UVM bridge

`gen_tb_top` (SV, the VCS `-top` and cocotb `TOPLEVEL`) declares the 19 config parameters and
forwards them to `gen_dut_top u_dut`; instantiates the clock/reset generator, the six interface
instances (`gen_ibus_if`, `gen_dbus_if`, `gen_icram_if`, `gen_scrkey_if`, `gen_irq_if`,
`gen_dbg_if`), the RVFI interface `gen_rvfi_if` (bundle of the wrapper's rvfi_* ports), the
misc-outputs interface `gen_misc_if` (alerts, crash_dump, double_fault, irq_pending, core_busy,
data_tag_o), and `gen_bridge_if`; puts every virtual interface into `uvm_config_db`; calls
`run_test()` with the single UVM test `gen_base_test` (tests differ by Python, not by UVM test
class, DV_prompt Section 9). Time-0: the wrapper's config banner plus the TB's own banner (seed
from `+ntb_random_seed`, `RANDOM_SEED` echoed by Python, regime schedule string).

Language split: programs (riscv-dv output or directed assembly/C compiled with `$RISCV_GCC`) and
run-time stimulus decisions are Python/C; agents, monitors, scoreboard, shim and covergroups are
SV/UVM/C++. Per-transaction randomization inside agents (layer 1) is constrained-random SV under
knob control and needs no recompile for a new test, which is the Section 9 reason; documented as
compliant, not a deviation.

Bridge (`gen_bridge_if`, SV interface; `gen_bridge` UVM component; `gen_tb/gen_bridge.py`):

| Field | Dir (Python view) | Semantics |
|---|---|---|
| `alive` | write once | set first; SV `initial` `$fatal`s if still 0 after `GEN_ALIVE_TIMEOUT_CYCLES` (TB_CONTRACT Section 2) |
| `stim_active` | write | objection holder: 1 while Python may still issue commands or checks |
| `cmd_valid`, `cmd_kind[7:0]`, `cmd_arg[3:0][31:0]`, `cmd_seq[15:0]` | write | one command per rising edge of `cmd_valid`; kinds: IRQ_SET, IRQ_CLR, NMI_PULSE, DBG_REQ, REGIME_SET, KEY_MODE, MEM_ERR_ARM, ICACHE_ECC_ARM, FETCH_EN, MEM_PEEK (v2, XM-M4: `cmd_arg[0]` = word address; the memory model's word is returned in `peek_data` with the ack), MISC |
| `peek_data[31:0]` | read after `cmd_ack` | (v2, XM-M4) the word read by the last MEM_PEEK |
| `cmd_ack`, `cmd_ack_seq[15:0]` | read (edge-awaited) | SV toggles `cmd_ack` after the sequence item is queued; Python awaits `RisingEdge`/`FallingEdge`, never polls |
| `listener_armed` | read | Python awaits it before the first command (TB_CONTRACT Section 5) |
| `cmds_consumed[15:0]` | read | compared with Python's sent count before finish |
| `evt_retired_target[31:0]`, `evt_cycle_target[31:0]` | write | (v2, A-01) thresholds: Python writes a retirement count or a cycle count it wants to be woken at |
| `evt_thresh_hit` | read (edge-awaited) | (v2, A-01) single-bit toggle raised by SV when `retired_count >= evt_retired_target` or `cycle >= evt_cycle_target`; Python awaits this ONE edge per threshold, never a counter |
| `evt_irq_taken`, `evt_dbg_entered`, `evt_eot_seen` | read (edge-awaited) | single-bit toggles raised by monitors on the named event |
| `evt_retired_count[31:0]`, `evt_err_count[15:0]` | read at finish only | values Python reads once for its end-of-test report; never awaited or polled |
| `finish_req`, `finish_ack` | write / read | end-of-test handshake with a caller-sized timeout |

Wave-level: `cmd_valid` is a level toggled by Python; the SV `always @(posedge cmd_valid)` block
captures `cmd_kind/arg/seq` in that delta and hands a `gen_cmd_item` to the addressed sequencer
through `uvm_config_db` handles; `cmd_ack` toggles in the next cycle. Two commands need two edges;
Python waits for the ack of one before raising the next. No signal in the bridge is a DUT signal.
(v2, A-01) Per-cycle Python polling exists nowhere in the TB: every wait on the Python side is a
cocotb edge trigger on a single-bit SV event (`cmd_ack`, `evt_thresh_hit`, `evt_irq_taken`,
`evt_dbg_entered`, `evt_eot_seen`, `finish_ack`, `listener_armed`), and the SV side evaluates the
thresholds. No polling waiver is requested.

### C3. Interface agents and test-equipment models

#### C3.1 gen_ibus_agent (instruction memory agent)

Purpose: the only driver of `instr_gnt_i`, `instr_rvalid_i`, `instr_rdata_i[38:0]`,
`instr_err_i`; a reactive slave serving the shared memory model. API: UVM agent
(`gen_ibus_agent`: `gen_ibus_driver`, `gen_ibus_monitor`, `gen_ibus_sequencer` for regime and
error-arm items, analysis port `ap` of `gen_bus_txn` {kind=FETCH, addr, data, intg, err,
gnt_delay, rvalid_delay, cycle_req, cycle_gnt, cycle_rvalid, outstanding_at_gnt, injected}).
Config object `gen_ibus_cfg` (also settable by REGIME_SET through the bridge).

| Knob (plusarg) | Meaning | Default |
|---|---|---|
| `+gen_ibus_gnt_min/max` | grant latency window in cycles (0 = same cycle) | 0 / 3 |
| `+gen_ibus_rvalid_min/max` | response latency after grant; hard floor 1 | 1 / 4 |
| `+gen_ibus_max_outstanding` | accepted grants in flight before withholding gnt; hard cap `GEN_IBUS_MAX_OUTSTANDING` (v2, A-04: `gen_tb_pkg` constant `= GEN_ICACHE_NUM_FB * ibex_pkg::IC_LINE_BEATS`, where `GEN_ICACHE_NUM_FB = 4` is the one unavoidable re-type of the icache localparam `NUM_FB`, rtl/ibex_icache.sv:72, cited there) | GEN_IBUS_MAX_OUTSTANDING |
| `+gen_ibus_err_rate` | per-transaction probability (per mille) of `instr_err_i` | 0 |
| `+gen_ibus_err_window=lo:hi` | address window where errors apply (any if unset) | unset |
| `+gen_ibus_intg_err_rate`, `+gen_ibus_intg_bits=1|2` | integrity corruption probability and flip count | 0 / 1 |
| `+gen_ibus_regime` | named distribution set: fast, slow, bursty, stall, err_heavy, intg_err | fast |
| `+gen_chk_ibus_proto`, `+gen_chk_ibus_outstanding`, `+gen_chk_bus_rvalid_legal` | checker enables | 1 |

Wave-level behaviour: `gnt` is combinational from `req` when the chosen delay is 0 (legal, LSU doc
89) or a flop-driven pulse otherwise; the driver never asserts `gnt` without `req` (BS MEM-17).
Each grant pushes {addr, delay, error/intg decision} into an in-order queue of depth
`GEN_IBUS_MAX_OUTSTANDING` (BS MEM-18); a response is popped after its latency and driven for
exactly one cycle from flops (`rvalid`, `rdata`, `err` registered; AN s5). (v2, rtl-arch T-022
evidence 5.2) Hard stimulus rule of both memory agents: `rvalid` is driven ONLY for a granted
request, never in the grant cycle and never without an outstanding grant; the icache does not
defend against either (rtl/ibex_icache.sv:851) and a sloppy model would corrupt its fill
bookkeeping silently. The rule is enforced by construction (minimum latency 1, response queue) and
asserted on the TB side by `sva_rvalid_legal` (a stimulus-legality self-check, C10). `rdata[31:0]`
= memory word, `rdata[38:32]` = `prim_secded_inv_39_32_enc` of it (vendor primitive as test
equipment) unless corrupted. PMP-denied fetches DO appear on this bus and are served normally
(BS MEM-16). Speculative fetches are served like any other; the agent does not know what the core
will execute.

| Checker id | Rule | Mutation classes (example locus) | Knob |
|---|---|---|---|
| `ibus_proto` | `req & ~gnt` => `req` and `addr` unchanged next cycle; `addr[1:0] == 0`; no `req` X | icache request hold / arbitration (`rtl/ibex_icache.sv:756-775, 842`), address mux (`:1030-1037`) | `+gen_chk_ibus_proto` |
| (agent-internal) `ibus_order` | (v2, XM-L3) responses consumed in grant order: an agent-internal `assert` inside gen_ibus_driver, not a checker row; no `+gen_chk_` knob and no trust-triad entry | TB self-check | none |
| `ibus_outstanding` | granted-unanswered `<= GEN_IBUS_MAX_OUTSTANDING`, and `core_busy_o != Off` while > 0 (exact) | fill-buffer counters (`rtl/ibex_icache.sv:759-784`), `busy_o` (`:1304`) | `+gen_chk_ibus_outstanding` |
| `sva_rvalid_legal` | (v2) TB stimulus legality: `instr_rvalid_i`/`data_rvalid_i` only while a grant is outstanding and never in the grant cycle | TB self-check (not a DUT checker) | `+gen_chk_bus_rvalid_legal` |

#### C3.2 gen_dbus_agent (data memory agent)

Purpose: driver of `data_gnt_i`, `data_rvalid_i`, `data_rdata_i[38:0]`, `data_err_i`; consumer of
`data_req_o/we/be/addr/wdata[38:0]/tag_o`; performs stores into the memory model (enabled lanes
only, BS MEM-08), serves loads, sinks MMIO windows (C3.3). Same structure and knob set as C3.1
with prefix `gen_dbus_`, plus:

| Knob | Meaning | Default |
|---|---|---|
| `+gen_dbus_max_outstanding` | hard cap `GEN_DBUS_MAX_OUTSTANDING` (v2, A-04: `gen_tb_pkg` constant = 2, the two halves of one split access per the LSU split rule rtl/ibex_load_store_unit.sv:403-405 and rtl/ibex_top.sv:229-233; cited there) | GEN_DBUS_MAX_OUTSTANDING |
| `+gen_dbus_err_half=first|second|both|any` | for split accesses, which half an injected error hits | any |
| `+gen_dbus_err_store_perform=0|1` | whether an errored store still updates the memory model (default: yes, the memory received it; the DUT ignores nothing on stores) | 1 |
| `+gen_dbus_regime` | fast, slow, bursty, stall, err_heavy, intg_err, mis_err_first, mis_err_second | fast |

Wave-level behaviour: as C3.1; response registers only, because the LSU may issue the next request
in the response cycle (AN s5). For an errored response `rdata` is still integrity-valid unless an
integrity error is also injected. For stores the agent returns a constant integrity-valid word
(the core checks store response integrity too, LSU doc 64-66). Every injected error (bus or
integrity) is published on `ap` with `injected = 1` so the scoreboard can arm the ISA model
(C5) and the NMI/alert checkers (C4). MMIO windows never return an error unless a directed test
arms one.

| Checker id | Rule | Mutation classes (locus) | Knob |
|---|---|---|---|
| `dbus_proto` | `req & ~gnt` => `req`, `addr`, `we`, `be`, `wdata[38:0]` unchanged next cycle (BS MEM-06); `addr[1:0]==0`; `data_tag_o == 0` | LSU output muxes (`rtl/ibex_load_store_unit.sv:719-724`), addr_last update (`:254-266`) | `+gen_chk_dbus_proto` |
| `dbus_outstanding` | granted-unanswered `<= GEN_DBUS_MAX_OUTSTANDING`; 2 only when the two halves of one split access (exact) | LSU FSM (`:431-600`) | `+gen_chk_dbus_outstanding` |
| `dbus_split` | split predicate `(word & off!=0) | (half & off==3)`; second address = first word + 4; be/lane table of BS MEM-08; second half issued after a first-half error (BS MEM-10) | split logic (`:403-405`), be generation (`:138-191`), wdata rotation (`:199-208`), WAIT_RVALID_MIS path (`:503-531`) | `+gen_chk_dbus_split` |
| `dbus_store_intg` | STORES only (`req & gnt & we`): `wdata[38:32]` decodes with zero syndrome over the full 32-bit rotated word including disabled lanes (BS MEM-08/15); on LOADS `wdata` is architecturally don't-care (F-DMEM-035) and is never an error: the checker is X-tolerant there and only records whether the RTL-defined always-valid encoding (BS MEM-15) held, as a coverage observation `gen_dbus_cg.cp_load_wdata_intg_valid` | encoder wiring (`rtl/ibex_load_store_unit.sv:731-735`) | `+gen_chk_dbus_store_intg` |

#### C3.3 gen_mem_model (shared memory, MMIO windows, image load)

Purpose: one sparse word-addressed memory behind both agents, test-equipment only. API: SV class
`gen_mem_model` with `load_vmem(path)`, `read32/write_masked(addr, data, be)`, `checksum()`,
`add_mmio(window, handler)`; handlers for the signature sink, the interrupt-ack register and the
end-of-test register. Image format (defined by `dv/auto_dv/stim/gen_elf2mem.py`, proven in
T-023): a word-addressed `$readmemh` file with `@<word index>` runs plus a `.sym.json` sidecar
(entry, segments, global symbols, checksum = CRC-32 over (word index, word) pairs plus the word
count, v2 XM-M3). The image
already holds everything at its final address: the `.gen_boot` entry (`j _start`) linked at
`{boot_addr[31:8], 8'h80}` and made the ELF entry point, and the `.debug_rom` section linked at
`DmHaltAddr` (exception entry at +8), both by `dv/auto_dv/stim/gen_riscv_dv_target/gen_link.ld`;
the memory model therefore needs neither a boot stub nor a `DmHaltAddr` alias. Knobs:
`+gen_mem_image=<vmem>`, `+gen_mem_image_crc32=<hex>`, `+gen_mem_image_words=<n>` (from the
sidecar; the SV model recomputes the CRC-32 over (index, word) pairs after `$readmemh`; mismatch =
`uvm_fatal MEM_LOAD`), `+gen_boot_addr` (must match the image's entry page), `+gen_sig_addr`,
`+gen_irq_ack_addr`, `+gen_eot_addr`. The SV digest routine is `gen_mem_model::crc32_index_word()`:
IEEE CRC-32 (zlib polynomial, init 0xFFFFFFFF, final XOR) over the loaded words in ascending index
order, each fed as 8 little-endian bytes (index, word), exactly `gen_elf2mem.checksum()` (v2, XM-M3).
Backdoor rule (v2, A-07, XM-M4): the image load is the only backdoor write and is verified twice:
(1) the SV digest above (`uvm_fatal MEM_LOAD` on mismatch); (2) a read-back through the bridge, not
through VPI (an SV class associative array is not VPI-visible): Python issues `MEM_PEEK` commands
for `GEN_MEM_READBACK_WORDS` (default 64) word addresses drawn from the image's index set with the
run seed, SV answers each in `peek_data[31:0]` with the `cmd_ack` edge, and Python compares against
the `.vmem` it parsed from the same file; any mismatch is a Python `assert` that fails the cocotb
test. `gen_handles.py`'s "memory-sample handles" are these bridge fields, nothing inside the model.
All other memory changes come from bus stores.
Wave-level: none (pure model); reads/writes complete in the agent's response flop.
Failure path: `uvm_fatal` on image/checksum mismatch or a write to an unmapped MMIO window;
`uvm_error MEM_UNMAPPED` on a bus access outside every mapped region unless a test arms
`+gen_mem_unmapped_ok=1` (then the agent returns an error response, which is how bus-error
stimulus by address works).

#### C3.4 gen_icache_ram_model (tag and data RAM models) and ECC injection

Purpose: transparent synchronous single-port RAMs for the core's `ic_tag_*` / `ic_data_*` ports,
one instance per way, with fault injection and RAM-side checks. API: SV module `gen_icache_ram`
parameterised by `Width`, `Depth = IC_NUM_LINES`; ports as the core's per-way slice; injection
through a class handle `gen_icache_ram_ctl` in `uvm_config_db` (`arm(way, index, kind =
TAG|DATA, bits = 1|2, when = NEXT_LOOKUP|INDEX_MATCH)`, driven by the bridge command
ICACHE_ECC_ARM). Knobs: `+gen_icram_init=zero|random`, default `random` (v2, A-05: random
contents are the realistic and sensitizing case; the core's reset invalidation sweep makes them
irrelevant for tags, and data of never-hit lines is never consumed; `zero` only for a directed
bring-up), `+gen_icram_ecc_rate` (per-lookup probability per regime), `+gen_chk_icram_*`.
Wave-level behaviour: read data valid the cycle after `req & ~write` and held until the next read
(registered read, exactly `prim_ram_1p`; the core samples in IC1, AN s9); writes on `req & write`
take effect at the same edge; the invalidation sweep (256 tag writes after reset and after each
fence.i, plus data writes of encoded zeros when a lookup coincides) is accepted silently (II s5).
Injection flips the chosen bits in the read data of the chosen way at the chosen lookup; the core
must then miss, refetch, write the line invalid and pulse `alert_minor_o` (BS: icache ECC
handling, `rtl/ibex_icache.sv:585-644`).

| Checker id | Rule | Mutation classes (locus) | Knob |
|---|---|---|---|
| `icram_write_ecc` | every written tag/data word, un-tweaked with the model's copy of the address-derived tweak (AN s9), decodes with zero syndrome | tag/data encoders and tweak application (`rtl/ibex_icache.sv:290-310, 321-454`) | `+gen_chk_icram_write_ecc` |
| `icram_inval_sweep` | after reset release and after every retired fence.i (RVFI), all 256 tag indices of every way are written invalid before any allocation write | invalidation FSM (`:1204-1268`) | `+gen_chk_icram_inval_sweep` |
| `icram_ecc_response` | an injected error at (way, index) is followed within `GEN_ICACHE_ECC_WINDOW` cycles by exactly one `alert_minor_o` pulse and an invalidation write to that index; a miss fill follows | ECC check and correction-write path (`:538-644`), `alert_minor_o` (`rtl/ibex_core.sv:1337`) | `+gen_chk_icram_ecc_response` |

#### C3.5 gen_scrkey_responder (scramble-key handshake)

Purpose: answers `ic_scr_key_req_o` pulses on `ic_scr_key_valid_i`. API: UVM driver on
`gen_scrkey_if` with sequence items {delay_cycles, reset_valid}; bridge command KEY_MODE.
Knobs: `+gen_key_reset_valid=0|1` (default 1, ibex_top behaviour), `+gen_key_delay_min/max`
(default 1/20), `+gen_key_regime=immediate|short|long|never_window`, `+gen_key_never_cycles`.
Wave-level: on the one-cycle `req` pulse (II s5), drop `valid` the next cycle, hold low for the
drawn delay, raise and hold until the next pulse; with `reset_valid = 0` the core requests out of
reset. During `AWAIT_SCRAMBLE_KEY` fence.i produces no new pulse (AN s9), so the responder never
sees back-to-back pulses.

| Checker id | Rule | Mutation classes (locus) | Knob |
|---|---|---|---|
| `scrkey_proto` | `req` is a single-cycle pulse; no `req` while a request is pending and `valid` is still 0; software-visible `cpuctrlsts.ic_scr_key_valid` (via RVFI CSR reads and `rvfi_ext_ic_scr_key_valid`) equals the pin registered by one cycle | inval FSM request logic (`rtl/ibex_icache.sv:1220-1264`), cs_registers key-valid flop (`rtl/ibex_cs_registers.sv:1938-1949`) | `+gen_chk_scrkey_proto` |

#### C3.6 gen_irq_agent (interrupt driver)

Purpose: drives `irq_software_i`, `irq_timer_i`, `irq_external_i`, `irq_fast_i[14:0]`,
`irq_nm_i` as levels. API: UVM agent on `gen_irq_if`; sequence item `gen_irq_item` {line mask
(`$bits(ibex_pkg::irqs_t)` bits: the 15 fast lines plus ext, sw, timer, v2 A-04), nmi, assert_delay, hold_policy = CYCLES(n) | UNTIL_ACK |
UNTIL_TAKEN | STICKY, release_delay}; bridge commands IRQ_SET/IRQ_CLR/NMI_PULSE. Knobs:
`+gen_irq_regime=quiet|sparse|storm|nested|nmi_mix`, `+gen_irq_min_gap`, `+gen_irq_hold_min/max`,
`+gen_irq_ack_addr` (shared with C3.3). Wave-level: lines change on the clock edge after the
command; UNTIL_ACK releases the line on the cycle after the handler's store to the ack register
(riscv-dv handler tail through our user-extension `gen_plic_section`, SN d); UNTIL_TAKEN releases
after `rvfi_intr` of the matching cause; a one-cycle pulse is a deliberate "may be missed"
stimulus (II s11). The agent publishes every edge with its cycle on `ap` for the checkers.
No checker inside the agent (checks live in C4.4).

#### C3.7 gen_dbg_agent (debug request driver)

Purpose: drives `debug_req_i`. API: agent on `gen_dbg_if`; item {assert_delay, hold_policy =
UNTIL_DEBUG_MODE | CYCLES(n) | STICKY}; bridge command DBG_REQ. Knobs: `+gen_dbg_regime=none|
sparse|dense|step_mix`, `+gen_dbg_hold_min/max`. Wave-level: level; UNTIL_DEBUG_MODE drops the
line the cycle after `rvfi_ext_debug_mode` rises on a retired record (or after the
`evt_dbg_entered` monitor event). The debug program is the image's `.debug_rom` section linked at
`DmHaltAddr` (gen_link.ld; default `dret` stub when a program defines none; riscv-dv-generated
debug ROMs are relocated there by `dv/auto_dv/stim/gen_relocate_debug_rom.py`, run by
`gen_program.py`; T-025 evidence). Debug requests are issued only after the program's init
(riscv-dv INITIALIZED signature or a retirement threshold) because the generated ROM uses the
program's kernel stack pointer. No checker inside the agent (C4.5).

### C4. Monitors and checkers

#### C4.1 gen_rvfi_monitor

Purpose: turns each `rvfi_valid` cycle into `gen_rvfi_txn` {order, insn, trap, halt, intr, mode,
ixl, rs1/rs2/rs3 addr+data, rd addr+data, pc_rdata, pc_wdata, mem addr/rmask/wmask/rdata/wdata,
ext_pre_mip, ext_post_mip, ext_nmi, ext_nmi_int, ext_debug_req, ext_debug_mode,
ext_rf_wr_suppress, ext_mcycle, ext_mhpmcounters[10] (+h), ext_ic_scr_key_valid, ext_irq_valid,
ext_expanded_insn_valid/insn/last, cycle}; also a separate `gen_rvfi_irq_txn` on
`rvfi_ext_irq_valid` without `rvfi_valid`. Analysis ports `ap` and `ap_irq`; raises
the bridge events (v2, A-01): the retirement count that feeds `evt_retired_target` / `evt_thresh_hit` and `evt_retired_count`, plus `evt_irq_taken`, `evt_dbg_entered`. Knob: `+gen_rvfi_trace=1` writes an ASCII
trace file (debug only). Wave-level: sampled on the posedge where `rvfi_valid` is 1; outputs are
flops in the core (SN a.4), so no combinational race. Checks (self-consistency of the trace):

| Checker id | Rule | Mutation classes (locus) | Knob |
|---|---|---|---|
| `rvfi_order` | `rvfi_order` increments by one per record; never repeats; `rvfi_halt == 0` | RVFI order pipeline (`rtl/ibex_core.sv:1908, 2088`) | `+gen_chk_rvfi_order` |
| `rvfi_pc_cont` | non-trap, non-redirect record: next record's `pc_rdata == pc_wdata`; traps/mret/dret/fence.i: `pc_wdata` not checked until F-RVFI-010 is ruled; `pc_rdata` continuity is checked instead | pc_wdata mux (`:2095`), pc_id capture | `+gen_chk_rvfi_pc_cont` |
| `rvfi_cap_quiet` | `*_rcap == NULL_CAP`, `mem_is_cap == 0` | carve-out sanity | `+gen_chk_rvfi_cap_quiet` |

#### C4.2 gen_misc_monitor: alerts, crash_dump_o, double_fault_seen_o, core_busy_o, data_tag_o

Purpose: samples the misc outputs every cycle into `gen_misc_txn` and runs the checkers below;
it owns the "expected injection" bookkeeping it receives from the agents' `ap` (injected
integrity and cache ECC errors) and from the scoreboard (retired traps, mret, CSR writes).

| Checker id | Rule | Mutation classes (locus) | Knob |
|---|---|---|---|
| `alert_minor` | `alert_minor_o` pulses only in the response window of an injected cache ECC error; each injection produces exactly one pulse | icache ECC error OR (`rtl/ibex_icache.sv:585`), `alert_minor_o` wiring (`rtl/ibex_core.sv:1337`) | `+gen_chk_alert_minor` |
| `alert_bus` | (v2, XM-L1) split by source: FETCH: `alert_major_bus_o` asserts in the `instr_rvalid_i` cycle of an injected corrupted beat whether or not the word is ever consumed (`instr_intg_err_o = instr_intg_err & instr_rvalid_i`, rtl/ibex_if_stage.sv:282; speculative and PMP-denied fetches included); DATA: asserts at the data response cycle of an injected corrupted load or store response (LSU registration to be verified at bring-up, `GEN_ALERT_BUS_WINDOW`); never otherwise. Class: exact (fetch), windowed (data) | integrity decoders (`rtl/ibex_load_store_unit.sv:385-393`, `rtl/ibex_if_stage.sv:276-282`), OR at `rtl/ibex_core.sv:1353` | `+gen_chk_alert_bus` |
| `alert_internal` | `alert_major_internal_o == 0` always (RegFileECC = 0: only `pc_mismatch_alert` remains, AN s9) | PC increment check (`rtl/ibex_if_stage.sv:658-692`), OR at `rtl/ibex_core.sv:1350` | `+gen_chk_alert_internal` |
| `crash_dump` | `exception_pc == model mepc` and `exception_addr == model mtval`, compared from `GEN_CSR_COMMIT_TO_RVFI_OFFSET` cycles before each retired CSR-write/trap record onward (class windowed, v2 A-09); `last_data_addr` == last granted data address (aligned rules of BS MEM-06, exact per grant); `current_pc/next_pc` compared only while `core_busy_o == Off` (pipe empty) | crash_dump assigns (`rtl/ibex_core.sv:1325-1330`), lsu_addr_last (`rtl/ibex_load_store_unit.sv:743`) | `+gen_chk_crash_dump` |
| `double_fault` | `double_fault_seen_o` pulses exactly when a synchronous trap record follows a previous synchronous trap record with no retired `mret` in between (model of `sync_exc_seen`, BS CTRL-23); `cpuctrlsts` bits 6/7 read back per model | set/clear/pulse logic (`rtl/ibex_cs_registers.sv:890-965`) | `+gen_chk_double_fault` |
| `core_busy` | `core_busy_o` is always exactly On or Off (mubi). (v2, A-10) After every retired WFI it is Off for exactly one cycle (WAIT_SLEEP, `ctrl_busy_o = 0` unconditionally, rtl/ibex_controller.sv:598-604) even when a wake condition is already true; it stays Off beyond that cycle only while no wake term (irq pending, NMI, debug request, single step, debug mode) is present and no bus beat is outstanding (SLEEP, :606-621); it returns to On the same cycle a wake input asserts (BS CTRL-06); no `instr_req_o`/`data_req_o` while Off. Class: exact | busy generation (`rtl/ibex_core.sv:496-522`), controller WAIT_SLEEP/SLEEP (`rtl/ibex_controller.sv:598-621`) | `+gen_chk_core_busy` |
| `data_tag_quiet` | `data_tag_o == 0` | carve-out sanity | `+gen_chk_data_tag_quiet` |
| `fetch_en` | while `fetch_enable_i != IbexMuBiOn`: no new `instr_req_o` except beats already owned by fill buffers (BS MEM-16), no new RVFI record whose `pc_rdata` differs from the pc at disable, trap-state changes allowed (Q-DL-8 default) | fetch gate (`rtl/ibex_core.sv:644-656`), controller halt_if (`rtl/ibex_controller.sv:996-999`) | `+gen_chk_fetch_en` |

#### C4.3 gen_pmp_model (fetch and data PMP checker)

Purpose: an intent-derived Smepmp model (16 regions, G = 0, TOR/NA4/NAPOT, L bit, mseccfg
MML/MMWP/RLB, priv = `mstatus.MPRV ? MPP : prv` for data, current prv for fetch, debug-mode
exemption for the DM window). Inputs: modelled pmpcfg/pmpaddr/mseccfg (from the CSR model of
record, C6) and every RVFI record (fetch address = `pc_rdata` and, for a 4-byte instruction
crossing a word, `pc_rdata + 2`; data address/size). Predicts per word half (AN s9).

| Checker id | Rule | Mutation classes (locus) | Knob |
|---|---|---|---|
| `pmp_fetch` | predicted fetch denial <=> record has `rvfi_trap` with cause 1 (the cause is observed through the handler's `csrr mcause`, C6) | region match / permission (`rtl/ibex_pmp.sv`), PMP_I/PMP_I2 channels (`rtl/ibex_core.sv:1590-1604`) | `+gen_chk_pmp_fetch` |
| `pmp_data` | predicted denial of a word half <=> no bus transaction for that word (dbus monitor) and a trap record with cause 5/7; `mtval` = original EA for a first-half fault, aligned second word for a second-half fault (BS MEM-13); the permitted other half still appears on the bus (RTL-defined, Q-DL-7 default). (v2, A-08) Privilege for the check follows the SPEC on the debug-mode case: with `dcsr.mprven = 0` the model ignores `mstatus.MPRV` in debug mode (B2/BUG-01 row of C5.3b), so tests that load/store in debug mode with MPRV set carry `expected_fail: true` until the bug is ruled | PMP_D channel and request gating (`rtl/ibex_core.sv:1063`), LSU pmp_err path (`rtl/ibex_load_store_unit.sv:472-531`) | `+gen_chk_pmp_data` |
| `pmp_csr_warl` | pmpcfg/pmpaddr/mseccfg read-backs equal the model's legalized values (locked regions, TOR ordering, G masking, RLB/MML rules) | CSR write legalization in cs_registers | `+gen_chk_pmp_csr_warl` |

#### C4.4 gen_irq_checker (interrupt and NMI entry)

| Checker id | Rule | Mutation classes (locus) | Knob |
|---|---|---|---|
| `irq_pending` | `irq_pending_o == |({sw, timer, ext, fast[14:0]} & mie_q)` every cycle, not gated by MIE/debug/nmi (BS CTRL-07). (v2, A-09) Class: windowed(`GEN_CSR_COMMIT_TO_RVFI_OFFSET`): the RTL commits `mie_q` at the CSR-write commit edge (rtl/ibex_cs_registers.sv:790, :1103-1106) while the record of the `csrw` appears after WB, so the model's `mie` value used for cycle t is the one committed by the record whose cycle is `t + GEN_CSR_COMMIT_TO_RVFI_OFFSET`; equivalently a settle window of `GEN_CSR_COMMIT_TO_RVFI_OFFSET` cycles (at least 2: the write commits in ID/EX, the record follows WB by one cycle, more when WB stalls, XM-M5) opens at each retired `mie` write record, the compare is suspended inside it and re-armed with the new value; pin edges need no window (pins are visible). The constant is measured at bring-up and pinned by a directed test | `irqs_o`/`irq_pending_o` (`rtl/ibex_cs_registers.sv:1044-1045`), mip wiring (`:408-412`) | `+gen_chk_irq_pending` |
| `irq_entry` | when enable conditions hold (`mstatus.MIE` or U-mode, not debug, not nmi_mode) and a line is pending, the next RVFI event is an interrupt entry: `rvfi_ext_irq_valid` or a record with `rvfi_intr = 1`, `pc_rdata == mtvec_base + 4*id`, id = highest priority pending (NMI > fast lowest-id > ext > sw > timer, BS CTRL-10), within `GEN_IRQ_ENTRY_BOUND` records/cycles after the current instruction completes; `pre_mip` of that record contains the taken id | controller handle_irq / IRQ_TAKEN (`rtl/ibex_controller.sv:498-511, 725-758`), priority select | `+gen_chk_irq_entry` |
| `irq_masked` | no interrupt entry while `mstatus.MIE == 0` in M-mode, in debug mode, or during NMI handling; a one-cycle pulse that is not sampled produces no entry | same | `+gen_chk_irq_masked` |
| `nmi_entry` | `irq_nm_i` => entry within bound regardless of MIE/mie, `mcause == 0x8000001F`, `pc_rdata == mtvec_base + 0x7C`, nested NMI ignored; `mret` from the NMI handler restores mstatus.MPP/MPIE, mepc, mcause from the mstack model (BS CTRL-11/13) | NMI path (`rtl/ibex_controller.sv:736-745`), mstack (`rtl/ibex_cs_registers.sv` mstack) | `+gen_chk_nmi_entry` |
| `nmi_internal` | an injected LSU response integrity error => `alert_major_bus_o`, `rvfi_ext_rf_wr_suppress` on the load, internal NMI with `mcause 0xFFFFFFE0` and `mtval` = the faulting address, taken at most one instruction later (BS CTRL-12); fetch-side integrity errors raise no NMI (AN s9) | mem_resp_intg_err path (`rtl/ibex_controller.sv:436-438`) | `+gen_chk_nmi_internal` |

Failure path: `uvm_error` with the id; the bound is a constant in `gen_tb_pkg`
(`GEN_IRQ_ENTRY_BOUND_RECORDS`, derived from the longest instruction the pipeline can hold:
a 37-cycle divide plus a two-half memory access plus bus latency; measured in bring-up).

#### C4.5 gen_debug_checker

| Checker id | Rule | Mutation classes (locus) | Knob |
|---|---|---|---|
| `dbg_entry` | `debug_req_i` (not in debug mode) => within bound a record with `rvfi_ext_debug_mode = 1` and `pc_rdata == DmHaltAddr`; `dcsr.cause` (read in the debug ROM, C6) = 3 for haltreq, 1 ebreak, 2 trigger, 4 step; `dpc` = pc_if for haltreq/step/trigger, the ebreak pc for ebreak (BS CTRL-24..26) | controller debug entry (`rtl/ibex_controller.sv:451-476, 764-800`), dcsr cause priority | `+gen_chk_dbg_entry` |
| `dbg_exc` | exception while in debug mode => `pc_rdata == DmExceptionAddr`, no CSR trap side effects (mepc/mcause unchanged) | debug exception vector (`EXC_PC_DBG_EXC`) | `+gen_chk_dbg_exc` |
| `dbg_masked` | no interrupt or NMI entry while `rvfi_ext_debug_mode = 1`; `debug_req_i` held during a Zcmp sequence enters only after `_last` (BS CTRL-31/39) | `handle_irq` gating | `+gen_chk_dbg_masked` |
| `dbg_dret` | `dret` returns to `dpc` with privilege `dcsr.prv`; single-step (`dcsr.step`) re-enters debug after exactly one retired instruction. (v2, A-08) SPEC direction on B1: `dret` into U clears `mstatus.MPRV` (Sdext); the model clears it and the checker expects it, so tests that `dret` into U with MPRV set carry `expected_fail: true` against the current RTL (B1 row of C5.3b) | dret path (`rtl/ibex_controller.sv`), mstatus restore in `rtl/ibex_cs_registers.sv` | `+gen_chk_dbg_dret` |
| `dbg_trigger` | `tdata1/tdata2` execute-address match (one trigger) enters debug before the matching instruction retires; M-mode writes to tdata1/2 ignored | trigger compare in cs_registers | `+gen_chk_dbg_trigger` |

#### C4.6 gen_counter_model

Purpose: predicts `mcycle`, `minstret`, `mhpmcounter3..12` from the boundary. `mcycle` = cycles
since reset release minus inhibited cycles plus software writes (no clock gate: sleep cycles
count, AN s9); `minstret` per BS CSR-20 (not counted: ebreak, ecall, illegal, fetch fault,
errored loads/stores, CSR writes to minstret(h); Zcmp counts once at `_last`; dummy instructions
DO count: exact only with dummies off or with probe P1); events 3..12: LSU-cycle, IF-wait,
loads (misaligned = 2), stores (= 2), jumps, branches, taken branches, compressed retired, mul
wait, div wait. Cycle-class events (3, 4, 11, 12) are modelled from the bus and RVFI timing
where a boundary derivation exists and otherwise checked as bounds (`0 <= delta <= cycles
elapsed`) and monotonic; the exactness class of each counter is stated in the API document.

| Checker id | Rule | Mutation classes (locus) | Knob |
|---|---|---|---|
| `ctr_mcycle` | `rvfi_ext_mcycle` equals the model's mcycle at `record_cycle - GEN_RVFI_ID_EXIT_OFFSET` (v2, A-09: the field is sampled when the instruction leaves ID, rtl/ibex_core.sv:2102, not at retirement; class windowed(`GEN_RVFI_ID_EXIT_OFFSET`)); mcycle(h) CSR read-backs equal the model at the read's own ID-exit cycle (same offset) | counter primitive (`rtl/ibex_counter.sv`), inhibit gating | `+gen_chk_ctr_mcycle` |
| `ctr_minstret` | (v2, XM-L4) exact while `cpuctrlsts.dummy_instr_en` (modelled) is 0; a BOUND check (`model <= observed <= model + cycles elapsed`) whenever it is 1; no dependence on probe P1, which stays coverage-only plus the BUG-02 quantification reproducer | perf_instr_ret (`rtl/ibex_wb_stage.sv:206-210`), `incr[2]` (`rtl/ibex_cs_registers.sv:1588`) | `+gen_chk_ctr_minstret` |
| `ctr_hpm_exact` | counters 5..10 (loads, stores, jumps, branches, taken, compressed) exact | event ORs in id/wb stage | `+gen_chk_ctr_hpm_exact` |
| `ctr_hpm_bound` | counters 3, 4, 11, 12 within bounds and monotonic; `mcountinhibit` stops them | inhibit/event wiring | `+gen_chk_ctr_hpm_bound` |

#### C4.7 gen_scoreboard

Purpose: the hub. Subscribes to `gen_rvfi_monitor`, both bus monitors, the irq/dbg agents'
`ap`, and `gen_misc_monitor`; owns the CSR model of record (C6), the counter model (C4.6), the
PMP model (C4.3), the irq/NMI/debug checkers (C4.4/C4.5) as sub-checkers, and the ISA-model
comparator (C5). Per RVFI record it: (1) folds Zcmp micro-ops (C5.1); (2) determines the
asynchronous events to inject; (3) associates the record with bus transactions by order (the
WB-stage retirement of a load/store follows its response, SN c.4 note; stores retire after
the response too because `WB_INSTR_STORE` waits for it); (4) calls the shim; (5) updates the
CSR/counter/PMP models; (6) runs the sub-checkers. End of test: compares Python's and SV's
command counters, drains outstanding bus transactions, reports counts. Knobs:
`+gen_chk_isa=0` disables the whole ISA compare (master); per-field knobs below; `+gen_sb_trace=1`
debug log.

(v2, A-11) The ISA comparator's checker rows, one per compared field, so the Test Writer can
produce isolated mutation evidence per field:

| Checker id | Rule | Mutation classes (example locus) | Knob |
|---|---|---|---|
| `isa_pc` | model pc before the step == `rvfi_pc_rdata` (exact per record) | fetch/branch target: `rtl/ibex_if_stage.sv` pc mux, `rtl/ibex_ex_block.sv` branch target ALU | `+gen_chk_isa_pc` |
| `isa_insn` | model instruction bits == `rvfi_insn` (compressed form for 16-bit) | compressed decoder expansion (`rtl/ibex_compressed_decoder.sv`), fetch data path | `+gen_chk_isa_insn` |
| `isa_trap` | model trap <=> `rvfi_trap`; cause per handler read-back | controller exception cause select (`rtl/ibex_controller.sv:299-337, 900-927`), decoder illegal detection | `+gen_chk_isa_trap` |
| `isa_rd` | GPR write (index, value) == `rvfi_rd_addr/rd_wdata` | ALU operator select (`rtl/ibex_alu.sv`), multiplier/divider (`rtl/ibex_multdiv_fast.sv`), decoder rd/we (`rtl/ibex_decoder.sv`), WB mux (`rtl/ibex_wb_stage.sv`) | `+gen_chk_isa_rd` |
| `isa_mem` | memory access address, size, store data == `rvfi_mem_*` | LSU address/data rotation and byte enables (`rtl/ibex_load_store_unit.sv:138-221`) | `+gen_chk_isa_mem` |
| `isa_prv` | `last_inst_priv == rvfi_mode` | privilege update on trap/mret (`rtl/ibex_cs_registers.sv:953-993`) | `+gen_chk_isa_prv` |
| `isa_pc_next` | model pc after the step == `rvfi_pc_wdata` (not on the F-RVFI-010 records) | pc increment / redirect (`rtl/ibex_if_stage.sv`) | `+gen_chk_isa_pc_next` |
| `isa_csr` | every model CSR write (commit log type 4) == the legalized expectation; read-backs per C6 | CSR legalization and read mux (`rtl/ibex_cs_registers.sv`) | `+gen_chk_isa_csr` |

#### C4.8 Exactness classes and their constants (v2, A-09)

| Checker | Class | Constant (gen_tb_pkg) and how it is set |
|---|---|---|
| `irq_pending` | windowed | `GEN_CSR_COMMIT_TO_RVFI_OFFSET`: cycles between the CSR commit edge and the RVFI record of the writing instruction; measured in bring-up, pinned by a directed `csrw mie` test |
| `crash_dump` (exception_pc/addr) | windowed | same constant |
| `ctr_mcycle` | windowed | `GEN_RVFI_ID_EXIT_OFFSET`: cycles between ID exit (sample point of `rvfi_ext_mcycle`) and the record; same method |
| `ctr_minstret`, `ctr_hpm_exact` | exact per record; `ctr_minstret` becomes bound while dummy instructions are enabled (XM-L4) | none |
| `ctr_hpm_bound` | bound | none |
| `alert_minor`, `alert_bus` | windowed | `GEN_ICACHE_ECC_WINDOW` (injection to alert), `GEN_ALERT_BUS_WINDOW` (response consumption cycle from the bus monitor to the alert) |
| `irq_entry`, `nmi_entry`, `dbg_entry` | windowed (bound on latency) | `GEN_IRQ_ENTRY_BOUND_RECORDS`, `GEN_DBG_ENTRY_BOUND_RECORDS` |
| `core_busy`, `ibus_*`, `dbus_*`, `scrkey_proto`, `icram_*`, `double_fault`, `fetch_en`, `data_tag_quiet`, `rvfi_*`, `pmp_*`, `isa_*` | exact | none |

### C5. ISA-model integration: gen_isa_shim and comparator policy (RR ask 3)

Model: upstream Spike pinned at 4ffd6ba860f4190ceac2716fa3c2cf139e85538f, built 2026-09-03 into
`tools/spike` (`libriscv.so`, `libsoftfloat.so`, `libfesvr.a`, headers under
`include/riscv|fesvr|softfloat|fdt`, `pkgconfig/riscv-riscv.pc`; evidence
`dv/auto_dv/evidence/gen_t019_spike_build.md`). Verified in the clone: `zcmp`/`zcb` ISA
extensions with `cm.push/pop/popret/popretz/mvsa01/mva01s/jalt` files; ratified Zba/Zbb/Zbc/Zbs
files; the draft-B files grevi, gorci, pack, packh, bext present; the draft-only ops grev/gorc
(non-alias), shfl/unshfl, cmix/cmov, fsl/fsr, crc32*, slo/sro(i), packu, bdep, bfp, xperm* ABSENT.
Whether grevi/gorci with non-alias immediates decode under the Zbb string is UNVERIFIED (second
link test, C5.1). (v2, A-14, verified by the Critic in the pinned source) `mie_csr_t::write_mask()`
(riscv/csrs.cc:993-1001) admits only MSIP/MTIP/MEIP plus S/H/LCOF bits when those extensions exist:
bits 16..30 are never writable through a CSR instruction, because `mip_or_mie_csr_t::
unlogged_write` is `final` and applies `write_mask()` (csrs.h:373-383; csrs.cc:951-954), so a
shadow re-applied through `csr_t::write` would NOT work (v2, XM-M1). `write_mask()` is a private
virtual, which C++ allows a subclass to override; and `select_an_interrupt_with_default_priority`
(processor.cc:258-262, `ctz` after giving nonstandard bits >= 16 priority over MEI/MSI/MTI) already
implements Ibex's order NMI-slot > fast lowest-id > external > software > timer, so no priority
emulation is needed. `mip_or_mie_csr_t::write_with_mask` (csrs.cc:946-949) is public and applies
only the caller's mask (used for pin injection into `mip`).

#### C5.1 gen_isa_shim API (C++20, built as `libgen_isa_shim.so`, loaded with `-LDFLAGS`)

Build: `g++ -std=c++2a -fPIC -shared -I tools/spike/include gen_isa_shim.cc -L tools/spike/lib
-lriscv -Wl,-rpath,<abs>/tools/spike/lib`; only `<prefix>/include` on the include path (adding
`include/fesvr` shadows the system `syscall.h` and breaks libstdc++'s `atomic_wait.h`; found in
the T-019 link test). Separate from VCS's `-CFLAGS '--std=c99'` C glue (R-4).

Object graph: our `gen_simif_t : simif_t` (the same `.vmem` image the SV memory model loads, which
already carries the boot entry and the debug ROM, plus the MMIO windows from the generated header
the SV memory map uses; `addr_to_mem` returns NULL
for every address so that ALL model loads/stores/fetches go through `mmio_fetch/load/store`,
which gives the shim full visibility of model memory traffic and per-access fault injection),
one `processor_t(isa, "mu", &cfg, &sim, 0, false, devnull, cerr)` with `cfg.pmpregions = 16`,
`cfg.pmpgranularity = 4`, `cfg.trigger_count = 1`, `enable_log_commits()`. Reset legalization
(C5.3) is applied after construction. Custom CSRs `cpuctrlsts` (0x7C0) and `secureseed` (0x7C1) are
our own `csr_t` subclasses, provided through the sanctioned extension point
`extension_t::get_csrs(processor_t&)` (tools/spike/include/riscv/extension.h:16) by a `gen_ibex_ext`
extension registered with `REGISTER_EXTENSION` and named in the ISA string, which places them in the
public `state.csrmap` (processor.h:90) (v2, A-16, XM-I1; no RVFI intercept); the
`time`/`timeh` entries (0xC01/0xC81) are replaced by a trapping `csr_t` whose `verify_permissions`
throws illegal-instruction, matching Ibex (v2, A-17).

(v2, A-16) Prerequisite before shim coding, DONE: the second link test
(`dv/auto_dv/work/tb-infra/gen_spike_linktest2.cc`, 98/98 checks, `out_linktest2/linktest2.log`,
evidence `dv/auto_dv/evidence/gen_t046_spike_linktest2.md`) demonstrates `gen_mie_csr_t` taking a fast interrupt
with Ibex's priority (retired 0, then 1), custom CSRs through `extension_t::get_csrs`, `wfi` /
`in_wfi`, `halt_request` entry and `dret`, a tdata1 write from debug mode and an execute-address
trigger entry, one `cm.push` step with `log_mem_write`, and aligned / misaligned `mmio_store`
faults. Three corrections it forced are marked "(link test 2)" below: the debug-entry pc parking,
the extension naming and reset order, and the byte-split misaligned MMIO path in C5.4.

| DPI export | Purpose |
|---|---|
| `gen_isa_reset(cfg_struct)` | build/reset the model; apply Ibex reset values (pc = boot + 0x80, mtvec = boot page | 1, mstatus = 0x80, PMP all zero, misa fixed) |
| `gen_isa_arm_async(pre_mip, taken_cause, nmi, nmi_int, debug_req, irq_valid)` | (v2, A-14, XM-M1) before a step: set `mip` to the raw `pre_mip` with `backdoor_write_with_mask` (so `csrr mip` compares). Because the model's `mie` holds Ibex's fast bits (gen_mie_csr_t, C5.3a) and Spike's default priority equals Ibex's, the model takes the same interrupt on its own; `taken_cause` (from the handler's `csrr mcause` read-back, or from `pre_mip` and the priority rule when the read-back has not arrived) is compared against the model's `mcause` after the entry step and mismatches raise `isa_trap`. Set `halt_request` for debug; emulate NMI entry |
| `gen_isa_arm_fault(kind, addr, size)` | make the next model access to `addr` fail (fetch/load/store access fault) |
| `gen_isa_note_memory_write(addr, data, be)` | (v2, A-15) reserved for TB-side writes the DUT did not perform (none expected); no longer needed for half-performed stores, which the shim's `mmio_store` performs per Ibex's rule (C5.4) |
| `gen_isa_step(txn_in, txn_out)` | step once (or fold, C5.2), return pc before/after, retired flag, trap cause, GPR write list, memory access list, CSR write list (from `log_reg_write` type 4), privilege |
| `gen_isa_exec_reference(insn, rs1, rs2, rd_out)` | shim-executed instruction for draft-B ops (C5.5) |
| `gen_isa_read_csr(addr)`, `gen_isa_read_gpr(idx)`, `gen_isa_write_csr(addr, val)` | read-back compare and legalization sync |
| `gen_isa_set_time(mcycle)` | keep `time`/`mcycle` in the model consistent when a test reads them |

Failure path: the shim never fails on its own; it returns status codes and the scoreboard raises
`uvm_error ISA_<field>` with expected-versus-actual per field; a model-side abort (unknown ISA
string, bad cfg) is caught at `gen_isa_reset` and reported as `uvm_fatal ISA_INIT`.

#### C5.2 Comparison unit and Zcmp folding

One RVFI record = one retirement or one trapping instruction. (v2, XM-M2) `processor_t::step`
takes a pending interrupt (and a trigger action) INSIDE its try block and then retires zero
instructions for that call (execute.cc:244, 317-318, 340-345), so the step rule depends on the
record class; `gen_isa_step` returns the retired count and the scoreboard asserts it:

| Record class | Steps the shim performs | What is compared |
|---|---|---|
| ordinary retirement | one `step(1)`; retired count must be 1 | full record compare below |
| synchronous trap (`rvfi_trap`) | one `step(1)`; retired count 0; the model's pc is now the handler | `rvfi_trap`, trap cause via the handler read-back, `mepc`/`mtval`/`mstatus` writes in `log_reg_write`; `pc_wdata` not compared (F-RVFI-010) |
| interrupt entry: a `gen_rvfi_irq_txn` (`rvfi_ext_irq_valid`) or a record with `rvfi_intr = 1` | first arm (`gen_isa_arm_async`), then `step(1)` that takes the interrupt (retired 0; verify pc == vector, `mcause`, `mepc`, `mstatus.MPIE/MIE`), then, for the `rvfi_intr` record, a second `step(1)` for the handler's first instruction (retired 1) | entry state after the first step; the record after the second |
| debug entry (`rvfi_ext_debug_mode` rises, or a trigger match) | set `halt_request = HR_REGULAR` (or let the trigger fire), `step(1)`: retired 0, `dcsr.cause`/`dpc` set; (link test 2) the step then fetches Spike's ROM entry 0x800, unbacked, and the fetch fault inside debug mode parks pc at DEBUG_ROM_TVEC with no mcause/mepc change (`enter_debug_mode` is private, processor.h:409); the shim sets pc = DmHaltAddr and clears `halt_request` (Spike never clears it); then `step(1)` for the ROM's first instruction | as above |
| Zcmp micro-op records | fold to `_last`, one `step(1)` (retired 1) or a trap step | union compare (below) |
| NMI entry | shim emulation of the entry, then `step(1)` for the handler's first instruction | entry state, then the record |

For an ordinary record the scoreboard compares: pc before step == `pc_rdata`; instruction bits (compressed form
when RVFI reports 16-bit); trap taken <=> `rvfi_trap`; GPR write (addr, data) == `rd_addr/rd_wdata`
(zero when none); memory access address + size + store data == `mem_*` (mask position ignored,
SN a.4); `last_inst_priv == rvfi_mode`; pc after step == `pc_wdata` except on the F-RVFI-010
records; each logged CSR write against the legalized expectation.

Zcmp (F-RVFI-022/023): each micro-op completes ID individually (`instr_gets_expanded_id` walks
INSTR_EXPANDED -> INSTR_EXPANDED_COMMIT -> INSTR_EXPANDED_LAST) and produces its own record with
`rvfi_insn` = the 32-bit micro-op, `rvfi_ext_expanded_insn_valid = 1`, `rvfi_ext_expanded_insn` =
the 16-bit cm.* encoding, `_last` on the final one (`rtl/ibex_core.sv:2263-2280`); `rvfi_order`
advances per record (UNVERIFIED). Policy: fold records from the first `expanded_insn_valid` to
`_last` into one architectural instruction and compare against ONE model step of cm.*: the union
of the records' GPR writes == the model's `log_reg_write` set; the ordered list of memory accesses
== the model's `log_mem_write/read` list; `pc_wdata` of the last record == model pc after the
step. A trap on micro-op k (record k has `rvfi_trap`, sequence ends): the model step traps; stores
performed by micro-ops 1..k-1 are compared with the stores the model performed before its trap
(visible through `gen_simif_t`). Interrupts and debug entry cannot split a sequence during the
COMMIT micro-ops (BS CTRL-39), consistent with the model taking interrupts between instructions;
`minstret` counts once per cm.* (BS CSR-20), consistent with the model.

#### C5.3 Legalization layer (Ibex WARL and platform rules the model lacks)

(v2, A-08) The table is split. C5.3a holds RTL-DEFINED rows: behaviour the specification leaves to
the implementation or that the Ibex documentation and RTL define; the model follows the RTL under
the standing checker-direction policy (intervention log Q-006 / Q-DL-5 default), each row citing
its source. C5.3b holds SPEC-VIOLATION rows: the team's bug candidates where the RTL contradicts a
RISC-V specification; the model and the checkers follow the SPECIFICATION, the tests that exercise
them carry `expected_fail: true` in the testlist with the bug id, and the shim must NOT legalize
the RTL behaviour away.

##### C5.3a RTL-defined rows (model follows the RTL)

| Item | Ibex rule (source) | Shim action |
|---|---|---|
| 64-bit state | the model keeps RV32 pc, GPRs and CSR values sign-extended in 64-bit `reg_t` (T-019 link test: pc read back as 0xffffffff8000000c) | every compare and every value passed to the model is truncated/zero-extended to 32 bits at the DPI boundary |
| Reset | mstatus 0x0000_0080 (MPIE 1, MPP U), prv M, PMP all OFF/0, mtvec = {boot[31:8], 8'h01}, pc = {boot[31:8], 8'h80} (AN s4/s9) | write state after `processor_t` construction (the model opens PMP and sets pc 0x1000 by default) |
| mip | raw pins, read-only (AN s3) | inject `pre_mip` raw with `backdoor_write_with_mask`; no masking |
| mie fast bits 16..30 | writable in Ibex (rtl/ibex_cs_registers.sv mie write) | (v2, A-14, XM-M1) verified: Spike's `mie_csr_t::write_mask()` never admits bits 16..30 (csrs.cc:993-1001) and `unlogged_write` is `final` (csrs.h:380), so no shadow through `csr_t::write` can work. No-patch route: the shim defines `gen_mie_csr_t : public mie_csr_t` overriding the private virtual `write_mask()` to return Spike's mask OR bits 16..30 (`GEN_IRQ_FAST_MASK` = `((1 << 15) - 1) << 16`, from `$bits(irqs_t.irq_fast)` and `CSR_MFIX_BIT_LOW`), and at `gen_isa_reset` installs one instance in `state.mie` (a `mie_csr_t_p`, processor.h:109) and in `state.csrmap[CSR_MIE]`; program `csrw mie` writes then take effect directly and `take_interrupt` sees them. Priority: Spike's `select_an_interrupt_with_default_priority` (processor.cc:258-262) already ranks nonstandard bits >= 16 above MEI > MSI > MTI and picks the lowest set bit, matching Ibex; no emulation. Closes Q-DL-10 / Q-011 for this item |
| mtvec | MODE forced 01, BASE[7:2] = 0 (BS CTRL-02) | after each retired mtvec write, write `(wdata & 0xFFFFFF00) | 1` into the model |
| misa | read-only | rewrite the fixed value after any retired misa write |
| mstatus | MPP 01/10 -> U (BS BUG-05); TW, MPRV, MPIE, MIE only | legalize after write |
| mcounteren | 13 bits, bit 1 forced 0, write dropped unless `mcounteren_writable_i == On` (AN s9) | legalize / drop |
| mcountinhibit, mhpmevent3..12 | Ibex masks / hardwired events (PERF doc) | legalize; counters compared with the TB model, never the ISS |
| mcycle/minstret/mhpmcounter | TB counter model (C4.6) | excluded from ISS compare; ISS counters synced on software writes only |
| NMI / internal NMI | cause 0x8000001F / 0xFFFFFFE0, vector base+0x7C, mstack save/restore (BS CTRL-11..13) | emulated in the shim: write mepc/mcause/mtval/mstatus, set pc, track nmi_mode; on mret restore from the shim's mstack |
| Debug | entry pc = `DmHaltAddr`, exception in debug = `DmExceptionAddr` (Spike hardcodes DEBUG_ROM_ENTRY 0x800 / DEBUG_ROM_TVEC 0x808, processor.cc:391, :423-425) | after `halt_request` + step override `state.pc`; on trap in debug mode override to `DmExceptionAddr`; `dcsr` legalization of the RTL-defined fields only (prv WARL to M/U, cause, ebreakm/ebreaku, step; xdebugver 4 which Spike also reports, csrs.cc:1600). NOT legalized: `dcsr.ebreaks` (C5.3b BUG-03), `dcsr.nmip` (C5.3b B5), MPRV handling in debug mode (C5.3b B2) |
| Triggers | one trigger, execute-address exact match only, `dmode = 1`, M-mode writes ignored (cs_registers.rst:355-405) | legalize tdata1/tdata2 writes (RTL-defined WARL subset); the tdata3/mcontext/scontext read-zero behaviour is NOT legalized (C5.3b B3) |
| PMP | per-half checks on misaligned accesses (AN s9); no misaligned exception (zicclsm); a permitted half of a partially denied misaligned store is performed (BS MEM-13, Q-DL-7 default) | ISA string includes `zicclsm`; the shim's `mmio_store` implements the per-word rule itself (C5.4, v2 A-15) |
| cpuctrlsts / secureseed | custom CSRs (cs_registers.rst 0x7C0/0x7C1) | (v2, A-16, link test 2) our own `csr_t` subclasses with Ibex's WARL fields, provided by extension `genibex` (ISA string `_xgenibex`; extension names cannot contain `_`, the parser splits on it, disasm/isa_parser.cc:331-336) and added to `csrmap` by the `reset()` that `gen_isa_reset` calls after construction (processor.cc:80-85, 170-173); `gen_mie_csr_t` is installed after that reset; `secureseed` reads 0 |
| time(h) | traps in Ibex (cs_registers.rst:596-599); Spike implements `time` as a readable CSR | (v2, A-17) replace the csrmap entries 0xC01/0xC81 with a trapping `csr_t` (`verify_permissions` throws illegal-instruction) |
| WFI | Ibex retires WFI and sleeps; model `step()` idles in `in_wfi` | clear `in_wfi` (public `clear_waiting_for_interrupt`, processor.h:364) when the DUT retires the next instruction without an interrupt; inject the wake interrupt otherwise |

##### C5.3b Spec-violation rows (model and checkers follow the specification; tests expected_fail)

| Bug id | RTL behaviour (source) | Specification | Model / checker direction | Affected checkers and tests |
|---|---|---|---|---|
| B1 | `dret` returning to U leaves `mstatus.MPRV` set (rtl/ibex_cs_registers.sv dret path; rtl-arch to re-verify, gen_t003_acceptance follow-up 1) | Sdext: `dret` clears MPRV when the new privilege is below M (Sdext.adoc:202) | model clears MPRV; `dbg_dret` expects it cleared | `dbg_dret`, `isa_csr`; debug tests that `dret` to U with MPRV = 1: `expected_fail: true` (B1) |
| B2 / BUG-01 | `mstatus.MPRV` honoured for data accesses in debug mode although `dcsr.mprven = 0` (BS CTRL-33) | Sdext: with `mprven = 0`, MPRV is ignored in debug mode | model uses `prv` for debug-mode accesses; `pmp_data` predicts accordingly | `pmp_data`, `isa_mem`; debug-mode load/store tests with MPRV set: `expected_fail: true` (BUG-01) |
| BUG-03 | `dcsr.ebreaks` writable without S-mode (Critic C-21) | Sdext: `ebreaks` is 0 when S-mode is absent; the pinned Spike forces it to 0 (csrs.cc:1625) | model NOT legalized (Spike's behaviour is the spec); `isa_csr` flags the DUT's writable bit on read-back | `isa_csr`; dcsr write/read tests: `expected_fail: true` (BUG-03) |
| B3 | `tdata3`, `mcontext`, `scontext` read 0 and ignore writes (cs_registers.rst:423-454) | Sdtrig: unimplemented trigger CSRs raise illegal-instruction (Sdtrig.adoc:370) | model traps on access; comparator expects `rvfi_trap` | `isa_trap`, `isa_csr`; CSR sweep entries for these three: `expected_fail: true` (B3) |
| B5 | `dcsr.nmip` hardwired 0 (cs_registers.rst dcsr table) | Sdext: `nmip` reflects a pending NMI while in debug mode | model sets `nmip` while `irq_nm_i` is pending in debug mode | `isa_csr`; debug-mode dcsr read with NMI pending: `expected_fail: true` (B5) |

Rows move from C5.3b to C5.3a only through an owner ruling recorded in the intervention log.

#### C5.4 Dummy instructions and half-performed misaligned stores

Dummy instructions never reach RVFI (`rvfi_stage_valid_d[0] = rvfi_id_done & ~dummy_instr_id`,
order not advanced): the comparator never sees them; their only residue is in the counters
(C4.6). Half-performed misaligned stores (F-RVFI-014, F-PMP-087, BS MEM-10/13), rewritten in v2
(A-15, corrected by link test 2): because `addr_to_mem` returns NULL for every address, each model
access reaches the shim's `mmio_load`/`mmio_store`/`mmio_fetch`; a naturally aligned access arrives
as ONE call carrying the full length, but `mmu_t::mmio` (riscv/mmu.cc:168-184) splits a misaligned
access into single-byte calls in ascending address order and stops at the first failing byte (the
fetch path uses `mmio_fetch`, mmu.cc:99; the aligned-only "one call" claim of the v2 draft was
measured wrong). The fault decision therefore stays the shim's, applied per byte: a byte belongs to
the word `addr & ~3`; the shim applies the PMP model and the armed bus faults per word, performs the
bytes of a permitted word into the model memory and fails the first byte of a denied word. Cases:
(a) first word denied: the first byte fails, nothing is written on the model side; on the DUT side
the second word IS written (BS MEM-13, Q-DL-7 default), so the shim performs the second word itself
before returning failure (it knows the whole access from the first call's address and the
instruction being stepped); (b) second word denied: the first word's bytes are written on both
sides, the byte at the aligned second address fails; (c) both denied: nothing is written. Spike
sets `mtval` to the ORIGINAL effective address in every case, while Ibex sets the word-aligned
second address for a second-half fault (BS MEM-10/13, AN s6): after a step that trapped with cause
5/7 the shim overrides `mtval` from its own record of the failing word (`put_csr(CSR_MTVAL)`
accepted, link test 2). No mirroring step is needed and no model byte-order assumption remains.
The event hits the bins `pmp_fault x {mis_first, mis_second, mis_both} x {load, store}` and the
bus-error equivalents. Whether case (a) is a defect is owner question Q-DL-7; the comparator models
the RTL behaviour by default (RTL-defined row of C5.3a).

#### C5.5 Draft bitmanip and trap-record policy

Draft-B (ENC s5, R-3): the riscv-dv target's `supported_isa` enables RV32ZBA/ZBB/ZBC/ZBS only
(no RV32B draft group), so random programs never emit Zbp/Zbr/Zbt/Zbf ops. The RTL's draft ops
(grev/gorc non-alias, shfl/unshfl, xperm, slo/sro(i), pack non-zext.h, packu, packh, crc32*,
cmix/cmov, fsl/fsr, bfp) and the reserved-bit leniency of sloi/sroi/grevi/gorci/shfli/unshfli are
covered by directed self-checking programs whose expected values come from small C reference
functions written from the public Bitmanip draft text (upstream riscv/riscv-bitmanip; a RISC-V
specification, not Ibex collateral). For such records the shim does not step the model (it would
raise illegal-instruction); it applies the reference result to rd and advances pc
(`gen_isa_exec_reference`). (v2, A-18) Reading the draft text is subject to owner question Q-003
(intervention log; default: allowed, cloned into tools/specs with recorded SHAs); if denied, the
Q-DL-2 fallback applies and the reference functions are derived from rtl/ibex_alu.sv and marked
"RTL-defined reference" in the feature list and here. The reference functions are new checkers:
each gets a failing-first test (TDD) and a named mutation with ablation like every other checker.
The Test Writer's encoding check of the lowRISC gcc 10.2 `-march=rv32imcb` output against ENC is
done (T-023 evidence: 62/62 mnemonics match).

Trap records (BUG-04 / B14): `rvfi_id_done` suppresses the ID-stage trap record when a WB
load/store error coincides (`rtl/ibex_core.sv:1851-1853`): one trap record where two instructions
faulted. Policy: the comparator expects exactly one trap per model trap; the WB error's record is
that trap (the model faults on the same access through `gen_simif_t`) and the following ID
instruction never executed on either side. Asynchronous injection follows SN c.2 with raw `mip`;
`pre_mip` is ignored on a record coinciding with `rvfi_ext_irq_valid` until F-RVFI-032 is
confirmed.

#### C5.6 Standalone fallback

`tools/spike/bin/spike --isa=<GEN_ISA_STRING> --priv=mu --pmpregions=16 --pmpgranularity=4
--triggers=1 -m<DM base:size>,<program base:size> --pc=<entry> --log-commits <elf>` produces a
per-instruction log. (v2, XM-L2) `GEN_ISA_STRING` is defined once, in the knobs codegen output
`gen_isa_shim_map.h` (and mirrored into `gen_tb/gen_knobs.py` for `gen_program.py`), currently
`rv32imc_zicsr_zifencei_zba_zbb_zbc_zbs_zca_zcb_zcmp_zicntr_zihpm_zicclsm` (the build is
RV32ZcaZcbZcmp); the lock-step shim (C5.1) and every standalone run use the same string; the memory
windows come from the same header (DmBaseAddr/DmAddrMask, boot page, ld PROG LENGTH), as
`gen_program.py` already derives them. It
(pc, insn, GPR/CSR writes, memory addresses) used only for bring-up of deterministic directed
programs and as a second opinion when the lock-step compare disagrees.

### C6. CSR observability plan (RR ask 2)

Facts: `ibex_core` has no `rvfi_csr_*` ports. RVFI does expose the value returned by every CSR
READ as `rvfi_rd_wdata` (rd != x0), `rvfi_ext_mcycle`, `rvfi_ext_mhpmcounters[3..12]`, raw `mip`
before/after each instruction, `rvfi_ext_debug_mode`, `rvfi_ext_ic_scr_key_valid`. Not visible:
the new value after a CSR write and the trap side effects at the moment they happen.

1. Model of record: CSR state is knowable from intent (reset values per AN/BS, every retired CSR
   write from `rvfi_insn` + `rs1_rdata`/immediate, every trap entry/exit from `rvfi_trap`,
   `rvfi_intr` and the handler pc), so the scoreboard predicts every CSR at every retirement with
   the legalization table; no probe is needed for checking.
2. Read-back convention for traps: every trap handler, NMI handler and debug ROM entry starts
   with a CSR read block before any CSR write: `csrr` of mcause, mepc, mtval, mstatus (handlers),
   dcsr, dpc (debug ROM), into GPRs; each read is an RVFI record compared against the model.
   riscv-dv handlers already read mcause/mepc/mstatus and, with `+require_signature_addr=1`,
   store them to the signature window (second channel on the data bus); our user-extension adds
   the mtval and debug-ROM reads; directed programs share `gen_trap_macros.h`.
3. Read-back convention for writes: (a) a riscv-dv user-extension stream `gen_csr_sweep_stream`,
   inserted at a knob-controlled frequency, reads every implemented CSR (mstatus, misa, mie,
   mtvec, mcountinhibit, mhpmevent3..12, mscratch, mepc, mcause, mtval, mip, pmpcfg0..3,
   pmpaddr0..15, mseccfg(h), tselect/tdata1..3, cpuctrlsts, mcycle(h), minstret(h),
   mhpmcounter3..12(h), mvendorid/marchid/mimpid/mhartid/mconfigptr, mcounteren; dcsr/dpc/
   dscratch inside the debug ROM only); (b) an end-of-test sweep of the same list before the
   tohost write. Read side effects: none except `secureseed` reads 0 and `time(h)` traps
   (expected by the sweep).
4. (v2, A-20) Shim self-validation only: after every retired CSR write the shim compares the
   model's post-write CSR against its own legalization table; a mismatch is a shim/legalization
   defect (`uvm_error ISA_LEGALIZE`), not a DUT observation. The DUT-facing check is the read-back
   (item 3) and the per-feature fire-check read directly after each write, which bounds the
   observation latency to one instruction.
6. (v2, A-19 conditions) The coverage plan carries `gen_csr_cg.cp_sweep_freq` (sweep frequency
   knob value) and `cp_write_read_gap` ("CSR write followed by a read of the same CSR within N
   records") so the observability gap is measured; the read blocks are `csrr` only; `mip` values
   come from `rvfi_ext_pre_mip`/`post_mip`, never from a read alone.
5. Behavioural observation: `gen_pmp_model` and `gen_irq_checker` predict faults and interrupts
   from the modelled CSRs, so a wrong CSR value surfaces as a wrong fault or interrupt even before
   any read.

Probe proposal for CSR state: none for checking; one debug-only candidate P6 in C8, off by
default, no checker depends on it.

### C7. Covergroup implementation strategy

- Homes: `gen_fcov_pkg` (class-based covergroups sampled by the scoreboard/monitors with
  transaction arguments) and `gen_<x>_cov` modules bound through `gen_binds.sv` for signal-level
  groups (bus handshakes, RAM events). Every covergroup type is `gen_<feature>_cg`; never added
  into another group (contract README). Bins derive their ranges from `ibex_pkg` parameters
  (`PMP_MAX_REGIONS`, `IC_*`, `$bits(irqs_t.irq_fast)`, `MHPMCounterNum` via the config object).
- Sampling: on monitor events only (RVFI record, bus grant/response, irq edge, alert pulse,
  regime change), never on a free-running clock; every sampling condition is written as a
  named `gen_smp_<name>` event whose definition is reviewed for vacuity (dv_principles Section 6).
- Crosses that need two sources (e.g. "interrupt asserted while a data response is outstanding")
  are sampled in the scoreboard, which has both transaction streams.
- Regime bins: `gen_regime_cg` samples every REGIME_SET command (regime id per agent) and the
  transition pairs, so layer 3 is covered (DV_prompt Section 6).
- Per-test expectation: each test's `dv/auto_dv/fcov_expectations/<test>.fcov.yaml` lists
  `<cg>.<cp>.<bin>` keys; `ci/check_fcov_expectations.py --vdb <vdb> --cm-name test_<t>_<seed>`
  runs per test pre-merge (fcov-expectation skill). (v2, A-21) Code-coverage scope is the DV
  Lead's recorded decision, implemented in Runtime's `dv/auto_dv/flow/gen_cm_hier.cfg`; this
  document does not restate it (C1's two-tree suggestion and Runtime's single `+tree <tb_top>.u_dut`
  differ only by the wrapper's wiring, which holds no logic). `cond` is added by Runtime (R-8). No
  RTL covergroups exist to collide with.

### C8. Probe register candidates and the Critic's rulings (v2)

Rulings recorded from `gen_critic_tb_arch_components_v1.md` C8 (binding); the register itself is
`dv/auto_dv/docs/gen_probe_register.md`.

| Id | Signal(s) | Ruling | Conditions |
|---|---|---|---|
| RVFI | `rvfi_*` ports of ibex_core under `+define+RVFI` | ACCEPTED as a boundary interface, not a probe | recorded as "define-gated DUT interface" so the register lists everything the TB reads inside gen_dut_top |
| P1 | `dummy_instr_id/wb`, `rf_raddr_a/b`, `rf_waddr_wb`, `rf_we_wb` (wrapper seam, ibex_core ports) | ACCEPTED for coverage and for the BUG-02/B7 quantification only | observation-only bind in gen_binds.sv on the seam nets (no reference below ibex_core); the only pass/fail use is the dummy-count reproducer for the minstret bug candidate, reported as such; `ctr_minstret` with dummies on stays `>=`; rationale: insertion cycles come from the RTL LFSR (rtl/ibex_dummy_instr.sv:60-75) and security.rst:44-47 says only "random intervals"; the bind's failure on a renamed net identifies itself |
| P2 | icache hit/miss internals | REJECTED for now | derivable at the boundary (tag read of both ways on `ic_tag_req_o`; a miss is followed by an `instr_req_o` fill of that line); re-apply only with URG evidence after a closure round |
| P3 | fill-buffer occupancy | REJECTED | equals granted-unanswered fetches, counted exactly by the ibus agent; "buffer full" is `outstanding == GEN_IBUS_MAX_OUTSTANDING` |
| P4 | `ctrl_fsm_cs` and the RTL `fcov_*` nets (rtl/ibex_controller.sv:1085-1095) | CONDITIONALLY ACCEPTED for coverage sampling only | never a checker input; each cross names its feature; bind through gen_binds.sv; the `fcov_*` nets exist only when `DV_FCOV_DISABLE` is undefined (the build never defines it: C10); re-review when the cross list exists |
| P5 | icache `valid_o`/`ready_i`/`rdata_o` seam | REJECTED for checking; not approved for coverage now | the stability rule is the RTL's own assertion (assertion coverage); F-FE-012 bins use the boundary derivation; re-apply with URG evidence |
| P6 | `cs_registers_i` CSR flops, `csr_wdata_int` | ACCEPTED as a debug-only aid | default off; knob declared once (`+gen_dbg_csr_probe=1`); never enabled in a measured regression (the flow fails a measured run that has it on); message names itself as a model-versus-RTL debug compare; not counted as a checker |

No checker depends on any probe; no per-cycle Python polling exists (A-01) and no waiver is
requested or granted.

### C9. Environment configuration, knobs and the three randomization layers

- `gen_env_cfg` (uvm_object): one field per plusarg in the tables above plus `seed`, `regime_sched`,
  `regime_pin`, `checker enables`, `build_config`. Built once in `gen_base_test::build_phase`
  from plusargs whose names come from `gen_tb_pkg::PLUSARG_*`; a mistyped plusarg name is
  impossible at the call site (strings are parameters) and an unknown `+gen_*` plusarg on the
  command line is a `uvm_fatal GEN_UNKNOWN_PLUSARG` at time 0 (v2, A-23: a warning is collected by
  nothing).
- Layer 1 (per transaction): `rand` fields with `dist` weights inside the agents' items (latency,
  error, integrity, hold policy), constrained by the current regime's ranges.
- Layer 2 (regimes): named sets of ranges/weights per agent (C3 tables), selected by
  `+gen_<agent>_regime=<name>` or by the bridge command REGIME_SET at run time.
- Layer 3 (schedule): Python derives a schedule from `RANDOM_SEED` (`gen_tb/gen_regimes.py`):
  a list of (trigger, agent, regime) where trigger is a retirement count or a cycle count; passed
  as `+gen_regime_sched=<agent>:<regime>@r<N>|c<N>,...` and reproduced by the Python side issuing
  REGIME_SET at the triggers: for each trigger Python writes `evt_retired_target` or
  `evt_cycle_target` and awaits the single `evt_thresh_hit` edge (v2, A-01; no counter is awaited).
  (v2, XM-L5) When `+gen_regime_sched` is supplied on the command line, Python CONSUMES it as the
  schedule (overriding the seed-derived one), so a specific schedule, not only a fixed regime, is
  reproducible; the banner echoes whether the schedule was derived or supplied.
  `+gen_regime_pin=<agent>:<regime>[,...]` pins regimes for the whole run (reproduction and
  directed tests), overriding the schedule; both strings are echoed in the time-0 banner.
- Error injection and event stimulus are also regime-driven (rates) with directed overrides
  (bridge commands MEM_ERR_ARM, ICACHE_ECC_ARM, IRQ_*, DBG_REQ).

### C10. Binds home: gen_binds.sv

All `bind` statements live here and nowhere else: protocol SVAs bound to `gen_dut_top` ports
(`gen_ibus_sva`, `gen_dbus_sva`, `gen_scrkey_sva`: the same rules as the C3 checkers, for
assertion coverage, each guarded by the matching `+gen_chk_*` knob through a bound-in
`gen_sva_ctl` interface), coverage modules `gen_*_cov`, and the probe monitors of C8 once
approved (P1 binds into `gen_dut_top`; P2/P3/P4/P6 into `u_ibex_core` sub-instances). No bind
forces or drives any DUT net; error injection is all at the boundary. Mutation runs use a mutated
RTL copy in a scratch out-dir (mutation-check skill), never binds and never the tree's RTL;
Runtime's build needs an RTL-root or filelist override for that copy (A-24, relayed).

(v2) Stimulus-legality assertion `sva_rvalid_legal` (rtl-arch T-022 evidence 5.2): bound to the
wrapper's bus ports, it asserts that `instr_rvalid_i` and `data_rvalid_i` are high only while the
agent has an outstanding grant and never in a grant cycle; a failure is a TB defect
(`uvm_error sva_rvalid_legal`, knob `+gen_chk_bus_rvalid_legal`), not a DUT checker.

(v2) rtl-arch's exclusion-evidence properties (`dv/auto_dv/work/rtl-arch/gen_cover_props_draft.sv`,
to be promoted as `dv/auto_dv/tb/gen_cover_props.sv`) are bound here when component code opens:
`bind gen_dut_top gen_cover_props gen_cover_props_i (.clk_i, .rst_ni)`. Decisions: (1) the
`T022_NEVER_*` never-taken checks stay `assert ... else $error` so a reachable arc is a COLLECTED
failure (`uvm_error`-equivalent through the report hook) under one knob `+gen_chk_t022_never`
(default on in every tier); the message names itself ("exclusion candidate is REACHABLE, withdraw
it"), Runtime's verdict lists ids `T022_*` separately as exclusion-evidence failures, and a hit
fails the run until rtl-arch withdraws the exclusion and removes the property: loud on purpose.
(2) `T022_COVER_*` stay cover-only (class R evidence). (3) Compile hazards listed in its header:
hierarchical references to module-scoped enum labels are replaced by the 3-bit encodings the header
gives if VCS rejects them; the wb_stage and multdiv paths are taken through their generate scopes
(`g_writeback_stage`, `gen_multdiv_fast`) exactly as the header says; a compile check is the first
step of that integration. (4) `DV_FCOV_DISABLE` is never defined in the TB build (the RTL `fcov_*`
nets used by P4 depend on it); the build documents this in gen_component_api_binds.md.

### C11. Constants home and Python handles module

`gen_tb_pkg` (as built): plusarg names, banner tag, memory-map constants, NOP composed from
`ibex_pkg::OPCODE_OP_IMM`, mubi helper; grows with the knob names of C3-C9 and the bounds
constants (`GEN_IRQ_ENTRY_BOUND_RECORDS`, `GEN_ICACHE_ECC_WINDOW`, `GEN_ALIVE_TIMEOUT_CYCLES`).
Single source: `gen_tb_knobs.yaml` -> `gen_knobs_codegen.py` -> `gen_tb_knobs_pkg.sv` (imported by
`gen_tb_pkg`), `gen_tb/gen_knobs.py`, `gen_isa_shim_map.h` (memory map for the shim); generated
files are committed and a `--check` mode diffs them (same pattern as `gen_filelist.py`).
`gen_tb/gen_handles.py` is the only Python file that spells a hierarchical path: it builds the
bridge, alive/finish and memory-sample handles from `TOPLEVEL` and fails loudly on a missing
handle at start-up. Filesystem paths are clone-root-relative or from `ci/env.sh` exports.
The T-005 diff-review findings were applied in T-029 (generate-scope RegFile guard, unused
constants dropped, `gen_rtl.f` header); the T-029 approval left three residuals for the next touch
of the T-005 files: R-01 gen_smoke's tier status must agree between this document (compile proof,
not a measured tier) and Runtime's `gen_testlist.yaml` (currently `tier: smoke`), to be settled
with Runtime before the first measured regression (preferred: unmeasured build check); R-02 the
two new guards (`ifndef RVFI`, RegFile != RegFileFF) compiled red once each and recorded; R-03 a
range `$fatal` for `+gen_smoke_intg_flip >= MemDataWidth`.

(v2, A-25) Site dependency: every test is cocotb-master, and cocotb runs on LSF are blocked until
the clone (its `.venv` VPI library and the Python test modules) is on shared storage (intervention
log Q-012; `dv/auto_dv/evidence/gen_t010_compile_path.md` Section 1). Interim mode: cocotb runs
execute with `--local` on the submit host while pure-SV runs fan out on LSF; the Phase 1 schedule
must not assume LSF fan-out for cocotb tests until Q-012 is resolved (Runtime's shared-storage
mirror is the applied default).

### Open items and UNVERIFIED list

- Q-DL-1 (RegFileECC/ResetAll/RVFI): wrapper defaults are the proposal; one-line change.
- Q-DL-7 (half-performed misaligned stores): comparator mirrors the RTL behaviour by default.
- Q-DL-10 / Q-011 (Spike patch): not needed for the `mie` fast bits (A-14: `write_with_mask` shadow);
  kept open only for divergences found later.
- Q-1/Q-2: wrapper literal per the pre-review; `GEN_DUT_SPLIT_INTG` implements "split" if wanted.
- Bring-up confirmations owed: Zcmp record count and `rvfi_order` stepping; model decode of
  grevi/gorci non-alias immediates (shim first unit test; link test 2 did not cover them); the constants of C4.8
  (`GEN_CSR_COMMIT_TO_RVFI_OFFSET`, `GEN_RVFI_ID_EXIT_OFFSET`, `GEN_IRQ_ENTRY_BOUND_RECORDS`,
  `GEN_DBG_ENTRY_BOUND_RECORDS`, `GEN_ICACHE_ECC_WINDOW`, `GEN_ALERT_BUS_WINDOW`) measured and
  pinned by directed tests; F-RVFI-010 and F-RVFI-032 rulings from rtl-arch; B1 re-verification by
  rtl-arch. Removed from this list in v2: model byte order on misaligned store faults (A-15) and the
  `mie` write mask (A-14), both now decided by verified facts.
- Second link test (A-16): DONE (`gen_spike_linktest2.cc`, 98/98); grevi/gorci non-alias decode
  remains to be checked in the shim's first unit test.

### 6.12 Per-component API documents

Skeletons generated from the sections (`dv/auto_dv/work/tb-infra/t031/gen_apidocs_a.py`,
`gen_apidocs_b.py`); each carries purpose, files, construction, knobs, wave-level behaviour,
checker rows, failure paths, coverage hooks and open items:

- `dv/auto_dv/docs/gen_component_api_binds.md`
- `dv/auto_dv/docs/gen_component_api_bridge.md`
- `dv/auto_dv/docs/gen_component_api_constants_handles.md`
- `dv/auto_dv/docs/gen_component_api_counter_model.md`
- `dv/auto_dv/docs/gen_component_api_coverage.md`
- `dv/auto_dv/docs/gen_component_api_dbg_agent.md`
- `dv/auto_dv/docs/gen_component_api_dbus_agent.md`
- `dv/auto_dv/docs/gen_component_api_debug_checker.md`
- `dv/auto_dv/docs/gen_component_api_dut_top.md`
- `dv/auto_dv/docs/gen_component_api_env_knobs.md`
- `dv/auto_dv/docs/gen_component_api_ibus_agent.md`
- `dv/auto_dv/docs/gen_component_api_icache_ram_model.md`
- `dv/auto_dv/docs/gen_component_api_irq_agent.md`
- `dv/auto_dv/docs/gen_component_api_irq_checker.md`
- `dv/auto_dv/docs/gen_component_api_isa_shim.md`
- `dv/auto_dv/docs/gen_component_api_mem_model.md`
- `dv/auto_dv/docs/gen_component_api_misc_monitor.md`
- `dv/auto_dv/docs/gen_component_api_pmp_model.md`
- `dv/auto_dv/docs/gen_component_api_rvfi_monitor.md`
- `dv/auto_dv/docs/gen_component_api_scoreboard.md`
- `dv/auto_dv/docs/gen_component_api_scrkey_responder.md`

### 6.13 RTL fact-check of the v2 sections (rtl-arch T-051): corrections and expected values for bring-up

Source: `dv/auto_dv/work/rtl-arch/gen_arch_v2_rtl_factcheck.md` (52 statement rows with file:line;
Section 2 derives every C4.8 constant; Section 4 lists eight corrections). TB Infra accepts all
eight. They are NOT yet in the embedded v2 text above because the Critic's re-review of that file
is in flight; they land there as a v3 amendment listed in the response file (or with the requested
changes if the verdict is REQUEST-CHANGES). Until then this subsection is the binding wording.

Corrections to the checker rules:

1. `core_busy` (C4.2): the one-cycle Off dip after WFI is a `ctrl_busy` fact; `core_busy_o` also
   carries `if_busy` (outstanding fetch beats, icache invalidation) and `lsu_busy`. Rule: in
   WAIT_SLEEP `core_busy_o == Off` iff no instruction-bus beat is outstanding, no invalidation is
   active and the LSU is idle; otherwise the dip is invisible. A WFI within the first 256 cycles
   after reset (invalidation sweep active) shows no dip. Class stays exact with this qualifier.
2. Counters (C4.6, `ctr_hpm_exact` events 5/6): a misaligned load or store counts ONE (perf_load_o /
   perf_store_o only in the IDLE arm), not two.
3. `alert_bus` DATA source (C4.2): `load/store_resp_intg_err_o` is combinational on the decoded
   response (`rtl/ibex_load_store_unit.sv:756-757`), so the alert is high in the `data_rvalid_i`
   cycle of the corrupted beat and only then: class exact for both sources; `GEN_ALERT_BUS_WINDOW`
   is 0 and is removed from C4.8; the T-044 property `sva_alert_bus_iff_intg` asserts the equality
   every cycle.
4. `irq_pending` and `crash_dump` offsets (C4.4, C4.2): `GEN_CSR_COMMIT_TO_RVFI_OFFSET` splits into
   two constants: `GEN_CSR_WRITE_TO_RVFI_OFFSET` = 2 cycles for CSR-write records (the commit edge to
   the record; a WB stall delays commit and record together, so it does NOT widen) and
   `GEN_TRAP_TO_RVFI_OFFSET` = 1 cycle for trap, mret and dret records; the interrupt marker
   (`rvfi_ext_irq_valid`) follows its commit by 2. Pin edges need no offset (combinational).
5. `irq_entry` and `dbg_entry` bounds (C4.4, C4.5): records that may retire between the pin or
   request edge and the entry: the instruction in WB (1), the instruction in ID (1) and, if the ID
   instruction is a Zcmp sequence, every remaining micro-op (cm.push 14, cm.pop 14, cm.popret 15,
   cm.popretz 16 records). `GEN_IRQ_ENTRY_BOUND_RECORDS` = `GEN_DBG_ENTRY_BOUND_RECORDS` = 17 worst
   case, 2 nominal; the WFI path adds 3 cycles and no record. Cycle form for the T-044 SVA:
   `17 * (gnt_max + rvalid_max + 2) + 40` derived from the agent knobs instead of the 4096 placeholder.
6. Zcmp records (C4.1): `rvfi_order` advances per micro-op record (static agreement; sim confirms).
7. BUG-04 policy (C4.7, C5.2): when a WB load/store error coincides with an ID-stage trap, expect
   the WB error's trap record now and the ID instruction's own record later (it re-executes); no
   "lost" record is modelled.
8. `icram_inval_sweep` anchor (C3.4): with `+gen_key_reset_valid=0` the 256 invalidation writes start
   only after the responder raises `ic_scr_key_valid_i`; the sweep is anchored at the key-valid edge,
   not at reset release.

Predicted C4.8 values (bring-up confirms these instead of measuring blind; each is pinned by the
directed test the fact-check names):

| Constant | Predicted | Derivation anchor | Directed confirmation |
|---|---|---|---|
| `GEN_CSR_WRITE_TO_RVFI_OFFSET` | 2 cycles | `csr_op_en` at `instr_id_done` (`rtl/ibex_id_stage.sv:747-749`), record at N+2 | csrw mie then csrr; record two cycles after `mie_q` changes |
| `GEN_TRAP_TO_RVFI_OFFSET` | 1 cycle | `csr_save_cause_o` in FLUSH (`rtl/ibex_controller.sv:845`), record at N+2 | any synchronous trap; crash_dump fields one cycle before the record |
| interrupt marker offset | 2 cycles | IRQ_TAKEN in N+1, marker output in N+3 | pin edge with the pipe empty |
| `GEN_RVFI_ID_EXIT_OFFSET` | 2 cycles; 2 + W for loads and stores (W = WB wait for the response, bounded by `gnt_max + rvalid_max`, twice for a split access) | `rvfi_ext_stage_mcycle[0]` sampled at the stage-0 load (`rtl/ibex_core.sv:2102`) | nop stream gives 2; a load under `+gen_dbus_rvalid_min/max=4` gives 2 + 3 |
| `GEN_IBUS_MAX_OUTSTANDING` / `GEN_DBUS_MAX_OUTSTANDING` | 8 / 2 | NUM_FB 4 x IC_LINE_BEATS 2; LSU split rule | slow-rvalid / fast-gnt regime after a branch |
| `GEN_ICACHE_ECC_WINDOW` | alert in the corrupted-rdata cycle (0 from rdata, 1 from the lookup request); invalidation write one cycle later | `ecc_err_ic1` combinational (`rtl/ibex_icache.sv:585`), `alert_minor_o` (`rtl/ibex_core.sv:1337`) | one injected tag error, one data error on the hitting way; T-044 `sva_alert_minor_window` tightened to exactly 1 |
| `GEN_ALERT_BUS_WINDOW` | 0 (removed; exact) | `rtl/ibex_if_stage.sv:282`, `rtl/ibex_load_store_unit.sv:756-757` | injected fetch and data corruption |
| `GEN_IRQ_ENTRY_BOUND_RECORDS`, `GEN_DBG_ENTRY_BOUND_RECORDS` | 17 worst case, 2 nominal | controller entry conditions (`rtl/ibex_controller.sv:704-720`), Zcmp expansion | interrupt raised with cm.popretz {ra, s0-s11} in ID; WFI wake |
| `GEN_ICACHE_NUM_FB` | 4 (the one re-typed localparam, `rtl/ibex_icache.sv:72`; not exported, so no static assert) | - | - |

## 7. Open questions with defaults (as they stand in `dv/auto_dv/docs/gen_intervention_log.md`)

| Id | Question (condensed) | Default applied while pending | Status |
|---|---|---|---|
| Q-002 (revised) | `gen_dut_top` build choices that fix the DUT boundary: RegFileECC = 0 with RegFileDataWidth = 32 (lockstep-only ECC outside the DUT), ResetAll = 1, `+define+RVFI`, MemECC = 1 (39-bit bus data), DummyInstructions = 1, ICacheTweakInfection = 1, DbgHwBreakNum = 1, Dm* defaults, CsrMvendorId = CsrMimpId = 0, PMP reset values from `ibex_pkg` | exactly the proposal; the config banner prints every value; LOG-004 keeps the 39-bit ports literal (split is TB-side, `GEN_DUT_SPLIT_INTG` opt-in) and no clock gate | pending |
| Q-008 (Q-DL-7, MEM-13) | after a PMP fault on the first half of a misaligned access Ibex still performs the permitted second half on the bus | model it as RTL-defined; cover `pmp_fault x {aligned, mis_first, mis_second, mis_both} x {load, store}`; bug log carries a security/integration note, not a bug | pending |
| Q-009 (Q-DL-8, CTRL-04) | with `fetch_enable_i` not exactly On, interrupt and debug entry still update mepc/mcause/dpc and the pc; invalid MuBi encodings act as Off with no alert | check the RTL behaviour as-is, cover both cases, record both as design notes, no bug filed | pending |
| Q-010 (Q-DL-9, MEM-05/19) | neither bus defends against an unsolicited `rvalid` or one in the grant cycle | passing tests never violate the protocol (agents enforce, `sva_rvalid_legal` checks); one directed informational test per bus, excluded from the pass gate | pending |
| Q-011 (Q-DL-10) | may a local patch file against the pinned Spike be carried when a legalization cannot live in the shim | allowed as a justified patch file under `dv/auto_dv/tools/`, never a fork; the shim remains first choice. Retired for the `mie` fast-bit item: `gen_mie_csr_t` needs no patch (link test 2). B14/BUG-04 (`rvfi_id_done` suppressing a trap record) noted for the comparator | pending |
| Q-012 | the clone lives on local NVMe of the submit host; LSF compute hosts cannot see it | out-trees under the shared `GEN_DV_OUT_ROOT`; the team builds a shared-storage mirror (rsync without .git and out-trees, venv from `ci/requirements.lock`) for LSF jobs; cocotb runs use `--local` until then | pending |
| Q-013 | tool-mandated fixed filenames versus the `gen_` prefix landing rule | committed sources carry the `gen_` prefix; `gen_program.py` materializes the fixed-name riscv-dv target out of tree at flow time | pending |

TB-Infra-level defaults recorded in the scoping notes and not escalated: Q-2 no clock gate in the
wrapper (`core_busy_o` exposed); Q-4 debug program linked at the real `DmHaltAddr` (no alias
needed since T-025); Q-5 RVFI classified as a boundary interface (ruled); Q-6 riscv-dv user
extension emits the MMIO interrupt acknowledge store.

## 8. DV Lead notes

Adopted 2026-09-03 07:04 UTC. TB Infra's Sections 1-7 are taken as written; the items below are the DV Lead's
additions, rulings and disagreements. Each names the section it qualifies; TB Infra revises its v2
component sections file, not this document, and the DV Lead re-adopts.

### 8.1 Rulings recorded in this document
1. Coverage scope (Section 5): two inner instances measured; wrapper reported informationally.
2. `-cm_glitch 0` (Section 5): adopted for every measured build; baseline re-measured.
3. Wrapper ports stay literal to the DV_prompt Section 2 ruling (LOG-004): `instr_rdata_i`,
   `data_rdata_i`, `data_wdata_o` are the 39-bit ports of `ibex_core` with integrity in bits [38:32];
   the `*_intg` split lives in the TB bus interface (`GEN_DUT_SPLIT_INTG` opt-in). This amends the DV
   Lead's reading-report note 6a (which had decided a split at the wrapper); observability is unchanged.
4. No clock gate in the wrapper; `core_busy_o` is the sleep observable (tb-infra Q-2, unchanged).
5. Checker direction for bug candidates follows dv/auto_dv/docs/gen_bug_log.md: spec-violation rows
   (B1/BUG-06, B2/BUG-01, B3, B5, B15/BUG-03) with the ISA model and checkers following the specification
   and the carrying test-plan items `expected-fail`; RTL-defined rows (B6 reclassified, B9 under
   out-of-spec stimulus, S1..S3, D1..D19) with the model following the RTL. B12 (mret clears
   sync_exc_seen) is documented behaviour (exception_interrupts.rst:191, cs_registers.rst:556) and is
   carried as a design-weakness note for the security owner, not as expected-fail. B14/BUG-04 is
   downgraded to an RVFI convention note pending its confirmation simulation (rtl-arch T-041 and the
   fact-check row 48): the comparator expects the WB error's trap record now and the killed ID
   instruction's own record after the handler; one record would re-open it.

### 8.2 Corrections from rtl-arch's RTL fact-check (gen_arch_v2_rtl_factcheck.md Section 4) that TB Infra applies to Section 6 and the C4.8 exactness table
1. `core_busy` (row 29): the one-cycle Off dip after WFI is a `ctrl_busy` fact; `core_busy_o` also
   carries `if_busy` (outstanding fetch beats, icache invalidation) and `lsu_busy`. Rule: in WAIT_SLEEP
   `core_busy_o == Off` iff no instruction-bus beat is outstanding, no invalidation is active and the
   LSU is idle; otherwise the dip is invisible (a WFI within 256 cycles of reset sees no dip). The
   feature list's F-DBG-044/059 and F-IRQ-051 state the `ctrl_busy` view and will carry this port
   rule in v3 (feature-list alignment item, Critic C-06 / A-10).
2. Counters (row 42): misaligned loads/stores count 1 (events 5/6); `ctr_hpm_exact` models one per
   instruction (feature list D6, F-PMC-034/036 agree).
3. `alert_bus` data source (row 26, Section 2.5): same-cycle, exact; `GEN_ALERT_BUS_WINDOW` = 0 or
   removed.
4. Commit-to-record offsets (rows 28, 35, Section 2.1): `GEN_CSR_COMMIT_TO_RVFI_OFFSET` is a fixed 2
   for CSR-write records and does not widen under WB stalls; trap/mret/dret records use 1; the
   interrupt marker 2. Two constants or a per-class table; the crash_dump compare uses the same
   per-class values.
5. Entry bounds (row 36, Section 2.6): nominal 2 records, worst case 17 (a Zcmp sequence of up to 16
   micro-op records plus the WB instruction); the WFI path adds 3 cycles and no record. The test plan's
   irq/debug entry-latency items (TP-IRQ / TP-DBG bound items) adopt the record-based bound.
6. Zcmp records (row 44): `rvfi_order` advances per micro-op record (static-agreed; one sim confirms).
7. BUG-04 policy (row 48): see 8.1 item 5.
8. Invalidation sweep anchor (row 17): with `+gen_key_reset_valid=0` the 256 writes start at the
   key-valid edge, not at reset release.
Predicted constants for bring-up (fact-check Section 2): `GEN_CSR_COMMIT_TO_RVFI_OFFSET` 2 / 1 per
class, `GEN_RVFI_ID_EXIT_OFFSET` 2 (+ W for loads/stores), `GEN_IBUS_MAX_OUTSTANDING` 8,
`GEN_DBUS_MAX_OUTSTANDING` 2, `GEN_ICACHE_ECC_WINDOW` 1 from the corrupted-rdata cycle,
`GEN_ALERT_BUS_WINDOW` 0, entry bound 17 records. T-044 property changes: derive
`DBG_ENTRY_BOUND_CYCLES` from the agent knobs (17 x (gnt_max + rvalid_max + 2) + 40) or use the
record-based checker; tighten `sva_alert_minor_window` to exactly 1; mark `alert_bus` exact.

### 8.3 Alignment items between this document and the plan set
1. `rvfi_trap` is 0 on an ebreak that enters debug mode (rtl/ibex_core.sv:1885-1886; Critic
   pre-review S-2). Checker and counter-model rule: the debug path is identified by
   `is_ebreak(rvfi_insn) && !rvfi_trap && next fetch == DmHaltAddr`; the exception path by
   `rvfi_trap = 1`; an ebreak-into-debug record is not counted in minstret (rtl/ibex_id_stage.sv:1218).
   The DBG test-plan items and F-DBG-017 are corrected to this rule in the consolidation.
2. Store-integrity checker scope (tb-infra C3.2, Critic C-10 item 4): `dbus_store_intg` checks
   `data_wdata_o[38:32]` on stores only (req & gnt & we), over the full rotated word including
   disabled lanes; on loads it records the RTL's always-valid encoding as the coverage observation
   `gen_dbus_cg.cp_load_wdata_intg_valid` and never errors. The feature list's F-DMEM-050 (added for
   MEM-15) is an RTL-defined observation, not an architectural requirement; F-DMEM-035 (load wdata
   don't-care architecturally) stands. Both are aligned in v3.
3. Requested checkers beyond Section 6 (gen_test_plan.md Section 2): gen_chk_bitmanip_ref (draft-0.93
   bitmanip reference for the ops Spike lacks; TB Infra's C5 draft-B policy covers it as the shim's C
   reference result), gen_chk_rvfi_proto (RVFI self-consistency), gen_chk_zcmp_seq, gen_chk_timing_isa,
   gen_chk_trap_timing, gen_chk_csr_flush, gen_chk_exc_flush, gen_chk_regime, gen_chk_reset,
   gen_sva_multdiv (F-MUL-028), gen_sva_csr_excl. TB Infra maps each onto an existing checker id or adds
   a row with mutation classes and a disable knob; the DV Lead accepts the mapping in the next
   re-adoption.
4. Regime knobs: gen_fcov_plan.md Section REG names 19 knobs (`+gen_knob_<name>`); Section 4.2 here
   uses `+gen_<agent>_regime=<name>` with `+gen_regime_pin` and `+gen_regime_sched`. These are the same
   layer-2/3 controls; TB Infra's `gen_knobs.py` codegen is the single source and the coverage plan's
   knob names are mapped onto it (name mapping recorded in gen_component_api_env_knobs.md).
5. Probe register: the coverage plan's probe candidates P1..P7 map onto the register's entries (P1
   accepted coverage-only, P2/P3/P5 rejected, P4 conditional, P6 off); P7 (dummy_instr_seed_en/_o, CSR
   part) needs an entry or a rejection. Test-plan items whose bins are P1-gated do not list those bins
   as must-hit until the register carries P1 (Critic pre-review S-14).
6. Program conventions (T-023, dv/auto_dv/evidence/gen_t023_stimulus_toolchain.md Section 6) are the
   ones the test plan's preconditions assume: boot entry at `boot_addr_i + 0x80` jumping to `_start`,
   `.text` at 0x80000100, `.debug_rom` at `DmHaltAddr`, `tohost` in `.data`, `mtvec_handler` 256-byte
   aligned; riscv-dv limited to ratified Zb*; fast interrupts, NMI, Zcb/Zcmp and draft-B ops as TB or
   directed stimulus.
7. Cross-model finding on the T-005 plan (dv/auto_dv/reviews/2026-09-03-claude-plan-gen_tb_scoping_notes.md
   finding 1) is applied by 8.1 item 3.

### 8.4 Open items the DV Lead carries
- Q-002 (wrapper parameters) confirmation; Q-008..Q-011 defaults in force; Q-012 storage mirror.
- F-CHERI-001 mirrors rtl-arch's exclusion file: rows 37-40 (Zcmp class-R arcs) stay out of the
  exclusion file until simulation covers pass; class-D rows follow the Critic's T-020 ruling 2; the
  table is re-aligned when the exclusion v2 draft lands (rtl-arch T-022).
- Runtime: state in the config banner whether the VCS build defines `SIMULATION` (prim_lfsr default
  seed randomisation, F-DIT-025).
