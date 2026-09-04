#!/usr/bin/env python3
"""gen_read_keyed.py <run-dir> [<run-dir> ...] | --self-test: read the fcov checker's keyed output against the
coverage report itself, instead of trusting its verdict line.

For each run directory: load result.yaml's fcov_check, parse the urg report the checker was pointed at with the
parser below, and compare bin by bin. Two independent readings of one report stand behind every count that way,
which is what lets a reader believe a figure the checker alone reports. Bins no manifest declares are printed too
(the owed ones), because only a direct reading of the report finds them at all.

The parser here is deliberately NOT the checker's code and not gen_fcov's: an independent reading is the point. It
reads urg's text grpinfo.txt (Group, then Summary for Variable/Cross sections, then NAME COUNT bin tables).

Exit codes: 0 every declared bin agrees; 1 a disagreement or a missing key; 2 a wrong call."""
import io
import re
import sys
from pathlib import Path

USAGE = "usage: gen_read_keyed.py <run-dir> [<run-dir> ...] | --self-test"
OWED_SUFFIXES = ("during_invalidation", "masked_duplicate_copy")


def _usage(msg=None):
    """A wrong call is answered, not crashed: these tools are read by reviewers who have not seen them before."""
    if msg:
        print(msg)
    print(USAGE)
    sys.exit(2)


def parse_report(grpinfo: Path) -> dict:
    """{covergroup: {section: {bin: count}}} from a urg text grpinfo.txt, by this file's own reading of the format."""
    out: dict = {}
    cg = sec = cols = None
    in_bins = False
    for raw in io.open(grpinfo, encoding="utf-8", errors="replace"):
        line = raw.rstrip("\n")
        m = re.match(r"^Group : (?:\S*::)?(\S+)\s*$", line)
        if m:
            cg, sec, in_bins = m.group(1), None, False
            out.setdefault(cg, {})
            continue
        m = re.match(r"^Summary for (?:Variable|Cross) (\S+)\s*$", line)
        if m:
            sec, in_bins = m.group(1), False
            if cg:
                out[cg].setdefault(sec, {})
            continue
        if re.match(r"^(Covered bins|Uncovered bins|Bins)\s*$", line):
            in_bins, cols = True, None
            continue
        if re.match(r"^-{3,}\s*$", line) or not line.strip():
            continue
        if in_bins and line.startswith("NAME"):
            cols = line
            continue
        if in_bins and cg and sec and cols:
            parts = line.split()
            if len(parts) >= 2 and re.match(r"^-?\d+$", parts[1]):
                out[cg][sec][parts[0]] = int(parts[1])
    return out


def flatten(rep: dict) -> dict:
    """<covergroup>.<section>.<bin> -> count, the key form the checker emits."""
    return {"%s.%s.%s" % (cg, sec, b): c
            for cg, secs in rep.items() for sec, bins in secs.items() for b, c in bins.items()}


def read_run(run: Path, yaml_mod) -> int:
    res = yaml_mod.safe_load(io.open(run / "result.yaml", encoding="utf-8"))
    fc = res.get("fcov_check") or {}
    print("\n=== %s ===" % res.get("test"))
    derived = fc.get("derived_report_dir")
    if not derived:
        print("  no derived report: fcov status %s" % fc.get("status"))
        return 1
    mine = flatten(parse_report(Path(derived) / "grpinfo.txt"))
    agree = differ = missing = 0
    for key, got in sorted((fc.get("bins") or {}).items()):
        state, count = got.get("state"), got.get("count")
        if key not in mine:
            print("  NOT IN MY READING  %-56s the checker says %s %s" % (key, state, count))
            missing += 1
        elif count is not None and str(mine[key]) != str(count):
            print("  COUNT DIFFERS      %-56s checker %s, my reading %s" % (key, count, mine[key]))
            differ += 1
        else:
            agree += 1
    print("  declared %s | my reading agrees on %d, differs on %d, absent from my reading %d"
          % (fc.get("declared"), agree, differ, missing))
    print("  the checker's own status line, NOT relied on above: %s" % fc.get("status"))
    owed = {k: v for k, v in mine.items() if any(k.endswith("." + o) for o in OWED_SUFFIXES)}
    print("  bins no manifest declares, from the report alone: %s" % (owed or "none present"))
    return differ + missing


