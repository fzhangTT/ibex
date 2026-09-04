# rt38 plan: an explicit deferred fcov reference, distinct from a missing one

STATUS: SHELVED, NOT FOR IMPLEMENTATION. LOG-091 took the manifest route and the Critic ruled rt38 a relaxation of P-07; this file is kept as the record of the rejected alternative, for its measurement and its consumer enumeration.

Ruling LOG-089. Plan only; nothing is implemented until the cross-model plan review and the Critic verdict are
recorded. Author: Runtime Manager. Target files named in Section 6.

## 1. Intent

The testlist cannot express two different states. Nobody wrote an fcov manifest for an entry, and an entry whose
manifest exists, is committed and unchanged, but whose per-run check a recorded ruling defers. Both read as
`fcov_expectation_file: null`, so `fcov_policy_failures` fails them alike.

Measured consequence at the commit this plan is written against: calling that function on round 1's own 53
planned runs, with every verdict set to PASS as if each had passed its own checks, flips 39 of them to FAIL. They
are the 13 measured entries detached by LOG-086 and LOG-088, at three seeds each. `bad` is then non-zero, the
regression returns 2, and gen_round dies before `collect`, so the round is never indexed. The count is unchanged
by the detaches: the same 13 entries would have failed their own expectation checks before them, seven on
covergroups not built at that commit and six measured unmet by the round-1 pre-flight.

rt38 gives the second state its own shape and keeps it verifiable. It does not make the policy lenient.

## 2. Scope of the field survey behind this plan

Every consumer of `fcov_expectation_file` in dv/auto_dv/flow and dv/auto_dv/tools was read or called on the null
case, self-test lines excluded. The loader accepts null and holds a non-null path to three equalities;
`red_grading_deferred` is false and concerns red fixtures only; gen_run requests no check; gen_fcov returns None;
`post_fcov_checks` skips; `summarize` counts the run in `runs_without_fcov_manifest`, reporting only;
gen_dashboard renders "no manifest", display only. Exactly one site turns null into a verdict:
`fcov_policy_failures`. The change surface is therefore one predicate plus its record.

## 3. The key

`fcov_expectation_deferred: "<reason>"` on the entry, a non-empty one-line reason naming the ruling that defers
the check. The manifest path is NOT repeated in the key: for a measured entry the loader already requires
`fcov_expectation_file` to be exactly `<manifest home>/<entry name>.fcov.yaml` or null, so the deferred entry's
artefact is derivable by that same convention and can be held to the same three equalities. Repeating the path
in a second key was considered and rejected: it would admit a deferred entry naming another entry's manifest,
which the attached form already forbids.

## 4. Loader rule (gen_flow_util.check_test)

For every entry, in this order:

1. `fcov_expectation_file` null, entry measured, tier in `fcov_manifest_required_tiers`, and no
   `fcov_expectation_deferred` -> die. An entry cannot silently lose its manifest.
2. `fcov_expectation_file` non-null and `fcov_expectation_deferred` set -> die. The two are exclusive.
3. `fcov_expectation_deferred` set and not a non-empty string after stripping -> die.
4. `fcov_expectation_deferred` set and the derived `<manifest home>/<entry name>.fcov.yaml` missing, or its own
   `test` field not equal to the entry name -> die. The artefact stays proven present; only the check is deferred.
5. `fcov_expectation_deferred` set on an unmeasured entry or a check-tier entry -> die. The policy exempts those
   already, so the key there would carry no meaning and could mask a real omission later.

## 5. Policy text, before and after

Before (gen_regress.fcov_policy_failures, the whole per-run body):

    if t["tier"] in required and t.get("measured", True) and not t.get("fcov_expectation_file") \
            and r["verdict"] == C.VERDICT_PASS:
        r["verdict"] = C.VERDICT_FAIL
        r["reason"] = <no fcov_expectation_file on tier ...>
        <write the verdict and reason back to the run's result.yaml>

