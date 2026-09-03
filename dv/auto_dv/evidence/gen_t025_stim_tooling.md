# T-025 evidence: stimulus tooling (debug-ROM relocation, Zc macros, gen_program.py)

Owner: tb-infra. Date: 2026-09-03 (05:41-05:52 UTC). Host: this site host, local runs, no LSF,
`bash -lc` with `ci/env.sh` sourced. Out-tree (not committed): `dv/auto_dv/work/tb-infra/out_t025/`
(`gen/` generator build with `support_debug_mode = 1`, `dbgprog/`, `zcprog/`). No vendored file
was modified. Deliverables (all `gen_` prefixed): `dv/auto_dv/stim/gen_relocate_debug_rom.py`,
`dv/auto_dv/stim/gen_zc_insn.h`, `dv/auto_dv/stim/gen_directed/gen_zc_directed.S`,
`dv/auto_dv/stim/gen_program.py`, and `dv/auto_dv/stim/gen_riscv_dv_target/gen_riscv_core_setting.sv`
(now `support_debug_mode = 1`; see Section 6 for the rename).

## 1. Debug-ROM relocation (gen_relocate_debug_rom.py)

riscv-dv emits the debug ROM as one block inside `.text`: `debug_rom:` ... (sub-programs,
single-step logic) ... `debug_end:` ... `debug_exception:` ... `instr_end:`; every internal
reference is a local label or `la` + `jalr`, so the block moves as a unit. The script inserts a
`.debug_rom` section switch plus an 8-byte uncompressed header (`j debug_rom`; `nop`;
`j debug_exception`) before `debug_rom:` and a `.section .text` before `instr_end:`;
`gen_link.ld` places `.debug_rom` at DmHaltAddr (0x1A110800), so the exception entry sits at
DmExceptionAddr (0x1A110808). Header symbols equal those of `gen_debug_rom_stub.S`, and
`gen_program.py` links the stub only when the program has no `.debug_rom` of its own.

Proof, one generated program (seed 7, `+gen_debug_section=1 +num_debug_sub_program=1
+enable_debug_single_step=1 +set_dcsr_ebreak=1`), through `gen_program.py`:

```
python3 dv/auto_dv/stim/gen_program.py --test gen_rand_smoke --seed 7 --out <out>/dbgprog \
    --gen-build <out>/gen --sim-opts "+gen_debug_section=1 +num_debug_sub_program=1 \
    +enable_debug_single_step=1 +set_dcsr_ebreak=1" --spike-check
```

Generator run (from gen_run.log): `$ /localdev/fzhang/ws/ibex-challenge/.venv/bin/python3 run.py --so -si vcs -ct /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/stim/gen_riscv_dv_target -ext /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/stim/gen_riscv_dv_target/user_extension --isa rv32imc_zba_zbb_zbc_zbs --mabi ilp32 -o /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_t025/gen -tn gen_rand_smoke --seed 7 -s gen --noclean --sim_opts=+gen_debug_section=1 +num_debug_sub_program=1 +enable_debug_single_step=1 +set_dcsr_ebreak=1`

Relocation: `/localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_t025/dbgprog/prog.S: relocated lines 2646-3155 (510 lines) into .debug_rom -> /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_t025/dbgprog/prog.S`

Layout and symbols (readelf, nm):

```
  [ 1] .debug_rom        PROGBITS        1a110800 000074 000726 00  AX  0   0  1
  [ 2] .gen_boot         PROGBITS        80000080 000880 000004 00  AX  0   0  1
  [ 3] .text             PROGBITS        80000100 000900 0026b4 00 WAX  0   0 256
Entry point 0x80000080
  LOAD           0x000074 0x1a110800 0x1a110800 0x00726 0x00726 R E 0x1
  LOAD           0x000880 0x80000080 0x80000080 0x1c428 0x1c428 RWE 0x100
   00     .debug_rom 
   01     .gen_boot .text .data .region_0 .region_1 .user_stack .kernel_stack
1a110800 T gen_debug_rom_entry
1a110808 T gen_debug_exception_entry
1a11080c t debug_rom
1a110b82 t debug_sub_1
1a110ea0 t debug_end
1a110f22 t debug_exception
80000080 T gen_boot_entry
80000100 T _start
800027c0 D tohost
```

Header and ROM start (objdump):

