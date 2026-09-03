#!/usr/bin/env python3
"""Verdict excerpts of a served request (CM103-m-2): the request manifest's rows plus the collected verdict lines of every
run, written as dv/auto_dv/evidence/gen_acceptance_<tag>_<seq>_verdict_excerpt.log so a reviewer of the commit can read what
the wave produced. The manifests live under dv/auto_dv/work/runtime/results/ (gitignored) and the run artefacts under the
out root (site storage), so a reader with access to both regenerates or checks an excerpt; without them the excerpt is a
copy, verifiable only against the artefacts it names.

  gen_acceptance_excerpt.py --request test-writer-071 --tag b3 [--write | --check]
  gen_acceptance_excerpt.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import tempfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = REPO_ROOT / "dv/auto_dv/work/runtime/results"
EVIDENCE_DIR = REPO_ROOT / "dv/auto_dv/evidence"
SELFTEST_TMP = REPO_ROOT / "dv/auto_dv/work/runtime/selftest_tmp"
# the verdict lines a run's logs contribute: the harness verdict, the fire schedule, the bin list, the UVM totals
KEEP = re.compile(r"GEN_TEST_FIRE fire_schedule_applied|GEN_TEST_BINS n=|GEN_TEST_PASS|GEN_TEST_FAIL|UVM_(ERROR|FATAL) :")
LOGS = ("sim_stdout.log", "sim.log")
NO_LINE = "no collected line"
LINE_MAX = 240


def ascii_only(s: str) -> str:
    return s.encode("ascii", "replace").decode("ascii")


def trunc(line: str, n: int = LINE_MAX) -> str:
    return line if len(line) <= n else line[:n] + f" ...[{len(line) - n} more chars]"


def excerpt_name(tag: str, request: str) -> str:
    return f"gen_acceptance_{tag}_{request.rsplit('-', 1)[-1]}_verdict_excerpt.log"


def render(request: str, tag: str, manifest: dict, results_rel: str) -> str:
    """The excerpt text for one request manifest; every run's logs are read from the manifest's sim_log directory."""
    seq = request.rsplit("-", 1)[-1]
    sms = manifest.get("server_mirror_sync") or {}
    echo = manifest.get("request_echo") or {}
    L = [f"# gen_acceptance_{tag}_{seq}_verdict_excerpt.log: batch-3 acceptance verdicts of request {request} (CM103-m-2)",
         f"# Source: the request manifest {results_rel}/{request}/manifest.yaml (work tree, unmirrored) and each",
         "# run's result.yaml, sim.log and sim_stdout.log under the out root (site storage). Lines are copied, long lines truncated as marked.",
         f"requester: {manifest.get('requester')}   purpose: {manifest.get('purpose')}   scope_decision: {manifest.get('scope_decision')}   status: {manifest.get('status')}",
         f"request tests: {echo.get('tests')}   seeds: {echo.get('seeds')}   coverage: {echo.get('coverage')}",
         f"received_utc: {manifest.get('received_utc')}   finished_utc: {manifest.get('finished_utc')}   regress_rc: {manifest.get('regress_rc')}",
         f"pinned_sha: {sms.get('pinned_sha')}   canary_sha: {sms.get('canary_sha')}   canary_decision: {sms.get('canary_decision')}",
         f"batch_record (work tree): {sms.get('batch_record')}",
         f"regress_outdir: {manifest.get('regress_outdir')}",
         f"regress_cmd: {manifest.get('regress_cmd')}",
         "summary: " + " ".join(f"{k}={v}" for k, v in (manifest.get("summary") or {}).items()),
         "",
         "## manifest rows (test, seed, verdict, reason, wall_s, lsf_job_id, sim_log)"]
    runs = manifest.get("runs") or []
    for r in runs:
        L.append(f"{r.get('test')} | {r.get('seed')} | {r.get('verdict')} | {r.get('reason')} | {r.get('wall_s')} | {r.get('lsf_job_id')} | {r.get('sim_log')}")
    for r in runs:
        rd = Path(r["sim_log"]).parent
        res_path = rd / "result.yaml"
        res = yaml.safe_load(res_path.read_text()) if res_path.exists() else {}
        L += ["", f"## run {r.get('test')} seed {r.get('seed')}: result.yaml" + ("" if res_path.exists() else " (missing)"),
              f"verdict: {res.get('verdict')}   reason: {res.get('reason')}",
              f"exit_code: {res.get('exit_code')}   timed_out: {res.get('timed_out')}   uvm_counts: {res.get('uvm_counts')}   cocotb_summary: {res.get('cocotb_summary')}",
              f"evidence: {trunc(' '.join(str(res.get('evidence') or '').split()))}",
              f"## run {r.get('test')} seed {r.get('seed')}: collected lines of sim_stdout.log and sim.log"]
        for logname in LOGS:
            p = rd / logname
            if not p.exists():
                L.append(f"{logname}: missing")
                continue
            n_before = len(L)
            for i, line in enumerate(p.read_text(errors="replace").splitlines(), 1):
                if KEEP.search(line):
                    L.append(f"{logname}:{i}: {trunc(' '.join(line.split()))}")
            if len(L) == n_before:
                L.append(f"{logname}: {NO_LINE}")
    return ascii_only("\n".join(L) + "\n")


def same_bytes(path: Path, text: str) -> bool:
    """--check compares the committed file byte for byte (read_bytes, so a CRLF rewrite is a difference)."""
    return path.exists() and path.read_bytes() == text.encode()


def excerpt_for(request: str, tag: str, results_dir: Path = RESULTS_DIR) -> str:
    manifest = yaml.safe_load((results_dir / request / "manifest.yaml").read_text())
    rel = results_dir.relative_to(REPO_ROOT).as_posix() if results_dir.is_relative_to(REPO_ROOT) else str(results_dir)
    return render(request, tag, manifest, rel)


def self_test() -> int:
    """A fabricated request tree: one PASS run with lines in both logs, one RED-OK run whose sim.log has no collected line,
    one run with a missing sim.log; the excerpt names each case, is ASCII and deterministic."""
    sys.path.insert(0, str(REPO_ROOT / "dv/auto_dv/flow"))
    import gen_flow_util as U   # the guarded removal of the scratch tree (A-002)
    SELFTEST_TMP.mkdir(parents=True, exist_ok=True)
    d = Path(tempfile.mkdtemp(prefix="gen_excerpt_selftest_", dir=SELFTEST_TMP))
    ok = True
    runs = []
    for name, seed, verdict, stdout_lines, sim_lines in (
            ("gen_test_x", 1, "PASS", ["1 ns INFO GEN_TEST_BINS n=2 a b", "2 ns INFO gen_test_x GEN_TEST_PASS"], ["UVM_ERROR :    0", "UVM_FATAL :    0"]),
            ("gen_test_x_red", 2, "RED-OK", ["AssertionError: GEN_TEST_FAIL gen_test_x: 1 fire-check failure(s): fire_a"], ["nothing collected here"]),
            ("gen_test_x", 3, "PASS", ["3 ns INFO gen_test_x GEN_TEST_PASS"], None)):
        rd = d / "runs" / f"{name}_{seed}"; rd.mkdir(parents=True)
        (rd / "sim_stdout.log").write_text("\n".join(stdout_lines) + "\n")
        if sim_lines is not None:
            (rd / "sim.log").write_text("\n".join(sim_lines) + "\n")
        (rd / "result.yaml").write_text(yaml.safe_dump({"verdict": verdict, "reason": "r", "exit_code": 0, "timed_out": False,
                                                          "evidence": "e\u00e9", "uvm_counts": {}, "cocotb_summary": {}}, allow_unicode=True))
        runs.append({"test": name, "seed": seed, "verdict": verdict, "reason": "r", "wall_s": 1.0, "lsf_job_id": "1", "sim_log": str(rd / "sim.log")})
    manifest = {"requester": "test-writer", "purpose": 1, "scope_decision": "accepted", "status": "done", "request_echo": {"tests": ["gen_test_x"], "seeds": 3, "coverage": False},
                "received_utc": "t0", "finished_utc": "t1", "regress_rc": 0, "server_mirror_sync": {"pinned_sha": "p", "canary_sha": "c", "canary_decision": "accepted", "batch_record": "b"},
                "regress_outdir": str(d), "regress_cmd": "cmd", "summary": {"planned": 3}, "runs": runs}
    text = render("test-writer-999", "zz", manifest, "results")
    text2 = render("test-writer-999", "zz", manifest, "results")
    lines = text.splitlines()
    cond = text == text2 and lines[0].startswith("# gen_acceptance_zz_999_verdict_excerpt.log") and "## manifest rows" in text
    ok &= cond; print("SELF-TEST", "ok " if cond else "BAD", "excerpt is deterministic, named after tag and sequence, carries the manifest rows")
    cond = "sim_stdout.log:1: 1 ns INFO GEN_TEST_BINS n=2 a b" in text and "sim.log:1: UVM_ERROR : 0" in text
    ok &= cond; print("SELF-TEST", "ok " if cond else "BAD", "collected lines carry their log and line number")
    cond = f"sim.log: {NO_LINE}" in text and "sim.log: missing" in text and "nothing collected here" not in text
    ok &= cond; print("SELF-TEST", "ok " if cond else "BAD", f"a log without a collected line says '{NO_LINE}' (CM110-L-2); a missing log says so; uncollected lines are not copied")
    cond = not [c for c in text.encode() if c > 127] and "evidence: e?" in text
    ok &= cond; print("SELF-TEST", "ok " if cond else "BAD", "output is ASCII (a non-ASCII byte becomes '?')")
    cond = excerpt_name("b3", "test-writer-071") == "gen_acceptance_b3_071_verdict_excerpt.log"
    ok &= cond; print("SELF-TEST", "ok " if cond else "BAD", "excerpt file name")
    exact, crlf, missing = d / "exact.log", d / "crlf.log", d / "missing.log"
    exact.write_bytes(text.encode()); crlf.write_bytes(text.replace("\n", "\r\n").encode())
    cond = same_bytes(exact, text) and not same_bytes(crlf, text) and not same_bytes(missing, text)
    ok &= cond; print("SELF-TEST", "ok " if cond else "BAD", "--check compares bytes: an exact copy is same, a CRLF rewrite and a missing file differ (CM115-I-1)")
    U.remove_tree_guarded(d, (SELFTEST_TMP,), "self-test dir")
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--request", action="append", default=[], help="request name, e.g. test-writer-071 (repeatable)")
    ap.add_argument("--tag", default="b3", help="wave tag in the excerpt file name")
    ap.add_argument("--write", action="store_true", help="write dv/auto_dv/evidence/<excerpt> (default: print the sha256 only)")
    ap.add_argument("--check", action="store_true", help="exit 1 when the committed excerpt differs from a fresh render")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.request:
        ap.error("--request is required")
    rc = 0
    for req in a.request:
        text = excerpt_for(req, a.tag)
        out = EVIDENCE_DIR / excerpt_name(a.tag, req)
        digest = hashlib.sha256(text.encode()).hexdigest()
        if a.write:
            out.write_text(text)
            print(f"wrote {out} sha256 {digest[:12]}")
        elif a.check:
            same = same_bytes(out, text)
            print(f"{'same' if same else 'DIFFERS'} {out} (fresh render sha256 {digest[:12]})")
            rc |= 0 if same else 1
        else:
            print(f"{out.name} sha256 {digest[:12]} ({text.count(chr(10))} lines; --write to store, --check to compare)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
