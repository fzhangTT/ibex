# Cross-model review - plan/spec file(s): dv/auto_dv/docs/gen_wp8_part1_plan.md at commit 2098158b

**Reviewer:** claude CLI 2.1.260 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 3efb31de-501d-4d53-88ce-7e43052ead3e; sandbox: bubblewrap, working directory = detached read-only checkout of commit 2098158b830a0cca2481c569083322d6ff584096 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit 2098158b830a0cca2481c569083322d6ff584096
**Date:** 2026-09-04
**Target:** plan/spec file(s): dv/auto_dv/docs/gen_wp8_part1_plan.md at commit 2098158b (echo at raw line 1)

---

TARGET: dv/auto_dv/docs/gen_wp8_part1_plan.md@c6d873ec

Reviewer identity: claude-fable-5-1 (Claude Code CLI, fresh session, default reasoning), reviewing commit 2098158 read-only; file sha256 c6d873ec2aa2… confirmed, 99 lines.

**What I verified against the repo**

- Bin table: the 44 CG-IC-006 rows of `gen_trace_tp_bin.csv` reduce to exactly the distinct bins tabulated; part 1 sums to 29, part 2 to 8. Correct.
- Renderer: `gen_fcov_codegen.py:148` is the per-covergroup IMPLEMENTED loop; every plan coverpoint renders with `ignore_bins na = {-1}`; 203 such clauses in `gen_fcov_groups.svh`. A cross tuple whose component sits in an ignore bin is excluded, so passing -1 for the four part-2 coverpoints leaves their real bins at 0 with nothing hidden. The split mechanism is sound in principle and consistent with the fcov-expectation rule (a manifest names only bins the test claims).
- Intent anchor `rtl/ibex_icache.sv:580-584` reads as the plan says.
- Probe-off judging exists today: `judge_data` uses form (b) when `probe_on` is 0 (`gen_checkers_pkg.sv:592-600`); no part-1 bin needs P9 if the sampler samples at closure.
- The zero-hits claim: `gen_tb_pkg.sv` has five comment lines containing "written" (e.g. `tag_shadow ... as written`, :560), none an identifier tracking data-RAM written-ness; `tag_shadow` tracks tag contents. The conclusion "nothing tracks data-RAM written-ness" stands; the sentence as a grep claim is false.

**Rubric results** (the diff is one markdown file; no code lines qualify)
- ai-slop-comments: `{"status": "PASS"}`
- rtl-purity: `{"status": "PASS"}`
- magic-numbers: `{"status": "PASS"}`
- forces-and-hier-access: `{"status": "PASS"}` (but see finding 6c on the planned forced alert)
- assertion-integrity: `{"status": "PASS"}`

**Findings**

[Critical][dv/auto_dv/docs/gen_wp8_part1_plan.md:45] "No tool change is required and none is proposed" and line 89 "Part 1 changes no coverpoint LINE in the plan" cannot both hold: adding CG-IC-006 to IMPLEMENTED makes the renderer refuse the plan as written. Dry run in a temp root (repo untouched): first `CG-IC-006: CSV coverpoints without a plan bins line: ['cp_multiway_mismatch']` (the parenthetical "(informational, TP-IC-038 only)" before `iff` defeats the `- cp_x iff ...: bins` regex), then `cr_ram_x_bits_x_way: no plan cross line` (", 8 bins:" between the components and the colon); `cp_knob`'s ": values none, rare, frequent" also lacks the `: bins` keyword. With those three lines normalised the render succeeds (CG-IC-006: 24 coverpoint bins, 16 cross bins). - The plan must pick one path and announce it: extend the codegen parser to accept these three forms (a tb-infra tool change, added to Sections 2 and 7), or make the DV Lead's next touch a hard prerequisite that normalises the three lines. Delete the "none proposed" sentence either way.

[High][dv/auto_dv/docs/gen_wp8_part1_plan.md:55] "published in the announcement for a read of an unwritten word": if this goes through `gen_icram_events::announce()` it floods the 256-deep queue (`gen_tb_pkg.sv`, `while (q.size() > 256) pop_front`). Every lookup reads both ways' data words whether or not the cache is enabled (`data_req_ic0 = lookup_req_ic0 | fill_req_ic0`, rtl:281), and early in every run almost all words are unwritten, so injections awaiting a form-(b) verdict (up to GEN_ICACHE_RETIRE_WINDOW = 64 cycles) get evicted and pulses become false "alert_minor_o high without an announced ECC injection" errors. - State that the uninitialised-read observation bypasses `q` (direct sampler call or its own counter) and never enters the alert_minor attribution path.

