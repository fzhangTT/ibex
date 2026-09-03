# T-023 evidence: stimulus toolchain proof (riscv-dv generator, toolchain, image, Spike)

Owner: tb-infra. Date: 2026-09-03 (05:28-05:36 UTC). Host: this site host, local runs, no LSF,
`bash -lc` with `ci/env.sh` sourced. Build configuration for the DUT: `opentitan`. Out-tree
(not committed): `dv/auto_dv/work/tb-infra/out_t023/`. Driver scripts (working files):
`dv/auto_dv/stim/gen_t023_flow.sh` (steps 3-5), `dv/auto_dv/stim/gen_zb_encoding_check.py` (both committed after the review).
Committed deliverables: `dv/auto_dv/stim/gen_riscv_dv_target/` (gen_riscv_core_setting.sv,
gen_testlist.yaml, gen_link.ld, gen_boot_stub.S, gen_debug_rom_stub.S, user_extension/gen_user_*;
the fixed names riscv-dv requires are materialized out-of-tree by `dv/auto_dv/stim/gen_program.py`
per owner question Q-013's default), `dv/auto_dv/stim/gen_elf2mem.py`, and the two scripts that
produce the numbers below: `dv/auto_dv/stim/gen_zb_encoding_check.py` (encoding check) and
`dv/auto_dv/stim/gen_t023_flow.sh` (the T-023 bring-up driver; superseded by `gen_program.py`).
The reference table is rtl-arch's `gen_rv32b_otearlgrey_encodings.md` (promotion to
`dv/auto_dv/docs/` requested). No vendored file was modified. Post-execution review
(APPROVE-WITH-CHANGES) changes applied in T-025: TINFO removed from the CSR list (not implemented
by rtl/ibex_cs_registers.sv), MHPMCOUNTER3H..12H listed fully, digest changed to CRC-32 over
(index, word) pairs, byte-granular segment merge, flow-time check of gen_link.ld against the SV
parameters; see `gen_t025_stim_tooling.md`.

## 1. riscv-dv generator compiled with VCS (step 1)

Command (run.py builds it from vendor/google_riscv-dv/yaml/simulator.yaml; `--cmp_opts=-licqueue`
adds the license queue; `-full64` comes from the yaml):

```
cd vendor/google_riscv-dv && python3 run.py --co -si vcs -ct <clone>/dv/auto_dv/stim/gen_riscv_dv_target \
    -ext <clone>/dv/auto_dv/stim/gen_riscv_dv_target/user_extension --isa rv32imc_zba_zbb_zbc_zbs --mabi ilp32 \
    -o <clone>/dv/auto_dv/work/tb-infra/out_t023/gen --cmp_opts=-licqueue -v
```

