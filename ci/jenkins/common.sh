#!/usr/bin/env bash
# Shared helper for ci/jenkins/{smoke,nightly,coverage}.sh: option parsing, OUT
# reservation, the make invocation, LSF phase-1 wrapping, and regr.log verdicts.
# Sourced, not executed. See docs/dv/BUILD_AND_SIM.md and ci/jenkins/README.md.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CI_ENV_SH="${CI_ENV_SH:-$REPO_ROOT/ci/env.sh}"

# Validation charsets (Global Constraints): closed allow-lists, because every
# value is later interpolated into the Makefile's double-quoted --args-list
# recipe (a quote/semicolon breaks out; whitespace breaks shlex pair-splitting).
readonly CI_RE_TOKEN='^[A-Za-z0-9_-]+$'
readonly CI_RE_TEST='^[A-Za-z0-9_,-]+$'
readonly CI_RE_PATH='^[A-Za-z0-9_/.+@-]+$'
readonly CI_RE_COCOTB_MODULE='^[A-Za-z0-9_.]+$'
readonly CI_RE_INT_POS='^[1-9][0-9]*$'
readonly CI_RE_INT_NONNEG='^[0-9]+$'

ci_usage() {
  cat <<'EOF'
Usage: <script> [OPTIONS]

  --test LIST                Comma-separated test name(s)
  --testlist YAML             Absolute path to an alternate riscv-dv testlist.yaml (stock if omitted)
  --directed-testlist YAML    Absolute path to an alternate directed_testlist.yaml (stock if omitted)
  --iterations N               Positive integer iteration count
  --seed S                     Nonnegative integer seed
  --config NAME                ibex_configs.yaml config name (default: opentitan)
  --out DIR                    Output directory (default: out_ci/<job>-<UTC timestamp>)
  --jobs N                     Positive integer make -jN / LSF slot count (default: 4)
  --lsf                        Submit under bsub -K
  --lsf-queue Q                 LSF queue name (default: regress)
  --cocotb                     Run the cocotb overlay
  --cocotb-module MOD           cocotb Python test module; implies --cocotb
  --dry-run                    Print the command(s) and exit 0
  --help                        Print this message and exit 0
EOF
}

_ci_arg_err() { # <message>
  echo "ERROR: $1" >&2
  ci_usage >&2
  exit 2
}

