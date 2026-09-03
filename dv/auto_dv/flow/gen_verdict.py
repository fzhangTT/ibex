#!/usr/bin/env python3
"""Pass/fail authority of the flow: decide a run's verdict from collected failure mechanisms
in the simulation log, never from the simulator exit code alone (SIM_RECIPE Section 5); a
nonzero exit code on an otherwise clean log is one more collected mechanism (FAIL), not a pass.

Rules, in order: a timed-out run is TIMEOUT; any collected failure mechanism (UVM_FATAL or
UVM_ERROR count > 0, an SV $fatal, a VCS runtime error, a cocotb CRITICAL or failing test, an
assertion failure) is FAIL; a missing end-of-test marker is FAIL; otherwise PASS. An
expected-fail test that FAILs is XFAIL; one that PASSes is reported FAIL (unexpected pass).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import gen_flow_const as C


def scan_log(lines: list[str], pass_marker: str | None) -> dict[str, Any]:
    """Return {verdict, reason, evidence, uvm_counts, cocotb_summary, finish_seen, marker_seen}."""
    uvm_counts: dict[str, int] = {}
    cocotb: dict[str, int] | None = None
    finish_seen = False
    marker_seen = False
    hits: list[tuple[str, int, str]] = []
    for idx, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        m = C.UVM_SUMMARY_RE.match(line)
        if m:
            uvm_counts[m.group(1)] = int(m.group(2))
            if m.group(1) in ("FATAL", "ERROR") and int(m.group(2)) > 0:
                hits.append((f"uvm_{m.group(1).lower()}_count", idx, line))
            continue
        m = C.COCOTB_SUMMARY_RE.search(line)
        if m:
            cocotb = {"tests": int(m.group(1)), "passed": int(m.group(2)),
                      "failed": int(m.group(3)), "skipped": int(m.group(4))}
            if cocotb["failed"] > 0 or cocotb["passed"] == 0:
                hits.append(("cocotb_summary", idx, line))
            continue
        if C.FINISH_RE.match(line):
            finish_seen = True
        if pass_marker and pass_marker in line:
            marker_seen = True
        for name, rx in C.FAIL_PATTERNS:
            if rx.search(line):
                hits.append((name, idx, line))
                break
    out: dict[str, Any] = {"uvm_counts": uvm_counts, "cocotb_summary": cocotb,
                           "finish_seen": finish_seen, "marker_seen": marker_seen,
                           "failure_hits": len(hits)}
    if hits:
        name, idx, line = hits[0]
        out.update(verdict=C.VERDICT_FAIL, reason=f"{name} at sim.log:{idx}", evidence=line[:300])
        return out
    marker_ok = marker_seen if pass_marker else finish_seen
    if not marker_ok:
        want = pass_marker or C.END_MARKER_DEFAULT
        out.update(verdict=C.VERDICT_FAIL, reason=f"end-of-test marker {want!r} not found", evidence="")
        return out
    out.update(verdict=C.VERDICT_PASS, reason="no collected failure mechanism; end marker present",
               evidence="")
    return out


def decide(sim_log: Path, pass_marker: str | None, timed_out: bool, expected_fail: bool = False,
           rc: int | None = None, extra_logs: list[Path] | None = None) -> dict[str, Any]:
    """sim.log (VCS -l) plus the simv stdout capture (cocotb's Python logging bypasses -l)."""
    if not sim_log.is_file():
        return {"verdict": C.VERDICT_FAIL, "reason": "sim.log missing", "evidence": "",
                "uvm_counts": {}, "cocotb_summary": None, "finish_seen": False,
                "marker_seen": False, "failure_hits": 0, "exit_code": rc}
    lines = sim_log.read_text(encoding="utf-8", errors="replace").splitlines()
    for extra in extra_logs or []:
        if extra.is_file():
            lines += extra.read_text(encoding="utf-8", errors="replace").splitlines()
    res = scan_log(lines, pass_marker)
    res["exit_code"] = rc
    if timed_out:
        res.update(verdict=C.VERDICT_TIMEOUT, reason="per-run timeout expired; process group killed")
    elif res["verdict"] == C.VERDICT_PASS and rc not in C.EXIT_CODES_CLEAN:
        res.update(verdict=C.VERDICT_FAIL, reason=f"nonzero exit ({rc}) with clean log")
    if expected_fail:
        if res["verdict"] == C.VERDICT_FAIL:
            res.update(verdict=C.VERDICT_XFAIL, reason="expected-fail: " + res["reason"])
        elif res["verdict"] == C.VERDICT_PASS:
            res.update(verdict=C.VERDICT_FAIL, reason="unexpected PASS of an expected-fail test")
    return res


def self_test() -> int:
    """Exercise the REAL scan_log on fabricated logs; each case names the rule it proves."""
    cases = [
        ("clean smoke", ["GEN_CONFIG_BANNER x", "GEN_SMOKE_PASS", "$finish called from file"],
         "GEN_SMOKE_PASS", C.VERDICT_PASS),
        ("missing marker", ["GEN_CONFIG_BANNER x", "$finish at simulation time 10"],
         "GEN_SMOKE_PASS", C.VERDICT_FAIL),
        ("sv fatal", ["Fatal: \"tb.sv\", 371: tb: at time 5", "GEN_SMOKE_FAIL: no retirement",
                      "GEN_SMOKE_PASS"], "GEN_SMOKE_PASS", C.VERDICT_FAIL),
        ("uvm error count", ["--- UVM Report Summary ---", "UVM_FATAL :    0", "UVM_ERROR :    2",
                             "UVM_WARNING :    0", "$finish at simulation time 10"], None, C.VERDICT_FAIL),
        ("uvm clean", ["UVM_FATAL :    0", "UVM_ERROR :    0", "$finish at simulation time 10"],
         None, C.VERDICT_PASS),
        ("uvm error line", ["UVM_ERROR @ 100: uvm_test_top [SB] mismatch", "UVM_ERROR :    1",
                            "$finish called"], None, C.VERDICT_FAIL),
        ("vcs runtime error", ["Error-[FCIBH] Illegal bin hit", "$finish called"], None, C.VERDICT_FAIL),
        ("cocotb fail", ["** TESTS=1 PASS=0 FAIL=1 SKIP=0 **", "$finish called"], None, C.VERDICT_FAIL),
        ("cocotb pass", ["** TESTS=1 PASS=1 FAIL=0 SKIP=0 **", "$finish called"], None, C.VERDICT_PASS),
        ("cocotb critical", ["CRITICAL Failed to import module", "$finish called"], None, C.VERDICT_FAIL),
        ("no finish", ["GEN_CONFIG_BANNER x"], None, C.VERDICT_FAIL),
        ("marker but no finish", ["GEN_TEST_PASS"], "GEN_TEST_PASS", C.VERDICT_PASS),
    ]
    ok = True
    for name, lines, marker, want in cases:
        got = scan_log(lines, marker)["verdict"]
        flag = "ok " if got == want else "BAD"
        if got != want:
            ok = False
        print(f"SELF-TEST {flag} {name}: want {want} got {got}")
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--sim-log", type=Path)
    ap.add_argument("--pass-marker", default=None)
    ap.add_argument("--timed-out", action="store_true")
    ap.add_argument("--expected-fail", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.sim_log:
        ap.error("--sim-log required")
    res = decide(a.sim_log, a.pass_marker, a.timed_out, a.expected_fail)
    for k, v in res.items():
        print(f"{k}: {v}")
    return 0 if res["verdict"] in (C.VERDICT_PASS, C.VERDICT_XFAIL) else 2


if __name__ == "__main__":
    sys.exit(main())
