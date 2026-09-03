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
import re
import sys
from pathlib import Path
from typing import Any

import gen_flow_const as C


def marker_matches(line: str, marker: str) -> bool:
    """The marker is the last whole token of the line (SV $display prints it alone; cocotb logging
    prefixes time, level and logger). A message that merely quotes the marker does not count."""
    return re.search(r"(^|\s)" + re.escape(marker) + r"\s*$", line) is not None


def scan_log(lines: list[str], pass_marker: str | None, build_config: str | None = None) -> dict[str, Any]:
    """Return {verdict, reason, evidence, uvm_counts, cocotb_summary, finish_seen, marker_seen,
    banner_seen, banner}. PASS requires: no collected failure mechanism, the end marker, and the
    time-zero config banner naming the expected build configuration (P-09)."""
    uvm_counts: dict[str, int] = {}
    cocotb: dict[str, int] | None = None
    finish_seen = False
    marker_seen = False
    banner_seen = build_config is None
    banner: list[str] = []
    hits: list[tuple[str, int, str]] = []
    banner_line = f"{C.BANNER_TAG} build_config={build_config}" if build_config else None
    for idx, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        if line.startswith(C.BANNER_TAG):
            banner.append(line)
            if banner_line and line.strip() == banner_line:
                banner_seen = True
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
        if pass_marker and marker_matches(line, pass_marker):
            marker_seen = True
        for name, rx in C.FAIL_PATTERNS:
            if rx.search(line):
                hits.append((name, idx, line))
                break
    out: dict[str, Any] = {"uvm_counts": uvm_counts, "cocotb_summary": cocotb,
                           "finish_seen": finish_seen, "marker_seen": marker_seen,
                           "banner_seen": banner_seen, "banner": banner, "failure_hits": len(hits)}
    if hits:
        name, idx, line = hits[0]
        out.update(verdict=C.VERDICT_FAIL, reason=f"{name} at log line {idx}", evidence=line[:300])
        return out
    marker_ok = marker_seen if pass_marker else finish_seen
    if not marker_ok:
        want = pass_marker or C.END_MARKER_DEFAULT
        out.update(verdict=C.VERDICT_FAIL, reason=f"end-of-test marker {want!r} not found", evidence="")
        return out
    if not banner_seen:
        out.update(verdict=C.VERDICT_FAIL, reason=f"config banner {banner_line!r} not found", evidence="")
        return out
    out.update(verdict=C.VERDICT_PASS, reason="no collected failure mechanism; end marker and config banner present",
               evidence="")
    return out


def crash_signature(paths: list[Path]) -> str | None:
    for p in paths:
        if p.is_file():
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                if C.CRASH_RE.search(line):
                    return f"{p.name}: {line.strip()[:200]}"
    return None


def decide_lines(lines: list[str], pass_marker: str | None, timed_out: bool, rc: int | None,
                 build_config: str | None, stderr_lines: list[str], sim_log_present: bool = True,
                 expected_fail: bool = False) -> dict[str, Any]:
    """The verdict rules on in-memory text (the self-test drives this with real log excerpts)."""
    if not sim_log_present and not timed_out:
        return {"verdict": C.VERDICT_FAIL, "reason": "sim.log missing", "evidence": "",
                "uvm_counts": {}, "cocotb_summary": None, "finish_seen": False, "marker_seen": False,
                "banner_seen": False, "banner": [], "failure_hits": 0, "exit_code": rc, "crash_signature": None}
    res = scan_log(lines, pass_marker, build_config)
    res["exit_code"] = rc
    crash = next((l.strip()[:200] for l in stderr_lines if C.CRASH_RE.search(l)), None)
    res["crash_signature"] = crash
    if timed_out:
        res.update(verdict=C.VERDICT_TIMEOUT,
                   reason="per-run timeout expired; simulator killed" + ("" if sim_log_present else " before sim.log existed"))
    elif res["verdict"] == C.VERDICT_PASS and crash:
        res.update(verdict=C.VERDICT_FAIL, reason=f"crash signature in stderr: {crash}")
    elif res["verdict"] == C.VERDICT_PASS and not (res["finish_seen"] or rc == 0):
        res.update(verdict=C.VERDICT_FAIL, reason=f"unexplained exit code {rc}: marker present but no $finish and rc != 0")
    elif res["verdict"] == C.VERDICT_PASS and rc not in C.EXIT_CODES_CLEAN:
        res.update(verdict=C.VERDICT_FAIL, reason=f"unexplained exit code {rc} with clean log")
    if expected_fail:
        if res["verdict"] == C.VERDICT_FAIL:
            res.update(verdict=C.VERDICT_XFAIL, reason="expected-fail: " + res["reason"])
        elif res["verdict"] == C.VERDICT_PASS:
            res.update(verdict=C.VERDICT_FAIL, reason="unexpected PASS of an expected-fail test")
    return res


