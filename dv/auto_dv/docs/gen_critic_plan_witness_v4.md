# Critic verdict: witness protocol text, plan v2h (commit b40ff52), light check of Section 0 against the committed template

Artifacts: dv/auto_dv/docs/gen_test_plan.md at b40ff52 (sha256 84ce8298c8806cbe, 23424 lines; Section 0 protocol :76-98,
token rule :110-115, WP rows :470-478), dv/auto_dv/tools/gen_trace_check.py at b40ff52 (vocabulary check, rendered-table
equality, manifest-not-found and dict-form handling), compared with dv/auto_dv/tests/gen_test_template.py and
gen_test_lib.py as committed at b0d6a3f (template v4) and unchanged at HEAD. Date: 2026-09-03T12:02Z   Role: Critic. Scope as
signalled: one section, does the text describe the committed template; pending citations marked; icram rows; the
token-removal rule. No cross-model round 8 (no mechanism changed); nothing of it read.

CRITIC VERDICT: APPROVE

## 1. Section 0 describes the template as committed

Checked point by point against gen_test_template.py (finish at :323-337, witness_epilogue :339ff) and gen_test_lib.py
(tp_id_of, witness_ids_of, WITNESS_IDS):
- a fire_tp_<area>_<nnn> method calls self.check(what, ok, detail, cycle_clause_true=True) only on the TRUE branch of its
  cycle-level clause; check() returns a CheckResult the template records: matches (CheckResult namedtuple, self.results).
- the finish() epilogue runs after the failure raise and BEFORE the finish handshake: matches the code order
  (check-count guard, manifest check, failure raise :334, witness_epilogue :335, bridge.finish :336, PASS_MARKER :337).
- one awaited COV_WITNESS <code> per passed result with cycle_clause_true, method name mapped by lib.tp_id_of, each id
  required in the testlist entry's witness_ids (TP ids), code from the rendered WITNESS_IDS table: matches
  (due = ok and cycle_clause_true; foreign-id assert against lib.witness_ids_of(name); lib.WITNESS_IDS[tp]).
- one table name, WITNESS_IDS; code = index = the CSV row; TB Infra renders GEN_WIT_IDS (SV) and WITNESS_IDS (Python) from
  gen_trace_witness_ids.csv; the tool now checks a rendered WITNESS_IDS against the CSV whenever gen_knobs.py carries one.
- host rules C-1 (COV_WITNESS token refused in tests; cycle_clause_true only inside a fire_* self.check; foreign id,
  missing table or missing command fail the run): match check_test_source and witness_epilogue.
- C-2 in the index form: the dispatcher receives +gen_witness_ids=<indices>; Runtime's gen_run converts the entry's TP ids
  with the CSV at the pinned commit and records both forms and the CSV sha in result.yaml (WP-2), as ruled.
- Pending citations are marked as pending: "v4c aligns the file name, the table name WITNESS_IDS and the epilogue issue
  point, WP-1" and the unforgeability condition "(Test Writer commit pending (Test Writer landing))". Both honest: the
  template already takes ids only from CheckResult records, and the structure check already protects finish() and
  witness_epilogue() from overrides; what is pending is the commit that states it as a rule.

## 2. icram rows and the token-removal rule

- 17 TP-IC items carry icram rows (icram lookup, icram inject); the yaml renders icram inject only, and the tool's new
  Section 0 vocabulary accepts lookup, tag_write and fill_write ahead of the writers. Consistent with the sunset design:
  a row the build does not render counts as absent, so those items stay marked until TB Infra adds the rows; the
  vocabulary check now rejects a misspelt row instead of accepting any word (the earlier regex did).
- Operational rule (:110-115), as I asked in witness v3: at the first export landing the DV Lead removes the tokens of
  every item whose rows the build manifest's export_sources lists, in the same change as Runtime's export_sources landing,
  regenerating the plan and the CSV (marked = 0) with the Test Writer regenerating the manifests; a failing tool run
  between the two landings is the expected signal; removal is decided from the build manifest, never from the yaml alone.
  The tool now prints every sunset message (not the first 60) so the operator has the whole list.

## 3. Tool at b40ff52

Run by me from a clean archive: sunset (C-3): export sources unknown: no --build-manifest given; /tmp/claude-1211405897/-localdev-fzhang-ws-ibex-challenge/b61c04c6-06f1-4059-978d-29bc6123dadd/scratchpad/plan_v2h/dv/auto_dv/tb/gen_tb_knobs.yaml renders 29 exact rows and 0 wildcard rows (absen
The changes tighten checks (vocabulary instead of a shape regex; rendered-table equality; a missing build manifest reported
as unknown; export_sources accepted as strings or {source, event} maps); the sunset and reverse-rule mechanisms of v2g are
unchanged, so the absence of a cross-model round 8 is consistent with what changed.

## 4. Nothing owed on the plan side

Open items stay where they were: WP-1/WP-2/WP-7 (TB Infra, Runtime), WP-5 rule (f) in the generator (Test Writer), the
first witnessed run with its foreign-id red (template v4 L-4), the first real export_sources field.
