#!/usr/bin/env python3
"""One-run F-1 pass of the exclusion file for a measured round (gen_exclusions_README.md sections 3, 7).

Usage, from the clone root with the tools of ci/env.sh:
    bash -lc 'source ci/env.sh && python3 dv/auto_dv/excl/gen_excl_f1_pass.py --round-dir dv/auto_dv/evidence/gen_round_1'
    (file names inside the round directory come from dv/auto_dv/flow/gen_flow_const.py ROUND_EV_*)
    ... --dry-run    rehearsal or unmeasured round: outputs only under the work dir, no EC-3 fill
    ... --self-test  dry run on gen_round_0_rebaseline; checks entry-set identity with the current file,
                     a clean strict load and a fully resolved Block join

Steps: round manifest -> merged vdb and its module dump (out-tree, the _module files are not copied
into evidence) -> gen_excl_select.py with the EC-3 fill from the round's asserts evidence copy -> strict load
with urg, any attempts.log fed back as a refutation input (bounded loop) -> plain load -> gated rows
without/with the file -> Block no-op join against the plain report (CM-3 / Critic L-3) -> constfile
copies (B.7 rule 3) -> README delta text and a summary YAML under dv/auto_dv/work/rtl-arch/gen_excl_f1_<tag>/.
Report-time urg only; LSF is never touched. README prose is never edited by this script: the delta
file holds the text for the author, the COUNTS block is rewritten by the generator as before.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "dv/auto_dv/flow"))
sys.path.insert(0, str(ROOT / "dv/auto_dv/excl"))
import gen_flow_const as C          # round-evidence file names: one home, no literals here
from gen_excl_select import URG_DUMP_MODULE_PREFIX   # URG's out-tree module dump names, defined once by their parser
EXCL = ROOT / "dv/auto_dv/excl"
GEN = EXCL / "gen_excl_select.py"
EL = EXCL / "gen_exclusions.el"
REPORT = EXCL / "gen_exclusions_select_report.md"
README = EXCL / "gen_exclusions_README.md"
PRECHECK = EXCL / "gen_precheck"
WORK_ROOT = ROOT / "dv/auto_dv/work/rtl-arch"
# The refutation inputs named in README section 1; the pass-1 log is header-form and must not seed the set.
SEED_ATTEMPTS = [PRECHECK / f"gen_attempts_round0_rebaseline_pass{i}.log" for i in (2, 3, 4)]
DEFAULT_LEAVES = ("u_ibex_core", "u_register_file")   # R-001 gated scopes
METRICS = ("line", "cond", "toggle", "fsm", "branch", "assert")
URG_TIMEOUT_S = 900
VERSION = "1"
# Per-object join scope of this version; the metrics below are the next steps, listed in every delta.
JOIN_SCOPE = "Block entries (LINE metric)"
NEXT_STEPS = ("Branch vectors: join each vector with the branch table row of its line in the plain report",
              "Condition vectors: join each vector with the cond table row (sub-expression index and values) of its line",
              "Toggle entries: join each port or field with the toggle table of the module (per bit and edge)",
              "FSM entries: join each state and transition with the FSM table of the module")


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def sh(cmd, timeout=URG_TIMEOUT_S):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def die(msg):
    sys.exit(f"gen_excl_f1_pass: {msg}")


def load_yaml(p):
    import yaml
    return yaml.safe_load(Path(p).read_text()) or {}


def round_inputs(round_dir, dry_run):
    """The merged vdb, its report dir, the module dump dir and the gated leaves of the round."""
    man = round_dir / C.ROUND_EV_REGRESS_MANIFEST
    if not man.is_file():
        die(f"{man} missing")
    m = load_yaml(man)
    cov = m.get("coverage") or {}
    measured = bool(cov.get("dashboard_txt")) and cov.get("status") == "ok"
    if not measured:
        if not dry_run:
            die(f"{man}: no measured merge (coverage.status={cov.get('status')!r}); an F-1 pass needs a measured round, use --dry-run to rehearse")
        cov = cov.get("unmeasured") or cov
    vdb = cov.get("merged_vdb")
    report_dir = cov.get("report_dir")
    if not vdb or not Path(vdb).exists():
        die(f"merged vdb not found: {vdb!r} (manifest {man})")
    dump = None
    for d in cov.get("full_exclusions_dump") or []:
        if Path(d).name.startswith(URG_DUMP_MODULE_PREFIX):
            dump = Path(d).parent
            break
    if dump is None and report_dir:
        cand = Path(report_dir).parent / C.URG_DUMP_DIRNAME
        if (cand / f"{URG_DUMP_MODULE_PREFIX}line").is_file():
            dump = cand
    if dump is None or not (dump / f"{URG_DUMP_MODULE_PREFIX}line").is_file():
        die(f"module dump ({URG_DUMP_MODULE_PREFIX}*) not found beside {report_dir}; the round must run with -dump {C.URG_DUMP_DIRNAME} (purpose 4)")
    leaves = tuple(k.split(".")[-1] for k in (cov.get("dut_scope") or {}).keys()) or DEFAULT_LEAVES
    return {"manifest": str(man), "measured": measured, "vdb": vdb, "report_dir": report_dir, "dump": str(dump),
            "leaves": leaves, "git_head": m.get("git", {}).get("head") if isinstance(m.get("git"), dict) else None}


def entry_set(el_path):
    """Sorted (module, entry line) pairs of an .el; annotations, checksums and comments ignored."""
    out, mod = [], None
    for raw in Path(el_path).read_text().splitlines():
        t = raw.strip()
        if t.startswith("MODULE:"):
            mod = t.split()[1]
        elif t and not t.startswith(("//", "CHECKSUM:", "ANNOTATION_BEGIN", "ANNOTATION_END")) and mod:
            out.append((mod, t))
    return sorted(out)


def run_generator(dump, out, report, attempts, ec3_asserts, ec3_round, readme):
    cmd = [sys.executable, str(GEN), "--dump", str(dump), "--out", str(out), "--report", str(report)]
    for a in attempts:
        cmd += ["--attempts", str(a)]
    if ec3_asserts:
        cmd += ["--ec3-asserts", str(ec3_asserts), "--ec3-round", ec3_round]
    if readme:
        cmd += ["--readme", str(readme)]
    rc, so, se = sh(cmd, timeout=600)
    return rc, so, se, " ".join(cmd)


def urg_load(vdb, el, report_dir, log):
    """Report-time urg; with el the load is strict. Returns rc, UCAPI counts and the attempts.log path if any."""
    report_dir.mkdir(parents=True, exist_ok=True)
    cmd = ["urg", "-full64", "-format", "text", "-dir", str(vdb)]
    if el:
        cmd += ["-elfile", str(el), "-excl_strict"]
    cmd += ["-show", "ratios", "-report", str(report_dir), "-log", str(log)]
    rc, so, se = sh(cmd)
    text = (Path(log).read_text(errors="replace") if Path(log).is_file() else "") + so + se
    att = report_dir / "attempts.log"
    return {"cmd": " ".join(cmd), "rc": rc, "ucapi_warnings": len(re.findall(r"Warning-\[UCAPI", text)),
            "ucapi_errors": len(re.findall(r"Error-\[UCAPI", text)), "attempts_log": str(att) if att.is_file() else None,
            "log": str(log), "report_dir": str(report_dir)}


def hier_rows(hier_txt, leaves):
    """Per gated leaf: metric -> (covered, total) from the URG hierarchy text (exclusion marker stripped)."""
    rows, cols = {}, []
    for line in Path(hier_txt).read_text(errors="replace").splitlines():
        toks = line.split()
        if not toks:
            continue
        if all(t in ("SCORE", "LINE", "COND", "TOGGLE", "FSM", "BRANCH", "ASSERT", "GROUP") for t in toks):
            cols = [t.lower() for t in toks]
            continue
        name = re.sub(r"\(x\)$|\(X\)$", "", toks[-1])
        if cols and name in leaves and name not in rows:
            vals, i, row = toks[:-1], 0, {}
            for c in cols:
                if c == "score":
                    i += 1
                    continue
                if i < len(vals) and vals[i] == "--":
                    i += 2
                    continue
                if i + 1 < len(vals) and re.match(r"^\d+/\d+$", vals[i + 1]):
                    a, b = vals[i + 1].split("/")
                    row[c] = (int(a), int(b))
                    i += 2
                else:
                    i += 1
            rows[name] = row
    missing = [l for l in leaves if l not in rows]
    if missing:
        die(f"gated leaves {missing} not found in {hier_txt}")
    return rows


def gate_row(rows):
    """Sum of covered and of total per metric over the disjoint gated scopes (the Runtime's gate rule)."""
    out = {}
    for m in METRICS:
        c = t = 0
        seen = False
        for r in rows.values():
            if m in r:
                c += r[m][0]
                t += r[m][1]
                seen = True
        if seen:
            out[m] = f"{c}/{t}"
    return out


def line_status(modinfo_txt):
    """(module, source line) -> (status, source text) from the Line Coverage sections; status is
    'a/b', 'unreachable', 'excluded' or None for a source line without a coverage row."""
    st, mod, in_line = {}, None, False
    for raw in Path(modinfo_txt).read_text(errors="replace").splitlines():
        m = re.match(r"^(\w[\w ]*?) Coverage for Module : (\S+)", raw)
        if m:
            in_line = m.group(1) == "Line"
            mod = re.sub(r"\(x\)$|\(X\)$", "", m.group(2))
            continue
        if raw.startswith("Module : "):
            in_line = False
            continue
        if in_line and mod:
            r = re.match(r"^(\d+)\s+(\d+/\d+|unreachable|excluded)?\s*(?:==>)?\s?(.*)$", raw, re.I)
            if r and (r.group(2) or r.group(3).strip()):
                st[(mod, int(r.group(1)))] = ((r.group(2) or "").lower() or None, r.group(3).strip())
    return st


def norm(t):
    return re.sub(r"\s+", "", t)


def lhs_key(t):
    """Assignment target of a statement (URG normalizes the right-hand side, the target survives)."""
    n = norm(t)
    m = re.match(r"^([^=<]+?)(<=|=)", n)
    return (m.group(1) + m.group(2)) if m else n[:24]


def strip_label(t):
    """Drop a case-item label `NAME:` in front of a statement; a `pkg::name` scope is not a label."""
    return re.sub(r"^\w+\s*:(?!:)\s*", "", t.strip())


def block_status(st, mod, line, sig, window=40):
    """Status of the Block's own row: the dump line when it is a statement line, else the first following
    statement line with the Block's assignment target (the dump line is then a block header)."""
    s = st.get((mod, line))
    if s and s[0]:
        return line, s[0]
    key = lhs_key(sig)
    for l in range(line + 1, line + window):
        s = st.get((mod, l))
        if s and s[0] and lhs_key(strip_label(s[1])) == key:
            return l, s[0]
    return None, None


def block_join(el_path, dump_dir, plain_modinfo):
    """Per Block entry of the .el: its dump line and the plain report's status there (no-op or effective)."""
    sys.path.insert(0, str(EXCL))
    import gen_excl_select as G   # module-level loads read the RTL, the packages and util/ibex_config.py
    by_key = {}
    for e in G.parse(str(dump_dir)):
        if e.metric == "line":
            by_key[(e.mod, e.header.strip())] = e.line
    st = line_status(plain_modinfo)
    rows = []
    for mod, t in entry_set(el_path):
        if not t.startswith("Block "):
            continue
        line = by_key.get((mod, t))
        sig = t.split('"')[3] if t.count('"') >= 4 else ""
        row_line, s = block_status(st, mod, line, sig) if line else (None, None)
        if line is None:
            cls = "UNRESOLVED-DUMP"        # entry text not found in the round's module dump
        elif s is None:
            cls = "UNRESOLVED-REPORT"      # no coverage row carrying the signature after the header line
        elif s == "unreachable":
            cls = "NO-OP"                  # constant analysis had already removed the object
        elif s.startswith("0/"):
            cls = "EFFECTIVE"
        else:
            cls = "ANOMALY"                # covered object excluded: the strict load should have refused it
        line = f"{line}->{row_line}" if row_line and row_line != line else line
        rows.append({"module": mod, "line": line, "status": s, "class": cls, "entry": t})
    return rows


def constfiles(round_dir, work):
    """constfile.txt of every build of the round, copied beside the pass outputs with its sha256."""
    out = []
    bm_pre, bm_suf = C.ROUND_EV_BUILD_MANIFEST_FMT.split("{build}")
    for bm in sorted(round_dir.glob(C.ROUND_EV_BUILD_MANIFEST_FMT.format(build="*"))):
        build = bm.name[len(bm_pre):-len(bm_suf)]
        b = load_yaml(bm)
        cf = b.get("constfile")
        if cf and Path(cf).is_file():
            dst = work / f"gen_constfile_{build}.txt"
            shutil.copyfile(cf, dst)
            out.append({"build": build, "source": cf, "copy": str(dst), "sha256": sha256(dst)})
        else:
            out.append({"build": build, "source": cf, "copy": None, "sha256": None})
    return out


def kinds(el_path):
    k = {}
    for _m, t in entry_set(el_path):
        k[t.split()[0]] = k.get(t.split()[0], 0) + 1
    return k


def write_delta(work, tag, S):
    """README text for the author (pass row, gated rows, flow bullet, section 4 and 7 wording, join summary)."""
    g0, g1 = S["gate_without"], S["gate_with"]
    k = S["kinds"]
    ec3 = S["ec3"]
    L = [f"# README delta for the F-1 pass {tag} (generated {S['generated_utc']}; paste into gen_exclusions_README.md, do not link this file)", ""]
    L += ["## Section 3, pass table row", "",
          f"| {S['pass_label']} | F-1 regeneration against the {tag} dump ({S['inputs']['dump']}); EC-3 {ec3['summary']} "
          f"| urg rc {S['strict']['rc']}, {S['strict']['ucapi_warnings']} UCAPI warnings, {S['strict']['ucapi_errors']} UCAPI errors, "
          f"attempts file: {'yes' if S['strict']['attempts_log'] else 'no'}, refutation iterations {S['iterations']} "
          f"(gen_precheck_urg_{tag}.log, gen_precheck_dashboard_{tag}.txt) |", ""]
    L += ["## Section 3, gated rows (from the plain and the strict urg reports of this pass)", "",
          "| Metric | without the file | with this file | objects removed | entries emitted |", "|---|---|---|---|---|"]
    emitted = {"line": f"{k.get('Block', 0)} Blocks", "cond": f"{k.get('Condition', 0)} vectors", "toggle": f"{k.get('Toggle', 0)} ports/fields",
               "fsm": f"{k.get('Transition', 0)} Transition (+{k.get('State', 0)} State)", "branch": f"{k.get('Branch', 0)} vectors", "assert": f"{k.get('Assert', 0)}"}
    for m in METRICS:
        a, b = g0.get(m, "-/-"), g1.get(m, "-/-")
        rem = (int(a.split("/")[1]) - int(b.split("/")[1])) if "/" in a and "/" in b and "-" not in a + b else "n/a"
        L.append(f"| {m.upper()} | {a} | {b} | {rem} | {emitted[m]} |")
    L += ["", "## Section 3, flow record bullet (fill the Runtime manifest fields when served)", "",
          f"- {S['inputs']['manifest']} ({tag}, measured merge {S['inputs']['vdb']}): the file of this pass "
          f"(md5 {S['el_md5']}, sha256 {S['el_sha256']}), author strict load urg rc {S['strict']['rc']}, {S['strict']['ucapi_warnings']} warnings, "
          f"{S['strict']['ucapi_errors']} errors, gated row " + " ".join(f"{m.upper()} {g1.get(m, '-')}" for m in METRICS) +
          "; Runtime elcheck: <request id> (received <utc>, finished <utc>), verdict <ok>.", ""]
    L += ["## Section 4 wording (refuted entries; keep the classes paragraph)", "",
          f"{S['dropped']} entries of the current selection are refuted by the attempts logs in force ({len(S['attempts_used'])} logs: "
          + ", ".join(Path(a).name for a in S["attempts_used"]) + "); the COUNTS block carries the same number.", ""]
    L += ["## Section 7 status (EC-3)", "", ec3["detail"], ""]
    J = S["join"]
    L += ["## No-op join, Block entries (CM-3 / Critic L-3); per-object table in " + S["join_file"], "",
          "| Class | Count | Meaning |", "|---|---|---|",
          f"| NO-OP | {J['NO-OP']} | line already unreachable in the plain report: the entry does not move the denominator |",
          f"| EFFECTIVE | {J['EFFECTIVE']} | line 0/N in the plain report: the entry removes the object |",
          f"| UNRESOLVED-REPORT | {J['UNRESOLVED-REPORT']} | no coverage row on that source line in the plain report |",
          f"| UNRESOLVED-DUMP | {J['UNRESOLVED-DUMP']} | entry text not found in the round's module dump |",
          f"| ANOMALY | {J['ANOMALY']} | covered object excluded (must be 0 after a clean strict load) |", "",
          "", f"NO-OP entries are KEPT in the file, not dropped: the .el is the only place that states the per-object justification "
          f"(annotation record), the strict load proves each entry legal either way, and an explicit entry keeps the exclusion when a "
          f"build's constant analysis (-cm_seqnoconst) decides the line differently. Dropping them would tie the file to one run's "
          f"unreachable set. The {J['NO-OP']} NO-OP entries therefore change no number in the gated rows.", "",
          f"## Driver version and next steps", "",
          f"gen_excl_f1_pass.py version {VERSION}: per-object join for {JOIN_SCOPE} only; Branch, Condition, Toggle and FSM entries "
          f"act through the gated-row delta above until the joins below exist.", ""] + [f"- next: {n}" for n in NEXT_STEPS] + [""]
    L += ["## Files of this pass", ""] + [f"- {f}" for f in S["files"]]
    p = work / f"gen_f1_{tag}_readme_delta.md"
    p.write_text("\n".join(L) + "\n")
    return p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--round-dir", help=f"{C.EVIDENCE_DIR.relative_to(C.REPO_ROOT)}/{C.ROUND_DIR_PREFIX}<n>")
    ap.add_argument("--tag", help="round tag written into the EC-3 fields and file names (default: from the directory name)")
    ap.add_argument("--pass-label", default="<pass>", help="pass number for the README row")
    ap.add_argument("--work-dir", help="default dv/auto_dv/work/rtl-arch/gen_excl_f1_<tag>")
    ap.add_argument("--dry-run", action="store_true", help="write only under the work dir; no EC-3 fill; unmeasured rounds allowed")
    ap.add_argument("--max-iter", type=int, default=3, help="refutation iterations (strict load -> attempts.log -> regenerate)")
    ap.add_argument("--self-test", action="store_true", help="dry run on gen_round_0_rebaseline with checks")
    a = ap.parse_args()
    os.chdir(ROOT)
    if shutil.which("urg") is None:
        die("urg not on PATH: run through bash -lc 'source ci/env.sh && ...'")
    if a.self_test:
        a.round_dir, a.dry_run = str((C.EVIDENCE_DIR / (C.ROUND_DIR_PREFIX + "0_rebaseline")).relative_to(C.REPO_ROOT)), True
    if not a.round_dir:
        die("--round-dir is required")
    round_dir = (ROOT / a.round_dir).resolve()
    tag = a.tag or round_dir.name.replace("gen_", "")
    work = Path(a.work_dir) if a.work_dir else WORK_ROOT / f"gen_excl_f1_{tag}"
    work.mkdir(parents=True, exist_ok=True)
    inputs = round_inputs(round_dir, a.dry_run)
    print(f"[f1] round {tag}: measured={inputs['measured']} vdb={inputs['vdb']}\n[f1] dump {inputs['dump']}\n[f1] work {work}")

    # Targets: the deliverables themselves, or work-dir copies for a rehearsal.
    if a.dry_run:
        el, rep, readme = work / f"gen_exclusions_{tag}.el", work / f"gen_select_report_{tag}.md", work / f"gen_README_{tag}.md"
        shutil.copyfile(README, readme)
    else:
        el, rep, readme = EL, REPORT, README
    before = {"el_md5": md5(EL), "el_sha256": sha256(EL), "entries": entry_set(EL)}

    asserts = round_dir / C.ROUND_EV_ASSERTS
    ec3_asserts = asserts if (inputs["measured"] and not a.dry_run and asserts.is_file()) else None
    ec3 = {"summary": "not filled (dry run)" if a.dry_run else (f"not filled: {C.ROUND_EV_ASSERTS} missing in the round evidence" if inputs["measured"] and not asserts.is_file() else "not filled"),
           "detail": "EC-3 not attempted." if not ec3_asserts else ""}
    attempts = [p for p in SEED_ATTEMPTS if p.is_file()]
    strict = None
    it = 0
    gen_cmd = ""
    while True:
        it += 1
        rc, so, se, gen_cmd = run_generator(inputs["dump"], el, rep, attempts, ec3_asserts, tag, readme)
        if rc != 0 and ec3_asserts and "EC-3 fill refused" in se:
            reason = se.strip().splitlines()[-1]
            ec3 = {"summary": "not filled (refused, class-D groups held out)", "detail": f"EC-3 fill refused by the generator: {reason}"}
            ec3_asserts = None
            rc, so, se, gen_cmd = run_generator(inputs["dump"], el, rep, attempts, None, tag, readme)
        if rc != 0:
            die(f"generator failed (rc {rc}):\n{so[-2000:]}\n{se[-2000:]}")
        (work / f"gen_f1_{tag}_generator_iter{it}.log").write_text(gen_cmd + "\n\n" + so + se)
        if ec3_asserts:
            ec3 = {"summary": f"filled from {asserts.relative_to(ROOT)} ({tag})",
                   "detail": "EC-3 filled: " + "; ".join(l for l in so.splitlines() if "class-D" in l or "attempts" in l.lower())[:600]}
        strict = urg_load(inputs["vdb"], el, work / f"gen_urg_report_with_iter{it}", work / f"gen_f1_{tag}_urg_with_iter{it}.log")
        print(f"[f1] iteration {it}: generator rc 0; strict load rc {strict['rc']} UCAPI w/e {strict['ucapi_warnings']}/{strict['ucapi_errors']} attempts={'yes' if strict['attempts_log'] else 'no'}")
        if strict["rc"] != 0 and strict["ucapi_errors"]:
            die(f"strict load failed with UCAPI errors; see {strict['log']}")
        if not strict["attempts_log"] or it >= a.max_iter:
            break
        keep = (work if a.dry_run else PRECHECK) / f"gen_attempts_{tag}_pass{it}.log"
        shutil.copyfile(strict["attempts_log"], keep)
        attempts.append(keep)
    plain = urg_load(inputs["vdb"], None, work / "gen_urg_report_plain", work / f"gen_f1_{tag}_urg_plain.log")
    if plain["rc"] != 0:
        die(f"plain load failed rc {plain['rc']}; see {plain['log']}")
    g0 = gate_row(hier_rows(Path(plain["report_dir"]) / "hierarchy.txt", inputs["leaves"]))
    g1 = gate_row(hier_rows(Path(strict["report_dir"]) / "hierarchy.txt", inputs["leaves"]))
    join_rows = block_join(el, inputs["dump"], Path(plain["report_dir"]) / "modinfo.txt")
    J = {c: sum(1 for r in join_rows if r["class"] == c) for c in ("NO-OP", "EFFECTIVE", "UNRESOLVED-REPORT", "UNRESOLVED-DUMP", "ANOMALY")}
    join_file = work / f"gen_f1_{tag}_noop_join.md"
    join_file.write_text("\n".join([f"# Block entries of {el.relative_to(ROOT)} joined with the plain report of {tag} (line status before exclusion)", "",
                                    "| Module | RTL line | plain status | class | entry |", "|---|---|---|---|---|"] +
                                   [f"| {r['module']} | {r['line']} | {r['status']} | {r['class']} | `{r['entry'][:100]}` |" for r in join_rows] +
                                   ["", "Classes: " + ", ".join(f"{k} {v}" for k, v in J.items()),
                                    "NO-OP entries are kept in the file for the annotation record (see the README delta)."]) + "\n")
    after = entry_set(el)
    same = after == before["entries"]
    diff_file = work / f"gen_f1_{tag}_entryset_diff.txt"
    b, s_ = set(before["entries"]), set(after)
    diff_file.write_text(f"entry set before: {len(b)} after: {len(s_)} identical: {same}\n" +
                         "".join(f"- {m}: {t}\n" for m, t in sorted(b - s_)) + "".join(f"+ {m}: {t}\n" for m, t in sorted(s_ - b)))
    dropped = 0
    m_ = re.search(r"^Dropped (\d+) entries", Path(rep).read_text(), re.M)
    if m_:
        dropped = int(m_.group(1))
    files = [str(el.relative_to(ROOT)), str(rep.relative_to(ROOT)), str(readme.relative_to(ROOT)), str(join_file.relative_to(ROOT)), str(diff_file.relative_to(ROOT))]
    if not a.dry_run:
        shutil.copyfile(strict["log"], PRECHECK / f"gen_precheck_urg_{tag}.log")
        shutil.copyfile(Path(strict["report_dir"]) / "dashboard.txt", PRECHECK / f"gen_precheck_dashboard_{tag}.txt")
        files += [f"dv/auto_dv/excl/gen_precheck/gen_precheck_urg_{tag}.log", f"dv/auto_dv/excl/gen_precheck/gen_precheck_dashboard_{tag}.txt"]
        files += [str(p.relative_to(ROOT)) for p in attempts if p.parent == PRECHECK and tag in p.name]
    cfs = constfiles(round_dir, work)
    files += [c["copy"].replace(str(ROOT) + "/", "") for c in cfs if c["copy"]]
    S = {"driver_version": VERSION, "generated_utc": now(), "tag": tag, "pass_label": a.pass_label, "dry_run": a.dry_run, "inputs": inputs, "generator_cmd": gen_cmd,
         "iterations": it, "attempts_used": [str(p.relative_to(ROOT)) for p in attempts], "strict": strict, "plain": plain,
         "gate_without": g0, "gate_with": g1, "el_md5": md5(el), "el_sha256": sha256(el), "el_before": {"md5": before["el_md5"], "sha256": before["el_sha256"]},
         "entry_set_identical_to_before": same, "kinds": kinds(el), "dropped": dropped, "ec3": ec3, "join": J, "join_file": str(join_file.relative_to(ROOT)),
         "constfiles": cfs, "files": files}
    delta = write_delta(work, tag, S)
    S["files"].append(str(delta.relative_to(ROOT)))
    import yaml
    (work / f"gen_f1_{tag}_summary.yaml").write_text(yaml.safe_dump(S, sort_keys=False))
    print(f"[f1] gated without {g0}\n[f1] gated with    {g1}\n[f1] entry set identical to the previous file: {same}; join {J}\n[f1] delta {delta}\n[f1] summary {work / f'gen_f1_{tag}_summary.yaml'}")

    if a.self_test:
        checks = {"strict load rc 0": strict["rc"] == 0, "no UCAPI warnings/errors": strict["ucapi_warnings"] == 0 and strict["ucapi_errors"] == 0,
                  "no attempts.log": strict["attempts_log"] is None, "entry set identical to the current file": same,
                  "gated covered counts unchanged by the file": all(g0[m].split("/")[0] == g1[m].split("/")[0] for m in g0 if m in g1),
                  "gated totals never grow with the file": all(int(g0[m].split("/")[1]) >= int(g1[m].split("/")[1]) for m in g0 if m in g1),
                  "every Block resolved, no anomaly": J["ANOMALY"] == 0 and J["UNRESOLVED-DUMP"] == 0 and J["UNRESOLVED-REPORT"] == 0}
        bad = [k for k, v in checks.items() if not v]
        for k, v in checks.items():
            print(f"[self-test] {'ok  ' if v else 'FAIL'} {k}")
        if bad:
            die("self-test FAILED: " + "; ".join(bad))
        print("[self-test] PASS")


if __name__ == "__main__":
    main()
