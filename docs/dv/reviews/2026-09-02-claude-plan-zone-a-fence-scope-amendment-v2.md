# Cross-model re-review — spec amendment v2: docs/superpowers/specs/2026-09-02-zone-a-fence-scope-amendment.md

**Reviewer:** claude CLI 2.1.258 (subagent); model: claude-opus-5; extended reasoning; SUBSTITUTE reviewer per CLAUDE.md fallback clause — codex unavailable (spend cap); re-review of v1 findings
**Date:** 2026-09-02
**Target:** plan/spec file(s): docs/superpowers/specs/2026-09-02-zone-a-fence-scope-amendment.md @ commit cb35bb86 (v2); v1 at commit 91460209; v1 review artifact `docs/dv/reviews/2026-09-02-claude-plan-zone-a-fence-scope-amendment.md` (REQUEST-CHANGES)

---

TARGET: docs/superpowers/specs/2026-09-02-zone-a-fence-scope-amendment.md@745146f8

Scope: verdict on each v1 finding against v2, plus defects in v2's **added** text. The two Criticals
are judged for the coherence of the owner rulings' carriage into the document, not on their merits —
the rulings are recorded controller decisions and are not reopened here (CLAUDE.md: disagreements
with a recorded ruling go to the human owner). v1's affirmed core thesis is not re-litigated.

## Verdicts on v1 findings

