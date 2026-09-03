#!/usr/bin/env bash
# ci/cleanroom-selftest.sh [--pre-overlay]
#
# License-free. Builds cleanroom exports into temp dirs with ci/make-cleanroom.sh and
# proves the checks it performs actually catch what they claim to, plus
# ci/check-landing.sh's accept/reject behavior. See docs/dv/process-logs/ws7/progress.md
# for what --pre-overlay does and does not prove (Task 2, the Zone A overlay, is not
# landed yet).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"

PRE_OVERLAY=0
[ "${1:-}" = "--pre-overlay" ] && PRE_OVERLAY=1

# Reuse make-cleanroom.sh's DENY/ALLOW arrays and cleanroom_* check functions (sourcing
# does not run its main). It sets -euo pipefail internally for its own build/verify
# logic; reassert our own looser options for the selftest's own flow, which expects
# and handles nonzero exits explicitly rather than aborting on them.
source "$REPO_ROOT/ci/make-cleanroom.sh"
set +e
set -uo pipefail

FAILURES=0
pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; FAILURES=$((FAILURES + 1)); }
check_status() { # <name> <expected-exit> <actual-exit>
  if [ "$3" -eq "$2" ]; then pass "$1"; else fail "$1 (expected exit $2, got $3)"; fi
}
check_fn() { # <name> <fn> <arg...>
  local name="$1"; shift
  local out
  if out="$("$@" 2>&1)"; then
    pass "$name"
  else
    fail "$name"
    echo "$out" | sed 's/^/  /'
  fi
}

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

run_build() { # <dest> [canary-mode]
  local dest="$1" canary="${2:-}"
  if [ "$PRE_OVERLAY" = "1" ]; then
    CLEANROOM_PRE_OVERLAY=1 CLEANROOM_CANARY="$canary" "$REPO_ROOT/ci/make-cleanroom.sh" "$dest"
  else
    CLEANROOM_CANARY="$canary" "$REPO_ROOT/ci/make-cleanroom.sh" "$dest"
  fi
}

echo "########## export build + checks (pre-overlay=$PRE_OVERLAY) ##########"

echo "== (a) plain export build =="
DEST="$T/export"
run_build "$DEST" >"$T/build.log" 2>&1
build_rc=$?
cat "$T/build.log"
check_status "(a) export build exits 0" 0 "$build_rc"

if [ "$build_rc" -eq 0 ]; then
  check_fn "(b) deny-list / default-deny absence" cleanroom_check_deny_absence "$DEST"
  check_fn "ci/reviews/ is exactly the six-file Zone A set" cleanroom_check_reviews_set "$DEST"
  check_fn "(c) artifact absence" cleanroom_check_artifact_absence "$DEST"
  check_fn "inventory tripwire" cleanroom_check_inventory "$DEST"

  if [ "$PRE_OVERLAY" != "1" ]; then
    check_fn "(d1) item-9 scan" cleanroom_check_item9_scan "$DEST"
    check_fn "(d2) whole-export identifier scan" cleanroom_check_whole_export_identifiers "$DEST"
    check_fn "(e) no remote mcp" cleanroom_check_no_remote_mcp "$DEST"
    check_fn "(h) exported validator" cleanroom_check_validator "$DEST"
  else
    echo "SKIP: (d1)/(d2)/(e)/(h) -- --pre-overlay mode (Task 2 overlay not landed; these checks are only meaningful once it has)"
  fi
else
  fail "(b)/(c)/inventory/(d1)/(d2)/(e)/(h) -- build did not succeed, nothing to re-verify"
fi

