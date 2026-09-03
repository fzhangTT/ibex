---
name: cross-review
description: Execute the cross-model review policy — the other model reviews a plan/spec before execution or a diff after execution, producing a committed, gated artifact. Use for every plan and every completed workstream/change per CLAUDE.md.
---

# cross-review

Executes CLAUDE.md's "Cross-model review policy". The executing model never self-approves.

## When Claude executed (codex reviews)

- Pre-execution (plan/spec): `bash .claude/skills/cross-review/scripts/run_codex_review.sh plan <file> (the file must be committed at HEAD: the reviewer reads the HEAD blob in a detached checkout, never the working tree) [...]`
- Post-execution (diff): `bash .claude/skills/cross-review/scripts/run_codex_review.sh diff <base_sha> <head_sha>`
- Optional: `REVIEW_FOCUS="<one sentence>"` in the environment adds an owner focus line to the
  prompt (rubrics and verdict contract still apply unchanged).

The wrapper embeds the Zone A rubric set — `GUIDE.md` plus exactly the five rubrics
`ai-slop-comments.md`, `rtl-purity.md`, `magic-numbers.md`, `forces-and-hier-access.md`,
`assertion-integrity.md` — and REFUSES to run if `ci/reviews/` does not contain exactly that set
(a missing or extra rubric is loud, never silent). It writes the artifact to `dv/auto_dv/reviews/`
with a reviewer-identity header and explicit review target, extracts the machine-readable verdict,
and exits 2 on `REQUEST-CHANGES`.

CLI reality (verified): codex-cli 0.149.1 cannot combine `codex exec review --base/--commit`
with a custom prompt in any argument order, so rubric reviews use plain `codex exec` with
resolved SHAs in the prompt — and the wrapper REFUSES an artifact that does not echo the exact
target range (`TARGET: <base>..<head>` line), which is the compensating control. If a future
CLI version lifts the limitation, switch to the explicit flag and drop the echo check.

## When codex is unavailable (Claude substitute)

Per CLAUDE.md's fallback clause: a fresh Opus-class-or-above Claude session (an unnamed subagent
with `model: opus`, or `claude -p`) gets the same prompt shape — target manifest echo, rubric set,
owner focus, single final verdict line. Record in the header: CLI version, model, and WHY codex was
unavailable (timeout, spend cap, outage) with the raw codex error kept in the artifact.

## When codex executed (Claude reviews)

Run `claude -p` with: the same Zone A rubric set (cat `ci/reviews/GUIDE.md` plus the five rubric
files named above — never a glob), the explicit target range, the same verdict-line contract; save
the artifact to `dv/auto_dv/reviews/` with the identity header (claude CLI version + model) and
commit it.

## Gate semantics (binding)

- `REQUEST-CHANGES` blocks progress: remediate (or record a controller ruling for disputed
  findings), then re-run this skill for a recorded re-review; proceed only on
  `APPROVE`/`APPROVE-WITH-CHANGES`.
- Commit the artifact(s) — including superseded rounds — under `dv/auto_dv/reviews/`; they are the
  trust-evidence trail.
- Disagreement with a recorded controller ruling goes to the human owner, not back into the loop.
