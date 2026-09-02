#!/usr/bin/env bash
# Build the lowRISC spike fork the ibex cosim TB links against.
# Rev pinned to match this repo's flake.nix; dv/cosim/* is written against it.
# Requires dtc on PATH — loaded by ci/env.sh.
# Needs ZIHPM enabled (aadf648d) so U-mode HPM-counter access is gated by
# mcounteren rather than blanket-disabled, matching ibex's mcounteren support.
set -euo pipefail
SPIKE_REV=aadf648d742de54f0a50eec01ceffd13ed12a1d1
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
# Static gcc runtimes for spike's own objects; note DT_NEEDED on libstdc++.so.6
# remains via shared Boost. Runtime compatibility on this site rests on
# gcc-toolset-11's DTS model (symbol floor = RHEL8 system libstdc++); the
# definitive check is the TB DPI link + simv load in the smoke test.
../configure --enable-commitlog --enable-misaligned --prefix="$PREFIX" \
             LDFLAGS="-static-libstdc++ -static-libgcc"
make -j"$(nproc)"
make install
echo "spike installed to $PREFIX"
