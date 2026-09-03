#!/usr/bin/env bash
# gen_run_fixture.sh <OUT build dir> <run name> <module> <vmem> [extra plusargs...]: one local fixture or test run against
# a gen_tb build (fixtures import from this directory); prints the decisive GEN_TEST_* lines
set -u
ROOT=/localdev/fzhang/ws/ibex-challenge
OUT=$1; NAME=$2; MODULE=$3; VMEM=$4; shift 4
dir=$OUT/$NAME; mkdir -p $dir
export PYTHONPATH=$ROOT
ARGS=$(python3 -c "from dv.auto_dv.gen_tb.gen_image import GenImage; print(' '.join(GenImage('$VMEM').plusargs()))")
LIBPY=$(cocotb-config --libpython)
( cd $dir && env SIM_DIR=$dir MODULE=$MODULE PYTHONPATH="$ROOT:$ROOT/dv/auto_dv/tests/gen_fixtures" LIBPYTHON_LOC=$LIBPY RANDOM_SEED=${SEED:-1} TOPLEVEL=gen_tb_top TOPLEVEL_LANG=verilog \
  $OUT/vcs_simv +vcs+lic+wait +ntb_random_seed=${SEED:-1} +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan $ARGS +gen_fetch_en_at_reset=0 "$@" -l $dir/sim.log > $dir/stdout.log 2>&1 )
echo "$NAME simv_exit=$?"
grep -h "GEN_TEST_SCHED\|GEN_TEST_PHASE\|GEN_TEST_EOT\|GEN_TEST_FIRE\|GEN_TEST_LAYERS\|GEN_TEST_PASS\|GEN_TEST_FAIL\|GEN_TEST_DRAIN\|GEN_TEST_BINS\|GEN_TEST_WITNESS\|AssertionError\|TESTS=\|UVM_ERROR :\|GEN_CMD_DISPATCH" $dir/stdout.log $dir/sim.log | sed 's/  */ /g' | sort -u | cut -c1-200
