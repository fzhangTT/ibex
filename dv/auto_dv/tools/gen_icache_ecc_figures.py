"""gen_icache_ecc_figures.py <landing root>: every landing-15 record figure re-derived from the RETAINED files, so no number in
the record is retyped from a run directory or from a review. Reads the retained excerpts' GEN_MISC summary line (kept
whole by this pass) and the retained mutant verdicts and excerpt headers. Prints JSON plus a markdown digest, and fails
loud on a field it cannot find or an arithmetic identity that does not hold."""
import json
import pathlib
import re
import sys
USAGE = "usage: gen_icache_ecc_figures.py <landing root>"


def _usage(msg=None):
    """A wrong call is answered, not crashed: the tools are read by reviewers who have not seen them before."""
    if msg:
        print(msg)
    print(USAGE)
    sys.exit(2)


if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
    _usage()


ROOT = pathlib.Path(sys.argv[1])
L = ROOT / "dv/auto_dv/evidence/gen_tdd_logs"
LK, MU = L / "lockstep", L / "mutations"

RUNS = ["ecc_data_freq", "ecc_data_freq_noprobe", "ecc_data_two", "ecc_both_freq", "ecc_data_rare",
        "ecc_tag_freq_probe", "ecc_tag_two", "green_h1_ecc_freq", "ut_isa_cov_zc", "lockstep_icache_en",
        "ecc_far_data_freq", "ecc_far_data_noprobe", "ecc_far_both_freq"]

MUT_ROOTS = ["DATAMISS_np", "DATAMISS_npf", "DATAWAY_np", "DATAWAY_npf", "RETSEQ_npf", "RETIDX_npf",
             "RED0", "DATAANN", "DATAMISS", "DATAWAY", "BITS", "ALIGN"]

DATA_RE = re.compile(
    r"data injections judged=(\d+) hit_way=(\d+) other_or_invalid_way=(\d+) \(other valid way (\d+)\) "
    r"unjudged=(\d+) \(ambiguous (\d+), pending at the end (\d+)\) missing=(\d+) other_way_pulses=(\d+) "
    r"held_pulses=(\d+) duplicate_copies visible=(\d+) masked=(\d+)")
AB_RE = re.compile(r"forms a/b both=(\d+) agree=(\d+) disagree=(\d+), b latency (\d+)\.\.(\d+)")
TAG_RE = re.compile(r"ecc injections judged=(\d+) qualified=(\d+) missing=(\d+)")
MINOR_RE = re.compile(r"alert_minor hits=(\d+) mismatches=(\d+)")
problems = []

# which retained run names belong to which root: one mutation proved on one program with the probe on or off
RUN_OF = {
    "DATAMISS_np": ("DATAMISS_catch_ecc_data_freq_noprobe", "DATAMISS_ablate_ecc_data_freq_noprobe"),
    "DATAMISS_npf": ("DATAMISS_catch_ecc_far_data_freq_noprobe", "DATAMISS_ablate_ecc_far_data_freq_noprobe"),
    "DATAWAY_np": ("DATAWAY_catch_ecc_data_freq_noprobe", "DATAWAY_ablate_ecc_data_freq_noprobe"),
    "DATAWAY_npf": ("DATAWAY_catch_ecc_far_data_freq_noprobe", "DATAWAY_ablate_ecc_far_data_freq_noprobe"),
    "RETSEQ_npf": ("RETSEQ_catch_ecc_far_data_freq_noprobe", "RETSEQ_ablate_ecc_far_data_freq_noprobe"),
    "RETIDX_npf": ("RETIDX_catch_ecc_far_data_freq_noprobe", "RETIDX_ablate_ecc_far_data_freq_noprobe"),
    "RED0": ("RED0_catch_ecc_data_freq", "RED0_ablate_ecc_data_freq"),
    "DATAANN": ("DATAANN_catch_ecc_data_freq", "DATAANN_ablate_ecc_data_freq"),
    "DATAMISS": ("DATAMISS_catch_ecc_data_freq", "DATAMISS_ablate_ecc_data_freq"),
    "DATAWAY": ("DATAWAY_catch_ecc_data_freq", "DATAWAY_ablate_ecc_data_freq"),
    "BITS": ("BITS_catch_ecc_tag_two", "BITS_ablate_ecc_tag_two"),
    "ALIGN": ("ALIGN_catch_ecc_far_data_freq", "ALIGN_ablate_ecc_far_data_freq"),
}


