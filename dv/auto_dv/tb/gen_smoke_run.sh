#!/usr/bin/env bash
# gen_smoke_run.sh: compile gen_smoke_tb_top (gen_dut_top under the opentitan config) and run the
# proof sequence GREEN, RED (no retirement), RED (integrity flip), GREEN, each into its own saved
# directory with its own log and exit status, so the red-run evidence is reproducible from one
# command (dv/auto_dv/evidence/gen_t029_smoke_red_runs.md). Flag set: docs/dv/SIM_RECIPE.md
# Sections 2 and 5. Local only (no LSF). Run from a login shell:
#   bash -lc 'source ci/env.sh && OUT=<dir> bash dv/auto_dv/tb/gen_smoke_run.sh'
# vcs runs from the clone root (gen_rtl.f is root-relative); every simv runs inside its run dir so
# simulator droppings stay out of the tree; compile droppings are swept into $OUT.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT" || exit 1
OUT="${OUT:-$ROOT/dv/auto_dv/work/tb-infra/out_smoke}"
SEED="${SEED:-1}"
CYCLES="${CYCLES:-3000}"
FLIP_BIT="${FLIP_BIT:-5}"
rm -rf "$OUT"; mkdir -p "$OUT"
SUMMARY="$OUT/runs_summary.txt"
: > "$SUMMARY"

CFG_OPTS="$(util/ibex_config.py opentitan vcs_opts)" || { echo "ibex_config.py failed"; exit 1; }
echo "config opts: $CFG_OPTS" | tee "$OUT/config_opts.txt"

# shellcheck disable=SC2086
vcs -full64 -sverilog \
    -f dv/auto_dv/tb/gen_rtl.f -f dv/auto_dv/tb/gen_smoke_tb.f \
    -top gen_smoke_tb_top \
    -ntb_opts uvm-1.2 +define+UVM +define+UVM_REGEX_NO_DPI +define+RVFI \
    $CFG_OPTS \
    -timescale=1ns/10ps \
    -licqueue \
    -LDFLAGS '-Wl,--no-as-needed' \
    -CFLAGS '--std=c99 -fno-extended-identifiers' \
    -Mdir="$OUT/vcs_simv.csrc" -o "$OUT/vcs_simv" \
    -debug_access+pp -xlrm uniq_prior_final -lca -kdb \
    -l "$OUT/compile.log"
rc=$?
echo "vcs exit: $rc" | tee -a "$OUT/compile.log"
for f in ucli.key vc_hdrs.h; do [ -e "$ROOT/$f" ] && mv -f "$ROOT/$f" "$OUT/"; done
[ $rc -eq 0 ] || { echo "compile FAILED rc=$rc" | tee -a "$SUMMARY"; exit $rc; }

# run NAME EXPECT extra-plusargs...   (EXPECT = PASS or FAIL: the token the run must print)
run() {
  local name="$1" expect="$2"; shift 2
  local dir="$OUT/$name"; mkdir -p "$dir"
  ( cd "$dir" && env SIM_DIR="$dir" "$OUT/vcs_simv" +vcs+lic+wait +ntb_random_seed="$SEED" \
      +UVM_TESTNAME=none +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan \
      "$@" -l "$dir/sim.log" > "$dir/stdout.log" 2>&1 )
  local xs=$?
  local tok="NONE"
  grep -q "GEN_SMOKE_PASS" "$dir/sim.log" && tok="PASS"
  grep -q "GEN_SMOKE_FAIL" "$dir/sim.log" && tok="FAIL"
  local fatal=$(grep -c "^Fatal:" "$dir/sim.log")
  local verdict="MISMATCH"; [ "$tok" = "$expect" ] && verdict="as-expected"
  printf "%-22s plusargs=[%s] simv_exit=%s token=%s fatal_lines=%s expected=%s -> %s\n" \
    "$name" "$*" "$xs" "$tok" "$fatal" "$expect" "$verdict" | tee -a "$SUMMARY"
  [ "$verdict" = "as-expected" ]
}
ok=0
run run_01_green         PASS +gen_smoke_cycles="$CYCLES"                               || ok=1
run run_02_red_noretire  FAIL +gen_smoke_cycles=1                                       || ok=1
run run_03_red_intg      FAIL +gen_smoke_cycles="$CYCLES" +gen_smoke_intg_flip="$FLIP_BIT" || ok=1
run run_04_green         PASS +gen_smoke_cycles="$CYCLES"                               || ok=1
echo "sequence result: $([ $ok -eq 0 ] && echo ALL-AS-EXPECTED || echo MISMATCH)" | tee -a "$SUMMARY"
exit $ok