REPORT_FIXTURE = """Group : gen_pkg::gen_x_cg

Summary for Variable cp_a

Covered bins

NAME   COUNT AT LEAST
hit_a  7     1
hit_b  0     1

----------

Summary for Variable cp_b

Bins

NAME   COUNT AT LEAST
only   3     1

----------
"""


def _self_test() -> None:
    """Fabricate a report and three result.yaml files, so agreement, a count mismatch and a missing key are all seen."""
    import tempfile
    try:
        import yaml
    except ImportError:
        _usage("PyYAML is needed for --self-test")
    ok = True
    with tempfile.TemporaryDirectory(prefix="gen_read_keyed_selftest_") as td:
        root = Path(td)
        rep = root / "urgReport_variable_form"
        rep.mkdir()
        (rep / "grpinfo.txt").write_text(REPORT_FIXTURE, encoding="ascii")

        parsed = flatten(parse_report(rep / "grpinfo.txt"))
        want = {"gen_x_cg.cp_a.hit_a": 7, "gen_x_cg.cp_a.hit_b": 0, "gen_x_cg.cp_b.only": 3}
        cond = parsed == want
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", "the parser reads three bins including a Bins-titled table (%s)" % parsed)

        cases = (("agreeing", {"gen_x_cg.cp_a.hit_a": {"state": "HIT", "count": "7"}}, 0),
                 ("a count mismatch", {"gen_x_cg.cp_a.hit_a": {"state": "HIT", "count": "99"}}, 1),
                 ("a key absent from the report", {"gen_x_cg.cp_a.nope": {"state": "HIT", "count": "1"}}, 1))
        for label, bins, want_rc in cases:
            run = root / label.replace(" ", "_")
            run.mkdir()
            (run / "result.yaml").write_text(yaml.safe_dump(
                {"test": "gen_selftest_" + label.replace(" ", "_"),
                 "fcov_check": {"status": "PASS", "declared": len(bins), "bins": bins,
                                "derived_report_dir": str(rep)}}, sort_keys=False), encoding="ascii")
            rc = read_run(run, yaml)
            cond = rc == want_rc
            ok &= cond
            print("SELF-TEST", "ok " if cond else "BAD",
                  "%s gives rc %d (want %d)" % (label, rc, want_rc))

        run = root / "no_report"
        run.mkdir()
        (run / "result.yaml").write_text(yaml.safe_dump(
            {"test": "gen_selftest_no_report", "fcov_check": {"status": "NO_MANIFEST", "bins": {}}},
            sort_keys=False), encoding="ascii")
        rc = read_run(run, yaml)
        cond = rc == 1
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", "a run with no derived report gives rc %d (want 1)" % rc)

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


def main() -> None:
    args = sys.argv[1:]
    if not args:
        _usage()
    if "--self-test" in args:
        if args != ["--self-test"]:
            _usage("--self-test takes no other argument")
        _self_test()
    if any(a.startswith("-") for a in args):
        _usage("unknown argument: %s" % next(a for a in args if a.startswith("-")))
    try:
        import yaml
    except ImportError:
        _usage("PyYAML is needed to read result.yaml")
    bad = 0
    for a in args:
        run = Path(a)
        if not (run / "result.yaml").is_file():
            _usage("no result.yaml under %s" % run)
        bad += read_run(run, yaml)
    print("\n%s" % ("every declared bin agrees with this file's own reading of the report" if bad == 0
                    else "%d disagreement(s) between the checker and this file's reading" % bad))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
