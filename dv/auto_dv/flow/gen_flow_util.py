#!/usr/bin/env python3
"""Shared helpers of the generated regression flow: yaml io, hashing, tool checks, testlist
loading, deterministic seeds, bounded subprocesses and the LSF submit-and-watch primitive."""

from __future__ import annotations

import datetime as _dt
import hashlib
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time
import zlib
from pathlib import Path
from typing import Any

import yaml

import gen_flow_const as C


# --- Small utilities ------------------------------------------------------------------------
def now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d-%H%M%S")


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def log(msg: str) -> None:
    print(f"[{now_utc()}] {msg}", flush=True)


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump_yaml(data: Any, path: Path) -> None:
    """Atomic write so a reader never sees a half-written manifest."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False, width=100)
    os.replace(tmp, path)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def filelist_entries(flist: Path, root: Path = C.REPO_ROOT) -> list[Path]:
    """Source files named by a VCS -f file (comments and +incdir+ lines skipped)."""
    files: list[Path] = []
    for raw in flist.read_text(encoding="utf-8").splitlines():
        line = raw.split("//", 1)[0].strip()
        if not line or line.startswith("+") or line.startswith("-"):
            continue
        files.append((root / line).resolve())
    return files


def filelist_digest(flists: list[Path]) -> dict[str, Any]:
    """sha256 of every filelist and one combined sha256 over the contents of all listed sources."""
    combined = hashlib.sha256()
    per_list = {}
    n = 0
    for fl in flists:
        per_list[str(fl.relative_to(C.REPO_ROOT))] = sha256_file(fl)
        for src in filelist_entries(fl):
            if not src.is_file():
                die(f"{fl}: listed source missing: {src}")
            combined.update(src.read_bytes())
            n += 1
    return {"filelists": per_list, "sources_sha256": combined.hexdigest(), "source_count": n}


def git_head() -> dict[str, Any]:
    def run(args: list[str]) -> str:
        r = subprocess.run(["git", *args], cwd=C.REPO_ROOT, capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else ""
    dirty = run(["status", "--porcelain", "--untracked-files=no"])
    return {"head": run(["rev-parse", "HEAD"]), "branch": run(["rev-parse", "--abbrev-ref", "HEAD"]),
            "dirty_tracked_files": bool(dirty)}


def tool_versions() -> dict[str, str]:
    out: dict[str, str] = {}
    r = subprocess.run(["vcs", "-full64", "-ID"], capture_output=True, text=True)
    m = re.search(r"Compiler version = (.+)", r.stdout + r.stderr)
    out["vcs"] = m.group(1).strip() if m else "unknown"
    r = subprocess.run(["urg", "-version"], capture_output=True, text=True)
    m = re.search(r"URG Version (\S+)", r.stdout + r.stderr)
    out["urg"] = m.group(1) if m else "unknown"
    out["python"] = sys.version.split()[0]
    cc = shutil.which("cocotb-config")
    if cc:
        r = subprocess.run([cc, "--version"], capture_output=True, text=True)
        out["cocotb"] = r.stdout.strip() or "unknown"
    out["vcs_home"] = os.environ.get("VCS_HOME", "")
    return out


def require_env(*tools: str) -> None:
    """Fail loud when ci/env.sh was not sourced (tool paths come from it alone)."""
    missing = [t for t in tools if shutil.which(t) is None]
    if missing:
        die(f"tools missing from PATH: {missing}; run under bash -lc 'source ci/env.sh && ...'")


def env_wrapped_command(argv: list[str], cwd: Path) -> list[str]:
    """Command for a fresh shell (LSF or local): source ci/env.sh, cd, then run argv."""
    inner = f"source {shlex.quote(str(C.ENV_SH))} >/dev/null 2>&1 && cd {shlex.quote(str(cwd))} && " \
            + " ".join(shlex.quote(a) for a in argv)
    return ["bash", "-lc", inner]


LOCAL_FS_TYPES = {"xfs", "ext4", "ext3", "ext2", "btrfs", "tmpfs", "overlay"}


def fs_type(path: Path) -> str:
    """Filesystem type name from df -T (stat -f reports site filesystems such as wekafs as a bare magic)."""
    probe = path
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    r = subprocess.run(["df", "-T", str(probe)], capture_output=True, text=True)
    lines = r.stdout.strip().splitlines()
    if len(lines) >= 2 and len(lines[-1].split()) >= 2:
        return lines[-1].split()[1].lower()
    r = subprocess.run(["stat", "-f", "-c", "%T", str(probe)], capture_output=True, text=True)
    return r.stdout.strip().lower()


def path_is_shared(path: Path) -> bool:
    """Heuristic from the filesystem type: network filesystems are shared, local block ones not."""
    fstype = fs_type(path)
    return bool(fstype) and fstype not in LOCAL_FS_TYPES


def require_sv_constants() -> None:
    """Flow steps call this first: SV and Python constants homes must agree (P-06)."""
    problems = C.check_sv_constants()
    if problems:
        die("constants mismatch between gen_tb_pkg.sv / ci checker and gen_flow_const.py: " + "; ".join(problems))


def parse_seed(text: str) -> int:
    try:
        v = int(text, 0)
    except ValueError:
        die(f"seed {text!r} is not an integer")
    if not (C.SEED_MIN <= v <= C.SEED_MAX):
        die(f"seed {v} outside [{C.SEED_MIN}, {C.SEED_MAX}]")
    return v


def derive_seeds(test_name: str, count: int, base_seed: int) -> list[int]:
    """Deterministic per-test seed list: same (test, base_seed) always yields the same seeds."""
    seeds: list[int] = []
    state = (base_seed ^ zlib.crc32(test_name.encode())) & 0xFFFFFFFF
    while len(seeds) < count:
        state = (1103515245 * state + 12345) & 0xFFFFFFFF
        s = (state >> 1) or 1
        if s not in seeds:
            seeds.append(s)
    return seeds


# --- Templates ------------------------------------------------------------------------------
def render_fields(text: str, fields: dict[str, str], comment_prefixes: tuple[str, ...] = ("//", "#")) -> str:
    """Replace {name} tokens for the given names only, leaving every other brace (Tcl, SV) intact.
    Fails loud only when a token of a KNOWN name survives; other {word} text is legitimate Tcl/SV."""
    body = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith(comment_prefixes))
    for k, v in fields.items():
        body = body.replace("{" + k + "}", str(v))
    leftover = re.findall(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", body)
    bad = [t for t in leftover if t in fields]
    if bad:
        raise ValueError(f"template still holds unrendered fields {bad}")
    return body + "\n"


def self_test() -> int:
    """Render both checked-in templates and check the Tcl braces survive (review finding, T-010)."""
    ok = True
    hier = render_fields(C.CM_HIER_TEMPLATE.read_text(encoding="utf-8"), {"tb_top": "top_x", "dut_instance": "u_y"})
    ok &= hier.strip() == "+tree top_x.u_y"
    print("SELF-TEST", "ok " if hier.strip() == "+tree top_x.u_y" else "BAD", "cm_hier render:", hier.strip())
    tcl = render_fields(C.DUMP_TCL_TEMPLATE.read_text(encoding="utf-8"),
                        {"tb_top": "top_x", "dut_instance": "u_y", "waves_fsdb": "w.fsdb", "waves_vpd": "w.vpd"})
    checks = {"tcl keeps if-braces": "if { [info exists ::env(VERDI_HOME)] } {" in tcl,
              "tcl renders fsdb line": 'fsdbDumpfile "$::env(SIM_DIR)/w.fsdb"' in tcl,
              "tcl renders sva scope": "fsdbDumpSVA 0 top_x.u_y" in tcl,
              "tcl renders dump -add braces": "dump -add { top_x } -depth 0" in tcl,
              "tcl has no unrendered field": "{tb_top}" not in tcl and "{waves_vpd}" not in tcl}
    for name, res in checks.items():
        ok &= res
        print("SELF-TEST", "ok " if res else "BAD", name)
    # P6 helper: a debug-only knob counts as enabled with no value or a non-zero value.
    p6 = {"+gen_chk_x": True, "+gen_chk_x=1": True, "+gen_chk_x=0": False, "+other=1": False, "+gen_chk_x=": False}
    for pa, want in p6.items():
        got = plusarg_enabled([pa], "gen_chk_x")
        ok &= got == want
        print("SELF-TEST", "ok " if got == want else "BAD", f"plusarg_enabled({pa!r}) == {want}")
    ok &= plusarg_name("+vcs+finish+1000") == "vcs+finish+1000"
    print("SELF-TEST", "ok " if plusarg_name("+vcs+finish+1000") == "vcs+finish+1000" else "BAD", "plusarg_name keeps + inside vcs+ names")
    # Gated trees must not nest (combine_rows would double count cumulative URG rows).
    n1 = nested_pairs(["u_dut.u_ibex_core", "u_dut.u_ibex_core.cs_registers_i"])
    n2 = nested_pairs(["u_dut.u_ibex_core", "u_dut.u_register_file"])
    n3 = nested_pairs(["u_dut.a", "u_dut.ab"])
    cond = n1 == [("u_dut.u_ibex_core", "u_dut.u_ibex_core.cs_registers_i")] and n2 == [] and n3 == []
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"nested gated trees detected, siblings and prefix-only names accepted: {n1} {n2} {n3}")
    import tempfile
    import yaml as _y
    with tempfile.TemporaryDirectory(prefix="gen_flow_util_selftest_", dir=C.selftest_tmp()) as td:
        t = load_yaml(C.TESTLIST_YAML)
        t["builds"]["gen_smoke"]["cov_trees"] = ["u_dut.u_ibex_core", "u_dut.u_ibex_core.cs_registers_i"]
        bad = Path(td) / "testlist_nested.yaml"
        bad.write_text(_y.safe_dump(t, sort_keys=False), encoding="utf-8")
        try:
            load_testlist(bad)
            cond = False
        except SystemExit:
            cond = True
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", "load_testlist refuses a testlist whose gated trees nest")
    for args, want_kept, want_dropped, label in (
            (["-cm_glitch", "0"], [], ["-cm_glitch", "0"], "value-taking flag takes its value"),
            (["-cm_seqnoconst", "-lca"], ["-lca"], ["-cm_seqnoconst"], "stand-alone -cm flag keeps the next argument (review 2a4916c #3)"),
            (["-cm_glitch", "0", "-xlrm", "0"], ["-xlrm", "0"], ["-cm_glitch", "0"], "same value elsewhere survives (positions, not values)")):
        kept, dropped = drop_cm_args(args)
        cond = kept == want_kept and dropped == want_dropped
        ok &= cond
        print(f"SELF-TEST {'ok ' if cond else 'BAD'} drop_cm_args {label}: kept={kept} dropped={dropped}")
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 2


# --- Testlist -------------------------------------------------------------------------------
def load_testlist(path: Path = C.TESTLIST_YAML) -> dict[str, Any]:
    data = load_yaml(path)
    if not isinstance(data, dict) or data.get("schema_version") != C.TESTLIST_SCHEMA_VERSION:
        die(f"{path}: schema_version must be {C.TESTLIST_SCHEMA_VERSION}")
    builds = data.get("builds") or {}
    tests = data.get("tests") or []
    unknown_top = set(data) - {"schema_version", "builds", "tests"} - set(C.TESTLIST_OPTIONAL_TOP_KEYS)
    if unknown_top:
        die(f"{path}: unknown top-level keys {sorted(unknown_top)}")
    for k in C.TESTLIST_OPTIONAL_TOP_KEYS:
        if k in data and not isinstance(data[k], list):
            die(f"{path}: {k} must be a list")
    for t_ in data.get("fcov_manifest_required_tiers") or []:
        if t_ not in C.ALL_TIERS:
            die(f"{path}: fcov_manifest_required_tiers names unknown tier {t_!r}")
    known_plusargs = set(C.sv_plusarg_names()) | set(C.SIMULATOR_PLUSARGS)
    for knob in data.get("debug_only_plusargs") or []:
        if knob not in C.sv_plusarg_names():
            die(f"{path}: debug_only_plusargs names {knob!r}, which is not a PLUSARG_* of {C.TB_PKG_SV.name} "
                "(the knob's one origin; TB Infra declares it there first)")
    for bname, b in builds.items():
        for k in C.BUILD_REQUIRED_KEYS:
            if k not in b:
                die(f"{path}: build {bname} lacks key {k!r}")
        unknown = set(b) - set(C.BUILD_REQUIRED_KEYS) - set(C.BUILD_OPTIONAL_KEYS)
        if unknown:
            die(f"{path}: build {bname} has unknown keys {sorted(unknown)}")
        trees = b.get("cov_trees")
        if trees is not None and (not isinstance(trees, list) or not trees or not all(isinstance(x, str) for x in trees)):
            die(f"{path}: build {bname} cov_trees must be a non-empty list of instance paths below tb_top")
        info = b.get("info_trees")
        if info is not None and (not isinstance(info, list) or not all(isinstance(x, str) for x in info)):
            die(f"{path}: build {bname} info_trees must be a list of instance paths below tb_top")
        if info and trees and set(info) & set(trees):
            die(f"{path}: build {bname}: a tree cannot be both gated (cov_trees) and informational (info_trees)")
        for key in ("pre_build", "extra_ldflags", "runtime_lib_dirs"):
            v = b.get(key)
            if v is not None and (not isinstance(v, list) or not all(isinstance(x, str) for x in v)):
                die(f"{path}: build {bname} {key} must be a list of strings")
        nested = nested_pairs(trees or [])
        if nested:
            die(f"{path}: build {bname}: gated cov_trees must not nest (URG hierarchy rows are cumulative over "
                f"children, the combining rule would double count): {nested}")
    names = set()
    for t in tests:
        for k in C.TEST_REQUIRED_KEYS:
            if k not in t:
                die(f"{path}: test {t.get('name')} lacks key {k!r}")
        unknown = set(t) - set(C.TEST_REQUIRED_KEYS) - set(C.TEST_OPTIONAL_KEYS)
        if unknown:
            die(f"{path}: test {t['name']} has unknown keys {sorted(unknown)}")
        if t["name"] in names:
            die(f"{path}: duplicate test name {t['name']}")
        names.add(t["name"])
        if t["tier"] not in C.ALL_TIERS:
            die(f"{path}: test {t['name']} tier {t['tier']!r} not in {C.ALL_TIERS}")
        if t["tier"] == C.CHECK_TIER and t.get("measured", True):
            die(f"{path}: test {t['name']} is tier {C.CHECK_TIER} and must be measured: false (Critic R-01)")
        if t["build"] not in builds:
            die(f"{path}: test {t['name']} names unknown build {t['build']!r}")
        if t["owner"] not in C.OWNER_ROLES:
            die(f"{path}: test {t['name']} owner {t['owner']!r} not a role slug")
        if not t["name"].startswith("gen_"):
            die(f"{path}: test {t['name']} lacks the gen_ prefix")
        if not isinstance(t["seeds"], (int, list)):
            die(f"{path}: test {t['name']} seeds must be a count or a list")
        if not isinstance(t["plusargs"], list):
            die(f"{path}: test {t['name']} plusargs must be a list")
        uvm = t.get("uvm_test")
        if uvm is not None and not (isinstance(uvm, str) and re.match(r"^[A-Za-z_]\w*$", uvm)):
            die(f"{path}: test {t['name']} uvm_test must be null or a class identifier, got {uvm!r}")
        prog = t.get("program")
        if prog is not None:
            if not isinstance(prog, dict):
                die(f"{path}: test {t['name']} program must be a mapping")
            unknown = set(prog) - set(C.PROGRAM_KEYS)
            if unknown:
                die(f"{path}: test {t['name']} program has unknown keys {sorted(unknown)}")
            if bool(prog.get("riscv_dv_test")) == bool(prog.get("directed")):
                die(f"{path}: test {t['name']} program needs exactly one of riscv_dv_test / directed")
            seed = prog.get("seed", C.PROGRAM_SEED_RUN)
            if not (seed == C.PROGRAM_SEED_RUN or isinstance(seed, int)):
                die(f"{path}: test {t['name']} program.seed must be an integer or {C.PROGRAM_SEED_RUN!r}")
        for pa in t["plusargs"]:
            name = plusarg_name(pa)
            if name is None:
                die(f"{path}: test {t['name']} plusarg {pa!r} is not of the form +name or +name=value")
            if name not in known_plusargs and not name.startswith(C.VCS_PLUSARG_PREFIX):
                die(f"{path}: test {t['name']} plusarg {pa!r}: name {name!r} is neither a PLUSARG_* of "
                    f"{C.TB_PKG_SV.name} nor a simulator/UVM plusarg (P-06 single source)")
    return data


def nested_pairs(trees: list[str]) -> list[tuple[str, str]]:
    """(ancestor, descendant) pairs among instance paths; a.b is an ancestor of a.b.c, not of a.bc."""
    out = []
    for x in trees:
        for y in trees:
            if x != y and y.startswith(x + "."):
                out.append((x, y))
    return out


def plusarg_name(pa: str) -> str | None:
    m = re.match(r"^\+([A-Za-z_][\w+]*)(=.*)?$", pa)
    return m.group(1) if m else None


def plusarg_enabled(plusargs: list[str], name: str) -> bool:
    """True when +name is present with no value or a value other than 0."""
    for pa in plusargs:
        if plusarg_name(pa) == name:
            val = pa.split("=", 1)[1] if "=" in pa else "1"
            return val.strip() not in ("0", "")
    return False


def test_by_name(testlist: dict[str, Any], name: str) -> dict[str, Any]:
    for t in testlist["tests"]:
        if t["name"] == name:
            return t
    die(f"test {name!r} not in {C.TESTLIST_YAML}")


def select_tests(testlist: dict[str, Any], tier: str | None, names: list[str] | None,
                 group: str | None) -> list[dict[str, Any]]:
    tests = testlist["tests"]
    if names:
        return [test_by_name(testlist, n) for n in names]
    if tier is None:
        die("select_tests: need a tier or explicit names")
    if tier == C.CHECK_TIER:
        return [t for t in tests if t["tier"] == C.CHECK_TIER]
    rank = C.TIER_RANK[tier]
    chosen = [t for t in tests if t["tier"] in C.TIER_RANK and C.TIER_RANK[t["tier"]] <= rank]
    if tier == "targeted" and group:
        chosen = [t for t in chosen if group in (t.get("feature_groups") or []) or t["tier"] == "smoke"]
    return chosen


def seeds_for_test(t: dict[str, Any], override: int | list[int] | None, base_seed: int) -> list[int]:
    spec = override if override is not None else t["seeds"]
    if isinstance(spec, list):
        return [parse_seed(str(s)) for s in spec]
    return derive_seeds(t["name"], int(spec), base_seed)


# --- Bounded subprocess -----------------------------------------------------------------------
def run_bounded(argv: list[str], cwd: Path, log_path: Path, timeout_s: float,
                env: dict[str, str] | None = None) -> tuple[int | None, float, bool]:
    """Run argv in its own process group, appending stdout+stderr to log_path.
    Returns (returncode or None, wall seconds, timed_out)."""
    start = time.monotonic()
    with log_path.open("ab") as lf:
        proc = subprocess.Popen(argv, cwd=cwd, stdout=lf, stderr=subprocess.STDOUT, env=env,
                                start_new_session=True)
        try:
            rc = proc.wait(timeout=timeout_s)
            return rc, time.monotonic() - start, False
        except subprocess.TimeoutExpired:
            _kill_group(proc)
            return None, time.monotonic() - start, True


def _kill_group(proc: subprocess.Popen) -> None:
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        proc.wait(timeout=C.TIMEOUT_GRACE_S)
    except (ProcessLookupError, subprocess.TimeoutExpired):
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()


# --- LSF submit-and-watch (only the runtime role calls this) --------------------------------
class LsfJob:
    """One `bsub -K` job with a pend allowance and a run deadline, watched from log files."""

    def __init__(self, argv: list[str], cwd: Path, job_name: str, slots: int, out_file: Path,
                 err_file: Path, run_timeout_s: float, pend_allowance_s: float = C.LSF_PEND_ALLOWANCE_S,
                 queue: str = C.LSF_QUEUE):
        self.argv = argv
        self.cwd = cwd
        self.job_name = job_name
        self.slots = slots
        self.out_file = out_file
        self.err_file = err_file
        self.run_timeout_s = run_timeout_s
        self.pend_allowance_s = pend_allowance_s
        self.queue = queue
        self.job_id: str | None = None
        self.host: str | None = None
        self.submit_time = 0.0
        self.start_time: float | None = None
        self.end_time: float | None = None
        self.bsub_rc: int | None = None
        self.killed_reason: str | None = None
        self.bsub_output: list[str] = []

    def bsub_argv(self) -> list[str]:
        wall_min = max(1, int((self.run_timeout_s + 300) // 60))
        return ["bsub", "-K", "-q", self.queue, "-n", str(self.slots), "-R", C.LSF_SPAN,
                "-J", self.job_name, "-cwd", str(self.cwd), "-o", str(self.out_file),
                "-e", str(self.err_file), "-W", str(wall_min), *self.argv]

    def run(self) -> None:
        self.cwd.mkdir(parents=True, exist_ok=True)
        self.submit_time = time.monotonic()
        proc = subprocess.Popen(self.bsub_argv(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, bufsize=1)
        reader = threading.Thread(target=self._read_bsub, args=(proc,), daemon=True)
        reader.start()
        while True:
            rc = proc.poll()
            if rc is not None:
                self.bsub_rc = rc
                break
            now = time.monotonic()
            if self.start_time is None and now - self.submit_time > self.pend_allowance_s:
                self._kill("pend allowance exceeded")
            elif self.start_time is not None and now - self.start_time > self.run_timeout_s + 120:
                self._kill("run deadline exceeded")
            time.sleep(min(C.LSF_POLL_S, 2))
        reader.join(timeout=5)
        self.end_time = time.monotonic()

    def _read_bsub(self, proc: subprocess.Popen) -> None:
        assert proc.stdout is not None
        for line in proc.stdout:
            line = line.rstrip("\n")
            self.bsub_output.append(line)
            m = C.LSF_SUBMIT_RE.search(line)
            if m:
                self.job_id = m.group(1)
            m = C.LSF_STARTED_RE.search(line)
            if m:
                self.host = m.group(1)
                self.start_time = time.monotonic()

    def _kill(self, reason: str) -> None:
        if self.killed_reason:
            return
        self.killed_reason = reason
        if self.job_id:
            subprocess.run(["bkill", self.job_id], capture_output=True, text=True)

    def report(self) -> dict[str, Any]:
        """LSF cost facts parsed from the -o job report file (deterministic, no bjobs call)."""
        rep: dict[str, Any] = {"job_id": self.job_id, "host": self.host, "queue": self.queue,
                               "slots": self.slots, "bsub_rc": self.bsub_rc,
                               "killed_reason": self.killed_reason,
                               "pend_s": round((self.start_time or self.end_time or 0) - self.submit_time, 1)
                               if self.submit_time else None,
                               "wall_s": round((self.end_time or 0) - (self.start_time or self.submit_time), 1)
                               if self.end_time else None,
                               "cpu_s": None, "max_mem": None}
        deadline = time.monotonic() + 30
        while not self.out_file.is_file() and time.monotonic() < deadline:
            time.sleep(1)
        if self.out_file.is_file():
            text = self.out_file.read_text(encoding="utf-8", errors="replace")
            m = C.LSF_REPORT_CPU_RE.search(text)
            rep["cpu_s"] = float(m.group(1)) if m else None
            m = C.LSF_REPORT_RUN_RE.search(text)
            if m:
                rep["lsf_run_s"] = float(m.group(1))
            m = C.LSF_REPORT_MEM_RE.search(text)
            rep["max_mem"] = f"{m.group(1)} {m.group(2)}" if m else None
            m = C.LSF_REPORT_HOST_RE.search(text)
            if m and not rep["host"]:
                rep["host"] = m.group(1)
        return rep


def lsf_job_name(tag: str, leaf: str) -> str:
    """gen_dv_<tag>_<leaf>: the tag scopes the cleanup check to one regression."""
    return f"{C.LSF_JOB_PREFIX}_{tag}_{leaf}" if tag else f"{C.LSF_JOB_PREFIX}_{leaf}"


def drop_cm_args(args: list[str]) -> tuple[list[str], list[str]]:
    """Split vcs arguments into (kept, dropped): every -cm* flag is dropped, and only a flag in
    C.CM_VALUE_FLAGS takes the following token with it; positions decide, never values."""
    kept: list[str] = []
    dropped: list[str] = []
    i = 0
    while i < len(args):
        x = args[i]
        if x.startswith("-cm"):
            dropped.append(x)
            if x in C.CM_VALUE_FLAGS and i + 1 < len(args):
                dropped.append(args[i + 1])
                i += 1
        else:
            kept.append(x)
        i += 1
    return kept, dropped


def lsf_jobs_left(prefix: str = C.LSF_JOB_PREFIX, settle_s: float = C.LSF_STATUS_SETTLE_S,
                  interval_s: float = 3.0) -> list[str]:
    """Job ids of this user's LSF jobs whose name starts with prefix (cleanup check). bjobs reports a
    finished job as RUN for a few seconds after bsub -K returned, so a non-empty answer is re-polled
    until it clears or settle_s elapses."""
    deadline = time.time() + settle_s
    while True:
        r = subprocess.run(["bjobs", "-noheader", "-o", "jobid job_name stat"], capture_output=True, text=True)
        out = []
        for line in r.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[1].startswith(prefix) and parts[2] in C.LSF_ACTIVE_STATES:
                out.append(parts[0])
        if not out or time.time() >= deadline:
            return out
        time.sleep(interval_s)


if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv else 0)
