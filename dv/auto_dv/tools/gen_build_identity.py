"""gen_build_identity.py [--expect <16 hex>] [--root <tree>]: print the build identity the committer gate recomputes,
so a retained header's claim can be checked by whoever reads it.

The identity is gen_flow_util.filelist_digest over dv/auto_dv/tb/gen_rtl.f and gen_tb.f, which is NOT the "sources
sha256" gen_tb_local.sh writes into its own compile log: two functions over two different input sets, so a retained
header must say which one it quotes. With --expect the tool exits 1 on a mismatch, so a hand-off script can gate on it.

Exit codes: 0 printed (and equal to --expect when given); 1 the digest differs from --expect; 2 a wrong call."""
import importlib.util
import pathlib
import sys

USAGE = "usage: gen_build_identity.py [--expect <16 hex>] [--root <tree>]"


def _usage(msg=None):
    """A wrong call is answered, not crashed: the tools are read by reviewers who have not seen them before."""
    if msg:
        print(msg)
    print(USAGE)
    sys.exit(2)


expect = None
root = pathlib.Path(__file__).resolve().parents[3]
args = sys.argv[1:]
while args:
    a = args.pop(0)
    if a in ("-h", "--help"):
        _usage()
    elif a == "--expect":
        if not args:
            _usage("--expect needs a value")
        expect = args.pop(0).lower()
    elif a == "--root":
        if not args:
            _usage("--root needs a value")
        root = pathlib.Path(args.pop(0)).resolve()
    else:
        _usage("unknown argument: %s" % a)

flow = root / "dv/auto_dv/flow"
if not (flow / "gen_flow_util.py").is_file():
    _usage("no flow under %s" % root)

# The flow module is loaded against the given tree, so the tool works on a detached archive as well as the clone.
spec_c = importlib.util.spec_from_file_location("gen_flow_const", flow / "gen_flow_const.py")
fc = importlib.util.module_from_spec(spec_c)
sys.modules["gen_flow_const"] = fc
spec_c.loader.exec_module(fc)
fc.SOURCE_ROOT = root
spec_u = importlib.util.spec_from_file_location("gen_flow_util", flow / "gen_flow_util.py")
fu = importlib.util.module_from_spec(spec_u)
spec_u.loader.exec_module(fu)
fu.C.SOURCE_ROOT = root

lists = [root / "dv/auto_dv/tb/gen_rtl.f", root / "dv/auto_dv/tb/gen_tb.f"]
digest = fu.filelist_digest(lists)
short = digest["sources_sha256"][:16]
print("build identity   %s   (filelist_digest over %s, %d sources)"
      % (short, " + ".join(p.name for p in lists), digest["source_count"]))
if expect is not None and short != expect:
    print("MISMATCH: expected %s" % expect)
    sys.exit(1)
