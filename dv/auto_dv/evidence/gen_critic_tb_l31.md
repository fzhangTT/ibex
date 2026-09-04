# Critic verdict: the range df28129..d732ad9 as one (tb-infra landing 31 7b18ac7, tb-infra landing31b 98edaad, RTL/Arch ruling record d732ad9), reviewed as tb_l31

Scope (the Orchestrator's): three working commits judged together: landing 31 (ten files: the irq_entry end-of-run rule replaced by a drain, the run-time
cap gen_irq_drain_cap_cycles with two yaml constants, the retained log gen_fu_l31_irq_drain.log with its manifest row, the two records, the MUT-NT2 catch
now failing with the in-run wording), landing31b (one row: the CM204-Low-3 figure corrected for CM206-Low-1) and rtl-arch's ruling record
gen_rvfi_irq_valid_exclusive_ruling.md (149 lines: the sva_rvfi_irq_valid_exclusive firing ruled legitimate DUT behaviour, the property to change, 36
firings re-derived, the wave owed). The commits c3c6fa6, e67045d and 0f2d1a3 in the range are review and Critic artifacts committed as written. Not in the
range: the DV Lead's v4r and v4s, Runtime's rt35 (tb_l30b is the separate re-review of the CR-30 lift on v4r).

Artifacts reviewed (committed blobs at d732ad9; sha256 first 16 hex):

- dv/auto_dv/env/gen_checkers_pkg.sv  2f2e2631bec35554
- dv/auto_dv/env/gen_env_pkg.sv  919c8cf874cbb673
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  66ccc391f04516de
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l31_irq_drain.log  1d1f7fee75185e53
- dv/auto_dv/evidence/gen_tdd_step2b.md  fd70c27b1d10a9fe
- dv/auto_dv/gen_tb/gen_knobs.py  4dace7013106817d
- dv/auto_dv/isa/gen_isa_shim_map.h  8289df5298815200
- dv/auto_dv/mutations/gen_mut_step2b.md  976cf827485a7a34
- dv/auto_dv/tb/gen_tb_knobs.yaml  805ec6eeeded3932
- dv/auto_dv/tb/gen_tb_pkg.sv  3f4919ad62777bdd
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  ac2afa2307a7908e
- dv/auto_dv/evidence/gen_rvfi_irq_valid_exclusive_ruling.md  e82cd5e38475b425

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_critic_tb_l30.md (3a3d311dea84cfde);
the mutation-proof standard in force since landing 12 (an identity block names the baseline the diff applied to, the mutated hash, the applied diff and
the root's identity, and a retained header names the build it claims); the evidence rule (a claimed run maps to a retained committed artifact or counts
as nothing); the rule that an RTL behaviour is stated with every gating term quoted.
Method: detached git worktree of 7b18ac7 for landing 31 (the landing gate: both codegen --check up to date, three UTs PASS, CONST, RED-CHECK, validate 27
OK, TBMAN 3464 rows 0 bad, build identity c1189fdc15a85844 over 117 sources recomputed by the committed tool and the gate; TB-source recipe
d34daf56c8871437 over 75 files); the retained log read whole; the records diffed; the checker, base test, package and yaml diffs read; the cap formula
re-derived from the code and the regime windows; the MUT-NT2 baseline hash reproduced from the gen_tb_top.sv blob; the digest function read
(gen_flow_util.py:92-104). Landing31b's row checked against my own tb_l29 census and the probe's print format. The ruling record read whole at d732ad9
with every RTL citation resolved in rtl/ibex_core.sv, rtl/ibex_wb_stage.sv and ibex_configs.yaml (RTL unchanged, git status clean), its Section 8
figures re-derived by python over the two reproducer runs it names, which live in tb-infra's gitignored working directory
dv/auto_dv/work/tb-infra/wit/l32a (read on disk, not retained: Section 3), and its working copy diffed against the committed one (the provenance
paragraph only). EXPOSURE: the Orchestrator's messages, TASKS rows 1184-1185 and 1236-1244 (rtl-arch's assignment, ruling and commit rows), tb-infra's
work note gen_irq_eor_finding.md, and the two run directories above. No subagent used. Section 6 reconciles with this range's cross-model review; its
artifact was the wrapper's empty placeholder while Sections 1-5 were written.

