# Task 4 Report: RISC-V toolchain

## Summary

Wrote `ci/get-toolchain.sh` verbatim from the brief. The primary path (lowRISC
rv32imcb tarball download) succeeded on the first try — no fallback needed.
Validated it against the exact `opentitan` ISA strings, not a generic probe.

## Step 1: Write ci/get-toolchain.sh

Written verbatim from the brief (17 lines, `chmod +x`). Committed as
`ci/get-toolchain.sh`.

## Step 2: Run it

`bash -lc 'source ci/env.sh && bash ci/get-toolchain.sh'`

Output (module noise omitted, see below for full log path):
```
ibex env: vcs=/tools_vendor/synopsys/vcs/X-2025.06-SP2/bin/vcs gcc=/tools_risc/opensrc/latest/newlib/bin/riscv64-unknown-elf-gcc spike=/localdev/fzhang/ws/tools/spike-ibex-cosim
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 41.8M  100 41.8M    0     0  57.2M      0 --:--:-- --:--:-- --:--:-- 78.9M
riscv32-unknown-elf-gcc (crosstool-NG 1.24.0.498_5075e1f) 10.2.0
```

The `gcc=` line above is from *before* the install (env.sh sourced first,
saw no lowRISC toolchain yet, fell back to the site riscv64 multilib at that
point) — this is expected and not a bug; it just reflects the pre-existing
env state at time of sourcing. The download itself completed cleanly (41.8M
in ~1s, no curl errors) and `riscv32-unknown-elf-gcc --version` from the
freshly-installed tree printed correctly. Full log:
`/tmp/claude-1211405897/-localdev-fzhang-ws-ibex/7c3315ed-cd4a-4f5d-8d62-849954689492/tasks/bwfarapcr.output`

Installed to `/localdev/fzhang/ws/tools/lowrisc-toolchain-gcc-rv32imcb/`
(tarball also left at `/localdev/fzhang/ws/tools/lowrisc-toolchain-gcc-rv32imcb-20220210-1.tar.xz`,
42M — both outside the repo, neither committed).

**Since the lowRISC tarball path succeeded, no fallback was needed.** Per the
task instructions, ran the Step 2 opentitan-ISA validation anyway (the
load-bearing check) rather than treating "gcc --version prints" as sufficient.

### ISA probe (adapted per controller ruling)

The brief's snippet (`ic.get_isas_for_config('opentitan')`, called with a
bare string) doesn't match the actual signature in
`dv/uvm/core_ibex/scripts/ibex_cmd.py`:
`get_isas_for_config(cfg: Config) -> Tuple[str, str]` — it takes a resolved
`Config` object, not a config-name string. Adapted the probe to first resolve
`cfg = ic.get_config('opentitan')` (which internally parses
`ibex_configs.yaml`), matching how `ibex_cmd.py`'s other functions are used
elsewhere in the DV scripts. Also used unqualified `import ibex_cmd` rather
than `import scripts.ibex_cmd`, since `ibex_cmd.py`'s own internal imports
(`from setup_imports import _IBEX_ROOT`, `import ibex_config`) are
unqualified — they assume `dv/uvm/core_ibex/scripts` itself is on
`PYTHONPATH`, exactly as `Makefile`'s `get_pythonpath()` sets it up (adds
`scripts/` directly, not `core_ibex/`).

Reproduced the Makefile's exact PYTHONPATH construction
(`from scripts.setup_imports import get_pythonpath; get_pythonpath()`, run
from `dv/uvm/core_ibex`) rather than hand-rolling a path:

```bash
source ci/env.sh
cd dv/uvm/core_ibex
export PYTHONPATH=$(python3 -c "from scripts.setup_imports import get_pythonpath; get_pythonpath()")
python3 -c "
import ibex_cmd as ic
cfg = ic.get_config('opentitan')
toolchain_isa, iss_isa = ic.get_isas_for_config(cfg)
print('TOOLCHAIN_ISA=' + toolchain_isa)
print('ISS_ISA=' + iss_isa)
"
```

