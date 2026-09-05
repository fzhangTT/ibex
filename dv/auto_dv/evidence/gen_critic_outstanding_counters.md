# Critic verdict: the "outstanding counters" group, 69eb33f..c045115 (tb-infra-2 landing 53)

Artifacts (the one commit of the range, c045115; sha256 first 16 hex of each blob at that commit):
- dv/auto_dv/tb/gen_protocol_props.sv a04f215611bd2736
- dv/auto_dv/env/gen_fcov_pkg.sv 3d9d64d8ba64bd24
- dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l53_outstanding_saturate.log 63c2b4b4c39eb85e
- dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l52_vacuity_corrigendum.log 0a877576e7339496
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md 2e5509f0a0acbeb7

Date: 2026-09-05 (UTC). Role: Critic. Method: the diff read from the committed blobs; every line number below is
"file:line at <commit>" read with git show; the landing's counter claims re-derived on three compiles of detached
worktrees at c045115 (clean 665d62e97890e7ca; c045115 plus my own one-shot spurious-response mutation in the bus
driver 5258f1e950485a12; the same mutated tree with only the four counter lines put back to their 69eb33f form
66bd39ffc6caa2c9), run on the retained lines and storm smokes and on a riscv-dv gen_rand_smoke program with data
traffic; the design obligations checked against rtl/ and doc/; the six gates run. Exposure: the cross-model
artifact rev61 was not read before Sections 1-5 were written; its commit subject (APPROVE-WITH-CHANGES, c884742)
was seen in git log while checking HEAD, its content only at Section 6. Logs and scripts: dv/auto_dv/work/critic/l53/
(ab_results.txt, compile_identities.txt, mutation_spurious_rvalid.diff, wrap_revert.diff, gates_c045115.log).

CRITIC VERDICT: REQUEST-CHANGES (confined to M-1: the same wrapping counter one file over, gen_bus_if.sv, whose
self-check the landing leaves manufacturing the flood it set out to remove; everything else in the landing is
approved as stated below and stands when M-1 lands).

## 1. What the landing claims and how it was checked

The commit c045115 (a) makes both outstanding counters of gen_protocol_props.sv saturate at zero (:133-136 at
c045115, replacing :128-129 at 69eb33f), (b) relabels the three properties whose only bound term is a TB counter
from DUT to TB with the design obligation stated in each comment (:192, :216, :227 at c045115), (c) gates the
mret classifier's interrupt-entry pre-state on a non-debug entry (gen_fcov_pkg.sv:453 at c045115), (d) retains
the A/B log and (e) a corrigendum to the landing-52 log, with (f) two manifest rows. Checked: the code by reading
and by my own A/B (Section 2); the obligations against the RTL and the memory-interface docs (Section 3); the
classifier term against my earlier reachability proof and against re-measured figures (Section 4); the records
line by line (Section 4); the gates and smokes on my clean compile (Section 4).

Gates on the c045115 worktree: gen_fcov_codegen --check up to date, gen_knobs_codegen --check up to date,
GEN_UT_FCOV_CODEGEN / GEN_UT_KNOBS_CODEGEN / GEN_UT_HANDLES PASS (0 failures), gen_unbuilt_mark_check PASS: six,
as the message says. Clean compile rc=0, identity 665d62e97890e7ca. The four retained smokes on it (the l47
recipes, images rebuilt earlier under critic_irq1b): storm, lines, dbgstorm, fetchen all PASS with 0 UVM_ERROR,
0 GEN_FCOV_REF and 0 counter-bound fires, matching the log's line 76.

## 2. The counter fix: derivation, the masking question, and the A/B re-run three ways

The saturating update (:133-136) takes the counter to zero exactly when rvalid is high and counter + grant is zero,
i.e. rvalid with counter == 0 and no grant this cycle. That cycle is inside the failure set of the response
obligation (sva_ibus_rvalid_outstanding / sva_dbus_rvalid_outstanding: rvalid |-> counter > 0, :191 / :215), so
every saturation event is a reported error and "saturating loses no report" holds by construction; the A/B below
confirms it on three fixtures. Afterwards the counter reads 0 with nothing truly outstanding (the spurious
response answered no request): the model is re-synchronised.

The wrapping update does the opposite. 0 - 1 reads 4294967295, and from then on the counter reads one below the truth
modulo 2^32 for the rest of the run: 4294967295 whenever the bus is idle (the bound floods and the data no-third-request
rule accuses the core on every request issued from idle) and 0 whenever one request is truly outstanding (every
legitimate response then fires the response obligation, a further spurious response in an idle gap passes it
unreported, an over-subscription of exactly one reads as legal, and the exact-value covers can never match: == 8
needs nine in flight, == 2 needs three, == 1 under a request needs two, which the DUT never does). rtl-arch's 280
bound fires are one idle gap of that run; my random arm below shows the whole shape (1489 bound fires and 218
accusations in a 2103-cycle run, 71 response-obligation fires of which 70 are the legitimate responses).

Can saturating at zero mask a genuine over-subscription? No. It acts only at the low side, only in a cycle the
response obligation already reports, and it leaves the counter at the true value afterwards; it removes the one
masking mode the wrapping design had (the permanent one-below reading). The residual both designs share: a
spurious response arriving while one real request is outstanding decrements to 0 without saturating and without a
report; the report comes when the real response arrives and finds the counter at 0, one event late, after which
the saturating counter is right again and the wrapping one is one below for good.

