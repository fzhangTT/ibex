#!/usr/bin/env bash
# Cross-model review entry point (CLAUDE.md policy). Prefers codex through the fence-provided
# wrapper; when codex is unavailable (spend cap, outage) falls back to a fresh
# `claude -p --model fable` session (owner ruling A-001) with the identical rubric set, target
# echo, and verdict contract, and records why codex was unavailable in the artifact header.
# Usage: gen_cross_review.sh plan <file> [...] | diff <base> <head> | replan <plan> <findings> <base_rev>
# Env:   REVIEW_FOCUS (optional owner focus sentence), REVIEWER=auto|codex|claude (default auto),
#        CLAUDE_REVIEW_MODEL (default fable), CLAUDE_REVIEW_EFFORT (default high).
# Prints "VERDICT: <verdict> <artifact>". Exit 0 on APPROVE/APPROVE-WITH-CHANGES, 2 on
# REQUEST-CHANGES, 1 on protocol errors.
set -euo pipefail
# Run from a private copy: bash reads scripts incrementally, so an edit to this file while a
# review is in flight would otherwise be executed at a stale offset.
if [ -z "${GEN_XR_RELOCATED:-}" ]; then
  _xr_root=$(git rev-parse --show-toplevel)/dv/auto_dv/work/orchestrator/review_self; mkdir -p "$_xr_root"; _self_copy=$(mktemp "$_xr_root/self.XXXXXX.sh"); cp "$0" "$_self_copy"
  GEN_XR_RELOCATED="$_self_copy" exec bash "$_self_copy" "$@"
fi
trap 'rm -f "$GEN_XR_RELOCATED"' EXIT
REPO=$(git rev-parse --show-toplevel); cd "$REPO"
MODE=${1:?plan|diff|replan}; shift
DATE=$(date +%Y-%m-%d)
WRAP=.claude/skills/cross-review/scripts/run_codex_review.sh
REVIEWER=${REVIEWER:-auto}
MODEL=${CLAUDE_REVIEW_MODEL:-fable}
EFFORT=${CLAUDE_REVIEW_EFFORT:-high}
NL=$'\n'

CODEX_ERR=""
probe_codex() {
  local out err
  out=$(mktemp); err=$(mktemp)
  if timeout 180 codex exec --sandbox read-only "Reply with exactly one line: PROBE-OK" >"$out" 2>"$err" \
     && grep -q 'PROBE-OK' "$out"; then rm -f "$out" "$err"; return 0; fi
  CODEX_ERR=$(grep -m1 -E 'ERROR|error|cap|timed out|Timeout' "$err" "$out" 2>/dev/null | sed 's/^[^:]*://' || true)
  [ -n "$CODEX_ERR" ] || CODEX_ERR="codex probe failed with no error text (rc/timeout)"
  rm -f "$out" "$err"; return 1
}

if [ "$REVIEWER" = codex ] || { [ "$REVIEWER" = auto ] && probe_codex; }; then
  rm -f "$GEN_XR_RELOCATED"; exec bash "$WRAP" "$MODE" "$@"
fi
[ "$REVIEWER" != codex ] || { echo "PROTOCOL ERROR: REVIEWER=codex forced but codex unavailable: $CODEX_ERR" >&2; exit 1; }
[ -n "$CODEX_ERR" ] || CODEX_ERR="REVIEWER=claude forced by caller"

# Same positive-list rubric assertion as the codex wrapper (a missing or extra rubric fails loud).
ZONE_A_RUBRICS="ai-slop-comments.md forces-and-hier-access.md magic-numbers.md rtl-purity.md assertion-integrity.md"
EXPECTED=$(printf '%s\n' GUIDE.md $ZONE_A_RUBRICS | LC_ALL=C sort)
ACTUAL=$(cd ci/reviews && ls -1 | LC_ALL=C sort)
[ "$ACTUAL" = "$EXPECTED" ] || { echo "PROTOCOL ERROR: ci/reviews/ does not match the Zone A rubric set." >&2; echo "have: $(echo $ACTUAL)" >&2; echo "want: $(echo $EXPECTED)" >&2; exit 1; }
RUBRICS=$(cd ci/reviews && cat GUIDE.md $ZONE_A_RUBRICS)

