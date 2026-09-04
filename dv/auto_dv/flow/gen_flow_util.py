#!/usr/bin/env python3
"""Shared helpers of the generated regression flow: yaml io, hashing, tool checks, testlist
loading, deterministic seeds, bounded subprocesses and the LSF submit-and-watch primitive."""

from __future__ import annotations

import datetime as _dt
import fnmatch
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


def manifest_test_mismatch(manifest_path: Path, entry_name: str) -> str | None:
    """The reason an entry must not name this manifest, or None. gen_fcov.check_test compares the manifest's own
    declared test against the entry name before it reads coverage, so a mismatch can only end unverifiable; caught
    here at load time instead. Scoped to that one field: the manifest's full schema is the sweep's business."""
    data = load_yaml(manifest_path)
    if not isinstance(data, dict):
        return "is not a mapping, so it declares no test"
    declared = data.get("test")
    if declared != entry_name:
        return f"declares test {declared!r}, not the entry name {entry_name!r}"
    return None


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


def filelist_entries(flist: Path, root: Path = C.SOURCE_ROOT) -> list[Path]:
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
        per_list[str(fl.relative_to(C.SOURCE_ROOT))] = sha256_file(fl)
        for src in filelist_entries(fl):
            if not src.is_file():
                die(f"{fl}: listed source missing: {src}")
            combined.update(src.read_bytes())
            n += 1
    return {"filelists": per_list, "sources_sha256": combined.hexdigest(), "source_count": n}


def sv_covergroup_files(flists: list[Path]) -> list[str]:
    """Sources of the given -f files that declare a covergroup (comments stripped), relative to the source root when
    inside it: the build manifest's covergroups_declared fact (lexical: comments stripped, ifdefs not evaluated)."""
    found: list[str] = []
    for fl in flists:
        for src in filelist_entries(fl):
            if src.suffix not in C.SV_SOURCE_SUFFIXES or not src.is_file():
                continue
            text = re.sub(r"/\*.*?\*/", "", src.read_text(encoding="utf-8", errors="replace"), flags=re.S)
            if any(C.COVERGROUP_DECL_RE.search(l.split("//", 1)[0]) for l in text.splitlines()):
                found.append(str(src.relative_to(C.SOURCE_ROOT)) if src.is_relative_to(C.SOURCE_ROOT) else str(src))
    return found


def load_build_manifest(path: Path) -> tuple[dict[str, Any] | None, Path]:
    """A build dir or its build_manifest.yaml -> (manifest or None when absent, the manifest path)."""
    p = path / C.BUILD_MANIFEST if path.is_dir() else path
    return (load_yaml(p) if p.is_file() else None), p


def b8_probe_sv_default_on(path: Path = C.B8_PROBE_SV) -> bool | None:
    """The B8 probe module's own enable default (`bit en = 1'b0;` in gen_b8_probe.sv) as a truth value, None when the file
    or the declaration is missing: the second build manifest fact behind the LOG-067 measured-dispatch refusal, because
    the probe reads its plusarg over that literal, not over the rendered knob table."""
    if not path.is_file():
        return None
    m = C.B8_PROBE_SV_DEFAULT_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    return None if m is None else m.group(1) == "1"


def measured_dispatch_verdict(canary_manifest: dict[str, Any] | None, where: str, pinned_sha: str | None) -> tuple[str, str | None]:
    """(decision, refusal): CANARY_ACCEPTED with None when the canary build manifest is a head-mode build of the pinned
    commit, records covergroups_declared true and records both B8 probe defaults off (LOG-067); else the decision naming the
    failed condition (CANARY_REFUSED_UNBOUND: no manifest, a worktree build whose covergroups may be an in-progress edit, a
    head build of another commit, or no pin; CANARY_REFUSED_NO_COVERGROUPS; CANARY_REFUSED_B8_PROBE, an absent fact
    included) with the refusal text naming the build, the manifest and the rule."""
    man = canary_manifest or {}
    head = f"canary build {man.get('build') or '?'} ({where})"
    decision = C.CANARY_REFUSED_UNBOUND
    if not man:
        why = "has no build manifest"
    elif man.get("source_mode") != C.SOURCE_MODE_HEAD:
        why = f"is a {man.get('source_mode') or 'unknown'}-mode build, not a head-mode build of the pinned commit"
    elif not pinned_sha:
        why = "cannot be bound: no pinned commit given"
    elif str(man.get("head_sha") or "") != pinned_sha:
        why = f"is the head-mode build of {str(man.get('head_sha') or '?')[:12]}, not of the pinned {pinned_sha[:12]}"
    elif man.get(C.COVERGROUPS_DECLARED_KEY) is not True:
        val = man.get(C.COVERGROUPS_DECLARED_KEY)
        decision, why = C.CANARY_REFUSED_NO_COVERGROUPS, f"records {C.COVERGROUPS_DECLARED_KEY}={'absent' if val is None else val}"
    else:
        facts = {k: man.get(k) for k in (C.B8_PROBE_KNOB_DEFAULT_KEY, C.B8_PROBE_SV_DEFAULT_KEY)}
        bad = {k: v for k, v in facts.items() if v is not False}
        if not bad:
            return C.CANARY_ACCEPTED, None
        decision = C.CANARY_REFUSED_B8_PROBE
        why = "records " + ", ".join(f"{k}={'absent' if v is None else v}" for k, v in bad.items()) + f" ({C.B8_PROBE_KNOB}); {C.B8_PROBE_RULE}"
    return decision, f"measured dispatch refused: {head} {why}; {C.MEASURED_DISPATCH_RULE}"


def measured_dispatch_refusal(canary_manifest: dict[str, Any] | None, where: str, pinned_sha: str | None) -> str | None:
    """The refusal text of measured_dispatch_verdict, None when the dispatch is allowed."""
    return measured_dispatch_verdict(canary_manifest, where, pinned_sha)[1]


def canary_build_facts(path: Path | None) -> dict[str, Any] | None:
    """The gate's inputs as a record for manifests and evidence: the build dir, its manifest path and the facts read."""
    if path is None:
        return None
    man, mp = load_build_manifest(path)
    man = man or {}
    return {"path": str(path), "manifest": str(mp), "manifest_present": bool(man), "build": man.get("build"),
            "source_mode": man.get("source_mode"), "head_sha": man.get("head_sha"),
            C.COVERGROUPS_DECLARED_KEY: man.get(C.COVERGROUPS_DECLARED_KEY), "covergroup_files": man.get("covergroup_files"),
            C.B8_PROBE_KNOB_DEFAULT_KEY: man.get(C.B8_PROBE_KNOB_DEFAULT_KEY), C.B8_PROBE_SV_DEFAULT_KEY: man.get(C.B8_PROBE_SV_DEFAULT_KEY)}


def remove_tree_guarded(path: Path, roots: tuple[Path, ...], what: str) -> int:
    """The flow's only way to delete a directory it computed (owner ruling A-002): the path must exist, be a directory
    and lie under one of the given roots (the out root, the work dir, the head-mirror family), else die; what is
    removed is logged with its entry count. Returns that count (0 for an empty directory, removed with rmdir)."""
    p = path.resolve()
    under = [r for r in roots if r is not None and (p == Path(r).resolve() or Path(r).resolve() in p.parents)]
    if not under:
        die(f"refusing to remove {what} {p}: not under any of {[str(r) for r in roots if r is not None]} (A-002)")
    if p in {Path(r).resolve() for r in roots if r is not None}:
        die(f"refusing to remove {what} {p}: it is a root itself (A-002)")
    if not p.is_dir():
        die(f"refusing to remove {what} {p}: not an existing directory (A-002)")
    n = sum(1 for _ in p.rglob("*"))
    if n == 0:
        p.rmdir()
    else:
        shutil.rmtree(p)
    log(f"removed {what} {p} ({n} entries) under {under[0]}")
    return n


def remove_selftest_tree(path: Path) -> int:
    """A self-test removes only what it created under the self-test scratch root (GEN_DV_SELFTEST_TMP or the default)."""
    return remove_tree_guarded(path, (Path(C.selftest_tmp()),), "self-test dir")


