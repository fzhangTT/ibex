# Critic supplement to tb_l24: the cross-model review of 1a7f506..71f207c, read after tb_l24 was frozen

Supplement to gen_critic_tb_l24.md (3cb1c007fa396cd7, committed 2b7a9b0, frozen). Written at the Orchestrator's instruction because that review returned
REQUEST-CHANGES with a Major on the fact tb_l24's L-1 rated Low. This file records the artifact as read, the severity difference with my reasoning, the
one correction the artifact forces on tb_l24, and tb_l25 as the re-review that closes both verdicts.

Artifact: dv/auto_dv/reviews/2026-09-04-claude-diff-1a7f5066-71f207ca.md  f0653b574d12cd65 (39 lines, committed 26b42b6; a fresh claude session at 71f207c). Its range holds fb494f4 (tb-infra landing 24) and 71f207c
(Runtime's loader rule).

Date: 2026-09-04 (UTC). Role: Critic. Method: every figure below re-derived on the fb494f4 worktree or a `git archive` of 1a7f506, with the flow's
own function (gen_flow_util.filelist_digest over the gen_tb build's filelists gen_rtl.f and gen_tb.f) and the team's TB-source recipe (gen_tb_local.sh's
find over env, tb, isa and gen_tb). No subagent used. EXPOSURE: the Orchestrator's message naming the Major and the artifact itself.

CORRIGENDUM to tb_l24: Section 2 marks CR-23-L-2 CLOSED. The row asked for the plan and the RAM comment; the plan and the anti-vacuity note are corrected,
but gen_icache_ram.sv:106-108 still reads "a never-written data line read on a lookup the DUT checks ... a read that raises no alert is a real no-alert
case", which the corrected plan says is not what the bin witnesses (the artifact's third Minor; verified on the tree). CR-23-L-2 is OPEN on that site
until the comment is reworded, which changes the sources identity and belongs with landing 25's re-take. I verified the plan and the note and took the
row's DONE for the comment: the same under-checking as the tb_l17 and tb_l18 corrigenda, one more time.

## 1. The Major: the fact, and why I hold Low

The artifact's Major (gen_fu_l23_wp8_cov_reds.log:5) says the evidence build w26 (9ff74126059016cb) "is NOT the committed sources of fb494f4, and the record
says it is", citing (a) the flow's filelist_digest at HEAD, f543c61bd688dd05 over 117 sources, (b) the identity blocks' "committed" hashes for
gen_checkers_pkg.sv (ceae51ad2b959198, the parent 1a7f506's file) and gen_tb_pkg.sv (1e9c6220b81b298f, said to match no committed version), and (c) the
evidence timestamps (12:23Z to 12:32Z) preceding the commit (12:45Z).

What I re-derived:

- The TB-source recipe over fb494f4's tree gives 9ff74126059016cb, the control root's and the tree build's logged value: under the identity the team has
  retained since landing 11, w26 IS fb494f4's TB sources (tb_l24 Method).
- Each of the six roots reproduces from fb494f4's blobs alone: applying the logged diff to fb494f4's file gives the logged mutated hash (6 of 6), and the
  fb494f4 list with that hash swapped in gives the root's logged sources sha (6 of 6, the two ablations with both their diffs). A root whose
  gen_checkers_pkg.sv or gen_tb_pkg.sv had been 1a7f506's could not produce those hashes, since the two commits' files differ and a hash reproduces from
  one base only. So the roots, including the unmutated control, carried fb494f4's content, the CM198-Nit comment edit included.
- 1e9c6220b81b298f is gen_tb_pkg.sv at 1a7f506 and at f0723d6; the artifact's "matches no committed version" is wrong on that point.
- The "committed" field of the identity blocks holds HEAD's file at the time the blocks were written, 1a7f506, not the file the diff was applied to. That
  is the defect tb_l24 L-1 names and it is a labelling defect: the diff's base is proven by reproduction to be fb494f4's file.
- The timestamps are consistent with the response row's account (every source edit finished, then the runs, then the hand-off and commit) and cannot
  distinguish it from the artifact's reading; the hashes can, and do.
- What the artifact has right: no retained gen_fu_l23 or gen_fu_l24 log carries the flow's own identity. filelist_digest over gen_rtl.f and gen_tb.f is
  f543c61bd688dd05 (117 sources) at fb494f4 and 5cf4fdc8845d428c at 1a7f506, so that digest would have settled the question on its own had it been
  retained; the TB-source recipe covers the 75 TB files and not the RTL or the file lists.

Severity: I hold Low on the fact I found (the stale "committed" labels), because the identity of every root reproduces from the committed tree and the
record's claim that the control equals the landing's build is true under the identity it names. I do not adopt the Major's factual statement. I adopt
the artifact's standard: from landing 25 every retained header and identity block carries the flow's filelist_digest beside the TB-source sha, and I
recompute it against the committed file lists as a standing check (done here: f543c61bd688dd05 at fb494f4). The gate is the Orchestrator's rule, the
stricter verdict governing until landing 25's recorded re-review passes both; nothing in this supplement lifts or lowers it.

## 2. The artifact's other rows, verified

- Minor (the part-1 manifest's header): "the loader permits an unmeasured entry to name it" was true at fb494f4 and withdrawn by 71f207c in the same range;
  adopted for landing 25 (reword to a checker-invocation artefact for the retained reds).
- Minor (the GREEN summary line and the truncated excerpts): the first half is tb_l24 L-3; the second half, that the failure fragments ("| 0 1 expected 0",
  "| 102, 100, 2) 0 expected 1") are cut from the macro's own line while the header says lines are read from the runs' files, I did not raise; verified
  against the macro's format and adopted.
- Minor (gen_icache_ram.sv:106): the corrigendum above.
- Low (value 512 without a derive: twin check): tb_l24 I-1; the artifact's fix (a derivation so the twin check covers it) adopted.
- Low (the history parenthetical at gen_tb_pkg.sv:547, "The queue bound that used to sit here ..."): verified; I did not raise it; adopted.
- Its confirmations (the loader rule's order, the knobs gates, the schema sweep, the anchors present, the CM198 third Minor being Runtime's) agree with tb_l24.

## 3. Closing

tb_l25, on landing 25, is the recorded re-review that closes tb_l23's chain for both verdicts: the per-entry manifests and the loader red (CR-23-L-1), the
RAM comment (CR-23-L-2 re-opened here), the CR-24 lows, this artifact's rows, and the flow's filelist_digest retained in every header. CRITIC VERDICT on
landing 24 stands as tb_l24 recorded it, APPROVE, with the corrigendum above and the identity standard adopted.