def decide(sim_log: Path, pass_marker: str | None, timed_out: bool, expected_fail: bool = False,
           rc: int | None = None, extra_logs: list[Path] | None = None, build_config: str | None = None,
           stderr_logs: list[Path] | None = None) -> dict[str, Any]:
    """sim.log (VCS -l) plus the simv stdout capture (cocotb's Python logging bypasses -l); crash
    signatures from lsf.err/run.log; PASS needs marker AND ($finish seen OR exit code 0) (P-02)."""
    lines = sim_log.read_text(encoding="utf-8", errors="replace").splitlines() if sim_log.is_file() else []
    for extra in extra_logs or []:
        if extra.is_file():
            lines += extra.read_text(encoding="utf-8", errors="replace").splitlines()
    stderr_lines: list[str] = []
    for p in stderr_logs or []:
        if p.is_file():
            stderr_lines += p.read_text(encoding="utf-8", errors="replace").splitlines()
    return decide_lines(lines, pass_marker, timed_out, rc, build_config, stderr_lines, sim_log.is_file(), expected_fail)


BANNER = "GEN_CONFIG_BANNER build_config=opentitan"
# Real sim.log excerpts from the P-01 red runs (t038_red/*, gen_smoke build of regress_t027_smoke_recheck).
REAL_FATAL = [
    "GEN_SMOKE: max_cycles=1 boot_addr=0x80000000",
    "GEN_SMOKE: retired=0 alerts=0 core_busy=On irq_pending=0 data_tag_o=0",
    'Fatal: "/localdev/fzhang/ws/ibex-challenge/dv/auto_dv/tb/gen_smoke_tb_top.sv", 386: gen_smoke_tb_top: at time 55000 ps',
    "GEN_SMOKE_FAIL: no RVFI retirement observed",
    '$finish called from file "/localdev/fzhang/ws/ibex-challenge/dv/auto_dv/tb/gen_smoke_tb_top.sv", line 386.',
    "$finish at simulation time                 5500",
]
REAL_GREEN = [
    "GEN_SMOKE: max_cycles=3000 boot_addr=0x80000000",
    "GEN_SMOKE: retired=2995 alerts=0 core_busy=On irq_pending=0 data_tag_o=0",
    "GEN_SMOKE_PASS",
    '$finish called from file "/localdev/fzhang/ws/ibex-challenge/dv/auto_dv/tb/gen_smoke_tb_top.sv", line 390.',
    "$finish at simulation time              3004500",
]
# Real cocotb stdout lines (t027_cocotb, LSF job 10930476).
REAL_COCOTB = [
    "  2055.00ns INFO     cocotb.gen_smoke_tb_top            GEN_COCOTB_PROBE_PASS",
    "  2055.01ns INFO     cocotb.regression                  gen_cocotb_probe passed",
    "                                                        ** TESTS=1 PASS=1 FAIL=0 SKIP=0                                    2055.01           0.10      21542.04  **",
    "$finish at simulation time               205501",
]


