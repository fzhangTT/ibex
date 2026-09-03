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
import concurrent.futures as cf
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml
from typing import Any

import gen_flow_const as C
import gen_flow_util as U
import gen_mirror as M

TIER_WORDS = {"smoke": "smoke", "targeted": "targeted", "full": "full", "all": "full", "check": "check"}


def parse_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ("yes", "y", "true", "1", "on")


def pending_requests(only: list[str] | None = None) -> list[Path]:
    C.REQUESTS_DIR.mkdir(parents=True, exist_ok=True)
    files = [p for p in C.REQUESTS_DIR.iterdir() if p.is_file() and C.REQUEST_NAME_RE.match(p.name)
             and (not only or p.stem in only)]
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
    elcheck = req.get("elcheck")
    if elcheck is not None:
        if purpose != 2:
            return None, "elcheck (report-only exclusion check) is a purpose-2 request"
        if not isinstance(elcheck, dict) or set(elcheck) - set(C.ELCHECK_KEYS) or not all(k in elcheck for k in C.ELCHECK_REQUIRED_KEYS):
            return None, f"elcheck must be a mapping with keys {C.ELCHECK_REQUIRED_KEYS} (optional: {C.ELCHECK_OPTIONAL_KEYS})"
        for k in C.ELCHECK_REQUIRED_KEYS:
            if not Path(elcheck[k]).is_file() and not Path(elcheck[k]).is_dir():
                return None, f"elcheck.{k} {elcheck[k]!r} does not exist"
    tests = req["tests"]
    if isinstance(tests, str):
        tests = [t.strip() for t in tests.split(",") if t.strip()]
    if not isinstance(tests, list) or (not tests and elcheck is None):
        return None, "tests must be a non-empty list, a comma list, or a tier word (empty only with elcheck)"
    seeds = req["seeds"]
    if isinstance(seeds, str) and seeds.strip().isdigit():
        seeds = int(seeds)
    if isinstance(seeds, str):
        seeds = [U.parse_seed(s.strip()) for s in seeds.split(",") if s.strip()]
    if not isinstance(seeds, (int, list)):
        return None, "seeds must be a count or an explicit list"
    if elcheck is not None and (tests or seeds):
        return None, "elcheck runs no simulation: tests and seeds must be empty"
    if elcheck is not None and req.get("build_vcs_args"):
        return None, "elcheck compiles nothing: build_vcs_args is not accepted with it"
    norm = dict(req)
    bva = req.get("build_vcs_args") or []
    if isinstance(bva, str):
        bva = [bva]
    if not isinstance(bva, list) or not all(isinstance(x, str) for x in bva):
        return None, "build_vcs_args must be a list of strings"
    source = req.get("source", C.SOURCE_MODE_HEAD)
    if source not in C.SOURCE_MODES:
        return None, f"source must be one of {C.SOURCE_MODES}"
    if purpose == 4 and source != C.SOURCE_MODE_HEAD:
        return None, "purpose 4 always runs from committed HEAD (source: head)"
    norm.update(source=source)
    norm.update(purpose=purpose, tests=tests, seeds=seeds, coverage=parse_bool(req["coverage"]),
                waves=parse_bool(req.get("waves", False)), group=req.get("group"),
                component=req.get("component"), notes=str(req.get("notes") or ""),
                build_vcs_args=bva, dump_exclusions=parse_bool(req.get("dump_exclusions", False)),
                elcheck=elcheck)
    return norm, None


def scope_for(req: dict[str, Any], testlist: dict[str, Any]) -> tuple[list[str] | None, str | None, dict[str, Any]]:
    """Return (gen_regress args, refusal reason, scope record). Only purpose 4 runs everything."""
    p = req["purpose"]
    tests = req["tests"]
    seeds = req["seeds"]
    tier = TIER_WORDS.get(tests[0].lower()) if len(tests) == 1 and tests[0].lower() in TIER_WORDS else None
    known = {t["name"] for t in testlist["tests"]}
    explicit = [] if tier else tests
    if req.get("elcheck") is not None:
        if not req.get("component"):
            return None, "purpose 2 needs a component (elcheck: name the exclusion file's component)", \
                {"purpose": p, "kind": "elcheck"}
        return [], None, {"purpose": p, "kind": "elcheck", "component": req["component"],
                          "vdb": req["elcheck"]["vdb"], "elfile": req["elcheck"]["elfile"], "tests": [], "seed_count": 0}
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