def misc_line(path):
    if not path.exists():
        problems.append("no retained excerpt: %s" % path.name)
        return None
    for l in path.read_text(errors="replace").splitlines():
        if "[GEN_MISC]" in l and l and not l.startswith("#"):
            return l
    problems.append("no GEN_MISC line in %s" % path.name)
    return None


def run_figures(name):
    p = LK / ("gen_fu_l16_%s_stdout_excerpt.log" % name)
    l = misc_line(p)
    if l is None:
        return None
    out = {"retained": p.name, "summary_chars": len(l)}
    m = MINOR_RE.search(l)
    if m:
        out["alert_minor_pulses"], out["alert_minor_mismatches"] = int(m.group(1)), int(m.group(2))
    m = TAG_RE.search(l)
    if m:
        out["tag_judged"], out["tag_qualified"], out["tag_missing"] = (int(m.group(i)) for i in (1, 2, 3))
    m = DATA_RE.search(l)
    if m:
        k = ["judged", "hit_way", "other_or_invalid_way", "other_valid_way", "unjudged", "ambiguous",
             "pending_at_end", "missing", "other_way_pulses", "held_pulses", "dup_visible", "dup_masked"]
        out.update(dict(zip(k, (int(x) for x in m.groups()))))
    else:
        if "data injections" in l:
            problems.append("%s: the data-injection fields did not parse" % name)
    m = AB_RE.search(l)
    if m:
        out.update({"ab_both": int(m.group(1)), "ab_agree": int(m.group(2)), "ab_disagree": int(m.group(3)),
                    "b_lat_min": int(m.group(4)), "b_lat_max": int(m.group(5))})
    elif "data injections" in l and out.get("judged"):
        problems.append("%s: the a/b fields did not parse" % name)
    # identities the record relies on. The field the log calls "judged" is the processed total: every announced
    # valid-way injection that reached a verdict decision, unjudged ones included. The decided population is
    # hit_way + other_or_invalid_way, which is what "reach" means for the measured-run form.
    if "judged" in out:
        tot = out["judged"]
        out["data_injections_total"] = tot
        decided = out["hit_way"] + out["other_or_invalid_way"]
        out["decided"] = decided
        noprobe = name.endswith("_noprobe")
        if decided + out["unjudged"] != tot:
            problems.append("%s: hit_way+other_or_invalid+unjudged != the processed total" % name)
        if noprobe and out["ambiguous"] + out["pending_at_end"] != out["unjudged"]:
            problems.append("%s: probe off, so ambiguous+pending should equal unjudged" % name)
        if not noprobe and out["unjudged"] != out["pending_at_end"]:
            problems.append("%s: probe on, so unjudged should equal the end-of-run pending count" % name)
        if out.get("ab_both", 0) > tot:
            problems.append("%s: a/b both exceeds the processed total" % name)
        if out.get("ab_agree", 0) + out.get("ab_disagree", 0) != out.get("ab_both", 0):
            problems.append("%s: agree+disagree != both" % name)
        if tot:
            out["reach_pct"] = round(100.0 * decided / tot, 1)
            if out["hit_way"] or out["unjudged"]:
                out["owed_seen_pct"] = None   # only meaningful against the probe-on run's hit_way, computed below
    return out


