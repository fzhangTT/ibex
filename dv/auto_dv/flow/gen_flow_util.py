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


def path_is_shared(path: Path) -> bool:
    """Heuristic from the filesystem type: network filesystems are shared, local block ones not."""
    probe = path
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    r = subprocess.run(["stat", "-f", "-c", "%T", str(probe)], capture_output=True, text=True)
    fstype = r.stdout.strip().lower()
    return bool(fstype) and fstype not in LOCAL_FS_TYPES


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


# --- Testlist -------------------------------------------------------------------------------
def load_testlist(path: Path = C.TESTLIST_YAML) -> dict[str, Any]:
    data = load_yaml(path)
    if not isinstance(data, dict) or data.get("schema_version") != C.TESTLIST_SCHEMA_VERSION:
        die(f"{path}: schema_version must be {C.TESTLIST_SCHEMA_VERSION}")
    builds = data.get("builds") or {}
    tests = data.get("tests") or []
    for bname, b in builds.items():
        for k in C.BUILD_REQUIRED_KEYS:
            if k not in b:
                die(f"{path}: build {bname} lacks key {k!r}")
        unknown = set(b) - set(C.BUILD_REQUIRED_KEYS) - set(C.BUILD_OPTIONAL_KEYS)
        if unknown:
            die(f"{path}: build {bname} has unknown keys {sorted(unknown)}")
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
        if t["tier"] not in C.TIERS:
            die(f"{path}: test {t['name']} tier {t['tier']!r} not in {C.TIERS}")
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
    return data


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
    rank = C.TIER_RANK[tier]
    chosen = [t for t in tests if C.TIER_RANK[t["tier"]] <= rank]
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


def lsf_jobs_left(prefix: str = C.LSF_JOB_PREFIX) -> list[str]:
    """Job ids of this user's LSF jobs whose name starts with prefix (cleanup check)."""
    r = subprocess.run(["bjobs", "-noheader", "-o", "jobid job_name stat"], capture_output=True, text=True)
    out = []
    for line in r.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1].startswith(prefix):
            out.append(parts[0])
    return out
