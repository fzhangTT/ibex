#!/usr/bin/env bash
# Run a codex review with the repo rubrics and a validated explicit target.
# Usage: run_codex_review.sh plan <file> [<file>...]     (pre-execution review)
#        run_codex_review.sh diff <base_sha> <head_sha>  (post-execution review)
#        run_codex_review.sh replan <plan> <findings-artifact> <base_rev>
#          (scoped re-review: verify prior findings + review only the plan's
#           delta since base_rev — for plans too large to re-review whole)
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
    NL=$'\n'
    for f in "$@"; do MANIFEST="${MANIFEST}TARGET: $f@$(sha256sum "$f" | cut -c1-8)${NL}"; done
    SCOPE_LINE="Review these documents against the spec and repo reality: $*. Echo, verbatim, as the FIRST lines of your output, one line per file exactly as given here:${NL}${MANIFEST}"
    NAME="plan-$(basename "${1%.*}")"
    ;;
  replan)
    PLAN_F=${1:?plan file}; FIND_F=${2:?findings artifact}; BASEREV=$(git rev-parse --verify "${3:?base rev}")
    TARGET_DESC="scoped re-review: ${PLAN_F} (delta since ${BASEREV:0:8}) against findings in ${FIND_F}"
    NL=$'\n'
    MANIFEST="TARGET: ${PLAN_F}@$(sha256sum "$PLAN_F" | cut -c1-8)${NL}TARGET: ${FIND_F}@$(sha256sum "$FIND_F" | cut -c1-8)${NL}"
    SCOPE_LINE="Scoped re-review (a recorded re-review per CLAUDE.md's gate): ${PLAN_F} was previously reviewed at commit ${BASEREV} and received the findings in ${FIND_F}. Do exactly two things: (1) verdict EACH finding in that artifact ADDRESSED or NOT ADDRESSED against the current plan text, with line evidence; (2) review ONLY the plan's changes since that commit (run: git diff ${BASEREV} -- ${PLAN_F}) for new defects the remediation introduced. Do NOT re-review unchanged plan content. Echo, verbatim, as the FIRST lines of your output, exactly these lines:${NL}${MANIFEST}"
    NAME="replan-$(basename "${PLAN_F%.*}")"
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
RC=0
# 150 min: sized to the observed worst-case codex review duration.
timeout 9000 codex exec --sandbox read-only "$PROMPT" > "$RAW" 2>"$RAW.err" || RC=$?
if [ "$RC" -eq 124 ]; then
  echo "PROTOCOL ERROR: codex review timed out after 9000s (site watchdog rule) — raw kept at $RAW"; exit 1
elif [ "$RC" -ne 0 ]; then
  echo "codex exec failed (rc=$RC)"; cat "$RAW.err" >&2; exit 1
fi

# Identity: prefer what the run itself reports; fall back to CLI/config probing.
CLI_VER=$(command codex --version 2>/dev/null | head -1)
RUN_MODEL=$(grep -m1 -oE '^model[:= ]+[A-Za-z0-9._-]+' "$RAW.err" 2>/dev/null || true)
RUN_REASONING=$(grep -m1 -oiE '^reasoning( effort)?[:= ]+[a-z]+' "$RAW.err" 2>/dev/null || true)
# Fail closed: identity requires the RUN's model and reasoning, not config defaults.
{ [ -n "$RUN_MODEL" ] && [ -n "$RUN_REASONING" ]; } || { echo "PROTOCOL ERROR: run did not report model/reasoning identity (model='$RUN_MODEL' reasoning='$RUN_REASONING')"; exit 1; }

LAST=$(tail -n 1 "$RAW")
case "$LAST" in
  "Final verdict: APPROVE"|"Final verdict: APPROVE-WITH-CHANGES"|"Final verdict: REQUEST-CHANGES") VERDICT=${LAST#Final verdict: };;
  *) echo "PROTOCOL ERROR: last raw-output line is not the sole exact verdict line: '$LAST'"; exit 1;;
esac
NV=$(grep -cE '^Final verdict: (APPROVE-WITH-CHANGES|APPROVE|REQUEST-CHANGES)$' "$RAW" || true)
[ "$NV" -eq 1 ] || { echo "PROTOCOL ERROR: expected exactly one verdict line in raw output, found $NV"; exit 1; }
if [ "$MODE" = diff ]; then
  [ "$(head -n 1 "$RAW")" = "TARGET: ${BASE}..${HEAD_}" ] || { echo "PROTOCOL ERROR: first raw-output line is not the exact target echo. Raw kept at $RAW"; exit 1; }
else
  NLINES=$(printf '%s' "$MANIFEST" | grep -c .)
  [ "$(head -n "$NLINES" "$RAW")" = "$(printf '%s' "$MANIFEST" | grep .)" ] || { echo "PROTOCOL ERROR: leading lines do not equal the plan target manifest, in order. Raw kept at $RAW"; exit 1; }
fi
# All protocol checks passed — install the artifact atomically.
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
} > "$ART.tmp" && mv "$ART.tmp" "$ART"
echo "VERDICT: $VERDICT $ART"
[ "$VERDICT" != "REQUEST-CHANGES" ] || exit 2