MEASURED. My mutation MUT-SPURIOUSRVALID (dv/auto_dv/env/gen_agents_pkg.sv, retained as
mutation_spurious_rvalid.diff): the data-bus driver asserts rvalid for one cycle at driver cycle 400 when its
pending queue is empty and the core has no request up, with a valid zero codeword as data. The same bytes in both
mutated trees (cmp identical); the wrapping tree differs from the saturating one only in :133-136 put back to the
69eb33f two lines (wrap_revert.diff). The properties module drives nothing, so the DUT sees the same stimulus in
both arms and the fire counts are comparable. The test's own compare passed in every arm (cocotb 1 passed); the
FAIL verdicts are the collected property errors alone.

| fixture (SEED 1) | arm | rvalid_outstanding | outstanding_max | no_third_request | u_dbus_if sva_rvalid_legal | u_dbus_if cov_rvalid_legal |
|---|---|---|---|---|---|---|
| lines (gen_ut_irq, P_IRQ; no data response before the end) | saturating | 1 | 0 | 0 | 1 | 0 |
| lines | wrapping | 1 | 2742 (cycles 401..3142, the end) | 0 | 1 | 0 |
| storm (gen_ut_lockstep, P_NMI storm; one data response, at cycle 17350) | saturating | 1 | 0 | 0 | 2 | (not reported) |
| storm | wrapping | 2 | 17071 | 3 | 2 | (not reported) |
| random (gen_rand_smoke seed 1, 29039 words, crc32 341ab2e5, tohost 80002940; 70 data responses) | clean c045115 | 0 | 0 | 0 | 0 | 70 |
| random | saturating | 1 | 0 | 0 | 71 | 0 |
| random | wrapping | 71 | 1489 | 218 | 71 | 0 |

The landing's shape reproduces (lines: the response obligation equal in both arms, the bound flood to zero), and
the two consequences its fixture could not show are measured here: the no-third-request ACCUSATION (3 and 218
fires with the wrapped counter, 0 saturating) and the response obligation's inversion after the wrap (the wrap arm's
extra fires are the legitimate responses: at cycle 17350 in the storm arm, 70 of 71 in the random arm). The five
exact-value covers read 0 matches in every arm, including the clean run: none of these programs performs a split
access or reaches depth 2 or 8, so the cover-death consequence stays unmeasured here as in the log.

## 3. The relabelling: the obligations against the RTL and the docs

- Data bus, at most two in flight, "the two halves of one split" (:216): the LSU issues the second word of a
  misaligned access from WAIT_RVALID_MIS with the first response still pending (rtl/ibex_load_store_unit.sv:503-531),
  and WAIT_RVALID_MIS_GNTS_DONE holds both outstanding with data_req_o low (:546-561); the split condition is
  :403-405 as the parameter comment cites. The capability path (CTX_WAIT_GNT1 / GNT2 / WAIT_RESP, :565-603) is the
  RTL's other two-deep case and is unreachable here: gen_dut_top.sv:206 ties cheriot_enable_i to IbexMuBiOff. So
  the comment is exact for this build.
- Data bus, never a request with two outstanding (:227): with the writeback stage, a memory instruction issues only
  while no load or store is outstanding in WB (rtl/ibex_id_stage.sv:1015-1019, data_req_allowed =
  ~outstanding_memory_access, released in the cycle lsu_resp_valid arrives), so a new request can meet a counter of
  1 (the final response of the previous access decrements at the end of that cycle) but never 2. Correct.
- Instruction bus, at most eight in flight (:192): NUM_FB 4 (rtl/ibex_icache.sv:72) times IC_LINE_BEATS 2
  (rtl/ibex_pkg.sv:406), the icache's fill buffers each making a line's beats of requests; this is the ICache
  build (round 0's sva_ibus_depth_max_seen matched 1878 times, gen_round_0/gen_asserts.txt), so the bound is
  realisable. With the prefetch buffer alone it would be NUM_REQS 2 (rtl/ibex_prefetch_buffer.sv:44); eight is a
  correct upper bound either way.
- The docs (doc/03_reference/load_store_unit.rst:95) allow multiple granted requests outstanding, answered in
  order, without a bound; the bounds are RTL facts, which is what "the DUT obligation it observes" says.
- After the change no DUT-annotated assertion reads either counter (grep over the blob: none). The label is a
  trailing comment with no machine consumer (no tool or flow file names gen_protocol_props); rtl-arch's committed
  reading still quotes ":185 // DUT (bound 8)" (gen_ibus_props_irq_signature_reading.md:24) as the pre-landing
  text it read, which is history, and the register row is the DV Lead's as the log's line 78 says.
- The relabelling is right for the reason the log gives: a property whose bound term is the TB's own model fires
  on a wrong model with no DUT behaviour (Section 2's wrap arm is that: 1489 bound fires and 218 accusations on a
  core that never broke either rule).

## 4. The classifier term, the corrigendum, the records

- gen_fcov_pkg.sv:453 at c045115: the interrupt-entry override now needs !st.debug_mode, the guard the register
  file's clear sits under (ibex_cs_registers.sv:918). Unreachable difference, as its comment says and as I proved
  for the mret group (rvfi_intr only via EXC_PC_IRQ, only from IRQ_TAKEN, which needs ~debug_mode_q). Measured
  unchanged on my clean build: mret_mpie1_pending 173 / 6 / 39 / 15 on storm / lines / dbgstorm / fetchen,
  mret_mie1_mpie1_pending and mret_mpie0_pending 0 in all four, the figures of my mret record at 9a42c17.
- The vacuity corrigendum quotes the l52 log's lines 53-56 verbatim (compared against the blob at 9c7f8f6, line
  breaks included); the l52 log's md5 is unchanged at fe418c61e39bf272f2814ec581a82794 at c045115. The correction
  itself (a check that cannot fire under a regime is vacuous there, not less sensitive) is right and is the DV
  Lead's ruling in its words. Two precision points are Lows below (L-4, L-5).
