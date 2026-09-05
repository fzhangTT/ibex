#!/usr/bin/env python3
"""Compile one TB top from the filelists of a build entry (docs/dv/SIM_RECIPE.md Section 2),
optionally with the Section 3 coverage instrumentation scoped to the gen_dut_top instance, the
Section 4 cocotb triple and the Section 6 wave access, into a fresh outdir, and write a build
manifest (command, flag groups, filelist digests, git HEAD, tool versions, compile-log summary).

Usage (from a login shell with ci/env.sh sourced, or through --lsf):
    gen_build.py --build gen_smoke --coverage [--cond] [--cocotb] [--waves] [--no-diag-noconst]
                 [--outdir DIR] [--lsf] [--define NAME ...] [--vcs-arg ARG ...]
                 [--rtl-root DIR --mutation-id ID]   # mutation build from a mutated RTL copy
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import gen_flow_const as C
import gen_flow_util as U
import gen_mirror as M


def config_opts() -> list[str]:
    r = subprocess.run([sys.executable, str(C.CONFIG_SCRIPT), C.BUILD_CONFIG, "vcs_opts"],
                       capture_output=True, text=True, cwd=C.SOURCE_ROOT)
    if r.returncode != 0:
        U.die(f"ibex_config.py failed: {r.stderr.strip()}")
    return shlex.split(r.stdout.strip())


def cocotb_lib(a: argparse.Namespace) -> tuple[str, dict[str, Any] | None]:
    """VPI library the simv loads at run time. LSF hosts see only the shared mirror, so the
    default is the mirror venv (fresh mirror required); --local-cocotb takes the clone venv."""
    if a.local_cocotb:
        cc = shutil.which("cocotb-config")
        if not cc:
            U.die("cocotb-config not on PATH; the venv is not active (ci/env.sh)")
        r = subprocess.run([cc, "--lib-name-path", "vpi", "vcs"], capture_output=True, text=True)
        lib = r.stdout.strip()
        if r.returncode != 0 or not Path(lib).is_file():
            U.die(f"cocotb VPI library not found: {lib!r}")
        return lib, None
    root = M.mirror_root()
    if root is None:
        U.die("cocotb build needs the shared mirror (gen_mirror.py --sync --venv) or --local-cocotb")
    st = M.status(root, pinned_head=os.environ.get(C.ENV_HEAD_SHA))
    if st["state"] != "fresh" and not a.allow_stale_mirror:
        U.die(f"mirror {root} is {st['state']} (clone {st.get('clone_sha256_now', '')[:12]} vs mirror "
              f"{st.get('mirror_sha256_now', '')[:12]}); run gen_mirror.py --sync, or --allow-stale-mirror")
    man = M.load_manifest(root) or {}
    lib = (man.get("venv") or {}).get("cocotb_vpi_lib")
    if not lib or not Path(lib).is_file():
        U.die(f"mirror venv has no cocotb VPI library; run gen_mirror.py --sync --venv")
    rec = {"root": str(root), "tree_sha256": man.get("tree_sha256"), "git_head": (man.get("git") or {}).get("head"),
           "synced_utc": man.get("synced_utc"), "venv": man.get("venv"), "env_sh": str(root / "ci" / "env.sh"),
           "state_at_build": st["state"], "tools_home": man.get("tools_home") or str(root),
           # Digest of the tools the simv binds to NOW (not the sync-time record): the run-time re-check compares to this.
           "tools_digest": M.tools_digest(Path(man.get("tools_home") or root)), "tools_digest_synced": man.get("tools_digest")}
    return lib, rec


def absolutize_filelist(src: Path, dst: Path, rtl_root: Path | None = None) -> list[dict[str, str]]:
    """Copy a clone-root-relative VCS -f file into the outdir with absolute paths, so vcs can run
    with the outdir as cwd (its side files then land there, never in the clone root). With an RTL
    root override (mutation builds, Critic A-24) a source that exists under rtl_root replaces the
    clone's copy; every substitution is returned with both digests for the manifest."""
    out: list[str] = []
    subs: list[dict[str, str]] = []
    for raw in src.read_text(encoding="utf-8").splitlines():
        code, _, comment = raw.partition("//")
        entry = code.strip()
        if not entry:
            out.append(raw)
            continue
        if entry.startswith("+incdir+"):
            entry = "+incdir+" + str((C.SOURCE_ROOT / entry[len("+incdir+"):]).resolve())
        elif not entry.startswith(("+", "-")):
            orig = (C.SOURCE_ROOT / entry).resolve()
            chosen = orig
            if rtl_root is not None and (rtl_root / entry).is_file():
                chosen = (rtl_root / entry).resolve()
                subs.append({"file": entry, "original_sha256": U.sha256_file(orig), "mutated_sha256": U.sha256_file(chosen),
                             "mutated_path": str(chosen)})
            entry = str(chosen)
        out.append(entry + ((" //" + comment) if comment else ""))
    dst.write_text("\n".join(out) + "\n", encoding="utf-8")
    return subs


