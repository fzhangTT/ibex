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
      neutralized (self_test verdict forced ok=True), --self-test reports PASS / exit 0 -
      the mutation SURVIVES undetected, proving the named detector (and nothing else) catches
      it. Both changes reverted; --self-test PASS on clean code. The record above is the generation-visible evidence contract; raw transcripts live
      in the infra-only evidence area, indexed from infra docs (never referenced from here -
      dv/auto_dv/** is generation-accessible and cites no infra/verification paths).

## MUT-002 (executed 2026-09-02)

    id: MUT-002
    result: full mutation-check procedure executed and passed (named detector CAUGHT the
      mutation with the hidden referee inert; ablation control SURVIVED with the detector
      disabled; reverted, re-verified green). All detail (file/line, original/mutated code,
      detector identity, commands, log excerpts) lives in the infra-only evidence area,
      indexed from infra docs (never referenced from here - dv/auto_dv/** is
      generation-accessible and cites no infra/verification paths).

## Index of mutation records in this directory

- `gen_mut_sva_rvalid_legal.md`: MUT-003, the bus-interface stimulus-legality self-check (T-068).
- `gen_mut_isa_fields.md`: MUT-004..MUT-007, per-field discrimination and ablation of the ISA comparator ids (T-068).
