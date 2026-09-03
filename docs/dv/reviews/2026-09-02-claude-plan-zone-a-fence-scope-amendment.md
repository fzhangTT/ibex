# Cross-model review — spec amendment: docs/superpowers/specs/2026-09-02-zone-a-fence-scope-amendment.md

**Reviewer:** claude CLI 2.1.258 (subagent); model: claude-opus-5; extended reasoning; SUBSTITUTE reviewer per CLAUDE.md fallback clause — codex unavailable (workspace spend cap)
**Date:** 2026-09-02
**Target:** plan/spec file(s): docs/superpowers/specs/2026-09-02-zone-a-fence-scope-amendment.md

---

TARGET: docs/superpowers/specs/2026-09-02-zone-a-fence-scope-amendment.md@ff5cf200

**[Critical][amendment:28-32 (change 1)]** "Zone A's MCP servers and skills are pointed at that
out-tree and nowhere else" names no enforcing layer, and the current wrapper design cannot provide
one. `ci/mcp/fsdb-mcp.sh:12` and `ci/mcp/verdi-cov-mcp.sh:12` both `exec "$SERVER"` with **no
path-scoping argument** — the FSDB file / coverage DB path arrives per tool call, so a Zone A
session can hand either server an absolute path into a sibling full clone's out-tree, which is
exactly where the blind run's human fcov VDB and cosim logs land (spec:158, 161). Only
`siliconpilot-mcp.sh:12` is scoped (`--workspace "$REPO_ROOT"`), and `ci/mcp/README.md:45` already
concedes `--workspace` "is not a sandbox". Consequence: change 3's escape case ("an MCP server
asked for a path outside the cleanroom out-tree must fail") is a test for a mechanism that does not
exist, so it can only ever be written to pass vacuously. Note the spec's existing runtime layer
(spec:163 — codex sandbox, `PreToolUse` hook on Read/Grep/Glob) does not cover this: MCP servers
are spawned as sibling processes of the client, outside a client-level sandbox, and the hook as
specified keys on Read/Grep/Glob only. — Recommendation: name the layer that enforces the rule and
size the escape test to it. Three candidates, in increasing strength: (a) a Zone A wrapper that
refuses to start unless the server accepts an allowed-root flag; (b) extend the `IBEX_DV_FENCE=1`
`PreToolUse` hook from Read/Grep/Glob to `mcp__fsdb*` / `mcp__verdi-cov*` tool arguments, denying
any absolute path outside `$CLEANROOM_ROOT`; (c) the only actual boundary — make Zone B's out-tree
unreadable to the Zone A user (filesystem perms / separate group). Given the stated threat model
(accidental, cooperative-but-fallible) (b) is proportionate, but it must be written down, because
change 3 depends on it.

**[Critical][amendment:9-12 (Decision), 28-32 (change 1)]** "Zone A therefore gets the **same MCP
servers** ... as the full tree" sweeps in `atlassian` (`.mcp.json:6`, `.codex/config.toml`), which
is not a file-path server at all — it is a remote HTTP server reaching Tenstorrent
Confluence/Jira, a plausible home for Ibex testplans, coverage plans and DV pages. Change 1's
"pointed at that out-tree" language constrains file-path servers only and does not touch it, and
the spec's Zone A network denial (spec:163) is scoped to "network fetches of ibex upstream/fork
URLs", so `mcp.atlassian.com` is not caught by any layer. `DV_prompt.txt:68-71` forbids "Any
existing Ibex DV collateral, wherever it lives ... or any other fork or integrator", which makes
this a policy violation on its face, and it defeats the amendment's own load-bearing argument
("the cleanroom clone itself contains no fenced files") because this server reaches outside the
clone entirely. — Recommendation: state explicitly that Zone A ships the **three local servers
only**; `atlassian` stays Zone B. Any future remote server in Zone A goes through the retained
"future Zone A MCP addition requires a fence review" clause.

**[Major][amendment:61 (triage table row)]** "`ci/reviews/*.md` rubrics | `test-overlap.md`
references existing tests | fence that one file, allow the rest" draws the line in the wrong place.
Five of the seven rubrics carry fenced paths or fenced identifiers:
- `ci/reviews/fence-integrity.md:12-16` enumerates the fenced tree
  (`dv/uvm/core_ibex/tests|riscv_dv_extension|directed_tests|fcov`, `dv/cosim`) and names "the
  human coverage model's dimensions, cosim internals" — a structural map of the collateral, and
  paraphrase leakage by the rubric's own definition. It also carries a binding fence note
  (`:7`) restricting it to "Zone B / evaluator context", so running it in a Zone A cross-review
  violates its own header.