_ci_check_path_value() { # <value> <option-name>
  case "$1" in
    /*) ;;
    *) _ci_arg_err "$2 needs an absolute path. Got '$1'." ;;
  esac
  [[ "$1" =~ $CI_RE_PATH ]] || _ci_arg_err "Invalid $2 value '$1'. Use only letters, digits, and _/.+@- characters. No whitespace."
}

ci_parse_args() {
  : "${CI_JOB_NAME:=ci}"
  : "${CI_CONFIG:=opentitan}"
  : "${CI_JOBS:=4}"
  : "${CI_LSF:=0}"
  : "${CI_LSF_QUEUE:=${LSF_QUEUE:-regress}}"
  : "${CI_COCOTB:=0}"
  : "${CI_COCOTB_MODULE:=}"
  : "${CI_COV:=0}"
  : "${CI_DRY_RUN:=0}"
  : "${CI_TEST:=}"
  : "${CI_TESTLIST:=}"
  : "${CI_DIRECTED_TESTLIST:=}"
  : "${CI_ITERATIONS:=}"
  : "${CI_SEED:=}"
  : "${CI_OUT:=out_ci/${CI_JOB_NAME}-$(date -u +%Y%m%d-%H%M%S)}"

  while [ $# -gt 0 ]; do
    case "$1" in
      --test)
        [ $# -ge 2 ] || _ci_arg_err "--test needs a value."
        [[ "$2" =~ $CI_RE_TEST ]] || _ci_arg_err "Invalid --test value '$2'. Use letters, digits, comma, underscore, hyphen only."
        CI_TEST="$2"; shift 2 ;;
      --testlist)
        [ $# -ge 2 ] || _ci_arg_err "--testlist needs a value."
        _ci_check_path_value "$2" "--testlist"
        CI_TESTLIST="$2"; shift 2 ;;
      --directed-testlist)
        [ $# -ge 2 ] || _ci_arg_err "--directed-testlist needs a value."
        _ci_check_path_value "$2" "--directed-testlist"
        CI_DIRECTED_TESTLIST="$2"; shift 2 ;;
      --iterations)
        [ $# -ge 2 ] || _ci_arg_err "--iterations needs a value."
        [[ "$2" =~ $CI_RE_INT_POS ]] || _ci_arg_err "Invalid --iterations value '$2'. Use a positive integer."
        CI_ITERATIONS="$2"; shift 2 ;;
      --seed)
        [ $# -ge 2 ] || _ci_arg_err "--seed needs a value."
        [[ "$2" =~ $CI_RE_INT_NONNEG ]] || _ci_arg_err "Invalid --seed value '$2'. Use a nonnegative integer."
        CI_SEED="$2"; shift 2 ;;
      --config)
        [ $# -ge 2 ] || _ci_arg_err "--config needs a value."
        [[ "$2" =~ $CI_RE_TOKEN ]] || _ci_arg_err "Invalid --config value '$2'. Use letters, digits, underscore, hyphen only."
        CI_CONFIG="$2"; shift 2 ;;
      --out)
        [ $# -ge 2 ] || _ci_arg_err "--out needs a value."
        CI_OUT="$2"; shift 2 ;;
      --jobs)
        [ $# -ge 2 ] || _ci_arg_err "--jobs needs a value."
        [[ "$2" =~ $CI_RE_INT_POS ]] || _ci_arg_err "Invalid --jobs value '$2'. Use a positive integer."
        CI_JOBS="$2"; shift 2 ;;
      --lsf)
        CI_LSF=1; shift ;;
      --lsf-queue)
        [ $# -ge 2 ] || _ci_arg_err "--lsf-queue needs a value."
        [[ "$2" =~ $CI_RE_TOKEN ]] || _ci_arg_err "Invalid --lsf-queue value '$2'. Use letters, digits, underscore, hyphen only."
        CI_LSF_QUEUE="$2"; shift 2 ;;
      --cocotb)
        CI_COCOTB=1; shift ;;
      --cocotb-module)
        [ $# -ge 2 ] || _ci_arg_err "--cocotb-module needs a value."
        [[ "$2" =~ $CI_RE_COCOTB_MODULE ]] || _ci_arg_err "Invalid --cocotb-module value '$2'. Use letters, digits, underscore, dot only."
        CI_COCOTB_MODULE="$2"; CI_COCOTB=1; shift 2 ;;
      --dry-run)
        CI_DRY_RUN=1; shift ;;
      --help)
        ci_usage; exit 0 ;;
      --)
        shift; break ;;
      *)
        _ci_arg_err "Unknown option: $1." ;;
    esac
  done
}

ci_reserve_out() { # <out_abs_dir>
  local out_abs="$1"
  local offender=""
  for d in run build metadata; do
    [ -e "$out_abs/$d" ] && { offender="$d"; break; }
  done
  if [ -n "$offender" ]; then
    echo "ERROR: $out_abs already contains $offender/ from a prior run. Use a fresh --out." >&2
    return 1
  fi

  mkdir -p "$out_abs" || { echo "ERROR: cannot create $out_abs." >&2; return 1; }

  local sentinel="$out_abs/.ci-out-owner"
  if ( set -o noclobber; : >"$sentinel" ) 2>/dev/null; then
    CI_OWNER_TOKEN="$(od -An -N8 -tx8 </dev/urandom | tr -d ' ')"
    printf '%s\n' "$CI_OWNER_TOKEN" >"$sentinel"
    export CI_OWNER_TOKEN
    return 0
  fi

  # Sentinel already exists: only the job that created it may reuse the dir
  # (the LSF inner invocation, which inherits CI_OWNER_TOKEN from the outer one).
  local existing
  existing="$(cat "$sentinel" 2>/dev/null)"
  if [ -n "${CI_OWNER_TOKEN:-}" ] && [ "${CI_OWNER_TOKEN:-}" = "$existing" ]; then
    return 0
  fi
  echo "ERROR: $out_abs is owned by another running job. Use a fresh --out." >&2
  return 1
}

ci_report_results() { # <out_abs_dir>
  local out_abs="$1"
  local log="$out_abs/run/regr.log"
  if [ -f "$log" ]; then
    local line
    line="$(head -n1 "$log")"
    if [[ "$line" =~ %\ PASS\ ([0-9]+)\ PASSED,\ ([0-9]+)\ FAILED ]]; then
      local failed="${BASH_REMATCH[2]}"
      echo "$line"
      if [ "$failed" -ne 0 ]; then
        sed -n '/# Details of failing tests/,/# Details of passing tests/p' "$log"
        return 1
      fi
      return 0
    fi
  fi
  echo "ERROR: no regr.log at $log. The run did not produce results." >&2
  return 1
}

_ci_print_cmd() { # print an argv array as one shell-quoted command line
  # Only %q-quote a token that actually needs it (whitespace/quotes/shell
  # metacharacters); every value here already passed a no-whitespace
  # validation charset, so comma/bracket-bearing values (test lists,
  # "span[hosts=1]") are the common case and read better unescaped.
  local out="" tok qtok
  for tok in "$@"; do
    case "$tok" in
      *' '*|*$'\t'*|*$'\n'*|*"'"*|*'"'*|*'\'*|*'$'*|*'`'*|*';'*|*'&'*|*'|'*|*'('*|*')'*|*'<'*|*'>'*|*'!'*|*'*'*|*'?'*)
        printf -v qtok '%q' "$tok" ;;
      *)
        qtok="$tok" ;;
    esac
    out+="$qtok "
  done
  echo "${out% }"
}

_ci_lsf_cancel() {
  trap - INT TERM
  [ -n "${child:-}" ] && kill "$child" 2>/dev/null
  local id="${jid:-}"
  if [ -z "$id" ] && [ -n "${CI_LSF_BSUB_LOG:-}" ] && [ -f "$CI_LSF_BSUB_LOG" ]; then
    id="$(sed -n 's/.*Job <\([0-9]\+\)> is submitted.*/\1/p' "$CI_LSF_BSUB_LOG" | head -n1)"
  fi
  [ -n "$id" ] && bkill "$id" 2>/dev/null
  exit 143
}