Effective vcs command line (line 1 of the generator build's compile.log):

```
vcs -file <clone>/vendor/google_riscv-dv/vcs.compile.option.f +incdir+<clone>/dv/auto_dv/stim/gen_riscv_dv_target +incdir+<clone>/dv/auto_dv/stim/gen_riscv_dv_target/user_extension +vcs+lic+wait -f <clone>/vendor/google_riscv-dv/files.f -full64 -l <clone>/dv/auto_dv/work/tb-infra/out_t023/gen/compile.log -LDFLAGS -Wl,--no-as-needed -CFLAGS --std=c99 -fno-extended-identifiers -Mdir=<clone>/dv/auto_dv/work/tb-infra/out_t023/gen/vcs_simv.csrc -o <clone>/dv/auto_dv/work/tb-infra/out_t023/gen/vcs_simv -licqueue
```

Result: `CPU time: 10.220 seconds to compile + .169 seconds to elab + .584 seconds to link`; 0 errors; vcs_simv 1.3 MB. Warning classes, all inside the vendored
generator's own coverage model and PMP class (nothing from our target files):

```
    488 Warning-[CPBRM]
    366 Warning-[PSBU]
    126 Warning-[SIOB]
      1 Warning-[LCA_FEATURES_ENABLED]
      1 Warning-[IVCB-MEMBER-PACKSTR-S]
```

Files named by the warnings: `    980 riscv_instr_cover_group.sv;       1 riscv_pmp_cfg.sv`.

## 2. The team's target directory (step 2)

`dv/auto_dv/stim/gen_riscv_dv_target/gen_riscv_core_setting.sv` (materialized as riscv_core_setting.sv), derived from rtl/ibex_pkg.sv and the RISC-V specifications:

```
parameter int XLEN = 32;
parameter satp_mode_t SATP_MODE = BARE;
privileged_mode_t supported_privileged_mode[] = {MACHINE_MODE, USER_MODE};
riscv_instr_group_t supported_isa[$] = {RV32I, RV32M, RV32C, RV32ZBA, RV32ZBB, RV32ZBC, RV32ZBS};
mtvec_mode_t supported_interrupt_mode[$] = {VECTORED};
int max_interrupt_vector_num = 32;
bit support_pmp = 1;
bit support_epmp = 1;
bit support_debug_mode = 0;
bit support_umode_trap = 0;
bit support_sfence = 0;
bit support_unaligned_load_store = 1'b1;
parameter int NUM_FLOAT_GPR = 32;
parameter int NUM_GPR = 32;
parameter int NUM_VEC_GPR = 32;
parameter int VECTOR_EXTENSION_ENABLE = 0;
parameter int VLEN = 512;
parameter int ELEN = 32;
parameter int SELEN = 8;
parameter int VELEN = int'($ln(ELEN)/$ln(2)) - 3;
parameter int MAX_LMUL = 8;
parameter int NUM_HARTS = 1;
```

Implemented CSR list: the ibex CSR table (cs_registers.rst) including the 16 PMP address CSRs,
mseccfg(h), triggers, debug CSRs, mcountinhibit, mhpmevent/mhpmcounter 3..12 (see the file).
Interrupt causes: M software/timer/external (fast interrupts and the NMI are TB-driven, not
generator causes). Exception causes: ibex codes 1, 2, 3, 5, 7, 8, 11.

`testlist.yaml` test `gen_rand_smoke`, gen_opts: ` +instr_cnt=300 +num_of_sub_program=0 +boot_mode=m +no_wfi=1 +tvec_alignment=8 +enable_zba_extension=1 +enable_zbb_extension=1 +enable_zbc_extension=1 +enable_zbs_extension=1 +pmp_num_regions=16 +pmp_granularity=0`. `gen_link.ld`: DM region at
0x1A110800 (`.debug_rom`, exception entry at +8), program region from 0x80000080 with the
`.gen_boot` entry first, then `.text` (256-byte aligned because of the vectored handler), then
the riscv-dv section order (.tohost, .page_table, .data, .user_stack, .kernel_data,
.kernel_stack, .bss). `gen_boot_stub.S`: `j _start` at the core's first-fetch address
`{boot_addr_i[31:8], 8'h80}`; ELF entry point = that address. `gen_debug_rom_stub.S`: default
`dret` entries at DmHaltAddr / DmExceptionAddr. `user_extension/`: empty hooks (user_define.h,
user_init.s, user_extension.svh).

## 3. One program from a fixed seed, assembled and linked (step 3)

Generation (seed 1): `python3 run.py --so -si vcs -ct <target> -ext <target>/user_extension
--isa rv32imc_zba_zbb_zbc_zbs --mabi ilp32 -o <out>/gen -tn gen_rand_smoke --seed 1 -s gen
--noclean -v`; generator run line: `vcs_simv +vcs+lic+wait  +ntb_random_seed=1 +UVM_TESTNAME=riscv_instr_base_test  +num_of_tests=1  +start_idx=0  +asm_file_name=/localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_t023/gen/asm_test/gen_rand_smoke  -l /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_t023/gen/sim_gen_rand_smoke_0.log +UVM_VERBOSITY=UVM_HIGH +instr_cnt=300 +num_of_sub_program=0 +boot_mode=m +`. Output
`<out>/gen/asm_test/gen_rand_smoke_0.S`: 4932 non-empty lines.

Assemble and link (team flow, not run.py's gcc step, so our linker script and stubs apply):

```
$RISCV_GCC -static -mcmodel=medany -fvisibility=hidden -nostdlib -nostartfiles \
    -march=rv32imcb -mabi=ilp32 -Wl,-N -T dv/auto_dv/stim/gen_riscv_dv_target/gen_link.ld -I dv/auto_dv/stim/gen_riscv_dv_target/user_extension \
    prog.S dv/auto_dv/stim/gen_riscv_dv_target/gen_boot_stub.S dv/auto_dv/stim/gen_riscv_dv_target/gen_debug_rom_stub.S -o prog.elf
```

gcc exit 0, no diagnostics. Symbols and layout:

```
1a110800 T gen_debug_rom_entry
1a110808 T gen_debug_exception_entry
80000080 T gen_boot_entry
80000100 T _start
80001800 t mtvec_handler
80002294 t test_done
8000229c t main
800026f0 t write_tohost
80002940 D tohost
  [ 1] .debug_rom        PROGBITS        1a110800 000074 000010 00  AX  0   0  1
  [ 2] .gen_boot         PROGBITS        80000080 000180 000004 00  AX  0   0  1
  [ 3] .text             PROGBITS        80000100 000200 00282c 00 WAX  0   0 256
  [ 4] .data             PROGBITS        80002940 002a40 000048 00  WA  0   0 64
  [ 7] .user_stack       PROGBITS        80013988 013a88 004e20 00  WA  0   0  4
  [ 8] .kernel_stack     PROGBITS        800187a8 0188a8 003e80 00  WA  0   0  4
Entry point 0x80000080
  LOAD           0x000074 0x1a110800 0x1a110800 0x00010 0x00010 R E 0x1
  LOAD           0x000180 0x80000080 0x80000080 0x1c5a8 0x1c5a8 RWE 0x100
   00     .debug_rom 
   01     .gen_boot .text .data .region_0 .region_1 .user_stack .kernel_stack
```

Entry and start of the program (objdump):

```
80000080 <gen_boot_entry>:
80000080:	0800006f          	j	80000100 <_start>

80000100 <_start>:
80000100:	f14022f3          	csrr	t0,mhartid
80000104:	4301                	li	t1,0
80000106:	00628263          	beq	t0,t1,8000010a <_start+0xa>
8000010a:	00000117          	auipc	sp,0x0
```

Bitmanip mnemonics in the generated program (count): sh1add:10 orn:8 clmulr:7 bexti:7 sext.b:6 sh3add:5 min:5 binv:5 sext.h:4 rori:4 rol:4 minu:4 max:4 clz:4 clmul:4 andn:4 sh2add:3 maxu:3 xnor:2 ror:2 cpop:2 bseti:2 binvi:2 bext:2 bclri:2 ctz:1 clmulh:1 bset:1 bclr:1

Assembler acceptance and encoding check against rtl-arch's decoder table
(`dv/auto_dv/work/rtl-arch/gen_rv32b_otearlgrey_encodings.md`), one instance of every mnemonic
in that table assembled with `-march=rv32imcb` and its f7/f3/hi5/imm fields compared
(`out_t023/zb_encoding_check.txt`; script `dv/auto_dv/stim/gen_zb_encoding_check.py`):

```
# march=rv32imcb gcc=/localdev/fzhang/ws/tools/lowrisc-toolchain-gcc-rv32imcb/bin/riscv32-unknown-elf-gcc
# accepted+match 62, accepted+mismatch 0, rejected 0
```

All 62 mnemonics (ratified Zba/Zbb/Zbc/Zbs and the draft Zbp/Zbr/Zbt/Zbf ops the RTL decodes)
are accepted by the lowRISC gcc 10.2 assembler under `-march=rv32imcb` and every encoding
matches the RTL table (0 mismatches, 0 rejections). Sample rows:

```
sh1add     0x203120b3   f7 0010000 f3 010 opc 0110011 MATCH
sh2add     0x203140b3   f7 0010000 f3 100 opc 0110011 MATCH
sh3add     0x203160b3   f7 0010000 f3 110 opc 0110011 MATCH
andn       0x403170b3   f7 0100000 f3 111 opc 0110011 MATCH
orn        0x403160b3   f7 0100000 f3 110 opc 0110011 MATCH
xnor       0x403140b3   f7 0100000 f3 100 opc 0110011 MATCH
cmov       0x2621d0b3   [26:25] 11 f3 101 opc 0110011 MATCH
fsl        0x1c4110b3   [26:25] 10 f3 001 opc 0110011 MATCH
fsr        0x1c4150b3   [26:25] 10 f3 101 opc 0110011 MATCH
sloi       0x20311093   hi5 00100 [26:20] 0000011 f3 001 opc 0010011 MATCH
rori       0x60315093   hi5 01100 [26:20] 0000011 f3 101 opc 0010011 MATCH
grevi      0x68315093   hi5 01101 [26:20] 0000011 f3 101 opc 0010011 MATCH
gorci      0x28315093   hi5 00101 [26:20] 0000011 f3 101 opc 0010011 MATCH
rev8       0x69815093   hi5 01101 [26:20] 0011000 f3 101 opc 0010011 MATCH
orc.b      0x28715093   hi5 00101 [26:20] 0000111 f3 101 opc 0010011 MATCH
fsri       0x1c315093   hi5 00011 [26:20] 1000011 f3 101 opc 0010011 MATCH
```

## 4. ELF to TB memory image (step 4)

`python3 dv/auto_dv/stim/gen_elf2mem.py prog.elf` (format defined in that file's docstring:
word-addressed `$readmemh` image with `@<word index>` runs, plus a `.sym.json` sidecar with
entry, segments, global symbols and the read-back checksum): 29038 words,
sum32 0xab1b7a25, entry 0x80000080, segments [{'vaddr': '0x1a110800', 'size': 16}, {'vaddr': '0x80000080', 'size': 116136}].
Image head:

```
@06844200
00c0006f
00000013
7b200073
```

## 5. Standalone Spike run (step 5)

```
tools/spike/bin/spike --isa=rv32imc_zicsr_zifencei_zba_zbb_zbc_zbs_zicntr_zihpm_zicclsm --priv=mu \
    --pmpregions=16 --pmpgranularity=4 --triggers=1 -m0x1a110000:0x1000,0x80000000:0x100000 \
    --pc=0x80000080 --log-commits --log=spike_commits.log prog.elf
```

Exit 0 (Spike's HTIF saw the `tohost` write with payload 1 = pass); 15259 commit-log
lines. Head (first fetch at the boot address, jump to `_start`, `csrr mhartid`):

```
core   0: 3 0x80000080 (0x0800006f)
core   0: 3 0x80000100 (0xf14022f3) x5  0x00000000
core   0: 3 0x80000104 (0x4301) x6  0x00000000
core   0: 3 0x80000106 (0x00628263)
core   0: 3 0x8000010a (0x00000117) x2  0x8000010a
```

Tail (the generator's `write_tohost: sw gp, tohost` store, `mem 0x80002940 0x00000001`, then
the `_exit` spin until HTIF polls; HTIF checks `tohost` every 5000 instructions, which is why a
few thousand spin-loop lines follow the store):

```
core   0: 3 0x800026f4 (0x243f2823) mem 0x80002940 0x00000001
core   0: 3 0x800026f8 (0xbfe5)
core   0: 3 0x800026f0 (0x00000f17) x30 0x800026f0
core   0: 3 0x800026f4 (0x243f2823) mem 0x80002940 0x00000001
```

## 6. Limitations found (inherited by the Test Writer)

1. Section alignment vs boot address: riscv-dv aligns the vectored `mtvec_handler` to 256 bytes
   inside `.text`, so `.text` cannot start at boot + 0x80; the `.gen_boot` entry section
   (`j _start`) is linked there instead and is the ELF entry point. Every program (generated or
   directed) must link `gen_boot_stub.S` unless it places its own entry at that address.
2. `-Wl,-N` is required with `gen_link.ld`: without it ld maps the ELF headers into the DM window
   as a PT_LOAD segment starting at 0x1A110000.
3. riscv-dv debug ROM: emitted as labels inside `.text`, not at `DmHaltAddr`; `support_debug_mode
   = 0` in the core setting until a post-processing step (or a user-extension override of the
   debug ROM generator) moves it into `.debug_rom` with the exception entry at +8. Directed debug
   programs can use `.debug_rom` today (gen_debug_rom_stub.S shows the layout).
4. riscv-dv knows only the standard interrupt causes 3/7/11; ibex's 15 fast interrupts and the
   NMI are TB stimulus, and the vectored table must have 32 entries (`max_interrupt_vector_num
   = 32`) so the generator emits handlers for ids 1..31.
5. Zcb/Zcmp: unknown to this riscv-dv revision and to gcc 10.2 (`-march` has no zcb/zcmp);
   directed programs must use `.insn`/`.2byte` encodings.
6. Draft bitmanip (Zbp/Zbr/Zbt/Zbf): the assembler accepts them and the encodings match the RTL,
   but the pinned upstream Spike lacks them (T-019 notes), so the riscv-dv target enables the
   ratified groups only; draft ops go through directed self-checking programs with the shim's
   reference-execution path (architecture sections C5.5).
7. run.py argument syntax: values beginning with `-` must use `=` (`--cmp_opts=-licqueue`);
   `--cmp_opts -licqueue` is parsed as a missing argument.
8. riscv-dv's `gcc_compile` step hard-codes `-T <riscv-dv>/scripts/link.ld` and
   `-I <riscv-dv>/user_extension`, so the team flow runs only the `gen` step of run.py and does
   assembly/linking itself (as above).
9. `riscv-dv`'s trap handlers clear `mip` with a CSR write, which is a no-op on ibex (read-only
   mip): level interrupts need the TB to deassert or the planned user-extension ack store.
10. Spike HTIF end detection polls `tohost` every 5000 instructions: the standalone log carries
    a spin-loop tail; the lock-step shim does not use HTIF (it sees the tohost store directly).
11. The generator's PMP setup writes `mseccfg` (`csrwi 0x747, 4` = RLB) before the regions; with
    `support_epmp = 1` random programs will exercise Smepmp; Spike accepted it here.

## 7. Acceptance

- Generator compiles with VCS (0 errors), warning classes listed and attributed to vendored files.
- Own target directory exists and drives the generator; program generated from seed 1.
- Assembled and linked with `$RISCV_GCC -march=rv32imcb`; mnemonic acceptance recorded (62/62)
  and encodings checked against the RTL table (0 mismatches).
- ELF converted to the defined image format with symbols and checksum.
- Standalone Spike runs the program from the boot address to its end-of-test marker, exit 0.
