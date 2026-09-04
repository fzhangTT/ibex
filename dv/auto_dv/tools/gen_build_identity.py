"""gen_build_identity.py [--expect <16 hex>] [--root <tree>]: print the build identity the committer gate recomputes,
so a retained header's claim can be checked by whoever reads it.

Two quantities are called "sources sha256" in prose and are not the same thing, so each is named here by its exact key
and input set. The one this tool prints is inputs.sources_sha256 in a build manifest: gen_flow_util.filelist_digest
over dv/auto_dv/tb/gen_rtl.f and gen_tb.f, the sources those two filelists name. The other is build_sources_sha256 in
a run header, written by gen_tb_local.sh over a find of dv/auto_dv/env, tb, isa and gen_tb, and printed by the same
script into its own compile log. A retained header that quotes a figure must say which key it quotes. With --expect
the tool exits 1 on a mismatch, so a hand-off can gate on it.

Exit codes: 0 printed (and equal to --expect when given); 1 the digest differs from --expect; 2 a wrong call."""
import importlib.util
import pathlib
import sys

USAGE = "usage: gen_build_identity.py [--expect <16 hex>] [--root <tree>] | --self-test"


def _usage(msg=None):
    """A wrong call is answered, not crashed: the tools are read by reviewers who have not seen them before."""
    if msg:
        print(msg)
    print(USAGE)
    sys.exit(2)



def _self_test():
    """Drive this tool as a subprocess against a synthetic tree, so the four exit paths are proven rather than read.

    The tree is synthetic because the real digest changes with every RTL or TB edit: a self-test that asserted the
    clone's own value would fail on the next unrelated commit and teach people to ignore it.
    """
    import shutil
    import subprocess
    import tempfile

    here = pathlib.Path(__file__).resolve()
    real_flow = here.parents[3] / "dv/auto_dv/flow"
    ok = True
    with tempfile.TemporaryDirectory(prefix="gen_build_identity_selftest_") as td:
        tree = pathlib.Path(td)
        (tree / "dv/auto_dv/flow").mkdir(parents=True)
        (tree / "dv/auto_dv/tb").mkdir(parents=True)
        for mod in ("gen_flow_const.py", "gen_flow_util.py"):
            shutil.copyfile(real_flow / mod, tree / "dv/auto_dv/flow" / mod)
        (tree / "dv/auto_dv/tb/a.sv").write_text("module a; endmodule\n", encoding="ascii")
        (tree / "dv/auto_dv/tb/b.sv").write_text("module b; endmodule\n", encoding="ascii")
        (tree / "dv/auto_dv/tb/gen_rtl.f").write_text("// synthetic\ndv/auto_dv/tb/a.sv\n", encoding="ascii")
        (tree / "dv/auto_dv/tb/gen_tb.f").write_text("// synthetic\ndv/auto_dv/tb/b.sv\n", encoding="ascii")

        def run(*extra):
            return subprocess.run([sys.executable, str(here), "--root", str(tree)] + list(extra),
                                  capture_output=True, text=True)

        r = run()
        digest = ""
        for tok in r.stdout.split():
            if len(tok) == 16 and all(c in "0123456789abcdef" for c in tok):
                digest = tok
                break
        cond = r.returncode == 0 and len(digest) == 16 and "2 sources" in r.stdout
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD",
              "the synthetic tree prints a digest over its 2 sources (rc %d, %s)" % (r.returncode, digest or "none"))

        r = run("--expect", digest)
        cond = r.returncode == 0 and "MISMATCH" not in r.stdout
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", "--expect with the true digest exits 0 (rc %d)" % r.returncode)

        r = run("--expect", "deadbeefdeadbeef")
        cond = r.returncode == 1 and "MISMATCH" in r.stdout
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD",
              "--expect with a wrong digest exits 1 and says MISMATCH (rc %d)" % r.returncode)

        r = run("--frobnicate")
        cond = r.returncode == 2 and "unknown argument" in r.stdout
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD",
              "an unknown argument exits 2 with the usage (rc %d)" % r.returncode)

        r = subprocess.run([sys.executable, str(here), "--root", str(tree / "dv")], capture_output=True, text=True)
        cond = r.returncode == 2 and "no flow under" in r.stdout
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", "a --root with no flow exits 2 (rc %d)" % r.returncode)

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if "--self-test" in sys.argv[1:]:
    if sys.argv[1:] != ["--self-test"]:
        _usage("--self-test takes no other argument")
    _self_test()


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