**[Critical-1 — tool data-reach has no enforcing layer] ADDRESSED (by owner ruling; carried
coherently, with one gap — see New-1).** v2 records the ruling at amendment:29-35 and again at
amendment:180-181, and the triage table's MCP row (amendment:106) now points at it rather than at
bare "change 1". The ruling text is internally coherent: it names the threat model it is calibrated
to (accidental contamination by cooperative-but-fallible agents, not adversarial exfiltration — the
same model at spec:135), states the isolation mechanism (the clone boundary; "Zone B evaluation runs
in separate clones", which matches spec:156's `ci/zoneb-run.sh <branch>` in a sibling full clone),
and demotes the old rule to advisory ("pointed (advisorily) at the cleanroom's own out-tree",
amendment:39-40) rather than leaving v1's unenforceable "and nowhere else" standing. v2 also removes
the premise-level gap v1 flagged: amendment:21-23 now says the clone contains "no fenced FSDBs or
coverage databases, which are run products that never enter a snapshot", which is the actual reason
the ruling holds. Escape §4 is correspondingly re-aimed at clone contents (amendment:72-75) instead
of at per-call path policing, so v1's "a test for a mechanism that does not exist" is resolved rather
than papered over. The one thing the ruling's carriage does not do is name the escape case that
tests the boundary the ruling relies on — New-1.

**[Critical-2 — "same MCP servers" sweeps in atlassian] ADDRESSED as recommended.**
amendment:39-42 now reads "Zone A ships the three local MCP servers only — siliconpilot,
fsdb-mcp-server, verdi-cov-mcp" and "**The atlassian server is Zone B only**", with the correct
rationale (remote HTTP to Confluence/Jira, no path-based rule can scope it) and the retained
"future Zone A MCP addition requires a fence review" clause. The Decision paragraph is fixed at
source: amendment:12-13 now says "the **local MCP servers**", not "the same MCP servers". The
`.codex/config.toml` Zone A variant is specified as "three local servers, no atlassian"
(amendment:62), and escape §4's second bullet asserts it positively against both client configs
(amendment:75-77). Verified against the tree: `.mcp.json` does carry `atlassian` as an `http`
server alongside the three local wrappers, so the change is aimed at a real entry.

**[Major-3 — ci/reviews rubric line drawn in the wrong place] ADDRESSED.** New change 3
(amendment:66-70) defines the Zone A rubric set positively and exactly as recommended:
`ai-slop-comments` as-is; `rtl-purity`/`magic-numbers`/`forces-and-hier-access` rewritten against
`dv/auto_dv/` homes; `assertion-integrity` with the Zone A inert-referee sentence;
`fence-integrity`+`test-overlap` Zone B only. The wrapper assertion is strengthened from v1's
"a fenced rubric's absence is loud" to "a missing **or extra** rubric is loud" (amendment:57-58),
which is the right shape for a positive list. The triage row is corrected in step (amendment:104),
and the "Consistent as written" paragraph now records that the two Zone B fence notes stay
(amendment:121-122), closing v1's "confirm that in the same delta".

**[Major-4 — change 2 omits three files] ADDRESSED for all four named files; partially regressed
elsewhere — see New-2.** `mutation-check` (amendment:53-56, with the Zone A operationalization
spelled out), `AGENTS.md` "**as a pair**" (amendment:60-61), `.codex/config.toml` (amendment:62),
and the lower-priority `simple-english` rescope (amendment:58-59) are all now in change 2. The
`AGENTS.md` justification checks out: `.codex/compat/validator.py:129-140` does assert the two files
together (byte-identical CRITICAL-INVARIANTS block, plus a duplication check).

**[Major-5 — TB_CONTRACT redaction under-specified] ADDRESSED as recommended.** amendment:63-65
converts it to "a **positive-list rewrite**, not a redaction", with the positive list taken from the
DV prompt (seeding, handshake pattern, failure path, ASCII-only logging) and an explicit exclusion
list that names the four leak classes v1 identified (module names, event names, manifest paths,
`check_logs.py` behavior). The precondition half of the recommendation also landed: amendment:83-84
adds that the Zone A `TB_CONTRACT.md` is "also fence-integrity-checked".

**[Major-6 — riscv-isa-sim "pristine upstream" unsatisfiable] ADDRESSED.** The triage row
(amendment:114) is rewritten to the correct action — "**omit from the snapshot**" — with v1's
reasoning preserved (the vendored `mseccfg_tests` tree is the collateral; the locked rev exists only
in the fork). The row also moved out of the "why it is collateral" column into a new Action column,
which is the right structural fix. Precondition change 5 splits the two vendors correctly:
"pristine upstream `vendor/google_riscv-dv` at the locked revision; **`vendor/riscv-isa-sim` absent
from the snapshot**" (amendment:85-86). The live DV_prompt.txt error is now called out for
correction (amendment:87-89) — substantively right, but the line citation is stale (New-4).

**[Major-7 — visible-run retirement not carried through §WS7] ADDRESSED.** v2 adds three new
execution-model deltas covering exactly the three sub-items: dual-run collapse with the canary
retired (amendment:146-149), `--compile-only` retired (amendment:150-153), and the WS7 gate
reworded (amendment:154-156, replacing spec:167's "results returned through the dual-run structured
report"). v1's specific ask — "state whether submission returns even a boolean or an exit status" —
is answered explicitly: "a mechanical acceptance only (branch received, evaluation queued — an exit
status, no content)". The section header is updated from "Two spec items follow" to "Spec deltas
that follow" (amendment:139), so the count no longer contradicts the list.

**[Major-8 — SIM_RECIPE.md is a derived document with no bound] ADDRESSED as recommended.** New
change 6 (amendment:90-94) states the allowlist (VCS compile/elab mechanics and flags, run/env
contract, LSF submission, coverage-merge/URG, site gotchas, Zone B submission command) and the
exclusions (test names, testlist schema, cosim attachment mechanics, fcov bind wiring,
`metadata.pickle` internals) — matching v1's list and adding `metadata.pickle`. The enforcement half
landed too: change 5 adds "the document **passes the fence-integrity rubric**" (amendment:82-83),
and the over-fenced triage row is bounded by the same allowlist (amendment:102).

**[Minor-9 — no supersession list] ADDRESSED.** New section at amendment:124-133. Every target
verified present and carrying the quoted rule: `ci/mcp/README.md:42-47` (§Zone scoping, "**no MCP
servers**"); `ci/mcp/siliconpilot-mcp.sh:4`, `ci/mcp/fsdb-mcp.sh:3`, `ci/mcp/verdi-cov-mcp.sh:3`
("Zone B only — never ship to the cleanroom"); `.codex/config.toml:1,5`; `ci/env.sh:31`; spec:119
(§WS5 zone scoping); spec:121, whose gate text is verbatim "the cleanroom clone demonstrates *no*
MCP servers configured"; spec:163 (enforcement item 2 "no MCP servers" and the "query an MCP" escape
case). v2 also supplies the replacement criterion for the WS5 gate item rather than only retiring it
("the cleanroom's client configs list exactly the three local servers and no remote ones"), which is
more than v1 asked for. The evidence/handoff lines are referenced generically rather than by path;
both are real (`docs/dv/evidence/ws5-fsdb-demo.txt:159` "**PARTIAL** — gate item 3 (cleanroom clone,
no MCP servers configured) is pending WS7";
`docs/superpowers/handoffs/2026-09-02-session2-handoff.md:41`), and the generic wording is adequate
since v2 correctly notes no false claim was made in either.