CRITIC VERDICT: REQUEST-CHANGES. One Medium on landing 31: the MUT-NT2 re-run's identity block retains no applied diff, so its mutated hash and root digest
cannot be reproduced, and the ablation root's identity line names the mutant's digest while claiming the same sources as the landing build, which the
contents-only digest makes impossible; the control's build is therefore not evidenced by identity. Two Lows on landing 31 (a counter printed but no longer
incremented; a drain of exactly the bound against a strictly-greater in-run rule) and one Low on the ruling record (its Section 8 rests on runs that are
not retained). Everything else verifies: the TDD pair, the cap and its derivation, the blast radius, landing31b's correction, and the ruling itself, whose
every RTL citation resolves and whose figures reproduce to the cycle. Landing31b carries no finding; the ruling stands on its RTL sections.

## 1. What was verified

| commit | item | evidence (re-derived by me) |
|---|---|---|
| 7b18ac7 (tb-infra landing 31) | the TDD pair: seed 7 of lockstep_irq_storm_nmi FAILs on the pre-fix build b48479a3bc6f1d9f with the end-of-run error (raised at cycle 17359, order 3184, finish_req at 17361, report at 173655 ns = cycle 17365.5 at 10 ns), and PASSes on the landing build with "drain: 17 records in 120 cycles", never taken 0, open after the drain 0 | the log's :13-30; b48479a3bc6f1d9f is the committed digest before the landing (unchanged since 1bbf0a0), c1189fdc15a85844 recomputed at 7b18ac7 |
| 7b18ac7 | the cap: max(i_gnt + i_rvalid, d_gnt + d_rvalid) + GEN_IRQ_DRAIN_RECORD_OVERHEAD_CYCLES 2, times GEN_IRQ_ENTRY_BOUND_RECORDS 17, plus GEN_IRQ_DRAIN_MARGIN_CYCLES 40 = (3+4+2)*17+40 = 193 at the short-regime maxima (gnt [1,3], rvalid [2,4]) from the effective agent cfg after the plusarg overrides and lower clamps | gen_tb_pkg.sv function below GEN_KNOBS_END; gen_tb_knobs.yaml:177-178; gen_agents_pkg.sv:108-136; the two constants rendered (codegen up to date) |
| 7b18ac7 | blast radius: six rows PASS, every drain "17 records in N cycles" with N = 110, 32, 115, 117, 34, 157, all below 193, so every drain ended on records | the log's :57-64 |
| 7b18ac7 | the MUT-NT2 re-run: the same fault (gen_tb_top.sv, irq_external withheld once 3572 records retired) now caught by the in-run rule with "not taken within 17 records (now order 3718)" on the same line 00004, raise cycle 22574 and order 3700 as the original catch (gen_mut_step2b.md:174, "last order 3710"); baseline 736a8d8099339024 | the log's :42-54; the baseline equals the gen_tb_top.sv blob at 7b18ac7; the mutated hash and the root digest not reproducible: Section 3 M-1 |
| 7b18ac7 | the checker change: report_phase no longer errors; a still-held expectation is counted eor_open and printed "open after the drain"; the base test holds its objection after finish_req until 17 records or the cap; the residual (a line starved while the core retires nothing) stated OWED in the log, gen_tdd_step2b.md and gen_mut_step2b.md | gen_checkers_pkg.sv and gen_env_pkg.sv diffs; the log's section 5 |
| 98edaad (tb-infra landing31b) | the CM204-Low-3 row now says 154 at c3bd17a and 2402704 and 158 at 332aa17, with the cause: a two-space parse dropped the one row whose detail overflows its column, the guard row cr_window | my tb_l29 census (154/154/158); the probe prints the detail as %-46s and cr_window's detail (49 characters) overflows it, so a two-space split drops that row |
| d732ad9 (rtl-arch ruling record) | every RTL citation resolves to the quoted text: RVFI_STAGES = WritebackStage ? 2 : 1 (:1660) with WritebackStage 1 (ibex_configs.yaml:49); the arrays at :1662 and :1763; rvfi_valid from [RVFI_STAGES-1] (:1775) and rvfi_ext_irq_valid from [RVFI_STAGES] (:1837), the rest of the ext group at :1829-1836; the comment at :2130-2133 and :2188-2191; the OR-guarded hops (:2134, :2140, :2192, :2198); the retirement side (:1864-1868, :1890, :2069) with no interrupt term; the pulse (:1965-1970) and its terms (:1928-1932); the entry enable (:1992) and capture (:2002); ready_wb_o and instr_done_wb_o (rtl/ibex_wb_stage.sv:185, :200) | each line read; one term the record leaves unquoted traced by me: rvfi_id_done = instr_id_done or (rvfi_flush_next and id_exception_o and not wb_exception_o) (:1851-1853), no interrupt term either, so the "nothing couples the two" statement holds with every term |
| d732ad9 | the ruling: exclusivity is not an invariant, the flag advances on an OR with itself, the pulse tolerates a writeback completing in its own cycle, so the property changes and the stimulus stays; not a bug candidate, no B8 row; the recommended replacement property with its two cautions and the trust-triad condition; the wave confirmation owed with what it needs | Sections 2-7 read against the RTL above; gen_b8_rtl_facts.md untouched in the range; the property at gen_protocol_props.sv:299 unchanged in the range and the cover at :304 present |
| d732ad9 | Section 8: 11 and 25 firings (36), each run's UVM error count equal to its firing count, the eleven window cycles 361 ... 18076, the first at 3655000 ps with the offending term (!rvfi_valid), the mapping (cycle + 4.5) x 10000 ps on all eleven, build cc08c9729184adc5, seed 1, the knob values, the image 156 words crc32 0x8e882c5b, the six files per run directory, no dump anywhere under the build | python over both sim.log files: 11 / 25 UVM_ERROR lines all of this property, the cycle list equal, the mapping holding on all 36, Offending '(!rvfi_valid)' 11 / 25 times, verdict.txt ERROR 11 / 25, run headers and image line as stated, find over the build directory 0 wave files. The runs are not retained: Section 3 L-3 |