MANIFEST=""
case "$MODE" in
  plan)
    TARGET_DESC="plan/spec file(s): $*"
    for f in "$@"; do MANIFEST="${MANIFEST}TARGET: $f@$(sha256sum "$f" | cut -c1-8)${NL}"; done
    SCOPE_LINE="Review these documents against the spec and repo reality: $*. Echo, verbatim, as the FIRST lines of your output, one line per file exactly as given here:${NL}${MANIFEST}"
    NAME="plan-$(basename "${1%.*}")" ;;
  replan)
    PLAN_F=${1:?plan file}; FIND_F=${2:?findings artifact}; BASEREV=$(git rev-parse --verify "${3:?base rev}")
    TARGET_DESC="scoped re-review: ${PLAN_F} (delta since ${BASEREV:0:8}) against findings in ${FIND_F}"
    MANIFEST="TARGET: ${PLAN_F}@$(sha256sum "$PLAN_F" | cut -c1-8)${NL}TARGET: ${FIND_F}@$(sha256sum "$FIND_F" | cut -c1-8)${NL}"
    SCOPE_LINE="Scoped re-review (a recorded re-review per CLAUDE.md's gate): ${PLAN_F} was previously reviewed at commit ${BASEREV} and received the findings in ${FIND_F}. Do exactly two things: (1) verdict EACH finding in that artifact ADDRESSED or NOT ADDRESSED against the current plan text, with line evidence; (2) review ONLY the plan's changes since that commit (run: git diff ${BASEREV} -- ${PLAN_F}) for new defects the remediation introduced. Do NOT re-review unchanged plan content. Echo, verbatim, as the FIRST lines of your output, exactly these lines:${NL}${MANIFEST}"
    NAME="replan-$(basename "${PLAN_F%.*}")" ;;
  diff)
    BASE=$(git rev-parse --verify "${1:?base}"); HEAD_=$(git rev-parse --verify "${2:?head}")
    TARGET_DESC="committed diff ${BASE:0:8}..${HEAD_:0:8}"
    SCOPE_LINE="Review ONLY the committed diff range ${BASE}..${HEAD_} (use git diff/log yourself). Your output's FIRST line must be exactly: TARGET: ${BASE}..${HEAD_} and your LAST line must be the single verdict line, nothing after it."
    NAME="diff-${BASE:0:8}-${HEAD_:0:8}" ;;
  *) echo "unknown mode: $MODE" >&2; exit 1 ;;
esac
[ -z "${REVIEW_FOCUS:-}" ] || SCOPE_LINE="${SCOPE_LINE}${NL}Review focus requested by the owner: ${REVIEW_FOCUS}"

mkdir -p dv/auto_dv/reviews
ART="dv/auto_dv/reviews/${DATE}-claude-${NAME}.md"
# Never overwrite an earlier round: plan and replan targets keep their basename across rounds.
_r=2; while [ -e "$ART" ]; do ART="dv/auto_dv/reviews/${DATE}-claude-${NAME}-r${_r}.md"; _r=$((_r+1)); done
mkdir -p "$REPO/dv/auto_dv/work/orchestrator/review_tmp"; XR_TMP=$(mktemp -d "$REPO/dv/auto_dv/work/orchestrator/review_tmp/run.XXXXXX"); PROMPT_F="$XR_TMP/prompt.txt"
cat >"$PROMPT_F" <<PEOF
Cross-model review (Claude-side work executed in another session; you review from a fresh session; policy: CLAUDE.md 'Cross-model review policy'). You are the independent reviewer, not the author: never approve because the work looks plausible; verify against the repository.
${SCOPE_LINE}
Apply every rubric below to what you review; read-only, modify nothing. Deliver the whole review as ONE final message with no questions to the user. Write NOTHING before the TARGET line(s): no preamble, no status sentence; the TARGET line is the first character of your message.
End with exactly one line: 'Final verdict: APPROVE' or 'Final verdict: APPROVE-WITH-CHANGES' or 'Final verdict: REQUEST-CHANGES', preceded by findings as [severity][file:line] issue - recommendation.

=== RUBRICS ===
${RUBRICS}
PEOF

RAW="$XR_TMP/raw"; RC=0
# 60 min: bounded per the site watchdog rule.
# OS-level sandbox (bubblewrap, unprivileged): the filesystem is bound read-only except this run's own
# output directory, so the reviewer cannot modify the clone. Network stays open because the model API
# needs it (a residual the codex sandbox does not have); web tools are disallowed by policy.
command -v bwrap >/dev/null || { echo "PROTOCOL ERROR: bwrap (bubblewrap) is required for the read-only reviewer sandbox"; exit 1; }
# Scratch HOME for the reviewer: only the CLI's credentials and account state are copied in, so the
# executing model's settings, global instructions, memory and hooks are neither readable nor writable
# from the sandbox. The reviewer's tool permissions therefore come from this command line alone.
RUN_HOME="$XR_TMP/home"; mkdir -p "$RUN_HOME/.claude"
[ -f "$HOME/.claude.json" ] && cp "$HOME/.claude.json" "$RUN_HOME/.claude.json"
[ -f "$HOME/.claude/.credentials.json" ] && install -m 600 "$HOME/.claude/.credentials.json" "$RUN_HOME/.claude/.credentials.json"
# The CLI itself is installed under $HOME on this host; expose that install read-only inside the scratch HOME.
CLAUDE_BIN=$(readlink -f "$(type -P claude)") || { echo "PROTOCOL ERROR: claude CLI not found"; exit 1; }
SANDBOX=(bwrap --ro-bind / / --dev /dev --unshare-pid --proc /proc --tmpfs /tmp --bind "$XR_TMP" "$XR_TMP" --bind "$RUN_HOME" "$HOME")
[ -d "$HOME/.local" ] && SANDBOX+=(--ro-bind "$HOME/.local" "$HOME/.local")
timeout 3600 "${SANDBOX[@]}" -- "$CLAUDE_BIN" -p --model "$MODEL" --effort "$EFFORT" --permission-mode dontAsk \
  --allowedTools "Read,Grep,Glob,Bash" --disallowedTools "Write,Edit,MultiEdit,NotebookEdit,WebFetch,WebSearch,Agent,Workflow" \
  --output-format json <"$PROMPT_F" >"$RAW.json" 2>"$RAW.err" || RC=$?
