# Critic verdict: the final exclusion file (pass 14), feature group pass-14

Artifacts (all at commit 255dca3; range de1ccf3..255dca3, whose dv/auto_dv/excl changes are 98b643e and the README
row of 255dca3):
- dv/auto_dv/excl/gen_exclusions.el  sha256 91dbc8c7ff9ce60b  2543 lines (byte-identical since 98b643e)
- dv/auto_dv/excl/gen_excl_select.py  7d6b515878aa17c1  1122 lines (7 changed lines in the range)
- dv/auto_dv/excl/gen_exclusions_README.md  4c9dd4327f6015ed  320;  gen_exclusions_select_report.md  d1a28931088e0685  145
- dv/auto_dv/excl/gen_precheck/gen_precheck_dashboard_round_0.txt  a9b0f1418c91a988  35;  gen_precheck_urg_round_0.log  f57172f9b9cf4b6f  14
- inputs judged against: DV_prompt.txt:118-123; docs/dv/dv_principles.md d9c27db18f511411; my exclusion verdicts
  gen_critic_exclusions_v1/v2/v3.md (v3: APPROVE of the draft form at 4125c36/9ebf2d9 with F-1 and F-3 open,
  "the regenerated file at F-1 comes back to me"); gen_critic_exclusions_draft_v2.md Section 5 (F-1..F-7);
  dv/auto_dv/evidence/gen_exclusions_draft_v2.md (B.7 rules, Part C rows); the round-0 record under gen_round_0/.
Date: 2026-09-05T02:36:33Z   Role: Critic
Method: detached worktree of 255dca3 in my scratchpad; report-time urg loads of the committed .el against the round's
measured merge /proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_1/cov/merged.vdb, run by me locally (no LSF):
strict, plain, and three controls; the generator re-run on the worktree with the pass-14 arguments; every class-D arm,
guarding assertion and enum read in the RTL at the cited lines; the file parsed entry by entry. The range's cross-model
review 3cc3c72 was NOT read before Sections 1-5 (Section 6 reconciles it). Exposure: none beyond my own earlier
verdicts on this file. Retained logs: dv/auto_dv/work/critic/excl_final/ (urg logs, dashboards, gated rows, the
attempts file of the positive control, the generator log, the report diff, the parse output).
This is the final-file verdict my v3 promised; it also closes the group under LOG-095 (excl is code scope) and gives the
reviewer approval DV_prompt.txt:122 requires for control-logic exclusions.

## 1. What the file is (parsed, not read from the README)
1424 entries: 189 Block, 83 Branch, 667 Condition, 463 Toggle, 2 Fsm, 5 State, 12 Transition, 3 Assert; 495 annotation
groups over 13 modules; every entry sits inside an ANNOTATION_BEGIN/END pair (0 outside). Class census over the 495
annotations: T 487 (CHERIoT constant tie), P 2 (build parameter), D 6 (enum default arm), R 0. 17 distinct T022_*
citations. 270 Condition entries name cheriot_enable_i. Largest scope ibex_cheriot_ex, 531 entries (the A.1 object
list). Against the pass-13 file (de1ccf3): +3 Block and +3 groups, the class-D spare-encoding default arms
(ibex_controller Block 149 :990-993, ibex_load_store_unit Block 142 :605-607, ibex_multdiv_fast Block 37 :522-524);
27 Class T annotation texts re-worded by the selector change (CM-18: the duplicated "Term(s)" sentence dropped when the
reason already carries the evidence; CM-19: the guard_analysis docstring restored as a docstring); every other kind
count unchanged (667 / 463 / 83 / 2 / 5 / 12 / 3). The commit message's "1424 entries across 13 modules" is exact.