def git_head() -> dict[str, Any]:
    def run(args: list[str]) -> str:
        r = subprocess.run(["git", *args], cwd=C.REPO_ROOT, capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else ""
    dirty = run(["status", "--porcelain", "--untracked-files=no"])
    return {"head": run(["rev-parse", "HEAD"]), "branch": run(["rev-parse", "--abbrev-ref", "HEAD"]),
            "dirty_tracked_files": bool(dirty)}


def _matches_direct(path: str, pattern: str) -> bool:
    """A glob of the non-input list matches a file directly under the glob's directory, never in a subdirectory
    (fnmatch alone lets * cross a slash)."""
    pdir, _, pname = pattern.rpartition("/")
    fdir, _, fname = path.rpartition("/")
    return fdir == pdir and fnmatch.fnmatchcase(fname, pname)


def is_build_input(path: str) -> bool:
    """The hold's classifier (dv/auto_dv/docs/gen_build_input_gate_rule.md): a mirrored file is a build input unless it
    is a listed hand-run tool or a record document directly under dv/auto_dv/docs; an unknown or new file is an input."""
    p = path.strip()
    if p in C.BUILD_INPUT_NONINPUT_TOOLS or p in C.BUILD_INPUT_NONINPUT_DOCS:
        return False
    return not any(_matches_direct(p, g) for g in C.BUILD_INPUT_NONINPUT_DOC_GLOBS)


def classify_delta(names: list[str]) -> tuple[list[str], list[str]]:
    """Differing file names split into (inputs, noninputs), each sorted without duplicates; inputs decide the hold."""
    inputs = sorted({n for n in names if is_build_input(n)})
    noninputs = sorted({n for n in names if not is_build_input(n)})
    return inputs, noninputs


def noninput_list_sha256() -> str:
    """Digest of the rendered non-input list, recorded so a batch record states which list decided."""
    rendered = "\n".join([*C.BUILD_INPUT_NONINPUT_TOOLS, *C.BUILD_INPUT_NONINPUT_DOCS, *C.BUILD_INPUT_NONINPUT_DOC_GLOBS]) + "\n"
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def noninput_list_check(repo_root: Path = C.REPO_ROOT) -> list[str]:
    """Problems of the non-input list against `git ls-files`: a listed file that is not tracked, a glob class that
    matches no tracked file. Empty when the list cannot have rotted."""
    r = subprocess.run(["git", "-C", str(repo_root), "ls-files", "--", "dv/auto_dv/tools", "dv/auto_dv/docs"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return [f"git ls-files failed: {r.stderr.strip()[:200]}"]
    tracked = set(r.stdout.split())
    problems = [f"not tracked: {n}" for n in (*C.BUILD_INPUT_NONINPUT_TOOLS, *C.BUILD_INPUT_NONINPUT_DOCS) if n not in tracked]
    problems += [f"glob matches no tracked file: {g}" for g in C.BUILD_INPUT_NONINPUT_DOC_GLOBS
                 if not any(_matches_direct(f, g) for f in tracked)]
    return problems


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

    def other_manifest(test_name: str) -> str:
        """A committed manifest in the home whose stem is not test_name (the self-test's group-manifest stand-in)."""
        home = C.FCOV_EXPECT_DIR.relative_to(C.SOURCE_ROOT).as_posix()
        names = sorted(p.name for p in C.FCOV_EXPECT_DIR.glob(f"*{C.FCOV_MANIFEST_SUFFIX}") if p.name != f"{test_name}{C.FCOV_MANIFEST_SUFFIX}")
        return f"{home}/{names[0]}"

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
        cond = red_expect_error(".*") is not None and red_expect_error("(") is not None and red_expect_error("") is not None \
            and red_expect_error("GEN_TEST_FAIL gen_x") is None
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", "red_expect_error: empty-matching, invalid and empty refused; a real signature accepted (one rule for loader and CLI)")
        cond = clone_relative_file("dv/auto_dv/flow/gen_stim.py") is not None and clone_relative_file("dv/auto_dv/flow/../../../ci/env.sh") is None \
            and clone_relative_file(str(C.REPO_ROOT / "ci" / "env.sh")) is None and clone_relative_file("dv/auto_dv/flow/gen_missing.py") is None
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", "clone_relative_file: accepts a clone file, refuses .., absolute and missing paths")
        import contextlib
        import io
        for label, mutate, *want in (
                ("red_fixture with expected_fail", lambda d: d["tests"][0].update(red_fixture=True, expected_fail=True, measured=False)),
                ("red_fixture with measured true", lambda d: d["tests"][0].update(red_fixture=True, measured=True, tier="smoke")),
                ("red_fixture without red_expect", lambda d: d["tests"][0].update(red_fixture=True, measured=False)),
                ("red_fixture with an invalid red_expect regex", lambda d: d["tests"][0].update(red_fixture=True, measured=False, red_expect="(")),
                ("red_expect without red_fixture", lambda d: d["tests"][0].update(red_expect="x")),
                ("red_expect matching the empty string (.*)", lambda d: d["tests"][0].update(red_fixture=True, measured=False, red_expect=".*")),
                ("red_expect matching the empty string (x?)", lambda d: d["tests"][0].update(red_fixture=True, measured=False, red_expect="x?")),
                ("red_expect matching the empty string (^)", lambda d: d["tests"][0].update(red_fixture=True, measured=False, red_expect="^")),
                ("program with generator and directed", lambda d: d["tests"][0].update(program={"generator": "dv/auto_dv/flow/gen_stim.py", "directed": ["x.S"], "seed": "run"})),
                ("program.generator naming a missing script", lambda d: d["tests"][0].update(program={"generator": "dv/auto_dv/tests/gen_programs/gen_missing_prog.py", "seed": "run"})),
                ("program.generator_args without generator", lambda d: d["tests"][0].update(program={"directed": ["dv/auto_dv/stim/gen_directed/gen_zc_directed.S"], "generator_args": ["--red"], "seed": "run"})),
                ("program.generator escaping the clone with ..", lambda d: d["tests"][0].update(program={"generator": "dv/auto_dv/flow/../../../ci/env.sh", "seed": "run"})),
                ("an export file value escaping the run directory", lambda d: d["tests"][0].update(plusargs=d["tests"][0]["plusargs"] + ["+gen_export_file=../outside.txt"])),
                ("an absolute export file value", lambda d: d["tests"][0].update(plusargs=d["tests"][0]["plusargs"] + ["+gen_export_file=/tmp/x.txt"])),
                ("a generic GEN_TEST_FAIL red_expect under red_expect_policy [fire_id]", lambda d: (d.__setitem__("red_expect_policy", ["fire_id"]),
                    d["tests"][0].update(red_fixture=True, measured=False, red_expect="GEN_TEST_FAIL gen_smoke: [0-9]+ fire-check failure"))),
                ("an unknown red_expect_policy token", lambda d: d.__setitem__("red_expect_policy", ["bogus"])),
                ("a red_expect that does not match its retained pinned-red log's harness line",
                 lambda d: next(t for t in d["tests"] if t["name"] == "gen_test_csr_access_red").update(red_expect=r"GEN_TEST_FAIL gen_test_csr_access: [0-9]+ fire-check failure\(s\):.*\bfire_tp_csr_999\b"),
                 "does not match the retained log's harness line"),
                ("a generic harness signature hidden behind a leading .* (policy fire_id)",
                 lambda d: next(t for t in d["tests"] if t.get("red_fixture")).update(red_expect=r".*GEN_TEST_FAIL x: [0-9]+ fire-check failure"),
                 "names no fire_ id"),
                ("witness_ids naming a TP id absent from the CSV", lambda d: d["tests"][0].update(witness_ids=["TP-NOPE-999"])),
                ("witness_ids as a bare string", lambda d: d["tests"][0].update(witness_ids="TP-BIT-036")),
                ("debug_only_plusargs missing a knob marked debug_only", lambda d: d.__setitem__("debug_only_plusargs", d["debug_only_plusargs"][:-1])),
                ("a measured entry turning on the B8 probe knob (LOG-067)",
                 lambda d: d["tests"][0].update(measured=True, tier="smoke", plusargs=d["tests"][0]["plusargs"] + [f"+{C.PLUSARG_CHK_SVA_B8}=1"]),
                 "LOG-067"),
                ("an fcov_expectation_file outside dv/auto_dv/fcov_expectations (CM153-L-1: the schema's manifest home)",
                 lambda d: d["tests"][0].update(measured=False, tier=C.CHECK_TIER, fcov_expectation_file="dv/auto_dv/evidence/gen_fcov_proof_slice5e.fcov.yaml"),
                 "is outside"),
                ("an fcov_expectation_file naming a missing file (CM153-L-1)",
                 lambda d: d["tests"][0].update(measured=False, tier=C.CHECK_TIER, fcov_expectation_file="dv/auto_dv/fcov_expectations/gen_no_such_test.fcov.yaml"),
                 "does not exist under"),
                ("a measured entry whose fcov_expectation_file stem is another test's (CM153-L-1, validate_manifest needs test == stem == entry)",
                 lambda d: d["tests"][0].update(measured=True, tier="smoke", fcov_expectation_file=other_manifest(d["tests"][0]["name"])),
                 "must be"),
                ("an unmeasured entry whose fcov_expectation_file stem is another test's (CR-23-L-1: check_test validates against the entry name whether measured or not)",
                 lambda d: d["tests"][0].update(measured=False, tier=C.CHECK_TIER, fcov_expectation_file=other_manifest(d["tests"][0]["name"])),
                 "must be"),
                ("a measured entry with icache ECC injection on and the alert_minor row off (LOG-077)",
                 lambda d: d["tests"][0].update(measured=True, tier="smoke", plusargs=d["tests"][0]["plusargs"] + [f"+{C.PLUSARG_KNOB_ICACHE_ECC_ERR_RATE}=rare", f"+{C.PLUSARG_CHK_ALERT_MINOR}=0"]),
                 "LOG-077"),
                ("a testlist plusarg value carrying a space (CM168-I-1)",
                 lambda d: d["tests"][0].update(plusargs=d["tests"][0]["plusargs"] + [f"+{C.PLUSARG_CHK_ALL}= 1"]),
                 "no whitespace"),
                ("a testlist plusarg value carrying a tab (CM168-I-1)",
                 lambda d: d["tests"][0].update(plusargs=d["tests"][0]["plusargs"] + [f"+{C.PLUSARG_CHK_ALL}=\t1"]),
                 "no whitespace"),
                ("a testlist plusarg value carrying a trailing newline (CM168-I-1: the widened value group accepted it)",
                 lambda d: d["tests"][0].update(plusargs=d["tests"][0]["plusargs"] + [f"+{C.PLUSARG_CHK_ALL}=1\n"]),
                 "no whitespace"),
                ("a testlist plusarg value carrying a carriage return (CM168-I-1)",
                 lambda d: d["tests"][0].update(plusargs=d["tests"][0]["plusargs"] + [f"+{C.PLUSARG_CHK_ALL}=1\r"]),
                 "no whitespace")):
            t2 = load_yaml(C.TESTLIST_YAML)
            mutate(t2)
            f = Path(td) / "testlist_bad.yaml"
            f.write_text(_y.safe_dump(t2, sort_keys=False), encoding="utf-8")
            err = io.StringIO()
            try:
                with contextlib.redirect_stderr(err):
                    load_testlist(f)
                cond = False
            except SystemExit:
                cond = not want or want[0] in err.getvalue()   # the refusal names the rule, not just any exit
            ok &= cond
            print("SELF-TEST", "ok " if cond else "BAD", f"load_testlist refuses {label}" + (f" (message names {want[0]!r})" if want else ""))
        # The manifest's own declared test against the entry name (the loader's third equality). Exercised on the
        # helper with fabricated files, because the loader refuses a manifest outside the manifest home and a
        # loader-level fixture would mean writing into a committed directory during a self-test.
        for label, doc, want in (
                ("a manifest declaring the entry's own name passes", {"test": "gen_probe_entry", "owner": "runtime"}, None),
                ("a manifest declaring another test is refused", {"test": "gen_other_entry", "owner": "runtime"}, "gen_other_entry"),
                ("a manifest with no test key is refused", {"owner": "runtime"}, "None"),
                ("a manifest that is not a mapping is refused", ["not", "a", "mapping"], "not a mapping")):
            fx = Path(td) / "gen_probe_entry.fcov.yaml"
            fx.write_text(_y.safe_dump(doc, sort_keys=False), encoding="utf-8")
            why = manifest_test_mismatch(fx, "gen_probe_entry")
            cond = (why is None) if want is None else (why is not None and want in why)
            ok &= cond
            print("SELF-TEST", "ok " if cond else "BAD", f"manifest_test_mismatch: {label} (got {why!r})")
        # LOG-067, the positive side: an unmeasured entry may turn the B8 probe knob on (a B8 evidence run).
        t3 = load_yaml(C.TESTLIST_YAML)
        t3["tests"][0].update(measured=False, tier=C.CHECK_TIER, plusargs=t3["tests"][0]["plusargs"] + [f"+{C.PLUSARG_CHK_SVA_B8}=1"])
        f3 = Path(td) / "testlist_b8_unmeasured.yaml"
        f3.write_text(_y.safe_dump(t3, sort_keys=False), encoding="utf-8")
        try:
            load_testlist(f3)
            cond = True
        except SystemExit:
            cond = False
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", "load_testlist accepts an unmeasured entry that turns the B8 probe knob on (B8 evidence runs stay possible)")
        # No unmeasured exemption: gen_fcov validates the manifest against the entry name on every entry, so null
        # is the only alternative to the entry naming its own manifest.
        for label, upd in (("a null fcov_expectation_file loads", dict(fcov_expectation_file=None)),):
            t5 = load_yaml(C.TESTLIST_YAML)
            t5["tests"][0].update(upd)
            f5 = Path(td) / "testlist_fcov_ok.yaml"
            f5.write_text(_y.safe_dump(t5, sort_keys=False), encoding="utf-8")
            try:
                load_testlist(f5)
                cond = True
            except SystemExit:
                cond = False
            ok &= cond
            print("SELF-TEST", "ok " if cond else "BAD", f"load_testlist: {label}")
        # LOG-077, the positive side: the row at its table default, or the run unmeasured, loads.
        for label, upd in (("a measured entry with the ECC rate rare and the alert_minor row at its default loads",
                            dict(measured=True, tier="smoke", plusargs=t3["tests"][0]["plusargs"][:1] + [f"+{C.PLUSARG_KNOB_ICACHE_ECC_ERR_RATE}=rare"])),
                           ("an unmeasured entry with the ECC rate frequent and the row off loads (evidence run)",
                            dict(measured=False, tier=C.CHECK_TIER, plusargs=t3["tests"][0]["plusargs"][:1] + [f"+{C.PLUSARG_KNOB_ICACHE_ECC_ERR_RATE}=frequent", f"+{C.PLUSARG_CHK_ALERT_MINOR}=0"]))):
            t4 = load_yaml(C.TESTLIST_YAML)
            t4["tests"][0].update(upd)
            f4 = Path(td) / "testlist_log077_ok.yaml"
            f4.write_text(_y.safe_dump(t4, sort_keys=False), encoding="utf-8")
            try:
                load_testlist(f4)
                cond = True
            except SystemExit:
                cond = False
            ok &= cond
            print("SELF-TEST", "ok " if cond else "BAD", f"load_testlist: {label}")
        # The positive side of the policy: a fire_ id in the signature is accepted.
        t3 = load_yaml(C.TESTLIST_YAML); t3["red_expect_policy"] = ["fire_id"]
        for t in t3["tests"]:
            if t.get("red_fixture") and str(t.get("red_expect", "")).startswith("GEN_TEST_FAIL") and "fire_" not in t["red_expect"]:
                t["red_expect"] = t["red_expect"] + r"\(s\): fire_eot_pass_code"
        f3 = Path(td) / "testlist_policy_ok.yaml"; f3.write_text(_y.safe_dump(t3, sort_keys=False), encoding="utf-8")
        try:
            load_testlist(f3); cond = True
        except SystemExit:
            cond = False
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", "red_expect_policy [fire_id] accepts signatures that name a fire_ id")
    # Witness table: the CSV's index column is the rendered index; a valid id resolves, an unknown id dies.
    wt = witness_index()
    cond = wt.get("TP-BIT-036") == 0 and len(wt) >= 200
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"witness_index from the real CSV: TP-BIT-036 -> {wt.get('TP-BIT-036')}, {len(wt)} ids")
    # T-226: the as-built protocol. Two ids of one owner group render (indices, the group's index, no plusarg unless the
    # TB declares one); an unknown id and ids of two owner groups are refused.
    w_ids, w_group_of, w_groups = witness_tables()
    grp = w_group_of["TP-DBG-004"]
    same = [i for i in w_ids if w_group_of[i] == grp][:2]
    rec = witness_render({"name": "gen_x", "witness_ids": same})
    cond = rec is not None and rec["indices"] == [wt[i] for i in same] and rec["owner_group"] == grp and rec["group_index"] == w_groups[grp] \
        and (rec["plusarg"] is None) == (witness_plusarg_name() is None) and "COV_WITNESS" in rec["protocol"]
    refused = []
    for ids in (["TP-NOPE-999"], ["TP-BIT-036", "TP-BIT-042"]):
        try:
            witness_render({"name": "gen_x", "witness_ids": ids}); refused.append(False)
        except SystemExit:
            refused.append(True)
    cond = cond and refused == [True, True] and w_group_of["TP-BIT-036"] != w_group_of["TP-BIT-042"]
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"witness_render (T-226): {same} of {grp} -> indices {rec['indices'] if rec else None}, group index {rec['group_index'] if rec else None}, plusarg {rec['plusarg'] if rec else None}; an unknown id and ids of two owner groups are refused {refused}")
    # export_facts on the real rendered table: exact rows only, every row a (source, event, fields) triple.
    ef = export_facts()
    cond = len(ef["export_sources"]) >= 1 and all(set(r) == {"source", "event", "fields"} for r in ef["export_sources"]) \
        and not any("*" in r["source"] or "*" in r["event"] for r in ef["export_sources"]) \
        and "gen_export_file" in ef["export_knobs"]
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"export_facts from the rendered table: {len(ef['export_sources'])} exact rows over sources {ef['export_source_names']}, knobs {sorted(ef['export_knobs'])}")
    # Declared rows: empty until an active-source list is rendered (never the rendered table); the emitted set is
    # never declared at build time (LOG-028a): empty with the unobserved origin until export files are observed.
    cond = isinstance(ef["export_sources_declared"], list) and (ef["export_sources_declared"] == [] or "EXPORT_ACTIVE_SOURCES" in ef["export_sources_declared_origin"]) \
        and ef["export_sources_emitted"] == [] and ef["export_sources_emitted_origin"] == C.EXPORT_EMITTED_UNOBSERVED and ef["export_rows_observed"] == []
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"export_sources_declared: {len(ef['export_sources_declared'])} rows ({ef['export_sources_declared_origin'][:60]}); emitted empty until observed")
    import tempfile as _tf0
    with _tf0.TemporaryDirectory(prefix="gen_flow_util_selftest_", dir=C.selftest_tmp()) as td0:
        # Fixture export files of one build: two runs, overlapping rows; the first run wins the first-seen slot.
        fa, fb, fc = Path(td0) / "a.txt", Path(td0) / "b.txt", Path(td0) / "c.txt"
        fa.write_text("# gen_export v2 seed=1 sources=ibus,pin fields=order\n# events ibus req addr\nE 0 pin fetch_enable a\nE 5 ibus req 80000000 0 f\nR 1 x\nE 7 ibus req 80000004 0 f\n", encoding="utf-8")
        fb.write_text("# gen_export v2 seed=2 sources=ibus,dbus fields=order\nE 0 ibus req 80000000 0 f\nE 3 dbus gnt 10000000 1 f\n", encoding="utf-8")
        fc.write_text("no header here\nE 0 misc bogus 1\n", encoding="utf-8")
        obs = export_observe([("run_a", fa), ("run_b", fb), ("run_c", fc)])
        rows = {r["row"]: r for r in obs["rows"]}
        cond = obs["sources"] == ["dbus", "ibus", "pin"] and obs["files"] == 2 and set(rows) == {"pin fetch_enable", "ibus req", "dbus gnt"} \
            and rows["ibus req"]["first_run"] == "run_a" and rows["ibus req"]["first_line"] == "E 5 ibus req 80000000 0 f" \
            and rows["dbus gnt"]["first_run"] == "run_b" and "misc bogus" not in rows
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"export_observe: sources union {obs['sources']} from 2 headed files, {len(rows)} first-seen rows, first run wins, a headerless file is skipped")
        rendered = [{"source": "ibus", "event": "req", "fields": []}, {"source": "dbus", "event": "gnt", "fields": []}, {"source": "icram", "event": "x", "fields": []}]
        em = emitted_from_observed(rendered, obs["sources"])
        cond = [r["source"] for r in em] == ["ibus", "dbus"]
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"emitted_from_observed: rendered rows kept only for header-named sources ({[r['source'] for r in em]})")
    import tempfile as _tf
    with _tf.TemporaryDirectory(prefix="gen_flow_util_selftest_", dir=C.selftest_tmp()) as td2:
        hp = Path(td2) / "gen_export.txt"
        hp.write_text("# gen_export v1 seed=1 build_config=opentitan counters=0 sources=ibus,dbus fields=order,pc_rdata\n# image x\n", encoding="utf-8")
        got = export_header_sources(hp)
        hp.write_text("# gen_export v1 seed=1 build_config=opentitan counters=0 sources= fields=order\n", encoding="utf-8")
        got_empty = export_header_sources(hp)
        cond = got == ["ibus", "dbus"] and got_empty == [] and export_header_sources(Path(td2) / "missing.txt") is None
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"export_header_sources: fabricated header sources=ibus,dbus -> {got}, empty -> {got_empty}, missing file -> None")
    rows_i = [{"source": "ibus", "event": "req", "fields": []}]
    cond = emitted_check([], []) is None and emitted_check(rows_i, ["ibus"]) is None \
        and "only in header ['ibus']" in (emitted_check([], ["ibus"]) or "") and "only in manifest ['ibus']" in (emitted_check(rows_i, []) or "")
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", "emitted_check: equal sets pass (empty and non-empty), a mismatch names the difference both ways")
    rows_id = rows_i + [{"source": "dbus", "event": "req", "fields": []}]
    cond = emitted_check(rows_id, ["ibus"], subset_ok=True) is None and emitted_check(rows_id, ["ibus"]) is not None \
        and "only in header ['pin']" in (emitted_check(rows_id, ["pin"], subset_ok=True) or "")
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", "emitted_check: with the sources knob narrowed a header subset passes, a source the build cannot emit still fails; unnarrowed needs equality")
    with tempfile.TemporaryDirectory(dir=C.selftest_tmp()) as td3:
        dup = Path(td3) / "dup.csv"
        dup.write_text("index,tp_item\n0,TP-X-001\n1,TP-X-002\n2,TP-X-001\n", encoding="utf-8")
        saved, C.WITNESS_CSV = C.WITNESS_CSV, dup
        try:
            witness_index(); dup_refused = False
        except SystemExit:
            dup_refused = True
        finally:
            C.WITNESS_CSV = saved
    cond = dup_refused
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", "witness_index: a CSV listing one TP id twice stops the flow")
    # Job and generator environments: the submitting shell's PYTHONPATH and staged-entries pointer never reach a run.
    import gen_run as _R
    import gen_stim as _S
    with tempfile.TemporaryDirectory(dir=C.selftest_tmp()) as td4:
        js = Path(td4) / "run_cmd.sh"
        _R.write_job_script(js, {"outdir": td4, "build": "x"}, ["simv"], {"SIM_DIR": td4, "PYTHONPATH": "/root"}, 10, Path(td4))
        lines = js.read_text(encoding="utf-8").splitlines()
        unset_at = [i for i, l in enumerate(lines) if l.startswith("unset ")]
        export_at = [i for i, l in enumerate(lines) if l.startswith("export ") and not l.startswith(f"export {C.ENV_TOOLCHECK_VAR}=")]
        marker_at = [i for i, l in enumerate(lines) if any(l == f"export {k}={v}" for k, v in C.JOB_ENV_SET.items())]
        cond = {l.split()[1] for l in lines if l.startswith("unset ")} == set(C.JOB_ENV_UNSET) and bool(unset_at) and bool(export_at) \
            and max(unset_at) < min(export_at) and any(l.startswith("export PYTHONPATH=") for l in lines) \
            and len(marker_at) == len(C.JOB_ENV_SET) and max(unset_at) < min(marker_at)
        slow_log = Path(td4) / "sim_stdout.log"
        slow_log.write_text("noise\nGEN_TEST_SLOW_TOTAL rounds=2 budget_cycles=300000\n$finish\n", encoding="utf-8")
        st = slow_total([Path(td4) / "missing.log", slow_log])
        cond_slow = st == {"rounds": 2, "budget_cycles": 300000} and slow_total([Path(td4) / "missing.log"]) is None
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"job script unsets {list(C.JOB_ENV_UNSET)} after cd, exports the flow-run marker {C.JOB_ENV_SET} and then the flow's own values (PYTHONPATH re-exported for cocotb)")
    ok &= cond_slow
    print("SELF-TEST", "ok " if cond_slow else "BAD", f"slow_total: parsed from the first log carrying the line ({st}); None without it")
    # Retained pinned-red log check on a fabricated evidence root: a suffixed check id defeats a \b-anchored signature.
    with tempfile.TemporaryDirectory(dir=C.selftest_tmp()) as td5:
        root = Path(td5); ev = root.joinpath(*C.RED_LOG_DIR_REL); ev.mkdir(parents=True)
        (ev / "gen_x_red1_stdout.log").write_text("UVM_INFO fine\nAssertionError: GEN_TEST_FAIL gen_test_x: 1 fire-check failure(s): fire_tp_x_001_ops: 3 ops\n"
                                                "** TESTS=1 PASS=0 FAIL=1 SKIP=0 **\n", encoding="utf-8")
        saved_root, C.SOURCE_ROOT = C.SOURCE_ROOT, root
        try:
            good = red_signature_check({"name": "gen_test_x_red", "pass_marker": "GEN_TEST_PASS", "red_expect": r"GEN_TEST_FAIL gen_test_x: [0-9]+ fire-check failure\(s\):.*\bfire_tp_x_001"})
            bad_sig = red_signature_check({"name": "gen_test_x_red", "pass_marker": "GEN_TEST_PASS", "red_expect": r"GEN_TEST_FAIL gen_test_x: [0-9]+ fire-check failure\(s\):.*\bfire_tp_x_001\b"})
            none = red_signature_check({"name": "gen_test_y_red", "pass_marker": "GEN_TEST_PASS", "red_expect": r"x"})
        finally:
            C.SOURCE_ROOT = saved_root
        (ev / "gen_z_red1_stdout.log").write_text("UVM_ERROR @ 5: [isa_rd] mismatch\nAssertionError: GEN_TEST_FAIL gen_test_z: 1 fire-check failure(s): fire_tp_z_001\n"
                                                "** TESTS=1 PASS=0 FAIL=1 SKIP=0 **\n", encoding="utf-8")
        z = {"name": "gen_test_z_red", "pass_marker": "GEN_TEST_PASS", "red_expect": r"GEN_TEST_FAIL gen_test_z: [0-9]+ fire-check failure\(s\):.*\bfire_tp_z_001(?!\d)"}
        saved_root, C.SOURCE_ROOT = C.SOURCE_ROOT, root
        try:
            stale_refused = red_signature_check(z)
            C.RED_STALE_ALLOWLIST["gen_test_z_red"] = ("T-XXX", "self-test entry")
            try:
                stale_allowed = red_signature_check(z)
            finally:
                del C.RED_STALE_ALLOWLIST["gen_test_z_red"]
        finally:
            C.SOURCE_ROOT = saved_root
        cond = good and good["refuse"] is None and good["harness_match"] and good["verdict"] == C.VERDICT_RED_OK and good["stale_cause"] is None \
            and bad_sig and bad_sig["refuse"] is not None and not bad_sig["harness_match"] and none is None \
            and stale_refused and stale_refused["refuse"] == C.RED_STALE_REFUSE and stale_refused["stale_evidence"] \
            and stale_allowed and stale_allowed["refuse"] is None and stale_allowed["stale_cause"] == C.RED_STALE_TEXT.format(task="T-XXX")
        # Lockstep family: a TB unit fixture failing through a collected UVM error, retained as an excerpt without a harness line.
        lk = root.joinpath(*C.RED_LOG_FAMILIES[1][0]); lk.mkdir(parents=True)
        (lk / "gen_refuse_me_red1_stdout_excerpt.log").write_text(
            "GEN_CONFIG_BANNER build_config=opentitan\n"
            "UVM_ERROR dv/auto_dv/env/gen_env_pkg.sv(97) @ 310500: uvm_test_top.env.dispatch [GEN_CMD_DISPATCH] REGIME_SET: no run-time consumer for knob_q (regime_set_consumer none)\n"
            "UVM_ERROR :    1\n  3115.01ns INFO     cocotb.regression                  gen_ut_refuse_me passed\n"
            "** TESTS=1 PASS=1 FAIL=0 SKIP=0 **\n", encoding="utf-8")
        saved_root, C.SOURCE_ROOT = C.SOURCE_ROOT, root
        try:
            lk_good = red_signature_check({"name": "gen_ut_refuse_me", "pass_marker": "GEN_UT_REFUSE_ME_PASS", "red_expect": r"UVM_ERROR .*\[GEN_CMD_DISPATCH\] REGIME_SET: no run-time consumer for "})
            lk_bad = red_signature_check({"name": "gen_ut_refuse_me", "pass_marker": "GEN_UT_REFUSE_ME_PASS", "red_expect": r"UVM_ERROR .*\[GEN_OTHER\]"})
        finally:
            C.SOURCE_ROOT = saved_root
        cond_lk = red_group("gen_ut_refuse_me") == "refuse_me" and red_group("gen_test_x_red") == "x" \
            and lk_good and lk_good["refuse"] is None and lk_good["verdict"] == C.VERDICT_RED_OK and lk_good["harness_match"] and "GEN_CMD_DISPATCH" in lk_good["harness_line"] \
            and lk_bad and lk_bad["refuse"] is not None and lk_bad["verdict"] != C.VERDICT_RED_OK and not lk_bad["stale_evidence"]
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", "red_signature_check: matching harness line passes (RED-OK), a \\b-anchored id defeated by a suffix is refused, no log -> None, a UVM error ahead of a matching harness line is refused (literal criterion) unless the entry is allowlisted, then stale with its task")
    ok &= cond_lk
    print("SELF-TEST", "ok " if cond_lk else "BAD", "lockstep family (gen_ut_ fixture, excerpt without a harness line): RED-OK with the matching red_expect is accepted, a non-matching red_expect is refused, groups strip gen_ut_/gen_test_ and _red")
    # CLI builders: a refused entry prints its refusal alone, an allowlisted stale entry its cause; the summary and exit code follow the counts.
    base = {"log": "/x/gen_q_red1_stdout.log", "harness_match": True, "verdict": C.VERDICT_FAIL, "refuse": None, "stale_evidence": False, "stale_cause": None}
    l_ok = red_check_line("gen_q_red", dict(base, verdict=C.VERDICT_RED_OK))
    l_ref = red_check_line("gen_q_red", dict(base, refuse=C.RED_STALE_REFUSE, stale_evidence=True, stale_cause=C.RED_STALE_TEXT.format(task="T-1")))
    l_mis = red_check_line("gen_q_red", dict(base, harness_match=False, refuse="red_expect does not match the retained log's harness line"))
    l_stale = red_check_line("gen_q_red", dict(base, stale_evidence=True, stale_cause=C.RED_STALE_TEXT.format(task="T-1")))
    s_ok = red_check_summary({}, {}); s_stale = red_check_summary({}, {C.RED_STALE_TEXT.format(task="T-1"): 2}); s_ref = red_check_summary({"harness-line mismatch": 1, "retained log not RED-OK": 2}, {})
    cond = l_ok.startswith("RED-CHECK ok  ") and "None" not in l_ref and l_ref.startswith("RED-CHECK FAIL") and C.RED_STALE_REFUSE in l_ref and "first collected" not in l_ref and "(T-1)" not in l_ref \
        and l_mis.startswith("RED-CHECK FAIL") and l_stale.startswith("RED-CHECK STALE") and "(T-1)" in l_stale \
        and s_ok == ("PASS", 0) and s_stale[1] == C.RED_CHECK_EXIT_STALE and s_stale[0].startswith("PASS (2 stale") \
        and s_ref[1] == C.RED_CHECK_EXIT_REFUSE and s_ref[0] == "FAIL (3 red entry(ies) refused: 1 harness-line mismatch; 2 retained log not RED-OK)"
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", "red check CLI builders: refused line without a stale suffix, stale line with its task, summary text and exit code per counts")
    # Request server partition: a head-mode request that merely carries an empty elcheck key builds and is pinned.
    import gen_serve_requests as _SR
    with tempfile.TemporaryDirectory(dir=C.selftest_tmp()) as td6:
        qa = Path(td6) / "a.yaml"; qa.write_text("requester: runtime\npurpose: 1\ntests: [gen_boot_zc]\nseeds: [1]\ncoverage: no\nelcheck:\nnotes: x\n", encoding="utf-8")
        qb = Path(td6) / "b.yaml"; qb.write_text("requester: rtl-arch\npurpose: 2\ntests: []\nseeds: []\ncoverage: no\nelcheck: {vdb: x, elfile: y}\nnotes: x\n", encoding="utf-8")
        qc = Path(td6) / "c.yaml"; qc.write_text("requester: runtime\npurpose: 3\ntests: [gen_boot_zc]\nseeds: [1]\ncoverage: no\nsource: worktree\nnotes: x\n", encoding="utf-8")
        pinned, p1, p234, rest = _SR.partition_pending([qa, qb, qc])
        cond = pinned == [qa] and p1 == [qa] and p234 == [] and rest == [qb, qc] and not _SR.request_is_elcheck(qa) and _SR.request_is_elcheck(qb)
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", "partition_pending: an empty elcheck key is not an elcheck (pinned, purpose-1 half); a real elcheck and a worktree request stay outside the hold")
    saved = {k: os.environ.get(k) for k in C.JOB_ENV_UNSET}
    try:
        for k in C.JOB_ENV_UNSET:
            os.environ[k] = "/leak"
        genv = _S.generator_env()
        cond = not any(k in genv for k in C.JOB_ENV_UNSET) and genv.get("PYTHONHASHSEED") == "0" and genv.get(C.ENV_BUILD_CONFIG) == C.BUILD_CONFIG
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", "generator environment drops the leaked variables, pins PYTHONHASHSEED and names the build configuration")
    try:
        if str(C.SOURCE_ROOT) not in sys.path:
            sys.path.insert(0, str(C.SOURCE_ROOT))
        import importlib as _il
        _tl = _il.import_module("dv.auto_dv.tests.gen_test_lib")
        cond, note = _tl.STAGED_ENTRIES_ENV in C.JOB_ENV_UNSET, f"gen_test_lib.STAGED_ENTRIES_ENV={_tl.STAGED_ENTRIES_ENV!r}"
        # The flow-run marker the template's guard reads must be the variable the job script exports (a rename on
        # either side is a BAD, as for the staged-entries variable).
        marker_ok, marker_note = _tl.FLOW_RUN_ENV in C.JOB_ENV_SET, f"gen_test_lib.FLOW_RUN_ENV={_tl.FLOW_RUN_ENV!r} vs JOB_ENV_SET {sorted(C.JOB_ENV_SET)}"
    except Exception as e:  # noqa: BLE001 - the harness module is the Test Writer's; report, do not crash
        cond, note = False, f"gen_test_lib not importable: {e}"
        marker_ok, marker_note = False, note
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"the staged-entries variable the harness reads is in JOB_ENV_UNSET ({note})")
    ok &= marker_ok
    print("SELF-TEST", "ok " if marker_ok else "BAD", f"the flow-run marker the template's guard reads is the one the job script exports ({marker_note})")
    for args, want_kept, want_dropped, label in (
            (["-cm_glitch", "0"], [], ["-cm_glitch", "0"], "value-taking flag takes its value"),
            (["-cm_seqnoconst", "-lca"], ["-lca"], ["-cm_seqnoconst"], "stand-alone -cm flag keeps the next argument"),
            (["-cm_glitch", "0", "-xlrm", "0"], ["-xlrm", "0"], ["-cm_glitch", "0"], "same value elsewhere survives (positions, not values)")):
        kept, dropped = drop_cm_args(args)
        cond = kept == want_kept and dropped == want_dropped
        ok &= cond
        print(f"SELF-TEST {'ok ' if cond else 'BAD'} drop_cm_args {label}: kept={kept} dropped={dropped}")
    cgd = Path(tempfile.mkdtemp(prefix="gen_cg_selftest_", dir=C.selftest_tmp()))
    (cgd / "a.sv").write_text("package p;\n  covergroup gen_x_cg @(posedge clk);\n  endgroup\nendpackage\n")
    (cgd / "b.sv").write_text("// covergroup gen_y_cg;\nmodule b; endmodule\n")
    (cgd / "c.sv").write_text("/* covergroup gen_z_cg;\n   endgroup */\nmodule c; endmodule\n")
    (cgd / "d.svh").write_text("`define GEN_COVERGROUP covergroup_like\n")
    (cgd / "e.v").write_text("covergroup not_sv;\n")
    (cgd / "f.f").write_text(f"// comment\n+incdir+{cgd}\n{cgd / 'a.sv'}\n{cgd / 'b.sv'} // trailing\n{cgd / 'c.sv'}\n{cgd / 'd.svh'}\n{cgd / 'e.v'}\n")
    cg = sv_covergroup_files([cgd / "f.f"])
    inside = (cgd / "a.sv").resolve().is_relative_to(C.SOURCE_ROOT)
    cond = [Path(x).name for x in cg] == ["a.sv"] and (Path(cg[0]).is_absolute() != inside if cg else False)
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"sv_covergroup_files: a declaration counts, line and block comments and a .v file do not: {cg}")
    remove_selftest_tree(cgd)
    gd = Path(tempfile.mkdtemp(prefix="gen_gate_selftest_", dir=C.selftest_tmp()))
    pin = "a" * 40
    def gate(man: dict[str, Any] | None, pinned: str | None = pin, where: Path = gd) -> str | None:
        if man is not None:
            dump_yaml(man, gd / C.BUILD_MANIFEST)
        return measured_dispatch_refusal(*load_build_manifest(where), pinned)
    head_ok = {"build": "gen_tb", "source_mode": C.SOURCE_MODE_HEAD, "head_sha": pin, C.COVERGROUPS_DECLARED_KEY: True, "covergroup_files": ["dv/auto_dv/env/x.sv"],
               C.B8_PROBE_KNOB_DEFAULT_KEY: False, C.B8_PROBE_SV_DEFAULT_KEY: False}
    r_true = gate(head_ok)
    r_false = gate(dict(head_ok, **{C.COVERGROUPS_DECLARED_KEY: False, "covergroup_files": []}))
    r_absent = gate({"build": "gen_tb", "source_mode": C.SOURCE_MODE_HEAD, "head_sha": pin})
    r_worktree = gate(dict(head_ok, source_mode=C.SOURCE_MODE_WORKTREE))
    r_other = gate(dict(head_ok, head_sha="b" * 40))
    r_nopin = gate(head_ok, pinned=None)
    r_none = gate(None, where=gd / "no_such_dir")
    r_b8_on = gate(dict(head_ok, **{C.B8_PROBE_KNOB_DEFAULT_KEY: True}))
    r_b8_absent = gate({k: v for k, v in head_ok.items() if k != C.B8_PROBE_KNOB_DEFAULT_KEY})
    r_sv_on = gate(dict(head_ok, **{C.B8_PROBE_SV_DEFAULT_KEY: True}))
    r_sv_absent = gate({k: v for k, v in head_ok.items() if k != C.B8_PROBE_SV_DEFAULT_KEY})
    cond_b8 = r_b8_on is not None and C.B8_PROBE_KNOB in r_b8_on and "LOG-067" in r_b8_on and r_b8_absent is not None and "absent" in r_b8_absent \
        and r_sv_on is not None and C.B8_PROBE_SV_DEFAULT_KEY in r_sv_on and r_sv_absent is not None and "absent" in r_sv_absent
    dump_yaml(dict(head_ok, **{C.B8_PROBE_KNOB_DEFAULT_KEY: True}), gd / C.BUILD_MANIFEST)
    v_b8 = measured_dispatch_verdict(*load_build_manifest(gd), pin)
    dump_yaml(dict(head_ok, **{C.COVERGROUPS_DECLARED_KEY: False}), gd / C.BUILD_MANIFEST)
    v_cg = measured_dispatch_verdict(*load_build_manifest(gd), pin)
    dump_yaml(dict(head_ok, source_mode=C.SOURCE_MODE_WORKTREE), gd / C.BUILD_MANIFEST)
    v_wt = measured_dispatch_verdict(*load_build_manifest(gd), pin)
    dump_yaml(head_ok, gd / C.BUILD_MANIFEST)
    v_ok = measured_dispatch_verdict(*load_build_manifest(gd), pin)
    cond_v = v_b8[0] == C.CANARY_REFUSED_B8_PROBE and v_cg[0] == C.CANARY_REFUSED_NO_COVERGROUPS and v_wt[0] == C.CANARY_REFUSED_UNBOUND \
        and v_ok == (C.CANARY_ACCEPTED, None) and v_b8[1] == r_b8_on
    ok &= cond_v
    print("SELF-TEST", "ok " if cond_v else "BAD", f"measured_dispatch_verdict labels the condition (CM136-L-1): knob default {v_b8[0]}, no covergroup {v_cg[0]}, worktree build {v_wt[0]}, good build {v_ok[0]}")
    facts = canary_build_facts(gd)
    cond_f = facts is not None and C.B8_PROBE_KNOB_DEFAULT_KEY in facts and C.B8_PROBE_SV_DEFAULT_KEY in facts and facts[C.COVERGROUPS_DECLARED_KEY] is True
    ok &= cond_f
    print("SELF-TEST", "ok " if cond_f else "BAD", f"canary_build_facts records the two B8 probe facts beside covergroups_declared (CM140-L-3): {[k for k in facts if k.startswith('b8_')] if facts else None}")
    rate, row = C.PLUSARG_KNOB_ICACHE_ECC_ERR_RATE, C.PLUSARG_CHK_ALERT_MINOR
    drate, bits = C.PLUSARG_KNOB_ICACHE_DATA_ECC_ERR_RATE, C.PLUSARG_KNOB_ICACHE_ECC_BITS
    for pas, defaults, want_refuse, label in (
            ([f"+{rate}=rare", f"+{row}=0"], None, True, "rate rare with the alert_minor row off refuses"),
            ([f"+{rate}=frequent"], None, False, "rate frequent with the row at its table default (1) runs"),
            ([f"+{rate}=rare", f"+{row}=1"], None, False, "rate rare with the row explicitly on runs"),
            ([f"+{rate}=none", f"+{row}=0"], None, False, "rate none with the row off runs (not triggered)"),
            ([f"+{row}=0"], None, False, "no rate plusarg (table default none) with the row off runs"),
            ([f"+{rate}=frequent"], {row: 0}, True, "a table default of 0 for the row (fabricated) refuses an entry that leaves it unmentioned"),
            ([f"+{row}=0"], {rate: "frequent"}, True, "a table default of frequent (fabricated) triggers the condition"),
            ([f"+{rate}=frequent", f"+{C.PLUSARG_CHK_ALL}=0"], None, True, "the master enable off with the row unmentioned refuses (the TB reads the row as off: chk_all ? val : (set && val); CM152-M-1)"),
            ([f"+{rate}=frequent", f"+{C.PLUSARG_CHK_ALL}=0", f"+{row}=1"], None, False, "the master enable off with the row set on runs (isolation mode, the explicit row wins)"),
            ([f"+{rate}=frequent", f"+{C.PLUSARG_CHK_ALL}=1", f"+{row}=0"], None, True, "the master enable on with the row set off refuses"),
            ([f"+{rate}=frequent"], {C.PLUSARG_CHK_ALL: 0}, True, "a table default of 0 for the master enable (fabricated) with the row unmentioned refuses"),
            ([f"+{rate}=frequent", f"+{C.PLUSARG_CHK_ALL}=0", f"+{row}"], None, True, "a bare +row with the master enable off refuses: the SV parses =%d only, so the bare form leaves the row unset (CM155-L-1)"),
            ([f"+{rate}=frequent", f"+{C.PLUSARG_CHK_ALL}=00"], None, True, "+gen_chk_all=00 reads 0 as the SV's %d does, master off, row unmentioned refuses (CM155-L-2)"),
            ([f"+{rate}=frequent", f"+{row}=00"], None, True, "+row=00 reads 0 as the SV's %d does, the row set off refuses (CM155-L-2)"),
            ([f"+{rate}=frequent", f"+{C.PLUSARG_CHK_ALL}=x"], None, True, "+gen_chk_all=x: VCS matches the name= prefix and converts the non-decimal remainder to 0, master off, row unmentioned refuses (CM159-M-1, flipping the CM155 fifth case)"),
            ([f"+{rate}=frequent", f"+{C.PLUSARG_CHK_ALL}=0", f"+{row}=off"], None, True, "+row=off under the master enable off: set with value 0 in the sim, refuses (CM159-M-1)"),
            ([f"+{rate}=frequent", f"+{C.PLUSARG_CHK_ALL}=0", f"+{row}=yes"], None, True, "+row=yes: set with value 0, refuses (CM159-M-1; the CM155-L-2 case relabelled, CM162-I-1)"),
            ([f"+{rate}=frequent", f"+{row}=false"], None, True, "+row=false with the master enable on: set with value 0, refuses (CM159-M-1)"),
            ([f"+{rate}=frequent", f"+{row}="], None, True, "+row= (empty): set with value 0, refuses (CM159-M-1; the old lambda refused it too)"),
            ([f"+{rate}=frequent", f"+{row}=0x1"], None, True, "+row=0x1: the remainder is not a decimal integer, value 0, refuses (CM159-M-1)"),
            ([f"+{rate}=frequent", f"+{row}=1abc"], None, True, "+row=1abc: not a decimal integer, value 0, refuses (CM159-M-1)"),
            ([f"+{rate}=frequent", f"+{C.PLUSARG_CHK_ALL}=false"], None, True, "+gen_chk_all=false: master off, row unmentioned refuses (CM159-M-1)"),
            ([f"+{rate}=frequent", f"+{row}=4294967296"], None, True, "+row=4294967296 wraps to 0 in the sim's 32-bit u, refuses (CM159-L-1)"),
            ([f"+{rate}=frequent", f"+{row}=-1"], None, False, "+row=-1 is non-zero in 32 bits, runs (CM159-L-1)"),
            ([f"+{rate}=frequent", f"+{C.PLUSARG_CHK_ALL}=0", f"+{row}", f"+{row}=1"], None, False, "a bare +row before +row=1: VCS skips the bare form (no name= match) and takes the = form, runs (CM159-L-2)"),
            ([f"+{rate}=frequent", f"+{row}=0", f"+{row}=1"], None, True, "+row=0 before +row=1: VCS takes the first = form, refuses (CM159-L-2)"),
            ([f"+{rate}=frequent", f"+{row}= 1"], None, True, "+row= 1 (embedded space): VCS converts no whitespace, set with value 0, refuses (CM162-L-1)"),
            ([f"+{rate}=frequent", f"+{row}=1 "], None, True, "+row=1 followed by a space: set with value 0, refuses (CM162-L-1)"),
            ([f"+{rate}=frequent", f"+{C.PLUSARG_CHK_ALL}= 1"], None, True, "+gen_chk_all= 1: the master enable reads set with value 0, row unmentioned refuses (CM162-L-1)"),
            ([f"+{rate}=frequent", f"+{row}=1_000"], None, False, "+row=1_000: VCS accepts the underscore digit separator, value 1000, runs (CM162-L-2)"),
            ([f"+{rate}=frequent", f"+{row}=_1"], None, False, "+row=_1: a leading separator, value 1, runs (CM162-L-2)"),
            ([f"+{rate}=frequent", f"+{row}=1__0"], None, False, "+row=1__0: value 10, runs (CM162-L-2)"),
            ([f"+{rate}=frequent", f"+{row}=-_1"], None, False, "+row=-_1: sign then separator, 0xFFFFFFFF in 32 bits, runs (CM162-L-2)"),
            ([f"+{rate}=frequent", f"+{row}=0_0"], None, True, "+row=0_0: value 0, refuses (CM162-L-2)"),
            ([f"+{rate}=frequent", f"+{row}=1_abc"], None, True, "+row=1_abc: letters after the separator are no decimal integer, value 0, refuses (CM162-L-2)"),
            ([f"+{rate}=frequent", f"+{row}=_"], None, True, "+row=_: a separator with no digit reads 0, refuses (CM162-L-2)"),
            ([f"+{rate}=frequent", f"+{row}=1\n"], None, True, "+row=1 with a trailing newline: VCS converts no whitespace, set with value 0, refuses (CM167-L-1)"),
            ([f"+{rate}=frequent", f"+{row}=1\r"], None, True, "+row=1 with a trailing carriage return: set with value 0, refuses (CM167-L-1)"),
            ([f"+{rate}=frequent", f"+{row}=1\r\n"], None, True, "+row=1 with CR LF: set with value 0, refuses (CM167-L-1)"),
            ([f"+{rate}=frequent", f"+{row}=\n1"], None, True, "+row= with a newline before the digit: VCS matches the name= prefix and reads 0, refuses (CM167-L-1, the plusarg_name hole)"),
            ([f"+{rate}=frequent", f"+{row}=_-1"], None, True, "+row=_-1: a separator before the sign reads 0 in VCS, refuses (CM167-I-1)"),
            ([f"+{rate}=frequent", f"+{row}=+-1"], None, True, "+row=+-1: a doubled sign reads 0, refuses (CM167-I-1)"),
            ([f"+{rate}=frequent", f"+{row}=--1"], None, True, "+row=--1: a doubled sign reads 0, refuses (CM167-I-1)"),
            ([f"+{rate}=frequent", f"+{row}=-"], None, True, "+row=-: a bare sign reads 0, refuses (CM167-I-1)"),
            ([f"+{rate}=frequent", f"+{row}=+"], None, True, "+row=+: a bare sign reads 0, refuses (CM167-I-1)"),
            ([f"+{rate}=frequent", f"+{row}=1-"], None, True, "+row=1-: a trailing sign reads 0, refuses (CM167-I-1)"),
            ([f"+{drate}=rare", f"+{row}=0"], None, True, "data-RAM rate rare with the alert_minor row off refuses (v3y extends the Q-018 conditions from the tag knob to the data knob)"),
            ([f"+{drate}=frequent"], None, False, "data-RAM rate frequent with the row at its table default (1) runs"),
            ([f"+{drate}=rare", f"+{row}=1"], None, False, "data-RAM rate rare with the row explicitly on runs"),
            ([f"+{drate}=none", f"+{row}=0"], None, False, "data-RAM rate none with the row off runs (not triggered)"),
            ([f"+{drate}=frequent", f"+{C.PLUSARG_CHK_ALL}=0"], None, True, "data-RAM rate frequent with the master enable off and the row unmentioned refuses"),
            ([f"+{rate}=none", f"+{drate}=rare", f"+{row}=0"], None, True, "tag rate none but data rate rare with the row off refuses: the data row triggers on its own"),
            ([f"+{bits}=two", f"+{row}=0"], None, False, "the bit count at two with both rates at their default none and the row off runs: the bit count injects nothing by itself, so the plan gives it no condition")):
        got = measured_knob_condition_refusal(pas, defaults)
        cond = (got is not None and "LOG-077" in got) if want_refuse else got is None
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"measured_knob_condition_refusal (LOG-077) {label}: {(got or 'None')[:80]}")
    cond = knob_default_by_plusarg(rate) == "none" and knob_default_by_plusarg(row) == 1 and knob_default_by_plusarg("gen_no_such_plusarg") is None
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"knob_default_by_plusarg from the rendered table: rate none, row 1, unknown None")
    svd = Path(tempfile.mkdtemp(prefix="gen_b8sv_selftest_", dir=C.selftest_tmp()))
    (svd / "on.sv").write_text("module p;\n  bit en = 1'b1;\nendmodule\n"); (svd / "off.sv").write_text("module p;\n  bit en = 1'b0;\nendmodule\n"); (svd / "none.sv").write_text("module p; endmodule\n")
    got_sv = (b8_probe_sv_default_on(svd / "on.sv"), b8_probe_sv_default_on(svd / "off.sv"), b8_probe_sv_default_on(svd / "none.sv"), b8_probe_sv_default_on(svd / "missing.sv"), b8_probe_sv_default_on())
    cond_sv = got_sv == (True, False, None, None, False)
    ok &= cond_sv
    print("SELF-TEST", "ok " if cond_sv else "BAD", f"b8_probe_sv_default_on (CM136-L-2): fabricated on/off/no-default/missing -> {got_sv[:4]}; the tree's gen_b8_probe.sv -> {got_sv[4]}")
    remove_selftest_tree(svd)
    ok &= cond_b8
    print("SELF-TEST", "ok " if cond_b8 else "BAD", f"measured_dispatch_refusal (LOG-067): a canary build whose knob table defaults the B8 probe knob on refuses naming the knob and the ruling; an absent fact refuses: {(r_b8_on or '')[:90]}")
    cond = (r_true is None
            and r_false is not None and "gen_tb" in r_false and f"{C.COVERGROUPS_DECLARED_KEY}=False" in r_false and "LOG-046a" in r_false
            and r_absent is not None and f"{C.COVERGROUPS_DECLARED_KEY}=absent" in r_absent
            and r_worktree is not None and "worktree-mode build" in r_worktree
            and r_other is not None and "not of the pinned" in r_other and pin[:12] in r_other
            and r_nopin is not None and "no pinned commit" in r_nopin
            and r_none is not None and "no build manifest" in r_none)
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"measured_dispatch_refusal: a head build of the pin with a covergroup passes; false or absent fact, a worktree build, a head build of another sha, no pin, no manifest refuse naming the condition: {(r_worktree or '')[:100]}")
    facts = canary_build_facts(gd)
    cond = facts is not None and facts["head_sha"] == pin and facts["source_mode"] == C.SOURCE_MODE_HEAD and facts[C.COVERGROUPS_DECLARED_KEY] is True \
        and facts["manifest_present"] and facts["manifest"] == str(gd / C.BUILD_MANIFEST) and canary_build_facts(None) is None
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", "canary_build_facts records path, manifest, source_mode, head_sha and the covergroup facts (None without a canary build)")
    remove_selftest_tree(gd)
    # The guard's own case derives its roots from the directory it created, so it holds under any GEN_DV_SELFTEST_TMP.
    rg = Path(tempfile.mkdtemp(prefix="gen_rm_selftest_", dir=C.selftest_tmp()))
    (rg / "a").mkdir(); (rg / "a" / "f.txt").write_text("x", encoding="utf-8"); (rg / "empty").mkdir(); (rg / "outside").mkdir()
    n_full = remove_tree_guarded(rg / "a", (rg.parent,), "self-test dir")
    n_empty = remove_tree_guarded(rg / "empty", (C.OUT_DIR, rg.parent), "self-test dir")
    refused = []
    for target, roots in ((rg / "outside", (C.REPO_ROOT / "ci",)), (rg, (rg,)), (rg / "missing", (rg.parent,)), (C.REPO_ROOT / "ci" / "env.sh", (C.REPO_ROOT,))):
        try:
            remove_tree_guarded(target, roots, "self-test dir"); refused.append(False)
        except SystemExit:
            refused.append(True)
    cond = n_full == 1 and not (rg / "a").exists() and n_empty == 0 and not (rg / "empty").exists() and refused == [True] * 4 \
        and (rg / "outside").is_dir() and (C.REPO_ROOT / "ci" / "env.sh").is_file()
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"remove_tree_guarded (A-002): removes a listed directory under its own root and logs its entry count (1, then an empty one); refuses a path outside the given roots, a root itself, a missing path and a file: {refused}")
    remove_selftest_tree(rg)
    # Build-input gate (dv/auto_dv/docs/gen_build_input_gate_rule.md): red cases 1-11 on fabricated name lists, 13 on the list.
    gate_cases = (
        (["dv/auto_dv/docs/gen_intervention_log.md"], [], ["dv/auto_dv/docs/gen_intervention_log.md"], "1 intervention log alone accepts"),
        (["dv/auto_dv/tools/gen_covergroup_set.py"], [], ["dv/auto_dv/tools/gen_covergroup_set.py"], "2 hand-run tool alone accepts"),
        (["dv/auto_dv/docs/gen_test_plan.md"], ["dv/auto_dv/docs/gen_test_plan.md"], [], "3 test plan refuses"),
        (["dv/auto_dv/flow/gen_testlist.yaml"], ["dv/auto_dv/flow/gen_testlist.yaml"], [], "4 testlist refuses"),
        (["rtl/ibex_core.sv"], ["rtl/ibex_core.sv"], [], "5 rtl refuses"),
        (["dv/auto_dv/docs/gen_some_new_doc.md"], ["dv/auto_dv/docs/gen_some_new_doc.md"], [], "6 unknown docs file refuses (default INPUT)"),
        (["dv/auto_dv/docs/gen_critic_flow_x.md", "dv/auto_dv/tools/gen_round_credit.py"], [],
         ["dv/auto_dv/docs/gen_critic_flow_x.md", "dv/auto_dv/tools/gen_round_credit.py"], "7 critic doc + credit tool accept"),
        (["dv/auto_dv/docs/gen_intervention_log.md", "dv/auto_dv/docs/gen_test_plan.md"], ["dv/auto_dv/docs/gen_test_plan.md"],
         ["dv/auto_dv/docs/gen_intervention_log.md"], "8 mixed list refuses on the plan, lets the log through"),
        (["dv/auto_dv/tools/gen_trace_check.py"], ["dv/auto_dv/tools/gen_trace_check.py"], [], "9 segmentable rule source refuses"),
        (["dv/auto_dv/tools/gen_plan_marker.py"], ["dv/auto_dv/tools/gen_plan_marker.py"], [], "10 marker token refuses"),
        (["dv/auto_dv/toolsx/y.py"], ["dv/auto_dv/toolsx/y.py"], [], "11a prefix boundary: toolsx refuses"),
        (["dv/auto_dv/docs/sub/gen_critic_x.md"], ["dv/auto_dv/docs/sub/gen_critic_x.md"], [], "11b glob matches directly under docs only"),
        (["dv/auto_dv/docs/gen_component_api_fcov.md"], [], ["dv/auto_dv/docs/gen_component_api_fcov.md"], "11c component doc accepts"),
        (["dv/auto_dv/docs/gen_critic_sub/x.md"], ["dv/auto_dv/docs/gen_critic_sub/x.md"], [], "11d a subdirectory named like the glob refuses"),
    )
    for names, want_in, want_non, label in gate_cases:
        got = classify_delta(names)
        cond = got == (want_in, want_non)
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD", f"build-input gate case {label}: {got}")
    problems = noninput_list_check()
    cond = problems == [] and len(noninput_list_sha256()) == 64
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", f"build-input gate case 13: every listed non-input is tracked and each glob class matches a tracked file ({problems}); list sha256 {noninput_list_sha256()[:12]}")
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 2


