# Critic: dv-principles conformance check of TB build step 1a, constants codegen (T-061)

Artifacts under review (committed state at HEAD eff6b58; step 1a landed in 2d833d6; sha256 first 16 hex of the HEAD blob):
- dv/auto_dv/tb/gen_tb_knobs.yaml (single source)                 c61eb08ccc6d1a76
- dv/auto_dv/tb/gen_knobs_codegen.py (renderer, --check)           a6b6163cfd8ad97e
- dv/auto_dv/tb/gen_tb_pkg.sv (GEN_KNOBS block plus hand-written)   56b0314aa6884fd8
- dv/auto_dv/gen_tb/gen_knobs.py (Python mirror)                    cdd6c7d3f091a386
- dv/auto_dv/isa/gen_isa_shim_map.h (C mirror)                      b70d7e00567177bc
- dv/auto_dv/tb/unit/gen_ut_knobs_codegen.py (unit test)            ec8ce39e4173c85b
- dv/auto_dv/evidence/gen_tdd_knobs_codegen.md (transcript)         ca346ec1788c3660
- dv/auto_dv/evidence/gen_critic_response_tb_arch.md (promoted)     15d1d350fad00f1d; TB Infra sections v3 b9a3cc16eccec313
Working tree at review time: the six code files are modified relative to HEAD (step 1b in progress: bridge command
codes, gen_env_cfg_knobs.svh, gen_is_known_plusarg, GEN_KNOB_ -> GEN_ENUM_ rename; +179/-48 lines). This verdict judges
the committed step 1a; where the working tree already changes a finding, the text says so.
Date: 2026-09-03 (UTC)
Role: Critic (dv-principles conformance, docs/dv/dv_principles.md; the cross-model post-execution review
dv/auto_dv/reviews/2026-09-03-claude-diff-dc6de881-2d833d60.md, APPROVE-WITH-CHANGES, was read to avoid duplication)

CRITIC VERDICT: REQUEST-CHANGES

The design is right: one YAML source, three rendered consumers, a `--check` mode that fails on drift, a unit test
written first with a retained red run, ASCII and determinism enforced by the renderer, a compile proof of the rendered
package, and the identifiers now match TB Infra's v3 sections (`chk_sva_rvalid_legal`, `knob_*`, the two offset
constants). Three mediums keep it from approval, all small: the one source silently accepts what it does not
understand (P-01), two derived values are re-typed beside their derivation (P-02), and the drift checker that everything
downstream trusts has never been shown to fail (P-03).

## 1. What I ran and audited

| Check | Result |
|---|---|
| python3 dv/auto_dv/tb/unit/gen_ut_knobs_codegen.py (ci/env.sh sourced, working tree) | PASS, 511 OK lines, 0 failures |
| python3 dv/auto_dv/tb/gen_knobs_codegen.py --check (working tree) | "up to date", rc 0 |
| YAML parse of gen_tb_knobs.yaml (HEAD and working tree) | 4 plusarg entries carry spurious keys created by unquoted commas (P-01) |
| Transcript artifact audit (four-point rule) | see Section 2 |

## 2. Transcript audit: each claimed run against its retained artifact

Rule: a claimed run maps to a distinct retained artifact whose path, mtime and in-log stamp agree; identical quoted text
is not evidence; unretained claims are labelled. Local times are -0400 (UTC = local + 4 h).

