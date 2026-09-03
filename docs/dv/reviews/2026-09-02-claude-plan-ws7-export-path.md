# Cross-model pre-execution review — WS7+WS6 re-cut plan (export path)

**Reviewer:** claude CLI 2.1.258 (subagent); model: claude-opus-5; extended reasoning; SUBSTITUTE reviewer per CLAUDE.md fallback clause — codex unavailable (spend cap), owner authorized
**Date:** 2026-09-02
**Target:** `docs/superpowers/plans/2026-09-02-ws7-knowledge-fence.md`, sha256 `66bb945c535a4185f2551f67b79995f409215cfc3da2ac3abfe1ae2c4a45efaa` (verified, working tree, uncommitted)
**Authorities:** spec `2026-09-01-auto-dv-setup-design.md` §WS5/§WS6/§WS7; amendment `2026-09-02-zone-a-fence-scope-amendment.md` v2.1 (BINDING); session-1 handoff items 1–2 and open items 4–5; `DV_prompt.txt` Sections 2/3/8/12 (untracked, owner-delivered — cited structurally)

---

TARGET: docs/superpowers/plans/2026-09-02-ws7-knowledge-fence.md@66bb945c

Scope: single targeted round per owner speed directive. The v1 snapshot-branch design is superseded
by owner directive and is not re-litigated; the deferred list is checked for completeness and honesty
only. Wave-1 execution is concurrent by recorded ruling, so findings are ordered to put the ones that
invalidate in-flight Wave-1 work first (C1–C4 and Ma1–Ma3 all land in Task 1's `DENY` array and
Task 2's overlay set — both being written right now).

## Mechanism assessment (the question asked)

**The export mechanism is sound in its core claim and is strictly stronger than v1 on one axis.**
`git archive HEAD | tar -x` into a fresh `git init` produces an object store that never contained a
fenced blob and has no remote, so the spec's "fetch master" escape case (spec:163) is not merely
blocked but *unrepresentable* — v1's published-branch clone kept an `origin` pointing at a repository
where fenced blobs live on other refs, and only `--single-branch` stood between Zone A and
`git fetch origin master`. `git archive` also ships only tracked-at-HEAD content, so gitignored run
products (`out*/`, `*.fsdb`, `*.vdb`, `*.daidir`) are absent by construction rather than by scan;
selftest check (c) is cheap insurance over a property the mechanism already guarantees. `.gitattributes`
currently sets no `export-ignore`, so nothing is silently omitted today. `.agents/skills/shared` is a
*relative* symlink (`../../.claude/skills`) and survives the export intact.

**What the mechanism does not carry over, and the plan does not say so:** v1 inherited spec:139's
rule that the builder *rejects any path it cannot classify*. A deny-array-only builder is
allow-by-default: every file added to `master` after today ships to Zone A unless someone remembers
to deny it. Selftest check (b) cannot detect this — it asserts the absence of exactly the paths the
script just deleted, so it proves the deletion ran, never that the list is complete. That gap is not
theoretical: the deny array as drafted already misses eight classes of fenced collateral that are in
the tree right now (C1–C3, Ma1–Ma3 below, all found by mechanical grep). Fixing the eight items
without fixing the shape leaves the next reviewer to find the ninth.

## Findings

**[Critical][plan:75-76] `dv/**` default-deny is replaced by an enumeration of five subdirectories, and two existing DV testbenches ship.**
The deny array lists `dv/uvm`, `dv/cosim`, `dv/verilator`, `dv/formal`, `dv/riscv_compliance`. The
spec's deny root is `dv/**` wholesale with `dv/auto_dv/**` allowlisted back (spec §WS7 "Fenced
content"), and the amendment keeps that row "consistent as written" (amendment:137). Under the plan's
enumeration, `git ls-tree` shows 37 `dv/` files surviving, including:
- `dv/cocotb/{__init__.py,ibex_cocotb.py}`, `dv/cocotb/common/{handshake.py,uvm_bridge.py}`,
  `dv/cocotb/tests/{test_hello.py,test_irq_from_python.py}` — the WS2 cocotb TB. `uvm_bridge.py` and
  `handshake.py` are the *implementation* of the alive-bit/objection/finish-polling handshake that
  amendment change 2 requires TB_CONTRACT.md to describe only as a generic PATTERN with "no
  existing-TB module names, event names, manifest paths". Shipping the source defeats the rewrite
  entirely. `uvm_bridge.py` and `test_irq_from_python.py` both match the plan's own identifier probe
  set.
- `dv/cs_registers/**` (23 files) — a complete existing CSR testbench with a C++ reference model
  (`model/register_model.{cc,h}`, `reg_driver/`, `rst_driver/`, `tb/tb_cs_registers.sv`). This is
  prior-art DV for a block Zone A must verify from scratch, including the reference-model approach.
— **Recommendation:** invert to the spec's shape: `DENY=( "dv" ... )` with an explicit
`ALLOW=( "dv/auto_dv" )` re-add applied after deletion (stage the allowlisted subtree aside, delete
`dv`, restore). Same change makes `dv/auto_dv/mutations/README.md` survive deliberately rather than
incidentally.

**[Critical][plan:76] The `vendor/riscv-isa-sim` deny entry misses the lock file and the vendor description, which disclose the fenced Spike fork by URL and branch.**
The repo carries `vendor/riscv_isa_sim.lock.hjson` and `vendor/riscv_isa_sim.vendor.hjson` —
*underscores*, siblings of the hyphenated directory, so no prefix or path match on
`vendor/riscv-isa-sim` removes them. `riscv_isa_sim.vendor.hjson` contains
`url: "https://github.com/lowrisc/riscv-isa-sim"`, `rev: "mseccfg_tests"`, and the `tests/mseccfg`
mapping — i.e. exactly the disclosure the amendment denies `ci/build-spike.sh` for ("still discloses
that a spike cosim referee exists and how it is built", amendment:135). `DV_prompt.txt` Section 12
precondition 6 is explicit and mechanical: *no path matching `vendor/riscv?isa?sim*` exists in the
clone — not the directory, not the lock file, not the vendor description.* The plan fails that check
as written.
— **Recommendation:** deny the glob `vendor/riscv?isa?sim*` (matching the precondition's own pattern),
not the directory name, and add precondition 6's exact pattern to selftest check (b).

**[Critical][plan:76] `vendor/google_riscv-dv` is denied outright, contradicting the amendment's launch precondition that it be present and pristine, and no pristine-replacement step exists anywhere in the plan.**
Amendment change 5 lists "pristine upstream `vendor/google_riscv-dv` at the locked revision" as a
launch precondition, and `DV_prompt.txt` Section 12 precondition 6 checks the `rev` in
`vendor/google_riscv-dv.lock.hjson` against a dated `riscv-dv-verified-on:` line in `FENCE.md`
attesting an empty tree-diff against upstream, plus "no file under `vendor/google_riscv-dv/` contains
the string `Ibex Specific`". Three consequences the plan does not address:
1. Deleting the tree makes the `rev` check unsatisfiable unless `vendor/google_riscv-dv.lock.hjson`
   is deliberately retained — and a naive `rm -rf "$STAGE/vendor/google_riscv-dv"*` would take the
   lock file with it.
2. The checked-in tree is *not* pristine: `grep -rl 'Ibex Specific' vendor/google_riscv-dv/` returns
   `src/riscv_instr_pkg.sv` and `euvm/riscv/gen/riscv_instr_pkg.d`. So "ship it as-is" also fails.
   The spec's stated action is *replace with pristine upstream at `71666eba`* (spec §WS7), which
   requires a network fetch and a verified empty diff — no plan step does this.
3. `vendor/google_riscv-dv.vendor.hjson` (not denied, sibling name) declares
   `patch_dir: "patches/google_riscv-dv"`, disclosing that local patches exist even after
   `vendor/patches/**` is denied.
— **Recommendation:** pick one and write it as a step: (a) fetch upstream riscv-dv at the lock rev
into the stage, verify empty tree-diff, retain the lock file, delete `*.vendor.hjson`, and emit the
`riscv-dv-verified-on:` line into FENCE.md; or (b) omit riscv-dv entirely and take this back to the
owner as an amendment change-5 deviation. Do not leave it implicit in a deny entry.

**[Critical][plan:117-121,126-165] The Zone A tree cannot satisfy the shipped validator and `DV_prompt.txt` Section 12 item 9 at the same time; the plan ships both and reconciles neither.**
Two hard, mechanically-checkable contradictions, both created by files the plan ships unmodified:
1. `docs/dv/dv_principles.md:133-150` is the hash-anchored canonical TRUST-TRIAD block, and its
   rule 2 text at line 142 reads ``run with `+disable_cosim=1` ``. `.codex/compat/validator.py`
   (`TRIAD_FILES`, `check_triad`) requires that block **byte-identical** in
   `.claude/skills/mutation-check/SKILL.md`, `.claude/skills/fcov-expectation/SKILL.md`, and
   `.claude/agents/ibex-test-generator.md` — all three of which the overlay rewrites, and all three
   of which item 9 scans for the string `disable_cosim`. Byte-identical mirror ⇒ item 9 fails;
   item-9-clean variants ⇒ validator fails.
2. `.codex/compat/validator.py:52-59` (`REQUIRED_POLICY_CLAUSES`) requires the literal string
   `docs/dv/reviews/` **in CLAUDE.md**; item 9 forbids that exact string in CLAUDE.md. The plan's
   Zone A CLAUDE.md cannot be written.
Additionally, `DV_prompt.txt` precondition 5 requires `docs/dv/dv_principles.md` to carry a dated
`fence-integrity: PASS` line attesting it names no existing test, TB module, or DV path — but the
full-tree file cites `docs/dv/evidence/` and `docs/dv/reviews/` at lines 130-132 and 156. The plan
treats dv_principles as a *full-tree edit only* (plan:117); it must also be an **overlay variant**.
— **Recommendation:** add three files to the overlay — `docs/dv/dv_principles.md` (Zone A canonical
triad block whose rule-2 sentence carries the Zone A operationalization from `DV_prompt.txt`
Section 8 instead of the plusarg; evidence/review paths rewritten to `dv/auto_dv/`; dated
`fence-integrity: PASS`), `.codex/compat/validator.py` (policy clause → `dv/auto_dv/reviews/`), and
re-anchor the three mirrors against the Zone A canonical block. State explicitly in Task 2 that each
mirror must be byte-identical to the **Zone A** canonical block. Then re-run
`python3 .codex/compat/validator.py --repo-root <export>` as a selftest check, which is the real
proof and costs one line.

**[Critical][plan:243-256, 137-143, 164-165] The launch preconditions the plan exists to satisfy are not produced by any step, so the stated Goal (invariant 2 lifts) is not reached at plan end.**
`DV_prompt.txt` Section 12 is a mechanical checklist the Orchestrator runs before spawning any
teammate. Against the plan:
- **precondition 3** — `SIM_RECIPE.md` must carry four dated marker lines: `executed-on:`,
  `submission-command:`, `spike-built-on:`, `fence-integrity: PASS`. None are mentioned at
  plan:137-143 or in Task 4. `spike-built-on:` requires that upstream `riscv/riscv-isa-sim` was
  **cloned over the network and built on this site** — an entire piece of work (network fetch,
  dependency build, wall-clock cost) that appears nowhere in the plan and is not on the deferred
  list either.
- **precondition 2** — `FENCE.md` must carry a `ci/` allowlist naming at least `ci/env.sh`,
  `ci/setup-venv.sh`, `ci/get-toolchain.sh`, `ci/check_fcov_expectations.py`, `ci/mcp/`,
  `ci/reviews/`. The Task 5 Step 1 outline (plan:251-256) has no allowlist section. It also must
  carry the `riscv-dv-verified-on:` line (C3).
- **precondition 5** — Zone A `CLAUDE.md` and `AGENTS.md` must contain the marker `FENCE-ZONE: A`
  **within their first ten lines**. Not in plan:126-130.
- **preconditions 4, 5, 9** — dated `fence-integrity: PASS` lines required on `TB_CONTRACT.md`,
  `dv_principles.md`, and `ci/reviews/GUIDE.md`. None mentioned.
- **precondition 7** — `dv/auto_dv/.gitignore` must ignore **`work/`**. plan:164 specifies
  `out*/` and "sim junk". One word, and it is a hard launch blocker.
- **precondition 9** — `run_codex_review.sh` must contain each of the five rubric basenames
  literally, must **not** contain `ci/reviews/*.md`, and must contain `dv/auto_dv/reviews/`.
  plan:154 says only that the wrapper "asserts the positive rubric list".
— **Recommendation:** add a Task 5 Step 0 that transcribes Section 12 items 2–9 into a checklist and
a Task 4 Step 6 that *runs* it against the export (it is entirely grep-able), and put the upstream
Spike clone+build in Task 4 as its own step with its own timeout — or, if the owner wants it out of
scope, put it on the deferred list and state that generation cannot launch until it is done. Either
is honest; silence is not.

**[Major][plan:77-78] `docs/dv/**` is enumerated rather than default-denied, and two derived documents that paraphrase fenced knowledge ship.**
The deny array names `BUILD_AND_SIM.md`, `COSIM.md`, `evidence`, `reviews`, `process-logs`. Two
tracked files survive:
- `docs/dv/known-followups.md` — cites `BUILD_AND_SIM.md`, names the `FCOV_NO_DEFAULT_SEQUENCE`
  guard (an item-9-scanned string) and, worse, describes an unclosed hole in the **human fcov
  model** ("enumerating the controller FSM's legal transitions explicitly"). That is coverage-model
  content the three-scope policy says never reaches Zone A.
- `docs/dv/tt-regress-assessment.md` — cites the spec by path and line and describes the regression
  flow's design rationale.
Both fall squarely under spec §WS7's "derived/infra documents that paraphrase fenced knowledge".
— **Recommendation:** deny `docs/dv` and allowlist back exactly the declassified set the spec and
session-1 open item 5 name: `TB_CONTRACT.md`, `FENCE.md`, `SIM_RECIPE.md`, `dv_principles.md`. Same
inversion as C1; it also removes the maintenance burden for every future `docs/dv/` file.

**[Major][plan:126-165] `ci/mcp/probes/fsdb_probe.py` is neither denied nor overlaid, and it contains a fenced TB identifier — precondition 9 scans `ci/mcp/` and fails.**
Running item 9's exact string set over its exact file list on the current tree returns 21 files;
every one is covered by the overlay except `ci/mcp/probes/fsdb_probe.py`, which matches the plan's
own probe identifier `core_ibex_tb_top` (it points at an FSDB produced by the existing TB).
`ci/mcp/probes/mcp_probe.py` is clean.
— **Recommendation:** add a Zone A `ci/mcp/probes/fsdb_probe.py` variant to the overlay (the FSDB
path becomes a `dv/auto_dv/` out-tree path), and replace Task 2 Step 3's five-string self-check with
item 9's exact ten-string scan over item 9's exact file list.

**[Major][plan:78-79] `.github/**` re-discloses the cosim referee, its build, and its directed test names after the three `ci/` cosim scripts are denied.**
`.github/actions/ibex-rtl-ci-steps/action.yml:84-99` sources `ci/setup-cosim.sh`, builds
`lowrisc:ibex:ibex_simple_system_cosim`, and invokes `./ci/run-cosim-test.sh` on `CoreMark`,
`pmp_smoke`, `dit_test`, `dummy_instr_test`. `.github/workflows/ci-formal.yml:44` does `cd dv/formal`.
Denying the scripts while shipping the workflow that names and drives them leaves the disclosure
intact and adds dangling references.
— **Recommendation:** deny `.github` (it is Zone B CI for the existing flow; Zone A owns its own
regression scripts per amendment:175-178). If any of it must ship, ship a Zone A variant.

**[Major][plan:83,106] Identifier check (d) includes `+disable_cosim`, which a deliberately-shipped file contains, so check (d) cannot pass — and the claim that `--pre-overlay` proves a–d is false.**
`docs/dv/dv_principles.md:142` ships to Zone A by design (amendment:179-183) and contains
`+disable_cosim=1`. With the probe set as drafted, the full export fails check (d) permanently, not
just before the overlay lands. Separately, plan:106 asserts `--pre-overlay` "still proves a–d" —
pre-overlay the export also contains `sim-debug`, `mutation-check`, `fcov-expectation`,
`ibex-test-generator`, `ci/env.sh`, and `ci/reviews/assertion-integrity.md`, all of which match the
probe set. Only a–c and f–g are provable pre-overlay.
— **Recommendation:** align the probe set with item 9's string list (which deliberately omits
`dv_principles.md` from its file list), scope the identifier grep to item 9's file list plus a
whole-export scan for the strings that are unconditionally forbidden (`core_ibex`,
`riscv_arithmetic_basic_test`, `mcounteren_test`, `spike_cosim`), and correct plan:106 to "a–c, f, g".

**[Major][plan:86-88] The planted canary proves anti-vacuity for check (d) only; checks (b), (c) and (e) have no failure probe.**
One canary file bearing a fenced identifier exercises the identifier grep and nothing else. A
mis-implemented deny loop, a `find` with a wrong predicate, or an MCP parse that never matches would
all pass silently — the exact failure mode `dv_principles.md` §6 anti-vacuity is about, applied here
to the verifier rather than to a checker.
— **Recommendation:** make the canary an enum: `CLEANROOM_CANARY=deny|artifact|mcp|identifier`,
planting respectively a file under a denied root, a zero-byte `x.fsdb`, a remote `url` entry in the
staged `.mcp.json`, and the identifier file. Assert a *named* failure for each — a run that fails for
the wrong reason is a passing canary that proves nothing.

**[Major][plan:40-43] The deferred list is incomplete on the three items that change what the fence covers, not just how it is delivered.**
Missing from the "if needed later" list, and therefore reading as covered when it is not:
1. **spec:139's unclassifiable-path rejection** — the single fence property genuinely lost in the
   re-cut (see Mechanism assessment). This is not snapshot machinery; it is what makes the fence
   default-deny.
2. **spec §WS7 enforcement-stack layer 2** — the Zone A agent runtime profile (permission rules
   denying `git fetch`/remote mutation and network fetches of ibex upstream/fork URLs, codex
   sandboxed with network restricted). The amendment retired only the "no MCP servers" clause of
   layer 2; the rest stands, and the plan neither implements nor defers it. `.claude/settings.json`
   ships unmodified (it is currently benign — one env var — but it is the file that would carry the
   permission rules).
3. **amendment change 4's escape cases** — "fetch master", "read sibling clone" (which the amendment
   explicitly *retains as the escape test for the tool data-reach ruling*), "fetch upstream ibex DV",
   and the **negative control** (fsdb-mcp opens a Zone A-produced FSDB). The plan defers "the full
   escape-test harness beyond the script's self-verify" without saying that this is what the harness
   contains — and the self-verify tests clone *contents*, never clone *boundary behaviour*.
— **Recommendation:** name all three in the deferred list with their authority sections, and fold
the cheapest one now: a positive inventory tripwire. Write `git archive`'s path list to
`ci/cleanroom-inventory.txt`, commit it, and have `make-cleanroom.sh` fail on any path present in the
export but absent from the file. Roughly ten lines, and it converts the deny array from
allow-by-default to triage-on-add, which is the property spec:139 was protecting.

**[Major][plan:14-18, Task 4 Step 1] "Updates are re-exports" is undefined against a Zone A working tree that has real work in it.**
The default destination is a fixed sibling path and Task 4 Step 1 writes to
`/localdev/fzhang/ws/ibex-cleanroom`. What happens on the second run — when Zone A has commits on
`cleanroom/<topic>` under `dv/auto_dv/**` — is not stated: clobber, refuse, or `git init` on top of
existing history are three different answers, and the first destroys the challenge's work product.
— **Recommendation:** one paragraph in FENCE.md plus one guard in the script: refuse a non-empty
DEST unless `--force`; document the update workflow as export-to-a-new-dir then
`git format-patch`/`git am` the `dv/auto_dv/**` commits across (which `check-landing.sh` already
validates).

**[Major][plan:244-249,257] The supersession list is missing two of its six entries, and the invariant-2 edit as scoped will fail the validator.**
Amendment:142-151 names six targets. Task 5's Files line covers `ci/mcp/README.md`, the three wrapper
headers, `.codex/config.toml`, and `ci/env.sh`; it omits **spec §WS5's zone-scoping paragraph and its
WS5 gate item** and **spec §WS7's enforcement-stack item 2 and its "query an MCP" escape case**. Task 4
Step 4 closes the WS5 *ledger* line, which is a different artifact from the spec text the amendment
names. Separately: `AGENTS.md` is absent from Task 5's Files list, but
`.codex/compat/validator.py:127-133` asserts the CRITICAL-INVARIANTS block byte-identical between
`CLAUDE.md` and `AGENTS.md` — editing invariant 2 in one file makes Step 2's "validator PASS"
impossible.
— **Recommendation:** add `docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md` and `AGENTS.md`
to Task 5's Files list; edit the invariant in both files in the same commit.

**[Major][plan:167-168] Task 2's ChipSmart discovery grep is two strings where the acceptance check is ten, so the fix set is under-scoped by construction.**
`grep -rl 'dv/uvm/core_ibex\|BUILD_AND_SIM' .claude/skills/` finds `create-tb`,
`rtl-workspace-exploration`, `vcs-rtl-compat`, `simple-english`. Item 9 additionally scans for bare
`core_ibex`, `COSIM.md`, `disable_cosim`, `FCOV_NO_DEFAULT_SEQUENCE`, `metadata.pickle`,
`docs/dv/reviews/`, `ci/reviews/test-overlap`, `ci/reviews/fence-integrity` over `.claude/skills/`,
`.claude/agents/`, `ci/env.sh`, `ci/mcp/`, `ci/reviews/`, `CLAUDE.md`, `AGENTS.md`,
`.codex/config.toml`, `TB_CONTRACT.md`, `SIM_RECIPE.md`.
— **Recommendation:** replace both the Step 1 discovery grep and the Step 3 self-check with item 9's
exact scan; that makes discovery, self-check, and acceptance the same command.

**[Major][plan:222-230] Task 4's gate is executable in principle but is under-specified against the `opentitan` build configuration, and it produces no `executed-on:` marker.**
The DUT ruling and the config make the smoke TB more than a clock generator: `opentitan` sets
`BaseIsa = BaseIsaRV32IorCHERIoT` (the 23 CHERI-touching RTL files must be in the compile even though
CHERIoT is out of coverage scope), `ICache=1`/`ICacheECC=1`/`ICacheScramble=1` (the TB must supply
the icache RAMs and answer the core's scramble-key request as test equipment, per `DV_prompt.txt`
Section 2), and `SecureIbex=1`. `RegFile = RegFileFF` does confirm the ruling's
`ibex_register_file_ff`. Because change 6 excludes TB file lists from SIM_RECIPE, Task 4 must assemble
an RTL filelist by hand or drive fusesoc from the shipped `.core` files — feasible (all `*.core` and
`rtl/**` ship) but not a 5-minute step, and `timeout 2700` for a first-ever hand-rolled elaboration
of this configuration plus any recipe-defect iterations is optimistic.
— **Recommendation:** state in Step 2 that the wrapper ties `cheriot_enable_i` to `IbexMuBiOff`, ties
off or stubs the icache RAM and scramble-key interfaces, and names how the RTL filelist is obtained;
raise the budget or make the iteration loop explicitly multi-invocation; and have the step write the
dated `executed-on:` marker into `ci/cleanroom-overlay/docs/dv/SIM_RECIPE.md` as its output (per
precondition 3), so the gate and the precondition are the same artifact.

**[Minor][plan:92] `set -uo pipefail` without `-e` means a failed `tar -x`, a failed deny deletion, or a failed overlay copy does not abort the build.**
Check (b) would catch a failed deletion and check (e) a failed `.mcp.json` overlay, but a partial
extract or a partial skill-overlay copy would pass every check and ship.
— **Recommendation:** `set -euo pipefail`, with explicit `|| die` on the pipeline stages.

**[Minor][plan:204] The mex gate query scopes `ci/jenkins`, a path Step 2 configures mex to ignore.**
`mex graph scope ci/jenkins` returns nothing by construction once the fenced globs are in the ignore
config, so the gate either fails or is satisfied vacuously.
— **Recommendation:** scope a visible DV-adjacent target instead — `ci/mcp/`, `ci/env.sh`, or
`util/` — and record why.

**[Minor][plan:191,196-199] Mirroring the deny globs into mex's ignore config creates a second copy of the list, contradicting the plan's own "one authority" claim (plan:41-42).**
— **Recommendation:** have Task 3 read the `DENY` array out of `make-cleanroom.sh` (or have the
script emit it with a `--print-deny` flag) rather than transcribing it; add a check that the two
agree.

**[Minor][plan:176-179] Task 2 Step 4's commit line lists `DV_prompt.txt` in the pathspec and then says not to add it.**
— **Recommendation:** drop it from the pathspec string; keep the explanatory note.

**[Minor][plan:120] The carried "verify, don't edit" ruling covers precondition 6 but not item 9, which is also already extended in the delivered prompt.**
`DV_prompt.txt` Section 12 item 9 already names `AGENTS.md` and `.codex/config.toml` in its scanned
set and already asserts the five-rubric list and the `run_codex_review.sh` string conditions —
i.e. amendment change 3's mechanical extension is already applied. The plan instructs an edit
(plan:118-119) that is at best a no-op on an owner-delivered, sign-off-bearing document. Precondition
6 is likewise already split.
— **Recommendation:** extend the carried ruling to item 9: verify and record both, edit neither.

**[Minor][plan:74-80] "the six verification RSTs under `doc/`" is not enumerated, and one adjacent file is worth a decision.**
The six are `doc/03_reference/{testplan,coverage_plan,verification,verification_stages,cosim}.rst`
plus `doc/01_overview/verification_overview.rst`. `doc/03_reference/images/tb*.svg` correctly covers
both `tb.svg` and `tb2.svg`. `doc/02_user/system_requirements.rst` mentions riscv-dv as a tool
requirement — benign under the "upstream riscv-dv is fair game" rule, but worth an explicit "allowed"
note so the next reviewer does not re-open it. Denying the six leaves dangling toctree entries in the
Sphinx build; harmless to the fence, worth one line in FENCE.md.
— **Recommendation:** enumerate the six literally in the `DENY` array with their `# why` comments.

**[Minor][plan:79-80] The selftest does not assert precondition 9's "`ci/reviews/` contains exactly six files".**
The overlay supplies five rubrics plus GUIDE.md and the deny array removes `fence-integrity.md` and
`test-overlap.md`, so the property should hold — but it is the precondition most likely to break
silently when someone adds a rubric to the full tree.
— **Recommendation:** add it as selftest check (h); it is one `find | wc -l` plus a name list.

**[Minor][plan, Task 5] Session-1 open item 4 — "validator no-pyyaml fallback weaker than main path (rides WS7 validator work)" — is silently dropped.**
The plan touches the validator nowhere. It pairs naturally with C4's Zone A validator variant.
— **Recommendation:** fold it into C4's validator work or move it to the deferred list by name.

**[Minor][plan:226] "the assertion exercised (force a bench-level stimulus toggle)" is a weaker gate than the repo's own anti-vacuity discipline for one extra line of work.**
An assertion that was evaluated proves the compile wired it up; an assertion that was made to *fail
once and then pass* proves it can discriminate.
— **Recommendation:** "toggle the stimulus so the assertion fires once (capture the failure line),
then restore and show it passing" — red→green, consistent with plan:46-47's own evidence rule.

**[Info][plan:29-31] The amendment's triage tables were diffed item by item; the rows the plan gets right are worth recording so the next round does not re-check them.**
Over-fenced table: `dv/uvm/core_ibex` mechanics → SIM_RECIPE ✔; `BUILD_AND_SIM.md`/`COSIM.md` split ✔;
`ci/reviews/*` positive Zone A set ✔ (exactly six files, matching precondition 9); skills/agents/
`CLAUDE.md`+`AGENTS.md`/`.codex/config.toml` variants ✔ (modulo Ma2, Ma9); MCP servers ✔;
`vendor/lowrisc_ip/dv/**` correctly *not* denied ✔. Under-fenced table: `formal/**` ✔;
`ci/jenkins/**` ✔; the three `ci/` cosim scripts ✔ (modulo Ma3); `vendor/patches/**` ✔;
`vendor/riscv-isa-sim` ✘ (C2). Three rows are prompt/FENCE.md *wording* actions with no plan step:
OpenTitan `hw/ip/rv_core_ibex/dv/**` ("add to the prompt's deny wording"), CHERIoT-Ibex `dv/**`
(URL/web deny), and the readthedocs URL deny. The plan's FENCE.md outline (plan:251-256) has no
URL/web-deny section at all.
— **Recommendation:** add a "denied by URL, not by path" section to FENCE.md Step 1 carrying those
three rows; they are the only fence rules a path-based builder structurally cannot enforce.

**[Info][plan:183-208] WS6 versus spec §WS6: nothing is dropped.**
Every spec §WS6 element is present — `npm install -g mex-agent`, `mex setup`, wiki from the repo,
anchor section merged into canonical `CLAUDE.md` with `AGENTS.md` unchanged, the SV-not-parsed limit
documented, the fenced-glob ignore config, the wiki-authoring rule ("no page may paraphrase fenced
content"), the two-instance model (full tree in Task 3, cleanroom in Task 4 Step 3), and both gate
items (`mex check` green, one `mex graph scope` query). The BLOCKED-on-package-name stop is a good
call. Only Mi2 and Mi3 apply. Note that running Task 3 in Wave 1 means the graph predates
`ci/cleanroom-overlay/**`; harmless, but a re-index at Task 4 would make the wiki match the final
layout.

## Assessment

The delivery mechanism is the right call and is technically stronger than the design it replaces on
the escape case that mattered most. The plan's structure — TDD selftest first, canary anti-vacuity,
an irreducible compile-and-run gate, honest "recipe defect ⇒ fix the recipe, never the fence"
handling — is the right shape, and the WS6 fold is complete. What it does not yet have is a fence
that is default-deny: five of the six Criticals and three of the Majors are the same root cause in
different clothes, namely that an enumerated deny list was substituted for the spec's deny-root plus
allowlist plus reject-the-unclassifiable, and the enumeration is measurably incomplete against the
tree as it stands today (two live testbenches, the Spike fork's URL and branch, two fcov-bearing
documents, one probe script, and the CI workflow that names the cosim tests all ship). The second
root cause is that `DV_prompt.txt` Section 12 was read for its rulings but not for its checklist: it
is the mechanical acceptance test for this entire workstream, and roughly a dozen of its concrete
requirements — four dated SIM_RECIPE markers, an upstream Spike build, a `ci/` allowlist,
`FENCE-ZONE: A` markers, `work/` in a `.gitignore` — have no step. C4 is the one finding that cannot
be fixed inside the current task shape: the shipped validator and the launch preconditions make
contradictory demands on three files, and resolving it adds `dv_principles.md` and the validator to
the overlay.

Impact on in-flight Wave 1: C1, C2, C3, Ma1, Ma2, Ma3 and Ma6 all rewrite Task 1's `DENY` array and
Task 1 Step 1's check-(b) list, and C4, Ma2, Ma9 rewrite Task 2's overlay file set. Both agents
should take these before their commit steps rather than after, since the deny-array inversion changes
the array's shape rather than adding entries to it. Task 3 is unaffected except for Mi2/Mi3. Nothing
here requires re-planning the workstream or revisiting the owner's export-path directive.

Final verdict: APPROVE-WITH-CHANGES
