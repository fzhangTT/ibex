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


def scan_log(lines: list[str], pass_marker: str | None, build_config: str,
             banner_lines: list[str] | None = None, origins: list[tuple[str, int]] | None = None) -> dict[str, Any]:
    """Return {verdict, reason, evidence, uvm_counts, cocotb_summary, finish_seen, marker_seen,
    banner_seen, banner}. PASS requires: no collected failure mechanism, the end marker, and the
    time-zero config banner naming the expected build configuration (P-09; never skippable). The
    banner is collected from `banner_lines` (sim.log only) when given, else from `lines`."""
    if not build_config:
        raise ValueError("scan_log: build_config is required (the banner rule is not skippable)")
    uvm_counts: dict[str, int] = {}
    cocotb: dict[str, int] | None = None
    finish_seen = False
    marker_seen = False
    banner_seen = False
    banner: list[str] = []
    hits: list[tuple[str, int, str]] = []
    banner_line = f"{C.BANNER_TAG} build_config={build_config}"
    for raw in (banner_lines if banner_lines is not None else lines):
        line = raw.rstrip("\n")
        if line.startswith(C.BANNER_TAG):
            banner.append(line)
            if line.strip() == banner_line:
                banner_seen = True
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
        # origins names the file and its own line for every scanned line (sim.log then the stdout capture);
        # without it the index into the scanned text is all there is.
        where = f"{origins[idx - 1][0]}:{origins[idx - 1][1]}" if origins and idx <= len(origins) else f"log line {idx}"
        # evidence is the display form (300 chars); evidence_line is the full line the red_expect regex sees.
        mech = mechanism_id(lines, idx)
        out.update(verdict=C.VERDICT_FAIL, reason=f"{name} at {where}" + (f" ({mech})" if mech else ""),
                   evidence=line[:300], evidence_line=line)
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


def grade_red_fixture(res: dict[str, Any], red_expect: str | None) -> dict[str, Any]:
    """Grade a red fixture's already-decided result. Called by decide_lines for a failure the sim log collected, and
    again after the fcov-expectation check for a failure that has no sim-log line by construction: a declared-but-unhit
    bin fails a run whose simulation passed, so the reason is the only evidence there is.

    Only a FAIL whose evidence matches red_expect is the designed outcome (RED-OK); any other FAIL is a broken
    fixture or environment; PASS means the checker it proves is dead; a TIMEOUT is not the designed failure.
    """
    if res["verdict"] == C.VERDICT_FAIL:
        evidence = res.get("evidence_line") or ""
        if not evidence:
            # No collected line (exit code, crash signature, missing marker or banner): never the designed failure.
            res.update(verdict=C.VERDICT_FAIL, reason=f"red fixture failed for an undeclared reason: {res['reason']}; "
                       "no collected evidence line for red_expect to match")
        elif red_expect and re.search(red_expect, evidence):
            res.update(verdict=C.VERDICT_RED_OK, reason=f"red fixture failed as designed (red_expect matched): {res['reason']}")
        else:
            res.update(verdict=C.VERDICT_FAIL, reason=f"red fixture failed for an undeclared reason: {res['reason']}; "
                       f"red_expect {red_expect!r} does not match the evidence {evidence[:80]!r}")
    elif res["verdict"] == C.VERDICT_PASS:
        res.update(verdict=C.VERDICT_FAIL, reason="red fixture passed unexpectedly: the failure it exists to show did not occur")
    return res


def mechanism_id(lines: list[str], idx: int) -> str | None:
    """The name of the mechanism the failing line at idx (1-based) belongs to, or None. The line's own bracketed
    id when it has one, else the first one within C.MECHANISM_LOOKAHEAD lines below it: a VCS assertion prints its
    source and Offending lines before the UVM_ERROR that names the property. Bounded so a later, unrelated error
    is never attributed to this one."""
    for i in range(idx - 1, min(idx - 1 + 1 + C.MECHANISM_LOOKAHEAD, len(lines))):
        m = C.MECHANISM_ID_RE.match(lines[i])
        if m:
            return m.group(1)
    return None


