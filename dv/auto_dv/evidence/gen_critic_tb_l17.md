# Critic verdict: tb-infra landing 16, the landing-15 review rows and the allocation evidence restored (commit e2f3f65, diff base ae0ce2f), reviewed as tb_l17

Scope (the Orchestrator's): the CM179 and CR-16 dispositions in gen_critic_response_fu2a.md, the tag-write history artifact
gen_fu_l16_trace17_tagwrite_history.log with its generator gen_trace_tagwrite_history.py (16 episodes, 13 at index 26 and 3 at index 27, the added way
derived per episode), the trace17 source delta gen_fu_l16_trace17_mutant.diff, the two other derivation tools committed under dv/auto_dv/tools/, and the
figures reader hardened against a silent missing count. No source, knob table or flow change.

Artifacts reviewed (committed blobs at e2f3f65; sha256 first 16 hex):

- dv/auto_dv/evidence/gen_critic_response_fu2a.md  2c9b41d0c8cf144c
- dv/auto_dv/evidence/gen_tdd_step2b.md  e6d113cf55d4c6ae
- dv/auto_dv/mutations/gen_mut_step2b.md  268457ca69855582
- dv/auto_dv/docs/gen_component_api_misc_monitor.md  be572fc0c800304f
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  80b4b7066eb6ab35
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l16_trace17_tagwrite_history.log  eeea4019be58e8d6
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l16_trace17_mutant.diff  83b51d025bd16c40
- dv/auto_dv/tools/gen_icache_ecc_figures.py  e12cb68fdd18d585
- dv/auto_dv/tools/gen_mutant_build_identity.py  885a77539e6c619a
- dv/auto_dv/tools/gen_trace_tagwrite_history.py  4d460baa4beb3fa1

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_critic_tb_l16.md
(ba4940caec224e93, the verdict whose rows this landing answers); rtl/ibex_icache.sv:499-513, :589-594 (read for tb_l15); LOG-079.
Method: detached git worktree of e2f3f65. The diff is the ten listed files (10 of 10 md5s OK at e2f3f65, 0 list mismatches), none under rtl/,
dv/auto_dv/tb, env, gen_tb, flow or the knob table. Re-derived by me: the two new manifest rows (bytes and md5); the trace17 diff is three added
$display lines and no removal, and applied to the committed gen_tb_pkg.sv (8b2fd577f2b46db6, the w18 list row) it yields a811c3db91e5ad9a, the
trace17 per-file list's row, so the trace build's one differing file is exactly this delta; the tag-write history's 16 episodes reconstructed
independently by me from its 322 retained tag-write lines (carry each way's valid bit and tag forward per index), identical to the artifact's list in
index, tag, added way, start and end cycle, and all 20 injections of gen_fu_l16_trace17_duplicate_copies.log fall inside an episode of their index; the
figures reader run on the worktree root (rc 0, 0 problems, every table figure equal to Section 16 and the landing-15 mutant table) and on three
corrupted copies (a bogus root, a GEN_MISC line cut at 400 characters, a catch header stripped of its python-counted total: rc 1 each, naming the
run and the missing field); `git grep` for the retired trace log finds no tracked citation outside review and Critic files; the alert_minor row and
the SUPERSEDED marking read in the diff. No subagent used. EXPOSURE: none beyond the Orchestrator's sha-and-scope message and the git log subjects.
The cross-model review of this range was running in parallel; Section 6 says whether its artifact was read; Section 7 carries the reconciliation
owed by gen_critic_flow_l14_merge.md (frozen), whose parallel artifact landed after that hand-off.

CRITIC VERDICT: APPROVE. The five CM179 minors and the eight CR-16 rows are answered as stated, the WP12-F2 allocation claim rests again on an
observational artifact that reproduces under my own reconstruction, the trace session's delta is now checkable from committed files, and the three
derivations are in the tree and behave as the record says. One low on the committed tools' usage text.

## 1. What was verified

| item | as built at e2f3f65 | evidence (re-derived by me) |
|---|---|---|
| the tag-write history (WP12-F2's allocation evidence restored) | gen_fu_l16_trace17_tagwrite_history.log: 322 ICTRACE tagwrite lines at indices 26 and 27 (the indices taken from the duplicate-copies artifact, 183 at 26 and 139 at 27) of the trace run's 1564; a reconstruction listing 16 episodes in which both ways held tag 00100000 valid at one index, 13 at 26 and 3 at 27, each with its start and end cycle and the way whose copy was added second (all 16 into way 0); the header says to read that aggregate narrowly (one program, one seed: the direction of each episode, not the way-selection policy) | my reconstruction from the 322 retained lines reproduces the 16 episodes exactly; the 20 duplicate-copy injections all lie inside an episode of their index (20 of 20): two retained artifacts agree; the 1564 total is the raw run's and is stated as such |
| its generator | gen_trace_tagwrite_history.py <landing root> <scratch root>: reads the trace session's stdout (scratch, unretained) and the retained duplicate-copies artifact for the indices, refuses when either is missing, writes the artifact and its manifest row | read; the artifact's header text equals the generator's; regeneration needs the scratch stdout, which the header names, so the artifact is the retained form and my reconstruction is its check |
| the trace17 source delta (CR-16 L-4 / CM179 m-3) | gen_fu_l16_trace17_mutant.diff: three added $display lines (inject, lookup, tagwrite) in gen_tb_pkg.sv, no removal; manifest row 2483 bytes | applied to the committed gen_tb_pkg.sv the result hashes to the trace17 list's row (a811c3db91e5ad9a): the trace build differs from w18 in this delta alone |
| the figures reader (CR-16 L-1 / CM179 m-2) and its hardening | dv/auto_dv/tools/gen_icache_ecc_figures.py <landing root>: re-derives every Section 16 figure and the mutant table from the retained excerpts, verdicts and headers; scans the whole comment block for the python-counted total and records a problem when it is absent, instead of reading one line and silently recording no count | rc 0 and 0 problems on the worktree, the tables equal to the records; rc 1 on a truncated summary line ("the data-injection fields did not parse"), on a header without its total ("no python-counted error total in the excerpt's comment block"), and on a bogus root |
| the identity gate | dv/auto_dv/tools/gen_mutant_build_identity.py <landing root> <build> <scratch root>: compares each out-of-tree root's per-file list with the landing build's and exits 1 unless exactly the mutation's file differs; 13 roots named including TRACE17 | read; its inputs are the gitignored work directory and the scratch roots, so it is tb-infra's process gate, not a reader's check; the committed per-file lists let a reader re-derive the same 13 matches (done in tb_l16) |
| CM179 m-1 / CR-16 L-2 | the landing-14 mutant table's heading says SUPERSEDED, a paragraph explains that landing 15 re-ran the six on w18 under the same paths, and one line under the table says the named files now hold the re-runs and the w16 identity is the tree at a28d1ae | the diff |
| CM179 m-5 / CR-16 L-3 | the three sites now say identical on the retained first 400 characters (13 of 13) and in every re-derived figure, the rest compared on unretained run outputs; the six mutants' reproduced counts named as retained evidence | the diff |
| CM179 m-4 / CR-16 L-5 | the alert_minor row names Section 5a where it introduces form (b) and quotes the reach on both programs | gen_component_api_misc_monitor.md:54 |
| CM179 m-2 / CR-16 L-1 (the deletes list) | the two record sites call gen_landing15_deletes.txt a gitignored work file and name the commit diff (10 deletions, 11 renames) as the authority | the diff |
| CR-16 I-1..I-3 | the DV Lead's re-pointing confirmed (no tracked citation of the retired trace log outside review and Critic files); I-2 relayed to Runtime; the MUT-ICE-WAY site-660 reading recorded in the mutant notes | `git grep`; the diff |
| Section 18 | "No build and no simulation"; the rows folded listed | honest |

## 2. Closure of tb_l16

CR-16 L-1..L-5 CLOSED; I-1..I-3 recorded. tb_l16's correction accepted: committing the readers under the work directory would not have tracked them.

## 3. Findings

### L-1 (low) [S5 single source; S4 record] The committed tools' usage text does not match the tools

gen_icache_ecc_figures.py's docstring still opens "gen_l15_figures.py <landing root>" (its scratchpad name); gen_mutant_build_identity.py's docstring
gives four positional arguments ("<landing root> <build> <scratch root> <build>") while the code reads three; and all three tools die with an IndexError
traceback when an argument is missing (a `--help` run of the figures reader treats the flag as the root and prints empty mutant blocks before exiting 1).
The tools work as the record says when called correctly (Method), so this is text, not evidence. Fix the two docstrings and print the usage line on a
missing argument.

### Informational

- I-1: the tag-write generator and the identity gate read the scratch roots and the gitignored work directory; the artifact and the per-file lists are
  the retained forms, and the record says so. A reader checks the artifact by reconstruction (as I did), not by regeneration.
- I-2: the run total of 1564 tag writes rests on the unretained stdout; the header says it was counted from the run's own lines. The 322 retained lines
  are what the reconstruction uses, so no figure the artifact derives depends on the 1564.
- I-3: the episode reconstruction reads the retained writes in the same way as the generator (a write completing the coexistence names the added way);
  the identical result from an independent implementation is what makes the 16 / 13 / 3 and the way-0 direction checkable rather than asserted.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S4 honesty: the allocation claim is put back on observation with the aggregate's limits
stated in the artifact itself; the superseded table is marked and its evidence located; the comparison claim split into measured and checkable
(conforming). S6 retention: the delta that makes the trace build identifiable is retained and reproduces the list row; the readers are in the tree
(conforming; L-1 on their text). S5: one usage line and one docstring name diverge from the code (L-1). One-line verdict: PASS.

## 5. Verdict

CRITIC VERDICT: APPROVE. Low L-1 with tb-infra's next touch. Rows CR-17.

## 6. Reconciliation with the cross-model review of the same range

Not read. At hand-off time dv/auto_dv/reviews/2026-09-04-claude-diff-ae0ce2f1-e2f3f65d.md existed as an empty, uncommitted file (0 lines, sha256 of the
empty input e3b0c44298fc1c14; `git log` names no commit for it): the review was still running and the Orchestrator's standing instruction is not to
wait. Its rows are reconciled by the Orchestrator's relay or in my next verdict; nothing in Sections 1-5 depends on it.

## 7. Reconciliation owed by gen_critic_flow_l14_merge.md (c7daa03d56381ab7, frozen): the cross-model review of fc81da5..ae0ce2f

Read now: dv/auto_dv/reviews/2026-09-04-claude-diff-fc81da5d-ae0ce2f1.md (sha256 a0803c4c2418034a, 42 lines, committed 2bc5bc4; a fresh claude
session on a detached checkout), APPROVE with two informational findings and no change requested.

- Verdicts agree: both approve Runtime's touch. Its verification matches mine point for point: the self-tests (151 / 28 ok, CONST-CHECK PASS), the three
  reds reproduced by reverting one fix at a time with exactly the new cases failing, the gate readings through both paths on the merged list, the
  docstrings against the code, the API sections, and the staging digest as a working-tree claim (my L-2; it notes the TL-L13-c precedent as I did).
- Not in its report: my L-1 (the eleven readings cited to an unretained merge verification log); it re-took the readings itself, as I did, and did not
  raise the retention point. L-1 stands as relayed.
- Its Info 1 (gen_test_plan.md:438 and :19432 still call the P6 widening "owed and parked" against an earlier gen_run.py): the plan owner's, not
  Runtime's; not a row of mine. Noted for the DV Lead's next touch.
- Its Info 2 (TESTLIST_PLUSARG_RULE's rationale says a whitespace-carrying value "reads 0" under $value$plusargs %d, while string-kind plusargs are
  read with %s and would carry the whitespace): adopted and verified as informational for Runtime's next touch. The TB holds both reader kinds
  (`command grep` over dv/auto_dv/tb, env and gen_tb finds %s readers beside the %d ones), so "reads other than written" is the exact reason; the
  refusal itself is right for every kind, as the review says, and no code change is asked.
