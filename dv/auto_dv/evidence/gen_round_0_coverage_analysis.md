# Round-1 coverage analysis: the numbers, and where the gaps are

Owner directive LOG-093, 22:25Z: analyze and report the coverage metrics after the first coverage regression,
then pause for review. NAMING: the team calls this round 1; the flow indexes measured rounds from zero, so its
evidence directory is dv/auto_dv/evidence/gen_round_0 and its regression tag is round_1. This file is
read-only analysis over the committed record d29d5db and the round's output directory; no run, no re-merge,
nothing regenerated.

EVERY FIGURE BELOW NAMES ITS SOURCE FILE AND ITS SCOPE. The three scopes are not interchangeable: the GATED
row is the two DUT subtrees the Section 5 ruling gates on, the REPORT-WIDE row covers everything urg saw
including the testbench, and the INFO scope is instrumented and never gated. Reading a report-wide number as a
gate figure is the specific error this round already produced once.

## 1. The gate row as measured

Source: cov/report/dashboard.txt and the gate_row block of gen_round_0/gen_regress_manifest.yaml. Gated
scopes: gen_tb_top.u_dut.u_ibex_core and gen_tb_top.u_dut.u_register_file, covered and total objects summed
over the two disjoint subtrees. Gate threshold 80.0 (gen_flow_const.py:514).

| metric | percent | covered / total | verdict at 80 |
|---|---|---|---|
| line | 83.83 | 3654/4359 | PASS |
| cond | 67.17 | 6464/9624 | BELOW GATE |
| toggle | 67.39 | 16877/25044 | BELOW GATE |
| fsm | 44.19 | 38/86 | BELOW GATE |
| branch | 75.41 | 1831/2428 | BELOW GATE |
| assert | 92.74 | 166/179 | PASS |

THE GROUP CELL IS NOT CLAIMED EITHER WAY, and the round record says so. Three quantities exist: 81.47 is URG's
report-wide bin ratio 3477/4268 over all 26 covergroups including the witness ledger (cov/report/groups.txt);
78.29 is gen_cov_report's weight-averaged mean of the 25 covergroup scores with the ledger excluded by SV
name, and has no bin denominator of its own; 85.89 is 3477/4048, bins excluding the ledger's 220 clauses,
which is the quantity the criterion's words name and which no artifact reports. Two committed artifacts of
this run disagree on the cell (gen_cov_report.py:138-140 against gen_round.py:106-109), so the group gate is
NOT claimed passed for round 1 and the fix is rt39.

THE EXCLUSION-ADJUSTED ROW, second and never in place of the measured one. Pass 14 is committed at 98b643e and
dv/auto_dv/excl/gen_exclusions_README.md:149-154 carries the GATED before and after: line 3654/4359 to
3654/4158, cond 6464/9624 to 6464/9375, toggle 16877/25044 to 16877/21102, fsm 38/86 to 38/74, branch
1831/2428 to 1831/2363, assert 166/179 to 166/176. COVERED COUNTS ARE IDENTICAL in every metric, so nothing
the file does hides a hit; only denominators move. THE EXCLUSIONS ARE NOT APPLIED TO THE RECORDED ROUND: this
is what the same merge reads with the file, not what round 1 measured.

MIND THE SCOPE ON THAT ROW TOO. The artifact a reader is likeliest to open,
dv/auto_dv/excl/gen_precheck/gen_precheck_dashboard_round_0.txt, carries the REPORT-WIDE adjusted row instead:
line 3688/4194, cond 6471/9384, toggle 19231/24698, fsm 38/74, branch 1848/2383, assert 229/254, score 76.47.
Only the fsm figure is common to both, because fsm objects exist only in the gated modules. The gated row
above is the one that pairs with the measured gate row.

ONE CAVEAT TRAVELS WITH IT, from gen_exclusions_README.md:186: the strict load behind those numbers is the
exclusion author's own, and the Runtime Manager's independent re-load against this round's merged vdb is owed
and not yet run. It is a second row from the author, not yet jointly verified.

INFORMATIONAL, never gated (cov/report/hierarchy.txt): gen_tb_top.u_dut scores 71.25. REPORT-WIDE
(dashboard.txt): score 72.64, line 83.91 3688/4395, cond 67.18 6471/9633, toggle 67.15 19231/28640, fsm 44.19
38/86, branch 75.49 1848/2448, assert 89.11 229/257, group 81.47. The report-wide numbers are HIGHER than the
gated ones for line and branch and LOWER for assert and toggle, which is why quoting one for the other is not
a rounding difference.

## 2. Code-coverage gaps, by module

