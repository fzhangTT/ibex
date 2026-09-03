# Task 4: Flow Plumbing — the `COCOTB=1` Knob — Report

## Status
✅ **COMPLETE**

## Step 1: How WAVES/cov_opts flow (and where the run-env differs)

`Makefile` declares `WAVES`/`COV` (default 0) and folds them into the
`--args-list` string passed to `scripts/metadata.py --op create_metadata`.
`metadata.py`'s `RegressionMetadata.arg_list_initializer` type-casts each
`KEY=VALUE` token against the dataclass field of the same (lowercased) name
and freezes them into `metadata.pickle`. `scripts/compile_tb.py` and
`scripts/run_rtl.py` load that pickle (`LockedMetadata`/
`RegressionMetadata.construct_from_metadata_dir`) and build a
`user_enables={'wave_opts': md.waves, ...}` dict plus a `user_subst_options`
dict, both passed to `riscvdv_interface.get_tool_cmds()`. That function reads
the `vcs` entry of `yaml/rtl_simulation.yaml`: static per-tool keys
(`wave_opts:`/`cov_opts:` blocks) are gated on/off by `user_enables` (empty
string when off), then `<K>` placeholders anywhere in the `cmd:` template are
substituted by `user_subst_options` (always applied, values computed in
Python — e.g. `'dir_shared_cov': (md.dir_shared_cov if md.cov else '')` is
the precedent I mirrored for `cocotb_compile_opts`, since the cocotb value
needs a `subprocess`-resolved absolute path, not a static yaml string). Every
`shlex.split()`'d command goes straight to `subprocess.run()` with no shell,
so nothing in these dicts may contain a `$VAR` reference.

The *run*-stage env is different in kind: `run_rtl.py`'s sim command already
uses a `env SIM_DIR=<test_dir> <tb_dir>/vcs_simv ...` prefix (the coreutils
`env` binary reading concrete `NAME=value` tokens off `argv`, still no
shell). Per the controller ruling, I did **not** extend that string-template
path for cocotb's env vars; instead I built a genuine Python `dict` in
`run_rtl.py` and pass it through `scripts_lib.run_one`'s existing
`env: Optional[Dict[str,str]]` parameter straight into `subprocess.run(env=...)`.
With `COCOTB=0` this stays `None` (subprocess inherits the parent env
unchanged, byte-identical to today). Stimulus plusargs (`+cocotb_*`) need no
new plumbing — they already ride `sim_opts` from `testlist.yaml`.

## Step 2: Implementation

- `dv/uvm/core_ibex/cocotb_pli.tab` (new): single line `acc+=rw,wn:*`.
- `Makefile`: `COCOTB := 0`, `COCOTB_MODULE := dv.cocotb.ibex_cocotb`; both
  added to the `create_metadata --args-list` string.
- `scripts/metadata.py`: added `cocotb: bool = False` and
  `cocotb_module: str = 'dv.cocotb.ibex_cocotb'` fields.
