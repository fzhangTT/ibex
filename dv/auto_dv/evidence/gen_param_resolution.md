# Effective ibex_core parameters under the "opentitan" build configuration

Owner: rtl-arch (T-003). Status: complete for the core; three wrapper-choice items are flagged
as OWNER QUESTION (section 4). Every value below is cited to its source line. Build configuration:
`opentitan` (ibex_configs.yaml:41-60). Verified 2026-09-03 against the clone at commit 1908ddd.

## 1. What the config script emits

`util/ibex_config.py opentitan vcs_opts` (executed, output copied verbatim):

```
+define+BaseIsa=ibex_pkg::BaseIsaRV32IorCHERIoT -pvalue+RV32E=0
+define+RV32M=ibex_pkg::RV32MSingleCycle +define+RV32B=ibex_pkg::RV32BOTEarlGrey
+define+RV32ZC=ibex_pkg::RV32ZcaZcbZcmp +define+RegFile=ibex_pkg::RegFileFF
-pvalue+BranchTargetALU=1 -pvalue+WritebackStage=1 -pvalue+ICache=1 -pvalue+ICacheECC=1
-pvalue+ICacheScramble=1 -pvalue+BranchPredictor=0 -pvalue+DbgTriggerEn=1 -pvalue+SecureIbex=1
-pvalue+PMPEnable=1 -pvalue+PMPGranularity=0 -pvalue+PMPNumRegions=16 -pvalue+MHPMCounterNum=10
-pvalue+MHPMCounterWidth=32
```

