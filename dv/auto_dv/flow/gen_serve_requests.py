#!/usr/bin/env python3
"""Run-request queue server (agent_team_prompt.txt, Runtime Manager section).

A requester writes dv/auto_dv/work/runtime/requests/<requester>-<seq>.yaml with the fields
requester, purpose (1..4), tests, seeds, coverage, notes. This script moves the file to
running/, executes gen_regress.py with the scope the purpose allows, refuses in writing a scope
larger than the purpose, writes results/<same-name>/manifest.yaml and moves the request to
done/. Schema and purposes: dv/auto_dv/docs/gen_runtime_api.md.

Usage:
    gen_serve_requests.py --once                 # serve everything pending, then exit
    gen_serve_requests.py --watch [--interval 30] [--duration 3600]
    gen_serve_requests.py --dry-run              # print the scope decision per pending request
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any

import gen_flow_const as C
import gen_flow_util as U

TIER_WORDS = {"smoke": "smoke", "targeted": "targeted", "full": "full", "all": "full"}


def parse_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ("yes", "y", "true", "1", "on")


def pending_requests() -> list[Path]:
    C.REQUESTS_DIR.mkdir(parents=True, exist_ok=True)
    files = [p for p in C.REQUESTS_DIR.iterdir() if p.is_file() and C.REQUEST_NAME_RE.match(p.name)]
    return sorted(files, key=lambda p: (p.stat().st_mtime, p.name))


def validate(req: Any, name: str) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(req, dict):
        return None, "request is not a mapping"
    missing = [k for k in C.REQUEST_REQUIRED_KEYS if k not in req]
    if missing:
        return None, f"missing keys {missing}"
    m = C.REQUEST_NAME_RE.match(name)
    if req["requester"] not in C.OWNER_ROLES:
        return None, f"requester {req['requester']!r} is not a role slug"
    if m and m.group("requester") != req["requester"]:
        return None, f"file name requester {m.group('requester')!r} != field {req['requester']!r}"
    try:
        purpose = int(req["purpose"])
    except (TypeError, ValueError):
        return None, "purpose must be an integer 1..4"
    if purpose not in C.PURPOSES:
        return None, f"purpose {purpose} not in {sorted(C.PURPOSES)}"
    tests = req["tests"]
    if isinstance(tests, str):
        tests = [t.strip() for t in tests.split(",") if t.strip()]
    if not isinstance(tests, list) or not tests:
        return None, "tests must be a non-empty list, a comma list, or a tier word"
    seeds = req["seeds"]
    if isinstance(seeds, str) and seeds.strip().isdigit():
        seeds = int(seeds)
    if isinstance(seeds, str):
        seeds = [U.parse_seed(s.strip()) for s in seeds.split(",") if s.strip()]
    if not isinstance(seeds, (int, list)):
        return None, "seeds must be a count or an explicit list"
    norm = dict(req)
    bva = req.get("build_vcs_args") or []
    if isinstance(bva, str):
        bva = [bva]
    if not isinstance(bva, list) or not all(isinstance(x, str) for x in bva):
        return None, "build_vcs_args must be a list of strings"
    norm.update(purpose=purpose, tests=tests, seeds=seeds, coverage=parse_bool(req["coverage"]),
                waves=parse_bool(req.get("waves", False)), group=req.get("group"),
                component=req.get("component"), notes=str(req.get("notes") or ""),
                build_vcs_args=bva, dump_exclusions=parse_bool(req.get("dump_exclusions", False)))
    return norm, None


def scope_for(req: dict[str, Any], testlist: dict[str, Any]) -> tuple[list[str] | None, str | None, dict[str, Any]]:
    """Return (gen_regress args, refusal reason, scope record). Only purpose 4 runs everything."""
    p = req["purpose"]
    tests = req["tests"]
    seeds = req["seeds"]
    tier = TIER_WORDS.get(tests[0].lower()) if len(tests) == 1 and tests[0].lower() in TIER_WORDS else None
    known = {t["name"] for t in testlist["tests"]}
    explicit = [] if tier else tests
    unknown = [t for t in explicit if t not in known and not t.startswith("component:")]
    if unknown:
        return None, f"unknown test(s) {unknown}; see gen_testlist.yaml", {}
    seed_count = len(seeds) if isinstance(seeds, list) else int(seeds)
    args: list[str] = []
    scope: dict[str, Any] = {"purpose": p, "tier": tier, "tests": explicit, "seed_count": seed_count,
                             "coverage": req["coverage"], "waves": req["waves"]}
    if p == 1:
        if tier or len(explicit) != C.PURPOSE1_MAX_TESTS:
            return None, f"purpose 1 (bring-up) runs exactly one named test, got {tests}", scope
        if seed_count > C.PURPOSE1_MAX_SEEDS:
            return None, f"purpose 1 allows at most {C.PURPOSE1_MAX_SEEDS} seeds, got {seed_count}", scope
        args += ["--tests", explicit[0]]
    elif p == 2:
        comp = req.get("component") or next((t.split(":", 1)[1] for t in explicit if t.startswith("component:")), None)
        if tier == "full":
            return None, "purpose 2 (component change) never runs the full tier; use purpose 4", scope
        if not comp and not explicit:
            return None, "purpose 2 needs a component (field component or tests: [component:<name>])", scope
        selected = {t["name"] for t in testlist["tests"] if t["tier"] == "smoke"}
        if comp:
            selected |= {t["name"] for t in testlist["tests"] if t.get("component") == comp}
            selected |= {t["name"] for t in testlist["tests"]
                         if "mutation" in (t.get("feature_groups") or []) and t.get("component") == comp}
        selected |= {t for t in explicit if not t.startswith("component:")}
        scope["component"] = comp
        scope["tests"] = sorted(selected)
        args += ["--tests", ",".join(sorted(selected))]
    elif p == 3:
        if tier or len(explicit) != 1 or not isinstance(seeds, list) or len(seeds) != C.PURPOSE3_SEEDS:
            return None, "purpose 3 (repro) runs exactly one test with exactly one explicit seed", scope
        args += ["--repro", explicit[0], str(seeds[0])]
        if req["waves"]:
            args.append("--waves")
        if req["coverage"]:
            scope["note"] = "coverage requested on a repro is ignored: a repro reruns test+seed exactly (purpose 3)"
    elif p == 4:
        if tier != "full":
            return None, "purpose 4 (gate or closure measurement) runs the full tier: tests: full", scope
        if not req["coverage"]:
            return None, "purpose 4 is a coverage measurement: coverage must be yes", scope
        if req["requester"] not in C.PURPOSE4_REQUESTERS:
            return None, (f"purpose 4 is requested by {C.PURPOSE4_REQUESTERS} only "
                          "(the DV Lead owns run-scope decisions); route the request through the DV Lead"), scope
        args += ["--tier", "full"]
    if p != 3:
        if isinstance(seeds, list):
            args += ["--seed-list", ",".join(str(s) for s in seeds)]
        elif p != 4:
            args += ["--seeds", str(seed_count)]
        if not req["coverage"]:
            args.append("--no-coverage")
        if req["waves"] and p in (1, 2):
            args.append("--waves")
        if req.get("group") and tier == "targeted":
            args += ["--group", str(req["group"])]
    # Instrumentation trials (purpose 2 only): a purpose-4 measurement never changes the flag set.
    if req.get("build_vcs_args"):
        if p != 2:
            return None, "build_vcs_args (instrumentation trial) is allowed under purpose 2 only", scope
        for x in req["build_vcs_args"]:
            args += ["--build-vcs-arg", x]
        scope["build_vcs_args"] = req["build_vcs_args"]
    if req.get("dump_exclusions") and p != 3:
        args.append("--dump-exclusions")
        scope["dump_exclusions"] = True
    return args, None, scope


def serve_one(path: Path, testlist: dict[str, Any], dry_run: bool, extra_args: list[str] | None = None) -> Path:
    name = path.stem
    C.RUNNING_DIR.mkdir(parents=True, exist_ok=True)
    C.DONE_DIR.mkdir(parents=True, exist_ok=True)
    result_dir = C.RESULTS_DIR / name
    result_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = result_dir / C.RESULTS_MANIFEST
    raw = U.load_yaml(path)
    req, err = validate(raw, path.name)
    record: dict[str, Any] = {"request": name, "request_file": str(path), "received_utc": U.now_utc(),
                              "request_echo": raw}
    if err:
        record.update(scope_decision="refused", refusal_reason=f"invalid request: {err}", status="done")
        if not dry_run:
            U.dump_yaml(record, manifest_path)
            shutil.move(str(path), str(C.DONE_DIR / path.name))
        U.log(f"{name}: REFUSED ({err})")
        return manifest_path
    args, refusal, scope = scope_for(req, testlist)
    record.update(requester=req["requester"], purpose=req["purpose"], purpose_text=C.PURPOSES[req["purpose"]],
                  scope=scope, notes=req["notes"])
    if refusal:
        record.update(scope_decision="refused", refusal_reason=refusal, status="done")
        if not dry_run:
            U.dump_yaml(record, manifest_path)
            shutil.move(str(path), str(C.DONE_DIR / path.name))
        U.log(f"{name}: REFUSED ({refusal})")
        return manifest_path
    outdir = C.OUT_DIR / f"regress_req_{name}"
    argv = [sys.executable, str(C.FLOW_DIR / "gen_regress.py"), *args, *(extra_args or []), "--outdir", str(outdir),
            "--force", "--request", name, "--requester", req["requester"], "--purpose", str(req["purpose"])]
    record.update(scope_decision="accepted", regress_cmd=" ".join(argv), regress_outdir=str(outdir),
                  operator_extra_args=list(extra_args or []))
    if dry_run:
        U.log(f"{name}: ACCEPT -> {' '.join(args)}")
        return manifest_path
    running = C.RUNNING_DIR / path.name
    shutil.move(str(path), str(running))
    record["status"] = "running"
    U.dump_yaml(record, manifest_path)
    U.log(f"{name}: running {' '.join(args)}")
    rc, wall, timed_out = U.run_bounded(argv, cwd=C.REPO_ROOT, log_path=result_dir / "serve.log", timeout_s=6 * 3600)
    reg_path = outdir / "manifest.yaml"
    reg = U.load_yaml(reg_path) if reg_path.is_file() else {}
    record.update(status="done", regress_rc=rc, regress_timed_out=timed_out, serve_wall_s=round(wall, 1),
                  regress_manifest=str(reg_path), build_config=reg.get("build_config"),
                  builds=reg.get("builds"), summary=reg.get("summary"), lsf_cost=reg.get("lsf_cost"),
                  coverage=reg.get("coverage"), finished_utc=U.now_utc(),
                  runs=[{k: r.get(k) for k in ("test", "seed", "verdict", "reason", "sim_log", "run_log",
                                                "run_cmd", "vdb", "cm_name", "waves", "wall_s", "owner",
                                                "fcov_check")}
                        | {"lsf_job_id": (r.get("lsf") or {}).get("job_id")} for r in reg.get("runs", [])])
    U.dump_yaml(record, manifest_path)
    shutil.move(str(running), str(C.DONE_DIR / path.name))
    s = record.get("summary") or {}
    U.log(f"{name}: done rc={rc} pass={s.get('pass')} fail={s.get('fail')} -> {manifest_path}")
    return manifest_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--once", action="store_true", help="serve every pending request, then exit (default)")
    mode.add_argument("--watch", action="store_true", help="poll the queue until --duration elapses")
    mode.add_argument("--dry-run", action="store_true", help="print scope decisions without running")
    ap.add_argument("--interval", type=int, default=30)
    ap.add_argument("--duration", type=int, default=3600)
    ap.add_argument("--testlist", type=Path, default=C.TESTLIST_YAML)
    ap.add_argument("--extra-arg", action="append", default=[],
                    help="gen_regress.py argument the runtime operator adds to every request served in this call "
                         "(recorded in the manifest as operator_extra_args); for knobs a request asked for in notes")
    a = ap.parse_args()
    if not a.dry_run:
        U.require_env("vcs", "urg", "bsub")
    testlist = U.load_testlist(a.testlist)
    deadline = time.time() + a.duration
    served = 0
    while True:
        for p in pending_requests():
            serve_one(p, testlist, a.dry_run, a.extra_arg)
            served += 1
        if not a.watch or time.time() >= deadline:
            break
        time.sleep(a.interval)
    U.log(f"served {served} request(s); pending now: {len(pending_requests())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
