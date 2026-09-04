# Critic verdict: tb-infra landing 12, Slice A part 2 (commit ba3799b, diff base 0778d23), reviewed as tb_l13

Scope (the Orchestrator's): CG-CMP-009 gen_cmp_zcmp_hazard_cg (sampler, rendering, the renderer's IMPLEMENTED list) with its trust triad on build b12x
(three gen_fcov_proof_slice5e* manifests, the sampler unit test, mutant FM16 with its ablation, 139 gen_fu_l14 logs); the directed program
gen_zcmp_hazard_directed.S; the T-235 sizing section (CM102-L-5); the CM148 rows and the records they correct.

Artifacts reviewed (committed blobs at ba3799b; sha256 first 16 hex):

- dv/auto_dv/env/gen_fcov_pkg.sv  802e323aab04ad8a
- dv/auto_dv/env/gen_fcov_groups.svh  c06a9a8b726c4ab5
- dv/auto_dv/tb/gen_fcov_codegen.py  072c7d6918da489e
- dv/auto_dv/stim/gen_directed/gen_zcmp_hazard_directed.S  e3b187f06c4d4d1c
- dv/auto_dv/evidence/gen_fcov_proof_slice5e.fcov.yaml  5fffc9539729eafa
- dv/auto_dv/evidence/gen_fcov_proof_slice5e2.fcov.yaml  781549ff93b28c16
- dv/auto_dv/evidence/gen_fcov_proof_slice5e3.fcov.yaml  2122f6b38f7519db
- dv/auto_dv/evidence/gen_fcov_proof_slice5e_fm16_ablation.fcov.yaml  75b32c321ead4689
- dv/auto_dv/evidence/gen_tdd_fcov.md  8664151b477a0a11
- dv/auto_dv/mutations/gen_mut_fcov.md  43492f05959ec3ed
- dv/auto_dv/evidence/gen_tdd_step2b.md  42af3d1a318f5d24
- dv/auto_dv/mutations/gen_mut_step2b.md  2223e0f19d3024cd
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  5518d04181403960
- dv/auto_dv/docs/gen_component_api_fcov.md  906fcf3187cc2f2f
- dv/auto_dv/docs/gen_component_api_isa_shim.md  4dc59495e1441fb9
- dv/auto_dv/docs/gen_component_api_scoreboard.md  9c6c02ed13b58beb
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  c9b5e2a03d212dbb
- dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l14_sources_sha256_b12.txt  57e0518a803da03b
- dv/auto_dv/docs/gen_fcov_plan.md  69b429210715adea
- the 139 gen_fu_l14_* files under dv/auto_dv/evidence/gen_tdd_logs/{fcov,mutations}/ (manifest rows recomputed 139/139)

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_fcov_plan.md
CG-CMP-009 (:785-800: the Sample line, the twelve pattern bins, the crosses and their ignores); tools/specs (Zcmp: the cm.push / cm.pop / cm.popret / cm.popretz
encodings funct3 101 with bits 12:8 = 11000 / 11010 / 11100 / 11110, cm.mvsa01 / cm.mva01s funct2 01 / 11, the rlist register sets ra, s0, s1, s2..s11);
rtl/ibex_id_stage.sv:1059-1062, :1117-1118 (the retired popret_ra_fwd path).
Method: detached git worktree of ba3799b. Build identity first-hand: the recipe of gen_tb_local.sh on the tree gives 57e0518a803da03b under the UTF-8 sort,
equal to the 36 run headers, the compile log and the sha256 of the retained 73-line list, byte-identical to my recompute (every listed file is the
committed blob: the landing's build is the committed tree). Library and flow self-tests PASS; both codegen --check up to date; the fcov codegen unit
test PASS; 19 covergroups and 2860 cross bins counted in the svh. The sampler's classifiers (zp_regs, hz_cm_kind, hz_rlist_cls) checked by me against
the Zcmp encodings and register lists; the FM16 canary hash compared with the committed gen_fcov_pkg.sv (802e323aab04ad8a, equal); the three proof
check logs, the unit-test case lines and the FM16 stamps read in the logs. One unnamed subagent (an evidence audit of the 139 files and the record
figures, told the fence, kept out of dv/auto_dv/reviews/), its findings re-checked where they carry weight. EXPOSURE: none beyond the Orchestrator's
sha-and-scope message and the git log subjects naming review levels; the CM148 rows quote the landing-11 artifact I had read for tb_l12. The
landing-12 cross-model artifact was not read before Sections 1-5; Section 6 reconciles.

CRITIC VERDICT: REQUEST-CHANGES. The hazard covergroup follows its plan Sample line in eleven of its twelve patterns, its proofs run on the
committed tree, its mutant is caught with a stamped ablation and a retained diff, and the CM148 record corrections are true of the artifacts. One
medium: the store_same_slot_then_pop bin matches any of the last 64 stores, and two of its three retained hits are stale-store matches, so the
bin's hits do not prove the plan's pattern (my finding, sharpened by the cross-model artifact's count, Section 5). Eight lows.

## 1. What was verified

| item | as built | intent anchor | evidence |
|---|---|---|---|
| sample point | one sample per pattern the sequence matches, at the last micro-op of a push / pop / popret / popretz (the Zcmp collector), at the move flush for the two move patterns, and pended to the next plain record for popret(z)_then_target (cp_ret_once: the next pc_rdata equals the loaded ra) | the plan's Sample: rvfi_ext_expanded_insn_last of any cm.*, the monitor's history identifying the neighbour pattern | greens on the directed program under three data-bus regimes: zcmp_hazard=41 / 41 / 34 samples, 0 mismatches |
| the twelve patterns | write_/load_pushed_reg_then_push from the instruction before the sequence against zp_regs(rlist); store_same_slot_then_pop against the last 64 plain-store words (M-1); push_then_pop_b2b / pop_then_push_b2b from the record before the first micro-op; popret_ra_deferred when the ra load's response latency exceeds one (the min1 response never defers, the plan's ignore); popret(z)_ft_cm with cp_ft_kind from the halfword at pc + 2 in the model's memory; load_then_mva01s and mvsa01_then_mva01s from the move collector's facts | the plan's bin definitions; the approximations (the 64-store window, the latency stand-in for "response after the addi entered ID", the fetch count for cp_redirect_once) stated in the API doc | all twelve hit in the default and long runs (urg: popret_ra_deferred 7, write_pushed_reg_then_push 8, ...), eleven in the min1 run (popret_ra_deferred 0, as the plan's ignore says) |
| classifiers | zp_regs: rlist 4 = {ra}, 5 adds s0 (x8), 6 adds s1 (x9), 7..14 add x18..x25, 15 adds x26 / x27: the Zcmp register sets (checked); hz_cm_kind: the four stack ops by bits 12:8 and the two moves by funct2 (checked); hz_rlist_cls 4 / 5..14 / 15 | the Zcmp spec | 10 unit rows (rlist 4 / 6 / 8 / 15, five halfwords, the classes), 84 cases 0 failures in five runs |
| rendering | 28 coverpoint bins, 74 cross bins with the CSV's tuples only; CG-CMP-009 in IMPLEMENTED; the group renders since plan v3f retired popret_ra_fwd | the renderer rules incl. Slice-A-1 | --check up to date; 19 groups; the codegen unit test PASS |
| proofs | slice5e (default: 26 bins), slice5e2 (long: 26, the deferral class), slice5e3 (same-cycle / min1: 24: no deferral, no long class), each on its own run; notes are the whole plan clause plus the lock-step sentence; the unowned cp_dmem_delay bins marked "credits nothing" | the plan's ignores | the three check logs PASS on 57e0518a803da03b; counts equal the urg group summaries (26 / 28 variables, crosses 35 / 74 and 30 / 74) |
| FM16 | the rlist class boundary off by one (rlist == 14 classed r15) | mutation-proof of cp_rlist_class | catch: slice5e FAILS on cp_rlist_class.r15 alone (r5_14 16 for 12); ablation: slice5e without that bin PASSES 25; both stamped (manifest md5, report, build 9647b7f65ea4fc03, mutant, time); original sha 802e323aab04ad8a = the committed sampler; the canary hashes gen_fcov_pkg.sv (equal); gen_fu_l14_FM16_mutant.diff retained |
| regression | 21 of 22 names PASS on b12x; lockstep_zcmp_dummy the B8 red by design (27 rows); the eleven earlier Slice A proofs re-checked PASS | the landing's own claim | verdicts and check logs |
| CM148 rows | M-1: the three sites now cite 215 (frequent) and 9 (rare), "about half of the 436 pulses; the other 221 passed the old slice through neighbouring lookups"; L-1: one Section 13; L-5: the misaligned-store consequence stated with the LSU line; L-2 / L-3 / L-4 deferred to the next source-changing landing | tb_l12 L-1, L-4, L-9 | verified in the diff and the l13 logs (UVM_ERROR 215 / 9) |
| T-235 sizing (CM102-L-5) | the five gaps with the never-committed estimates and the as-built size, each naming the built mechanism | the plan's ranking needed a committed artifact | consistent with the shim (one wording slip, L-1) |