Source: cov/report/modlist.txt, ranked by MISSED objects (line + cond + toggle + fsm + branch), which ranks by
work remaining rather than by percentage. The top four modules hold 7073 of the missed objects.

| missed | module | line | cond | toggle | fsm | branch |
|---|---|---|---|---|---|---|
| 2211 | ibex_cheriot_ex | 132/336 | 87/347 | 743/2404 | -- | 41/127 |
| 1833 | ibex_cs_registers | 364/441 | 421/695 | 792/2202 | -- | 218/290 |
| 1815 | ibex_pmp | 234/358 | 2533/3966 | 73/200 | -- | 148/279 |
| 1214 | ibex_core | 377/390 | 455/647 | 1919/2908 | -- | 87/107 |
| 915 | gen_dut_top | -- | -- | 1695/2610 | -- | -- |
| 555 | ibex_controller | 140/244 | 169/312 | 331/570 | 5/26 | 44/92 |
| 524 | ibex_if_stage | 50/57 | 98/148 | 945/1400 | -- | 27/39 |
| 488 | ibex_id_stage | 82/89 | 229/268 | 1377/1808 | -- | 76/87 |
| 414 | ibex_wb_stage | 35/35 | 70/91 | 407/796 | -- | 15/19 |
| 392 | ibex_decoder | 426/471 | 115/157 | 585/794 | -- | 186/282 |
| 325 | ibex_load_store_unit | 170/205 | 123/197 | 510/678 | 6/22 | 79/111 |
| 224 | ibex_icache | 325/331 | 908/1049 | 537/604 | 5/8 | 193/200 |

TWO OF THE TOP THREE ARE FEATURE-SHAPED RATHER THAN STIMULUS-SHAPED. ibex_pmp misses 1433 of 3966 conditions,
and no round-1 test configures PMP: the two PMP entries in the testlist are unmeasured and their manifests
were removed because every bin they owned sits on an unbuilt covergroup. ibex_cheriot_ex misses 2211 objects
and no test exercises CHERIoT capability paths at all. Neither is a seed problem; both need tests that do not
exist.

gen_dut_top's 915 missed are all toggle, on the testbench wrapper rather than the DUT, and it is not in a
gated scope. It appears here because it is in the report and a reader will see it; it should not be worked.

### FSM detail

Source: cov/report/modlist.txt FSM column. Five modules carry FSM coverage and they account for the whole
38/86: the gate's worst metric is concentrated, not diffuse.

| module | transitions covered | transitions missed |
|---|---|---|
| ibex_controller | 5/26 | 21 |
| ibex_load_store_unit | 6/22 | 16 |
| ibex_icache | 5/8 | 3 |
| ibex_compressed_decoder | 14/17 | 3 |
| ibex_multdiv_fast | 8/13 | 5 |

The controller alone misses 21 of the 86, and its line coverage tells the same story: 140 of 244 lines, with
the whole ALWAYS block at ibex_controller.sv:504 uncovered (0 of 4) and the main block at :541 at 78 of 171.
Its FSM is the DECODE/FLUSH/IRQ/DEBUG state machine, so the unhit states and transitions are the exception,
debug-entry and interrupt paths this round barely drove: the round has no interrupt test, no debug test and no
exception-heavy test among its twelve measured entries.

### The 13 unhit assertions

Source: cov/report/asserts.txt, rows under the two gated scopes with zero real successes. The gate row counts
166 of 179; I parsed 180 gated rows and 14 zero-success rows, one of which is a repeated instance name, so the
set below is the 13 the gate counts plus that duplicate. They fall into four causes, and only one is a
stimulus gap:

CONFIGURATION, not stimulus (5): the dummy-instruction LFSR assertions NextStateCheck_A, NoLockups_A,
  LfsrLockupCheck_A and MaximalLengthCheck1_A under if_stage_i.gen_dummy_instr, plus
  g_cheriot_rf.g_dummy_r0.DummyWriteTargetsX0 in the register file. Dummy instruction insertion is never
  enabled in this round, so these have no attempts that could succeed.
CONFIGURATION, structurally absent (2): AlwaysInstrClearOnMispredict in the controller and NoMispredBranch in
  the IF stage. The DUT is built with BranchPredictor=0 (GEN_CONFIG_BANNER in every run log), so a mispredict
  cannot occur and these two cannot be hit by any stimulus at this configuration.
PROBE, off by ruling (1): if_stage_i.gen_b8_probe_i.sva_b8_dummy_in_expansion. LOG-067 keeps the B8 probe knob
  off in every measured run, so this is unhit by design and must not be counted as a gap.
