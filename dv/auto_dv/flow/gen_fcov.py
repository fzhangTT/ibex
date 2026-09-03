#!/usr/bin/env python3
"""fcov-expectation wiring (trust triad rule 3): every test declares the functional-coverage bins
it intends to hit in dv/auto_dv/fcov_expectations/<test>.fcov.yaml; a declared-but-unhit bin
FAILS the run. The verdict is ci/check_fcov_expectations.py's (per test, pre-merge, on the test's
own vdb slice via `urg -tests <vdb minus .vdb>/<cm_name>`); this module validates the manifest
schema, drives the checker, parses its per-bin lines and carries the anti-vacuity notes through.

Manifest schema (`<test>.fcov.yaml`, file stem == test name):
    test: gen_<name>                      # must equal the file stem
    owner: <role slug>
    bins:                                 # gen_<feature>_cg.<coverpoint>.<bin>, at least one
      - gen_regime_cg.cp_regime.bin_fast
    anti_vacuity:                         # one note per declared bin: why a hit evidences the stimulus
      gen_regime_cg.cp_regime.bin_fast: "regime knob sampled once per phase; fast only when the schedule selects it"
The checker reads only `bins:`; the flow reads the rest (notes are carried, never interpreted).

Usage:
    gen_fcov.py --validate <manifest.fcov.yaml> [...]     # schema check (exit 1 on a violation)
    gen_fcov.py --self-test                                # fabricated urg report dir through the real checker
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import gen_flow_const as C
import gen_flow_util as U

BIN_RE = re.compile(r"^(gen_\w+)\.([A-Za-z_]\w*)\.(\S+)$")
RESULT_LINE_RE = re.compile(r"^FCOV-EXPECTATION: (\S+) = (HIT|UNHIT|MISSING-FROM-REPORT) \(count=(\S+)\)")
STATUS_BY_EXIT = C.FCOV_EXIT_CODES
REASON_UNMET = "fcov expectation unmet"
REASON_UNVERIFIABLE = "fcov expectation unverifiable"


def manifest_path(test: dict[str, Any]) -> Path | None:
    f = test.get("fcov_expectation_file")
    return (C.REPO_ROOT / f).resolve() if f else None


def validate_manifest(path: Path, test_name: str | None = None) -> tuple[dict[str, Any] | None, list[str]]:
    """Schema rules the flow enforces on top of the checker's `bins:` parse."""
    problems: list[str] = []
    if not path.is_file():
        return None, [f"{path}: missing"]
    data = U.load_yaml(path)
    if not isinstance(data, dict):
        return None, [f"{path}: not a mapping"]
    stem = path.name[: -len(".fcov.yaml")] if path.name.endswith(".fcov.yaml") else path.stem
    if data.get("test") != stem:
        problems.append(f"test: {data.get('test')!r} must equal the file stem {stem!r}")
    if test_name and data.get("test") != test_name:
        problems.append(f"manifest test {data.get('test')!r} is not the testlist entry {test_name!r}")
    if data.get("owner") not in C.OWNER_ROLES:
        problems.append(f"owner {data.get('owner')!r} is not a role slug")
    bins = data.get("bins")
    if not isinstance(bins, list) or not bins:
        problems.append("bins: must be a non-empty list")
        bins = []
    seen: set[str] = set()
    for b in bins:
        if not isinstance(b, str) or not BIN_RE.match(b):
            problems.append(f"bin {b!r}: expected gen_<feature>_cg.<coverpoint>.<bin> (gen_ namespace)")
        elif b in seen:
            problems.append(f"bin {b!r} declared twice")
        seen.add(b if isinstance(b, str) else str(b))
    notes = data.get("anti_vacuity")
    if not isinstance(notes, dict):
        problems.append("anti_vacuity: must be a mapping bin -> note (one per declared bin)")
        notes = {}
    for b in bins:
        if isinstance(b, str) and not str(notes.get(b, "")).strip():
            problems.append(f"bin {b!r}: anti_vacuity note missing")
    for extra in set(notes) - set(bins):
        problems.append(f"anti_vacuity note for undeclared bin {extra!r}")
    unknown = set(data) - {"test", "owner", "bins", "anti_vacuity", "notes"}
    if unknown:
        problems.append(f"unknown keys {sorted(unknown)}")
    return data, problems


