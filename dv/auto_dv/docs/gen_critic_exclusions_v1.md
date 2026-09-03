# Critic verdict: coverage exclusion set, draft form (T-069 landing, commit dca91fd)

Artifacts under review (committed blobs at dca91fd = HEAD content for these files except the README; sha256 first 16 hex):
- dv/auto_dv/excl/gen_exclusions.el (2133 lines, 41 MODULE/metric scopes, 204 annotation groups)      4a2a6c817d8a8c4d
- dv/auto_dv/excl/gen_excl_select.py (508 lines)                                                       00438dbe59570943
- dv/auto_dv/excl/gen_exclusions_README.md (152 lines; the working tree carries an uncommitted edit of
  Section 5 item 4, see I-1)                                                                            c65b9c86dac9dd70
- dv/auto_dv/excl/gen_exclusions_select_report.md (147 lines)                                          029cebed34ed0757
- dv/auto_dv/excl/gen_precheck/ (attempts logs pass1..4, urg logs pass1/pass8, dashboard pass8)
- Reference dump: /proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_0_rebaseline/cov_unmeasured/full_exclusions/
  (fullexclude_module.{line,branch,cond,tgl,fsm,assert}, 03:13:49 local); reference vdb the same tree's merged.vdb.
Date: 2026-09-03 (UTC). Role: Critic (DV_prompt.txt Section 4: every exclusion needs a written justification; control-logic
exclusions need an unreachability argument and this reviewer's approval). Rulings applied: gen_critic_exclusions_draft_v1.md
(R-1..R-5, E-01..E-05, EC-1..EC-6) and gen_critic_exclusions_draft_v2.md (conditions F-1..F-7). The cross-model review of the
same commit was not read before this verdict.

CRITIC VERDICT: REQUEST-CHANGES

The mechanism is sound and the file is almost right: every one of the 1597 entries is a verbatim copy of a dump object under
its own MODULE checksum, the 48 refuted objects are gone and provably covered, the dashboard deltas are exactly what the
README claims, and every excluded block in the shared modules lies inside a dead range of the approved draft. One block is
nevertheless reachable in RV32I mode and excluded: the mstack shadow-capability update, which the draft's own carve-back list
names as live (M-1). That is the one defect DV_prompt Section 5 calls the number-one risk, so it blocks the draft until the
selection honours the carve-backs; the fix is a few lines in the generator and one regeneration.

## 1. Mechanical verification (my own scripts against the committed file and the dump)

| Check | Result |
|---|---|
| Entries copied verbatim (id, checksum, signature, vector) from fullexclude_module.<metric> under the same MODULE | 1597 of 1597 found (227 Block, 116 Branch, 769 Condition, 463 Toggle, 2 Fsm, 5 State, 12 Transition, 3 Assert) |
| Module CHECKSUM lines equal the dump's | 41 of 41 |
| The 48 dropped entries (select report lines 99-147) | each appears in a strict-load attempts log (pass1: 285 attempts, pass2: 60, pass3: 38, pass4: 1), so URG itself refuted them as covered; none remains in the file; all 48 are real dump objects |
| Block placement in the shared modules (dump annotation "LineNumber" precedes its entry, the pairing gen_excl_select.py:16-18 and :34-76 uses) | 132 of 132 excluded blocks lie inside the dead ranges the select report lists (lines 5-19); the live illegal-instruction cause at rtl/ibex_controller.sv:865 (dump Block 110) is not in the file, the excluded cause-2 block is Block 132 at :937 inside the dead cheriot_wb_err_prio arm |
| Condition vector semantics | every bare `(cheriot_enable_i == ibex_pkg::IbexMuBiOn)` entry excludes only vector "1" (110 entries across nine modules); compound entries exclude only vectors with a CHERIoT operand at 1 (samples at controller, core, cs_registers) |
| T022_* proof names cited in annotations | 17 names, all resolve in dv/auto_dv/evidence/gen_t022_formal/sources/gen_t022_assertions_extract.txt |
| Dashboard deltas (README lines 74-81 vs gen_precheck/gen_precheck_dashboard_pass8.txt vs the re-baseline dashboard) | identical numerators; LINE 4351 -> 4057, COND 9566 -> 9220, TOGGLE 26958 -> 23016, FSM 86 -> 74, BRANCH 2418 -> 2320 as claimed; ASSERT: the top-level instance row moves 143/178 -> 143/175 (the three g_cheriot_rf assertions are honoured), while URG's total row stays 143/178 because it nets uvm_pkg's three (I-1) |
| Class R rows 37-40 | absent (no cm_state entries); F-5 met |
| EC-3 placeholders on the three guarded class-D arms | present ("attempts N, failures 0 ... TO BE FILLED"); F-3 open as stated |

## 2. Annotation groups verified against rtl/ for gen_dut_top's configuration (19 groups)

| Group (file line) | Class | RTL checked | Holds |
|---|---|---|---|
| controller :690-696 (812) | P | rtl/ibex_controller.sv:690-696 `if (BranchPredictor)` body; BranchPredictor = 0; EC-1 T022_CORE_BP0 | yes |
| controller :990-993 (815) | D spare | :988-994 default -> RESET; guard IbexCtrlStateValid :1104 | yes |
| decoder :1342-1344/:1348-1350 (1424) | P | rtl/ibex_decoder.sv:1341-1351 `if (RV32B == RV32BFull)` bodies; RV32B = RV32BOTEarlGrey; case items :1341/:1347 stay live | yes |
| icache :1268 (1559) | D no spare | rtl/ibex_icache.sv:193-198 2-bit enum, 4 values; :1268 default | yes |
| id_stage :968-970 (1569) | D no spare | rtl/ibex_id_stage.sv:861 1-bit enum; :968-970 default | yes |
| LSU :605-607 (1749) | D spare | rtl/ibex_load_store_unit.sv:603-608; guard IbexLsuStateValid :821 | yes |
| multdiv :522-524 (1928) | D spare | rtl/ibex_multdiv_fast.sv:520-525; guard IbexMultDivStateValid :532 | yes |
| multdiv :238-240 (1931) | D no spare | :142-144 1-bit enum; :236-241 default | yes |
| cheriot_ex A.1 block group (8) | T | result_cap_o/result_data_o arms: module logic dead behind the tie except the live list (draft A.1; T022_LSU_CHERI0 etc.) | yes |
| controller fetch-error and LSU-error CHERIoT arms | T | :850-858 tag/bound violation, :901-908 and :915-922 `(On) & lsu_err_is_cheriot_q` arms (causes 28, 6, 4), :928-948 cheriot_ex/wb/asr_err_prio arms (cause 28 and the cause-2 at :937) | yes |
| controller conditions on cheriot_branch_req_i / cheriot_wb_err_q | T (A.4) | vectors 01/10/11 excluded, 00 kept | yes |
| core PMP request ternaries (Branch vectors) | T | rtl/ibex_core.sv:1590-1593, :1627-1630 `(On) ? '0 : ...` true arms | yes |
| core Condition 82 branch_target_ex select (1002) | T | `instr_is_cheriot_id` constant 0: vector "1" only | yes |
| core Toggle ports (cheriot_enable_i, data_tag_i/o, rf_*cap_ecc, rvfi_*cap fields) | T (A.5) | constants under the tie (T022_CORE_CHERI0, wrapper ties) | yes |
| compressed decoder :230-233, :557-560 blocks | T | `if ((BaseIsa..) && (On))` arms; else arms not excluded | yes |
| cs_registers Condition 135 mshwm select (1255) | T | csr_mshwm_set_i constant 0 (T022_CSR_MSHWM0): vector "1" only | yes |
| LSU FSM CTX_* states/transitions, cap_rx_fsm_q (Fsm entries) | T (A.6) | CHERIoT store-context and cap-receive states; T022_LSU_NO_CTX, T022_CRX_IDLE | yes |
| register_file_ff Assert g_cheriot_rf.Cheriot*MSBClear (3) and Toggle rcap/wcap ports | T (A.7/A.5) | constant-0 antecedent; cap seam constant | yes |
| register_file_ff Conditions 67/70 (.el 2018, 2021) on the `g_cheriot_rf.cheriot_enabled` select | T (A.4) | rtl/ibex_register_file_ff.sv:95 `cheriot_enabled = (cheriot_enable_i == IbexMuBiOn)`, constant 0; only vector "1" (the cap-read arm) excluded, the RV32I arm and the A.8 rf_shared storage stay in coverage | yes |
| cs_registers blocks :2108-2209 (group 1094, entries 1113-1121) | T | 16 of 17 blocks under `*_en_cheriot` or `(On) && ...` gates (e.g. :2062-2068 pcc_cap_q under `else if (On)`, :2138/:2141/:2187 under (On)); ONE block reachable, see M-1 | no (M-1) |

## 3. Findings

M-1 (medium) A reachable RV32I block is excluded. gen_exclusions.el:1115 `Block 299 "1318991522" "gen_scr.mstack_epc_cap_q <=
mepc_cap;"` is rtl/ibex_cs_registers.sv:2130 in the always_ff at :2126-2132, enabled by `mstack_en`. `mstack_en` is set at
:933 inside the `csr_save_cause_i ... else if (!debug_mode_i)` branch (:918-933), which fires on every non-debug trap or
interrupt entry in RV32I mode; the statement executes on every such entry (its value, mepc_cap, is constant, but line and
block coverage count the statement). The draft's own carve-back list names it: gen_exclusions_draft.md A.8 (line 256)
"mstack_epc_cap_q ... (toggle in RV32I mode on traps)", and my plan-set verdict (gen_critic_plan_set_v1.md Section 6) relayed
the same object to rtl-arch. The selector picked it because A.3's range :2108-2209 is applied as a whole (gen_excl_select.py
select spec; the only live-object lists in the generator are CHERIOT_EX_LIVE_LINES / CHERIOT_EX_LIVE_PORTS for
ibex_cheriot_ex, :355-356), so README line 53 "A.8 carve-backs ... 0, never selected" is not true for this block. The
round-0 re-baseline could not refute it: the NOP smoke takes no trap, so the object was uncovered and the strict load had
nothing to attempt. Required: an explicit A.8 carve-back list for the shared modules in the generator (at least
ibex_cs_registers :2130, applied as a per-block exclusion from the range), regeneration of the file and the report, and a
strict-load pre-check that is still clean; the README's Section 2 row for A.8 states the mechanism. F-6 and F-7 stay open
until then.