# --- Testlist -------------------------------------------------------------------------------
def red_expect_error(rx: Any) -> str | None:
    """Why a red_expect value is unusable (None when fine): one rule for the loader and the verdict CLI."""
    if not isinstance(rx, str) or not rx:
        return "red_expect must be a non-empty regex"
    try:
        compiled = re.compile(rx)
    except re.error as e:
        return f"red_expect {rx!r} is not a valid regex ({e})"
    if compiled.search(""):
        return f"red_expect {rx!r} matches the empty string and would accept any FAIL without a collected line"
    return None


def clone_relative_file(rel: Any) -> Path | None:
    """The clone file a clone-relative path names, or None when the path is absolute, escapes the clone
    (.. or a symlink) or names no regular file."""
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        return None
    p = (C.SOURCE_ROOT / rel).resolve()
    root = C.SOURCE_ROOT.resolve()
    return p if p.is_file() and (p == root or root in p.parents) else None


def require_under_source_root(mod: Any, name: str) -> None:
    """A module imported by dotted name from the source root must live there: a leaked PYTHONPATH must not supply
    a dv/ package the source tree lacks."""
    f = getattr(mod, "__file__", None)
    root = C.SOURCE_ROOT.resolve()
    if not f or root not in Path(f).resolve().parents:
        die(f"{name} was imported from {f!r}, not from the source root {root}")


