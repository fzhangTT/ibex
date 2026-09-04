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
platform rule the model lacks. AS BUILT (step 2a): `dv/auto_dv/isa/gen_isa_shim.h` (C ABI), `gen_isa_shim.cc` (implementation and the scalar DPI wrappers `gen_isa_reset_dpi`, `gen_isa_step_dpi`, `gen_isa_is_draft_b`), `gen_isa_dpi_pkg.sv` (imports), `gen_isa_shim_build.sh` (`lib`: libgen_isa_shim.so next to the simv, linked with `-LDFLAGS "-L<out>/lib -lgen_isa_shim -Wl,-rpath,<out>/lib"`; `test`: the C++ unit test). The shim owns a sparse word memory loaded from the same .vmem (every access is MMIO to Spike), legalizes reset (pc, mtvec, mstatus 0x80, PMP off, misa fixed to the RTL's MISA_VALUE through a constant csr_t, time/timeh trapping), installs `gen_mie_csr_t` and the `genibex` extension (cpuctrlsts 8 writable bits, secureseed), legalizes mtvec and mcounteren after each step (a logged CSR address `get_csr` rejects, e.g. mtval2 on traps, is recorded unlegalized), reports retired count, trap cause/tval, rd write, first memory access and the CSR write list per step, parks debug entry at DmHaltAddr, and computes grev/gorc for `gen_isa_exec_reference` (the other draft-B ops arrive with their directed tests). Unit test `gen_ut_isa_shim.cc` (51 checks) and transcript `dv/auto_dv/evidence/gen_tdd_isa_shim.md`.

## 2. Files (planned) and how to call it

`dv/auto_dv/isa/gen_isa_shim.cc` (C++20, built as `libgen_isa_shim.so` with only
`tools/spike/include` on the include path, loaded through `-LDFLAGS`), `gen_isa_shim_map.h`
(generated memory map), `dv/auto_dv/env/gen_isa_dpi.sv` (imports). Feasibility: `dv/auto_dv/
evidence/gen_t019_spike_build.md` (14/14 API link test).

DPI exports: `gen_isa_reset(cfg)`, `gen_isa_arm_async(pre_mip, taken_cause, nmi, nmi_int, debug_req,
irq_valid)`, `gen_isa_arm_fault(kind, addr, size, tval)`, `gen_isa_note_memory_write(addr, data, be)`,
`gen_isa_step(txn_in, txn_out)` (returns the number of instructions the model retired in that step: 0 for a
step that only took an interrupt, trigger or synchronous trap, 1 otherwise; the scoreboard asserts it per
record class, C5.2, v2 XM-M2), `gen_isa_exec_reference(insn, rs1, rs2, rs3, rd_out)` (draft-B ops: grev/gorc, slo/sro, shfl/unshfl, xperm, cmov/cmix, fsl/fsr/fsri, bfp, crc32 and crc32c, pack/packu/packh; T-102),
`gen_isa_read_csr(addr)`, `gen_isa_write_csr(addr, val)`, `gen_isa_set_time(mcycle)` (one 64-bit counter write; a second write before a step trips Spike's assert), `gen_isa_set_hpm(idx, lo, hi)` and `gen_isa_set_status(ic_scr_key_valid)` (T-102 syncs from the record); the step record carries `prv_before` (the privilege the instruction executed in) beside `prv`; GPR and pc
accessors `gen_isa_read_gpr(idx)`, `gen_isa_write_gpr(idx, val)`, `gen_isa_get_pc()`, `gen_isa_set_pc(pc)`,
`gen_isa_is_draft_b(insn)`; per-step log accessors (T-068) `gen_isa_reg_write(i, idx, val)` (the i-th
integer register write of the last step), `gen_isa_mem_write(i, addr, data, size)`,
`gen_isa_mem_read(i, addr, data, size)` and `gen_isa_fetch_insn(pc)` (the instruction the model fetches at
pc). Called only by gen_scoreboard.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_isa_string=<isa>` | `PLUSARG_ISA_STRING` | model ISA string; the single definition is `GEN_ISA_STRING` in the generated `gen_isa_shim_map.h`, shared with `gen_program.py` (v2 XM-L2); the plusarg only overrides for debug | GEN_ISA_STRING (gen_tb_knobs.yaml isa_string; currently rv32imc_zicsr_zifencei_zba_zbb_zbc_zbs_zca_zcb_zcmp_zicntr_zihpm_zicclsm_smepmp: smepmp because Ibex implements mseccfg) |
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
needs the same pc override. Memory (A-15, corrected by link test 2): with `addr_to_mem` NULL
every access is served byte-wise through `mmio_fetch/load/store` over the shim's sparse memory (an
aligned access arrives as one full-length call, a misaligned one as single-byte calls in address order
that stop at the first failing byte, `mmu_t::mmio`, mmu.cc:168-184; the shim serves each call byte by
byte from its word map), and an armed bus fault (`gen_isa_arm_fault`) applies to the bytes it covers; its `tval` is written to mtval after the
faulting step (the DUT's failing-transaction address, gen_component_api_scoreboard.md; Spike's own tval is the effective address).
NOT implemented (T-068): the per-word PMP rule (perform the permitted first word, fault the second, BS
MEM-13) and the mtval override to the aligned second word; both are owed with the misaligned-access
directed test (C5.4 pending). Legalization (component sections C5.3a, RTL-defined rows; the per-row
built or deferred status is Section 4a): reset values
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

## 4a. C5.3a / C5.4 rows: built or deferred (T-068)

| Row | Status | Where / note |
|---|---|---|
| reset values (pc, mtvec, mstatus 0x80, prv M, PMP off, mie/mcause/mepc/mtval/mscratch 0) | BUILT | `legalize_after_reset` |
| mie fast bits 16..30 | BUILT | `gen_mie_csr_t` |
| misa read-only Ibex value | BUILT | `gen_const_csr_t` |
| time/timeh trapping | BUILT | `gen_trap_csr_t` |
| mtvec BASE[7:2] = 0, MODE = 1 | BUILT | `legalize_csr_write` |
| mcounteren 13 bits gated by mcounteren_writable | BUILT | `legalize_csr_write` |
| cpuctrlsts 8 writable bits and secureseed | BUILT | `genibex` extension |
| debug entry parked at DmHaltAddr | BUILT | `gen_isa_step` |
| mip injection from pre_mip | BUILT | `gen_isa_arm_async` |
| smepmp (mseccfg) | BUILT | via the ISA string |
| mstatus MPP legalization (01/10 -> U) | DEFERRED | - |
| mhpmevent3..31 read-only Ibex values (event bit i-3 for the `GEN_MHPM_COUNTER_NUM` implemented counters, 0 beyond) | BUILT (T-102) | `legalize_after_reset`, `gen_const_csr_t` |
| mcountinhibit mask | DEFERRED | - |
| marchid = `GEN_CSR_MARCHID_VALUE` (ibex_pkg) | BUILT (T-102) | `legalize_after_reset`, `gen_const_csr_t` |
| mhpmcounter3..(3+N-1) and the hpmcounter aliases synced from RVFI (`gen_isa_set_hpm`) | BUILT (T-102) | `gen_masked_csr_t` holders, `counter_proxy_csr_t` aliases |
| mcycle synced from RVFI (`gen_isa_set_time`, one 64-bit write) | BUILT (T-102; the two-write form asserted in Spike and was never called before) | `gen_isa_set_time` |
| mstatus without XS/SD (Spike sets XS for a custom extension; Ibex has none) | BUILT (T-102) | `gen_mstatus_view_t` on the csrmap entry, the inner object stays the privilege state |
| cpuctrlsts bit 8 = ic_scr_key_valid from RVFI (`gen_isa_set_status`) | BUILT (T-102; an RVFI-consistency anchor until scrkey_proto) | `gen_cpuctrl_csr_t` |
| cpuctrlsts bits 6/7 (sync_exc_seen, double_fault_seen, `GEN_CPUCTRLSTS_*_BIT`) set from the model's own synchronous exceptions outside debug mode, sync_exc_seen cleared by mret, both software-writable | BUILT (T-102b, T-102c: exceptions taken in debug mode and debug entry set nothing; unit case section 9) | `gen_cpuctrl_csr_t::set_flags`, unit test sections 7 and 9 |
| armed bus fault (`gen_isa_arm_fault(GEN_ISA_FAULT_KIND_LOAD / _STORE, addr, size, tval)`) applies to the next step only and leaves `tval` in mtval (unit test section 13); the comparator arms it for a trapping load/store record ONLY when gen_bus_driver announced a bus error for that word (T-137, `gen_bus_err_log`), otherwise the model decides (a PMP denial is Spike's own) | BUILT (T-102c; conditioned T-137) | `fault_hits`, `gen_isa_step` |
| mtval = 0 on a breakpoint exception ([c.]ebreak): Ibex writes 0, Spike the pc, both spec-legal (rtl-arch R10, rtl/ibex_controller.sv:550, :894-897) | BUILT (this landing; unit test section 8, red 3 failures then green) | `gen_isa_step` after the step |
| NMI and internal-NMI emulation: `gen_isa_arm_async(pre_mip, nmi_mtval, nmi, nmi_int, ...)` makes the next step the entry (rtl/ibex_cs_registers.sv:905-945: MPIE = MIE, MIE = 0, MPP = prv, mepc = pc, mcause 0x8000001F or 0xFFFFFFE0, mtval = nmi_mtval for the internal cause, prv M, pc = mtvec base + 0x7C) with one recoverable mstack level (MPIE, MPP, mepc, mcause) restored by the mret that leaves NMI mode (:967-974); the external pin outranks the internal cause | BUILT (landing 2a; unit test sections 10-12, red 16 failures then green) | `g_nmi`, `g_mstack`, `g_nmi_mode` in `gen_isa_step` |
| tdata1/tdata2 written in debug mode only; tdata1 reads Ibex's fixed mcontrol view `GEN_TDATA1_IBEX_RDATA` plus the execute bit (rtl/ibex_cs_registers.sv:1848-1864) | BUILT (T-102) | `gen_trigger_view_t` |
| dcsr legalization and trigger entry pc override | DEFERRED | - |
| WFI in_wfi clearing | DEFERRED | - |
| B5 nmip direction | DEFERRED | pinned Spike has no nmip: the model equals the RTL by absence, not by design |
| C5.4 per-word misaligned rule and mtval override | DEFERRED | owed with the misaligned-access directed test (Section 4) |
| CSR-state compare (isa_csr) | DEFERRED | declared knob, no compare yet |

## 5. Checkers

None: this component carries no pass/fail check (test equipment or infrastructure). Mutation classes:
the shim carries no checker; the comparator's ids and mutation classes are in
gen_component_api_scoreboard.md.

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
misaligned `mmio_store` (byte split, mtval override; the shim itself does not yet implement the rule,
Section 4a). Still before coding: verify grevi/gorci non-alias
decode; write the C5.3a/C5.3b tables into this document as rows with an RTL cite and a test each (R-2).

## Recoverable-NMI stack convention (landing 2c, CR8 fu2a L-3)

The shim keeps one `mstack` (MPIE, MPP, mepc, mcause) as the RTL does (rtl/ibex_cs_registers.sv:921-935): it is pushed on EVERY
exception entry outside debug mode, the emulated NMI entry included, from the CSR values before that entry. An mret executed while
in NMI mode restores MPIE / MPP / mepc / mcause from the stack and leaves NMI mode (rtl :967-974, rtl/ibex_controller.sv:954-960);
an mret outside NMI mode is Spike's. So a trap nested inside the NMI handler pushes the NMI's own context, and the nested trap's
mret (the first mret) restores that context and ends NMI mode while jumping to the nested trap's mepc (back into the handler); the
handler's own mret is then a plain one. Unit test section 12b holds the case (red on the entry-only push: 6 failures,
gen_fu_l7_ut_isa_shim_red_nested.log; green gen_fu_l7_ut_isa_shim.log). The irq checker exits NMI mode by depth, which is lenient
toward the bound and does not enter the compare.

## Counter CSRs (T-235): Ibex's mcountinhibit, minstret and the unimplemented counters

Authority: dv/auto_dv/evidence/gen_counter_csr_anchors.md section 10. Two parts: Runtime's holders (gen_isa_shim_counters.h / .cc,
installed by `gen_install_counter_holders` in legalize_after_reset) and tb-infra's minstret proxy and step-loop rules (gen_isa_shim.cc).
- `gen_mcountinhibit_csr_t` replaces mcountinhibit in Spike's csrmap: bits 0 and 2..12 writable, bit 1 and 31:13 read 0, reset 0
  (rtl/ibex_cs_registers.sv:1554-1561, :1714). Spike's OWN mcountinhibit is never touched, so Spike's minstret keeps counting every
  retirement and `retired` (the minstret delta of a step) stays derivable under IR = 1: a step under the inhibit retires, it is not a
  synthesized trap any more (the Test Writer's gen_pmc_ctrl blocker).
- `gen_zero_csr_t` for mhpmcounter13..31, mhpmcounter13h..31h and mhpmevent13..31: read 0, writes ignored, no trap in M
  (:1699-1700, :1716-1717, :1615-1618).
- `gen_minstret_proxy_t` (one 64-bit view; CSR_MINSTRET and CSR_MINSTRETH are `gen_minstret_half_csr_t` objects that know their half
  from the address, tb_l9 M-1; CSR_INSTRET / INSTRETH through Spike's counter proxies on them, so the U-mode aliases stay legal iff
  mcounteren.IR): Ibex's value = Spike's counter minus `g_inh`, the retirements
  Ibex did not count. The step loop adds a step's retirement to `g_inh` when the holder's IR bit is set AFTER the step: an instruction retires
  under the inhibit state it leaves behind, so the csrw that sets IR is itself not counted and the csrw that clears it is (rtl/ibex_cs_registers.sv:1643;
  measured on the Test Writer's gen_pmc_ctrl program, whose first form of the rule, the state as the step began, read one less
  than the DUT after every IR clear: the retained red gen_fu_l9_lockstep_pmc_s1_on_red_*). An explicit write defines the value (`g_inh` = 0; the writer itself is not counted,
  Spike's written flag) with the two corners of an instruction retiring in the write cycle, decided by the retirement gap the scoreboard
  passes before every step (`gen_isa_set_retire_gap(t.cycle - previous record's cycle)`; 1 = back to back), and only when that previous
  record was not itself a minstret / minstreth writer (neither side counted a writer, so nothing was lost: tb_l9 M-2), and only for the
  program's own writer: a low-word write while Ibex's own low word (Spike's minus the inhibited retirements) had just wrapped loses the
  carry Ibex never took (`g_inh` = 2^32; rtl/ibex_counter.sv:36-37, :44-47; decided on Ibex's word, not Spike's raw counter: CM123-L-2), a
  high-word write reloads the low word with its pre-increment value (`g_inh` = 1; :40, :44-47). A TB-side write (gen_isa_write_csr) is
  no instruction: it takes neither corner, does not mark the next step as after a writer (CM123-L-3, tb_l11 L-5), and clears Spike's
  written flag with `bump(0)` so it does not eat the next retirement's increment. A draft-B op the scoreboard executes itself is counted
  through `gen_isa_count_retire` (unless IR inhibits), since the model never steps it (landing 11, finding L11-F1). The retirement gap
  reaches the shim for EVERY record, whichever path compares it (CM123-L-1). mcycle needs none of this: the TB syncs it
  from the record before every step.
- Not modelled: the hazard variant of the high-word corner (a csrw with a register hazard against a load in WB defers the write one
  cycle to an empty WB, rtl/ibex_id_stage.sv:1059-1062, :1120): the gap rule sees the retirement gap, not the hazard, so a program with that pattern
  reads one more than Ibex; the DUT's own dummy instructions count in Ibex and not in the model, and no knob narrows the compare: a program that
  enables dummy instructions through cpuctrl and then reads minstret raises isa_rd misses (the retained dummy programs read no counter).
  Unit test sections 14 (Runtime's holders, 23 rows) and 15 (the proxy, 46 check calls after its header: 35 at the inner indentation and 11
  re-reset and TB-write checks at the outer; 24 at the T-235 commit, 7 tb_l9 rows, 15 landing-11 rows for CM123-L-2 / L-3 and tb_l11 L-5): reds gen_fu_l9_ut_isa_shim_red_t235.log (8 failures on the pre-integration shim, run with an intermediate
  test file: CM123-L-8), gen_fu_l12_ut_isa_shim_red_tbl9.log (2 failures, the landing-10 test on the committed T-235 shim) and
  gen_fu_l13_ut_isa_shim_red_73ff075.log (the landing-11 test on the committed landing-10 shim: 4 failing checks); green gen_fu_l13_ut_isa_shim.log
  (293 OK, stamped with the landing-11 shim).

### T-235 sizing (CM102-L-5): the five gaps between Spike's counters and Ibex's, as sized before the build and as built

The sizing tb-infra relayed to the DV Lead before T-235 (through the Orchestrator, by message, never committed: CM102-L-5) is recorded here
against what was built, so the plan's ranking has a committed artifact behind it. The five gaps, each with the size the estimate gave and the
size the build took:
1. mcountinhibit: Ibex implements bits 0 and 2..12 (mcycle, minstret, mhpmcounter3..12), Spike a different writable set. Estimate: one CSR
   holder class, a day's slice of Runtime's part. Built: `gen_mcountinhibit_csr_t` (gen_isa_shim_counters.h / .cc, Runtime's part R), 23 unit-test
   rows in section 14; Spike's own mcountinhibit untouched so `retired` stays derivable under IR = 1.
2. The unimplemented counters mhpmcounter13..31 (and h) and mhpmevent13..31: Ibex reads 0 and ignores writes without trapping, Spike traps
   or holds them. Estimate: one read-zero holder class installed on 57 addresses, same slice. Built: `gen_zero_csr_t`, installed by
   `gen_install_counter_holders`; the CG-CSR-004 hpm_unimpl family is an independent compare against the constant zero (plan v3h).
3. minstret / minstreth under mcountinhibit.IR and the two write corners (the instruction retiring in the write cycle: a low write loses the
   carry, a high write reloads the low word). Estimate: the largest gap, a proxy over Spike's counter plus a per-record gap from the
   scoreboard, two to three days including the reds. Built: `gen_minstret_proxy_t` with `gen_minstret_half_csr_t` per address, `g_inh`, the
   retirement gap DPI, the writer rule (the writer itself is never counted; the record after a writer is counted but skips the write-cycle corner), the draft-B count
   (landing 11); 35 section-15 rows; measured on gen_pmc_ctrl (8000 records, 0 mismatches) and on the directed minstret programs.
4. The U-mode aliases instret / instreth: legal iff mcounteren.IR, through Spike's counter proxies over the halves. Estimate: hours. Built:
   `counter_proxy_csr_t` instances over `lo` / `hi` in the same csrmap edit.
5. mcycle and the HPM counters 3..12: Ibex's values come from the record (record-synced consistency compares, not model predictions), so
   the gap is a sync, not a model. Estimate: hours, already partly built (gen_isa_set_time / gen_isa_set_hpm before every step). Built as
   estimated; the compare class is stated in gen_component_api_scoreboard.md (Critic T-102 M-1).
Not part of the five and not modelled (stated above): the hazard variant of the high-word corner and the DUT's dummy instructions under a
minstret read.