I-1 (info) README Section 5 item 4 (HEAD) says the ASSERT denominator "stayed 178"; the pass-8 dashboard shows the
gen_smoke_tb_top row at 143/175 (the three assertions excluded) and only the total row at 143/178 (uvm_pkg's three added
back). The working tree already carries the corrected paragraph; it is uncommitted at review time, so this verdict cites
the HEAD text.

I-2 (info) Run request dv/auto_dv/work/runtime/requests/rtl-arch-003.yaml (the strict load through the flow, purpose 2) is
filed and not yet served; the README's Section 3 is the author's pre-check, and F-1 is met only by the load on the first
measured regression's own vdb, as the README says.

I-3 (info) The urg pre-check commands wrote their report directories under the session scratchpad; the committed record is
the dashboard and the urg logs under gen_precheck/, which is enough for the draft form. The final-file run goes through
the flow and lands in the out root.

## 4. Status of conditions F-1..F-7 for the final file (this verdict does not approve the final file)

F-1 open (first measured regression); F-2 met (verified in gen_critic_exclusions_draft_v2.md addendum, bd1cfbe); F-3 open
(EC-3 report); F-4 met for the decision and the cheriot_enable_i conditions, and the fetch_enable_i conditions are correctly
absent; F-5 met; F-6 and F-7 open until M-1 is fixed (one entry outside the approved object set).

## 5. Method and fence record

Scripts run by me: verbatim and checksum match of the committed .el against the dump; exact-line check of the 48 dropped
entries against the .el and the attempts logs; block placement through the dump's LineNumber annotations against the dead
ranges; condition-vector semantics; proof-name resolution. RTL lines read as cited. The urg pre-check was not re-run (report-
time tool run is Runtime's; the committed logs and dashboard were audited by stamp and content). No LSF command; no fence
event; the cross-model artifact of the same commit was not opened.