**[Minor-10 — escape cases necessary but not sufficient] ADDRESSED (three of four as recommended;
one moot under the ruling).** (b) the positive no-remote-MCP assertion is amendment:75-77; (c) the
retirement of the spec's "query an MCP" case is stated inline there and again in the supersession
list; (d) the negative control is amendment:78-80, and correctly grounded in the same anti-vacuity
discipline v1 cited (`dv_principles.md` §6). (a) — a path inside the clone but outside the out-tree —
is moot once the ruling removes path policing, and v2 substitutes the clone-contents scan including
history (amendment:72-74), which is the right replacement probe. Change 4's framing sentence
("adjusted to what the rulings make true") is honest about why the shape changed.

**[Note — dv_principles §6 scoping sentence] Strengthened.** v2 changes "should gain" to "gains"
(amendment:163-164), fixes v1's tense slip ("as handoff item 4.2 already **did**"), and adds the
`mutation-check` skill variant as the operational carrier — matching Major-4's fix.

**[Note — design judgment / two uncited supports] NOT ADDRESSED (non-gating).** v1 suggested v2 cite
two supports for its own thesis. Neither appears in v2: the DV prompt already *requires* an MCP tool
in Zone A (`DV_prompt.txt:110`, the siliconpilot `cone_of_influence` tool, cited for every
control-vs-data exclusion argument — verified), and spec:154's design rule ("if Zone A code cannot
compile without fenced sources, the coupling exceeds the contract — fix the contract, never grant a
fence exception"). This was a Note, not a gating finding; see New-6.

## New defects in v2's added or revised text

**[Major][amendment:109-117 (under-fenced triage table)] Two under-fenced rows were silently deleted
in the v1→v2 revision, narrowing the fence with no finding requesting it and no replacement
anywhere in v2.** v1's table carried `ci/jenkins/**` ("names existing tests
(`testdata/regr_pass.log`), testlists, and drives the existing flow (`common.sh`,
`check_testlist_knob.sh`)") and `ci/build-spike.sh`, `ci/setup-cosim.sh`, `ci/run-cosim-test.sh`
("build and exercise the Zone B cosim (lowRISC Spike fork)"). Both rows are gone from v2's table,
which otherwise only *gained* an Action column. Neither string appears anywhere else in v2 — not in
change 2, not in the "Consistent as written" paragraph, not in the supersession list. Verified that
both rows were factual: `ci/jenkins/`, `ci/build-spike.sh`, `ci/setup-cosim.sh`,
`ci/run-cosim-test.sh` all exist, and `ci/jenkins/selftest.sh:21` does consume
`testdata/regr_pass.log`. The cosim-script row is made *more* load-bearing by v2's own change 5:
once `vendor/riscv-isa-sim` is absent from the snapshot, a shipped `ci/build-spike.sh` still tells
Zone A that a lowRISC Spike cosim referee exists and how it is built — which is precisely the
existence disclosure `DV_prompt.txt` forbids and which change 6 excludes from `SIM_RECIPE.md`.
— Recommendation: restore both rows to the under-fenced table with Action "deny", or, if the owner
intends them allowed, state the ruling and the rationale explicitly. A silent table deletion in a
document whose whole purpose is to fix the fence line is the one edit that should never be
unexplained.