## 2. Rows

- CM206-Low-1 (tb-infra's, relayed from the tb_l29 artifact): answered by landing31b as stated and verified. TASKS row 1184 (the checker defect found by the
  24-seed sweep): closed by landing 31's TDD pair on the retained seed-7 evidence. CR-30 rows: not in this range (v4r). CR-29: none were open.

## 3. Findings

- M-1 (landing 31; gen_fu_l31_irq_drain.log:36-46 and gen_mut_step2b.md:286): the mutation-proof's identity evidence is defective twice. (a) The re-run's
  identity block names a baseline (736a8d8099339024, which reproduces from the gen_tb_top.sv blob) and a mutated hash (84524c5d5e90222c) but no applied
  diff: none in the log, none retained as a mutant diff (the landing-12 and landing-13 mutants retain gen_fu_l12_MUTCNT_mutant.diff and
  gen_fu_l13_NT3b_mutant.diff), and the original MUT-NT2 artefacts (build 4e4a02897de732d3, a gen_tb_top.sv two landings older) cannot supply it; so
  neither the mutated hash nor the root digest 3d8e81ccd20737c7 can be reproduced. (b) The ablation root (:36-37) claims "root's own identity:
  3d8e81ccd20737c7 before the fault was applied (the same sources as the landing build)", while the header (:9) defines 3d8e81ccd20737c7 as the landing
  sources WITH the fault and filelist_digest hashes listed contents only (gen_flow_util.py:92-104), so the same sources give c1189fdc15a85844; the two lines
  cannot both be right, and the control's build is not evidenced by identity as written. The catch line and the ablation PASS are not in doubt; their
  identity chain is. Required: retain the applied diff as gen_fu_l31_MUTNT2_mutant.diff with a manifest row and show the diff on the baseline gives the
  mutated hash and the root digest; state the ablation build's measured identity in a corrigendum row of gen_mut_step2b.md (the log's bytes never move),
  with how the line was got wrong.
- L-1 (landing 31; gen_checkers_pkg.sv:33, :271): never_taken is declared and printed ("never taken=%0d") but no longer incremented anywhere, the
  report_phase site now incrementing eor_open, so "never taken=0" in every summary from this landing on is structural, not measured, and a reader of the
  log's :28 takes it for a result. Remove it from the summary or say in the record that it is retired.
- L-2 (landing 31; gen_env_pkg.sv:375 against gen_checkers_pkg.sv:127): the drain waits for exactly GEN_IRQ_ENTRY_BOUND_RECORDS records while the in-run
  rule judges only expectations with st.order - order_at > GEN_IRQ_ENTRY_BOUND_RECORDS, so an expectation raised at the last stimulus record reaches age
  17 at most and is never judged, ending as "open after the drain" rather than as a verdict. The seed-7 case (age 19) is unaffected; one more record (the
  bound plus one) closes the gap, or the record states why the boundary case is left to the residual.