def decide_lines(lines: list[str], pass_marker: str | None, timed_out: bool, rc: int | None,
                 build_config: str, stderr_lines: list[str], sim_log_present: bool = True,
                 expected_fail: bool = False, banner_lines: list[str] | None = None,
                 red_fixture: bool = False, red_expect: str | None = None,
                 origins: list[tuple[str, int]] | None = None) -> dict[str, Any]:
    """The verdict rules on in-memory text (the self-test drives this with real log excerpts)."""
    if not sim_log_present and not timed_out:
        return {"verdict": C.VERDICT_FAIL, "reason": "sim.log missing", "evidence": "",
                "uvm_counts": {}, "cocotb_summary": None, "finish_seen": False, "marker_seen": False,
                "banner_seen": False, "banner": [], "failure_hits": 0, "exit_code": rc, "crash_signature": None}
    res = scan_log(lines, pass_marker, build_config, banner_lines, origins)
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
    if red_fixture:
        res = grade_red_fixture(res, red_expect)
    return res


def decide(sim_log: Path, pass_marker: str | None, timed_out: bool, expected_fail: bool = False,
           rc: int | None = None, extra_logs: list[Path] | None = None, build_config: str = C.BUILD_CONFIG,
           stderr_logs: list[Path] | None = None, red_fixture: bool = False,
           red_expect: str | None = None) -> dict[str, Any]:
    """sim.log (VCS -l) plus the simv stdout capture (cocotb's Python logging bypasses -l); the
    config banner is taken from sim.log alone; crash signatures from lsf.err/run.log; PASS needs
    marker AND ($finish seen OR exit code 0) (P-02)."""
    sim_lines = sim_log.read_text(encoding="utf-8", errors="replace").splitlines() if sim_log.is_file() else []
    lines = list(sim_lines)
    origins = [(sim_log.name, i) for i in range(1, len(sim_lines) + 1)]
    for extra in extra_logs or []:
        if extra.is_file():
            more = extra.read_text(encoding="utf-8", errors="replace").splitlines()
            lines += more
            origins += [(extra.name, i) for i in range(1, len(more) + 1)]
    stderr_lines: list[str] = []
    for p in stderr_logs or []:
        if p.is_file():
            stderr_lines += p.read_text(encoding="utf-8", errors="replace").splitlines()
    return decide_lines(lines, pass_marker, timed_out, rc, build_config, stderr_lines, sim_log.is_file(),
                        expected_fail, banner_lines=sim_lines, red_fixture=red_fixture, red_expect=red_expect,
                        origins=origins)


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


# Real-shaped kill reports: bash 4.4.20 on soc-l-11 (2026-09-03 08:35Z) running the run_cmd.sh form
# (timeout -k 20 900 <simv> ...) with a stand-in vcs_simv that raised the signal on itself; verbatim.
REAL_SHAPE_SEGV = '/localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/runtime/selftest_tmp/crash_shape/run_cmd_SEGV.sh: line 7: 2853260 Segmentation fault      timeout -k 20 900 /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/runtime/selftest_tmp/crash_shape/vcs_simv_SEGV +vcs+lic+wait +ntb_random_seed=1 > /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/runtime/selftest_tmp/crash_shape/sim_stdout_SEGV.log 2>&1'
REAL_SHAPE_KILL = '/localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/runtime/selftest_tmp/crash_shape/run_cmd_KILL.sh: line 7: 2853999 Killed                  timeout -k 20 900 /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/runtime/selftest_tmp/crash_shape/vcs_simv_KILL +vcs+lic+wait +ntb_random_seed=1 > /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/runtime/selftest_tmp/crash_shape/sim_stdout_KILL.log 2>&1'


