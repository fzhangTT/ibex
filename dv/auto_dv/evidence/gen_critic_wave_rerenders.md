# Critic verdict: the "wave re-renders" group, ba4860b..9c28944 (test-writer-2, Hand B)

Artifacts (the one commit of the range, 9c28944; sha256 first 16 hex of each blob at that commit):
- dv/auto_dv/tests/gen_test_cmp_zcb.py 260a40a471aaeb64; dv/auto_dv/fcov_expectations/gen_test_cmp_zcb.fcov.yaml 948ab3ce4a41caea
- dv/auto_dv/tests/gen_test_cmp_zcmp_basic.py 781ff1914f8223d5; .../gen_test_cmp_zcmp_basic.fcov.yaml 3274469aa87f475e
- dv/auto_dv/tests/gen_test_mul_div.py 5e193adfea20c719; .../gen_test_mul_div.fcov.yaml 53dc62935747d2c4
- dv/auto_dv/tests/gen_test_isa_shift.py 4980d48a438a854a; .../gen_test_isa_shift.fcov.yaml 7e0ee60a7f4086bc
- dv/auto_dv/tests/gen_test_mul_mul.py d43e5462e2326944; .../gen_test_mul_mul.fcov.yaml f2f5269d5ce6ef7f
- dv/auto_dv/tests/gen_test_pmp_csr_warl.py f6b9242022fa8878; .../gen_test_pmp_csr_warl.fcov.yaml b1d4daa07ddf6f9f
- dv/auto_dv/tests/gen_test_cmp_zca.py a8bc5d8a1781c6cd; .../gen_test_cmp_zca.fcov.yaml 8e3cc8537b4bd425
- dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_fu_wave_rerender.log 380d51fd640c6a72
- dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_manifest.md 8cff98e0b40e82b5
- dv/auto_dv/evidence/gen_tdd_batch3.md 8fdca569f8daede6 (Section 19); dv/auto_dv/evidence/gen_critic_response_batch3.md dad6002efba722da

Date: 2026-09-05 (UTC). Role: Critic. Method: every removed and added bin re-derived by me from the committed blobs
(the manifests at ba4860b and 9c28944, the census and not-hit tables at 1fb417f as retained at 9c28944) with my own
script, independent of the landing's; the seven touched manifests and the untouched bit_ratified re-rendered by me from
their committed modules on a detached archive of 9c28944 with the manifest generator; the two non-seed-dependent reason
texts checked against the sampler and the round-0 record; the record's Section 19 and the log read line by line.
Exposure: the Orchestrator's range message named rev63's outcome (three Lows, one Info) before this file was written;
rev63's content (6e1ee4c) is read only in Section 6. Logs: dv/auto_dv/work/critic/wave/checks.txt.

CRITIC VERDICT: APPROVE (five Lows owed as disclosed, the fifth adopted from rev63 in Section 6; no Medium).

## 1. The removed set is the census's, bin for bin