if [ "$RC" -eq 124 ]; then echo "PROTOCOL ERROR: claude review timed out after 3600s; raw kept at $RAW.json"; exit 1
elif [ "$RC" -ne 0 ]; then echo "claude -p failed (rc=$RC)"; cat "$RAW.err" >&2; exit 1; fi
python3 - "$RAW.json" "$RAW" >"$RAW.meta" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
text = d.get("result") or ""
open(sys.argv[2], "w").write(text.rstrip("\n") + "\n")
print("MODELS=" + ",".join(sorted((d.get("modelUsage") or {}).keys())))
print("SESSION=" + str(d.get("session_id")))
print("IS_ERROR=" + str(d.get("is_error")))
PY
RUN_MODEL=$(sed -n 's/^MODELS=//p' "$RAW.meta"); SESSION=$(sed -n 's/^SESSION=//p' "$RAW.meta"); IS_ERR=$(sed -n 's/^IS_ERROR=//p' "$RAW.meta")
[ -n "$RUN_MODEL" ] || { echo "PROTOCOL ERROR: run did not report a model identity"; exit 1; }
[ "$IS_ERR" = "False" ] || { echo "PROTOCOL ERROR: the run reported is_error=$IS_ERR; raw kept at $RAW"; exit 1; }
CLI_VER=$(claude --version 2>/dev/null | head -1)

LAST=$(tail -n 1 "$RAW")
case "$LAST" in
  "Final verdict: APPROVE"|"Final verdict: APPROVE-WITH-CHANGES"|"Final verdict: REQUEST-CHANGES") VERDICT=${LAST#Final verdict: } ;;
  *) echo "PROTOCOL ERROR: last output line is not the sole exact verdict line: '$LAST'. Raw kept at $RAW"; exit 1 ;;
esac
NV=$(grep -cE '^Final verdict: (APPROVE-WITH-CHANGES|APPROVE|REQUEST-CHANGES)$' "$RAW" || true)
[ "$NV" -eq 1 ] || { echo "PROTOCOL ERROR: expected exactly one verdict line, found $NV. Raw kept at $RAW"; exit 1; }
# Target echo: the exact line(s) must appear as the first non-empty line(s), allowing at most two
# preamble lines (the compensating control is the exact echo, not its row number); the offset is recorded.
ECHO_OFF=$(grep -n -m1 '^TARGET: ' "$RAW" | cut -d: -f1); ECHO_OFF=${ECHO_OFF:-0}
[ "$ECHO_OFF" -ge 1 ] && [ "$ECHO_OFF" -le 3 ] || { echo "PROTOCOL ERROR: no TARGET echo within the first three lines. Raw kept at $RAW"; exit 1; }
if [ "$MODE" = diff ]; then
  [ "$(sed -n "${ECHO_OFF}p" "$RAW")" = "TARGET: ${BASE}..${HEAD_}" ] || { echo "PROTOCOL ERROR: TARGET line is not the exact target echo. Raw kept at $RAW"; exit 1; }
else
  NLINES=$(printf '%s' "$MANIFEST" | grep -c .)
  [ "$(sed -n "${ECHO_OFF},$((ECHO_OFF+NLINES-1))p" "$RAW")" = "$(printf '%s' "$MANIFEST" | grep .)" ] || { echo "PROTOCOL ERROR: TARGET lines do not equal the target manifest, in order. Raw kept at $RAW"; exit 1; }
fi
{
  echo "# Cross-model review - ${TARGET_DESC}"
  echo
  echo "**Reviewer:** claude CLI ${CLI_VER}; run-reported model: ${RUN_MODEL}; requested effort: ${EFFORT} (the CLI does not report the effective setting); fresh session ${SESSION}; sandbox: bubblewrap, filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)"
  echo "**Codex unavailable because:** ${CODEX_ERR}"
  echo "**Date:** ${DATE}"
  echo "**Target:** ${TARGET_DESC} (echo at raw line ${ECHO_OFF})"
  echo
  echo "---"
  echo
  cat "$RAW"
} >"$ART.tmp" && mv "$ART.tmp" "$ART"
rm -rf "$XR_TMP"
echo "VERDICT: $VERDICT $ART"
[ "$VERDICT" != "REQUEST-CHANGES" ] || exit 2
