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
    -show ratios a/b); percent = 100 * covered / total; a metric no row reports stays n/a.
    PRECONDITION: the scopes are disjoint subtrees (no scope is an ancestor of another); URG's
    hierarchy rows are cumulative over children, so nested scopes would double count. load_testlist
    refuses nested cov_trees; this function trusts that."""
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
    out["rule"] = ("sum of covered and of total objects per metric over the gated scopes (disjoint subtrees, never nested); "
                   "percent = 100 * covered / total")
    return out


def merge(cov_dir: Path, vdbs: list[Path], elfiles: list[Path] | None = None,
          extra: list[str] | None = None, dut_scopes: list[str] | None = None,
          dump_exclusions: bool = False, info_scopes: list[str] | None = None) -> dict[str, Any]:
    """SIM_RECIPE Section 8 merge. Exclusion files load with -excl_strict, so an entry
    that hides a covered or stale object makes the merge FAIL instead of silently dropping it."""
    cov_dir.mkdir(parents=True, exist_ok=True)
    report = cov_dir / C.URG_REPORT_DIRNAME
    banned = [x for x in (extra or []) if x in C.URG_EXCL_BANNED]
    if banned:
        U.die(f"urg options {banned} are banned by the exclusion policy: propagation and bypass are never added")
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
        # Witness ledger: excluded by name from the functional score (the combining rule of record) and reported
        # beside it; without groups.txt or without a ledger row the URG total stands.
        groups_txt, grpinfo_txt = report / "groups.txt", report / "grpinfo.txt"
        rows = parse_groups(groups_txt.read_text(encoding="utf-8", errors="replace")) if groups_txt.is_file() else []
        res["group_score"] = group_score_excluding(rows, C.LEDGER_COVERGROUPS)
        res["group_score"]["urg_total"] = res["totals"].get("group", C.NOT_APPLICABLE)
        res["group_quantities"] = group_quantities(rows, res["totals"], C.LEDGER_COVERGROUPS)
        res["ledger"] = ledger_summary(grpinfo_txt.read_text(encoding="utf-8", errors="replace"), C.LEDGER_COVERGROUPS) \
            if grpinfo_txt.is_file() else ledger_summary("", C.LEDGER_COVERGROUPS)
        # The plan says the ledger exists: a report with covergroups but no ledger row is a broken TB, not a pass.
        has_group_total = res["totals"].get("group") not in (None, C.NOT_APPLICABLE)
        if C.LEDGER_REQUIRED and has_group_total and not rows:
            res["status"] = status = "ledger_missing"
            res["ledger"]["error"] = f"URG reports a group score but {groups_txt.name} is absent or has no summary table, so the ledger cannot be told apart"
        elif C.LEDGER_REQUIRED and has_group_total and not res["group_score"]["ledger_excluded"]:
            res["status"] = status = "ledger_missing"
            res["ledger"]["error"] = f"no ledger covergroup {C.LEDGER_COVERGROUPS} among {len(rows)} covergroups"
        if dut_scopes and len(good) == len(dut_scopes):
            res["gate_row"] = combine_rows(good)
            # One selector, no fallback that depends on what the run contained: the percent and the
            # denominator that produced it always come from the same named quantity.
            cell = group_cell(res["group_quantities"])
            res["gate_row"]["group"] = cell.get("percent") if cell.get("percent") is not None else C.NOT_APPLICABLE
            if cell.get("ratio"):
                res["gate_row"]["ratios"]["group"] = cell["ratio"]
            res["gate_row"]["group_cell"] = cell
            res["gate_row"]["ledger"] = res["ledger"]["text"]
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


# URG suffixes an instance name with (x) when exclusions apply to it and (X) when they apply below it.
URG_EXCL_MARKERS = ("(x)", "(X)")


def parse_groups(text: str) -> list[dict[str, Any]]:
    """Per-covergroup rows of URG's groups.txt: the first table whose header carries SCORE, WEIGHT and NAME;
    a row is <score> <weight> <name> (score may be --). Instance paths are reduced to the covergroup name."""
    rows: list[dict[str, Any]] = []
    cols: list[str] = []
    for line in text.splitlines():
        toks = line.split()
        if cols and rows and (not toks or line.startswith("Summary for")):
            break   # the summary table ends at the first blank line or per-group block; those blocks are not rows
        if not toks:
            continue
        if not cols and "SCORE" in toks and "WEIGHT" in toks and "NAME" in toks:
            cols = toks
            continue
        if cols and len(toks) >= 3 and toks[-1] not in ("NAME",):
            try:
                score = None if toks[cols.index("SCORE")] == "--" else float(toks[cols.index("SCORE")])
                weight = int(toks[cols.index("WEIGHT")])
            except (ValueError, IndexError):
                continue
            def _int(col: str) -> int | None:
                try:
                    return int(toks[cols.index(col)])
                except (ValueError, IndexError):
                    return None
            rows.append({"name": toks[-1].split("::")[-1], "score": score, "weight": weight,
                         "covered": _int("COVERED"), "expected": _int("EXPECTED")})
    return rows


def group_score_excluding(rows: list[dict[str, Any]], excluded: tuple[str, ...]) -> dict[str, Any]:
    """URG's functional score is the weight-averaged covergroup score; recompute it without the excluded names
    (the combining rule of record for the witness ledger)."""
    def is_ledger(name: str) -> bool:
        return name in excluded   # by SV covergroup name only (an SV identifier cannot carry a plan id's dash)
    kept = [g for g in rows if not is_ledger(g["name"]) and g["score"] is not None and g["weight"] > 0]
    dropped = sorted({g["name"] for g in rows if is_ledger(g["name"])})
    wsum = sum(g["weight"] for g in kept)
    score = round(sum(g["score"] * g["weight"] for g in kept) / wsum, 2) if wsum else None
    return {"score": score, "covergroups_scored": len(kept), "ledger_excluded": dropped}


def group_quantities(rows: list[dict[str, Any]], totals: dict[str, Any], excluded: tuple[str, ...]) -> dict[str, Any]:
    """The three group quantities this flow can state, each under its own name, each carrying the
    denominator that produced it and a scope string in words. They are different measurements of one run
    and are never interchangeable; nothing here decides which one a gate should read.

    group_bins_gate   hit bins / declared bins over the covergroups in gate scope, the ledger out of BOTH
                      terms (scoping only the denominator passes a round whose ledger is unhit and is wrong
                      the moment a clause is witnessed)
    group_bins_all    hit bins / declared bins over every covergroup URG reports, ledger included
    group_score_weighted  URG's weight-averaged covergroup score with the ledger dropped: a percent with no
                      bin denominator of its own, so it is emitted without a ratio
    """
    scored = [g for g in rows if g["name"] not in excluded]
    dropped = sorted({g["name"] for g in rows if g["name"] in excluded})
    def _sum(items: list[dict[str, Any]], key: str) -> int | None:
        vals = [g[key] for g in items if g.get(key) is not None]
        return sum(vals) if len(vals) == len(items) and items else None
    hit_gate, dec_gate = _sum(scored, "covered"), _sum(scored, "expected")
    hit_all, dec_all = _sum(rows, "covered"), _sum(rows, "expected")
    weighted = group_score_excluding(rows, excluded)
    ledger_bins = [(g.get("covered"), g.get("expected")) for g in rows if g["name"] in excluded]
    return {
        "group_bins_gate": {
            "percent": round(100.0 * hit_gate / dec_gate, 2) if dec_gate else None,
            "hit": hit_gate, "declared": dec_gate,
            "ratio": f"{hit_gate}/{dec_gate}" if dec_gate else None,
            "covergroups": len(scored), "excluded_covergroups": dropped,
            "excluded_bins": ledger_bins,
            "scope": C.GROUP_SCOPE_GATE.format(excluded=", ".join(dropped) or "none")},
        "group_bins_all": {
            "percent": round(100.0 * hit_all / dec_all, 2) if dec_all else None,
            "hit": hit_all, "declared": dec_all,
            "ratio": f"{hit_all}/{dec_all}" if dec_all else None,
            "covergroups": len(rows), "scope": C.GROUP_SCOPE_ALL},
        "group_score_weighted": {
            "percent": weighted["score"], "ratio": None,
            "covergroups": weighted["covergroups_scored"],
            "excluded_covergroups": weighted["ledger_excluded"],
            "scope": C.GROUP_SCOPE_WEIGHTED},
        "urg_report_total": {"percent": totals.get("group"),
                             "ratio": (totals.get("ratios") or {}).get("group"),
                             "scope": C.GROUP_SCOPE_URG_TOTAL},
    }


def group_cell(quantities: dict[str, Any], field: str = None) -> dict[str, Any]:
    """THE ONE SELECTOR. Every consumer that prints a group cell reads it through here, so the flow states
    one quantity in one place instead of three modules each choosing. Which field it names is a question
    for the criterion ruling, not for this code: the ruling is suspended (LOG-097 addenda 3 and 4), so the
    default is recorded as the open question it is and changing it is a one-token change here."""
    name = field or C.GROUP_CELL_FIELD
    q = dict(quantities.get(name) or {})
    q["field"] = name
    q["selector_note"] = C.GROUP_CELL_SELECTOR_NOTE
    return q


def ledger_summary(grpinfo_text: str, ledger: tuple[str, ...]) -> dict[str, Any]:
    """witnessed clauses: N of M, from the ledger covergroups' bins in grpinfo.txt (the structure the fcov checker
    parses: `Group : <path>::<cg>`, `Summary for Variable <cp>`, Covered/Uncovered bins tables)."""
    hit = total = 0
    in_ledger = False
    section = None
    for line in grpinfo_text.splitlines():
        g = re.match(r"^Group : \S*::(\S+)$", line)
        if g:
            in_ledger = g.group(1) in ledger
            section = None
            continue
        if not in_ledger:
            continue
        if re.match(r"^(Uncovered bins|Covered bins)$", line):
            section = line
            continue
        if re.match(r"^(Excluded/Illegal bins|Summary for|Variables for|-{10,}|={10,})", line):
            section = None
            continue
        b = re.match(r"^([A-Za-z_][\w\[\]>=\-:.]*)\s+(\d+)\s+\d+", line)
        if b and section:
            total += 1
            hit += 1 if int(b.group(2)) > 0 else 0
    ids = C.LEDGER_PLAN_ID
    return {"covergroups": list(ledger), "plan_id": C.LEDGER_PLAN_ID, "witnessed": hit, "clauses": total,
            "text": f"witnessed clauses: {hit} of {total} ({ids})" if total else f"witnessed clauses: none in report ({ids})"}


def parse_hierarchy_rows(text: str, scope: str) -> dict[str, Any]:
    """Row of the instance <scope> (matched on its leaf name, exclusion marker stripped) in hierarchy text."""
    leaf = scope.split(".")[-1]
    cols: list[str] = []
    for line in text.splitlines():
        toks = line.split()
        if not toks:
            continue
        if all(t in URG_COLUMN_ALIASES for t in toks):
            cols = toks
            continue
        name, marker = toks[-1], None
        for m in URG_EXCL_MARKERS:
            if name.endswith(m):
                name, marker = name[:-len(m)], m
        if cols and name == leaf:
            out = _parse_row(cols, toks[:-1])
            out["instance"] = scope
            out["excl_marker"] = marker
            return out
    return {"parse_error": f"instance {scope} (leaf {leaf}) not found"}


def parse_hierarchy_row(hier: Path, scope: str) -> dict[str, Any]:
    if not hier.is_file():
        return {"parse_error": f"{hier} missing"}
    out = parse_hierarchy_rows(hier.read_text(encoding="utf-8", errors="replace"), scope)
    if "parse_error" in out:
        out["parse_error"] += f" in {hier}"
    return out


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


# Real hierarchy.txt excerpts (regress_req_runtime-004, 2026-09-03 08:50Z): the same instance row without and
# with an exclusion file loaded; URG appends (x) to an instance that carries exclusions.
REAL_HIER_PLAIN = """    SCORE   LINE              COND              TOGGLE             FSM          BRANCH           ASSERT
     31.97   37.81 1596/4221   26.62 2504/9407    6.92 1678/24236    6.98 6/86   31.43 726/2310   82.08 142/173  u_ibex_core
