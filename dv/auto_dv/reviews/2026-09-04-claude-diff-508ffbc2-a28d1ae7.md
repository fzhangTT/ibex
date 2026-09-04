# Cross-model review - committed diff 508ffbc2..a28d1ae7

**Reviewer:** claude CLI 2.1.260 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 752cadbf-2860-406e-a146-dce16fb59abc; sandbox: bubblewrap, working directory = detached read-only checkout of commit a28d1ae7dfbc5f6ca1bea6b2b1db24bdbb6717cd (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit a28d1ae7dfbc5f6ca1bea6b2b1db24bdbb6717cd
**Date:** 2026-09-04
**Target:** committed diff 508ffbc2..a28d1ae7 (echo at raw line 1)

---

TARGET: 508ffbc29589ca2cbff854019cac9ab73bbe3cb2..a28d1ae7dfbc5f6ca1bea6b2b1db24bdbb6717cd

**Scope verified.** One commit, 149 files, no `rtl/` file in the diff (RTL-purity PASS). The only non-tb-infra change is the three-line `debug_only_plusargs` edit in `dv/auto_dv/flow/gen_testlist.yaml`, and `gen_ut_knobs_codegen.py` lines 136-141 do require every `debug_only: true` knob (here `probe_ic_lookup`, `gen_tb_knobs.yaml:115`) to appear in that list, so the joint landing is justified.

**What I confirmed against the repository**

- The data-RAM hook (`gen_icache_ram.sv`) flips one or two distinct positions inside one 39-bit beat (`inject_mask` keeps p2 in p1's beat and distinct from p1). The tag un-tweak (`tag_tweak`: index at offsets `i*(IC_INDEX_W+IC_TAG_ECC_SIZE)`) matches `rtl/ibex_icache.sv:389-394`; the data tweak (`{addr[31:3],3'b0}` at `i*39`) matches `:342-348`. The OR hit mux is at `:507-513` and `ecc_err_ic1` at `:585`, as the records cite. The probe binds `lookup_addr_ic1` (`[ADDR_W-1:IC_INDEX_HI+1]`, `:114`), width `ADDR_W-IC_INDEX_HI-1` = 21; read-only, knob default 0, debug_only, header and register carry the LOG-079/C10 wording.
- The judge implements the stated semantics: window `p > c && p-c <= 2` (read cycle excluded), `pending_in_window` holds pulses for verdict-pending valid-way data injections, `attribute_pulse` picks owed-uncredited first then excusing (unqualified tag / unjudged data), never a none-owed verdict, `resolve_held` walks the held queue in arrival order, `report_phase` marks end-of-run pending as unjudged before releasing. Pulse without any owing or excusing candidate and owed-without-pulse both fail through `uvm_error` under `chk_alert_minor`.
- Mutants: all six catch/ablate headers carry `+gen_chk_all=0 +gen_chk_alert_minor=1` / `=0`, build shas differ from w16 and match the record; UVM_ERROR totals in the logs are 988/494/483/830/930/13 as recorded; every ablation is 0. Thirteen w16 evidence runs are UVM_ERROR 0 with all checks on. Far program shas and image crc/words match the program-tie files. `ut_isa_cov_zc` self-test line says 131 cases, 0 failures. The `hx_rs_field`/`insn_has_rs1` fix admits funct3 011 only for `rd==2` (c.addi16sp), two UT rows added. WP12-F2's trace (`gen_fu_l16_TRACE_index26.log`) does show way 0 and way 1 both valid with tag 00100000 at index 26 (cycles 1908/1916, and 2125's `v0=1 v1=1`) before the joint invalidation at 2127. Plan-review commits 5c58317/3012239/f1c9d70 exist.

**Findings**

[major][dv/auto_dv/evidence/gen_tdd_step2b.md:685] The Section 16 figures for duplicate copies (16/4, 20/2, 19/14), forms a/b agreement (554/554, 583/583, 575/575, 20/20, 174/174, 185/185, "32 of 243" at line 710), (b)'s latency (7..16, minimum 4 at line 713) and the alignment histogram (line 702, "00100000 in 20448 of 20509 cycles") are not in any retained artifact: every `*_stdout_excerpt.log` truncates the `GEN_MISC` summary at 400 characters (e.g. `gen_fu_l16_ecc_data_freq_stdout_excerpt.log:35` ends at `other_way`), so `other_way_pulses`, `held_pulses`, `duplicate_copies`, `forms a/b` and `b latency` are cut off, and no file holds the probe-tag histogram. These a/b numbers are the only evidence that the measured-run form (b) agrees with the probe. Recommendation: retain the full `GEN_MISC` line per run (or an untruncated summary excerpt) and the alignment count, and re-derive the record's figures from them.

[major][dv/auto_dv/mutations/gen_mut_step2b.md:222] The measured-run judge (form (b), `gen_checkers_pkg.sv:555-597`) has no catch evidence of its own: RED0, DATAANN, DATAMISS, DATAWAY and ALIGN all run with `+gen_probe_ic_lookup=1`, where `judge_data` takes `va` and form (b) is statistics only; BITS is tag-only. With the probe off, form (b) judges 148 of 494 owed injections on the one-region program and 27 of 180 on the far program (the noprobe summaries), the rest excusing pulses as unjudged. Recommendation: add a DATAMISS and a DATAWAY catch with the probe off (both programs) so the checker that actually runs in measured entries is shown to fail, and state the judged fraction in measured runs as the checker's power in Section 16 and the API row.

[minor][dv/auto_dv/tb/gen_icache_ram.sv:92] `{shadow_tag(...)[20:0], addr[7:0], 3'b000}` hand-encodes `IC_TAG_SIZE-1`, `IC_INDEX_W` and `IC_LINE_W`; likewise the probe's default `TagW = 21` (`gen_ic_lookup_probe.sv:9`). Recommendation: derive from `ibex_pkg` (`IC_TAG_SIZE-2:0`, `IC_INDEX_W-1:0`, `{IC_LINE_W{1'b0}}`) so a geometry change cannot silently mis-address the un-tweak.

[minor][dv/auto_dv/evidence/gen_tdd_step2b.md:739] Refers to `gen_l14_testlist_entries.yaml`, which is not in the tree (`git ls-files` finds no such file). Recommendation: commit the file or name where the probe-on/noprobe candidate entries actually live.

[minor][dv/auto_dv/docs/gen_probe_register.md:31] The P9 row's boundary-alternative column says form (b) is "the DV Lead's measured-run form (b), not built here", while this landing builds it (`tag_b`/`verdict_b`). Recommendation: reword to "built in the misc monitor; see the alert_minor row".

[minor][dv/auto_dv/evidence/gen_critic_response_fu2a.md:195] The CM171 (first) rule text says "an unqualified tag injection never consumes a pulse", but as built it sits in the excusing tier and does absorb a pulse when nothing owes it (pre-existing tag behaviour). Recommendation: say "never takes a pulse from an owed injection".

Rubric results: ai-slop-comments PASS, rtl-purity PASS, magic-numbers FAIL (the [minor] above), forces-and-hier-access PASS (read-only bind, justified in header and `gen_binds.sv`), assertion-integrity PASS (alert_minor checks restructured, not weakened; lat-0 pulses now fail).

Final verdict: APPROVE-WITH-CHANGES
