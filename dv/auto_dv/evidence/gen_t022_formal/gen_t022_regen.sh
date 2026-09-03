#!/usr/bin/env bash
# Regenerate the T-022 formal model from this clone and re-run one SymbiYosys job.
# Usage (from the clone root, after `source ci/env.sh`):
#   bash dv/auto_dv/evidence/gen_t022_formal/gen_t022_regen.sh <outdir> [job ...]
# Steps: sv2v -> t022_all.v (byte-identical to the retained model), yosys netlist, formal copies
# from the patches, then `sby -f` for every job named (default: t022_core5).
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../../../.." && pwd)
E="$ROOT/dv/auto_dv/evidence/gen_t022_formal"
OUT=${1:?outdir required}; shift || true
JOBS=("$@"); [ ${#JOBS[@]} -eq 0 ] && JOBS=(t022_core5)
mkdir -p "$OUT"; cd "$ROOT"

# 0. The scratch top re-types the opentitan integer parameters (model/gen_t022_top.sv). Fail loud if
#    they differ from `util/ibex_config.py opentitan vcs_opts` (-pvalue+NAME=VALUE): a config change
#    would otherwise silently invalidate every proof below.
python3 - "$E/model/gen_t022_top.sv" <<'PYCHK'
import re, subprocess, sys
top = open(sys.argv[1]).read()
cfg = subprocess.run([sys.executable, "util/ibex_config.py", "opentitan", "vcs_opts"],
                     check=True, capture_output=True, text=True).stdout
want = {m.group(1): int(m.group(2)) for m in re.finditer(r"-pvalue\+(\w+)=(\d+)", cfg)}
blk = top[top.index("gen_dut_top #("):top.index(") u_dut")]
def val(v):
    v = v.strip(); m = re.match(r"^\d+'[bhd]([0-9a-fA-F]+)$", v)
    return int(m.group(1), {"b": 2, "h": 16, "d": 10}[v.split("'")[1][0]]) if m else int(v)
have = {m.group(1): val(m.group(2)) for m in re.finditer(r"\.(\w+)\(([^)]*)\)", blk)}
bad = [f"{k}: top={have.get(k)} config={want[k]}" for k in want if have.get(k) != want[k]]
extra = sorted(set(have) - set(want))
if bad or extra:
    sys.exit("gen_t022_regen: scratch-top parameters disagree with util/ibex_config.py opentitan: "
             + "; ".join(bad) + (" ; not in config: " + ", ".join(extra) if extra else ""))
print(f"gen_t022_regen: {len(want)} scratch-top parameters equal util/ibex_config.py opentitan vcs_opts")
PYCHK

# 1. SystemVerilog -> Verilog-2005. Defines: SYNTHESIS + DV_FCOV_DISABLE drop the DV macros; the
#    five enum defines are `util/ibex_config.py opentitan vcs_opts` (+define+ terms). The -pvalue+
#    integers of that config are set on the scratch top (model/gen_t022_top.sv), not here.
FILES=$(grep -v '^//' dv/auto_dv/tb/gen_rtl.f | grep -v '^+incdir' | grep -v '^$')
sv2v -DSYNTHESIS -DDV_FCOV_DISABLE \
  -DBaseIsa=ibex_pkg::BaseIsaRV32IorCHERIoT -DRV32M=ibex_pkg::RV32MSingleCycle \
  -DRV32B=ibex_pkg::RV32BOTEarlGrey -DRV32ZC=ibex_pkg::RV32ZcaZcbZcmp -DRegFile=ibex_pkg::RegFileFF \
  -Ivendor/lowrisc_ip/dv/sv/dv_utils -Ivendor/lowrisc_ip/ip/prim/rtl \
  $FILES dv/auto_dv/tb/gen_tb_pkg.sv dv/auto_dv/tb/gen_dut_top.sv "$E/model/gen_t022_top.sv" \
  > "$OUT/t022_all_full.v"

# 2. Drop the wrapper's config banner and elaboration guard (string functions yosys cannot parse):
#    keep gen_dut_top up to the close of its u_register_file instantiation, then endmodule.
awk 'BEGIN{skip=0} /^module gen_dut_top \(/{in_dut=1}
     in_dut && /^\t\) u_register_file\(/{rf=1}
     in_dut && rf && /^\t\);$/ && !skip {print; print "endmodule"; skip=1; next}
     skip && /^endmodule$/ {skip=0; in_dut=0; next}
     !skip {print}' "$OUT/t022_all_full.v" > "$OUT/t022_all.v"

# 3. Flattened netlist with constant propagation (section 4.3 of gen_unreachability_evidence.md).
sed "s|/tmp/[^ ]*/scratchpad/|$OUT/|g" "$E/model/gen_t022_elab.ys" > "$OUT/t022_elab.ys"
yosys -q -l "$OUT/t022_elab.log" "$OUT/t022_elab.ys"

# 4. Assertion-bearing formal copies = t022_all.v + the retained patch (RTL untouched). Every
#    committed file carries the gen_ landing prefix; the tool-native name (what the .sby [files]
#    section names) is the basename without it.
for p in "$E"/sources/gen_t022_formal*.patch; do
  v=$(basename "$p" .patch); v=${v#gen_}
  patch -s -o "$OUT/$v.v" "$OUT/t022_all.v" "$p"
done

# 5. Re-run jobs. The retained .sby files name the original scratchpad path in [files]; point them
#    at the regenerated copy. Evidence rule: a run counts only with 0 implicit declarations.
for j in "${JOBS[@]}"; do
  sed "s|^/tmp/.*/\(t022_formal[^/]*\.v\)$|$OUT/\1|" "$E/jobs/gen_$j.sby" > "$OUT/$j.sby"
  (cd "$OUT" && sby -f "$j.sby" > "$OUT/$j.out" 2>&1) || true
  echo "$j: $(grep -E 'summary: (successful|counterexample|unreached)|DONE' "$OUT/$j.out" | tr '\n' ' ')"
  echo "$j: implicit declarations = $(grep -c 'implicitly declared' "$OUT/$j/model/design.log" || true); smt2 asserts = $(grep -c assert "$OUT/$j/model/design_smt2.smt2" || true) (retained: $(cat "$E/runs/$j/gen_smt2_assert_count.txt" 2>/dev/null))"
done
