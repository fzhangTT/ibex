# gen_unreachability_evidence.md -- machine evidence for the exclusion candidates (T-022)

Owner: rtl-arch. Status: DRAFT delivered 2026-09-03 (~06:05 UTC); EC labels, Runtime T-010 facts and the -cm_glitch trial decision added ~06:10 UTC. Companion file:
dv/auto_dv/work/rtl-arch/gen_cover_props_draft.sv (SVA covers/asserts for TB Infra to bind).
Inputs: gen_exclusions_draft.md Part A (CHERIoT carve-out) and Part C (43 arcs, classes T/P/D/R),
gen_cheriot_carveout.md, gen_hierarchy_map.md Part C. Build: opentitan configuration, DUT =
dv/auto_dv/tb/gen_dut_top.sv with cheriot_enable_i tied IbexMuBiOff (gen_dut_top.sv:202).
No RTL was modified. No LSF was used. Every tool ran locally on this clone's rtl/ and
vendor/lowrisc_ip/ip plus the wrapper in dv/auto_dv/tb/. ASCII only.

Evidence classes used in this file:

- constant-tie: the arc needs a net that is a constant under the wrapper tie or the build
  parameters; verified either by yosys constant propagation on the flattened netlist or by a
  proved assertion that the net is always 0.
- structural proof: an unbounded proof by SymbiYosys k-induction on the whole gen_dut_top netlist
  (sv2v -> yosys -> yosys-smtbmc/yices), or a full enum encoding (no spare state value exists).
- cover-property pending: only bounded evidence exists (BMC to a fixed depth, k-induction
  inconclusive); a simulation cover property in gen_cover_props_draft.sv decides.
- reachable, withdrawn: a witness trace exists under a legal environment. None of the 43 arcs ended
  in this class; two candidate PREMISES did (section 5) and were restated, not the arcs.

Caveat that applies to every proof below: the environment is the wrapper boundary with all inputs
unconstrained except rst_ni low at step 0 (and, for the Zcmp runs, the four bus-protocol
assumptions in section 4.4). Instruction-cache RAM read data (ic_tag_rdata_i, ic_data_rdata_i) is
also unconstrained, which over-approximates reality. Proofs therefore cover functional
reachability; they say nothing about fault injection into state registers (relevant to class D).

## 1. Result summary

| Group | Items | Evidence class | Machine result |
|---|---|---|---|
| CHERIoT constant-tie cone (Part A carve-out) | 1 cone, 14 assertion groups | constant-tie + structural proof | PROVED, unbounded (run t022_core5, k-induction depth 5, PASS) |
| Class T arcs (28 of 43) | rows 2-11, 13-22, 24-29, 36, 41 | constant-tie + structural proof | PROVED via the cone (each row's gating net is in a proved group, section 4.2) |
| Class P arcs (5 of 43) | rows 12, 30, 32, 42-43 | constant-tie (parameter) | row 12 PROVED (T022_CORE_BP0) and yosys constant 1'0; rows 30, 32, 42-43 elaboration constants, RTL/configuration evidence only (no separate netlist witness extracted) |
| Class D default arms (6 of 43) | rows 1, 23, 33 | structural proof | PROVED: state registers never hold a spare encoding (T022_CTRL_NAMED, T022_LSU_NAMED, T022_MD_NAMED) |
| Class D default arms (cont.) | rows 31, 34, 35 | structural (full encoding) | enum width equals log2(number of values): no spare encoding exists |
| Class R Zcmp arms (4 of 43) | rows 37-40 | cover-property pending | no counterexample within 14 cycles of reset (bmc, section 4.5) and class-mismatch cover UNREACHED to depth 12+ under a compliant bus; k-induction inconclusive |

Counts: T 28 + P 5 + D 6 + R 4 = 43 arcs; 39 arcs have an unbounded structural argument (28 T,
1 P by proof, 4 P by elaboration constant, 6 D), 4 arcs (R) stay pending on simulation covers.

## 1a. Critic evidence classes (EC-1..EC-6) and where each stands

The Critic's rulings (dv/auto_dv/docs/gen_critic_exclusions_draft_v1.md, evidence-class
definitions and the per-class table at its end) name six classes. The Orchestrator ruled that the
passing k-induction results are EC-1 evidence (static structural). Status per class today:

| EC | Definition (short) | Status for the exclusion candidates | Where |
|---|---|---|---|
| EC-1 static structural | RTL declaration / generate / parameter condition, or the tie chain G1-G8; the k-induction proofs count here | DONE for T (28), P (5), D (6): sections 4.1-4.3. R (4): bounded only, not EC-1 | this file |
| EC-2 constant analysis | -cm_seqnoconst / -diag noconst constfile.txt entry, URG "Unreachable" status | PARTIAL (Runtime T-010, dv/auto_dv/evidence/gen_t010_compile_path.md section 5): the tie is recognised and propagated (constfile.txt lists u_ibex_core cheriot_enable_i[0] "0 always"; 673 constant entries) but URG marks only directly dependent objects Unreachable (ibex_cheriot_ex: 5 line rows, 54 condition vectors, 22 toggle rows; module still 126/336 lines). Annotated .el entries stay necessary. Seven UCAPI-CSM mismatches: see 4.3 | T-010 evidence; 4.3 |
| EC-3 runtime assertion | guarding RTL assertion compiled (INC_ASSERT, vendor/lowrisc_ip/ip/prim/rtl/prim_assert.sv:104-111) with attempts > 0 and failures 0 in every measured regression | NOT YET: needs the first measured regression's assertion report. Assertions named per class in 4.6 | Runtime / DV Lead |
| EC-4 DV cover property | DV-authored SVA bound from dv/auto_dv passing as an assertion with its precondition cover firing | DRAFT WRITTEN, not run: gen_cover_props_draft.sv (T022_NEVER_zcmp_class_change and the seven per-state covers implement the Critic's R-3 class-R property verbatim). Integration route confirmed by TB Infra (C10 v2): bound as gen_cover_props.sv from gen_binds.sv, T022_NEVER_* under +gen_chk_t022_never (collected failure), T022_COVER_* cover-only, compile hazards handled as the header says | TB Infra compiles/binds |
| EC-5 strict load | urg -elfile -excl_strict loads the final file with no rejected entry on a legal-stimulus merge | NOT YET: no final .el exists; the flow enforces -excl_strict whenever --elfile is given (T-010 R-5 rows) | Runtime |
| EC-6 cone of influence | siliconpilot cone_of_influence with the opentitan context for data-net toggle exclusions | NOT APPLICABLE yet (no data-path toggle exclusion proposed); the tool cannot take the config context (section 3), so when needed the yosys flattened netlist of section 2.1 is the fallback | this file |

Runtime facts folded in (T-010 evidence, forwarded by the Orchestrator): the coverage tree is
<tb_top>.u_dut with u_ibex_core and u_register_file inside (gen_smoke_tb_top.u_dut today; the real
TB top keeps u_dut); URG reports the FSM metric with six extracted machines (cm_state_q,
ctrl_fsm_cs 10 states / 26 transitions, ls_fsm_cs, cap_rx_fsm_q, md_state_q, inval_state_q;
transitions scored, states listed) so the FSM entries of gen_exclusions_draft.md A.6 apply;
condition coverage is reported and gated, so condition-level entries matter; -cm_hier with
-cm_tgl portsonly compiled without a warning; three uvm_pkg assertions sit outside the DUT tree.

## 2. Toolchain, inputs and method

### 2.1 Model construction (scratchpad only; RTL untouched)

1. Source set: every file in dv/auto_dv/tb/gen_rtl.f (prim_* from vendor/lowrisc_ip/ip and
   rtl/*.sv), plus dv/auto_dv/tb/gen_tb_pkg.sv and dv/auto_dv/tb/gen_dut_top.sv. Include dirs as in
   gen_rtl.f (vendor/lowrisc_ip/dv/sv/dv_utils for the unavoidable dv_fcov_macros.svh include,
   vendor/lowrisc_ip/ip/prim/rtl).
2. sv2v v0.0.13 converted the SystemVerilog to Verilog-2005 (single file t022_all.v) with the
   defines -DSYNTHESIS -DDV_FCOV_DISABLE and the opentitan enum-parameter defines that
   `util/ibex_config.py opentitan vcs_opts` emits (BaseIsa=BaseIsaRV32IorCHERIoT,
   RV32M=RV32MSingleCycle, RV32B=RV32BOTEarlGrey, RV32ZC=RV32ZcaZcbZcmp, RegFile=RegFileFF), which the
   wrapper consumes (gen_param_resolution.md section 3). The converted gen_dut_top was truncated
   after its u_register_file instantiation to drop the $display banner and string functions that
   yosys cannot parse (behaviour-free code).
3. Scratch top gen_t022_top.sv exposes the 48 wrapper ports with literal widths (38, 27, 77, [2])
   and instantiates gen_dut_top with the opentitan integer parameters: PMPEnable=1,
   PMPGranularity=0, PMPNumRegions=16, MHPMCounterNum=10, MHPMCounterWidth=32, RV32E=0,
   BranchTargetALU=1, WritebackStage=1, ICache=1, ICacheECC=1, ICacheScramble=1, BranchPredictor=0,
   DbgTriggerEn=1, SecureIbex=1 (derived: ResetAll=1, DummyInstructions=1, MemECC=1, per
   gen_param_resolution.md). Wrapper tie: CheriotEnable = IbexMuBiOff (gen_dut_top.sv:202).
4. Yosys 0.64+181 elaboration script t022_elab.ys: `read_verilog -sv t022_all.v; hierarchy -check
   -top gen_t022_top; proc; flatten; async2sync; opt -full; stat; write_rtlil t022_flat.il`.
   Result: 6796 cells after optimisation. Used for the constant-propagation evidence (section 4.3).
5. Formal copies t022_formal_*.v: the converted file with immediate assertions inserted into the
   module bodies (form `always @(posedge clk_i) if (rst_ni) assert(<expr>); // T022_<NAME>`) and
   `initial assume(!rst_ni);` in the scratch top. SymbiYosys job files (t022_*.sby):
   `[options] mode prove / depth 5; [engines] smtbmc yices; [script] read -formal -sv <file>;
   prep -top gen_t022_top; async2sync`. Prepared model: 9009 cells (t022_core5/model/design.il).
   Solver: Yices 2.7.0 through yosys-smtbmc. Tools: /tools_risc/tt/siliconpilot/latest/bin.

### 2.2 Semantics checks and non-vacuity

- Step semantics (tiny experiment sem.v, scratchpad t022_sem/): an immediate assert in a clocked
  block is checked one step after the values it samples (smtbmc reports "step k+1" for values of
  step k); async2sync makes the asynchronous reset act at the clock edge; flops without reset get
  an arbitrary initial value (anyinit). Every trace decode below uses this mapping.
- Implicit declarations: yosys silently creates a 1-bit wire for an undeclared name, which makes
  `assert(!x)` fail spuriously and `assert(x <= 7)` pass vacuously. Every run used as evidence was
  checked with `grep "implicitly declared" <run>/model/design.log`: t022_core, t022_core5,
  t022_zcmp3 and the module-level runs report none. Runs t022_core2/3/4 had 5-6 implicit names
  (wb_stage nets declared inside generate block g_writeback_stage, cheriot_fatal_err_q inside a
  generate block) and are NOT used as evidence; their assertions were moved into the right scope
  (t022_core5).
- Assertions present in the SMT model: `grep -c assert design_smt2.smt2` = 20 (t022_core), 46
  (t022_core5).
- The assertions bite: with free LSU inputs the module-level LSU run FAILED at step 3
  (lsu_is_cap_i driven high by the solver); the same assertions PASS at core level where that input
  is the proved-zero net. The implicit-wire runs FAILED at step 2. Non-vacuity is therefore shown by
  both a positive and a negative result of the same properties.
- Retention (Critic N-1): every job file, the sv2v output, the scratch top, the yosys script and
  netlist, every assertion-bearing formal copy, every sby log, and per run the logfiles, status,
  traces, the implicit-declaration grep count and the SMT2 assert count are copied under
  dv/auto_dv/work/rtl-arch/t022/ (section 8); the scratchpad is no longer the only holder.
- Independent reproduction: the siliconpilot MCP tool formal_verify (mode prove, depth 5, top
  gen_t022_top, file t022_formal_core.v) returned PASS "successful proof by k-induction" with its own
  script (read_verilog -sv; prep -top; no async2sync). It wrote its work directory .formal_work/ into
  the repo root; that directory was removed (tool output, not a deliverable).

## 3. siliconpilot MCP tools: attempts and limitations (honest record)

| Tool | Inputs | Result | Limitation |
|---|---|---|---|
| yosys_analyze, formal_verify (SV frontend) | rtl/ file set with opentitan defines | ERROR "ibex_pkg.sv:350: syntax error, unexpected OP_CAST" | the plain yosys Verilog frontend does not accept the struct-literal cast in ibex_pkg; bypassed with sv2v (section 2.1) |
| formal_verify (on the sv2v output) | t022_formal_core.v, top gen_t022_top, prove depth 5 | PASS, k-induction successful | works only on pre-converted Verilog; writes .formal_work/ into the repo root |
| rtl_analyze mode fsm | rtl/ibex_controller.sv, ibex_load_store_unit.sv, others | 0 FSMs found | regex-based extractor; does not recognise the typedef-enum + always_comb case idiom Ibex uses |
| rtl_analyze mode type | ibex_pkg.sv and module files | total_bits null for the enums | no width evaluation; enum widths were taken from the declarations instead |
| parameter_resolve | gen_dut_top.sv / ibex_core.sv | declared defaults only | does not evaluate expressions such as MemDataWidth = MemECC ? 32+7 : 32 |
| cone_of_influence | ibex_core.cheriot_enable_mubi_err, ibex_load_store_unit.data_tag_o | see gen_exclusions_draft.md Part C tail | elaborates default parameters (BaseIsa = RV32I, not our build) and stops at always_comb-driven nets |
| fv_parse_assertion | dv/auto_dv/work/rtl-arch/gen_cover_props_draft.sv | "2 assertions, 0 named properties" (the two macro templates, unnamed) | does not expand `define macros; cannot inventory the ~35 macro-instantiated properties; usable only on files with literal property statements |
| yosys `sat -prove` on t022_flat.il | 51 candidate nets (t022_nets.txt) | "No SAT model available for async FF cell" and "Failed to parse lhs proof expression" for absent nets | abandoned; SymbiYosys used instead |

## 4. Per-item records

Every record: tool, command/inputs, result, limitation. "PROVED" means basecase passed and
temporal induction succeeded (unbounded) in the named run; the assertion text is verbatim from the
formal copy so the record can be re-run.

### 4.1 CHERIoT constant-tie cone (carve-out, gen_exclusions_draft.md Part A)

Run t022_core5 (sby prove, depth 5, PASS; no implicit declarations; 17 assertion statements).
SBY summary lines, verbatim (stamps are the tool's local clock, UTC-4): `SBY  1:54:04 [t022_core5]
summary: successful proof by k-induction.` and `SBY  1:54:04 [t022_core5] DONE (PASS, rc=0)`; the
earlier 8-group run: `SBY  1:29:50 [t022_core] DONE (PASS, rc=0)`. Retained artefacts: section 8.
Module placement is where the assertion was inserted (module scope unless noted).

| Assertion (module) | Expression (verbatim) | Result |
|---|---|---|
| T022_CORE_CHERI0 (ibex_core) | `!cheriot_enable_mubi_err && !cheriot_exec_id && !instr_is_cheriot_id && !lsu_is_cap && !lsu_cheriot_err && !cheriot_wb_err && !cheriot_ex_err && !cheriot_branch_req && !lsu_err_is_cheriot && !cheriot_fatal_err && !data_tag_o` | PROVED |
| T022_CORE_CHERI0_B (ibex_core) | `!cheriot_branch_req_spec && !cheriot_load_id && !cheriot_store_id && !cheriot_rf_we && !cheriot_csr_op_en && !cheriot_csr_set_mie && !cheriot_csr_clr_mie && !csr_mshwm_set && !csr_dbg_tclr_fault && !instr_fetch_cheriot_acc_vio && !instr_fetch_cheriot_bound_vio && !csr_mepcc_clrtag` | PROVED (needed T022_CSR_MSHWM0 as a strengthening invariant, see below) |
| T022_CTRL_CHERI0 (ibex_controller) | `!cheriot_ex_err_q && !cheriot_wb_err_q && !cheriot_asr_err_q && !lsu_err_is_cheriot_q` | PROVED |
| T022_CTRL_PRIO0 (ibex_controller) | `!cheriot_ex_err_prio && !cheriot_wb_err_prio && !cheriot_asr_err_prio` | PROVED |
| T022_LSU_CHERI0 (ibex_load_store_unit) | `!cheriot_err_q && !resp_is_cap_q && !lsu_go_goodcap && !cpu_req_erred` | PROVED |
| T022_LSU_NO_CTX (ibex_load_store_unit) | `!(ls_fsm_cs == 4'd5 \|\| ls_fsm_cs == 4'd6 \|\| ls_fsm_cs == 4'd7)` (CTX_WAIT_GNT1/GNT2/RESP) | PROVED |
| T022_CRX_IDLE (ibex_load_store_unit) | `cap_rx_fsm_q == 3'd0` (CRX_IDLE) | PROVED |
| T022_DEC_CHERI0 (ibex_decoder) | `!illegal_reg_16 && !instr_is_legal_cheriot && cheriot_data_req_o == 1'b0 && instr_is_cheriot_o == 1'b0` | PROVED |
| T022_ID_CHERI0 (ibex_id_stage) | `!cheriot_lsu_req_dec && !cheriot_exec_id_o` | PROVED |
| T022_IF_CHERI0 (ibex_if_stage) | `!cheriot_acc_vio && !cheriot_bound_vio && !cheriot_force_uc` | PROVED |
| T022_WB_CHERI0 (ibex_wb_stage, inside generate g_writeback_stage) | `!wb_valid_q \|\| (!wb_is_cheriot_q && !wb_cheriot_load_q && !wb_cheriot_store_q && !cheriot_rf_we_q)` | PROVED |
| T022_CSR_CHERI0 (ibex_cs_registers) | `!mshwm_en && !mshwmb_en && !cdbg_ctrl_en && !cheriot_fatal_err_o` | PROVED |
| T022_CSR_MSHWM0 (ibex_cs_registers) | `(mshwm_q == 32'd0) && (mshwmb_q == 32'd0) && !mshwm_en_combi && !mshwmb_en` | PROVED |
| T022_RF_CAP0 (ibex_register_file_ff) | `rcap_a_o == 0 && rcap_b_o == 0` | PROVED |

Notes on the cone:

- The wrapper tie is the root: cheriot_enable_i == IbexMuBiOff at ibex_core (gen_dut_top.sv:202);
  T022_CORE_CHERI0 proves the derived enable-error net is 0, and the decoder/ID/IF/LSU/WB/CSR groups
  prove every downstream CHERIoT control net is 0 in every reachable state. This is the
  machine-checked form of the constant-tie argument in gen_cheriot_carveout.md Part A.
- csr_mshwm_set is NOT a CHERIoT-gated net by construction: rtl/ibex_cheriot_ex.sv:991 computes it
  from the ordinary RV32 store request (lsu_req_o = rv32_lsu_req_i when instr_is_cheriot_i is 0,
  :943) and the stack high-water-mark window `lsu_addr_o[31:4] >= csr_mshwmb_i[31:4] &&
  lsu_addr_o[31:4] < csr_mshwm_i[31:4]`. It is 0 only because mshwm and mshwmb stay at their reset
  value 0 (rtl/ibex_cs_registers.sv:1304-1330, ResetValue '0): their CSR write enables require
  cheriot_enable_i == IbexMuBiOn (:879-882) and the set path needs csr_mshwm_set itself (:1301,
  circular). The first induction attempt failed exactly here (solver seeded mshwm non-zero from an
  unreachable state); T022_CSR_MSHWM0 closes it. Implication for the carve-out: the u_ibex_cheriot_ex
  output csr_mshwm_set_o and the cs_registers mshwm path are unreachable by a chain through two
  CSRs, not by a direct tie; the exclusion entry should cite this file.
- Traces of the discarded runs: t022_core2/3/4 failed at step 2 on wb_stage names that were implicit
  wires (section 2.2); the real flops (g_writeback_stage.wb_*_q) are 0 in those traces.

### 4.2 The 43 arcs (gen_exclusions_draft.md Part C rows) and the 6 default arms

| Row(s) | Arc | Class | Evidence | Tool / run | Result |
|---|---|---|---|---|---|
| 1 | ctrl default -> RESET (rtl/ibex_controller.sv:990-993) | D | T022_CTRL_NAMED `ctrl_fsm_cs <= 4'd9` | sby t022_core, t022_core5 | PROVED: encodings 10-15 never held |
| 2-3 | fetch-err CHERIoT arms (:850-858) | T | guard `(cheriot_enable_i == IbexMuBiOn) & instr_fetch_cheriot_*_vio_i`; both factors 0: tie + T022_CORE_CHERI0_B (instr_fetch_cheriot_acc/bound_vio) | sby t022_core5 | PROVED |
| 4 | illegal mtval CHERIoT (:866-867) | T | select is the On comparison; tie | wrapper tie + T022_CORE_CHERI0 (mubi err 0) | constant-tie |
| 5 | ebreak mtval = pc (:894-897) | T | On comparison; tie | as row 4 | constant-tie |
| 6-7 | store/load err CHERIoT arms (:901-908, :915-922) | T | lsu_err_is_cheriot_q = 0: T022_CTRL_CHERI0 | sby t022_core5 | PROVED |
| 8-10 | cheriot_ex/wb/asr_err_prio (:928-948) | T | T022_CTRL_PRIO0 and T022_CTRL_CHERI0 | sby t022_core5 | PROVED |
| 11 | pc_set via cheriot_branch_req (:681-682) | T | cheriot_branch_req = 0: T022_CORE_CHERI0; _spec: T022_CORE_CHERI0_B | sby t022_core5 | PROVED |
| 12 | nt_branch_mispredict / bp arms (:684, :690-696) | P | T022_CORE_BP0 `!instr_bp_taken_id && !nt_branch_mispredict`; yosys constants `connect \u_dut.u_ibex_core.instr_bp_taken_id 1'0`, `...nt_branch_mispredict 1'0`, `...if_stage_i.predict_branch_taken 1'0` (t022_flat.il lines 93394, 93368, 90676) | sby t022_core5; yosys opt -full | PROVED and constant-tie |
| 13 | exc_req CHERIoT terms (:269, :276) | T | cheriot_ex_err, cheriot_wb_err = 0: T022_CORE_CHERI0 | sby t022_core5 | PROVED |
| 14-22 | LSU CHERIoT arcs (rtl/ibex_load_store_unit.sv:437-467, :565-603) | T | entry needs On (tie); CTX_* states never held: T022_LSU_NO_CTX; cap regs 0: T022_LSU_CHERI0 | sby t022_core5 | PROVED |
| 23 | LSU default (:605-607) | D | T022_LSU_NAMED `ls_fsm_cs <= 4'd7` | sby t022_core5 | PROVED: encodings 8-15 never held |
| 24-28 | cap_rx FSM (:615-624) | T | T022_CRX_IDLE `cap_rx_fsm_q == 3'd0` | sby t022_core5 | PROVED: frozen in CRX_IDLE |
| 29 | id_fsm cheriot_lsu_req_dec (rtl/ibex_id_stage.sv:901-909) | T | T022_ID_CHERI0; T022_DEC_CHERI0 (cheriot_data_req_o == 0) | sby t022_core5 | PROVED |
| 30 | jump multicycle !BranchTargetALU (:936-942) | P | BranchTargetALU=1 is a parameter of the scratch top / config; the `!BranchTargetALU` term is an elaboration constant | configuration + RTL | constant-tie (parameter); no separate netlist witness extracted |
| 31 | id_fsm default (:968-970) | D | id_fsm_e is 1 bit with 2 named values (rtl/ibex_id_stage.sv:861): no spare encoding | declaration | structural (full encoding) |
| 32 | branch !BTALU sub-term (:920-928) | P | as row 30 | configuration + RTL | constant-tie (parameter) |
| 33 | divider default (rtl/ibex_multdiv_fast.sv:522-524) | D | T022_MD_NAMED `md_state_q != 3'd7` | sby t022_core5 | PROVED: the one spare encoding never held |
| 34 | multiplier default (:238-240) | D | mult_fsm_e is 1 bit with 2 named values (rtl/ibex_multdiv_fast.sv:142-144) | declaration | structural (full encoding) |
| 35 | icache inval default (rtl/ibex_icache.sv:1268) | D | inval_state_e is 2 bits with 4 named values (rtl/ibex_icache.sv:193-198) | declaration | structural (full encoding) |
| 36 | Zcmp illegal in CHERIoT (rtl/ibex_compressed_decoder.sv:615-620) | T | On comparison; tie | wrapper tie | constant-tie |
| 37-40 | Zcmp mismatched-state defaults (:682, :773, :804, :832) | R | section 4.4 | sby t022_zcmp, t022_zcmp2, t022_zcmp3, t022_zcmp3c | cover-property pending (bounded: no CEX to depth 8, cover unreached to depth 12) |
| 41 | WB CHERIoT terms (rtl/ibex_wb_stage.sv:115-116, :190-196) | T | T022_WB_CHERI0 (inside g_writeback_stage), inputs proved 0 by T022_CORE_CHERI0/_B | sby t022_core5 | PROVED |
| 42-43 | BCOMPRESS/BDECOMPRESS multicycle (rtl/ibex_decoder.sv:1341-1352) | P | `RV32B == RV32BFull` is false for RV32B = RV32BOTEarlGrey (define); legality case :641-642 also rejects the encodings | configuration + RTL (gen_rv32b_otearlgrey_encodings.md) | constant-tie (parameter); no separate netlist witness extracted |

Honesty note on rows 30, 32, 42-43: sv2v substitutes the parameter and yosys `opt` removes the
dead branch, so the arcs have no corresponding logic in t022_flat.il, but I did not build a named
witness for their disappearance (no distinct net survives to point at). The evidence is the
configuration value plus the RTL condition; VCS constant analysis (`-cm_seqnoconst`, already in
SIM_RECIPE.md section 3) should report them Unreachable independently.

Class D caveat (for the Critic ruling in gen_exclusions_draft.md Part C): rows 1, 23, 33 are proved
unreachable for a fault-free state register. The proofs model every flop faithfully but have no
fault-injection semantics; under a bit-flip fault model the default arms are exactly the intended
alert paths. Whether "fault-injection-only" counts as unreachable for coverage is still the
Critic's call; the machine evidence is now complete for the functional side.

### 4.3 Constant propagation evidence (yosys, t022_flat.il)

Command: t022_elab.ys (section 2.1). Constant connections found by `grep "connect" t022_flat.il`:

```
90593:  connect \u_dut.u_ibex_core.id_stage_i.controller_i.instr_bp_taken_i 1'0
90634:  connect \u_dut.u_ibex_core.if_stage_i.instr_bp_taken_o 1'0
90676:  connect \u_dut.u_ibex_core.if_stage_i.predict_branch_taken 1'0
91468:  connect \u_dut.u_ibex_core.id_stage_i.instr_bp_taken_i 1'0
93368:  connect \u_dut.u_ibex_core.nt_branch_mispredict 1'0
93394:  connect \u_dut.u_ibex_core.instr_bp_taken_id 1'0
```

This is the same analysis VCS `-cm_seqnoconst` performs for the Unreachable annotation; the two
tools should agree on row 12.

EC-2 status from the Runtime T-010 merges (dv/auto_dv/evidence/gen_t010_compile_path.md section 5)
and the UCAPI-CSM finding: every merge.log carries `Warning-[UCAPI-CSM] coverage status mismatch`
on seven condition objects that VCS marked Unreachable at compile time but URG sees as covered in
simulation: cheriot_enable_i terms at rtl/ibex_cheriot_ex.sv:970, rtl/ibex_cs_registers.sv:377 and
:1020, rtl/ibex_core.sv:1343; fetch_enable_i terms at rtl/ibex_core.sv:648, :649 and :1414 (the
last a smoke-top tie only), with `Note-[UCAPI-RCGLTCH]` suggesting `-cm_glitch 0`. The ties cannot
change, so the "covered" event is a time-zero evaluation glitch. It matters for EC-5: a covered
status on a tie condition makes `-excl_strict` reject the matching Condition entry. Decision: the
trial IS requested, as a purpose-2 run (instrumentation change) in
dv/auto_dv/work/runtime/requests/rtl-arch-001.yaml (gen_regress.py --build-vcs-arg "-cm_glitch 0",
smoke tier, own outdir). Outcome (served 06:06Z as results/rtl-arch-001, gen_smoke seeds 1080223093 and 1164951914, both
PASS, urg rc 0): with `-cm_glitch 0` the merge.log carries NO Warning at all (14 lines; 0 UCAPI-CSM,
0 UCAPI-RCGLTCH), so the seven tie conditions no longer show as covered and their Condition entries
would pass -excl_strict. Denominators are identical to the T-010 baseline (LINE /4351, COND /9566,
TOGGLE /26958, FSM /86, BRANCH /2418, ASSERT /178: the flag changes no object count). Numerators are
much lower (trial LINE 1694, COND 2547, BRANCH 798 against baseline 2397, 3579, 992) although the
trial merged TWO seeds and the baseline ONE (seed 330815564); toggle and assert numerators are equal
(1994, 143). The Runtime Manager's report on the request closes the attribution question: gen_smoke is a
deterministic NOP program (both trial seeds give identical totals), the same-day standard-flag smoke
merge (regress_t027_smoke_recheck) carries 14 UCAPI-CSM lines (the seven objects, each twice) and 1
RCGLTCH, and the denominators are identical, so the flag changed only what counts as hit: about 700
line, 1000 condition and 200 branch objects of the NOP smoke were covered by zero-time glitch events
only. The same-seed control (rtl-arch-002, served 06:16Z into the unmeasured tree because purpose-2
tests carry measured: false) then confirmed it by measurement: the SAME two seeds with the standard
flags give exactly the baseline DUT row (LINE 2397/4351, COND 3579/9566, BRANCH 992/2418, TOGGLE
1994/26958, FSM 6/86, ASSERT 143/178) and the merge.log carries 14 UCAPI-CSM and 1 RCGLTCH lines
again. The whole numerator difference is the glitch filter. VCS accepted the
flag with one new compile warning, Warning-[VCM-OPTIGN] "-cm_glitch option does not work with fsm
and path" (build/gen_smoke/compile.log): the FSM metric is not glitch-filtered. For future requests
the schema has the fields build_vcs_args and dump_exclusions (gen_runtime_api.md section 4).
What the flag does (Coverage Technology Reference Manual X-2025.06-SP2, "Using Glitch
Suppression", pp.185-186, scratchpad cov_ref.txt): `-cm_glitch 0` removes delta-cycle glitches;
for line coverage VCS records only the LAST execution of an always block within the glitch period,
and for condition/toggle coverage it ignores values that exist only transiently within the period.
Lines and condition vectors that execute only in intermediate delta cycles of a timestep (a
combinational block re-evaluated as its inputs settle) therefore stop counting, which is exactly
the mechanism behind the seven "covered" tie conditions and would also explain lower LINE/COND/
BRANCH numerators with unchanged denominators and unchanged toggle/assert counts. The flag lowers the
gate number by removing transient evaluations (a smaller, more honest number). rtl-arch's
recommendation to the DV Lead (decision LOG-007): adopt `-cm_glitch 0` for measured builds, because
(a) glitch-only hits are not DUT behaviour and inflate line/condition/branch by roughly a third on
this smoke, (b) without it the seven tie conditions stay "covered" and their Condition exclusions
fail EC-5, (c) denominators and the toggle/assert/FSM numbers are unaffected; caveat: FSM is not
filtered (VCM-OPTIGN), and the change must be made before the first measured regression so no
baseline is re-set mid-flight. The manual also notes the flag is a runtime option for toggle coverage
only and that `-cm_glitch 0+nolinecontassign` keeps continuous assigns out of the filter. Unreachable marks in ibex_cheriot_ex are unchanged by
the flag (5 line rows, 54 condition vectors, 22 toggle rows, 132 marks). Trial artefacts:
<out root>/regress_req_rtl-arch-001/build/gen_smoke/constfile.txt and cov/full_exclusions/
(12 fullexclude files), to be copied beside the annotated .el when it exists.
Evidence copies for EC-2/EC-5: every coverage build writes constfile.txt and every purpose-4 merge
dumps <outdir>/cov/full_exclusions/; both are copied beside the annotated .el file when it exists. The CHERIoT nets are NOT simple constants in the netlist (they depend
on flops and the mubi compare), which is why they needed the induction proof rather than constant
propagation; -cm_seqnoconst may or may not mark them (Runtime T-010 confirmation still pending).

### 4.4 Class R: Zcmp mismatched-state default arms (rows 37-40)

Property under test: "while cm_state_q != CmIdle the instruction presented to the expander does
not change class". Five runs, in order:

| Run | Property (verbatim) | Environment | Result | Reading |
|---|---|---|---|---|
| t022_zcmp | T022_ZCMP_INSTR_STABLE `(cm_state_q == 3'd0) \|\| (instr_i == t022_instr_prev)` (32-bit) | free inputs | FAIL, basecase step 6 | LEGITIMATE counterexample against the 32-bit premise: instr_i 0x0000b842 -> 0x8000b842 while cm_state_q = 2 (CmPushDecrSp). The icache marks a compressed instruction valid from its low halfword alone and back-fills [31:16] later (rtl/ibex_icache.sv:1131-1133 output_valid, :1192 rdata_o). The Zcmp class is decided by instr_i[15:0] only (rtl/ibex_compressed_decoder.sv:627-835 read bits [15:13], [12:8], [6:5], [1:0]), so the premise is restated on [15:0]. |
| t022_zcmp2 | T022_ZCMP_INSTR_STABLE16 `(cm_state_q == 3'd0) \|\| (instr_i[15:0] == t022_instr_prev[15:0])` | free inputs | FAIL, basecase step 7 | ARTEFACT of the free bus: the solver returned instr_rvalid_i in the same cycle as instr_gnt_i (step 4) with no outstanding beat; the icache assigns any rvalid to the oldest expecting fill buffer without checking the grant count (rtl/ibex_icache.sv:851 `fill_rvd_arb[fb] = instr_rvalid_i & fill_rvd_exp[fb] & ...`), so its beat bookkeeping was corrupted and an errored beat (integrity error, instr_intg_err) was presented as the output word (fetch_err = 1, valid_i = 0 via rtl/ibex_if_stage.sv:492). Not a legal environment; bus assumptions added. |
| t022_zcmp3 (prove, depth 8) | T022_ZCMP_INSTR_STABLE16V `(cm_state_q == 3'd0) \|\| !valid_i \|\| (instr_i[15:0] == t022_instr_prev[15:0])`; T022_ZCMP_SEQ_INSTR `(cm_state_q == 3'd0) \|\| !valid_i \|\| (instr_i[15:0] == t022_seq_instr)` where t022_seq_instr samples instr_i[15:0] while idle and holds mid-sequence | four assumptions in the top: `!instr_gnt_i \|\| instr_req_o`; `!instr_rvalid_i \|\| (outstanding_i != 0)`; same two for the data bus; outstanding counters count gnt minus rvalid | UNKNOWN: basecase PASS through depth 8 (no counterexample from reset), induction step fails from an unreachable start state | bounded evidence only; k-induction inconclusive because t022_seq_instr and the expander state are not constrained enough for the induction hypothesis |
| t022_zcmp3c (cover, depth 12) | T022_COVER_ZCMP_CLASS_MISMATCH `(cm_state_q != 3'd0) && t022_is_zcmp && (instr_i[15:0] != t022_seq_instr)` with t022_is_zcmp = the cm.push/pop/popret/popretz/mvsa01/mva01s encodings | same assumptions | FAIL = cover UNREACHED within 12 cycles | no legal trace of 12 cycles from reset presents a different Zcmp encoding mid-sequence; this is the direct bounded statement about rows 37-40 |
| t022_zcmp3b (bmc 24), t022_zcmp3p (prove 16), t022_zcmp3c20 (cover 20) | as t022_zcmp3 / t022_zcmp3c | same | RUNNING at document time (each step takes minutes past depth 12); results will be appended to section 4.5 when they finish | deeper bounded evidence |

Reading for the exclusion decision: rows 37-40 are unreachable within 12 cycles of reset under a
protocol-compliant bus, and no functional mechanism for a class change mid-sequence was found:
fetch_ready is held low during expansion (rtl/ibex_if_stage.sv:808-809), the icache holds the beat
data in fill_data_q (rtl/ibex_icache.sv:1015-1021) and advances the output address only on
output_ready (:801, :1101), and flush_expanded (pc_set & PC_EXC, :483) resets the expander in the
same edge the fetch redirects. An unbounded proof was not obtained, so the class stays
"cover-property pending": the covers T022_COVER_zcmp_instr_changes_midseq (now on [15:0] with
valid_i), T022_COVER_zcmp_fetch_err_midseq, T022_COVER_zcmp_push/pop/mv_default and the
non-vacuity covers T022_COVER_zcmp_midseq_seen / _flush_midseq in gen_cover_props_draft.sv decide
in simulation. Rows 37-40 stay OUT of the exclusion file until the regression shows them never
hit (as gen_exclusions_draft.md Part C already states).

### 4.5 Deeper bounded runs (appended when finished)

Results (logs: scratchpad t022_sby_zcmp3b.out, t022_sby_zcmp3p.out, t022_sby_zcmp3c20.out):
- t022_zcmp3b (bmc, requested depth 24): assertions T022_ZCMP_INSTR_STABLE16V and T022_ZCMP_SEQ_INSTR
  checked with NO failure through step 13; step 14 was still being solved when the 25-minute
  timeout killed the run (each step past 12 takes minutes). Bound achieved: 14 cycles from reset
  (steps 0-13) under the bus assumptions.
- t022_zcmp3p (prove, depth 16): base case passed through step 13, step 14 unfinished at the
  timeout; the induction step had already failed from an unreachable start state at the earlier
  depth-8 run and was not completed here. k-induction remains inconclusive.
- t022_zcmp3c20 (cover, depth 20): T022_COVER_ZCMP_CLASS_MISMATCH UNREACHED through step 13
  (step 14 was being solved when the 25-minute timeout killed the run).
  Bound: no class-mismatch witness within 14 cycles of reset under a compliant bus.
Net effect on class R: the bounded evidence is "no class change mid-sequence within 14 cycles of
reset under a compliant bus" and "no class-mismatch witness within 14 cycles"; still no
unbounded proof, so the class stays cover-property pending (4.4).

### 4.6 Required EC set per class (Critic table) against today's evidence

| Class | Critic requirement | EC-1 | EC-2 | EC-3 (assertion to report) | EC-4 | EC-5 |
|---|---|---|---|---|---|---|
| T, 28 arcs + A.3-A.7 objects | EC-1, EC-2, EC-3, EC-5 | proved (4.1, 4.2) | partial (T-010) | IbexCheriotLoadDisabled, IbexCheriotStoreDisabled, IbexInstrNotCheriot, IbexCheriotExecDisabled (rtl/ibex_id_stage.sv:1297-1300); IbexLsuIsCapDisabled, IbexLsuCheriotErrDisabled (rtl/ibex_load_store_unit.sv:833-834); IbexCheriotClrMieDisabled, IbexCheriotSetMieDisabled (rtl/ibex_cs_registers.sv:1996-1997); controller one-hot ASSERT (rtl/ibex_controller.sv:377-383) | n/a | pending |
| u_ibex_cheriot_ex object list | dump minus live list, EC-2 for instr_is_cheriot_i / cheriot_exec_id_i, EC-5 | T022_DEC_CHERI0 (instr_is_cheriot_o == 0), T022_ID_CHERI0 (cheriot_exec_id_o == 0) proved | partial: 132 marks in the instance (T-010) | as class T | n/a | pending |
| P, 5 arcs | EC-1 (parameter + banner), EC-2 or explicit entries, EC-5 | proved / elaboration constant (4.2, 4.3) | row 12 expected Unreachable (yosys constants agree); others unknown until URG | none | n/a | pending |
| D no spare encoding, 3 | EC-1 (enum cite), EC-5 | declaration cites (4.2 rows 31, 34, 35) | n/a | none required | n/a | pending |
| D spare encodings, 3 | EC-1 (enum + spare count), EC-3, EC-5, merge hygiene | proved (T022_CTRL_NAMED, T022_LSU_NAMED, T022_MD_NAMED); spare counts 6, 8, 1 | n/a | IbexCtrlStateValid (rtl/ibex_controller.sv:1104-1106), IbexLsuStateValid (rtl/ibex_load_store_unit.sv:821-824), IbexMultDivStateValid (rtl/ibex_multdiv_fast.sv:532-533) | n/a | pending |
| R Zcmp, 4 | EC-4, EC-3 IbexPushPopFSMStable, Phase-1 URG uncovered | bounded only (4.4, 4.5: 14 cycles) | n/a | IbexPushPopFSMStable (rtl/ibex_compressed_decoder.sv:937) | drafted, not run | not in file |

## 5. Findings that change earlier text (no RTL bug candidates from this task)

1. Part C rows 37-40 argument sketch said "the icache holds rdata_o stable while ready_i is low
   (doc icache.rst:246, not RTL-proven here)". RTL-proven now: FALSE for bits [31:16] of a
   compressed instruction (back-fill, rtl/ibex_icache.sv:1131-1133, :1192) and TRUE only as a
   bounded statement for [15:0]. The exclusion argument is restated on instr_i[15:0] in
   gen_cover_props_draft.sv and in this file; gen_exclusions_draft.md Part C carries a pointer.
2. The icache does not defend against a response that arrives with no granted request
   (rtl/ibex_icache.sv:851). This is by design (the bus protocol forbids it) but it means the TB
   memory model MUST enforce "rvalid only for a granted request and never in the grant cycle"
   (gen_interface_inventory.md protocol rules); a sloppy model corrupts icache bookkeeping silently
   and produces phantom fetch errors. Flag to TB Infra.
3. The CHERIoT carve-out argument for csr_mshwm_set / mshwm CSR path is a two-CSR chain, not a
   direct tie (section 4.1 note); the exclusion entry wording in gen_exclusions_draft.md A.3
   (cs_registers rows) should cite rtl/ibex_cheriot_ex.sv:991 and rtl/ibex_cs_registers.sv:879-882,
   :1301, :1304-1330.
4. The Part C COI column ("not run") is superseded by section 4.2 of this file.

## 6. Mapping to gen_cover_props_draft.sv

| Evidence item | Draft property (bind target gen_dut_top) | Kind |
|---|---|---|
| T022_CORE_CHERI0 / _B | T022_NEVER_cheriot_enable_mubi_err, _cheriot_exec_id, _instr_is_cheriot_id, _lsu_is_cap, _lsu_cheriot_err, _cheriot_wb_err, _cheriot_ex_err, _cheriot_branch_req, _lsu_err_is_cheriot, _cheriot_fatal_err, _data_tag_o, _cheriot_load_store_id, _cheriot_csr_ops, _fetch_cheriot_vio, _csr_mepcc_clrtag | assert (proved; regression re-check) |
| T022_CTRL_CHERI0 / PRIO0 | T022_NEVER_ctrl_cheriot_q, T022_NEVER_ctrl_cheriot_prio | assert |
| T022_LSU_NO_CTX / LSU_CHERI0 / CRX_IDLE | T022_NEVER_lsu_ctx_state, _lsu_ctx_next, _cap_rx_fsm, _lsu_cheriot_regs | assert |
| T022_ID_CHERI0 / DEC_CHERI0 / WB_CHERI0 / IF_CHERI0 / CSR_CHERI0 / CSR_MSHWM0 / RF_CAP0 | T022_NEVER_id_cheriot_lsu_req_dec, _dec_cheriot, _wb_cheriot (g_writeback_stage paths), _if_cheriot, _csr_cheriot (now includes mshwm_q/mshwmb_q == 0), _rf_cap, T022_TIE_cheriot_enable | assert |
| T022_CORE_BP0 | T022_NEVER_bp_taken | assert |
| T022_CTRL_NAMED / LSU_NAMED / MD_NAMED | T022_NEVER_ctrl_default, _lsu_default, _md_default | assert |
| rows 37-40 | T022_COVER_zcmp_instr_changes_midseq, _fetch_err_midseq, _push_default, _pop_default, _mv_default, _midseq_seen, _flush_midseq | cover (pending class) |
| BUG-07 reproducer trigger | T022_COVER_bug07_dummy_midseq | cover (not an exclusion) |

## 7. What each owner needs

- TB Infra: compile gen_cover_props_draft.sv in the binds home; the header lists the three compile
  hazards (hierarchical enum labels, g_writeback_stage and gen_multdiv_fast generate scopes) and
  the severity policy question ($error on a withdrawn exclusion). Enforce the bus rule in finding
  5.2 in the memory model.
- DV Lead: rows 37-40 stay out of the exclusion file (pending covers); rows 1, 23, 33 have the
  functional proof but still need the Critic's fault-injection ruling; the carve-out entries for
  cs_registers should cite the mshwm chain (finding 5.3). No new bug candidates.
- Runtime: nothing yet; when a compile path exists, a -cm_seqnoconst / `-diag noconst` report will
  show whether VCS marks the CHERIoT nets Unreachable by itself (section 4.3 note).
- Orchestrator: deliverables are this file and gen_cover_props_draft.sv; scratch artefacts remain in
  the session scratchpad (not committed).

## 8. Retained artefacts (Critic N-1) and reproduction

Retained under dv/auto_dv/work/rtl-arch/t022/ (working tree, not committed; the Orchestrator decides
what moves to dv/auto_dv/evidence/):

- jobs/: every SymbiYosys job file (t022_core.sby, t022_core2..5.sby, t022_zcmp.sby, t022_zcmp2.sby,
  t022_zcmp3.sby, t022_zcmp3b.sby, t022_zcmp3c.sby, t022_zcmp3c20.sby, t022_zcmp3p.sby, t022_lsu2.sby,
  t022_ibex_controller.sby, t022_ibex_load_store_unit.sby, t022_ibex_multdiv_fast.sby).
- model/: t022_all.v (sv2v output), gen_t022_top.sv (scratch top), t022_elab.ys, t022_flat.il (yosys
  netlist, 6796 cells).
- sources/: the assertion-bearing formal copies t022_formal_*.v and t022_assertions_extract.txt (every
  inserted T022_* assert/assume/cover with file:line, 117 lines: the extract the Critic asked for).
- logs/: every sby stdout log t022_sby_*.out, t022_sby_summaries.txt (the summary and DONE lines per
  run with their SBY stamps), t022_sat_results.txt, t022_nets.txt.
- runs/<job>/: logfile.txt, engine logfiles, status, config.sby, PASS/FAIL/UNKNOWN marker, every
  counterexample trace (trace.vcd / trace_induct.vcd, class-R bounded-run traces included),
  implicit_declarations.txt (the grep count and lines; t022_core5: "= 0"), smt2_assert_count.txt
  (t022_core5: 46). runs/t022_sem/ holds the step-semantics experiment.

Summary lines as retained (logs/t022_sby_summaries.txt; stamps are the tool's local clock, UTC-4):

```
SBY  1:29:50 [t022_core] summary: successful proof by k-induction.        DONE (PASS, rc=0)
SBY  1:54:04 [t022_core5] summary: successful proof by k-induction.       DONE (PASS, rc=0)
SBY  1:31:33 [t022_lsu2] summary: successful proof by k-induction.        DONE (PASS, rc=0)
SBY  1:28:17 [t022_ibex_controller] summary: successful proof by k-induction.   DONE (PASS, rc=0)
SBY  1:28:16 [t022_ibex_multdiv_fast] summary: successful proof by k-induction. DONE (PASS, rc=0)
SBY  1:28:15 [t022_ibex_load_store_unit] failed assertion ... t022_formal.v:14268 step 3   DONE (FAIL) (artefact: free lsu_is_cap_i, section 2.2)
SBY  1:31:46 [t022_zcmp] counterexample trace [basecase] ... t022_formal_zcmp.v:7632   DONE (FAIL) (legitimate: [31:16] back-fill, 4.4)
SBY  1:38:43 [t022_zcmp2] counterexample trace [basecase] ... t022_formal_zcmp2.v:7632  DONE (FAIL) (artefact: free bus, 4.4)
SBY  1:47:55 [t022_zcmp3] counterexample trace [induction] ... :7634, :7635             DONE (UNKNOWN, rc=4) (basecase passed to depth 8)
SBY  1:49:29 [t022_zcmp3c] summary: unreached cover statements: ... :7636               DONE (FAIL, rc=2) (= cover unreached to depth 12)
SBY  2:15:30 [t022_zcmp3b] engine_0: terminating process                                (timeout in step 14; no failure through step 13)
SBY  2:15:30 [t022_zcmp3p] engine_0.basecase: terminating process                       (timeout in step 14; no failure through step 13)
SBY  2:40:30 [t022_zcmp3c20] engine_0: terminating process                              (timeout in step 14; cover unreached through step 13)
```

Reproduction (local, no LSF):

```
# from dv/auto_dv/work/rtl-arch/t022/ (model/, jobs/, sources/ as retained; the paths inside the .sby files point at the scratchpad and are rewritten to the retained copies when re-run)
yosys -q t022_elab.ys                      # flattened netlist + constants (section 4.3)
sby -f t022_core5.sby                      # whole-core proof set (section 4.1, 4.2) -> DONE (PASS)
sby -f t022_zcmp3.sby                      # Zcmp bounded proof (section 4.4) -> UNKNOWN (basecase pass, induction fails)
sby -f t022_zcmp3c.sby                     # Zcmp class-mismatch cover, depth 12 -> unreached
grep "implicitly declared" <run>/model/design.log   # must be empty for a run to count as evidence
```
