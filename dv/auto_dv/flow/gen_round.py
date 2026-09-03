#!/usr/bin/env python3
"""Phase 1 gate and closure-round measurement procedure (DV_prompt Sections 4 and 5).

One round = one full measured regression (gen_regress.py --tier full --purpose 4: coverage with
cond, exclusion files loaded with -excl_strict, full-exclusions dump), its URG report copied into a
dated evidence directory dv/auto_dv/evidence/gen_round_<n>/, and the round index
dv/auto_dv/evidence/gen_rounds.yaml updated with the DUT-scope numbers, the gain against the
previous round (G = 0.5 points on any gated metric) and the no-gain streak against N = 5. A metric
URG does not report is recorded as n/a: it is neither gated nor part of the gain computation.

Usage:
    gen_round.py --round <n> [--elfile F ...] [--seeds N] [--base-seed S] [--tag T] [--force]
    gen_round.py --dry-run [--tag T]     # check tier, unmeasured; evidence dir gen_round_0_dryrun, not a round
    gen_round.py --collect <regress outdir> --round <n> [--dry-run]   # evidence + index from an existing regression
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Any

import gen_flow_const as C
import gen_flow_util as U
import gen_cov_report as R

GATED_CODE_METRICS = ("line", "cond", "toggle", "fsm", "branch", "assert")
WARNING_RE = re.compile(r"^(Warning|Error|Note)-\[([\w-]+)\]")


def run_regression(a: argparse.Namespace, tag: str) -> Path:
    outdir = C.OUT_DIR / f"regress_{tag}"
    argv = [sys.executable, str(C.FLOW_DIR / "gen_regress.py"), "--tag", tag, "--dump-exclusions"]
    if a.dry_run:
        argv += ["--tier", C.CHECK_TIER]
    else:
        argv += ["--tier", "full", "--purpose", "4", "--requester", a.requester]
    for e in a.elfile or []:
        argv += ["--elfile", str(e)]
    if a.seeds:
        argv += ["--seeds", str(a.seeds)]
    if a.base_seed is not None:
        argv += ["--base-seed", str(a.base_seed)]
    if a.force:
        argv.append("--force")
    U.log(f"round regression: {' '.join(argv[2:])}")
    rc, wall, timed_out = U.run_bounded(argv, cwd=C.REPO_ROOT, log_path=C.WORK_DIR / "round_regress_driver.log",
                                        timeout_s=a.timeout_s)
    U.log(f"gen_regress.py exit {rc} after {wall:.0f}s")
    if not (outdir / "manifest.yaml").is_file():
        U.die(f"no manifest under {outdir}; see {C.WORK_DIR / 'round_regress_driver.log'}")
    return outdir


def metric_row(cov: dict[str, Any]) -> dict[str, Any]:
    """DUT-scope row (code metrics from the DUT instance, group from the grand total), n/a kept."""
    totals = cov.get("totals") or {}
    scopes = cov.get("dut_scope") or {}
    row: dict[str, Any] = {}
    first = next(iter(scopes.values()), None) if scopes else None
    src = first if isinstance(first, dict) and "parse_error" not in first else totals
    for m in GATED_CODE_METRICS:
        row[m] = src.get(m, C.NOT_APPLICABLE)
    row["group"] = totals.get("group", C.NOT_APPLICABLE)
    ratios = dict((src.get("ratios") or {}))
    if (totals.get("ratios") or {}).get("group"):
        ratios["group"] = totals["ratios"]["group"]
    row["ratios"] = ratios
    return row


def gain_against(prev: dict[str, Any] | None, cur: dict[str, Any]) -> dict[str, Any]:
    """Per-metric delta in points, the max over gated metrics that both rounds report, and the
    verdict against G. n/a on either side excludes the metric from the computation."""
    deltas: dict[str, Any] = {}
    for m in C.URG_METRICS:
        c = cur.get(m)
        p = (prev or {}).get(m)
        deltas[m] = round(c - p, 2) if isinstance(c, float) and isinstance(p, float) else C.NOT_APPLICABLE
    numeric = [d for d in deltas.values() if isinstance(d, float)]
    max_gain = max(numeric) if numeric else None
    return {"deltas": deltas, "max_gain": max_gain,
            "shows_gain": (max_gain is not None and max_gain >= C.ROUND_GAIN_G) if prev else None,
            "G": C.ROUND_GAIN_G}


def gate_status(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for m in C.URG_METRICS:
        v = row.get(m)
        out[m] = "n/a (not reported by URG; excluded from the gate)" if not isinstance(v, float) else \
            ("PASS" if v >= C.GATE_PCT else "below gate")
    return out


def warning_counts(merge_log: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    if merge_log.is_file():
        for line in merge_log.read_text(encoding="utf-8", errors="replace").splitlines():
            m = WARNING_RE.match(line)
            if m:
                key = f"{m.group(1)}-[{m.group(2)}]"
                counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def dut_rows(hier: Path, scopes: list[str]) -> str:
    """Header plus the rows of the DUT scopes from hierarchy.txt."""
    if not hier.is_file():
        return "hierarchy.txt missing\n"
    lines = hier.read_text(encoding="utf-8", errors="replace").splitlines()
    leaves = {s.split(".")[-1] for s in scopes}
    out: list[str] = []
    header = ""
    for line in lines:
        toks = line.split()
        if toks and all(t in R.URG_COLUMN_ALIASES for t in toks):
            header = line
        elif toks and toks[-1] in leaves:
            out.append(header)
            out.append(line)
    return "\n".join(out) + "\n" if out else "no DUT row found\n"


def collect(outdir: Path, round_no: int, dry_run: bool, label: str | None) -> Path:
    man = U.load_yaml(outdir / "manifest.yaml")
    cov_all = man.get("coverage") or {}
    # A dry run on the check tier has no measured merge; its unmeasured merge is the source, labelled.
    cov = cov_all if cov_all.get("dashboard_txt") else (cov_all.get("unmeasured") or {})
    source = "measured merge" if cov_all.get("dashboard_txt") else "UNMEASURED merge (dry run / check tier)"
    name = f"{C.ROUND_DIR_PREFIX}{round_no}" + ("_dryrun" if dry_run else "")
    ev = C.EVIDENCE_DIR / name
    if ev.exists():
        U.die(f"{ev} exists; an evidence directory is never overwritten (pick another --round or --tag)")
    ev.mkdir(parents=True)
    report = Path(cov.get("report_dir") or "")
    copied: list[str] = []
    for f in ("dashboard.txt", "hierarchy.txt", "tests.txt", "groups.txt", "grpinfo.txt"):
        src = report / f
        if src.is_file():
            shutil.copyfile(src, ev / f)
            copied.append(f)
    scopes = [b.get("cov_scope") for b in (man.get("builds") or {}).values() if b.get("cov_scope")]
    for b in (man.get("builds") or {}).values():
        scopes += b.get("cov_scopes") or []
    scopes = sorted(set(scopes))
    (ev / "hierarchy_dut_rows.txt").write_text(dut_rows(report / "hierarchy.txt", scopes), encoding="utf-8")
    if not (report / "groups.txt").is_file():
        (ev / "groups_summary.txt").write_text("no covergroup in this merge: functional coverage n/a\n", encoding="utf-8")
    dump_dir = Path(cov.get("report_dir") or "").parent / C.URG_DUMP_DIRNAME
    dumped = []
    if dump_dir.is_dir():
        (ev / "full_exclusions").mkdir()
        for f in sorted(dump_dir.glob("fullexclude.*")):
            shutil.copyfile(f, ev / "full_exclusions" / f.name)
            dumped.append(f.name)
    merge_log = Path(cov.get("merge_log") or "")
    wc = warning_counts(merge_log)
    (ev / "merge_log_warnings.txt").write_text(
        "\n".join(f"{k}: {v}" for k, v in wc.items()) + ("\n" if wc else "no Warning/Error/Note lines\n"), encoding="utf-8")
    if merge_log.is_file():
        shutil.copyfile(merge_log, ev / "merge.log")
    for bname, b in (man.get("builds") or {}).items():
        bm = Path(b.get("manifest") or "")
        if bm.is_file():
            shutil.copyfile(bm, ev / f"build_manifest_{bname}.yaml")
    shutil.copyfile(C.TESTLIST_YAML, ev / "testlist_snapshot.yaml")
    shutil.copyfile(outdir / "manifest.yaml", ev / "regress_manifest.yaml")
    for e in cov.get("elfiles") or []:
        (ev / "elfiles").mkdir(exist_ok=True)
        shutil.copyfile(e, ev / "elfiles" / Path(e).name)
    row = metric_row(cov)
    index = U.load_yaml(C.ROUND_INDEX) if C.ROUND_INDEX.is_file() else {"G": C.ROUND_GAIN_G, "N": C.ROUND_NO_GAIN_N,
                                                                          "gate_pct": C.GATE_PCT, "rounds": [], "dry_runs": []}
    prev = index["rounds"][-1] if (index["rounds"] and not dry_run) else None
    gain = gain_against(prev["metrics"] if prev else None, row)
    streak = 0 if (prev is None or gain["shows_gain"]) else int(prev.get("no_gain_streak", 0)) + 1
    entry = {"round": round_no, "dry_run": dry_run, "label": label, "date_utc": U.now_utc(), "evidence_dir": str(ev),
             "regress_outdir": str(outdir), "regress_tag": man.get("tag"), "git_head": (man.get("git") or {}).get("head"),
             "build_config": man.get("build_config"), "source": source, "tests_in_report": (cov.get("totals") or {}).get("tests_in_report"),
             "runs": man.get("summary"), "metrics": row, "gate": gate_status(row), "gain": gain,
             "no_gain_streak": streak, "stopping_rule_fired": (streak >= C.ROUND_NO_GAIN_N) if not dry_run else None,
             "exclusion_files": cov.get("elfiles") or [], "excl_strict": cov.get("excl_strict"),
             "exclusion_violations": cov.get("exclusion_violations") or [], "merge_warnings": wc,
             "testlist_sha256": U.sha256_file(C.TESTLIST_YAML), "copied": copied, "full_exclusions_files": dumped}
    if dry_run:
        index.setdefault("dry_runs", []).append(entry)
    else:
        index["rounds"].append(entry)
    U.dump_yaml(index, C.ROUND_INDEX)
    (ev / "gen_round_summary.md").write_text(render_summary(entry, prev), encoding="utf-8")
    U.log(f"evidence written to {ev}; index {C.ROUND_INDEX}")
    return ev


def fmt(v: Any) -> str:
    return f"{v:.2f}" if isinstance(v, float) else str(v)


def render_summary(e: dict[str, Any], prev: dict[str, Any] | None) -> str:
    title = (f"Closure round {e['round']}: measured coverage evidence" if not e["dry_run"]
             else "DRY RUN of the round procedure (not a round): UNMEASURED coverage, check tier")
    L = [f"# {title} (generated by dv/auto_dv/flow/gen_round.py)", ""]
    if e["dry_run"]:
        L += ["**DRY RUN, UNMEASURED.** Source: the check tier (build/elaboration checks, `measured: false`), its",
              "unmeasured merge. These numbers are NOT a closure round, do not enter the round counter or the gain",
              "computation, and are listed under `dry_runs` in gen_rounds.yaml. The procedure, not the coverage, is",
              "what this directory proves.", ""]
    L += [f"Date (UTC): {e['date_utc']}. Build configuration: `{e['build_config']}`. Git HEAD: `{e['git_head']}`.",
          f"Regression: `{e['regress_outdir']}` (tag {e['regress_tag']}); source: {e['source']}; tests in report:",
          f"{e['tests_in_report']}; runs: {e['runs']}.", "",
          f"Exclusion files (loaded with -excl_strict={e['excl_strict']}): {e['exclusion_files'] or 'none'};",
          f"strict violations: {e['exclusion_violations'] or 'none'}. Testlist snapshot sha256 `{e['testlist_sha256']}`.", "",
          "## Metrics (DUT-scope row; n/a = URG did not report the metric: excluded from gate and gain)", "",
          "| Metric | Percent | covered/total | Gate (80) | Delta vs previous round |", "|---|---|---|---|---|"]
    for m in C.URG_METRICS:
        v = e["metrics"].get(m)
        ratio = (e["metrics"].get("ratios") or {}).get(m, "")
        L.append(f"| {m} | {fmt(v)} | {ratio} | {e['gate'][m]} | {fmt(e['gain']['deltas'][m])} |")
    L += ["", f"Gain rule: G = {C.ROUND_GAIN_G} points on any gated metric. Max delta: {fmt(e['gain']['max_gain'])}; "
          f"shows gain: {e['gain']['shows_gain']} (None when there is no previous round). No-gain streak: "
          f"{e['no_gain_streak']} of N = {C.ROUND_NO_GAIN_N}; stopping rule fired: {e['stopping_rule_fired']}.", "",
          "## Files in this directory", "",
          "- `dashboard.txt`, `hierarchy.txt`, `tests.txt` (URG text report), `hierarchy_dut_rows.txt` (the DUT-scope rows)",
          "- `groups.txt` / `grpinfo.txt` when covergroups exist, else `groups_summary.txt` stating n/a",
          "- `full_exclusions/fullexclude.<metric>` (URG -dump full_exclusions of this merge; the `_module` variants stay in the out-tree)",
          "- `merge.log` and `merge_log_warnings.txt` (counts per Warning/Error/Note class)",
          "- `build_manifest_<build>.yaml`, `testlist_snapshot.yaml`, `regress_manifest.yaml`, `elfiles/` (exclusion files used)", "",
          "## Merge log warning counts", ""] + [f"- {k}: {v}" for k, v in e["merge_warnings"].items()]
    if prev:
        L += ["", f"Previous round: {prev['round']} ({prev['date_utc']}, `{prev['evidence_dir']}`)."]
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--round", type=int, help="closure round number (0 = Phase 1 gate baseline)")
    ap.add_argument("--dry-run", action="store_true", help="check tier, unmeasured; evidence gen_round_<n>_dryrun")
    ap.add_argument("--collect", type=Path, help="existing regression outdir: only evidence + index")
    ap.add_argument("--elfile", type=Path, action="append", help="exclusion file(s) for the measured merge")
    ap.add_argument("--seeds", type=int)
    ap.add_argument("--base-seed", type=int)
    ap.add_argument("--tag", help="regression tag (default round_<n> or round_<n>_dryrun)")
    ap.add_argument("--label", help="free text for the index entry (e.g. 'Phase 1 gate')")
    ap.add_argument("--requester", default="dv-lead", help="role that requested the measurement")
    ap.add_argument("--timeout-s", type=int, default=6 * 3600)
    ap.add_argument("--force", action="store_true", help="replace an existing regression outdir (never an evidence dir)")
    a = ap.parse_args()
    if a.round is None:
        if a.dry_run:
            a.round = 0
        else:
            ap.error("--round is required")
    U.require_env("vcs", "urg", "bsub")
    U.require_sv_constants()
    if a.collect:
        outdir = a.collect.resolve()
    else:
        tag = a.tag or (f"round_{a.round}" + ("_dryrun" if a.dry_run else ""))
        outdir = run_regression(a, tag)
    ev = collect(outdir, a.round, a.dry_run, a.label)
    rc, _, _ = U.run_bounded([sys.executable, str(C.FLOW_DIR / "gen_dashboard.py")], cwd=C.REPO_ROOT,
                             log_path=C.WORK_DIR / "round_dashboard.log", timeout_s=600)
    U.log(f"dashboard regenerated (rc={rc}); evidence {ev}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
