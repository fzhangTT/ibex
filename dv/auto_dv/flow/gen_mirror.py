#!/usr/bin/env python3
"""Shared-storage mirror of the clone for LSF jobs that need the clone's files on the compute
host (intervention log Q-012 default): rsync of the source subset, a Python venv built ON shared
storage with ci/setup-venv.sh semantics, the spike install, and a manifest (git HEAD, content
hash of the run-time-consumed files) so a stale mirror fails loud at build and run time.

The submit-host compile keeps using the clone; only runtime artefacts come from the mirror: the
cocotb VPI library and libpython of the mirror venv, the Python test modules (PYTHONPATH), spike.

Usage:
    gen_mirror.py --sync [--venv] [--spike]      # rsync (+ venv, + tools/spike), write the manifest;
                                                 # run --venv once after a fresh mirror (without it the
                                                 # manifest reports venv MISSING, and cocotb builds refuse)
    gen_mirror.py --check                        # fresh | stale (sources) | stale_venv (lock changed: run --venv); exit 1 unless fresh
    gen_mirror.py --status                       # print the manifest
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import sys
from pathlib import Path
from typing import Any

import gen_flow_const as C
import gen_flow_util as U

SPIKE_ITEM = "tools/spike"


def git_pathspecs() -> list[str]:
    """The mirrored subset (C.MIRROR_*) as git pathspecs: the one set export_head archives and the request server's
    canary hold diffs, so a mirrored file cannot change unseen between canary and batch."""
    specs: list[str] = []
    # :(glob) keeps a top-level glob such as *.core from matching recursively.
    for item in [*C.MIRROR_ITEMS, *(f":(glob){g}" for g in C.MIRROR_GLOB_ITEMS)]:
        r = subprocess.run(["git", "-C", str(C.REPO_ROOT), "ls-files", "--", item], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            specs.append(item)
    return specs + [f":(exclude){e}" for e in C.MIRROR_EXCLUDE_PATHS]
MANIFEST_NAME = "gen_mirror_manifest.yaml"
# The venv is only as fresh as the lock files it was built from (T-027 review).
VENV_INPUT_FILES = ["ci/requirements.lock", "ci/requirements-cocotb.txt", "ci/setup-venv.sh"]
# The freshness hash covers only what a compute host CONSUMES at run time: the Python modules
# (cocotb tests, flow helpers) and the environment scripts. RTL and TB sources are compiled on the
# submit host from the clone, and documents churn constantly, so they are mirrored but not hashed.
RUNTIME_HASH_GLOBS = ["dv/auto_dv/**/*.py", "ci/env.sh", "ci/setup-venv.sh", "ci/requirements.lock",
                      "ci/requirements-cocotb.txt"]
HASH_SKIP_DIRS = {".venv", "tools", "__pycache__", "work"}


def head_sha() -> str:
    r = subprocess.run(["git", "-C", str(C.REPO_ROOT), "rev-parse", "HEAD"], capture_output=True, text=True)
    if r.returncode != 0:
        U.die("git rev-parse HEAD failed (head mode needs the clone's git metadata)")
    return r.stdout.strip()


def export_head(stage: Path, sha: str | None = None) -> str:
    """Materialize the committed HEAD subset (git_pathspecs, tracked files only) under stage with git archive:
    no checkout, no fetch, the working tree untouched. Returns the HEAD sha. tools/spike is a build product
    outside git and is mirrored from the clone separately."""
    sha = sha or head_sha()
    if stage.exists():
        # The self-test root is a valid staging home too, so an export can be exercised from a checkout whose
        # work directory does not exist.
        U.remove_tree_guarded(stage, (C.WORK_DIR, head_family(), Path(C.selftest_tmp())), "export staging dir")
    stage.mkdir(parents=True)
    specs = git_pathspecs()
    tar = stage.parent / (stage.name + ".tar")
    r = subprocess.run(["git", "-C", str(C.REPO_ROOT), "archive", "--format=tar", "-o", str(tar), sha, "--", *specs],
                       capture_output=True, text=True)
    if r.returncode != 0:
        U.die(f"git archive {sha[:12]} failed: {r.stderr.strip()[:200]}")
    r = subprocess.run(["tar", "-xf", str(tar), "-C", str(stage)], capture_output=True, text=True)
    tar.unlink(missing_ok=True)
    if r.returncode != 0:
        U.die(f"tar extract of the HEAD export failed: {r.stderr.strip()[:200]}")
    return sha


def site_mirror_root() -> Path | None:
    """The worktree mirror and tools home named by the site pointer (dv/auto_dv/work/runtime/gen_site.yaml)."""
    if C.SITE_YAML.is_file():
        for line in C.SITE_YAML.read_text(encoding="utf-8").splitlines():
            if line.startswith("mirror_root:"):
                return Path(line.split(":", 1)[1].strip())
    return None


def mirror_root() -> Path | None:
    """The mirror this process binds to: GEN_DV_MIRROR_ROOT (a head-mode process names its per-sha head tree),
    else the site's worktree mirror."""
    v = os.environ.get(C.ENV_MIRROR_ROOT)
    return Path(v) if v else site_mirror_root()


