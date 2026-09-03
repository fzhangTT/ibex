# Critic verdict: Test Writer landing 3k (commit 56e37d7, diff base e4cbdd8), batch-1 v8

Artifacts reviewed (committed blobs at 56e37d7; sha256 first 16 hex):

- dv/auto_dv/tests/gen_test_csr_reset.py  fa34eabf2967c152
- dv/auto_dv/evidence/gen_tdd_batch1.md  7ef4bef096b0d268
- dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_manifest.md  e16cfe02a836b062
- dv/auto_dv/fcov_expectations/gen_test_csr_reset.fcov.yaml  1b2f5dc1a524eb84
- the ten added logs dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_t206_* and gen_t206fix_* (manifest rows recomputed)

Date: 2026-09-03 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411,
DV_prompt.txt, gen_test_plan.md items TP-CSR-037 / 105..109, gen_fcov_plan.md CG-CSR-007 / CG-CSR-016, this clone's RTL and doc/.
Method: committed blobs only; from a clean archive of 56e37d7 with no environment variable: library self-test PASS (it checks
gen_test_csr_reset.py's structure and runs the manifest self-test), flow self-test PASS, --check-red-signatures PASS with
gen_test_csr_reset_red RED-OK, gen_fcov_manifest --test-module re-render byte-identical to the committed manifest; the ten logs
read from the blobs and their md5s recomputed. No subagent. The cross-model artifact was not read before Sections 1-4 were
written (its file name was seen in a directory listing); Section 5 is the reconciliation.

CRITIC VERDICT: APPROVE, with one medium owed with conditions (M-1, the manifest question) and three lows.

## 1. What the landing does and what was verified

The change is two files: gen_test_csr_reset.py drops knob_debug_req_regime from its schedulable set (four knobs remain:
imem_gnt_delay, imem_rvalid_delay, irq_line_mix, scr_key_delay) and its docstring says why; gen_tdd_batch1.md Section 13
records T-206. No plan, library, template, flow or manifest file changes.

- The incident (round 0, seed 1028791296) is on record: gen_t206_csr_reset_1028791296_asis_stdout_excerpt.log shows the
  draw `debug_req_regime=storm ...`, the phase-0 apply of the storm at cycle 63, the mid-run phase at c19746 and the
  runaway; the control gen_t206_csr_reset_1028791296_dbgnone_stdout_excerpt.log is the same seed with
  `pinned=knob_debug_req_regime` and PASS (`fire_schedule_applied ok=True reached 4 of 8 ... applied 4`). The knob is the
  only difference. Both excerpts' md5s equal the transcript's (df3e87f0..., 45be0c98...).
- The fix runs: the three round-0 seeds PASS with the four-knob draw printed in-log (`GEN_TEST_KNOBS pinned=- drawn=
  imem_gnt_delay=... irq_line_mix=... scr_key_delay=...`, no debug knob), GEN_TEST_BINS n=81 (the declared set, equal to
  the manifest's 81 bins), UVM_ERROR 0 in the sim.logs, fire_schedule_applied ok=True; the pinned red TP-CSR-106 at seed 1
  fails first (`fire_tp_csr_106 ok=False ... mcause got 0x40901104 expected 0x00000000`, RED-OK) under the fixed test.
  The four stdout md5s equal the transcript table's. Run headers carry sources_sha 156eb9357b79552e and template_sha
  abbe6fcb78e53a27 (the 3h template blob I hashed in gen_critic_batch1_v7.md); the build is out_head8, an export of
  9e7c440 with the 3h template, not the landed tree (14 TB files differ between 9e7c440 and e4cbdd8): acceptable for a
  change that touches the test's knob set only, and stated in the transcript.
- Manifest of logs: 10 rows in gen_tdd_logs/test_writer/gen_manifest.md, sizes and md5s recomputed from the blobs, 10/10.
- Cause analysis checked against the RTL: a debug request is taken regardless of mstatus.MIE (rtl/ibex_controller.sv
  handle_irq / debug_req path; interrupts are gated by MIE, debug requests are not), so a program without code in the
  debug-module window halts there and never returns to its report stores; the same round's irq_regime=storm on
  gen_test_rst_boot passed because that program keeps mie = 0 (its docstring says so). Not a DUT defect; the comparator
  followed the DUT with 0 mismatches.
- No other test schedules knob_debug_req_regime (grep of dv/auto_dv/tests at 56e37d7); knob_irq_regime is scheduled by
  gen_test_rst_boot (mie stays 0, declared) and gen_test_csr_reset.

## 2. The two judgements asked for

### 2.1 Unscheduling knob_debug_req_regime is an honest limit, not hidden plan stimulus

- The only item of this test whose Knobs line names debug_req_regime is TP-CSR-108 (gen_test_plan.md:6234-6243). Its
  Preconditions and Stimulus require a directed debug request within the first 32 cycles and a debug ROM that reads
  dcsr / dpc / dscratch0 / 1 first. This test never delivered that: its program has no code in the debug-module window and
  the DBG_REQ bridge codes are not rendered, and the docstring already declared the debug-mode clause not built
  (gen_test_csr_reset.py:28-29, unchanged by 3k). The knob as scheduled produced a random storm from the debug agent, not
  the item's stimulus, and the storm could only halt the core in a code-less window.
- So nothing the test was delivering is removed; a regime that produced only runaway is. The docstring states the reason
  and the seed (gen_test_csr_reset.py:54-58), the item's clause stays declared not built, and the red is on record.
- The remaining limit is the item itself: TP-CSR-108 is titled "dcsr via first debug entry; trigger CSRs in M" and the
  test builds the second half only. That was true before 3k and is the subject of 2.2.

### 2.2 The manifest question is raised, not answered, and understated

- The committed manifest (re-render identical) declares 81 must-hit bins and has no bins_not_hit section. By my count 13
  of them need a debug entry or a debug-mode CSR access that this test cannot make: gen_csr_debug_csr_cg.cp_csr.dcsr,
  cp_dbg.dbg, cp_trap.ok, cr_csr_dbg_trap.dcsr_dbg_ok (CG-CSR-007 samples only debug-CSR accesses; an access without a trap
  is a debug-mode access) and gen_csr_reset_read_cg.cp_csr.dcsr, cp_csr.dpc, cp_csr.dscratch0, cp_csr.dscratch1, cp_dbg.dbg,
  cr_dbg_reset.dcsr_dbg, dpc_dbg, dscratch0_dbg, dscratch1_dbg (CG-CSR-016: a hit proves the reset value was read back and
  compared; dcsr / dpc / dscratch are debug-mode-only, an M-mode read traps and reads nothing back). The transcript names
  two (gen_csr_debug_csr_cg.cp_dbg.dbg, cr_csr_dbg_trap.dcsr_dbg_ok).
- The transcript says these bins "are a separate question for the manifest (bins_not_hit or a debug-ROM program) before
  the test is measured for functional coverage". That is the honest statement of an open item, not its resolution: when
  Runtime measures this test the fcov gate fails on 13 declared bins, which is the mechanism working, but the manifest is
  known to be wrong today.

## 3. Findings

### M-1 (medium, disclosed; owed with conditions) [S6 fcov-expectation; S4 honesty over green] Thirteen declared must-hit bins are unreachable by this test and the manifest still declares them

- Location: dv/auto_dv/fcov_expectations/gen_test_csr_reset.fcov.yaml (bins section, the 13 listed in 2.2); the
  disclosure at gen_tdd_batch1.md Section 13 names 2.
- Why medium: the fcov-expectation leg of the trust triad requires the manifest to say what the test will hit; a manifest
  that declares bins the test cannot hit is an expectation known to be false, and it decides TP-CSR-108's crediting (the
  item's first half is the debug entry). The mechanism is disclosed and the two resolutions are named, so it is owed.
- Conditions: (a) the count corrected to the 13 bins (or my count refuted bin by bin); (b) before this test is measured,
  either bins_not_hit rows with the reason (no debug ROM in the program; DBG_REQ codes unrendered) for each, or a
  debug-ROM program plan with its owner and landing; (c) the DV Lead rules whether TP-CSR-108 may be credited from this
  test at all while its debug half is not built, or is split / moved to a debug-capable test; the ruling is recorded in
  the intervention log and the entry's rule (g) statement. Until then the test is measured only with the manifest as
  committed (LOG-044: REQUEST-CHANGES gates crediting, not measurement).

### L-1 (low) [S6 structural guard] The rule "no debug regime for a program without a debug ROM" lives in briefs only

The transcript says the template has no guard because the lint's red-source list is frozen (LOG-024d). The guard does
not need the lint: the yaml marks the knob `regime_set_consumer: dbg` and the program plan knows whether it emits
debug-window code, both TB-side facts, so the library can refuse a schedulable set that names a dbg-consumer knob for a
program without debug handling (and an irq-consumer knob for a program without a handler unless mie is pinned 0).
Proposed to the Orchestrator as a ruling; a red fixture (a test declaring the knob without debug handling refused at
import) would prove it.

### L-2 (low) [S6 evidence identity] The run header stamps the template but not the test module

The header line carries sources_sha and template_sha; the test module under test is identified only by its name and,
indirectly, by the drawn knob set. For a landing whose whole change is one test file, a test_sha in the header would
close the identity chain the way template_sha does. Add it to the harness header.

### L-3 (low) [S4 record] The Knobs sentence of the docstring still claims the item's Knobs line

gen_test_csr_reset.py:54-55: "the items' Knobs lines name imem_gnt_delay, imem_rvalid_delay, irq_line_mix,
debug_req_regime and scr_key_delay". True, and debug_req_regime belongs to TP-CSR-108 only, whose clause the test does not
build; say so in the sentence ("debug_req_regime is TP-CSR-108's, whose debug half is not built here") so a reader does
not take the test to cover the item's stimulus set.

### Informational

- I-1: the fix runs were made on out_head8 (9e7c440 + the 3h template), not on the landed tree; the change is a knob set
  so the result transfers, and the transcript states the build. No re-run is asked for.
- I-2: the transcript's "Lesson for every test" is consistent with the tree: no other test schedules the debug knob, and
  the one other test scheduling knob_irq_regime keeps mie = 0 by declaration.
- I-3: LOG-042e crediting conditions do not apply (gen_csr_reset is not a regime item).

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S1 stimulus: the removed regime was unrealistic for this
program (a debug storm without a debug ROM), so the change improves realism; S2 no checker changed; S4 honesty: the
incident, the cause and the control are on record with md5s that match; S6: TDD red (as-is) to green (three seeds) with a
control (the pinned knob) and the pinned item red kept; fcov-expectation leg: M-1. One-line verdict: PASS with M-1 owed.

## 5. Reconciliation with the cross-model artifact (dv/auto_dv/reviews/2026-09-03-claude-diff-e4cbdd8b-56e37d75.md, read after Sections 1-4 were written)

The artifact's verdict is APPROVE-WITH-CHANGES with two minors and one info; mine is APPROVE with one owed medium and
three lows. Same verifications, same results: the ten logs match the manifest byte-for-byte, the as-is excerpt reproduces
the runaway and the pinned-knob control passes, the three fix runs draw four knobs and PASS, the red run fails on
fire_tp_csr_106 only, the manifest re-render is byte-identical, no other test names the debug knob. The artifact adds a
confirming line I did not check (`[GEN_DBG] requests=0` in the fix runs); carried as the artifact's.

- Its first minor is my M-1: it lists the same 13 unreachable bins and calls the record an undercount, rating it minor
  because the failure would surface honestly once fcov is measured. I keep medium owed: the manifest is the
  fcov-expectation leg of the triad and the bins decide TP-CSR-108's crediting, so the resolution must precede
  measurement rather than follow it. Adopted from it: the renderer already honours a template-declared bins_not_hit
  (gen_fcov_manifest.py:257-302, the mechanism my batch-3 verdicts exercised), so condition (b) has a landed mechanism.
- Its second minor (the docstring does not say the declared manifest still carries debug-mode bins the test cannot hit;
  not_built = {} and bins_not_hit unset) is adopted and verified as L-4: add the sentence so docstring and manifest agree.
- Its info nit (the seed and T-206 in the docstring are a history breadcrumb) is not adopted: the seed is what makes the
  stated limit reproducible from the record, and the project's docstrings cite the T-id by convention; the author's
  choice stands.
- Mine that it does not carry: L-1 (a library-level guard from TB-side facts, proposed as a ruling), L-2 (test_sha in the
  run header), L-3 (the Knobs sentence).

### L-4 (low, adopted from the artifact, verified) The docstring and the manifest disagree about the debug-mode bins

gen_test_csr_reset.py:57-58 says the debug-mode clauses are the not-built clauses above; it does not say the committed
manifest still declares 13 debug-mode bins the test cannot hit (`not_built = {}` at :140, no bins_not_hit). One sentence
stating that, pending M-1's resolution, makes the two agree.
