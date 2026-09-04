# Critic verdict: tb-infra landing 15, WP-12 re-proved on build w18 (commit 5eb7ddb, diff base 7d4561f), reviewed as tb_l16

Scope (the Orchestrator's): the re-review of landing 14 under tb_l15's REQUEST-CHANGES: build w18 identity, the width derivation from ibex_pkg,
the 13 evidence runs and 12 mutants against the retained gen_fu_l16_* logs, the measured-run judge's probe-off catches and the two mutations of its
own retirement rule (CR-15 M-2), whole-line retention and per-check-site header counts (CR-15 M-1), the alignment-histogram artifact, gen_tdd_step2b.md
Sections 16 and 17, the gen_mut_step2b.md landing-15 section, and the CM173 and CR-15 dispositions in gen_critic_response_fu2a.md. Known: the DV Lead's
three citations of the retired trace log dangle until its next touch. This verdict lifts or keeps the gate on the gen_l14 testlist merge.

Artifacts reviewed (committed blobs at 5eb7ddb; sha256 first 16 hex):

- dv/auto_dv/tb/gen_icache_ram.sv  9e5770ded0ff84a6
- dv/auto_dv/tb/gen_ic_lookup_probe.sv  466e59e7e74606df
- dv/auto_dv/tb/gen_tb_pkg.sv  8b2fd577f2b46db6
- dv/auto_dv/tb/gen_protocol_props.sv  f77b58c15fa0fa14
- dv/auto_dv/tb/gen_tb_knobs.yaml  aa0b4ff6f3bac3e8
- dv/auto_dv/gen_tb/gen_knobs.py  c5fcc3e7c375d0ff
- dv/auto_dv/env/gen_checkers_pkg.sv  ee64c4f8212bbc1b
- dv/auto_dv/evidence/gen_tdd_step2b.md  ba053891308bc224
- dv/auto_dv/mutations/gen_mut_step2b.md  739a593d9af9fc22
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  0c01429e9b470d77
- dv/auto_dv/docs/gen_component_api_misc_monitor.md  28c6eddc722865f2
- dv/auto_dv/docs/gen_probe_register.md  213f39283df70acf
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  5ecb5327f66dc2ac
- dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l16_sources_sha256_w18.txt  cff50f81508de1a9
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l16_trace17_lookup_tag_histogram.txt  a72a8a0a4c1f27cf
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l16_trace17_duplicate_copies.log  23f17849bdfc0b71
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l16_RETSEQ_npf_mutant.diff  85ac9874ab725e6f
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l16_RETIDX_npf_mutant.diff  c8c32a352df079c8
- dv/auto_dv/work/tb-infra/gen_landing15_files.txt  d96355752253a11c (gitignored work file named by the Orchestrator, read from the shared tree; sha256 of the working copy)
- dv/auto_dv/work/tb-infra/gen_landing15_hashes.txt  c8ffccf89309d7df (gitignored work file named by the Orchestrator, read from the shared tree; sha256 of the working copy)
- dv/auto_dv/work/tb-infra/gen_landing15_deletes.txt  a41de98ab9282f0d (gitignored work file named by the Orchestrator, read from the shared tree; sha256 of the working copy)
- the 166 gen_fu_l16_* files under dv/auto_dv/evidence/gen_tdd_logs/{lockstep,mutations,fcov}/ (manifest rows recomputed by me: 166 size and md5 matches, 0 mismatches)

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; LOG-067, LOG-079;
gen_critic_tb_l15.md (8e5b3a3e0d280c0a, the verdict under re-review); rtl/ibex_icache.sv:327-350, :385-397, :474-490, :499-513, :585, :589-594 (read for
tb_l15; the geometry parameters ADDR_W, IC_INDEX_HI, IC_INDEX_W, IC_LINE_W, IC_TAG_SIZE from ibex_pkg give 21, 20, 7 and 3 under this configuration).
Method: detached git worktree of 5eb7ddb. The landing list checked against the diff: 69 added + 77 modified = the 146 listed files, 146 of 146 md5s
OK at 5eb7ddb; 21 deleted = the deletes list, 0 mismatches either way; the diff holds no rtl/ file. Build w18 identity first-hand: the recipe on the
tree gives cff50f81508de1a9 under the UTF-8 sort, equal to the 13 evidence headers, the compile log and the sha256 of the retained 75-row list,
byte-identical to my recompute: the landing's build is the committed tree. Library and flow self-tests PASS; both codegen --check up to date; both
codegen unit tests PASS. Re-derived by me with one command each: the 38-header build histogram; each of the 13 mutant and trace per-file lists
differs from w18's in exactly the named file and hashes to its header's and compile log's sha; the 12 catch totals from the verdict files and the
12 ablation PASS lines; the per-site counts in the 12 catch headers; the a / b agreement, duplicate-copy, latency and judged fields of the 13
summary lines; the plusargs (12 catches +gen_chk_all=0 +gen_chk_alert_minor=1, 12 ablations alert_minor=0, 0 of 14 probe-off headers naming the
probe, 18 probe-on headers); 38 of 38 excerpt headers say counted by python and 38 of 38 say the summary line is kept whole; the first 400
characters of the 13 summary lines equal the w16 lines retained at 7d4561f (13 of 13); the histogram and duplicate-copy artifacts. One unnamed
sonnet subagent (LOG-083a/b) recomputed the manifest, the histogram attribution and the program ties against expected values stated in its brief
with `command grep -a`; every count of its that enters this verdict was re-derived by me. EXPOSURE: none beyond the Orchestrator's sha-and-scope
message and the git log subjects. The cross-model review of this range was running in parallel; Section 6 says whether its artifact was read.

CRITIC VERDICT: APPROVE. Both mediums of tb_l15 are answered with retained evidence: the summary lines are kept whole and every figure Section 16
quotes is in them; form (b), the judge measured runs use, now has reds of its own (RETSEQ and RETIDX, mutations of its retirement rule, caught
probe-off on the far program with the referees inert, ablations at 0) beside four probe-off data reds. The eight lows and I-1 are closed. Three new
lows, none touching the evidence itself, plus two adopted from the cross-model review after Sections 1-5 were written (the trace session's source
delta unretained; the alert_minor row without a pointer to its reach section). The gate on the gen_l14 merge lifts.

## 1. What was verified

| item | as built at 5eb7ddb | evidence (retained, re-derived by me) |
|---|---|---|
| CR-15 M-1: the figures retained | the excerpt tool keeps a GEN_MISC summary line whole (688..719 characters on the 13 evidence excerpts; every other line capped at 400, line 2 of every excerpt says so) | ecc_data_freq: judged=904 hit_way=494 other_or_invalid_way=410 unjudged=0 (ambiguous 350) missing=0, hits=494, visible=16 masked=4, both=554 agree=554, latency 7..16; noprobe 148 / 406 / 350; two 899 / 436 / 463, 434, 583 / 583, 20 / 2; both 925 / 912, 902 / 445, 1309, 575 / 575, 19 / 14; rare 27 / 14 / 13, 14, 20 / 20; tag_freq_probe and green_h1 925 / 915 / 906; tag_two 940 / 931 / 916; far 619 / 180 / 438 / 1, 180, 174 / 174, latency 4..25; far noprobe 27 / 147 / 445; far both 598 / 583, 613 / 172 / 2 pending, 742, 185 / 185: every figure Section 16 quotes is in the retained line |
| the alignment histogram | gen_fu_l16_trace17_lookup_tag_histogram.txt: tag 00100000 in 20448 cycles, 00000000 in 61, of 20509 lookup lines (20448 + 61 = 20509), from the trace17 session on w18 (build 74c372d4823c6bc1, its own compile log, 75-row list differing from w18 in gen_tb_pkg.sv only, one green run) | the file; the ALIGN mutation's silence on the one-region program is now checkable |
| the duplicate copies (WP12-F2) | gen_fu_l16_trace17_duplicate_copies.log: 20 announced injections with both ways valid under one tag (17 at index 26, 3 at 27) = ecc_data_freq's 16 visible + 4 masked | two independent artifacts agree; the earlier one-index filter retired |
| CR-15 M-2: form (b)'s own reds | RETSEQ (`if (rt_disc[k]) return -1` made `if (0)`: the sequential-flow requirement dropped) 71 errors = 664: 42 + 687: 29; RETIDX (the index match made `if (1)`) 22 = 664: 10 + 687: 12; both on gen_icache_ecc_far_directed.S probe OFF, +gen_chk_all=0 +gen_chk_alert_minor=1, ablations PASS 0; neither touches the RAM model | the diffs, the verdicts, the headers; with the probe off nothing but the retirement stream decides the hit way, so these are the reds tb_l15 asked for |
| probe-off data reds | DATAMISS 150 (one-region) and 21 (far), DATAWAY 557 = 660: 453 + 687: 104 (one-region) and 49 = 664: 26 + 687: 22 + 660: 1 (far), all probe OFF, ablations PASS 0 | the verdicts and headers; the 660 count under DATAWAY is the announcement landing on an invalid way, which is no candidate (the RED0 diff's `valid_w[way]` term) |
| the six landing-14 mutants on w18 | RED0 988 = 494 + 494, DATAANN 494, DATAMISS 483, DATAWAY 830 = 453 + 377, BITS 930 (site 682), ALIGN 13 (site 664): the w16 counts reproduced exactly | 12 catches, 12 ablations; every catch and ablation pair carries one build sha that equals its list's sha256 and its compile log's line |
| CR-15 L-1: per-site counts | every catch header carries "counted by python: N" and the per-site counts with a digit-normalised message sample; sums equal totals on all 12 | re-derived |
| CR-15 L-2: unidentified builds | 21 files retired with their manifest rows (the two w11 runs and driver log, the w14 run, the nine trace-copy files, the w16 identity pair); every fact re-proved on w18: the mis-association red became RETSEQ / RETIDX, the trace evidence one identified session, the pulse-window observation demoted to a development note | the deletes list = the diff's 21 deletions; 0 manifest rows name a retired file; w16's identity remains recoverable from the tree at a28d1ae (tb_l15 verified it first-hand) |
| CR-15 L-3: the reach | Section 17 and the new Section 5a of the misc-monitor doc: 554 of 904 (61.3 percent) and 174 of 619 (28.1 percent) decided probe-off; of the injections that owed a pulse 148 of 494 (30.0) and 27 of 180 (15.0); Q-019 named as what would raise it | the noprobe lines (148 + 406 = 554, 27 + 147 = 174) and the probe-on hit-way counts; arithmetic checked |
| CR-15 L-4 | the trace session is one green run, no seventh ablation; the C10 note in gen_protocol_props.sv names P9 beside B8 as a second read-only bind carrying no property | the diff |
| CR-15 L-5 / CM173 m-1 | gen_icache_ram.sv:92 `[IC_TAG_SIZE-2:0], addr[IC_INDEX_W-1:0], {IC_LINE_W{1'b0}}`; gen_ic_lookup_probe.sv TagW = ADDR_W - IC_INDEX_HI - 1 | equal to 20, 7, 3 and 21 under this configuration; the 13 summary lines equal the w16 lines on their retained first 400 characters (13 of 13) and the six mutant counts reproduce: the change is measured behaviour-preserving |
| CR-15 L-6 / L-7 / L-8, I-1 | Section 16 says the seven entries are a gitignored work file parked under the gate; the P9 row says built in the misc monitor as tag_b / verdict_b; the CM171 (first) row reads "never takes a pulse from an owed injection"; 38 of 38 headers say counted by python | the diffs and the headers |
| the P9 conditions (LOG-079) | unchanged: read-only bind, knob default off and debug_only, the knobs unit test PASS on the debug_only list equality | self-tests |

## 2. Closure of tb_l15

CR-15 M-1, M-2, L-1..L-8 and I-1 CLOSED; I-2..I-4 recorded. The REQUEST-CHANGES of tb_l15 is lifted by this verdict.

## 3. Findings

### L-1 (low) [S4 record] Two readers called checked-in are not in the tree

gen_tdd_step2b.md:768 says every figure is "re-derived from the retained line by a checked-in reader (scratchpad/gen_l15_figures.py)" and
gen_mut_step2b.md:237 and the CM173-M-1 row name scratchpad/gen_l15_mut_identity.py and gen_l15_figures.py; `git ls-files` at 5eb7ddb holds neither.
The figures and the identities do not depend on them (I re-derived both from the retained files with shell commands), so this is the record's
description of its tooling, not its evidence. Commit the two readers under dv/auto_dv/work/tb-infra/ or say "scratchpad reader, not retained".

### L-2 (low) [S4 record] The landing-14 mutant table names builds and file contents that no longer exist

The landing-14 section of gen_mut_step2b.md keeps its six rows with the w16 mutant build shas (d1d9020eb7b548a6, 7d89695d799dc0b9, 1961cbb8fdbb2913,
97a589a799b81066, 21b77abf9c06b6f8, da54df85425870e4) and the gen_fu_l16_<M>_catch_* file names; those files now hold the w18 re-runs (c048df91ff5107ff
and the others) and the w16 identity pair is retired. The heading points at the landing-15 table but the rows are not marked. One line under the table:
the files named here hold the landing-15 re-runs; the w16 identity is the tree at a28d1ae.

### L-3 (low) [S4 record] "Byte-identical to w16's on all 13" rests on the scratch logs beyond 400 characters

Section 16 says the 13 w18 evidence runs "give summary lines byte-identical to w16's on all 13". The w16 lines retained at 7d4561f are the 400-character
cuts, so the retained comparison reaches 400 characters (13 of 13 equal, my check); the rest was compared against the scratch logs, which are not
retained. The six landing-14 mutants reproducing their counts is retained evidence of the same point. Say "identical on the retained 400 characters and
in every re-derived figure".

### Informational

- I-1: gen_feature_list.md:11362 and gen_test_plan.md:438 and :17853 cite the retired gen_fu_l16_TRACE_index26.log; known, the DV Lead's next touch.
- I-2: the compile logs carry the sources sha on their last lines, not the first; the identity check reads it wherever it is.
- I-3: DATAWAY on the far program probe-off fires site 660 once: the announcement moved to a way that was invalid, so the window held no candidate; a
  correct reading of the checker, recorded here so the split is not mistaken for a defect.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S6 trust triad: form (b) now has two named mutations of its own rule caught with the
referees inert, ablations PASS, on identified builds whose lists differ from w18 in the named file only (conforming; tb_l15 M-2 closed). S4 honesty:
unidentifiable evidence retired and re-proved rather than kept, the pulse-window observation demoted, the reach stated as the checker's power
(conforming; L-1..L-3 are wording). S5 single source: the geometry from ibex_pkg (conforming). S2: unchanged from tb_l15. One-line verdict: PASS.

## 5. Verdict

CRITIC VERDICT: APPROVE. Lows L-1..L-5 (L-4 and L-5 adopted, Section 6) with the next touch. The gate on the gen_l14 testlist merge lifts.

## 6. Reconciliation with the cross-model review of the same range

Read after Sections 1-5 were written: dv/auto_dv/reviews/2026-09-04-claude-diff-7d4561f1-5eb7ddbb.md (sha256 8370f14d1d0d5e13, 38 lines, committed
30b4b8b; claude CLI, fresh session, codex at its spend cap), APPROVE-WITH-CHANGES with five minors. Its confirmations (the geometry values from
rtl/ibex_pkg.sv, the 13 lists differing in one file, the RETSEQ / RETIDX diffs inside tag_b, every Section 16 figure in the whole lines, the manifest,
the three DV Lead citations) agree with Section 1.

- Minor 1 is my L-2 (the landing-14 table's w16 shas). Its sharper point is adopted: the rows break the section's own rule at gen_mut_step2b.md:210,
  since no retained header carries those shas any more. Same fix.
- Minor 2 is my L-1 (the untracked readers) and adds that gen_tdd_step2b.md:816 and the CR-15-L-2 row cite dv/auto_dv/work/tb-infra/gen_landing15_deletes.txt,
  which dv/auto_dv/.gitignore excludes (verified: `git check-ignore` names it; 0 gen_landing15 files tracked). Adopted into L-1: the record cites a
  path a reader of the tree cannot open, the shape of CM173-m-2; the deletion set is recoverable from the diff itself (21 deletions, checked), so name
  the diff or commit the list. My header's three list lines are marked accordingly (working-copy hashes of gitignored files named by the Orchestrator).
- Minor 3, the trace session's source delta is not retained: the trace17 list shows gen_tb_pkg.sv differing from w18, the old gen_fu_l16_TRACE_mutant.diff
  is retired and no gen_fu_l16_trace17_mutant.diff replaces it (verified: seven trace17 files, no diff), so "only the TRACE displays applied" is a claim.
  Adopted and verified as L-4 (low) [S6 identity]: the two figures the session produced cross-check against w18's own ecc_data_freq counts (16 + 4 = 20)
  and the one-region program's single tag, which is why it stays low; retain the applied diff as for every other out-of-tree copy.
- Minor 4, the alert_minor row (gen_component_api_misc_monitor.md:54) carries no pointer to Section 5a or to the reach figure, while CM173-M-2 asked
  for the fraction in the API row: adopted and verified as L-5 (low) [S4 record] (the row's line holds no "5a"; the only line naming both is the
  Section 5a heading). One clause in the row's data-half sentence pointing at Section 5a.
- Minor 5 is my L-3 (the byte-identical claim). Same fix.
- Not in the cross-model review: nothing of mine beyond the informational items. Verdicts agree in substance: both approve; it carries changes as minors,
  I carry them as lows L-1..L-5. The gate on the gen_l14 merge lifts under both.
