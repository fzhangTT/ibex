# Response file: reviews of the exclusion set (commit dca91fd, dv/auto_dv/excl/**)

Owner: rtl-arch. Created 2026-09-03 09:05Z ahead of the findings; rows filled 09:16Z for the cross-model review of dca91fd, 09:22Z for the Critic's REQUEST-CHANGES on dca91fd (dv/auto_dv/work/critic/gen_critic_exclusions_v1.md) and the low from the review of 13c0dfd (dv/auto_dv/reviews/2026-09-03-claude-diff-ece187a3-13c0dfd0.md). One file for both reviewers. Reviews expected: post-execution
cross-model review (target 42e6f28..dca91fd) and the Critic's check of the same commit. Rule: every
finding gets one row below with ADDRESSED or DISPUTED and the evidence; gen_exclusions.el is never
edited silently: a change to the file is a regeneration by dv/auto_dv/excl/gen_excl_select.py with
the selection-spec change named here and re-proved by a strict load.

## 1. Findings (filled as they arrive)

Row ids: CM-n = cross-model review findings (dca91fd: CM-1..CM-6; 13c0dfd: CM-7), CR-M-n = Critic
findings (gen_critic_exclusions_v1.md). Commit timing note: 0475b94 carries the pass-10 file (md5
3b67ac6f909ac21d83609c9239399e68, still containing the CR-M-1 object at .el:1327/:1329); the
regeneration that removes it (pass 12, md5 73fa4c3ba87878c5f5a429261ee5861a, generated 09:20Z) is in
the working tree and is what the file list of 09:22Z named for commit.