## 2. Findings

### L-1 (low) [S4 record] Figures and attributions

"section 15 (the proxy, 35 rows: 24 at the T-235 commit, 7 tb_l9 rows, 4 landing-11 rows)" in the shim API doc: by the measure that gave 24 and 31
(the OK rows under the section header in the retained logs) gen_fu_l13_ut_isa_shim.log has 46, and the source has 46 check calls after the header
(35 at the inner indentation, 11 re-reset and TB-write checks at the outer): landing 11 added 15 by that measure, and "4" is the red log's failure
count. The sizing section's item 3 says "the writer itself is never counted, neither is the record after a writer": the code counts the record after
a writer and only skips the write-cycle corner (`!g_prev_minstret_written` at the corner test). The fcov API doc's "Also in this part: the tracked
reset value corrected to 0" belongs to landing 11 (CM138-M-2; 0778d23 already reads `= 0`). gen_fu_l14_lockstep_zcmp_dummy's excerpt header says
"green on build b12" of a FAIL-by-design run. One build id carries four names (b12, b12x, l12_root, l12_rehearsal).

### M-1 (medium) [S2 a bin whose hits do not prove the pattern] store_same_slot_then_pop accepts any of the last 64 plain stores

The plan's bin is "sw to a slot the following cm.pop loads" (F-CMP-068: a pop right after a store to its slots) and its anti-vacuity clause says a hit
proves the pattern executed. The sampler matches a pop's load words against the last 64 plain-store words (st_addr), so a store to that address from
an earlier frame counts. The directed program has one intended instance (`sw t0, 4(sp)` then `cm.pop 6`), yet the bin counts 3 in every proof
(gen_fu_l14_slice5e_check.log: `store_same_slot_then_pop = HIT (count=3)`): the `cm.pop 6, 1` and `cm.pop 15` frames overlap that store's address and
are counted as the hazard without any store between their push and pop. Two of the three retained hits are not the pattern, and the manifests declare
the bin as proven. Required: a store counts only between the sequence's own push and its pop (or within a bounded record distance), the count
re-proven at 1 on this program, and the API doc's window sentence replaced by the rule.