"""
REAL_HIER_EXCL_TOP = """SCORE   LINE              COND              TOGGLE             FSM          BRANCH           ASSERT
 33.71   41.75 1694/4057   27.62 2547/9220    8.66 1994/23016    8.11 6/74   34.40 798/2320   81.71 143/175  gen_smoke_tb_top(X)
"""
REAL_HIER_EXCL = """    SCORE   LINE              COND              TOGGLE             FSM          BRANCH           ASSERT
     33.25   40.64 1596/3927   27.63 2504/9061    8.24 1678/20364    8.11 6/74   32.82 726/2212   82.08 142/173  u_ibex_core(x)
"""


def self_test() -> int:
    ok = True
    plain = parse_hierarchy_rows(REAL_HIER_PLAIN, "gen_smoke_tb_top.u_dut.u_ibex_core")
    excl = parse_hierarchy_rows(REAL_HIER_EXCL, "gen_smoke_tb_top.u_dut.u_ibex_core")
    for name, row, want_line, want_marker in (("real row without exclusions", plain, "1596/4221", None),
                                              ("real row with exclusions, (x) marker", excl, "1596/3927", "(x)")):
        cond = "parse_error" not in row and row["ratios"]["line"] == want_line and row.get("excl_marker") == want_marker
        ok &= cond
        print(f"SELF-TEST {'ok ' if cond else 'BAD'} {name}: {row.get('parse_error') or row['ratios']['line']} marker={row.get('excl_marker')}")
    top = parse_hierarchy_rows(REAL_HIER_EXCL_TOP, "gen_smoke_tb_top")
    cond = "parse_error" not in top and top["ratios"]["toggle"] == "1994/23016" and top.get("excl_marker") == "(X)"
    ok &= cond
    print(f"SELF-TEST {'ok ' if cond else 'BAD'} real top row with exclusions below, (X) marker: {top.get('parse_error') or top['ratios']['toggle']} marker={top.get('excl_marker')}")
    miss = parse_hierarchy_rows(REAL_HIER_EXCL, "gen_smoke_tb_top.u_dut.u_register_file")
    cond = "parse_error" in miss
    ok &= cond
    print(f"SELF-TEST {'ok ' if cond else 'BAD'} an absent instance is a parse_error, never a silent row")
    comb = combine_rows([plain, excl])
    cond = comb["ratios"]["line"] == "3192/8148"
    ok &= cond
    print(f"SELF-TEST {'ok ' if cond else 'BAD'} combine_rows sums covered/total: {comb['ratios']['line']}")
    # Witness ledger exclusion (ruling 2026-09-03): fabricated groups.txt rows until a covergroup exists on this site.
    plain_rows = parse_groups("Total groups coverage summary\nSCORE   WEIGHT  NAME\n 40.00       1  gen_regime_cg\n 60.00       1  gen_irq_cg\n")
    ledger_rows = parse_groups("Total groups coverage summary\nSCORE   WEIGHT  NAME\n 40.00       1  gen_regime_cg\n 60.00       1  gen_irq_cg\n"
                              "  5.00       1  gen_tb_top.u_env.u_cov::gen_wit_cycle_clause_cg\n")
    a, b = group_score_excluding(plain_rows, C.LEDGER_COVERGROUPS), group_score_excluding(ledger_rows, C.LEDGER_COVERGROUPS)
    cond = a["score"] == b["score"] == 50.0 and b["ledger_excluded"] == ["gen_wit_cycle_clause_cg"] and a["ledger_excluded"] == []
    ok &= cond
    print(f"SELF-TEST {'ok ' if cond else 'BAD'} fabricated groups.txt: the score with the ledger group present equals the score without it ({a['score']} vs {b['score']}), ledger excluded by name")
    # The per-group blocks that follow URG's summary table must not be ingested as rows (fabricated block shape:
    # score-like lines after a "Summary for Group" header; the real block format is not covered here).
    blocks = ("Total groups coverage summary\nSCORE   WEIGHT  NAME\n 40.00       1  gen_regime_cg\n 60.00       1  gen_irq_cg\n\n"
              "Summary for Group gen_regime_cg\n 12.50       1  cp_regime\n 87.50       1  cp_other\n")
    rows_b = parse_groups(blocks)
    cond = [g["name"] for g in rows_b] == ["gen_regime_cg", "gen_irq_cg"]
    ok &= cond
    print(f"SELF-TEST {'ok ' if cond else 'BAD'} fabricated groups.txt: only the summary table is parsed, per-group blocks are ignored ({[g['name'] for g in rows_b]})")
    name_rows = parse_groups("SCORE   WEIGHT  NAME\n 40.00       1  gen_regime_cg\n  5.00       1  gen_wit_cycle_clause_cg\n  7.00       1  gen_wit_lookalike_cg\n")
    gs = group_score_excluding(name_rows, C.LEDGER_COVERGROUPS)
    cond = gs["ledger_excluded"] == ["gen_wit_cycle_clause_cg"] and gs["covergroups_scored"] == 2
    ok &= cond
    print(f"SELF-TEST {'ok ' if cond else 'BAD'} the ledger is matched by its SV covergroup name only; a look-alike name stays in the score ({gs})")
    grp = ("Group : gen_tb_top.u_env.u_cov::gen_wit_cycle_clause_cg\n\nSummary for Variable cp_clause\n\nCovered bins\n\nNAME COUNT AT_LEAST NUMBER\n"
           "w_tp_bit_036 3 1 1\nw_tp_bit_042 1 1 1\n\nUncovered bins\n\nNAME COUNT AT_LEAST NUMBER\nw_tp_bit_043 0 1 1\n\n----------\n"
           "Group : gen_tb_top.u_env.u_cov::gen_regime_cg\n\nSummary for Variable cp_regime\n\nCovered bins\n\nNAME COUNT AT_LEAST NUMBER\nbin_fast 9 1 1\n")
    led = ledger_summary(grp, C.LEDGER_COVERGROUPS)
    cond = led["witnessed"] == 2 and led["clauses"] == 3 and led["text"] == "witnessed clauses: 2 of 3 (CG-WIT-001)"
    ok &= cond
    print(f"SELF-TEST {'ok ' if cond else 'BAD'} fabricated grpinfo.txt: ledger bins counted only from the ledger covergroup: {led['text']}")
    # The three group quantities and the one selector.
    rows39 = [{"name": "gen_a_cg", "score": 50.0, "weight": 1, "covered": 5, "expected": 10},
              {"name": "gen_b_cg", "score": 100.0, "weight": 1, "covered": 10, "expected": 10},
              {"name": C.LEDGER_COVERGROUPS[0], "score": 0.0, "weight": 1, "covered": 0, "expected": 80}]
    tot39 = {"group": 15.0, "ratios": {"group": "15/100"}}
    q = group_quantities(rows39, tot39, C.LEDGER_COVERGROUPS)
    cond = q["group_bins_gate"]["ratio"] == "15/20" and q["group_bins_gate"]["percent"] == 75.0
    ok &= cond
    print(f"SELF-TEST {'ok ' if cond else 'BAD'} group_bins_gate takes the ledger out of BOTH terms: {q['group_bins_gate']['ratio']}")
    cond = q["group_bins_all"]["ratio"] == "15/100" and q["group_bins_all"]["percent"] == 15.0
    ok &= cond
    print(f"SELF-TEST {'ok ' if cond else 'BAD'} group_bins_all keeps the ledger in both terms: {q['group_bins_all']['ratio']}")
    cond = q["group_score_weighted"]["ratio"] is None and q["group_score_weighted"]["percent"] == 75.0
    ok &= cond
    print(f"SELF-TEST {'ok ' if cond else 'BAD'} group_score_weighted carries NO ratio: a percent over covergroups has no bin denominator")
    witnessed = [dict(g) for g in rows39]
    witnessed[-1]["covered"] = 7
    qw = group_quantities(witnessed, tot39, C.LEDGER_COVERGROUPS)
    denom_only = f"{sum(g['covered'] for g in witnessed)}/{qw['group_bins_gate']['declared']}"
    cond = qw["group_bins_gate"]["ratio"] == "15/20" and denom_only == "22/20"
    ok &= cond
    print(f"SELF-TEST {'ok ' if cond else 'BAD'} a WITNESSED ledger leaves the gate figure at "
          f"{qw['group_bins_gate']['ratio']}, where scoping only the denominator would give {denom_only}")
    cell = group_cell(q)
    cond = (cell["field"] == C.GROUP_CELL_FIELD and cell["percent"] == q[C.GROUP_CELL_FIELD]["percent"]
            and cell["ratio"] == q[C.GROUP_CELL_FIELD]["ratio"] and cell["scope"] == q[C.GROUP_CELL_FIELD]["scope"])
    ok &= cond
    print(f"SELF-TEST {'ok ' if cond else 'BAD'} group_cell pairs one percent with its own ratio and scope: "
          f"{cell['field']} {cell['percent']} ({cell['ratio']})")
    cond = group_cell(q, "group_score_weighted")["field"] == "group_score_weighted"
    ok &= cond
    print(f"SELF-TEST {'ok ' if cond else 'BAD'} the selector names its field, so another quantity is one token away")
    rec39 = C.EVIDENCE_DIR / "gen_round_0" / "gen_groups.txt"
    if rec39.is_file():
        real = group_quantities(parse_groups(rec39.read_text(encoding="utf-8", errors="replace")),
                                {"group": 81.47, "ratios": {"group": "3477/4268"}}, C.LEDGER_COVERGROUPS)
        cond = (real["group_bins_gate"]["ratio"] == "3477/4048" and real["group_bins_gate"]["percent"] == 85.89
                and real["group_bins_all"]["ratio"] == "3477/4268" and real["group_bins_all"]["percent"] == 81.47
                and real["group_score_weighted"]["percent"] == 78.29)
        ok &= cond
        print(f"SELF-TEST {'ok ' if cond else 'BAD'} COMMITTED round-0 report: gate "
              f"{real['group_bins_gate']['percent']} ({real['group_bins_gate']['ratio']}), all "
              f"{real['group_bins_all']['percent']} ({real['group_bins_all']['ratio']}), weighted "
              f"{real['group_score_weighted']['percent']}")
    else:
        print("SELF-TEST ok  committed round-0 group report absent here: control skipped, stated not silent")
    print("SELF-TEST: rows named 'real ...' are verbatim hierarchy.txt excerpts of regress_req_runtime-004; the ledger cases are fabricated until a covergroup exists")
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 2


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
    sub.add_parser("self-test", help="hierarchy row parsing on real URG excerpts (with and without exclusion markers)")
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
    if a.cmd == "self-test":
        return self_test()
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