def knobs_module() -> Any:
    """TB Infra's rendered knob table imported from the source root (and verified to live there)."""
    import importlib
    if str(C.SOURCE_ROOT) not in sys.path:
        sys.path.insert(0, str(C.SOURCE_ROOT))
    try:
        knobs = importlib.import_module(C.KNOBS_MODULE)
    except ModuleNotFoundError as e:
        die(f"{C.KNOBS_MODULE} is not importable ({e}); the rendered knob table is the origin of knobs and export events")
    require_under_source_root(knobs, C.KNOBS_MODULE)
    return knobs


def export_facts() -> dict[str, Any]:
    """What a build of this source tree can export, copied row for row from the rendered table (plan sunset
    trigger C-3): export_sources = [{source, event, fields}] (one exact event per row, no wildcards) and
    export_knobs = {plusarg: compiled default} for the gen_export_* knobs."""
    k = knobs_module()
    rows = [{"source": str(r[0]), "event": str(r[1]), "fields": [str(f) for f in (r[2] if len(r) > 2 else [])]}
            for r in getattr(k, "EXPORT_EVENTS", ())]
    bad = [r for r in rows if "*" in r["source"] or "*" in r["event"]]
    if bad:
        die(f"rendered EXPORT_EVENTS still carries wildcard rows {bad}; the exact table is required")
    # PLUSARGS is keyed by knob name; the plusarg string sits in each row.
    knobs = {p["plusarg"]: p.get("default") for p in getattr(k, "PLUSARGS", {}).values()
             if isinstance(p, dict) and str(p.get("plusarg", "")).startswith("gen_export")}
    # Declared rows (ruling 2026-09-03): the rows whose writer the codegen says is instanced (EXPORT_ACTIVE_SOURCES);
    # until TB Infra renders that list it is EMPTY, never the rendered table. The EMITTED set is not declared at all:
    # it is observed after the runs from the export files' headers (LOG-028a, export_observe), so a fresh build
    # carries an empty emitted set with the unobserved origin.
    active = getattr(k, "EXPORT_ACTIVE_SOURCES", None)
    if active is None:
        declared, origin = [], "no rendered active-source list yet (EXPORT_ACTIVE_SOURCES absent): empty by ruling"
    else:
        active_set = {str(a) for a in active}
        declared, origin = [r for r in rows if r["source"] in active_set], "rows of EXPORT_EVENTS whose source is in EXPORT_ACTIVE_SOURCES"
    return {"export_sources": rows, "export_source_names": sorted({r["source"] for r in rows}),
            "export_sources_declared": declared, "export_sources_declared_origin": origin,
            "export_sources_emitted": [], "export_sources_emitted_origin": C.EXPORT_EMITTED_UNOBSERVED, "export_rows_observed": [],
            "export_knobs": knobs, "export_record_fields": list(getattr(k, "EXPORT_RECORD_FIELDS", ()))}


