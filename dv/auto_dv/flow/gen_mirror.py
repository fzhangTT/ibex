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
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import gen_flow_const as C
import gen_flow_util as U

# Clone subset the compute host needs; paths are clone-root relative (rsync --relative keeps them).
MIRROR_ITEMS = ["rtl", "vendor/lowrisc_ip", "vendor/google_riscv-dv", "util", "ci", "dv/auto_dv",
                "ibex_configs.yaml", "python-requirements.txt"]
MIRROR_GLOB_ITEMS = ["*.core"]
MIRROR_EXCLUDES = [".git", "__pycache__", "*.pyc", "dv/auto_dv/work", ".venv", "out*", "*.vdb", "*.fsdb"]
SPIKE_ITEM = "tools/spike"
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


def export_head(stage: Path) -> str:
    """Materialize the committed HEAD subset (MIRROR_ITEMS, tracked files only) under stage with git archive:
    no checkout, no fetch, the working tree untouched. Returns the HEAD sha. tools/spike is a build product
    outside git and is mirrored from the clone separately."""
    sha = head_sha()
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    specs: list[str] = []
    for item in MIRROR_ITEMS + MIRROR_GLOB_ITEMS:
        r = subprocess.run(["git", "-C", str(C.REPO_ROOT), "ls-files", "--", item], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            specs.append(item)
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


def mirror_root() -> Path | None:
    """mirror_root: of the site pointer file (dv/auto_dv/work/runtime/gen_site.yaml)."""
    v = os.environ.get("GEN_DV_MIRROR_ROOT")
    if v:
        return Path(v)
    if C.SITE_YAML.is_file():
        for line in C.SITE_YAML.read_text(encoding="utf-8").splitlines():
            if line.startswith("mirror_root:"):
                return Path(line.split(":", 1)[1].strip())
    return None


def mirrored_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for item in MIRROR_ITEMS:
        p = root / item
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            for f in sorted(p.rglob("*")):
                rel = f.relative_to(root)
                if f.is_file() and not any(part in HASH_SKIP_DIRS or part.endswith(".pyc") for part in rel.parts) \
                        and "dv/auto_dv/work" not in rel.as_posix():
                    files.append(f)
    for g in MIRROR_GLOB_ITEMS:
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
    for e in MIRROR_EXCLUDES:
        argv += ["--exclude", e]
    srcs = [f"{root}/./{item}" for item in MIRROR_ITEMS if (root / item).exists()]
    srcs += [f"{root}/./{p.name}" for g in MIRROR_GLOB_ITEMS for p in sorted(root.glob(g))]
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
        info["cocotb_vpi_lib"] = lib if r.returncode == 0 and Path(lib).is_file() and str(dst) in lib else None
        r = subprocess.run([str(cc), "--libpython"], capture_output=True, text=True)
        info["libpython"] = r.stdout.strip() if r.returncode == 0 else None
        r = subprocess.run([str(dst / ".venv" / "bin" / "python3"), "--version"], capture_output=True, text=True)
        info["python"] = r.stdout.strip() if r.returncode == 0 else None
    return info


def load_manifest(dst: Path) -> dict[str, Any] | None:
    p = dst / MANIFEST_NAME
    return U.load_yaml(p) if p.is_file() else None


def status(dst: Path) -> dict[str, Any]:
    """fresh: mirror manifest hash == source hash now == mirror tree hash now; else stale/missing. The source is
    the working tree for a worktree-mode mirror and a fresh HEAD export for a head-mode one (a new commit
    makes a head-mode mirror stale)."""
    man = load_manifest(dst)
    if not man:
        return {"state": "missing", "mirror_root": str(dst)}
    mode = man.get("source") or C.SOURCE_MODE_WORKTREE
    if mode == C.SOURCE_MODE_HEAD:
        stage = C.WORK_DIR / "head_stage_status"
        sha_now = export_head(stage)
        clone_hash, clone_n = tree_hash(stage)
        shutil.rmtree(stage, ignore_errors=True)
        if sha_now != man.get("head_sha"):
            clone_hash = f"HEAD moved to {sha_now}"
    else:
        clone_hash, clone_n = tree_hash(C.REPO_ROOT)
    mirror_hash, mirror_n = tree_hash(dst)
    state = "fresh" if (clone_hash == man["tree_sha256"] == mirror_hash) else "stale"
    venv_req = (man.get("venv") or {}).get("requirements_sha256")
    if state == "fresh" and venv_req != requirements_hash(C.REPO_ROOT):
        state = "stale_venv"
    return {"state": state, "mirror_root": str(dst), "manifest_sha256": man["tree_sha256"],
            "venv_requirements_sha256": venv_req, "clone_requirements_sha256": requirements_hash(C.REPO_ROOT),
            "clone_sha256_now": clone_hash, "mirror_sha256_now": mirror_hash, "clone_runtime_files": clone_n,
            "mirror_runtime_files": mirror_n, "mirror_files": man.get("file_count"),
            "git_head": man.get("git", {}).get("head"), "synced_utc": man.get("synced_utc"),
            "venv_ok": bool((man.get("venv") or {}).get("cocotb_vpi_lib")), "spike": man.get("spike_present"),
            "source": mode, "head_sha": man.get("head_sha")}


def self_test() -> int:
    """The HEAD export is the committed tree: a tracked file that differs in the working tree is exported at
    its committed content, and the export carries no .git and no work/ subtree."""
    ok = True
    stage = C.WORK_DIR / "head_stage_selftest"
    sha = export_head(stage)
    cond = (stage / "dv" / "auto_dv" / "flow" / "gen_flow_const.py").is_file() and not (stage / ".git").exists()
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"HEAD {sha[:12]} exported with the flow sources and without .git")
    r = subprocess.run(["git", "-C", str(C.REPO_ROOT), "status", "--porcelain", "--untracked-files=no", "--", "dv/auto_dv", "rtl"],
                       capture_output=True, text=True)
    modified = [l[3:].strip() for l in r.stdout.splitlines() if l[:2].strip() in ("M", "MM", "AM") and not l[3:].startswith("dv/auto_dv/work")]
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
    shutil.rmtree(stage, ignore_errors=True)
    print("SELF-TEST:", "PASS" if ok else "FAIL")
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
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.mirror_root is None:
        U.die(f"no mirror root: set mirror_root in {C.SITE_YAML} or GEN_DV_MIRROR_ROOT")
    dst = a.mirror_root.resolve()
    if a.sync:
        U.require_env("rsync")
        if not U.path_is_shared(dst):
            U.log(f"WARNING: {dst} is on a local filesystem; LSF hosts will not see it")
        logs = dst.parent / (dst.name + "_logs")
        logs.mkdir(parents=True, exist_ok=True)
        if a.source == C.SOURCE_MODE_HEAD:
            stage = C.WORK_DIR / "head_stage"
            sha = export_head(stage)
            src_root = stage
            U.log(f"HEAD {sha[:12]} exported to {stage}")
        else:
            src_root, sha = C.REPO_ROOT, U.git_head()["head"]
        rsync(src_root, dst, logs / "rsync.log")
        prev = load_manifest(dst) or {}
        man: dict[str, Any] = {"mirror_root": str(dst), "clone": str(C.REPO_ROOT), "synced_utc": U.now_utc(),
                               "git": U.git_head(), "source": a.source, "head_sha": sha,
                               "items": MIRROR_ITEMS + MIRROR_GLOB_ITEMS, "excludes": MIRROR_EXCLUDES}
        man["tree_sha256"], man["runtime_file_count"] = tree_hash(dst)
        man["file_count"] = len(mirrored_files(dst))
        man["runtime_hash_globs"] = RUNTIME_HASH_GLOBS
        man["spike_present"] = rsync_spike(C.REPO_ROOT, dst, logs / "rsync_spike.log") if a.spike \
            else (dst / SPIKE_ITEM / "bin" / "spike").is_file()
        # Without --venv the venv facts (incl. the requirements hash it was BUILT from) carry over.
        man["venv"] = build_venv(dst, logs / "venv.log") if a.venv else prev.get("venv")
        U.dump_yaml(man, dst / MANIFEST_NAME)
        U.log(f"mirror manifest {dst / MANIFEST_NAME}: source {a.source}, {man['file_count']} files, sha256 {man['tree_sha256'][:16]}..., "
              f"git {man['git']['head'][:12]}, venv {'ok' if (man.get('venv') or {}).get('cocotb_vpi_lib') else 'MISSING'}, "
              f"spike {man['spike_present']}")
    if a.check or a.status:
        st = status(dst)
        for k, v in st.items():
            print(f"{k}: {v}")
        if a.check and st["state"] != "fresh":
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
