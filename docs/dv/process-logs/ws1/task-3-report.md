# Task 3 Report: Build lowRISC spike (`ci/build-spike.sh`)

Branch: `fzhang/auto-dv-setup`

## Step 1: Verify the gap (red)

```
$ bash -lc 'source ci/env.sh && pkg-config --exists riscv-riscv && echo FOUND || echo MISSING'
...
ibex env: vcs=/tools_vendor/synopsys/vcs/X-2025.06-SP2/bin/vcs gcc=/tools_risc/opensrc/latest/newlib/bin/riscv64-unknown-elf-gcc spike=NOT-BUILT
MISSING
```

Matches expected: `MISSING`.

## Step 2: Build prerequisites

```
$ command -v dtc; command -v cmake; gcc --version | head -1
/usr/bin/cmake
gcc (GCC) 11.2.1 20220127 (Red Hat 11.2.1-9)
```

- `cmake`: present at `/usr/bin/cmake`.
- `gcc`: 11.2.1, matches expected gcc-toolset-11.
- `dtc`: **not** at `/usr/bin/dtc` and not on PATH by default. `module avail dtc` shows `dtc/1.7.2` available (site modulefile `/tools_soc/tt/Modules/modulefiles/dtc/1.7.2`). Not "truly absent" — loaded via `module load dtc/1.7.2` before invoking the build (confirmed `command -v dtc` → `/tools_soc/opensrc/dtc/1.7.2/bin/dtc`, `dtc --version` → `DTC 1.7.2`). This module load is **not** baked into `ci/build-spike.sh` or `ci/env.sh` — it's an invocation-time prerequisite, same as the VCS/Python modules `env.sh` already loads. Whoever runs this script on this site needs `module load dtc/1.7.2` first (or it should be folded into `ci/env.sh` in a future task — out of scope here).

## Step 3: Wrote `ci/build-spike.sh`

Written verbatim from the brief — see `/localdev/fzhang/ws/ibex/ci/build-spike.sh`. No modifications were needed.

## Step 4: Run it

Two false starts, both environmental, before a clean run:

1. **First attempt** — I launched the build wrapped in `nohup ... &` *inside* a tool call that itself used `run_in_background: true`. The double-backgrounding meant the outer tool call returned (and was reaped) immediately after echoing the child PID, killing the detached build before it got past sourcing `ci/env.sh`. No clone occurred. Fixed by passing the real build command directly to `run_in_background: true` with no extra `&`/`nohup`.

2. **Second attempt** — `bash -lc 'source ci/env.sh && module load dtc/1.7.2 && bash ci/build-spike.sh'` exited 1 right after the `dtc` module-load line, before any clone/configure/make output. Root cause: this site's Modules install has a broken `.modulerc` (`Module ERROR: invalid command name "module-hide"` — see the repeated errors in the log from *every* module load, including the VCS/Python ones `env.sh` already does). `module load dtc/1.7.2` successfully loads dtc onto PATH but still returns exit code **1** (confirmed by running it standalone and checking `$?`). Chaining it with `&&` short-circuited before `bash ci/build-spike.sh` ran. Fixed by using `;` instead of `&&` between `module load` and the actual build invocation — a shell/environment quirk unrelated to the build script itself, so no change to `ci/build-spike.sh`.

3. **Successful run**: `bash -lc 'source ci/env.sh; module load dtc/1.7.2; command -v dtc; bash ci/build-spike.sh'`, backgrounded via the tool's native `run_in_background: true`. Exited 0.

```
... (clone, checkout 4b97396656485a129119deaec2ba35e5bf354841, configure, make -j192, make install) ...
spike installed to /localdev/fzhang/ws/tools/spike-ibex-cosim

[exited with code 0]
```

No compiler errors under gcc 11 — the pinned rev built clean, no CXXFLAGS/patches needed.