Confirmed `ibex_configs.yaml`'s `opentitan` entry has
`RV32B: "ibex_pkg::RV32BOTEarlGrey"` (line 45), matching the brief's claim.

**Exact output:**
```
PYTHONPATH=/localdev/fzhang/ws/ibex:/localdev/fzhang/ws/ibex/util:/localdev/fzhang/ws/ibex/dv/uvm/core_ibex/scripts:/localdev/fzhang/ws/ibex/dv/uvm/core_ibex/riscv_dv_extension:/localdev/fzhang/ws/ibex/dv/uvm/core_ibex/yaml:/localdev/fzhang/ws/ibex/vendor/google_riscv-dv/scripts
TOOLCHAIN_ISA=rv32imcb
ISS_ISA=rv32imc_Zba_Zbb_Zbc_Zbs_XZbf_XZbp_XZbr_XZbt
```

`TOOLCHAIN_ISA` (`rv32imcb`) is the gcc `-march` value; `ISS_ISA` is the
riscv-dv generator ISA key (base + bitmanip extension list) — both are
exactly what `IBEX_CONFIG=opentitan` emits for every test, independent of
test filtering, confirming the brief's claim.

### gcc -march validation

First attempt hit a sandbox artifact, not a real failure: `echo ... > /tmp/t.c`
returned "Permission denied" (this session's `/tmp` is restricted — the
scratchpad dir must be used instead per environment instructions), yet a
stale/pre-existing `/tmp/t.c` let the compile silently "succeed," which would
have been a false positive. Re-ran cleanly under the session scratchpad
directory instead:

```
$ ls -la .../scratchpad/t.c
-rw-rw-r-- 1 fzhang fzhang 22 Sep  1 17:02 .../scratchpad/t.c
$ "$RISCV_GCC" -march=rv32imcb -mabi=ilp32 -o .../scratchpad/t .../scratchpad/t.c && echo MARCH-OK
MARCH-OK
$ ls -la .../scratchpad/t
-rwxrwxr-x 1 fzhang fzhang 31764 Sep  1 17:02 .../scratchpad/t
```

Fresh 22-byte source, fresh 31764-byte ELF output, `MARCH-OK` printed — this
is a genuine, verified compile of the exact `opentitan`-emitted `-march`
string by the newly-installed lowRISC toolchain. No fallback path exercised
or needed.

## Step 3: Verify env.sh picks it up

`bash -lc 'source ci/env.sh && "$RISCV_GCC" --version | head -1'`

```
ibex env: vcs=/tools_vendor/synopsys/vcs/X-2025.06-SP2/bin/vcs gcc=/localdev/fzhang/ws/tools/lowrisc-toolchain-gcc-rv32imcb/bin/riscv32-unknown-elf-gcc spike=/localdev/fzhang/ws/tools/spike-ibex-cosim
riscv32-unknown-elf-gcc (crosstool-NG 1.24.0.498_5075e1f) 10.2.0
```