def red_group(test_name: str) -> str:
    """The retained-log group of a red fixture: the test name without its test prefix and the red suffix."""
    group = test_name
    for pre in C.RED_TEST_PREFIXES:
        if group.startswith(pre):
            group = group[len(pre):]
            break
    return group[: -len(C.RED_TEST_SUFFIX)] if group.endswith(C.RED_TEST_SUFFIX) else group


def red_log_for(test_name: str) -> tuple[Path | None, Path | None, str | None]:
    """The retained pinned-red stdout log of a red fixture under the source root (its sim.log sibling when present, and
    the family's harness-line prefix, None for a family whose designed failure is a collected UVM error), by the first
    RED_LOG_FAMILIES entry that holds one; (None, None, None) when no family does."""
    group = red_group(test_name)
    for dir_rel, patterns, sim_pat, harness in C.RED_LOG_FAMILIES:
        d = C.SOURCE_ROOT.joinpath(*dir_rel)
        if not d.is_dir():
            continue
        for pat in patterns:
            p = d / pat.format(group=group)
            if p.is_file():
                sim = d / sim_pat.format(group=group) if sim_pat else None
                return p, (sim if sim is not None and sim.is_file() else None), harness
    return None, None, None


def red_signature_check(test: dict[str, Any]) -> dict[str, Any] | None:
    """The reviewer's method: the retained pinned-red log of a red fixture, run through the verdict with the entry's
    red_expect, must come out RED-OK. None when no retained log exists (head trees carry no evidence; a fixture
    without a retained log is not provable here). For a family without a harness line the match IS the RED-OK
    verdict, so such an entry is never stale and RED_STALE_ALLOWLIST cannot apply to it."""
    import gen_verdict as V
    stdout, sim, harness_prefix = red_log_for(test["name"])
    if stdout is None:
        return None
    sim_lines = sim.read_text(encoding="utf-8", errors="replace").splitlines() if sim else []
    lines = sim_lines + stdout.read_text(encoding="utf-8", errors="replace").splitlines()
    res = V.decide_lines(lines, test.get("pass_marker"), False, 1, C.BUILD_CONFIG, [], True, False,
                         banner_lines=sim_lines or None, red_fixture=True, red_expect=test.get("red_expect"))
    # Two checks: the designed-failure line of the retained log must match the regex, and the log must come out RED-OK
    # through the verdict (the literal criterion, T-153). A log whose verdict is not RED-OK is refused unless the entry
    # is on RED_STALE_ALLOWLIST (a live comparator row ahead of the harness line). A family without a harness line
    # (a fixture failing through a collected UVM error) has the verdict's own evidence line as its designed failure,
    # which RED-OK already requires to match red_expect.
    rx = test.get("red_expect") or ""
    if harness_prefix:
        harness = next((l.strip() for l in lines if harness_prefix in l), None)
        match = bool(harness and re.search(rx, harness))
        mismatch_text = "red_expect does not match the retained log's harness line"
    else:
        harness = str(res.get("evidence") or "").strip() or None
        match = res["verdict"] == C.VERDICT_RED_OK
        mismatch_text = "the retained log's collected evidence line does not come out RED-OK with this red_expect"
    stale = bool(match and res["verdict"] != C.VERDICT_RED_OK)
    allow = C.RED_STALE_ALLOWLIST.get(test["name"])
    if not match:
        refuse = (f"no {harness_prefix or 'collected evidence'} line in the retained pinned-red log" if not harness
                  else mismatch_text)
    elif stale and allow is None:
        refuse = C.RED_STALE_REFUSE
    else:
        refuse = None
    return {"log": str(stdout), "sim_log": str(sim) if sim else None, "verdict": res["verdict"], "reason": res["reason"],
            "evidence": str(res.get("evidence") or "")[:200], "harness_line": (harness or "")[:200], "harness_match": match,
            "refuse": refuse, "stale_evidence": stale,
            "stale_cause": C.RED_STALE_TEXT.format(task=allow[0]) if (stale and allow is not None) else None}