[High][dv/auto_dv/docs/gen_wp8_part1_plan.md:59] Anti-vacuity of `uninitialised_data_ram`: unwritten-word reads occur from the first lookup in every test, including with the cache disabled and during the reset sweep (`lookup_actual_ic0` masks only the check, rtl:266). Sampling "each lookup that read a never-written line" hits the bin trivially and overlaps `disabled_cache` and `during_invalidation`. Also, the sweep writes data words with ECC(0) whenever a lookup request coincides (`data_write_ic0 = tag_write_ic0`, rtl:283), so which words stay never-written is stimulus-dependent and those sweep writes must count as writes. - Qualify the sample: a checked lookup (`qualified_at`) whose hit way is not the unwritten way or a miss; state which bin wins when several no-alert reasons apply; state that sweep data writes set the flag.

[Medium][dv/auto_dv/docs/gen_wp8_part1_plan.md:54] "cleared on reset": neither the model's `mem` (initial block only) nor the DUT's RAMs lose contents on reset, so after a mid-run reset (CG-RST-001 is implemented) previously written valid codewords would be flagged uninitialised and hit the bin for a TB artefact. - Set on write, never cleared (initial block only), and say explicitly that invalidation does not clear it.

[Medium][dv/auto_dv/docs/gen_wp8_part1_plan.md:64] Window semantics unspecified per signal: `rvfi_ext_nmi_int` is a per-retirement RVFI flag (`rtl/ibex_core.sv:1830`), not a level, so over the 2-cycle GEN_ICACHE_ECC_WINDOW it can never be seen and the NMI term is vacuous. The plan also does not say how an alert level that predates or outlasts the window is judged. - Define the alert term as any high cycle in 1..GEN_ICACHE_ECC_WINDOW (a persistent level counts as not quiet) and the NMI term over a retirement window (GEN_ICACHE_RETIRE_WINDOW). Note the "one routing" already exists: `gen_model_state.nmi_int_pend` (`gen_rvfi_pkg.sv:69,207`) reaches `gen_misc_monitor::write_state` (`gen_checkers_pkg.sv:408`); use it instead of a second path, and reword "referenced ZERO times", which is true of the string only.

[Medium][dv/auto_dv/docs/gen_wp8_part1_plan.md:76] Trust-triad detectors are unnamed. (a) The written-flag red ("flag forced false must fail the new no-alert classification") names no failing check; for a coverage observation the red is the fcov-expectation manifest failing on the declared bin, or a `GEN_FCOV_UT` case (`gen_fcov_pkg.sv:1667`). (b) The quiet-window mutation ("one cycle short, boundary alert missed") yields a wrongly-hit bin, which no manifest can catch (manifests fail only unhit bins); the detector must be a `GEN_FCOV_UT` case or a directed check. (c) The red "a forced assertion of one major alert" forces a DUT output, trips the forces rubric and `gen_chk_alerts` (`gen_checkers_pkg.sv:471-474`). - Name the detector for each red and mutation; use legitimate stimulus (a bus integrity corruption raising alert_major_bus/internal NMI) or a UT injection of recorded levels.

[Medium][dv/auto_dv/docs/gen_wp8_part1_plan.md:21] Sample timing and probe-off judging are only implied. - State that the sample fires at closure (judged or closed), that cp_alert_pulses takes form (b) in measured runs and -1 when unjudged, and that the sampler never reads `probe_on`, `lk_cyc` or `lk_tag`.

[Low][dv/auto_dv/docs/gen_wp8_part1_plan.md:50] "return zero hits across the RAM model, the TB package and the checkers" is false as a text claim (five hits in `gen_tb_pkg.sv`). - Reword to "no identifier tracks data-RAM written-ness; `tag_shadow` tracks tag contents only".

[Low][dv/auto_dv/docs/gen_wp8_part1_plan.md:24] `cp_knob` renders three real bins (none, rare, frequent) with no CSV rows, so they are namable in no manifest; this matches existing operand-only groups. - Say so, so the 29-bin manifest count is not misread as the render's count.

[Low][dv/auto_dv/docs/gen_wp8_part1_plan.md:3] `gen_test_plan.md:434` defines WP-8 as the three icram export rows (lookup, tag_write, fill_write) plus the digest guard; the formatters exist (`gen_export_event_lines.svh:84-91`) but `gen_icache_ram.sv` announces none of them. - State whether those rows are part 1, part 2, or elsewhere.

Bin derivation, split mechanism, ETA statement and announcement obligations are correct as written; the plan is blocked only because its stated constraints make it unbuildable and because the two observations lack the qualifications above.

Final verdict: REQUEST-CHANGES
