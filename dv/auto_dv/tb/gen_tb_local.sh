#!/usr/bin/env bash
# gen_tb_local.sh: local (no LSF) compile of gen_tb_top with the SIM_RECIPE Section 4 cocotb triple,
# and cocotb-master runs of one Python module with plusargs, for TB Infra unit tests and TDD
# transcripts. Runtime's flow (dv/auto_dv/flow) owns real regressions; the VCS flag groups are read from
# its constants home (gen_flow_const.py) so the two compiles cannot drift, and each run's verdict comes
# from its verdict tool (gen_verdict.py), never from a grep of this script's own.
#   bash -lc 'source ci/env.sh && bash dv/auto_dv/tb/gen_tb_local.sh compile <OUT>'
#   bash -lc 'source ci/env.sh && bash dv/auto_dv/tb/gen_tb_local.sh run <OUT> <name> <module> [plusargs...]'
# OUT must be a new directory inside the clone (an existing one is refused unless FORCE=1).
# PASS_MARKER=<token> names the end-of-test marker the verdict expects (default: derived from <module>).
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT" || exit 1
MODE="${1:-}"; OUT="${2:-}"; shift 2 2>/dev/null
case "$OUT" in "$ROOT"/*) ;; *) echo "gen_tb_local.sh: OUT must be inside $ROOT (got '$OUT')" >&2; exit 2 ;; esac
SEED="${SEED:-1}"
FLOW=dv/auto_dv/flow
sv_string() { sed -n "s/.*\bstring[[:space:]]\+$2[[:space:]]*=[[:space:]]*\"\([^\"]*\)\".*/\1/p" "$1" | head -1; }
# VCS flag groups from Runtime's constants home, NUL-separated so a flag value with spaces survives
flow_flags() { python3 -c "
import sys; sys.path.insert(0, '$FLOW'); import gen_flow_const as C
sys.stdout.write('\0'.join(C.VCS_BASE_FLAGS + C.VCS_UVM_FLAGS + C.VCS_COMMON_FLAGS + C.VCS_DEBUG_PP_FLAGS + [C.COCOTB_DEFINE]))"; }
case "$MODE" in
  compile)
    if [ -e "$OUT" ]; then
      if [ "${FORCE:-0}" = "1" ]; then rm -rf "$OUT"; else echo "gen_tb_local.sh: OUT exists ($OUT); set FORCE=1 to wipe" >&2; exit 2; fi
    fi
    mkdir -p "$OUT"
    CFG_OPTS="$(util/ibex_config.py opentitan vcs_opts)" || { echo "ibex_config.py failed" >&2; exit 1; }
    VPI_LIB="$(cocotb-config --lib-name-path vpi vcs)" || { echo "cocotb-config failed (venv?)" >&2; exit 1; }
    mapfile -d '' VCS_FLAGS < <(flow_flags) || { echo "gen_flow_const.py flag read failed" >&2; exit 1; }
    [ "${#VCS_FLAGS[@]}" -gt 0 ] || { echo "gen_flow_const.py returned no flags" >&2; exit 1; }
    echo "config opts: $CFG_OPTS" > "$OUT/config_opts.txt"
    printf 'flow flags:'; printf ' %q' "${VCS_FLAGS[@]}"; echo
    { printf 'flow flags:'; printf ' %q' "${VCS_FLAGS[@]}"; echo; } >> "$OUT/config_opts.txt"
    # the ISA shim shared library (Spike behind DPI) goes next to the simv; VCS links it via -LDFLAGS. The shim
    # carries no rpath, so the simv link resolves its spike dependency through -rpath-link (link time only).
    bash dv/auto_dv/isa/gen_isa_shim_build.sh lib "$OUT/lib" || { echo "shim build failed" >&2; exit 1; }
    # shellcheck disable=SC2086
    vcs "${VCS_FLAGS[@]}" \
        -f dv/auto_dv/tb/gen_rtl.f -f dv/auto_dv/tb/gen_tb.f \
        -top gen_tb_top \
        +define+RVFI \
        $CFG_OPTS \
        -LDFLAGS "-Wl,--no-as-needed -L$OUT/lib -lgen_isa_shim -Wl,-rpath,$OUT/lib -Wl,-rpath-link,$ROOT/tools/spike/lib" \
        -Mdir="$OUT/vcs_simv.csrc" -o "$OUT/vcs_simv" \
        +vpi -P "$FLOW/gen_pli.tab" -load "$VPI_LIB" \
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
    # the shim has no baked rpath for spike: the run exports the library dirs like the flow's runtime_lib_dirs
    export LD_LIBRARY_PATH="$OUT/lib:$ROOT/tools/spike/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
    echo "# run $NAME: $(date -u +%Y-%m-%dT%H:%M:%SZ) host=$(hostname) seed=$SEED module=$MODULE plusargs=[$*]" > "$dir/run_header.txt"
    ( cd "$dir" && env SIM_DIR="$dir" MODULE="$MODULE" PYTHONPATH="$ROOT" LIBPYTHON_LOC="$LIBPY" \
        RANDOM_SEED="$SEED" TOPLEVEL=gen_tb_top TOPLEVEL_LANG=verilog \
        "$OUT/vcs_simv" +vcs+lic+wait +ntb_random_seed="$SEED" +UVM_TESTNAME=gen_base_test \
        +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES "+$ARG_BUILD_CONFIG=opentitan" "$@" \
        -l "$dir/sim.log" > "$dir/stdout.log" 2>&1 )
    xs=$?
    # the flow's verdict (gen_verdict.decide: sim.log plus the stdout capture that carries cocotb's summary,
    # and the simv exit code, exactly as gen_run.py judges a regression run)
    marker="${PASS_MARKER:-$(echo "${MODULE##*.}" | tr '[:lower:]' '[:upper:]')_PASS}"
    python3 - "$dir" "$marker" "$xs" > "$dir/verdict.txt" 2>&1 <<PY
import sys; sys.path.insert(0, "$FLOW")
from pathlib import Path
import gen_verdict as V, gen_flow_const as C
d, marker, rc = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3])
r = V.decide(d / "sim.log", marker, False, rc=rc, extra_logs=[d / "stdout.log"], build_config=C.BUILD_CONFIG)
for k in ("verdict", "reason", "evidence", "uvm_counts", "cocotb_summary", "marker_seen", "banner_seen", "exit_code"):
    print(f"{k}: {r.get(k)}")
PY
    verdict="$(grep -E '^(verdict|reason):' "$dir/verdict.txt" | tr '\n' ' ')"
    uerr=$(grep -c "^UVM_ERROR [^:]*@" "$dir/sim.log")
    printf "%-24s module=%s plusargs=[%s] simv_exit=%s uvm_errors=%s verdict: %s\n" \
      "$NAME" "$MODULE" "$*" "$xs" "$uerr" "$verdict" | tee -a "$OUT/runs_summary.txt"
    exit $xs ;;
  *) echo "usage: gen_tb_local.sh compile <OUT> | run <OUT> <name> <module> [plusargs...]" >&2; exit 2 ;;
esac
