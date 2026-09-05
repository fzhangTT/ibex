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
