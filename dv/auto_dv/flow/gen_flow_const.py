#!/usr/bin/env python3
"""Single constants home of the generated regression flow (Python side).

Every path, plusarg name, log marker, LSF default and schema constant the flow scripts use is
defined here and imported; no script re-types a literal. The SV-side constants home is
dv/auto_dv/tb/gen_tb_pkg.sv; `--check` proves the two agree on the shared names.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# --- Repository anchors (everything resolves from the clone root) ---------------------------
FLOW_DIR = Path(__file__).resolve().parent
REPO_ROOT = FLOW_DIR.parents[2]
ENV_SH = REPO_ROOT / "ci" / "env.sh"
CONFIG_SCRIPT = REPO_ROOT / "util" / "ibex_config.py"
FCOV_CHECKER = REPO_ROOT / "ci" / "check_fcov_expectations.py"
TB_DIR = REPO_ROOT / "dv" / "auto_dv" / "tb"
TB_PKG_SV = TB_DIR / "gen_tb_pkg.sv"
FCOV_EXPECT_DIR = REPO_ROOT / "dv" / "auto_dv" / "fcov_expectations"
DOCS_DIR = REPO_ROOT / "dv" / "auto_dv" / "docs"
DASHBOARD_MD = DOCS_DIR / "gen_dashboard.md"
DASHBOARD_METRICS_MD = DOCS_DIR / "dashboard_metrics.md"

TESTLIST_YAML = FLOW_DIR / "gen_testlist.yaml"
CM_HIER_TEMPLATE = FLOW_DIR / "gen_cm_hier.cfg"
PLI_TAB = FLOW_DIR / "gen_pli.tab"
DUMP_TCL_TEMPLATE = FLOW_DIR / "gen_dump.tcl"

# --- Working tree of the runtime role (not committed) ----------------------------------------
WORK_DIR = REPO_ROOT / "dv" / "auto_dv" / "work" / "runtime"
SITE_YAML = WORK_DIR / "gen_site.yaml"
ENV_OUT_ROOT = "GEN_DV_OUT_ROOT"


def _out_root() -> Path:
    """Out-tree root: env var, else the site pointer file, else the clone's work tree.
    LSF jobs read and write out-trees, so on a site whose clone is on local disk this must
    point at shared storage (SIM_RECIPE Section 7)."""
    import os
    v = os.environ.get(ENV_OUT_ROOT)
    if v:
        return Path(v)
    if SITE_YAML.is_file():
        m = re.search(r"^out_root:\s*(\S+)", SITE_YAML.read_text(encoding="utf-8"), re.M)
        if m:
            return Path(m.group(1))
    return WORK_DIR / "out"


OUT_DIR = _out_root()
STAGED_ENV_SH = "env.sh"
ENV_TOOLCHECK_VAR = "IBEX_ENV_TOOLCHECK"
REQUESTS_DIR = WORK_DIR / "requests"
RUNNING_DIR = WORK_DIR / "running"
DONE_DIR = WORK_DIR / "done"
RESULTS_DIR = WORK_DIR / "results"

# --- Build configuration (fixed for the whole effort, DV_prompt.txt Section 2) ---------------
BUILD_CONFIG = "opentitan"

# --- Plusarg names shared with gen_tb_pkg.sv (checked by --check) ----------------------------
PLUSARG_BUILD_CONFIG = "gen_build_config"
PLUSARG_SMOKE_CYCLES = "gen_smoke_cycles"
BANNER_TAG = "GEN_CONFIG_BANNER"
# name in gen_tb_pkg.sv -> value here
SV_SHARED_CONSTANTS = {
    "PLUSARG_BUILD_CONFIG": PLUSARG_BUILD_CONFIG,
    "PLUSARG_SMOKE_CYCLES": PLUSARG_SMOKE_CYCLES,
    "GEN_BANNER_TAG": BANNER_TAG,
}

# Simulator/UVM plusargs (names fixed by VCS and UVM, not by the TB).
PLUSARG_NTB_SEED = "ntb_random_seed"
PLUSARG_UVM_TESTNAME = "UVM_TESTNAME"
PLUSARG_UVM_VERBOSITY = "UVM_VERBOSITY"
PLUSARG_UVM_NO_RELNOTES = "UVM_NO_RELNOTES"
UVM_VERBOSITY_DEFAULT = "UVM_LOW"

# --- Seeds: one run seed drives every source of randomness ----------------------------------
SEED_MIN = 1
SEED_MAX = 2**31 - 1
ENV_RANDOM_SEED = "RANDOM_SEED"
SEED_RECORD_TAG = "GEN_RUN_SEED"

# --- VCS compile flag groups (docs/dv/SIM_RECIPE.md Sections 2, 3, 4, 6) ---------------------
VCS_BASE_FLAGS = ["-full64", "-sverilog"]
VCS_UVM_FLAGS = ["-ntb_opts", "uvm-1.2", "+define+UVM", "+define+UVM_REGEX_NO_DPI"]
VCS_COMMON_FLAGS = [
    "-timescale=1ns/10ps",
    "-licqueue",
    "-LDFLAGS", "-Wl,--no-as-needed",
    "-CFLAGS", "--std=c99 -fno-extended-identifiers",
    "-xlrm", "uniq_prior_final",
    "-lca", "-kdb",
]
VCS_DEBUG_PP_FLAGS = ["-debug_access+pp"]
# SIM_RECIPE Section 6 lists -ucli at compile time too; VCS X-2025.06-SP2 rejects that
# (Error-[DBG_UCLI_DEP]), so -ucli goes on the simv command line only (gen_run.py --waves).
VCS_DEBUG_WAVES_FLAGS = ["-debug_access+all"]
# Verified set from SIM_RECIPE Section 3; cond is the T-010 trial metric (see gen_runtime_api.md).
COV_METRICS_VERIFIED = "line+tgl+assert+fsm+branch"
COV_METRICS_WITH_COND = "line+cond+tgl+assert+fsm+branch"
# Glitch filter: off until the DV Lead rules on -cm_glitch 0 (intervention log LOG-008; trial
# rtl-arch-001/-002). Flipping this constant changes every measured build; re-measure round 0 after.
COV_GLITCH_FILTER = False
COV_GLITCH_FLAGS = ["-cm_glitch", "0"]
COV_COMPILE_EXTRA = ["-cm_tgl", "portsonly", "-cm_tgl", "structarr", "-cm_report", "noinitial",
                     "-cm_seqnoconst"] + (COV_GLITCH_FLAGS if COV_GLITCH_FILTER else [])
COV_RUNTIME_EXTRA = ["-cm_log", "/dev/null", "-assert", "nopostproc"]
COV_DIAG_NOCONST = ["-diag", "noconst"]
COCOTB_DEFINE = "+define+COCOTB_SIM"
COCOTB_ENV_MODULE = "MODULE"
COCOTB_ENV_TOPLEVEL = "TOPLEVEL"
COCOTB_ENV_TOPLEVEL_LANG = "TOPLEVEL_LANG"
COCOTB_TOPLEVEL_LANG = "verilog"
COCOTB_ENV_LIBPYTHON = "LIBPYTHON_LOC"
CM_NAME_PREFIX = "test_"
BUILD_VDB_NAME = "build.vdb"
MERGED_VDB_NAME = "merged.vdb"
URG_REPORT_DIRNAME = "report"
# Exclusion policy (Critic ruling R-5): strict loading is mandatory, propagation is banned, the
# full-exclusions dump of a measured merge is kept beside the annotated exclusion file.
URG_EXCL_STRICT = ["-excl_strict"]
URG_EXCL_BANNED = ("-excl_propagation", "-excl_bypass_checks")
URG_DUMP_EXCLUSIONS = ["-dump", "full_exclusions"]
URG_DUMP_DIRNAME = "full_exclusions"
URG_DUMP_GLOB = "fullexclude*"
# merge.log signatures that make a strict merge FAIL (a covered or stale object was excluded).
URG_EXCL_VIOLATION_RE = re.compile(r"Warning-\[UCAPI-ILOAD\]|Illegal exclusion attempt|Error-\[UCAPI")
UNMEASURED_COV_DIRNAME = "cov_unmeasured"
URG_DASHBOARD_TXT = "dashboard.txt"
URG_MERGE_LOG = "merge.log"

# --- Run-time defaults ----------------------------------------------------------------------
SIMV_NAME = "vcs_simv"
SIMV_CSRC_NAME = "vcs_simv.csrc"
COMPILE_LOG = "compile.log"
BUILD_MANIFEST = "build_manifest.yaml"
BUILD_LATEST_SUFFIX = ".latest"
SIM_LOG = "sim.log"
# simv stdout+stderr: cocotb's Python logging bypasses the VCS -l log, so the job captures it too
# and the verdict scans both files.
SIM_STDOUT_LOG = "sim_stdout.log"
LSF_ACTIVE_STATES = ("PEND", "RUN", "PSUSP", "USUSP", "SSUSP", "WAIT", "PROV")
RUN_LOG = "run.log"
RUN_CMD_SH = "run_cmd.sh"
RESULT_YAML = "result.yaml"
LSF_OUT = "lsf.out"
LSF_ERR = "lsf.err"
WAVES_FSDB = "waves.fsdb"
WAVES_VPD = "waves.vpd"
DUMP_TCL = "dump.tcl"
DEFAULT_TIMEOUT_S = 1800
TIMEOUT_GRACE_S = 20

# --- LSF (SIM_RECIPE Section 7; exclusive to the runtime role) -------------------------------
LSF_QUEUE = "regress"
LSF_SIM_SLOTS = 1
LSF_BUILD_SLOTS = 4
LSF_SPAN = "span[hosts=1]"
LSF_JOB_PREFIX = "gen_dv"
LSF_PEND_ALLOWANCE_S = 3600
LSF_POLL_S = 15
LSF_SUBMIT_RE = re.compile(r"Job <(\d+)> is submitted to queue <([^>]+)>")
LSF_STARTED_RE = re.compile(r"<<Starting on (\S+)>>")
# Job-report fields LSF writes into the -o file; the flow's LSF cost source.
LSF_REPORT_CPU_RE = re.compile(r"CPU time\s*:\s*([\d.]+)\s*sec")
LSF_REPORT_RUN_RE = re.compile(r"Run time\s*:\s*([\d.]+)\s*sec")
LSF_REPORT_MEM_RE = re.compile(r"Max Memory\s*:\s*([\d.]+)\s*(\w+)")
LSF_REPORT_HOST_RE = re.compile(r"executed on host\(s\) <([^>]+)>")

# --- Testlist schema ------------------------------------------------------------------------
TESTLIST_SCHEMA_VERSION = 1
TIERS = ("smoke", "targeted", "full")
TIER_RANK = {t: i for i, t in enumerate(TIERS)}
# Build/elaboration checks (gen_smoke, the cocotb probe): outside the measured tiers, selectable
# only by name or with --tier check; never in a measured merge (Critic R-01).
CHECK_TIER = "check"
ALL_TIERS = TIERS + (CHECK_TIER,)
TEST_REQUIRED_KEYS = ("name", "description", "tier", "build", "plusargs", "seeds",
                      "fcov_expectation_file", "timeout_s", "owner")
TEST_OPTIONAL_KEYS = ("uvm_test", "pass_marker", "feature_groups", "cocotb_module",
                      "expected_fail", "component", "notes", "measured")
BUILD_REQUIRED_KEYS = ("tb_top", "dut_instance", "filelists")
# cov_trees: coverage scope roots below tb_top (default [dut_instance]); the single source of the
# -cm_hier scope (Critic P-04; the DV Lead rules on wrapper vs core+regfile).
BUILD_OPTIONAL_KEYS = ("defines", "cocotb", "description", "extra_vcs_args", "cov_trees")
# Testlist header policies: fcov_manifest_required_tiers (P-07), debug_only_plusargs (tb-arch P6).
TESTLIST_OPTIONAL_TOP_KEYS = ("fcov_manifest_required_tiers", "debug_only_plusargs")
# Plusarg names a testlist entry may use besides the gen_tb_pkg.sv PLUSARG_* set (P-06).
SIMULATOR_PLUSARGS = ("ntb_random_seed", "UVM_TESTNAME", "UVM_VERBOSITY", "UVM_NO_RELNOTES", "UVM_TIMEOUT",
                      "UVM_MAX_QUIT_COUNT")
# VCS runtime plusargs carry their value inside the name (+vcs+finish+<time>, +vcs+lic+wait): prefix match.
VCS_PLUSARG_PREFIX = "vcs+"
OWNER_ROLES = ("orchestrator", "dv-lead", "rtl-arch", "tb-infra", "test-writer", "runtime",
               "critic")

# --- Run-request queue (agent_team_prompt.txt, Runtime Manager section) ----------------------
REQUEST_REQUIRED_KEYS = ("requester", "purpose", "tests", "seeds", "coverage", "notes")
REQUEST_NAME_RE = re.compile(r"^(?P<requester>[a-z-]+)-(?P<seq>\d+)\.ya?ml$")
PURPOSES = {
    1: "bring-up of one test: that test, a handful of seeds",
    2: "TB component change: smoke tier + the tests that exercise the component + mutation runs",
    3: "failure reproduction: the single test and seed",
    4: "Phase 1 gate or closure-round measurement: the full regression with coverage",
}
PURPOSE1_MAX_TESTS = 1
PURPOSE1_MAX_SEEDS = 5
PURPOSE3_SEEDS = 1
PURPOSE4_REQUESTERS = ("dv-lead", "orchestrator")
RESULTS_MANIFEST = "manifest.yaml"

# --- Verdicts -------------------------------------------------------------------------------
VERDICT_PASS = "PASS"
VERDICT_FAIL = "FAIL"
VERDICT_TIMEOUT = "TIMEOUT"
VERDICT_NOT_RUN = "NOT_RUN"
VERDICT_XFAIL = "XFAIL"
END_MARKER_DEFAULT = "$finish"
# simv exit codes that do not by themselves fail a clean-log run (0; 124 = coreutils timeout, TIMEOUT).
EXIT_CODES_CLEAN = (0, 124)
# Crash signatures scanned in lsf.err and run.log (the simulator dies without a sim.log message).
CRASH_RE = re.compile(r"Segmentation fault|Killed|core dumped|Aborted|Bus error|Illegal instruction")
# ci/check_fcov_expectations.py exit codes (its module docstring: 0 all hit; 2 unhit; 1 protocol error).
FCOV_EXIT_CODES = {0: "PASS", 2: "UNHIT", 1: "PROTOCOL_ERROR"}
FCOV_DOCSTRING_ANCHORS = ("0 all declared bins hit", "2 declared-but-unhit", "1 usage/protocol error")
# Collected failure mechanisms scanned in sim.log (name, regex). Order = report priority.
FAIL_PATTERNS = (
    ("uvm_fatal", re.compile(r"^UVM_FATAL\s+(?!:\s*0\b)")),
    ("uvm_error", re.compile(r"^UVM_ERROR\s+(?!:\s*0\b)")),
    ("sv_fatal", re.compile(r"^Fatal:|\$fatal|GEN_\w*_FAIL")),
    ("vcs_runtime_error", re.compile(r"^Error-\[|^Error:")),
    ("cocotb_critical", re.compile(r"\bCRITICAL\b")),
    ("cocotb_test_fail", re.compile(r"\*\*\s+TESTS=\d+\s+PASS=\d+\s+FAIL=(?!0\b)\d+")),
    ("assertion_failure", re.compile(r"Assertion .* failed|Offending")),
)
UVM_SUMMARY_RE = re.compile(r"^UVM_(FATAL|ERROR|WARNING|INFO)\s*:\s*(\d+)")
COCOTB_SUMMARY_RE = re.compile(r"\*\*\s+TESTS=(\d+)\s+PASS=(\d+)\s+FAIL=(\d+)\s+SKIP=(\d+)")
FINISH_RE = re.compile(r"^\$finish (at simulation time|called)")

# --- URG dashboard metrics (DV_prompt Section 4: six code metrics + functional) --------------
URG_METRICS = ("line", "cond", "toggle", "fsm", "branch", "assert", "group")
NOT_APPLICABLE = "n/a"
# Gate and stopping rule (DV_prompt Section 4): 80 percent per gated metric; a round shows gain
# when a gated metric improves by at least G points; stop after N consecutive rounds without gain.
# A metric URG does not report is n/a: excluded from the gate and from the gain computation.
GATE_PCT = 80.0
ROUND_GAIN_G = 0.5
ROUND_NO_GAIN_N = 5
EVIDENCE_DIR = REPO_ROOT / "dv" / "auto_dv" / "evidence"
ROUND_INDEX = EVIDENCE_DIR / "gen_rounds.yaml"
ROUND_DIR_PREFIX = "gen_round_"


def sv_plusarg_names(tb_pkg: Path = TB_PKG_SV) -> dict[str, str]:
    """Every `parameter string PLUSARG_<X> = "<name>"` of the SV constants home: {name: PLUSARG_X}."""
    if not tb_pkg.is_file():
        return {}
    text = tb_pkg.read_text(encoding="utf-8")
    return {m.group(2): m.group(1)
            for m in re.finditer(r'parameter\s+string\s+(PLUSARG_\w+)\s*=\s*"([^"]*)"', text)}


def check_sv_constants(tb_pkg: Path = TB_PKG_SV) -> list[str]:
    """Mismatches between this module and gen_tb_pkg.sv for the shared names, plus the
    fcov-checker exit-code contract against its own docstring (P-06 single source)."""
    problems: list[str] = []
    if not tb_pkg.is_file():
        return [f"{tb_pkg}: missing"]
    text = tb_pkg.read_text(encoding="utf-8")
    for sv_name, py_value in SV_SHARED_CONSTANTS.items():
        m = re.search(rf'parameter\s+string\s+{sv_name}\s*=\s*"([^"]*)"', text)
        if not m:
            problems.append(f"{sv_name}: not declared in {tb_pkg}")
        elif m.group(1) != py_value:
            problems.append(f"{sv_name}: SV={m.group(1)!r} Python={py_value!r}")
    if FCOV_CHECKER.is_file():
        doc = FCOV_CHECKER.read_text(encoding="utf-8")
        for anchor in FCOV_DOCSTRING_ANCHORS:
            if anchor not in doc:
                problems.append(f"{FCOV_CHECKER.name}: exit-code contract text {anchor!r} not found; "
                                f"FCOV_EXIT_CODES may be stale")
    return problems


def main() -> int:
    if "--check" in sys.argv:
        problems = check_sv_constants()
        for p in problems:
            print("CONST-CHECK MISMATCH:", p)
        print("CONST-CHECK:", "PASS" if not problems else "FAIL")
        return 0 if not problems else 1
    print(f"REPO_ROOT={REPO_ROOT}")
    print(f"WORK_DIR={WORK_DIR}")
    print(f"TESTLIST_YAML={TESTLIST_YAML}")
    print("usage: gen_flow_const.py --check   (compare shared names with gen_tb_pkg.sv)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