- `ci/reviews/assertion-integrity.md:15,25-26,30-32` names `FCOV_NO_DEFAULT_SEQUENCE`,
  `core_ibex_fcov_if.sv` (the human fcov bind file) and `+disable_cosim`.
- `ci/reviews/rtl-purity.md:8` names `dv/uvm/core_ibex/fcov/core_ibex_fcov_bind.sv`.
- `ci/reviews/forces-and-hier-access.md:10-15` builds its whole rule on `dv/cocotb/common/` handles
  and `cctb_alive`/`cocotb_active` — existing-TB API, and in Zone A actively wrong, since the team
  builds its own TB.
- `ci/reviews/magic-numbers.md:12-16` names "the bind files for fcov", `dv/cocotb/common/`, and
  "the testlist yamls".
— Recommendation: define the Zone A rubric set **positively** (ai-slop-comments as-is;
rtl-purity/magic-numbers/forces rewritten against `dv/auto_dv/` homes; assertion-integrity with the
Zone A inert-referee sentence; fence-integrity and test-overlap Zone B only) and make the
cross-review wrapper's asserted list that set. The mechanism change 2 proposes is otherwise right
and well-aimed: `.claude/skills/cross-review/scripts/run_codex_review.sh:20` currently globs
(`cat "$REPO"/ci/reviews/GUIDE.md "$REPO"/ci/reviews/*.md`), so a missing rubric is silent today.

**[Major][amendment:38-44 (change 2)]** The Zone A variant list omits three files carrying the same
defect the amendment is fixing elsewhere:
- `.claude/skills/mutation-check/SKILL.md:20,35` operationalizes "hidden referees inert" as
  `+disable_cosim=1` — the exact full-tree-only plusarg the amendment correctly flags for
  `dv_principles.md §6` at amendment:95-99. The skill is the *operational* surface; fixing the
  principles file and not the skill leaves Zone A with an unexecutable instruction in the place it
  will actually be read.
- `AGENTS.md` — the codex delegator that mirrors the Critical Invariants and the client-mechanics
  table, and that `.codex/compat/validator.py` asserts as a pair with `CLAUDE.md`. A Zone A
  `CLAUDE.md` without a matching Zone A `AGENTS.md` breaks that contract for codex teammates, who
  `DV_prompt.txt:290-291` expects to run the review policy in Zone A.
- `.codex/config.toml` — carries the Zone-B MCP block (`:1,:5`) and the trust settings; spec:119
  already said the snapshot replaces *both* client configs, and change 1 changes what the Zone A
  one must contain.
Lower priority but same category: `.claude/skills/simple-english/SKILL.md:8,30,39-41` names
`BUILD_AND_SIM.md` and `ci/reviews/*.md` as its in-scope surfaces.

**[Major][amendment:42-44 (change 2, TB_CONTRACT item) and 100-102]** "with the `dv/uvm/core_ibex`
paths and the `BUILD_AND_SIM.md` references removed" under-specifies the redaction; the leak
surface in `docs/dv/TB_CONTRACT.md` is architectural, not just path-shaped. §2-§3 document the
`dv.cocotb.common.handshake` / `uvm_bridge` module surface, the named event `"cocotb_irq_raise"`
(i.e. that the existing TB has a Python-reachable irq agent), and `trigger_received_count` /
`handler_entry_count` semantics (`:80-92`); §7 gives the manifest home
`dv/uvm/core_ibex/fcov_expectations/<testname>.fcov.yaml` (`:143`). "Hard rule 1" (`:51-56`)
describes `check_logs.py`'s PASS-banner behavior — flow-specific, and for a from-scratch TB
misleading rather than merely leaky. — Recommendation: make the Zone A variant a **positive-list
rewrite**, not a redaction of the existing doc. The positive list already exists:
`DV_prompt.txt:239-241` scopes it to "seeding, handshake, failure path, ASCII-only logging". Add
"the Zone A `TB_CONTRACT.md` passes the fence-integrity rubric" to the launch preconditions —
`DV_prompt.txt:305-306` (precondition 4) currently checks only for absent `dv/uvm/core_ibex` paths
and absent `BUILD_AND_SIM.md` references, so a leaky variant passes it.

