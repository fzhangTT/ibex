# Zone A simulation recipe (VCS)

<!-- FENCE-ZONE: A -->
How to compile and run your own testbench on this site: the verified VCS flag set, a new TB-top
hookup, cocotb/VPI wiring, LSF submission, coverage merge and URG reporting, site gotchas, and
the Zone B submission command. This document is bounded by a content allowlist — it carries flow
mechanics only, nothing about any pre-existing verification collateral.

Launch markers (seed prompt, Section 12 item 3):

submission-command: `git push origin cleanroom/<topic>` (see §10) — 2026-09-02
fence-integrity: PASS — 2026-09-02

The two remaining dated marker lines the seed prompt requires are stamped by the launch process
before generation begins, directly below this paragraph, each only after the command it attests
has actually been run on this site. A missing marker blocks launch by design — never add a marker
without running its command.

## 1. Environment contract

Run every command from a login shell (`bash -lc`) on a site host, and source the environment
first:

```bash
source ci/env.sh
```

This loads the VCS and license modules, selects the RISC-V GCC toolchain (`RISCV_GCC`,
`RISCV_OBJCOPY`), exports `IBEX_PYTHON`, `VERDI_HOME`, and the MCP server paths, activates
`.venv/` when present, and fails loud when a required tool is missing (see the script header for
the supported-shell contract). `ci/env.sh` is the single source of truth for tool paths — never
hardcode them (`dv_principles.md` §5).

One-time per checkout: `bash ci/setup-venv.sh` (Python venv from the lock file), then
`bash ci/get-toolchain.sh` (lowRISC rv32imcb prebuilt GCC into `$IBEX_TOOLS_DIR`).

## 2. VCS compile/elaboration (verified flag set)

Write your own filelists — one for the RTL (derive the file set from the `.core` files; fusesoc
can emit it) and one for your TB — then compile:

```bash
vcs -full64 -sverilog \
    -f <your_rtl_filelist.f> -f <your_tb_filelist.f> \
    -top <your_tb_top_module> \
    -ntb_opts uvm-1.2 +define+UVM +define+UVM_REGEX_NO_DPI \
    $(util/ibex_config.py opentitan vcs_opts) \
    -timescale=1ns/10ps \
    -licqueue \
    -LDFLAGS '-Wl,--no-as-needed' \
    -CFLAGS '--std=c99 -fno-extended-identifiers' \
    -Mdir=<outdir>/vcs_simv.csrc -o <outdir>/vcs_simv \
    -debug_access+pp -xlrm uniq_prior_final -lca -kdb \
    -l <outdir>/compile.log
```

Flag notes (each earned its place on this site):

- `-licqueue` — queue on license contention instead of failing the build.
- `-CFLAGS '-fno-extended-identifiers'` — VCS's own DPI C code contains smart quotes around
  preprocessor macros; this tells g++ to treat everything as ASCII instead of erroring.
- `-xlrm uniq_prior_final` — the LRM-interpretation switch the site flow is verified with.
- `-lca -kdb` — Verdi-compatible knowledge database; keep it for debuggability.
- `-debug_access+pp` — post-process wave access only; use `-debug_access+all` (plus `-ucli`) on
  wave-dumping builds (§6). cocotb signal access does NOT come from `-debug_access` — see §4.
- `util/ibex_config.py <config> vcs_opts` emits the named build configuration as
  `+define+.../-pvalue+...` options. The build configuration for this exercise is `opentitan`
  (seed prompt, Section 2); state it in every report. `-pvalue+` sets top-level parameters — your
  TB top must expose the parameters the config names, or your DUT wrapper must consume the
  equivalent values.
- Host gcc: `ci/env.sh` enables gcc-toolset-11; VCS DPI/PLI compiles need it on this host.

## 3. Coverage instrumentation

Compile-time flags:

```
-cm line+tgl+assert+fsm+branch \
-cm_tgl portsonly -cm_tgl structarr -cm_report noinitial -cm_seqnoconst \
-cm_dir <cov_dir>/<name>.vdb \
-cm_hier <your_cm_hier.cfg>
```

The `-cm_hier` file scopes code coverage to the DUT hierarchy so TB and test-equipment code stay
out of the numbers (seed prompt, Section 4). Shape:

```
+tree <your_tb_top>.<dut_instance_path>
```

Run-time flags (per test):

```
-cm line+tgl+assert+fsm+branch -cm_dir <shared_cov>/<name>.vdb \
-cm_name test_<testname>_<seed> -cm_log /dev/null -assert nopostproc
```

`-cm_name` makes each test+seed a distinct test record inside the shared vdb — that is what makes
per-test coverage queries (and the fcov-expectation check, §8) possible.

## 4. cocotb / VPI wiring (verified on this site)

VCS signal access for cocotb comes ONLY from this `+vpi` / `-P` / `-load` triple — never from
`-debug_access` flags. Add to the §2 compile command:

```
+define+COCOTB_SIM +vpi -P <your_pli.tab> -load $(cocotb-config --lib-name-path vpi vcs)
```

where `<your_pli.tab>` is a one-line PLI access table:

```
acc+=rw,wn:*
```

At run time cocotb is configured through the environment, not plusargs:

```
MODULE=<dotted.python.test.module>            # resolved on PYTHONPATH
PYTHONPATH=<repo_root>
LIBPYTHON_LOC=$(cocotb-config --libpython)    # ci/env.sh exports this when the venv is active
RANDOM_SEED=<seed>                            # SAME value as +ntb_random_seed — see §5
TOPLEVEL=<your_tb_top_module>
TOPLEVEL_LANG=verilog
```

