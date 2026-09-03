# Critic verdict: witness ledger follow-ups in plan v2f (commit 7594017), re-check of the gate sentence, Section 1 and the tool

Artifacts at commit 7594017 (sha256 first 16 hex, lines):
- dv/auto_dv/docs/gen_fcov_plan.md      29db095f1cd2eaab  7020 (gate :74-80; ledger rows :180, :182; CG-WIT-001 :7010ff)
- dv/auto_dv/docs/gen_test_plan.md      ff4de35043872c49  23363 (Section 0 protocol :67-79; Section 1 rows)
- dv/auto_dv/docs/gen_feature_list.md   63ddaa3283b7806c  13645
- dv/auto_dv/tools/gen_trace_check.py   3441712ce4396632    85
- dv/auto_dv/docs/gen_trace_tp_bin.csv  1fc1cb55ece20c0f  24999;  gen_trace_feature_tp.csv  e4c4b0b15fe184da  2057
Date: 2026-09-03T11:26Z   Role: Critic   Previous: gen_critic_plan_witness_v1.md (6a60d54; W-1 medium, W-2 low, W-3 low, C-1..C-5).
Scope, as signalled: the gate sentence, Section 1 and gen_trace_check.py. Round 6 (scoped cross-model) is not read;
its three items go to v2g per the Orchestrator.

CRITIC VERDICT: APPROVE on the three re-checked items (W-1, W-2, W-3 closed; C-4 and C-5 in place); C-3 stays OPEN
for v2g, and one new low.

## 1. Re-checked at 7594017

- W-1 (gate) CLOSED. gen_fcov_plan.md:74-80: the gate is the URG functional-group score over the spec-derived and
  adopted covergroups; CG-WIT-001 is "EXCLUDED from that number without exception (Runtime gives it weight 0 in the gate
  computation)" and is reported beside it as "witnessed clauses: N of M marked items", the way adopted bins are counted
  separately; its bins stay in the per-test manifests after the sunset. The CG-WIT-001 block (:7010) repeats the rule.
- C-4 (naming and counting) CLOSED. gen_test_plan.md Section 1: covergroups 207 with the ledger counted separately,
  distinct bins 15825 (the 220 ledger bins excluded), a separate row "Witnessed-clause ledger (CG-WIT-001, outside the
  score, the bin total and traceability): 220 bins for 220 marked items"; gen_fcov_plan.md:180 and :182 carry the same
  two rows. CG-WIT-001's Features field is "none (ledger of fire-check results ...)".
- W-2 / C-5 (tool) CLOSED. gen_trace_check.py: ACTIVE->bin excludes CG-WIT-001 bins and prints both counts (run by me
  from a clean archive of the commit: 705/705 excluding the ledger, 705/705 including it); bins->feature exempts the
  ledger (207/207 covergroups); a ledger line prints the 220 bins, spec-derived 15776 and adopted 49. PASS.
- W-3 CLOSED. The nine features that at 6a60d54 were named only by CG-WIT-001 (F-DMEM-009/034/045/051, F-IC-045/046,
  F-IRQ-057, F-PMC-053, F-TRG-027) are now named by their real covergroups (checked by script; the ledger's Features
  field is none).
- C-1 / C-2 (protocol) present as plan text: gen_test_plan.md:67-71, the finish() epilogue issues COV_WITNESS for exactly
  the ids whose fire_<tp_id> result is TRUE, before the finish handshake; a direct call outside the epilogue is refused
  by the structure check; the dispatcher raises GEN_WITNESS_FOREIGN for an id outside the running test's rendered set.
  Implementation is the Test Writer's and TB Infra's; I check it when it lands.

## 2. Open

- C-3 (mechanical sunset) OPEN. The plan text (:73-79) defines the two inputs (Runtime's export_sources in
  build_manifest.yaml, TB Infra's rendered exact event rows) and says the tool fails a still-marked item whose row is
  present. The committed tool does not do that: gen_trace_check.py:79-81 prints a fixed "export sources unknown
  (sunset trigger inactive until the rendered export table exists)" and counts the marked items; there is no parse of
  either input and no failure path. The signal's description of the tool is ahead of the code. This is round 6's first
  item and belongs to v2g; it does not change today's numbers.
- W-4 (low, new). 28 ACTIVE features are named by no covergroup's Features field at all (after alias / fold resolution;
  e.g. F-CMP-029, F-CMP-054, F-CSR-041, F-CSR-071, F-CSR-073, F-DBG-045, F-DBG-048, F-DBG-061, F-DIT-022, F-DIT-027,
  F-DIT-030, F-DMEM-050, ...). They reach ACTIVE->bin through their items' CSV rows, so the completeness numbers are
  unaffected, but a reader of the coverage plan cannot find them from any covergroup. The tool checks only that named
  features exist; add the reverse report (ACTIVE features named by no non-ledger covergroup) and name them in the
  covergroups that host their items' bins.

## 3. What closes the rest

v2g with the round-6 items: the tool's sunset failure path (C-3), the manifest exclusion of marked witness bins in
gen_fcov_manifest.py (my batch-1 finding M-2 is the same defect), and the Section 9 alignment. W-4 may ride along.