## 2. Reproduction
- Strict load (02:17:16Z-02:17:20Z): urg rc 0, no UCAPI line, no attempts file; dashboard identical to the committed
  gen_precheck_dashboard_round_0.txt apart from the Date / Command line / User header lines. Gated rows, the two
  instances summed (u_ibex_core(x) + u_register_file(x)): LINE 3525/4028 + 129/130 = 3654/4158; COND 6310/9216 +
  154/159 = 6464/9375; TOGGLE 16650/20870 + 227/232 = 16877/21102; FSM 38/74; BRANCH 1726/2255 + 105/108 = 1831/2363;
  ASSERT 165/174 + 1/2 = 166/176.
- Plain load (no file): 3525/4229 + 129/130 = 3654/4359; 6310/9465 + 154/159 = 6464/9624; 16650/24742 + 227/302 =
  16877/25044; 38/86; 1726/2320 + 105/108 = 1831/2428; 165/174 + 1/5 = 166/179: the round record's gate row. Covered
  counts equal on both sides of every metric; the six rows equal the README Section 3 table, the 98b643e message and the
  rtl-arch-009 record (dv/auto_dv/work/runtime/done/rtl-arch-009.yaml: baseline_rc 0, strict_rc 0, PASS).
- Positive control: a copy of the file with two Block entries for objects the rebaseline strict load had refused as
  covered (ibex_load_store_unit Block 161 and 164, from gen_attempts_round0_rebaseline_pass1.log) produces
  Warning-[UCAPI-ILOAD] "Illegal exclusion attempt ... object for Line metric which is covered" and an attempts.log in the
  report directory (retained: excl_final/attempts_mut3.log). urg's exit code stays 0; the flow reads the UCAPI count and
  the attempts file (gen_regress.py: exclusion_violation, exit 3). So "0 UCAPI warnings, no attempts file" is a
  discriminating statement, not a default.
- Checksum controls: a one-digit change of one entry checksum (ibex_cheriot_ex Block 8; separately the effective
  ibex_controller Block 149) changes no number and raises no warning: dashboards identical to the strict run. The entry
  checksum is not a strict-load guard; objects match by id and signature. No exposure at the fixed RTL (the head-mode
  mirror of 4a00702); recorded as O-1.
- Generator re-run on the worktree of 255dca3 with the pass-14 arguments (dump, the three pass2-4 attempts logs,
  --ec3-asserts gen_round_0/gen_asserts.txt --ec3-round round_0; 3 s): the .el is byte-identical (91dbc8c7ff9ce60b);
  the report differs only in the --out path of its line 141. The selector's self-test runs on every invocation
  (gen_excl_select.py:870) and passed.

## 3. The final-file conditions (gen_critic_exclusions_draft_v2.md Section 5), judged against the file
- F-1 MET. Generated from the measured merge's own dump (regress_round_1/cov/full_exclusions, dump date 22:00:23Z, the
  round's end); measured tests only (36 runs of the 12 measured entries; the 17 unmeasured runs merged into
  cov_unmeasured, B.7 rule 6); legal stimulus: the plusarg census of gen_round_0/gen_testlist_snapshot.yaml finds no
  fault-injection, illegal-stimulus or debug knob on any measured entry; strict load with 0 rejections three times
  (author, rtl-arch-009, mine).
- F-2 MET. dv/auto_dv/evidence/gen_t022_formal/ is committed (7 entries); each of the 17 cited T022_* names resolves to
  3-12 files there (T022_CORE_BP0 6, T022_CORE_CHERI0 11, T022_CORE_CHERI0_B 5, T022_CRX_IDLE 12, T022_CSR_CHERI0 5,
  T022_CSR_MSHWM0 3, T022_CTRL_CHERI0 12, T022_CTRL_NAMED 12, T022_CTRL_PRIO0 6, T022_DEC_CHERI0 5, T022_ID_CHERI0 5,
  T022_LSU_CHERI0 12, T022_LSU_NAMED 12, T022_LSU_NO_CTX 12, T022_MD_NAMED 12, T022_RF_CAP0 6, T022_WB_CHERI0 5).
