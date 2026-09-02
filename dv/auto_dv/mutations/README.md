# Mutation records

One block per mutation, kept as evidence next to the checker it proves (mutation-check skill).

    id: MUT-<NNN>
    file: <path>:<line>
    original: <the one-line original>
    mutated: <the one-line mutation>
    expected_detector: <the NAMED checker/test that must catch it>
    result: CAUGHT by <detector> (<date>); ablation control: SURVIVED with detector disabled; reverted.

## MUT-001 (worked example, executed 2026-09-01)

    id: MUT-001
    file: ci/check_fcov_expectations.py (classify())
    original: return [b for b in declared if hits.get(b, 0) <= 0]
    mutated:  return [b for b in declared if hits.get(b, 0) < 0]
    expected_detector: ci/check_fcov_expectations.py --self-test
    result: CAUGHT (--self-test FAIL, exit 2); reverted, --self-test PASS.
    ablation_control (executed 2026-09-01): with the mutation applied AND the detector
      neutralized (self_test verdict forced ok=True), --self-test reports PASS / exit 0 —
      the mutation SURVIVES undetected, proving the named detector (and nothing else) catches
      it. Both changes reverted; --self-test PASS on clean code. The record above is the generation-visible evidence contract; raw transcripts live
      in the infra-only evidence area, indexed from infra docs (never referenced from here —
      dv/auto_dv/** is generation-accessible and cites no infra/verification paths).

## MUT-002 (WS2 flagship checker, executed 2026-09-02)

    id: MUT-002
    file: dv/uvm/core_ibex/tb/core_ibex_tb_top.sv:487
    original: end else if (controller_state == ibex_pkg::IRQ_TAKEN) begin
    mutated:  end else if (1'b0) begin
    expected_detector: dv/cocotb/tests/test_irq_from_python.py's handler-entry check
      (the count == triggers_sent and count >= max(n, 3) asserts together)
    result: CAUGHT (2026-09-02): TEST=cocotb_irq_python_test COCOTB=1
      COCOTB_MODULE=dv.cocotb.tests.test_irq_from_python SEED=1, testlist sim_opts carrying
      +disable_cosim=1 for this run (hidden referee inert). Flow FAILED
      (0.00% PASS 0 PASSED, 1 FAILED); log-extract attribution:
        AssertionError: COCOTB-IRQ-CHECK: handler_entry_count=0 != triggers_sent=3; an
        IRQ_TAKEN entry not attributable to a python trigger occurred, or one was missed
      at dv/cocotb/tests/test_irq_from_python.py line 84 (the named equality assert) --
      no cosim-related or other failure signature present.
    ablation_control (executed 2026-09-02): same mutation applied, both handler-entry
      asserts commented out. Flow PASSED (100.00% PASS 1 PASSED, 0 FAILED) with
      handler_entry_count=0 (triggered=3, required>=3) logged and unchecked -- the
      mutation SURVIVES undetected by anything else in the flow (no cosim mismatch, no
      UVM_ERROR), proving the named checker is what catches it. All three edits (mutation,
      ablation, and the testlist +disable_cosim=1 addition) reverted; re-ran clean
      (100.00% PASS 1 PASSED, 0 FAILED, handler_entry_count=3 == triggers_sent=3).
    tdd_history_exception: this checker predates the trust triad's red-first order in this
      workstream (WS2 Milestone B shipped before mutation-check was applied retroactively);
      no fabricated red-then-green history is claimed. MUT-002 above is the compensating
      mutation-proof evidence, per the WS2 codex-review-04 ruling. Raw sim log excerpts for
      both the caught and ablation runs are in
      docs/dv/process-logs/ws2/mut-002-transcript.txt.