Mechanics (util/ibex_config.py:262-264, ibex_core.core:66-153): integer/bool fields become
`-pvalue+<Name>=<v>`, which VCS applies ONLY to parameters of the top-level module (SIM_RECIPE.md
section 2 note). Enum-typed fields (BaseIsa, RV32M, RV32B, RV32ZC, RegFile) become `+define+`
because VCS cannot override enum parameters from the command line (doc/02_user/integration.rst:
264-269). NOTHING under rtl/ consumes these defines (grep of rtl/ for `RV32M etc.: zero hits);
the only consumer in the clone is examples/simple_system/rtl/ibex_simple_system.sv:59-62, which
uses the pattern `parameter ibex_pkg::rv32m_e RV32M = `RV32M;` guarded by `ifndef` defaults
(:9). The DUT wrapper is therefore the place where both mechanisms must land (section 3).

## 2. ibex_core parameter values (rtl/ibex_core.sv:17-59 declarations)

Values are what ibex_top would pass (rtl/ibex_top.sv:369-410) for this config; the wrapper is
expected to mirror that derivation unless the owner rules otherwise (section 4).

| ibex_core parameter (decl line) | Value | Source of the value |
|---|---|---|
| BaseIsa (:18) | ibex_pkg::BaseIsaRV32IorCHERIoT (=1, rtl/ibex_pkg.sv:36-39) | +define+BaseIsa; ibex_top.sv:409 |
| PMPEnable (:19) | 1 | -pvalue+; ibex_top.sv:370 |
| PMPGranularity (:20) | 0 | -pvalue+; ibex_top.sv:371 |
| PMPNumRegions (:21) | 16 (= PMP_MAX_REGIONS, ibex_pkg.sv:419) | -pvalue+; ibex_top.sv:372 |
| PMPRstCfg (:22) | ibex_pkg::PmpCfgRst: all 16 regions lock=0 mode=OFF exec=write=read=0 (ibex_pkg.sv:769-786) | default; ibex_top.sv:22, :373 |
| PMPRstAddr (:23) | ibex_pkg::PmpAddrRst: all 16 = 34'h0 (ibex_pkg.sv:791-808) | default; ibex_top.sv:23, :374 |
| PMPRstMsecCfg (:24) | ibex_pkg::PmpMseccfgRst = {rlb 0, mmwp 0, mml 0} (ibex_pkg.sv:810) | default; ibex_top.sv:24, :375 |
| MHPMCounterNum (:25) | 10 (counters mhpmcounter3..12 exist) | -pvalue+; ibex_top.sv:376 |
| MHPMCounterWidth (:26) | 32 | -pvalue+; ibex_top.sv:377 |
| RV32E (:27) | 0 | -pvalue+; ibex_top.sv:378 |
| RV32M (:28) | ibex_pkg::RV32MSingleCycle (=3, ibex_pkg.sv:47-52) | +define+RV32M; ibex_top.sv:379 |
| RV32B (:29) | ibex_pkg::RV32BOTEarlGrey (=2, ibex_pkg.sv:54-59) | +define+RV32B; ibex_top.sv:380 |
| RV32ZC (:30) | ibex_pkg::RV32ZcaZcbZcmp (=3, ibex_pkg.sv:61-66) | +define+RV32ZC; ibex_top.sv:381 |
| BranchTargetALU (:31) | 1 | -pvalue+; ibex_top.sv:382 |
| WritebackStage (:32) | 1 | -pvalue+; ibex_top.sv:392 |
| ICache (:33) | 1 | -pvalue+; ibex_top.sv:383 |
| ICacheECC (:34) | 1 | -pvalue+; ibex_top.sv:384 |
| ICacheTweakInfection (:35) | 1 | ibex_top.sv:45 `= SecureIbex`, :385 (ibex_core default is 0) |
| BusSizeECC (:36) | 39 = BUS_SIZE 32 + IC_DATA_ECC_SIZE 7 | ibex_top.sv:221-222; ibex_pkg.sv:397, :412 (ibex_core default is 32) |
| TagSizeECC (:37) | 28 = IC_TAG_SIZE 22 + IC_TAG_ECC_SIZE 6 | ibex_top.sv:224-225; ibex_pkg.sv:410, :413 (ibex_core default is 22) |
| LineSizeECC (:38) | 78 = BusSizeECC 39 * IC_LINE_BEATS 2 | ibex_top.sv:223; ibex_pkg.sv:406 (ibex_core default is 64) |
| BranchPredictor (:39) | 0 | -pvalue+; ibex_top.sv:389 |
| DbgTriggerEn (:40) | 1 | -pvalue+; ibex_top.sv:390 |
| DbgHwBreakNum (:41) | 1 | ibex_top.sv:38 default, :391 (not in the config) |
| ResetAll (:42) | ibex_top passes 1 (`Lockstep = SecureIbex`, `ResetAll = Lockstep`, ibex_top.sv:212-213, :393); ibex_core default is 0 | OWNER QUESTION Q-B (section 4) |
| RndCnstLfsrSeed (:43) | ibex_pkg::RndCnstLfsrSeedDefault = 32'hac533bf4 (ibex_pkg.sv:741) | default; ibex_top.sv:46, :394 |
| RndCnstLfsrPerm (:44) | ibex_pkg::RndCnstLfsrPermDefault = 160'h1e35ecba467fd1b12e958152c04fa43878a8daed (ibex_pkg.sv:742-744) | default; ibex_top.sv:47, :395 |
| SecureIbex (:45) | 1 | -pvalue+; ibex_top.sv:396 |
| DummyInstructions (:46) | 1 | ibex_top.sv:214 `= SecureIbex`, :397 (ibex_core default is 0) |
| RegFileECC (:47) | ibex_top passes 0 (`localparam bit RegFileECC = 1'b0`, ibex_top.sv:215, :398; the lockstep shadow core gets `RegFileLockstepECC = Lockstep` = 1, :216, :1145) | OWNER QUESTION Q-A (section 4) |
| RegFileDataWidth (:48) | 32 (ibex_top.sv:217, :399); must be 39 if RegFileECC=1 | follows Q-A |
| RegFileCapEccWidth (:49) | 35 = REGCAP_W (ibex_top.sv:400; rtl/ibex_cheriot_pkg.sv:28); must be 42 = REGCAP_W+7 if RegFileECC=1 (ibex_top.sv:219 declares that value but only passes it to the lockstep core, :1148) | follows Q-A; hazard in section 4 |
| MemECC (:50) | 1 | ibex_top.sv:41 `= SecureIbex`, :401 |
| MemDataWidth (:51) | 39 = 32 + 7 | ibex_top.sv:42, :402 (ibex_core default expression gives the same when MemECC=1) |
| DmBaseAddr (:52) | 32'h1A110000 | default; ibex_top.sv:48, :403 |
| DmAddrMask (:53) | 32'h00000FFF | default; ibex_top.sv:49, :404 |
| DmHaltAddr (:54) | 32'h1A110800 | default; ibex_top.sv:50, :405 |
| DmExceptionAddr (:55) | 32'h1A110808 | default; ibex_top.sv:51, :406 |
| CsrMvendorId (:57) | 32'h0 | default; ibex_top.sv:58, :407 |
| CsrMimpId (:59) | 32'h0 | default; ibex_top.sv:63, :408 |

ibex_core-internal localparams (rtl/ibex_core.sv:193-197): PMPNumChan = 3; DataIndTiming =
SecureIbex = 1; PCIncrCheck = SecureIbex = 1; ShadowCSR = 1'b0 (hard-wired: shadow CSR alerts
cannot fire in this DUT).

