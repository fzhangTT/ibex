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

# --- smoke.sh ---
out=$(./smoke.sh --dry-run 2>&1); st=$?
check_status "smoke: dry-run exits 0" 0 $st
check "smoke: default TEST" "TEST=riscv_arithmetic_basic_test,mcounteren_test" "$out"
check "smoke: default ITERATIONS" "ITERATIONS=1" "$out"
check "smoke: default SEED" "SEED=1" "$out"
check "smoke: vcs flow" "SIMULATOR=vcs" "$out"
out=$(./smoke.sh --dry-run --testlist /x/tl.yaml --directed-testlist /x/dt.yaml 2>&1)
check "smoke: suite knob riscv-dv" "RISCV-DV-TESTLIST=/x/tl.yaml" "$out"
check "smoke: suite knob directed" "DIRECTED-TESTLIST=/x/dt.yaml" "$out"
out=$(./smoke.sh --dry-run --lsf --jobs 8 --lsf-queue normal 2>&1)
check "smoke: lsf wraps bsub -K" "bsub -K" "$out"
check "smoke: lsf queue" "-q normal" "$out"
check "smoke: lsf single host" "span[hosts=1]" "$out"
case "$out" in *" --lsf"*) echo "FAIL: smoke: inner command still carries --lsf"; FAILURES=$((FAILURES+1));; *) echo "PASS: smoke: inner command drops --lsf";; esac
out=$(./smoke.sh --no-such-flag 2>&1); st=$?
check_status "smoke: unknown flag exits 2" 2 $st
out=$(./smoke.sh --dry-run --jobs banana 2>&1); st=$?
check_status "smoke: non-integer --jobs exits 2" 2 $st
out=$(./smoke.sh --dry-run --lsf --lsf-queue 'q; rm -rf /' 2>&1); st=$?
check_status "smoke: queue token validation exits 2" 2 $st
out=$(./smoke.sh --dry-run --config 'opentitan"; touch /tmp/pwned; echo "' 2>&1); st=$?
check_status "smoke: config injection attempt exits 2" 2 $st
out=$(./smoke.sh --dry-run --test 'a_test;b' 2>&1); st=$?
check_status "smoke: test-name metacharacter exits 2" 2 $st
out=$(./smoke.sh --dry-run --testlist '/tmp/has space.yaml' 2>&1); st=$?
check_status "smoke: whitespace testlist path exits 2" 2 $st
out=$(./smoke.sh --dry-run --jobs 0 2>&1); st=$?
check_status "smoke: --jobs 0 exits 2" 2 $st
out=$(./smoke.sh --dry-run --iterations 0 2>&1); st=$?
check_status "smoke: --iterations 0 exits 2" 2 $st
out=$(./smoke.sh --dry-run --test lh-misaligned,div-01 2>&1); st=$?
check_status "smoke: hyphenated test names accepted" 0 $st
check "smoke: hyphenated TEST passthrough" "TEST=lh-misaligned,div-01" "$out"
out=$(./smoke.sh --dry-run --out 'out_ci/x$(shell touch /tmp/pwned)' 2>&1); st=$?
check_status "smoke: make-function metacharacters in --out exit 2" 2 $st
out=$(./smoke.sh --dry-run --out 'out_ci/has space' 2>&1); st=$?
check_status "smoke: whitespace --out exits 2" 2 $st
out=$(./smoke.sh --dry-run --out 'out_ci/ws@2/smoke' 2>&1); st=$?
check_status "smoke: Jenkins @-suffix workspace path accepted" 0 $st
out=$(./smoke.sh --dry-run --testlist '/x/ws@2/tl.yaml' 2>&1); st=$?
check_status "smoke: @-suffix testlist path accepted" 0 $st
out=$(./smoke.sh --dry-run --cocotb-module dv.cocotb.gen_irq 2>&1); st=$?
check_status "smoke: --cocotb-module accepted" 0 $st
check "smoke: cocotb-module implies COCOTB=1" "COCOTB=1" "$out"
check "smoke: COCOTB_MODULE passthrough" "COCOTB_MODULE=dv.cocotb.gen_irq" "$out"
out=$(./smoke.sh --dry-run --cocotb-module 'bad;module' 2>&1); st=$?
check_status "smoke: cocotb-module metacharacters exit 2" 2 $st
out=$(CI_ENV_SH="$PWD/testdata/env_fail.sh" ./smoke.sh --out "$(mktemp -d)/o" 2>&1); st=$?
check_status "smoke: failing env.sh stops the run" 1 $st
check "smoke: env failure message" "environment setup failed" "$out"

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
