# Critic verdict: excl-critic-rows (rtl-arch closes the exclusion final-file verdict's rows; the pass retains its evidence)

Artifacts at 7fb1aeb (feature group excl-critic-rows, GROUP COMPLETE; range e6ed6d8..7fb1aeb, one commit):
- dv/auto_dv/excl/gen_excl_f1_pass.py  sha256 73bd8495982d493c  554 lines (CODE: gzip_n, retention at every non-rehearsal pass,
  entry_set_delta with delta_self_test, the chain self-test's identity check replaced)
- dv/auto_dv/excl/gen_precheck/gen_precheck_constfile_gen_tb_round_0.txt.gz  fbf29436fff477fb  13285 bytes
- dv/auto_dv/excl/gen_precheck/gen_precheck_noop_join_round_0.md  6431104931c66372  196 lines
- dv/auto_dv/excl/gen_exclusions_README.md  83d1dec94eeae5d0  363 lines
- dv/auto_dv/evidence/gen_critic_response_exclusions.md  aac14d302558dbed  99 lines (rows CR-FF-M1, L1, L2, O1, SF-1, SF-2)
- unchanged: dv/auto_dv/excl/gen_exclusions.el 91dbc8c7ff9ce60b
Judged against: my exclusion final-file verdict gen_critic_excl_final.md (9c1de66) rows M-1, L-1, L-2, O-1; B.7 rule 3
(gen_exclusions_draft_v2.md); the commit message of 7fb1aeb; docs/dv/dv_principles.md d9c27db18f511411.
Date: 2026-09-05T03:14:13Z   Role: Critic
Method: detached worktree of 7fb1aeb in my scratchpad (removed after the logs were retained under
dv/auto_dv/work/critic/exclrows/); the retained constfile archive reproduced by my own gzip call over the out-tree
constfile; the retained join counted by table row; the new pass script's --self-test run in the worktree, and the 26a517a
script's --self-test run beside it as the control for SF-2; the rehearsal delta read for the object-id claim; every
README correction read against the file. No cross-model review of this range exists at HEAD 92d6ea2; Section 6 follows
by corrigendum when it lands. Exposure: none.

## 1. My rows, closed
- M-1 (constfile.txt of the measured merge cited as EC-2 by all 495 annotations, retained nowhere): CLOSED. The retained
  archive has a reproducible gzip header (FLG 0x00, MTIME 0) and decompresses to sha256 d84de5fcaf2f4bdc, 369118 bytes,
  7051 lines, the out-tree regress_round_1/build/gen_tb/constfile.txt byte for byte; my own
  gzip.GzipFile(filename="", mode="wb", mtime=0) over that file yields the committed 13285 bytes, sha256 fbf29436fff477fb.
  The README pass-14 row names the path, both sizes and the hash. The owed condition of the exclusion verdict is met.
- L-1 (README Section 6 stale rows): CLOSED. F-1 reads "MET at pass 14: generated from the measured round_0 dump ...
  three independent strict loads"; F-6 reads "495 annotation groups over 1424 entries (381 was the pass-12 figure)";
  the title, the closing sentence, the F-6 / F-7 closers and reviewer note 4 (178 -> 175 named as the pass-10 re-baseline
  figure beside the round_0 179 -> 176) corrected with them. Each read against the file (495 / 1424 / 179 -> 176 are my
  own counts from the exclusion verdict).
- L-2 (the per-entry no-op join unretained): CLOSED. gen_precheck_noop_join_round_0.md carries 189 Block rows, 105 NO-OP
  and 84 EFFECTIVE (my count by row), the figures the README table quotes; the README names the path and hash.
- O-1 (entry checksums are not a strict-load guard): recorded as README Section 5 note 8 with the measurement attributed,
  plus the pass's own finding on object ids (Section 2 below).

## 2. The code, run
- gzip_n: GzipFile(filename="", mode="wb", fileobj=..., mtime=0), the shape the rt39 plan v2 adopts for modlist/modinfo;
  reproducible (above). constfiles() retains the archive only when retain is set, which the caller passes as None for a
  dry run (--dry-run / --self-test) and PRECHECK otherwise; the join is copied to gen_precheck/ on the same branch.
- --self-test (a rehearsal on gen_round_0_rebaseline, urg report-time loads, work dir under the worktree): PASS, rc 0;
  seven checks ok including "entry set matches the current file up to object ids and the EC-3 hold-out"; the delta
  printed as 5 renumbered by this build, 3 class-D arms held out, 0 unexplained; git status of the worktree afterwards
  lists no tracked file, so a rehearsal writes nothing into the tree (SF-1's claim).
- The control for SF-2: the 26a517a script run the same way fails exactly its "entry set identical to the current file"
  check with the other six ok (join NO-OP 105 / EFFECTIVE 81 on the re-baseline, the three class-D arms absent), rc 1.
  The red at HEAD the author reported was real and pre-existing since pass 14.
- entry_set_delta: identity = (module, kind, checksum + signature) with the object id stripped; a before-only entry is
  "renumbered" if an after-only entry shares its identity, "held_out" if it is a Block and EC-3 was not filled, else
  "unexplained"; after-only leftovers are unexplained. The rehearsal delta file shows the object-id fact the README now
  records: five entries over four ibex_if_stage Condition objects with identical checksums, expressions and vectors carry
  ids 25 / 37 / 40 / 43 in the round_0 file and 21 / 33 / 36 / 39 in the re-baseline build (retained:
  exclrows/gen_f1_round_0_rebaseline_entryset_diff.txt).
- delta_self_test: six cases at every invocation, three of which the classifier must refuse (an entry dropped, an
  entry added, a class-D arm absent although EC-3 was filled) and one that must count a changed checksum as two
  unexplained entries; it ran ("delta self-test ok (6 cases)") ahead of both rehearsals. The chain check passes only on
  zero unexplained with the hold-out count equal to EC3_HELD_OUT_BLOCKS (3) when EC-3 is unfilled and 0 when filled.

## 3. dv_principles.md conformance
PASS. Section 4: SF-2 is the author's own red at HEAD, established with a control and replaced by a classifier that
cannot pass by explaining everything; the README now states the history as history. Section 5: the one new inline
comment and the docstrings state intent. Section 6: for a tool, the negative self-test cases are the proof that the
check discriminates; they exist and ran.

## 4. Rows
- L-1 (Low, pre-existing, found by my run). gen_excl_f1_pass.py requires --work-dir to lie under the clone root: with a
  work dir elsewhere both the new and the old script crash at the join header (Path.relative_to(ROOT) at :492 in the new
  file, :428 in the old) after the generator and the strict load have run. The default work dir is in-tree, so the
  committed passes are unaffected; refuse an out-of-tree --work-dir up front, or render the path with a fallback.
- Observation. The response file discloses that the CM220 dispositions live in the 26a517a commit message rather than as
  rows; the disclosure is the right minimum, and it is the same gap my round-2 form verdict raised for CM223.

CRITIC VERDICT: APPROVE. The landing retains the two artefacts the exclusion verdict asked for in reproducible form,
corrects every stale README statement I named and four more of the same class, replaces a self-test that had been red
since pass 14 with a classifier that refuses what it cannot explain, and leaves the exclusion file untouched. My M-1, L-1
and L-2 of gen_critic_excl_final.md are CLOSED; L-1 here is a pre-existing usability defect, not a condition.