def compose_command(build: dict[str, Any], outdir: Path, a: argparse.Namespace) -> tuple[list[str], dict[str, list[str]]]:
    groups: dict[str, list[str]] = {}
    groups["base"] = list(C.VCS_BASE_FLAGS)
    groups["filelists"] = []
    a.rtl_substitutions = []
    for fl in build["filelists"]:
        dst = outdir / Path(fl).name
        a.rtl_substitutions += absolutize_filelist(C.SOURCE_ROOT / fl, dst, a.rtl_root)
        groups["filelists"] += ["-f", str(dst)]
    if a.rtl_root is not None:
        used = {sub["file"] for sub in a.rtl_substitutions}
        present = {f.relative_to(a.rtl_root).as_posix() for f in a.rtl_root.rglob("*") if f.is_file()}
        leftovers = sorted(present - used)
        if not a.rtl_substitutions:
            U.die(f"--rtl-root {a.rtl_root}: no listed source exists there; nothing would be mutated")
        if leftovers:
            U.die(f"--rtl-root {a.rtl_root}: {len(leftovers)} file(s) match no filelist entry (typo or wrong layout): "
                  f"{leftovers[:10]}")
    groups["top"] = ["-top", build["tb_top"]]
    groups["uvm"] = list(C.VCS_UVM_FLAGS)
    groups["defines"] = [f"+define+{d}" for d in list(build.get("defines") or []) + list(a.define or [])]
    groups["config"] = config_opts()
    groups["common"] = list(C.VCS_COMMON_FLAGS)
    # One -LDFLAGS string: the SIM_RECIPE base plus the build entry's extra_ldflags (placeholders rendered).
    ldflags = [C.LDFLAGS_BASE] + [render_build_field("extra_ldflags", x, build_fields(a, outdir))
                                  for x in (build.get("extra_ldflags") or [])]
    groups["ldflags"] = ["-LDFLAGS", " ".join(ldflags)]
    groups["output"] = [f"-Mdir={outdir / C.SIMV_CSRC_NAME}", "-o", str(outdir / C.SIMV_NAME)]
    groups["debug"] = list(C.VCS_DEBUG_WAVES_FLAGS if a.waves else C.VCS_DEBUG_PP_FLAGS)
    if a.coverage:
        hier = outdir / "cm_hier.cfg"
        # One +tree per coverage root; the build entry (cov_trees, default the DUT instance) is the
        # single source of the scope (P-04).
        tmpl = C.CM_HIER_TEMPLATE.read_text(encoding="utf-8")
        hier.write_text("".join(U.render_fields(tmpl, {"tb_top": build["tb_top"], "dut_instance": tree})
                                for tree in cov_trees(build) + info_trees(build)), encoding="utf-8")
        metrics = C.COV_METRICS_WITH_COND if a.cond else C.COV_METRICS_VERIFIED
        groups["coverage"] = ["-cm", metrics, *C.COV_COMPILE_EXTRA,
                              "-cm_dir", str(outdir / C.BUILD_VDB_NAME), "-cm_hier", str(hier)]
        # Constant-analysis diagnostics (constfile.txt) are the auto-Unreachable evidence (R-5.3).
        if not a.no_diag_noconst:
            groups["coverage"] += list(C.COV_DIAG_NOCONST)
    if a.cocotb or build.get("cocotb"):
        tab = outdir / C.PLI_TAB.name
        shutil.copyfile(C.PLI_TAB, tab)
        lib, a.mirror_record = cocotb_lib(a)
        groups["cocotb"] = [C.COCOTB_DEFINE, "+vpi", "-P", str(tab), "-load", lib]
    extra = list(build.get("extra_vcs_args") or []) + list(a.vcs_arg or [])
    if not a.coverage:
        # Coverage sub-options (-cm_glitch 0 and friends) mean nothing without -cm and only draw
        # Warning-[VCM-INSOPTMIS]; a no-coverage build drops them and records that it did.
        extra, a.dropped_cm_args = U.drop_cm_args(extra)
    else:
        a.dropped_cm_args = []
    groups["extra"] = extra
    groups["log"] = ["-l", str(outdir / C.COMPILE_LOG)]
    argv = ["vcs"]
    for g in ("base", "filelists", "top", "uvm", "defines", "config", "common", "ldflags", "output", "debug",
              "coverage", "cocotb", "extra", "log"):
        argv += groups.get(g, [])
    return argv, groups


