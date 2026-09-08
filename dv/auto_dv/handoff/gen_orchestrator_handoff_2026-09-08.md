# Committed copy of the Orchestrator handoff of 2026-09-08

Verbatim copy (made 2026-09-08T04:46:27Z, owner directive LOG-104) of the gitignored working file
dv/auto_dv/work/orchestrator/HANDOFF_2026-09-08.md. The four role STATUS files it names are committed beside it as
gen_status_<role>_2026-09-08.md (their final handover block is at the top). Paths of the form dv/auto_dv/work/... exist only in
the originating clone (/localdev/fzhang/ws/ibex-challenge); dv/auto_dv/gen_INVENTORY.md maps the tree. Nothing below the rule
is edited.

---

# ORCHESTRATOR HANDOFF - written 2026-09-08T04:44:52Z (date -u) - Ibex auto-DV cleanroom, branch cleanroom/run-a

Read this, then dv/auto_dv/work/orchestrator/TASKS.md (the authoritative event log, newest at the bottom), then the four
role STATUS files (dv/auto_dv/work/{dv-lead,rtl-arch,tb-infra,test-writer}/STATUS.md; the handover block at the top of each
is that role's own handoff; runtime and critic were not respawned in this window). The owner's directives live in
dv/auto_dv/docs/gen_intervention_log.md (LOG-101 .. LOG-104). The previous handoff (2026-09-05) is at
dv/auto_dv/handoff/gen_orchestrator_handoff_2026-09-05.md; everything it lists as owed and not named below is still owed.

## 1. Where things stand
- HEAD at handoff: fdd1e7d (landing 67); the commit that adds this handoff and the STATUS copies comes after it.
  Every hand of 2026-09-07/08 is committed and pushed to origin
  (git@github.com:fzhangTT/ibex.git, branch cleanroom/run-a). The tree is clean.
- The team was STOPPED on the owner's directive (LOG-104) after the final bug-log touch landed.
- Owner rulings of this window: LOG-101 (no cross-model review, no Critic), LOG-102 (DV Lead on Fable, every other spawned
  agent on Opus), LOG-103 (evidence bar = retained red + retained green + waveform confirmation), LOG-104 (this stop).
- Bug log dv/auto_dv/docs/gen_bug_log.md is at v2j: plain language, P1/P2/P3 ratings, numbered steps, per-bug test
  command; every P1 and P2 entry has a committed expected-fail test (B8; B1, B2, B7 both halves, B11, B16, B17, B20).
  P3 entries without a test: B3, B5, B10 (blocked on TB defect T12), B14, B15, B19, B22. B22's green control run IS measured and
  committed (record gen_tdd_bug_tests.md Section 10 at 1391ab1); the bug log's B22 Evidence line still says "owed"
  because the hands crossed; folding the cite (v2k) is the DV Lead's first owed item.
- TB landings of this window: B16 arm-count knob (e7e7a94), counter model + gen_ut_counters (c746629), follow-on with the
  NMI-pulse proof run + T11 scoreboard fix (87fd39f). TB defect register: T11 FIXED (d8a2324), T12 open, T10 open.
- Coverage gate unchanged since LOG-100 (round 1: 3477/4048 = 85.89); no round 2 was run.

## 2. First resume items, in order
1. Owner decisions: witness-bin marking (a: expected-fail-only bins out, 3477/4042 = 86.02; b: plus informational bins,
   86.06; c: leave), a B10 test at P3 (needs the T12 comparator fix first), and what follows (round 2 needs a runtime
   instance on Opus for the LOG-100 tool half and the dispatch; or the handover backlog; or pause).
2. tb-infra: the bus-agent grant repair LANDED as landing 67 (commit fdd1e7d; record
   dv/auto_dv/evidence/gen_tdd_gnt_repair.md, retained logs gen_tdd_logs/fcov/gen_fu_l67_*). Read its Section 3 first: the
   ruled clause "the capture must read the SAME registered sample the decision used" is NOT built (built as written it is
   a full cycle stale in the VCS scheduling regions; 564297 errors on seed 165313640); the built form uses one edge for
   gate and capture, the address read from the net at the edge the gate passed. The Orchestrator landed it as consistent
   with the gate's intent; the DV Lead rules on the clause at resume (accept the built form and reword the ruling, or
   require another shape). Acceptance measured: grant-property firings 0 on both seeds, the unbooked response and the
   isa_pc collapse gone on 165313640, the second seed's runaway gone, sva_rvfi_irq_valid_exclusive (LOG-085, frozen)
   still firing so the flow verdict stays FAIL on all four runs, data-side control runs clean, withdrawn=1/3 as the
   positive control. Not settled (Section 11): no seed sweep; the pair record's rvalid_outstanding readings left as a
   reading. The re-dump waveform hold's release condition (the repair's validation) is met; the two FSDBs are releasable
   on the owner's word, not yet deleted. Owed rows: the Section 9 dummy-wait gap in the counter-model API document, the
   stale task id in the scoreboard. The earlier phantom-grant reproduction finding is
   dv/auto_dv/work/tb-infra/gen_grant_reproduction_2026-09-08.md.
