#!/usr/bin/env bash
# Build the lowRISC spike fork the ibex cosim TB links against.
# Rev pinned to match this repo's flake.nix; dv/cosim/* is written against it.
set -euo pipefail
SPIKE_REV=4b97396656485a129119deaec2ba35e5bf354841
IBEX_TOOLS_DIR="${IBEX_TOOLS_DIR:-/localdev/fzhang/ws/tools}"
PREFIX="${SPIKE_INSTALL:-$IBEX_TOOLS_DIR/spike-ibex-cosim}"
SRC="$IBEX_TOOLS_DIR/src/riscv-isa-sim-lowrisc"

mkdir -p "$IBEX_TOOLS_DIR/src"
if [ ! -d "$SRC/.git" ]; then
    git clone https://github.com/lowRISC/riscv-isa-sim.git "$SRC"
fi
git -C "$SRC" fetch --all --tags
git -C "$SRC" checkout "$SPIKE_REV"

mkdir -p "$SRC/build"
cd "$SRC/build"
# Static gcc runtimes: the TB's DPI .so must load inside VCS, whose bundled
# libstdc++ may predate the build compiler's (flake.nix does the same).
../configure --enable-commitlog --enable-misaligned --prefix="$PREFIX" \
             LDFLAGS="-static-libstdc++ -static-libgcc"
make -j"$(nproc)"
make install
echo "spike installed to $PREFIX"
