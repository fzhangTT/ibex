# Response file: reviews of the exclusion set (commit dca91fd, dv/auto_dv/excl/**)

Owner: rtl-arch. Created 2026-09-03 09:05Z ahead of the findings; rows filled 09:16Z for the cross-model review (the Critic's rows follow when its check lands). Reviews expected: post-execution
cross-model review (target 42e6f28..dca91fd) and the Critic's check of the same commit. Rule: every
finding gets one row below with ADDRESSED or DISPUTED and the evidence; gen_exclusions.el is never
edited silently: a change to the file is a regeneration by dv/auto_dv/excl/gen_excl_select.py with
the selection-spec change named here and re-proved by a strict load.

## 1. Findings (filled as they arrive)

| # | Review | Finding (short) | Verdict | Evidence / action |
|---|---|---|---|---|
| H-1 | cross-model dca91fd [high] gen_excl_select.py:355 | the A.1 sweep excluded reachable-but-masked ibex_cheriot_ex logic (check_rv32, all-false arms of check_cheriot, err_cause_comb fall-through) under an unreachability claim | ADDRESSED | the sweep is replaced by a guard analysis of rtl/ibex_cheriot_ex.sv (gen_excl_select.py guard_analysis / cheriot_ex_branch_dead_vectors / ex_const): an object is excluded only when an enclosing arm requires a constant-0 term or follows a constant-1 one, the constants being the yosys constant-propagation list (t022_flat.il, regenerable) plus the decoder defaults rtl/ibex_decoder.sv:297-303; each annotation names the guard and the term. Result: check_rv32 :699-737 live, check_cheriot else arms live, err_cause_comb :922 live, shared-adder defaults live (all four reviewer examples), 265 dead lines; entries dropped from 103 Blocks / 112 Branch vectors / 343 Condition vectors to 75 / 66 / 119; the gated LINE denominator with the file rises 4057 -> 4134 (the masked logic now counts). Strict load pass 9 and 10 clean (gen_precheck_urg_pass10.log); README section 1 rule 3 and section 4 rewritten. |
| M-1 | [medium] README:81, :127-130 | ASSERT row compared different scopes; the Assert entries do take effect | ADDRESSED | README section 3 table is now the gated rows summed from the hierarchy reports (ASSERT 143/178 -> 143/175, 3 removed) with the URG top-row explanation as a note; section 5 item 4 closed; the annotation names the macro correctly (`ASSERT(name, cheriot_enabled \|-> ...)`, not ASSERT_IF). |
| M-2 | [medium] README:74-80 | "objects removed" not reconciled with entry counts | ADDRESSED (explanation + census; exact no-op list is a follow-up) | README section 3: per metric the objects removed, the entries emitted and the mechanism (multi-line Blocks; vectors already Unreachable by -cm_seqnoconst are no-ops; toggle objects per bit and edge; FSM states unscored), plus the status-token census of the pass-10 report (LINE excluded 847 / unreachable 1115, BRANCH 244 / 373, TOGGLE 828 / 179, ASSERT 3, FSM 18). The per-object join of dump, .el and report that names every no-op entry is the follow-up for the first measured regression (both carry line numbers). |
| M-3 | [medium] README:5-8 | authority chain under git-ignored dv/auto_dv/work/ | ADDRESSED | promoted to dv/auto_dv/evidence/: gen_exclusions_draft_v2.md, gen_unreachability_evidence.md, gen_cheriot_carveout.md, gen_param_resolution.md, gen_hierarchy_map.md (ASCII, byte copies of the working files at 09:12Z); the Critic rulings were already committed there (gen_critic_exclusions_draft_v1/v2.md). README header now lists every path with what it contributes. Annotations cite the documents by name (no directory), resolvable at the committed paths. |
| L-1 | [low] gen_excl_select.py:107-108 | class-D annotations carry "TO BE FILLED" EC-3 fields | ADDRESSED | the three spare-encoding groups are held out unless --allow-unfilled-ec3 is given; the .el header states the hold-out; README section 1 rule 7 and F-3 row updated. The three 2a groups (no spare encoding, no EC-3 requirement) stay in. |
| L-2 | [low] gen_excl_select.py:130-131, 156-157 | class-P parameter values re-typed as prose | ADDRESSED | gen_excl_select.py runs `util/ibex_config.py opentitan vcs_opts` at generation, stops unless BranchPredictor = 0, BranchTargetALU = 1 and RV32B = RV32BOTEarlGrey, records the read values in the selection report, and the class-P annotation states that the values were verified at generation. |

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
