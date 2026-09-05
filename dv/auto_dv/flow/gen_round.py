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
    gen_round.py --dry-run [--tag T] [--tests a,b --seed-list s] [--evidence-name gen_round_0_rebaseline]
                                         # check tier (or the named tests), unmeasured; not a round
    gen_round.py --collect <regress outdir> --round <n> [--dry-run]   # evidence + index from an existing regression
"""

from __future__ import annotations

import argparse
import gzip
import subprocess
import re
import shutil
import sys
from pathlib import Path
from typing import Any

import gen_flow_const as C
import gen_flow_util as U
import gen_cov_report as R
import gen_mirror as M

# Gated code metrics = every URG metric but functional coverage (group), which DV_prompt Section 4
# gates by two conditions (bins >= 80 AND traceability) and which never enters the gain rule.
GATED_CODE_METRICS = tuple(m for m in C.URG_METRICS if m != "group")
WARNING_RE = re.compile(r"^(Warning|Error|Note)-\[([\w-]+)\]")


def run_regression(a: argparse.Namespace, tag: str) -> Path:
    outdir = C.OUT_DIR / f"regress_{tag}"
    argv = [sys.executable, str(C.FLOW_DIR / "gen_regress.py"), "--tag", tag, "--dump-exclusions"]
    if a.tests:
        argv += ["--tests", a.tests]
    elif a.dry_run:
        argv += ["--tier", C.CHECK_TIER]
    else:
        argv += ["--tier", "full", "--purpose", "4", "--requester", a.requester, "--source", C.SOURCE_MODE_HEAD,
                 "--head-sha", a.pinned_sha, "--canary-build", str(a.canary_build)]
    if a.seed_list:
        argv += ["--seed-list", a.seed_list]
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
    # gen_regress.py: 0 clean; 2 a run FAILed, TIMED OUT or was NOT_RUN; 3 merge failure or strict
    # exclusion violation. A round is a measurement of a passing regression: anything else is refused.
    if rc != 0 or timed_out:
        U.die(f"gen_regress.py exit {rc} (timed_out={timed_out}): the regression is not clean, the round is not "
              f"indexed; fix and rerun (manifest {outdir / 'manifest.yaml'})")
    return outdir


def regression_verdict(man: dict[str, Any]) -> dict[str, Any]:
    """What gen_regress.py would have exited with, recomputed from the manifest (for --collect)."""
    s = man.get("summary") or {}
    cov = man.get("coverage")
    bad_runs = int(s.get("fail", 0)) + int(s.get("timeout", 0)) + int(s.get("not_run", 0))
    if not isinstance(cov, dict):
        # No coverage block at all (regression without coverage, or interrupted): nothing to measure.
        return {"verdict": "unknown", "status": man.get("status"), "bad_runs": bad_runs, "coverage_status": None,
                "exclusion_violations": []}
    cov_ok = cov.get("status") in ("ok", "ok_no_measured_tests")
    verdict = "clean" if (bad_runs == 0 and cov_ok and man.get("status") == "done") else "not clean"
    return {"verdict": verdict, "status": man.get("status"), "bad_runs": bad_runs, "coverage_status": cov.get("status"),
            "exclusion_violations": cov.get("exclusion_violations") or []}


def metric_row(cov: dict[str, Any]) -> dict[str, Any]:
    """The gate row: the gated DUT scopes combined per metric (DV Lead ruling, gen_tb_architecture.md
    Section 5: u_dut.u_ibex_core + u_dut.u_register_file, covered and total objects summed), group from
    gen_cov_report.group_cell, the one selector, so the percent and its denominator always come from the
    same named quantity; n/a kept. Never the grand total for code metrics: a missing or unparsed gate row
    is a hard error naming what is missing."""
    totals = cov.get("totals") or {}
    gate = cov.get("gate_row")
    scopes = cov.get("dut_scope") or {}
    if not scopes:
        U.die("coverage record has no gated DUT-scope rows (dut_scope empty): the round needs the cov_trees rows of "
              "hierarchy.txt, not the grand total")
    if not isinstance(gate, dict) or "parse_error" in gate:
        bad = {k: v.get("parse_error") for k, v in scopes.items() if isinstance(v, dict) and "parse_error" in v}
        U.die(f"gate row not available ({(gate or {}).get('parse_error')}); unparsed scopes: {bad}")
    row: dict[str, Any] = {"scope": " + ".join(gate.get("combined_from") or sorted(scopes)),
                           "combining_rule": gate.get("rule")}
    for m in GATED_CODE_METRICS:
        row[m] = gate.get(m, C.NOT_APPLICABLE)
    # One selector for the group cell (rt39 item one): the percent and the ratio always come from the
    # same named quantity, so no consumer can pair a percent from one definition with another's denominator.
    cell = R.group_cell(cov.get("group_quantities") or {})
    row["group"] = cell.get("percent") if cell.get("percent") is not None else C.NOT_APPLICABLE
    ratios = dict(gate.get("ratios") or {})
    if cell.get("ratio"):
        ratios["group"] = cell["ratio"]
    row["group_cell"] = cell
    row["ratios"] = ratios
    row["info_scopes"] = {k: {m: v.get(m) for m in C.URG_METRICS} | {"ratios": v.get("ratios")}
                          for k, v in (cov.get("info_scope") or {}).items() if isinstance(v, dict)}
    return row


def gain_against(prev: dict[str, Any] | None, cur: dict[str, Any]) -> dict[str, Any]:
    """Per-metric delta in points, the max over gated metrics that both rounds report, and the
    verdict against G. n/a on either side excludes the metric from the computation."""
    deltas: dict[str, Any] = {}
    for m in C.URG_METRICS:
        c = cur.get(m)
        p = (prev or {}).get(m)
        deltas[m] = round(c - p, 2) if isinstance(c, float) and isinstance(p, float) else C.NOT_APPLICABLE
    # Gain is defined on the gated code metrics; group (two-condition gate) is reported but not counted.
    numeric = [deltas[m] for m in GATED_CODE_METRICS if isinstance(deltas[m], float)]
    max_gain = max(numeric) if numeric else None
    return {"deltas": deltas, "max_gain": max_gain,
            "shows_gain": (max_gain is not None and max_gain >= C.ROUND_GAIN_G) if prev else None,
            "G": C.ROUND_GAIN_G}


def gate_status(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for m in C.URG_METRICS:
        v = row.get(m)
        if not isinstance(v, float):
            out[m] = "n/a (not reported by URG; excluded from the gate)"
        elif m == "group":
            out[m] = ("bins >= 80" if v >= C.GATE_PCT else "bins below 80") + " (traceability not checked here)"
        else:
            out[m] = "PASS" if v >= C.GATE_PCT else "below gate"
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


def collect(outdir: Path, round_no: int, dry_run: bool, label: str | None,
            evidence_root: Path = C.EVIDENCE_DIR, index_path: Path = C.ROUND_INDEX,
            evidence_name: str | None = None) -> Path:
    """evidence_root / index_path default to the committed homes; a self-test points them elsewhere.
    evidence_name overrides the directory name (dry runs only, e.g. gen_round_0_rebaseline)."""
    man = U.load_yaml(outdir / "manifest.yaml")
    cov_all = man.get("coverage") or {}
    # A dry run on the check tier has no measured merge; its unmeasured merge is the source, labelled.
    cov = cov_all if cov_all.get("dashboard_txt") else (cov_all.get("unmeasured") or {})
    source = "measured merge" if cov_all.get("dashboard_txt") else "UNMEASURED merge (dry run / check tier)"
    name = f"{C.ROUND_DIR_PREFIX}{round_no}" + ("_dryrun" if dry_run else "")
    if evidence_name:
        if not dry_run:
            U.die("--evidence-name is for dry runs only; real rounds are named gen_round_<n>")
        if not evidence_name.startswith(C.ROUND_DIR_PREFIX):
            U.die(f"--evidence-name must start with {C.ROUND_DIR_PREFIX}")
        name = evidence_name
    ev = evidence_root / name
    if ev.exists():
        U.die(f"{ev} exists; an evidence directory is never overwritten (pick another --round or --tag)")
    # Every refusal below happens before anything is written: a refused round leaves no directory.
    reg_verdict = regression_verdict(man)
    if reg_verdict["verdict"] == "unknown":
        U.die(f"regression {outdir} has no coverage block ({reg_verdict}); nothing to measure, not indexed")
    if reg_verdict["verdict"] != "clean" and not dry_run:
        U.die(f"regression {outdir} is not clean ({reg_verdict}); a round is indexed only for a clean regression")
    row = metric_row(cov)
    if index_path.is_file():
        index = U.load_yaml(index_path)
    else:
        U.log(f"no round index yet; creating {index_path}")
        index = {"G": C.ROUND_GAIN_G, "N": C.ROUND_NO_GAIN_N, "gate_pct": C.GATE_PCT, "rounds": [], "dry_runs": []}
    if not dry_run and round_no != len(index["rounds"]):
        U.die(f"round number {round_no} does not follow the index (next round is {len(index['rounds'])})")
    ev.mkdir(parents=True)
    report = Path(cov.get("report_dir") or "")
    copied: list[str] = []
    # asserts.txt: per-assertion ATTEMPTS / REAL SUCCESSES / FAILURES, the EC-3 evidence rtl-arch reads
    # (gen_excl_select.py --ec3-asserts) from a committed file rather than the out-tree.
    for f in C.ROUND_URG_FILES:
        src = report / f
        if src.is_file():
            shutil.copyfile(src, ev / C.round_evidence_name(f))
            copied.append(C.round_evidence_name(f))
    # rt39 item five: the two large URG products, retained compressed with the reproducible shape.
    gz_copied: list[str] = []
    for f in C.ROUND_URG_GZ_FILES:
        src = report / f
        if src.is_file():
            name = C.round_evidence_name(f) + ".gz"
            retain_gz(src, ev / name)
            gz_copied.append(name)
    scopes = [b.get("cov_scope") for b in (man.get("builds") or {}).values() if b.get("cov_scope")]
    for b in (man.get("builds") or {}).values():
        scopes += b.get("cov_scopes") or []
    scopes = sorted(set(scopes))
    (ev / C.ROUND_EV_HIERARCHY_DUT_ROWS).write_text(dut_rows(report / "hierarchy.txt", scopes), encoding="utf-8")
    if not (report / "groups.txt").is_file():
        (ev / C.ROUND_EV_GROUPS_SUMMARY).write_text("no covergroup in this merge: functional coverage n/a\n", encoding="utf-8")
    dump_dir = Path(cov.get("report_dir") or "").parent / C.URG_DUMP_DIRNAME
    dumped = []
    # The URG dump is several MB of text: a real round keeps it gzip-compressed beside the report;
    # a dry run (unmeasured data) does not copy it at all, the out-tree keeps it.
    if dump_dir.is_dir() and not dry_run:
        (ev / C.ROUND_EV_FULL_EXCL_DIR).mkdir()
        for f in sorted(dump_dir.glob(C.URG_DUMP_METRIC_GLOB)):
            retain_gz(f, ev / C.ROUND_EV_FULL_EXCL_DIR / C.round_evidence_name(f.name + ".gz"))
            dumped.append(C.round_evidence_name(f.name + ".gz"))
    merge_log = Path(cov.get("merge_log") or "")
    wc = warning_counts(merge_log)
    (ev / C.ROUND_EV_MERGE_LOG_WARNINGS).write_text(
        "\n".join(f"{k}: {v}" for k, v in wc.items()) + ("\n" if wc else "no Warning/Error/Note lines\n"), encoding="utf-8")
    if merge_log.is_file():
        shutil.copyfile(merge_log, ev / C.ROUND_EV_MERGE_LOG)
    for bname, b in (man.get("builds") or {}).items():
        bm = Path(b.get("manifest") or "")
        if bm.is_file():
            shutil.copyfile(bm, ev / C.ROUND_EV_BUILD_MANIFEST_FMT.format(build=bname))
    # CM222 M-3: the canary's build manifest is retained beside the round's, so the identity above can be re-derived from the commit.
    _cm = Path((man.get("canary_build") or {}).get("manifest") or "")
    if _cm.is_file():
        shutil.copyfile(_cm, ev / C.ROUND_EV_CANARY_MANIFEST)
        copied.append(C.ROUND_EV_CANARY_MANIFEST)
    shutil.copyfile(C.TESTLIST_YAML, ev / C.ROUND_EV_TESTLIST_SNAPSHOT)
    shutil.copyfile(outdir / "manifest.yaml", ev / C.ROUND_EV_REGRESS_MANIFEST)
    for e in cov.get("elfiles") or []:
        (ev / C.ROUND_EV_ELFILES_DIR).mkdir(exist_ok=True)
        shutil.copyfile(e, ev / C.ROUND_EV_ELFILES_DIR / C.round_evidence_name(Path(e).name))
    # rt39 item four: the canary's identity against the round's. Both values travel with the compare
    # result, so a reader of the commit never has to open a path under work/ that git does not track.
    canary = man.get("canary_build") or {}
    round_sources = None
    for _b in (man.get("builds") or {}).values():
        _bm = U.load_yaml(Path(_b.get("manifest"))) if _b.get("manifest") and Path(_b["manifest"]).is_file() else {}
        round_sources = round_sources or ((_bm.get("inputs") or {}).get("sources_sha256"))
    canary_sources = canary.get("sources_sha256")
    sources_match = (canary_sources == round_sources) if (canary_sources and round_sources) else None
    prev = index["rounds"][-1] if (index["rounds"] and not dry_run) else None
    gain = gain_against(prev["metrics"] if prev else None, row)
    streak = 0 if (prev is None or gain["shows_gain"]) else int(prev.get("no_gain_streak", 0)) + 1
    git = man.get("git") or {}
    entry = {"round": round_no, "dry_run": dry_run, "label": label, "date_utc": U.now_utc(), "evidence_dir": str(ev),
             "regress_outdir": str(outdir), "regress_tag": man.get("tag"), "git_head": git.get("head"),
             "canary_build": man.get("canary_build"),
             "canary_sources_sha256": canary_sources, "round_sources_sha256": round_sources,
             "sources_sha256_match": sources_match, "sources_sha256_scope": C.SOURCES_DIGEST_SCOPE,
             "git_dirty_tracked_files": git.get("dirty_tracked_files"),
             "dirty_tracked_tree": git.get("dirty_tracked_tree"),
             "dirty_tracked_tree_scope": git.get("dirty_scope"),
             "dirty_tracked_tree_stamp_utc": git.get("dirty_stamp_utc"),
             "flow_git_status_now": flow_git_status(),
             "dirty_flow_dir_scope": C.DIRTY_SCOPE_FLOW_DIR,
             "dirty_flow_dir_stamp_utc": U.now_utc(),
             "regression_verdict": reg_verdict,
             "build_config": man.get("build_config"), "source": source, "tests_in_report": (cov.get("totals") or {}).get("tests_in_report"),
             "runs": man.get("summary"), "metrics": row, "gate": gate_status(row), "gain": gain,
             "no_gain_streak": streak, "stopping_rule_fired": (streak >= C.ROUND_NO_GAIN_N) if not dry_run else None,
             "glitch_filter": cov.get("glitch_filter"), "rulings": cov.get("rulings"),
             "exclusion_files": cov.get("elfiles") or [], "excl_strict": cov.get("excl_strict"),
             "exclusion_violations": cov.get("exclusion_violations") or [], "merge_warnings": wc,
             "testlist": {"path": str(C.TESTLIST_YAML), "sha256": U.sha256_file(C.TESTLIST_YAML)},
             "testlist_sha256": U.sha256_file(C.TESTLIST_YAML), "copied": copied, "gz_copied": gz_copied, "full_exclusions_files": dumped,
             "full_exclusions_note": ("dry run: dump not copied (stays in the out-tree)" if dry_run else
                                      "gzip copies in the evidence directory")}
    if dry_run:
        index.setdefault("dry_runs", []).append(entry)
    else:
        index["rounds"].append(entry)
    U.dump_yaml(index, index_path)
    (ev / C.ROUND_EV_SUMMARY).write_text(render_summary(entry, prev), encoding="utf-8")
    U.log(f"evidence written to {ev}; index {index_path}")
    return ev


def flow_git_status() -> list[str]:
    """Uncommitted state of the flow at collect time (so a round produced from modified or untracked
    flow files says so). Its scope differs from git_head's: this one is flow-directory scoped and
    includes untracked files, and the entry records both scopes and both stamps for that reason."""
    r = subprocess.run(["git", "status", "--porcelain", "dv/auto_dv/flow"], cwd=C.REPO_ROOT, capture_output=True, text=True)
    return [l.rstrip() for l in r.stdout.splitlines()]


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
    L += [f"Date (UTC): {e['date_utc']}. Build configuration: `{e['build_config']}`. Git HEAD: `{e['git_head']}` "
          f"(tracked files dirty at regression time: {e.get('git_dirty_tracked_files')}; flow status at collect time: "
          f"{e.get('flow_git_status_now') or 'clean'}). Regression verdict: {e.get('regression_verdict', {}).get('verdict')}.",
          f"Regression: `{e['regress_outdir']}` (tag {e['regress_tag']}); source: {e['source']}; tests in report:",
          f"{e['tests_in_report']}; runs: {e['runs']}.", "",
          f"Exclusion files (loaded with -excl_strict={e['excl_strict']}): {e['exclusion_files'] or 'none'};",
          f"strict violations: {e['exclusion_violations'] or 'none'}. Testlist snapshot sha256 `{e['testlist_sha256']}`.", "",
          f"Rulings applied (gen_tb_architecture.md Section 5): scope = {e.get('rulings', {}).get('scope', 'n/a')}; "
          f"glitch = {e.get('rulings', {}).get('glitch', 'n/a')}. Glitch filter (-cm_glitch 0) on the builds of this "
          f"merge: {e.get('glitch_filter')}; FSM coverage is not glitch-filtered (VCS Warning-[VCM-OPTIGN]).", "",
          f"## Metrics (gate row = `{e['metrics'].get('scope')}` combined: {e['metrics'].get('combining_rule')}; "
          "n/a = URG did not report the metric: excluded from gate and gain; group is gated by bins >= 80 AND "
          "traceability, the latter not checked here, and never counts toward the gain)", "",
          "| Metric | Percent | covered/total | Gate (80) | Delta vs previous round |", "|---|---|---|---|---|"]
    for m in C.URG_METRICS:
        v = e["metrics"].get(m)
        ratio = (e["metrics"].get("ratios") or {}).get(m, "")
        L.append(f"| {m} | {fmt(v)} | {ratio} | {e['gate'][m]} | {fmt(e['gain']['deltas'][m])} |")
    info = e["metrics"].get("info_scopes") or {}
    if info:
        L += ["", "Informational scopes (instrumented, reported, never gated):", "",
              "| Scope | " + " | ".join(C.URG_METRICS) + " |", "|---|" + "---|" * len(C.URG_METRICS)]
        for sc, v in info.items():
            L.append(f"| `{sc}` | " + " | ".join(
                (f"{fmt(v.get(m))} ({(v.get('ratios') or {}).get(m, '')})" if isinstance(v.get(m), float) else fmt(v.get(m)))
                for m in C.URG_METRICS) + " |")
    L += ["", f"Gain rule: G = {C.ROUND_GAIN_G} points on any gated metric. Max delta: {fmt(e['gain']['max_gain'])}; "
          f"shows gain: {e['gain']['shows_gain']} (None when there is no previous round). No-gain streak: "
          f"{e['no_gain_streak']} of N = {C.ROUND_NO_GAIN_N}; stopping rule fired: {e['stopping_rule_fired']}.", "",
          "## Files in this directory", "",
          f"- `{C.ROUND_EV_DASHBOARD}`, `{C.ROUND_EV_HIERARCHY}`, `{C.ROUND_EV_TESTS}` (URG text report), `{C.ROUND_EV_HIERARCHY_DUT_ROWS}` (the DUT-scope rows), `{C.ROUND_EV_ASSERTS}` (EC-3 evidence)",
          f"- `{C.ROUND_EV_GROUPS}` / `{C.ROUND_EV_GRPINFO}` when covergroups exist, else `{C.ROUND_EV_GROUPS_SUMMARY}` stating n/a",
          f"- {C.ROUND_EV_FULL_EXCL_DIR}: {e.get('full_exclusions_note')} (`{C.round_evidence_name('fullexclude.<metric>.gz')}`, gzip; the `_module` variants stay in the out-tree)",
          f"- `{C.ROUND_EV_MERGE_LOG}` and `{C.ROUND_EV_MERGE_LOG_WARNINGS}` (counts per Warning/Error/Note class)",
          f"- `{C.ROUND_EV_BUILD_MANIFEST_FMT.format(build='<build>')}`, `{C.ROUND_EV_TESTLIST_SNAPSHOT}`, `{C.ROUND_EV_REGRESS_MANIFEST}`, `elfiles/` (exclusion files used)", "",
          "## Merge log warning counts", ""] + [f"- {k}: {v}" for k, v in e["merge_warnings"].items()]
    if prev:
        L += ["", f"Previous round: {prev['round']} ({prev['date_utc']}, `{prev['evidence_dir']}`)."]
    return "\n".join(L) + "\n"


def check_canary_build(path: Path, pinned_sha: str | None) -> tuple[int, str]:
    """The pre-dispatch gate (LOG-046a): the canary regression's build must be a head-mode build of the commit this
    round pins and record covergroups_declared true; otherwise the measured round is refused here, before any job,
    with ROUND_EXIT_REFUSED."""
    man, mp = U.load_build_manifest(path)
    refusal = U.measured_dispatch_refusal(man, str(mp), pinned_sha)
    if refusal:
        return C.ROUND_EXIT_REFUSED, "REFUSED: " + refusal
    return 0, (f"canary build {man.get('build')} ({mp}) is the head-mode build of the pinned {str(pinned_sha)[:12]} and records "
               f"{C.COVERGROUPS_DECLARED_KEY} true ({len(man.get('covergroup_files') or [])} covergroup source(s)); measured dispatch allowed")


def retain_gz(src: Path, dst: Path) -> None:
    """Gzip a URG text product into the evidence directory reproducibly, through `gzip -n`, which is the
    recipe the round record already documents and the shape the committed archives carry. Python's
    GzipFile writes a different XFL/OS pair, so a record written one way and re-derived the other would
    not match; gzip.open additionally stores the output name and the wall-clock mtime."""
    out = subprocess.run([C.GZIP_BIN, "-n", "-c", str(src)], capture_output=True)
    if out.returncode != 0:
        U.die(f"{C.GZIP_BIN} -n failed on {src} (rc={out.returncode}): {out.stderr.decode('utf-8', 'replace')[:200]}")
    dst.write_bytes(out.stdout)


def self_test() -> int:
    """check_canary_build on fabricated build manifests (no simulation)."""
    import tempfile
    ok = True
    d = Path(tempfile.mkdtemp(prefix="gen_round_selftest_", dir=C.selftest_tmp()))
    pin = "c" * 40
    head = {"build": "gen_tb", "source_mode": C.SOURCE_MODE_HEAD, "head_sha": pin, C.COVERGROUPS_DECLARED_KEY: True, "covergroup_files": ["a.sv"], C.B8_PROBE_KNOB_DEFAULT_KEY: False, C.B8_PROBE_SV_DEFAULT_KEY: False}
    cases = ((f"{C.COVERGROUPS_DECLARED_KEY} false refuses", dict(head, **{C.COVERGROUPS_DECLARED_KEY: False, "covergroup_files": []}), C.ROUND_EXIT_REFUSED, f"{C.COVERGROUPS_DECLARED_KEY}=False"),
             (f"{C.B8_PROBE_KNOB_DEFAULT_KEY} true refuses (LOG-067)", dict(head, **{C.B8_PROBE_KNOB_DEFAULT_KEY: True}), C.ROUND_EXIT_REFUSED, f"{C.B8_PROBE_KNOB_DEFAULT_KEY}=True"),
             (f"{C.B8_PROBE_SV_DEFAULT_KEY} true refuses (LOG-067, CM136-L-2)", dict(head, **{C.B8_PROBE_SV_DEFAULT_KEY: True}), C.ROUND_EXIT_REFUSED, f"{C.B8_PROBE_SV_DEFAULT_KEY}=True"),
             ("fact absent (older manifest) refuses", {"build": "gen_tb", "source_mode": C.SOURCE_MODE_HEAD, "head_sha": pin}, C.ROUND_EXIT_REFUSED, f"{C.COVERGROUPS_DECLARED_KEY}=absent"),
             ("a worktree build refuses even with a covergroup", dict(head, source_mode=C.SOURCE_MODE_WORKTREE), C.ROUND_EXIT_REFUSED, "worktree-mode build"),
             ("a head build of another commit refuses", dict(head, head_sha="d" * 40), C.ROUND_EXIT_REFUSED, "not of the pinned"),
             ("a head build of the pinned commit with a covergroup dispatches", head, 0, "measured dispatch allowed"))
    for label, man, want_rc, want_text in cases:
        U.dump_yaml(man, d / C.BUILD_MANIFEST)
        rc, msg = check_canary_build(d, pin)
        cond = rc == want_rc and want_text in msg and "gen_tb" in msg and (("LOG-046a" in msg) == (want_rc != 0))
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"{label}: rc {rc}: {msg[:110]}")
    rc, msg = check_canary_build(d / "no_such_build", pin)
    cond = rc == C.ROUND_EXIT_REFUSED and "no build manifest" in msg
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"missing canary build dir refuses: rc {rc}")
    # item five: retain_gz is reproducible: the header carries no source name and no wall-clock mtime, so
    # two collects of one source give one digest (gzip.open stores both and the two differ).
    src = d / "modlist.txt"
    src.write_bytes(b"module top\nmodule leaf\n" * 300)
    a_gz, b_gz = d / "a.txt.gz", d / "b.txt.gz"
    retain_gz(src, a_gz)
    retain_gz(src, b_gz)
    head_a, head_b = a_gz.read_bytes()[:10], b_gz.read_bytes()[:10]
    mtime_a = int.from_bytes(head_a[4:8], "little")
    mtime_b = int.from_bytes(head_b[4:8], "little")
    named = bool(head_a[3] & 0x08) or bool(head_b[3] & 0x08)
    same = U.sha256_file(a_gz) == U.sha256_file(b_gz)
    cond = mtime_a == 0 and mtime_b == 0 and not named and same
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD",
          f"retain_gz is reproducible: mtime {mtime_a}/{mtime_b}, stored-name flag {named}, "
          f"digests {'equal' if same else 'DIFFER'}")
    cond = gzip.decompress(a_gz.read_bytes()) == src.read_bytes()
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", "retain_gz round-trips the source bytes unchanged")
    U.remove_selftest_tree(d)
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 2


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
    ap.add_argument("--canary-build", type=Path,
                    help="build dir (or build_manifest.yaml) of the canary regression: a measured round dispatches only when it "
                         "is a head-mode build of the commit the round pins and records covergroups_declared true (LOG-046a)")
    ap.add_argument("--evidence-root", type=Path, default=C.EVIDENCE_DIR,
                    help="self-test only: write the evidence dir and index elsewhere than dv/auto_dv/evidence")
    ap.add_argument("--evidence-name", help="dry runs only: evidence directory name (gen_round_<n>_<suffix>)")
    ap.add_argument("--tests", help="dry runs / re-baselines: explicit test list instead of the tier")
    ap.add_argument("--seed-list", help="explicit seeds for the selected tests")
    a = ap.parse_args()
    index_path = C.ROUND_INDEX if a.evidence_root == C.EVIDENCE_DIR else a.evidence_root / C.ROUND_INDEX.name
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
        a.pinned_sha = None
        if not (a.dry_run or a.tests):
            # A measured round (tier full, purpose 4) pins HEAD now and never dispatches unless the canary is a head-mode
            # build of exactly that commit with a covergroup declared; the regression is then pinned to the same sha.
            if a.canary_build is None:
                U.log(f"REFUSED: --canary-build is required for a measured round ({C.MEASURED_DISPATCH_RULE})")
                return C.ROUND_EXIT_REFUSED
            a.pinned_sha = M.head_sha()
            rc, msg = check_canary_build(a.canary_build, a.pinned_sha)
            U.log(msg)
            if rc:
                return rc
        tag = a.tag or (f"round_{a.round}" + ("_dryrun" if a.dry_run else ""))
        outdir = run_regression(a, tag)
    ev = collect(outdir, a.round, a.dry_run, a.label, a.evidence_root, index_path, a.evidence_name)
    rc, _, _ = U.run_bounded([sys.executable, str(C.FLOW_DIR / "gen_dashboard.py")], cwd=C.REPO_ROOT,
                             log_path=C.WORK_DIR / "round_dashboard.log", timeout_s=600)
    U.log(f"dashboard regenerated (rc={rc}); evidence {ev}")
    return 0


if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv else main())
