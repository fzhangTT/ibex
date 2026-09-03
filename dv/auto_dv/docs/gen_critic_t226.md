# Critic closure check: T-226, the template witness epilogue in the as-built COV_WITNESS <index> <group> form (commit ae4b2e2, diff base f2b9272)

Artifacts reviewed (committed blobs at ae4b2e2; sha256 first 16 hex):

- dv/auto_dv/tests/gen_test_template.py  d47cc7e90130fe5c
- dv/auto_dv/tests/gen_test_lib.py  95b94683d40ffc9b
- dv/auto_dv/tests/gen_fixtures/gen_ut_witness_base.py  64fdd6e1553f371d
- dv/auto_dv/tests/gen_fixtures/gen_ut_witness_ok.py  86927ab264008433
- dv/auto_dv/tests/gen_fixtures/gen_ut_witness_othergroup.py  b90fec4e3081bbfb
- dv/auto_dv/docs/gen_test_template_api.md  d39b4cb46cb28db9
- dv/auto_dv/evidence/gen_tdd_test_template.md  a60e87c9819a46a0
- dv/auto_dv/gen_tb/gen_knobs.py  831623ca746b8f38
- dv/auto_dv/env/gen_wit_bins.svh  7e83e60046d40a76
- dv/auto_dv/env/gen_fcov_pkg.sv  551aacf81c6165b7
- the eight added logs dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_t226_* (manifest rows recomputed, 8/8)

Date: 2026-09-03 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411,
gen_critic_tb_l2b.md M-1 (T-226) and its conditions, gen_component_api_fcov.md Section 7, the plan's WP-1 as built.
Method: clean archive of ae4b2e2; library self-test PASS and gen_knobs_codegen --check up to date on the archive; a script of
mine comparing the Python tables gen_knobs.WITNESS_IDS / WITNESS_GROUP_OF / WITNESS_GROUPS with the SV render
gen_wit_bins.svh (GEN_WITNESS_TP_NAMES, GEN_WITNESS_GROUP_OF, GEN_WITNESS_GROUP_NAMES): all three equal, 220 items, 90 groups;
the six retained fixture runs read from the blobs (headers, decisive lines, md5s). No subagent. The cross-model artifact
(2026-09-03-claude-diff-f2b9272d-ae4b2e22.md) was not read before Sections 1-3; Section 4 reconciles.

