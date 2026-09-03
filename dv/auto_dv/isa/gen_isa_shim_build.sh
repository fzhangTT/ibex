#!/usr/bin/env bash
# gen_isa_shim_build.sh: build the ISA shim as a shared library for VCS (-LDFLAGS "-L<out> -lgen_isa_shim")
# and, with `test`, the C++ unit test. No RPATH is baked in: the run flow exports LD_LIBRARY_PATH for the
# spike libraries (test mode exports it itself before running the binary). Spike headers/libs from
# tools/spike (only <prefix>/include on the include path: fesvr/syscall.h must not shadow the system
# header). <outdir> is any absolute path, inside or outside the clone.
#   bash -lc 'source ci/env.sh && bash dv/auto_dv/isa/gen_isa_shim_build.sh lib  <outdir>'
#   bash -lc 'source ci/env.sh && bash dv/auto_dv/isa/gen_isa_shim_build.sh test <outdir> <prog.vmem>'
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT" || exit 1
MODE="${1:?lib|test}"; OUT="${2:?outdir}"
case "$OUT" in /*) ;; *) echo "outdir must be an absolute path" >&2; exit 2 ;; esac
mkdir -p "$OUT"
SPIKE=tools/spike
CXX=g++
FLAGS=(-std=c++2a -O1 -Wall -Wno-unused-parameter -fPIC -I "$SPIKE/include" -I dv/auto_dv/isa)
LIBS=(-L "$SPIKE/lib" -lriscv -lsoftfloat)
SRC=(dv/auto_dv/isa/gen_isa_shim.cc dv/auto_dv/isa/gen_isa_shim_counters.cc)
for f in "${SRC[@]}"; do [ -f "$f" ] || { echo "gen_isa_shim_build.sh: $f does not exist" >&2; exit 3; }; done
case "$MODE" in
  lib)
    "$CXX" "${FLAGS[@]}" -shared "${SRC[@]}" "${LIBS[@]}" -o "$OUT/libgen_isa_shim.so" && echo "built $OUT/libgen_isa_shim.so" ;;
  test)
    VMEM="${3:?prog.vmem}"
    "$CXX" "${FLAGS[@]}" dv/auto_dv/isa/gen_ut_isa_shim.cc "${SRC[@]}" "${LIBS[@]}" -o "$OUT/gen_ut_isa_shim" || exit $?
    export LD_LIBRARY_PATH="$ROOT/$SPIKE/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
    echo "# gen_ut_isa_shim $(date -u +%Y-%m-%dT%H:%M:%SZ) shim sha256 $(sha256sum "${SRC[0]}" | cut -c1-16) counters sha256 $(sha256sum "${SRC[1]}" | cut -c1-16) test sha256 $(sha256sum dv/auto_dv/isa/gen_ut_isa_shim.cc | cut -c1-16) image $VMEM"
    "$OUT/gen_ut_isa_shim" "$VMEM" ;;
  *) echo "usage: lib|test" >&2; exit 2 ;;
esac
