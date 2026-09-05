#!/usr/bin/env python3
"""fcov-expectation wiring (trust triad rule 3): every test declares the functional-coverage bins
it intends to hit in dv/auto_dv/fcov_expectations/<test>.fcov.yaml; a declared-but-unhit bin
FAILS the run. The verdict is ci/check_fcov_expectations.py's (per test, pre-merge, on the test's
own vdb slice via `urg -tests <vdb minus .vdb>/<cm_name>`); this module validates the manifest
schema, drives the checker, parses its per-bin lines and carries the anti-vacuity notes through.

Cross bins (LOG-054): urg's grpinfo.txt lists a cross under `Summary for Cross <cr>` and names each
row by its component tuple (one column per coverpoint, then COUNT AT LEAST), never by a bin name; the
checker reads only `Summary for Variable` sections with NAME COUNT rows. This module runs the per-test
urg report itself (the checker's own command and isolation check), derives a variable-form grpinfo.txt
beside the original (each cross section becomes a variable section whose rows carry the tuple joined
with `_`, the manifests' cross-bin names; variable sections are copied unchanged) and calls the checker
with --report-dir on the derived report. Both files stay in the run dir and the result names them.

Manifest schema (`<test>.fcov.yaml`, file stem == test name):
    test: gen_<name>                      # must equal the file stem
    owner: <role slug>
    bins:                                 # gen_<feature>_cg.<coverpoint>.<bin>, at least one
      - gen_regime_cg.cp_regime.bin_fast
    anti_vacuity:                         # one note per declared bin: why a hit evidences the stimulus
      gen_regime_cg.cp_regime.bin_fast: "regime knob sampled once per phase; fast only when the schedule selects it"
The checker reads only `bins:` (raw `- token` lines, so bins are written bare, never quoted); the
flow reads the rest (anti-vacuity notes are carried, never interpreted). No other keys.

Usage:
    gen_fcov.py --validate <manifest.fcov.yaml> [...]     # schema check (exit 1 on a violation)
    gen_fcov.py --self-test                                # fabricated urg report dir through the real checker
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import gen_flow_const as C
import gen_flow_util as U

BIN_RE = re.compile(r"^(gen_\w+)\.([A-Za-z_]\w*)\.([^.\s]+)$")
QUOTED_BIN_LINE_RE = re.compile(r"""^\s*-\s*["']""")
RESULT_LINE_RE = re.compile(r"^FCOV-EXPECTATION: (\S+) = (HIT|UNHIT|MISSING-FROM-REPORT) \(count=(\S+)\)")
STATUS_BY_EXIT = C.FCOV_EXIT_CODES
REASON_UNMET = C.FCOV_UNMET_REASON
REASON_UNVERIFIABLE = "fcov expectation unverifiable"
CAUSE_NO_GRPINFO = "per-test urg report has no grpinfo.txt (no covergroup in this vdb)"
CAUSE_URG_FAILED = "per-test urg report failed"
CAUSE_ISOLATION = "per-test isolation not confirmed (want exactly 1 test = the run's cm_name in tests.txt)"
DERIVED_REPORT_DIRNAME = "urgReport_variable_form"
CROSS_SECTION_RE = re.compile(r"^Summary for Cross (\S+)\s*$")
SECTION_START_RE = re.compile(r"^(Summary for (Variable|Group|Cross)\b|Variables for Group\b|Group : )")
BINS_TITLE_RE = re.compile(r"^(Uncovered bins|Covered bins|Bins)\s*$")   # "Bins": urg's title when every bin is covered
TUPLE_TOKEN_RE = re.compile(r"\[[^\]]*\]|\S+")   # a bracketed component (possibly multi-valued) or a bare token
CHECKER_MODE = "--report-dir on the variable-form grpinfo.txt derived by gen_fcov (cross rows named by their tuple)"
# The checker's own per-test urg command and isolation regexes, re-typed here because ci/ belongs to another owner; the
# self-test parses ci/check_fcov_expectations.py and asserts these copies equal its source, so drift fails loud.
URG_PER_TEST_ARGV = ("urg", "-full64", "-dir", "<vdb>", "-format", "text", "-report", "<report>", "-tests", "<sel_file>")
ISOLATION_TOTAL_RE = r"Total tests in report: (\d+)"
ISOLATION_EXACT_RE_FMT = r"^\S*/{cm}\s*$"
COLLISION_REFUSE = "derived cross-bin names collide in the variable-form report (the checker would sum their counts)"
CROSS_SAMPLE = Path(__file__).resolve().parent / "gen_fixtures" / "gen_grpinfo_cross_sample.txt"   # real urg excerpt, header lines say from where
CROSS_SAMPLE_TBINFRA = CROSS_SAMPLE.parent / "gen_grpinfo_cross_sample_tbinfra.txt"   # TB Infra's T-215 probe report, whole, same header form


