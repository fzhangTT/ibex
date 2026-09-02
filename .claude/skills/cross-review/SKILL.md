---
name: cross-review
description: Execute the cross-model review policy — the other model reviews a plan/spec before execution or a diff after execution, producing a committed, gated artifact. Use for every plan and every completed workstream/change per CLAUDE.md.
---

# cross-review

Executes CLAUDE.md's "Cross-model review policy". The executing model never self-approves.

## When Claude executed (codex reviews)

- Pre-execution (plan/spec): `bash .claude/skills/cross-review/scripts/run_codex_review.sh plan <file> [...]`
- Post-execution (diff): `bash .claude/skills/cross-review/scripts/run_codex_review.sh diff <base_sha> <head_sha>`

The wrapper embeds every rubric from `ci/reviews/`, writes the artifact to `docs/dv/reviews/`
with a reviewer-identity header and explicit review target, extracts the machine-readable
verdict, and exits 2 on `REQUEST-CHANGES`.

CLI reality (verified): codex-cli 0.149.1 cannot combine `codex exec review --base/--commit`
with a custom prompt in any argument order, so rubric reviews use plain `codex exec` with
resolved SHAs in the prompt — and the wrapper REFUSES an artifact that does not echo the exact
target range (`TARGET: <base>..<head>` line), which is the compensating control. If a future
CLI version lifts the limitation, switch to the explicit flag and drop the echo check.

## When codex executed (Claude reviews)

Run `claude -p` with: the same rubric set (`cat ci/reviews/GUIDE.md ci/reviews/*.md`), the
explicit target range, the same verdict-line contract; save the artifact to `docs/dv/reviews/`
with the identity header (claude CLI version + model) and commit it.

## Gate semantics (binding)

- `REQUEST-CHANGES` blocks progress: remediate (or record a controller ruling for disputed
  findings), then re-run this skill for a recorded re-review; proceed only on
  `APPROVE`/`APPROVE-WITH-CHANGES`.
- Commit the artifact(s) — including superseded rounds — under `docs/dv/reviews/`; they are the
  trust-evidence trail.
- Disagreement with a recorded controller ruling goes to the human owner, not back into the loop.
