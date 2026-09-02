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
    result: CAUGHT (--self-test FAIL, exit 2); reverted, --self-test PASS. Ablation control:
      the detector IS the self-test — with it not run, nothing else fails: survives trivially.