def manifest_path(test: dict[str, Any]) -> Path | None:
    """The manifest under the source root the run binds to (the loader checks existence there; in head mode that is the
    pinned tree, not the clone the flow code runs from)."""
    f = test.get("fcov_expectation_file")
    return (C.SOURCE_ROOT / f).resolve() if f else None


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
    unknown = set(data) - {"test", "owner", "bins", "anti_vacuity"}
    if unknown:
        problems.append(f"unknown keys {sorted(unknown)}")
    # The checker reads the raw `- <token>` lines: a quoted YAML entry would reach it with its quotes.
    in_bins = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if re.match(r"^bins:\s*$", line):
            in_bins = True
            continue
        if line and not line.startswith(" ") and not line.startswith("-"):
            in_bins = False
        if in_bins and QUOTED_BIN_LINE_RE.match(line):
            problems.append(f"quoted bin line {line.strip()!r}: write the bin bare (the checker reads the raw token)")
    return data, problems


def run_checker(manifest: Path, vdb: Path | None, cm_name: str | None, log_path: Path,
                report_dir: Path | None = None, declared_bins: list[str] | None = None) -> dict[str, Any]:
    """ci/check_fcov_expectations.py on one test slice; the per-bin lines are parsed, not judged.
    `declared` counts the manifest's bins (validated), never the lines the checker managed to print."""
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
    declared = len(declared_bins) if declared_bins is not None else len(bins)
    cause = protocol_cause(r.stdout + r.stderr, log_path.parent) if status == "PROTOCOL_ERROR" else None
    return {"exit_code": r.returncode, "status": status, "log": str(log_path), "bins": bins,
            "unmet_bins": unmet, "declared": declared, "hit": sum(1 for v in bins.values() if v["state"] == "HIT"),
            "cause": cause,
            "reason": None if status == "PASS" else
            (f"{REASON_UNMET}: {len(unmet)} declared bin(s) not hit {unmet[:5]}" if status == "UNHIT"
             else f"{REASON_UNVERIFIABLE}: {cause or f'checker exit {r.returncode}'} (see {log_path.name})")}


def per_test_report(vdb: Path, cm_name: str, workdir: Path) -> tuple[Path | None, str | None]:
    """The checker's own per-test urg report (`urg -tests <vdb minus .vdb>/<cm_name>`, text format) and its
    isolation check, run here so the report can be rewritten before the checker reads it. Returns (report dir or
    None, cause or None); urg's output is kept in the work dir."""
    report = workdir / "urgReport"
    ident = f"{str(vdb)[:-4] if str(vdb).endswith('.vdb') else str(vdb)}/{cm_name}"
    sel_file = workdir / "test_selection.txt"
    sel_file.write_text(ident + "\n", encoding="utf-8")
    fill = {"<vdb>": str(vdb), "<report>": str(report), "<sel_file>": str(sel_file)}
    r = subprocess.run([fill.get(tok, tok) for tok in URG_PER_TEST_ARGV], capture_output=True, text=True)
    (workdir / "urg_stdout.log").write_text(r.stdout + r.stderr, encoding="utf-8")
    if not report.is_dir():
        return None, CAUSE_URG_FAILED
    # Isolation first: a selection that names no test of this vdb also yields a report without grpinfo.txt, and that
    # is a wrong cm_name, not a TB without a covergroup.
    tests_txt = (report / "tests.txt").read_text(encoding="utf-8", errors="replace") if (report / "tests.txt").is_file() else ""
    m = re.search(ISOLATION_TOTAL_RE, tests_txt)
    exact = re.search(ISOLATION_EXACT_RE_FMT.format(cm=re.escape(cm_name)), tests_txt, re.M)
    if not m or m.group(1) != "1" or not exact:
        return report, f"{CAUSE_ISOLATION}; tests.txt says: {m.group(0) if m else 'unparseable'}"
    if r.returncode != 0 or not (report / "grpinfo.txt").is_file():
        return report, CAUSE_NO_GRPINFO if r.returncode == 0 else CAUSE_URG_FAILED
    return report, None