`env.sh`'s existing `[ -x "$RISCV_TOOLCHAIN/bin/riscv32-unknown-elf-gcc" ]`
check (Task 1's code, unmodified) now resolves to the freshly-installed
lowRISC toolchain in a fresh shell, as designed — no changes to `env.sh`
were needed.

## Files changed

- `ci/get-toolchain.sh` (new, 17 lines, executable) — committed verbatim
  from the brief.
- Nothing else in the repo touched. Toolchain artifacts
  (`/localdev/fzhang/ws/tools/lowrisc-toolchain-gcc-rv32imcb/` and the
  42M `.tar.xz`) live outside the repo and are not committed.

## Self-review

- Script matches the brief byte-for-byte (diffed the written file against
  the brief's fenced block; identical).
- Idempotent: re-running is safe — `[ -f "$NAME.tar.xz" ]` skips a re-download,
  `rm -rf "$DEST"` before `mv` handles re-runs cleanly.
- Did not hardcode `IBEX_TOOLS_DIR`; script respects the exported env var
  and only falls back to the site-specific default when unset, consistent
  with `ci/env.sh`'s own pattern.
- Verified the tarball/version matches `ci/vars.env`'s
  `RISCV_TOOLCHAIN_TAR_VERSION=20220210-1` and
  `RISCV_TOOLCHAIN_TAR_VARIANT=lowrisc-toolchain-gcc-rv32imcb`.
- Caught and corrected a false-positive in my own validation run (the
  `/tmp` permission-denied issue silently masked by a stale file) before
  reporting the `-march` check as passing — re-ran under a directory I
  could confirm was freshly written to.
- No repo files beyond `ci/get-toolchain.sh` are staged/committed; commit
  message ends with the required `Co-Authored-By` trailer.

## Concerns

- None blocking. Minor note for whoever picks up later WS1 tasks: the ISA
  probe snippet as literally written in the brief
  (`ic.get_isas_for_config('opentitan')`, called with a bare string) does not
  match `ibex_cmd.py`'s actual signature — it needs a `Config` object from
  `ic.get_config('opentitan')` first. Adapted per the controller ruling in
  my task instructions; flagging in case the brief text itself should be
  corrected for future reuse.

## Commit

`78f07202` — `[ci] Add lowRISC rv32imcb toolchain fetch script`

---

## Fix round 1 (review findings)

Two Important findings from review; three deferred Minor findings (checksum,
tarball-kept comment, rm/mv window) were explicitly not acted on per
instruction.

### Finding 1: crash-unsafe download cache

**Problem:** `[ -f "$NAME.tar.xz" ] || curl -fL -o "$NAME.tar.xz" "$URL"` — an
interrupted `curl` (network blip, Ctrl-C, OOM-kill) leaves a truncated
`$NAME.tar.xz` on disk. Every subsequent re-run of the script sees the file
exists, skips the download, and hands `tar` a corrupt archive — failing until
someone manually notices and deletes the stale file.

**Fix:** download to a `.part` sibling and atomically rename into place only
on success, so a truncated download never occupies the trusted filename:

```bash
[ -f "$NAME.tar.xz" ] || { curl -fL -o "$NAME.tar.xz.part" "$URL" && mv "$NAME.tar.xz.part" "$NAME.tar.xz"; }
```

No checksum added (deferred minor, per review).

**Re-verification — cache-hit path still works** (tarball already present
from the original run, script should skip curl and just re-extract/reinstall):

```
$ bash -lc 'source ci/env.sh && bash ci/get-toolchain.sh'
...
ibex env: vcs=/tools_vendor/synopsys/vcs/X-2025.06-SP2/bin/vcs gcc=/localdev/fzhang/ws/tools/lowrisc-toolchain-gcc-rv32imcb/bin/riscv32-unknown-elf-gcc spike=/localdev/fzhang/ws/tools/spike-ibex-cosim
riscv32-unknown-elf-gcc (crosstool-NG 1.24.0.498_5075e1f) 10.2.0
```
No curl progress bar printed (confirmed the `[ -f ... ]` guard short-circuited
on the existing good tarball) — script still completed successfully end to
end.

**Crash simulation — stale `.part` must not poison the cache:**

```
$ cd /localdev/fzhang/ws/tools
$ mv lowrisc-toolchain-gcc-rv32imcb-20220210-1.tar.xz lowrisc-toolchain-gcc-rv32imcb-20220210-1.tar.xz.bak
$ echo "garbage-truncated-download" > lowrisc-toolchain-gcc-rv32imcb-20220210-1.tar.xz.part
$ ls -la lowrisc-toolchain-gcc-rv32imcb-20220210-1.tar.xz.part
-rw-rw-r-- 1 fzhang fzhang 27 Sep  1 17:07 lowrisc-toolchain-gcc-rv32imcb-20220210-1.tar.xz.part
```

This reproduces the crash state: no finished `.tar.xz`, but a stray
truncated `.part` left behind, exactly as an interrupted prior run would
leave it. Ran the script against this state:

```
$ cd /localdev/fzhang/ws/ibex
$ bash -lc 'source ci/env.sh && bash ci/get-toolchain.sh'
...
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 41.8M  100 41.8M    0     0  94.8M      0 --:--:-- --:--:-- --:--:-- 94.8M
riscv32-unknown-elf-gcc (crosstool-NG 1.24.0.498_5075e1f) 10.2.0
```

Post-run state:
```
$ ls -la lowrisc-toolchain-gcc-rv32imcb-20220210-1.tar.xz.part
ls: cannot access '...': No such file or directory
$ ls -la lowrisc-toolchain-gcc-rv32imcb-20220210-1.tar.xz
-rw-rw-r-- 1 fzhang fzhang 43859232 Sep  1 17:07 lowrisc-toolchain-gcc-rv32imcb-20220210-1.tar.xz
$ file lowrisc-toolchain-gcc-rv32imcb-20220210-1.tar.xz
lowrisc-toolchain-gcc-rv32imcb-20220210-1.tar.xz: XZ compressed data
```

The 27-byte garbage `.part` was correctly ignored (the existence guard only
checks the finished `.tar.xz` name, which was absent), `curl` re-downloaded
the full 41.8M cleanly, and the atomic `mv` left a valid 43,859,232-byte XZ
archive with no leftover `.part` — no stale-cache poisoning. Removed the
`.bak` backup afterward; end state is identical to before the simulation
(same toolchain, re-fetched fresh).

### Finding 2: MARCH-OK compile not provably tied to the lowRISC gcc

**Problem:** original validation ran `RISCV_GCC` resolution and the compile
as separate shell invocations/snippets, and never echoed the resolved
`$RISCV_GCC` path next to the compile — so the passing `MARCH-OK` couldn't be
proven to have come from the newly-installed lowRISC gcc rather than some
other toolchain left on `PATH`.

**Fix:** no code change (script is already correct); re-ran the validation
as one continuous transcript in a single fresh shell, echoing the resolved
path immediately before using it:

```
$ bash -lc 'source ci/env.sh; echo "RISCV_GCC=$RISCV_GCC"; "$RISCV_GCC" --version | head -1; echo "int main(){return 0;}" > <scratch>/t4.c; "$RISCV_GCC" -march=rv32imcb -mabi=ilp32 -o <scratch>/t4 <scratch>/t4.c && echo MARCH-OK && ls -la <scratch>/t4'
...
RISCV_GCC=/localdev/fzhang/ws/tools/lowrisc-toolchain-gcc-rv32imcb/bin/riscv32-unknown-elf-gcc
riscv32-unknown-elf-gcc (crosstool-NG 1.24.0.498_5075e1f) 10.2.0
MARCH-OK
-rwxrwxr-x 1 fzhang fzhang 31768 Sep  1 17:08 <scratch>/t4
```

This single transcript now directly chains: `RISCV_GCC` resolves to the
lowRISC-installed binary -> that exact binary's `--version` banner ->
that exact `$RISCV_GCC` invocation compiles `-march=rv32imcb -mabi=ilp32`
successfully -> a freshly-timestamped 31768-byte ELF is produced. No
ambiguity about which toolchain was exercised.

### Fix-round verification summary

- `ci/get-toolchain.sh`: cache-hit path re-verified working; crash/stale-`.part`
  scenario simulated and confirmed non-poisoning; atomic download logic is
  the only functional change.
- gcc validation re-run as one continuous, unambiguous transcript per review
  instruction.
- No other files touched. Committed as a follow-up commit with the same
  co-author trailer.
