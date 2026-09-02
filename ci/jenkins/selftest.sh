#!/usr/bin/env bash
# Self-test for ci/jenkins scripts. No simulator, no license, no LSF submission.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
FAILURES=0
check() { # <name> <needle> <haystack>
  if [[ "$3" == *"$2"* ]]; then echo "PASS: $1"; else
    echo "FAIL: $1 — expected to find [$2] in output:"; echo "$3" | sed 's/^/  | /'
    FAILURES=$((FAILURES + 1))
  fi
}
check_status() { # <name> <expected-exit> <actual-exit>
  if [[ "$3" -eq "$2" ]]; then echo "PASS: $1"; else
    echo "FAIL: $1 — expected exit $2, got $3"; FAILURES=$((FAILURES + 1))
  fi
}
T=$(mktemp -d)

# --- common.sh: ci_report_results against fixtures ---
mkdir -p "$T/pass/run" "$T/fail/run" "$T/empty/run"
cp testdata/regr_pass.log "$T/pass/run/regr.log"
cp testdata/regr_fail.log "$T/fail/run/regr.log"
( CI_JOB_NAME=selftest; source ./common.sh; ci_report_results "$T/pass" ); check_status "report: pass log exits 0" 0 $?
( CI_JOB_NAME=selftest; source ./common.sh; ci_report_results "$T/fail" ); check_status "report: fail log exits nonzero" 1 $?
( CI_JOB_NAME=selftest; source ./common.sh; ci_report_results "$T/empty" ); check_status "report: missing regr.log exits nonzero" 1 $?

# --- common.sh: ci_reserve_out ---
mkdir -p "$T/poisoned/run" "$T/owned"; echo foreign > "$T/owned/.ci-out-owner"
( CI_JOB_NAME=selftest; source ./common.sh; ci_reserve_out "$T/fresh" ); check_status "reserve: fresh dir ok" 0 $?
[ -f "$T/fresh/.ci-out-owner" ] && echo "PASS: reserve: sentinel created" || { echo "FAIL: reserve: no sentinel"; FAILURES=$((FAILURES+1)); }
( CI_JOB_NAME=selftest; source ./common.sh; ci_reserve_out "$T/poisoned" ); check_status "reserve: prior run/ rejected" 1 $?
( CI_JOB_NAME=selftest; source ./common.sh; unset CI_OWNER_TOKEN; ci_reserve_out "$T/owned" ); check_status "reserve: foreign sentinel rejected" 1 $?
echo tok123 > "$T/owned/.ci-out-owner"
( CI_JOB_NAME=selftest; source ./common.sh; CI_OWNER_TOKEN=tok123 ci_reserve_out "$T/owned" ); check_status "reserve: matching owner token accepted" 0 $?
( CI_JOB_NAME=selftest; source ./common.sh; CI_OWNER_TOKEN=other ci_reserve_out "$T/owned" ); check_status "reserve: mismatched owner token rejected" 1 $?

# --- LSF cancellation (mocked; proves the trap kills the exact submitted job) ---
# lsf-stub/bsub prints "Job <42> is submitted." then sleeps 60; lsf-stub/bkill logs its args
# to $LSF_STUB_LOG. smoke.sh exists from Task 3 on; guard so Task 1's run skips it cleanly.
if [ -x ./smoke.sh ]; then
  rm -f "$T/bkill.log"
  CI_ENV_SH="$PWD/testdata/env_ok.sh" LSF_STUB_LOG="$T/bkill.log" PATH="$PWD/testdata/lsf-stub:$PATH" \
    ./smoke.sh --lsf --out "$T/lsf-cancel" & SPID=$!
  sleep 3; kill -TERM "$SPID" 2>/dev/null; wait "$SPID" 2>/dev/null
  grep -q "42" "$T/bkill.log" 2>/dev/null && echo "PASS: lsf cancel bkills job 42" || { echo "FAIL: lsf cancel did not bkill job 42"; FAILURES=$((FAILURES+1)); }
else
  echo "SKIP: lsf cancel (smoke.sh not yet present)"
fi

rm -rf "$T"
echo; echo "selftest: $FAILURES failure(s)"
[[ "$FAILURES" -eq 0 ]]
