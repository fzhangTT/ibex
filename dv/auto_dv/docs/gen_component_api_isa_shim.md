# Component API: gen_isa_shim (Spike DPI-C shim and legalization layer)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C5; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

Upstream Spike (pinned 4ffd6ba860f4190ceac2716fa3c2cf139e85538f, `tools/spike`) as a step-locked
library behind DPI-C: one `processor_t` over our own `simif_t` (memory image, MMIO windows, fault
injection), stepped once per RVFI record, with a legalization layer for every Ibex WARL and
platform rule the model lacks.

## 2. Files (planned) and how to call it

`dv/auto_dv/isa/gen_isa_shim.cc` (C++20, built as `libgen_isa_shim.so` with only
`tools/spike/include` on the include path, loaded through `-LDFLAGS`), `gen_isa_shim_map.h`
(generated memory map), `dv/auto_dv/env/gen_isa_dpi.sv` (imports). Feasibility: `dv/auto_dv/
evidence/gen_t019_spike_build.md` (14/14 API link test).

DPI exports: `gen_isa_reset(cfg)`, `gen_isa_arm_async(pre_mip, taken_cause, nmi, nmi_int, debug_req,
irq_valid)`, `gen_isa_arm_fault(kind, addr, size)`, `gen_isa_note_memory_write(addr, data, be)`,
`gen_isa_step(txn_in, txn_out)` (returns the number of instructions the model retired in that step: 0 for a
step that only took an interrupt, trigger or synchronous trap, 1 otherwise; the scoreboard asserts it per
record class, C5.2, v2 XM-M2), `gen_isa_exec_reference(insn, rs1, rs2, rd_out)` (draft-B ops),
`gen_isa_read_csr(addr)`, `gen_isa_read_gpr(idx)`, `gen_isa_write_csr(addr, val)`,
`gen_isa_set_time(mcycle)`. Called only by gen_scoreboard.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_isa_string=<isa>` | `PLUSARG_ISA_STRING` | model ISA string; the single definition is `GEN_ISA_STRING` in the generated `gen_isa_shim_map.h`, shared with `gen_program.py` (v2 XM-L2); the plusarg only overrides for debug | GEN_ISA_STRING = rv32imc_zicsr_zifencei_zba_zbb_zbc_zbs_zca_zcb_zcmp_zicntr_zihpm_zicclsm |
| `+gen_isa_log=<path>` | `PLUSARG_ISA_LOG` | model commit log for debug (empty = /dev/null) | unset |

## 4. Wave-level behaviour

Model state is 64-bit sign-extended for RV32: every compared value is truncated to 32 bits at the
DPI boundary. Interrupts (A-14, XM-M1, verified in the pinned source): `mie_csr_t::write_mask()` never
admits bits 16..30 (csrs.cc:993-1001) and `mip_or_mie_csr_t::unlogged_write` is `final` and applies it
(csrs.h:373-383), so the shim defines `gen_mie_csr_t : public mie_csr_t` overriding the private virtual
`write_mask()` to add bits 16..30 (`GEN_IRQ_FAST_MASK`) and installs one instance in `state.mie` and
`state.csrmap[CSR_MIE]` at `gen_isa_reset` (no patch); program `csrw mie` then takes effect and
`take_interrupt` sees the fast bits. Spike's `select_an_interrupt_with_default_priority`
(processor.cc:258-262) already ranks nonstandard bits above MEI > MSI > MTI and picks the lowest set bit,
matching Ibex, so no priority emulation exists; `mip` is set to the raw `pre_mip` with
`backdoor_write_with_mask`, and the model's `mcause` after the entry step is compared with the DUT's.
Step rule (XM-M2): a step that takes an interrupt, a trigger or a synchronous trap retires 0
instructions, so interrupt and debug entries take an entry step plus a step for the handler's first
instruction; `gen_isa_step` returns the retired count. Debug entry (link test 2): `enter_debug_mode`
is private, so the shim sets `halt_request = HR_REGULAR` and steps; the step enters debug mode, then
fetches the Spike ROM entry 0x800, which is unbacked, so the fetch fault inside debug mode parks pc at
DEBUG_ROM_TVEC (0x808) with nothing retired and no mcause/mepc change; the shim then sets pc =
DmHaltAddr and clears `halt_request` (Spike never clears it). A trigger entry likewise retires 0 and
needs the same pc override. Memory (A-15, corrected by link test 2): with `addr_to_mem` NULL a
naturally aligned access reaches `mmio_load/store/fetch` as ONE full-length call, but `mmu_t::mmio`
(mmu.cc:168-184) splits a misaligned access into single-byte calls in address order and stops at the
first failing byte. The shim therefore implements Ibex's per-word rule per byte (a byte belongs to
word `addr & ~3`; a byte of a denied word fails), which performs exactly the permitted first word and
faults on the second (BS MEM-13); Spike then reports `mtval` = the original EA for both halves, so for
a second-word fault the shim overrides `mtval` to the aligned second word after the step from its own
record of the failing byte (`put_csr(CSR_MTVAL)` accepted). Legalization (component sections C5.3a, RTL-defined rows): reset values
(mstatus 0x80, prv M, PMP all OFF, mtvec = boot page | 1, pc = boot + 0x80); mip raw; mtvec MODE 01
and BASE[7:2] = 0; misa read-only; mstatus MPP 01/10 -> U; mcounteren 13 bits gated by
mcounteren_writable_i; counters excluded from the ISS compare; NMI and internal NMI emulated (cause
0x8000001F / 0xFFFFFFE0, vector base + 0x7C, mstack); debug entry pc override to DmHaltAddr /
DmExceptionAddr; one trigger; zicclsm; cpuctrlsts/secureseed as own `csr_t` subclasses provided through
`extension_t::get_csrs` (tools/spike/include/riscv/extension.h:16, XM-I1) into `state.csrmap`: the extension is
named `genibex` (ISA-string extension names cannot contain underscores: the parser splits on `_`, disasm/
isa_parser.cc:331-336) and the CSRs enter `csrmap` only in the `reset()` that `gen_isa_reset` calls after
construction (the constructor's own reset runs before extensions are registered, processor.cc:80-85), so
`gen_mie_csr_t` is installed after that reset; time(h) entries replaced by a trapping `csr_t` (A-17); WFI in_wfi handling. NOT
legalized (C5.3b spec-violation rows, model follows the spec, tests expected_fail): B1 dret MPRV,
B2/BUG-01 MPRV in debug with mprven = 0, BUG-03 dcsr.ebreaks (Spike forces 0, csrs.cc:1625), B3
tdata3/mcontext/scontext trapping, B5 dcsr.nmip.

## 5. Checkers

None: this component carries no pass/fail check (test equipment or infrastructure).

## 6. Failure path and diagnostics

The shim never fails on its own: it returns status codes and field diffs; the scoreboard raises
`uvm_error isa_<field>`; a model-side abort at reset (bad ISA string, bad cfg) is reported as
`uvm_fatal ISA_INIT`.

## 7. Coverage hooks

None directly (the scoreboard samples compare outcomes).

## 8. At build

Second link test (A-16) DONE: `dv/auto_dv/work/tb-infra/gen_spike_linktest2.cc`, 98/98 checks
(`dv/auto_dv/work/tb-infra/out_linktest2/linktest2.log`; evidence `dv/auto_dv/evidence/gen_t046_spike_linktest2.md`): fast interrupt through `gen_mie_csr_t` with Ibex's priority and
retired counts 0 then 1, custom CSRs through `extension_t::get_csrs`, wfi/in_wfi, halt_request entry,
tdata1 from debug mode + dret + execute trigger, cm.push with one `log_mem_write`, aligned and
misaligned `mmio_store` (byte split, mtval override). Still before coding: verify grevi/gorci non-alias
decode; write the C5.3a/C5.3b tables into this document as rows with an RTL cite and a test each (R-2).
