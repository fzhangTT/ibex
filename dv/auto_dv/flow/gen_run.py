#!/usr/bin/env python3
"""Run one test with one seed (docs/dv/SIM_RECIPE.md Section 5) and decide its verdict.

One seed drives +ntb_random_seed (SV) and RANDOM_SEED (Python); both are recorded at time zero
in run.log and in the simv command line at the head of sim.log. Coverage runs write into a
shared vdb under -cm_name test_<name>_<seed>; waves are optional; a per-run timeout bounds the
simulator (coreutils timeout inside the job, a watchdog outside it). Pass/fail comes from
gen_verdict.py (collected mechanisms), never the exit code.

The simulation itself is a generated bash script, run_cmd.sh, that sources the env.sh staged
in the build outdir: it runs unchanged on this host (default) or as an LSF job (--lsf), so a
compute host needs only the shared out-tree, not the clone or its Python venv.

Usage:
    gen_run.py --build-dir DIR --test NAME --seed N --run-dir DIR [--cov-dir VDB | --no-coverage]
               [--lsf] [--waves] [--timeout-s N] [--fcov-check] [--plusarg +x=y ...]
"""

from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import gen_fcov as F
import gen_flow_const as C
import gen_flow_util as U
import gen_mirror as M
import gen_stim as S
import gen_verdict as V


def cm_name(test: str, seed: int) -> str:
    return f"{C.CM_NAME_PREFIX}{test}_{seed}"


def compose(build: dict[str, Any], test: dict[str, Any], seed: int, run_dir: Path, cov_vdb: Path | None,
            waves: bool, extra_plusargs: list[str]) -> tuple[list[str], dict[str, str]]:
    """simv argv and the job environment (SIM_DIR, RANDOM_SEED, cocotb variables)."""
    argv = [build["simv"], "+vcs+lic+wait", f"+{C.PLUSARG_NTB_SEED}={seed}"]
    uvm_test = test.get("uvm_test")
    if uvm_test:
        argv.append(f"+{C.PLUSARG_UVM_TESTNAME}={uvm_test}")
    argv += [f"+{C.PLUSARG_UVM_VERBOSITY}={C.UVM_VERBOSITY_DEFAULT}", f"+{C.PLUSARG_UVM_NO_RELNOTES}",
             f"+{C.PLUSARG_BUILD_CONFIG}={build['build_config']}"]
    # An operator plusarg replaces a same-name testlist plusarg: VCS takes the FIRST occurrence.
    extra_names = {U.plusarg_name(x) for x in extra_plusargs}
    argv += [x for x in test["plusargs"] if U.plusarg_name(x) not in extra_names] + list(extra_plusargs)
    argv += ["-l", str(run_dir / C.SIM_LOG)]
    if cov_vdb is not None:
        argv += ["-cm", build["cov_metrics"], "-cm_dir", str(cov_vdb), "-cm_name", cm_name(test["name"], seed),
                 *C.COV_RUNTIME_EXTRA]
    if waves:
        if not build.get("waves"):
            U.die("waves requested but the build was not compiled with --waves (-debug_access+all)")
        tcl = run_dir / C.DUMP_TCL
        tcl.write_text(U.render_fields(C.DUMP_TCL_TEMPLATE.read_text(encoding="utf-8"),
                                       {"tb_top": build["tb_top"], "dut_instance": build["dut_instance"],
                                        "waves_fsdb": C.WAVES_FSDB, "waves_vpd": C.WAVES_VPD}), encoding="utf-8")
        argv += ["-ucli", "-do", str(tcl)]
    env: dict[str, str] = {"SIM_DIR": str(run_dir), C.ENV_RANDOM_SEED: str(seed)}
    lib_dirs = list(build.get("runtime_lib_dirs") or [])
    if lib_dirs:
        # Shared libraries the simv or its DPI shim load at run time (shim next to the simv, the mirror's
        # spike); a compute host cannot follow an rpath into the clone, LD_LIBRARY_PATH can.
        env["LD_LIBRARY_PATH"] = ":".join(lib_dirs) + "${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
    if test.get("cocotb_module"):
        if not build.get("cocotb"):
            U.die(f"test {test['name']} is cocotb-driven but build {build['build']} was compiled without --cocotb")
        mirror = build.get("mirror")
        # PYTHONPATH root: the mirror on LSF (the clone is invisible there), the clone for local-cocotb builds.
        py_root = Path(mirror["root"]) if mirror else C.REPO_ROOT
        env.update({C.COCOTB_ENV_MODULE: test["cocotb_module"], "PYTHONPATH": str(py_root),
                    C.COCOTB_ENV_TOPLEVEL: build["tb_top"], C.COCOTB_ENV_TOPLEVEL_LANG: C.COCOTB_TOPLEVEL_LANG})
        if not mirror:
            lib = os.environ.get(C.COCOTB_ENV_LIBPYTHON)
            if not lib:
                U.die(f"{C.COCOTB_ENV_LIBPYTHON} unset: cocotb venv not active (ci/env.sh)")
            env[C.COCOTB_ENV_LIBPYTHON] = lib
    return argv, env