# The same two reports with the PID field re-rendered the way bash prints it (%5ld): a PID below 10000
# carries leading spaces.
SHORT_PID_SEGV = '/localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/runtime/selftest_tmp/crash_shape/run_cmd_SEGV.sh: line 7:   537 Segmentation fault      timeout -k 20 900 /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/runtime/selftest_tmp/crash_shape/vcs_simv_SEGV +vcs+lic+wait +ntb_random_seed=1 > /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/runtime/selftest_tmp/crash_shape/sim_stdout_SEGV.log 2>&1'
SHORT_PID_KILL = '/localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/runtime/selftest_tmp/crash_shape/run_cmd_KILL.sh: line 7:     7 Killed                  timeout -k 20 900 /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/runtime/selftest_tmp/crash_shape/vcs_simv_KILL +vcs+lic+wait +ntb_random_seed=1 > /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/runtime/selftest_tmp/crash_shape/sim_stdout_KILL.log 2>&1'


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
        ("fabricated: marker but no $finish and rc 0 (P-02: rc 0 counts as clean end)", B + ["GEN_SMOKE_PASS"], "GEN_SMOKE_PASS", 0, False, [], True, C.VERDICT_PASS),
        ("fabricated: marker but no $finish and no rc (P-02 flipped case 12)", B + ["GEN_SMOKE_PASS"], "GEN_SMOKE_PASS", None, False, [], True, C.VERDICT_FAIL),
        ("fabricated: marker, $finish, rc 139 (P-02 unexplained exit code)", B + REAL_GREEN, "GEN_SMOKE_PASS", 139, False, [], True, C.VERDICT_FAIL),
        ("fabricated: direct simv invocation shape with (core dumped), not the job script's form (P-02)", B + REAL_GREEN, "GEN_SMOKE_PASS", 0, False, ["bash: line 1: 12345 Segmentation fault      (core dumped) vcs_simv"], True, C.VERDICT_FAIL),
        ("fabricated: bare shell kill report, direct simv shape", B + REAL_GREEN, "GEN_SMOKE_PASS", 0, False, ["12345 Killed                  vcs_simv +vcs+lic+wait"], True, C.VERDICT_FAIL),
        ("real-shaped: job-script SIGSEGV report (timeout-wrapped simv), clean log, rc 0", B + REAL_GREEN, "GEN_SMOKE_PASS", 0, False, [REAL_SHAPE_SEGV], True, C.VERDICT_FAIL),
        ("real-shaped: job-script SIGKILL report (timeout-wrapped simv), clean log, rc 0", B + REAL_GREEN, "GEN_SMOKE_PASS", 0, False, [REAL_SHAPE_KILL], True, C.VERDICT_FAIL),
        ("real-shaped: SIGSEGV report with a 3-digit PID (bash %5ld padding)", B + REAL_GREEN, "GEN_SMOKE_PASS", 0, False, [SHORT_PID_SEGV], True, C.VERDICT_FAIL),
        ("real-shaped: SIGKILL report with a 1-digit PID (bash %5ld padding)", B + REAL_GREEN, "GEN_SMOKE_PASS", 0, False, [SHORT_PID_KILL], True, C.VERDICT_FAIL),
        ("real (tb-infra-002, job 10932403): ISS log line with 'Illegal instruction' is NOT a crash", B + REAL_GREEN, "GEN_SMOKE_PASS", 0, False,
         ["               12000: Illegal instruction (hart 0) at PC 0x80000080: 0x00000000"], True, C.VERDICT_PASS),
        ("fabricated: marker quoted inside a message is not the marker (P-02)", B + ["waiting for GEN_SMOKE_PASS marker", "$finish called"], "GEN_SMOKE_PASS", 0, False, [], True, C.VERDICT_FAIL),
        ("fabricated: no config banner (P-09)", REAL_GREEN, "GEN_SMOKE_PASS", 0, False, [], True, C.VERDICT_FAIL),
        ("fabricated: wrong config in banner (P-09)", ["GEN_CONFIG_BANNER build_config=small"] + REAL_GREEN, "GEN_SMOKE_PASS", 0, False, [], True, C.VERDICT_FAIL),
        ("fabricated: sim.log missing without timeout", [], "GEN_SMOKE_PASS", 1, False, [], False, C.VERDICT_FAIL),
        ("fabricated: uvm error count", B + ["--- UVM Report Summary ---", "UVM_FATAL :    0", "UVM_ERROR :    2", "$finish at simulation time 10"], None, 0, False, [], True, C.VERDICT_FAIL),
        ("fabricated: uvm clean", B + ["UVM_FATAL :    0", "UVM_ERROR :    0", "$finish at simulation time 10"], None, 0, False, [], True, C.VERDICT_PASS),
        ("fabricated: uvm error line", B + ["UVM_ERROR @ 100: uvm_test_top [SB] mismatch", "UVM_ERROR :    1", "$finish called"], None, 0, False, [], True, C.VERDICT_FAIL),
        ("fabricated: vcs runtime error", B + ["Error-[FCIBH] Illegal bin hit", "$finish called"], None, 0, False, [], True, C.VERDICT_FAIL),
        ("fabricated: cocotb fail summary", B + ["** TESTS=1 PASS=0 FAIL=1 SKIP=0 **", "$finish called"], None, 0, False, [], True, C.VERDICT_FAIL),
        ("fabricated: cocotb critical", B + ["CRITICAL Failed to import module", "$finish called"], None, 0, False, [], True, C.VERDICT_FAIL),
        ("fabricated: no $finish, no marker", B, None, 0, False, [], True, C.VERDICT_FAIL),
    ]
    ok = True
    for name, lines, marker, rc, timed_out, stderr, present, want in cases:
        got = decide_lines(lines, marker, timed_out, rc, "opentitan", stderr, present)["verdict"]
        flag = "ok " if got == want else "BAD"
        ok &= got == want
        print(f"SELF-TEST {flag} {name}: want {want} got {got}")
    # A red fixture whose only failure is an unmet fcov expectation: the sim log PASSES by construction, so the
    # reason is the only evidence. Graded through grade_red_fixture directly, which is how gen_run reaches it after
    # the fcov check.
    fcov_reason = f"{C.FCOV_UNMET_REASON}: 1 declared bin(s) not hit ['gen_ic_ecc_cg.cp_ram.data']"
    # The reason carries no regex metacharacter, so it goes in unescaped: re.escape would escape the
    # spaces and the loader's rt37 rule, which looks for the reason as a substring, would no longer see it.
    fcov_sig = C.FCOV_UNMET_REASON + r": [0-9]+ declared bin\(s\) not hit .*gen_ic_ecc_cg\.cp_ram\.data"
    r_ok = grade_red_fixture({"verdict": C.VERDICT_FAIL, "reason": fcov_reason, "evidence_line": fcov_reason}, fcov_sig)
    cond = r_ok["verdict"] == C.VERDICT_RED_OK
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD",
          f"an fcov-unmet red fixture grades RED-OK when red_expect matches its reason (got {r_ok['verdict']})")
    other = "fcov expectation unverifiable: per-test isolation not confirmed"
    r_no = grade_red_fixture({"verdict": C.VERDICT_FAIL, "reason": other, "evidence_line": other}, fcov_sig)
    cond = r_no["verdict"] == C.VERDICT_FAIL and "undeclared reason" in r_no["reason"]
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD",
          f"a red fixture failing a DIFFERENT way is not RED-OK (got {r_no['verdict']})")
    # Red fixtures (testlist red_fixture: true): FAIL is the designed outcome, PASS is a dead checker.
    # red_expect is matched against the FIRST collected evidence line (here the Fatal: line, not GEN_SMOKE_FAIL).
    red_fail = decide_lines(B + REAL_FATAL, "GEN_SMOKE_PASS", False, 0, "opentitan", [], True, red_fixture=True,
                            red_expect=r"^Fatal: .*gen_smoke_tb_top")
    red_other = decide_lines(B + REAL_FATAL, "GEN_SMOKE_PASS", False, 0, "opentitan", [], True, red_fixture=True,
                             red_expect=r"GEN_TEST_FAIL gen_test_boot_retire")
    red_none = decide_lines(B + REAL_FATAL, "GEN_SMOKE_PASS", False, 0, "opentitan", [], True, red_fixture=True)
    red_pass = decide_lines(B + REAL_GREEN, "GEN_SMOKE_PASS", False, 0, "opentitan", [], True, red_fixture=True,
                            red_expect=r"GEN_SMOKE_FAIL")
    red_to = decide_lines([], "GEN_SMOKE_PASS", True, 124, "opentitan", [], False, red_fixture=True, red_expect=r"x")
    # No collected line (clean log, rc 139): even a regex matching "" must not make it RED-OK.
    red_empty = decide_lines(B + REAL_GREEN, "GEN_SMOKE_PASS", False, 139, "opentitan", [], True, red_fixture=True, red_expect=r".*")
    # The regex sees the full line: a signature past column 300 still matches.
    long_line = " " * 320 + "AssertionError: GEN_TEST_FAIL gen_x: 1 fire-check failure(s)"
    red_long = decide_lines(B + [long_line], "GEN_SMOKE_PASS", False, 0, "opentitan", [], True, red_fixture=True,
                            red_expect=r"GEN_TEST_FAIL gen_x")
    for name, got, want, needle in (("red fixture: real $fatal log whose evidence matches red_expect is RED-OK", red_fail, C.VERDICT_RED_OK, "red_expect matched"),
                                    ("red fixture: real $fatal log whose red_expect names a LATER line (GEN_TEST_FAIL) is FAIL (undeclared reason)", red_other, C.VERDICT_FAIL, "undeclared reason"),
                                    ("red fixture: no red_expect at all is FAIL (undeclared reason)", red_none, C.VERDICT_FAIL, "undeclared reason"),
                                    ("red fixture: real green log is FAIL (dead checker)", red_pass, C.VERDICT_FAIL, "passed unexpectedly"),
                                    ("red fixture: timeout stays TIMEOUT", red_to, C.VERDICT_TIMEOUT, "timeout"),
                                    ("red fixture: FAIL without a collected line is never RED-OK, even with red_expect '.*'", red_empty, C.VERDICT_FAIL, "no collected evidence line"),
                                    ("red fixture: signature beyond column 300 matches (full line, not the display cut)", red_long, C.VERDICT_RED_OK, "red_expect matched")):
        cond = got["verdict"] == want and needle in got["reason"]
        ok &= cond
        print(f"SELF-TEST {'ok ' if cond else 'BAD'} {name}: want {want} got {got['verdict']} ({got['reason'][:60]})")
    # The crash regex alone: the job script's report shape for every signal word, and the ISS line that stays clean.
    for width, fixture, word in (("7-digit PID", REAL_SHAPE_SEGV, "Segmentation fault"), ("3-digit PID", SHORT_PID_SEGV, "Segmentation fault"),
                                 ("1-digit PID", SHORT_PID_KILL, "Killed")):
        for sig in ("Segmentation fault", "Bus error", "Aborted", "Illegal instruction", "Killed", "Terminated"):
            cond = bool(C.CRASH_RE.search(fixture.replace(word, sig)))
            ok &= cond
            print(f"SELF-TEST {'ok ' if cond else 'BAD'} crash regex matches the job-script report, {width}, {sig!r}")
    cond = not C.CRASH_RE.search("               12000: Illegal instruction (hart 0) at PC 0x80000080: 0x00000000")
    ok &= cond
    print(f"SELF-TEST {'ok ' if cond else 'BAD'} crash regex leaves the ISS 'Illegal instruction (hart 0)' line clean")
    # File-based decide(): the path gen_run.py takes (sim.log, stdout capture, stderr logs on disk).
    import tempfile
    with tempfile.TemporaryDirectory(prefix="gen_verdict_selftest_", dir=C.selftest_tmp()) as td:
        d = Path(td)
        (d / "sim.log").write_text("\n".join(B + REAL_GREEN) + "\n", encoding="utf-8")
        (d / "sim_stdout.log").write_text("", encoding="utf-8")
        (d / "lsf.err").write_text("", encoding="utf-8")
        file_cases = [
            ("fabricated file: decide(): clean log, rc 0", 0, False, "", C.VERDICT_PASS),
            ("fabricated file: decide(): clean log, rc 1", 1, False, "", C.VERDICT_FAIL),
            ("fabricated file: decide(): rc 124 + timed_out", 124, True, "", C.VERDICT_TIMEOUT),
            ("fabricated file: decide(): clean log, crash in lsf.err", 0, False, "bash: line 1: 4242 Segmentation fault      (core dumped)", C.VERDICT_FAIL),
        ]
        for name, rc, timed_out, err_text, want in file_cases:
            (d / "lsf.err").write_text(err_text + ("\n" if err_text else ""), encoding="utf-8")
            got = decide(d / "sim.log", "GEN_SMOKE_PASS", timed_out, False, rc, extra_logs=[d / "sim_stdout.log"],
                         build_config="opentitan", stderr_logs=[d / "lsf.err"])["verdict"]
            flag = "ok " if got == want else "BAD"
            ok &= got == want
            print(f"SELF-TEST {flag} {name}: want {want} got {got}")
        # Locator: a failure in the stdout capture is named by that file and its own line, never by an
        # index into the concatenated text.
        (d / "sim_stdout.log").write_text("\n".join(["cocotb line"] * 4 + ["AssertionError: GEN_TEST_FAIL gen_x: 1 fire-check failure(s)"]) + "\n", encoding="utf-8")
        (d / "lsf.err").write_text("", encoding="utf-8")
        got = decide(d / "sim.log", "GEN_SMOKE_PASS", False, False, 0, extra_logs=[d / "sim_stdout.log"],
                     build_config="opentitan", stderr_logs=[d / "lsf.err"])
        cond = got["verdict"] == C.VERDICT_FAIL and got["reason"].endswith("at sim_stdout.log:5")
        ok &= cond
        print(f"SELF-TEST {'ok ' if cond else 'BAD'} fabricated file: failure in the stdout capture is located as sim_stdout.log:5: {got['reason']}")
        (d / "sim_stdout.log").write_text("", encoding="utf-8")
        (d / "sim.log").unlink()
        got = decide(d / "sim.log", "GEN_SMOKE_PASS", True, False, 124, build_config="opentitan")["verdict"]
        ok &= got == C.VERDICT_TIMEOUT
        print(f"SELF-TEST {'ok ' if got == C.VERDICT_TIMEOUT else 'BAD'} fabricated file: decide(): no sim.log + timed_out: want TIMEOUT got {got}")
    got = decide_lines(REAL_GREEN, "GEN_SMOKE_PASS", False, 0, "opentitan", [], True, banner_lines=REAL_GREEN)
    cond = got["verdict"] == C.VERDICT_FAIL and "banner" in got["reason"]
    ok &= cond
    print(f"SELF-TEST {'ok ' if cond else 'BAD'} fabricated: banner in the stdout capture only does not count (sim.log has none): {got['verdict']}")
    try:
        scan_log(B + REAL_GREEN, "GEN_SMOKE_PASS", "")
        cond = False
    except ValueError:
        cond = True
    ok &= cond
    print(f"SELF-TEST {'ok ' if cond else 'BAD'} fabricated: banner rule not skippable (empty build_config raises)")

    # A VCS assertion failure names its property one or two lines BELOW the line the earliest-hit rule reports,
    # so the reason takes the name from there; a distant unrelated error must not be taken.
    sva = ['"gen_protocol_props.sv", 299: gen_tb_top.u_dut.p_i.sva_rvfi_irq_valid_exclusive: started at 65915000ps failed at 65915000ps',
           "\tOffending '(!rvfi_valid)'",
           "UVM_ERROR @ 6591500: reporter [sva_rvfi_irq_valid_exclusive] GEN_PROTO: protocol property violated at cycle 6587",
           "GEN_TEST_PASS"]
    r_near = decide_lines(sva, "GEN_TEST_PASS", False, 0, C.BUILD_CONFIG, [])
    r_far = decide_lines(sva[:2] + ["filler"] * (C.MECHANISM_LOOKAHEAD + 2) + [sva[2], sva[3]],
                         "GEN_TEST_PASS", False, 0, C.BUILD_CONFIG, [])
    r_own = decide_lines(["UVM_ERROR @ 5: reporter [isa_insn] mismatch", "GEN_TEST_PASS"],
                         "GEN_TEST_PASS", False, 0, C.BUILD_CONFIG, [])
    cond = ("sva_rvfi_irq_valid_exclusive" in r_near["reason"] and r_near["evidence_line"] == sva[1]
            and "sva_rvfi_irq_valid_exclusive" not in r_far["reason"]
            and "(isa_insn)" in r_own["reason"])
    ok &= cond
    print(f"SELF-TEST {'ok ' if cond else 'BAD'} fabricated: the reason names the mechanism from the next lines when its own line has none, "
          f"never from beyond {C.MECHANISM_LOOKAHEAD} lines, and the evidence line is unchanged: "
          f"near {r_near['reason']!r}; far {r_far['reason']!r}; own {r_own['reason']!r}")
    print("SELF-TEST: cases named 'real ...' are verbatim excerpts of runs on this site (LSF job ids given); "
          "'real-shaped ...' are bash kill reports captured from the job-script form with a stand-in simv; "
          "'fabricated ...' pin a rule on synthetic text until a real run exists")
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--sim-log", type=Path)
    ap.add_argument("--pass-marker", default=None)
    ap.add_argument("--timed-out", action="store_true")
    ap.add_argument("--expected-fail", action="store_true")
    ap.add_argument("--exit-code", type=int, default=None,
                    help="simv exit code; without it a clean log is FAIL (unexplained exit code None), as in the flow")
    ap.add_argument("--extra-log", type=Path, action="append", default=[],
                    help="stdout capture scanned with sim.log (repeatable; gen_run.py passes sim_stdout.log)")
    ap.add_argument("--stderr-log", type=Path, action="append", default=[],
                    help="job-script stderr scanned for crash signatures (repeatable; lsf.err, run.log)")
    ap.add_argument("--build-config", default=C.BUILD_CONFIG)
    ap.add_argument("--red-fixture", action="store_true", help="testlist red_fixture: FAIL matching --red-expect is RED-OK")
    ap.add_argument("--red-expect", default=None, help="regex the collected evidence line must match for RED-OK")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.sim_log:
        ap.error("--sim-log required")
    if a.red_fixture:
        import gen_flow_util as U
        err = U.red_expect_error(a.red_expect)
        if err:
            ap.error(f"--red-fixture needs a usable --red-expect: {err}")
    res = decide(a.sim_log, a.pass_marker, a.timed_out, a.expected_fail, rc=a.exit_code, extra_logs=a.extra_log,
                 build_config=a.build_config, stderr_logs=a.stderr_log, red_fixture=a.red_fixture, red_expect=a.red_expect)
    for k, v in res.items():
        print(f"{k}: {v}")
    return 0 if res["verdict"] in (C.VERDICT_PASS, C.VERDICT_XFAIL, C.VERDICT_RED_OK) else 2


if __name__ == "__main__":
    sys.exit(main())