- L-3 (rtl-arch ruling record, Section 8 and :6-7): the section is titled "What the retained runs do confirm" and its figures are read from
  dv/auto_dv/work/tb-infra/wit/l32a/irq_nmi_window and irq_nmi_late, a gitignored working directory; nothing of either run is under gen_tdd_logs at
  d732ad9 (0 files match), so under the evidence rule the 36 firings, the cycle list and the offending term rest on nothing committed. The ruling itself
  (Sections 1-5) rests on the RTL and is unaffected. Required: retain the two runs' firing lines, verdict files and run headers as one excerpt log under
  gen_tdd_logs with a manifest row (their hashes checked against the record), or reword "retained" to "working-tree" and mark the section's figures
  unretained.

### Informational

- I-1: the six blast-radius rows carry no per-row identity or seed; the header's "landing build" covers them by context only.
- I-2: gen_tdd_step2b.md's "one seed in 24 swept" refers to the local sweep of TASKS row 1184, not to a retained artefact, and claims no retention.
- I-3: the ruling record discloses what it did not verify (:148-149, the arm of the NMI pulse in tb-infra's tree), states the wave as owed with what a
  confirmation needs, and marks its recommended property as needing its own red and mutation before adoption; all three are the honest form. The knob
  it names, gen_knob_nmi_after_irq_delay, is not in the committed gen_tb_knobs.yaml at d732ad9 (tb-infra's in-flight NMI-route knob), which the record's
  provenance paragraph covers.
- I-4: the record's Section 5 timing (pulse condition at C, the port at C+4, rvfi_valid at C+4 iff rvfi_wb_done at C+3) follows from the cited registers;
  which alignment each firing took is left open in Section 7 and does not bear on the ruling.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S6 trust triad: landing 31's red-green pair conforms (the false failure reproduced on the
prior build, gone on the landing build, both identities named); its mutation-proof is NON-CONFORMING at the identity block (M-1: no applied diff, the
ablation's identity self-contradictory). S4 honesty: the drain's residual stated as owed (conforming); a dead counter printed as a figure (L-1,
non-conforming at one field); the ruling record's disclosures exemplary, its "retained" for gitignored runs not (L-3). S2 realistic stimulus: the ruling
keeps the stimulus unconstrained and moves the property, the right direction. One-line verdict: FAIL on S6 for landing 31's identity evidence; PASS
elsewhere.

## 5. Verdict

CRITIC VERDICT: REQUEST-CHANGES on the range df28129..d732ad9, for M-1 (landing 31). Rows CR-31: M-1, L-1, L-2 (tb-infra), L-3 (rtl-arch). What lifts it:
tb-infra's landing-31 correction (the retained diff with its reproduction, the ablation identity corrigendum, the counter, the drain length or its stated
reason) re-reviewed as tb_l31b, and rtl-arch's retention or rewording of Section 8 in the same or a following touch; nothing built on landing 31's
mutation-proof proceeds before then. Landing31b (98edaad) carries no finding. The ruling record's Sections 1-7 stand as written and may be relied on now:
the property is to change and the stimulus is not to be constrained.

## 6. Reconciliation with the range's cross-model review

Artifact: dv/auto_dv/reviews/2026-09-04-claude-diff-df281290-d732ad9f.md (972e7ac093d41ec5, 50 lines), read after Sections 1-5 were written (it was the wrapper's
empty placeholder while they were). Reviewer: Claude Fable 5.1 as the fallback (codex spend cap), fresh session on a detached read-only checkout of
d732ad9. Its verdict: APPROVE-WITH-CHANGES with one Medium, four Lows and one Info, the assertion-integrity rubric FAIL and the other four PASS. Mine:
REQUEST-CHANGES. Both carry a Medium on landing 31, on different items; the findings overlap on four of six and the two verdicts differ on severity and on
the gate, not on any shared fact.

Shared recomputations, each re-run by me and equal to the artifact's: the identities (c1189fdc15a85844 at 7b18ac7 and at HEAD, b48479a3bc6f1d9f at df28129,
by the committed tool); the cap 193 from the short windows [1,3] and [2,4] (gen_tb_pkg.sv:207-213, gen_tb_knobs.yaml:79-85) and the effective cfg maxima
through the plusarg overrides and lower clamps (gen_agents_pkg.sv:107-136), read by the drain at gen_env_pkg.sv:373-374; the manifest row 5698 /
e3dedb80ad15dfa5ebf3f783d489ff3f; the baseline 736a8d8099339024 as the gen_tb_top.sv blob; codegen up to date for the two constants; the census 154 at
c3bd17a and 2402704, 158 at 332aa17; every RTL citation of the ruling record and the property text at :299 with the cover at :304; no wave under the
build; the local compile figure d34daf56c8871437 at 7b18ac7 (my recipe gives the same), which 3d8e81ccd20737c7 also fails to match.

