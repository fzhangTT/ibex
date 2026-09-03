#!/usr/bin/env bash
# gen_isa_shim_build.sh: build the ISA shim as a shared library for VCS (-LDFLAGS "-L<out> -lgen_isa_shim
# -Wl,-rpath,<out>") and, with `test`, the C++ unit test. Spike headers/libs from tools/spike (only
# <prefix>/include on the include path: fesvr/syscall.h must not shadow the system header).
#   bash -lc 'source ci/env.sh && bash dv/auto_dv/isa/gen_isa_shim_build.sh lib  <outdir>'
#   bash -lc 'source ci/env.sh && bash dv/auto_dv/isa/gen_isa_shim_build.sh test <outdir> <prog.vmem>'
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT" || exit 1
MODE="${1:?lib|test}"; OUT="${2:?outdir}"
case "$OUT" in "$ROOT"/*) ;; *) echo "outdir must be inside $ROOT" >&2; exit 2 ;; esac
mkdir -p "$OUT"
SPIKE=tools/spike
CXX=g++
FLAGS=(-std=c++2a -O1 -Wall -Wno-unused-parameter -fPIC -I "$SPIKE/include" -I dv/auto_dv/isa)
LIBS=(-L "$SPIKE/lib" -lriscv -lsoftfloat -Wl,-rpath,"$ROOT/$SPIKE/lib")
SRC=dv/auto_dv/isa/gen_isa_shim.cc
[ -f "$SRC" ] || { echo "gen_isa_shim_build.sh: $SRC does not exist" >&2; exit 3; }
case "$MODE" in
  lib)
    "$CXX" "${FLAGS[@]}" -shared "$SRC" "${LIBS[@]}" -o "$OUT/libgen_isa_shim.so" && echo "built $OUT/libgen_isa_shim.so" ;;
  test)
    VMEM="${3:?prog.vmem}"
    "$CXX" "${FLAGS[@]}" dv/auto_dv/isa/gen_ut_isa_shim.cc "$SRC" "${LIBS[@]}" -o "$OUT/gen_ut_isa_shim" || exit $?
    "$OUT/gen_ut_isa_shim" "$VMEM" ;;
  *) echo "usage: lib|test" >&2; exit 2 ;;
esac