ci_lsf_run() { # <out_abs_dir> <bsub argv...>
  local out_abs="$1"; shift
  local -a bsub_cmd=("$@")
  CI_LSF_BSUB_LOG="$out_abs/bsub.log"

  # jid/child must exist before the trap is armed (set -u hazard): a signal
  # between arming and the bsub launch must not crash the handler mid-cancel.
  jid=""
  child=""
  trap _ci_lsf_cancel INT TERM

  # Process substitution (not a literal pipe) keeps bsub itself as the
  # backgrounded process, so $! is bsub's own pid, not tee's.
  "${bsub_cmd[@]}" > >(tee "$CI_LSF_BSUB_LOG") 2>&1 &
  child=$!

  local deadline=$((SECONDS + 120))
  while [ -z "$jid" ]; do
    jid="$(sed -n 's/.*Job <\([0-9]\+\)> is submitted.*/\1/p' "$CI_LSF_BSUB_LOG" 2>/dev/null | head -n1)"
    [ -n "$jid" ] && break
    if ! kill -0 "$child" 2>/dev/null; then
      break
    fi
    if [ "$SECONDS" -ge "$deadline" ]; then
      kill "$child" 2>/dev/null
      jid="$(sed -n 's/.*Job <\([0-9]\+\)> is submitted.*/\1/p' "$CI_LSF_BSUB_LOG" 2>/dev/null | head -n1)"
      [ -n "$jid" ] && bkill "$jid" 2>/dev/null
      echo "ERROR: bsub did not report a job id within 120s ($CI_LSF_BSUB_LOG)." >&2
      trap - INT TERM
      return 1
    fi
    sleep 1
  done

  if [ -z "$jid" ]; then
    echo "ERROR: bsub exited without reporting a job id ($CI_LSF_BSUB_LOG)." >&2
    trap - INT TERM
    wait "$child" 2>/dev/null
    return 1
  fi

  wait "$child"
  local status=$?
  trap - INT TERM
  return "$status"
}

