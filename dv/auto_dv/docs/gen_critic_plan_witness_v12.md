# Critic verdict: plan witness v12 on 624fdea (the DV Lead's commits since v11's target f6b42ea: 8bd254c, e83b2cc, 4a71798, b57b08c, 812ed54, 8aa3292, ea4e5c6, 624fdea; the Test Writer's aa13338 as path B's committed side)

Artifacts reviewed (committed blobs at 624fdea; sha256 first 16 hex):

- dv/auto_dv/docs/gen_test_plan.md  23c6930fcd678e3f
- dv/auto_dv/docs/gen_fcov_plan.md  b7306b290ea55375
- dv/auto_dv/docs/gen_bug_log.md  4b2a9516c0a49c30
- dv/auto_dv/docs/gen_feature_list.md  92578d9722f6ec5b
- dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md  2abaf1d770691eb0
- dv/auto_dv/evidence/gen_round0_promotion_table.md  a8f18e1c678dfa96
- dv/auto_dv/evidence/gen_round0_covergroup_set.md  64f2992b0435f99f
- dv/auto_dv/evidence/gen_round0_covergroup_set.csv  78a0f66937c7f057
- dv/auto_dv/evidence/gen_round0_credit/gen_round0_credit.md  42eb41cd70e4b852
- dv/auto_dv/evidence/gen_round0_credit/gen_round0_credit.csv  56e722521b85bd88
- dv/auto_dv/evidence/gen_round0_credit/gen_round0_credit_summary.md  114391d27019c1f8
- dv/auto_dv/tools/gen_round_credit.py  438dcad08d57af20
- dv/auto_dv/tools/gen_plan_holds.py  3d365fd677c7716c
- dv/auto_dv/tools/gen_covergroup_set.py  a89dfed046cd9b09
- dv/auto_dv/tools/gen_promotion_table.py  ae7d7acada7947f1
- dv/auto_dv/flow/gen_testlist.yaml  adb6dc10617d7a9a
- dv/auto_dv/fcov_expectations/gen_test_cmp_zcmp_basic.fcov.yaml  4a4e9d432e48bcde
- dv/auto_dv/tests/gen_test_isa_alu.py  4e8764914f0f2c68
- dv/auto_dv/tests/gen_programs/gen_isa_alu_prog.py  04536ebfc7384210

Date: 2026-09-03 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411,
DV_prompt.txt, LOG-051 / LOG-055 / LOG-065 / LOG-069, the Zc specification (tools/specs/riscv-isa-manual/src/unpriv/zcmp.adoc:1163, :1174,
:1201-1202), upstream Spike's cm_mvsa01.h under tools/riscv-isa-sim (the allowed upstream clone: `require(insn.rvc_r1sc() != insn.rvc_r2sc())`),
rtl/ibex_compressed_decoder.sv, rtl/ibex_if_stage.sv, rtl/ibex_controller.sv, rtl/ibex_dummy_instr.sv, rtl/ibex_id_stage.sv, my v11 and tb_l6.
Method (as v11): clean archive of 624fdea; library self-test, flow self-test, gen_round_credit --self-test and gen_trace_check PASS; the three
generated evidence sets regenerated with the invocations printed in their headers: promotion table and covergroup set (md and csv) byte-
identical, the credit report and csv byte-identical when written to the committed paths (a scratch-path run differs only in the echoed output
paths of its own header line); every cited commit checked as an ancestor of 624fdea; two unnamed subagents (a statement-by-statement honesty
audit of the added plan text against the tree; a rulings review against spec, RTL and TB code), both told the fence and kept out of
dv/auto_dv/reviews/; the decisive facts re-checked first-hand. The ten cross-model artifacts for these commits were not read before Sections
1-5; Section 6 reconciles.

CRITIC VERDICT: REQUEST-CHANGES

