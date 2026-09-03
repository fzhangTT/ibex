# Response file: reviews of the exclusion set (commit dca91fd, dv/auto_dv/excl/**)

Owner: rtl-arch. Created 2026-09-03 09:05Z ahead of the findings. Reviews expected: post-execution
cross-model review (target 42e6f28..dca91fd) and the Critic's check of the same commit. Rule: every
finding gets one row below with ADDRESSED or DISPUTED and the evidence; gen_exclusions.el is never
edited silently: a change to the file is a regeneration by dv/auto_dv/excl/gen_excl_select.py with
the selection-spec change named here and re-proved by a strict load.

## 1. Findings (filled as they arrive)

| # | Review | Finding (short) | Verdict | Evidence / action |
|---|---|---|---|---|
| - | - | (none received yet) | - | - |

## 2. Evidence prepared in advance for the announced review focus

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
