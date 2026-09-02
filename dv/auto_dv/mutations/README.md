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
      it. Both changes reverted; --self-test PASS on clean code. Transcript in the WS3
      process log.