def red_check_line(name: str, chk: dict[str, Any]) -> str:
    """One --check-red-signatures line: the tag (ok / STALE / FAIL), the log, the harness match, the verdict, then the
    refusal text or the stale cause (a refused entry never carries a stale suffix)."""
    ok_ = chk["refuse"] is None
    tag = "ok  " if ok_ and not chk["stale_evidence"] else ("STALE" if ok_ else "FAIL")
    line = f"RED-CHECK {tag} {name}: {Path(chk['log']).name}; harness match={chk['harness_match']}; verdict {chk['verdict']}"
    if chk["refuse"]:
        line += f"; {chk['refuse']}"
    elif chk["stale_cause"]:
        line += f"; {chk['stale_cause']} (the verdict's first collected line is not the harness line)"
    return line


def red_check_summary(refused: dict[str, int], causes: dict[str, int]) -> tuple[str, int]:
    """The --check-red-signatures summary and exit code: refusals (by kind) -> RED_CHECK_EXIT_REFUSE, only allowlisted
    stale logs (by task) -> RED_CHECK_EXIT_STALE, else PASS and 0."""
    bad, stale = sum(refused.values()), sum(causes.values())
    if bad:
        return f"FAIL ({bad} red entry(ies) refused: " + "; ".join(f"{n} {k}" for k, n in sorted(refused.items())) + ")", C.RED_CHECK_EXIT_REFUSE
    if stale:
        return (f"PASS ({stale} stale retained log(s), the literal verdict criterion is not met yet: "
                + "; ".join(f"{n} {c}" for c, n in sorted(causes.items())) + ")"), C.RED_CHECK_EXIT_STALE
    return "PASS", 0