def run_checker(manifest: Path, vdb: Path | None, cm_name: str | None, log_path: Path,
                report_dir: Path | None = None) -> dict[str, Any]:
    """ci/check_fcov_expectations.py on one test slice; the per-bin lines are parsed, not judged."""
    argv = [sys.executable, str(C.FCOV_CHECKER), "--manifest", str(manifest)]
    if report_dir is not None:
        argv += ["--report-dir", str(report_dir)]
    else:
        argv += ["--vdb", str(vdb), "--cm-name", str(cm_name)]
    # The checker creates its urg work dir with tempfile.mkdtemp(prefix="fcovexp_"); TMPDIR points it
    # into the run dir so the per-test report is retained beside the run and never shares /tmp with
    # other workspaces' checker output (fence: a shared /tmp can expose foreign out-trees).
    log_path.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, TMPDIR=str(log_path.parent))
    r = subprocess.run(argv, capture_output=True, text=True, cwd=C.REPO_ROOT, env=env)
    log_path.write_text(" ".join(argv) + "\n" + r.stdout + r.stderr, encoding="utf-8")
    bins: dict[str, dict[str, Any]] = {}
    for line in r.stdout.splitlines():
        m = RESULT_LINE_RE.match(line)
        if m:
            bins[m.group(1)] = {"state": m.group(2), "count": m.group(3)}
    status = STATUS_BY_EXIT.get(r.returncode, "UNKNOWN")
    unmet = sorted(b for b, v in bins.items() if v["state"] != "HIT")
    return {"exit_code": r.returncode, "status": status, "log": str(log_path), "bins": bins,
            "unmet_bins": unmet, "declared": len(bins), "hit": sum(1 for v in bins.values() if v["state"] == "HIT"),
            "reason": None if status == "PASS" else
            (f"{REASON_UNMET}: {len(unmet)} declared bin(s) not hit {unmet[:5]}" if status == "UNHIT"
             else f"{REASON_UNVERIFIABLE}: checker exit {r.returncode} (see {log_path.name})")}


def check_test(test: dict[str, Any], vdb: Path, cm_name: str, run_dir: Path) -> dict[str, Any]:
    """Flow entry: schema validation, then the checker; anti-vacuity notes carried into the record."""
    mpath = manifest_path(test)
    if mpath is None:
        return {"status": "NO_MANIFEST", "exit_code": None, "log": None, "bins": {}, "unmet_bins": [],
                "declared": 0, "hit": 0, "reason": None, "manifest": None}
    data, problems = validate_manifest(mpath, test["name"])
    if problems:
        log = run_dir / "fcov_check.log"
        log.write_text("manifest schema violations:\n" + "\n".join(problems) + "\n", encoding="utf-8")
        return {"status": "PROTOCOL_ERROR", "exit_code": None, "log": str(log), "bins": {}, "unmet_bins": [],
                "declared": 0, "hit": 0, "manifest": str(mpath),
                "reason": f"{REASON_UNVERIFIABLE}: manifest schema violation ({problems[0]})"}
    res = run_checker(mpath, vdb, cm_name, run_dir / "fcov_check.log")
    res["manifest"] = str(mpath)
    res["anti_vacuity"] = {b: (data or {}).get("anti_vacuity", {}).get(b) for b in (data or {}).get("bins", [])}
    res["owner"] = (data or {}).get("owner")
    return res