- The l53 log's citations hold: :122 and :128-129 at 69eb33f for the declaration and the wrapping update; :220
  for the third DUT-annotated reader; the ten readers at 69eb33f are exactly :184 :185 :208 :209 :220 (assertions)
  and :189 :215 :216 :225 :226 (covers). "No measured round ever wrapped a counter": gen_round_0/gen_asserts.txt
  shows 0 failures for both bounds and the no-third-request rule over 5408327 attempts across the 53 runs; the
  rebaseline directory retains no assertion file, so "zero in the rebaseline" is not checkable from the tree.
- The commit message's "280 in one wave run" is rtl-arch's table row for seed 165313640; "5285 error lines" and
  "the same three times" are the landing's fixture figures (mine differ because my injection cycle and fixtures
  differ; the shape is the same).
- gen_manifest.md at c045115: 3511 rows; the two new rows carry 6458 bytes / 7fdaebaceb6f7ea840a944a759cc6894 and
  2917 bytes / ae804c11036468525f4ebc4dac8de6de, equal to the blobs. Both logs ASCII.
- For the record (an Orchestrator note on the previous group, carried here because gen_critic_irq_checker_fix.md is
  committed): the knobs-codegen parser test rode in landing 52 without belonging to its feature group, because it
  was verified; the 9c7f8f6 commit message does not say so. Records-only.

## 5. Conformance, rows, verdict

Conformance (dv_principles.md): the counter change removes a TB model's self-inflicted false failures without
weakening any check (every saturation event is a reported failure, Section 2); the relabelling makes the
downstream reading "a failure here is a design bug" true for every DUT-labelled property; the log states what its
fixture did not show; the corrigendum leaves the corrected log's bytes untouched.