CRITIC VERDICT: APPROVE, with one medium owed (M-1, a structure-check gap the fixture base itself exercises; a LOG-024d ruling
item). The Test Writer's part of T-226 closes my gen_critic_tb_l2b.md M-1 condition for the template; the
end-to-end proof through the real dispatcher is owed with the first committed entry that lists witness_ids (Runtime's part).

## 1. What the touch does and what was verified

- gen_test_template.py witness_epilogue (:369-394): due items = passed fire checks with cycle_clause_true; each id must be in the
  entry's witness_ids (unchanged), the tables must be rendered (unchanged), and now the test's own plan group
  (lib.test_group(name) = gen_fcov_manifest.plan_group_of: gen_test_<x> -> gen_<x>, one home) must be known to WITNESS_GROUPS and
  must equal the rendered owner of every due item (lib.WITNESS_GROUP_OF); the command goes through GenBridge.cov_witness(tp, own),
  which sends COV_WITNESS <WITNESS_IDS[tp]> <WITNESS_GROUPS[own]> and returns the covergroup's distinct-bin count, logged as
  GEN_TEST_WITNESS id= code= group= group_idx= bins=. The arg1 = 0 defect of my l2b M-1 is gone.
- gen_test_lib.py exposes WITNESS_GROUP_OF / WITNESS_GROUPS beside WITNESS_IDS from gen_knobs; the F_PATCH lint still refuses a
  test module assigning the library tables (the fixtures are not test modules).
- Fixtures: the base replaces bridge.cov_witness with a recorder (the fixtures' fake code 7 must never reach the SV table now that
  the dispatcher routes the command) and patches the owner and group tables; the docstring "no SV side exists" is gone; a fifth
  fixture gen_ut_witness_othergroup is the red of the new owner check, with its unguarded control (the template minus the owner
  assertion, diff retained as gen_t226_unguarded_template.diff).
- Runs on out_head14 (sources 893384b8eec4e6d5, template_sha d47cc7e90130fe5c = the committed template, test_sha per fixture, e.g.
  86927ab264008433 = gen_ut_witness_ok.py): ok green (`GEN_TEST_WITNESS id=TP-CMP-036 code=7 group=gen_cmp_zcb group_idx=0 bins=0`,
  GEN_TEST_PASS); foreign, noid, notable reds with the designed GEN_TEST_FAIL lines; othergroup red (`witness for TP-CMP-036 owned by
  gen_cmp_zcmp_events, issued by gen_cmp_zcb`); the unguarded control witnesses the foreign owner (GEN_TEST_PASS from the template,
  the fixture's own assertion then fails the cocotb test: TESTS=1 PASS=0 FAIL=1). Manifest rows 8/8 recompute.
- API doc Section 9 describes the as-built form and says no committed entry lists witness_ids yet (Runtime's witness_render first).

## 2. Can the Python-side owner check and the SV check disagree?

- Both derive from one source. The Python tables (gen_knobs.py: WITNESS_IDS, WITNESS_GROUP_OF, WITNESS_GROUPS) and the SV tables
  (gen_wit_bins.svh: GEN_WITNESS_TP_NAMES, GEN_WITNESS_GROUP_OF, GEN_WITNESS_GROUP_NAMES) are rendered by gen_knobs_codegen.py from
  gen_trace_witness_ids.csv in the same order (items by row, groups by first appearance). At ae4b2e2 my script finds the three
  tables equal (220 items, 90 groups) and --check up to date, so the Python assert `owner == own` and the SV
  `GEN_WITNESS_GROUP_OF[idx] != owner` decide the same relation on the same index the bridge sends.
- When they could differ: only if one render is stale against the other (a CSV edit rendered into gen_knobs.py but not into the
  svh, or the reverse). Then the two checks disagree loudly, not silently: the Python side refuses or the SV side raises
  GEN_WITNESS_FOREIGN / GEN_CMD_DISPATCH, and either is a collected failure. A silent agreement in the wrong is possible only if
  both renders are stale in the same way against the CSV, which --check detects; --check is run by the unit test and not by the
  flow before a build (my gen_critic_tb_l3.md L-5). The residual is L-2 below.
- Group naming: `own` comes from the test's name (gen_test_<x> -> gen_<x>), the CSV's test_group column from the plan; a test
  hosting a group whose name does not follow the derivation fails loud ("the rendered witness tables know no group").

## 3. Findings

### L-1 (low) [S4 record] The unguarded control's result column

gen_tdd_test_template.md Section 10 lists t226_witness_othergroup_unguarded as "PASS (the check is the difference)"; the retained
excerpt shows the template's GEN_TEST_PASS followed by the fixture's own assertion failing the cocotb test (TESTS=1 PASS=0 FAIL=1).
Say "template PASS, fixture assertion FAIL" so the row reads as the ablation it is.

### L-2 (low) [S6 single source at build time] The two renders are proven equal only by the unit test

The flow compiles gen_wit_bins.svh and imports gen_knobs.py without running gen_knobs_codegen --check; a stale pair would fail loud
at the first witness but a same-way-stale pair (both behind the CSV) would witness under an outdated ownership. Run --check in the
build step or embed the CSV sha256 in both renders and compare it in the bridge handshake.

### Informational

- I-1: no retained run exercises the real path template -> bridge -> SV dispatcher -> covergroup (the fixtures record the command;
  the SV report line reads witnesses=0 in the ok run). The Test Writer states this ("the one real witness green follows" with the
  first entry that lists witness_ids); that green is the closing evidence of T-226 and belongs to Runtime's part.
- I-2: the closure rows CR-1v8-M-1 (T-222, the thirteen bins under bins_not_hit with a green run) and CR-1v8-L-2 / L-3 (test_sha
  in the run header; the Knobs sentence) in gen_critic_response_batch1.md match what I verified in the batch-3 touch; CR-1v8-L-1
  (the library-level guard) is deferred to the next template touch under LOG-050.

## 4. Reconciliation with the cross-model artifact (dv/auto_dv/reviews/2026-09-03-claude-diff-f2b9272d-ae4b2e22.md, read after Sections 1-3 were written)

APPROVE-WITH-CHANGES: three minors, three infos. Its reading of the two-sided check (one codegen run, one CSV, Python compares
names and SV compares indices from the same mapping) agrees with Section 2, and it adds that the flow's loader refuses an entry
whose ids span groups or whose CSV and rendered indices disagree. Verified and adopted:

### M-1 (medium, owed) [S6 structure check] A test can replace the template's bridge call or command method at run time and the lint does not refuse it

The artifact's first minor: the lint's class-body branch matches only `self.<attr>` assignments whose value is the bare self,
so `self.bridge.cov_witness = fake` inside a method passes check_test_source. I reproduced it on the archive with a copy of
gen_test_csr_reset.py carrying one injected line in its first method: `self.bridge.cov_witness = self._f` is ACCEPTED, and so is
`self.cmd = self._f` (the artifact believed the latter covered by F_OVERRIDE; it is not, as an instance assignment). The fixture
base itself uses the first form (gen_ut_witness_base.py:57), so the path is reachable from a test module. Consequence: a test
can disable the Python-side owner pre-check and the witness log line; it cannot disable the SV check (GEN_WITNESS_FOREIGN) or
forge the ledger, which stays the fact of record, and the COV_WITNESS token itself is still refused in tests. Why medium rather
than the artifact's minor: the guarantee the plan states (C-1: tests never issue the command; the template's epilogue is the one
issuer) rests on the lint, and the gap covers every template-owned method, not the witness path alone; it predates this touch
(the `self.cmd` form was accepted before it) and is disclosed here, so it is owed, not blocking. Required: under LOG-024d (the
frozen refused-form list) a ruling that extends F_ASSIGN to attribute chains rooted at self and to instance assignment of
template-owned methods, with red sources (`self.bridge.cov_witness = _f`, `self.cmd = _f`) in the library self-test.

- Its second minor is my L-1 (the unguarded control's result cell). Its third minor (the ok row's `bins=0` is the recorder's
  return and the sim.log shows witnesses=0) is my I-1; adopted addition: Section 10 should say in words that the fixtures prove
  the Python side only.
- Correction to my Section 2 from its verification, checked in the blob: Runtime's witness_render at ae4b2e2 (gen_flow_util.py:949-982)
  already implements the as-built form (no plusarg required; the ids' indices checked equal between the CSV and the rendered
  WITNESS_IDS; one owner group required; the plusarg None unless the SV constants home names one), so the API doc's "(T-226:
  Runtime's witness_render first)" is stale (its third info): the remaining step is an entry that lists witness_ids. The flow's
  index check covers a stale gen_knobs.py against the CSV; my L-2 residual is narrowed to the svh render, which the flow does not
  read.
- Its first info ("since landing 2b" in the fixture docstring narrates history) and its second (the paragraph after Section 9's
  rewritten text still describes the ledger as sampled on export events) are carried as its own, both record items for the next
  doc touch.

Mine that the artifact does not carry: L-2 as narrowed above.