GENUINE GAPS (5): IbexPipelineFlushOnChangingDebugMode and PipeEmptyOnIrq in the controller, and
  CheriotRaddrAMSBClear, CheriotRaddrBMSBClear and CheriotWaddrMSBClear in the register file. The first two
  are the debug-mode and interrupt paths the round never drove; the three CHERIoT ones need capability
  register addressing this round never produced.

## 3. Functional gaps

Source: cov/report/groups.txt, all 26 covergroups. Ten are at or above 80 and one is the ledger. The nine real
gaps, with a cause class for each:

| covergroup | covered/expected | score | cause class |
|---|---|---|---|
| gen_wit_cycle_clause_cg | 0/220 | 0.00 | LEDGER, not coverage: excluded from the score by SV name |
| gen_ic_ecc_cg | 1/40 | 2.50 | knob off: no round-1 entry sets the ECC rate knob |
| gen_rst_boot_cg | 11/44 | 25.00 | stimulus gap: one boot shape, no reset variation |
| gen_sec_ctrl_inputs_cg | 17/51 | 33.33 | stimulus gap: security inputs driven at one value |
| gen_div_timing_cg | 44/122 | 36.07 | stimulus gap: needs DIT on and fetch-stall shapes |
| gen_mul_timing_cg | 33/80 | 41.25 | stimulus gap: needs writeback-busy shapes |
| gen_cmp_zcmp_pushpop_cg | 204/291 | 70.10 | stimulus gap: rlist x spimm product under-swept |
| gen_isa_jump_cg | 75/103 | 72.82 | stimulus gap: jalr imm x target-align product |
| gen_isa_branch_cg | 153/208 | 73.56 | stimulus gap: compressed branch forms never emitted |

THE LARGEST FUNCTIONAL GAP IS STRUCTURAL AND IS NOT IN THIS TABLE. 182 covergroups named in the plan are not
rendered in gen_fcov_groups.svh at this commit, carrying 758 declarations that had to leave the manifests
before the round could run (LOG-090, LOG-091). Nothing in the 26 above measures them, and no amount of
stimulus reaches a covergroup that does not exist. That is the single biggest lever on functional coverage and
it is TB work, not test work.

THE 41 RE-SCOPED BINS remain uncovered by anything in the round. Of the 66 bins the second re-scope removed,
25 are hit somewhere in the merged run and 41 are not; the split is measured in the round record against this
run's own merged report. They are excluded from every per-run expectation, so no check will ever report them:
they are only visible here and in the round record.

## 4. Ranked gap list

Ranked by expected gain against the gated row, with the owner and whether round 2 can reach it. Gain is the
missed-object count where I have it and a qualitative estimate where I do not; I have not modelled how many of
each module's misses a given test would actually reach, and I say so rather than publish a fabricated delta.

| # | gap | expected gain | owner | reachable in round 2 |
|---|---|---|---|---|
| 1 | 182 unbuilt covergroups, 758 declarations | caps the whole functional axis | tb-infra | partly: each one built is measurable at once |
| 2 | ibex_pmp: no PMP test can be MEASURED yet, see below | 1815 missed objects | tb-infra then test-writer | NO, blocked by P-07 |
| 3 | ibex_cheriot_ex: MOSTLY OUT OF SCOPE, see Section 5 | 2211 missed, most carved out | rtl-arch (ruled) | n/a |
| 4 | controller FSM 5/26: no irq/debug/exception test | 21 of 86 FSM, plus controller line/branch | test-writer | yes: an irq and a debug entry |
| 5 | LSU FSM 6/22 | 16 FSM objects | test-writer | yes: error-response and misaligned shapes |
| 6 | gen_ic_ecc_cg 1/40: the ECC knob is never set | 39 bins | runtime + test-writer | yes, with the LOG-077 alert checker on |
| 7 | gen_div_timing_cg 44/122 and gen_mul_timing_cg 33/80 | 125 bins | test-writer | yes: DIT and writeback-busy shapes |
| 8 | op x register-relationship product, 12 pack + 5 same-register bins | 17 bins | test-writer (generator) | yes: table entry and sweep are one change |
| 9 | compressed-branch and successor sequencing | 55 in isa_branch, 17 in cmp_zca | test-writer (generator) | yes |
| 10 | the 3 CHERIoT register-file assertions | 3 assertions | test-writer | no: needs capability addressing |

## 4b. The plan-credit gap, which no coverage percentage shows

The Critic's round verdict measured gen_round_credit.py against the round manifest: 66 of 185 hosted plan
items credited, with 50 unhit, 18 not fired and 51 unverified, and PMP at 31 of 31. That is a different
question from the percentages above and a harsher one: it asks how much of the PLAN this round exercised, not
how much of the RTL the stimulus touched. A reader who sees line at 83.83 and stops has not seen that under
two fifths of the hosted plan items are credited.

