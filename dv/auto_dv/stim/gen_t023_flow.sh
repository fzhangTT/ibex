#!/usr/bin/env bash
# T-023 stimulus toolchain proof (bring-up driver kept as evidence; the maintained flow is
# dv/auto_dv/stim/gen_program.py), steps 3-5: generate one seeded program with the compiled riscv-dv
# generator, assemble/link it with the lowRISC toolchain and gen_link.ld, convert to the TB image,
# run it standalone on the pinned upstream Spike. Run from a login shell with ci/env.sh sourced.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
T="$ROOT/dv/auto_dv/stim/gen_riscv_dv_target"   # NOTE: run.py needs the fixed-name copy gen_program.py materializes
OUT="$ROOT/dv/auto_dv/work/tb-infra/out_t023"
GEN="$OUT/gen"
SEED="${SEED:-1}"
TEST="${TEST:-gen_rand_smoke}"
ISA_SPIKE="rv32imc_zicsr_zifencei_zba_zbb_zbc_zbs_zicntr_zihpm_zicclsm"
OBJDUMP="$(dirname "$RISCV_GCC")/$(basename "$RISCV_GCC" | sed s/-gcc/-objdump/)"
NM="$(dirname "$RISCV_GCC")/$(basename "$RISCV_GCC" | sed s/-gcc/-nm/)"
mkdir -p "$OUT/prog"

echo "=== step 3a: generate (seed $SEED, test $TEST)"
cd "$ROOT/vendor/google_riscv-dv" || exit 1
python3 run.py --so -si vcs -ct "$T" -ext "$T/user_extension" --isa rv32imc_zba_zbb_zbc_zbs --mabi ilp32 \
  -o "$GEN" -tn "$TEST" --seed "$SEED" -s gen --noclean -v > "$OUT/runpy_so.log" 2>&1
echo "run.py --so exit: $?"
ASM="$(ls "$GEN"/asm_test/${TEST}_*.S 2>/dev/null | head -1)"
[ -n "$ASM" ] || { echo "no .S produced; see $OUT/runpy_so.log"; tail -20 "$OUT/runpy_so.log"; exit 1; }
cp "$ASM" "$OUT/prog/prog.S"
echo "generated: $ASM ($(grep -cvE '^\s*(#|$)' "$ASM") non-empty lines)"

echo "=== step 3b: assemble + link (gcc -march=rv32imcb, gen_link.ld, -Wl,-N)"
cd "$ROOT" || exit 1
"$RISCV_GCC" -static -mcmodel=medany -fvisibility=hidden -nostdlib -nostartfiles \
  -march=rv32imcb -mabi=ilp32 -Wl,-N -T "$T/gen_link.ld" -I "$T/user_extension" \
  "$OUT/prog/prog.S" "$T/gen_boot_stub.S" "$T/gen_debug_rom_stub.S" -o "$OUT/prog/prog.elf" > "$OUT/prog/gcc.log" 2>&1
echo "gcc exit: $?"; cat "$OUT/prog/gcc.log" | head -20
"$OBJDUMP" -d "$OUT/prog/prog.elf" > "$OUT/prog/prog.dis"
"$NM" -n "$OUT/prog/prog.elf" > "$OUT/prog/prog.nm"
echo "symbols: $(grep -E ' (gen_boot_entry|_start|tohost|test_done|mtvec_handler|gen_debug_rom_entry)$' "$OUT/prog/prog.nm" | tr '\n' ';')"
echo "zb mnemonics in program: $(grep -oE '\b(sh[123]add|andn|orn|xnor|rol|ror|rori|min|max|minu|maxu|clz|ctz|cpop|sext\.[bh]|zext\.h|rev8|orc\.b|clmul[rh]?|bclr|bset|binv|bext|bclri|bseti|binvi|bexti)\b' "$OUT/prog/prog.dis" | sort | uniq -c | sort -rn | tr '\n' ';')"

echo "=== step 4: ELF -> TB image"
python3 "$ROOT/dv/auto_dv/stim/gen_elf2mem.py" "$OUT/prog/prog.elf"

echo "=== step 5: standalone Spike"
ENTRY=$(python3 -c "import json;print(json.load(open('$OUT/prog/prog.sym.json'))['entry'])")
timeout 120 "$ROOT/tools/spike/bin/spike" --isa="$ISA_SPIKE" --priv=mu --pmpregions=16 --pmpgranularity=4 \
  --triggers=1 -m0x1a110000:0x1000,0x80000000:0x100000 --pc="$ENTRY" --log-commits \
  --log="$OUT/prog/spike_commits.log" "$OUT/prog/prog.elf" > "$OUT/prog/spike_stdout.log" 2>&1
echo "spike exit: $? (0 = tohost pass code)"
echo "commit log lines: $(wc -l < "$OUT/prog/spike_commits.log")"
head -3 "$OUT/prog/spike_commits.log"; echo ...; tail -3 "$OUT/prog/spike_commits.log"
