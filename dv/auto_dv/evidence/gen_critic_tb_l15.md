# Critic verdict: tb-infra landing 14, WP-12 (commit a28d1ae, diff base 508ffbc), reviewed as tb_l15

Scope (the Orchestrator's): the data-RAM ECC injection hook and its two hit judges (form a, the P9 probe; form b, the retirement stream), the P9
lookup-address probe under the LOG-079 conditions, the far directed program, gen_tdd_step2b.md Section 16 and the gen_mut_step2b.md landing-14 section
against the gen_fu_l16_* logs (build w16), the rows CM169 / CM170 / CM171 (fu2a) and CM165 / CR-14 (fcov), the findings WP12-F1 / F2 / F3, and
Runtime's one-line testlist change (gen_probe_ic_lookup added to debug_only_plusargs) that lands with it. Known and owed elsewhere, not findings here:
the excerpt headers' "counted by grep" wording, CG-IC-006's sampler (WP-8), the probe-on entries unmeasured pending Q-019. This file sits under
dv/auto_dv/evidence/ at the Orchestrator's instruction (earlier verdicts sit under dv/auto_dv/docs/).

Artifacts reviewed (committed blobs at a28d1ae; sha256 first 16 hex):

- dv/auto_dv/tb/gen_icache_ram.sv  ed2f15766dd7d225
- dv/auto_dv/tb/gen_tb_pkg.sv  1e28c45499a85c3e
- dv/auto_dv/env/gen_checkers_pkg.sv  ee64c4f8212bbc1b
- dv/auto_dv/tb/gen_ic_lookup_probe.sv  aaa41bc33531e074
- dv/auto_dv/tb/gen_binds.sv  25567cadebc11201
- dv/auto_dv/tb/gen_tb_knobs.yaml  fb0d612922a189f8
- dv/auto_dv/gen_tb/gen_knobs.py  f9cb1ab896779405
- dv/auto_dv/tb/gen_env_cfg_knobs.svh  e99dab7d64116b25
- dv/auto_dv/flow/gen_testlist.yaml  77f93865ec8f930b
- dv/auto_dv/env/gen_env_pkg.sv  b741a6ea75d47475
- dv/auto_dv/env/gen_fcov_pkg.sv  75138bb00d6cb3fa
- dv/auto_dv/stim/gen_directed/gen_icache_ecc_far_directed.S  de2d6aa9c83cbc56
- dv/auto_dv/stim/gen_directed/gen_icache_ecc_directed.S  3cbeb83684a67946
- dv/auto_dv/evidence/gen_tdd_step2b.md  5c6bd2eea3214233
- dv/auto_dv/mutations/gen_mut_step2b.md  cb9551ac02dae9f6
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  066eb7e7b773c7b6
- dv/auto_dv/evidence/gen_critic_response_fcov.md  29ebac847f88868e
- dv/auto_dv/evidence/gen_tdd_fcov.md  cdbb21460a53f0f1
- dv/auto_dv/docs/gen_component_api_misc_monitor.md  57b4a027d8852844
- dv/auto_dv/docs/gen_component_api_binds.md  291454068fbf3280
- dv/auto_dv/docs/gen_probe_register.md  baeffa81ba34347e
- dv/auto_dv/docs/gen_component_api_fcov.md  72a208329579ad35
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  ce917bff26c4b076
- dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l16_sources_sha256_w16.txt  de983a8e68063c27
- the 118 gen_fu_l16_* files under dv/auto_dv/evidence/gen_tdd_logs/{lockstep,mutations,fcov}/ (manifest rows recomputed 118/118) and the five re-stamped gen_fu_l15_slice6*_red_check_b12x.log

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; LOG-067, LOG-079;
rtl/ibex_icache.sv:251-252 (the lookup address and index), :327-350 (the data tweak: the line address at every beat's offset), :385-397 (the tag tweak: the
index at every beat's offset), :474-490 (lookup_addr_ic1 registered on the lookup grant), :499-513 (tag match against {1, tag}; the hit-data mux ORs the
matching ways' un-tweaked words), :585 (a data error counts only on a hit), :589-594 (the correction invalidates the matching ways).
Method: detached git worktree of a28d1ae. Build w16 identity first-hand: the recipe of gen_tb_local.sh on the tree gives de983a8e68063c27 under the
UTF-8 sort, equal to the 13 w16 run headers, the compile log and the sha256 of the retained 75-line list, byte-identical to my recompute: the landing's
build is the committed tree. Library and flow self-tests PASS; both codegen --check up to date; the fcov codegen unit test PASS; the knobs codegen unit
test PASS (it requires the testlist's debug_only_plusargs list to equal the knobs marked debug_only, which is why Runtime's line lands here). The hook,
the tweak model, the two judge forms and the pulse attribution were read in the diff and checked against the RTL lines above; the counts below were
re-derived by me with one command each (the 118 / 118 manifest rows and files, the 30-header build histogram, the seven mutant totals from the
verdict files, the 400-character length of every GEN_MISC summary line in the sixteen excerpts, the absence of the a / b agreement and duplicate
figures from every retained file). One unnamed sonnet subagent (LOG-083a/b) recomputed the manifest md5s, the header histogram, the GEN_MISC
figures, the mutant identities and the program ties against expected values stated in its brief, with `command grep -a` over the logs; every count it
returned that enters this verdict was re-derived by me. EXPOSURE: none beyond the Orchestrator's sha-and-scope message and the git log subjects naming
review levels. The cross-model review of this range was running in parallel; Section 6 says whether its artifact was read.

CRITIC VERDICT: REQUEST-CHANGES. The hook, the tweak model, the P9 probe and the two judge forms are built as the plan owner's rulings and the RTL
ask, and the mutants prove the hit judgement with the probe on. One medium: the figure the record offers as the proof that the measured-run judge
(form b) is right, forms a and b agreeing on every double-judged injection (554 / 554, 583 / 583, 575 / 575, 174 / 174, 185 / 185, 20 / 20), is in no
retained file: every GEN_MISC summary line in the sixteen excerpts is cut at 400 characters before the agreement and duplicate-copy fields, and no
other log carries them. A second medium, adopted from the cross-model review after Sections 1-5 were written and verified by me: the five data-side
mutants (RED0, DATAANN, DATAMISS, DATAWAY, ALIGN) all ran with +gen_probe_ic_lookup=1, where form (a) decides, so form (b) has no catch evidence of
its own. Four lows, plus four adopted from the cross-model review.

## 1. What was verified

| item | as built | anchor | evidence |
|---|---|---|---|
| the data-RAM hook | gen_icache_ram.sv (IsTag = 0): at knob_icache_data_ecc_err_rate's rate_per_mille a read is corrupted in one beat by one or two distinct positions (knob_icache_ecc_bits), each instance on its own xorshift stream (WP12-F1); the announcement carries cycle, way, index, beat, bits, qualified, every way's un-tweaked valid bit and tag from the tag shadow, and whether a flipped bit rose in the un-tweaked data word | rtl/ibex_icache.sv:327-350 (data tweak = the line address at each 39-bit beat's base; the TB's data_tweak matches), :385-397 (tag tweak = the index at each (IC_INDEX_W + IC_TAG_ECC_SIZE) offset; the TB's tag_tweak matches) | MUT-ICE-DATA-ANN 494 `without an announced ECC injection`; MUT-ICE-DATA-MISS 483 `missing within`; MUT-BITS 930 `missing within` (two bits on the tag path); all ablations PASS 0; the mutant builds' lists differ from w16 in the mutated file only; canaries hash the mutated file (gen_icache_ram.sv ed2f15766dd7d225 = the committed blob) |
| the hit judgement | the DUT checks data ECC only on the way the lookup hit, and ORs the matching ways' un-tweaked words; hit way = the way whose stored {valid, tag} equals {1, lookup tag}; one match: the injected way must be it; several (duplicate copies): the injected way must be one and a flipped bit must have risen | :499-513, :585 (verified) | MUT-ICE-WAY (the announcement names the other way) 830 errors (453 + 377), ablation PASS |
| form (a), the P9 probe | gen_ic_lookup_probe.sv bound into ibex_icache: inputs only, no assertion, publishes lookup_addr_ic1 each cycle while +gen_probe_ic_lookup=1; the tag of cycle c + 1 belongs to the read at c | :474-490 (lookup_addr_ic1 registered on the grant); LOG-079: read-only, default off, debug_only, the P9 row APPROVED, the bind header records the exception | MUT-ALIGN (the tag of c + 2) 13 errors on the far program, silent on the one-region program and said so; the knobs unit test enforces the debug_only list equality; the testlist line is Runtime's one file |
| form (b), the retirement stream | the first retirement after the read whose pc line index equals the injected index reveals the tag, provided it and every retirement between are sequential flow; a discontinuity first = ambiguous (unjudged, excuses a pulse, fails nothing); none within GEN_ICACHE_RETIRE_WINDOW = 64 = unjudged; the run's end = pending | the plan owner's form (b) (LOG-079) | the w11 red of the earlier rule (a jump retiring right after the read taken as the revealing retirement: 30 errors on the far program probe-off, 32 of 243 disagreements probe-on), fixed by requiring the revealing retirement to be sequential; greens probe-off: 0 errors |
| pulse attribution | a pulse's window is the GEN_ICACHE_ECC_WINDOW cycles before it (the read cycle excluded); held while a valid-way data injection in it has no verdict; credited to the nearest owing injection (a qualified tag injection, a hit-way data injection), else the nearest excusing one (an unqualified tag injection, an unjudged data injection); a none-owed verdict never consumes; a pulse nobody owes or excuses is an error; an owed injection without its pulse is missing | plan v3x, CM169-L-1, CM170, CM171 (the rows read against the code: as built) | RED0 (the monitor before the data half) 988 = 494 + 494; the w14 run's 11 pulses shifted by the read-cycle exclusion |
| the tweak shadow | gen_icram_events keeps every tag write (the reset sweep and the correction writes included) and un-tweaks by index; the data word beside an invalidation or correction tag write lands under the zero tweak in a way that write invalidates (CM169-L-2, stated) | :327-333 (data_address zero on inval / ecc writes) | consistent |
| greens on w16 | ecc_data_freq 904 judged / 494 hit way / 410 other or invalid / 0 unjudged (350 ambiguous for b) / 0 missing, 494 pulses; noprobe 148 / 406 / 350 unjudged; two bits 899 / 436 / 463, 434 pulses; both 925 tag (912 qualified) and 902 data (445 hit), 1309 pulses; rare 27 / 14 / 13; the tag half 925 / 915 / 906 (pair counting fixed, WP12-F1); far 619 / 180 / 438 (165 a valid way that lost) / 1 pending, 180 pulses; far noprobe 27 / 147 / 445 unjudged; far both 598 / 583 tag, 613 / 172 data, 742 pulses; 0 errors on every green | Section 16 | every figure above matched by the subagent against the summary lines and re-derived by me for the three noprobe / rare tails; the a / b and duplicate figures: M-1 |
| findings | WP12-F1 (both instances on one $urandom stream: pair injections; fixed, the tag half's 870 were pair counts), WP12-F2 (a DUT corner: a second copy of a valid line allocated after a correction refetch; the judge owes a pulse only when a flipped bit rose), WP12-F3 (a block-local initializer is static, twice) | honest records; F2 routed to the plan owner and rtl-arch | the TRACE copy's index-26 filter (gen_fu_l16_TRACE_index26.log) |
| folded rows | CR-14 L-1..L-5 (the not-reached prose, sb3, the five reds re-stamped and their urg commands retained, the imm / divt images named, the sparse regime), CM165 L-1..L-3 and I-1 (c.lui's rs1 fixed with two unit rows), CM169 / CM170 / CM171 as built | tb_l14 | the diffs; the re-stamped reds' rows recomputed |

## 2. Closure of the base verdicts

- gen_critic_tb_l14.md: L-1..L-5 CLOSED (L-3 with the reds re-stamped and the b12x urg commands retained; L-6 the c.lui fix with two rows).
- The tb_l12 / tb_l13 items folded earlier stay closed; the excerpt headers' wording is owed to the next landing as the Orchestrator said.

## 3. Findings

### M-1 (medium) [S4 record; S6 retention] The measured-run judge's validation figures are in no retained file

Section 16 rests the correctness of form (b), the judge measured runs will use, on its agreement with the probe: "forms a and b both judged 554 and agreed
on all 554" (ecc_data_freq), 583 / 583, 575 / 575, 174 / 174, 185 / 185, 20 / 20, and on the duplicate-copy counts (16 / 4, 20 / 2, 19 / 14). Every
GEN_MISC summary line in the sixteen gen_fu_l16 excerpts is exactly 400 characters long (my count on all sixteen), cut before the a / b and duplicate
fields ("... missing=0 other_w" on ecc_data_freq, "other_way_pulses=" on ecc_data_rare), and `command grep -a` for the words over every gen_fu_l16 file
finds them only in compile logs, mutant diffs and the excerpts' own descriptive headers (the ecc_data_freq header states the agreement; the run output below it does not). Under the team's rule an
unretained figure counts as nothing, so the record's proof that form (b) equals form (a) is a claim. Form (b) has a red (the w11 mis-association, 30
errors) and greens (0 errors probe-off), which stand; the agreement statistics do not. Required: the excerpt tool keeps the whole summary line (or the
summary is split over lines under 400 characters), the agreement and duplicate counters re-retained from the same runs, and the record's figures cited
to those lines.

### L-1 (low) [S4 record] Message-kind splits from twelve-line samples

The mutant rows give kinds per mutant (RED0 494 `without an announced` + 494 `missing within`; MUT-ICE-WAY 453 + 377; the w11 probe-off red 12 missing
+ 18 unowed). The totals are the verdict files' UVM_ERROR counts (988, 830, 30: re-derived); the splits are not: the excerpts keep the first twelve
lines (RED0's alternate 6 / 6, MUT-ICE-WAY's read 9 / 3, the w11 run's 9 / 3), and no retained line counts the kinds over the whole run. Count the kinds
in the excerpt header ("of them <kind>: N", the B8 form) or retain the checker's own per-kind counters.

### L-2 (low) [S6 identity] Builds behind reds and a finding without lists or compile logs

The w11 runs (88b4dfef94d52a84, the form-b mis-association red) have the driver log's "sources sha256" line and no compile log or per-file list; the w14
run (da2b53697542119c) has only its header, excerpt and verdict; the TRACE copy (bddc7925e4b5752e, the evidence of WP12-F2) has its compile log and
diff but is a copy of the w6 sources, an earlier build with no retained list, and gen_fu_l16_driver_trace.log describes a different session (mut_root/TRACEX
with three sub-mutations over gen_tb_pkg.sv, gen_checkers_pkg.sv and gen_icache_ram.sv) whose original sha for gen_tb_pkg.sv (61072aae763ab440) is w6's,
not the committed 1e28c45499a85c3e. The reds and the finding are real; their builds are identified by a header sha alone. Retain the list and the
compile log of every build whose run a record cites (tb_l12 L-6, again), and a driver log that describes the retained TRACE run.

### L-3 (low) [S2 coverage of the measured-run judge] Form (b) judges few injections on a jumpy program

On the far program probe-off, 445 of 619 valid-way data injections are unjudged (ambiguous 444: a jump every 14 instructions) and 174 are judged; on the
one-region program 350 of 904. Every unjudged injection excuses a pulse, so on control-flow-dense code the measured-run judge is largely silent and a
missing pulse there would not fail. Section 16 says so implicitly ("the jump every 14 instructions makes most associations ambiguous"); state it as
the judge's coverage figure in the API doc (the fraction judged per program) so a measured run's verdict is read with it, and record Q-019's outcome as
the way to raise it.

### L-4 (low) [S4 record] Ablation count and a stale statement

The landing-14 mutant table lists six mutants; seven ablation runs are retained (TRACE's included, PASS 0), and the TRACE catch run carries 10 errors
(the trace copy's own reds on the pre-fix w6 sources) with no row describing what those errors are. The binds doc's "the second and only other bind that
reads DUT internals" is true; the SVA layer header (gen_protocol_props.sv) still names the B8 probe as "the one property over DUT internals" and should
name P9 too, since LOG-079 puts the exception on the LOG-067 path.

### Informational

- I-1: the excerpt headers say "counted by grep" on all 30 gen_fu_l16 excerpts (my count) while the record says python counted; known and owed, the
  numbers equal the UVM summaries.
- I-2: the ALIGN mutant is caught only on the far program, and the record says why (the one-region program's tag never changes between consecutive
  lookups): the alignment proof rests on one program, honestly.
- I-3: WP12-F2 is a DUT corner (a second valid copy of a line after a correction refetch; the hit mux ORs the copies, rtl/ibex_icache.sv:507-513): the
  judge handles it and the record routes it to the plan owner and rtl-arch; the routing is the right form for a finding outside the TB's remit.
- I-4: Runtime's testlist line is the only non-tb-infra file and exists because the knobs unit test requires the two debug_only lists to agree; the
  joint landing is the honest form.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S2 derive from intent: the hook and both judge forms follow the plan owner's rulings and
cite the RTL lines that define the hit and the tweaks (conforming; L-3 on the measured-run form's reach). S6 trust triad: RED0 and five mutants with
ablations on identified builds, the alignment mutant on the program that can catch it (conforming); the validation figures of form (b) unretained (M-1);
three builds without lists (L-2). S4 honesty: the three findings recorded against the TB and the DUT (conforming); the kind splits and the TRACE row
(L-1, L-4). One-line verdict: FAIL on M-1 until the figures are retained.

## 5. Verdict

CRITIC VERDICT: REQUEST-CHANGES (M-1, M-2 adopted). Lows L-1..L-4 and the adopted lows with the same touch. The source is not in question; the
retention and the mutation evidence of its measured-run form are.

## 6. Reconciliation with the cross-model review of the same range

Read after Sections 1-5 were written: dv/auto_dv/reviews/2026-09-04-claude-diff-508ffbc2-a28d1ae7.md (sha256 04db108b1ae44d48, 37 lines, committed
96bb84c; claude CLI, fresh session, codex at its spend cap), APPROVE-WITH-CHANGES with two majors and four minors.

- Its first major is my M-1 (the Section 16 figures unretained). It names more unretained figures than I did: form (b)'s latency 7..16 and minimum 4,
  and the alignment histogram "00100000 in 20448 of 20509 cycles" (gen_tdd_step2b.md:702, :713). Adopted and verified: `command grep -al 20448` over
  the gen_fu_l16 files finds nothing (20509 alone appears in three excerpts as a cycle count). M-1 covers them.
- Its second major is adopted as M-2 (medium) [S6 trust triad]: the five data-side mutants (RED0, DATAANN, DATAMISS, DATAWAY, ALIGN) carry
  +gen_probe_ic_lookup=1 in their catch and ablation headers (verified, six pairs read: BITS carries no probe plusarg and is tag-only), so every red of
  the data judgement was decided by form (a) and form (b), the form measured runs use, has no mutant that it alone catches. Form (b) has a red (the w11
  mis-association, 30 errors probe-off) and greens; a mutant of the retirement rule (the sequential-flow requirement or the index match) run probe-off
  on the far program, caught by form (b) with the referees inert, is owed before a measured entry relies on it. I under-weighted this as L-3 (its
  reach); the missing red is the sharper finding.
- Minor 1, hand-encoded widths (gen_icache_ram.sv:92 `[20:0], addr[7:0], 3'b000`; gen_ic_lookup_probe.sv:9 `TagW = 21`): adopted and verified as L-5
  (low) [S5 single source]: derive from ibex_pkg (IC_TAG_SIZE, IC_INDEX_W, IC_LINE_W).
- Minor 2, gen_tdd_step2b.md:739 names gen_l14_testlist_entries.yaml, which `git ls-files` at a28d1ae does not hold: adopted and verified as L-6 (low)
  [S4 record]: name the staged file's location or commit it with the entries.
- Minor 3, the P9 row's boundary column says form (b) is "not built here" (gen_probe_register.md:31) while this landing builds it: adopted and verified as
  L-7 (low) [S4 record].
- Minor 4, the CM171 (first) row says "an unqualified tag injection never consumes a pulse" (gen_critic_response_fu2a.md:195) while as built it sits in
  the excusing tier and absorbs a pulse nothing owes (gen_checkers_pkg.sv:631): adopted and verified as L-8 (low) [S4 record]: "never takes a pulse from
  an owed injection".
- Not in the cross-model review: L-1 (kind splits), L-2 (builds without lists; the TRACE driver log), L-3 (form (b)'s reach), L-4 (the seventh ablation
  and the SVA header). Its rubric results (rtl-purity PASS, forces-and-hier-access PASS on the read-only bind, assertion-integrity PASS) agree with
  Section 1.
- Verdict difference: it approves with changes; I request changes, because M-1 removes the retained proof of the measured-run judge and M-2 shows that
  judge has no red of its own, and the team's rule counts an unretained claim as nothing. Both go to the Orchestrator as the recorded verdicts.
