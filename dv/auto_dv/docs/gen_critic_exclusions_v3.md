# Critic verdict: exclusion set, third review (commit 4125c36, pass-12 file)

Artifact: dv/auto_dv/excl/gen_exclusions.el at commit 4125c36
sha256 (first 16 hex): 103eb06933839dec   md5: 73fa4c3ba87878c5f5a429261ee5861a (as claimed)
1421 entry lines, 381 annotation groups, 41 (module, metric) scopes; 186 Block, 83 Branch-vector, 667 Condition-vector,
463 Toggle, 2 Fsm + 5 State + 12 Transition, 3 Assert.
Also judged at the same commit: dv/auto_dv/excl/gen_excl_select.py (5ec3fffa0c66d070, 980 lines),
gen_exclusions_README.md (64a3277ef29ffa22, 285), gen_exclusions_select_report.md (16e3728964bf81be, 145),
dv/auto_dv/evidence/gen_critic_response_exclusions.md (7fcb72f63ffe6da6, 76; rows CR-M-1, CM-1..CM-7),
Runtime manifest dv/auto_dv/work/runtime/results/rtl-arch-006/manifest.yaml (working path).
Date: 2026-09-03T09:58Z   Role: Critic   Previous: gen_critic_exclusions_v1.md (dca91fd) and _v2.md (0475b94), both
REQUEST-CHANGES on the one medium M-1. This verdict is the cited ruling; a byte-identical copy is under
dv/auto_dv/evidence/gen_critic_exclusions_v3.md.

CRITIC VERDICT: APPROVE (draft-form exclusion file; final-file conditions F-1 and F-3 stay open until the first
measured regression, as agreed in gen_critic_exclusions_draft_v2.md section 5)

## 1. M-1 closed

- The object is gone: 0 hits in the file for checksum 1318991522 and for the text `mstack_epc_cap_q <= mepc_cap`.
- Mechanism, not luck: gen_excl_select.py:119-131 is an explicit CARVE_BACK table per shared module (signature
  regexes and line ranges from draft A.8 and its v1 list), applied as the last filter over every emitted line
  (carved_back(), :133-139; applied at :837, :867, :956) with every hit reported. The selection report lists the
  hits: cs_registers :2128, :2130, :2142 (the mstack_epc_cap_q always_ff, all three arms), decoder :351, :824,
  :856, :873 (`illegal_insn = 1'b1` else arms of the CHERIoT opcode bodies), and three register-file ternary
  vectors. A second layer, the guard analysis on every shared module (report lines 6-18), keeps 21 in-range
  cs_registers blocks live on its own, among them the two else arms :473 / :482 and the three `illegal_csr = 1'b1`
  arms that dca91fd had excluded and nobody had caught.
- Response row CR-M-1 exists at the committed path and is accurate.

## 2. Verified at 4125c36 (re-run of every check from v1 and v2)