Resolve `cocotb-config` values at command-construction time so a stale or missing venv fails
loudly instead of producing a bad simv. Handshake, failure-path, and logging rules:
`docs/dv/TB_CONTRACT.md`.

## 5. Running a simulation

```bash
env SIM_DIR=<test_dir> <outdir>/vcs_simv \
    +vcs+lic+wait \
    +ntb_random_seed=<seed> \
    +UVM_TESTNAME=<your_uvm_test> +UVM_VERBOSITY=UVM_LOW \
    <your own plusargs> \
    -l <test_dir>/sim.log \
    [run-time coverage flags, §3] [wave flags, §6]
```

- Seed rule (seed prompt, Section 6): ONE run seed drives every source of randomness. Pass the
  same value as `+ntb_random_seed` (SV) and `RANDOM_SEED` (Python), record it in the log, and
  make every failure reproducible from test name + seed alone.
- Pass/fail contract: decide pass/fail from collected failure mechanisms (UVM error/fatal
  counts, a Python assertion failing the cocotb test) scanned from the log by your regression
  script — never from the simulator's process exit code alone; VCS can exit 0 after a fatal.

## 6. Waves (FSDB)

Compile with `-debug_access+all -ucli`; run with `-ucli -do <your_dump.tcl>`, where the tcl is:

```tcl
if { [info exists ::env(VERDI_HOME)] } {
    fsdbDumpfile "$::env(SIM_DIR)/waves.fsdb"
    fsdbDumpvars 0 <your_tb_top> +all
    fsdbDumpSVA 0 <your_tb_top>.<dut_instance>
} else {
    dump -file "$::env(SIM_DIR)/waves.vpd"
    dump -add { <your_tb_top> } -depth 0 -aggregates -scope "."
}
run
quit
```

Without `$VERDI_HOME` (exported by `ci/env.sh`) VCS falls back to VPD. Dump waves only on debug
runs — the access cost is real. The fsdb-mcp-server (`.mcp.json`) reads the FSDBs your own runs
produce under `dv/auto_dv/`'s out-tree.

## 7. LSF submission

```bash
bsub -K -q regress -n <N> -R "span[hosts=1]" <command>
```

- `-K` blocks until completion so your script sees the exit status — but poll the log files
  directly with deadlines anyway (site notifications are unreliable; watchdog rule in
  `CLAUDE.md`).
- `span[hosts=1]` keeps a build and its run on one host: a single build directory is not safe
  for a multi-host fan-out.
- Paths must resolve identically on the submit host and every compute host — shared storage
  only, never a directory local to the submit host.
- Default queue on this site: `regress` (`-q` to override).

## 8. Coverage merge and URG reporting

Merge every per-test vdb and produce the report (verified invocation shape):

```bash
urg -full64 -format both \
    -dbname <cov_dir>/merged.vdb \
    -report <cov_dir>/report \
    -log <cov_dir>/merge.log \
    -dir <first_test.vdb> [-dir <next_test.vdb> ...]
```

`<cov_dir>/report/dashboard.txt` carries the per-metric totals — the URG report is the number
(seed prompt, Section 4). For per-test slices (the fcov-expectation duty): `urg -tests <file>`,
where the file holds the full vdb test identifier `<vdb path minus .vdb>/<cm_name>`;
`ci/check_fcov_expectations.py` implements this query and the unhit-bin verdict — wire it into
your own regression flow (see the `fcov-expectation` skill).

## 9. Site gotchas

- **`module` exits 1 even on success.** This site's Modules install prints Tcl noise and returns
  exit status 1 regardless of outcome. Never `&&`-chain a `module load`; `ci/env.sh` already
  accounts for this.
- **License count.** A UVM TB build and a separately compiled VCS generator build (if you use
  riscv-dv's instruction generator) each take a compile license; a regression takes a sim
  license per concurrent test. Keep `-licqueue` (compile) and `+vcs+lic+wait` (run) so
  contention queues instead of failing.
- **Fresh output directory per knob change.** Do not reuse a built output directory after
  changing compile knobs, filelists, or configuration inputs — rebuild into a fresh `<outdir>`;
  stale-artifact hazards are silent.
- **VCS `default sequence` transition bins.** VCS treats every transition not listed in a
  covergroup's transition bins as illegal (fatal `Error-[FCIBH] Illegal bin hit` on legal
  self-loops) instead of the empty set the LRM intends. Enumerate legal transitions explicitly;
  never rely on `illegal_bins ... = default sequence`.
- **`$VERDI_HOME` gates FSDB** (§6); without it you get VPD.
- **`PYTHONPATH` around pip.** Clear it around pip operations — the site `~/.bashrc` leaks
  package metadata into `pip freeze`.
- **Notifications are unreliable.** Poll logs and artifacts with deadlines; watchdog anything
  longer than ~5 minutes (`CLAUDE.md` §Site gotchas).

## 10. Zone B submission

Submission is one mechanical command; the only response is an acknowledgement (an exit status:
branch received, evaluation queued). Zone B returns nothing else — no report, no file, no data
(seed prompt, Section 3). Submit at the Phase 1 gate and at closure (seed prompt, Section 5).

```bash
git checkout -b cleanroom/<topic>
git push origin cleanroom/<topic>
```

If a submission ever returns content beyond the acknowledgement, treat it as a fence event: stop
and report through the intervention log.