def cov_trees(build: dict[str, Any]) -> list[str]:
    """Gated roots (DV Lead ruling: the two inner instances); default the DUT instance."""
    return list(build.get("cov_trees") or [build["dut_instance"]])


def info_trees(build: dict[str, Any]) -> list[str]:
    """Instrumented, reported informationally, never gated (the wrapper)."""
    return list(build.get("info_trees") or [])


def cov_scopes(build: dict[str, Any]) -> list[str]:
    return [f"{build['tb_top']}.{t}" for t in cov_trees(build)]


def info_scopes(build: dict[str, Any]) -> list[str]:
    return [f"{build['tb_top']}.{t}" for t in info_trees(build)]


def source_facts() -> dict[str, Any]:
    """source_mode and head_sha of the tree this build reads, taken from that tree's mirror manifest when the
    process is bound to a mirror (never inferred from the mere presence of an environment variable)."""
    if not os.environ.get(C.ENV_SOURCE_ROOT):
        return {"source_mode": C.SOURCE_MODE_WORKTREE, "head_sha": U.git_head()["head"]}
    man = M.load_manifest(C.SOURCE_ROOT) or {}
    if man.get("source") != C.SOURCE_MODE_HEAD or not man.get("head_sha"):
        U.die(f"{C.SOURCE_ROOT} is bound as the source root but carries no head-mode mirror manifest")
    pinned = os.environ.get(C.ENV_HEAD_SHA)
    if pinned and pinned != man["head_sha"]:
        U.die(f"pinned {C.ENV_HEAD_SHA}={pinned[:12]} but {C.SOURCE_ROOT} is the tree of {man['head_sha'][:12]}")
    return {"source_mode": C.SOURCE_MODE_HEAD, "head_sha": man["head_sha"]}


def build_fields(a: argparse.Namespace, outdir: Path) -> dict[str, str]:
    """Placeholders a build entry may use: {outdir}, and {mirror} = the tree the runs execute from
    (the shared mirror; the clone for --local-cocotb builds, whose runs stay on the submit host)."""
    fields = {"outdir": str(outdir)}
    run_root = C.SOURCE_ROOT if a.local_cocotb else M.mirror_root()
    if run_root:
        fields["mirror"] = str(run_root)
    return fields