| # | Review | Finding (short) | Verdict | Evidence / action |
|---|---|---|---|---|
| CM-1 | cross-model dca91fd [high] gen_excl_select.py:355 | the A.1 sweep excluded reachable-but-masked ibex_cheriot_ex logic (check_rv32, all-false arms of check_cheriot, err_cause_comb fall-through) under an unreachability claim | ADDRESSED | the sweep is replaced by a guard analysis, now applied to EVERY module with Block ranges (see CR-M-1 below for the same defect class in the shared modules): rtl/ibex_cheriot_ex.sv (gen_excl_select.py guard_analysis / cheriot_ex_branch_dead_vectors / ex_const): an object is excluded only when an enclosing arm requires a constant-0 term or follows a constant-1 one, the constants being the yosys constant-propagation list (t022_flat.il, regenerable) plus the decoder defaults rtl/ibex_decoder.sv:297-303; each annotation names the guard and the term. Result: check_rv32 :699-737 live, check_cheriot else arms live, err_cause_comb :922 live, shared-adder defaults live (all four reviewer examples), 265 dead lines; entries dropped from 103 Blocks / 112 Branch vectors / 343 Condition vectors to 75 / 66 / 119; the gated LINE denominator with the file rises 4057 -> 4134 (the masked logic now counts). Strict load pass 9 and 10 clean (gen_precheck_urg_pass10.log); README section 1 rule 3 and section 4 rewritten. |
| CR-M-1 | Critic gen_critic_exclusions_v1.md M-1 (medium) gen_exclusions.el:1115 | rtl/ibex_cs_registers.sv:2130 `gen_scr.mstack_epc_cap_q <= mepc_cap` (enable mstack_en fires on every non-debug trap) was excluded by the A.3 range :2108-2209 although draft A.8 names it live; README line 53 was false for it | ADDRESSED | two layers, both in gen_excl_select.py: (1) the guard analysis is generalised to the shared modules (guard_analysis on every module of MODULE_RTL; ex_const knows the tie compare, the CONST0 names, *_en_cheriot, the cheriot_csr_* inputs, the opentitan parameters and the RV32B define): a Block is selected only when it is inside an approved A.3/P range AND under a dead guard, except the explicit enum-default and never-held-state ranges whose cone is the enum declaration or the T022 state proof; the report lists every in-range block kept live, e.g. cs_registers :473/:482 `csr_rdata_int = mtvec_q / mepc_q` (the live else arms of the On-gated illegal check, excluded in dca91fd and caught by nobody until the predicate) and :682/:690/:698 `illegal_csr = 1'b1`; (2) an explicit CARVE_BACK table per shared module (signature regexes and line ranges from draft A.8 and its v1 list: mstack_epc_cap_q, *_combi, controller :827-840/:909-914/:923-926/illegal_insn_d, id_stage instr_kill :1033-1036/instr_is_rv32lsu_id, core rvfi_id_done :1851-1853/branch_target_ex/alert_major_internal_o, LSU :650-653/:664-667, decoder illegal arms, register-file shared nets, cheriot_ex live lines and csr_mshwm_new_o) applied as the last filter over every emitted line, hits reported. Result: mstack_epc_cap_q appears nowhere in the file (grep count 0); 186 Blocks (dca91fd: 227); strict load passes 11 and 12 clean; gated LINE with the file 1694/4154 (dca91fd 4057). Collateral kept in coverage, documented in README section 5: cs_registers :2142 `mepc_cap <= mstack_epc_cap_q` (dead guard, removed by the signature filter), the constant-selector SCR read-mux items :2018-2048 the indentation analysis did not resolve, three register-file ternary vectors on rcap_r0/rf_shared. |
| CM-2 | cross-model dca91fd [medium] README:81, :127-130 | ASSERT row compared different scopes; the Assert entries do take effect | ADDRESSED | README section 3 table is now the gated rows summed from the hierarchy reports (ASSERT 143/178 -> 143/175, 3 removed) with the URG top-row explanation as a note; section 5 item 4 closed; the annotation names the macro correctly (`ASSERT(name, cheriot_enabled \|-> ...)`, not ASSERT_IF). |
| CM-3 | cross-model dca91fd [medium] README:74-80 | "objects removed" not reconciled with entry counts | ADDRESSED (explanation + census; exact no-op list is a follow-up) | README section 3: per metric the objects removed, the entries emitted and the mechanism (multi-line Blocks; vectors already Unreachable by -cm_seqnoconst are no-ops; toggle objects per bit and edge; FSM states unscored), plus the status-token census of the pass-10 report (LINE excluded 847 / unreachable 1115, BRANCH 244 / 373, TOGGLE 828 / 179, ASSERT 3, FSM 18). The per-object join of dump, .el and report that names every no-op entry is the follow-up for the first measured regression (both carry line numbers). |
| CM-4 | cross-model dca91fd [medium] README:5-8 | authority chain under git-ignored dv/auto_dv/work/ | ADDRESSED | promoted to dv/auto_dv/evidence/: gen_exclusions_draft_v2.md, gen_unreachability_evidence.md, gen_cheriot_carveout.md, gen_param_resolution.md, gen_hierarchy_map.md (ASCII, byte copies of the working files at 09:12Z); the Critic rulings were already committed there (gen_critic_exclusions_draft_v1/v2.md). README header now lists every path with what it contributes. Annotations cite the documents by name (no directory), resolvable at the committed paths. |
| CM-5 | cross-model dca91fd [low] gen_excl_select.py:107-108 | class-D annotations carry "TO BE FILLED" EC-3 fields | ADDRESSED | the three spare-encoding groups are held out unless --allow-unfilled-ec3 is given; the .el header states the hold-out; README section 1 rule 7 and F-3 row updated. The three 2a groups (no spare encoding, no EC-3 requirement) stay in. |
| CM-7 | cross-model 13c0dfd [low] gen_exclusions_README.md:95 | "served at 09:0xZ" and "no report-only request kind at 08:50Z" imprecise | ADDRESSED | README section 3 now quotes the manifests: rtl-arch-003 received 08:50:30Z, refused with reason `invalid request: tests must be a non-empty list, a comma list, or a tier word (empty only with elcheck)`; rtl-arch-004 received 08:58:25Z, finished 08:58:31Z; rtl-arch-005 received 09:13:43Z, finished 09:13:52Z. |
| CM-6 | cross-model dca91fd [low] gen_excl_select.py:130-131, 156-157 | class-P parameter values re-typed as prose | ADDRESSED | gen_excl_select.py runs `util/ibex_config.py opentitan vcs_opts` at generation, stops unless BranchPredictor = 0, BranchTargetALU = 1 and RV32B = RV32BOTEarlGrey, records the read values in the selection report, and the class-P annotation states that the values were verified at generation. |

