# Critic verdict: exclusion set, second review (commit 0475b94)

Artifact: dv/auto_dv/excl/gen_exclusions.el at commit 0475b94
sha256 (first 16 hex): e43c2dcb50ffd9a2   md5: 3b67ac6f909ac21d83609c9239399e68
1442 entry lines, 384 annotation groups, 41 MODULE scopes (379 cheriot-out-of-scope, 3 class D, 2 class P)
Also judged at the same commit: dv/auto_dv/excl/gen_excl_select.py (865 lines), gen_exclusions_README.md (v2),
gen_exclusions_select_report.md, dv/auto_dv/evidence/gen_critic_response_exclusions.md (68 lines, committed path),
Runtime manifest dv/auto_dv/work/runtime/results/rtl-arch-005/manifest.yaml (working path, not yet promoted).
Date: 2026-09-03T09:28Z   Role: Critic   Previous verdict: gen_critic_exclusions_v1.md (dca91fd, REQUEST-CHANGES, one medium)

CRITIC VERDICT: REQUEST-CHANGES

The regenerated file is a real improvement (section 2), but the one medium finding of v1 is unchanged in the
committed text, and the request that reached me described it as addressed. The response file answers the six
cross-model rows only and says the Critic's rows "follow when its check lands"; no row addresses M-1.

## 1. Findings

### M-1 (medium, carried from v1, NOT addressed): a reachable RV32I block is still excluded

- Location: gen_exclusions.el:1327, `Block 299 "1318991522" "gen_scr.mstack_epc_cap_q <= mepc_cap;"`, inside
  the ibex_cs_registers class-T group whose header is at .el:1306 (range rtl/ibex_cs_registers.sv:2108-2209).
- RTL: rtl/ibex_cs_registers.sv:2126-2132. The always_ff enable is `mstack_en`, set at :933 on every non-debug
  trap entry; the block has no cheriot_enable_i guard. Any exception or interrupt in RV32I mode executes it.
- Evidence that the strict load cannot catch it: the round-0 re-baseline dump has no attempt on checksum
  1318991522 (both gen_precheck attempts logs: 0 hits), i.e. the smoke stimulus takes no trap. The first
  measured regression with any trap test will cover it and `-excl_strict` will then reject the entry, so this
  also threatens F-1 / EC-5, not only F-6 / F-7.
