# T-019 evidence: upstream Spike (riscv-isa-sim) clone and build

Owner: tb-infra. Date: 2026-09-03 (05:12-05:16 UTC). Host: this site host, local build, no LSF,
`bash -lc` with `ci/env.sh` sourced (gcc-toolset-11 host compiler, dtc 1.7.2 on PATH). Recipe:
docs/dv/SIM_RECIPE.md Section 11. Locations (both untracked; `tools/` is excluded through
`.git/info/exclude`, never committed): clone `tools/riscv-isa-sim`, install prefix `tools/spike`.
The fenced paths `/localdev/fzhang/ws/tools/spike-ibex-cosim` and `/localdev/fzhang/ws/tools/src`
were not read or referenced.

## 1. Commands (from dv/auto_dv/work/tb-infra/spike_build.log)

```
cd tools && rm -rf riscv-isa-sim spike
mkdir riscv-isa-sim && cd riscv-isa-sim && git init -q
git remote add origin https://github.com/riscv/riscv-isa-sim.git
git fetch --depth 1 origin 4ffd6ba860f4190ceac2716fa3c2cf139e85538f && git checkout -q FETCH_HEAD
mkdir -p build && cd build
../configure --prefix=<clone>/tools/spike --with-boost=no --with-boost-asio=no --with-boost-regex=no
make -j8
make install
```

Log markers:

```
Thu Sep  3 05:12:08 UTC 2026
+ git init -q
+ git remote add origin https://github.com/riscv/riscv-isa-sim.git
+ git fetch --depth 1 origin 4ffd6ba860f4190ceac2716fa3c2cf139e85538f
+ git checkout -q FETCH_HEAD
+ echo 'spike commit: 4ffd6ba860f4190ceac2716fa3c2cf139e85538f'
spike commit: 4ffd6ba860f4190ceac2716fa3c2cf139e85538f
+ ../configure --prefix=/localdev/fzhang/ws/ibex-challenge/tools/spike --with-boost=no --with-boost-asio=no --with-boost-regex=no
+ echo 'configure ok'
configure ok
+ make -j8
+ echo 'make ok'
make ok
+ make install
+ echo 'install ok'
install ok
+ echo BUILD_EXIT=0
BUILD_EXIT=0
Thu Sep  3 05:14:06 UTC 2026
```

Pinned commit (verified after checkout): `4ffd6ba860f4190ceac2716fa3c2cf139e85538f` (the commit SIM_RECIPE.md's `spike-built-on` line
names; Spike version string 1.1.1-dev).

## 2. configure summary (excerpt of build/configure.log)

```
checking for dtc... /tools_soc/opensrc/dtc/1.7.2/bin/dtc
config.status: creating Makefile
config.status: creating config.h
```

Boost disabled by the three `--with-boost*=no` flags (site boost 1.66 does not compile under the
gcc-11 C++17/20 mode); only the `-s` socket option is lost.

## 3. make log tail (build/make.log)

```
g++ -L. -Wl,--export-dynamic   -Wl,-rpath,/localdev/fzhang/ws/ibex-challenge/tools/spike/lib  extension.o -o spike-log-parser spike-log-parser.o  libspike_main.
g++ -L. -Wl,--export-dynamic   -Wl,-rpath,/localdev/fzhang/ws/ibex-challenge/tools/spike/lib  extension.o -o xspike xspike.o  libspike_main.a  libriscv.a  libdi
g++ -L. -Wl,--export-dynamic   -Wl,-rpath,/localdev/fzhang/ws/ibex-challenge/tools/spike/lib  extension.o -o termios-xspike termios-xspike.o  libspike_main.a  l
g++ -L. -Wl,--export-dynamic   -Wl,-rpath,/localdev/fzhang/ws/ibex-challenge/tools/spike/lib   -o spike-dasm spike-dasm.o  libspike_dasm.a  libriscv.a  libsoftf
```

Wall clock: about 2 minutes with -j8 (05:12:24 start of make to 05:14:06 BUILD_EXIT=0).

## 4. Installed artifacts

Binaries (`tools/spike/bin`): elf2hex spike spike-dasm spike-log-parser termios-xspike xspike

