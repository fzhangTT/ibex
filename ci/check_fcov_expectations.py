#!/usr/bin/env python3
"""fcov-expectation checker: fail a test whose declared coverage bins were not hit.

The trust-triad rule 3 (docs/dv/dv_principles.md §6): every new test declares the
functional-coverage bins it intends to hit; declared-but-unhit bins FAIL the run,
verified per-test and pre-merge.

Per-test isolation mechanism (proven on VCS X-2025.06-SP2): the flow writes all tests
of one OUT tree into a shared VDB (`<OUT>/run/coverage/shared_cov/test.vdb`)
differentiated by `-cm_name test_<test>_<seed>`; `urg -tests <file>` selects one test
when the file contains the FULL vdb test identifier, which is
`<vdb path minus .vdb>/<cm_name>` (e.g. `.../shared_cov/test/test_riscv_arithmetic_
basic_test_1`) — verified to yield "Total tests in report: 1". Bin detail is parsed
from the text report's `grpinfo.txt`.

Manifest format (`<test>.fcov.yaml`):
    bins:
      - <covergroup>.<coverpoint>.<bin>   # e.g. uarch_cg.cp_controller_fsm.out_of_decode0
Counts for same-named covergroups sum across instances (e.g. core + shadow-core binds) —
the expectation is "hit anywhere in this test".

Modes:
    --self-test                  exercise hit/unhit classification on fabricated data
    --report-dir DIR             parse an existing urg report dir (skip urg invocation)
    --vdb VDB --cm-name NAME     run urg per-test selection, then parse
Exit codes: 0 all declared bins hit; 2 declared-but-unhit (test must FAIL);
            1 usage/protocol error (missing manifest, unparseable report, isolation
            impossible) — a protocol error also FAILS the run: unverifiable != pass.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def parse_manifest(path: Path) -> list[str]:
    bins: list[str] = []
    in_bins = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if re.match(r"^bins:\s*$", line):
            in_bins = True
            continue
        m = re.match(r"^\s*-\s*(\S+)\s*$", line)
        if in_bins and m:
            bins.append(m.group(1))
        elif line and not line.startswith(" "):
            in_bins = False
    if not bins:
        raise ValueError(f"{path}: no bins declared")
    return bins


def parse_groups_report(report_dir: Path) -> dict[str, int]:
    """Return {cg.coverpoint.bin: summed_hit_count} from urg's text report grpinfo.txt.

    grpinfo.txt structure (verified): `Group : <instance-path>::<cg>` headers,
    `Summary for Variable <cp>` per coverpoint, then `Uncovered bins` /
    `Covered bins` tables with rows `NAME COUNT AT_LEAST [NUMBER]`. Range rows
    (COUNT `--`) are skipped. Counts sum across instances of the same <cg>.
    """
    f = report_dir / "grpinfo.txt"
    if not f.is_file():
        raise ValueError(f"{f}: missing")
    hits: dict[str, int] = {}
    group = cp = None
    in_bins = False
    for raw in f.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.rstrip()
        g = re.match(r"^Group : \S*::(\S+)$", line)
        if g:
            group, cp, in_bins = g.group(1), None, False
            continue
        c = re.match(r"^Summary for Variable (\S+)$", line)
        if c:
            cp, in_bins = c.group(1), False
            continue
        if re.match(r"^(Uncovered bins|Covered bins)$", line):
            in_bins = True
            continue
        if re.match(r"^(Excluded/Illegal bins|Summary for|Variables for|-{10,}|={10,})", line):
            in_bins = False
            continue
        b = re.match(r"^([A-Za-z_][\w\[\]>=\-:.]*)\s+(\d+)\s+\d+", line)
        if in_bins and b and group and cp and b.group(1) != "NAME":
            key = f"{group}.{cp}.{b.group(1)}"
            hits[key] = hits.get(key, 0) + int(b.group(2))
    if not hits:
        raise ValueError(f"{f}: no covergroup bin rows parsed")
    return hits


def urg_per_test_report(vdb: Path, cm_name: str, workdir: Path) -> Path:
    """Generate a per-test urg text report; probe selection-flag support."""
    report = workdir / "urgReport"
    ident = f"{str(vdb)[:-4] if str(vdb).endswith('.vdb') else str(vdb)}/{cm_name}"
    sel_file = workdir / "test_selection.txt"
    sel_file.write_text(ident + "\n")
    cmd = ["urg", "-full64", "-dir", str(vdb), "-format", "text",
           "-report", str(report), "-tests", str(sel_file)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not (report / "grpinfo.txt").is_file():
        raise RuntimeError(f"urg per-test report failed: {(r.stdout + r.stderr)[-500:]}")
    tests_txt = (report / "tests.txt").read_text(encoding="utf-8", errors="replace") \
        if (report / "tests.txt").is_file() else ""
    m = re.search(r"Total tests in report: (\d+)", tests_txt)
    exact = re.search(rf"^\S*/{re.escape(cm_name)}\s*$", tests_txt, re.M)
    if not m or m.group(1) != "1" or not exact:
        raise RuntimeError(
            f"per-test isolation not confirmed (want exactly 1 test = {cm_name}); "
            f"tests.txt says: {m.group(0) if m else 'unparseable'}")
    return report


def classify(declared: list[str], hits: dict[str, int]) -> list[str]:
    """The one classification rule: a declared bin with no positive hit count is unhit."""
    return [b for b in declared if hits.get(b, 0) <= 0]


def self_test() -> int:
    # Exercises the REAL classify() — never a copy of its logic.
    fake = {"uarch_cg::cp_a.hit_bin": 3, "uarch_cg::cp_a.unhit_bin": 0}
    ok = (classify(["uarch_cg::cp_a.hit_bin"], fake) == []
          and classify(["uarch_cg::cp_a.hit_bin", "uarch_cg::cp_a.unhit_bin"], fake)
          == ["uarch_cg::cp_a.unhit_bin"]
          and classify(["uarch_cg::cp_a.no_such_bin"], fake) == ["uarch_cg::cp_a.no_such_bin"])
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path)
    ap.add_argument("--vdb", type=Path)
    ap.add_argument("--cm-name")
    ap.add_argument("--report-dir", type=Path, help="parse an existing urg report dir")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.manifest:
        print("ERROR: --manifest required", file=sys.stderr)
        return 1
    try:
        declared = parse_manifest(args.manifest)
        if args.report_dir:
            report = args.report_dir
        else:
            if not (args.vdb and args.cm_name):
                print("ERROR: need --vdb and --cm-name (or --report-dir)", file=sys.stderr)
                return 1
            report = urg_per_test_report(args.vdb, args.cm_name, Path(tempfile.mkdtemp(prefix="fcovexp_")))
        hits = parse_groups_report(report)
    except (ValueError, RuntimeError, OSError) as e:
        print(f"FCOV-EXPECTATION PROTOCOL ERROR: {e}", file=sys.stderr)
        return 1

    unhit = classify(declared, hits)
    for b in declared:
        state = "HIT" if hits.get(b, 0) > 0 else ("UNHIT" if b in hits else "MISSING-FROM-REPORT")
        print(f"FCOV-EXPECTATION: {b} = {state} (count={hits.get(b, 'n/a')})")
    if unhit:
        print(f"FCOV-EXPECTATION: FAIL — {len(unhit)} declared bin(s) not hit: {', '.join(unhit)}")
        return 2
    print(f"FCOV-EXPECTATION: PASS — all {len(declared)} declared bins hit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
