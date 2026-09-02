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
    MANIFEST=""
    for f in "$@"; do MANIFEST="${MANIFEST}TARGET: $f@$(sha256sum "$f" | cut -c1-8)\n"; done
    SCOPE_LINE="Review these documents against the spec and repo reality: $*. Echo, verbatim, as the FIRST lines of your output, one line per file exactly as given here:\n${MANIFEST}"
    NAME="plan-$(basename "${1%.*}")"
    ;;
  diff)
    BASE=$(git rev-parse --verify "${1:?base}") ; HEAD_=$(git rev-parse --verify "${2:?head}")
    TARGET_DESC="committed diff ${BASE:0:8}..${HEAD_:0:8}"
    SCOPE_LINE="Review ONLY the committed diff range ${BASE}..${HEAD_} (use git diff/log yourself). Your output's FIRST line must be exactly: TARGET: ${BASE}..${HEAD_} — and your LAST line must be the single verdict line, nothing after it."
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
RUN_REASONING=$(grep -m1 -oiE 'reasoning( effort)?[:= ]+[a-z]+' "$RAW.err" "$RAW" 2>/dev/null | head -1 || true)
# Fail closed: identity requires the RUN's model and reasoning, not config defaults.
{ [ -n "$RUN_MODEL" ] && [ -n "$RUN_REASONING" ]; } || { echo "PROTOCOL ERROR: run did not report model/reasoning identity (model='$RUN_MODEL' reasoning='$RUN_REASONING')"; exit 1; }

{
  echo "# Cross-model review — ${TARGET_DESC}"
  echo
  echo "**Reviewer:** ${CLI_VER}; run-reported: ${RUN_MODEL}; ${RUN_REASONING}"
  echo "**Date:** ${DATE}"
  echo "**Target:** ${TARGET_DESC}"
  echo
  echo "---"
  echo
  cat "$RAW"
} > "$ART"

LAST=$(tail -n 1 "$RAW")
case "$LAST" in
  "Final verdict: APPROVE"|"Final verdict: APPROVE-WITH-CHANGES"|"Final verdict: REQUEST-CHANGES") VERDICT=${LAST#Final verdict: };;
  *) echo "PROTOCOL ERROR: last raw-output line is not the sole exact verdict line: '$LAST'"; exit 1;;
esac
NV=$(grep -cE '^Final verdict: (APPROVE-WITH-CHANGES|APPROVE|REQUEST-CHANGES)$' "$RAW" || true)
[ "$NV" -eq 1 ] || { echo "PROTOCOL ERROR: expected exactly one verdict line in raw output, found $NV"; exit 1; }
if [ "$MODE" = diff ]; then
  [ "$(head -n 1 "$RAW")" = "TARGET: ${BASE}..${HEAD_}" ] || { echo "PROTOCOL ERROR: first raw-output line is not the exact target echo. Artifact: $ART"; exit 1; }
else
  printf '%b' "$MANIFEST" | while IFS= read -r ln; do [ -z "$ln" ] && continue; grep -Fqx "$ln" "$RAW" || { echo "PROTOCOL ERROR: plan target line not echoed exactly: '$ln'"; exit 1; }; done || exit 1
fi
echo "VERDICT: $VERDICT $ART"
[ "$VERDICT" != "REQUEST-CHANGES" ] || exit 2