**[Major][amendment:71 (under-fenced table) and change 4 / DV_prompt.txt:308-309]** "`vendor/riscv-isa-sim/**`
... replace with pristine upstream at the locked rev, as done for riscv-dv" is mechanically
unsatisfiable. `vendor/riscv_isa_sim.vendor.hjson` sets `upstream.url:
https://github.com/lowrisc/riscv-isa-sim`, `rev: mseccfg_tests`, and
`vendor/riscv_isa_sim.lock.hjson` locks `a4b823a1c7a260b532e1aa41b4d929e9634a7222` — a lowRISC-fork
SHA with no counterpart in `riscv/riscv-isa-sim`. "Pristine upstream at the locked revision"
therefore restores the fork, which is the thing being fenced. The riscv-dv analogy does not carry:
its upstream genuinely is `chipsalliance/riscv-dv` at `71666eba` with local patches applied on top
(spec:142). Note also the vendored tree is only `tests/mseccfg`, `arch_test_target`, `LICENSE` —
the mseccfg PMP suite is the collateral, and upstream spike has no such directory to substitute.
— Recommendation: for riscv-isa-sim the correct action is **omit from the snapshot**
(`DV_prompt.txt:58-61` already permits and expects the team to fetch upstream Spike itself), and
reword precondition 12.6 to "`vendor/riscv-isa-sim` is absent; `vendor/google_riscv-dv` is pristine
upstream at its locked revision." The same wording error is live in `DV_prompt.txt:308-309` today.

**[Major][amendment:30-34 (change 1, "retires the spec's visible-run report")]** The retirement is
asserted but not carried through §WS7, leaving live contradictions in the amended spec:
- spec:158's dual-run architecture exists solely to protect a visible report; with no return
  channel it collapses to a single evaluation run, and the canary noninterference test on the same
  line loses its subject.
- spec:156's `ci/zoneb-submit.sh --compile-only` "fast feedback path", with its fenced-path
  redaction rules, *is* a return channel. The amendment's "nothing returns" retires it without
  saying so. State whether submission returns even a boolean or an exit status.
- spec:167 (the WS7 gate) demands the round-trip "results returned through the dual-run structured
  report (an AI-check failure comes back; a canary blind-only finding is withheld...)" — now
  unsatisfiable. Restate the gate (submission accepted; evaluation artifacts produced Zone-B-side
  only; landing-validator round-trip demonstrated).
— Recommendation: add an explicit §WS7 delta covering dual-run collapse, the canary's fate,
`--compile-only`, and the gate wording. `ci/reviews/fence-integrity.md:7` and
`ci/reviews/test-overlap.md:7` remain correct as written; confirm that in the same delta.

**[Major][amendment:59 (over-fenced table) and change 4]** `docs/dv/SIM_RECIPE.md` is a new derived
document distilled from `dv/uvm/core_ibex/{Makefile,scripts/,yaml/,wrapper.mk,vcs.tcl}` — precisely
the category spec:144 fences ("derived/infra documents that paraphrase fenced knowledge"). The
mechanics/collateral split is defensible for VCS flags, LSF submission and URG merge, but those
same scripts carry the testlist schema, the `metadata.pickle` single-writer design,
`ibex_dv_cosim_dpi.f`, and the fcov bind wiring; a recipe written from them can leak that a cosim
referee and a human fcov model exist and how they attach — which `DV_prompt.txt:68-71` forbids and
which would contaminate the very coverage-model design the challenge measures. — Recommendation:
bind SIM_RECIPE.md to an explicit content allowlist (compile, run, coverage-merge/URG, LSF submit,
site gotchas; no test names, no testlist schema copied from the existing yamls, no cosim/fcov bind
mechanics) and add "SIM_RECIPE.md passes the fence-integrity rubric" to the launch preconditions —
`DV_prompt.txt:303-304` (precondition 3) currently checks only that a command exists and was
executed once.