- Generator: gen_excl_select.py still applies the shared-module report ranges whole. There is no carve-back
  list for shared modules; the only mention is the comment at line 8 ("A.8 carve-backs never selected").
  README v2 section 2 still carries the row "A.8 carve-backs, class R rows 37-40 | 0 | never selected", which
  is false for :2130 (the draft's own A.8 line names it live).
- Required change: (a) an explicit per-line carve-back list for the shared modules in gen_excl_select.py,
  applied when a report range is expanded, with :2130 (the whole mstack_epc_cap_q always_ff arm) as its first
  member; (b) Block 299 absent from the regenerated file; (c) README section 2 replaces "never selected" with the
  carve-back list and its count; (d) the response file gets the Critic M-1 row with the commit that fixes it.
  Block 306 at .el:1329 (`mepc_cap <= gen_scr.mstack_epc_cap_q`, the restore path) sits under the
  cheriot_enable_i == IbexMuBiOn guard and stays excluded.

### L-1 (low): constant lists are a literal snapshot, cited against a working path

- gen_excl_select.py:390-408 defines CHERIOT_EX_CONST0_1BIT (55 names) and CHERIOT_EX_CONST_ZERO_MULTI as
  Python literals; the comment cites dv/auto_dv/work/rtl-arch/t022/model/t022_flat.il. The netlist IS committed
  (dv/auto_dv/evidence/gen_t022_formal/t022_flat.il), but nothing compares the literals with it.
- Required change (non-blocking): cite the evidence path, and either add a check mode that re-derives the two
  sets from the committed .il connect list and diffs them, or record the derivation command and its output in
  the README so the "yosys constant propagation" claim in every ibex_cheriot_ex annotation is auditable.

### L-2 (low): README section 3 predates the served run

- README line 143 says the rtl-arch-005 manifest path "is appended when served". The run was served 09:13:52Z
  with verdict ok; the committed README does not carry the path. Add it at the next regeneration.

### L-3 (note): working tree already ahead of HEAD

- All five excl files differ from HEAD in the working tree (rtl-arch editing). The working-tree select report
  lists ibex_register_file_ff Conditions 67/70/74 (cheriot_enabled ternary selects) in a dropped/not-selected
  list while the HEAD .el carries them at .el:2224-2230. Not a finding against 0475b94; the next commit must
  land .el, report and README together, and I judge only what is committed.

## 2. Verified at 0475b94 (all checks re-run on the committed blob)

- Verbatim copy: 1442/1442 entry lines match the round-0 re-baseline dump (fullexclude_module.*) after
  stripping the dump's comment prefix; 0 CHECKSUM mismatches across the 41 scopes.
- Dead-range placement: 129/129 shared-module Blocks lie inside the report's dead ranges (annotation LineNumber
  precedes its entry, as the generator's parse() assumes); 75 ibex_cheriot_ex Blocks; the class-D spare arms
  are held out (3 class-D no-spare and 2 class-P groups remain, as README section 1 item 7 says).
- Dropped entries: the 10 refuted cs_registers reset-value Blocks (checksums 2749661524, 4291899431, 2707070097,
  268972480, 3536564520, 3315413595, 746695531, 2244136683, 2252920583, 4238278554) are absent from the file
  (0 hits each) and present in both gen_precheck attempts logs (2 hits each).
- Cross-model H-1 arms: `check_rv32`, the all-false `check_cheriot` arms and the :922 fall-through
  (`cheriot_wb_err_info_d = cheriot_wb_err_info_q`) have no entry in the file (0 hits).
- Guard analysis soundness, eight ibex_cheriot_ex arms read against the RTL:
  1. :296-318 `case (1'b1)` items `cheriot_operator_i.CGET_FIELD`, `CSEAL | CUNSEAL`: the operator struct is
     the decoder default `'0` (rtl/ibex_decoder.sv:297) and only the CHERIoT decode path sets it; items are
     constant 0. Sound.
  2. :386 `else if (cheriot_setbounds_sel_i == SETBOUNDS_CRAM)`: selector default SETBOUNDS_NONE = 3'h0
     (rtl/ibex_decoder.sv:303, rtl/ibex_cheriot_pkg.sv:900), CRAM = 3'h6 (:906); the evaluator resolves enum
     literals from the packages and returns constant 0 for the comparison. Sound. The complementary rule
     (`== <zero-encoded literal>` is constant 1 and kills the later arms of the chain) is also correct.
  3. :466 Condition 27 `(perm_vio | illegal_scr_addr)`, all three OR vectors, inside the CCSR_RW case item.
     Sound (whole condition inside a dead arm).
  4. :499 Block 46 `trcap.valid = rf_fullcap_a.valid`, same CCSR_RW arm. Sound.
  5. :231 Condition 105 `(instr_is_cheriot_i | instr_is_rv32lsu_i)` vector "10" only: the impossible operand
     value is excluded and the live ternary arm (RV32 loads/stores) is kept. Sound and correctly narrow.
  6. :913 `CCSR_RW & cheriot_wb_err_raw & cheriot_exec_id_i`: AND with a constant-0 term. Sound.
  7. :915 `cheriot_wb_err_raw & cheriot_exec_id_i` and :917 `(is_load_cap | is_store_cap) & cheriot_lsu_err &
     cheriot_exec_id_i`: cheriot_exec_id_i is listed constant and the RTL agrees
     (rtl/ibex_id_stage.sv:1069 and :1160, `(cheriot_enable_i == IbexMuBiOn) & ...`); is_load_cap /
     is_store_cap are operator-struct fields (rtl/ibex_cheriot_ex.sv:560-561). Sound.
  8. :920 `rv32_lsu_req_i & rv32_lsu_err`: rv32_lsu_req_i is live in RV32I mode, but rv32_lsu_err is
     `(cheriot_enable_i == IbexMuBiOn) & ~debug_mode_i & ...` (rtl/ibex_cheriot_ex.sv:740), constant 0. Sound.
  Evaluator direction: AND is dead on any constant-0 term, OR only when every term is constant 0, negation
  inverts, unknown names return None and keep the object; nesting follows indentation with paren balance for
  multi-line conditions. The conservative direction is right; the residual risk is a mis-indented arm in the
  RTL, which the per-arm annotation makes visible to a reader.
- Runtime rtl-arch-005 (elcheck): elfile sha256 e43c2dcb50ffd9a2... equals the HEAD blob; scopes
  gen_smoke_tb_top.u_dut.u_ibex_core and .u_register_file; with_elfile status ok, urg rc 0, excl_strict true,
  0 exclusion violations. Gated rows with the file equal README section 3 exactly:
  LINE 1694/4134, COND 2547/9319, TOGGLE 1682/20596, FSM 6/74, BRANCH 798/2353, ASSERT 143/175
  (without the file: 4351 / 9566 / 24538 / 86 / 2418 / 178). Excluded counts on the gate row: line 217,
  cond 247, toggle 3942, fsm 12, branch 65, assert 3. The pass-10 dashboard agrees.
- Config guard: parameters are read through util/ibex_config.py (gen_excl_select.py:733-740), not re-typed.
- Five authority documents are under dv/auto_dv/evidence/ as claimed (README section 4 paths resolve).

## 3. Final-file conditions (gen_critic_exclusions_draft_v2.md section 5)

F-2, F-4, F-5 met (unchanged). F-1 and F-3 wait for the first measured regression. F-6 and F-7 stay OPEN on
M-1: an entry that the draft's own A.8 names live is an entry outside the agreed object list. Closing M-1
closes both for this file; F-1 then also depends on the carve-back, see the EC-5 note under M-1.

## 4. What closes this verdict

One regeneration with the M-1 carve-back and the README row, plus the Critic M-1 row in the response file.
No other change is required; L-1..L-3 may ride along. On that commit I re-run the verbatim, placement and
dropped-entry checks (minutes) and expect APPROVE pending EC-3 / EC-5 at the first measured regression.