class ElcheckError(Exception):
    """An elcheck that cannot run to completion; recorded in the manifest, never a die of the server."""


def scopes_for_vdb(vdb: Path, build_name: str | None) -> tuple[list[str], list[str], str]:
    """The gated and informational scopes of the build that produced a vdb: read from the build manifest
    of the regression the vdb belongs to (walk up to its manifest.yaml), never re-typed."""
    for parent in vdb.resolve().parents:
        man = parent / "manifest.yaml"
        if man.is_file():
            reg = U.load_yaml(man)
            builds = reg.get("builds") or {}
            name = build_name or (next(iter(builds)) if len(builds) == 1 else None)
            if name not in builds:
                raise ElcheckError(f"regression {man} has builds {sorted(builds)}; name one with elcheck.build")
            bman = U.load_yaml(Path(builds[name]["manifest"]))
            return list(bman.get("cov_scopes") or []), list(bman.get("info_scopes") or []), str(builds[name]["manifest"])
    raise ElcheckError(f"no regression manifest.yaml above {vdb}")


def merge_warnings(merge_log: str) -> list[str]:
    p = Path(merge_log)
    return [l.rstrip() for l in p.read_text(encoding="utf-8", errors="replace").splitlines()
            if l.startswith("Warning-[") or l.startswith("Error-[")] if p.is_file() else []


def run_elcheck(req: dict[str, Any], outdir: Path) -> dict[str, Any]:
    """Report-only strict load of an exclusion file against an existing vdb through the flow's URG wrapper:
    one merge with the file (-excl_strict, full_exclusions dump) and one without, same scopes."""
    vdb = Path(req["elcheck"]["vdb"]).resolve()
    elfile = Path(req["elcheck"]["elfile"]).resolve()
    dut, info, bman = scopes_for_vdb(vdb, req["elcheck"].get("build"))

    def merge_cli(cov_dir: Path, with_file: bool) -> dict[str, Any]:
        argv = [sys.executable, str(C.FLOW_DIR / "gen_cov_report.py"), "merge", "--cov-dir", str(cov_dir), "--vdb", str(vdb)]
        argv += [a for s in dut for a in ("--dut-scope", s)] + [a for s in info for a in ("--info-scope", s)]
        if with_file:
            argv += ["--elfile", str(elfile), "--dump-exclusions"]
        rc, wall, timed_out = U.run_bounded(argv, cwd=C.REPO_ROOT, log_path=cov_dir.parent / f"{cov_dir.name}.log",
                                            timeout_s=C.ELCHECK_TIMEOUT_S)
        res_path = cov_dir / "coverage.yaml"
        if timed_out or not res_path.is_file():
            raise ElcheckError(f"merge into {cov_dir} did not produce coverage.yaml (rc={rc}, timed_out={timed_out}); "
                               f"see {cov_dir.parent / (cov_dir.name + '.log')}")
        res = U.load_yaml(res_path)
        res["merge_rc"] = rc
        res["merge_warnings"] = merge_warnings(res["merge_log"])
        return res

    outdir.mkdir(parents=True, exist_ok=True)
    with_el = merge_cli(outdir / "cov_elcheck", True)
    without = merge_cli(outdir / "cov_plain", False)
    # Per-metric excluded counts: the denominators the exclusion file removed from the gated rows.
    excluded: dict[str, Any] = {}
    gw, gwo = with_el.get("gate_row") or {}, without.get("gate_row") or {}
    if "ratios" in gw and "ratios" in gwo:
        for metric, r_with in gw["ratios"].items():
            r_wo = gwo["ratios"].get(metric)
            if r_wo and "/" in r_with and "/" in r_wo:
                excluded[metric] = int(r_wo.split("/")[1]) - int(r_with.split("/")[1])
    return {"kind": "elcheck", "vdb": str(vdb), "elfile": str(elfile), "elfile_sha256": U.sha256_file(elfile),
            "scopes_from": bman, "dut_scopes": dut, "info_scopes": info, "with_elfile": with_el,
            "without_elfile": without, "excluded_counts_gate_row": excluded,
            "verdict": "ok" if with_el["status"] == "ok" and not with_el["exclusion_violations"] else "failed"}


