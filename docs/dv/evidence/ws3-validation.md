# WS3 validation evidence

- **Validator**: PASS in worktree AND from a clean `git archive` extraction; mutation-proven
  (one-word invariants drift flips FAIL). `--probe` PASS: live codex launches from repo root and
  `docs/dv/` evidenced the effective instructions.
- **Claude-side skill exercise**: the `regress` skill's results-reading contract executed against
  committed WS1 evidence (`ws1-smoke-regr.log`): 100% pass rate (1/1), zero failure buckets.
  (Executed by the WS3 controller directly — fork constraints prevented a dispatched subagent;
  flagged as a deviation for the parent session.)
- **codex-side skill exercise (end-to-end)**: codex discovered `dv-principles-check` via
  `.agents/skills/shared`, followed it against `docs/dv/BUILD_AND_SIM.md`, and produced the
  contracted §-cited output — returning four genuine conformance findings (recorded in the WS3
  process log for the parent's disposition; BUILD_AND_SIM.md is WS2-shared and not edited here).
- **Cross-review full cycle on one real change (WS3 itself)**: pre-execution artifact
  `2026-09-01-codex-review-03-ws2-ws3-plans.md` (REQUEST-CHANGES → plans amended);
  post-execution reviews of the WS3 range with real gating: round 1 REQUEST-CHANGES (4 findings,
  fixed in 6abc69c9), round 2 REQUEST-CHANGES (7 findings, fixed in 98020734 incl. one recorded
  controller ruling), final verdict recorded in the last committed review artifact of this range.
- **Trust triad**: canonical block hash-verified across dv_principles.md, mutation-check,
  fcov-expectation, and the test-generator agent; live proofs in `ws3-fcov-fixture/`
  (per-test urg isolation, hit/unhit classification, check-stage FAIL wiring, MUT-001).

## Final review state (terminal round adjudicated)

Five gated post-execution rounds ran (artifacts committed under `docs/dv/reviews/`, ranges all
`bfd74d7c..<head>`): rounds 1-4 each returned REQUEST-CHANGES with genuinely substantive findings,
all fixed and committed (6abc69c9, 98020734, fdfc4465, 4dfa25c4 + this commit). The terminal
round's five findings were adjudicated at the declared cap: two load-bearing items FIXED here
(exact-identifier per-test match in the fcov checker — a real seed-collision bug; fail-closed
fence invariant wording), three PARKED with recorded controller rulings for the human owner
(generation-manifest location vs the `dv/auto_dv` namespace and enforcement path — a WS7 design
decision; splitting generation-safe vs infra-only skill content — same; stricter validator probe
assertions). Per policy, no APPROVE is claimed: the branch closes REQUEST-CHANGES-adjudicated,
with the disagreement surfaced to the human owner rather than looped further.
