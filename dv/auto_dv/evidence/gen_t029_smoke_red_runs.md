# T-029 evidence: gen_smoke_tb_top failure paths proven (red runs) and Critic P-01..P-07 closure

Owner: tb-infra. Date: 2026-09-03 (05:54-05:55 UTC). Host: this site host, local, no LSF, `bash -lc`
with `ci/env.sh` sourced. Build configuration: `opentitan`. Fresh out-tree
`dv/auto_dv/work/tb-infra/out_t029/smoke/` (compile), `red1/`, `red2/`, `green2/` (runs).
Driver: `dv/auto_dv/work/tb-infra/gen_t005_compile.sh` (working file; vcs from the clone root,
simv from the out directory, droppings swept into the out-tree: no `ucli.key` at the clone root
after this run). Critic report: `dv/auto_dv/docs/gen_critic_t005_dv_principles_v1.md`.

## 1. Edits made for T-029 (the only edits to the T-005 files)

| Finding | Change |
|---|---|
| P-01 (medium) unproven `$fatal` paths | red runs below; smoke red-run knob `+gen_smoke_intg_flip=<bit>` (`gen_tb_pkg::PLUSARG_SMOKE_INTG_FLIP`) added to gen_smoke_tb_top.sv; no new check |
| P-02 (medium) vacuous pass without RVFI | gen_smoke_tb_top.sv: `` `ifndef RVFI `` time-0 `$fatal("gen_smoke_tb_top requires +define+RVFI ...")` |
| P-03 (low) undocumented smoke contract | gen_component_api_dut_top.md Section 5a: tokens, knobs, what fails, tier statement |
| P-04 (low) banner gaps | gen_dut_top.sv banner prints `RndCnstLfsrSeed`, `RndCnstLfsrPerm` and names the PMP reset parameters as ibex_core (ibex_pkg) defaults |
| P-05 (low) re-typed literals | gen_tb_pkg.sv: `GEN_BOOT_FETCH_OFFSET`, `GEN_DATA_W`, `GEN_INTG_W` removed (no consumer) |
| P-06 (low) dangling Q tags | gen_dut_top.sv header cites gen_intervention_log.md Q-002 (revised) and LOG-004 |
| P-07 (low) guard timing vs doc | gen_dut_top.sv: RegFile guard is now a generate-scope `$fatal` (elaboration system task); API doc wording matches |
| cross-review info | gen_filelist.py header now reads `fusesoc 2.4.3`; gen_rtl.f regenerated (94 entries, unchanged list) |

Regression-tier statement: `gen_smoke_tb_top` is the compile/elaboration proof for T-005/T-010
only and is NOT a regression-tier test; the real TB top replaces it. Its two `$fatal` checks are
TB self-checks whose failure paths are proven below; trust-triad rules 2 and 3 do not apply to it
because it never enters a tier (if Runtime ever lists it, this statement is void and both rules
apply).

## 2. Compile (fresh out directory)

Same command as `dv/auto_dv/evidence/gen_t005_compile_log_excerpt.md` Section 1 (unchanged
flag set; `+define+RVFI`; config from `util/ibex_config.py opentitan vcs_opts`). Result:
`CPU time: 8.020 seconds to compile + .241 seconds to elab + .767 seconds to link`; 0 errors; warning classes unchanged from T-005 (all in rtl/ibex_core.sv RVFI stage loop
and the `-lca` flag):

```
     32 Warning-[SIOB]
      1 Warning-[LCA_FEATURES_ENABLED]
