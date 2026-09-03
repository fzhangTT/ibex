#!/usr/bin/env bash
# gen_tb_local.sh: local (no LSF) compile of gen_tb_top with the SIM_RECIPE Section 4 cocotb triple,
# and cocotb-master runs of one Python module with plusargs, for TB Infra unit tests and TDD
# transcripts. Runtime's flow (dv/auto_dv/flow) owns real regressions; this mirrors its flags.
#   bash -lc 'source ci/env.sh && bash dv/auto_dv/tb/gen_tb_local.sh compile <OUT>'
#   bash -lc 'source ci/env.sh && bash dv/auto_dv/tb/gen_tb_local.sh run <OUT> <name> <module> [plusargs...]'
# OUT must be a new directory inside the clone (an existing one is refused unless FORCE=1).
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT" || exit 1
MODE="${1:-}"; OUT="${2:-}"; shift 2 2>/dev/null
case "$OUT" in "$ROOT"/*) ;; *) echo "gen_tb_local.sh: OUT must be inside $ROOT (got '$OUT')" >&2; exit 2 ;; esac
SEED="${SEED:-1}"
sv_string() { sed -n "s/.*\bstring[[:space:]]\+$2[[:space:]]*=[[:space:]]*\"\([^\"]*\)\".*/\1/p" "$1" | head -1; }
case "$MODE" in
  compile)
    if [ -e "$OUT" ]; then
      if [ "${FORCE:-0}" = "1" ]; then rm -rf "$OUT"; else echo "gen_tb_local.sh: OUT exists ($OUT); set FORCE=1 to wipe" >&2; exit 2; fi
    fi
    mkdir -p "$OUT"
    CFG_OPTS="$(util/ibex_config.py opentitan vcs_opts)" || { echo "ibex_config.py failed" >&2; exit 1; }
    VPI_LIB="$(cocotb-config --lib-name-path vpi vcs)" || { echo "cocotb-config failed (venv?)" >&2; exit 1; }
    echo "config opts: $CFG_OPTS" > "$OUT/config_opts.txt"
    # shellcheck disable=SC2086
    vcs -full64 -sverilog \
        -f dv/auto_dv/tb/gen_rtl.f -f dv/auto_dv/tb/gen_tb.f \
        -top gen_tb_top \
        -ntb_opts uvm-1.2 +define+UVM +define+UVM_REGEX_NO_DPI +define+RVFI \
        $CFG_OPTS \
        -timescale=1ns/10ps -licqueue \
        -LDFLAGS '-Wl,--no-as-needed' -CFLAGS '--std=c99 -fno-extended-identifiers' \
        -Mdir="$OUT/vcs_simv.csrc" -o "$OUT/vcs_simv" \
        -debug_access+pp -xlrm uniq_prior_final -lca -kdb \
        +define+COCOTB_SIM +vpi -P dv/auto_dv/flow/gen_pli.tab -load "$VPI_LIB" \
        -l "$OUT/compile.log"
    rc=$?
    for f in ucli.key vc_hdrs.h; do [ -e "$ROOT/$f" ] && mv -f "$ROOT/$f" "$OUT/"; done
    echo "vcs exit: $rc" | tee -a "$OUT/compile.log"
    exit $rc ;;
  run)
    NAME="${1:?run name}"; MODULE="${2:?python module}"; shift 2
    [ -x "$OUT/vcs_simv" ] || { echo "gen_tb_local.sh: no simv in $OUT" >&2; exit 2; }
    dir="$OUT/$NAME"; mkdir -p "$dir"
    LIBPY="$(cocotb-config --libpython)" || exit 1
    ARG_BUILD_CONFIG="$(sv_string dv/auto_dv/tb/gen_tb_pkg.sv PLUSARG_BUILD_CONFIG)"
    ( cd "$dir" && env SIM_DIR="$dir" MODULE="$MODULE" PYTHONPATH="$ROOT" LIBPYTHON_LOC="$LIBPY" \
        RANDOM_SEED="$SEED" TOPLEVEL=gen_tb_top TOPLEVEL_LANG=verilog \
        "$OUT/vcs_simv" +vcs+lic+wait +ntb_random_seed="$SEED" +UVM_TESTNAME=gen_base_test \
        +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES "+$ARG_BUILD_CONFIG=opentitan" "$@" \
        -l "$dir/sim.log" > "$dir/stdout.log" 2>&1 )
    xs=$?
    fatal=$(grep -c "^Fatal:\|^UVM_FATAL [^:]*@\|GEN_ALIVE_TIMEOUT" "$dir/sim.log")
    uerr=$(grep -c "^UVM_ERROR [^:]*@" "$dir/sim.log")
    # cocotb prints its summary on stdout (TESTS=n PASS=p FAIL=f); look in both logs
    cpass=$(grep -h "TESTS=" "$dir/sim.log" "$dir/stdout.log" 2>/dev/null | grep -c "FAIL=0 ")
    cfail=$(grep -h "TESTS=" "$dir/sim.log" "$dir/stdout.log" 2>/dev/null | grep -c "FAIL=[1-9]")
    printf "%-24s module=%s plusargs=[%s] simv_exit=%s fatal_lines=%s uvm_errors=%s cocotb_pass=%s cocotb_fail=%s\n" \
      "$NAME" "$MODULE" "$*" "$xs" "$fatal" "$uerr" "$cpass" "$cfail" | tee -a "$OUT/runs_summary.txt"
    exit $xs ;;
  *) echo "usage: gen_tb_local.sh compile <OUT> | run <OUT> <name> <module> [plusargs...]" >&2; exit 2 ;;
esac