### L-2 (low) [S6] The ten new classifier rows have no red

The vector table's mechanism has its red (FM4UT, landing 9); the new rows are asserted values that have only passed. The FM16 build fails "rlist
classes 4 / 9 / 15" by construction (rlist 15 classed r5_14); one gen_ut_isa_cov run on it, retained, gives the rows their red at no cost.

### L-3 (low) [schema] The ablation manifest keeps a note for a bin it removed

gen_fcov_proof_slice5e_fm16_ablation.fcov.yaml has 26 anti_vacuity keys for 25 bins: the note of cp_rlist_class.r15 stayed after the bin left the
list, and the checker did not object. Landing 7 dropped such notes (1070 -> 1059) as a rule; apply it to the derivation tool and make the checker
refuse a note without a bin.

### L-4 (low) [S6 retention] Unstamped proof checks, no driver log, the image tie by directory name

The three slice5e check logs and the eleven re-checks carry no stamp line while the FM16 pair does (tb_l12 L-6 again); no driver log of the b12x
regression is retained (the FM16 batch log is the only one); the directed program's tie to the runs' image (crc 2a45342c, 202 words) is the directory
name zcmp_hz and the excerpt headers, with no line binding the .S to the crc. Stamp the proof checks; retain the driver log; print the source's sha
beside the image crc.

### Informational

