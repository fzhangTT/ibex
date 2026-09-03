#!/usr/bin/env python3
"""Single constants home of the generated regression flow (Python side).

Every path, plusarg name, log marker, LSF default and schema constant the flow scripts use is
defined here and imported; no script re-types a literal. The SV-side constants home is
dv/auto_dv/tb/gen_tb_pkg.sv; `--check` proves the two agree on the shared names.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# --- Repository anchors (everything resolves from the clone root) ---------------------------
FLOW_DIR = Path(__file__).resolve().parent
REPO_ROOT = FLOW_DIR.parents[2]
# Source root: the tree that builds, programs, generators, the testlist and the knob table are read
# from. The clone by default; a head-mode regression re-executes itself with GEN_DV_SOURCE_ROOT set to
# the mirror synced from committed HEAD, so a shared working tree mid-edit can never reach a measured run.
ENV_SOURCE_ROOT = "GEN_DV_SOURCE_ROOT"
ENV_HEAD_SHA = "GEN_DV_HEAD_SHA"
# Removed from every simulation job and program-generator environment before the flow's own values are applied:
# the site shell leaks PYTHONPATH (a cocotb run gets exactly the source root back), and a developer shell's
# staged-entries pointer (gen_test_lib.STAGED_ENTRIES_ENV) must never reach a flow run.
JOB_ENV_UNSET = ("PYTHONPATH", "GEN_TEST_STAGED_ENTRIES")
# Exported in every simulation job after the unsets: the harness refuses developer-only inputs when it sees this marker.
JOB_ENV_SET = {"GEN_DV_FLOW_RUN": "1"}
# The harness ends every run with this line (LOG-030): n > 0 report stores lagged n program budgets while the core
# kept retiring (slow bus regimes), so a run can be slow but green; recorded per run so slowness is visible.
SLOW_TOTAL_RE = r"GEN_TEST_SLOW_TOTAL rounds=(\d+) budget_cycles=(\d+)"
SOURCE_ROOT = Path(os.environ[ENV_SOURCE_ROOT]).resolve() if os.environ.get(ENV_SOURCE_ROOT) else REPO_ROOT
SOURCE_MODE_HEAD = "head"
SOURCE_MODE_WORKTREE = "worktree"
SOURCE_MODES = (SOURCE_MODE_HEAD, SOURCE_MODE_WORKTREE)
ENV_MIRROR_ROOT = "GEN_DV_MIRROR_ROOT"   # the mirror a process binds to (a head-mode process: its per-sha head tree)
HEAD_MIRROR_SUFFIX = "_head"            # per-sha head trees live beside the worktree mirror: <site root>_head/<sha12>
HEAD_MIRRORS_KEEP = 6                   # newest head trees always kept by the prune step
HEAD_MIRRORS_KEEP_HOURS = 3.0           # head trees younger than this are never pruned
LEASE_DIRNAME = ".leases"               # a live consumer (regression, batch) leases its head tree here; leased trees are never pruned
LEASE_MAX_AGE_H = 12.0                  # a lease this host cannot probe (another host's pid) counts as live at most this long
# The mirrored source subset, one list for the worktree rsync, the head-mode git archive and the request server's
# canary hold (git diff over exactly this set): clone-root-relative items, top-level globs, and the excluded
# non-inputs that nothing reads at build or run time (queue files, review records, evidence documents).
MIRROR_ITEMS = ("rtl", "vendor/lowrisc_ip", "vendor/google_riscv-dv", "util", "ci", "dv/auto_dv",
                "ibex_configs.yaml", "python-requirements.txt")
MIRROR_GLOB_ITEMS = ("*.core",)
MIRROR_EXCLUDE_PATHS = ("dv/auto_dv/work", "dv/auto_dv/reviews", "dv/auto_dv/evidence")
MIRROR_EXCLUDE_PATTERNS = (".git", "__pycache__", "*.pyc", ".venv", "out*", "*.vdb", "*.fsdb")   # untracked build products
# Head-mode batch decisions (request server): every batch needs the commit a gen_boot_zc canary passed on and is
# refused, with the record kept, when that commit is missing or differs from HEAD in a mirrored file.
CANARY_ACCEPTED = "accepted"
CANARY_REFUSED_DELTA = "refused_build_inputs_changed"
CANARY_REFUSED_MISSING = "refused_no_canary_sha"
ENV_SH = REPO_ROOT / "ci" / "env.sh"
CONFIG_SCRIPT = SOURCE_ROOT / "util" / "ibex_config.py"
FCOV_CHECKER = SOURCE_ROOT / "ci" / "check_fcov_expectations.py"
TB_DIR = SOURCE_ROOT / "dv" / "auto_dv" / "tb"
TB_PKG_SV = TB_DIR / "gen_tb_pkg.sv"
# TB Infra's rendered knob table (one origin of the debug_only property and of every plusarg name).
KNOBS_MODULE = "dv.auto_dv.gen_tb.gen_knobs"
FCOV_EXPECT_DIR = SOURCE_ROOT / "dv" / "auto_dv" / "fcov_expectations"
DOCS_DIR = REPO_ROOT / "dv" / "auto_dv" / "docs"
DASHBOARD_MD = DOCS_DIR / "gen_dashboard.md"
DASHBOARD_METRICS_MD = DOCS_DIR / "dashboard_metrics.md"

TESTLIST_YAML = SOURCE_ROOT / "dv" / "auto_dv" / "flow" / "gen_testlist.yaml"
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


def site_value(key: str) -> str | None:
    """Other site pointers of gen_site.yaml (e.g. riscv_dv_gen_build: a prebuilt riscv-dv generator)."""
    if SITE_YAML.is_file():
        m = re.search(rf"^{re.escape(key)}:\s*(\S+)", SITE_YAML.read_text(encoding="utf-8"), re.M)
        if m:
            return m.group(1)
    return None


STAGED_ENV_SH = "env.sh"
ENV_TOOLCHECK_VAR = "IBEX_ENV_TOOLCHECK"
SELFTEST_TMP = WORK_DIR / "selftest_tmp"   # scratch parent of every flow self-test (never the shared /tmp, F-001)


SELFTEST_TMP_ENV = "GEN_DV_SELFTEST_TMP"   # reviewer override: a private scratch dir when the clone is read-only


def selftest_tmp() -> str:
    """Scratch parent for self-tests: under the runtime work tree (or the directory GEN_DV_SELFTEST_TMP
    names explicitly), never the shared /tmp (F-001)."""
    root = Path(os.environ[SELFTEST_TMP_ENV]) if os.environ.get(SELFTEST_TMP_ENV) else SELFTEST_TMP
    root.mkdir(parents=True, exist_ok=True)
    return str(root)


REQUESTS_DIR = WORK_DIR / "requests"
BATCHES_DIR = WORK_DIR / "batches"   # one record per head-mode batch decision (accepted or refused)
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
# Standing rule: the glitch filter (-cm_glitch 0, ruled in LOG-008) is a build-entry knob
# (builds.<name>.extra_vcs_args of gen_testlist.yaml), never a flow constant; this list is the
# SIM_RECIPE Section 3 set only.
COV_COMPILE_EXTRA = ["-cm_tgl", "portsonly", "-cm_tgl", "structarr", "-cm_report", "noinitial",
                     "-cm_seqnoconst"]
COV_RUNTIME_EXTRA = ["-cm_log", "/dev/null", "-assert", "nopostproc"]
# VCS coverage flags that take one value; every other -cm* flag stands alone (the no-coverage drop uses this).
CM_VALUE_FLAGS = ("-cm", "-cm_dir", "-cm_name", "-cm_hier", "-cm_glitch", "-cm_tgl", "-cm_line", "-cm_cond",
                  "-cm_report", "-cm_log", "-cm_libs", "-cm_assert_hier", "-cm_fsmopt")
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
URG_DUMP_METRIC_GLOB = "fullexclude.*"   # the per-metric dump files a round copies (the _module variants stay in the out-tree)
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
MIRROR_SYNC_TIMEOUT_S = 1800   # gen_mirror.py --sync --spike, whether gen_regress or the request server runs it
ELCHECK_TIMEOUT_S = 1800       # one report-only URG merge of the exclusion check
LSF_STATUS_SETTLE_S = 15.0   # bjobs shows a finished job as RUN for a few seconds after bsub -K returns
JOB_TIMEOUT_CMD = "timeout"   # first word of the job script's simv line; bash's kill report quotes it first

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
                      "expected_fail", "component", "notes", "measured", "program", "red_fixture", "red_expect",
                      "keep_artifacts", "witness_ids")
# Witness protocol (plan WP rows): a test entry lists the TP ids whose clause it witnesses; the flow renders the
# indices of dv/auto_dv/docs/gen_trace_witness_ids.csv (its index column) into the SV plusarg named by the
# constants home and records ids, indices and the CSV digest in result.yaml.
WITNESS_CSV = SOURCE_ROOT / "dv" / "auto_dv" / "docs" / "gen_trace_witness_ids.csv"
SV_PLUSARG_WITNESS_IDS = "PLUSARG_WITNESS_IDS"
# Retention of the per-run export file: purposes 1-3 keep every artifact; a purpose-4 regression prunes the
# file named by the test's export plusarg after the manifest is written, for PASS / RED-OK runs only, unless
# the entry says keep_artifacts: true; every pruned path is recorded in result.yaml (pruned_artifacts); the
# file must lie inside the run directory. The plusarg name comes from the SV constants home.
# The identifier of the export-file plusarg in gen_tb_pkg.sv (the string value is read there, never re-typed).
SV_PLUSARG_EXPORT_FILE = "PLUSARG_EXPORT_FILE"
SV_PLUSARG_EXPORT_SOURCES = "PLUSARG_EXPORT_SOURCES"   # the sources knob; its "all" value keeps the header/manifest equality rule
EXPORT_SOURCES_ALL = "all"
# Observed export rows (LOG-028a): the sunset trusts what the sink wrote, so a build's emitted set comes from the
# header sources= of its runs' export files and the per-row first-seen list from their E lines, never from the yaml.
EXPORT_EVENT_LINE_PREFIX = "E "
EXPORT_FIRST_LINE_MAX = 200
EXPORT_EMITTED_UNOBSERVED = "no export file observed yet: a run of this build that writes an export file fills it (LOG-028a)"
RETENTION_PRUNE_PURPOSES = (4,)
# program: the test's memory image comes from dv/auto_dv/stim/gen_program.py before the run.
PROGRAM_TOOL = SOURCE_ROOT / "dv" / "auto_dv" / "stim" / "gen_program.py"
PROGRAM_KEYS = ("riscv_dv_test", "directed", "generator", "generator_args", "seed", "extra_args", "spike_check")
PROGRAM_SOURCE_FORMS = ("riscv_dv_test", "directed", "generator")   # exactly one per program block
PROGRAM_GENERATOR_SOURCE = "gen_source.S"   # the per-seed source a program generator writes into <run>/program/
PROGRAM_SEED_RUN = "run"
PROGRAM_DIRNAME = "program"
PROGRAM_VMEM = "prog.vmem"
PROGRAM_SIDECAR = "prog.sym.json"
# TB Infra's image helper: the run's image plusargs come from GenImage.plusargs(), never re-typed here.
IMAGE_HELPER_MODULE = "dv.auto_dv.gen_tb.gen_image"
BUILD_REQUIRED_KEYS = ("tb_top", "dut_instance", "filelists")
# cov_trees: the gated coverage roots below tb_top (single source of the -cm_hier scope; ruled:
# the two inner instances, never nested).
# info_trees: instrumented and reported informationally (the wrapper), never in the gate numbers.
# pre_build: commands run (clone root cwd, env sourced) before vcs, "{outdir}" rendered; extra_ldflags:
# appended to the SIM_RECIPE -LDFLAGS base, "{outdir}" rendered; runtime_lib_dirs: LD_LIBRARY_PATH of
# every run of the build, "{outdir}" and "{mirror}" rendered (shared libraries such as the ISA shim
# and the mirror's spike, which a compute host cannot reach through a clone-path rpath).
BUILD_OPTIONAL_KEYS = ("defines", "cocotb", "description", "extra_vcs_args", "cov_trees", "info_trees",
                       "pre_build", "extra_ldflags", "runtime_lib_dirs")
LDFLAGS_BASE = "-Wl,--no-as-needed"
# DV Lead rulings applied by the flow (dv/auto_dv/docs/gen_tb_architecture.md Section 5). The scope
# text names no instance: the names come from the build entry's cov_trees / info_trees (single source).
RULING_SCOPE_TEMPLATE = ("gen_tb_architecture.md Section 5: the gate numbers are the gated cov_trees {gated} combined "
                         "per metric (sum of covered and of total objects, percent = 100 x covered / total; the gated "
                         "trees must not nest); the info_trees {info} are reported informationally, never gated")
RULING_GLITCH = ("gen_tb_architecture.md Section 5 (LOG-007/008): every measured build uses -cm_glitch 0 "
                 "(builds.<name>.extra_vcs_args); FSM coverage is not glitch-filtered (VCS Warning-[VCM-OPTIGN])")
GLITCH_FLAGS = ("-cm_glitch", "0")
# Exported to every tool the flow launches (gen_program.py and friends) so the build-configuration
# name has one home; a tool that reads it instead of its own constant stays in step with the flow.
ENV_BUILD_CONFIG = "GEN_BUILD_CONFIG"


def ruling_scope_text(gated: list[str], info: list[str]) -> str:
    return RULING_SCOPE_TEMPLATE.format(gated=sorted(gated) or "[none]", info=sorted(info) or "[none]")
# Testlist header policies: fcov_manifest_required_tiers (P-07), debug_only_plusargs (tb-arch P6).
TESTLIST_OPTIONAL_TOP_KEYS = ("fcov_manifest_required_tiers", "debug_only_plusargs", "red_expect_policy")
# red_expect_policy tokens: fire_id = a red_expect starting with GEN_TEST_FAIL must name a fire_ id (the harness
# prints the designed fire id on that line, so a generic signature would accept any fixture failure).
RED_EXPECT_POLICY_FIRE_ID = "fire_id"
RED_EXPECT_POLICIES = (RED_EXPECT_POLICY_FIRE_ID,)
RED_EXPECT_FIRE_TOKEN = "fire_"
RED_EXPECT_HARNESS_PREFIX = "GEN_TEST_FAIL"
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
SERVE_MAX_CONCURRENT_P1 = 4           # independent purpose-1 requests served at once (ruling 2026-09-03)
# Report-only exclusion check (purpose 2, no simulation): strict load of an exclusion file against an existing vdb.
ELCHECK_REQUIRED_KEYS = ("vdb", "elfile")
ELCHECK_OPTIONAL_KEYS = ("build",)
ELCHECK_KEYS = ELCHECK_REQUIRED_KEYS + ELCHECK_OPTIONAL_KEYS

# --- Verdicts -------------------------------------------------------------------------------
VERDICT_PASS = "PASS"
VERDICT_FAIL = "FAIL"
VERDICT_TIMEOUT = "TIMEOUT"
VERDICT_NOT_RUN = "NOT_RUN"
VERDICT_XFAIL = "XFAIL"
VERDICT_RED_OK = "RED-OK"   # a red fixture failed as designed (never a regression failure, never coverage)
END_MARKER_DEFAULT = "$finish"
# simv exit codes that do not by themselves fail a clean-log run (0; 124 = coreutils timeout, TIMEOUT).
EXIT_CODES_CLEAN = (0, 124)
# Crash signatures: the SHELL's process-termination report (job script stderr = lsf.err, or run.log
# for local runs), never free text. An ISS/TB log line such as "Illegal instruction (hart 0) at PC"
# must not match (real false positive on gen_ut_bridge, tb-infra-002).
# bash prints the PID with %5ld: a short PID carries leading spaces (": line 7:   537 Killed ...").
CRASH_RE = re.compile(r"(^|: )\s*(\d+\s+)?(Segmentation fault|Bus error|Aborted|Illegal instruction|Killed|Terminated)"
                      r"(\s+\(core dumped\))?\s*(" + re.escape(JOB_TIMEOUT_CMD) + r"( |$)|\S*simv\S*|bash|$)"
                      r"|\(core dumped\)|timeout: sending signal")
# ci/check_fcov_expectations.py exit codes (its module docstring: 0 all hit; 2 unhit; 1 protocol error).
FCOV_EXIT_CODES = {0: "PASS", 2: "UNHIT", 1: "PROTOCOL_ERROR"}
FCOV_DOCSTRING_ANCHORS = ("0 all declared bins hit", "2 declared-but-unhit", "1 usage/protocol error")
# Collected failure mechanisms scanned in sim.log (name, regex). Order = report priority.
FAIL_PATTERNS = (
    ("uvm_fatal", re.compile(r"^UVM_FATAL\s+(?!:\s*0\b)")),
    ("uvm_error", re.compile(r"^UVM_ERROR\s+(?!:\s*0\b)")),
    ("gen_fail_marker", re.compile(r"GEN_\w*_FAIL")),
    ("sv_fatal", re.compile(r"^Fatal:|\$fatal")),
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
# Witness ledger covergroups (fcov plan CG-WIT-001, rendered as gen_cg_wit_cycle_clause): a ledger of fire-check
# results, not DUT coverage. Ruling 2026-09-03: excluded by name from the functional-group score in the flow's
# combining rule (the mechanism of record; TB Infra's option.weight = 0 is defence in depth) and reported
# beside the score as "witnessed clauses: N of M".
# Keyed on the SV covergroup name URG reports (architecture rule C7: plan gen_cg_<area>_<name> -> implementation
# gen_<name>_cg; the committed fcov manifests render gen_wit_cycle_clause_cg). The plan-name alias stays only until
# TB Infra confirms the SV name in the export addendum v4c Section 9.
LEDGER_COVERGROUPS = ("gen_wit_cycle_clause_cg", "gen_cg_wit_cycle_clause")
LEDGER_PLAN_ID = "CG-WIT-001"    # label in the ledger text only; the ledger is matched by SV covergroup name
LEDGER_REQUIRED = True   # a merge that reports covergroups but no ledger row fails loud (the plan says the ledger exists)
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
# Round evidence files: gen_round.py writes them and the exclusion tools under dv/auto_dv/excl read them (EC-3 fill,
# F1 pass), so the names have this one home and every file carries the landing rule's prefix.
EVIDENCE_FILE_PREFIX = "gen_"


def round_evidence_name(name: str) -> str:
    """Evidence file name of a URG or flow product: the prefix added once (a gen_ name stays as it is)."""
    return name if name.startswith(EVIDENCE_FILE_PREFIX) else EVIDENCE_FILE_PREFIX + name


ROUND_URG_FILES = ("dashboard.txt", "hierarchy.txt", "tests.txt", "groups.txt", "grpinfo.txt", "asserts.txt")   # copied when present
ROUND_EV_DASHBOARD = round_evidence_name("dashboard.txt")
ROUND_EV_HIERARCHY = round_evidence_name("hierarchy.txt")
ROUND_EV_TESTS = round_evidence_name("tests.txt")
ROUND_EV_GROUPS = round_evidence_name("groups.txt")
ROUND_EV_GRPINFO = round_evidence_name("grpinfo.txt")
ROUND_EV_ASSERTS = round_evidence_name("asserts.txt")                     # EC-3 evidence (gen_excl_select.py --ec3-asserts)
ROUND_EV_REGRESS_MANIFEST = round_evidence_name("regress_manifest.yaml")   # read beside it by both exclusion tools
ROUND_EV_HIERARCHY_DUT_ROWS = round_evidence_name("hierarchy_dut_rows.txt")
ROUND_EV_GROUPS_SUMMARY = round_evidence_name("groups_summary.txt")
ROUND_EV_MERGE_LOG = round_evidence_name("merge.log")
ROUND_EV_MERGE_LOG_WARNINGS = round_evidence_name("merge_log_warnings.txt")
ROUND_EV_TESTLIST_SNAPSHOT = round_evidence_name("testlist_snapshot.yaml")
ROUND_EV_BUILD_MANIFEST_FMT = EVIDENCE_FILE_PREFIX + "build_manifest_{build}.yaml"
ROUND_EV_FULL_EXCL_DIR = URG_DUMP_DIRNAME   # holds round_evidence_name(fullexclude.<metric>) + .gz
ROUND_EV_ELFILES_DIR = "elfiles"
ROUND_EV_SUMMARY = "gen_round_summary.md"
ROUND_EC3_ASSERTS_RE = rf"^dv/auto_dv/evidence/{ROUND_DIR_PREFIX}[^/]+/{re.escape(ROUND_EV_ASSERTS)}$"   # the EC-3 input the selector accepts


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