def self_test() -> int:
    """Exercise the REAL decide_lines on real log excerpts; each case names the rule it pins."""
    B = [BANNER]
    cases = [
        # name, lines, marker, rc, timed_out, stderr, sim_log_present, want
        ("real green smoke (job 10930765)", B + REAL_GREEN, "GEN_SMOKE_PASS", 0, False, [], True, C.VERDICT_PASS),
        ("real $fatal smoke (job 10930762): Fatal line + GEN_SMOKE_FAIL, rc 0", B + REAL_FATAL, "GEN_SMOKE_PASS", 0, False, [], True, C.VERDICT_FAIL),
        ("real timeout (job 10930764): rc 124, no sim.log", [], "GEN_SMOKE_PASS", 124, True, [], False, C.VERDICT_TIMEOUT),
        ("real missing marker (job 10930763)", B + REAL_GREEN, "GEN_NEVER_PRINTED", 0, False, [], True, C.VERDICT_FAIL),
        ("real cocotb probe (job 10930476)", B + REAL_COCOTB, "GEN_COCOTB_PROBE_PASS", 0, False, [], True, C.VERDICT_PASS),
        ("marker but no $finish and rc 0 (P-02: rc 0 counts as clean end)", B + ["GEN_SMOKE_PASS"], "GEN_SMOKE_PASS", 0, False, [], True, C.VERDICT_PASS),
        ("marker but no $finish and no rc (P-02 flipped case 12)", B + ["GEN_SMOKE_PASS"], "GEN_SMOKE_PASS", None, False, [], True, C.VERDICT_FAIL),
        ("marker, $finish, rc 139 (P-02 unexplained exit code)", B + REAL_GREEN, "GEN_SMOKE_PASS", 139, False, [], True, C.VERDICT_FAIL),
        ("clean log, crash signature in stderr (P-02)", B + REAL_GREEN, "GEN_SMOKE_PASS", 0, False, ["bash: line 1: 12345 Segmentation fault      (core dumped) vcs_simv"], True, C.VERDICT_FAIL),
        ("marker quoted inside a message is not the marker (P-02)", B + ["waiting for GEN_SMOKE_PASS marker", "$finish called"], "GEN_SMOKE_PASS", 0, False, [], True, C.VERDICT_FAIL),
        ("no config banner (P-09)", REAL_GREEN, "GEN_SMOKE_PASS", 0, False, [], True, C.VERDICT_FAIL),
        ("wrong config in banner (P-09)", ["GEN_CONFIG_BANNER build_config=small"] + REAL_GREEN, "GEN_SMOKE_PASS", 0, False, [], True, C.VERDICT_FAIL),
        ("sim.log missing without timeout", [], "GEN_SMOKE_PASS", 1, False, [], False, C.VERDICT_FAIL),
        ("uvm error count", B + ["--- UVM Report Summary ---", "UVM_FATAL :    0", "UVM_ERROR :    2", "$finish at simulation time 10"], None, 0, False, [], True, C.VERDICT_FAIL),
        ("uvm clean", B + ["UVM_FATAL :    0", "UVM_ERROR :    0", "$finish at simulation time 10"], None, 0, False, [], True, C.VERDICT_PASS),
        ("uvm error line", B + ["UVM_ERROR @ 100: uvm_test_top [SB] mismatch", "UVM_ERROR :    1", "$finish called"], None, 0, False, [], True, C.VERDICT_FAIL),
        ("vcs runtime error", B + ["Error-[FCIBH] Illegal bin hit", "$finish called"], None, 0, False, [], True, C.VERDICT_FAIL),
        ("cocotb fail summary", B + ["** TESTS=1 PASS=0 FAIL=1 SKIP=0 **", "$finish called"], None, 0, False, [], True, C.VERDICT_FAIL),
        ("cocotb critical", B + ["CRITICAL Failed to import module", "$finish called"], None, 0, False, [], True, C.VERDICT_FAIL),
        ("no $finish, no marker", B, None, 0, False, [], True, C.VERDICT_FAIL),
    ]
    ok = True
    for name, lines, marker, rc, timed_out, stderr, present, want in cases:
        got = decide_lines(lines, marker, timed_out, rc, "opentitan", stderr, present)["verdict"]
        flag = "ok " if got == want else "BAD"
        ok &= got == want
        print(f"SELF-TEST {flag} {name}: want {want} got {got}")
    # File-based decide(): the path gen_run.py takes (sim.log, stdout capture, stderr logs on disk).
    import tempfile
    with tempfile.TemporaryDirectory(prefix="gen_verdict_selftest_") as td:
        d = Path(td)
        (d / "sim.log").write_text("\n".join(B + REAL_GREEN) + "\n", encoding="utf-8")
        (d / "sim_stdout.log").write_text("", encoding="utf-8")
        (d / "lsf.err").write_text("", encoding="utf-8")
        file_cases = [
            ("decide(): clean log, rc 0", 0, False, "", C.VERDICT_PASS),
            ("decide(): clean log, rc 1", 1, False, "", C.VERDICT_FAIL),
            ("decide(): rc 124 + timed_out", 124, True, "", C.VERDICT_TIMEOUT),
            ("decide(): clean log, crash in lsf.err", 0, False, "bash: line 1: 4242 Segmentation fault      (core dumped)", C.VERDICT_FAIL),
        ]
        for name, rc, timed_out, err_text, want in file_cases:
            (d / "lsf.err").write_text(err_text + ("\n" if err_text else ""), encoding="utf-8")
            got = decide(d / "sim.log", "GEN_SMOKE_PASS", timed_out, False, rc, extra_logs=[d / "sim_stdout.log"],
                         build_config="opentitan", stderr_logs=[d / "lsf.err"])["verdict"]
            flag = "ok " if got == want else "BAD"
            ok &= got == want
            print(f"SELF-TEST {flag} {name}: want {want} got {got}")
        (d / "sim.log").unlink()
        got = decide(d / "sim.log", "GEN_SMOKE_PASS", True, False, 124, build_config="opentitan")["verdict"]
        ok &= got == C.VERDICT_TIMEOUT
        print(f"SELF-TEST {'ok ' if got == C.VERDICT_TIMEOUT else 'BAD'} decide(): no sim.log + timed_out: want TIMEOUT got {got}")
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
    res = decide(a.sim_log, a.pass_marker, a.timed_out, a.expected_fail, build_config=C.BUILD_CONFIG)
    for k, v in res.items():
        print(f"{k}: {v}")
    return 0 if res["verdict"] in (C.VERDICT_PASS, C.VERDICT_XFAIL) else 2


if __name__ == "__main__":
    sys.exit(main())