def slow_total(logs: list[Path]) -> dict[str, int] | None:
    """The harness's GEN_TEST_SLOW_TOTAL line of a run (rounds, budget_cycles) from the first log that carries it; None
    when no log does (a template without the line, or a run that never reached its end)."""
    rx = re.compile(C.SLOW_TOTAL_RE)
    for p in logs:
        if not Path(p).is_file():
            continue
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = rx.search(line)
                if m:
                    return {"rounds": int(m.group(1)), "budget_cycles": int(m.group(2))}
    return None


def export_observe(files: list[tuple[str, Path]]) -> dict[str, Any]:
    """What the sink actually wrote (LOG-028a) over the export files of one build, in the order given: the union of
    the headers' sources= sets, and the per-row first-seen list (row "<source> <event>" of an E line, the run that
    first showed it, that first line). Files without a gen_export header are skipped and not counted."""
    sources: set[str] = set()
    rows: dict[str, dict[str, Any]] = {}
    used = 0
    for run_id, path in files:
        header = export_header_sources(Path(path))
        if header is None:
            continue
        used += 1
        sources.update(header)
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if not line.startswith(C.EXPORT_EVENT_LINE_PREFIX):
                    continue
                tok = line.split()
                if len(tok) < 4:
                    continue
                key = f"{tok[2]} {tok[3]}"
                if key not in rows:
                    rows[key] = {"row": key, "first_run": run_id, "first_line": line.rstrip()[:C.EXPORT_FIRST_LINE_MAX]}
    return {"sources": sorted(sources), "files": used, "rows": [rows[k] for k in sorted(rows)]}


def emitted_from_observed(rendered_rows: list[dict[str, Any]], sources: list[str]) -> list[dict[str, Any]]:
    """The rendered rows whose source the sink's headers actually named."""
    s = set(sources or [])
    return [r for r in rendered_rows or [] if r["source"] in s]


def export_header_sources(path: Path) -> list[str] | None:
    """The sources= list of an export file's first header line (`# gen_export v1 ... sources=a,b ...`): the
    run-time truth of which writers emitted; None when the file or the header is absent."""
    if not path.is_file():
        return None
    with open(path, encoding="utf-8", errors="replace") as fh:
        first = fh.readline()
    m = re.search(r"\bsources=(\S*)", first)
    if not first.startswith("# gen_export") or not m:
        return None
    return [t for t in m.group(1).split(",") if t]


def emitted_check(emitted_rows: list[dict[str, Any]], header_sources: list[str], subset_ok: bool = False) -> str | None:
    """The header's sources= set must equal the manifest's emitted set; with the sources knob narrowed (subset_ok)
    the header may be a subset, never a source the build cannot emit. The message names the difference."""
    manifest = {r["source"] for r in emitted_rows or []}
    header = set(header_sources or [])
    if manifest == header or (subset_ok and header <= manifest):
        return None
    return (f"export sources emitted mismatch: manifest {sorted(manifest)} vs export header sources= {sorted(header)}"
            f" (only in manifest {sorted(manifest - header)}, only in header {sorted(header - manifest)})")