3. test-writer: B22's green control LANDED (1391ab1). Owed at the next touch of a file, never as a hand of its own: the
   Sections 6-9 counter waveform readings re-derived with the siliconpilot reader; the seven bare-date docstrings; the
   test_writer area manifest's header (810 rows: 701 four-field, 109 five-field from line 715 on; declare the fifth column
   or fold the labels; no consumer parses it); the mseccfg re-render after one measured run (dv-lead ruling, TASKS 04:13Z);
   mul_div parked; a B22 testlist entry only if the owner asks for a P3 test.
4. dv-lead: gen_comment_census.py vacuous green outside a git root (refuse or filesystem walk) and its arithmetic false
   positive; TP-PMP-010's unhosted group; T10's Fixed cell after the bus repair; the B22 Evidence cite once the control lands.
5. rtl-arch: one owed touch of dv/auto_dv/evidence/gen_b10_b16_rtl_facts.md Section 1.5.1, after its table, in its words:
   "The FSDB these figures were read from is not retained (the out tree has since been removed), so they cannot be
   re-derived; what survives as their check is tb-infra's independent reading of the same capture in
   gen_fu_l64_b16_waveform.log:19, which agrees on all four data_rvalid_i transitions in this window, and the retained
   comparator line, which agrees on the value written." (The figures were checked against both anchors at the stop and
   hold.) Second owed clause: gen_ibus_props_irq_signature_reading.md Section 2 labels sva_ibus_outstanding_max a DUT
   property as at its pinned base 4017573; it is now declared a TB property (the term is the testbench's own outstanding
   counter, made saturating after that base), so one clause noting the reclassification, cited to the commit that made it
   (rtl-arch handover Addendum 2 carries the git evidence). Then standing duties only. The next exclusion pass is 15, not 14 (pass 14 already ran against the round_0 dump,
   dv/auto_dv/excl/gen_exclusions_README.md row 14; the finisher refuses a label already in the table); use the
   pass-labelled gen_f1_pass_run.sh with gen_f1_pass_finish.py in dv/auto_dv/work/rtl-arch/, not the pass14 pair.

## 3. Mechanics (dv/auto_dv/work/orchestrator/chains/)
- plan/chain.sh <sha256 list> (message in plan/commit_msg.txt): docs, tests, tools; gates 1/2, TB gate, HASH-LAST, STAGED.
- rec/chain.sh <sha256 list> <msgfile>: records-only, fast.
- irqfix/chain_fixes_only_sha.sh <two-column sha256 list>: TB code; needs BOTH irqfix/commit_msg.txt and
  irqfix/commit_msg_fixes.txt; runs KNOBSGEN, LIB, SMOKE.
- All three carry an OTHERRE line of other roles' HOLD files; widen it at HOLD time (idempotent python, then bash -n).
- Hand form: one list of paths with sha256 first-12 verified on a detached archive of HEAD assembled from the list alone;
  frozen until confirmation; HOLD line before the first edit of a committed file (a codegen render is an edit, so the yaml
  behind it is frozen too); WITHDRAW waits for acknowledgement; a WITHDRAW that crosses a commit does not undo it.
- Confirm only after reading the chain's exit line; then check every committed blob against the handed hashes; push with
  GIT_SSH_COMMAND='ssh -o BatchMode=yes' git push origin cleanroom/run-a; append TASKS.md.
- Respawn briefs: chains/respawn/ (Opus for every role except a running DV Lead, LOG-102).

## 4. Tool cautions
- fsdb-mcp-server returned inconsistent answers within one session on test-writer's B22 FSDB (a correct first range query,
  then point samples carrying values from much earlier times, then empty ranges over windows that contain transitions;
  reopening the session did not help). A waveform reading from it needs a second reader (siliconpilot queryWaveform) or the
  TB's own export record before it goes into a record. Committed B1 and B2 readings were re-derived and stand; the counter
  readings of gen_tdd_bug_tests.md Sections 6-9 are corroborated by the runs' logs but not yet re-derived (owed).
- gen_comment_census.py prints a vacuous green outside a git root (fix parked or landed per dv-lead's handover).

## 5. Held artefacts and scratch state
- tb-infra's re-dump waveforms of seeds 165313640 and 1207954461: release condition (the repair's validation) met by
  landing 67; releasable on the owner's word, not deleted at the stop.
- The shared scratchpad under /tmp is at 68 G with 51 G free on that filesystem (tb-infra, 04:38Z); the large directories
  belong to several roles and some are cited by committed records, so nothing was reclaimed at the stop. A successor
  reclaims only directories no committed record cites, by literal path (A-002), after the owner's word.
- test-writer's build roots head_export20..23 in dv/auto_dv/work/test-writer/ (rebuildable; keep until the B22 control lands).