- F-3 MET. The three class-D(2b) annotations read "attempts 5408327, failures 0 in round_0
  (dv/auto_dv/evidence/gen_round_0/gen_asserts.txt)"; gen_asserts.txt rows 195, 228, 273 carry ATTEMPTS 5408327, REAL
  SUCCESSES 5408183, FAILURES 0 for IbexMultDivStateValid, IbexCtrlStateValid, IbexLsuStateValid. RTL read: the
  default arms rtl/ibex_controller.sv:990-993 (default -> RESET), rtl/ibex_load_store_unit.sv:605-607 (ls_fsm_ns = IDLE),
  rtl/ibex_multdiv_fast.sv:522-524 (md_state_d = MD_IDLE); the guards `ASSERT(IbexCtrlStateValid, ctrl_fsm_cs inside
  {10 states})` :1104-1106, `ASSERT(IbexLsuStateValid, ls_fsm_cs inside {8 states})` :821-824,
  `ASSERT(IbexMultDivStateValid, md_state_q inside {7 states})` :532-533; the enums ctrl_fsm_e logic [3:0] with 10
  named values (6 spare, rtl/ibex_pkg.sv:291-302), ls_fsm_e logic [3:0] with 8 (8 spare, :816-820), md_fsm_e 3-bit with 7
  (1 spare, rtl/ibex_multdiv_fast.sv:90-92): the annotations state exactly these.
- F-4 MET. The measured build carries -cm_glitch 0 (gen_build_manifest_gen_tb.yaml:18 glitch_filter true, :75) and the
  regress manifest records glitch_filter true; the fetch_enable_i tie conditions (ibex_core.sv:648, :649, :1405, :1414)
  are listed by the select report as NOT selected and are absent from the file; the cheriot_enable_i tie conditions
  are in, under the glitch filter the ruling requires.
- F-5 MET. No Class R annotation; rows 37-40 absent.
- F-6 MET. 1424 of 1424 entries inside an annotation; every annotation names its class, an evidence token (EC-n or a
  T022_* proof) and its RTL location: 235 with rtl/<file>.sv:<line>, 260 with the module file and line (A.4 vectors) or
  the port itself (A.5 toggles: the port is the toggle object). The A.1 object list is reproduced entry by entry.
- F-7 MET under the recorded rulings. The entry set is Part A (A.1 object list, A.4 impossible-value vectors, A.5
  ports, A.7 vacuous assertions), the shared-module guard-analysis dead arms my v3 verdict admitted (gen_critic_exclusions_v3.md,
  APPROVE at 4125c36 / 9ebf2d9) and the six C.2 default arms (Part C rows 1, 23, 33 since pass 14; 31, 34, 35 before);
  rows referenced 1, 12, 23, 29, 31, 33, 34, 35, 36; the A.8 carve-back filter kept 7 Blocks and removed 3 vectors
  (select report); the refuted-and-dropped list is carried from the pass2-4 attempts logs; against pass 13 the object
  set grew by exactly the three C.2 arms.

## 4. DV_prompt.txt:118-123
Every exclusion carries a written justification in its annotation (1424 / 1424). Every control-logic exclusion carries
an unreachability argument: the constant tie cheriot_enable_i = IbexMuBiOff at dv/auto_dv/tb/gen_dut_top.sv:206 with the
EC-1 k-induction proofs (class T, 487 groups), the elaboration parameters BranchPredictor = 0 / BranchTargetALU = 1 with
the config check (class P, 2), the spare enum encodings with EC-1 and the EC-3 runtime guard (class D, 3 of 6; the other
3 are full encodings). This verdict is the reviewer approval the clause requires. The data-bit-feeds-control clause does
not arise: the 463 toggle entries are CHERIoT-only ports tied constant (A.5), excluded on unreachability, not as data
path. The three excluded assertions (rtl/ibex_register_file_ff.sv:237-239, antecedent cheriot_enabled constant 0) show
ATTEMPTS 5408327 and REAL SUCCESSES 0 in gen_asserts.txt:55-57: vacuous as annotated.

