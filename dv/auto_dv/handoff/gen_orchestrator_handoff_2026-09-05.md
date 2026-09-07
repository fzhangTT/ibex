# Committed copy of the Orchestrator handoff of 2026-09-05

Verbatim copy (made 2026-09-07T18:17:38Z, owner request of 2026-09-07) of the gitignored working file
dv/auto_dv/work/orchestrator/HANDOFF_2026-09-05.md, so the handoff survives a re-clone. The six role STATUS files it
names are committed beside it as gen_status_<role>_2026-09-05.md (their HANDOVER block is at the top of each). Every
path of the form dv/auto_dv/work/... exists only in the originating clone (/localdev/fzhang/ws/ibex-challenge);
dv/auto_dv/gen_INVENTORY.md maps the tree for a reader without that clone. Nothing below the rule is edited.

---

# ORCHESTRATOR HANDOFF - written 2026-09-05T19:10:46Z (date -u) - Ibex auto-DV cleanroom, branch cleanroom/run-a

Read this, then dv/auto_dv/work/orchestrator/TASKS.md (the authoritative event log, newest at the bottom), then the six
role STATUS files (dv/auto_dv/work/{critic,dv-lead,rtl-arch,runtime,tb-infra,test-writer}/STATUS.md; the HANDOVER block at
the top of each is that role's own handoff; the active instances were critic, dv-lead, rtl-arch, runtime-2, tb-infra-2,
test-writer-2). The owner's directives live in dv/auto_dv/docs/gen_intervention_log.md (LOG-093 .. LOG-100).

## 1. Where things stand
- HEAD at handoff: see git log; the last content commits are LOG-100 (f2a2a5b) and ci/env.sh's fail-loud export.
  Every hand of 2026-09-05 is committed; the tree is clean except the Critic's gen_critic_form_v3.md if its Section 13
  was mid-append when the stop came (see its STATUS; the text is in dv/auto_dv/work/critic/form3/s13_ready.txt).
- The team was PAUSED at clean points on the owner's directive (18:52Z) and then STOPPED for this handoff (19:05Z).
  A new team may be created at resume; the respawn briefs used today are under chains/respawn/.
- Owner decisions of 19:05Z (LOG-100): (1) the functional-coverage GATE is the bin fraction with the witness ledger out of
  both terms (round 1: 3477/4048 = 85.89, first condition passes; traceability confirmation is a separate finding); the
  plan's per-family equal-weight group score is REPORTED BESIDE it as the secondary metric (option C). (2) ci/env.sh derives
  LIBPYTHON_LOC from the clone venv and fails loud (done, committed, tested; LOG-100 records the contract exception).

## 2. First resume items, in order
1. Apply decision 1 as ONE joint group (DV Lead + runtime-2), one cross-model review, one Critic verdict:
   - runtime-2: gen_cov_report gate cell = bin fraction from ONE filtered covergroup list (ledger out of both terms), the
     percent with its denominator and a scope string in the summary header and the dashboard; remove the content-dependent
     fallback (gen_cov_report.py:138 at the time of LOG-097 addendum 3); a per-family group-score TOOL (spec-derived and
     adopted totals separately) reported beside the gate; the stored round-1 figure restated 81.47 -> 85.89 in the index
     entry beside the stored value (collected files byte-identical, LOG-092).
   - DV Lead: gen_fcov_plan.md criterion text at the four sites its STATUS handover names (the gate sentence, its
     restatement, the completeness-measure section, the reporting clause; LOG-100 corrigendum) rewritten to LOG-100; the round-2
     request form's Section 11 acceptance; the round-1 record's group-gate cell ("not claimed") updated to cite LOG-100.