- Verbatim copy: 1421/1421 entry lines match the round-0 re-baseline dump (fullexclude_module.*); 41/41 scope
  CHECKSUM headers match the dump (the header precedes its MODULE line in both files; my first comparison this
  pass paired them the other way and reported mismatches that were mine, not the file's).
- Placement: 186/186 Blocks lie inside the report's ranges (LineNumber annotation preceding each entry); 111 are
  shared-module blocks, 75 ibex_cheriot_ex.
- Guard analysis on the shared modules, read against the RTL for every selected range head and 30 of the 111
  blocks: cs_registers :471 / :480 (the On arm of CSR_MTVEC / CSR_MEPC), :680 / :688 / :696 (CSR_MSHWM, MSHWMB,
  CDBG_CTRL under `cheriot_enable_i == On`), :714 (`!PMPEnable || On` with PMPEnable = 1 from the config),
  :2067 (else-if On), :2116 / :2144 / :2158 / :2173 / :2189 / :2206 / :2208 (`*_en_cheriot`, each
  `cheriot_csr_op_en_i && ...` at :2108 / :2121 / :2149 / :2179, constant 0 by the tie chain), :2139 / :2187
  (`On && csr_save_cause_i ...`), :2223 (cheriot_fatal_err); controller :319 / :329 / :331 (`On & cheriot_*_err_q`),
  :694 (BranchPredictor = 0, class P), :852 / :856 (`On & instr_fetch_cheriot_acc_vio_i`), :896 (On), :903-:946
  (the exception-cause arms under `On & lsu_err_is_cheriot_q`, cheriot_ex_err_prio, cheriot_wb_err_prio,
  cheriot_asr_err_prio, all constant-0 prio nets or On); id_stage :904 / :906 (the cheriot_lsu_req_dec case item,
  On); core :2224 (resp_is_cap_q); decoder :314-:323 and :793-:876 (`dual & On & ~illegal_c_insn_i`, else arms
  carved back), :1342-:1350 (`RV32B == RV32BFull`, class P); LSU :139 / :211 / :437 (`dual & On & lsu_is_cap_i`,
  `cpu_req_erred`); compressed decoder ranges (`dual && On`). No unsound exclusion found. The conservative
  direction holds: the SCR read-mux items :2018-:2053 and the ten reset-value blocks are kept live because the
  predicate cannot resolve them, and :2142 is kept live by the signature filter although its guard is dead.
- A.4 vector semantics, sampled: `((cheriot_enable_i == On) & cheriot_branch_req_i)` vectors 01, 10, 11
  excluded, 00 kept; likewise `& cheriot_wb_err_q`. Correct.
- Dropped entries: the ten refuted cs_registers reset-value blocks are absent (0 hits) and listed live in the report.
- Strict load: gen_precheck_urg_pass12.log has 0 UCAPI / Warning / Error lines against the round-0 vdb with
  -excl_strict. Runtime rtl-arch-006 (elfile sha256 103eb069... equals the committed blob): verdict ok,
  with_elfile status ok, urg rc 0, excl_strict true, 0 exclusion violations, excluded objects on the gate row
  line 197 / cond 247 / toggle 3942 / fsm 12 / branch 65 / assert 3, which reproduces the README section 3 table
  (LINE 1694/4351 -> 1694/4154, COND 2547/9566 -> 2547/9319, TOGGLE 1682/24538 -> 1682/20596, FSM 6/86 -> 6/74,
  BRANCH 798/2418 -> 798/2353, ASSERT 143/178 -> 143/175).
- Cross-model rows: CM-1 (the four reviewer arms now live, verified in v2 and unchanged), CM-2 (ASSERT 3 entries,
  gated 178 -> 175), CM-4 (five authority documents under evidence/, paths resolve), CM-5 (class-D spare groups
  held out: report lines 56-58), CM-6 (config guard: report line 5 records BranchPredictor=0 BranchTargetALU=1
  RV32B=RV32BOTEarlGrey from util/ibex_config.py), CM-7 (manifest times quoted). CM-3's per-object no-op list is
  an open follow-up by its own text (L-3).

## 3. Final-file conditions

F-2, F-4, F-5 met (unchanged). F-6 and F-7 now MET: every entry sits inside the agreed object list and the one
entry outside it (M-1) is removed by an explicit mechanism whose hits are reported. F-1 (generated at the first
measured regression against its own dump, legal measured stimulus, EC-5 clean) and F-3 (EC-3 attempts/failures
for the three guarded default arms; README section 7 gives the procedure) stay open until that regression. The
file may be loaded on measured runs now; the regenerated file at F-1 comes back to me.

## 4. Lows (none blocking)

- L-1 README section 2 row "A.8 carve-backs, class R rows 37-40 | 0 | never selected": the count of entries in
  the file is 0, but "never selected" contradicts the report, which shows 10 objects selected by the predicates
  and then removed by the filter. Say "selected and removed by the carve-back filter: 7 Blocks, 3 vectors".
- L-2 The pass-12 urg report directory named in gen_precheck_urg_pass12.log is the agent session's scratchpad
  (.../scratchpad/excl_precheck/report12), which is not retained. The committed log and dashboard suffice for this
  approval; future strict-load reports should be written under dv/auto_dv/work/rtl-arch/ or evidence/.
- L-3 CM-3 follow-up: the per-object join of dump, .el and report naming every no-op entry, due at the first
  measured regression.
- L-4 The working tree already differs from 4125c36 in all five excl files (655 insertions); the next commit
  lands .el, report and README together, and I re-check on that commit only if the file changes.


## 5. Addendum: pass 13 at commit 9ebf2d9 (annotation-only regeneration), judged 2026-09-03T10:03Z

Artifact: dv/auto_dv/excl/gen_exclusions.el at 9ebf2d9, sha256 3a815ffc68358b5e, md5 9b642ef57393d8b3af8de9485a8f6f88
(as claimed), 2534 lines, 1421 entry lines, 492 annotation groups (381 at 4125c36: the A.4 groups are now split per
constant term), 41 scopes. Generator 4c546d09cf935663 (1114 lines), README 560ea61a42d47a57, report 4217f64a9d13c21c,
response file 30095f5f62f3a9c4 (rows CM-8..CM-17 added).

CRITIC VERDICT (9ebf2d9): APPROVE, same terms as section 3 above. This addendum makes the v3 verdict cover both commits.

- Entry-set equality, verified by script: the sorted set of entry lines plus MODULE and CHECKSUM lines is identical
  between 4125c36 and 9ebf2d9 (0 differing lines). Only ANNOTATION lines changed (626 lines) and the entry order
  inside some scopes moved with the regrouping (47 sequence differences), which URG does not care about.
- Rows checked: CM-8 every A.4 annotation names the constant operand, its value and the impossible vector bit (sampled
  at rtl/ibex_cheriot_ex.sv:362); CM-9 0 citations of work/rtl-arch remain in the file; CM-10 / CM-12 split_neg()
  binds a negation to one token or one balanced group, self_test() (gen_excl_select.py:481-513, 16 cases) runs at
  every generation (:863) and stops the run on a failure; I imported the committed generator and ran self_test():
  passes; CM-15 the explicit LSU range is (618, 623) and :616-617 is now a dead-arm selection (entry unchanged);
  CM-14 the README COUNTS block (1421 entries, 41 / 492, 21 live in-range, 7 carve-backs, 0 refuted, 3 filter hits)
  agrees with the report; CM-16 per-module scoping (EX_MOD, MODULE_PARAMS) present; CM-17 the EC-3 fill accepts only
  dv/auto_dv/evidence/gen_round_<n>/asserts.txt with a measured merge recorded (:874-886) and records the relative path.
- Strict load pass 13: gen_precheck_urg_pass13.log has 0 UCAPI / Warning / Error lines; the pass-13 dashboard's gated
  LINE / COND / FSM / BRANCH ratios equal pass 12 (1694/4154, 2547/9319, 6/74, 798/2353), as an entry-identical file must.
- Lows L-1..L-4 of section 4 stand; L-1 (the "never selected" row) is superseded by the generated COUNTS block, which
  now states the carve-back and filter counts.