The artifact's findings against mine:

- Its Medium (gen_env_pkg.sv:375, the drain length equals the bound while the in-run judge needs age greater than the bound, so the boundary case the
  retired error did flag is now unjudged): the same finding as my L-2, which I rated Low. Its severity is adopted: the removed rule flagged an
  expectation at age 17 and the replacement counts it open without an error, the disclosed residual names the retirement-stall case and not this
  boundary, and the commit message's "the in-run bound is the single judge" holds only for expectations at least one record older than the last stimulus
  record; that is a checker weakened at its boundary without saying so, the class the assertion-integrity rubric names. The id stays L-2 so the
  correction already prepared against the CR-31 ids keeps its references; it is read as Medium from here on and is already in Section 5's lift. The fix
  it names (bound plus one, or judging at the drain's end, then the TDD pair and MUT-NT2 re-run and the resolution stated in the log and
  gen_tdd_step2b.md) is the right one.
- Its Low (gen_checkers_pkg.sv:270, never_taken printed but never incremented): my L-1, agreement, including that the log and gen_tdd_step2b.md cite
  "never taken 0" as evidence.
- Its Low (gen_fu_l31_irq_drain.log:9, the identity 3d8e81ccd20737c7 labelled three ways, no anchor, the applied diff not retained so 84524c5d5e90222c
  cannot be checked): my M-1. I keep Medium: the identity chain is the trust-triad evidence of the mutation-proof, and a control whose identity line
  cannot be right as written is not evidenced by identity. The artifact adds two facts I verified: line 43's "root's own identity: 3d8e81ccd20737c7" for the
  mutant run agrees with the header, so :37 is the odd line, and the digest matches neither the landing build's filelist digest nor its local compile
  figure. Its fix (print the local compile figure, say which key 3d8e81ccd20737c7 is and at which state, retain the diff and cite it from
  gen_mut_step2b.md:286) and mine (the diff with its reproduction, the ablation identity by corrigendum row) are the same work.
- Its Low (gen_component_api_irq_checker.md:20 and :121 still document the retired end-of-run rule as a uvm_error at report; the file is untouched in
  the range): a miss of tb_l31, adopted and verified (both lines read at d732ad9, 0 touches in the range). The class my rules name: a component's API
  document is a peer record of the checker and is re-read when the checker's rule changes; I read the checker, the base test and the two evidence records
  and not the API document.
- Its Low (gen_rvfi_irq_valid_exclusive_ruling.md:125, Section 8 rests on gitignored runs and on a knob absent from the committed tree, and :11 cites
  rtl/ibex_configs.yaml where the file is ibex_configs.yaml at the root): the runs are my L-3 and the knob's absence my I-3; the path error is a miss of
  tb_l31, adopted and verified (git ls-tree shows the file at the root only; the record's :11 says rtl/). I resolved the citation by reading the root file
  at :49 and did not compare the path the record wrote, the class my rules name (a cited path is re-derived as written, not as understood).
- Its Info (no unit test exercises gen_irq_drain_cap_cycles although its placement below the generated region is justified as unit-testable): adopted as
  an informational miss, verified (no file under tb/unit or gen_tb names the function).

On the verdicts: the artifact's APPROVE-WITH-CHANGES carries a Medium it calls "a one-record boundary gap with a stated, checkable fix" and a rubric FAIL;
under the team's gating a Medium that is neither closed nor disclosed as owed is a REQUEST-CHANGES, which is what Section 5 records, and the Orchestrator
arbitrates the gate. Nothing in Sections 1-5 is contradicted by the artifact; no corrigendum. Two misses and one severity adopted, all riding the same
landing-31 correction (tb-infra) and the record's next touch (rtl-arch); the CM208 rows carry them, no CR-31 row is added.