**[Minor][amendment — no supersession list]** The amendment supersedes shipped WS5 text but names
no file, so the shipped tree will silently diverge from a binding spec. For the record, these carry
the retired rule: `ci/mcp/README.md:44-47` (§Zone scoping), `ci/mcp/siliconpilot-mcp.sh:4`,
`ci/mcp/fsdb-mcp.sh:3`, `ci/mcp/verdi-cov-mcp.sh:3` ("Zone B only — never ship to the cleanroom"),
`.codex/config.toml:1,5`, `ci/env.sh:31`, spec:119 (§WS5 Zone scoping), spec:121 (WS5 gate item
"the cleanroom clone demonstrates *no* MCP servers configured"), and spec:163 (enforcement-stack
item 2 "no MCP servers", plus the escape-test case "query an MCP", which must become "query an MCP
for a path outside the cleanroom out-tree"). The retired gate item is also referenced as pending in
`docs/dv/evidence/ws5-fsdb-demo.txt:159` and `docs/superpowers/handoffs/2026-09-02-session2-handoff.md:41`
— no false claim was made there (both mark it PARTIAL/pending WS7), but the criterion they point at
will no longer exist. — Recommendation: list these in the amendment as the supersession set.

**[Minor][amendment:45-46 (change 3)]** The two added escape cases are necessary but not
sufficient for what the amendment changes. Missing: (a) a Zone A MCP call handed a path inside the
cleanroom clone but outside its out-tree — `.git/`, where the single-branch snapshot history lives
— to anchor the rule at the right boundary; (b) the remote-server case from finding 2, asserted
positively (a Zone A session has **no** remote MCP configured), since a path-based test cannot
detect it; (c) retirement of the spec's existing "query an MCP" case (see previous finding);
(d) a **negative control** — an in-out-tree query must SUCCEED, or a server that fails every query
passes the suite vacuously. (d) is the same anti-vacuity discipline `dv_principles.md §6` rule 3
imposes on coverage bins; the escape suite should be held to its own house standard.

**[Note][amendment:95-99]** Verified and correct. `docs/dv/dv_principles.md` §6 states
`+disable_cosim=1` *inside* the `TRUST-TRIAD-CANONICAL-BEGIN/END` block, so the instruction to add
the Zone A scoping sentence *outside* that block is right and preserves the anchor.
`DV_prompt.txt:216-220` (Section 8) already carries the Zone A operationalization verbatim ("every
Zone A check other than the named one is disabled for the evidence run"), so the two will agree.

**[Note] Factual verification (read-only).** Confirmed: `.claude/skills/{regress,sim-debug,fcov-expectation,cross-review}`
and `.claude/agents/{ibex-debug-analyzer,ibex-test-generator}.md` all exist and all do reference
fenced documents as claimed; `fcov-expectation` does write outside `dv/auto_dv/`
(`SKILL.md:32` → `dv/uvm/core_ibex/fcov_expectations/`). `formal/{data_ind_timing,icache}` exist at
repo root (the `formal/**` under-fence is real). `vendor/lowrisc_ip/dv/` and
`vendor/lowrisc_ip/ip/prim/dv/` exist and contain no Ibex-named files (`find -iname '*ibex*'`
empty), supporting the "allow: generic lowRISC DV libraries" ruling.
`dv/uvm/core_ibex/{Makefile,scripts,yaml,wrapper.mk,vcs.tcl}` all present. `DV_prompt.txt` exists at
repo root with Sections 8 (`:203`) and 12 (`:294`) as referenced, and precondition 12.2-12.7 matches
the amendment's change-4 list. `docs/dv/TB_CONTRACT.md` documents cocotb on the existing TB, as
stated. The one claim that does not survive verification is the riscv-isa-sim one (finding 6).

**[Note] Design judgment on the core thesis.** "Fence the collateral, not the tools" is sound
against the spec's *stated* threat model (spec:135 — accidental contamination by
cooperative-but-fallible agents and humans, explicitly not adversarial exfiltration). The central
argument — the cleanroom clone contains no fenced blobs, so a code-analysis server pointed at it
has nothing fenced to read — is correct and follows from the orphan-snapshot design (spec:146-152).
Two supports the amendment does not cite and should: `DV_prompt.txt:104` already *requires* an MCP
tool (`siliconpilot cone_of_influence`) for every control-vs-data exclusion argument, so the shipped
prompt already contradicts "no MCP servers in Zone A"; and spec:154's design rule ("if Zone A code
cannot compile without fenced sources, the coupling exceeds the contract — fix the contract, never
grant a fence exception") is the same fence-the-data-not-the-tooling instinct applied to
compilation. The cut is the right cut. What is not yet right is the completeness of the perimeter
drawn around the data (findings 1, 2, 3, 5, 8) — and the amendment cannot bind while its central
rule (change 1) has no enforcement mechanism and its escape test (change 3) has nothing to test.

Final verdict: REQUEST-CHANGES