echo
echo "== (f) planted canaries (anti-vacuity: CLEANROOM_CANARY=deny|artifact|mcp|identifier) =="
# Each canary must be caught by its OWN named check, not merely produce some nonzero
# exit -- a canary caught by the wrong check (or failing for an unrelated reason, e.g.
# a network hiccup in the riscv-dv fetch) must fail this selftest, not pass vacuously.
canary_expect() {
  case "$1" in
    deny) echo "dv/ has content beyond the dv/auto_dv/ allowlist" ;;
    artifact) echo "run artifact present in export" ;;
    mcp) echo "remote (http/url) MCP server entry" ;;
    identifier) echo "fenced identifier 'riscv_arithmetic_basic_test' present in export" ;;
  esac
}
for c in deny artifact mcp identifier; do
  if [ "$PRE_OVERLAY" = "1" ] && { [ "$c" = "mcp" ] || [ "$c" = "identifier" ]; }; then
    echo "SKIP: (f) canary=$c -- its check ((e) or (d2)) is itself skipped pre-overlay, so this canary has nothing to catch it"
    continue
  fi
  expect="$(canary_expect "$c")"
  CDEST="$T/export-canary-$c"
  run_build "$CDEST" "$c" >"$T/canary-$c.log" 2>&1
  crc=$?
  cat "$T/canary-$c.log"
  if [ "$crc" -eq 0 ]; then
    fail "(f) canary=$c build unexpectedly exited 0"
  elif grep -qF "$expect" "$T/canary-$c.log"; then
    pass "(f) canary=$c build fails as expected, caught by its own check ('$expect')"
  else
    fail "(f) canary=$c build failed, but NOT with its expected check ('$expect' not found -- wrong check may have caught it, or it failed for an unrelated reason)"
  fi
done

echo
echo "########## (g) landing check ##########"
LR="$T/landing-repo"
mkdir -p "$LR/dv/auto_dv"
(
  cd "$LR" && git init -q && git checkout -q -b main
  echo "seed" > dv/auto_dv/.gitignore
  git add -A && git -c user.email=t@t -c user.name=t commit -q -m base
)
BASE_SHA="$(git -C "$LR" rev-parse HEAD)"

( cd "$LR" && echo "module gen_foo; endmodule" > dv/auto_dv/gen_foo.sv && git add -A && git -c user.email=t@t -c user.name=t commit -q -m accept )
ACCEPT_SHA="$(git -C "$LR" rev-parse HEAD)"
( cd "$LR" && "$REPO_ROOT/ci/check-landing.sh" "$BASE_SHA" "$ACCEPT_SHA" ) >"$T/g-accept.log" 2>&1
check_status "(g) accepts synthetic dv/auto_dv/gen_foo.sv" 0 "$?"
cat "$T/g-accept.log"

git -C "$LR" reset -q --hard "$BASE_SHA"
( cd "$LR" && mkdir -p dv/uvm && echo x > dv/uvm/leak.sv && git add -A && git -c user.email=t@t -c user.name=t commit -q -m "reject: outside namespace" )
OUTSIDE_SHA="$(git -C "$LR" rev-parse HEAD)"
( cd "$LR" && "$REPO_ROOT/ci/check-landing.sh" "$BASE_SHA" "$OUTSIDE_SHA" ) >"$T/g-outside.log" 2>&1
check_status "(g)(i) rejects change outside dv/auto_dv/" 1 "$?"
cat "$T/g-outside.log"

git -C "$LR" reset -q --hard "$BASE_SHA"
( cd "$LR" && echo "module x; endmodule" > dv/auto_dv/nogen.sv && git add -A && git -c user.email=t@t -c user.name=t commit -q -m "reject: no gen_ prefix" )
NOGEN_SHA="$(git -C "$LR" rev-parse HEAD)"
( cd "$LR" && "$REPO_ROOT/ci/check-landing.sh" "$BASE_SHA" "$NOGEN_SHA" ) >"$T/g-nogen.log" 2>&1
check_status "(g)(ii) rejects dv/auto_dv/ file without gen_" 1 "$?"
cat "$T/g-nogen.log"

git -C "$LR" reset -q --hard "$BASE_SHA"
( cd "$LR" && ln -s /etc/passwd dv/auto_dv/gen_link.sv && git add -A && git -c user.email=t@t -c user.name=t commit -q -m "reject: symlink" )
SYMLINK_SHA="$(git -C "$LR" rev-parse HEAD)"
( cd "$LR" && "$REPO_ROOT/ci/check-landing.sh" "$BASE_SHA" "$SYMLINK_SHA" ) >"$T/g-symlink.log" 2>&1
check_status "(g)(iii) rejects symlink" 1 "$?"
cat "$T/g-symlink.log"

echo
echo "selftest: $FAILURES failure(s)"
[ "$FAILURES" -eq 0 ] && exit 0 || exit 1