```

## 3. Green run

`<out>/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=none +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan +gen_smoke_cycles=3000 -l <out>/sim/sim.log` (from `<out>/sim`):

```
GEN_CONFIG_BANNER build_config=opentitan
GEN_CONFIG_BANNER BaseIsa=BaseIsaRV32IorCHERIoT RV32M=RV32MSingleCycle RV32B=RV32BOTEarlGrey RV32ZC=RV32ZcaZcbZcmp RegFile=RegFileFF
GEN_CONFIG_BANNER RV32E=0 BranchTargetALU=1 WritebackStage=1 ICache=1 ICacheECC=1 ICacheScramble=1
GEN_CONFIG_BANNER BranchPredictor=0 DbgTriggerEn=1 DbgHwBreakNum=1 SecureIbex=1
GEN_CONFIG_BANNER PMPEnable=1 PMPGranularity=0 PMPNumRegions=16 MHPMCounterNum=10 MHPMCounterWidth=32
GEN_CONFIG_BANNER RegFileECC=0 ResetAll=1 DummyInstructions=1 MemECC=1 ICacheTweakInfection=1
GEN_CONFIG_BANNER MemDataWidth=39 RegFileDataWidth=32 RegFileCapEccWidth=35 BusSizeECC=39 TagSizeECC=28 LineSizeECC=78
GEN_CONFIG_BANNER DmBaseAddr=0x1a110000 DmAddrMask=0x00000fff DmHaltAddr=0x1a110800 DmExceptionAddr=0x1a110808
GEN_CONFIG_BANNER CsrMvendorId=0x00000000 CsrMimpId=0x00000000 cheriot_enable=Off rf_test_en=0
GEN_CONFIG_BANNER RndCnstLfsrSeed=0xac533bf4 RndCnstLfsrPerm=0x1e35ecba467fd1b12e958152c04fa43878a8daed
GEN_CONFIG_BANNER PMPRstCfg/PMPRstAddr/PMPRstMsecCfg=ibex_pkg::PmpCfgRst/PmpAddrRst/PmpMseccfgRst (ibex_core defaults, all regions OFF)
GEN_CONFIG_BANNER RVFI=1
GEN_CONFIG_BANNER GEN_DUT_SPLIT_INTG=0
GEN_SMOKE: max_cycles=3000 boot_addr=0x80000000
GEN_SMOKE: retired=2995 alerts=0 core_busy=On irq_pending=0 data_tag_o=0
GEN_SMOKE_PASS
$finish called from file "dv/auto_dv/tb/gen_smoke_tb_top.sv", line 390.
$finish at simulation time              3004500
```

## 4. Red run 1: retirement check (`GEN_SMOKE_FAIL: no RVFI retirement observed`)

`<out>/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=none +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan +gen_smoke_cycles=1 -l <out>/red1/sim.log` (one post-reset cycle:
nothing can retire):

```
GEN_SMOKE: max_cycles=1 boot_addr=0x80000000
GEN_SMOKE: retired=0 alerts=0 core_busy=On irq_pending=0 data_tag_o=0
Fatal: "dv/auto_dv/tb/gen_smoke_tb_top.sv", 386: gen_smoke_tb_top: at time 55000 ps
GEN_SMOKE_FAIL: no RVFI retirement observed
$finish called from file "dv/auto_dv/tb/gen_smoke_tb_top.sv", line 386.
$finish at simulation time                 5500
```

The `$fatal` fires (VCS "Fatal:" line) with the named token. The simv process exit status was 0
in this run: pass/fail MUST be taken from the token and the collected fatal, never from the exit
code (SIM_RECIPE Section 5), which the smoke contract states.

## 5. Red run 2: alert check (`GEN_SMOKE_FAIL: <n> alert cycles observed`)

`<out>/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=none +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan +gen_smoke_cycles=3000 +gen_smoke_intg_flip=5 -l <out>/red2/sim.log`
(bit 5 of the TB-side SECDED-encoded NOP word flipped on every fetch response; the core's
integrity decoder sees a single-bit error on each consumed fetch, raises `alert_major_bus_o` and
treats the fetch as an instruction access fault, so the program traps repeatedly):

```
GEN_SMOKE: corrupting NOP word bit 5 (expect alert_major_bus_o)
GEN_SMOKE: max_cycles=3000 boot_addr=0x80000000
GEN_SMOKE: retired=999 alerts=2998 core_busy=On irq_pending=0 data_tag_o=0
Fatal: "dv/auto_dv/tb/gen_smoke_tb_top.sv", 388: gen_smoke_tb_top: at time 30045000 ps
GEN_SMOKE_FAIL: 2998 alert cycles observed
$finish called from file "dv/auto_dv/tb/gen_smoke_tb_top.sv", line 388.
$finish at simulation time              3004500
```

## 6. Green re-run after the red runs

```
GEN_SMOKE: max_cycles=3000 boot_addr=0x80000000
GEN_SMOKE: retired=2995 alerts=0 core_busy=On irq_pending=0 data_tag_o=0
GEN_SMOKE_PASS
$finish called from file "dv/auto_dv/tb/gen_smoke_tb_top.sv", line 390.
$finish at simulation time              3004500
```

## 7. Acceptance

- Both `$fatal` checks shown to fire with their tokens (Sections 4 and 5); green before and after.
- Vacuous-pass guard added (P-02); not exercised here because a build without `+define+RVFI` is
  not part of any flow; it is a one-line time-0 `$fatal` whose failure path is the same VCS
  mechanism shown in Sections 4-5.
- Compile evidence for T-005 remains valid: same command, same warning classes, banner extended.