**[Major][amendment:49-65 (change 2)] `ci/env.sh` and `ci/mcp/README.md` were dropped from the Zone
A variant list; the supersession list is not a substitute for them.** v1's change 2 required a Zone
A variant of `ci/env.sh` ("the spike-fork comment and paths removed") and `ci/mcp/README.md` ("a
`dv/uvm/core_ibex` path example"). v2's change 2 drops both. They reappear only in the supersession
list (amendment:126-128) — but that list's stated action is "update the shipped file's retired
Zone-B-only rule" in the **full** tree, which is a different operation from producing a Zone A
variant of a file that ships into the cleanroom. The content that motivated the v1 entries is
untouched by a comment update: `ci/env.sh:70-71` reads "Spike (lowRISC ibex_cosim fork, built by
`ci/build-spike.sh`)" and exports `SPIKE_INSTALL`, with further `ci/build-spike.sh` references at
`:39,:89,:97`; `ci/mcp/README.md:38` uses `dv/uvm/core_ibex/` as its worked path example. `ci/env.sh`
is also named in the DV prompt's own mechanical Zone A check (Section 12 item 9, at DV_prompt.txt:323-325),
so the amendment and the prompt now disagree about whether it needs a variant. — Recommendation:
restore `ci/env.sh` to change 2 (with the cosim-fork disclosure, not just the MCP comment, as the
reason) and add `ci/mcp/README.md`; keep both in the supersession list as well, since the two
actions are independent.