2. tb-infra-2: the bus-agent repair on the gated shape (grant = ready AND live request; rtl-arch Section 12 at d19e6bf
   cited by number), precondition met by the pair record 85b7bef, acceptance per seed in runtime-2's flow on
   gen_test_irq_basic 165313640 and 1207954461: zero grant-property firings; grant and retirement counts inside the
   committed agent's range from the pair record; lockstep and referee clean against the record's column. The mutation
   pair (gen_mut_phantomgrant*.diff at 36011ea) proves the GATE only. First action: one local run of gen_test_irq_basic at
   165313640 on the committed driver (rtl-arch measures 1 firing in the retained logs); if it reproduces, it is the fast
   red-to-green loop, not the acceptance. Retain run headers, summaries and logs under the site output root from the start
   (rev89's Low: scratchpad-only artifacts are unreadable from any checkout).
3. Round 2 dispatch after 1: the form's selector call restated at dispatch, the canary build, --base-seed 20260905,
   rtl-arch's F-1 exclusion chain at the announcement, the round record, its reviews, the analysis, then pause (LOG-097).
   The irq entry's promotion conditions (d) forty-seed sweep, (e) regime-independent end-of-test expectation,
   (f) the wedge (T3 narrowed, deep-shift case unreached) stay open; the DV Lead rules the entry's standing at dispatch.

## 3. Owed rows by role (details in TASKS.md and each STATUS)
- DV Lead: RECORD the fifth-case (LOG-030) fact-citation ruling in the tree (Section 0's fact case or the response record),
  since rev95 found it cited from nowhere; rev92's two Lows (Section 0's WHAT GOES must name task/work-package ids; gen_trace_check.py:12 docstring and
  :161 trailing comment still carry T-140, WP-8 at :111) + the Critic's L-14/L-15; T3's caveat and T10's cell from
  landing 63 (36011ea) with three qualifiers (arm B's precondition; arm A bounds protocol not data; the vectoring scope);
  the Critic's counters L-4/L-5 corrigenda rulings already sent to tb-infra-2; L-11 closed at e4aef00 (Critic 3990916).
- tb-infra-2: rev94's rows on landing 63 (three Mediums: Row 4's "modules that do not vector interrupts" is FALSE, gen_ut_irq
  boots a vector table and takes vectored entries, so the precondition is the falling-edge redirect alone; the run roots
  are dead scratch paths, retain the run headers, census/injection/firing lines and the 44 verdict lines under gen_tdd_logs
  with manifest rows from tb-infra/handoff/runs/; cite Section 11.3 and 12 at d19e6bf, the pair record at 85b7bef and the
  DV Lead's rulings by location; Lows: the depth bound measured only at the injection cycle, the mislabelled census comment;
  Info: no pre-execution plan review, say it ran under the register's T10 ruling) as one companion with rev89's rows as a corrigendum companion to the l62 log (the +1 irq_entry is the NMI-mode mirror's,
  DERIVED; the three-build measurement; both bases named; Section 12 not 12.1; my commit message a8792ce repeats the wrong
  cause); rev94's rows on landing 63 when it lands; the two gen_smoke_run.sh Critic labels and the four gen_dut_top.sv
  Q-002 header lines at those files' next touch; its side of the re-dump waveform release held for the 18333 window.
- runtime-2: a run-time check of the linked VPI library against the pinned venv (recorded in the build manifest today,
  read back by nothing: LOG-100 corrigendum); the routed comment-census lists were short (same broken shape), so each owner
  censuses its own directory with gen_comment_census.py --root <dir> (corrected figures in TASKS.md 19:1xZ; .sv not
  censused); rev95's rows on the census tool (Medium: the correction section's headline "the original 35 was the right line count"
  does not reproduce, 35 being the occurrence count at 555f17a after two sites were swept, so restate it against the tool's
  own output; Lows: a scope fixture (.tcl/.f, a parse refusal), Tcl's ';#' form, all dates per line, and the LOG-030 ruling
  cited from nowhere in the tree; Infos: expose --ext or drop the claim, reconcile the '.sh and .csv' line, say the moved
  cites follow the comment); the census self-test is now in rt34/wt_gate.sh (my file);
  the linked-VPI-library identity item; the harness end-of-run-line citation (the DV Lead ruled: the id stays on the
  decided clause); the wt_hygdbg worktree under the old scratchpad (remove with git worktree remove if still listed).
- test-writer-2: rev93's Info (the sweep-count row mixes two commits' counts: name the commit); sixteen census comment
  sites under dv/auto_dv/tests at their files' next touch; parked: mul_div landing after round 2, the third fixture wait,
  the five PMP bins on the DV Lead's ruling.
