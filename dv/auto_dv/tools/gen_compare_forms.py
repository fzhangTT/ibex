#!/usr/bin/env python3
"""gen_compare_forms.py: compare one entry set across two run forms bin by bin, and read each report's own
isolation evidence rather than assuming the flow delivered it.

An entry run alone into its own vdb and the same entry run into a shared vdb should agree on every declared bin.
Where they do not, either the shared slice is not the per-test slice or the entry's stimulus depends on its
neighbours, and a coverage figure taken from the shared form is then not the figure the entry earns. The number of
tests in each report is read out of the report's own tests.txt, so the isolation claim rests on the artefact and
not on the flow's promise.

Usage:
    gen_compare_forms.py --isolated ROOT --shared ROOT --entries a,b,c
    gen_compare_forms.py --self-test

ROOT layouts: the isolated root holds <entry>/result.yaml; the shared root holds <entry>_<seed>/result.yaml.
Exit codes: 0 every entry agrees on every declared bin with one test per report; 1 a disagreement, a verdict
mismatch or a report holding other than one test; 2 a wrong call.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

TESTS_IN_REPORT_RE = re.compile(r"Total tests in report:\s*(\d+)")


def load_run(run_dir: Path) -> dict[str, Any]:
    """One run's verdict, fcov status, per-bin (state, count) and the test count its own report declares."""
    res = yaml.safe_load(io.open(run_dir / "result.yaml", encoding="utf-8"))
    fc = res.get("fcov_check") or {}
    bins = {k: (v.get("state"), str(v.get("count"))) for k, v in (fc.get("bins") or {}).items()}
    tests_in_report = None
    if fc.get("report_dir"):
        tests_txt = Path(fc["report_dir"]) / "tests.txt"
        if tests_txt.is_file():
            m = TESTS_IN_REPORT_RE.search(tests_txt.read_text(errors="replace"))
            tests_in_report = int(m.group(1)) if m else None
    return {"verdict": res.get("verdict"), "status": fc.get("status"), "bins": bins,
            "tests_in_report": tests_in_report}


def compare(isolated_root: Path, shared_root: Path, entries: tuple[str, ...], seed: int = 1) -> dict[str, Any]:
    """Per entry: the two forms' bins compared key by key. The shared directory is named exactly, never globbed:
    these entry names are prefixes of one another, so a glob silently picks a sibling."""
    rows: list[dict[str, Any]] = []
    for name in entries:
        iso = load_run(isolated_root / name)
        shared = load_run(shared_root / f"{name}_{seed}")
        keys = sorted(set(iso["bins"]) | set(shared["bins"]))
        differing = [k for k in keys if iso["bins"].get(k) != shared["bins"].get(k)]
        rows.append({"entry": name, "isolated": iso, "shared": shared, "bins": len(keys),
                     "agree": len(keys) - len(differing), "differing": differing,
                     "verdicts_equal": iso["verdict"] == shared["verdict"],
                     "one_test_each": iso["tests_in_report"] == 1 and shared["tests_in_report"] == 1})
    bad = [r["entry"] for r in rows if r["differing"] or not r["verdicts_equal"] or not r["one_test_each"]]
    return {"rows": rows, "bins": sum(r["bins"] for r in rows), "agree": sum(r["agree"] for r in rows),
            "differing": sum(len(r["differing"]) for r in rows), "bad": bad}


def report(result: dict[str, Any]) -> None:
    print("%-46s %-8s %-8s %s" % ("entry", "isolated", "shared", "bins / isolation (tests in each report)"))
    for r in result["rows"]:
        print("%-46s %-8s %-8s %2d bins, %2d agree | isolated report %s test(s), shared report %s test(s)"
              % (r["entry"], r["isolated"]["verdict"], r["shared"]["verdict"], r["bins"], r["agree"],
                 r["isolated"]["tests_in_report"], r["shared"]["tests_in_report"]))
        for k in r["differing"]:
            print("    DIFFERS %-56s isolated %s shared %s"
                  % (k, r["isolated"]["bins"].get(k), r["shared"]["bins"].get(k)))
    print("\ntotal declared bins compared %d | identical in both forms %d | differing %d"
          % (result["bins"], result["agree"], result["differing"]))
    print("every report in both forms holds exactly one test: %s"
          % ("yes" if not result["bad"] else "NO, see " + ", ".join(result["bad"])))


def write_fixture(run_dir: Path, verdict: str, bins: dict[str, tuple[str, str]], tests_in_report: int | None,
                  report_name: str = "urgReport") -> None:
    """One fabricated run for the self-test. Each rewrite gets its own report directory, so a tests.txt written by
    an earlier fixture cannot be read as this one's isolation evidence."""
    run_dir.mkdir(parents=True, exist_ok=True)
    report_dir = run_dir / report_name
    report_dir.mkdir(exist_ok=True)
    if tests_in_report is not None:
        (report_dir / "tests.txt").write_text(f"Total tests in report: {tests_in_report}\n", encoding="ascii")
    doc = {"verdict": verdict,
           "fcov_check": {"status": "PASS", "report_dir": str(report_dir),
                          "bins": {k: {"state": s, "count": c} for k, (s, c) in bins.items()}}}
    (run_dir / "result.yaml").write_text(yaml.safe_dump(doc, sort_keys=False), encoding="ascii")