| Claim (transcript section) | Artifact | mtime | In-log stamp / content | Result |
|---|---|---|---|---|
| 1 red run, 2 failures | dv/auto_dv/work/tb-infra/tdd/knobs_codegen_red.log (333 B) | 03:10:54 | "# RED run: 2026-09-03T07:10:54Z", two FAIL lines, exit=1 | consistent |
| 2 green attempt 1 aborts on GEN_BOOT_ADDR_DEFAULT | tdd/knobs_codegen_green.log lines 1-231 | 03:14:47 (file) | "# GREEN run: 07:13:46Z"; line 230 "cannot find parameter GEN_BOOT_ADDR_DEFAULT"; exit=1 | consistent (two runs appended to one file, each with its own stamp) |
| 3 green run 2 PASS | same file lines 232-495 | | "# GREEN run 2: 07:14:43Z"; line 494 PASS (0 failures); exit=0 | consistent |
| 4 `--check` fails on a mutated target, passes after re-render | none retained (no path named; tdd/ holds no such log) | - | - | UNRETAINED: the claim rests on a hand-typed excerpt (P-03) |
| 5 zc program re-run, Spike exit 0 | out_codegen/zc/spike_stdout.log, spike_commits.log, prog.* | 03:14:55 | command line present; no exit status line in the log | partially retained: the run is there, the exit status is not (L-4) |
| 5 compile proof, VCS exit 0, 0 errors, four smoke runs | out_codegen/smoke/compile.log, runs_summary.txt, run_0[1-4]_* | 03:15:21-45 | 0 Error lines; "sequence result: ALL-AS-EXPECTED" | consistent |
| 6 step 1b red / green | tdd/knobs_codegen_1b_red.log, knobs_codegen_1b_green.log | 03:20:11, 03:21:26 | "07:20:10Z" 4 FAIL / "07:21:26Z" PASS | consistent (step 1b, outside this verdict's scope, noted) |
| 6 re-run after the GEN_KNOB_ -> GEN_ENUM_ rename, "509 checks" | none retained | - | - | UNRETAINED (my own run today: 511 OK) |

## 3. Conformance to dv_principles.md

| Principle | Finding |
|---|---|
| S5 single source, no re-typed literals | Met in structure: plusarg names, knob sets, constants, memory map and ISA string have one origin and three rendered consumers; `GEN_IBUS_MAX_OUTSTANDING` derives from `ibex_pkg::IC_LINE_BEATS` in SV; the memory map is read from gen_dut_top.sv and gen_link.ld at render time (`sv_param`, `ld_prog_length`) and cross-checked (boot page + 0x80 == PROG origin). Not met in two places: P-02 and P-04 |
| S2 fail through a collected mechanism | Met: the unit test exits 1 on the first failure; `--check` exits 1 and names the stale file; `load()` dies on duplicate names, bad kinds, bad enums; the renderer dies on non-ASCII output |
| S6 rule 1 TDD | Met: the red run precedes the implementation and is retained with a stamp (Section 2); green attempt 1 exposed a real renderer defect (an alias the regex readers cannot parse), which is the kind of failure TDD exists to catch |
| S6 rule 2 mutation-proof for the checker | Not met for `--check`: the only mutation is a hand-typed excerpt (P-03) |
| S6 rule 3 fcov-expectation | n/a (no covergroup in this step) |
| Determinism, ASCII, no timestamps in outputs | Met: `render_*` emit no timestamps; `main()` dies on any non-ASCII character in any target |
| Fence | Met: only this clone's RTL (ibex_pkg, gen_dut_top), gen_link.ld and the flow are read |

## 4. Findings

P-01 (medium) The single source accepts what it does not understand. Four `desc` values contain unquoted commas inside
YAML flow mappings, so the parser splits them into spurious keys and truncates the description: `smoke_intg_flip` (key
"bit of the SECDED-encoded NOP word to flip (absent = no corruption)"), `dbg_csr_probe` ("debug only", "never in a
measured run"), `mem_image_crc32` ("word) pairs from the .sym.json sidecar", "recomputed after load"), `regime_sched`
("... (consumed when supplied", "else derived from RANDOM_SEED and echoed)"). The truncation is rendered into all three
consumers (HEAD gen_tb_pkg.sv: `PLUSARG_SMOKE_INTG_FLIP ... // int, default unset: smoke red-run knob`; `PLUSARG_MEM_IMAGE_CRC32
... CRC-32 over (index`). The descriptions themselves are harmless; the mechanism is not: `load()` validates kinds and
enum sets but never rejects an unknown key, so a misspelled `default:` or `debug_only:` in a future entry would be
silently ignored and the knob would render with the wrong default or without its debug-only refusal, which is exactly
the "mistyped gate silently no-ops" failure dv_principles S5 warns about. Required: quote every `desc` (or use block
mappings), and make `load()` die on any key outside the schema for plusargs, constants, memory_map and registers;
the unit test asserts that a fixture with an unknown key is refused. (Cross-model medium 1: agree, root cause and
prevention added.)

P-02 (medium) Re-typed derived values. `GEN_IBUS_MAX_OUTSTANDING` carries `value: 8` beside its SV derivation
`GEN_ICACHE_NUM_FB * ibex_pkg::IC_LINE_BEATS`, and `GEN_IRQ_FAST_MASK` carries `value: 2147418112` beside
`((32'h1 << $bits(ibex_pkg::irqs_t) - 3) - 1) << 16`. The SV side derives; the Python and C mirrors take the literal, and
nothing checks that the two agree, so a change in ibex_pkg (IC_LINE_BYTES, BUS_BYTES, the irq_fast width) would leave the
shim and Python with stale values while SV moves. Required: one origin for the numbers as well: the renderer derives
`value` by reading rtl/ibex_pkg.sv (IC_LINE_BYTES / BUS_BYTES, the `logic [14:0] irq_fast` width at ibex_pkg.sv:339, as it
already reads gen_dut_top.sv for the DM window), or the unit test parses those parameters and asserts the literals; and
the `sv` expression and the literal are rendered from the same computed number. (Cross-model medium 2: agree.)

P-03 (medium) `--check` is the checker every downstream file trusts and it has never been shown to fail in a retained,
mechanical way. The unit test runs `--check` only on a fresh tree (positive path); the mutation in transcript Section 4 has
no retained log and is not repeatable by the test. Required: the unit test performs the mutation itself (render into a
temporary copy of the tree, or give the codegen a `--root`/target override, mutate one constant in each of the three
rendered files in turn, assert `--check` exits 1 and names the stale file, restore, assert exit 0), and the transcript
cites the retained log of that run. (Cross-model medium 4: agree; this is trust-triad rule 2 for the checker.)

P-04 (low) The one source duplicates values inside itself: `boot_addr` default 0x80000000 and
`memory_map.boot_addr_default`; `mem_readback_words` default 64 and `GEN_MEM_READBACK_WORDS_DEFAULT`; `alive_timeout`
default 100000 and `GEN_ALIVE_TIMEOUT_CYCLES_DEFAULT`. Required: the plusarg default references the constant (a
`default_from:` key resolved at render time) or the constant is dropped in favour of the plusarg default. (Cross-model
medium 3: agree on substance, graded low here because both copies live in one file and the renderer can enforce it.)

P-05 (low) `rvfi_trace`, `isa_string` and `isa_log` are described as debug-only but carry no `debug_only: true`, so
Runtime's measured-run refusal (which the unit test verifies for `dbg_csr_probe`) does not cover them. `isa_string`
matters: an ISA override in a measured run changes the reference model. Required: mark all three `debug_only: true`
and let the existing unit-test check pick them up. (Cross-model low: agree.)

P-06 (low, fixed in the working tree) At HEAD the enum-set parameters render as `GEN_KNOB_KNOB_<NAME>_VALUES` (double
prefix, 40 occurrences); the working tree renames the prefix to `GEN_ENUM_` and the transcript says the test and
`--check` were re-run (509 checks) with no retained log (Section 2). Retain the log of the re-run or state it as
unretained; my own run today (511 OK, `--check` up to date) covers the current tree.

P-07 (low, design note for step 1b) `gen_is_known_plusarg(name)` (working tree) cannot by itself deliver A-23 ("an
unknown +gen_* plusarg is a uvm_fatal at time 0"): SystemVerilog has no way to enumerate the plusargs present on the
command line, only to test known names. The fatal needs the argument list from outside SV (cocotb reading
/proc/self/cmdline, or the flow passing the list), or it stays at the flow level where Runtime's testlist loader already
refuses unknown names before a run starts (its P-06). State which one gen_base_test implements.

L-1 (info) The transcript's "Spike exit 0" for the zc re-run has no exit-status line in out_codegen/zc/spike_stdout.log;
future run logs record `exit=<rc>` as the tdd logs do.

L-2 (info) gen_stim/gen_program.py comment at :52 still says the codegen "will emit" the ISA string (cross-model low);
and the unit test's docstring narrates the TDD history that the transcript already carries (cross-model low; the
repository comment rule prefers intent over history).

## 5. Required before re-review

1. P-01: quote the descriptions; strict key validation in `load()`; a refused-fixture check in the unit test.
2. P-02: derive the two literals from rtl/ibex_pkg.sv (or assert them in the unit test against a parse of it).
3. P-03: the mutation of `--check` inside the unit test, with a retained log named in the transcript.
4. P-04, P-05, P-06 as time allows; P-07 answered in the step 1b design.
5. Response file: dv/auto_dv/evidence/gen_critic_response_tb_step1a.md, one row per finding (standing rule).

The re-review re-runs the unit test and `--check`, re-parses the YAML for spurious keys, and re-audits the transcript.

## 6. Method and fence record

Inputs: the seven committed files (HEAD blobs hashed above), the working-tree copies for the run, the retained logs under
dv/auto_dv/work/tb-infra/tdd/ and out_codegen/, rtl/ibex_pkg.sv for the derived-value facts, the cross-model review of
2d833d6. The unit test and the check mode were run by me under ci/env.sh. No LSF command; no fence event.