- rtl-arch: rev94 Low: three facts the l63 record attributes to it are not in the tree (the vector-table disassembly of
  0x80000350, the phase schedule moving at 70500 and 71500, the "two symptoms are one event" reading that its own Section
  11.9 frames as unseparated): land them in the signature record with the reconciliation, or the l63 companion marks them
  unrecorded. NOTE the Orchestrator relayed rtl-arch's conditional "if neither module vectors interrupts" as fact; it was
  false for gen_ut_irq. Three parked items (the README-delta heading literal "(CM-3 / Critic L-3)" at gen_excl_f1_pass.py:442 changes
  with the next README regeneration at the F-1 chain pass; the "(F-3 open)" narration at gen_excl_select.py:864 at that
  file's next touch; a one-line cross-reference from the B8 facts record to Section 12); its waveform side released in
  writing, effective when tb-infra-2 releases.
- Critic: form Section 13 on e4aef00..2f92709 (written; hand or in the tree); reconciliation lines for rev89 (9.3 on the
  counters record, owning that 9.2 read past the +1 attribution), rev94 and rev95 when they land.

## 4. Reviews in flight / to launch (fallback Claude reviewer; artifacts in dv/auto_dv/reviews/)
- rev94 (landing 63) and rev95 (the census tool) both landed and are committed (4cf619c and the commit after it); their
  rows are in section 3. No review is in flight at handoff.
- Committed today: rev75..rev93 (every group of the day reviewed; all APPROVE-WITH-CHANGES or APPROVE).

## 5. Mechanics (copied from the session scratchpad into dv/auto_dv/work/orchestrator/chains/)
- chains/rec/chain.sh <sha256-list> <msgfile> (records); chains/plan/chain.sh <list> with the message in
  plan/commit_msg.txt (plan/records; gate 2 re-renders 17 manifests expecting zero diffs, runs gen_section_check on the
  two template records and gen_register_cites.py); chains/irqfix/chain_fixes_only_sha.sh <list> with
  irqfix/commit_msg_fixes.txt (TB code, runs the smoke); chains/rt37/chain.sh <list> with rt37/commit_msg.txt (flow;
  calls rt30/wt_gate.sh and rt34/wt_gate.sh). The copies' S= lines point at this chains/ directory itself, so they run from
  here and write their logs and the team trash under it; point S= at a new session's scratchpad instead if preferred.
- OTHERRE in every chain lists other roles' files that may be dirty under HOLD; widen it when a HOLD arrives, not when a
  chain refuses (BOUNDARY BAD). Chains run serially; never commit a review artifact while a chain runs; read a chain's exit
  line in one turn and confirm the commit in the next; a confirmation never shares a response with the Bash that reads it.
- Review launcher: copy chains/rev56/launcher.sh with sed s/rev56/revNN/g and BASE=/HEAD_= filled; a focus.txt beside it
  (73 examples under chains/focus/); nohup bash launcher.sh > launcher_out.txt; artifact
  dv/auto_dv/reviews/2026-MM-DD-claude-diff-<base8>-<head8>.md; the review has a 3600 s timeout; a zero-byte artifact is
  a review in flight.
- Standing rules: fence (FENCE.md; never the sibling spike fork, tools/src, other branches/remotes/clones, network DV
  collateral, no listing of the shared /tmp); DV never modifies RTL; gen_ prefix, ASCII, intent-only comments (the
  code-comment rule now lives in gen_test_plan.md Section 0); A-002 no rm on variable paths (literal paths; the team
  trash under the scratchpad, purged after a 10-minute ctime settle); one committer; hands are one list with sha256
  first-12 verified on a detached archive of HEAD, frozen until confirmation; HOLD before the first edit of a committed
  file; WITHDRAW waits for acknowledgement and does not undo a commit it crosses; retained logs are never reopened
  (companions); STATUS stamps from date -u; the pre-hand evidence rule (a run that could have failed; template Section 22).

## 6. Held and released artefacts
- Re-dump waveforms of seeds 165313640 and 1207954461 (4017573): HELD by tb-infra-2 for the falling-edge redirect window
  (export cycle 18333); rtl-arch released its side in writing. runtime-2 must not reclaim.
- The agent-fix pair's regression logs (sim.log and stdout pairs, 4.3 GB): moved to the site trash path recorded in
  dv/auto_dv/evidence/gen_agentfix_pair/gen_move_record.md and gen_release_widened.md; reversible.
- Round-1 merged vdb and urg report: preserved under the site output root with a retention manifest (LOG-097).

## 7. Open owner items
- None blocking after LOG-100. The traceability-confirmation condition of the functional gate (a non-author reviewer
  confirms the mapping) has never been claimed and needs an owner-visible finding before the gate is called PASSED.
