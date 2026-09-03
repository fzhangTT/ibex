# Critic verdict: witness ledger, third review (plan v2g, commit 7ac3744): C-3 implemented, reverse rule, rule (f)

Artifacts at commit 7ac3744 (sha256 first 16 hex, lines):
- dv/auto_dv/tools/gen_trace_check.py         3fe7b4bea5a9c3b8   155 (--knobs, --build-manifest, sunset, reverse rule)
- dv/auto_dv/docs/gen_trace_witness_ids.csv   c1ec0da46550f9c7   221 (header + 220 rows: index, tp_item, bin, test_group, marked)
- dv/auto_dv/docs/gen_test_plan.md            2d418ca6465562b8 23393 (Section 0 protocol in index form, WP-1..WP-7 at :453-459; 220 [export-rows: ...] annotations)
- dv/auto_dv/docs/gen_fcov_plan.md            27c5b4c72a2cac53  6992 (rule (f) at :37-38 and :6971; CG-WIT-001 Sample rewritten)
- dv/auto_dv/docs/gen_feature_list.md         af8c7d6f77de2cf2 13645
- dv/auto_dv/tests/gen_fcov_manifest.py       ea6d89c6c28a1329   305 (Test Writer's; no rule (f) code yet)
- dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md  e34bf1173833720c  266 (Sections 11 and 12)
Date: 2026-09-03T11:42Z   Role: Critic   Previous: gen_critic_plan_witness_v2.md (7594017; C-3 open, W-4 low). The round-7 artifact
was not read. Every tool result below is from my own runs on a clean archive of the commit with synthetic inputs.

CRITIC VERDICT: APPROVE on the re-checked items (C-3 implemented and verified; W-4 closed; rule (f) stated with a
sufficient input). One item stays open on the Test Writer's side: the generator does not apply rule (f) yet.

## 1. C-3, the mechanical sunset (verified by execution)

gen_trace_check.py parses the [export-rows: ...] annotation of every marked item (220 of 220 carry one; a marked item
without it or with a malformed row is an error), the yaml export event table (rows whose event is "<name>" count as
absent: 8 exact rows and 4 wildcard rows today), and an optional build manifest's export_sources. Runs from a clean
archive of 7ac3744:
1. No --build-manifest: PASS, exit 0; the sunset line reads "export sources unknown: no --build-manifest given; ...
   renders 8 exact rows and 4 wildcard rows (absent); ..." and nothing else changes.
2. Synthetic manifest with exactly the two rows of TP-ISA-024 (ibus req, ibus gnt): FAIL, exit 1, "20 still-marked
   items have every export row present", each named ("sunset: still-marked item whose export rows are all present in
   the build (remove the token, gen_test_plan.md Section 0): TP-ISA-024", ... TP-IC-057): every marked item whose row
   set is a subset of the build's rows fails, as the rule says.
3. Synthetic manifest with export_sources: [] : PASS, "0 rows; 0 still-marked items have every export row present".
4. Synthetic manifest without the field: PASS, "export sources unknown: <path> has no export_sources field (Runtime
   request, gen_test_plan.md Section 2a WP-6)".
5. Synthetic manifest with "pin irq_fast3" standing for an item's "pin irq_fast" row (TP-ISA-040's eight rows): FAIL,
   38 items named, TP-ISA-040 first: the irq_fast wildcard matches a numbered rendered row, as designed.
C-3 CLOSED. Operational note (not a finding): at the first export landing the failure list will be long (20 items
for two ibus rows); the DV Lead removes the tokens in bulk in the same change that Runtime adds export_sources.

## 2. W-4, the reverse rule

The tool computes the ACTIVE features named by no non-ledger covergroup's Features field (:69) and reports them as
violations. My own script over the committed feature list and coverage plan: 0 unnamed ACTIVE features (28 at
7594017). W-4 CLOSED.

## 3. Rule (f) and the witness-ids CSV

- Plan text: gen_fcov_plan.md:37-38 states rule (f) (ledger bins whose item carries the marker, column marked = 1 of
  gen_trace_witness_ids.csv, are excluded from the owning test's manifest); :6971 repeats it in the CG-WIT-001 block;
  Section 0 of the test plan gives the protocol in the index form (arg0 = CSV index, GEN_WIT_IDS rendered in CSV order)
  with request rows WP-1..WP-7 naming the owner of each part.
- The CSV is a sufficient single input for the generator: 220 rows, index 0..219 in the order of the CG-WIT-001 rows
  of gen_trace_tp_bin.csv, tp_item, bin, test_group and marked (all 220 marked today); the tool checks every one of
  those relations against the plan and the bin CSV and fails on a mismatch.
- OPEN (Test Writer, WP-5; my batch-1 M-2): gen_fcov_manifest.py at 7ac3744 has no reference to the CSV (0 hits), and
  regenerating gen_test_csr_trap_setup from this commit still emits 4 witness lines (w_tp_csr_029, w_tp_csr_031 and
  their notes), so the committed manifest of that test still declares two marked witness bins as must-hit. The
  response row CM-r6-M2 says this honestly ("generator and manifest are the Test Writer's"). Closes with the Test
  Writer's next landing; I re-check the regenerated manifests then.

## 4. Consistency of the protocol with what the template landed (b0d6a3f)

The template's witness_epilogue issues COV_WITNESS with lib.WITNESS_IDS[tp] as arg0 and refuses ids outside the entry's
witness_ids; WP-1 defines arg0 as the CSV index and WP-2 the per-test set as CSV indices in a plusarg. The two agree
once TB Infra renders WITNESS_IDS from the CSV in order (WP-1) and Runtime renders witness_ids into the entries (WP-2);
the Test Writer's structure check already refuses direct COV_WITNESS calls (WP-4). Nothing to change on the plan side.

## 5. What remains for the ledger

WP-5 (generator rule (f), Test Writer), WP-1/WP-2/WP-7 (TB Infra, Runtime), the first witnessed run with a red for the
foreign-id path (template v4 L-4), and the first real export_sources field (WP-6), after which the tool's sunset line
turns from "unknown" into a count and the DV Lead removes tokens.
