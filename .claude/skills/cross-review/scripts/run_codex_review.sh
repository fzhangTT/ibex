#!/usr/bin/env bash
# Run a codex review with the repo rubrics and a validated explicit target.
# Usage: run_codex_review.sh plan <file> [<file>...]     (pre-execution review)
#        run_codex_review.sh diff <base_sha> <head_sha>  (post-execution review)
# Writes the artifact to docs/dv/reviews/ and prints "VERDICT: <verdict> <artifact>".
# Exit: 0 on APPROVE/APPROVE-WITH-CHANGES, 2 on REQUEST-CHANGES, 1 on protocol errors.
#
# codex-cli 0.149.1 cannot combine `codex exec review --base/--commit` with a custom
# prompt (verified empirically, all argument orders) — so rubric reviews use plain
# `codex exec` with the resolved SHAs in the prompt, and this wrapper VALIDATES that
# the review output echoes both SHAs (the compensating control for the explicit-target
# requirement in CLAUDE.md's cross-model policy).
set -euo pipefail
REPO=$(git rev-parse --show-toplevel)
MODE=${1:?plan|diff}; shift
DATE=$(date +%Y-%m-%d)
RUBRICS=$(cat "$REPO"/ci/reviews/GUIDE.md "$REPO"/ci/reviews/*.md)

case "$MODE" in
  plan)
    TARGET_DESC="plan/spec file(s): $*"
    SCOPE_LINE="Review these documents against the spec and repo reality: $*"
    NAME="plan-$(basename "${1%.*}")"
    ;;
  diff)
    BASE=$(git rev-parse --verify "${1:?base}") ; HEAD_=$(git rev-parse --verify "${2:?head}")
    TARGET_DESC="committed diff ${BASE:0:8}..${HEAD_:0:8}"
    SCOPE_LINE="Review ONLY the committed diff range ${BASE}..${HEAD_} (use git diff/log yourself). Echo the exact range you reviewed, verbatim, on the first line of your output as: TARGET: ${BASE}..${HEAD_}"
    NAME="diff-${BASE:0:8}-${HEAD_:0:8}"
    ;;
  *) echo "unknown mode: $MODE" >&2; exit 1;;
esac

ART="$REPO/docs/dv/reviews/${DATE}-codex-${NAME}.md"
PROMPT="Cross-model review (Claude-side work, you review; policy: CLAUDE.md 'Cross-model review policy').
${SCOPE_LINE}
Apply every rubric below to what you review; read-only — modify nothing.
End with exactly one line: 'Final verdict: APPROVE' or 'Final verdict: APPROVE-WITH-CHANGES' or 'Final verdict: REQUEST-CHANGES', preceded by findings as [severity][file:line] issue — recommendation.

=== RUBRICS ===
${RUBRICS}"

RAW=$(mktemp)
command codex exec --sandbox read-only "$PROMPT" > "$RAW" 2>"$RAW.err" || { echo "codex exec failed"; cat "$RAW.err" >&2; exit 1; }

# Identity: prefer what the run itself reports; fall back to CLI/config probing.
CLI_VER=$(command codex --version 2>/dev/null | head -1)
RUN_MODEL=$(grep -m1 -oE 'model[:= ]+[A-Za-z0-9._-]+' "$RAW.err" "$RAW" 2>/dev/null | head -1 || true)
CFG_MODEL=$(grep -m1 -E '^model ' ~/.codex/config.toml 2>/dev/null || true)
CFG_REASONING=$(grep -m1 -E '^model_reasoning_effort' ~/.codex/config.toml 2>/dev/null || true)

{
  echo "# Cross-model review — ${TARGET_DESC}"
  echo
  echo "**Reviewer:** ${CLI_VER}; run-reported: ${RUN_MODEL:-n/a}; config: ${CFG_MODEL:-n/a}; reasoning: ${CFG_REASONING:-n/a}"
  echo "**Date:** ${DATE}"
  echo "**Target:** ${TARGET_DESC}"
  echo
  echo "---"
  echo
  cat "$RAW"
} > "$ART"

NV=$(grep -cE '^Final verdict: (APPROVE-WITH-CHANGES|APPROVE|REQUEST-CHANGES)$' "$ART" || true)
[ "$NV" -eq 1 ] || { echo "PROTOCOL ERROR: expected exactly one verdict line, found $NV in $ART"; exit 1; }
VERDICT=$(grep -E '^Final verdict: ' "$ART" | sed 's/Final verdict: //')
if [ "$MODE" = diff ]; then
  grep -Fq "TARGET: ${BASE}..${HEAD_}" "$ART" || { echo "PROTOCOL ERROR: review did not echo the exact target range (fixed-string match) — cannot trust scope. Artifact: $ART"; exit 1; }
fi
echo "VERDICT: $VERDICT $ART"
[ "$VERDICT" != "REQUEST-CHANGES" ] || exit 2