- `scripts/scripts_lib.py`: new `get_cocotb_config_path(ibex_root)` helper,
  shared by compile and run stages (both re-derive independently, per the
  ruling — neither trusts `ci/env.sh`'s export). Resolves
  `<ibex_root>/.venv/bin/cocotb-config` by absolute path only (never PATH),
  raises `RuntimeError` if missing, then runs `--version` and raises loudly
  if it isn't exactly `1.9.2`.
- `scripts/compile_tb.py`: when `md.cocotb`, resolves the vpi `.so` via
  `cocotb-config --lib-name-path vpi vcs` and builds
  `cocotb_compile_opts = f'+define+COCOTB_SIM +vpi -P {tab.resolve()} -load {vpi_so}'`;
  `''` otherwise. Added as `subst_vars_dict['cocotb_compile_opts']`.
- `yaml/rtl_simulation.yaml`: vcs `compile.cmd` gained a trailing
  `<cocotb_compile_opts>` token (after `<cosim_opts>`). No sim-side yaml
  change — the run env is Python-dict-only (see Step 1).
- `scripts/run_rtl.py`: when `md.cocotb`, re-derives `cocotb-config`,
  resolves `LIBPYTHON_LOC` via `--libpython`, builds `PYTHONPATH` as
  `os.pathsep.join([str(md.ibex_root)] + ([inherited] if inherited else []))`,
  and constructs `sim_env = dict(os.environ); sim_env.update({MODULE,
  PYTHONPATH, LIBPYTHON_LOC, RANDOM_SEED: str(trr.seed), TOPLEVEL:
  'core_ibex_tb_top', TOPLEVEL_LANG: 'verilog'})`, passed as `env=sim_env`
  to `run_one()`. `sim_env = None` when `COCOTB=0` (untouched inheritance).

## Step 3: Dependency tracking

- `scripts/ibex_sim.mk`: added `COCOTB` to `rtl-tb-compile-var-deps` (now
  `SIMULATOR COV WAVES COCOTB`) so the TB recompiles when it changes.
- Added a **new** run-stage tracking list (none existed before): a
  `rtl-sim-vars-path := $(BUILD-DIR)/.rtl_sim.vars.mk` dump file tracking
  `COCOTB COCOTB_MODULE`, wired as an extra prerequisite + `dump-vars` call
  on the `$(rtl-sim-logs)` pattern rule. Without this, flipping
  `COCOTB_MODULE` alone (no compile-flag change) would silently reuse a
  stale `rtl_sim.log` since nothing else depends on it.

## Root-caused issue (in scope per the brief's pydantic/metadata clause)

The brief's Step 5 says "in the SAME OUT, rerun with `COCOTB=1`... compile
re-triggers." Doing that literally (same `OUT=out_off`, no other cleanup)
**does** re-trigger the VCS invocation (Makefile's `vars-differ` correctly
prints `Repeating compiling TB because variable COCOTB has changed value.`)
but the recompiled command line came out with **zero** cocotb flags. I
root-caused this: `scripts/metadata.py`'s `Ops.CREATE` handler unconditionally
returns early if `metadata.pickle` already exists in the OUT tree —
`RegressionMetadata` is a one-time snapshot per OUT dir, never updated by a
later `make` invocation regardless of new `KEY=VALUE` args. This is
pre-existing behavior, not something COCOTB introduces — the same would
happen flipping `WAVES`/`COV`/`SIMULATOR` in a persisted OUT. The
Makefile-level `.tb.vars.mk` dependency dump lives under `$(BUILD-DIR)`
(`out/build/`), a *sibling* of `$(METADATA-DIR)` (`out/metadata/`), so the
correct way to exercise a same-OUT transition is `rm -rf out/metadata`
(cheap; regenerates on the next `make`) while leaving `out/build` (and its
`.tb.vars.mk`/compiled artifacts) in place — that lets `create_metadata`
actually re-parse the new knob value while the Makefile's own change
-detection still fires genuinely off the persisted dump. I used this
methodology for Step 5 and it reproduced exactly the intended behavior (see
Verification). I did not change `metadata.py`'s create-once semantics
itself — that's a wider-reaching flow characteristic outside Task 4's scope,
and this doesn't block Milestone A/B (Task 5/7 use fresh OUT dirs per run).

## Verification

All runs against `IBEX_CONFIG=opentitan SIMULATOR=vcs`, env sourced from
`ci/env.sh` (venv cocotb 1.9.2 confirmed via `get_cocotb_config_path`).

**Step 4 (off, fresh `OUT=out_off`):** compile succeeded
(`vcs_simv up to date`, `CPU time: ... to compile + ... to elab + ... to link`).
Grep of the actual compile command line for `COCOTB|vpi|cocotb`: **0 hits**.
(The whole-log grep shows 2 harmless hits — `Parsing design file
.../core_ibex_cocotb_if.sv` / `.../core_ibex_cocotb_pkg.sv` — Task 2's files
are unconditionally listed in `ibex_dv.f` and compile away under the absent
`` `ifdef COCOTB_SIM ``, per the Global Constraints; these are filenames
being parsed, not active flags.)

**Step 5 (on, same OUT, `out/metadata` cleared):**
`Repeating compiling TB because variable COCOTB has changed value.` printed;
recompiled command line (105 modules now, incl. `core_ibex_cocotb_if`/
`core_ibex_cocotb_pkg`, up from 103) ends with:
`+define+COCOTB_SIM +vpi -P /localdev/fzhang/ws/ibex/dv/uvm/core_ibex/cocotb_pli.tab -load /localdev/fzhang/ws/ibex/.venv/lib/python3.12/site-packages/cocotb/libs/libcocotbvpi_vcs.so`
— absolute tab path and resolved `.so` confirmed.

**Transition back (`COCOTB=0`, same OUT, `out/metadata` cleared again):**
`Repeating compiling TB because variable COCOTB has changed value.` printed
again; recompiled command line back to 103 modules, cocotb tokens: 0 hits.

**Run-side env logic (isolated check, no full sim — that's Task 5):**
`get_cocotb_config_path()` resolves `.venv/bin/cocotb-config`, `--libpython`
returns a real `.so` path, `PYTHONPATH` builds as
`<ibex_root>:<inherited...>`; negative test against a nonexistent root raises
`RuntimeError: COCOTB=1 but cocotb-config was not found at ...` as required.

All test `out*/` trees removed after verification (`out_off` etc.); nothing
under `out*/` is tracked (`dv/uvm/core_ibex/.gitignore:11` already covers it).

## Concerns
- The metadata create-once characteristic described above is real and
  affects `WAVES`/`COV`/`SIMULATOR` too, not just `COCOTB`. It's out of this
  task's scope to fix, but worth flagging for whoever documents the
  supported knob-flipping workflow (Task 8, `BUILD_AND_SIM.md`): flipping
  any top-level knob in a persisted `OUT` requires clearing `OUT/metadata`
  (not necessarily the whole `OUT` tree) for the new value to actually take
  effect, even though the Makefile's dependency-tracking will *look* like
  it's rebuilding correctly on its own.
- I did not exercise the run-stage `rtl-sim-vars-prereq` end-to-end (that
  needs a real `rtl_sim_run`/test binary, which is Task 5's Milestone-A
  territory); the compile-stage transition proof and the isolated env-dict
  unit checks are the evidence for this task.

## Files Changed
- New: `dv/uvm/core_ibex/cocotb_pli.tab`
- Modified: `dv/uvm/core_ibex/Makefile`, `dv/uvm/core_ibex/scripts/metadata.py`,
  `dv/uvm/core_ibex/scripts/scripts_lib.py`,
  `dv/uvm/core_ibex/scripts/compile_tb.py`, `dv/uvm/core_ibex/scripts/run_rtl.py`,
  `dv/uvm/core_ibex/scripts/ibex_sim.mk`, `dv/uvm/core_ibex/yaml/rtl_simulation.yaml`