THE REGENERATION IS MINE AND IT IS A GATE, not a chore. Section 10 of the round-1 request makes the credit
report, the promotion table and the covergroup set regenerated at the round's commit part of acceptance; the
tools are mine; and it has not been done. The Critic's round verdict,
dv/auto_dv/evidence/gen_critic_round1_record.md at 8c83b3a, is REQUEST-CHANGES on 4a00702..de1ccf3 confined to
exactly that acceptance (CR-40 M-1), with the DV Lead named as owner. It closes when the regeneration lands at
the round's commit and a recorded re-review passes, and it is the first item I take up when the pause lifts.

TWO FIGURES FROM THE CRITIC'S PROBE bound that work and are theirs rather than mine: the promotion table at 20
entries, and the covergroup set at 25 covergroups, 2864 bins and 22 manifests regenerated at the round's
commit. I re-derive both when I run the regeneration, and the round record carries mine at that point.

## 5. What these numbers do NOT mean

PASS 14 HAS LANDED AND SECTION 1 CARRIES ITS ROW. This merge ran with no exclusion file, so the MEASURED gated
row counts every unreachable-by-construction object against the score and is a floor rather than an
assessment; the adjusted row in Section 1 is what the same merge reads with pass 14's file. Two things about
it change this document's own gap list. The largest single block of the 1424 entries, 531 of them or 37 per
cent, is the CHERIoT out-of-scope carve-out under the owner ruling, so most of ibex_cheriot_ex's 2211 missed
objects are RULED OUT OF SCOPE rather than untested and item 3 above is struck as a stimulus target. The next
tier is guard-proven dead lines, decoder 150, if_stage 85, load_store_unit 59, controller 44, cs_registers 37,
compressed_decoder 33, id_stage 11, core 2, register_file_ff 2, dead from the build configuration rather than
from missing stimulus. AND AN ENTRY COUNT IS NOT A COVERAGE IMPACT: rtl-arch's own join says 105 entries are
no-ops and 84 effective, so quoting 1424 as impact would overstate it by an order of magnitude.

ITEM 2 OF THE RANKED LIST IS BLOCKED BY THE POLICY THIS ROUND IS BUILT ON, and it would be the easiest thing
in this document to misread as a quick win. Not one gen_pmp covergroup is rendered in gen_fcov_groups.svh: the
count is zero. All three PMP entries, gen_test_pmp_csr_warl, gen_test_pmp_mseccfg and gen_test_pmp_lock, read
measured false with a null manifest reference, because every bin their items own sits on a covergroup that
does not exist. Under P-07 a measured entry on smoke or targeted must carry a manifest, a manifest may not
declare a bin of a covergroup that does not exist, and an entry that can declare nothing cannot be measured at
all. So ibex_pmp's 1815 missed objects are NOT reachable by simply measuring the entries that exist: a gen_pmp
covergroup has to be built, or those items re-planned onto built ones, before any PMP test can be measured.
That makes item 2 tb-infra's before it is the Test Writer's, and it is the same structural gap as the 182
unbuilt covergroups rather than a separate one.

THREE OF THE 13 UNHIT ASSERTIONS AND TWO CONFIGURATION CLASSES CANNOT BE FIXED BY STIMULUS at this build: the
mispredict pair is structurally absent with BranchPredictor=0, the dummy-instruction set needs the feature
enabled, and the B8 probe is off by ruling. Counting them as gaps would put five items on a backlog that no
test can close.

THE GROUP CELL IS DISPUTED, as Section 1 says, and the round record does not claim the group gate passed. Any
round-over-round group delta computed before rt39 lands would compare two different quantities.

THE PERCENTAGES ARE OVER 36 MEASURED RUNS of 12 entries at 3 seeds. Seven entries and 17 runs of the round
contribute no measured coverage by design, and the check tier's 84 entries were not selected at all, so this
is not a measurement of everything the testbench can do.

RUNTIME-2'S TABLES HAVE LANDED, committed at 702d3ba as dv/auto_dv/evidence/gen_round_0_coverage_tables.md
(e63e10a93cf1, 244 lines), carrying the cuts this file summarises: a per-module AND a per-family toggle view,
every unhit FSM transition named, the 13 unhit assertions by full path, and the zero-hit coverpoints of every
covergroup below 80. Their self-check is that the 102 gated instance rows sum to the gate row on all six
metrics; note the table PRINTS the top 40 of those 102, which its caption states, so the sum is a claim about
the extraction rather than about the printed rows. I re-derived the same partition independently from
cov/report/modlist.txt for the module ranking above and for the FSM column, where the five modules sum to
38/86 exactly, which agrees with their tables and the record.