def render_build_field(kind: str, tmpl: str, fields: dict[str, str]) -> str:
    """Token replacement; a brace token left over fails the build (a silent drop or KeyError would hide it)."""
    text = tmpl
    for k, v in fields.items():
        text = text.replace("{" + k + "}", v)
    left = re.findall(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", text)
    if left:
        U.die(f"build entry {kind} {tmpl!r}: placeholder(s) {left} not renderable (known: {sorted(fields)}; "
              "{mirror} needs mirror_root in gen_site.yaml unless --local-cocotb)")
    return text


def run_pre_build(build: dict[str, Any], outdir: Path, timeout_s: int, fields: dict[str, str]) -> list[dict[str, Any]]:
    """The build entry's pre_build commands (e.g. the ISA shim library), in order, clone root as cwd,
    the sourced environment inherited; any failure stops the build. Products under <outdir> are digested."""
    records: list[dict[str, Any]] = []
    for i, tmpl in enumerate(build.get("pre_build") or []):
        cmd = render_build_field("pre_build", tmpl, fields)
        log = outdir / f"pre_build_{i}.log"
        rc, wall, timed_out = U.run_bounded(["bash", "-c", cmd], cwd=C.SOURCE_ROOT, log_path=log, timeout_s=timeout_s)
        rec = {"command": cmd, "rc": rc, "wall_s": round(wall, 1), "timed_out": timed_out, "log": str(log)}
        records.append(rec)
        if rc != 0 or timed_out:
            U.die(f"pre_build step {i} failed (rc={rc}, timed_out={timed_out}): {cmd}; see {log}")
    lib_dir = outdir / "lib"
    if lib_dir.is_dir():
        for r in records:
            r["products"] = {f.name: U.sha256_file(f) for f in sorted(lib_dir.iterdir()) if f.is_file()}
    return records


def runtime_lib_dirs(build: dict[str, Any], fields: dict[str, str]) -> list[str]:
    return [render_build_field("runtime_lib_dirs", x, fields) for x in (build.get("runtime_lib_dirs") or [])]


def summarize_compile_log(log: Path) -> dict[str, Any]:
    text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    errors = re.findall(r"^Error-\[([\w-]+)\]", text, re.M)
    warnings = re.findall(r"^Warning-\[([\w-]+)\]", text, re.M)
    wcount: dict[str, int] = {}
    for w in warnings:
        wcount[w] = wcount.get(w, 0) + 1
    m = re.search(r"^\s*Version (\S+)", text, re.M)
    return {"error_count": len(errors), "error_classes": sorted(set(errors)),
            "warning_classes": dict(sorted(wcount.items())),
            "elab_ok": "CPU time:" in text and not errors,
            "compiler_version": m.group(1) if m else None,
            "cm_hier_note": bool(re.search(r"cm_hier|portsonly", text, re.I))}


def compile_config(argv: list[str]) -> dict[str, list[str]]:
    """Every compile-time define and parameter in the assembled command, in command order. The build
    entry's own `defines` group is one of several sources (the uvm, config and cocotb groups emit more),
    so a field populated from that group alone describes the entry rather than the compile."""
    return {"defines_all": [x for x in argv if x.startswith(C.VCS_DEFINE_PREFIX)],
            "parameters_all": [x for x in argv if x.startswith(C.VCS_PVALUE_PREFIX)]}


def self_test() -> int:
    """compile_config over a fabricated command and over the committed round-0 build record. No compile."""
    ok = True
    cfg = config_opts()
    argv = ["vcs", "-full64", "+define+UVM", *cfg, "+define+COCOTB_SIM", "-o", "simv"]
    got = compile_config(argv)
    cfg_defines = [x for x in cfg if x.startswith(C.VCS_DEFINE_PREFIX)]
    cfg_params = [x for x in cfg if x.startswith(C.VCS_PVALUE_PREFIX)]
    cond = bool(cfg_defines) and all(d in got["defines_all"] for d in cfg_defines)
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD",
          f"every define the config group emits reaches defines_all ({len(cfg_defines)} of them)")
    cond = got["parameters_all"] == cfg_params and len(got["parameters_all"]) == sum(
        1 for x in argv if x.startswith(C.VCS_PVALUE_PREFIX))
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD",
          f"parameters_all is every -pvalue in the command, in order ({len(got['parameters_all'])})")
    cond = got["defines_all"][0] == "+define+UVM" and got["defines_all"][-1] == "+define+COCOTB_SIM"
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD", "defines_all keeps command order")
    cond = "defines" not in got
    ok &= cond
    print("SELF-TEST", "ok " if cond else "BAD",
          "the old `defines` key is gone: one name never means two populations (CM222 L-1)")
    # Control on real committed bytes: the round-0 build record's own command.
    rec = C.EVIDENCE_DIR / "gen_round_0" / "gen_build_manifest_gen_tb.yaml"
    if rec.is_file():
        man = U.load_yaml(rec)
        cmd = shlex.split(man.get("command") or "")
        real = compile_config(cmd)
        old = list(man.get("defines") or [])
        cond = (len(real["defines_all"]) > len(old) and all(d in real["defines_all"] for d in old)
                and len(real["parameters_all"]) > 0)
        ok &= cond
        print("SELF-TEST", "ok " if cond else "BAD",
              f"committed round-0 record: the old key held {len(old)} define(s) of the "
              f"{len(real['defines_all'])} the command carries, with {len(real['parameters_all'])} parameter(s)")
    else:
        print("SELF-TEST ok  committed round-0 build record absent here: control skipped, stated not silent")
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true", help="compile_config cases, no compile")
    ap.add_argument("--build", help="build name from gen_testlist.yaml")
    ap.add_argument("--testlist", type=Path, default=C.TESTLIST_YAML)
    ap.add_argument("--outdir", type=Path, help="default: work/runtime/out/<build>-<utc stamp>")
    ap.add_argument("--coverage", action="store_true", help="SIM_RECIPE Section 3 instrumentation")
    ap.add_argument("--cond", action="store_true", help="add condition coverage to the metric set")
    ap.add_argument("--no-diag-noconst", action="store_true",
                    help="drop -diag noconst (constfile.txt is written by default on coverage builds)")
    ap.add_argument("--vcs-arg", action="append", help="extra vcs argument for trials (repeatable)")
    ap.add_argument("--cocotb", action="store_true", help="force the Section 4 cocotb triple")
    ap.add_argument("--local-cocotb", action="store_true",
                    help="cocotb library from the clone venv (local runs only; LSF hosts cannot see it)")
    ap.add_argument("--allow-stale-mirror", action="store_true", help="build against a stale mirror (not for evidence)")
    ap.add_argument("--waves", action="store_true", help="compile with -debug_access+all -ucli")
    ap.add_argument("--define", action="append", help="extra +define+ name (repeatable)")
    ap.add_argument("--lsf", action="store_true",
                    help="run this compile as a bsub -K job (needs the clone on shared storage)")
    ap.add_argument("--lsf-slots", type=int, default=C.LSF_BUILD_SLOTS)
    ap.add_argument("--timeout-s", type=int, default=3600)
    ap.add_argument("--force", action="store_true", help="delete an existing outdir first")
    ap.add_argument("--rtl-root", type=Path,
                    help="mutation builds (Critic A-24): directory holding mutated copies of RTL files, "
                         "clone-relative layout (e.g. <dir>/rtl/ibex_alu.sv); DV never edits rtl/ in place")
    ap.add_argument("--mutation-id", help="mutation identifier recorded with --rtl-root (required with it)")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.build:
        ap.error("--build is required")
    if os.environ.get(C.ENV_SOURCE_ROOT):
        M.lease_if_head_tree(C.SOURCE_ROOT, f'build_{a.build}')   # standalone head-tree consumer: prune must skip the tree
    if (a.rtl_root is None) != (a.mutation_id is None):
        ap.error("--rtl-root and --mutation-id go together")
    U.require_sv_constants()
    testlist = U.load_testlist(a.testlist)
    if a.build not in testlist["builds"]:
        U.die(f"build {a.build!r} not in {a.testlist}")
    build = testlist["builds"][a.build]
    outdir = (a.outdir or (C.OUT_DIR / f"{a.build}-{U.stamp_utc()}")).resolve()
    if outdir.exists():
        if not a.force:
            U.die(f"{outdir} exists; fresh outdir per build (SIM_RECIPE Section 9) or --force")
        U.remove_tree_guarded(outdir, (C.OUT_DIR, C.WORK_DIR), "build outdir (--force)")
    outdir.mkdir(parents=True)

    if a.lsf:
        # Re-invoke this script on a compute host with the same knobs minus --lsf.
        inner = [sys.executable, str(Path(__file__).resolve()), "--build", a.build, "--outdir", str(outdir),
                 "--testlist", str(a.testlist), "--force", "--timeout-s", str(a.timeout_s)]
        for flag in ("coverage", "cond", "no_diag_noconst", "cocotb", "waves", "local_cocotb", "allow_stale_mirror"):
            if getattr(a, flag):
                inner.append("--" + flag.replace("_", "-"))
        for d in a.define or []:
            inner += ["--define", d]
        for x in a.vcs_arg or []:
            inner += ["--vcs-arg", x]
        if a.rtl_root:
            inner += ["--rtl-root", str(a.rtl_root), "--mutation-id", a.mutation_id]
        job = U.LsfJob(U.env_wrapped_command(inner, C.REPO_ROOT), cwd=outdir,
                       job_name=f"{C.LSF_JOB_PREFIX}_build_{a.build}", slots=a.lsf_slots,
                       out_file=outdir / C.LSF_OUT, err_file=outdir / C.LSF_ERR, run_timeout_s=a.timeout_s)
        U.log(f"submitting build {a.build} to LSF: {' '.join(job.bsub_argv()[:12])} ...")
        job.run()
        rep = job.report()
        U.log(f"LSF build job {rep['job_id']} on {rep['host']}: bsub rc={rep['bsub_rc']} cpu_s={rep['cpu_s']}")
        manifest_path = outdir / C.BUILD_MANIFEST
        if manifest_path.is_file():
            man = U.load_yaml(manifest_path)
            man["lsf"] = rep
            U.dump_yaml(man, manifest_path)
            return 0 if man.get("status") == "ok" else 1
        U.die(f"LSF build produced no manifest; see {outdir / C.LSF_OUT}")

    U.require_env("vcs")
    a.mirror_record = None
    pre_build = run_pre_build(build, outdir, a.timeout_s, build_fields(a, outdir))
    argv, groups = compose_command(build, outdir, a)
    cg_files = U.sv_covergroup_files([C.SOURCE_ROOT / f for f in build["filelists"]])
    # Staged copy of the environment entry point: run jobs source it from the (shared) outdir.
    shutil.copyfile(C.ENV_SH, outdir / C.STAGED_ENV_SH)
    (outdir / "compile_cmd.sh").write_text(
        "#!/usr/bin/env bash\n# Exact compile command (ci/env.sh sourced; filelists are absolute copies).\n"
        f"cd {shlex.quote(str(outdir))}\n" + " \\\n    ".join(shlex.quote(x) for x in argv) + "\n",
        encoding="utf-8")
    manifest: dict[str, Any] = {
        "build": a.build, "description": build.get("description"), "tb_top": build["tb_top"],
        "dut_instance": build["dut_instance"], "build_config": C.BUILD_CONFIG, "outdir": str(outdir),
        "simv": str(outdir / C.SIMV_NAME), "compile_log": str(outdir / C.COMPILE_LOG),
        "coverage": bool(a.coverage), "cov_metrics": (groups.get("coverage") or [None, None])[1],
        "cov_scope": cov_scopes(build)[0] if a.coverage else None,
        "cov_scopes": cov_scopes(build) if a.coverage else [],
        "info_scopes": info_scopes(build) if a.coverage else [],
        "glitch_filter": all(f in groups["extra"] for f in C.GLITCH_FLAGS) if a.coverage else None,
        "rtl_root_override": str(a.rtl_root.resolve()) if a.rtl_root else None, "mutation_id": a.mutation_id,
        "rtl_substitutions": a.rtl_substitutions,
        "build_vdb": str(outdir / C.BUILD_VDB_NAME) if a.coverage else None,
        "cocotb": bool(a.cocotb or build.get("cocotb")), "waves": bool(a.waves), "mirror": a.mirror_record,
        "pre_build": pre_build, "ldflags": groups["ldflags"][1], "runtime_lib_dirs": runtime_lib_dirs(build, build_fields(a, outdir)),
        "dropped_cm_args_no_coverage": a.dropped_cm_args,
        **compile_config(argv), "constfile": str(outdir / "constfile.txt") if a.coverage and not a.no_diag_noconst else None,
        "command": " ".join(shlex.quote(x) for x in argv), "flag_groups": groups,
        "inputs": U.filelist_digest([C.SOURCE_ROOT / f for f in build["filelists"]]),
        "covergroup_files": cg_files, C.COVERGROUPS_DECLARED_KEY: bool(cg_files),
        C.B8_PROBE_KNOB_DEFAULT_KEY: U.knob_default_on(C.B8_PROBE_KNOB), C.B8_PROBE_SV_DEFAULT_KEY: U.b8_probe_sv_default_on(),
        "source_root": str(C.SOURCE_ROOT), **source_facts(), **U.export_facts(),
        "staged_env_sh": {"path": str(outdir / C.STAGED_ENV_SH), "sha256": U.sha256_file(C.ENV_SH)},
        "git": U.git_head(), "tools": U.tool_versions(), "started_utc": U.now_utc(),
    }
    U.dump_yaml(manifest, outdir / C.BUILD_MANIFEST)
    U.log(f"compiling {a.build} -> {outdir}")
    # cwd = outdir: filelists are absolute, so every vcs side file (constfile.txt, ucli.key, the
    # FSM schematic xml) lands here and never in the clone root, even with concurrent compiles.
    rc, wall, timed_out = U.run_bounded(argv, cwd=outdir, log_path=outdir / "vcs_stdout.log",
                                        timeout_s=a.timeout_s)
    summary = summarize_compile_log(outdir / C.COMPILE_LOG)
    simv_ok = (outdir / C.SIMV_NAME).is_file()
    status = "ok" if (rc == 0 and simv_ok and summary["error_count"] == 0 and not timed_out) else "failed"
    manifest.update(vcs_rc=rc, wall_s=round(wall, 1), timed_out=timed_out, compile_summary=summary,
                    status=status, finished_utc=U.now_utc())
    U.dump_yaml(manifest, outdir / C.BUILD_MANIFEST)
    (C.OUT_DIR / f"{a.build}{C.BUILD_LATEST_SUFFIX}").write_text(str(outdir) + "\n", encoding="utf-8")
    U.log(f"build {a.build}: {status} (vcs rc={rc}, errors={summary['error_count']}, "
          f"warnings={summary['warning_classes']}, {wall:.0f}s)")
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