```
Spike RISC-V ISA Simulator 1.1.1-dev

usage: spike [host options] <target program> [target options]
```

Libraries (`tools/spike/lib`, bytes and name):

```
369171080 libcustomext.so
7764806 libdisasm.a
9368034 libfesvr.a
381468168 libriscv.so
845432 libsoftfloat.so
```

pkg-config files: `tools/spike/lib/pkgconfig/riscv-riscv.pc`, `riscv-fesvr.pc`, `riscv-disasm.pc`.

Headers (`tools/spike/include`):

```
riscv: 33 files
fesvr: 16 files
softfloat: 2 files
fdt: 3 files
abstract_device.h abstract_interrupt_controller.h bloom_filter.h cachesim.h cfg.h common.h csrs.h debug_defines.h debug_module.h debug_rom_defines.h decode.h devices.h disasm.h dtb_discovery.h dts.h encoding.h entropy_source.h extension.h imsic.h isa_parser.h jtag_dtm.h log_file.h memtracer.h mmu.h platform.h processor.h remote_bitbang.h rocc.h sim.h simif.h trap.h triggers.h vector_unit.h
```

## 5. Library API link test (shim feasibility)

Source: `dv/auto_dv/work/tb-infra/gen_spike_linktest.cc` (working file). It builds one
`processor_t` without `sim_t` over our own `simif_t` (flat memory, MMIO failing), steps three
instructions (addi, addi, sh1add), and exercises `enable_log_commits`/`log_reg_write`,
`get_csr`/`put_csr`, `mip->backdoor_write_with_mask`, `n_pmp`, and an instruction access fault
through `simif_t` landing on mtvec. Build and run:

```
g++ -std=c++2a -I tools/spike/include dv/auto_dv/work/tb-infra/gen_spike_linktest.cc \
    -L tools/spike/lib -lriscv -Wl,-rpath,$PWD/tools/spike/lib -o <out>/gen_spike_linktest
<out>/gen_spike_linktest
```

Result (`dv/auto_dv/work/tb-infra/out_t019/linktest.log`):

```
x1 after addi                got 0x5 exp 0x5 OK
log_reg_write has x1         got 0x1 exp 0x1 OK
x2 after addi                got 0xc exp 0xc OK
x3 after sh1add              got 0x16 exp 0x16 OK
pc after 3 steps (low32)     got 0x8000000c exp 0x8000000c OK
pc raw is sign-extended      got 0xffffffff exp 0xffffffff OK
priv is M                    got 0x3 exp 0x3 OK
last_inst_priv               got 0x3 exp 0x3 OK
mstatus peek                 got 0x0 exp 0x0 OK
mscratch put/get             got 0xdeadbeef exp 0xdeadbeef OK
mip backdoor MTIP            got 0x80 exp 0x80 OK
mip backdoor cleared         got 0x0 exp 0x0 OK
pmp region count             got 0x10 exp 0x10 OK
fetch fault -> mtvec         got 0x80000100 exp 0x80000100 OK
mcause instr access fault    got 0x1 exp 0x1 OK
GEN_SPIKE_LINKTEST PASS (0 failures)
```

Two findings for the DPI shim design, both recorded in the TB architecture component sections
(C5.1, C5.3):

1. Include path: only `<prefix>/include` may be on the include path. Adding
   `<prefix>/include/fesvr` shadows the system `<syscall.h>` with fesvr's `syscall.h` and
   libstdc++'s `atomic_wait.h` fails with `SYS_futex was not declared` (first attempt).
2. RV32 state is held sign-extended in 64-bit `reg_t` (pc read back as 0xffffffff8000000c after
   the first attempt compared 64 bits); the shim truncates every compared value to 32 bits.

## 6. Acceptance

- Clone at the pinned commit: yes. Configure with boost disabled: yes. `make -j8` and
  `make install`: exit 0. `tools/spike/bin/spike --help` runs: yes.
- `libriscv.so`, `libsoftfloat.so`, `libfesvr.a`, `libdisasm.a`, `libcustomext.so` and the
  header directories exist: yes.
- Library usable from an external C++20 program with the API the shim needs: yes (14/14 checks).
