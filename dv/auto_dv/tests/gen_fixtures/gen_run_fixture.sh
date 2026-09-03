#!/usr/bin/env bash
# gen_run_fixture.sh <OUT build dir> <run name> <module> <vmem> [extra plusargs...]: one local fixture or test run against
# a gen_tb build (fixtures import from this directory); prints the decisive GEN_TEST_* lines; the run header names the build, the
# template and the test module by sha256 prefix
# GEN_TB_PYROOT (optional): a tree whose dv/auto_dv/gen_tb (rendered knobs, bridge) matches the build, searched before the
# clone; needed when the build is an export of HEAD and the clone's gen_tb is mid-edit (the export must not carry dv/auto_dv/tests).
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
OUT=$1; NAME=$2; MODULE=$3; VMEM=$4; shift 4
case "$VMEM" in /*) ;; *) echo "gen_run_fixture.sh: vmem path must be absolute (the run changes directory)" >&2; exit 2 ;; esac
dir=$OUT/$NAME; mkdir -p $dir
PYROOTS="${GEN_TB_PYROOT:+$GEN_TB_PYROOT:}$ROOT"
export PYTHONPATH=$PYROOTS
ARGS=$(python3 -c "from dv.auto_dv.gen_tb.gen_image import GenImage; print(' '.join(GenImage('$VMEM').plusargs()))")
LIBPY=$(cocotb-config --libpython)
# the shim has no baked rpath for spike: export the library dirs like gen_tb_local.sh run and the flow's runtime_lib_dirs
export LD_LIBRARY_PATH="$OUT/lib:$ROOT/tools/spike/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
# the build identity is the sources sha the compile step recorded (gen_tb_local.sh compile); a run header without one names an unknown build
SRC_SHA=$(sed -n 's/^sources sha256 ([^)]*): //p' $OUT/config_opts.txt 2>/dev/null | head -1)
# the template the run executes is the first PYROOTS entry that carries it (Python's resolution over the namespace package), else the clone's
TPL_SHA=$(IFS=:; for r in $PYROOTS; do [ -f "$r/dv/auto_dv/tests/gen_test_template.py" ] && { sha256sum "$r/dv/auto_dv/tests/gen_test_template.py" | cut -c1-16; break; }; done)
# the test module the run executes, resolved the same way (dotted name to a file under the first PYROOTS entry carrying it)
MODPATH=$(echo "$MODULE" | tr . /).py
TEST_SHA=$(IFS=:; for r in $PYROOTS $ROOT/dv/auto_dv/tests/gen_fixtures; do [ -f "$r/$MODPATH" ] && { sha256sum "$r/$MODPATH" | cut -c1-16; break; }; [ -f "$r/${MODPATH##*/}" ] && { sha256sum "$r/${MODPATH##*/}" | cut -c1-16; break; }; done)
echo "# run $NAME: $(date -u +%Y-%m-%dT%H:%M:%SZ) host=$(hostname) seed=${SEED:-1} module=$MODULE build=$OUT sources_sha=${SRC_SHA:-unknown} template_sha=${TPL_SHA:-unknown} test_sha=${TEST_SHA:-unknown} pyroot=${GEN_TB_PYROOT:-$ROOT} vmem=$VMEM plusargs=[$*]" > $dir/run_header.txt
( cd $dir && env SIM_DIR=$dir MODULE=$MODULE PYTHONPATH="$PYROOTS:$ROOT/dv/auto_dv/tests/gen_fixtures" LIBPYTHON_LOC=$LIBPY RANDOM_SEED=${SEED:-1} TOPLEVEL=gen_tb_top TOPLEVEL_LANG=verilog \
  $OUT/vcs_simv +vcs+lic+wait +ntb_random_seed=${SEED:-1} +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan $ARGS +gen_fetch_en_at_reset=0 "$@" -l $dir/sim.log > $dir/stdout.log 2>&1 )
echo "$NAME simv_exit=$?"
grep -h "GEN_TEST_SCHED\|GEN_TEST_PHASE\|GEN_TEST_EOT\|GEN_TEST_FIRE\|GEN_TEST_LAYERS\|GEN_TEST_PASS\|GEN_TEST_FAIL\|GEN_TEST_DRAIN\|GEN_TEST_BINS\|GEN_TEST_WITNESS\|AssertionError\|TESTS=\|UVM_ERROR :\|GEN_CMD_DISPATCH" $dir/stdout.log $dir/sim.log | sed 's/  */ /g' | sort -u | cut -c1-200
