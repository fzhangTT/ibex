# Critic opinion and verdict: CG-WIT-001, the test-issued witness bins (plan v2e, commit 6a60d54)

Artifacts at commit 6a60d54 (sha256 first 16 hex, lines):
- dv/auto_dv/docs/gen_fcov_plan.md      4d794612ccd39950  7008 (CG-WIT-001 at :6987; gate at :74 and :6856-6859)
- dv/auto_dv/docs/gen_test_plan.md      8c16a038f75a90a1  23339 (Section 0 :55-65 marker and COV_WITNESS; Section 1.3, 220 items)
- dv/auto_dv/docs/gen_feature_list.md   979e96d6ded5cda3  13645
- dv/auto_dv/tools/gen_trace_check.py   a580c089a09cd677    79
- dv/auto_dv/docs/gen_trace_tp_bin.csv  1fc1cb55ece20c0f  24999;  gen_trace_feature_tp.csv  e4c4b0b15fe184da  2057
Date: 2026-09-03T10:48Z   Role: Critic   Asked (Orchestrator): (1) is a bin hit by the test's own COV_WITNESS command admissible as a
fire-check witness under dv_principles; (2) if so, must it be reported outside the 80 percent functional-coverage
number; (3) does a CG-WIT-001 bin alone credit a Feature in gen_trace_check.py. The round-5 cross-model artifact and
the DV Lead's prepared positions were not read; this opinion was drafted before the signal from the committed text.

CRITIC VERDICT: REQUEST-CHANGES on the v2e text (the mechanism is admissible as a ledger under the conditions below;
two defects in the committed text: the gate sentence includes the witness group, and the trace checker's crediting
rule would accept a witness-only feature). Both are expected to land in v2f together with round 5.

## 1. Q1: admissibility

Admissible as a LEDGER of fire-check results, not as functional coverage of the DUT, under conditions C-1..C-5.

- What the bin measures: a decision taken in Python (the cycle-level clause evaluated TRUE against the export), not a
  DUT observation. The plan's Sample line says so ("a hit proves the cycle-level fact was asserted, not merely that
  the test ran"). dv_principles S3 places "did it fire" in the test; the witness mirrors that check into the coverage
  database so the regression can ask which of the 220 cycle-clause items has ever been asserted. That bookkeeping use
  is legitimate, and the manifest machinery (declared-but-unhit fails the run, S6 rule 3) is a real gain once the
  marker is removed.
- Why it is not DUT coverage: S6 rule 3 requires an anti-vacuity review of every sampling condition. The condition here
  is "the test issued the command"; the covergroup cannot distinguish a clause that passed on DUT data from a test that
  issues COV_WITNESS unconditionally. The bin's truth is the truth of the test's clause, which the fire-check already
  collects and fails on; the bin adds no independent evidence about the DUT and cannot fail on a DUT mutation. A
  coverage number that includes it can be raised by test code alone. CG-WIT-001's Features field names 282 features
  (207 ACTIVE): read as coverage, one test-issued group would "cover" 207 of 705 active features.

Conditions:
- C-1 Issue point. COV_WITNESS <id> is issued only from the owning test's fire_<tp_id> method and only on the TRUE branch
  of the clause; gen_test_lib.check_test_source refuses a COV_WITNESS call outside a fire_* method or one not guarded by a
  non-literal condition, as it already refuses a literal ok argument. This is the only place the Sample line's
  anti-vacuity claim can be made true.
- C-2 One owner. The dispatcher accepts COV_WITNESS <id> only from the test that owns the item (id list per test rendered
  from the plan); any other id is a collected error, never a bin.
- C-3 Mechanical sunset. The marker token is removed by the plan generator when the clause's event source appears in the
  export's source list (+gen_export_sources / the E-line kinds of gen_export.py), and gen_trace_check.py fails when a
  marked item's source is in the tree while the marker remains. A hand edit that may never happen is not a sunset.