**Build duration**: much faster than the brief's 10-20 min estimate — this host has `nproc` = 192. Cross-checking filesystem timestamps: task launched ~16:26:33, checked-out source files timestamped ~16:26:38 (clone+checkout ~5s), first object file compiled ~16:26:46, final `spike` binary linked ~16:27:22 (compile phase ~36s), full script (clone → configure → make -j192 → install) exited ~16:27:24 — **total wall time ~51 seconds**. Pinned source revision confirmed: `git -C .../riscv-isa-sim-lowrisc log -1` → `4b97396656485a129119deaec2ba35e5bf354841`, matching `SPIKE_REV` exactly.

Installed artifacts:
```
$ ls /localdev/fzhang/ws/tools/spike-ibex-cosim/bin/
elf2hex  spike  spike-dasm  spike-log-parser  termios-xspike  xspike
$ ls /localdev/fzhang/ws/tools/spike-ibex-cosim/lib/pkgconfig/
riscv-disasm.pc  riscv-fdt.pc  riscv-fesvr.pc  riscv-riscv.pc
```

## Step 5: Verify (green)

```
$ bash -lc 'source ci/env.sh && pkg-config --exists riscv-riscv riscv-disasm riscv-fdt riscv-fesvr && echo ALL-FOUND && $SPIKE_PATH/spike --help 2>&1 | head -3'
...
ibex env: vcs=/tools_vendor/synopsys/vcs/X-2025.06-SP2/bin/vcs gcc=/tools_risc/opensrc/latest/newlib/bin/riscv64-unknown-elf-gcc spike=/localdev/fzhang/ws/tools/spike-ibex-cosim
ALL-FOUND
Spike RISC-V ISA Simulator 1.1.1-dev

usage: spike [host options] <target program> [target options]
```

Matches expected: `ALL-FOUND` plus spike's usage banner.

## Step 6: Commit

```
git add ci/build-spike.sh
git commit -m "[ci] Add lowRISC spike build script for cosim" \
  -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

(Commit SHA recorded in the reply to the controller.)

## Files changed

- `ci/build-spike.sh` (new) — verbatim from the brief, no edits.
- No changes to `ci/env.sh` or any other task's files.

## Self-review

- Script matches the brief's Step 3 content exactly; diffed byte-for-byte against the brief before writing.
- No source patches to spike were needed (gcc 11 built the pinned rev clean) — nothing to document as a CXXFLAGS workaround.
- Left `ci/build-spike.sh` non-executable (`-rw-rw-r--`), matching the sibling `ci/env.sh` convention and the brief's own invocation pattern (`bash ci/build-spike.sh`, never `./ci/build-spike.sh`).
- Nothing under `out/`, `.venv/`, or `/localdev/fzhang/ws/tools/` was added to the commit — verified `git status`/`git diff --stat` shows only the new script.
- `IBEX_TOOLS_DIR`/`SPIKE_INSTALL` defaults in the script match `ci/env.sh`'s exports, so the script is safe to run standalone (without sourcing `env.sh` first) as well as via the documented `source ci/env.sh && bash ci/build-spike.sh` flow.

## Concerns for the controller

1. **`dtc` module load is not automated anywhere.** Anyone re-running this build on this site must `module load dtc/1.7.2` first; it's not in `ci/env.sh` and the brief didn't ask me to add it there (out of scope for this task, and I didn't want to touch a file owned by Tasks 1-2 without being asked). Worth a follow-up task or a note in the brief for whoever runs this next, or documenting it in the build script's own comments if that's judged in-scope for Task 3 after all.
2. **Site's Modules install is broken** (`Module ERROR: invalid command name "module-hide"` on every single `module load`, including the pre-existing VCS/Python loads in `ci/env.sh`). It doesn't block anything in practice — `env.sh` was already tolerating this via `2>/dev/null || true` on the profile source — but the `module load dtc/1.7.2` command itself returns exit status 1 despite succeeding, so it can never be safely chained with `&&`. Flagging this in case it trips up a future script that does something like `module load X && do_thing`.
3. Build was far faster than the brief's 10-20 minute estimate (~51s) due to this host's 192-core count — not a concern, just noting the discrepancy so it isn't mistaken for a truncated/incomplete build in future runs.

## Fix round 1 (post-review)

Two Important findings from review, both ruled by the controller. The two Minor findings (unconditional refetch, partial-clone edge) were explicitly deferred — not acted on.

**Finding 1 — dtc prerequisite un-automated.** The brief's documented invocation (`source ci/env.sh && bash ci/build-spike.sh`) failed on this site without a manual `module load dtc/1.7.2` first. Fix: added to `ci/env.sh`, next to the existing module loads:

```bash
# dtc is a spike build dep (ci/build-spike.sh); this site's module command
# exits 1 even on a successful load, hence the `|| true`.
module load dtc/1.7.2 2>/dev/null || true
```

Also added a one-line header comment to `ci/build-spike.sh`: `# Requires dtc on PATH — loaded by ci/env.sh.`

