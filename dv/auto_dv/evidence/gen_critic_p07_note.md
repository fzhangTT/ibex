# Critic note: is a loader-validated, reasoned fcov deferral (rt38, LOG-089) within P-07's intent, or a relaxation?

Asked by the Orchestrator (2026-09-04T20:50:36Z, deciding input between runtime-2's rt38 plan and the DV Lead's ruling). Artifacts read (sha256 first 16):
dv/auto_dv/docs/gen_rt38_fcov_deferral_plan.md (untracked, 134 lines) f757f577d23c46ce; dv/auto_dv/work/dv-lead/gen_p07_manifest_semantics_ruling.md (90 lines)
0ba012ee7d45fbba; docs/dv/dv_principles.md d9c27db18f511411 (trust triad rule 3, lines 148-152); dv/auto_dv/flow/gen_regress.py at d1f6019 5c9869bbe0784aee
(fcov_policy_failures :237-258); the LOG-089 entry (gen_intervention_log.md ~:2130-2167). Role: Critic. Method: the rule's text against the plan's Section 5
predicate and Section 8 claims; the policy's history in the log (LOG-039 / T-178: measured false exempt by design); my own tb_l35 / tb_l37 verification of
the detaches re-read for what it did and did not check.

CRITIC VERDICT: RELAXATION. A per-entry deferral key that lets the policy pass a measured run whose expectation is not enforced is a change to what
trust-triad rule 3 requires, not an implementation of it; rt38 therefore needs the owner's ruling, not a Critic approval, and I will not approve its plan on
the Critic's authority.

Why, in order of weight:

1. Rule 3's operative clause is a verdict, not an artefact: "declared-but-unhit bins FAIL the run" (dv_principles.md:149). Under rt38 the 13 entries keep
   manifests whose declarations are KNOWN unmet at the round's own seeds (the pre-flight: 18 of 24 runs UNHIT; LOG-088) and the runs do not fail. That is
   the exact state the clause forbids, produced by design rather than by omission. The manifest being committed and unchanged does not satisfy the rule;
   the rule is about the run's outcome.
2. P-07 (fcov_policy_failures) is the enforcement arm for the case where the statement of intent is not enforced at all. Its subject, per its own
   docstring and the LOG-039 / T-178 history, is a MEASURED run whose coverage enters the measured merge without an enforced expectation. rt38's deferred
   bucket admits 39 of the round's 45 measured runs into the measured merge and the credited total with no enforced claim. Naming the ruling in a reason
   string records the fact; it does not change the fact.
3. "It does not make the policy lenient" (plan Section 1 and 8) is contradicted by the plan's own Section 5: the failing branch is reached only when the
   key is absent, so 39 runs that the committed policy fails would pass. A policy whose verdict on the same runs moves from FAIL to PASS is lenient in the
   only sense that matters for a gate, however carefully the pass is labelled.
4. The plan's real merits are hygiene, not a rebuttal: loader rules 1 to 5 make a silent omission fail at load, the deferred runs are kept out of the
   expectation pass count, and the artefact stays held to the three equalities. Those are good properties for whatever mechanism the owner rules on; they
   do not make a waiver of rule 3 into compliance with it.
5. Honesty over green (dv_principles S4) cuts the same way: a round that indexes because its checks were deferred is a green the rule says should be red.
   The honest instruments that stay inside the rules as written are the two the DV Lead names: fix the declarations (plan-side "not in manifest" marks for
   unbuilt covergroups; per-bin bins_not_hit with reasons for bins not guaranteed per run; the 123 stable unmet bins triaged as stimulus or declaration
   defects) and slip the round; or, if the owner wants the flow exercised end to end now, set the 13 to measured: false, which P-07 exempts by design and
   which R-5.5 keeps out of the measured merge, and label the round a flow rehearsal in those words. Either is within the rules; rt38 is not.

Two things I owe on the record:

- My tb_l35 and tb_l37 approvals of the LOG-086 and LOG-088 detaches verified their mechanics (fields, loader counts, manifests unchanged, the figures) and
  did not apply fcov_policy_failures to the detached MEASURED entries, although tb_l34 Section 6 quotes that function's exemptions. The consequence
  runtime-2 measured (39 planned runs flipped to FAIL) was there to be found in both verdicts and I did not find it. Neither verdict claimed the round
  would index, and both stand on what they verified; the miss is recorded here and in my STATUS.
- If the owner rules that a reasoned deferral is acceptable policy, I will review rt38's plan on its own terms. The conditions I would hold it to are
  already visible: rules 1 to 5 as written with their five reds; the deferred bucket never summed into pass and never read as covered; the round record
  naming every deferred entry with its reason beside the checked ones; the 123 stable unmet bins stated as findings; and the deferral key removed from an
  entry the moment its declaration is fixed, with a loader rule that a deferral older than one round dies.

No Critic row is raised; this note is the Orchestrator's deciding input and goes to the owner with the schedule question, as LOG-089 provides.
