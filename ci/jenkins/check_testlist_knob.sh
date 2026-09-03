#!/usr/bin/env bash
# Prove the testlist-override knob reaches metadata (no simulator needed).
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$REPO_ROOT/ci/env.sh" || { echo "ERROR: environment setup failed. Stop." >&2; exit 1; }
cd "$REPO_ROOT/dv/uvm/core_ibex"
PYTHONPATH=$(python3 -c 'from scripts.setup_imports import get_pythonpath; get_pythonpath()') \
python3 - <<'EOF'
# metadata.py is runtime-typechecked against pathlib3x, not stdlib pathlib.
import pathlib3x as pathlib
import sys, tempfile
sys.path.insert(0, 'scripts')
from metadata import RegressionMetadata
with tempfile.TemporaryDirectory() as td:
    td = pathlib.Path(td)
    md = RegressionMetadata.arg_list_initializer(
        dir_metadata=td/'metadata', dir_out=td, git_commit='selfcheck',
        args_list='SEED=1 RISCVDV_TESTLIST=/tmp/alt_testlist.yaml DIRECTED_TESTLIST=/tmp/alt_directed.yaml')
    assert str(md.ibex_riscvdv_testlist) == '/tmp/alt_testlist.yaml', md.ibex_riscvdv_testlist
    assert str(md.directed_test_data) == '/tmp/alt_directed.yaml', md.directed_test_data
    md2 = RegressionMetadata.arg_list_initializer(
        dir_metadata=td/'m2', dir_out=td, git_commit='selfcheck', args_list='SEED=1')
    assert md2.ibex_riscvdv_testlist.name == 'testlist.yaml', md2.ibex_riscvdv_testlist
    assert md2.directed_test_data.name == 'directed_testlist.yaml', md2.directed_test_data
print('check_testlist_knob: PASS')
EOF

# Unit check alone would pass even with no Makefile plumbing; prove the
# make -> --args-list hop too (no license; -n prints the recipe, doesn't run it).
recipe=$(make -C "$REPO_ROOT/dv/uvm/core_ibex" -n run \
           RISCV-DV-TESTLIST=/tmp/alt_testlist.yaml DIRECTED-TESTLIST=/tmp/alt_directed.yaml \
           TEST=all SEED=1 SIMULATOR=vcs 2>/dev/null)
case "$recipe" in
  *"RISCVDV_TESTLIST=/tmp/alt_testlist.yaml"*) : ;;
  *) echo "FAIL: Makefile does not pass RISCV-DV-TESTLIST into --args-list" >&2; exit 1;;
esac
case "$recipe" in
  *"DIRECTED_TESTLIST=/tmp/alt_directed.yaml"*) : ;;
  *) echo "FAIL: Makefile does not pass DIRECTED-TESTLIST into --args-list" >&2; exit 1;;
esac
echo "check_testlist_knob: make-boundary PASS"