def serve_one(path: Path, testlist: dict[str, Any], dry_run: bool, extra_args: list[str] | None = None,
              server_sync: dict[str, Any] | None = None, refusal_override: str | None = None) -> Path:
    name = path.stem
    C.RUNNING_DIR.mkdir(parents=True, exist_ok=True)
    C.DONE_DIR.mkdir(parents=True, exist_ok=True)
    result_dir = C.RESULTS_DIR / name
    result_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = result_dir / C.RESULTS_MANIFEST
    try:
        raw = U.load_yaml(path)
        req, err = validate(raw, path.name)
    except yaml.YAMLError as e:
        # A file that does not parse is refused in writing like any other invalid request, never a crash.
        raw, req, err = path.read_text(encoding="utf-8", errors="replace"), None, f"YAML parse error: {e}"
    record: dict[str, Any] = {"request": name, "request_file": str(path), "received_utc": U.now_utc(),
                              "request_echo": raw, "out_root": str(C.OUT_DIR)}
    if err:
        record.update(scope_decision="refused", refusal_reason=f"invalid request: {err}", status="done")
        if not dry_run:
            U.dump_yaml(record, manifest_path)
            shutil.move(str(path), str(C.DONE_DIR / path.name))
        U.log(f"{name}: REFUSED ({err})")
        return manifest_path
    args, refusal, scope = scope_for(req, testlist)
    refusal = refusal or refusal_override   # a pass-level refusal (the measured-dispatch gate) is recorded like a scope refusal
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
    if scope.get("kind") == "elcheck":
        record.update(scope_decision="accepted", status="running", elcheck_outdir=str(outdir))
        if dry_run:
            U.log(f"{name}: ACCEPT -> elcheck {scope['elfile']} against {scope['vdb']}")
            return manifest_path
        running = C.RUNNING_DIR / path.name
        shutil.move(str(path), str(running))
        U.dump_yaml(record, manifest_path)
        t0 = time.time()
        outdir.mkdir(parents=True, exist_ok=True)
        try:
            record["elcheck"] = run_elcheck(req, outdir)
        except (ElcheckError, Exception, SystemExit) as e:  # noqa: B014 - a die anywhere below must still be recorded
            record["elcheck"] = {"kind": "elcheck", "verdict": "failed", "error": f"{type(e).__name__}: {e}"}
        record.update(status="done", serve_wall_s=round(time.time() - t0, 1), finished_utc=U.now_utc())
        U.dump_yaml(record, manifest_path)
        shutil.move(str(running), str(C.DONE_DIR / path.name))
        U.log(f"{name}: elcheck {record['elcheck']['verdict']} -> {manifest_path}")
        return manifest_path
    argv = [sys.executable, str(C.FLOW_DIR / "gen_regress.py"), *args, *(extra_args or []), "--outdir", str(outdir),
            "--force", "--request", name, "--requester", req["requester"], "--purpose", str(req["purpose"]),
            "--source", req.get("source", C.SOURCE_MODE_HEAD)]
    record.update(scope_decision="accepted", regress_cmd=" ".join(argv), regress_outdir=str(outdir),
                  operator_extra_args=list(extra_args or []), server_mirror_sync=server_sync)
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
                                                "run_cmd", "vdb", "cm_name", "waves", "wall_s", "owner", "slow_total",
                                                "fcov_check")}
                        | {"lsf_job_id": (r.get("lsf") or {}).get("job_id")} for r in reg.get("runs", [])])
    U.dump_yaml(record, manifest_path)
    shutil.move(str(running), str(C.DONE_DIR / path.name))
    s = record.get("summary") or {}
    U.log(f"{name}: done rc={rc} pass={s.get('pass')} fail={s.get('fail')} -> {manifest_path}")
    return manifest_path