- C-4 Naming and counting. The group is reported as "witnessed clauses", never as bins hit or features covered; the
  Features field stays for traceability; Section 1's "distinct bins referenced" (16045 at 6a60d54) counts the 220 witness
  bins separately, as the 49 adopted bins already are.
- C-5 Trace-checker rule (Q3 below): ACTIVE->bin completeness excludes CG-WIT-001 bins, and the tool reports the
  count of features and items that would rest on witness bins alone (expected 0).

Equivalent without a bridge command: the flow already parses GEN_TEST_FIRE lines; a regression-level ledger of
fire_<tp_id> results from the logs gives the same 220-entry table with no TB command and no group in the DUT coverage
namespace. Either route is acceptable; the DV Lead chose the covergroup route for the manifest machinery, a fair
reason. The conditions apply to that route.

## 2. Q2: outside the 80 percent number

Yes, without exception. The gate (gen_fcov_plan.md:74, :6856-6859) is the URG functional-group score with equal group
weights after ignore_bins; at 6a60d54 the text does not exclude CG-WIT-001, so it is one group of 208: a fully witnessed
regression adds about half a percentage point that no DUT behaviour produced and a partially witnessed one subtracts
it. Both directions corrupt the number the gate is judged on. Precedent exists in the same file: adopted bins are
"counted separately" (:33, :48, :177, :6876). Required: the witness group is excluded from the gate score (URG group
weight 0, or the gate computed over the group list minus CG-WIT-001) and reported on its own line as "witnessed
clauses: n of 220 (m still marked coverage-only)". It stays in the per-test fcov-expectation manifests after the
sunset, where its job is to fail a run, not to raise a score. This is finding W-1 (medium) on the v2e text.

## 3. Q3: does a witness bin alone credit a Feature in gen_trace_check.py?

- The rule (gen_trace_check.py at 6a60d54): a feature is "without bin" only when none of its items has any CSV bin
  (`no_bin = [f for f in active if not any(t in tp2bin for t in f2tp.get(f, ()))]`). The covergroup of the bin is not
  examined, so a feature whose items carry only CG-WIT-001 bins WOULD count toward ACTIVE->bin 705/705.
- Today's data, computed by me from the committed CSVs with the tool's own feature-to-item and item-to-bin joins:
  ACTIVE features whose items carry only witness bins: 0; items whose only CSV bins are witness
  bins: 0. So the 705/705 at 6a60d54 rests on DUT-sampled bins; the rule merely permits the
  opposite. Finding W-2 (low, becomes medium the day it is non-zero): the rule must exclude CG-WIT-001 (condition C-5),
  and print the two counts on every run.
- Side observation (low, W-3): nine ACTIVE features are named in no covergroup Features field other than CG-WIT-001's
  (F-DMEM-009, F-DMEM-034, F-DMEM-045, F-DMEM-051, F-IC-045, F-IC-046, F-IRQ-057, F-PMC-053, F-TRG-027), although their
  items' bins live in other covergroups (e.g. F-DMEM-009: CG-DMEM-001/CG-DMEM-003, F-DMEM-034: CG-DMEM-001, F-DMEM-045: CG-DMEM-008, F-DMEM-051: CG-DMEM-008). The
  Features fields of those covergroups should name them, so traceability does not run through the witness group.
- gen_trace_check.py from a clean archive of 6a60d54: PASS; 208 covergroups, 16045/16045 bins, 220 marked items,
  74 regression-level coverpoints.

## 4. Summary of required changes for v2f

W-1 (medium): gate excludes CG-WIT-001 and reports witnessed clauses separately; Section 1 counts the 220 witness bins
separately. W-2 (low): trace-checker rule excludes CG-WIT-001 from ACTIVE->bin and reports the witness-only counts.
C-1..C-4 recorded in gen_test_plan.md Section 0 and the Test Writer's structure check (C-1 is the Test Writer's; C-2
is TB Infra's dispatcher; C-3 is the DV Lead's generator). W-3 (low) as time allows. I re-check the gate sentence,
Section 1 and the tool on v2f.