For each of the six entries the set of bins declared at ba4860b and not at 9c28944 equals the census's under-the-bar
rows for that entry (gen_wave_4017573/gen_wave_census.txt: 9, 6, 6, 4, 2, 1; 28 in all, 5 coverpoint bins and 23 cross
legs by the census's own [CROSS LEG] marks); nothing was added to any of the six, and every pre-existing not_hit reason
is byte-identical before and after. Every removed bin's new reason carries the census's N of 40 for that bin (my check
matched each count against the census row), names 4017573 and the census file, and says the entry does not guarantee
the bin per run while it stays PLANNED in traceability and credited from the merged report. The declared totals move
96 to 87, 325 to 319, 196 to 190, 120 to 116, 338 to 336, 179 to 178 (1254 to 1226), as the record says.

## 2. The classes are the ruled ones, and the two non-seed-dependent reasons are true of the tree

Twenty reasons open with "seed-dependent"; four with "generator label defect, not seed-dependent" (mul_div's
cr_op_divisor div/divu/rem/remu _pos_rand legs at 38, 36, 39, 37 of 40); four with "seed-dependent by measurement,
cause undiagnosed" (mul_div cp_delta.d2 and cr_dit_div0_delta.dit0_div0_d2 at 39, mul_mul cr_op_delta_clean.mulhsu_d2
and mulhu_d2 at 38), which are the DV Lead's three classes with the memberships the record states. The label-defect
reason's mechanism is the sampler's: div_divisor_cls (gen_fcov_pkg.sv:879-893 at 9c28944) books the six named values,
then eq_dividend, then abs_gt_dividend, then the sign class, so a divisor drawn by sign alone whose magnitude exceeds the
dividend is abs_gt_dividend and never pos_rand; the reason names the defect, the fix owed (a draw that rejects the
classifier's other classes, proven against the sampler's rule, then a fresh forty-seed block) and does not bury it as
seed-dependent. The generator itself is untouched by the range, as the record says; the working tree's development
copy of that fix is not in it. The undiagnosed reason claims nothing beyond the count and names the four as one shape.

## 3. The cross-operand rule, the removal direction

Every removed cross leg is itself a census under-the-bar row, so nothing was removed whose operands stand; and for each
removed coverpoint bin (cp_rs1_class one, p16, two; cp_hazard.popretz_ft_cm; cp_delta.d2) no declared cross leg of its
covergroup carrying that bin's name as its final segment remains at 9c28944 (my scan over the new declared sets: empty
leak list for all six), which agrees with the retained log's mechanical check and, as the record notes, says the census
is complete on those legs. The five following legs' reasons name the component they follow and its count.

## 4. cmp_zca: the 21 shapes return, the never bin stays out with a corrected reason

The bins added to gen_test_cmp_zca's declared set are exactly the 21 gen_cmp_zca_cg rows the not-hit table reads at
40 of 40 (gen_wave_nothit.txt: 22 shapes, 21 at every seed, 1 never), 300 to 321; nothing removed; three not_hit lines
remain (cp_cj_off.self and the two seed-dependent c_lwsp lines, untouched). cp_cj_off.self's reason is now entry-scoped
and true: this program emits no zero-offset c.j or c.jal, the bin is 0 of 40 in the wave, other entries retire the
park-here idiom (the round-0 merged report reads self 398 in that coverpoint, gen_round_0/gen_grpinfo.txt), and the
earlier "exclusive with termination" framing is withdrawn. This closes the cmp_zca half of my generator-fixes M-1 from
a forty-seed measurement at the fixing commit, which is what that row asked for.

## 5. Renders, records, rows, verdict

- Renders: with the manifest generator on a detached archive of 9c28944, all seven touched manifests and
  gen_test_bit_ratified's re-render byte-identical to the committed files (8 of 8, zero diff); the log's Section D
  says the same for all seventeen.