def request_source(path: Path) -> str:
    try:
        raw = U.load_yaml(path)
        return str(raw.get("source", C.SOURCE_MODE_HEAD)) if isinstance(raw, dict) else C.SOURCE_MODE_HEAD
    except (yaml.YAMLError, TypeError, ValueError):
        return C.SOURCE_MODE_HEAD


def request_purpose(path: Path) -> int | None:
    try:
        raw = U.load_yaml(path)
        return int(raw.get("purpose")) if isinstance(raw, dict) else None
    except (yaml.YAMLError, TypeError, ValueError):
        return None


def resolve_commit(ref: str) -> str:
    """Full sha of a commit this clone has; an unknown ref stops the server (the canary must name a real commit)."""
    r = subprocess.run(["git", "-C", str(C.REPO_ROOT), "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        U.die(f"--canary-sha {ref!r} is not a commit of this clone")
    return r.stdout.strip()


def build_input_delta(sha_a: str, sha_b: str) -> dict[str, Any]:
    """The hold's decision between two commits over the mirrored subset (M.git_pathspecs, the set a head tree is built
    from): `delta` is the deciding subset (the build inputs that differ, by name), `noninputs_changed` the differing
    files the classifier let through, `delta_full` the whole mirrored diff --stat (transparency only); a rename counts
    under both names; a failed git command refuses with the error as the delta."""
    base = ["git", "-C", str(C.REPO_ROOT), "diff"]
    ns = subprocess.run([*base, "--name-status", sha_a, sha_b, "--", *M.git_pathspecs()], capture_output=True, text=True)
    st = subprocess.run([*base, "--stat=200", sha_a, sha_b, "--", *M.git_pathspecs()], capture_output=True, text=True)
    rec: dict[str, Any] = {"delta": [], "delta_full": st.stdout.strip() if st.returncode == 0 else f"git diff failed: {st.stderr.strip()[:200]}",
                           "noninputs_changed": [], "noninput_list_sha256": U.noninput_list_sha256(), "decision": C.CANARY_ACCEPTED}
    if ns.returncode != 0:
        rec.update(delta=[f"git diff failed: {ns.stderr.strip()[:200]}"], decision=C.CANARY_REFUSED_DELTA)
        return rec
    names = [n for row in ns.stdout.splitlines() if row.strip() for n in row.split("\t")[1:]]
    inputs, noninputs = U.classify_delta(names)
    rec.update(delta=inputs, noninputs_changed=noninputs, decision=C.CANARY_REFUSED_DELTA if inputs else C.CANARY_ACCEPTED)
    return rec


def write_batch_record(rec: dict[str, Any]) -> Path:
    """One file per head-mode batch decision (accepted or refused: both shas, the pathspecs, the delta, the requests)."""
    C.BATCHES_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"{rec['utc'].replace('-', '').replace(':', '')}_{rec['pinned_sha'][:12]}"
    p = C.BATCHES_DIR / f"{stem}.yaml"
    n = 1
    while p.exists():   # two decisions within one second keep two records
        n += 1
        p = C.BATCHES_DIR / f"{stem}_{n}.yaml"
    U.dump_yaml(rec, p)
    return p


def pinned_testlist(head_tree: Path) -> dict[str, Any]:
    """The pinned tree's committed testlist, validated by a process bound to that tree."""
    env = dict(os.environ, **{C.ENV_SOURCE_ROOT: str(head_tree), C.ENV_MIRROR_ROOT: str(head_tree)})
    r = subprocess.run([sys.executable, str(C.FLOW_DIR / "gen_flow_util.py"), "--dump-testlist",
                        str(head_tree / "dv" / "auto_dv" / "flow" / "gen_testlist.yaml")], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        U.die(f"the pinned tree's testlist does not validate: {r.stderr.strip()[-300:]}")
    import json
    return json.loads(r.stdout)


def request_is_elcheck(path: Path) -> bool:
    """A report-only exclusion check builds nothing, so it stays outside the canary hold."""
    try:
        raw = U.load_yaml(path)
        return isinstance(raw, dict) and raw.get("elcheck") is not None   # the same test validate() applies
    except (yaml.YAMLError, TypeError, ValueError):
        return False


def partition_pending(pending: list[Path]) -> tuple[list[Path], list[Path], list[Path], list[Path]]:
    """pinned = head-mode requests that build (any purpose, no real elcheck), then its purpose-1 and purpose-2..4
    halves, then the rest (worktree requests, elchecks)."""
    pinned = [p for p in pending if request_source(p) == C.SOURCE_MODE_HEAD and not request_is_elcheck(p)]
    p1 = [p for p in pinned if request_purpose(p) == 1]
    return pinned, p1, [p for p in pinned if p not in p1], [p for p in pending if p not in pinned]


def measured_gate(p234: list[Path], canary_build: Path | None, pinned_sha: str | None) -> tuple[list[Path], str | None, dict[str, Any]]:
    """Purpose-4 requests of a batch (measured rounds) dispatch only on a head-mode canary build of the batch's pinned
    commit that declares a covergroup (LOG-046a): the purpose-4 subset, the refusal text (None when allowed, or when
    the batch has none) and the record with the facts read."""
    p4 = [p for p in p234 if request_purpose(p) == 4]
    if not p4:
        return [], None, {}
    man, mp = U.load_build_manifest(canary_build) if canary_build else (None, Path("(no --canary-build)"))
    refusal = U.measured_dispatch_refusal(man, str(mp), pinned_sha)
    return p4, refusal, {"canary_build": str(canary_build) if canary_build else None, "pinned_sha": pinned_sha,
                         "facts": U.canary_build_facts(canary_build),
                         "decision": C.CANARY_REFUSED_NO_COVERGROUPS if refusal else C.CANARY_ACCEPTED, "refusal": refusal}


def self_test() -> int:
    """measured_gate on fabricated requests and canary build manifests (no queue, no simulation)."""
    import tempfile
    ok = True
    d = Path(tempfile.mkdtemp(prefix="gen_serve_selftest_", dir=C.selftest_tmp()))
    r4, r2 = d / "req4.yaml", d / "req2.yaml"
    U.dump_yaml({"purpose": 4, "requester": "dv-lead"}, r4)
    U.dump_yaml({"purpose": 2, "requester": "tb-infra"}, r2)
    b = d / "canary_build"; b.mkdir()
    pin = "e" * 40
    head = {"build": "gen_tb", "source_mode": C.SOURCE_MODE_HEAD, "head_sha": pin, C.COVERGROUPS_DECLARED_KEY: True, "covergroup_files": ["x.sv"]}
    U.dump_yaml(dict(head, **{C.COVERGROUPS_DECLARED_KEY: False, "covergroup_files": []}), b / C.BUILD_MANIFEST)
    p4, refusal, gate = measured_gate([r2, r4], b, pin)
    cond = p4 == [r4] and refusal is not None and f"{C.COVERGROUPS_DECLARED_KEY}=False" in refusal and gate["decision"] == C.CANARY_REFUSED_NO_COVERGROUPS and gate["facts"]["head_sha"] == pin
    ok &= cond; print("SELF-TEST", "ok " if cond else "BAD", f"canary build without a covergroup: the purpose-4 request is refused, the purpose-2 one is not in the gate, the facts are recorded: {gate['decision']}")
    p4, refusal, gate = measured_gate([r2, r4], None, pin)
    cond = p4 == [r4] and refusal is not None and "(no --canary-build)" in refusal and gate["canary_build"] is None and gate["facts"] is None
    ok &= cond; print("SELF-TEST", "ok " if cond else "BAD", "no --canary-build: the purpose-4 request is refused naming the missing argument")
    U.dump_yaml(dict(head, source_mode=C.SOURCE_MODE_WORKTREE), b / C.BUILD_MANIFEST)
    _, r_wt, _ = measured_gate([r4], b, pin)
    U.dump_yaml(dict(head, head_sha="f" * 40), b / C.BUILD_MANIFEST)
    _, r_other, _ = measured_gate([r4], b, pin)
    cond = r_wt is not None and "worktree-mode build" in r_wt and r_other is not None and "not of the pinned" in r_other
    ok &= cond; print("SELF-TEST", "ok " if cond else "BAD", "a worktree canary build and a head build of another sha refuse the purpose-4 request (CM46-M-1)")
    U.dump_yaml(head, b / C.BUILD_MANIFEST)
    p4, refusal, gate = measured_gate([r2, r4], b, pin)
    cond = p4 == [r4] and refusal is None and gate["decision"] == C.CANARY_ACCEPTED
    ok &= cond; print("SELF-TEST", "ok " if cond else "BAD", "a head-mode canary build of the pinned sha with a covergroup: the purpose-4 request dispatches (accepted)")
    cond = measured_gate([r2], None, pin) == ([], None, {})
    ok &= cond; print("SELF-TEST", "ok " if cond else "BAD", "a batch without a purpose-4 request needs no canary build")
    U.remove_selftest_tree(d)
    # Build-input gate (dv/auto_dv/docs/gen_build_input_gate_rule.md) cases 12 and 14.
    same = build_input_delta("HEAD", "HEAD")
    cond = set(same) == {"delta", "delta_full", "noninputs_changed", "noninput_list_sha256", "decision"} and same["delta"] == [] \
        and same["noninputs_changed"] == [] and same["decision"] == C.CANARY_ACCEPTED and same["noninput_list_sha256"] == U.noninput_list_sha256()
    ok &= cond; print("SELF-TEST", "ok " if cond else "BAD", f"build-input gate case 12: build_input_delta returns exactly the five fields; HEAD..HEAD accepts: {same['decision']}")
    history = (("0a07536d84b7236e423963a46b92ce6a016028aa", "1dbb8bff28bf2acc7a58e341d257b9e4fae86053", [], ["dv/auto_dv/docs/gen_intervention_log.md"], C.CANARY_ACCEPTED),
               ("1dbb8bff28bf2acc7a58e341d257b9e4fae86053", "902da1f693d84779684d0e4ea6f3f483a8ed960f", ["dv/auto_dv/docs/gen_fcov_plan.md", "dv/auto_dv/docs/gen_feature_list.md", "dv/auto_dv/docs/gen_test_plan.md"],
                ["dv/auto_dv/docs/gen_bug_log.md", "dv/auto_dv/tools/gen_covergroup_set.py"], C.CANARY_REFUSED_DELTA))
    for a, b, want_delta, want_non, want_decision in history:
        present = all(subprocess.run(["git", "-C", str(C.REPO_ROOT), "cat-file", "-e", f"{x}^{{commit}}"], capture_output=True).returncode == 0 for x in (a, b))
        if not present:
            print(f"SELF-TEST skip build-input gate case 14 {a[:7]}..{b[:7]}: a sha is absent from this clone")
            continue
        got = build_input_delta(a, b)
        cond = got["delta"] == want_delta and got["noninputs_changed"] == want_non and got["decision"] == want_decision and got["delta_full"].strip() != ""
        ok &= cond; print("SELF-TEST", "ok " if cond else "BAD", f"build-input gate case 14 {a[:7]}..{b[:7]}: {got['decision']} delta={got['delta']} noninputs={got['noninputs_changed']}")
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 2


def serve_pass(pending: list[Path], testlist: dict[str, Any], dry_run: bool, extra_args: list[str],
               max_concurrent: int, canary_sha: str | None = None, canary_build: Path | None = None) -> int:
    """One pass over the queue. Every head-mode request that builds (any purpose; a worktree request is served
    alone, an elcheck builds nothing) is pinned to one commit behind the canary hold: the purpose-1 requests
    run concurrently, purposes 2 to 4 follow one at a time on the same pinned tree (a measured round on an
    unvouched HEAD is exactly what the hold exists for); everything else is served in file order."""
    pinned, p1, p234, rest = partition_pending(pending)
    if pinned and not dry_run:
        batch_sha = M.head_sha()
        rec: dict[str, Any] = {"utc": U.now_utc(), "requests": [p.stem for p in pinned], "pinned_sha": batch_sha,
                               "canary_sha": canary_sha, "delta_pathspecs": M.git_pathspecs(), "delta": [], "delta_full": "",
                               "noninputs_changed": [], "noninput_list_sha256": U.noninput_list_sha256(), "decision": None}
        # The hold is decided before any sync, so a held batch costs one record per pass and never a re-sync.
        if canary_sha is None:
            rec["decision"] = C.CANARY_REFUSED_MISSING
        elif canary_sha == batch_sha:
            rec["decision"] = C.CANARY_ACCEPTED
        else:
            rec.update(build_input_delta(canary_sha, batch_sha))
        rec_path = write_batch_record(rec)
        if rec["decision"] != C.CANARY_ACCEPTED:
            U.log(f"REFUSING the head-mode batch this pass ({rec['decision']}): canary {str(canary_sha)[:12]} vs HEAD "
                  f"{batch_sha[:12]}; {len(pinned)} request(s) stay pending; record {rec_path}"
                  + (f"\nbuild inputs changed: {rec['delta']}" if rec["delta"] else "")
                  + (f"\nnon-inputs let through: {rec['noninputs_changed']}" if rec["noninputs_changed"] else ""))
            for p in rest:
                serve_one(p, testlist, dry_run, extra_args)
            return len(rest)
        if rec["noninputs_changed"]:
            U.log(f"canary {str(canary_sha)[:12]} vs HEAD {batch_sha[:12]} differ in non-inputs only, batch accepted "
                  f"(list {rec['noninput_list_sha256'][:12]}): {rec['noninputs_changed']}")
        # One sync for the whole batch: concurrent regressions must not race on the mirror tree.
        rc, wall, timed_out = U.run_bounded([sys.executable, str(C.FLOW_DIR / "gen_mirror.py"), "--sync", "--spike", "--source", C.SOURCE_MODE_HEAD,
                                             "--head-sha", batch_sha],
                                            cwd=C.REPO_ROOT, log_path=C.WORK_DIR / "serve_mirror_sync.log",
                                            timeout_s=C.MIRROR_SYNC_TIMEOUT_S)
        head_tree = M.head_mirror_root(batch_sha)
        synced = M.load_manifest(head_tree) or {}
        sync = {"rc": rc, "timed_out": timed_out, "wall_s": round(wall, 1), "spike": True, "utc": U.now_utc(),
                "source": synced.get("source"), "head_sha": synced.get("head_sha"), "head_tree": str(head_tree),
                "pinned_sha": batch_sha, "canary_sha": canary_sha, "canary_decision": rec["decision"],
                "canary_to_batch_build_input_delta": rec["delta"], "canary_to_batch_noninputs_changed": rec["noninputs_changed"],
                "batch": [p.stem for p in pinned], "batch_record": str(rec_path)}
        p4, p4_refusal, gate = measured_gate(p234, canary_build, batch_sha)
        if p4:
            sync["measured_dispatch"] = gate
            if p4_refusal:
                U.log(f"REFUSING {len(p4)} purpose-4 request(s) ({C.CANARY_REFUSED_NO_COVERGROUPS}): {p4_refusal}")
        manifests: list[Path] = []
        if rc == 0 and not timed_out and sync.get("head_sha") == batch_sha:
            U.log(f"batch mirror sync rc={rc} in {wall:.0f}s for {len(pinned)} head-mode request(s) ({len(p1)} purpose-1), pinned to {batch_sha[:12]}")
            # Scope decisions for the batch come from the pinned tree's committed testlist, validated by a process
            # bound to that tree (not by this server, whose source root is the clone).
            head_testlist = pinned_testlist(head_tree)
            batch_lease = M.lease_head_tree(head_tree, "batch_" + "_".join(p.stem for p in pinned)[:60])
            # Every regression of the batch is pinned to the commit the batch was synced from.
            batch_args = list(extra_args) + ["--no-sync-mirror", "--head-sha", str(sync["head_sha"])]
            try:
                with cf.ThreadPoolExecutor(max_workers=max(1, max_concurrent)) as pool:
                    manifests = list(pool.map(lambda p: serve_one(p, head_testlist, dry_run, batch_args, sync), p1))
                # Purposes 2 to 4 (trials, repros, measured rounds): one at a time on the same pinned tree.
                p4_args = batch_args + (["--canary-build", str(canary_build)] if canary_build else [])
                manifests += [serve_one(p, head_testlist, dry_run, p4_args if p in p4 else batch_args, sync, p4_refusal if p in p4 else None) for p in p234]
            finally:
                M.release_lease(batch_lease)
        else:
            # Without one good shared sync the batch must not fan out: each regression syncs the PINNED commit for
            # itself, in turn, so the record's pinned_sha stays true (HEAD may have moved meanwhile).
            sync["batch_serialized"] = "batch mirror sync failed; requests served one at a time, each syncing the pinned commit itself"
            U.log(f"WARNING: batch mirror sync rc={rc} timed_out={timed_out}; serializing {len(pinned)} head-mode request(s) pinned to {batch_sha[:12]}")
            pin_args = list(extra_args) + ["--head-sha", batch_sha]
            p4_pin_args = pin_args + (["--canary-build", str(canary_build)] if canary_build else [])
            manifests = [serve_one(p, testlist, dry_run, p4_pin_args if p in p4 else pin_args, sync, p4_refusal if p in p4 else None) for p in [*p1, *p234]]
        rec.update(sync=sync, manifests=[str(m) for m in manifests], completed_utc=U.now_utc())
        U.dump_yaml(rec, rec_path)
    elif pinned:
        # Dry run: scope decisions only, no sync and no hold.
        for p in pinned:
            serve_one(p, testlist, dry_run, extra_args)
    for p in rest:
        serve_one(p, testlist, dry_run, extra_args)
    return len(pending)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--once", action="store_true", help="serve every pending request, then exit (default)")
    mode.add_argument("--watch", action="store_true", help="poll the queue until --duration elapses")
    mode.add_argument("--dry-run", action="store_true", help="print scope decisions without running")
    ap.add_argument("--interval", type=int, default=30)
    ap.add_argument("--duration", type=int, default=3600)
    ap.add_argument("--testlist", type=Path, default=C.TESTLIST_YAML)
    ap.add_argument("--only", action="append", default=[], help="serve only the named pending request(s)")
    ap.add_argument("--canary-sha", default=None,
                    help="commit the gen_boot_zc canary passed on: required for every head-mode purpose-1 batch, which is "
                         "refused (and the refusal recorded under work/runtime/batches/) when it is absent or when a "
                         "mirrored file differs between that commit and HEAD")
    ap.add_argument("--canary-build", type=Path, default=None,
                    help="build dir (or build_manifest.yaml) of the canary regression: a purpose-4 request is refused "
                         "(refused_no_covergroups) unless it is a head-mode build of the batch's pinned commit recording covergroups_declared true (LOG-046a)")
    ap.add_argument("--max-concurrent", type=int, default=C.SERVE_MAX_CONCURRENT_P1,
                    help="independent purpose-1 requests served at once (ruling: purposes 2-4 stay serialized)")
    ap.add_argument("--extra-arg", action="append", default=[],
                    help="gen_regress.py argument the runtime operator adds to every request served in this call "
                         "(recorded in the manifest as operator_extra_args); for knobs a request asked for in notes")
    a = ap.parse_args()
    if a.canary_sha:
        a.canary_sha = resolve_commit(a.canary_sha)
    if not a.dry_run:
        U.require_env("vcs", "urg", "bsub")
    testlist = U.load_testlist(a.testlist)
    deadline = time.time() + a.duration
    served = 0
    while True:
        served += serve_pass(pending_requests(a.only), testlist, a.dry_run, a.extra_arg, a.max_concurrent, a.canary_sha, a.canary_build)
        if not a.watch or time.time() >= deadline:
            break
        time.sleep(a.interval)
    U.log(f"served {served} request(s); pending now: {len(pending_requests())}")
    return 0


if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv else main())