def check_mirror_for_run(build: dict[str, Any]) -> dict[str, Any] | None:
    """A cocotb run needs the mirror the simv was built against: same tree hash, else fail loud."""
    mirror = build.get("mirror")
    if not mirror:
        return None
    root = Path(mirror["root"])
    man = M.load_manifest(root)
    if not man:
        U.die(f"mirror manifest missing under {root}")
    # Recompute the hash of the mirror tree itself: a manual edit under the mirror must also fail loud.
    tree_now, _ = M.tree_hash(root)
    if not (man.get("tree_sha256") == mirror.get("tree_sha256") == tree_now):
        U.die(f"mirror {root} differs from the build's record (build {str(mirror.get('tree_sha256'))[:12]}, "
              f"manifest {str(man.get('tree_sha256'))[:12]}, tree now {tree_now[:12]}); rebuild or re-sync")
    return {"root": str(root), "tree_sha256": tree_now, "git_head": (man.get("git") or {}).get("head")}


def write_job_script(path: Path, build: dict[str, Any], argv: list[str], env: dict[str, str],
                     timeout_s: int, run_dir: Path) -> None:
    """Self-contained job: staged env.sh, seed record, bounded simv, exit-code file."""
    # cocotb runs source the mirror's ci/env.sh: it activates the mirror venv (VIRTUAL_ENV, PATH,
    # LIBPYTHON_LOC via cocotb-config) exactly as the clone's env.sh does on the submit host.
    mirror = build.get("mirror") if env.get(C.COCOTB_ENV_MODULE) else None
    env_sh = Path(mirror["env_sh"]) if mirror else Path(build["outdir"]) / C.STAGED_ENV_SH
    lines = [
        "#!/usr/bin/env bash",
        "# Exact simulation command; runs on this host or as an LSF job. Reproduce: bash run_cmd.sh",
        f"export {C.ENV_TOOLCHECK_VAR}=off",
        f"source {shlex.quote(str(env_sh))} >/dev/null 2>&1",
        "echo \"GEN_RUN_ENV env_sh=" + str(env_sh) + " VIRTUAL_ENV=${VIRTUAL_ENV:-none} "
        f"{C.COCOTB_ENV_LIBPYTHON}=${{{C.COCOTB_ENV_LIBPYTHON}:-none}} python3=$(command -v python3)\"",
        f"cd {shlex.quote(str(run_dir))} || exit 97",
        *[f"export {k}={v}" if k == "LD_LIBRARY_PATH" else f"export {k}={shlex.quote(v)}" for k, v in env.items()],
        f"echo \"{C.SEED_RECORD_TAG} {C.PLUSARG_NTB_SEED}=${C.ENV_RANDOM_SEED} {C.ENV_RANDOM_SEED}=${C.ENV_RANDOM_SEED} host=$(hostname) utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)\"",
        f"{C.JOB_TIMEOUT_CMD} -k {C.TIMEOUT_GRACE_S} {timeout_s} \\",
        "    " + " \\\n    ".join(shlex.quote(x) for x in argv) + " \\",
        f"    > {shlex.quote(str(run_dir / C.SIM_STDOUT_LOG))} 2>&1",
        "rc=$?",
        f"echo $rc > {shlex.quote(str(run_dir / 'exit_code'))}",
        "echo \"GEN_RUN_EXIT rc=$rc utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)\"",
        "exit $rc",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    path.chmod(0o755)


def apply_fcov_check(result: dict[str, Any], test: dict[str, Any], vdb: Path, seed: int, run_dir: Path) -> None:
    """Trust-triad rule 3 as a collected mechanism: a declared-but-unhit bin (or an unverifiable
    query) turns a PASS into FAIL with the distinct reason 'fcov expectation unmet/unverifiable'."""
    fc = F.check_test(test, vdb, cm_name(test["name"], seed), run_dir)
    result["fcov_check"] = fc
    if fc["status"] != "PASS" and result["verdict"] in (C.VERDICT_PASS, C.VERDICT_XFAIL):
        result["verdict"] = C.VERDICT_FAIL
        result["reason"] = fc["reason"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build-dir", type=Path, required=True, help="outdir of gen_build.py")
    ap.add_argument("--test", required=True)
    ap.add_argument("--testlist", type=Path, default=C.TESTLIST_YAML)
    ap.add_argument("--seed", required=True)
    ap.add_argument("--run-dir", type=Path, required=True)
    ap.add_argument("--cov-dir", type=Path,
                    help="shared vdb path (default: the build's compile-time vdb, which holds the design data)")
    ap.add_argument("--no-coverage", action="store_true", help="run without -cm even on a coverage build")
    ap.add_argument("--lsf", action="store_true", help="submit run_cmd.sh as a bsub -K job")
    ap.add_argument("--pend-allowance-s", type=int, default=C.LSF_PEND_ALLOWANCE_S)
    ap.add_argument("--job-tag", default="", help="regression tag inside the LSF job name (per-regression cleanup check)")
    ap.add_argument("--waves", action="store_true")
    ap.add_argument("--timeout-s", type=int, help="override the testlist timeout_s")
    ap.add_argument("--plusarg", action="append", default=[], help="extra plusarg (repeatable)")
    ap.add_argument("--fcov-check", action="store_true",
                    help="run the fcov-expectation check now (single writer to the vdb)")
    ap.add_argument("--measured", choices=("auto", "yes", "no"), default="auto",
                    help="measured run (coverage enters a measured merge): auto = testlist measured flag")
    ap.add_argument("--pass-marker", help="override the testlist pass_marker (red-run evidence only)")
    a = ap.parse_args()
    U.require_sv_constants()

    build_manifest = a.build_dir.resolve() / C.BUILD_MANIFEST
    if not build_manifest.is_file():
        U.die(f"{build_manifest}: missing (not a gen_build.py outdir)")
    build = U.load_yaml(build_manifest)
    if build.get("status") != "ok":
        U.die(f"build {build.get('build')} status is {build.get('status')!r}")
    testlist = U.load_testlist(a.testlist)
    test = U.test_by_name(testlist, a.test)
    if test["build"] != build["build"]:
        U.die(f"test {a.test} needs build {test['build']!r}, given {build['build']!r}")
    seed = U.parse_seed(str(a.seed))
    run_dir = a.run_dir.resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    timeout_s = a.timeout_s or int(test["timeout_s"]) or C.DEFAULT_TIMEOUT_S

    measured = bool(test.get("measured", True)) if a.measured == "auto" else (a.measured == "yes")
    if build.get("mutation_id"):
        measured = False
    cov_vdb: Path | None = None
    if build.get("coverage") and not a.no_coverage:
        build_vdb = Path(build["build_vdb"]).resolve()
        if measured:
            cov_vdb = (a.cov_dir or build_vdb).resolve()
        else:
            # The measured/unmeasured split holds for a standalone run too (T-027 review): an unmeasured
            # run never writes into the build vdb; default is a seeded copy beside the build.
            cov_vdb = (a.cov_dir or (Path(build["outdir"]) / C.UNMEASURED_COV_DIRNAME / f"{build['build']}.vdb")).resolve()
            if cov_vdb == build_vdb:
                U.die(f"unmeasured run (measured: false / mutation) must not write into the build vdb {build_vdb}; "
                      "give --cov-dir a separate tree or use --no-coverage")
            if not cov_vdb.exists():
                cov_vdb.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(build_vdb, cov_vdb)
        cov_vdb.parent.mkdir(parents=True, exist_ok=True)
    if a.pass_marker and measured:
        U.die("--pass-marker overrides the testlist marker for red-run evidence only; refused on a measured run "
              "(use --measured no or --no-coverage)")
    pass_marker = a.pass_marker or test.get("pass_marker")
    # Debug-only knobs (tb-arch P6) never run in a measured coverage run: refuse in writing.
    debug_only = [n for n in (testlist.get("debug_only_plusargs") or [])
                  if U.plusarg_enabled(list(test["plusargs"]) + list(a.plusarg), n)]
    if measured and cov_vdb is not None and debug_only:
        refusal = {"test": test["name"], "seed": seed, "verdict": C.VERDICT_NOT_RUN,
                   "reason": f"debug-only plusarg(s) {debug_only} enabled in a measured coverage run (P6); "
                             "run it unmeasured (measured: false or --measured no)",
                   "run_dir": str(run_dir), "build": build["build"], "owner": test["owner"], "measured": True,
                   "sim_log": None, "run_log": None, "run_cmd": None, "vdb": None, "cm_name": None, "waves": None,
                   "wall_s": None, "lsf": None, "exit_code": None}
        U.dump_yaml(refusal, run_dir / C.RESULT_YAML)
        U.log(f"{test['name']} seed={seed}: NOT_RUN ({refusal['reason']})")
        return 2
    program_rec = None
    extra_plusargs = list(a.plusarg)
    if test.get("program"):
        # The image is built on the submit host into the (shared) run dir; the job only reads it.
        program_rec = S.build_program(test["program"], seed, run_dir / C.PROGRAM_DIRNAME,
                                      run_dir / "gen_program_driver.log", timeout_s=timeout_s)
        image_args = S.image_plusargs(program_rec)
        program_rec["image_plusargs"] = image_args
        extra_plusargs = image_args + extra_plusargs
    argv, env = compose(build, test, seed, run_dir, cov_vdb, a.waves, extra_plusargs)
    mirror_used = check_mirror_for_run(build) if test.get("cocotb_module") else None
    for stale in (C.SIM_LOG, C.SIM_STDOUT_LOG, C.RESULT_YAML, "exit_code", C.LSF_OUT, C.LSF_ERR):
        if (run_dir / stale).exists():
            (run_dir / stale).unlink()
    job_script = run_dir / C.RUN_CMD_SH
    write_job_script(job_script, build, argv, env, timeout_s, run_dir)

    run_log = run_dir / C.RUN_LOG
    with run_log.open("w", encoding="utf-8") as lf:
        lf.write(f"{C.SEED_RECORD_TAG} test={test['name']} seed={seed} {C.PLUSARG_NTB_SEED}={seed} "
                 f"{C.ENV_RANDOM_SEED}={seed} utc={U.now_utc()}\n")
        lf.write(f"GEN_RUN_BUILD {build['build']} simv={build['simv']} config={build['build_config']} "
                 f"git={build['git']['head']}\n")
        lf.write(f"GEN_RUN_CMD {' '.join(shlex.quote(x) for x in argv)}\n")
        lf.write(f"GEN_RUN_TIMEOUT_S {timeout_s} mode={'lsf' if a.lsf else 'local'}\n")
    U.log(f"run {test['name']} seed={seed} ({'LSF' if a.lsf else 'local'}) -> {run_dir}")
    start = time.time()
    lsf: dict[str, Any] | None = None
    if a.lsf:
        job = U.LsfJob(["bash", str(job_script)], cwd=run_dir, job_name=U.lsf_job_name(a.job_tag, f"{test['name']}_{seed}"),
                       slots=C.LSF_SIM_SLOTS, out_file=run_dir / C.LSF_OUT, err_file=run_dir / C.LSF_ERR,
                       run_timeout_s=timeout_s, pend_allowance_s=a.pend_allowance_s)
        (run_dir / "bsub_cmd.txt").write_text(" ".join(shlex.quote(x) for x in job.bsub_argv()) + "\n",
                                              encoding="utf-8")
        job.run()
        lsf = job.report()
        with (run_dir / "bsub_cmd.txt").open("a", encoding="utf-8") as bf:
            bf.write("\n".join(job.bsub_output) + "\n")
        wall = (lsf.get("wall_s") or 0.0)
        rc_file = run_dir / "exit_code"
        rc: int | None = int(rc_file.read_text().strip()) if rc_file.is_file() else None
        timed_out = rc == 124 or job.killed_reason == "run deadline exceeded"
    else:
        rc, wall, timed_out = U.run_bounded(["bash", str(job_script)], cwd=run_dir, log_path=run_log,
                                            timeout_s=timeout_s + C.TIMEOUT_GRACE_S + 60)
        if rc == 124:
            timed_out = True

    sim_log = run_dir / C.SIM_LOG
    res = V.decide(sim_log, pass_marker, timed_out, bool(test.get("expected_fail")), rc,
                   extra_logs=[run_dir / C.SIM_STDOUT_LOG], build_config=build["build_config"],
                   stderr_logs=[run_dir / C.LSF_ERR, run_log], red_fixture=bool(test.get("red_fixture")),
                   red_expect=test.get("red_expect"))
    if lsf and lsf.get("killed_reason") and res["verdict"] == C.VERDICT_PASS:
        res.update(verdict=C.VERDICT_FAIL, reason=f"LSF job killed: {lsf['killed_reason']}")
    result: dict[str, Any] = {
        "test": test["name"], "seed": seed, "verdict": res["verdict"], "reason": res["reason"],
        "evidence": res["evidence"], "exit_code": rc, "timed_out": timed_out,
        "wall_s": round(wall, 1), "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(start)),
        "finished_utc": U.now_utc(), "build": build["build"], "build_dir": str(a.build_dir.resolve()),
        "build_config": build["build_config"], "run_dir": str(run_dir), "sim_log": str(sim_log),
        "run_log": str(run_log), "run_cmd": str(job_script), "sim_stdout_log": str(run_dir / C.SIM_STDOUT_LOG),
        "vdb": str(cov_vdb) if cov_vdb else None, "cm_name": cm_name(test["name"], seed) if cov_vdb else None,
        "waves": str(run_dir / C.WAVES_FSDB) if (run_dir / C.WAVES_FSDB).exists()
        else (str(run_dir / C.WAVES_VPD) if (run_dir / C.WAVES_VPD).exists() else None),
        "uvm_counts": res["uvm_counts"], "cocotb_summary": res["cocotb_summary"],
        "finish_seen": res["finish_seen"], "marker_seen": res["marker_seen"], "pass_marker": pass_marker,
        "banner_seen": res["banner_seen"], "banner": res["banner"], "crash_signature": res.get("crash_signature"),
        "measured": measured, "mutation_id": build.get("mutation_id"),
        "expected_fail": bool(test.get("expected_fail")), "red_fixture": bool(test.get("red_fixture")),
        "red_expect": test.get("red_expect"), "owner": test["owner"],
        "fcov_expectation_file": test.get("fcov_expectation_file"), "fcov_check": None, "lsf": lsf,
        "cocotb_module": test.get("cocotb_module"), "mirror": mirror_used, "program": program_rec,
        "testlist": {"path": str(a.testlist.resolve()), "sha256": U.sha256_file(a.testlist)},
    }
    if a.fcov_check and cov_vdb and test.get("fcov_expectation_file"):
        # Standalone run = single writer to the vdb, so the per-test slice is readable now.
        apply_fcov_check(result, test, cov_vdb, seed, run_dir)
    U.dump_yaml(result, run_dir / C.RESULT_YAML)
    with run_log.open("a", encoding="utf-8") as lf:
        lf.write(f"GEN_RUN_VERDICT {result['verdict']} reason={result['reason']} wall_s={result['wall_s']} "
                 f"exit_code={rc}" + (f" lsf_job={lsf['job_id']} host={lsf['host']}" if lsf else "") + "\n")
    U.log(f"{test['name']} seed={seed}: {result['verdict']} ({result['reason']}) in {wall:.0f}s"
          + (f" [LSF {lsf['job_id']} on {lsf['host']}]" if lsf else ""))
    return 0 if result["verdict"] in (C.VERDICT_PASS, C.VERDICT_XFAIL, C.VERDICT_RED_OK) else 2


if __name__ == "__main__":
    sys.exit(main())