def checker_forms(checker: Path) -> tuple[tuple[str, ...], str, str]:
    """From ci/check_fcov_expectations.py's source: urg_per_test_report's argv list (str(x) calls as <x>) and its two
    isolation regexes (the f-string's formatted part as {cm}), for the drift self-test."""
    import ast
    tree = ast.parse(checker.read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "urg_per_test_report")
    argv: tuple[str, ...] = ()
    regexes: list[str] = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign) and any(isinstance(x, ast.Name) and x.id == "cmd" for x in node.targets) and isinstance(node.value, ast.List):
            toks = []
            for e in node.value.elts:
                if isinstance(e, ast.Constant):
                    toks.append(str(e.value))
                elif isinstance(e, ast.Call) and isinstance(e.func, ast.Name) and e.func.id == "str" and isinstance(e.args[0], ast.Name):
                    toks.append(f"<{e.args[0].id}>")
                else:
                    toks.append("<?>")
            argv = tuple(toks)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "search" and node.args:
            a = node.args[0]
            if isinstance(a, ast.Constant):
                regexes.append(str(a.value))
            elif isinstance(a, ast.JoinedStr):
                regexes.append("".join(str(v.value) if isinstance(v, ast.Constant) else "{cm}" for v in a.values))
    total = next((r for r in regexes if "Total tests" in r), "")
    exact = next((r for r in regexes if "{cm}" in r), "")
    return argv, total, exact


def tuple_row(line: str, name_cols: int) -> str | None:
    """One bin row of a tuple-form table as a NAME row, or None for a line that is not one single bin: a hole group
    (multi-valued `[a , b]` or `*` components, `--` counts) or a stray line. Auto-generated cross bins print their
    components bracketed (`[c_mul] [distinct] 0 1 1`) or bare (`c_mul pos_rand all_ones 1 1`); the name is the
    components joined with `_`, the manifests' cross-bin naming."""
    toks = TUPLE_TOKEN_RE.findall(line)
    if len(toks) <= name_cols or not toks[name_cols].isdigit():
        return None
    names = []
    for tok in toks[:name_cols]:
        inner = tok[1:-1].strip() if tok.startswith("[") and tok.endswith("]") else tok
        if not inner or "," in inner or inner == "*":
            return None
        names.append(inner)
    return "_".join(names) + " " + " ".join(toks[name_cols:])


def derive_variable_form(text: str) -> tuple[str, dict[str, Any]]:
    """The variable-form grpinfo.txt the checker can read. Cross sections: `Summary for Cross <cr>` becomes
    `Summary for Variable <cr>`, and in each bins table the header's name columns (those before COUNT) collapse into
    one NAME column whose value is the row's components joined with `_` (a one-column NAME table keeps its names), the
    count columns following, single-spaced; hole-group rows stay as they are (the checker ignores them). In every
    section a table titled `Bins` (urg's title when all bins are covered, which the checker does not read) is
    retitled `Covered bins`. Everything else is copied byte for byte."""
    out: list[str] = []
    stats: dict[str, Any] = {"cross_sections": 0, "cross_tables": 0, "cross_rows": 0, "bins_tables_retitled": 0,
                             "name_collisions": 0, "collisions": []}
    in_cross = False
    name_cols: int | None = None      # name columns of the current cross table
    awaiting_header = False           # between a table title and its header line
    seen: dict[str, str] = {}         # derived name -> source row, per cross section (the checker sums equal keys)
    cross_name = ""
    for line in text.splitlines():
        m = CROSS_SECTION_RE.match(line)
        if m:
            in_cross, name_cols, awaiting_header = True, None, False
            seen, cross_name = {}, m.group(1)
            stats["cross_sections"] += 1
            out.append(f"Summary for Variable {m.group(1)}")
            continue
        if in_cross and SECTION_START_RE.match(line):
            in_cross, name_cols, awaiting_header = False, None, False
        title = BINS_TITLE_RE.match(line)
        if title and title.group(1) == "Bins":
            stats["bins_tables_retitled"] += 1
            line = "Covered bins"
        if in_cross:
            toks = line.split()
            if title:
                name_cols, awaiting_header = None, True
                stats["cross_tables"] += 1
            elif awaiting_header and toks:
                if "COUNT" in toks and toks.index("COUNT") >= 1:
                    name_cols = toks.index("COUNT")
                    out.append("NAME " + " ".join(toks[name_cols:]))
                    awaiting_header = False
                    continue
                awaiting_header = False   # a table without a COUNT header is left as it is
            elif name_cols is not None:
                if not toks:
                    name_cols = None      # a blank line ends the table
                else:
                    row = tuple_row(line, name_cols)
                    if row is not None:
                        name = row.split(" ", 1)[0]
                        if name in seen and seen[name] != line.strip():
                            stats["name_collisions"] += 1
                            if len(stats["collisions"]) < 10:
                                stats["collisions"].append(f"{cross_name}.{name}: {seen[name]!r} and {line.strip()!r}")
                        seen.setdefault(name, line.strip())
                        out.append(row)
                        stats["cross_rows"] += 1
                        continue
        out.append(line)
    return "\n".join(out) + "\n", stats


