#!/usr/bin/env python3
"""Regression driver: select tests from gen_testlist.yaml (a tier, explicit names, or one
--repro test seed), compile every build they need, fan the runs out on LSF (bsub -K, one
watchdog per job, log polling with deadlines), run the fcov-expectation checks after every
writer to the shared vdb has finished, merge coverage with urg (SIM_RECIPE Section 8) and write
<outdir>/manifest.yaml plus a one-screen summary.

Usage:
    gen_regress.py --tier smoke|targeted|full [--group G] [--seeds N] [--base-seed S]
    gen_regress.py --tests gen_a,gen_b [--seeds N | --seed-list 1,2,3]
    gen_regress.py --repro gen_a 12345 [--waves]
Common knobs: --outdir DIR | --tag T, --no-coverage, --no-cond, --max-parallel N, --local,
              --build-lsf, --waves, --purpose P, --request NAME, --requester ROLE,
              --elfile F (strict), --dump-exclusions, --build-vcs-arg ARG
Tests with `measured: false` (mutation-evidence, forced-error) run into a separate vdb tree and
never enter the measured merge (Critic ruling R-5.5).
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import shutil
import sys
import time
from pathlib import Path
from typing import Any

import gen_flow_const as C
import gen_flow_util as U
import gen_cov_report as R
import gen_run as RUN


def plan_runs(testlist: dict[str, Any], a: argparse.Namespace) -> list[tuple[dict[str, Any], int]]:
    if a.repro:
        t = U.test_by_name(testlist, a.repro[0])
        return [(t, U.parse_seed(a.repro[1]))]
    names = [n for n in (a.tests or "").split(",") if n] or None
    tests = U.select_tests(testlist, a.tier, names, a.group)
    override: int | list[int] | None = None
    if a.seed_list:
        override = [U.parse_seed(s) for s in a.seed_list.split(",")]
    elif a.seeds is not None:
        override = a.seeds
    plan = []
    for t in tests:
        for s in U.seeds_for_test(t, override, a.base_seed):
            plan.append((t, s))
    return plan


def compile_build(name: str, outdir: Path, a: argparse.Namespace, coverage: bool) -> dict[str, Any]:
    bdir = outdir / "build" / name
    argv = [sys.executable, str(C.FLOW_DIR / "gen_build.py"), "--build", name, "--outdir", str(bdir),
            "--testlist", str(a.testlist)]
    if coverage:
        argv.append("--coverage")
        if not a.no_cond:
            argv.append("--cond")
    if a.waves:
        argv.append("--waves")
    for x in a.build_vcs_arg or []:
        argv += ["--vcs-arg", x]
    if a.rtl_root:
        argv += ["--rtl-root", str(a.rtl_root), "--mutation-id", a.mutation_id]
    if a.build_lsf and not a.local:
        argv.append("--lsf")
    U.log(f"build {name}: {' '.join(argv[2:])}")
    rc, wall, timed_out = U.run_bounded(argv, cwd=C.REPO_ROOT, log_path=outdir / "regress.log",
                                        timeout_s=a.build_timeout_s)
    man_path = bdir / C.BUILD_MANIFEST
    man = U.load_yaml(man_path) if man_path.is_file() else {}
    unmeasured_vdb = None
    if coverage and man.get("status") == "ok" and man.get("build_vdb"):
        # Separate -cm_dir tree for non-measured tests (R-5.5), seeded with the compile-time design data.
        unmeasured_vdb = outdir / C.UNMEASURED_COV_DIRNAME / f"{name}.vdb"
        unmeasured_vdb.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(man["build_vdb"], unmeasured_vdb)
    return {"dir": str(bdir), "manifest": str(man_path), "status": man.get("status", "failed"),
            "rc": rc, "wall_s": round(wall, 1), "timed_out": timed_out, "lsf": man.get("lsf"),
            "cov_metrics": man.get("cov_metrics"), "defines": man.get("defines"), "constfile": man.get("constfile"),
            "cov_scope": man.get("cov_scope"), "cov_scopes": man.get("cov_scopes") or [],
            "info_scopes": man.get("info_scopes") or [], "glitch_filter": man.get("glitch_filter"), "vdb": None,
            "mutation_id": man.get("mutation_id"), "rtl_root_override": man.get("rtl_root_override"),
            "rtl_substitutions": man.get("rtl_substitutions"),
            "unmeasured_vdb": str(unmeasured_vdb) if unmeasured_vdb else None}


def run_one(t: dict[str, Any], seed: int, build: dict[str, Any], outdir: Path, a: argparse.Namespace,
            coverage: bool) -> dict[str, Any]:
    """One test+seed through gen_run.py (which submits its own bsub -K job unless --local)."""
    run_dir = outdir / "runs" / f"{t['name']}_{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)
    measured = bool(t.get("measured", True)) and not a.mutation_id
    cov_vdb = Path(build["dir"]) / C.BUILD_VDB_NAME if measured else Path(build["unmeasured_vdb"] or "")
    argv = [sys.executable, str(C.FLOW_DIR / "gen_run.py"), "--build-dir", build["dir"], "--test", t["name"],
            "--seed", str(seed), "--run-dir", str(run_dir), "--testlist", str(a.testlist),
            "--pend-allowance-s", str(a.pend_allowance_s), "--job-tag", outdir.name,
            "--measured", "yes" if measured else "no"]
    if coverage:
        argv += ["--cov-dir", str(cov_vdb)]
    else:
        argv.append("--no-coverage")
    if a.waves:
        argv.append("--waves")
    if not a.local:
        argv.append("--lsf")
    timeout_s = int(t["timeout_s"]) or C.DEFAULT_TIMEOUT_S
    outer = timeout_s + C.TIMEOUT_GRACE_S + 300 + (0 if a.local else a.pend_allowance_s)
    U.run_bounded(argv, cwd=run_dir, log_path=run_dir / "driver.log", timeout_s=outer)
    res_path = run_dir / C.RESULT_YAML
    if res_path.is_file():
        res = U.load_yaml(res_path)
    else:
        res = {"test": t["name"], "seed": seed, "verdict": C.VERDICT_NOT_RUN,
               "reason": "gen_run.py wrote no result.yaml (see driver.log)", "sim_log": str(run_dir / C.SIM_LOG),
               "run_log": str(run_dir / C.RUN_LOG), "run_cmd": str(run_dir / C.RUN_CMD_SH), "vdb": None,
               "cm_name": None, "waves": None, "wall_s": None, "owner": t["owner"], "lsf": None}
    res["result_yaml"] = str(res_path)
    res["run_dir"] = str(run_dir)
    res["measured"] = measured
    lsf = res.get("lsf")
    U.log(f"{t['name']} seed={seed}: {res['verdict']} ({res.get('reason')})"
          + (f" [LSF {lsf['job_id']} on {lsf['host']}]" if lsf else ""))
    return res


def post_fcov_checks(runs: list[dict[str, Any]], testlist: dict[str, Any], outdir: Path) -> None:
    """Per-test, pre-merge (trust triad rule 3), only after every writer to the vdb has finished:
    each PASS/XFAIL run with a manifest is checked on its own vdb slice; unmet or unverifiable
    expectations turn the run into FAIL with the distinct reason."""
    for r in runs:
        t = U.test_by_name(testlist, r["test"])
        if not (t.get("fcov_expectation_file") and r.get("vdb")):
            continue
        if r["verdict"] not in (C.VERDICT_PASS, C.VERDICT_XFAIL):
            continue
        RUN.apply_fcov_check(r, t, Path(r["vdb"]), int(r["seed"]), Path(r["run_dir"]))
        res_path = Path(r["result_yaml"])
        if res_path.is_file():
            stored = U.load_yaml(res_path)
            stored["fcov_check"] = r["fcov_check"]
            stored["verdict"] = r["verdict"]
            stored["reason"] = r["reason"]
            U.dump_yaml(stored, res_path)


def fcov_summary(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Expectation results per test for the manifest and the dashboard."""
    per_test: dict[str, dict[str, Any]] = {}
    for r in runs:
        fc = r.get("fcov_check") or {}
        entry = per_test.setdefault(r["test"], {"runs": 0, "checked": 0, "pass": 0, "unmet": 0, "unverifiable": 0,
                                                "declared_bins": 0, "unmet_bins": []})
        entry["runs"] += 1
        if not fc or fc.get("status") == "NO_MANIFEST":
            continue
        entry["checked"] += 1
        entry["declared_bins"] = max(entry["declared_bins"], fc.get("declared", 0))
        if fc.get("status") == "PASS":
            entry["pass"] += 1
        elif fc.get("status") == "UNHIT":
            entry["unmet"] += 1
            entry["unmet_bins"] = sorted(set(entry["unmet_bins"]) | set(fc.get("unmet_bins") or []))
        else:
            entry["unverifiable"] += 1
    totals = {"checked": sum(e["checked"] for e in per_test.values()), "pass": sum(e["pass"] for e in per_test.values()),
              "unmet": sum(e["unmet"] for e in per_test.values()),
              "unverifiable": sum(e["unverifiable"] for e in per_test.values())}
    return {"totals": totals, "per_test": per_test}


