# T-029 / T-036 evidence: gen_smoke_tb_top failure paths proven (green, red, red, green)

Owner: tb-infra. First written 2026-09-03 05:55 UTC (T-029); REWRITTEN 06:22 UTC (T-036) after the
cross-model diff review (`dv/auto_dv/reviews/2026-09-03-claude-diff-881a771a-3c623e54.md`, major:
the v1 "green re-run" section had no artifact and the cited paths did not match disk; logged as
LOG-005). Every path below exists on disk and every number is copied from the named file. Host:
this site host, local, no LSF, `bash -lc` with `ci/env.sh` sourced. Build configuration:
`opentitan`. Out-tree (not committed): `dv/auto_dv/work/tb-infra/out_t036/smoke/`.

Driver (committed): `dv/auto_dv/tb/gen_smoke_run.sh`. It compiles once and then runs the fixed
sequence GREEN, RED (no retirement), RED (integrity flip), GREEN, each into its own directory
`run_01_green/`, `run_02_red_noretire/`, `run_03_red_intg/`, `run_04_green/` with its own
`sim.log`, `stdout.log` and per-run exit status, and writes `runs_summary.txt` (one line per run:
plusargs, simv exit status (the `simv_exit` field is the only record of the exit status; sim.log does not carry it), verdict token found, number of VCS "Fatal:" lines, expected token,
as-expected or MISMATCH). Invocation used here:

```
bash -lc 'source ci/env.sh && OUT=<clone>/dv/auto_dv/work/tb-infra/out_t036/smoke bash dv/auto_dv/tb/gen_smoke_run.sh'
```

Critic report closed by T-029: `dv/auto_dv/docs/gen_critic_t005_dv_principles_v1.md` (APPROVED in
`gen_critic_t005_dv_principles_v2.md` with residuals R-01..R-03).

## 1. Edits made for T-029 (the only edits to the T-005 files)

| Finding | Change |
|---|---|
| P-01 (medium) unproven `$fatal` paths | red runs below; smoke red-run knob `+gen_smoke_intg_flip=<bit>` (`gen_tb_pkg::PLUSARG_SMOKE_INTG_FLIP`) added to gen_smoke_tb_top.sv; no new check |
| P-02 (medium) vacuous pass without RVFI | gen_smoke_tb_top.sv: `` `ifndef RVFI `` time-0 `$fatal("gen_smoke_tb_top requires +define+RVFI ...")` |
| P-03 (low) undocumented smoke contract | gen_component_api_dut_top.md Section 5a: tokens, knobs, what fails, tier statement |
| P-04 (low) banner gaps | gen_dut_top.sv banner prints `RndCnstLfsrSeed`, `RndCnstLfsrPerm` and names the PMP reset parameters as ibex_core (ibex_pkg) defaults |
| P-05 (low) re-typed literals | gen_tb_pkg.sv: `GEN_BOOT_FETCH_OFFSET`, `GEN_DATA_W`, `GEN_INTG_W` removed (no consumer) |
| P-06 (low) dangling Q tags | gen_dut_top.sv header cites gen_intervention_log.md Q-002 (revised) and LOG-004 |
| P-07 (low) guard timing vs doc | gen_dut_top.sv: RegFile guard is a generate-scope `$fatal` (elaboration system task); API doc wording matches |
| cross-review info | gen_filelist.py header reads `fusesoc 2.4.3`; gen_rtl.f regenerated (list unchanged) |
| T-036 (diff review minor) | the driver is committed as `dv/auto_dv/tb/gen_smoke_run.sh` and performs the whole sequence |

Tier statement: `gen_smoke_tb_top` is the compile/elaboration proof for T-005/T-010 and is NOT a
measured regression test. Runtime places it in the `check` tier (`measured: false`, selectable
only by `--tier check` or by name; R-01 resolution, T-038), so trust-triad rules 2 and 3 do not
apply to it; its two `$fatal` checks are TB self-checks whose failure paths are proven below.
Residuals R-02 (compile the two guards red once) and R-03 (range `$fatal` on the flip bit) are
owed on the next touch of the T-005 files.

## 2. Compile (fresh out directory, `out_t036/smoke/compile.log`)

Same command as `dv/auto_dv/evidence/gen_t005_compile_log_excerpt.md` Section 1 (unchanged flag
set; `+define+RVFI`; config from `util/ibex_config.py opentitan vcs_opts`). `CPU time: 6.702 seconds to compile + .228 seconds to elab + .681 seconds to link`; 0 errors;
warning classes unchanged from T-005:

```
     32 Warning-[SIOB]
      1 Warning-[LCA_FEATURES_ENABLED]
