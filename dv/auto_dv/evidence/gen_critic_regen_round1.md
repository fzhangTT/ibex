# Critic verdict: regen-round1 (the round-1 records regenerated at 4a00702; the round acceptance, CR-40 M-1)

Artifacts at 0203c6e (feature group regen-round1, GROUP COMPLETE; the group's one commit inside 3e23389..0203c6e, whose
other commits are the rt37 and pass-14-rows groups and records):
- dv/auto_dv/tools/gen_unbuilt_mark_check.py  8f4fa6c5099d863b  203 lines
- dv/auto_dv/tools/gen_covergroup_set.py  d8ced14adf74eaf8  189 lines
- dv/auto_dv/tools/gen_promotion_table.py  cdcb3bdf984b9e8a  111 lines
- dv/auto_dv/tools/gen_round_credit.py  911ba0a439a6f7fa  271 lines
- dv/auto_dv/evidence/gen_round1_covergroup_set.md  e9af1d9a328aa6b1  92 lines
- dv/auto_dv/evidence/gen_round1_covergroup_set.csv  76c85d151b5a5971  26 lines
- dv/auto_dv/evidence/gen_round1_promotion_table.md  4c30aa4493aaf7e5  41 lines
- dv/auto_dv/evidence/gen_round1_credit/gen_round1_credit.md  8a4995b774eadfbd  235 lines
- dv/auto_dv/evidence/gen_round1_credit/gen_round1_credit.csv  b976971a7ff5280e  186 lines
- dv/auto_dv/evidence/gen_round1_credit/gen_round1_credit_summary.md  f5710976bd48e009  47 lines
- dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md  2f19ff4b0e6c70f1  881 lines
Judged against: my round-1 record verdict CR-40 M-1 (gen_critic_round1_record.md:82-91 at 8c83b3a); gen_round1_request.md
Section 10 (:270-275, the acceptance clause); LOG-097 (3e23389: the regeneration at 4a00702 with the gen_unbuilt_mark_check.py
ledger blind spot fixed in the same group; the Critic's re-review lifts the acceptance gate); the DV Lead's finding of the
blind spot (TASKS.md 00:40:29Z: built 26 not 25, the ledger gen_wit_cycle_clause_cg rendered in gen_fcov_pkg.sv);
docs/dv/dv_principles.md d9c27db18f511411.
Date: 2026-09-05T02:55:16Z   Role: Critic
Method: detached worktrees of 0203c6e and of 4a00702 in my scratchpad (removed after the logs were retained under
dv/auto_dv/work/critic/regen1/); the three printed regeneration commands re-run twice (inside the 0203c6e worktree, and
with the 0203c6e tools copied into the 4a00702 worktree); the verifier run on the 0203c6e tree, on its self-test and on
three fixture trees against both the old (3e23389) and the new tool; the refusal probes; git diff for the baseline
records. EXPOSURE, stated plainly: before these sections were written I saw the commit subject of the range review 156dac5
in git log (its headline rows, including a Medium on gen_unbuilt_mark_check.py:64 reading 28 for 26) and read its three
rt37 body lines for the rt37 verdict; the regen-round1 body rows were not read before Section 6. My expectation of 26
rendered covergroups was written in dv/auto_dv/work/critic/gen_regen1_prep_notes.md at 01:47Z, before that subject
existed; the measurement below is mine.

## 1. What the group delivers
Six records under gen_round1_* names (the gen_round0_* baseline stays byte-identical: git diff 3e23389 0203c6e on the six
baseline paths is empty), four tool changes (gen_covergroup_set.py and gen_promotion_table.py: a required --label or
explicit output paths, exclusive, validated, no default; --note echoed shlex-quoted in a one-line printed regeneration
command; gen_round_credit.py: --note and the heading id round1-measured; gen_unbuilt_mark_check.py: reads
gen_fcov_groups.svh and gen_fcov_pkg.sv, fifth self-test case), and Section 19 of the DV Lead's response file (15 rows).
Figures in the records, re-derived: covergroup set 25 covergroups / 2864 referenced bins / 22 manifests; promotion table
20 entries; credit 185 hosted items in 17 groups, 66 credited, 50 unhit, 18 not fired, 51 unverified. They equal my
2026-09-04 22:26Z probe of the round manifest recorded in gen_round1_verdict_prep.md (185 / 66 / 50 / 18 / 51; 20; 25 / 2864 / 22).

## 2. Reproduction
- Byte for byte, at the inputs' commit: the 0203c6e tools copied into a worktree of 4a00702 and the three printed commands
  run there reproduce all six records byte-identical to 0203c6e (cmp on each; regen1/regen4a_*.log).
- At 0203c6e itself, five of six reproduce; gen_round1_covergroup_set.md differs in one line, its inputs digest
  (e203d99d614e in the record, 1f3fd629d171 at 0203c6e): two manifests changed between 4a00702 and 0203c6e
  (gen_test_bit_ratified.fcov.yaml 24 lines, gen_test_csr_trap_setup.fcov.yaml 2 lines) without changing the set (the
  .csv reproduces). The record header's wording ("from the commit that carries these inputs") is exact; the response
  row's is not (L-1).
- Refusal probes: bare gen_covergroup_set.py and gen_promotion_table.py exit 1 with "no output location: pass --label
  <team round name>, or ..." and write nothing (git status unchanged).
- gen_unbuilt_mark_check.py at 0203c6e: "MARK 147 marked coverpoint(s) of 1943 on 181 unbuilt covergroup(s); 28
  covergroup(s) rendered; DECL 22 referenced manifest(s) judged of 23 present; 0 declaration(s) on an unrendered
  covergroup; PASS"; --self-test PASS (five cases).
- The ledger fix, red and green on fixture trees copied from 0203c6e (regen1/fixture_*.log):
  (a) the MARK appended to the ledger coverpoint (gen_fcov_plan.md:6877, CG-WIT-001 cp_clause): old tool PASS
  (148 marks of 1944, 25 rendered), new tool "MARK FAIL gen_fcov_plan.md:6877 CG-WIT-001 cp_clause:
  gen_wit_cycle_clause_cg IS rendered", exit 1;
  (b) a referenced manifest (gen_test_rst_boot.fcov.yaml) declaring gen_wit_cycle_clause_cg.cp_clause.w_tp_isa_024: old
  tool DECL FAIL, new tool PASS. The blind spot is closed in both legs.
  (c) the same manifest declaring counts.cp_x.b: old tool DECL FAIL ("on unrendered covergroup counts"), new tool PASS.
  There is no covergroup "counts": see M-1.

## 3. The rendered set (M-1, measured)
The reader at gen_unbuilt_mark_check.py:64 applies re.findall(r"covergroup\s+(\w+)") to every source file; over
gen_fcov_pkg.sv it matches prose: line 5 (a comment, "the covergroup itself counts them") and line 79 (a uvm_error
string, "the covergroup counts %0d distinct bins"). The tool therefore holds 28 names, of which 26 are declarations
(line-start "covergroup <name>" with comments stripped: the 25 in gen_fcov_groups.svh plus gen_wit_cycle_clause_cg in the
package) and two are the words "counts" and "itself". Effects: the MARK line prints a false count (28); the DECL leg
accepts a bin declared on "counts" or "itself" as built (fixture (c)); the unbuilt figures are right (181 / 1943: neither
word is a plan covergroup). No committed plan line or manifest names either word, so no committed artifact is misjudged
today. The commit message and Section 19 (:878, "rendered covergroups 25 to 28") report the false count as the fix's
effect; the DV Lead's own finding said 26.

## 4. CR-40 M-1 and the acceptance
The regeneration half is MET: credit report, promotion table and covergroup set regenerated from the round's inputs at
its pinned commit 4a00702, labelled (record label round1, landing label regen-round1-at-4a00702, heading id
round1-measured), reproducible byte for byte, committed as round evidence with the Section 19 rows, the baseline
untouched. The remaining half of the row, one sentence in the log stating that Section 10's acceptance is met, is the
Orchestrator's to record after this re-review (LOG-097: "the Critic's re-review lifts the acceptance gate"). CR-40 M-1
is LIFTED by this verdict on that understanding; the tb_l40 REQUEST-CHANGES on the acceptance no longer stands.

## 5. Rows
- M-1 (Medium, OWED inside this APPROVE, disclosed, with a hard condition). gen_unbuilt_mark_check.py:64 reads prose as
  covergroup names (Section 3): 28 rendered for 26, and a bin declared on "counts" or "itself" passes the DECL leg.
  Required: match declarations only (a line whose first token is "covergroup", comments stripped, or the
  gen_<name>_cg shape the codegen emits), a self-test case with a comment and a string containing "covergroup <word>"
  that must not count, and the MARK line reading 26 on the tree. Condition: fixed and re-verified (fixture (c) fails
  again) BEFORE any verdict relies on this verifier, that is before the PMP step-1 family landing is judged under
  LOG-096; until then the tool's rendered count is not to be quoted. Owed rather than blocking because no committed
  artifact is misjudged (measured) and the group's purpose, the acceptance, does not rest on it.
- L-1 (Low, records). Section 19's row "Each record reproduces at the commit that carries it" is imprecise: at 0203c6e the
  covergroup-set record's inputs digest differs (Section 2); the records reproduce with the carrying commit's tools over
  the 4a00702 inputs, which is what the record headers say. State it that way.
- L-2 (Low, dv_principles.md Section 5 / the comment rule). The self-test comment at gen_unbuilt_mark_check.py:168-169
  ("Before the fix this case passed, which is the whole defect") narrates history; keep the intent ("a covergroup
  defined in the package counts as built") and drop the before/after.
- L-3 (Low, records). The 0203c6e commit message and Section 19 :878 state "rendered covergroups 25 to 28"; correct to 26
  with the M-1 fix (the message stands; the response row and any later record carry the corrected figure).
- Verified without finding: --label validation (letters, digits, underscore; exclusive with --md/--csv or --out); the
  printed commands are one unwrapped line and copy-paste reproduce (Section 2); the heading id and RECORD NOTE name both
  round names; the baseline six records byte-identical; the credit tool's heading dictionary comment states intent.
- dv_principles.md conformance: Sections 1, 2 and 6 do not apply to record generators and a plan verifier beyond their
  self-tests (the verifier's exists and passes; the generators prove themselves by byte reproduction); Section 4 honesty:
  the false 28 is L-3 and the M-1 cause; Section 5: L-2.

CRITIC VERDICT: APPROVE. The round-1 records are regenerated at the round's pinned commit, reproduce byte for byte, and
lift CR-40 M-1's regeneration requirement; the acceptance sentence follows in the log. The ledger blind spot is closed in
both legs of the verifier (measured red and green), with M-1 owed under the condition above: the same change taught the
verifier to read two words of prose as covergroups, to be fixed before the verifier judges the next family landing.

## 6. Reconciliation with the cross-model range review (body read after Sections 1-5)
dv/auto_dv/reviews/2026-09-04-claude-diff-3e233893-0203c6e5.md at 156dac5 (a341fd9bcd473ef5, APPROVE-WITH-CHANGES; one
Medium, three Lows, three Infos over the three groups), body read at 2026-09-05T02:56:06Z. Exposure as stated in the method line: its
subject was seen before Sections 1-5; the body was not.
- Medium (gen_unbuilt_mark_check.py:64 reads prose at gen_fcov_pkg.sv lines 5 and 79; 28 for 26; the row :878 records the
  inflated figure): the same finding as my M-1, the same two lines, the same remedy (anchor the match to a definition, a
  self-test case with "covergroup foo" in a comment, restate the row 25 to 26). The reviewer's "no false verdict today
  because plan covergroup names carry the gen_ prefix" is the same conclusion as my fixture (c): the false acceptance
  needs a manifest naming "counts" or "itself". M-1 stands, owed under its condition.
- Low (gen_fcov_plan.md:5066 names the superseded gen_round0_covergroup_set.md in the present tense; the "one live pointer"
  row is incomplete): not in my Sections 1-5; verified at 0203c6e (the line names gen_round0_covergroup_set.md in the present tense). Adopted as L-4: add the line to the plan-touch repoint list or correct
  Section 19's row to name both pointers.
- Low (gen_archive_manifest.md:8, 23 for 21 files): runtime-2's record, outside this verdict's target; noted, not judged.
- Low (:168-169 history-narrating comment) = my L-2.
- Info (gen_round_credit.py: --note and the header restructure beyond the heading id; the baseline gen_round0_credit.md no
  longer reproduces by its own printed command with HEAD tools): disclosed by the author in Section 19; the baseline's
  inputs drifted at the re-scope anyway, so it is a frozen record either way. Adopted as an observation, no row.
- Info (rt37 fixture literal) and Info (policy trail): the rt37 verdict's Section 5 covers them.
- Not in the review: L-1 (the "reproduces at the commit that carries it" wording against the measured digest difference at
  0203c6e). The verdict stands: APPROVE with M-1 owed under its condition, rows L-1..L-4; CR-40 M-1 lifted on the
  regeneration, the acceptance sentence to be recorded by the Orchestrator.