def summarize(runs: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {v: 0 for v in (C.VERDICT_PASS, C.VERDICT_FAIL, C.VERDICT_XFAIL, C.VERDICT_TIMEOUT, C.VERDICT_NOT_RUN)}
    for r in runs:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    n = len(runs)
    good = counts[C.VERDICT_PASS] + counts[C.VERDICT_XFAIL]
    out = {"planned": n, **{k.lower(): v for k, v in counts.items()},
           "pass_rate_pct": round(100.0 * good / n, 2) if n else None}
    # Trust-triad rule 3 accounting (P-07): runs without a declared-bins manifest are listed, never silent.
    exempt = sorted({r["test"] for r in runs if not r.get("fcov_expectation_file")})
    out["runs_without_fcov_manifest"] = sum(1 for r in runs if not r.get("fcov_expectation_file"))
    out["tests_without_fcov_manifest"] = exempt
    return out


def fcov_policy_failures(runs: list[dict[str, Any]], testlist: dict[str, Any], covergroups_exist: bool) -> None:
    """A null manifest is a missing trust-triad artefact on (a) every tier the testlist header names
    and (b) every measured tier as soon as any covergroup exists in the merged report (the policy
    becomes live with the first covergroup; tier check stays exempt)."""
    required = set(testlist.get("fcov_manifest_required_tiers") or [])
    if covergroups_exist:
        required |= set(C.TIERS)
    for r in runs:
        t = U.test_by_name(testlist, r["test"])
        if t["tier"] in required and not t.get("fcov_expectation_file") and r["verdict"] == C.VERDICT_PASS:
            r["verdict"] = C.VERDICT_FAIL
            r["reason"] = (f"no fcov_expectation_file on tier {t['tier']} while covergroups exist "
                           "(trust triad rule 3)" if covergroups_exist and t["tier"] not in
                           set(testlist.get("fcov_manifest_required_tiers") or []) else
                           f"no fcov_expectation_file on tier {t['tier']} (fcov_manifest_required_tiers)")
            res_path = Path(r["result_yaml"]) if r.get("result_yaml") else None
            if res_path and res_path.is_file():
                stored = U.load_yaml(res_path)
                stored["verdict"] = r["verdict"]
                stored["reason"] = r["reason"]
                U.dump_yaml(stored, res_path)


def lsf_cost(builds: dict[str, Any], runs: list[dict[str, Any]]) -> dict[str, Any]:
    cost = {"jobs": 0, "cpu_s": 0.0, "wall_s": 0.0, "pend_s": 0.0, "slot_s": 0.0, "cpu_unknown_jobs": 0}
    reports = [b.get("lsf") for b in builds.values()] + [r.get("lsf") for r in runs]
    for rep in reports:
        if not rep or not rep.get("job_id"):
            continue
        cost["jobs"] += 1
        if rep.get("cpu_s") is None:
            cost["cpu_unknown_jobs"] += 1
        else:
            cost["cpu_s"] += rep["cpu_s"]
        cost["wall_s"] += rep.get("wall_s") or 0.0
        cost["pend_s"] += rep.get("pend_s") or 0.0
        cost["slot_s"] += (rep.get("wall_s") or 0.0) * (rep.get("slots") or 1)
    for k in ("cpu_s", "wall_s", "pend_s", "slot_s"):
        cost[k] = round(cost[k], 1)
    return cost


def self_test() -> int:
    """fcov_policy_failures and fcov_summary on fabricated run records (no simulation)."""
    tl = {"tests": [{"name": "gen_a", "tier": "smoke", "fcov_expectation_file": None},
                    {"name": "gen_b", "tier": "check", "fcov_expectation_file": None},
                    {"name": "gen_c", "tier": "targeted", "fcov_expectation_file": "x.fcov.yaml"}],
          "fcov_manifest_required_tiers": []}
    def runs():
        return [{"test": "gen_a", "seed": 1, "verdict": C.VERDICT_PASS, "reason": "", "result_yaml": None,
                 "fcov_expectation_file": None},
                {"test": "gen_b", "seed": 1, "verdict": C.VERDICT_PASS, "reason": "", "result_yaml": None,
                 "fcov_expectation_file": None},
                {"test": "gen_c", "seed": 1, "verdict": C.VERDICT_PASS, "reason": "", "result_yaml": None,
                 "fcov_expectation_file": "x.fcov.yaml",
                 "fcov_check": {"status": "UNHIT", "declared": 3, "hit": 2, "unmet_bins": ["gen_x_cg.cp.b"]}}]
    ok = True
    r = runs(); fcov_policy_failures(r, tl, covergroups_exist=False)
    cond = [x["verdict"] for x in r] == [C.VERDICT_PASS] * 3
    ok &= cond; print("SELF-TEST", "ok " if cond else "BAD", "no covergroup yet: null manifests pass")
    r = runs(); fcov_policy_failures(r, tl, covergroups_exist=True)
    cond = r[0]["verdict"] == C.VERDICT_FAIL and "covergroups exist" in r[0]["reason"] and r[1]["verdict"] == C.VERDICT_PASS
    ok &= cond; print("SELF-TEST", "ok " if cond else "BAD", "covergroups exist: smoke null manifest FAILs, tier check exempt")
    tl2 = dict(tl, fcov_manifest_required_tiers=["smoke"])
    r = runs(); fcov_policy_failures(r, tl2, covergroups_exist=False)
    cond = r[0]["verdict"] == C.VERDICT_FAIL and "fcov_manifest_required_tiers" in r[0]["reason"]
    ok &= cond; print("SELF-TEST", "ok " if cond else "BAD", "header policy: named tier FAILs without a manifest")
    fs = fcov_summary(runs())
    cond = fs["totals"] == {"checked": 1, "pass": 0, "unmet": 1, "unverifiable": 0} and \
        fs["per_test"]["gen_c"]["unmet_bins"] == ["gen_x_cg.cp.b"] and fs["per_test"]["gen_a"]["checked"] == 0
    ok &= cond; print("SELF-TEST", "ok " if cond else "BAD", f"fcov_summary totals/per_test: {fs['totals']}")
    sm = summarize(runs())
    cond = sm["runs_without_fcov_manifest"] == 2 and sm["tests_without_fcov_manifest"] == ["gen_a", "gen_b"]
    ok &= cond; print("SELF-TEST", "ok " if cond else "BAD", "summarize counts runs without a manifest")
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 2


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sel = ap.add_mutually_exclusive_group()
    sel.add_argument("--tier", choices=C.ALL_TIERS)
    sel.add_argument("--tests", help="comma-separated test names")
    sel.add_argument("--repro", nargs=2, metavar=("TEST", "SEED"), help="rerun exactly one test+seed")
    ap.add_argument("--group", help="feature group filter for --tier targeted")
    ap.add_argument("--seeds", type=int, help="seed count per test (overrides the testlist)")
    ap.add_argument("--seed-list", help="explicit comma-separated seeds for every selected test")
    ap.add_argument("--base-seed", type=int, default=None, help="base of the deterministic seed derivation")
    ap.add_argument("--testlist", type=Path, default=C.TESTLIST_YAML)
    ap.add_argument("--outdir", type=Path)
    ap.add_argument("--tag", help="outdir = work/runtime/out/regress_<tag> (default: utc stamp)")
    ap.add_argument("--no-coverage", action="store_true")
    ap.add_argument("--no-cond", action="store_true", help="drop condition coverage from the metric set")
    ap.add_argument("--waves", action="store_true", help="waves build + dump on every run (debug only)")
    ap.add_argument("--max-parallel", type=int, default=8)
    ap.add_argument("--local", action="store_true", help="no LSF: build and run on this host")
    ap.add_argument("--build-lsf", action="store_true",
                    help="compile through LSF too (needs the clone on shared storage; default: compile here)")
    ap.add_argument("--build-timeout-s", type=int, default=3600)
    ap.add_argument("--pend-allowance-s", type=int, default=C.LSF_PEND_ALLOWANCE_S)
    ap.add_argument("--purpose", type=int, choices=sorted(C.PURPOSES))
    ap.add_argument("--request", help="run-request name this regression serves")
    ap.add_argument("--requester", help="role slug of the requester")
    ap.add_argument("--elfile", type=Path, action="append",
                    help="URG exclusion file(s) for the measured merge (loaded with -excl_strict)")
    ap.add_argument("--dump-exclusions", action="store_true",
                    help="urg -dump full_exclusions at the measured merge (implied by --purpose 4)")
    ap.add_argument("--build-vcs-arg", action="append", help="extra vcs argument for every build (trials)")
    ap.add_argument("--no-sync-mirror", action="store_true",
                    help="do not re-sync the shared mirror before cocotb builds (default: sync)")
    ap.add_argument("--allow-local-out-root", action="store_true",
                    help="proceed with an out root on a local filesystem (debug on a single host only)")
    ap.add_argument("--rtl-root", type=Path, help="mutation build: directory of mutated RTL copies (A-24)")
    ap.add_argument("--mutation-id", help="mutation identifier (with --rtl-root); every run is unmeasured")
    ap.add_argument("--force", action="store_true", help="delete an existing outdir")
    a = ap.parse_args()
    if not (a.tier or a.tests or a.repro):
        ap.error("one of --tier, --tests, --repro is required")
    U.require_env("vcs", "urg", "bsub" if not a.local else "vcs")
    U.require_sv_constants()
    if (a.rtl_root is None) != (a.mutation_id is None):
        ap.error("--rtl-root and --mutation-id go together")
    if a.mutation_id and a.purpose == 4:
        ap.error("a mutation build never enters a measurement (purpose 4)")
    if not a.local and not U.path_is_shared(C.OUT_DIR) and not a.allow_local_out_root:
        U.die(f"out root {C.OUT_DIR} is on a local filesystem ({U.fs_type(C.OUT_DIR)}); LSF jobs cannot see it. "
              f"Set out_root in {C.SITE_YAML} or {C.ENV_OUT_ROOT} (SIM_RECIPE Section 7), or --allow-local-out-root")

    start = time.time()
    testlist = U.load_testlist(a.testlist)
    if a.base_seed is None:
        a.base_seed = int(start) & 0x7FFFFFFF
    coverage = not a.no_coverage and not a.repro
    plan = plan_runs(testlist, a)
    if not plan:
        U.die("no test selected")
    outdir = (a.outdir or (C.OUT_DIR / f"regress_{a.tag or U.stamp_utc()}")).resolve()
    if outdir.exists():
        if not a.force:
            U.die(f"{outdir} exists (fresh outdir per regression; --force to replace)")
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)
    shutil.copyfile(a.testlist, outdir / "testlist_used.yaml")
    manifest: dict[str, Any] = {
        "kind": "regression", "tag": a.tag, "request": a.request, "requester": a.requester,
        "out_root": str(C.OUT_DIR), "out_root_fs": U.fs_type(C.OUT_DIR), "site_yaml": str(C.SITE_YAML),
        "testlist": {"path": str(a.testlist.resolve()), "sha256": U.sha256_file(a.testlist),
                     "copy": str(outdir / "testlist_used.yaml")},
        "mutation": {"id": a.mutation_id, "rtl_root": str(a.rtl_root)} if a.mutation_id else None,
        "purpose": a.purpose, "purpose_text": C.PURPOSES.get(a.purpose) if a.purpose else None,
        "build_config": C.BUILD_CONFIG,
        "scope": {"tier": a.tier, "tests": a.tests, "group": a.group, "repro": a.repro,
                  "seeds_override": a.seeds, "seed_list": a.seed_list, "base_seed": a.base_seed,
                  "coverage": coverage, "cond": coverage and not a.no_cond, "waves": a.waves,
                  "local": a.local, "max_parallel": a.max_parallel},
        "planned_runs": [{"test": t["name"], "seed": s, "build": t["build"]} for t, s in plan],
        "outdir": str(outdir), "regress_log": str(outdir / "regress.log"),
        "git": U.git_head(), "tools": U.tool_versions(), "started_utc": U.now_utc(), "status": "running",
    }
    U.dump_yaml(manifest, outdir / "manifest.yaml")
    U.log(f"regression {outdir.name}: {len(plan)} runs, coverage={coverage}, base_seed={a.base_seed}")

    builds: dict[str, Any] = {}
    needs_mirror = any(testlist["builds"][b].get("cocotb") for b in {t["build"] for t, _ in plan})
    if needs_mirror and not a.no_sync_mirror and not a.local:
        # cocotb builds load the VPI library from the mirror venv and runs import from the mirror:
        # sync it first so the build records the revision the runs will see.
        rc, wall, _ = U.run_bounded([sys.executable, str(C.FLOW_DIR / "gen_mirror.py"), "--sync"], cwd=C.REPO_ROOT,
                                    log_path=outdir / "regress.log", timeout_s=1800)
        manifest["mirror_sync"] = {"rc": rc, "wall_s": round(wall, 1)}
        U.log(f"mirror sync rc={rc} in {wall:.0f}s")
        if rc != 0:
            U.die(f"gen_mirror.py --sync failed; see {outdir / 'regress.log'}")
    for bname in sorted({t["build"] for t, _ in plan}):
        builds[bname] = compile_build(bname, outdir, a, coverage)
        manifest["builds"] = builds
        U.dump_yaml(manifest, outdir / "manifest.yaml")
        if builds[bname]["status"] != "ok":
            U.log(f"build {bname} FAILED; runs on it are NOT_RUN")

    runs: list[dict[str, Any]] = []
    with cf.ThreadPoolExecutor(max_workers=max(1, a.max_parallel)) as pool:
        futs = []
        for t, s in plan:
            b = builds[t["build"]]
            if b["status"] != "ok":
                runs.append({"test": t["name"], "seed": s, "verdict": C.VERDICT_NOT_RUN,
                             "reason": f"build {t['build']} failed", "owner": t["owner"], "lsf": None,
                             "vdb": None, "cm_name": None, "waves": None, "sim_log": None, "run_log": None,
                             "run_cmd": None, "result_yaml": None, "wall_s": None, "run_dir": None})
                continue
            futs.append(pool.submit(run_one, t, s, b, outdir, a, coverage))
        for f in cf.as_completed(futs):
            runs.append(f.result())
            manifest["runs"] = sorted(runs, key=lambda r: (r["test"], r["seed"]))
            manifest["summary"] = summarize(runs)
            U.dump_yaml(manifest, outdir / "manifest.yaml")
    runs.sort(key=lambda r: (r["test"], r["seed"]))

    cov_status = "not_requested"
    if coverage:
        post_fcov_checks(runs, testlist, outdir)
        measured_vdbs: list[Path] = []
        unmeasured_vdbs: list[Path] = []
        for bname, b in builds.items():
            cand = Path(b["dir"]) / C.BUILD_VDB_NAME
            b["vdb"] = str(cand) if cand.is_dir() else None
            if b["vdb"] and any(r.get("vdb") and r.get("measured", True) for r in runs if r.get("build") == bname):
                measured_vdbs.append(cand)
            if b.get("unmeasured_vdb") and any(r.get("vdb") and not r.get("measured", True) for r in runs
                                               if r.get("build") == bname):
                unmeasured_vdbs.append(Path(b["unmeasured_vdb"]))
        dut_scopes = sorted({sc for b in builds.values() for sc in (b.get("cov_scopes") or [b.get("cov_scope")]) if sc})
        info_scopes = sorted({sc for b in builds.values() for sc in (b.get("info_scopes") or [])})
        dump = a.dump_exclusions or a.purpose == 4
        if measured_vdbs:
            U.log(f"urg merge (measured) of {len(measured_vdbs)} vdb(s)" + (" with exclusion dump" if dump else ""))
            cov = R.merge(outdir / "cov", sorted(measured_vdbs), a.elfile, dut_scopes=dut_scopes, dump_exclusions=dump,
                          info_scopes=info_scopes)
            cov["build_defines"] = {n: b.get("defines") for n, b in builds.items()}
            cov["glitch_filter"] = {n: b.get("glitch_filter") for n, b in builds.items()}
            cov["rulings"] = {"scope": C.ruling_scope_text(dut_scopes, info_scopes), "glitch": C.RULING_GLITCH}
            cov["constfiles"] = {n: b.get("constfile") for n, b in builds.items()}
            cov["measured_tests"] = sorted({r["test"] for r in runs if r.get("measured", True)})
        elif not any(r.get("measured", True) for r in runs):
            cov = {"status": "ok_no_measured_tests", "urg_rc": None, "totals": {}, "dut_scope": {},
                   "note": "every selected test is measured: false; no measured merge"}
        else:
            cov = {"status": "no_vdb", "urg_rc": None, "totals": {}, "dut_scope": {}, "note": "no measured vdb produced"}
        cov_status = cov["status"]
        if unmeasured_vdbs:
            U.log(f"urg merge (unmeasured, informational) of {len(unmeasured_vdbs)} vdb(s)")
            # A requested exclusion dump lands on the unmeasured merge when no measured merge exists.
            cov["unmeasured"] = R.merge(outdir / C.UNMEASURED_COV_DIRNAME, sorted(unmeasured_vdbs), None,
                                        dut_scopes=dut_scopes, dump_exclusions=dump and not measured_vdbs,
                                        info_scopes=info_scopes)
            cov["unmeasured"]["tests"] = sorted({r["test"] for r in runs if not r.get("measured", True)})
            cov["unmeasured"]["glitch_filter"] = {n: b.get("glitch_filter") for n, b in builds.items()}
            cov["unmeasured"]["rulings"] = {"scope": C.ruling_scope_text(dut_scopes, info_scopes), "glitch": C.RULING_GLITCH}
        manifest["coverage"] = cov
        # Covergroups exist once URG reports a GROUP total in any merge of this regression.
        groups_seen = any((m_.get("totals") or {}).get("group") not in (None, C.NOT_APPLICABLE)
                          for m_ in (cov, cov.get("unmeasured") or {}))
        fcov_policy_failures(runs, testlist, groups_seen)
        manifest["fcov"] = fcov_summary(runs)
        manifest["fcov"]["covergroups_exist"] = groups_seen
        if cov.get("dashboard_txt"):
            U.log(f"URG dashboard: {cov['dashboard_txt']} totals={cov['totals']}")
        if cov.get("exclusion_violations"):
            U.log(f"EXCLUSION VIOLATION (strict): {cov['exclusion_violations'][:3]} -> merge FAILED")
    manifest.update(runs=runs, summary=summarize(runs), lsf_cost=lsf_cost(builds, runs),
                    finished_utc=U.now_utc(), wall_s=round(time.time() - start, 1), status="done",
                    lsf_jobs_left=U.lsf_jobs_left(U.lsf_job_name(outdir.name, "")) if not a.local else [])
    U.dump_yaml(manifest, outdir / "manifest.yaml")
    s = manifest["summary"]
    ft = (manifest.get("fcov") or {}).get("totals") or {}
    U.log(f"done: {s['pass']} pass, {s['fail']} fail, {s['xfail']} xfail, {s['timeout']} timeout, "
          f"{s['not_run']} not_run of {s['planned']}; fcov expectations checked {ft.get('checked', 0)} "
          f"(unmet {ft.get('unmet', 0)}, unverifiable {ft.get('unverifiable', 0)}); {s['runs_without_fcov_manifest']} "
          f"run(s) without an fcov manifest {s['tests_without_fcov_manifest']}; manifest {outdir / 'manifest.yaml'}")
    if manifest["lsf_jobs_left"]:
        U.log(f"WARNING: LSF jobs still present with prefix {C.LSF_JOB_PREFIX}: {manifest['lsf_jobs_left']}")
    bad = s["fail"] + s["timeout"] + s["not_run"]
    if coverage and cov_status not in ("ok", "ok_no_measured_tests"):
        U.log(f"coverage merge status {cov_status!r}: regression FAILED")
        return 3
    return 0 if bad == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