```

## 3. The four runs (`out_t036/smoke/runs_summary.txt`, verbatim)

Common plusargs of every run: `+vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=none +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan`; each run executed from inside its own directory.

```
run_01_green           plusargs=[+gen_smoke_cycles=3000] simv_exit=0 token=PASS fatal_lines=0 expected=PASS -> as-expected
run_02_red_noretire    plusargs=[+gen_smoke_cycles=1] simv_exit=0 token=FAIL fatal_lines=1 expected=FAIL -> as-expected
run_03_red_intg        plusargs=[+gen_smoke_cycles=3000 +gen_smoke_intg_flip=5] simv_exit=0 token=FAIL fatal_lines=1 expected=FAIL -> as-expected
run_04_green           plusargs=[+gen_smoke_cycles=3000] simv_exit=0 token=PASS fatal_lines=0 expected=PASS -> as-expected
sequence result: ALL-AS-EXPECTED
```

Driver changes after this evidence was recorded (Critic v3 findings D-01/D-02, applied 2026-09-03
06:55 UTC): the driver refuses an existing OUT unless `FORCE=1` is given explicitly, refuses an OUT
outside the clone, and reads the plusarg names from `gen_tb_pkg.sv` and the verdict tokens from
`gen_smoke_tb_top.sv` instead of re-typing them (echoed into `<OUT>/names.txt`). Re-proof of the
changed driver: `dv/auto_dv/work/tb-infra/out_d0102/` (fresh directory), same four verdict lines,
sequence result ALL-AS-EXPECTED, compile 0 errors, driver exit 0. The artifacts cited above in
`out_t036/smoke/` are unchanged.

Log timestamps (creation order proves the sequence; `ls --time-style` host-local EDT = UTC-4, so 02:22 local is 06:22 UTC, matching the header):

```
2026-09-03_02:22:19 dv/auto_dv/work/tb-infra/out_t036/smoke/run_01_green/sim.log
2026-09-03_02:22:24 dv/auto_dv/work/tb-infra/out_t036/smoke/run_02_red_noretire/sim.log
2026-09-03_02:22:33 dv/auto_dv/work/tb-infra/out_t036/smoke/run_03_red_intg/sim.log
2026-09-03_02:22:38 dv/auto_dv/work/tb-infra/out_t036/smoke/run_04_green/sim.log
```

### 3.1 run_01_green (`out_t036/smoke/run_01_green/sim.log`)

```
GEN_CONFIG_BANNER RndCnstLfsrSeed=0xac533bf4 RndCnstLfsrPerm=0x1e35ecba467fd1b12e958152c04fa43878a8daed
GEN_CONFIG_BANNER PMPRstCfg/PMPRstAddr/PMPRstMsecCfg=ibex_pkg::PmpCfgRst/PmpAddrRst/PmpMseccfgRst (ibex_core defaults, all regions OFF)
GEN_SMOKE: max_cycles=3000 boot_addr=0x80000000
GEN_SMOKE: retired=2995 alerts=0 core_busy=On irq_pending=0 data_tag_o=0
GEN_SMOKE_PASS
$finish called from file "dv/auto_dv/tb/gen_smoke_tb_top.sv", line 390.
$finish at simulation time              3004500
```

### 3.2 run_02_red_noretire: retirement check fires (`+gen_smoke_cycles=1`)

```
GEN_CONFIG_BANNER RndCnstLfsrSeed=0xac533bf4 RndCnstLfsrPerm=0x1e35ecba467fd1b12e958152c04fa43878a8daed
GEN_CONFIG_BANNER PMPRstCfg/PMPRstAddr/PMPRstMsecCfg=ibex_pkg::PmpCfgRst/PmpAddrRst/PmpMseccfgRst (ibex_core defaults, all regions OFF)
GEN_SMOKE: max_cycles=1 boot_addr=0x80000000
GEN_SMOKE: retired=0 alerts=0 core_busy=On irq_pending=0 data_tag_o=0
Fatal: "dv/auto_dv/tb/gen_smoke_tb_top.sv", 386: gen_smoke_tb_top: at time 55000 ps
GEN_SMOKE_FAIL: no RVFI retirement observed
$finish called from file "dv/auto_dv/tb/gen_smoke_tb_top.sv", line 386.
$finish at simulation time                 5500
```

### 3.3 run_03_red_intg: alert check fires (`+gen_smoke_intg_flip=5`)

Bit 5 of the TB-side SECDED-encoded NOP word is flipped on every fetch response; the core's
integrity decoder sees a single-bit error on each consumed fetch, raises `alert_major_bus_o` and
treats the fetch as an instruction access fault, so the program traps repeatedly.

```
GEN_CONFIG_BANNER RndCnstLfsrSeed=0xac533bf4 RndCnstLfsrPerm=0x1e35ecba467fd1b12e958152c04fa43878a8daed
GEN_CONFIG_BANNER PMPRstCfg/PMPRstAddr/PMPRstMsecCfg=ibex_pkg::PmpCfgRst/PmpAddrRst/PmpMseccfgRst (ibex_core defaults, all regions OFF)
GEN_SMOKE: corrupting NOP word bit 5 (expect alert_major_bus_o)
GEN_SMOKE: max_cycles=3000 boot_addr=0x80000000
GEN_SMOKE: retired=999 alerts=2998 core_busy=On irq_pending=0 data_tag_o=0
Fatal: "dv/auto_dv/tb/gen_smoke_tb_top.sv", 388: gen_smoke_tb_top: at time 30045000 ps
GEN_SMOKE_FAIL: 2998 alert cycles observed
$finish called from file "dv/auto_dv/tb/gen_smoke_tb_top.sv", line 388.
$finish at simulation time              3004500
```

### 3.4 run_04_green (after both red runs; `out_t036/smoke/run_04_green/sim.log`)

```
GEN_CONFIG_BANNER RndCnstLfsrSeed=0xac533bf4 RndCnstLfsrPerm=0x1e35ecba467fd1b12e958152c04fa43878a8daed
GEN_CONFIG_BANNER PMPRstCfg/PMPRstAddr/PMPRstMsecCfg=ibex_pkg::PmpCfgRst/PmpAddrRst/PmpMseccfgRst (ibex_core defaults, all regions OFF)
GEN_SMOKE: max_cycles=3000 boot_addr=0x80000000
GEN_SMOKE: retired=2995 alerts=0 core_busy=On irq_pending=0 data_tag_o=0
GEN_SMOKE_PASS
$finish called from file "dv/auto_dv/tb/gen_smoke_tb_top.sv", line 390.
$finish at simulation time              3004500
```

## 4. Reading the results

- Both `$fatal` checks fire with their tokens (3.2, 3.3) and the smoke passes before and after
  (3.1, 3.4). The simv process exit status is 0 in ALL four runs, including the two red runs:
  pass/fail MUST be taken from the tokens and the collected fatal, never from the exit code
  (SIM_RECIPE Section 5); the smoke contract and `runs_summary.txt` state exactly that.
- The vacuous-pass guard (P-02) is a one-line time-0 `$fatal` for a build without `+define+RVFI`;
  it is not exercised by this sequence (residual R-02 will compile it red once and record it).
- Compile evidence for T-005 remains valid: same command, same warning classes, banner extended.