def self_test() -> int:
    ok = True
    hit = ("HIT", "7")
    with tempfile.TemporaryDirectory(prefix="gen_compare_forms_selftest_") as td:
        d = Path(td)
        iso, shared = d / "iso", d / "shared"
        # Two entries whose names are prefixes of one another, which is why the shared side is named exactly.
        write_fixture(iso / "gen_a", "PASS", {"cg.cp.x": hit}, 1)
        write_fixture(shared / "gen_a_1", "PASS", {"cg.cp.x": hit}, 1)
        write_fixture(iso / "gen_a_two", "PASS", {"cg.cp.y": hit}, 1)
        write_fixture(shared / "gen_a_two_1", "PASS", {"cg.cp.y": hit}, 1)
        r = compare(iso, shared, ("gen_a", "gen_a_two"))
        cond = r["bad"] == [] and r["bins"] == 2 and r["agree"] == 2 and r["differing"] == 0
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD",
              f"two forms agreeing on every bin with one test per report: bad={r['bad']} agree={r['agree']}")
        # The prefix trap: gen_a's shared row must be gen_a_1, never gen_a_two_1.
        cond = r["rows"][0]["differing"] == [] and set(r["rows"][0]["isolated"]["bins"]) == {"cg.cp.x"}
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD",
              f"the shared directory is named exactly, so a prefix sibling is not picked: {sorted(r['rows'][0]['isolated']['bins'])}")
        # A count that moved between the forms is listed, not summarised away.
        write_fixture(shared / "gen_a_1", "PASS", {"cg.cp.x": ("HIT", "3")}, 1, "urgReport_b")
        r = compare(iso, shared, ("gen_a",))
        cond = r["bad"] == ["gen_a"] and r["differing"] == 1 and r["rows"][0]["differing"] == ["cg.cp.x"]
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD",
              f"a bin whose count differs between the forms is named: differing={r['rows'][0]['differing']}")
        # A bin only one form declares differs, since the other form has no reading of it at all.
        write_fixture(shared / "gen_a_1", "PASS", {"cg.cp.x": hit, "cg.cp.z": hit}, 1, "urgReport_c")
        r = compare(iso, shared, ("gen_a",))
        cond = r["rows"][0]["differing"] == ["cg.cp.z"] and r["bins"] == 2
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD",
              f"a bin present in one form only counts as differing: {r['rows'][0]['differing']}")
        # Isolation is read from the report: two tests in it is a failure even when every bin agrees.
        write_fixture(shared / "gen_a_1", "PASS", {"cg.cp.x": hit}, 2, "urgReport_d")
        r = compare(iso, shared, ("gen_a",))
        cond = r["differing"] == 0 and r["bad"] == ["gen_a"] and not r["rows"][0]["one_test_each"]
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD",
              f"a report holding two tests fails on isolation even with every bin agreeing: bad={r['bad']}")
        # No tests.txt at all is not silently an isolated report.
        write_fixture(shared / "gen_a_1", "PASS", {"cg.cp.x": hit}, None, "urgReport_e")
        r = compare(iso, shared, ("gen_a",))
        cond = r["bad"] == ["gen_a"] and r["rows"][0]["shared"]["tests_in_report"] is None
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD",
              "a report with no tests.txt is not read as isolated (tests_in_report None)")
        # A verdict difference is a failure on its own.
        write_fixture(shared / "gen_a_1", "FAIL", {"cg.cp.x": hit}, 1, "urgReport_f")
        r = compare(iso, shared, ("gen_a",))
        cond = r["differing"] == 0 and r["bad"] == ["gen_a"] and not r["rows"][0]["verdicts_equal"]
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD",
              f"the same bins under different verdicts is a failure: verdicts_equal={r['rows'][0]['verdicts_equal']}")
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--isolated", type=Path, help="root holding <entry>/result.yaml")
    ap.add_argument("--shared", type=Path, help="root holding <entry>_<seed>/result.yaml")
    # Named by the caller, never defaulted from the testlist: the set of entries carrying any given covergroup's
    # bins grows as entries land, so a default would change what a recorded invocation compared. Enforced on the
    # compare path rather than by argparse, so --self-test still needs no entry list.
    ap.add_argument("--entries", help="comma-separated entry names to compare (required unless --self-test)")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.isolated and a.shared):
        ap.error("--isolated and --shared are both required")
    if not a.entries:
        ap.error("--entries is required (the entry set is never defaulted from the testlist)")
    entries = tuple(x.strip() for x in a.entries.split(",") if x.strip())
    if not entries:
        ap.error("--entries named no entry")
    missing = [str(a.isolated / n) for n in entries if not (a.isolated / n / "result.yaml").is_file()]
    missing += [str(a.shared / f"{n}_{a.seed}") for n in entries
                if not (a.shared / f"{n}_{a.seed}" / "result.yaml").is_file()]
    if missing:
        print("no result.yaml under: " + ", ".join(missing), file=sys.stderr)
        return 2
    result = compare(a.isolated, a.shared, entries, a.seed)
    report(result)
    return 1 if result["bad"] else 0


if __name__ == "__main__":
    sys.exit(main())