def fabricate_report(dst: Path, cg: str, cp: str, hits: dict[str, int]) -> None:
    """A urg text report dir with the grpinfo.txt shape the checker parses (its docstring)."""
    lines = [f"Group : gen_tb_top.u_env.u_cov::{cg}", "", f"Summary for Variable {cp}", "",
             "Covered bins", "", "NAME COUNT AT_LEAST NUMBER"]
    lines += [f"{b} {n} 1 1" for b, n in hits.items() if n > 0]
    lines += ["", "Uncovered bins", "", "NAME COUNT AT_LEAST NUMBER"]
    lines += [f"{b} {n} 1 1" for b, n in hits.items() if n <= 0]
    lines += ["", "----------"]
    dst.mkdir(parents=True, exist_ok=True)
    (dst / "grpinfo.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def self_test() -> int:
    """Fabricate a manifest and a urg report dir; drive the REAL checker (--report-dir) and this
    module's parsing; the vdb slice selection (`urg -tests`) is not exercised here."""
    ok = True
    with tempfile.TemporaryDirectory(prefix="gen_fcov_selftest_") as td:
        d = Path(td)
        cg, cp = "gen_selftest_cg", "cp_mode"
        good = d / "gen_selftest_ok.fcov.yaml"
        good.write_text(f"test: gen_selftest_ok\nowner: runtime\nbins:\n  - {cg}.{cp}.bin_a\n  - {cg}.{cp}.bin_b\n"
                        f"anti_vacuity:\n  {cg}.{cp}.bin_a: sampled once per mode switch\n"
                        f"  {cg}.{cp}.bin_b: sampled once per mode switch\n", encoding="utf-8")
        _, problems = validate_manifest(good)
        ok &= not problems
        print("SELF-TEST", "ok " if not problems else "BAD", "schema accepts a well-formed manifest", problems)
        bad = d / "gen_selftest_bad.fcov.yaml"
        bad.write_text(f"test: other\nowner: nobody\nbins:\n  - notgen_cg.{cp}.bin_a\n  - {cg}.{cp}.bin_a\n"
                       f"anti_vacuity: {{}}\n", encoding="utf-8")
        _, problems = validate_manifest(bad)
        want = ["file stem", "role slug", "gen_ namespace", "anti_vacuity note missing"]
        got = all(any(w in p for p in problems) for w in want)
        ok &= got
        print("SELF-TEST", "ok " if got else "BAD", f"schema rejects stem/owner/namespace/note violations ({len(problems)} problems)")
        rep_hit = d / "report_hit"
        fabricate_report(rep_hit, cg, cp, {"bin_a": 3, "bin_b": 1})
        res = run_checker(good, None, None, d / "hit.log", report_dir=rep_hit)
        cond = res["status"] == "PASS" and res["hit"] == 2 and res["unmet_bins"] == []
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"checker PASS on all-hit fixture: {res['status']} hit={res['hit']}")
        rep_miss = d / "report_miss"
        fabricate_report(rep_miss, cg, cp, {"bin_a": 3, "bin_b": 0})
        res = run_checker(good, None, None, d / "miss.log", report_dir=rep_miss)
        cond = res["status"] == "UNHIT" and res["unmet_bins"] == [f"{cg}.{cp}.bin_b"] and res["reason"].startswith(REASON_UNMET)
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"checker UNHIT on one unhit bin: {res['status']} {res['unmet_bins']} reason={res['reason']}")
        rep_absent = d / "report_absent"
        fabricate_report(rep_absent, cg, cp, {"bin_a": 3})
        res = run_checker(good, None, None, d / "absent.log", report_dir=rep_absent)
        cond = res["status"] == "UNHIT" and res["bins"].get(f"{cg}.{cp}.bin_b", {}).get("state") == "MISSING-FROM-REPORT"
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"a declared bin absent from the report counts as unmet: {res['bins'].get(f'{cg}.{cp}.bin_b')}")
        res = run_checker(good, None, None, d / "noreport.log", report_dir=d / "does_not_exist")
        cond = res["status"] == "PROTOCOL_ERROR" and res["reason"].startswith(REASON_UNVERIFIABLE)
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"unverifiable query is not a pass: {res['status']}")
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--validate", nargs="*", type=Path, help="manifest file(s) to schema-check")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.validate is not None:
        files = a.validate or sorted(C.FCOV_EXPECT_DIR.glob("*.fcov.yaml"))
        rc = 0
        for f in files:
            _, problems = validate_manifest(f)
            print(f"{f}: {'OK' if not problems else 'FAIL'}")
            for p in problems:
                print("   ", p)
                rc = 1
        if not files:
            print(f"no manifest under {C.FCOV_EXPECT_DIR}")
        return rc
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
