"""gen_mutant_build_identity.py <landing root> <build> <scratch root>: every mutant build must differ from the landing build in exactly the
file its mutation names, and nothing else. This is the gate that catches a root left over from an earlier batch on an
earlier build, which would otherwise be retained as if it belonged to this pass. Compares each root's per-file sha256
list against the landing build's and prints the differing files; exits 1 on any root that does not differ in exactly one
file, or whose differing file is not the mutation's file.

Exit codes, kept distinct so a routine cleanup does not read as a failure: 0 every root verified; 1 a real mismatch,
which is a build that does not differ from the landing build in exactly its mutated file; 2 a wrong call; 3 nothing
mismatched but at least one root could not be checked because its scratch tree is purged, so run this BEFORE the
cleanup that follows a landing."""
import pathlib
import sys
USAGE = "usage: gen_mutant_build_identity.py <landing root> <build> <scratch root>"


def _usage(msg=None):
    """A wrong call is answered, not crashed: the tools are read by reviewers who have not seen them before."""
    if msg:
        print(msg)
    print(USAGE)
    sys.exit(2)


if len(sys.argv) < 4 or sys.argv[1] in ("-h", "--help"):
    _usage()


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
# Three outcomes, kept apart on purpose: a purged scratch root cannot be verified and must not be counted as a
# mismatch, or a routine cleanup reads as a wall of failures to whoever runs this after a landing.
bad, absent, verified = 0, 0, 0
for rid, mfile in MUT_FILE.items():
    p = S / "mut_root" / rid / "out/sources_sha256.txt"
    lst = read_list(p)
    if lst is None:
        print("%-13s NOT VERIFIABLE: no sources list (the scratch root is purged after its landing)" % rid)
        absent += 1
        continue
    if set(lst) != set(base):
        print("%-13s MISMATCH: file set differs from the landing build" % rid)
        bad += 1
        continue
    diff = sorted(f for f in base if lst[f] != base[f])
    ok = diff == [mfile]
    print("%-13s differs in %d file(s): %s  %s" % (rid, len(diff), ", ".join(diff) or "none", "OK" if ok else "MISMATCH (expected %s)" % mfile))
    verified += 1 if ok else 0
    bad += 0 if ok else 1
print("\nverified %d, MISMATCHED %d, not verifiable (root purged) %d" % (verified, bad, absent))
if bad:
    print("FAIL: a mutant build does not differ from the landing build in exactly its mutated file")
    sys.exit(1)
if absent:
    print("INCOMPLETE: nothing mismatched, but %d root(s) could not be checked; re-run before the roots are purged" % absent)
    sys.exit(3)
sys.exit(0)