**[Major][amendment:71-80 (change 4, escape tests)] The escape suite does not carry the escape case
the tool-data-reach ruling actually rests on.** The ruling's load-bearing premise is stated at
amendment:31-33: "Zone B evaluation runs in separate clones ... the isolation is the clone
boundary." All four of change 4's probes look *inward* — the clone's own contents, the clone's own
client configs, skill path resolution inside the clone, and an in-clone negative control. None
tests the clone **boundary**: whether a Zone A session can reach a sibling full clone's out-tree,
which is where the ruling explicitly puts the fenced FSDB/VDB/log. The spec's existing suite does
carry that case — spec:163 lists "read sibling clone" among the four contamination attempts — but
change 4 neither retains nor cites it, while explicitly retiring its list-neighbour ("replaces the
spec's old 'query an MCP' case"). Read literally, change 4 reads as the complete adjusted suite, so
the one probe that verifies the ruling's premise is at risk of being dropped by the same edit that
relies on it. This is a gap in the ruling's *carriage*, not a challenge to the ruling: the owner
chose contents-verification over per-call policing, and contents-verification of the cleanroom alone
is a strictly weaker claim than the boundary the ruling names. — Recommendation: add a bullet to
change 4 stating that spec:163's "read sibling clone" case is **retained and is the escape test for
the tool data-reach ruling**, alongside the retained "fetch master" and "fetch upstream ibex DV"
cases; only "query an MCP" is replaced.

**[Minor][amendment:87-89 (change 5)] The `DV_prompt.txt:308-309` citation is stale, and citing that
file by line is unstable.** Lines 308-309 in the current tree are the PROPOSED-RULING grep check
(precondition 1). The riscv-isa-sim wording the amendment means to correct is precondition 6, at
**DV_prompt.txt:317-318**: "`vendor/riscv-isa-sim` and `vendor/google_riscv-dv` are pristine upstream
at their locked revisions, not the lowRISC or locally patched forks." The substantive claim is
correct — only the locator is wrong. Root cause worth recording: `DV_prompt.txt` is **untracked**
(`git status` reports `?? DV_prompt.txt`), so it is not pinned by the commit this amendment is
reviewed at, and every line citation into it drifts silently; v1's citations to the same file are
off by the same 8-9 lines. — Recommendation: cite by structural address ("Section 12 precondition
6") rather than by line, here and in the change-5 parenthetical. Separately, note that precondition
6 bundles both vendors in one sentence, so the correction is a split, not a word swap.

**[Minor][amendment:73-74 (change 4, first bullet)] "the sync validator already rejects
unclassifiable paths" is a present-tense claim about a component that does not exist.** `ci/`
contains no `sync-cleanroom.sh`, no `make-cleanroom.sh`, and no landing validator — WS7 is
unimplemented. The behaviour is a design requirement at spec:139 ("the sync script **rejects any
path it cannot classify**"), not shipped state. The word matters because the clause is offered as
part of why the contents scan is sufficient. — Recommendation: reword to "the sync validator
rejects unclassifiable paths (spec:139) — this escape case and that validator land together in
WS7."

**[Minor][amendment:49-65, 81-89] v2 dropped v1's "the mechanical acceptance check is `DV_prompt.txt`
Section 12 item 9" and left precondition 9 stale against its own expanded change 2/3.** Precondition
9 (DV_prompt.txt:323-325) currently asserts only that no file under `.claude/skills/`,
`.claude/agents/`, `ci/env.sh`, or `docs/dv/TB_CONTRACT.md` contains `dv/uvm/core_ibex`,
`BUILD_AND_SIM.md`, or `COSIM.md`, plus the cross-review artifact path. It does not cover `AGENTS.md`
or `.codex/config.toml` (both newly required by change 2), does not assert the positive rubric list
(change 3), and still names `ci/env.sh` — which change 2 no longer lists (see New-2). v2 does the
"correct the DV prompt" work for precondition 6 but not for 9, so the amendment now specifies a
Zone A variant set with no mechanical acceptance check behind most of it. — Recommendation: restore
a sentence tying change 2 and change 3 to Section 12 item 9, and state that item 9's string and
file lists are extended to match (`AGENTS.md`, `.codex/config.toml`, the asserted rubric list).

**[Minor][amendment — Decision and "Why the spec fenced the tools" sections] Two cheap
self-supporting citations still absent.** Carried from v1's design-judgment Note: `DV_prompt.txt:110`
already *requires* the siliconpilot `cone_of_influence` MCP tool for every control-vs-data exclusion
argument, so the shipped prompt already contradicts "no MCP servers in Zone A" — this is the
strongest available support for change 1 and it costs one clause. spec:154's design rule is the same
instinct applied to compilation. — Recommendation: cite both in the "Why the spec fenced the tools"
section; an amendment that overturns a shipped rule is stronger for showing the shipped tree already
disagreed with it.

**[Note] Verified without issue.** The `AGENTS.md`-pairing rationale (`.codex/compat/validator.py`
asserts the two files together), the supersession list's eight targets, spec:121's and spec:167's
quoted gate wording, `ci/cleanroom-compile.sh` as a spec-defined Zone A artifact (spec:154 — and v2
correctly adds "and its own sim runs" beside it, since spec:154 scopes that script to "no simv run"),
and the `.mcp.json` atlassian entry all check out as v2 describes them. v2's structural additions —
the Action column, the supersession section, the four execution-model deltas — are net improvements
in a document that was materially incomplete at v1.

**[Note] Ruling coherence, summary.** Both owner rulings are recorded twice (Decision section and
the Rulings-recorded list) and are consistent with each other and with the surrounding text; no
place in v2 still asserts the superseded "same MCP servers" or "pointed at that out-tree and nowhere
else" language. The rulings' merits are not in scope for this re-review and are not addressed.

## Assessment

All nine v1 findings are addressed — the two Criticals by owner ruling carried coherently into the
Decision section, the escape-test section, and the triage table; the five Majors and two Minors by
substantive new text (changes 3, 4, 6, the supersession section, and four execution-model deltas)
that in several places goes beyond what v1 asked for. The document that binds is materially better
than v1.

The remaining defects are all additive text fixes to an otherwise sound amendment: one silent table
deletion to restore or justify (New-1), two files to put back in change 2 (New-2), one escape case
to name explicitly so the ruling's own premise is tested (New-3), and four small consistency and
citation repairs. None of them contradicts the thesis, the rulings, or the spec deltas, and none
requires re-planning — but New-1 and New-3 change what the fence covers and what the WS7 gate
verifies, so they should be folded before the amendment is treated as binding rather than left to
WS7 planning.

Final verdict: APPROVE-WITH-CHANGES