- M-1 (Medium; tb-infra-2). THE SAME COUNTER ONE FILE OVER. dv/auto_dv/tb/gen_bus_if.sv:31 at c045115 declares
  `int unsigned outstanding` and :38 updates it as `outstanding + ((req && gnt) ? 1 : 0) - (rvalid ? 1 : 0)`, the
  69eb33f expression; the interface is instantiated once per bus (u_ibus_if, u_dbus_if), and its readers are the
  stimulus-legality self-check sva_rvalid_legal (:47, a collected UVM error, the check the file's header says
  rtl-arch's T-022 evidence 5.2 relies on) and the cover cov_rvalid_legal (:51). It wrapped identically to the
  properties' counters before the landing (rtl-arch's two wave runs: 70199 sva_ibus_rvalid_outstanding fires beside
  the same count of sva_rvalid_legal in my irqchk record; round 0: equal attempt counts, 468337 / 97518) and it still
  wraps after it. MEASURED on the saturating build with the same one-shot: random program, 71 sva_rvalid_legal fires
  where the properties' response obligation fires once, cov_rvalid_legal 0 matches against 70 on the clean build
  (the interface's cover died for the run); storm program, a second fire at cycle 17350 on the tohost store's
  legitimate response. Reasoned, not measured: while the interface counter reads 4294967295, a further spurious
  response passes the self-check silently. The commit message ("The two outstanding-request counters were
  unsigned ... Both counters now saturate") and the log's sweep ("TEN readers of these two counters", :15-18) state
  the population as two counters and ten readers; the tree has a third declaration with two more readers, same
  expression, same consequence class, undisclosed. Fix: the same saturation at gen_bus_if.sv:38 with its comment
  (:29-30), and an A/B whose fixture has data traffic after the injection (the random-program shape above),
  reporting sva_rvalid_legal and cov_rvalid_legal beside the properties' rows.
- L-1 (Low, records; tb-infra-2). The log names one build ("THE ONE BUILD EVERY FIGURE COMES FROM", out_l53b) and
  then two ("Two builds, identical but for the counter"); the wrapping build has no identity, out directory or
  source statement, and the mutation's text, injection cycle and fixture are not retained, so the A/B cannot be
  reproduced from the log's own text (the shape rev59 found in the l52 log and my L-1 there). rev61 grades this Medium
  under dv_principles.md rule 2's mutation record; that rule binds a NEW checker's proof, and this A/B is a fix's evidence
  with no new checker, so I hold it at Low against the record standard the team set with the l52 log (mutation text,
  md5 before and after); the corrigendum both reviews ask for is the same.
- L-2 (Low, records). The log's A/B fixture has no data request after the injection ("the program makes no data
  request during the wrapped window", :40-41), so "the response obligation fires THE SAME THREE TIMES in both" is a
  property of that fixture: with traffic after the injection the wrapping arm fires it on every legitimate response
  (71 against 1). The equality is the right claim for saturation (no real event lost) but the log presents it as
  the measured difference between the designs, while the actual behavioural difference, re-synchronisation, is
  unshown; the log discloses the fixture's limits for the covers and the accusation but not for this row.
- L-3 (Low, records; tb-infra-2; adopted from rev61 Low 1, and my own A/B shares the limit). Both the log's A/B and
  mine inject on the data bus only; the instruction-bus saturation (:133-134) is verified by inspection of identical
  arithmetic, never by a fire. The log lists two unmeasured consequences and should list this third one.
- L-4 (Low, records; tb-infra-2 with the DV Lead). The corrigendum names the vacuous regime "a heavy storm"
  (:12-13) and gives the condition as its consequence ("no unmasked stretch reaches the bound at all"). The regime
  is the condition, not the storm: the retained storm smoke is a heavy storm by the tree's own knob and the fixed
  checker caught a withheld line twelve times on it (gen_critic_irq_checker_fix.md Section 3). State the regime as
  "fewer than 18 consecutive takeable records between masked records for the rest of the test" and name the
  retained smoke as outside it.
- L-5 (Low, records; DV Lead). The corrigendum's "condition (a) is met at 9c7f8f6" and "added to the irq entry's
  promotion conditions" (:30) refer to a list with no committed home: the tree at c045115 mentions the irq entry's
  promotion conditions only in gen_chkfix_reruns/gen_index.md:5, and the plan carries none. The corrigendum says
  the DV Lead gives the second expectation a plan-side home; the conditions list needs one too, or the sentence
  cites nothing.

- L-6 (Low, code comment; tb-infra-2; adopted from rev61 Low 3). gen_fcov_pkg.sv:450-452 at c045115 restates the
  !debug_mode_i guard the comment two lines above already gives and attributes the reachability proof to "The Critic",
  a process reference in code rather than the design intent. One line suffices: the RTL guard is carried so the
  classifier does not rest on a reachability argument.

Verdict: CRITIC VERDICT: REQUEST-CHANGES on 69eb33f..c045115, confined to M-1. Approved as they stand: the
saturating update and its no-masking property (derived and measured three ways), the three relabels with their
obligations (checked against the RTL), the classifier's debug term (unreachable, figures unchanged), the vacuity
corrigendum's verbatim quotation and its ruling, the manifest rows, the six gates and the four smokes. L-1..L-6
owed as disclosed. Re-review scope on the M-1 fix: the gen_bus_if.sv diff, its A/B with data traffic after the
injection, and the corrected population sentences.

## 6. Reconciliation with the cross-model artifact rev61

Read after Sections 1-5 were written: dv/auto_dv/reviews/2026-09-05-claude-diff-69eb33fa-c0451154.md at c884742
(claude CLI fallback under owner ruling A-001, codex over its spend cap; APPROVE-WITH-CHANGES; one Major, one
Medium, three Lows).

- Its Major is my M-1, found independently: the untouched wrapping counter at gen_bus_if.sv:38 with sva_rvalid_legal
  and cov_rvalid_legal as readers, the same fix asked for. Two corrections to its description, from measurement.
  rev61 says the interface's self-check "passes every subsequent unsolicited response for the rest of the run and
  its cover reads true vacuously"; the counter reads one below the truth after the wrap, so the self-check is blind
  only while the bus is idle and FIRES on every legitimate response arriving with one outstanding (71 fires on the
  fixed build's random arm, 70 of them legitimate), and the cover does not read true, it dies (0 matches against 70 on
  the clean build). The same correction applies to rev61's "Better than the log states" paragraph: under the wrap the
  response obligation is not blind after its first fire, it inverts (71 fires in my wrapping random arm, one real).
- On the verdict we differ, and the difference is the measurement. rev61 holds the defect "contained" because the
  properties' own obligation now catches the spurious response, and approves with changes. The purpose the landing
  states is that one bad response must not manufacture a flood of collected errors; on the fixed tree one bad
  response still manufactures 71 collected UVM errors and kills a cover, through the counter the landing's population
  sentences say does not exist. An undisclosed population claim the tree contradicts is REQUEST-CHANGES under my
  rules, and the fix is small; the re-review scope is stated in Section 5.
- Its Medium is my L-1 with the added point that the one-shot's "3 fires" cannot be reconciled without the injection's
  shape; adopted into L-1's wording as the corrigendum content, held at Low for the reason given there. The point
  itself is right: my one-cycle injection fires the response obligation once per arm, so the log's three fires mean
  three cycles of rvalid or three injections, which the log should say.
- Its Low 1 (the ibus arm unmeasured) adopted as L-3, with my own A/B named as sharing the limit.
- Its Low 2 (the :216 gloss "the two halves of one split" narrower than the mechanism) NOT adopted. The two other
  routes it names do not reach two outstanding: after WAIT_RVALID_MIS_GNTS_DONE returns to IDLE the second half alone
  is outstanding (counter 1), and the next memory instruction cannot issue until that response arrives, because
  data_req_allowed = ~outstanding_memory_access releases only in the lsu_resp_valid cycle (rtl/ibex_id_stage.sv:1015-1019
  with the WB stage's outstanding_load_wb / outstanding_store_wb, rtl/ibex_wb_stage.sv:193-196); the "pipelined
  unrelated request ... with one outstanding" of the file's own comment (:219-220) is a request issued in the previous
  access's response cycle, which leaves the counter at 1 (+1 grant, -1 response). The split is the only two-deep case
  in this build (Section 3), so the gloss is exact.
- Its Low 3 (the comment at gen_fcov_pkg.sv:450-452 restating the guard and naming "The Critic") adopted as L-6.
- Its verified list matches Sections 2-4 on every shared point (the max(0, ...) reading of the update, the same-cycle
  grant case, the readers after the change, the two design bounds against the LSU and the icache, the classifier
  term's unreachability, the verbatim quotation, the manifest rows, the resolved old line numbers, the mutation
  absent from the tree). rev61 did not run the code; every measured figure in this file is mine.

## Corrigendum to Section 5 M-1 (appended after the HOLD of 2026-09-05; Sections 1-6 unchanged)

M-1's evidence sentence reads "rtl-arch's two wave runs: 70199 sva_ibus_rvalid_outstanding fires beside the same count of
sva_rvalid_legal in my irqchk record". That mixes two runs of seed 1207954461: 70199 is rtl-arch's count on the 4017573 wave
run (gen_ibus_props_irq_signature_reading.md:51-54, where sva_rvalid_legal is not tabulated), and the equal pair
70208 = 70208 (sva_rvalid_legal beside sva_ibus_rvalid_outstanding) is my own run on the 9c7f8f6 build
(gen_critic_irq_checker_fix.md Section 3 and its corrigendum). The inference the sentence carries, that the interface's
counter and the properties' counter are the same computation, stands on my run's equal pair and on round 0's equal
attempt counts; the wave run's 70199 is not part of it. Nothing else in M-1 moves; the 71 fires and the dead cover were
measured on my own builds (Section 2's table).

## 7. Recorded re-verdict on 69eb33f..8ee50ea, the outstanding-counters group (landings 53 and 55; HOLD sent to the Orchestrator first; Sections 1-6 and the corrigendum unchanged)

Artifacts at 8ee50ea (sha256 first 16 hex): dv/auto_dv/tb/gen_bus_if.sv f9f602e73787bd96; dv/auto_dv/tb/gen_protocol_props.sv
b75e705d84f13b23; dv/auto_dv/env/gen_fcov_pkg.sv a78b6d8b986c3b19; dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l55_bus_if_saturate.log
15fa378b6168086e; dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md b3d1ce2025bce3ad (3514 rows; the l55 row 13529 bytes /
828722b01dfb20087bc3ce3e3150fa68 equals the blob; ASCII). Method: the diff read from the blobs; the fix measured by me on the fixture
that found the defect (a build of 8ee50ea with my one-shot spurious-response mutation, identity d0198afb576c3e3f, the random program
of Section 2); the log's four build identities recomputed offline from archives of committed trees with gen_tb_local.sh's own
recipe; the :216 comment checked against the RTL and the build's parameters. Exposure: the Orchestrator's range message named
rev66's two Mediums and three of its Lows before this section was written; rev66's content is read only in 7.4. Logs:
dv/auto_dv/work/critic/l53/ (README.txt, preread_l55.txt, runs/ab_rand2_sat55).

### 7.1 M-1, the interface counter: closed

gen_bus_if.sv:38-40 at 8ee50ea saturates with the same expression as the properties' counters (rvalid with nothing counted and no
grant leaves zero). Measured by me on the fixture of Section 2 that found the defect (one spurious data response at driver cycle
400, then 70 legitimate responses): sva_rvalid_legal fires once where it fired 71 times at c045115, cov_rvalid_legal matches 70 of
70 where it matched none, the properties' response obligation fires once, the bounds and the no-third-request rule zero. The
landing's own two reds read and consistent: four consecutive injections caught 4 of 4 by the saturating interface against 1 of 4 by
the wrapping one with the c045115 properties counter as the oracle reporting 4 in both; one early injection on the storm smoke
producing the wrapping interface's second, false fire at cycle 17508 against one real event in both. The population sentences are
corrected in the l53 corrigendum ("twelve readers, in two files"; the sweep scoped to one file), and its line-count correction of
the l53 A/B (response obligation 1 not 3, bound 2642 not 5285) agrees with my Section 2 figures (1 and 2742 on my injection
cycle). The gen_fcov_pkg.sv comment is folded to one line without the process reference (my L-6). M-1 CLOSED.

### 7.2 Two things the landing gets wrong

- M-2 (Medium, records and identity; tb-infra-2). The l55 log's header says its four builds come from "an archive of HEAD and
  nothing else", W unchanged and S "with this landing's two tb files copied over it", and names them by identity: W clean
  665d62e97890e7ca, S clean 4ebaa0bc49091b37. Recomputed by me with the runner's own recipe (the sorted sha256 list over
  env, tb, isa and gen_tb, then its digest) on archives of committed trees: a pure c045115 tree gives 665d62e97890e7ca, so W is
  c045115's tree and "HEAD" means c045115, the commit before landing 54, not the HEAD the landing was handed against; and NO
  assembly of committed blobs gives S: c045115 plus the landing's two tb files 83b4e1c21e7e215e, plus its three changed files
  1f0ef6bfcfd6c7b6, plus gen_bus_if.sv alone 8cfd1adbd78ef5dc, plus gen_bus_if.sv and gen_fcov_pkg.sv 3181568c3e0ac532;
  b9e5fad plus the two tb files 35046bc4793eb3a3, plus the three 2f874eb63deeb6bb (which is the pure 8ee50ea tree). The S root
  therefore carried at least one tb file that is not a committed blob, and the log's evidence certifies sources the tree does
  not hold; the same holds for the two l53 A/B builds the corrigendum now names (cb66d1b569cba4fb, 0d548320b34bf9d9), whose
  mutation text is not retained. My run on the committed sources supplies the fix's measurement, so the code is not in doubt;
  the record is. Fix: retain the S root's two tb file digests beside the identities and say how they differ from the committed
  blobs, or re-run the two reds on a root assembled from committed blobs; and name the archive's commit by sha.
- M-3 (Medium, a design-obligation comment stating an RTL route that does not exist; tb-infra-2). gen_protocol_props.sv:216 at
  8ee50ea now reads "never more than 2 data beats in flight, reached either by the two halves of one split or by a
  boundary-shaped access with a pipelined unrelated request behind it, as :219-220 records". The second route cannot reach
  two. This build has WritebackStage=1 (every retained run banner reads WritebackStage=1; gen_dut_top's default of 0 is
  overridden by the build), so a new memory instruction issues only when data_req_allowed = ~outstanding_memory_access
  (rtl/ibex_id_stage.sv:1015-1019), which releases in the cycle lsu_resp_valid arrives: the unrelated request is granted no
  earlier than the previous access's response cycle, and the counter reads 1 + 1 - 1 = 1 in that cycle. The comment it cites,
  :219-220, says exactly that ("with one outstanding"). Only the split, whose second half is issued while the first is
  unanswered (WAIT_RVALID_MIS), reaches two. My Section 6 rejected this route when rev61 offered it as its Low 2, with these
  terms; the landing adopted the row into the obligation comment without a measurement or an RTL citation. Fix: restore the
  split-only wording, or write that the :219-220 case leaves one outstanding and is not a route to two.

### 7.3 The Lows of Section 5 and two new ones

- L-1 answered: the corrigendum names both l53 A/B builds, the fixture and the plusargs (with the identity limit of M-2).
- L-2 not answered: the corrigendum restates "the response obligation fires the SAME number of times in both builds" as the
  deciding claim; with data traffic after the injection the wrapping arm fires it more, not the same (Section 2: 71 against
  1; 2 against 1 on the storm), those extra fires being false. The claim to make is "saturation loses no real report", which
  the four-injection red now proves; the equality sentence should go. Owed.
- L-3 answered: the log says the ibus arm is verified by inspection.
- L-4 and L-5 (the vacuity regime's name; the promotion conditions' home) belong to the l52 vacuity corrigendum and the DV Lead
  and are untouched by this landing; still owed there, and my irq re-verdict (gen_critic_irq_checker_fix.md Section 7, M-3)
  now measures that the storm-shape vacuity persists, which is the regime statement those rows asked for.
- L-6 answered: the comment at gen_fcov_pkg.sv:450-451 is one line and names no reviewer.
- L-7 (Low, records). The log's "archive of HEAD" is c045115's tree by identity while the landing commits on top of b9e5fad;
  name the base by sha. (Part of M-2's fix.)
- L-8 (Low, records). The l55 log calls the c045115 properties counter "fixed and reviewed at c045115" as its oracle; reviewed
  is right, but the identity of the oracle in the S build is the same unresolved root as M-2, so the oracle's provenance
  inherits the gap until M-2 closes.

### 7.4 Reconciliation with the cross-model artifact rev66

Read after 7.1-7.3 were written: dv/auto_dv/reviews/2026-09-05-claude-diff-69eb33fa-8ee50eac.md at a516fef (claude CLI
fallback under A-001; APPROVE-WITH-CHANGES; two Mediums, seven Lows). Its verified list agrees with 7.1 on the saturation
arithmetic, the twelve-reader sweep (it adds the driver's pend.size() counters and the Python export as non-wrapping, which I
had not listed), the reverted mutant, the reds' arithmetic, the corrigendum's figures and the manifest row; it recomputed the W
identity as I did and got the same value.

- Its Medium 1 (the :216 second route) is my M-3, found independently with the same RTL terms and the same fix. One correction to
  its premise: it says this build has WritebackStage=0 from gen_dut_top.sv:51's default; the build overrides it and every
  retained run banner reads WritebackStage=1, so the governing line is ibex_id_stage.sv:1015-1019 (the branch it also cites),
  not :1146. The conclusion holds on either branch.
- Its Medium 2 (the S identity) is my M-2; its recomputed values (83b4e1c21e7e215e, 35046bc4793eb3a3, 861209d7f0fd1ed1) equal
  mine, and I add four further candidates that also miss (1f0ef6bfcfd6c7b6, 8cfd1adbd78ef5dc, 3181568c3e0ac532,
  2f874eb63deeb6bb).
- Its Low 1 (a grant and a spurious response in one cycle with nothing outstanding leave the count at 0 with one truly in flight,
  a bounded residual the l53 log's "exactly" sentence does not admit; the decrement form outstanding + gnt - (rvalid &&
  outstanding > 0) reads the truth on every path) is the residual my Section 2 named as shared by both designs; its expression
  is a real improvement and is adopted as L-9 (Low, code; tb-infra-2), with the l53 sentence to be qualified.
- Its Low 2 (cov_rvalid_legal measured in neither l55 table, though my re-review scope asked for it) is right and adopted as L-10
  (Low, records); my run supplies 0 against 70 at c045115 and 70 at 8ee50ea.
- Its Low 3 (the three mutants described in prose only) is my L-1 of Section 5 seen again; adopted as L-11 (Low, records) with
  my grading reason as the acceptable decline.
- Its Low 4 (the counting rule's "+1" is UVM's per-id report-count line, not the message-less tally) is verified on the retained log rev66 cites, which prints the per-id table under 'Report counts by id'; adopted as
  L-12 (Low, records wording).
- Its Low 5 is my L-2, still owed (7.3).
- Its Low 6 (the storm red's "no event at all" and "the whole rest of the run is traffic" overstate: the 17508 fire is the
  fixture's one legitimate data response, reported falsely) is right and adopted as L-13 (Low, records).
- Its Low 7 (my L-4 undispositioned; L-5's home is the form's promotion-conditions table at 242a64b, uncited) agrees with 7.3;
  the L-5 home is right and I cite it there.
- On the verdict we agree on both Mediums and differ on the form as before: rev66 approves with changes; under my rules an
  identity that does not resolve and an obligation comment contradicting the RTL are REQUEST-CHANGES until the companion lands.

### 7.5 Verdict

CRITIC VERDICT: REQUEST-CHANGES on 69eb33f..8ee50ea, confined to M-2 and M-3. M-1 is CLOSED (the fix measured by me on the
committed sources: 71 fires to 1, a dead cover to 70 of 70) and the saturation of both counters is approved; the l53 corrigendum's
corrections are right. What remains is a record that cannot be tied to the tree (M-2) and one obligation comment that names a
route the RTL does not permit (M-3), both small to fix. L-2, L-4, L-5, L-7, L-8 and, from 7.4, L-9..L-13 owed as disclosed.

## 8. Confirmation on 69eb33f..ac2d306 (landing 58, counters fix 3): M-3 closed, M-2 standing; REQUEST-CHANGES confined to the identity row (appended under a HOLD, 2026-09-05T14:39:19Z; Sections 1-7 unchanged)

Artifacts at ac2d306: gen_bus_if.sv, gen_protocol_props.sv, gen_fu_l58_decrement_saturate.log (md5 f4d9c925 per its manifest row,
10952 bytes), gen_manifest.md; rev76 (dv/auto_dv/reviews/2026-09-05-claude-diff-c0451154-ac2d3062.md at d8bed4e, 5c419f806485c0e9).
Method: two out-of-tree archives of 4bd933f, E unchanged and F with ac2d306's two tb files laid over it (their blobs checked),
each clean and with my own MUT-SPURIOUSWINDOW (a response asserted with the pending queue empty on every driver cycle 300 to 399,
both agents; script retained under my scratch and its outputs under dv/auto_dv/work/critic/l53/), compiled with the local flow;
gen_ut_irq on the irq1 program (crc32 8e882c5b, 156 words) at seed 1; the re-dump run re-read; the identity method checked
(the run header's build_sources_sha256 is sha256 of the build's sources_sha256.txt); rev76 read after the findings were fixed
(l53/draft_s8_fix3_prerev76.txt, with post-read notes appended and dated). Exposure: the Orchestrator's messages relayed one fact
(the two counters as one offset mechanism) and, after my draft, tb-infra-2's explanation that the log's two digests are the mutant
builds' headers. Logs: l53/fix3_prechecks.txt, l53/fix3_red_rerun.txt.

- Row 1, the decrement form: the diff replaces the sum test with a decrement qualified on the pre-update count in gen_bus_if.sv and
  on both counters in gen_protocol_props.sv; the four traced cases follow from the expression, and the one case that differs from
  the sum form is a grant with a spurious response on an empty count, which now reads 1.
- THE RED REPRODUCES PER PROPERTY EXACTLY. E (sum form): sva_rvalid_legal 129, sva_ibus_rvalid_outstanding 29,
  sva_dbus_rvalid_outstanding 100; F (decrement): 110, 10, 100. The interface check splits by its own message text into dbus 100
  and ibus 29 on E and dbus 100 and ibus 10 on F, so the nineteen removed interface fires are the ibus obligation's nineteen, which
  the log asserts from equal differences and my runs derive. Both clean builds PASS with zero real errors. The DUT's own assertion
  NoMemResponseWithoutPendingAccess (rtl/ibex_core.sv:1390) fires 100 times in both mutant runs. L-6 (Low, records; tb-infra-2):
  the totals read 2684 and 2646 here against the log's 2640 and 2602, both 44 higher in the lockstep and crash_dump ids while the
  38 and every per-property figure are exact; the log quotes no run header or summary line, so the constant cannot be traced.
- Row 2, one defect: on the 165313640 re-dump the eight sva_ibus_rvalid_outstanding cycles [18345, 18363, 18408, 18422, 18457,
  18979, 19032, 19108] equal the eight sva_rvalid_legal cycles, the eight sva_ibus_outstanding_max floods start one cycle after
  each and run 9, 40, 9, 27, 24, 48, 71 and 52 cycles as listed, and the last real error is inside the eighth flood. I-1 (Info):
  the list names no bus (the run's ids are the IBUS counter's) and "every real UVM_ERROR" is the five bus-protocol ids only (627
  real errors in the run, the isa_*, crash_dump and MEM_UNMAPPED ids interleaved from 18368 omitted).
- Row 3, M-3 CLOSED: the :218 annotation now says the build elaborates WritebackStage=1 from -pvalue on the compile line, names
  gen_dut_top.sv:51 as the default, and cites the branch taken (gen_stall_mem, data_req_allowed = ~outstanding_memory_access at
  rtl/ibex_id_stage.sv:1019), consistent with the round-0 build command and banner Section 7 read; the split is the only route to
  two.
- Row 4, M-2 STANDING. The log says the roots are archives of 4bd933f with E's identity 1c4f99930208695f and F's dd9f4cd5ddd825de.
  An archive of 4bd933f built by the same flow has identity b7067f660ed88693 (my E; my 38b729a build before it reads the same,
  there being no TB file change between 38b729a and 4bd933f) and 4bd933f plus ac2d306's two tb files has edb6e789fe40b5c5 (my F;
  the TB diff 4bd933f..ac2d306 is exactly those two files). The log's two identities therefore name no archive of 4bd933f, which is
  the fault rev66's second Medium and my M-2 were about, repeated with a base sha that does not verify. The relayed explanation,
  that the two digests are the mutant roots' headers, is stated here as relayed: with the window mutation retained only as prose it
  cannot be tested from the tree (my own mutant identities, bdf3ac45167f0232 and ea3dc3e72a29d5ad, come from a different injection
  text and prove nothing about theirs). The red's substance stands on my builds; the record's basis does not. M-2 closes when a
  companion gives the clean roots' identities, the two copied files' digests against the ac2d306 blobs, and the mutation as a
  retained diff with the wrapper digest it produces, and states which digests the table used. The landing-55 S build
  (4ebaa0bc49091b37) stays unresolved with it.
- Row 5, the landing-53 figures: out_l53wrapmut/r and out_l53satmut/r are named by relative path only and I could not locate them
  (not under ibex_dv_out, ibex_dv_probe, the clone's work directories or the project scratch), so the corrected integers 1 and 2642
  are not re-derived here; Section 7 measured the response obligation 71 to 1 on my own builds. The counting rule's doubling holds on
  my mutant run (mentions 200, 58 and 260 against firings 100, 29 and 129); my sim.log carries no Report Summary, so the per-id and
  tally halves are not re-derived. L-7 (Low, records; tb-infra-2): give the retained runs' absolute roots or quote their lines.
- The remaining rows: my L-2 is answered (the equal-fire equality was a quiet-fixture artefact; this red, 100 injected and 100
  reported by both forms, is the general evidence). L-4 and L-5 are NOT dispositioned by landing 55's log or the l56 companion as
  the log says: my rows at 7.4 place them with the l52 vacuity corrigendum and the DV Lead, where they stay owed. L-8 (Low, records;
  tb-infra-2): the log's mutant diff is prose, as the three SPURIOUSRVALID mutants before it; the l57 fixtures it points at are the
  irq mutants, not these.

Reconciliation with rev76 (read after the rows above were fixed):
- Its Medium is my M-2 as it stands, with the same two recomputed identities (it validated the recipe on c045115 as Section 7 had);
  it adds that the log does not say whether the digests are clean or mutant roots, retains no copied-file digest, and leaves the S
  build unresolved. Agreed on every part.
- Its Low on the counting-rule root is my L-7 (same search, same absence). Its Low on the red's unquoted figures: my per-bus split
  derives the nineteen it says are asserted. Its Low on Row 2's overstatement is my I-1 widened, verified on my own breakdown. Its
  Low on the mutants-as-prose misattribution is my L-8, verified against landing 57's retained files. Its Low on L-4 and L-5 is
  verified against my own rows and adopted. Its Info on the annotation's line numbers is fair and not a row of mine.
- Verdict after reconciliation: unchanged. Both agree there is no Major and that M-3 closes.

CRITIC VERDICT: REQUEST-CHANGES on 69eb33f..ac2d306, confined to M-2 (the build identities that name no archive of 4bd933f, and
the mutation retained as prose). M-3 is CLOSED; M-1 stayed closed from Section 7; the red's per-property claims reproduce to the
digit; L-6, L-7 and L-8 and I-1 are owed with M-2's companion, L-4 and L-5 with the DV Lead. The group closes when that companion
lands and its digests verify.
