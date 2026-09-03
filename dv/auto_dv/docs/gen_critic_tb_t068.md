# Critic verdict: TB Infra T-068 remediation (commit df83749), steps 1a, 1b, 1c and 2a in one pass

Artifacts at commit df83749 (sha256 first 16 hex, lines):
- dv/auto_dv/evidence/gen_critic_response_tb_step1a.md  d48fd4a30aa18249  41
- dv/auto_dv/evidence/gen_critic_response_tb_step1b.md  d3339893259dea99  39
- dv/auto_dv/evidence/gen_critic_response_tb_step1c.md  2908dab1c6a8d190  24
- dv/auto_dv/evidence/gen_critic_response_tb_step2a.md  1f5f21612b34946c  34
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md      da247ae3ff8784f3  184 (178 retained files)
- dv/auto_dv/mutations/gen_mut_sva_rvalid_legal.md      8f6dbe0f614a0879  44
- dv/auto_dv/mutations/gen_mut_isa_fields.md            fcab41bf3ffd470a  54
- code: dv/auto_dv/tb/**, env/gen_agents_pkg.sv, gen_cfg_pkg.sv, gen_env_pkg.sv, gen_rvfi_pkg.sv, isa/**, gen_tb/**,
  stim/gen_program.py, the component API documents
Date: 2026-09-03T09:48Z   Role: Critic   Supersedes: gen_critic_tb_step1a_dv_principles_v1.md and
gen_critic_tb_step1b_dv_principles_v1.md (both REQUEST-CHANGES); first Critic verdict on steps 1c and 2a.
Every row below was checked against the committed code or the committed log, never against the response text
alone. Items the transcripts label UNRETAINED are listed in section 5 and count as nothing.

CRITIC VERDICT: APPROVE (steps 1a, 1b, 1c, 2a), with the three disputed rows ruled in section 3 and four
low residuals in section 4 that do not block.

## 1. My own findings (steps 1a and 1b)

| Row | Claimed | Verified at df83749 |
|---|---|---|
| 1a P-01 unknown keys, split descs | FIXED | 0 unquoted `desc:` lines in gen_tb_knobs.yaml; `check_keys` (gen_knobs_codegen.py:87-92) applied to every section (:97-158); nine refused fixtures in gen_ut_knobs_codegen.py:61-66, :216-221; knobs_codegen_t068.log 674 OK, `exit=0`. |
| 1a P-02 re-typed derived values | FIXED | `derive:` on GEN_IBUS_MAX_OUTSTANDING, GEN_IRQ_FAST_W, GEN_IRQ_FAST_MASK (yaml :158, :171-172); codegen reads rtl/ibex_pkg.sv (:25, :72-75, :181); time-0 GEN_WIDTH_GUARD fatals in gen_tb_top.sv:69-74; log lines 357-359 re-derive independently. |
| 1a P-03 --check never shown failing | FIXED | `--root` (codegen :482); unit test mutates each rendered target and asserts exit 1 then 0 (log lines 677-681). |
| 1a P-04 duplicated defaults | FIXED | `default_from:` on mem_readback_words, boot_addr, alive_timeout, finish_timeout (yaml :20-26); log lines 360-363. |
| 1a P-05 debug-only flags | FIXED | `debug_only: true` on dbg_csr_probe, rvfi_trace, sb_trace, isa_string, isa_log; testlist `debug_only_plusargs` lists the five. |
| 1a P-06 GEN_KNOB_KNOB_ prefix | FIXED | 0 occurrences in gen_tb_pkg.sv, 44 GEN_ENUM_. The "509 checks" re-run is labelled UNRETAINED and not counted. |
| 1a P-07 | n/a | Withdrawn by me (step-1b verdict section 5); neg_unknown_plusarg_t068 retained with verdict. |
| 1a L-1, L-2 | labelled / FIXED | New logs end with `exit=<rc>`; gen_program.py:52 comment is intent-only. |
| 1b M-1 uvm_error with cocotb PASS never forced red through the flow | FIXED | I re-ran gen_verdict.decide myself on the two committed logs (marker GEN_UT_BRIDGE_PASS, rc 0, stdout as extra log): neg_uvm_error_cocotb_pass_t068 -> FAIL, `uvm_error at log line 30`, ERROR 23, cocotb 1 passed; ut_bridge_1c_uvm_error -> FAIL, `uvm_error at log line 27`, ERROR 1, cocotb 1 passed. Same result as the retained verdict.txt. The run header names the forcing plusarg (+gen_boot_addr=00000000). Closed. |
| 1b L-1 finish() order | FIXED | gen_bridge.py:79-87: accounting assert, then stim_active 0, then finish_req. |
| 1b L-2 dut.clk | FIXED | gen_ut_bridge_neg.py:8, :16-18: GenHandles and one Timer from GEN_CLK_PERIOD_NS. |
| 1b L-3 / I-3 hart_id literal | FIXED | yaml knob hart_id; gen_tb_top.sv:59-63 reads +gen_hart_id; port at :179. |
| 1b L-4 driver columns | FIXED | gen_tb_local.sh:68-80 records gen_verdict.decide output in verdict.txt; the T-068 verdict files are retained (manifest). |
| 1b L-5 UTC header | FIXED | run_header.txt per run (gen_tb_local.sh:61), e.g. `2026-09-03T09:10:39Z host=soc-l-11 seed=1 ...`. |
| 1b L-6 step-1a items | FIXED | as above. |
| 1b I-1 kind_name re-typed | FIXED | rendered gen_cmd_name (gen_tb_pkg.sv:255) used by the item and the dispatcher. |

## 2. Cross-model rows I could verify (1a, 1b, 1c, 2a)

- 1b finish_timeout consumer: gen_bridge.py:17-19, :86. Clock `#(ClkHalfPeriodNs * 1ns)` gen_tb_top.sv:49. Bare bool
  plusargs: gen_env_pkg.sv:200 and neg_bare_bool_t068 (`UVM_FATAL ... [GEN_BARE_PLUSARG] +gen_chk_all needs =0 or =1`).
  irq_fast width from `$bits(GEN_IRQS_ZERO.irq_fast)`. GEN_NO_COCOTB: gen_env_pkg.sv:209-210 and neg_no_cocotb_t068 at
  time 0. API documents: 0 retired knob names left in gen_component_api_*.md.
- 1c knob no-op: gen_agents_pkg.sv:308-310 sets chk_rvalid_legal_en from the env config with the chk_all isolation
  rule and reports armed / disabled at time 0. Grant latency: req_cycle / gnt_delay published by the driver. Boot
  precondition: gen_ut_boot.py:37 assert, red boot_noprecond_t068 (verdict FAIL cocotb_summary). Geometry from
  `$bits(vif.rdata)` with a GEN_BUS_DRIVER fatal (:199-200, :208). FETCH_EN through gen_ctrl_driver at the falling
  edge (:374-411; boot_zc_t068 `[GEN_CTRL] fetch_enable_i <= On` at 65000). GenImage.sample draws non-zero words
  first (gen_image.py:51-52).
- 1c MUT-003 (sva_rvalid_legal): locus gen_agents_pkg.sv:277 is `vif.gnt = 1'b1;` after the revert; the record,
  mut003_mutation.txt and mutations_driver_t068.log (`reverted: identical`) agree. Isolated run header carries
  `+gen_chk_all=0 +gen_chk_sva_rvalid_legal=1`; the log shows only sva_rvalid_legal armed and `ISA compare disabled
  by knob`; exactly 2 `[sva_rvalid_legal]` errors, cocotb PASS, verdict FAIL `assertion_failure at log line 31`.
  Default run: 2 errors. Ablation: 0 real UVM_ERROR lines, `disabled by knob`, verdict PASS. Attempt 1 retained
  and explained. Trust triad rule 2 met for this TB self-check.
- 2a comparator: knob ut_lockstep_min_ratio_pct absent from the yaml; gen_ut_lockstep.py:54 asserts
  `consumed == retired`; lockstep_zc_t068 `retired 169 consumed 169 mismatches 0` with `records=148 ... folded=21`,
  lockstep_s7_t068 `retired 2002 consumed 2002 mismatches 0`; both verdict PASS. Zcmp fold compare implemented
  (gen_rvfi_pkg.sv:193-232: GPR-write union, ordered stores with size 4, ordered load addresses; ids isa_rd and
  isa_mem). Draft-B path model-sourced (:261-282, gen_isa_fetch_insn / gen_isa_read_gpr / gen_isa_set_pc), labelled
  UNEXERCISED (draft_b=0 in both programs). Forced red ids counted from the committed log: isa_insn 135, isa_mem 11,
  isa_pc 135, isa_pc_next 136, isa_rd 123, isa_trap 136, verdict FAIL `uvm_error at log line 31`; the flow's
  red_fixture handling is Runtime's (984b99d). SV literal replaced by ibex_pkg::CSR_MTVEC. API documents carry
  scoreboard section 5a (mutation class per id) and shim section 4a (8 rows marked DEFERRED).
- 2a MUT-004..MUT-007, counted from the committed logs: isolated headers `+gen_chk_all=0 +gen_chk_isa=1
  +gen_chk_isa_<f>=1`; isolated and default runs each carry exactly one id: isa_rd 124, isa_mem 8, isa_trap 148,
  isa_pc_next 148; every ablation run has 0 real UVM_ERROR lines; verdicts FAIL (`uvm_error at log line 31`) and
  PASS. The record's numbers are the logs' numbers.
- Retention: 178 manifest rows; every committed copy matches its manifest md5 and byte count; no committed file
  under gen_tdd_logs is missing from the manifest. History narration: 0 hits for the four phrases in tb, env,
  gen_tb and isa.

## 3. Rulings on the three disputed rows

- D-1 MemDataWidth mirror with a time-0 $fatal (1b): ACCEPT. gen_tb_top.sv:36 mirrors the wrapper's derivation and
  :69-70 fatals at time 0 when it differs from `$bits(u_dut.instr_rdata_i)`. Under dv_principles S5 the mirror is a
  value defined twice, but the guard makes any drift fail loud at every elaboration, and removing it would touch
  the approved DUT wrapper. Accepted as is.
- D-2 C-side shim constants with RTL citations (2a): ACCEPT AS INTERIM, NOT AS FINAL. I checked the values against
  the RTL for the opentitan configuration: kIbexMisa bits C, I, M, U, X, MXL match rtl/ibex_cs_registers.sv:188-204
  (MisaXBit :182 is 1 for BaseIsaRV32IorCHERIoT); kMcounterenMask 0x1FFD matches :1566-1567 (13 bits, bit 1 forced
  0) for MHPMCounterNum = 10; kMstatusReset 0x80 matches MSTATUS_RST_VAL :1052-1056; 0x7C0 / 0x7C1 are
  ibex_pkg::CSR_CPUCTRLSTS / CSR_SECURESEED (rtl/ibex_pkg.sv:692-693). kCpuctrlWmask 0xFF matches the eight bits of
  cpu_ctrl_sts_part_t (rtl/ibex_cs_registers.sv:239-246). Two parts of the dispute's reasoning do not hold: the two CSR addresses ARE ibex_pkg
  parameters, so the existing ibex_pkg parse can render them now; and the mcounteren width is MHPMCounterNum, a
  configuration parameter, so a configuration change would desynchronise the shim silently. Condition (low,
  non-blocking): render the CSR addresses and MHPMCounterNum through the codegen (config from util/ibex_config.py)
  at the CSR-compare landing at the latest; keep MISA and the mstatus reset as cited literals until then, each with
  an isa-shim unit check against the RTL text or the rendered value.
- D-3 RTL-level bug injection left to the Test Writer (2a): ACCEPT the division of labour, with the count
  recorded. MUT-004..007 prove, for isa_rd, isa_mem, isa_trap and isa_pc_next, that the named id fires alone, that
  the knob silences exactly it, and that the flow collects the failure (section 2). That is the checker-side half
  of trust triad rule 2. It is not the DUT-defect half: a mutation of the RTL, per checker id, caught by the named
  id with hidden referees inert (Test Writer plan section 5, purpose-2 runs) remains owed before any isa_* id is
  counted mutation-proof in a measured regression. gen_component_api_scoreboard.md section 5a must say "TB-side
  proof done; RTL-level owed" per id until then. isa_pc and isa_insn have only the forced-red evidence (a model
  perturbation, not per-field) and isa_prv has never fired; their per-field proofs are owed with the first
  U-mode program, as the record says.

## 4. Residuals (low, none blocking)

- R-1 The "no RPATH/RUNPATH" claim (2a appendix, gen_tdd_isa_shim.md) has no retained readelf output; the
  compile logs show only VCS's own rpath flags. Retain the `readelf -d` output or label the claim UNRETAINED.
- R-2 D-2 condition above (render the CSR addresses and MHPMCounterNum; unit-check MISA and the mstatus reset).
- R-3 Declared-but-never-exercised paths, all labelled: draft-B (owed grevi/gorci program), isa_prv (owed U-mode
  program), interrupt and debug entry steps (arrive with step 2b). Each stays listed until its red exists.
- R-4 gen_agents_pkg.sv:199-200 compares the interface width against `$bits(logic [38:0])`: acceptable because
  39/32 is the SECDED encoder's own geometry and the check fails loud, but the literal should name the encoder
  constant when one is rendered.

## 5. Items labelled UNRETAINED (counted as nothing here)

knobs codegen: Section 5 Spike exit status, the hand-typed --check excerpt, the "509 checks" re-run. Bridge: two
compile defects. Boot agents: compile 1 (NCE) and run 1 (0x80000398). Lockstep: attempts 1 and 2. Every one is
labelled in its transcript (grep counts 3 / 1 / 1 / 1); the isa_shim transcript claims nothing unretained except
R-1.

## 6. Principle walk on the new code (docs/dv/dv_principles.md, read fresh)

S1 preconditions asserted (gen_ut_boot, gen_ut_lockstep); counts and widths derived (`$bits`, derive:,
default_from:). S2 every failure path proven red through the flow's own verdict function (uvm_error with cocotb
PASS, sv_fatal, uvm_fatal, cocotb assert, assertion_failure). S4 limitations labelled, nothing down-scoped
silently. S5 one constants home per language domain through the codegen, guards instead of silent mirrors,
narration removed, plusargs by rendered name. S6 every claim I checked has a retained artifact with a matching
md5. No violation found beyond the D-2 condition.