After:

    if not (t["tier"] in required and t.get("measured", True) and not t.get("fcov_expectation_file")):
        continue
    if t.get("fcov_expectation_deferred"):
        r["fcov_deferred"] = t["fcov_expectation_deferred"]
        continue
    if r["verdict"] == C.VERDICT_PASS:
        r["verdict"] = C.VERDICT_FAIL
        r["reason"] = <unchanged text>
        <write-back unchanged>

The failing branch keeps its `verdict == PASS` guard and its text verbatim, so no run that fails today passes
tomorrow. The deferred branch changes no verdict and never writes a verdict back.

## 6. Record wording

- Each deferred run carries `fcov_deferred: "<reason>"` in its result and in the regression manifest's run row.
- `fcov_summary` gains `deferred` (a count) and `tests_deferred` (the entry names with their reasons). The
  existing `pass` total is untouched, so a deferred run is never counted as having passed an expectation.
- gen_dashboard prints `expectation deferred: <reason>` where it prints `no manifest` today.
- The round record states those entries as counted-only with the expectation deferred, naming the ruling, beside
  the entries whose expectation was checked.
- gen_runtime_api.md documents the key, the five loader rules, and the sentence that a deferred entry's coverage
  is credited while its expectation is not checked.

Files: dv/auto_dv/flow/gen_flow_util.py, dv/auto_dv/flow/gen_regress.py, dv/auto_dv/flow/gen_flow_const.py (the
reason-key name and the deferred bucket name), dv/auto_dv/flow/gen_dashboard.py, dv/auto_dv/docs/gen_runtime_api.md.

## 7. Reds and self-tests

Five reds, each failing against the pre-change code and passing after, one per loader rule of Section 4.

Policy self-tests, both directions, added beside the three existing cases which stay unchanged and passing
(counted from the three calls to fcov_policy_failures in gen_regress's self-test, not from memory):

- a measured smoke entry WITH the key: the run stays PASS, no write-back, and it appears in `deferred` with its
  reason;
- the same entry WITHOUT the key: FAIL with today's text, which is the proof the absolute rule still holds.

Positive control on the real committed testlist, not a fixture: in an archive of HEAD with the key overlaid on
the 13 entries, the loader accepts them and the policy leaves all 39 runs PASS in the deferred bucket; without
the overlay the same call flips all 39, which is the measurement of Section 1 re-run as the control. A fabricated
fourteenth measured entry with neither key nor manifest still fails in both archives.

Whole-flow self-tests green: gen_flow_util, gen_regress, gen_run, gen_fcov, gen_verdict, gen_round, gen_mirror,
gen_serve_requests. Retained TDD log under dv/auto_dv/evidence/gen_tdd_logs/flow with a manifest row.

No simulation is required at any point: the loader and the policy are pure Python over the testlist and the run
records, so rt38 consumes no LSF and does not compete with a round dispatch.

## 8. What this does NOT relax

- An entry that never had a manifest still fails on every required tier. Rule 1 of Section 4 makes the omission
  louder than it is today, because it fails at load rather than at the merge.
- A deferred entry is never reported as passing an expectation, and its bins are never counted as covered.
- The artefact is still held to the three equalities through the derived conventional path.
- The measured merge, the measured/unmeasured vdb split (Critic R-5.5), and the unmeasured path are untouched.
- Red fixtures and `red_grading_deferred` are untouched; a red fixture naming a manifest stays a distinct
  mechanism.
- P6, LOG-067 and LOG-077 are untouched.
- Nothing in rt38 excuses the 123 bins the pre-flight found unmet at every seed. Deferring a check does not close
  a bin, and the round record must not read as though it does.

## 9. Sequencing and expected wall time

rt38 lands first, as a flow touch. The 13 entries get the key with their LOG-086 and LOG-088 reasons in a
separate testlist touch afterwards, with the confirmations that touch already uses.

Expected wall time, my own work, no LSF: implementation with the five reds and the two policy cases about 60 to
90 minutes; the retained log and the response rows about 20; the follow-up testlist touch with its confirmations
about 20 to 30. Review turnaround is not mine to estimate. Nothing here needs a simulator, a build or a queue
slot.