def mut_figures(rid):
    out = {"root": rid, "runs": {}}
    mid = rid.split("_")[0]
    for f in sorted(MU.glob("gen_fu_l16_%s_*_verdict.txt" % mid)):
        name = f.name[len("gen_fu_l16_"):-len("_verdict.txt")]
        if name not in RUN_OF.get(rid, ()):
            continue
        v = f.read_text(errors="replace")
        verdict = "FAIL" if re.search(r"^verdict:\s*FAIL", v, re.M) else ("PASS" if re.search(r"^verdict:\s*PASS", v, re.M) else "?")
        ex = MU / ("gen_fu_l16_%s_stdout_excerpt.log" % name)
        errs, kinds = None, {}
        if ex.exists():
            # The counts live in the excerpt's leading comment block, whose line order belongs to the retention
            # tool rather than to this reader. Scan the whole block and fail loud when the total is absent, instead
            # of reading one line and silently recording no count if it ever moves off it.
            head = "\n".join(l for l in ex.read_text(errors="replace").splitlines() if l.startswith("#"))
            m = re.search(r"counted by python: (\d+)", head)
            if m:
                errs = int(m.group(1))
            else:
                problems.append("%s %s: no python-counted error total in the excerpt's comment block" % (rid, name))
            for km, kv in re.findall(r'([A-Za-z0-9_.]+\(\d+\)) "[^"]*": (\d+)', head):
                kinds[km] = int(kv)
            if errs and not kinds:
                problems.append("%s %s: %d errors but no per-check-site split in the comment block" % (rid, name, errs))
        else:
            problems.append("%s %s: no retained excerpt" % (rid, name))
        out["runs"][name] = {"verdict": verdict, "uvm_errors": errs, "per_site": kinds}
    if not out["runs"]:
        problems.append("%s: no retained verdicts" % rid)
        return out
    catch = [r for n, r in out["runs"].items() if "_catch_" in n]
    ablate = [r for n, r in out["runs"].items() if "_ablate_" in n]
    out["caught"] = all(r["verdict"] == "FAIL" and (r["uvm_errors"] or 0) > 0 for r in catch) and bool(catch)
    out["ablation_clean"] = all(r["verdict"] == "PASS" and (r["uvm_errors"] or 0) == 0 for r in ablate) and bool(ablate)
    if not out["caught"]:
        problems.append("%s: a catch run did not fail with errors" % rid)
    if not out["ablation_clean"]:
        problems.append("%s: an ablation did not pass with zero errors" % rid)
    return out


res = {"runs": {r: run_figures(r) for r in RUNS}, "mutants": {m: mut_figures(m) for m in MUT_ROOTS}}

# the safety-relevant fraction: of the injections that actually owed a pulse (form (a)'s hit_way count on the
# probe-on run of the same program), how many did the measured-run form identify as owing one
PAIRS = {"ecc_data_freq_noprobe": "ecc_data_freq", "ecc_far_data_noprobe": "ecc_far_data_freq"}
for off, on in PAIRS.items():
    a, b = res["runs"].get(on), res["runs"].get(off)
    if a and b and "hit_way" in a and "hit_way" in b:
        b["owed_total_from_probe_on"] = a["hit_way"]
        b["owed_seen_pct"] = round(100.0 * b["hit_way"] / a["hit_way"], 1) if a["hit_way"] else None
        if b["decided"] != a.get("ab_both"):
            problems.append("%s: the population form (b) decided with the probe off (%d) differs from the a/b both count of %s (%s)"
                            % (off, b["decided"], on, a.get("ab_both")))
res["problems"] = problems

print(json.dumps(res, indent=1, sort_keys=True))
print("\n---- digest ----")
print("| run | judged | unjudged (amb, pend) | hit_way | other/invalid | missing | pulses | held | dup vis/masked | a/b both/agree/dis | b lat |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for r in RUNS:
    d = res["runs"][r]
    if not d or "judged" not in d:
        continue
    print("| %s | %d | %d (%d, %d) | %d | %d | %d | %s | %d | %d/%d | %s/%s/%s | %s..%s |" % (
        r, d["judged"], d["unjudged"], d["ambiguous"], d["pending_at_end"], d["hit_way"],
        d["other_or_invalid_way"], d["missing"], d.get("alert_minor_pulses", "-"), d["held_pulses"],
        d["dup_visible"], d["dup_masked"], d.get("ab_both", "-"), d.get("ab_agree", "-"),
        d.get("ab_disagree", "-"), d.get("b_lat_min", "-"), d.get("b_lat_max", "-")))
print("\n| mutant root | caught | ablation clean | catch errors | per check site |")
print("|---|---|---|---|---|")
for m in MUT_ROOTS:
    d = res["mutants"][m]
    for n, r in sorted(d.get("runs", {}).items()):
        if "_catch_" not in n:
            continue
        sites = ", ".join("%s=%d" % kv for kv in sorted(r["per_site"].items()))
        print("| %s (%s) | %s | %s | %s | %s |" % (m, n, d.get("caught"), d.get("ablation_clean"), r["uvm_errors"], sites))
print("\nproblems: %d" % len(problems))
for p in problems:
    print("  -", p)
sys.exit(1 if problems else 0)