def witness_index() -> dict[str, int]:
    """tp_item -> index from the witness CSV at the source root (the CSV's own index column, the value the
    bridge command COV_WITNESS carries); a missing file or column stops the flow."""
    import csv
    if not C.WITNESS_CSV.is_file():
        die(f"{C.WITNESS_CSV}: missing (the witness id table)")
    with open(C.WITNESS_CSV, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows or "index" not in rows[0] or "tp_item" not in rows[0]:
        die(f"{C.WITNESS_CSV}: needs the columns index and tp_item")
    out: dict[str, int] = {}
    for r in rows:
        key = r["tp_item"].strip()
        if key in out:
            die(f"{C.WITNESS_CSV}: tp_item {key} is listed twice (indices {out[key]} and {r['index']})")
        try:
            out[key] = int(r["index"])
        except ValueError:
            die(f"{C.WITNESS_CSV}: row {r!r} has a non-integer index")
    return out


def witness_plusarg_name() -> str | None:
    """The +gen_witness_ids plusarg string as the SV constants home declares it (None until TB Infra lands it)."""
    return {ident: name for name, ident in C.sv_plusarg_names().items()}.get(C.SV_PLUSARG_WITNESS_IDS)


def witness_tables() -> tuple[dict[str, int], dict[str, str], dict[str, int]]:
    """WITNESS_IDS, WITNESS_GROUP_OF and WITNESS_GROUPS from TB Infra's rendered knob table: the tables the bridge's
    cov_witness call and the covergroup use (COV_WITNESS arg0 = WITNESS_IDS[tp], arg1 = WITNESS_GROUPS[owner group])."""
    import importlib
    if str(C.SOURCE_ROOT) not in sys.path:
        sys.path.insert(0, str(C.SOURCE_ROOT))
    try:
        knobs = importlib.import_module(C.KNOBS_MODULE)
    except ModuleNotFoundError as e:
        die(f"{C.KNOBS_MODULE} is not importable ({e}); the rendered witness tables live there")
    require_under_source_root(knobs, C.KNOBS_MODULE)
    for attr in ("WITNESS_IDS", "WITNESS_GROUP_OF", "WITNESS_GROUPS"):
        if not isinstance(getattr(knobs, attr, None), dict):
            die(f"{C.KNOBS_MODULE} renders no {attr} table (witness protocol not landed)")
    return knobs.WITNESS_IDS, knobs.WITNESS_GROUP_OF, knobs.WITNESS_GROUPS


def witness_render(test: dict[str, Any]) -> dict[str, Any] | None:
    """The witness record of a test entry, as the TB built the protocol (T-226): the TP ids, their indices (the CSV's
    index column, equal to the rendered WITNESS_IDS), the one owner group they share and its WITNESS_GROUPS index,
    which the test's epilogue sends as COV_WITNESS <index> <group>. The TB declares no witness plusarg (the epilogue
    reads the entry itself), so `plusarg` is None unless the SV constants home names one. None when the entry lists
    no witness_ids; an id absent from the CSV or the rendered table, a CSV/table index disagreement, or ids of several
    owner groups (the dispatcher refuses another group's item, GEN_WITNESS_FOREIGN) stop the flow."""
    ids = test.get("witness_ids")
    if not ids:
        return None
    table = witness_index()
    missing = [i for i in ids if i not in table]
    if missing:
        die(f"test {test['name']}: witness_ids {missing} are not in {C.WITNESS_CSV.name}")
    w_ids, w_group_of, w_groups = witness_tables()
    unknown = [i for i in ids if i not in w_ids or i not in w_group_of]
    if unknown:
        die(f"test {test['name']}: witness_ids {unknown} are not in the rendered WITNESS_IDS / WITNESS_GROUP_OF tables of {C.KNOBS_MODULE}")
    disagree = [i for i in ids if w_ids[i] != table[i]]
    if disagree:
        die(f"test {test['name']}: witness index of {disagree} differs between {C.WITNESS_CSV.name} and the rendered WITNESS_IDS (re-render the knob table)")
    groups = sorted({w_group_of[i] for i in ids})
    if len(groups) != 1:
        die(f"test {test['name']}: witness_ids span the owner groups {groups}; an entry witnesses items of its own group only "
            f"(the dispatcher refuses another group's item)")
    group = groups[0]
    if group not in w_groups:
        die(f"test {test['name']}: owner group {group} has no WITNESS_GROUPS index")
    indices = [table[i] for i in ids]
    name = witness_plusarg_name()
    return {"tp_ids": list(ids), "indices": indices, "owner_group": group, "group_index": w_groups[group],
            "csv": str(C.WITNESS_CSV), "csv_sha256": sha256_file(C.WITNESS_CSV),
            "protocol": "COV_WITNESS <index> <group index>, issued by the test's epilogue through the bridge",
            "plusarg": (f"+{name}=" + ",".join(str(i) for i in indices)) if name else None}


def debug_only_from_knobs() -> set[str]:
    """Plusarg names marked debug_only in TB Infra's rendered knob table (gen_knobs.PLUSARGS): the one
    origin of the property and of the names themselves, so no naming rule is re-encoded here."""
    import importlib
    if str(C.SOURCE_ROOT) not in sys.path:
        sys.path.insert(0, str(C.SOURCE_ROOT))
    try:
        knobs = importlib.import_module(C.KNOBS_MODULE)
    except ModuleNotFoundError as e:
        die(f"{C.KNOBS_MODULE} is not importable ({e}); the rendered knob table is the debug_only origin")
    require_under_source_root(knobs, C.KNOBS_MODULE)
    return {p["plusarg"] for p in knobs.PLUSARGS.values() if p.get("debug_only")}


def knob_default_by_plusarg(plusarg: str):
    """The rendered knob table's default of the knob whose plusarg is `plusarg`, None when no knob carries it (read from the
    source tree the process binds to, as the other knob-table readers do)."""
    import importlib
    if str(C.SOURCE_ROOT) not in sys.path:
        sys.path.insert(0, str(C.SOURCE_ROOT))
    try:
        knobs = importlib.import_module(C.KNOBS_MODULE)
    except ModuleNotFoundError as e:
        die(f"{C.KNOBS_MODULE} is not importable ({e}); the rendered knob table is the origin of knob defaults")
    require_under_source_root(knobs, C.KNOBS_MODULE)
    for entry in knobs.PLUSARGS.values():
        if entry.get("plusarg") == plusarg:
            return entry.get("default")
    return None


def effective_knob_value(plusargs: list[str], plusarg: str, defaults: dict[str, Any] | None = None) -> str | None:
    """The value a run gives `plusarg`: the plusarg's value (a bare +name counts as 1), else the knob table's default
    (`defaults` overrides the table for self-tests), as a string; None when neither names it."""
    for pa in plusargs:
        if plusarg_name(pa) == plusarg:
            return pa.split("=", 1)[1].strip() if "=" in pa else "1"
    d = defaults[plusarg] if defaults and plusarg in defaults else knob_default_by_plusarg(plusarg)
    return None if d is None else str(d)


PLUSARG_DECIMAL_RE = re.compile(r"[+-]?[0-9_]*[0-9][0-9_]*")   # the whole remainder VCS's %d converts: a leading sign, digits, _ separators; anything else (whitespace, newlines included) reads 0


def checker_knob_state(plusargs: list[str], name: str, defaults: dict[str, Any] | None = None) -> tuple[bool, bool]:
    """(set, on) of a bool checker knob as VCS's `$value$plusargs({PLUSARG, "=%d"}, u)` reads it: the first plusarg
    whose text starts with "name=" matches (a bare +name never matches, so it is skipped, not stopped at), and the match
    sets the knob; the value is the remainder as a decimal integer in the 32 bits of u (sign and underscore digit separators
    as VCS accepts them: 1_000 is 1000; the sign, if any, leads the digits), and any other remainder (yes, off, false,
    empty, 0x1, 1abc, _-1, +-1, a bare or trailing sign, or one carrying whitespace: VCS converts no whitespace, so " 1",
    "1 " and "1" followed by a newline read 0) reads 0; unset, on follows the table default."""
    for pa in plusargs:
        if plusarg_name(pa) != name or "=" not in pa:
            continue
        rest = pa.split("=", 1)[1]
        val = (int(rest.replace("_", ""), 10) & 0xFFFFFFFF) if PLUSARG_DECIMAL_RE.fullmatch(rest) else 0
        return True, val != 0
    d = defaults[name] if defaults and name in defaults else knob_default_by_plusarg(name)
    return False, str(d).strip() not in ("0", "", "None", "False")


def checker_row_on(plusargs: list[str], row: str, defaults: dict[str, Any] | None = None) -> bool:
    """Whether the TB runs checker row `row` on: gen_chk_en(cfg, val, set) = chk_all ? val : (set && val)
    (gen_checkers_pkg.sv:19), with set and val read as checker_knob_state reads them."""
    row_set, row_on = checker_knob_state(plusargs, row, defaults)
    _, master_on = checker_knob_state(plusargs, C.PLUSARG_CHK_ALL, defaults)
    return row_on if master_on else (row_set and row_on)


def measured_knob_condition_refusal(plusargs: list[str], defaults: dict[str, Any] | None = None) -> str | None:
    """The MEASURED_KNOB_CONDITIONS row a measured run with these effective plusargs violates (its rule text with the
    values seen), or None. The trigger value comes from the plusargs, else from the knob table's default; the required
    knob is a checker row and is judged as the TB judges it (checker_row_on: the master enable's precedence included)."""
    for cond in C.MEASURED_KNOB_CONDITIONS:
        trig = effective_knob_value(plusargs, cond["trigger"], defaults)
        if trig not in cond["values"]:
            continue
        if checker_row_on(plusargs, cond["requires"], defaults):
            continue
        req = effective_knob_value(plusargs, cond["requires"], defaults)
        master = effective_knob_value(plusargs, C.PLUSARG_CHK_ALL, defaults)
        return (f"+{cond['trigger']}={trig} while +{cond['requires']} reads off (row {'absent' if req is None else req}, "
                f"+{C.PLUSARG_CHK_ALL} {'absent' if master is None else master}); {cond['rule']}")
    return None


def knob_default_on(knob: str) -> bool | None:
    """The rendered knob table's default of `knob` as a truth value, None when the table has no such knob: the build
    manifest fact behind the LOG-067 measured-dispatch refusal (read from the source tree the build binds to)."""
    import importlib
    if str(C.SOURCE_ROOT) not in sys.path:
        sys.path.insert(0, str(C.SOURCE_ROOT))
    try:
        knobs = importlib.import_module(C.KNOBS_MODULE)
    except ModuleNotFoundError as e:
        die(f"{C.KNOBS_MODULE} is not importable ({e}); the rendered knob table is the origin of knob defaults")
    require_under_source_root(knobs, C.KNOBS_MODULE)
    entry = knobs.PLUSARGS.get(knob)
    if entry is None:
        return None
    return str(entry.get("default")).strip() not in ("0", "", "None", "False")


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
    for pol in data.get("red_expect_policy") or []:
        if pol not in C.RED_EXPECT_POLICIES:
            die(f"{path}: red_expect_policy names unknown policy {pol!r} (known: {C.RED_EXPECT_POLICIES})")
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
        if t.get("measured", True) and plusarg_enabled(t.get("plusargs") or [], C.PLUSARG_CHK_SVA_B8):
            die(f"{path}: test {t['name']} is measured and turns on +{C.PLUSARG_CHK_SVA_B8}; {C.B8_PROBE_RULE}")
        if t.get("measured", True):
            why = measured_knob_condition_refusal(t.get("plusargs") or [])
            if why:
                die(f"{path}: test {t['name']} is measured and carries {why}")
        fcov = t.get("fcov_expectation_file")
        if fcov is not None:
            home = C.FCOV_EXPECT_DIR.relative_to(C.SOURCE_ROOT).as_posix()
            fp = Path(str(fcov))
            if fp.parent.as_posix() != home:
                die(f"{path}: test {t['name']} fcov_expectation_file {fcov} is outside {home}/ (the schema's manifest home, the one directory the covergroup-set and manifest tools read; a check-tier entry with a proof manifest elsewhere uses null)")
            if not (C.SOURCE_ROOT / fp).is_file():
                die(f"{path}: test {t['name']} fcov_expectation_file {fcov} does not exist under the source root")
            # Every entry, measured or not: gen_fcov.check_test validates the manifest against the entry name before it
            # reads coverage, so a differing stem can only end as an unverifiable protocol error.
            if fp.name != f"{t['name']}{C.FCOV_MANIFEST_SUFFIX}":
                die(f"{path}: test {t['name']} fcov_expectation_file {fcov} must be {home}/{t['name']}{C.FCOV_MANIFEST_SUFFIX} or null (validate_manifest needs the manifest's test, the file stem and the entry name equal on every entry; a shared or group manifest fails the per-entry check as unverifiable)")
            why = manifest_test_mismatch(C.SOURCE_ROOT / fp, t["name"])
            if why:
                die(f"{path}: test {t['name']} fcov_expectation_file {fcov} {why} (the third equality: the sweep checks the manifest's test against its file stem, this checks it against the entry, so drift is caught at load rather than as an unverifiable run)")
        if t.get("red_fixture"):
            if t.get("expected_fail"):
                die(f"{path}: test {t['name']}: red_fixture and expected_fail are exclusive (a fixture is not an RTL-bug candidate)")
            if t.get("measured", True):
                die(f"{path}: test {t['name']}: a red_fixture must be measured: false (never counted as coverage)")
            err = red_expect_error(t.get("red_expect"))
            if err:
                die(f"{path}: test {t['name']}: a red_fixture must declare the evidence line of its designed failure: {err}")
            rx = t["red_expect"]
            # The harness prefix anywhere in the regex (a leading .* or an AssertionError: prefix is still the harness line).
            if C.RED_EXPECT_POLICY_FIRE_ID in (data.get("red_expect_policy") or []) and C.RED_EXPECT_HARNESS_PREFIX in rx \
                    and C.RED_EXPECT_FIRE_TOKEN not in rx:
                die(f"{path}: test {t['name']}: red_expect {rx!r} matches the {C.RED_EXPECT_HARNESS_PREFIX} harness line but names no "
                    f"{C.RED_EXPECT_FIRE_TOKEN} id (policy {C.RED_EXPECT_POLICY_FIRE_ID}: the designed fire id is on that line)")
            # The signature must match the fixture's own retained pinned-red log when one exists.
            chk = red_signature_check(t)
            if chk and chk["refuse"]:
                die(f"{path}: test {t['name']}: red_expect {rx!r} refused: {chk['refuse']} ({Path(chk['log']).name}: "
                    f"harness {chk['harness_line'][:120]!r}; verdict {chk['verdict']}: {chk['reason'][:120]})")
        elif t.get("red_expect") is not None:
            die(f"{path}: test {t['name']}: red_expect is only meaningful with red_fixture: true")
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
            forms = [k for k in C.PROGRAM_SOURCE_FORMS if prog.get(k)]
            if len(forms) != 1:
                die(f"{path}: test {t['name']} program needs exactly one of {'/'.join(C.PROGRAM_SOURCE_FORMS)}, got {forms}")
            gen = prog.get("generator")
            if gen is not None:
                if clone_relative_file(gen) is None:
                    die(f"{path}: test {t['name']} program.generator must be a clone-relative path (no .., no symlink out of the clone) to an existing script, got {gen!r}")
            gargs = prog.get("generator_args")
            if gargs is not None and (gen is None or not isinstance(gargs, list) or not all(isinstance(x, str) for x in gargs)):
                die(f"{path}: test {t['name']} program.generator_args must be a list of strings and needs program.generator")
            seed = prog.get("seed", C.PROGRAM_SEED_RUN)
            if not (seed == C.PROGRAM_SEED_RUN or isinstance(seed, int)):
                die(f"{path}: test {t['name']} program.seed must be an integer or {C.PROGRAM_SEED_RUN!r}")
        w = t.get("witness_ids")
        if w is not None:
            if not isinstance(w, list) or not w or not all(isinstance(x, str) and x for x in w):
                die(f"{path}: test {t['name']}: witness_ids must be a non-empty list of TP ids")
            witness_render(t)   # dies on an id absent from the CSV or the rendered tables, or on ids of several owner groups
        by_ident = {ident: n for n, ident in C.sv_plusarg_names().items()}
        export_name, witness_name = by_ident.get(C.SV_PLUSARG_EXPORT_FILE), by_ident.get(C.SV_PLUSARG_WITNESS_IDS)
        for pa in t["plusargs"]:
            name = plusarg_name(pa)
            if any(c in C.TESTLIST_PLUSARG_WHITESPACE for c in pa):
                die(f"{path}: test {t['name']} plusarg {pa!r}: {C.TESTLIST_PLUSARG_RULE}")
            if witness_name and name == witness_name:
                die(f"{path}: test {t['name']} plusarg {pa!r}: the witness plusarg is rendered by the flow from witness_ids, never listed by hand")
            if export_name and name == export_name:
                val = plusarg_value(pa) or ""
                if not val or Path(val).is_absolute() or ".." in Path(val).parts:
                    die(f"{path}: test {t['name']} plusarg {pa!r}: the export file must be a plain name inside the run directory")
            if name is None:
                die(f"{path}: test {t['name']} plusarg {pa!r} is not of the form +name or +name=value")
            if name not in known_plusargs and not name.startswith(C.VCS_PLUSARG_PREFIX):
                die(f"{path}: test {t['name']} plusarg {pa!r}: name {name!r} is neither a PLUSARG_* of "
                    f"{C.TB_PKG_SV.name} nor a simulator/UVM plusarg (P-06 single source)")
    declared = set(data.get("debug_only_plusargs") or [])
    from_knobs = debug_only_from_knobs()
    if declared != from_knobs:
        die(f"{path}: debug_only_plusargs {sorted(declared)} disagrees with the knobs marked debug_only in "
            f"{C.KNOBS_MODULE} {sorted(from_knobs)}; the rendered knob table is the one origin")
    return data


def nested_pairs(trees: list[str]) -> list[tuple[str, str]]:
    """(ancestor, descendant) pairs among instance paths; a.b is an ancestor of a.b.c, not of a.bc."""
    out = []
    for x in trees:
        for y in trees:
            if x != y and y.startswith(x + "."):
                out.append((x, y))
    return out


def plusarg_value(pa: str) -> str | None:
    """The value of a +name=value plusarg (None for a bare +name)."""
    return pa.split("=", 1)[1] if "=" in pa else None


def plusarg_name(pa: str) -> str | None:
    m = re.match(r"^\+([A-Za-z_][\w+]*)(=[\s\S]*)?$", pa)   # the value may span newlines: VCS matches the name= prefix whatever follows
    return m.group(1) if m else None


def plusarg_enabled(plusargs: list[str], name: str) -> bool:
    """True when +name is present with no value, or with a value that is neither 0 nor empty once stripped.

    Deliberately stricter than the VCS-faithful checker_knob_state, and used only for the forbidden-knob gates (P6 and
    B8_PROBE_RULE): once stripped, only "0" and an empty value read off, so +name, +name=00, +name=x and "+name= 1"
    all refuse an entry VCS itself would read as 0. Under-reading a forbidden knob would let a measured run through;
    over-reading only asks the author to write the 0 plainly."""
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
    if "--check-red-signatures" in sys.argv:
        # Every red fixture of a testlist against its retained pinned-red log. Exit RED_CHECK_EXIT_REFUSE when a signature
        # does not match its log's harness line or the log's own verdict is not RED-OK, RED_CHECK_EXIT_STALE when the only
        # non-RED-OK logs belong to allowlisted entries (a pending comparator row), 0 when every checked log is RED-OK.
        nxt = sys.argv[sys.argv.index("--check-red-signatures") + 1:][:1]
        tl = Path(nxt[0]) if nxt and not nxt[0].startswith("--") else C.TESTLIST_YAML   # a following flag is not a path
        data = load_yaml(tl)
        causes: dict[str, int] = {}
        refused: dict[str, int] = {}
        for t in data.get("tests", []):
            if not t.get("red_fixture"):
                continue
            chk = red_signature_check(t)
            if chk is None:
                print(f"RED-CHECK skip  {t['name']}: no retained pinned-red log")
                continue
            if chk["refuse"]:
                kind = "harness-line mismatch" if chk["refuse"] != C.RED_STALE_REFUSE else "retained log not RED-OK"
                refused[kind] = refused.get(kind, 0) + 1
            elif chk["stale_cause"]:
                causes[chk["stale_cause"]] = causes.get(chk["stale_cause"], 0) + 1
            print(red_check_line(t["name"], chk))
        verdict, code = red_check_summary(refused, causes)
        print("RED-CHECK:", verdict)
        sys.exit(code)
    if "--dump-testlist" in sys.argv:
        # Validated testlist as JSON; run with GEN_DV_SOURCE_ROOT set so the validation reads the pinned tree.
        import json
        real_stdout, sys.stdout = sys.stdout, sys.stderr   # a log line during the load must not corrupt the JSON
        data = load_testlist(Path(sys.argv[sys.argv.index("--dump-testlist") + 1]))
        sys.stdout = real_stdout
        print(json.dumps(data))
        sys.exit(0)
    sys.exit(self_test() if "--self-test" in sys.argv else 0)