- Records: gen_fu_wave_rerender.log 30536 bytes / 2ada6695f013e2d2e76f27ac59fe7372 equals its manifest row; ASCII.
  Section 19 states the rule applied, the three classes, what comes back and how (a fresh forty-seed block at a fix's
  commit, never the wave's numbers), and what is not claimed. Its records paragraph says the "24 cross legs" figure was
  a hand-off message's; the committed wave index (gen_wave_4017573/gen_index.md:50 at 1fb417f) also says "24 are CROSS
  LEGS" against its own table's 23, so the discrepancy is in a committed record too (L-1).
- The reason-class vocabulary: gen_test_template.py:85-87 documents three classes (seed-dependent, stimulus,
  declaration); this landing writes two further tokens as ruled. The one committed consumer that keys on the words,
  gen_round_form_check.py:227-234, reads a round form's prose and not the manifests, so nothing parses these reasons by
  class today; the template comment should name the two new tokens or point at the ruling (L-2).
- The two removed operand bins of cmp_zcb's cp_rs1_class and cp_hazard.popretz_ft_cm are coverpoint bins of
  covergroups other entries also sample; their merged-report credit is stated in each reason and is the right
  consequence of the per-run rule.
- Nothing in this range touches a generator, a sampler or a plan line, as Section 19 says (the range's stat carries no
  such file).

Conformance (dv_principles.md): honesty over green in the direction that costs coverage credit, a false per-run
declaration corrected at 28 bins, each with the measurement that condemns it; the 21 returns rest on a forty-seed
measurement at the fixing commit and not on the reader; every render reproduces.

- L-1 (Low, records; runtime-2). The committed wave index's prose "24 are CROSS LEGS" (gen_index.md:50 at 1fb417f)
  disagrees with its table and the census (23); a corrigendum beside the index.
- L-2 (Low, records; Test Writer). The template's documented reason classes do not include the two tokens this landing
  introduces; add them or cite the ruling.
- L-3 (Low, records; Test Writer). The four label-defect reasons repeat a five-line diagnosis verbatim in each; one
  named note with four one-line references would keep the manifests readable, a style point only.
- L-4 (Low, records; DV Lead). The DV Lead's per-run-manifest rule and the three-class ruling are cited from a task
  record (Orchestrator TASKS 2026-09-05T10:08:17Z) rather than from a plan document; the wave re-render will be read
  from the plan set later, so the ruling needs a home there.
Verdict: CRITIC VERDICT: APPROVE on ba4860b..9c28944. The removed set, the counts, the classes, the removal-direction
rule and the 21 cmp_zca returns are re-derived from the committed blobs and agree with the landing; L-1..L-4 owed as
disclosed.

## 6. Reconciliation with the cross-model artifact rev63

Read after Sections 1-5 were written: dv/auto_dv/reviews/2026-09-05-claude-diff-ba4860ba-9c289445.md at 6e1ee4c
(claude CLI fallback under A-001; APPROVE-WITH-CHANGES; three Lows, one Info). Its nine verifications and Sections 1-5
agree on every shared point (the 28-bin removed set against the census, the counts in every reason, the 20/4/4 classes,
the empty leak list and the follower legs, the 21 cmp_zca returns against the not-hit table and the 398 figure against
gen_grpinfo.txt:11670, the manifest row, the seven renders at the commit). It adds three checks I record as its: the
label-defect claim traced into gen_mul_div_prog.py (divisor() :179-197 falling through to rand_unnamed, the
divisor:pos_rand unit's dividend drawn from mostly small named values, so the draw lands abs_gt_dividend most of the
time), the census and not-hit digests in the log header against the files, and a wider consumer sweep for the class
prefix (gen_round_credit.py, gen_covergroup_set.py, gen_round_form_check.py all key on the bin name), which confirms
my narrower one.

- Its Low 1 (the committed wave index's prose "24 are CROSS LEGS" against its table's 23, so the record's attribution
  to a message alone is incomplete) is my L-1, found independently, same fix.
- Its Low 2 is new and verified: the folded apply_handB.py in the log writes cp_cj_off.self's reason ending "(398 merged
  hits in round 0)" while the committed module (gen_test_cmp_zca.py:123) and manifest end "(398 merged hits in round 0,
  gen_round_0/gen_grpinfo.txt)"; the log's Section C check passes on substrings, so the folded script did not produce
  the committed bytes and the log does not say so. Adopted as L-5 (Low, records; Test Writer): state the post-edit in
  the log's companion or Section 19; the committed text is the better one.
- Its Low 3 (the two new class tokens against the template's documented three) is my L-2; it places the template line
  with the DV Lead, which agrees with my L-4's point that the ruling needs a plan-side home.
- Its Info (the log's Section D render check ran on the pre-commit working tree) is answered by its and my renders at
  9c28944, both zero diff; no action.
- Verdict unchanged: APPROVE; L-1..L-5 owed as disclosed. rev63 and this file agree there is no Major or Medium.