The plan is honest against the tree in 55 of 66 checked statements, with two false sentences and seven imprecise ones (record items); every
ruling has a correct rationale and a decidable criterion; nothing is credited (0 of 162) and no hold is lifted beyond LOG-051. One medium
blocks: the LOG-051 carve-outs (twelve items UNCREDITED until T-183, four COUNTED ONLY) exist only as prose in the LIFTED records, while the
crediting rule says gen_round_credit.py applies the rule and the tool knows only hold sections that no longer exist (M-1).

## 1. Honesty against the tree (LOG-055)

The added or changed statements of gen_test_plan.md, gen_fcov_plan.md, gen_bug_log.md, gen_feature_list.md and the response file that
assert something about the tree were enumerated (66) and each checked against 624fdea: cited commits exist and are ancestors (all, except
7d1e521, cited only as the undone v2x per LOG-068); cited files and logs exist; described code and evidence present. Results: 55 TRUE, 7
PARTIAL, 2 FALSE, 2 UNVERIFIABLE (a Spike source path that is now verified first-hand, see Basis; and a forward-looking review-state clause).

Verified TRUE, among others: rule C-2 and WP-2 rewritten to the as-built witness form (my v11 L-3); the LIFTED records point at ff4637c for
the 165 / 246 held items (my v11 L-4) and the counts match that commit's sections; no gen_pmc_ctrl testlist entry is committed (15
occurrences of the sentence, all true); the shim's already-built counter behaviours and the two real gaps (retirement from Spike's minstret
delta; no mcountinhibit model) match gen_isa_shim.cc; B8's reproduction files and the run header's build sha exist as cited; the B8 RTL
anchors (if_stage :492-493, :526-528, :535, :808-809; compressed decoder :889, :937; dummy_instr :97, :103-104, :115; controller :474-477,
:498-500; id_stage :1218-1220) hold line by line; TP-CMP-074 exists as expected-fail (B8) with its group and four CG-CMP-008 witness bins in
the fcov plan; the B4 joint landing removed cm_mvsa01_yes from gen_test_cmp_zcmp_basic's manifest (472 bins) and the CSV row from TP-CMP-053;
the seven "iff rvfi_rd_addr != 0" result-class lines, cp_wrap's address-space definition and cp_mcen_gate's observation half are in 61c97c1's
diff; the thirteen csr_reset bins are under bins_not_hit at 54f2ee8; the credit report's embedded Section 1.7 equals the summary file.

FALSE: gen_bug_log.md:102 says tb-infra's gen_tdd_fcov.md:79 still carries the rlist-12 mis-attribution ("tb-infra to correct") while at
624fdea that line already reads rlist-15 (corrected in 61c97c1, an ancestor); the response file's regeneration row says "the 64-entry
testlist at 053fa2c" while that testlist has 71 entries (sha adb6dc10617d, equal to 624fdea's; 0a07536 had 64).

PARTIAL: "built in tb-infra landing 6 at 61c97c1" for the HINT-by-form rule (gen_fcov_plan.md:621) and for the mtvec low whole-value
threshold (:1221 area): both behaviours predate 61c97c1 in the sampler and landing 6 only documented them, so "ruled / recorded in landing 6"
is the true wording; "revised through 1bccc58" for gen_counter_csr_anchors.md while the file's last touch is 8ddd7f6; the CG-CSR-002 Sample
line's "(and, being a read-back, reopens)" where the sampler reopens a pair only on a write with rd != x0; three historical response rows
(CM74-M-3, CM87-L-2, CM92-M-2) describing a state that later commits superseded without a re-date; the landing-6 response row counting
five things "built there" where two were documented there.

## 2. Generated evidence, crediting and holds

- Regenerations: identical (Method). Headers name the input shas gen_test_plan.md 23c6930fcd67 and gen_testlist.yaml adb6dc10617d, both
  recomputed equal; the credit digest 7429f925df5c reproduces.
- Credit: 162 items hosted, credited 0, held 0, 162 NOT-RUN-CLEAN; no plan sentence or generated file credits an item; the LIFTED records
  keep LOG-051's scope (T-136; T-137 for bus-error arming with the twelve T-183 items UNCREDITED and TP-IRQ-079 / TP-SEC-025 COUNTED ONLY) and
  v2u adds TP-IRQ-073 / 075 to COUNTED ONLY (my v11 L-1, a narrowing). T-235 places gen_pmc_ctrl unmeasured and uncounted until the shim
  gaps close (a new carve-out by decision, no conflict with LOG-051).
