# Component API: gen_icache_ram (tag and data RAM models with ECC injection)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C3.4; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

Transparent synchronous single-port RAMs for the core's `ic_tag_*` / `ic_data_*` ports, one
instance per way, with fault injection and RAM-side checks. The core generates the ECC bits and
the address-derived tweak; the model stores bits verbatim (it replaces ibex_top's scrambled
`prim_ram_1p_scr`, which is test equipment by ruling).

## 2. Files (planned) and how to call it

`dv/auto_dv/tb/gen_icache_ram.sv` (module, parameters `Width`, `Depth = IC_NUM_LINES`; one
per way for tags with `TagSizeECC`, one per way for data with `LineSizeECC`), control class
`gen_icache_ram_ctl` (in `uvm_config_db`), interface `gen_icram_if` for the monitor/checkers.

Instantiated in `gen_tb_top` on the wrapper's RAM ports. Injection: `ctl.arm(way, index, kind =
TAG|DATA, bits = 1|2, when = NEXT_LOOKUP|INDEX_MATCH)`, driven by the bridge command
ICACHE_ECC_ARM or by the regime rate.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_icram_init=zero|random` | `PLUSARG_ICRAM_INIT` | initial contents (the reset invalidation sweep makes tags irrelevant; data of never-hit lines is never consumed) | random |
| `+gen_icram_ecc_rate=<per_mille>` | `PLUSARG_ICRAM_ECC_RATE` | per-lookup injection probability per regime | 0 |
| `+gen_icram_ecc_bits=1|2` | `PLUSARG_ICRAM_ECC_BITS` | bits flipped per injection | 1 |
| `+gen_chk_icram_write_ecc / _inval_sweep / _ecc_response` | `PLUSARG_CHK_*` | checker enables | 1 |

## 4. Wave-level behaviour

Read data valid the cycle after `req & ~write` and held until the next read (registered read,
exactly `prim_ram_1p`; the core samples in IC1). Writes on `req & write` take effect at the same
edge. The invalidation sweep (256 tag writes after reset and after every fence.i, plus data writes
of encoded zeros when a lookup coincides) is accepted silently. Injection flips the chosen bits in
the read data of the chosen way at the chosen lookup; the core must miss, refetch, write the line
invalid and pulse `alert_minor_o`.

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `icram_write_ecc` | every written tag/data word, un-tweaked with the model's copy of the address-derived tweak, decodes with zero syndrome | tag/data encoders and tweak application (`rtl/ibex_icache.sv:290-310, 321-454`) | `+gen_chk_icram_write_ecc=0` |
| `icram_inval_sweep` | after reset release and after every retired fence.i, all 256 tag indices of every way are written invalid before any allocation write | invalidation FSM (`rtl/ibex_icache.sv:1204-1268`) | `+gen_chk_icram_inval_sweep=0` |
| `icram_ecc_response` | an injected error at (way, index) is followed within `GEN_ICACHE_ECC_WINDOW` cycles by exactly one `alert_minor_o` pulse and an invalidation write to that index; a miss fill follows | ECC check and correction-write path (`rtl/ibex_icache.sv:538-644`), `alert_minor_o` (`rtl/ibex_core.sv:1337`) | `+gen_chk_icram_ecc_response=0` |

## 6. Failure path and diagnostics

`uvm_error` per id; `uvm_fatal ICRAM_PORT` on X on `req`/`write`/`addr` after reset (protocol-
impossible). Debug behind `+gen_dbg_icram=1`.

## 7. Coverage hooks

`gen_icram_cg`: lookups per way, allocations, invalidation sweeps (reset / fence.i), ECC
injections (tag/data x bits) and their responses, hit/miss derivation feed for P2.

## 8. At build

Verify the tweak reproduction against the first waveforms (if the tweak cannot be reproduced,
drop `icram_write_ecc` and record why); measure `GEN_ICACHE_ECC_WINDOW`.
