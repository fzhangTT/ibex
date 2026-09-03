#!/usr/bin/env bash
# Fetch the lowRISC rv32imcb toolchain release (bitmanip-patched GCC).
# Version matches ci/vars.env (RISCV_TOOLCHAIN_TAR_VERSION=20220210-1).
set -euo pipefail
VER=20220210-1
NAME=lowrisc-toolchain-gcc-rv32imcb-$VER
URL=https://github.com/lowRISC/lowrisc-toolchains/releases/download/$VER/$NAME.tar.xz
IBEX_TOOLS_DIR="${IBEX_TOOLS_DIR:-/localdev/fzhang/ws/tools}"
DEST="$IBEX_TOOLS_DIR/lowrisc-toolchain-gcc-rv32imcb"

mkdir -p "$IBEX_TOOLS_DIR"
cd "$IBEX_TOOLS_DIR"
[ -f "$NAME.tar.xz" ] || { curl -fL -o "$NAME.tar.xz.part" "$URL" && mv "$NAME.tar.xz.part" "$NAME.tar.xz"; }
tar xf "$NAME.tar.xz"
rm -rf "$DEST"
mv "$NAME" "$DEST"
"$DEST/bin/riscv32-unknown-elf-gcc" --version | head -1