ICacheScramble (config field, -pvalue+ICacheScramble=1) is NOT an ibex_core parameter. In
ibex_top it selects prim_ram_1p_scr for the icache RAMs (rtl/ibex_top.sv:43-44, :53-54). The
RAMs are TB test equipment (DV_prompt.txt Section 2), so the wrapper must accept the -pvalue+
(to keep the config command usable unchanged) but has nothing to forward; whether the TB RAM
model scrambles is a TB choice with no effect on DUT coverage.

## 3. What the wrapper must expose or consume

1. Declare top-level parameters with EXACTLY the config names and integer/bit types so the
   `-pvalue+` options apply: RV32E, BranchTargetALU, WritebackStage, ICache, ICacheECC,
   ICacheScramble, BranchPredictor, DbgTriggerEn, SecureIbex, PMPEnable, PMPGranularity,
   PMPNumRegions, MHPMCounterNum, MHPMCounterWidth. Forward all but ICacheScramble to ibex_core.
   A mismatch in a name is silent (VCS warns, the default applies): the time-0 config banner
   (dv_principles.md section 1) should print every one of them from the elaborated wrapper.
2. Consume the five `+define+` values as enum parameter defaults, e.g.
   `parameter ibex_pkg::rv32m_e RV32M = `RV32M;` with `ifndef fallbacks, following
   examples/simple_system/rtl/ibex_simple_system.sv:9-12, :59-62. BaseIsa must reach ibex_core,
   ibex_register_file_ff, and every module that has a BaseIsa parameter through ibex_core.
   RegFile selects the register-file module: only RegFileFF is in scope (DV_prompt Section 2);
   the wrapper may `ASSERT_INIT` that `RegFile == RegFileFF` rather than generate three variants.
3. Derive, as ibex_top does: DummyInstructions = SecureIbex; MemECC = SecureIbex; MemDataWidth =
   MemECC ? 39 : 32; ICacheTweakInfection = SecureIbex; BusSizeECC / TagSizeECC / LineSizeECC per
   ibex_top.sv:221-225 (do NOT rely on ibex_core defaults: they are the non-ECC widths 32/22/64
   and the icache RAM ports would be mis-sized).
4. Tie `cheriot_enable_i` to `ibex_pkg::IbexMuBiOff` (owner ruling).
5. Register file instance, mirroring rtl/ibex_top.sv:532-559 (gen_regfile_ff):
   `ibex_register_file_ff #(.BaseIsa(BaseIsa), .RV32E(RV32E), .DataWidth(RegFileDataWidth),
   .DummyInstructions(DummyInstructions), .WordZeroVal(RegFileDataWidth'(prim_secded_pkg::
   SecdedInv3932ZeroWord)))`. SecdedInv3932ZeroWord = 39'h2A00000000
   (vendor/lowrisc_ip/ip/prim/rtl/prim_secded_pkg.sv:275); truncated to 32 bits it is 0. With
   RegFileECC=1 the RF must also get CapWidth = RegFileCapEccWidth = 42 (its default is REGCAP_W
   = 35, rtl/ibex_register_file_ff.sv:58) so that rf_wcap_ecc_wb_o / rf_rcap_*_ecc_i widths match
   rtl/ibex_core.sv:100-102. Port wiring: rtl/ibex_top.sv:540-559 (test_en_i is unused by the FF
   file, rtl/ibex_register_file_ff.sv:232-233; tie 0).