**Finding 2 — static-libstdc++ comment was untruthful.** Reviewer verified via `ldd` that the produced binaries still carry `DT_NEEDED` on `libstdc++.so.6`/`libgcc_s.so.1` (shared Boost 1.66 on this site re-introduces them), so the original comment's claim didn't hold. Fix: kept the `LDFLAGS` unchanged (still correct for spike's own objects) and rewrote the comment in `ci/build-spike.sh` to state reality:

```bash
# Static gcc runtimes for spike's own objects; note DT_NEEDED on libstdc++.so.6
# remains via shared Boost. Runtime compatibility on this site rests on
# gcc-toolset-11's DTS model (symbol floor = RHEL8 system libstdc++); the
# definitive check is the TB DPI link + simv load in the smoke test.
```

Did not attempt static Boost or a different compiler, per the ruling.

### Re-verification

```
$ bash -lc 'source ci/env.sh && bash ci/build-spike.sh'
... (clone/fetch already-present src, checkout 4b97396656485a129119deaec2ba35e5bf354841,
     configure, make -j192, make install) ...
spike installed to /localdev/fzhang/ws/tools/spike-ibex-cosim

[exited with code 0]
```

Succeeded end-to-end with **no manual dtc step** — confirms Finding 1's fix. Command completed quickly (source tree already present from the first build; this run re-fetched/rechecked-out and relinked).

Step 5 green check re-run, unchanged pass:

```
$ bash -lc 'source ci/env.sh && pkg-config --exists riscv-riscv riscv-disasm riscv-fdt riscv-fesvr && echo ALL-FOUND && $SPIKE_PATH/spike --help 2>&1 | head -3'
...
ibex env: vcs=/tools_vendor/synopsys/vcs/X-2025.06-SP2/bin/vcs gcc=/tools_risc/opensrc/latest/newlib/bin/riscv64-unknown-elf-gcc spike=/localdev/fzhang/ws/tools/spike-ibex-cosim
ALL-FOUND
Spike RISC-V ISA Simulator 1.1.1-dev

usage: spike [host options] <target program> [target options]
```

Confirmed Finding 2's factual claim directly:

```
$ ldd /localdev/fzhang/ws/tools/spike-ibex-cosim/bin/spike | grep -E 'libstdc\+\+|libgcc_s|boost'
	libboost_regex.so.1.66.0 => /lib64/libboost_regex.so.1.66.0 (...)
	libboost_system.so.1.66.0 => /lib64/libboost_system.so.1.66.0 (...)
	libstdc++.so.6 => /lib64/libstdc++.so.6 (...)
	libgcc_s.so.1 => /lib64/libgcc_s.so.1 (...)
```

Matches the reviewer's finding exactly — the rewritten comment is now accurate.

### Files changed (fix round 1)

- `ci/env.sh` — added `module load dtc/1.7.2 2>/dev/null || true`.
- `ci/build-spike.sh` — added a header comment noting the dtc dependency; rewrote the static-libstdc++ comment to state reality.