```
1a110800 <gen_debug_rom_entry>:
1a110800:	00c0006f          	j	1a11080c <debug_rom>
1a110804:	00000013          	nop

1a110808 <gen_debug_exception_entry>:
1a110808:	71a0006f          	j	1a110f22 <debug_exception>
1a11080c <debug_rom>:
1a11080c:	18f1                	addi	a7,a7,-4
1a11080e:	0088a023          	sw	s0,0(a7)
```

Spike standalone: exit 0, 14464 commit lines, last lines:

```
core   0: 3 0x800025ae (0x00000f17) x30 0x800025ae
core   0: 3 0x800025b2 (0x203f2923) mem 0x800027c0 0x00000001
```

The ROM is linked and loaded at DmHaltAddr; it is not executed here because standalone Spike has
no debug request source (the TB's debug agent exercises it). Sidecar: seed 7, steps
['generate', 'debug_rom_relocate', 'link', 'image', 'spike_check'], debug_rom = program, entry 0x80000080, 29396 words,
sum32 0xefe41d6b.

## 2. Zcb / Zcmp assembler macros (gen_zc_insn.h) and the directed program

binutils 2.35 (lowRISC gcc 10.2) knows neither Zcb nor Zcmp and rejects raw `.insn N, value`
(`Error: unrecognized opcode`), so every macro emits the 16-bit word with `.2byte`. Encodings
follow the Zc* specification v1.0.0 and were cross-checked against rtl/ibex_compressed_decoder.sv
(Zcb: C0 funct3 100 at :266-326 with imm bit order uimm[0] = instr[6], uimm[1] = instr[5]; C1
funct3 100, funct2 11, {instr[12], instr[6:5]} = 111 unary / 110 c.mul at :430-519; Zcmp: C2
funct3 101, instr[12:8] = 11000 push / 11010 pop / 11100 popretz / 11110 popret, rlist =
instr[7:4], spimm = instr[3:2], at :615-725; sreg' map cm_mvsa01/cm_mva01s at :153-165).
Macros: c_lbu, c_lhu, c_lh, c_sb, c_sh, c_zext_b, c_sext_b, c_zext_h, c_sext_h, c_not, c_mul,
cm_push, cm_pop, cm_popret, cm_popretz, cm_mvsa01, cm_mva01s (register arguments are x-numbers;
each macro checks the compressed-register range with `.error`).

Directed self-checking program `gen_zc_directed.S` (pass = tohost 1, fail = tohost 3):

```
$ /localdev/fzhang/ws/tools/lowrisc-toolchain-gcc-rv32imcb/bin/riscv32-unknown-elf-gcc -static -mcmodel=medany -fvisibility=hidden -nostdlib -nostartfiles -march=rv32imcb -mabi=ilp32 -Wl,-N -T dv/auto_dv/stim/gen_riscv_dv_target/gen_link.ld -I dv/auto_dv/stim/gen_riscv_dv_target/user_extension -I dv/auto_dv/stim dv/auto_dv/stim/gen_directed/gen_zc_directed.S dv/auto_dv/stim/gen_riscv_dv_target/gen_boot_stub.S dv/auto_dv/stim/gen_riscv_dv_target/gen_debug_rom_stub.S -o dv/auto_dv/work/tb-infra/out_t025/zcprog/prog.elf
$ timeout 120 tools/spike/bin/spike --isa=rv32imc_zicsr_zifencei_zba_zbb_zbc_zbs_zcb_zcmp_zicntr_zihpm_zicclsm --priv=mu --pmpregions=16 --pmpgranularity=4 --triggers=1 -m0x1a110000:0x1000,0x80000000:0x100000 --pc=0x80000080 --log-commits --log=dv/auto_dv/work/tb-infra/out_t025/zcprog/spike_commits.log dv/auto_dv/work/tb-infra/out_t025/zcprog/prog.elf
```

Spike: exit 0 (pass); the Zc instructions as executed, with the model's register
and memory effects (each line: pc, 16-bit encoding, effects):

```
core   0: 3 0x800000ae (0xb872) x2  0x80000390 mem 0x8000039c 0x44444444 mem 0x80000398 0x33333333 mem 0x80000394 0x22222222 mem 0x80000390 0x11111111
core   0: 3 0x800000da (0xba72) x1  0x11111111 x2  0x800003a0 x8  0x22222222 x9  0x33333333 x18 0x44444444 mem 0x8000039c mem 0x80000398 mem 0x80000394 mem 0x80000390
core   0: 3 0x80000110 (0xb856) x2  0x80000380 mem 0x8000039c 0x22222222 mem 0x80000398 0x11111111
core   0: 3 0x8000012a (0xba56) x1  0x11111111 x2  0x800003a0 x8  0x22222222 mem 0x8000039c mem 0x80000398
core   0: 3 0x80000140 (0xac26) x8  0xa0a0a0a0 x9  0xa1a1a1a1
core   0: 3 0x8000016e (0xad6e) x10 0x52525252 x11 0x53535353
core   0: 3 0x800001cc (0x9e61) x12 0x00000078
core   0: 3 0x800001de (0x9e65) x12 0xffffff80
core   0: 3 0x800001f0 (0x9e69) x12 0x0000abcd
core   0: 3 0x80000204 (0x9e6d) x12 0xffffabcd
core   0: 3 0x80000218 (0x9e75) x12 0xf0f0f0f0
core   0: 3 0x8000022a (0x9e55) x12 0xffffffd6
core   0: 3 0x8000023c (0xb842) x2  0x80000390 mem 0x8000039c 0x80000244
core   0: 3 0x80000240 (0xbe42) x1  0x80000244 x2  0x800003a0 mem 0x8000039c
core   0: 3 0x80000250 (0xb842) x2  0x80000390 mem 0x8000039c 0x8000025e
core   0: 3 0x8000025a (0xbc42) x1  0x8000025e x2  0x800003a0 x10 0x00000000 mem 0x8000039c
```

Reading: `0xb872` = cm.push {ra,s0-s2},-16 (sp 0x800003a0 -> 0x80000390; s2 at sp_old-4, s1,
s0, ra at sp_old-16); `0xba72` = cm.pop restoring x1/x8/x9/x18 and sp; `0xb856`/`0xba56` =
cm.push/pop {ra,s0} with spimm 1 (stack_adj 32); `0xac26` = cm.mvsa01 s0,s1 (a0/a1 -> s0/s1);
`0xad6e` = cm.mva01s s2,s3 (-> a0/a1); `0x9e61` c.zext.b, `0x9e65` c.sext.b, `0x9e69` c.zext.h,
`0x9e6d` c.sext.h, `0x9e75` c.not, `0x9e55` c.mul (7 * -6 = 0xffffffd6); `0xb842`/`0xbe42` =
cm.push {ra} / cm.popret; `0xb842`/`0xbc42` = cm.push {ra} / cm.popretz (a0 = 0). The Zcb
load/store macros executed too (c.sb/c.sh/c.lbu/c.lhu/c.lh appear as `0x8...`/`0x9...` C0 forms
and their checks passed).

First attempt failed on the program's own expectation, not the encoding: I had assumed ra is
stored at sp_old-4; Spike (and rtl/ibex_compressed_decoder.sv `cm_push_store_reg`, which stores
`cm_rlist_top_reg` first at sp-4) store the LIST TOP at sp_old-4 and ra at the lowest address:

```
core   0: 3 0x800000ae (0xb872) x2  0x80000390 mem 0x8000039c 0x44444444 mem 0x80000398 0x33333333 mem 0x80000394 0x22222222 mem 0x80000390 0x11111111
```

The expectation was corrected; this is recorded as the reference rule for the TB's Zcmp checks.
Note: objdump decodes `0xb872` as `fsd ft8,48(sp)` (it lacks Zcmp); disassembly of Zc programs
must not be trusted, the Spike log is the readable record.

## 3. gen_program.py (single (config, seed) -> ELF + image + sidecar driver)

Steps: generator compile if the build is missing (`run.py --co`), generation (`run.py --so ...
--seed <seed> -s gen`), debug-ROM relocation, assemble + link (`$RISCV_GCC -march=rv32imcb
-mabi=ilp32 -Wl,-N -T gen_link.ld -I <target>/user_extension -I dv/auto_dv/stim <sources>
gen_boot_stub.S [gen_debug_rom_stub.S]`), `gen_elf2mem.py`, optional `--spike-check` with the
pinned Spike (`--isa=rv32imc_zicsr_zifencei_zba_zbb_zbc_zbs_zcb_zcmp_zicntr_zihpm_zicclsm --priv=mu
--pmpregions=16 --pmpgranularity=4 --triggers=1 -m0x1a110000:0x1000,0x80000000:0x100000
--pc=<entry> --log-commits`). The sidecar `prog.sym.json` carries the one run seed, the test name
or directed sources, the generator plusargs, the steps run, which debug ROM was linked, tool
versions, the Spike check result, entry, segments, symbols and the read-back checksum. Both runs
above went through it (generated: seed 7; directed: seed 1, recorded although no randomization
happens for a directed source).

## 4. Limitations and notes for the Test Writer

1. Zcmp stack layout: list top at sp_old-4, ra at sp_old-stack_adj_base (spec and RTL agree);
   write checks accordingly.
2. objdump cannot disassemble Zcb/Zcmp (misdecodes as F/D forms); read the Spike log or the
   macros' comments. The lowRISC toolchain also cannot assemble Zc mnemonics: use gen_zc_insn.h.
3. The relocated riscv-dv debug ROM is proven by link/load only in this evidence; its execution
   is exercised by the TB debug agent. riscv-dv's ROM saves registers through `x17` as a stack
   pointer and expects the kernel stack (`tp`/`x17` setup in the program's init), so a debug
   request before the program's init completes lands in a ROM that uses an uninitialised x17: the
   TB must gate debug requests behind the riscv-dv INITIALIZED signature or a retirement count.
4. `gen_program.py` reuses a compiled generator through `--gen-build`; a core-setting change
   (riscv_core_setting.sv) requires a fresh generator build directory (the setting is compiled in).
5. Spike's `--isa` for Zc programs must name `zcb_zcmp`; the default in gen_program.py does.

## 5. Acceptance

- (1) relocation: generated debug-ROM program links with `.debug_rom` at 0x1A110800, exception
  entry at 0x1A110808, runs on Spike to tohost (exit 0).
- (2) macros + directed program: 17 Zcb/Zcmp macros; the directed program passes on Spike (exit 0).
- (3) driver: both programs produced through gen_program.py with seed, steps and checksum in the
  sidecar.

## 6. Changes from the T-023 post-execution review (folded in here, 05:52-05:55 UTC)

Review: `dv/auto_dv/reviews/2026-09-03-claude-diff-0b9c93c7-0b8d60b4.md` (APPROVE-WITH-CHANGES).

| Finding | Change |
|---|---|
| major 1: TINFO listed but not implemented | removed from `implemented_csr` (rtl/ibex_cs_registers.sv does not decode 0x7A4); header states the RTL-derivation rule |
| major 2: evidence scripts uncommitted | `gen_zb_encoding_check.py` and `gen_t023_flow.sh` moved under `dv/auto_dv/stim/`; T-023 evidence cites them and carries the effective vcs command from the generator's compile.log |
| major 3: tool-mandated file names (Q-013 default) | committed sources renamed `gen_riscv_core_setting.sv`, `gen_testlist.yaml`, `user_extension/gen_user_define.h`, `gen_user_init.s`, `gen_user_extension.svh`; `gen_program.py` materializes the fixed-name target directory out-of-tree (`<gen_build>/target/`, `<out>/target/`) before every riscv-dv or gcc call |
| medium: address-independent digest | `gen_elf2mem.py` digest is now CRC-32 over (word index, word) pairs in ascending order (8 LE bytes per pair) plus the word count; docstring states it as the requirement the SV memory model and the shim must meet |
| minor: MHPMCOUNTER3H..12H | listed fully |
| minor: ld constants vs SV | `gen_program.py` reads `DmHaltAddr` from gen_dut_top.sv and `GEN_BOOT_ADDR_DEFAULT` from gen_tb_pkg.sv and fails loud if gen_link.ld's DM/PROG origins differ |
| minor: abutting segments | segments merged at byte granularity before word packing |

Re-proof with the renamed sources and a fresh generator build (`out_t029/stim/`): directed Zc
program OK (204 words, crc32 0xcf0cb3b8, Spike exit 0); generated debug-ROM program (seed 7,
same plusargs as Section 1) OK with steps generator_compile, generate, debug_rom_relocate, link,
image, spike_check (29396 words, crc32 0xa768741f, Spike exit 0, 14464 commit lines); the
materialized `gen_build/target/` holds riscv_core_setting.sv, testlist.yaml and
user_extension/{user_define.h, user_init.s, user_extension.svh}; generator compile 0 errors.