def collision_refusal(stats: dict[str, Any]) -> str | None:
    """Two distinct tuples whose components carry `_` can derive the same name ((a, b_c) and (a_b, c)); the checker
    would sum their counts and could report HIT for a tuple that was unhit, so a derived report with a collision is
    refused (FAIL, unverifiable) rather than judged."""
    n = int(stats.get("name_collisions") or 0)
    if n == 0:
        return None
    return f"{COLLISION_REFUSE}: {n} collision(s), e.g. {stats.get('collisions', [])[:3]}"


def derived_report(report: Path) -> tuple[Path, dict[str, Any]]:
    """Write the variable-form report beside the original (grpinfo.txt rewritten; tests.txt and dashboard.txt
    copied for the record); the original report dir is never touched."""
    dst = report.parent / DERIVED_REPORT_DIRNAME
    dst.mkdir(exist_ok=True)
    text, stats = derive_variable_form((report / "grpinfo.txt").read_text(encoding="utf-8", errors="replace"))
    (dst / "grpinfo.txt").write_text(text, encoding="utf-8")
    for name in ("tests.txt", "dashboard.txt"):
        if (report / name).is_file():
            shutil.copyfile(report / name, dst / name)
    return dst, stats


def protocol_cause(checker_output: str, run_dir: Path) -> str:
    """Name the cause of a checker protocol error from what is on disk (the checker's own message
    quotes urg's tail, which does not say what was missing)."""
    if "urg per-test report failed" in checker_output:
        reports = sorted(run_dir.glob("fcovexp_*/urgReport"))
        if reports and not (reports[-1] / "grpinfo.txt").is_file():
            return CAUSE_NO_GRPINFO
        return CAUSE_URG_FAILED
    if "per-test isolation not confirmed" in checker_output:
        return "per-test isolation not confirmed by the checker"
    if "no covergroup bin rows parsed" in checker_output:
        return "grpinfo.txt holds no covergroup bin rows"
    if "no bins declared" in checker_output:
        return "manifest declares no bins"
    return "checker protocol error"


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
    # Retain the manifest as used beside the run: the proof never rests on an uncommitted working file.
    shutil.copyfile(mpath, run_dir / "fcov_manifest_used.yaml")
    declared = list((data or {}).get("bins", []))
    work = Path(tempfile.mkdtemp(prefix="fcovexp_", dir=run_dir))
    report, cause = per_test_report(vdb, cm_name, work)
    if cause:
        log = run_dir / "fcov_check.log"
        log.write_text(f"per-test urg report: {cause}\nurg output: {work / 'urg_stdout.log'}\n", encoding="utf-8")
        return {"status": "PROTOCOL_ERROR", "exit_code": None, "log": str(log), "bins": {}, "unmet_bins": [],
                "declared": len(declared), "hit": 0, "cause": cause, "manifest": str(mpath),
                "manifest_copy": str(run_dir / "fcov_manifest_used.yaml"), "manifest_sha256": U.sha256_file(mpath),
                "report_dir": str(report) if report else None, "derived_report_dir": None, "derived_grpinfo": None,
                "checker_mode": CHECKER_MODE, "anti_vacuity": {b: (data or {}).get("anti_vacuity", {}).get(b) for b in declared},
                "owner": (data or {}).get("owner"), "reason": f"{REASON_UNVERIFIABLE}: {cause} (see fcov_check.log)"}
    derived, stats = derived_report(report)
    refusal = collision_refusal(stats)
    if refusal:
        log = run_dir / "fcov_check.log"
        log.write_text(f"derived report refused: {refusal}\nreport: {report}\nderived: {derived}\n", encoding="utf-8")
        return {"status": "PROTOCOL_ERROR", "exit_code": None, "log": str(log), "bins": {}, "unmet_bins": [],
                "declared": len(declared), "hit": 0, "cause": refusal, "manifest": str(mpath),
                "manifest_copy": str(run_dir / "fcov_manifest_used.yaml"), "manifest_sha256": U.sha256_file(mpath),
                "report_dir": str(report), "derived_report_dir": str(derived), "derived_grpinfo": stats,
                "checker_mode": CHECKER_MODE, "anti_vacuity": {b: (data or {}).get("anti_vacuity", {}).get(b) for b in declared},
                "owner": (data or {}).get("owner"), "reason": f"{REASON_UNVERIFIABLE}: {refusal} (see fcov_check.log)"}
    res = run_checker(mpath, None, None, run_dir / "fcov_check.log", report_dir=derived, declared_bins=declared)
    res.update(report_dir=str(report), derived_report_dir=str(derived), derived_grpinfo=stats, checker_mode=CHECKER_MODE)
    res["manifest"] = str(mpath)
    res["manifest_copy"] = str(run_dir / "fcov_manifest_used.yaml")
    res["manifest_sha256"] = U.sha256_file(mpath)
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
    with tempfile.TemporaryDirectory(prefix="gen_fcov_selftest_", dir=C.selftest_tmp()) as td:
        d = Path(td)
        cg, cp = "gen_selftest_cg", "cp_mode"
        good = d / "gen_selftest_ok.fcov.yaml"
        good.write_text(f"test: gen_selftest_ok\nowner: runtime\nbins:\n  - {cg}.{cp}.bin_a\n  - {cg}.{cp}.bin_b\n"
                        f"anti_vacuity:\n  {cg}.{cp}.bin_a: sampled once per mode switch\n"
                        f"  {cg}.{cp}.bin_b: sampled once per mode switch\n", encoding="utf-8")
        _, problems = validate_manifest(good)
        ok &= not problems
        print("SELF-TEST", "ok " if not problems else "BAD", "fabricated manifest: schema accepts a well-formed manifest", problems)
        bad = d / "gen_selftest_bad.fcov.yaml"
        bad.write_text(f"test: other\nowner: nobody\nbins:\n  - notgen_cg.{cp}.bin_a\n  - {cg}.{cp}.bin_a\n"
                       f"anti_vacuity: {{}}\n", encoding="utf-8")
        _, problems = validate_manifest(bad)
        want = ["file stem", "role slug", "gen_ namespace", "anti_vacuity note missing"]
        got = all(any(w in p for p in problems) for w in want)
        ok &= got
        print("SELF-TEST", "ok " if got else "BAD", f"fabricated manifest: schema rejects stem/owner/namespace/note violations ({len(problems)} problems)")
        quoted = d / "gen_selftest_quoted.fcov.yaml"
        quoted.write_text(f"test: gen_selftest_quoted\nowner: runtime\nbins:\n  - \"{cg}.{cp}.bin_a\"\n  - {cg}.{cp}.bin.extra\n"
                          f"anti_vacuity:\n  {cg}.{cp}.bin_a: x\n  {cg}.{cp}.bin.extra: x\n", encoding="utf-8")
        _, problems = validate_manifest(quoted)
        got = any("quoted bin line" in p_ for p_ in problems) and any("gen_ namespace" in p_ for p_ in problems)
        ok &= got
        print("SELF-TEST", "ok " if got else "BAD", f"fabricated manifest: quoted bin line and a fourth dotted part are rejected ({len(problems)} problems)")
        rep_hit = d / "report_hit"
        fabricate_report(rep_hit, cg, cp, {"bin_a": 3, "bin_b": 1})
        res = run_checker(good, None, None, d / "hit.log", report_dir=rep_hit)
        cond = res["status"] == "PASS" and res["hit"] == 2 and res["unmet_bins"] == []
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"fabricated report: checker PASS on all-hit fixture: {res['status']} hit={res['hit']}")
        rep_miss = d / "report_miss"
        fabricate_report(rep_miss, cg, cp, {"bin_a": 3, "bin_b": 0})
        res = run_checker(good, None, None, d / "miss.log", report_dir=rep_miss)
        cond = res["status"] == "UNHIT" and res["unmet_bins"] == [f"{cg}.{cp}.bin_b"] and res["reason"].startswith(REASON_UNMET)
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"fabricated report: checker UNHIT on one unhit bin: {res['status']} {res['unmet_bins']} reason={res['reason']}")
        rep_absent = d / "report_absent"
        fabricate_report(rep_absent, cg, cp, {"bin_a": 3})
        res = run_checker(good, None, None, d / "absent.log", report_dir=rep_absent)
        cond = res["status"] == "UNHIT" and res["bins"].get(f"{cg}.{cp}.bin_b", {}).get("state") == "MISSING-FROM-REPORT"
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"fabricated report: a declared bin absent from the report counts as unmet: {res['bins'].get(f'{cg}.{cp}.bin_b')}")
        res = run_checker(good, None, None, d / "noreport.log", report_dir=d / "does_not_exist",
                          declared_bins=[f"{cg}.{cp}.bin_a", f"{cg}.{cp}.bin_b"])
        cond = res["status"] == "PROTOCOL_ERROR" and res["reason"].startswith(REASON_UNVERIFIABLE) and res["declared"] == 2
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"fabricated report: unverifiable query is not a pass and keeps declared=2: {res['status']} declared={res['declared']}")
        # Cross bins (LOG-054): a fabricated grpinfo.txt in urg's tuple form, derived to the variable form, through the REAL checker.
        var_block = ["Summary for Variable cp_op", "", "Covered bins", "", "NAME  COUNT AT LEAST NUMBER ", "c_mul 5     1        1      ", "", "----------"]
        var_full = ["Summary for Variable cp_full", "", "Bins", "", "NAME  COUNT AT LEAST ", "hit_a 4     1        ", "", "----------"]
        cross_block = ["Summary for Cross cr_extremes", "", "Samples crossed: cp_op cp_rs1_class cp_rs2_class",
                       "CATEGORY                           EXPECTED UNCOVERED COVERED PERCENT MISSING ", "User Defined Cross Bins            3        1         2       66.67           ", "",
                       "Automatically Generated Cross Bins for cr_extremes", "", "Element holes", "",
                       "cp_op   cp_rs1_class          cp_rs2_class COUNT AT LEAST NUMBER ", "[mulh]  [pos_rand , neg_rand] *            --    --       6      ", "",
                       "Uncovered bins", "", "cp_op   cp_rs1_class cp_rs2_class COUNT AT LEAST NUMBER ", "[c_mul] [distinct]   [zero]       0     1        1      ",
                       "[mul]   [zero , one] [zero]       --    --       2      ", "",
                       "Covered bins", "", "cp_op cp_rs1_class cp_rs2_class COUNT AT LEAST ", "c_mul all_ones     neg_rand     2     1        ",
                       "c_mul zero         pos_rand     7     1        ", "",
                       "User Defined Cross Bins for cr_extremes", "", "Uncovered bins", "", "NAME                    COUNT AT LEAST NUMBER ",
                       "c_mul_all_ones_all_ones 0     1        1      ", "", "----------"]
        cross_full = ["Summary for Cross cr_full", "", "CATEGORY                EXPECTED UNCOVERED COVERED PERCENT MISSING ", "User Defined Cross Bins 1        0         1       100.00          ", "",
                      "User Defined Cross Bins for cr_full", "", "Bins", "", "NAME            COUNT AT LEAST ", "mul_all_ones    7     1        ", "", "----------"]
        rep_x = d / "report_cross"; rep_x.mkdir()
        (rep_x / "grpinfo.txt").write_text("\n".join(["Group : gen_tb_top.u_env.u_cov::gen_x_cg", ""] + var_block + [""] + cross_block + [""] + var_block + [""] + cross_full + [""] + var_full) + "\n", encoding="utf-8")
        (rep_x / "tests.txt").write_text("Total tests in report: 1\n/x/build/test_gen_x_1\n", encoding="utf-8")
        derived, stats = derived_report(rep_x)
        dtext = (derived / "grpinfo.txt").read_text(encoding="utf-8")
        xm = d / "gen_selftest_x.fcov.yaml"
        bins_x = ["gen_x_cg.cp_op.c_mul", "gen_x_cg.cr_extremes.c_mul_all_ones_neg_rand", "gen_x_cg.cr_extremes.c_mul_all_ones_all_ones",
                  "gen_x_cg.cr_extremes.c_mul_distinct_zero", "gen_x_cg.cr_full.mul_all_ones", "gen_x_cg.cp_full.hit_a"]
        xm.write_text("test: gen_selftest_x\nowner: runtime\nbins:\n" + "".join(f"  - {b}\n" for b in bins_x) + "anti_vacuity:\n" + "".join(f"  {b}: x\n" for b in bins_x), encoding="utf-8")
        before = run_checker(xm, None, None, d / "cross_before.log", report_dir=rep_x)
        after = run_checker(xm, None, None, d / "cross_after.log", report_dir=derived)
        st = {b: after["bins"][b]["state"] for b in bins_x}
        cond = (stats == {"cross_sections": 2, "cross_tables": 4, "cross_rows": 5, "bins_tables_retitled": 2, "name_collisions": 0, "collisions": []}
                and "Summary for Variable cr_extremes" in dtext and "Summary for Cross" not in dtext and "\nBins\n" not in dtext
                and "c_mul_all_ones_neg_rand 2 1" in dtext and "c_mul_distinct_zero 0 1 1" in dtext and "[mul]   [zero , one] [zero]       --    --       2" in dtext
                and "[mulh]  [pos_rand , neg_rand] *" in dtext and "c_mul_all_ones_all_ones 0 1 1" in dtext
                and dtext.count("\n".join(var_block)) == 2 and (derived / "tests.txt").is_file() and (rep_x / "grpinfo.txt").read_text(encoding="utf-8").count("Summary for Cross") == 2
                and before["bins"]["gen_x_cg.cr_extremes.c_mul_all_ones_neg_rand"]["state"] == "MISSING-FROM-REPORT"
                and before["bins"]["gen_x_cg.cr_full.mul_all_ones"]["state"] == "MISSING-FROM-REPORT" and before["bins"]["gen_x_cg.cp_full.hit_a"]["state"] == "MISSING-FROM-REPORT"
                and after["bins"]["gen_x_cg.cr_extremes.c_mul_all_ones_neg_rand"] == {"state": "HIT", "count": "2"}
                and st == {"gen_x_cg.cp_op.c_mul": "HIT", "gen_x_cg.cr_extremes.c_mul_all_ones_neg_rand": "HIT", "gen_x_cg.cr_extremes.c_mul_all_ones_all_ones": "UNHIT",
                           "gen_x_cg.cr_extremes.c_mul_distinct_zero": "UNHIT", "gen_x_cg.cr_full.mul_all_ones": "HIT", "gen_x_cg.cp_full.hit_a": "HIT"}
                and after["status"] == "UNHIT")
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"cross bins through the REAL checker: MISSING-FROM-REPORT on the original report, on the derived form a bare tuple row is HIT, a bracketed auto row UNHIT, a named row UNHIT, an all-covered 'Bins' table HIT in a cross and in a variable, hole groups left alone; variable sections otherwise byte-identical; original untouched; stats {stats}")
        print("SELF-TEST", "ok " if cond else "BAD", f"derived states: {st}")
        # The re-typed checker forms must equal the checker's own source, so drift fails here.
        argv_c, total_c, exact_c = checker_forms(C.FCOV_CHECKER)
        cond = argv_c == URG_PER_TEST_ARGV and total_c == ISOLATION_TOTAL_RE and exact_c == ISOLATION_EXACT_RE_FMT
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"checker drift: the flow's urg argv and isolation regexes equal those parsed from {C.FCOV_CHECKER.name}: {argv_c} {total_c!r} {exact_c!r}")
        # A constructed name collision is counted and refused; a clean report is not.
        coll = ["Group : gen_tb_top.u_env.u_cov::gen_c_cg", "", "Summary for Cross cr_c", "", "Covered bins", "",
                "cp_x cp_y COUNT AT LEAST ", "a    b_c  3     1        ", "", "Uncovered bins", "", "cp_x cp_y COUNT AT LEAST NUMBER ",
                "[a_b] [c]  0     1        1      ", "[d]   [e]  0     1        1      ", "", "----------"]
        rep_c = d / "report_collision"; rep_c.mkdir()
        (rep_c / "grpinfo.txt").write_text("\n".join(coll) + "\n", encoding="utf-8")
        _, stats_c = derived_report(rep_c)
        r_c = collision_refusal(stats_c)
        cond = stats_c["name_collisions"] == 1 and stats_c["collisions"] and stats_c["collisions"][0].startswith("cr_c.a_b_c:") \
            and r_c is not None and COLLISION_REFUSE in r_c and collision_refusal(stats) is None and stats["name_collisions"] == 0
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"cross-name collision: (a, b_c) and (a_b, c) derive one name, counted and refused ({stats_c['name_collisions']}); the fabricated and real reports have none")
        # The real sample: a per-test urg grpinfo.txt excerpt of the flow's own probe (gen_test_mul_mul on the committed covergroups).
        rep_s = d / "report_sample"; rep_s.mkdir()
        shutil.copyfile(CROSS_SAMPLE, rep_s / "grpinfo.txt")
        (rep_s / "tests.txt").write_text("Total tests in report: 1\n/x/build/test_gen_test_mul_mul_250519699\n", encoding="utf-8")
        derived_s, stats_s = derived_report(rep_s)
        want = {"gen_mul_ops_cg.cr_op_rd_x0.mul_no": ("HIT", "94"), "gen_mul_ops_cg.cr_op_rd_x0.c_mul_yes": ("UNHIT", "0"),
                "gen_mul_ops_cg.cr_op_rs1.mul_all_ones": ("HIT", "10"), "gen_mul_ops_cg.cr_op_same.mul_distinct": ("HIT", "80"),
                "gen_mul_ops_cg.cr_op_same.mulh_all_same": ("UNHIT", "0"), "gen_mul_ops_cg.cr_op_same.c_mul_distinct": ("UNHIT", "0"),
                "gen_mul_ops_cg.cr_extremes.c_mul_pos_rand_all_ones": ("HIT", "1"), "gen_isa_shift_cg.cr_sra_sign.sra_msb_only_s0": ("UNHIT", "0"),
                "gen_mul_ops_cg.cp_op.mul": ("HIT", None), "gen_mul_ops_cg.cr_op_same.no_such_bin": ("MISSING-FROM-REPORT", "n/a")}
        sm = d / "gen_selftest_sample.fcov.yaml"
        sm.write_text("test: gen_selftest_sample\nowner: runtime\nbins:\n" + "".join(f"  - {b}\n" for b in want) + "anti_vacuity:\n" + "".join(f"  {b}: x\n" for b in want), encoding="utf-8")
        before_s = run_checker(sm, None, None, d / "sample_before.log", report_dir=rep_s)
        after_s = run_checker(sm, None, None, d / "sample_after.log", report_dir=derived_s)
        got = {b: (after_s["bins"][b]["state"], after_s["bins"][b]["count"] if want[b][1] is not None else None) for b in want}
        cross_before = {b: before_s["bins"][b]["state"] for b in want if ".cr_" in b}
        cond = (got == want and all(s == "MISSING-FROM-REPORT" for s in cross_before.values())
                and before_s["bins"]["gen_mul_ops_cg.cp_op.mul"]["state"] == "HIT" and after_s["status"] == "UNHIT"
                and stats_s["cross_sections"] == 12 and stats_s["bins_tables_retitled"] >= 2 and stats_s["cross_rows"] > 100
                and stats_s["name_collisions"] == 0)
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"real sample {CROSS_SAMPLE.name} through the REAL checker: every cross bin MISSING-FROM-REPORT on the raw report; on the derived form gen_mul_ops_cg.cr_op_rd_x0.mul_no is HIT (count 94), a 'Bins'-table bin HIT, bare and bracketed auto rows HIT/UNHIT, a 3-component row UNHIT, a plain variable bin HIT both times, an absent bin MISSING; stats {stats_s}")
        if not cond:
            print("   got:", got, "| cross before:", cross_before)
        # TB Infra's own probe report (T-215 sample): its three-bin manifest passes only through the derived form.
        rep_t = d / "report_tbinfra"; rep_t.mkdir()
        shutil.copyfile(CROSS_SAMPLE_TBINFRA, rep_t / "grpinfo.txt")
        derived_t, stats_t = derived_report(rep_t)
        want_t = {"gen_mul_ops_cg.cp_op.mul": ("HIT", "185"), "gen_mul_ops_cg.cr_op_rd_x0.mul_no": ("HIT", "148"), "gen_isa_alu_reg_cg.cp_op.xor": ("HIT", "148")}
        tm = d / "gen_selftest_tbinfra.fcov.yaml"
        tm.write_text("test: gen_selftest_tbinfra\nowner: runtime\nbins:\n" + "".join(f"  - {b}\n" for b in want_t) + "anti_vacuity:\n" + "".join(f"  {b}: x\n" for b in want_t), encoding="utf-8")
        before_t = run_checker(tm, None, None, d / "tbinfra_before.log", report_dir=rep_t)
        after_t = run_checker(tm, None, None, d / "tbinfra_after.log", report_dir=derived_t)
        got_t = {b: (after_t["bins"][b]["state"], after_t["bins"][b]["count"]) for b in want_t}
        cond = (got_t == want_t and after_t["status"] == "PASS" and before_t["status"] == "UNHIT"
                and before_t["bins"]["gen_mul_ops_cg.cr_op_rd_x0.mul_no"]["state"] == "MISSING-FROM-REPORT"
                and before_t["bins"]["gen_mul_ops_cg.cp_op.mul"]["state"] == "HIT"
                and before_t["bins"]["gen_isa_alu_reg_cg.cp_op.xor"] == {"state": "HIT", "count": "148"}
                and stats_t["cross_sections"] == 21 and stats_t["bins_tables_retitled"] == 12 and stats_t["name_collisions"] == 0)
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"TB Infra's sample {CROSS_SAMPLE_TBINFRA.name} through the REAL checker: raw report UNHIT with the cross bin MISSING-FROM-REPORT and the plain bins HIT (the keyword bin xor read as xor on both reports), derived report PASS 3 of 3 (mul_no HIT 148, mul 185, xor 148); stats {stats_t}")
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