- Tier rule: the promotion table flags gen_test_pmp_mseccfg and gen_test_pmp_lock "targeted (TESTLIST SAYS smoke)"; the testlist at 624fdea
  still lists both at smoke; LOG-069 assigns the fix to Runtime. The plan is honest (the flag shows); the testlist does not yet comply.

## 3. The rulings

| ruling | rationale checked | decidable | credits / built claims | weakening stated |
|---|---|---|---|---|
| B4-R1 (cm_mvsa01 with r1s' == r2s' is TP-CMP-051's expected-fail alone) | zcmp.adoc:1163 / :1174 make the encoding illegal; upstream Spike `require(rvc_r1sc() != rvc_r2sc())`; rtl/ibex_compressed_decoder.sv:778-806 has no illegal term and emits two moves with the COMMIT tag on the first (:790); TP-CMP-051 asserts the spec outcome and logs the RTL's, expected-fail | yes: the bin's owner in the CSV (TP-CMP-051 only), the manifest without it (472 bins), the reproducer entry expected_fail | nothing credited; the reproducer run cited exists (a9b63ae) | the bin leaves the only committed manifest with the reason; not stated: it is measured by no committed test until gen_cmp_zcmp_basic_xfail exists (a proposed group, L-4) |
| B8 recorded, TP-CMP-074, the mv-pair clause | the expansion FSM advances on id_in_ready_i with no dummy term while ID takes the dummy: the anchors verified; the 27 rows / 33 lost micro-ops tally reproduces from the export and the row mapping; the mv-pair clause (a dummy on the first move never replayed because the second carries LAST) follows :791 / :798 / :808-809 | yes: TP-CMP-074's fire-check quantities and checkers; expected-fail (B8) | not built, not claimed; CG-CMP-008 has no renderer and the row says so; dummy-enabled runs excluded from coverage evidence (manifest row, testlist measured false, TP-RST-022) | the Zcmp forms leave the dummies-on half of TP-RST-022 with the reason |
| T-235 (gen_pmc_ctrl unmeasured until the shim gaps close) | three of the five gaps verified in gen_isa_shim.cc (minstret-delta retirement :431 / :465-477; no mcountinhibit; no minstreth h-write), one stated as a measurement, one not checkable from the allowed read set | yes: no testlist entry; NOT BUILT on eleven items | "13 of 14 items built" is a relayed note; no test file exists; not credited | yes; one marker gap (L-6) |
| L5R-1 (cp_wrap as the address-space wrap) | the raw carry is 1 for every backward branch; a wrap of pc + imm is unreachable from the 0x80000000 window for branches and jumps, so CG-ISA-007.cp_wrap.yes waits for WP-9; path B: auipc imm20 0x7FFFF from any pc >= 0x80001000 wraps (0x80001000 + 0x7FFFF000 = 2^32); aa13338's program emits one such auipc per alignment in the second half, asserts pc >= 0x80001000, and gen_test_isa_alu.py:264-272 requires the wrap set at both alignments and compares the value from the linked pc: an asserted check, not only a bin; the sampler implements the definition (gen_fcov_pkg.sv:681-685) | yes | nothing credited; gen_isa_lui_auipc_cg is not rendered, so the isa_alu manifest's wrap bins are implemented by nothing yet (L-7) | fewer branch cases count: the intended correction, with reason |
| L5R-2 (mtvec low on the whole value) | equivalent to mtvec[31:12] == 0; the sampler tests v < 32'h1000 | yes | the code predates landing 6 (L-3) | none |
| L5R-3 (CG-CSR-002's Sample line names the sampler's own tracker) | matches csr_track (write opens, rd != x0 read-back closes, replacement counted); the three Sample lines still naming the non-existent gen_chk_csr_readback are disclosed with T-249 scheduled | yes | none | the anti-vacuity claim narrowed with the reason; one wording error (L-5) |
| L5R-4 (cp_mcen_gate from the pin in the write's W-DEC window) | the pin is the right observation; the built point is the RVFI record's arrival, GEN_CSR_WRITE_TO_RVFI_OFFSET after commit, equal while the pin is run-static | yes | the observation half built (61c97c1), WP-10 NOT BUILT stated | the deviation of the built point from the ruled window is not reconciled (L-8) |
| WP-10, T-249, TBQ-L4-1 / L4-2 | WP-10 NOT BUILT matches gen_agents_pkg.sv (the pin set once in build_phase); T-249 names six Sample lines, all present; HINT-by-form and na on rd = x0 match the sampler | yes | none | none |

## 4. Findings

### M-1 (medium) [S4 honesty; LOG-055] The LOG-051 carve-outs are prose the crediting tool does not apply

The crediting rule (gen_test_plan.md:206-210) says it is "applied by dv/auto_dv/tools/gen_round_credit.py" and excludes items "under no
measurement hold (Sections 1.4 / 1.5)". Those sections were removed in part 4b; gen_plan_holds.py discovers holds only from headings of the
form "## 1.<n> Items under the T-<xxx> measurement hold" (HOLD_HDR), of which the plan now has none, and gen_round_credit.py carries no
UNCREDITED / COUNTED-ONLY logic (grep: none). The twelve T-183 items, TP-IRQ-079 / TP-SEC-025 and now TP-IRQ-073 / 075 are therefore
excluded by sentences the tool never reads: the first clean measured round would credit them. No effect at 624fdea (0 credited, no clean
run), which is why this is a medium and not a high; undisclosed, which is why it blocks. Required: a machine-readable carve-out record the
tool applies (a hold-section form the existing discovery reads, tagged UNCREDITED / COUNTED-ONLY per item, or a table the credit tool
loads), a self-test case for each tag, and the rule sentence corrected from "Sections 1.4 / 1.5" to the record the tool reads; or, if the
carve-outs are to be applied by hand at the first crediting, the rule must say so and name who applies them.

### L-1 (low) [S4 record] Two false sentences

gen_bug_log.md:102 (the gen_tdd_fcov.md:79 attribution already corrected at 61c97c1) and the regeneration row's "64-entry testlist at
053fa2c" (71 entries). Correct both.

### L-2 (low) [S4 record] "Built in landing 6" for two behaviours landing 6 only documented

The HINT-by-form rule (gen_fcov_plan.md:621) and the mtvec low threshold (:1221 area) were already the sampler's behaviour before 61c97c1;
the landing-6 response row counts them among five things built there. Say "ruled / recorded".

### L-3 (low) [S4 record] Stale anchors

"revised through 1bccc58" for gen_counter_csr_anchors.md (last touch 8ddd7f6); the three historical response rows (CM74-M-3, CM87-L-2,
CM92-M-2) whose state later commits superseded, without a re-date.

### L-4 (low) [S4 disclosure] B4-R1 leaves the bin measured by nothing

cr_insn_equal.cm_mvsa01_yes is TP-CMP-051's, and gen_cmp_zcmp_basic_xfail is a proposed group with no test, manifest or testlist entry;
the rendered covergroup still carries the bin. State that it is measured by no committed test until the xfail test exists.

### L-5 (low) [S4 precision] The CG-CSR-002 Sample line's reopen clause

"the next CSR-op record with rd != x0 ... closes it (and, being a read-back, reopens)": csr_track reopens only when the closing record is
itself a write (is_write), a pure csrr closes without reopening. Correct the clause (also CM96-L-2's wording).

### L-6 (low) [S4 marker] gen_chk_csr_readback named as the gate without its UNBUILT marker

TP-PMC-022 and TP-PMC-032 name gen_chk_csr_readback as the gate of Ibex-specific behaviour while Section 0a marks it UNBUILT (read-backs
checked at program level meanwhile). Carry the marker into the two items.

### L-7 (low) [S4 disclosure] Path B's bins are implemented by nothing yet

gen_test_isa_alu.fcov.yaml declares cp_wrap.yes and the auipc wrap crosses under the new definition, and the test asserts the wrap
arithmetic (aa13338), but gen_isa_lui_auipc_cg is not rendered at 624fdea; the CM92-M-1 row should restate that the bins wait for the
renderer slice.

### L-8 (low) [S2 deviation] L5R-4's built observation point

The ruling asks for the pin in the write's W-DEC window; the built sampler reads it at the RVFI record (two cycles after commit), equal
while the pin is run-static and material once WP-10 lands with the 1..20-instruction spacing TP-PMC-057 wants. Record the deviation
beside the ruling until WP-10.

### Informational

- I-1: the testlist tiers of the two PMP tests violate the plan's tier rule at 624fdea; the promotion table flags it and LOG-069 assigns
  the fix to Runtime. Honest, pending.
- I-2: TP-CMP-065 / 074's fire-checks rely on dummies incrementing minstret, itself bug candidate B7; the plan says so.
- I-3: gen_covergroup_set.py's --fcov-dir fix reproduces the four historical totals the record states (3779 / 3778 / 3889).

## 5. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S4 honesty: 55 of 66 statements true, the false and imprecise ones record
items (L-1..L-3), the carve-outs' enforcement gap the one substantive contradiction (M-1); S2 derive from intent: every ruling anchored in the
spec, the RTL or the TB code (conforming), L5R-4's built point a stated-to-be deviation (L-8); S6: nothing credited, no hold lifted beyond
LOG-051, generated evidence reproducible. One-line verdict: FAIL on M-1 until the carve-outs are enforceable or the rule names the hand step.

## 6. Reconciliation with the nine cross-model artifacts (read after Sections 1-5 were written)

All nine are APPROVE-WITH-CHANGES (5e6186c0-8bd254c9, b151bdfb-e83b2cce, c0303177-4a717987, 1dbb8bff-b57b08c8, 4b78a0b6-812ed54e,
0670607d-8aa3292c, d54746c7-ea4e5c66, aa133386-624fdea5, 65b72282-aa133386). Their mediums are, in sequence, closed by the next commit
of the chain and the closures are verified in Section 1: the controller-anchor swap and the rlist-12 / rlist-15 attribution (v2t
artifact) fixed in v2u; the T-235 "runs unmeasured" sentence and the B4 reproducer citation (v2u artifact) fixed in v2v and the B4 joint
landing; the CG-ISA-004 cp_wrap redefinition against the committed isa_alu manifest and L5R-4 with neither path built (v2v artifact)
resolved by path B (v2w with aa13338) and the WP-10 NOT BUILT marker; the three remaining "gen_chk_csr_readback pair completion" Sample
lines undisclosed (L5R-3 artifact) disclosed in v2x/v2y with T-249; the landing-6 attributions stating the wrong commit state (v2w
artifact) corrected in v2x/v2y and v2z; the cp_mcen_gate line still calling landing 6 "awaiting commit" (v2x/v2y artifact) corrected in
v2z. The last artifact's medium (the cp_mcen_gate line records no deviation for the mechanism as built) is my L-8.

Adopted after verification:
- L-9 (low, from the v2x/v2y artifact): the T-249 row lists five manifests to re-render while gen_test_csr_trap_setup.fcov.yaml also quotes
  the anti-vacuity construct (154 occurrences of gen_chk_csr_readback in that manifest at 624fdea; the row does not name it).
  Add the sixth manifest to T-249 (or state why it is out of scope).
- The v2w artifact's low (TP-ISA-006's Preconditions still place the wrap iterations in the last page while the Stimulus now runs them
  in today's window too) is carried as its own for the next plan touch.

Mine that no artifact carries: M-1 (the LOG-051 carve-outs are prose the crediting tool does not apply), L-1 (the two false sentences),
L-4 (the B4 bin measured by nothing), L-6 (the UNBUILT marker on TP-PMC-022 / 032), L-7 (path B's bins implemented by nothing yet).
