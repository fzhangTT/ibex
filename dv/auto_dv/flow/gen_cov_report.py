#!/usr/bin/env python3
"""Coverage merge and URG reporting (docs/dv/SIM_RECIPE.md Section 8) plus the deterministic
reader of the text report: the per-metric DUT-scope totals are the numbers (DV_prompt Section
4); a metric URG does not report is recorded as n/a, never 0 or 100.

Two rows are read: the grand total of report/dashboard.txt and the row of the DUT instance
(<tb_top>.<dut_instance>) in report/hierarchy.txt. They differ only where objects outside the
-cm_hier scope exist (assertions of uvm_pkg); the DUT row is the gate number.

Usage:
    gen_cov_report.py merge --cov-dir DIR --vdb A.vdb [--vdb B.vdb ...] [--elfile F ...]
                            [--dut-scope gen_smoke_tb_top.u_dut ...] [--dump-exclusions]
    gen_cov_report.py parse --report-dir DIR [--dut-scope SCOPE]
    gen_cov_report.py unreachable --report-dir DIR --module ibex_cheriot_ex
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import gen_flow_const as C
import gen_flow_util as U

URG_COLUMN_ALIASES = {"LINE": "line", "COND": "cond", "TOGGLE": "toggle", "FSM": "fsm",
                      "BRANCH": "branch", "ASSERT": "assert", "GROUP": "group", "SCORE": "score"}
RATIO_RE = re.compile(r"^\d+/\d+$")


def combine_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """The gate row over several DUT scopes (DV Lead ruling, gen_tb_architecture.md Section 5): per
    metric, covered and total objects are summed over the rows that report the metric (from URG's
    -show ratios a/b); percent = 100 * covered / total; a metric no row reports stays n/a."""
    out: dict[str, Any] = {m: C.NOT_APPLICABLE for m in C.URG_METRICS}
    out["score"] = C.NOT_APPLICABLE
    ratios: dict[str, str] = {}
    for m in C.URG_METRICS:
        cov_sum = tot_sum = 0
        seen = False
        for r in rows:
            ratio = (r.get("ratios") or {}).get(m)
            if ratio and RATIO_RE.match(ratio):
                a, b = ratio.split("/")
                cov_sum += int(a)
                tot_sum += int(b)
                seen = True
        if seen and tot_sum > 0:
            out[m] = round(100.0 * cov_sum / tot_sum, 2)
            ratios[m] = f"{cov_sum}/{tot_sum}"
    out["ratios"] = ratios
    out["combined_from"] = [r.get("instance") for r in rows]
    out["rule"] = "sum of covered and of total objects per metric over the gated scopes; percent = 100 * covered / total"
    return out


def merge(cov_dir: Path, vdbs: list[Path], elfiles: list[Path] | None = None,
          extra: list[str] | None = None, dut_scopes: list[str] | None = None,
          dump_exclusions: bool = False, info_scopes: list[str] | None = None) -> dict[str, Any]:
    """SIM_RECIPE Section 8 merge. Exclusion files load with -excl_strict (Critic R-5.1): an entry
    that hides a covered or stale object makes the merge FAIL instead of silently dropping it."""
    cov_dir.mkdir(parents=True, exist_ok=True)
    report = cov_dir / C.URG_REPORT_DIRNAME
    banned = [x for x in (extra or []) if x in C.URG_EXCL_BANNED]
    if banned:
        U.die(f"urg options {banned} are banned by the exclusion policy (R-5.2)")
    argv = ["urg", "-full64", "-format", "both", "-dbname", str(cov_dir / C.MERGED_VDB_NAME),
            "-report", str(report), "-log", str(cov_dir / C.URG_MERGE_LOG), "-show", "ratios"]
    for v in vdbs:
        if not v.is_dir():
            U.die(f"vdb missing: {v}")
        argv += ["-dir", str(v)]
    for e in elfiles or []:
        if not e.is_file():
            U.die(f"exclusion file missing: {e}")
        argv += ["-elfile", str(e)]
    if elfiles:
        argv += list(C.URG_EXCL_STRICT)
    if dump_exclusions:
        argv += list(C.URG_DUMP_EXCLUSIONS)
    argv += list(extra or [])
    (cov_dir / "urg_cmd.sh").write_text("#!/usr/bin/env bash\ncd " + str(cov_dir) + "\n" + " ".join(argv) + "\n",
                                        encoding="utf-8")
    rc, wall, timed_out = U.run_bounded(argv, cwd=cov_dir, log_path=cov_dir / "urg_stdout.log", timeout_s=3600)
    dash = report / C.URG_DASHBOARD_TXT
    log_text = (cov_dir / C.URG_MERGE_LOG).read_text(encoding="utf-8", errors="replace") \
        if (cov_dir / C.URG_MERGE_LOG).is_file() else ""
    violations = [l.strip() for l in log_text.splitlines() if C.URG_EXCL_VIOLATION_RE.search(l)]
    dump_dir = cov_dir / C.URG_DUMP_DIRNAME
    dumped: list[str] = []
    if dump_exclusions:
        dump_dir.mkdir(exist_ok=True)
        for f in sorted(cov_dir.glob(C.URG_DUMP_GLOB)):
            f.replace(dump_dir / f.name)
            dumped.append(str(dump_dir / f.name))
    status = "ok"
    if rc != 0 or timed_out or not dash.is_file():
        status = "urg_failed"
    elif violations:
        status = "exclusion_violation"
    res: dict[str, Any] = {"status": status, "merged_vdb": str(cov_dir / C.MERGED_VDB_NAME),
                           "report_dir": str(report), "dashboard_txt": str(dash) if dash.is_file() else None,
                           "merge_log": str(cov_dir / C.URG_MERGE_LOG), "urg_rc": rc,
                           "urg_wall_s": round(wall, 1), "urg_timed_out": timed_out, "urg_cmd": " ".join(argv),
                           "input_vdbs": [str(v) for v in vdbs], "elfiles": [str(e) for e in (elfiles or [])],
                           "excl_strict": bool(elfiles), "exclusion_violations": violations,
                           "full_exclusions_dump": dumped, "totals": {}, "dut_scope": {}}
    if dash.is_file():
        res["totals"] = parse_dashboard(dash)
        res["dut_scope"] = {s: parse_hierarchy_row(report / "hierarchy.txt", s) for s in (dut_scopes or [])}
        res["info_scope"] = {s: parse_hierarchy_row(report / "hierarchy.txt", s) for s in (info_scopes or [])}
        good = [r for r in res["dut_scope"].values() if isinstance(r, dict) and "parse_error" not in r]
        if dut_scopes and len(good) == len(dut_scopes):
            res["gate_row"] = combine_rows(good)
            res["gate_row"]["group"] = res["totals"].get("group", C.NOT_APPLICABLE)
            if (res["totals"].get("ratios") or {}).get("group"):
                res["gate_row"]["ratios"]["group"] = res["totals"]["ratios"]["group"]
        else:
            res["gate_row"] = {"parse_error": f"{len(dut_scopes or [])} gated scope(s), {len(good)} parsed"}
        res["limited_design"] = "Limited design loaded" in log_text
    return res


def _parse_row(cols: list[str], toks: list[str]) -> dict[str, Any]:
    """Map a URG table row (percent, optional a/b ratio per column) onto metric keys."""
    out: dict[str, Any] = {m: C.NOT_APPLICABLE for m in C.URG_METRICS}
    out["score"] = C.NOT_APPLICABLE
    ratios: dict[str, str] = {}
    i = 0
    for col in cols:
        if i >= len(toks):
            break
        key = URG_COLUMN_ALIASES[col]
        tok = toks[i]
        i += 1
        if tok in ("--", "-"):
            if i < len(toks) and toks[i] in ("--", "-"):
                i += 1
            continue
        try:
            out[key] = float(tok)
        except ValueError:
            out["parse_error"] = f"unexpected token {tok!r} for {col}"
            return out
        if i < len(toks) and RATIO_RE.match(toks[i]):
            ratios[key] = toks[i]
            i += 1
    out["ratios"] = ratios
    return out


def parse_dashboard(dash: Path) -> dict[str, Any]:
    """Grand totals from the 'Total Coverage Summary' table of dashboard.txt."""
    lines = dash.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("Total Coverage Summary"):
            cols: list[str] = []
            for nxt in lines[i + 1:]:
                toks = nxt.split()
                if not toks:
                    if cols:
                        break
                    continue
                if not cols:
                    if all(t in URG_COLUMN_ALIASES for t in toks):
                        cols = toks
                        continue
                    return {"parse_error": f"unexpected header {toks}"}
                out = _parse_row(cols, toks)
                m = re.search(r"Number of tests:\s*(\d+)", "\n".join(lines))
                if m:
                    out["tests_in_report"] = int(m.group(1))
                out["columns_reported"] = [URG_COLUMN_ALIASES[c] for c in cols if c != "SCORE"]
                return out
    return {"parse_error": "no 'Total Coverage Summary' section"}


def parse_hierarchy_row(hier: Path, scope: str) -> dict[str, Any]:
    """Row of the instance <scope> (matched on its leaf name) in hierarchy.txt."""
    leaf = scope.split(".")[-1]
    if not hier.is_file():
        return {"parse_error": f"{hier} missing"}
    cols: list[str] = []
    for line in hier.read_text(encoding="utf-8", errors="replace").splitlines():
        toks = line.split()
        if not toks:
            continue
        if all(t in URG_COLUMN_ALIASES for t in toks):
            cols = toks
            continue
        if cols and toks[-1] == leaf:
            out = _parse_row(cols, toks[:-1])
            out["instance"] = scope
            return out
    return {"parse_error": f"instance {scope} (leaf {leaf}) not found in {hier}"}


def module_section(report_dir: Path, module: str) -> str:
    """The 'Module : <module>' section of modinfo.txt."""
    text = (report_dir / "modinfo.txt").read_text(encoding="utf-8", errors="replace")
    m = re.search(rf"^Module : {re.escape(module)}\s*$", text, re.M)
    if not m:
        return ""
    rest = text[m.end():]
    n = re.search(r"^Module : ", rest, re.M)
    return rest[: n.start()] if n else rest


def unreachable_summary(report_dir: Path, module: str) -> dict[str, Any]:
    """Counts of URG 'Unreachable' marks (constant analysis) inside one module's report section."""
    sec = module_section(report_dir, module)
    if not sec:
        return {"module": module, "found": False}
    head = sec.splitlines()[1:4]
    line_unreach = len(re.findall(r"^\s*\d+\s+unreachable\s", sec, re.M))
    cond_unreach = len(re.findall(r"^\s*[01 ]+Unreachable\s*$", sec, re.M))
    tgl_unreach = len(re.findall(r"^\S+\s+Unreachable", sec, re.M))
    return {"module": module, "found": True, "score_rows": [h.strip() for h in head if h.strip()],
            "unreachable_marks_total": len(re.findall(r"nreachable", sec)),
            "line_rows_unreachable": line_unreach, "cond_vectors_unreachable": cond_unreach,
            "toggle_rows_unreachable": tgl_unreach}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("merge")
    m.add_argument("--cov-dir", type=Path, required=True)
    m.add_argument("--vdb", type=Path, action="append", required=True)
    m.add_argument("--elfile", type=Path, action="append")
    m.add_argument("--dut-scope", action="append", default=[], help="gated scope (repeat; rows are combined)")
    m.add_argument("--info-scope", action="append", default=[], help="informational scope (reported, never gated)")
    m.add_argument("--urg-arg", action="append", default=[])
    m.add_argument("--dump-exclusions", action="store_true", help="urg -dump full_exclusions into <cov-dir>/full_exclusions")
    p = sub.add_parser("parse")
    p.add_argument("--report-dir", type=Path, required=True)
    p.add_argument("--dut-scope", action="append", default=[])
    u = sub.add_parser("unreachable")
    u.add_argument("--report-dir", type=Path, required=True)
    u.add_argument("--module", required=True)
    a = ap.parse_args()
    if a.cmd == "merge":
        U.require_env("urg")
        res = merge(a.cov_dir.resolve(), [v.resolve() for v in a.vdb], a.elfile, a.urg_arg, a.dut_scope,
                    a.dump_exclusions, a.info_scope)
        U.dump_yaml(res, a.cov_dir.resolve() / "coverage.yaml")
        print(f"status={res['status']} urg rc={res['urg_rc']} violations={len(res['exclusion_violations'])} "
              f"totals={res['totals']} dut_scope={res['dut_scope']} gate_row={res.get('gate_row')}")
        return 0 if res["status"] == "ok" else 1
    if a.cmd == "parse":
        print("totals:", parse_dashboard(a.report_dir / C.URG_DASHBOARD_TXT))
        for s in a.dut_scope:
            print(f"dut_scope {s}:", parse_hierarchy_row(a.report_dir / "hierarchy.txt", s))
        return 0
    for k, v in unreachable_summary(a.report_dir, a.module).items():
        print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