## 5. Rows
- M-1 (Medium, OWED inside this APPROVE, disclosed here). B.7 rule 3 (gen_exclusions_draft_v2.md: the -dump
  full_exclusions files AND constfile.txt of the measured merge are copied beside the annotated .el and committed) is
  half met: the dump is retained (gen_round_0/full_exclusions/*.gz), the constfile is not. constfile.txt of the measured
  build (369118 bytes, 7051 lines, sha256 d84de5fcaf2f4bdc) exists only in the out-tree
  (regress_round_1/build/gen_tb/constfile.txt, cited by gen_regress_manifest.yaml:232 and :64056) and in the
  git-ignored dv/auto_dv/work/rtl-arch/gen_excl_f1_round_0/gen_constfile_gen_tb.txt (same sha256); git ls-files finds
  no constfile anywhere. Every one of the 495 annotations cites "EC-2 constfile" as an evidence class, so the cited
  evidence is unretained (the standard F-2 applies to T022_* citations). The file's correctness does not rest on it and
  the build is reproducible from the pinned commit's recorded identity, hence owed, not blocking. Required: the
  constfile committed gzip -n (reproducible header, as gen_modlist.txt.gz) beside the .el under gen_precheck/ or under
  gen_round_0/, its sha256 in the README pass-14 row; or an Orchestrator ruling that the out-tree copy plus the
  recorded hash suffices. Due with rtl-arch's next excl touch (the CM220 touch in progress).
- L-1 (Low, records). gen_exclusions_README.md Section 6 is stale against the file it describes: the F-1 row (:274)
  still reads "draft form: generated from the round-0 re-baseline dump", the F-3 row (:276) "OPEN ... held out", while
  the .el header line 5 and the pass-14 row (:142) say the regeneration ran against round_0 and EC-3 is filled; the F-6
  row (:279) says "381 annotation groups", the pass-12 figure (the same README says 495 at :122; the file has 495).
- L-2 (Low, records; my v3 L-3 follow-up). The per-entry no-op join (105 NO-OP / 84 EFFECTIVE) that the README's Section
  3 table rests on exists only as a work artefact (dv/auto_dv/work/rtl-arch/gen_excl_f1_round_0/gen_f1_round_0_noop_join.md,
  21839 bytes, "not retained"). Retain it (or its sha256 with the command that regenerates it) so the table is checkable
  from the tree.
- L-3 (Low, records). The independent re-load the README row cites (rtl-arch-009: rc 0 / 0 / 0, six equal gated rows)
  is untracked at HEAD (dv/auto_dv/work/runtime/done/rtl-arch-009.yaml); the Orchestrator announced its retained copy
  under gen_round_0. Closes when that copy is committed; my own strict load reproduces its figures meanwhile.
- O-1 (observation, no action on the file). Entry checksums are not a strict-load guard (Section 2); a file regenerated
  against a changed RTL would be caught by -excl_strict only where objects are covered. Worth one sentence in the README's
  reviewer notes when it is next touched.
- Selector change (7 lines, gen_excl_select.py:443-447 and :667-672): CM-18 and CM-19 dispositions verified against the
  diff; the re-worded annotations keep their evidence term; the docstring is now guard_analysis.__doc__.
- dv_principles.md conformance (skill dv-principles-check, doc read fresh, d9c27db18f511411): PASS. Section 1 and 2
  (stimulus, checkers) do not apply to an exclusion file; Section 4 honesty: the stale README rows are L-1, the file
  itself states its sources (header lines 2-5); Section 5: the selector diff adds no history comment; Section 6: the
  trust triad does not apply to an exclusion file, and the selector self-tests on every run.

CRITIC VERDICT: APPROVE. The final exclusion file dv/auto_dv/excl/gen_exclusions.el at 255dca3 (sha256
91dbc8c7ff9ce60b) is approved for measured rounds: conditions F-1..F-7 are met, every control-logic exclusion carries its
unreachability argument, the strict load reproduces with a discriminating positive control, and the generator
reproduces the file byte for byte. M-1 (constfile retention, B.7 rule 3 / EC-2) is owed under the condition stated;
L-1..L-3 are records rows. The gen_excl_select.py change in the range is approved with it.

## 6. Reconciliation with the cross-model range review (read after Sections 1-5)
dv/auto_dv/reviews/2026-09-04-claude-diff-de1ccf32-255dca32.md at 3cc3c72 (e2f03b8beb7b8e37, APPROVE-WITH-CHANGES, CM220:
four medium, three low, one info), read at 2026-09-05T02:40:23Z. Two follow-on commits landed meanwhile: 26a517a (rtl-arch, CM220 rows,
"feature group pass-14-rows") and 8fb9705 (elcheck bullets re-pointed, records-only). The .el is byte-identical from
98b643e through HEAD 2cfb6fd; 26a517a changes gen_excl_select.py only in the report's emitted-path line (repo-relative),
no entry, so per the Orchestrator's ruling it is judged by its own range review and only noted here.
- CM220 medium 1 (README :111 "0 (held out)", :227 "held out", F-3 :276 "OPEN"): verified at 255dca3; overlaps my L-1
  (I had F-3 and add F-1 :274 and F-6 :279; the reviewer adds :111 and :227). 26a517a fixes :111, :227 and F-3 (HEAD :307
  "CLOSED at pass 14"); the F-1 row (HEAD :305, still "draft form ... re-baseline dump") and the F-6 "381 annotation groups"
  (HEAD :310) remain stale: L-1 stays open for those two rows.
- CM220 medium 2 (README :95 and the Section 3 intro name the re-baseline as the current provenance): not in my Sections
  1-5 (I read a post-fix tree for that part; recorded as my miss). Verified at 255dca3 (:95 "the round-0 re-baseline");
  closed by 26a517a (HEAD :95 "the measured round_0 dump"). Adopted and verified.
- CM220 medium 3 (the ASSERT row note "143/178 ... does not move"): verified at 255dca3 (:158); false for round 0, my strict
  and plain dashboards show 229/254 against 229/257. Not in my Sections 1-5 for the same reason; closed by 26a517a (HEAD :176
  "DOES move ... 229/257 to 229/254"). Adopted and verified.
- CM220 medium 4 (rtl-arch-009 quoted from an untracked manifest) = my L-3 (Low here because my own strict load reproduces
  its figures). Closed at HEAD: dv/auto_dv/evidence/gen_round_0/gen_elcheck_rtl_arch_009.yaml is tracked (26a517a). L-3 CLOSED.
- CM220 low 1 (select report line 141 carries an absolute clone path): verified at 255dca3 (my regeneration diff shows the
  same line); adopted as L-4; closed by 26a517a (repo-relative print, report line now "to dv/auto_dv/excl/gen_exclusions.el").
- CM220 low 2 (the no-op join totals recorded in no committed excl file) = my L-2 in part: at 255dca3 the README carried no
  join table (verified: no NO-OP / EFFECTIVE line); 26a517a adds the five-class table (105 / 84). The per-entry join file
  that the table rests on is still a work artefact: L-2 stays open as stated.
- CM220 low 3 and info (gen_archive_manifest.md file count and out-tree claims): runtime-2's record, outside this verdict's
  target; not judged.
- Not in CM220: M-1 (the constfile of the measured merge unretained, B.7 rule 3 / EC-2, owed), O-1 (entry checksums are not
  a strict-load guard), the positive control that makes the 0-rejection statement discriminating, and the RTL reading of
  the class-D arms, guards and enums. The verdict stands as in Section 5: APPROVE with M-1 owed; open records rows L-1 (F-1
  and F-6 rows) and L-2; L-3 and L-4 closed at HEAD.
