"""gen_mutant_build_identity.py <landing root> <build> <scratch root> <build>: every mutant build must differ from the landing build in exactly the
file its mutation names, and nothing else. This is the gate that catches a root left over from an earlier batch on an
earlier build, which would otherwise be retained as if it belonged to this pass. Compares each root's per-file sha256
list against the landing build's and prints the differing files; exits 1 on any root that does not differ in exactly one
file, or whose differing file is not the mutation's file."""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
B = sys.argv[2]
S = pathlib.Path(sys.argv[3])   # the scratch root holding the out-of-tree mutant roots

MUT_FILE = {
    "DATAMISS_np": "dv/auto_dv/tb/gen_icache_ram.sv",
    "DATAMISS_npf": "dv/auto_dv/tb/gen_icache_ram.sv",
    "DATAWAY_np": "dv/auto_dv/tb/gen_icache_ram.sv",
    "DATAWAY_npf": "dv/auto_dv/tb/gen_icache_ram.sv",
    "RETSEQ_npf": "dv/auto_dv/env/gen_checkers_pkg.sv",
    "RETIDX_npf": "dv/auto_dv/env/gen_checkers_pkg.sv",
    "RED0": "dv/auto_dv/env/gen_checkers_pkg.sv",
    "DATAANN": "dv/auto_dv/tb/gen_icache_ram.sv",
    "DATAMISS": "dv/auto_dv/tb/gen_icache_ram.sv",
    "DATAWAY": "dv/auto_dv/tb/gen_icache_ram.sv",
    "BITS": "dv/auto_dv/tb/gen_icache_ram.sv",
    "ALIGN": "dv/auto_dv/env/gen_checkers_pkg.sv",
    "TRACE17": "dv/auto_dv/tb/gen_tb_pkg.sv",
}


def read_list(p):
    out = {}
    if not p.exists():
        return None
    for l in p.read_text().splitlines():
        parts = l.split()
        if len(parts) == 2:
            out[parts[1]] = parts[0]
    return out


base = read_list(ROOT / "dv/auto_dv/work/tb-infra/wit" / B / "sources_sha256.txt")
if not base:
    print("REFUSED: no sources list for build %s" % B)
    sys.exit(1)
print("landing build %s: %d files" % (B, len(base)))
bad = 0
for rid, mfile in MUT_FILE.items():
    p = S / "mut_root" / rid / "out/sources_sha256.txt"
    lst = read_list(p)
    if lst is None:
        print("%-13s NO SOURCES LIST (root absent or not compiled)" % rid)
        bad += 1
        continue
    if set(lst) != set(base):
        print("%-13s FILE SET DIFFERS from the landing build" % rid)
        bad += 1
        continue
    diff = sorted(f for f in base if lst[f] != base[f])
    ok = diff == [mfile]
    print("%-13s differs in %d file(s): %s  %s" % (rid, len(diff), ", ".join(diff) or "none", "OK" if ok else "MISMATCH (expected %s)" % mfile))
    if not ok:
        bad += 1
print("\nroots not matching their mutation: %d" % bad)
sys.exit(1 if bad else 0)