6. Defines the build needs beyond the config: `+define+RVFI` if the RVFI ports are wanted (the
   config does not set it; only the .core lint/format targets do, ibex_core.core:185, :200). The
   RTL includes `prim_assert.sv` (vendor/lowrisc_ip/ip/prim/rtl/) and `dv_fcov_macros.svh`
   (vendor/lowrisc_ip/dv/sv/dv_utils/, included by rtl/ibex_core.sv:12, rtl/ibex_load_store_unit.sv:16
   and others): both directories must be on the include path. `DV_FCOV_SIGNAL` (dv_fcov_macros.svh:
   88-96) creates `fcov_*` nets inside the DUT unless `DV_FCOV_DISABLE` is defined; these are
   combinational mirrors and will appear in toggle/line coverage of the DUT hierarchy. Do not
   define SYNTHESIS (it removes the fcov signals and some assertions). INC_ASSERT is defined by
   prim_assert.sv for simulators that support SVA (prim_assert.sv:59-111): confirm in the compile
   log, because the ibex_core protocol assertions (NoMemResponseWithoutPendingAccess etc.,
   rtl/ibex_core.sv:1356-1422) live under `ifdef INC_ASSERT`.
7. File set: use ibex_core.core files_rtl (ibex_core.core:19-40) plus rtl/ibex_pkg.sv and
   rtl/ibex_cheriot_pkg.sv (ibex_pkg.core:9-12) plus the prim files. rtl/ibex_core.f is STALE:
   it omits ibex_pmp.sv, ibex_csr.sv, ibex_wb_stage.sv, ibex_dummy_instr.sv, ibex_icache.sv,
   ibex_branch_predict.sv, ibex_cheriot_ex.sv, ibex_cheriot_pkg.sv (compare rtl/ibex_core.f:5-21
   with ibex_core.core:19-40). Prim modules instantiated inside the DUT (verified by grep of the
   instantiations): prim_buf (vendor/lowrisc_ip/ip/prim_generic/rtl/prim_buf.sv),
   prim_secded_inv_39_32_enc/dec, prim_secded_inv_28_22_enc/dec, prim_lfsr (needs
   prim_cipher_pkg.sv compiled for the non-elaborated branch to parse), prim_secded_pkg (for the
   wrapper's WordZeroVal). prim_secded_inv_64_57_enc/dec only if RegFileECC=1.
   prim_clock_gating is a .core dependency but nothing in the DUT instantiates it.

## 4. Owner questions (wrapper choices that change the DUT boundary; for the DV Lead to word)

Q-A RegFileECC. ibex_top gives the MAIN core RegFileECC=0 (rtl/ibex_top.sv:215) and checks the
register-file ECC only in the lockstep shadow core (doc/03_reference/security.rst:91-100). The
lockstep core is out of scope, so a wrapper that mirrors ibex_top has NO register-file ECC check
anywhere, `gen_regfile_ecc` (rtl/ibex_core.sv:1214-1303) does not elaborate, and
alert_major_internal_o reduces to `pc_mismatch_alert` (rtl/ibex_core.sv:1350-1351 with
csr_shadow_err, cheriot_fatal_err, cheriot_enable_mubi_err constant 0). A wrapper that sets
RegFileECC=1 instead brings the encoder/decoders, the 39-bit RF and the rf_ecc_err_comb alert
into the DUT (more coverable logic, matches the SecureIbex intent, differs from OpenTitan's
integration). Consequences of RegFileECC=1: RegFileDataWidth=39, RegFileCapEccWidth=42 (else the
part-select rtl/ibex_core.sv:1264/1271 `[RegFileCapEccWidth-1:REGCAP_W]` is the reversed range
[34:35]), RF WordZeroVal=39'h2A00000000 (else every x0 read alerts), RF CapWidth=42.
Recommendation from rtl-arch: mirror ibex_top (RegFileECC=0) unless the owner wants the RF ECC
feature verified; state the choice in the config banner.

Q-B ResetAll. ibex_top passes 1 for SecureIbex builds (rtl/ibex_top.sv:212-213); ibex_core's
default is 0. It selects whether data-path flops have resets (e.g. rtl/ibex_if_stage.sv:589-616,
rtl/ibex_icache.sv:226-234, rtl/ibex_compressed_decoder.sv:893-909, rtl/ibex_wb_stage.sv:126-160).
Recommendation: ResetAll=1 (mirror ibex_top; also avoids X-propagation into coverage sampling).

Q-C RVFI. Not part of the config. Recommendation: `+define+RVFI` so the retirement trace is the
ISA-model comparison point (DV_prompt Section 7). It adds only flops and outputs, no functional
change; note the RVFI block reads hierarchical internals (rtl/ibex_core.sv:1851-1853, :2280-2292).

## 5. ibex_pkg constants a TB package should import, never re-type

Widths and sizes (rtl/ibex_pkg.sv:396-417), computed values in parentheses: ADDR_W 32, BUS_SIZE
32, BUS_BYTES (4), BUS_W (2), IC_SIZE_BYTES 4096, IC_NUM_WAYS 2, IC_LINE_SIZE 64, IC_LINE_BYTES
(8), IC_LINE_W (3), IC_NUM_LINES (256), IC_LINE_BEATS (2), IC_LINE_BEATS_W (1), IC_INDEX_W (8),
IC_INDEX_HI (10), IC_TAG_SIZE (22), IC_OUTPUT_BEATS (2), IC_DATA_ECC_SIZE 7, IC_TAG_ECC_SIZE 6,
SCRAMBLE_KEY_W 128, SCRAMBLE_NONCE_W 64. PMP: PMP_MAX_REGIONS 16, PMP_CFG_W 8, PMP_ADDR_MSB 33,
PMP_ADDR_LSB 2, PMP_I/PMP_I2/PMP_D channel indices (:419-430). MuBi: IbexMuBiWidth 4,
IbexMuBiOn 4'b0101, IbexMuBiOff 4'b1010 (:752-760). LFSR: LfsrWidth 32 and the RndCnst defaults
(:738-747). CSR bit positions CSR_MSTATUS_*_BIT, CSR_MSIX_BIT 3, CSR_MTIX_BIT 7, CSR_MEIX_BIT 11,
CSR_MFIX_BIT_LOW/HIGH 16/30, CSR_MSECCFG_*_BIT (:700-721); CSR_MARCHID_VALUE {1'b0, 31'd22},
CSR_MCONFIGPTR_VALUE 0, CSR_MISA_MXL 1 (:709, :727, :734).

Types and enums to import for stimulus/checking: base_isa_e, rv32m_e, rv32b_e, rv32zc_e,
regfile_e; opcode_e; alu_op_e, md_op_e; csr_op_e, priv_lvl_e, x_debug_ver_e; wb_instr_type_e;
ctrl_fsm_e (controller states), pc_sel_e, exc_pc_sel_e, instr_exp_e; irqs_t (15 fast + 3), 
exc_cause_t and the ExcCause* localparams (:343-380); nmi_int_cause_e; dbg_cause_e; pmp_req_e,
pmp_cfg_mode_e, pmp_cfg_t, pmp_mseccfg_t; csr_num_e (the full CSR address map, :463-694);
crash_dump_t (:16-22); ibex_mubi_t; ls_fsm_e, cap_rx_fsm_t (LSU FSM states, :816-822).
From rtl/ibex_cheriot_pkg.sv only REGCAP_W (:28) and cap_t (:87-98) are needed to size the
carve-out ports. From prim_secded_pkg: SecdedInv3932ZeroWord (:275).

Derived numbers the TB must not hard-code: number of PMP regions (PMPNumRegions), number of
perf counters (MHPMCounterNum -> mhpmcounter3..3+MHPMCounterNum-1), fast irq count (15 =
$bits(irqs_t.irq_fast)), icache RAM geometry (IC_NUM_WAYS x IC_NUM_LINES x TagSizeECC /
LineSizeECC), max outstanding data requests (2, see gen_interface_inventory.md), icache fill
buffers (NUM_FB = 4, rtl/ibex_icache.sv:72, a module localparam the TB can only mirror with a
comment pointing at the line).
