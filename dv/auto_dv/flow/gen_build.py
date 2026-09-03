#!/usr/bin/env python3
"""Compile one TB top from the filelists of a build entry (docs/dv/SIM_RECIPE.md Section 2),
optionally with the Section 3 coverage instrumentation scoped to the gen_dut_top instance, the
Section 4 cocotb triple and the Section 6 wave access, into a fresh outdir, and write a build
manifest (command, flag groups, filelist digests, git HEAD, tool versions, compile-log summary).

Usage (from a login shell with ci/env.sh sourced, or through --lsf):
    gen_build.py --build gen_smoke --coverage [--cond] [--cocotb] [--waves] [--no-diag-noconst]
                 [--outdir DIR] [--lsf] [--define NAME ...] [--vcs-arg ARG ...]
"""

from __future__ import annotations

import argparse
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
                       capture_output=True, text=True, cwd=C.REPO_ROOT)
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
    st = M.status(root)
    if st["state"] != "fresh" and not a.allow_stale_mirror:
        U.die(f"mirror {root} is {st['state']} (clone {st.get('clone_sha256_now', '')[:12]} vs mirror "
              f"{st.get('mirror_sha256_now', '')[:12]}); run gen_mirror.py --sync, or --allow-stale-mirror")
    man = M.load_manifest(root) or {}
    lib = (man.get("venv") or {}).get("cocotb_vpi_lib")
    if not lib or not Path(lib).is_file():
        U.die(f"mirror venv has no cocotb VPI library; run gen_mirror.py --sync --venv")
    rec = {"root": str(root), "tree_sha256": man.get("tree_sha256"), "git_head": (man.get("git") or {}).get("head"),
           "synced_utc": man.get("synced_utc"), "venv": man.get("venv"), "env_sh": str(root / "ci" / "env.sh"),
           "state_at_build": st["state"]}
    return lib, rec


def absolutize_filelist(src: Path, dst: Path) -> None:
    """Copy a clone-root-relative VCS -f file into the outdir with absolute paths, so vcs can run
    with the outdir as cwd (its side files then land there, never in the clone root)."""
    out: list[str] = []
    for raw in src.read_text(encoding="utf-8").splitlines():
        code, _, comment = raw.partition("//")
        entry = code.strip()
        if not entry:
            out.append(raw)
            continue
        if entry.startswith("+incdir+"):
            entry = "+incdir+" + str((C.REPO_ROOT / entry[len("+incdir+"):]).resolve())
        elif not entry.startswith(("+", "-")):
            entry = str((C.REPO_ROOT / entry).resolve())
        out.append(entry + ((" //" + comment) if comment else ""))
    dst.write_text("\n".join(out) + "\n", encoding="utf-8")


def compose_command(build: dict[str, Any], outdir: Path, a: argparse.Namespace) -> tuple[list[str], dict[str, list[str]]]:
    groups: dict[str, list[str]] = {}
    groups["base"] = list(C.VCS_BASE_FLAGS)
    groups["filelists"] = []
    for fl in build["filelists"]:
        dst = outdir / Path(fl).name
        absolutize_filelist(C.REPO_ROOT / fl, dst)
        groups["filelists"] += ["-f", str(dst)]
    groups["top"] = ["-top", build["tb_top"]]
    groups["uvm"] = list(C.VCS_UVM_FLAGS)
    groups["defines"] = [f"+define+{d}" for d in list(build.get("defines") or []) + list(a.define or [])]
    groups["config"] = config_opts()
    groups["common"] = list(C.VCS_COMMON_FLAGS)
    groups["output"] = [f"-Mdir={outdir / C.SIMV_CSRC_NAME}", "-o", str(outdir / C.SIMV_NAME)]
    groups["debug"] = list(C.VCS_DEBUG_WAVES_FLAGS if a.waves else C.VCS_DEBUG_PP_FLAGS)
    if a.coverage:
        hier = outdir / "cm_hier.cfg"
        hier.write_text(U.render_fields(C.CM_HIER_TEMPLATE.read_text(encoding="utf-8"),
                                        {"tb_top": build["tb_top"], "dut_instance": build["dut_instance"]}),
                        encoding="utf-8")
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
    groups["extra"] = list(build.get("extra_vcs_args") or []) + list(a.vcs_arg or [])
    groups["log"] = ["-l", str(outdir / C.COMPILE_LOG)]
    argv = ["vcs"]
    for g in ("base", "filelists", "top", "uvm", "defines", "config", "common", "output", "debug",
              "coverage", "cocotb", "extra", "log"):
        argv += groups.get(g, [])
    return argv, groups


def summarize_compile_log(log: Path) -> dict[str, Any]:
    text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    errors = re.findall(r"^Error-\[([\w-]+)\]", text, re.M)
    warnings = re.findall(r"^Warning-\[([\w-]+)\]", text, re.M)
    wcount: dict[str, int] = {}
    for w in warnings:
        wcount[w] = wcount.get(w, 0) + 1
    m = re.search(r"Compiler version (\S+)", text)
    return {"error_count": len(errors), "error_classes": sorted(set(errors)),
            "warning_classes": dict(sorted(wcount.items())),
            "elab_ok": "CPU time:" in text and not errors,
            "compiler_version": m.group(1) if m else None,
            "cm_hier_note": bool(re.search(r"cm_hier|portsonly", text, re.I))}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", required=True, help="build name from gen_testlist.yaml")
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
    a = ap.parse_args()

    testlist = U.load_testlist(a.testlist)
    if a.build not in testlist["builds"]:
        U.die(f"build {a.build!r} not in {a.testlist}")
    build = testlist["builds"][a.build]
    outdir = (a.outdir or (C.OUT_DIR / f"{a.build}-{U.stamp_utc()}")).resolve()
    if outdir.exists():
        if not a.force:
            U.die(f"{outdir} exists; fresh outdir per build (SIM_RECIPE Section 9) or --force")
        shutil.rmtree(outdir)
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
    argv, groups = compose_command(build, outdir, a)
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
        "cov_scope": f"{build['tb_top']}.{build['dut_instance']}" if a.coverage else None,
        "build_vdb": str(outdir / C.BUILD_VDB_NAME) if a.coverage else None,
        "cocotb": bool(a.cocotb or build.get("cocotb")), "waves": bool(a.waves), "mirror": a.mirror_record,
        "defines": groups["defines"], "constfile": str(outdir / "constfile.txt") if a.coverage and not a.no_diag_noconst else None,
        "command": " ".join(shlex.quote(x) for x in argv), "flag_groups": groups,
        "inputs": U.filelist_digest([C.REPO_ROOT / f for f in build["filelists"]]),
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
