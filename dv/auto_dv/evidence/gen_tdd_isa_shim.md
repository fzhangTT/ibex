# TDD transcript: gen_isa_shim (Spike-backed ISA model, architecture C5; build step 2a, shim unit test 1)

Component: `dv/auto_dv/isa/gen_isa_shim.h` (C ABI), `gen_isa_shim.cc` (implementation + DPI wrappers),
`gen_isa_dpi_pkg.sv` (SV imports), `gen_isa_shim_build.sh` (shared library for VCS, C++ unit test).
Test: `dv/auto_dv/isa/gen_ut_isa_shim.cc` on the directed Zc image `out_codegen/zc/prog.vmem` (the same
image the DUT boots in gen_tdd_boot_agents.md). Logs: `dv/auto_dv/work/tb-infra/tdd/isa_shim_red.log`,
`isa_shim_green.log`, `out_isa/ut_green.log`. Owner: tb-infra.

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