ci_main() {
  ci_parse_args "$@"

  # Resolve CI_OUT to an absolute path: pure path math, no env sourcing, so
  # dry-run can print before ci_env_sh is ever touched.
  case "$CI_OUT" in
    /*) CI_OUT_ABS="$CI_OUT" ;;
    *) CI_OUT_ABS="$REPO_ROOT/dv/uvm/core_ibex/$CI_OUT" ;;
  esac
  if [[ ! "$CI_OUT_ABS" =~ $CI_RE_PATH ]]; then
    echo "ERROR: Invalid --out value. Resolved path '$CI_OUT_ABS' must use only letters, digits, and _/.+@- characters. No whitespace." >&2
    ci_usage >&2
    exit 2
  fi

  local -a make_cmd=(
    make -C "$REPO_ROOT/dv/uvm/core_ibex" "-j$CI_JOBS" SIMULATOR=vcs ISS=spike
    "IBEX_CONFIG=$CI_CONFIG" "TEST=$CI_TEST" "SEED=$CI_SEED" "OUT=$CI_OUT_ABS"
  )
  [ -n "${CI_ITERATIONS:-}" ] && make_cmd+=("ITERATIONS=$CI_ITERATIONS")
  [ "$CI_COV" = "1" ] && make_cmd+=("COV=1")
  [ "$CI_COCOTB" = "1" ] && make_cmd+=("COCOTB=1")
  [ -n "${CI_COCOTB_MODULE:-}" ] && make_cmd+=("COCOTB_MODULE=$CI_COCOTB_MODULE")
  [ -n "${CI_TESTLIST:-}" ] && make_cmd+=("RISCV-DV-TESTLIST=$CI_TESTLIST")
  [ -n "${CI_DIRECTED_TESTLIST:-}" ] && make_cmd+=("DIRECTED-TESTLIST=$CI_DIRECTED_TESTLIST")

  local -a bsub_cmd=()
  if [ "$CI_LSF" = "1" ]; then
    # Re-invoke the calling script with all values resolved to explicit flags
    # and --lsf dropped, so the inner invocation is deterministic.
    local self_abs
    self_abs="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
    local -a inner_cmd=("$self_abs" --test "$CI_TEST" --seed "$CI_SEED" --config "$CI_CONFIG" \
                         --out "$CI_OUT_ABS" --jobs "$CI_JOBS")
    [ -n "${CI_ITERATIONS:-}" ] && inner_cmd+=(--iterations "$CI_ITERATIONS")
    [ -n "${CI_TESTLIST:-}" ] && inner_cmd+=(--testlist "$CI_TESTLIST")
    [ -n "${CI_DIRECTED_TESTLIST:-}" ] && inner_cmd+=(--directed-testlist "$CI_DIRECTED_TESTLIST")
    if [ -n "${CI_COCOTB_MODULE:-}" ]; then
      inner_cmd+=(--cocotb-module "$CI_COCOTB_MODULE")
    elif [ "$CI_COCOTB" = "1" ]; then
      inner_cmd+=(--cocotb)
    fi
    bsub_cmd=(bsub -K -J "ibex-${CI_JOB_NAME}" -q "$CI_LSF_QUEUE" -n "$CI_JOBS" \
              -R "span[hosts=1]" -o "$CI_OUT_ABS/lsf.log" "${inner_cmd[@]}")
  fi

  if [ "$CI_DRY_RUN" = "1" ]; then
    if [ "$CI_LSF" = "1" ]; then
      _ci_print_cmd "${bsub_cmd[@]}"
    else
      _ci_print_cmd "${make_cmd[@]}"
    fi
    return 0
  fi

  source "$CI_ENV_SH" || { echo "ERROR: environment setup failed ($CI_ENV_SH). Stop." >&2; return 1; }

  ci_reserve_out "$CI_OUT_ABS" || return 1

  if [ -n "${CI_TESTLIST:-}" ] && [ ! -f "$CI_TESTLIST" ]; then
    echo "ERROR: testlist not found: $CI_TESTLIST. Provide an existing --testlist path." >&2
    return 1
  fi
  if [ -n "${CI_DIRECTED_TESTLIST:-}" ] && [ ! -f "$CI_DIRECTED_TESTLIST" ]; then
    echo "ERROR: directed testlist not found: $CI_DIRECTED_TESTLIST. Provide an existing --directed-testlist path." >&2
    return 1
  fi

  local make_status
  if [ "$CI_LSF" = "1" ]; then
    ci_lsf_run "$CI_OUT_ABS" "${bsub_cmd[@]}"
    make_status=$?
  else
    "${make_cmd[@]}"
    make_status=$?
  fi

  local report_status
  ci_report_results "$CI_OUT_ABS"
  report_status=$?

  [ "$make_status" -eq 0 ] && [ "$report_status" -eq 0 ]
}