## 2. Evidence prepared in advance for the announced review focus (written before the findings; E-4 and E-5 superseded by the rows above where they differ)

E-1 Justification versus RTL. Every group's ANNOTATION names class, RTL location, tie chain or
parameter, EC set and the T022_* proof; the proofs are re-runnable from
dv/auto_dv/evidence/gen_t022_formal/ (gen_t022_regen.sh, parameter guard, README section 5 job-to-class
map). The RTL facts behind the tie chain: dv/auto_dv/work/rtl-arch/gen_cheriot_carveout.md (G1-G8),
gen_unreachability_evidence.md 4.1/4.2.

E-2 Verbatim copy from the urg dump. gen_excl_select.py copies each entry line unchanged from
fullexclude_module.<metric> (id, checksum, signature, vector) of the round-0 re-baseline dump; the
selection report gen_exclusions_select_report.md counts matches per rule. Spot check for a reviewer:
`grep -F '<entry line>' <outdir>/cov_unmeasured/full_exclusions/fullexclude_module.<metric>` finds
every non-annotation line of the .el prefixed by `// `.

E-3 Strict-load evidence. dv/auto_dv/excl/gen_precheck/: pass 1 log and attempts (285 covered
objects attempted: the header-line and statement-header lessons, README section 3), passes 2-4
attempts (the --attempts inputs), pass 8 urg log (0 warnings, 0 errors) and dashboard. Runtime
repeats the load through the flow under rtl-arch-003; its manifest path goes into the README.

E-4 The three Assert entries (MODULE ibex_register_file_ff, g_cheriot_rf.Cheriot*MSBClear). They ARE
applied: pass-8 asserts.txt "Summary for Assertions: Excluded 3" and the three detail rows read
"Excluded"; the u_register_file hierarchy row changes from ASSERT 1/5 (round-0 report) to 1/2
(pass 8), and the flow's gated row (u_ibex_core + u_register_file) from 143/178 to 143/175 in
Runtime's elcheck manifest runtime-007. Only URG's top "Total Coverage Summary" ASSERT figure is
143/178 both ways because that summary nets out no-attempt assertions. README section 3 table now
quotes the gated rows from runtime-007 (the author pre-check dashboards were the informational u_dut
summary rows, which also explains the TOGGLE 1994 vs 1682 numerator difference) and section 5 item 4
is resolved; this file records both edits to the committed README.

E-5 Anything that excludes a reachable path. The strict load is the oracle: 48 draft objects that
the NOP smoke covered were refuted and dropped (README section 4, select report "Dropped"). Every
remaining Block/Branch/Condition entry is either inside a CHERIoT-only arm, a vector whose
constant-tie operand takes its impossible value, a parameter-dead body (class P) or an enum default
arm (class D). Known limits, stated rather than hidden: (a) the A.4 vector selection relies on URG's
vector encoding (operand values in source order; a top-level negation or ternary condition is
encoded by its inner expression or select), verified by the strict load (a wrong reading is
rejected as "covered" or leaves the impossible vector in coverage, never excludes a possible one
silently); (b) the fetch_enable_i and mcounteren_writable_i comparisons are never selected; (c) the
unclassified conditions listed in the select report stay in coverage.

E-6 Scope form. MODULE scopes are used because every DUT module has exactly one instance under
u_dut (u_ibex_core, u_register_file trees), so MODULE and INSTANCE select the same objects and the
file does not embed the TB top name (B.7 rule 5). The Assert entries prove the point: MODULE-scoped
entries are reported under the instance path in asserts.txt.

E-7 Class D default arms. Block entries for the six default-arm statements; URG emits no separate
case-default branch vector for these case statements in this dump (README section 5 item 5); EC-3
attempts/failures fields are literal "TO BE FILLED" placeholders until the first measured
regression (F-3), so a reviewer can grep for them.
