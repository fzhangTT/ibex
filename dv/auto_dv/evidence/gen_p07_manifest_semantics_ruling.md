# DV Lead ruling: P-07 and per-run manifest semantics (round-1 blocker)

Asked by runtime-2 (their report: the LOG-086 and LOG-088 detaches do not clear round 1). The reading of the
manifest rule is mine; the schedule consequence is the owner's. Every figure below I derived by calling the
code, at the round's pinned commit d1f6019, not by reading it.

## 1. The finding reproduces exactly

I called `gen_regress.fcov_policy_failures` on the round's own 53 planned runs with every verdict set to PASS.
39 of 53 flip to FAIL, over the 13 detached measured entries at three seeds each, reason verbatim:

    no fcov_expectation_file on tier smoke (fcov_manifest_required_tiers)

It fires with `covergroups_exist` True and False alike: the testlist header names smoke and targeted
(gen_testlist.yaml:59) and the widening at gen_regress.py:243-244 only ADDS tiers. The condition is
gen_regress.py:247, `t["tier"] in required and t.get("measured", True) and not
t.get("fcov_expectation_file") and r["verdict"] == C.VERDICT_PASS`. A failing run refuses the round's index,
so the round as configured measures nothing.

## 2. P-07 stays absolute

No relaxation, no new "deferred" state in the testlist, no flow change. P-07 is the enforcement arm of
trust-triad rule 3, and the case in front of us is exactly its subject: a measured run whose coverage enters
the credited total with no enforced statement of intent. A round with 13 of 15 measured entries unchecked
would produce a coverage number that 39 of its 45 measured runs made no claim for. The rule is not the
obstacle. It is the thing that caught the plan set being wrong.

## 3. The detaches were the wrong instrument, and half of that is mine

A manifest is RENDERED FROM MY PLAN: gen_fcov_manifest.py takes the union of the group's items' bins from
gen_trace_tp_bin.csv and applies the exclusion rules of gen_fcov_plan.md Section 0. So an over-declared
manifest is a plan defect. Detaching the manifest deletes the intent statement rather than correcting it,
which is why the failure simply moved from the expectation check to the policy: the same 13 entries, the same
39 runs, before and after. LOG-086 and LOG-088 should be superseded rather than extended.

## 4. The correct instruments already exist, and neither needs a flow change

- **An unbuilt covergroup.** Its coverpoints carry `not in manifest` on their plan line (Section 0 rule (c),
  read by gen_fcov_manifest.py). Coarse granularity is correct here: nothing in a covergroup that does not
  exist can be hit. This covers LOG-086's seven entries. Mine to edit, Test Writer re-renders.
- **A built bin the test does not guarantee per run.** `bins_not_hit = {"<bin>": "<reason>"}` as a class
  attribute of the test module, parsed at gen_fcov_manifest.py:302, which drops the bin from the declared set
  and emits a `# not_hit <bin>: <reason>` header line. Per bin, and it forces a written reason. This covers
  LOG-088's six entries. Established practice, not a proposal: seven committed test modules use it, and
  gen_test_rst_boot.py:150-152 already excludes one bin with the reason "irq agent absent: no interrupt line
  is driven".

## 5. The semantics question, answered now because the round cannot dispatch without it

**A manifest declares what the test guarantees PER RUN.** The flow's check is per run, one unmet bin fails
the run, so that is the only reading its enforcement supports. Three consequences:

1. A bin hit at some seeds and not others does not belong in the per-run declared set. It stays in the plan's
   traceability as PLANNED and is credited from the merged report when any run hits it. Its `bins_not_hit`
   reason is that it is not guaranteed per run.
2. A bin hit at NO seed is not a semantics question, it is a defect: either the stimulus is missing (fix the
   program) or the declaration is wrong (out, with the reason saying which). The 123 bins unmet at every seed
   are that class, and they are the half no granularity change excuses.
3. A cumulative expectation is a different artefact from a per-run manifest and needs the flow's check to be
   cumulative. That is Runtime's change, it is frozen, and under this ruling it is NOT a prerequisite for
   round 1.

## 6. Guard rail

An entry cannot `bins_not_hit` its way to a pass. gen_fcov.py:330 treats "manifest declares no bins" as a
cause, and the result is unverifiable rather than PASS, so a measured entry must retain a non-empty
guaranteed set. If any of the 13 cannot, its group has a stimulus gap and it must not be measured this round.

## 7. What this costs, plainly

It slips the round. The work before dispatch: my plan-side `not in manifest` marks for the unbuilt
covergroups; the Test Writer's `bins_not_hit` entries with a reason for the built-but-unhit bins (246 over the
six, clustered by cause, so a generated dict reviewed bin by bin, plus the seven entries' unbuilt sets); a
manifest re-render; reverting the two detaches. The 123 stable bins need real triage. What it buys is a round
whose coverage number every measured run made an enforced claim for.

## 8. The fallback I do not recommend

Set the 13 to `measured: false`. P-07 exempts unmeasured entries, so the round dispatches today, but Critic
R-5.5 sends their coverage to the unmeasured vdb and the round's measured coverage comes from 6 runs over 2
entries. That is a flow rehearsal, not the first coverage measurement, and the round record would have to say
so in those words. If the owner wants the flow exercised end to end now, this is the honest way to do it,
labelled as such.

## 9. One defect this creates in my committed form

gen_round1_request.md (committed at d1f6019) says the detached entries' coverage is "still credited". That is
wrong while the round does not index: it is merged, and credit requires an indexed round. runtime-2 is right
to ask me to drop it. I am holding the corrigendum rather than patching twice, because section 5 changes
again with whichever option is chosen.

## 10. Refinement (supersedes clause 4(a))

One instrument, not two, and no plan edit. gen_test_lib.py:915-918 derives a test's `declare_bins()` through
`gen_fcov_manifest.plan_bins`, the same function that renders the manifest, so a bin added to a test's
`bins_not_hit` leaves BOTH by construction. `bins_not_hit` therefore covers the unbuilt-covergroup class and
the built-but-unhit class alike, with no plan change, no generator change and no self-test change. The 147
coverpoint lines over 25 covergroups that clause 4(a) would have marked are off the critical path.

The guard rail of clause 6 then bites three entries. Excluding every bin whose covergroup does not exist
leaves nothing to declare for gen_test_bit_draft (15 of 15), gen_test_csr_reset (68 of 68) and
gen_test_pmp_csr_warl (266 of 266), so those three cannot make a per-run claim and must go `measured: false`
until their covergroups are built. Their incidental coverage on built groups leaves the credited merge, which
is the price of not crediting coverage no entry has claimed.

The round then keeps its 53 runs, because the three still run, and becomes 12 measured entries at 36 measured
runs with ALL TWELVE checked against re-scoped manifests. Guaranteed sets: bit_ratified 654, isa_alu 563,
mul_mul 338, cmp_zcmp_basic 325, cmp_zca 324, mul_div 196, isa_cti 184, csr_trap_setup 151, isa_shift 120,
cmp_zcb 96, rst_boot 6, csr_access 4.

Two thin sets (csr_access 4, rst_boot 6) and the whole class A set have never been checked by any run, so the
re-scoped manifests need a re-flight at the round's seeds before dispatch, the same 24-run pattern runtime-2
ran. That re-flight is the acceptance gate, not a nicety.

Bin lists, per class and per entry, with the class A and class B reason strings ready and the class C reason
shape stated: dv/auto_dv/work/dv-lead/gen_bins_not_hit_worklist.md.