def head_mirror_root(sha: str) -> Path:
    """The per-sha head tree: sources of one commit, never rewritten by a worktree sync or by another sha."""
    site = site_mirror_root()
    if site is None:
        U.die(f"no mirror root: set mirror_root in {C.SITE_YAML}")
    return Path(str(site) + C.HEAD_MIRROR_SUFFIX) / sha[:12]


@contextlib.contextmanager
def sync_lock(site: Path):
    """One sync at a time across every process that writes under the site mirror family."""
    lock_path = site.parent / (site.name + ".sync.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def link_tools(dst: Path, site: Path) -> None:
    """A head tree shares the tools home (venv, tools/spike) of the worktree mirror through symlinks: env.sh in
    the head tree activates <tree>/.venv, which resolves to the one venv built on shared storage."""
    for name in (".venv", "tools"):
        link, target = dst / name, site / name
        if link.is_symlink() or link.exists():
            continue
        if target.exists():
            link.symlink_to(target)


def lease_head_tree(tree: Path, tag: str) -> Path:
    """A live consumer registers itself in its head tree; the prune step never removes a leased tree."""
    d = tree / C.LEASE_DIRNAME
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{os.getpid()}_{re.sub(r'[^A-Za-z0-9_.-]', '_', tag)}.lease"
    U.dump_yaml({"pid": os.getpid(), "tag": tag, "host": os.uname().nodename, "started_utc": U.now_utc()}, p)
    return p


def release_lease(p: Path) -> None:
    p.unlink(missing_ok=True)


def lease_if_head_tree(tree: Path, tag: str) -> Path | None:
    """A standalone consumer (gen_build, gen_run) bound to a head tree leases it until exit, like a regression does; None
    when the tree is not one of the head family (worktree mirror, clone)."""
    fam = head_family()
    try:
        under = fam is not None and Path(tree).resolve().is_relative_to(fam.resolve())
    except (OSError, ValueError):
        under = False
    if not under:
        return None
    import atexit
    lease = lease_head_tree(Path(tree), tag)
    atexit.register(release_lease, lease)
    return lease


def live_leases(tree: Path) -> list[dict[str, Any]]:
    """Leases whose process is still alive on this host; stale files (dead pid) are removed."""
    out: list[dict[str, Any]] = []
    d = tree / C.LEASE_DIRNAME
    if not d.is_dir():
        return out
    for p in sorted(d.glob("*.lease")):
        rec = U.load_yaml(p) or {}
        pid = int(rec.get("pid") or 0)
        alive = False
        if pid > 0 and rec.get("host") == os.uname().nodename:
            try:
                os.kill(pid, 0)
                alive = True
            except OSError:
                alive = False
        elif pid > 0:
            # Another host's process cannot be probed: live until the lease outlives every bounded consumer.
            import time as _t
            alive = (_t.time() - p.stat().st_mtime) < C.LEASE_MAX_AGE_H * 3600
        if alive:
            out.append(dict(rec, lease=str(p)))
        else:
            p.unlink(missing_ok=True)
    return out


def head_family() -> Path | None:
    site = site_mirror_root()
    return Path(str(site) + C.HEAD_MIRROR_SUFFIX) if site else None


def head_trees() -> list[Path]:
    fam = head_family()
    if not fam or not fam.is_dir():
        return []
    return sorted((p for p in fam.iterdir() if p.is_dir() and not p.name.endswith("_logs") and (p / MANIFEST_NAME).is_file()),
                  key=lambda p: p.stat().st_mtime, reverse=True)


def prune_head_mirrors() -> dict[str, Any]:
    """The prune step (run from the runtime tick, never from a sync): remove head trees beyond the newest
    HEAD_MIRRORS_KEEP that are older than HEAD_MIRRORS_KEEP_HOURS and carry no live lease."""
    import time as _t
    result: dict[str, Any] = {"removed": [], "kept_leased": [], "kept_recent": [], "kept_newest": []}
    trees = head_trees()
    result["kept_newest"] = [p.name for p in trees[:C.HEAD_MIRRORS_KEEP]]
    for p in trees[C.HEAD_MIRRORS_KEEP:]:
        if live_leases(p):
            result["kept_leased"].append(p.name)
            continue
        if _t.time() - p.stat().st_mtime < C.HEAD_MIRRORS_KEEP_HOURS * 3600:
            result["kept_recent"].append(p.name)
            continue
        # A-002: only a manifest-bearing tree under the head family is removed, and the removal is logged with its size.
        fam = head_family()
        U.remove_tree_guarded(p, (fam,), "head tree")
        if (p.parent / (p.name + "_logs")).is_dir():
            U.remove_tree_guarded(p.parent / (p.name + "_logs"), (fam,), "head tree logs")
        result["removed"].append(p.name)
    return result


def tools_digest(site: Path) -> str | None:
    """sha256 over the tools home a build binds to: every file under tools/spike/lib and the venv's cocotb VPI
    library; recorded per build and re-checked before every run (a rewrite under a consumer fails loud)."""
    h = hashlib.sha256()
    lib = site / SPIKE_ITEM / "lib"
    files = sorted(p for p in lib.rglob("*") if p.is_file()) if lib.is_dir() else []
    vpi = (venv_info(site) or {}).get("cocotb_vpi_lib")
    if vpi and Path(vpi).is_file():
        files.append(Path(vpi))
    if not files:
        return None
    for f in files:
        h.update(str(f).encode()); h.update(b"\0"); h.update(f.read_bytes()); h.update(b"\0")
    return h.hexdigest()


def mirrored_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for item in C.MIRROR_ITEMS:
        p = root / item
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            for f in sorted(p.rglob("*")):
                rel = f.relative_to(root)
                if f.is_file() and not any(part in HASH_SKIP_DIRS or part.endswith(".pyc") for part in rel.parts) \
                        and not any(rel.as_posix() == e or rel.as_posix().startswith(e + "/") for e in C.MIRROR_EXCLUDE_PATHS):
                    files.append(f)
    for g in C.MIRROR_GLOB_ITEMS:
        files += sorted(root.glob(g))
    return sorted(set(files))


def runtime_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for g in RUNTIME_HASH_GLOBS:
        for f in root.glob(g):
            rel = f.relative_to(root)
            if f.is_file() and not any(part in HASH_SKIP_DIRS for part in rel.parts):
                files.append(f)
    return sorted(set(files))


def tree_hash(root: Path) -> tuple[str, int]:
    """sha256 over (relative path, content) of every run-time-consumed file (RUNTIME_HASH_GLOBS)."""
    h = hashlib.sha256()
    files = runtime_files(root)
    for f in files:
        h.update(f.relative_to(root).as_posix().encode())
        h.update(b"\0")
        h.update(f.read_bytes())
        h.update(b"\0")
    return h.hexdigest(), len(files)


def rsync(root: Path, dst: Path, log: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    argv = ["rsync", "-a", "--delete", "--delete-excluded", "--relative"]
    for e in (*C.MIRROR_EXCLUDE_PATHS, *C.MIRROR_EXCLUDE_PATTERNS):
        argv += ["--exclude", e]
    srcs = [f"{root}/./{item}" for item in C.MIRROR_ITEMS if (root / item).exists()]
    srcs += [f"{root}/./{p.name}" for g in C.MIRROR_GLOB_ITEMS for p in sorted(root.glob(g))]
    argv += srcs + [str(dst) + "/"]
    rc, wall, timed_out = U.run_bounded(argv, cwd=root, log_path=log, timeout_s=1800)
    if rc != 0 or timed_out:
        U.die(f"rsync failed (rc={rc}, timed_out={timed_out}); see {log}")
    U.log(f"rsync done in {wall:.0f}s -> {dst}")


def rsync_spike(root: Path, dst: Path, log: Path) -> bool:
    src = root / SPIKE_ITEM
    if not src.is_dir():
        U.log(f"no {SPIKE_ITEM} in the clone; skipped")
        return False
    argv = ["rsync", "-a", "--delete", "--relative", f"{root}/./{SPIKE_ITEM}", str(dst) + "/"]
    rc, wall, timed_out = U.run_bounded(argv, cwd=root, log_path=log, timeout_s=3600)
    if rc != 0 or timed_out:
        U.die(f"rsync of {SPIKE_ITEM} failed (rc={rc}); see {log}")
    U.log(f"spike install mirrored in {wall:.0f}s")
    return True


def build_venv(dst: Path, log: Path) -> dict[str, Any]:
    """ci/setup-venv.sh of the MIRROR: its .venv gets shared absolute paths; PYTHONPATH cleared."""
    script = dst / "ci" / "setup-venv.sh"
    if not script.is_file():
        U.die(f"{script} missing; --sync first")
    inner = (f"source {C.ENV_SH} >/dev/null 2>&1; unset PYTHONPATH; deactivate 2>/dev/null; "
             f"cd {dst} && bash ci/setup-venv.sh")
    rc, wall, timed_out = U.run_bounded(["bash", "-lc", inner], cwd=dst, log_path=log, timeout_s=3600)
    info = venv_info(dst)
    info.update(rc=rc, wall_s=round(wall, 1), timed_out=timed_out, log=str(log))
    if rc != 0 or timed_out or not info.get("cocotb_vpi_lib"):
        U.die(f"mirror venv build failed (rc={rc}); see {log}")
    U.log(f"mirror venv built in {wall:.0f}s: cocotb vpi lib {info['cocotb_vpi_lib']}")
    return info


def requirements_hash(root: Path) -> str:
    h = hashlib.sha256()
    for rel in VENV_INPUT_FILES:
        f = root / rel
        h.update(rel.encode() + b"\0" + (f.read_bytes() if f.is_file() else b"MISSING") + b"\0")
    return h.hexdigest()


def venv_info(dst: Path) -> dict[str, Any]:
    cc = dst / ".venv" / "bin" / "cocotb-config"
    info: dict[str, Any] = {"venv": str(dst / ".venv"), "cocotb_config": str(cc) if cc.is_file() else None,
                            "cocotb_vpi_lib": None, "libpython": None, "python": None,
                            "requirements_sha256": requirements_hash(dst)}
    if cc.is_file():
        r = subprocess.run([str(cc), "--lib-name-path", "vpi", "vcs"], capture_output=True, text=True)
        lib = r.stdout.strip()
        # The venv may be reached through a symlink (a head tree sharing the tools home): compare resolved paths.
        venv_real = (dst / ".venv").resolve()
        info["cocotb_vpi_lib"] = lib if r.returncode == 0 and Path(lib).is_file() and str(venv_real) in str(Path(lib).resolve()) else None
        r = subprocess.run([str(cc), "--libpython"], capture_output=True, text=True)
        info["libpython"] = r.stdout.strip() if r.returncode == 0 else None
        r = subprocess.run([str(dst / ".venv" / "bin" / "python3"), "--version"], capture_output=True, text=True)
        info["python"] = r.stdout.strip() if r.returncode == 0 else None
    return info


def load_manifest(dst: Path) -> dict[str, Any] | None:
    p = dst / MANIFEST_NAME
    return U.load_yaml(p) if p.is_file() else None


def status(dst: Path, pinned_head: str | None = None) -> dict[str, Any]:
    """fresh: mirror manifest hash == source hash now == mirror tree hash now; else stale/missing. The source is
    the working tree for a worktree-mode mirror and a fresh HEAD export for a head-mode one (a new commit
    makes a head-mode mirror stale)."""
    man = load_manifest(dst)
    if not man:
        return {"state": "missing", "mirror_root": str(dst)}
    mode = man.get("source") or C.SOURCE_MODE_WORKTREE
    if mode == C.SOURCE_MODE_HEAD and pinned_head:
        # A pinned consumer (a head-mode build or run) asks "is this the mirror of sha X": answered from the
        # manifest, no re-export, so concurrent consumers never touch a shared staging directory.
        clone_n = man.get("runtime_file_count")
        clone_hash = man["tree_sha256"] if man.get("head_sha") == pinned_head else f"pinned HEAD {pinned_head} != mirror head {man.get('head_sha')}"
    elif mode == C.SOURCE_MODE_HEAD:
        stage = Path(tempfile.mkdtemp(prefix="head_stage_status_", dir=C.WORK_DIR))
        sha_now = export_head(stage)
        clone_hash, clone_n = tree_hash(stage)
        U.remove_tree_guarded(stage, (C.WORK_DIR,), "status staging dir")
        if sha_now != man.get("head_sha"):
            clone_hash = f"HEAD moved to {sha_now}"
    else:
        clone_hash, clone_n = tree_hash(C.REPO_ROOT)
    mirror_hash, mirror_n = tree_hash(dst)
    state = "fresh" if (clone_hash == man["tree_sha256"] == mirror_hash) else "stale"
    venv_req = (man.get("venv") or {}).get("requirements_sha256")
    # The venv must match the requirements of the tree it serves (the worktree mirror's or the head tree's ci/).
    if state == "fresh" and venv_req != requirements_hash(dst):
        state = "stale_venv"
    return {"state": state, "mirror_root": str(dst), "manifest_sha256": man["tree_sha256"],
            "venv_requirements_sha256": venv_req, "source_requirements_sha256": requirements_hash(dst),
            "clone_sha256_now": clone_hash, "mirror_sha256_now": mirror_hash, "clone_runtime_files": clone_n,
            "mirror_runtime_files": mirror_n, "mirror_files": man.get("file_count"),
            "git_head": man.get("git", {}).get("head"), "synced_utc": man.get("synced_utc"),
            "venv_ok": bool((man.get("venv") or {}).get("cocotb_vpi_lib")), "spike": man.get("spike_present"),
            "source": mode, "head_sha": man.get("head_sha")}


def self_test() -> int:
    """The HEAD export is the committed tree: a tracked file that differs in the working tree is exported at
    its committed content, and the export carries no .git and no work/ subtree."""
    ok = True
    # The self-test stages under the self-test scratch root, not the work directory, so it runs from a
    # read-only checkout the way a reviewer re-derives it.
    stage = Path(C.selftest_tmp()) / "head_stage_selftest"
    sha = export_head(stage)
    cond = (stage / "dv" / "auto_dv" / "flow" / "gen_flow_const.py").is_file() and not (stage / ".git").exists()
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"HEAD {sha[:12]} exported with the flow sources and without .git")
    present = [e for e in C.MIRROR_EXCLUDE_PATHS if (stage / e).exists()]
    specs = git_pathspecs()
    cond = not present and all(f":(exclude){e}" in specs for e in C.MIRROR_EXCLUDE_PATHS) and "dv/auto_dv" in specs
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"the HEAD export carries none of the excluded non-inputs {list(C.MIRROR_EXCLUDE_PATHS)} and the same pathspecs drive the canary diff (present: {present})")
    r = subprocess.run(["git", "-C", str(C.REPO_ROOT), "status", "--porcelain", "--untracked-files=no", "--", "dv/auto_dv", "rtl"],
                       capture_output=True, text=True)
    # Only a file inside the mirrored set can show the export ignores the working tree; excluded paths never export.
    modified = [l[3:].strip() for l in r.stdout.splitlines() if l[:2].strip() in ("M", "MM", "AM")
                and not any(l[3:].strip().startswith(e + "/") for e in C.MIRROR_EXCLUDE_PATHS)]
    if modified:
        rel = modified[0]
        committed = subprocess.run(["git", "-C", str(C.REPO_ROOT), "show", f"{sha}:{rel}"], capture_output=True).stdout
        exported = (stage / rel).read_bytes()
        working = (C.REPO_ROOT / rel).read_bytes()
        cond = exported == committed and exported != working
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"{rel}: exported bytes == committed bytes, != the working tree's edit ({len(modified)} tracked file(s) differ)")
    else:
        print("SELF-TEST ok  (no tracked file under dv/auto_dv or rtl differs from HEAD right now; the working-tree-invisibility check had nothing to bite on)")
    U.remove_selftest_tree(stage)
    # Two concurrent exports never share a staging directory: both complete with the same file set.
    import threading
    results: dict[str, int] = {}
    def worker(tag: str) -> None:
        d = Path(tempfile.mkdtemp(prefix=f"head_stage_selftest_{tag}_", dir=C.selftest_tmp()))
        export_head(d, sha)
        results[tag] = len([p for p in d.rglob("*") if p.is_file()])
        U.remove_selftest_tree(d)
    ts = [threading.Thread(target=worker, args=(t,)) for t in ("a", "b")]
    [t.start() for t in ts]; [t.join() for t in ts]
    cond = results.get("a", -1) == results.get("b", -2) and results.get("a", 0) > 100
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"two concurrent HEAD exports into distinct staging dirs: {results}")
    # Per-sha head trees are distinct paths, and a pinned status never consults the moving HEAD. The head family hangs
    # off the site pointer's mirror_root, which a clean checkout lacks (gen_site.yaml is git-ignored): reported as skipped there.
    skipped = 0
    if site_mirror_root() is None:
        skipped += 1
        print(f"SELF-TEST skip head trees are keyed by sha under one family dir: no mirror_root ({C.SITE_YAML} absent or without a mirror_root line)")
    else:
        ra, rb = head_mirror_root("a" * 40), head_mirror_root("b" * 40)
        cond = ra != rb and ra.parent == rb.parent and ra.parent.name.endswith(C.HEAD_MIRROR_SUFFIX)
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"head trees are keyed by sha under one family dir: {ra.parent.name}/{ra.name} vs {rb.name}")
    tiny = Path(tempfile.mkdtemp(prefix="head_tree_selftest_", dir=C.selftest_tmp()))
    (tiny / "ci").mkdir(); (tiny / "ci" / "env.sh").write_text("# tiny\n", encoding="utf-8")
    h, n = tree_hash(tiny)
    U.dump_yaml({"source": C.SOURCE_MODE_HEAD, "head_sha": "a" * 40, "tree_sha256": h, "runtime_file_count": n,
                 "venv": {"requirements_sha256": requirements_hash(tiny), "cocotb_vpi_lib": "x"}}, tiny / MANIFEST_NAME)
    st_ok = status(tiny, pinned_head="a" * 40); st_other = status(tiny, pinned_head="b" * 40)
    cond = st_ok["state"] == "fresh" and st_other["state"] == "stale" and "pinned HEAD" in str(st_other["clone_sha256_now"])
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"pinned status: the pinned sha decides (fresh for its sha, stale for another), HEAD now {head_sha()[:12]} irrelevant")
    # A same-sha re-sync (rsync --delete over the mirrored items) leaves a lease at the tree root alone.
    dst = Path(tempfile.mkdtemp(prefix="head_tree_selftest_dst_", dir=C.selftest_tmp()))
    (dst / C.LEASE_DIRNAME).mkdir()
    keep = dst / C.LEASE_DIRNAME / "1_keep.lease"; keep.write_text("pid: 1\n", encoding="utf-8")
    rlog = Path(C.selftest_tmp()) / "head_tree_selftest_rsync.log"
    rsync(tiny, dst, rlog); rsync(tiny, dst, rlog)
    cond = keep.is_file() and (dst / "ci" / "env.sh").is_file()
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", "two rsyncs with --delete into one tree keep the lease directory at its root")
    U.remove_selftest_tree(dst); rlog.unlink(missing_ok=True)
    U.remove_selftest_tree(tiny)
    # Leases: a live lease is seen, a dead pid's lease is dropped.
    tree = Path(tempfile.mkdtemp(prefix="head_lease_selftest_", dir=C.selftest_tmp()))
    lease = lease_head_tree(tree, "selftest")
    U.dump_yaml({"pid": 999999999, "tag": "dead", "host": os.uname().nodename, "started_utc": U.now_utc()}, tree / C.LEASE_DIRNAME / "999999999_dead.lease")
    live = live_leases(tree)
    cond = len(live) == 1 and live[0]["tag"] == "selftest" and not (tree / C.LEASE_DIRNAME / "999999999_dead.lease").exists()
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"leases: the live process's lease counts, a dead pid's lease is removed ({len(live)} live)")
    release_lease(lease)
    cond = live_leases(tree) == []
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", "leases: released lease is gone")
    # Standalone consumers: a tree outside the head family gets no lease; a real head tree gets one, released at exit.
    outside = lease_if_head_tree(tree, "selftest_outside")
    real = head_trees()
    inside = lease_if_head_tree(real[0], "selftest_inside") if real else None
    cond = outside is None and (not real or (inside is not None and inside.is_file()))
    if inside:
        release_lease(inside)
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"lease_if_head_tree: no lease outside the head family, a lease inside it ({real[0].name if real else 'no head tree present'})")
    # A lease this host cannot probe stays live only up to LEASE_MAX_AGE_H.
    import time as _time
    foreign = tree / C.LEASE_DIRNAME / "1_foreign.lease"
    U.dump_yaml({"pid": 1, "tag": "foreign", "host": "another-host", "started_utc": U.now_utc()}, foreign)
    fresh_live = [l["tag"] for l in live_leases(tree)] == ["foreign"]
    old = _time.time() - (C.LEASE_MAX_AGE_H + 1) * 3600
    os.utime(foreign, (old, old))
    cond = fresh_live and live_leases(tree) == [] and not foreign.exists()
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"leases: another host's lease is live while younger than {C.LEASE_MAX_AGE_H} h and dropped after")
    U.remove_selftest_tree(tree)
    print("SELF-TEST:", ("PASS" if ok else "FAIL") + (f" ({skipped} case(s) skipped: no mirror_root in this checkout)" if skipped else ""))
    return 0 if ok else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mirror-root", type=Path, default=mirror_root())
    ap.add_argument("--sync", action="store_true")
    ap.add_argument("--venv", action="store_true", help="(re)build the mirror venv after --sync")
    ap.add_argument("--spike", action="store_true", help="mirror tools/spike after --sync")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--source", choices=C.SOURCE_MODES, default=C.SOURCE_MODE_WORKTREE,
                    help="sync from the working tree (worktree) or from committed HEAD via git archive (head)")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--head-sha", default=None, help="head mode: export exactly this commit (a batch pins it before syncing)")
    ap.add_argument("--prune", action="store_true", help="remove old, unleased head trees (the runtime tick runs this; a sync never does)")
    ap.add_argument("--force-tools", action="store_true", help="rewrite the tools home (--spike/--venv) even while head trees are leased")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.mirror_root is None:
        U.die(f"no mirror root: set mirror_root in {C.SITE_YAML} or GEN_DV_MIRROR_ROOT")
    dst = a.mirror_root.resolve()
    if a.sync:
        U.require_env("rsync")
        site = site_mirror_root()
        if site is None:
            U.die(f"no site mirror root in {C.SITE_YAML}")
        head_mode = a.source == C.SOURCE_MODE_HEAD
        sha = (a.head_sha or head_sha()) if head_mode else U.git_head()["head"]
        dst = head_mirror_root(sha) if head_mode else site
        if not U.path_is_shared(dst.parent if head_mode else dst):
            U.log(f"WARNING: {dst} is on a local filesystem; LSF hosts will not see it")
        logs = dst.parent / (dst.name + "_logs")
        logs.mkdir(parents=True, exist_ok=True)
        if not head_mode and (a.spike or a.venv) and not a.force_tools:
            leased = [t.name for t in head_trees() if live_leases(t)]
            if leased:
                U.die(f"--spike/--venv rewrite the tools home that leased head trees {leased} are using; wait or --force-tools")
        with sync_lock(site):
            if head_mode:
                # Sources of exactly this commit into their own tree; the tools home is shared through symlinks.
                stage = Path(tempfile.mkdtemp(prefix="head_stage_", dir=C.WORK_DIR))
                export_head(stage, sha)
                rsync(stage, dst, logs / "rsync.log")
                U.remove_tree_guarded(stage, (C.WORK_DIR,), "sync staging dir")
                link_tools(dst, site)
                U.log(f"HEAD {sha[:12]} synced into {dst}")
            else:
                rsync(C.REPO_ROOT, dst, logs / "rsync.log")
            prev = load_manifest(dst) or {}
            man: dict[str, Any] = {"mirror_root": str(dst), "clone": str(C.REPO_ROOT), "synced_utc": U.now_utc(),
                                   "git": U.git_head(), "source": a.source, "head_sha": sha, "tools_home": str(site),
                                   "items": [*C.MIRROR_ITEMS, *C.MIRROR_GLOB_ITEMS], "excludes": [*C.MIRROR_EXCLUDE_PATHS, *C.MIRROR_EXCLUDE_PATTERNS]}
            man["tree_sha256"], man["runtime_file_count"] = tree_hash(dst)
            man["file_count"] = len(mirrored_files(dst))
            man["runtime_hash_globs"] = RUNTIME_HASH_GLOBS
            # tools/spike lives in the tools home only; a head tree reaches it through its symlink, and a head-mode
            # sync never rewrites the tools home (--spike there means: require it present).
            man["spike_present"] = rsync_spike(C.REPO_ROOT, site, logs / "rsync_spike.log") if (a.spike and not head_mode) \
                else (dst / SPIKE_ITEM / "bin" / "spike").is_file()
            if head_mode and a.spike and not man["spike_present"]:
                U.die(f"tools home {site} has no tools/spike; run gen_mirror.py --sync --spike --source worktree first")
            if a.venv:
                man["venv"] = build_venv(site, logs / "venv.log")
            elif head_mode:
                # The shared venv seen from this tree (resolved through the symlink), built-from hash carried over.
                info = venv_info(dst)
                site_venv = (load_manifest(site) or {}).get("venv") or {}
                info["requirements_sha256"] = site_venv.get("requirements_sha256", info["requirements_sha256"])
                man["venv"] = info
            else:
                man["venv"] = prev.get("venv")
            man["tools_digest"] = tools_digest(site)
            U.dump_yaml(man, dst / MANIFEST_NAME)
        U.log(f"mirror manifest {dst / MANIFEST_NAME}: source {a.source}, {man['file_count']} files, sha256 {man['tree_sha256'][:16]}..., "
              f"git {man['git']['head'][:12]}, venv {'ok' if (man.get('venv') or {}).get('cocotb_vpi_lib') else 'MISSING'}, "
              f"spike {man['spike_present']}")
    if a.prune:
        res = prune_head_mirrors()
        U.log(f"prune: removed {res['removed']}, kept leased {res['kept_leased']}, kept recent {res['kept_recent']}, newest kept {len(res['kept_newest'])}")
    if a.check or a.status:
        if not a.sync:
            dst = head_mirror_root(a.head_sha or head_sha()) if a.source == C.SOURCE_MODE_HEAD else a.mirror_root.resolve()
        st = status(dst)
        for k, v in st.items():
            print(f"{k}: {v}")
        if a.check and st["state"] != "fresh":
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
