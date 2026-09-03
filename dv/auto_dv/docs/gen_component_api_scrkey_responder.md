# Component API: gen_scrkey_responder (scramble-key handshake)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C3.5; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

Answers the core's one-cycle `ic_scr_key_req_o` pulses on `ic_scr_key_valid_i`, standing in for
ibex_top's key logic and the OTP key provider.

## 2. Files (planned) and how to call it

`dv/auto_dv/tb/gen_scrkey_if.sv`, `dv/auto_dv/env/gen_scrkey_pkg.sv` (`gen_scrkey_cfg`,
`gen_scrkey_item` {delay_cycles, reset_valid}, driver, monitor, sequencer).

Config from plusargs; bridge command KEY_MODE changes the regime at run time.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_key_reset_valid=0|1` | `PLUSARG_KEY_RESET_VALID` | value of ic_scr_key_valid_i out of reset (1 = ibex_top behaviour; 0 forces a request at reset) | 1 |
| `+gen_key_delay_min/max=<n>` | `PLUSARG_KEY_DELAY_MIN/MAX` | cycles valid stays low after a request | 1 / 20 |
| `+gen_key_regime=immediate|short|long|never_window` | `PLUSARG_KEY_REGIME` | distribution set | short |
| `+gen_key_never_cycles=<n>` | `PLUSARG_KEY_NEVER_CYCLES` | length of the never_window (key withheld) | 0 |
| `+gen_chk_scrkey_proto` | `PLUSARG_CHK_SCRKEY_PROTO` | checker enable | 1 |

## 4. Wave-level behaviour

On the one-cycle `req` pulse, drop `valid` the next cycle, hold it low for the drawn delay,
raise it and hold until the next pulse. A fence.i during AWAIT_SCRAMBLE_KEY produces no new pulse
(rtl-arch AN s9), so back-to-back pulses never occur. Fetch is never blocked by an invalid key
(pass-through); nothing is cached while the key is invalid.

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `scrkey_proto` | `req` is a single-cycle pulse; no `req` while a request is pending and `valid` is still 0; `cpuctrlsts.ic_scr_key_valid` (RVFI CSR reads, `rvfi_ext_ic_scr_key_valid`) equals the pin registered by one cycle | inval FSM request logic (`rtl/ibex_icache.sv:1220-1264`), cs_registers key-valid flop (`rtl/ibex_cs_registers.sv:1938-1949`) | `+gen_chk_scrkey_proto=0` |

## 6. Failure path and diagnostics

`uvm_error scrkey_proto` with cycle and state. Debug behind `+gen_dbg_scrkey=1`.

## 7. Coverage hooks

`gen_scrkey_cg`: request cause (reset, fence.i, fence.i during invalidation), delay bins, regime,
key-invalid windows overlapping fetches.

## 8. At build

Confirm the pulse timing against the first waveform; cover valid tied high (no request at
reset).