- I-1: CM148 L-2 (the grace rule's over-wide sweep), L-3 and L-4 are deferred to "the next source-changing landing" while this landing changed
  gen_fcov_pkg.sv and cut build b12x; the rows arrived after the cut, so the deferral is a scheduling choice. The grace-rule fix (tb_l12 L-7) waits
  with them.
- I-2: the T-235 sizing section records estimates that were never committed against what was built, with the plan's ranking now anchored: the
  honest closing form of CM102-L-5.
- I-3: cross coverage of the hazard group is reported from urg (35 / 74, 30 / 74) while the manifests declare coverpoint bins only, consistent
  with the crediting rule until T-215.

## 3. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S2 derive from intent: eleven patterns follow the Sample line and the bin
definitions with their approximations stated (conforming); one bin's hits do not prove its pattern (M-1) and one back-to-back class can misfire
(L-5). S6 trust triad: proofs on the committed build, the mutant with a stamped ablation and a retained diff (conforming); the new unit rows
without a red (L-2). S4 honesty: the CM148 corrections true of the logs (conforming); the figures of L-1. One-line verdict: FAIL on M-1 until fixed.

## 4. Verdict

CRITIC VERDICT: REQUEST-CHANGES (M-1). Lows L-1..L-8 to tb-infra's next touch; M-1's fix and re-proof are the re-review's gate.

## 5. Reconciliation with the cross-model artifact (dv/auto_dv/reviews/2026-09-03-claude-diff-0778d231-ba3799b0.md, read after Sections 1-4 were written)

APPROVE-WITH-CHANGES: two mediums, five lows.

- Its first medium is my store_same_slot_then_pop finding with the count that decides the level: I had rated the 64-store window Low as a width
  question; the artifact's observation that the bin counts 3 where the program holds one instance, verified in gen_fu_l14_slice5e_check.log and in the
  program's frames, shows two of the three retained hits are not the pattern. Promoted to M-1 (the artifact's own level); the verdict follows.
- Adopted and verified, as L-5 (low) [S2 classification]: hz_b2b_prev (gen_fcov_pkg.sv:593) takes prev_seq_kind whenever the record before the
  sequence carried ext_exp_last, but prev_seq_kind is written only in the push / pop block (:709) and never by the move collector, while
  rvfi_ext_expanded_insn_last is set for every expanded instruction, moves included; `cm.push; cm.mvsa01; cm.pop` therefore samples push_then_pop_b2b
  with a move between, and a sequence skipped for !zp_sp_valid leaves a stale kind. No retained program interleaves them, so no proof is wrong today.
  Held at Low (the artifact: medium) for that reason; required with M-1's touch: record the kind of every closed sequence (moves included) and
  clear it when a sequence is skipped.
- Adopted and verified, as L-6 (low) [S4 record]: the slice5e3 sentence attributes its 24-bin count to the absent deferral and the absent long class,
  but slice5e (26) has no long bin either; the second bin the min1 run lacks is cp_redirect_once.yes (slice5e3 declares no cp_redirect_once key; the
  default run hits it 7 times). Say which bin and why, if known.
- Adopted and verified, as L-7 (low) [S5 code]: zp_addi_cycle is reset and written (:135, :592, :669) and never read; the deferral test uses the
  latency stand-in the doc states, so the state is dead. The delay class boundaries (== 1, <= 4) are hand-encoded a third time (:738) beside lat_cls
  and zp_delay_cls, and the sequence path passes the pushpop group's class value (dl = zcmp_v[11], :691) as the hazard group's, relying on the two
  groups' 0..2 indices coinciding; the pushpop class MIX lands in no hazard bin silently. zp_regs re-encodes the s-register map that zcmp_sreg
  holds. One helper for the hazard classes and the rlist mask from zcmp_sreg.
- Adopted and verified, as L-8 (low) [S4 record]: the CM148-L-4 deferral says "the .S files are in the sources list"; gen_fu_l14_sources_sha256_b12.txt
  has no .S entry (programs are images, not build sources), so that half of the deferral rests on scope, not on the build hash.
- Its icache_enable misattribution low is inside my L-1.
- Not in the artifact: L-2 (the new rows without a red), L-3 (the stale note in the ablation manifest), L-4 (the unstamped proof checks, the missing
  driver log, the image tie), the rest of L-1, I-1..I-3.
- Verdict disagreement, stated: the artifact approves with changes; I hold REQUEST-CHANGES because a declared, proven bin's retained hits are
  mostly not its pattern, which is the fcov form of a check that passes for the wrong reason; the fix is small and the re-proof is one run.
