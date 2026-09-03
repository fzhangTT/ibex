# TDD transcript: gen_isa_shim (Spike-backed ISA model, architecture C5; build step 2a, shim unit test 1)

Component: `dv/auto_dv/isa/gen_isa_shim.h` (C ABI), `gen_isa_shim.cc` (implementation + DPI wrappers),
`gen_isa_dpi_pkg.sv` (SV imports), `gen_isa_shim_build.sh` (shared library for VCS, C++ unit test).
Test: `dv/auto_dv/isa/gen_ut_isa_shim.cc` on the directed Zc image `out_codegen/zc/prog.vmem` (the same
image the DUT boots in gen_tdd_boot_agents.md). Logs: `dv/auto_dv/work/tb-infra/tdd/isa_shim_red.log`,
`gen_isa_shim_green.log`, `out_isa/ut_green.log`. Owner: tb-infra.

## 1. Red (header and test written first; no implementation)

```
# RED: 2026-09-03T07:56:00Z host=soc-l-11 cmd: gen_isa_shim_build.sh test out_isa zc/prog.vmem (gen_isa_shim.cc absent)
gen_isa_shim_build.sh: dv/auto_dv/isa/gen_isa_shim.cc does not exist
exit=3
```

## 2. Green attempt 1: one shim defect and three wrong test expectations, all disclosed

```
# GREEN attempt 1: 2026-09-03T07:58:49Z host=soc-l-11
```

Attempt 1 aborted with an uncaught `trap_illegal_instruction`: on the grevi trap Spike logs a CSR write
to 0x34B (mtval2), which `get_csr` rejects without the H extension; the shim's post-step CSR
legalization read it back unguarded. Fix: the legalization loop catches `trap_t` for logged addresses that
are not readable and records the logged value unlegalized (the shim note "csr 0x34b logged but not
readable (cause 2)" is visible in the green run). The three remaining FAILs were wrong TEST values: the
image entry `j _start` jumps +4 (0x80000084, the vmem shows `_start` right after the entry word), the mtvec
legalization of 0x80001234 is 0x80001201 (BASE[7:2] cleared keeps 0x1200), and cpuctrlsts has EIGHT
writable bits (icache_enable .. double_fault_seen, rtl/ibex_cs_registers.sv:239-246; ic_scr_key_valid at
bit 8 is read-only), not seven.

## 3. Green

```
exit=0
exit=0  GEN_UT_ISA_SHIM PASS (0 failures)  51 checks
```

What the 51 checks prove: Ibex reset legalization after `processor_t` construction (pc = boot page + 0x80,
mtvec = page | 1, mstatus 0x80 with MPP U, prv M, misa 0x40901104 = RV32IMCU + X as the RTL's MISA_VALUE
with MisaXBit = 1, PMP all OFF, mie/mcause 0); the real Zc image executes through the model over the
shim's own sparse memory (every access MMIO from Spike's view) to its `tohost` store with value 1 in 149
steps and no trap; grevi/gorci with the ratified immediates (rev8, orc.b) retire with the expected values
while other immediates trap with cause 2 and mtval = the instruction and retire 0, and
`gen_isa_exec_reference` computes grev/gorc for any immediate (vectors 0x2138a9b4, 0x333cfffc, 0x1e6a2c48,
0x30003) and rejects a plain addi; after retired CSR writes: mtvec BASE[7:2] forced 0 and MODE 1 (also
reported in the step's CSR write list), the fast interrupt bit 16 sticks in mie (gen_mie_csr_t), cpuctrlsts
writes land masked through the genibex extension; gpr and pc accessors. The shared library exports 22
`gen_isa_*` symbols (`nm -D`).

## 4. T-068 (2026-09-03): claim correction, accessors, build script

Correction (cross-model 2a medium 6): the shim's header comment, `gen_component_api_isa_shim.md` Section 4 and
the step-2a commit message described a byte-wise misaligned MMIO rule (per-word PMP splitting, the permitted
first word performed, the second faulted, `mtval` overridden to the aligned second word). The shim does NOT
implement that: every access is served byte-wise through `mmio_fetch/load/store` over the sparse memory and an
armed bus fault fails the bytes it covers; the per-word rule and the mtval override are pending with the
misaligned-access directed test (C5.4). The link-test-2 evidence that Spike splits misaligned accesses per byte
stands; it was never the shim's implementation. Also pending, now listed in the API document (Section 4a):
mstatus MPP legalization, mcountinhibit/mhpmevent masks, NMI emulation, dcsr/tdata legalization, WFI
`in_wfi`, the B5 `nmip` direction, the CSR-state compare.

New in T-068: per-step accessors `gen_isa_reg_write(i, idx, val)` (every integer register write of the step),
`gen_isa_mem_write(i, addr, data, size)`, `gen_isa_mem_read(i, ...)`, `gen_isa_fetch_insn(pc)`, and
`reg_writes` in `gen_isa_step_t` (the scoreboard's Zcmp union compare and draft-B path consume them); the
identical `if (logging) ... else ...` branches collapsed; `GEN_MM_BOOT_PAGE_MASK` from the rendered header
instead of a literal. Build script: any absolute outdir (inside or outside the clone) is accepted, no RPATH is
baked in (the flow's `runtime_lib_dirs` and the local driver export LD_LIBRARY_PATH; the simv link uses
`-Wl,-rpath-link`), and `test` mode exports the path itself. The history sentence in the unit test's header
is gone.

Unit test re-run (retained `dv/auto_dv/evidence/gen_tdd_logs/isa_shim/ut_run_t068.log`):

```
# T-068 shim unit test: 2026-09-03T08:45:31Z host=soc-l-11 cmd: bash dv/auto_dv/isa/gen_isa_shim_build.sh test ... prog.vmem
GEN_UT_ISA_SHIM PASS (0 failures)
```
85 OK lines (51 before): the new checks cover a cm.push step (4 stores, descending 4-byte-aligned addresses,
`mem_write(0)` equals the first-access fields, -1 past the end), a cm.pop step (5 register writes in ascending
index order, 4 loads), a single-write step, `fetch_insn(pc_before) == insn` on every step and 0 on an unmapped
pc. `readelf -d` on the built library shows no RPATH/RUNPATH (retained: `dv/auto_dv/evidence/gen_tdd_logs/isa_shim/gen_readelf_libgen_isa_shim_t068.txt`, NEEDED entries only, `grep -ci rpath: 0`); a library build into Runtime's shared out root
(`/proj_soc/user_dev/fzhang/ibex_dv_out/t068_shim_outdir_check/lib`) succeeded. The 2a logs are retained as
`gen_isa_shim_red.log`, `gen_isa_shim_green.log`, `gen_ut_green_2a.log`.
