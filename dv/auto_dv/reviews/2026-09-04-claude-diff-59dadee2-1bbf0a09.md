# Cross-model review - committed diff 59dadee2..1bbf0a09

**Reviewer:** claude CLI 2.1.260 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session b9630115-50ee-4ca6-8f24-686dc46e0fb2; sandbox: bubblewrap, working directory = detached read-only checkout of commit 1bbf0a0901453ea4b6bb0e7bce392d39f52fe477 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit 1bbf0a0901453ea4b6bb0e7bce392d39f52fe477
**Date:** 2026-09-04
**Target:** committed diff 59dadee2..1bbf0a09 (echo at raw line 1)

---

TARGET: 59dadee24da19e5576b7908ccf03b4bf37bc0be9..1bbf0a0901453ea4b6bb0e7bce392d39f52fe477

Reviewer: Claude (claude-fable-5-1), fresh session, read-only detached checkout of 1bbf0a0; one commit in range.

**Verified against the tree (recomputed, not read):**
- Build identity: `gen_flow_util.filelist_digest` over `dv/auto_dv/tb/gen_rtl.f` + `gen_tb.f` on this checkout gives `b48479a3bc6f1d9f…`, 117 sources. Equal to the figure in all three retained headers. CM200-Major-1's remedy is met: the gate can now recompute the number the record claims.
- Identity blocks: baseline hashes `a59dd6fe0ced0033` (gen_tb_pkg.sv), `d4b339e24ff36ba8` (gen_fcov_pkg.sv), `d4b41edaa722a2e3` (gen_checkers_pkg.sv), `fc376b9db3ad3868` (gen_icache_ram.sv) all equal the committed blobs. Applying each of the six logged diffs to the committed blob reproduces the logged mutated hash exactly: UNINITQ 9e2a149f03fe2cf1, WINSHORT 838ecf44cf15a987, UNINITQ_ABL 888be574c95d16cc, WINSHORT_ABL cff18c9758c19583, UNINITALL 8c75b4f2890e24fd, UNINITDRAIN 972307eb7e5f17c8. Ablation blocks name the kept fault in applied order (CR-24-L-2 met).
- Self-test: gen_fcov_pkg.sv holds exactly 148 `GEN_FCOV_UT` invocations; the retained failure lines cite :1924/:1925/:1928 and those lines hold the named cases; 146 = 148−2 and 144 = 148−4 are the two ablation removals (CR-24-L-3 / CM200-Minor-2 met). ci/check_fcov_expectations.py sha256 prefix 282127c9994dd824 matches the cross-bins log.
- gen_manifest.md sizes/md5 for the three logs match the committed files.
- Manifests: nine files, `test` == stem in each, `bins` == `anti_vacuity` keys, union is exactly 13; deleted group manifest minus union = {during_invalidation, masked_duplicate_copy} and nothing else. Per-entry counts in the headers agree with the plan's (10, 9, 22) and (4, 2, 14). `gen_fcov.py --validate` sweep: 27 OK, exit 0 (CM199-I-1 / CM200-Minor-1 met).
- Knob derivation: `(IC_SIZE_BYTES // IC_NUM_WAYS // IC_LINE_BYTES) * IC_NUM_WAYS` matches ibex_pkg.sv:405's definition of IC_NUM_LINES; `gen_knobs_codegen.py --check` reports up to date; the `_PY` twin is compared in gen_tb_top.sv:79-80 (CM200-Low-1 met). History parenthetical gone from gen_tb_pkg.sv:548 (CM200-Low-2 met).
- RTL citations read line by line in rtl/ibex_icache.sv: :257 top bit of fill_tag_ic0 is `(~inval_write_req & ~ecc_write_req)`; :266 lookup_actual_ic0; :277 tag_write_ic0's three writers; :280/:283; :294/:302 tag ECC encode; :499-500 compare against `{1'b1, lookup_addr…}` with the literal on :500; :501 tag_invalid_ic1; :504 `tag_hit_ic1 = |tag_match_ic1`; :507-514 the always_comb mux; :568-573 the decoder instance; :583-584 the comment; :585 the term. All correct; the two-mechanism argument and its exhaustiveness claim hold (CM200-Minor-3 / CM199-M-1 / re-opened CR-23-L-2 met at gen_icache_ram.sv:106-111).
- Testlist: the eight entries exist under those names at gen_testlist.yaml:1912-2378; `gen_ut_lockstep_icache_ecc_tag_disabled` appears nowhere outside its manifest, as stated.

**Findings**

[Minor][dv/auto_dv/docs/gen_wp8_part1_plan.md:429] As committed, no run enforces any of the nine manifests. The flow binds a manifest only through the entry's `fcov_expectation_file` (gen_fcov.py:71-75; check_test returns NO_MANIFEST at :337-340 when it is null), and all eight WP-8 entries carry `fcov_expectation_file: null` (gen_testlist.yaml:1920 and the seven siblings). The 27 OK sweep is 18 bound manifests plus exactly these nine unbound ones. The plan and the CM200-Minor-1 row describe the check as "per entry" and say only the ninth entry is staged for Runtime; neither says the eight bindings are also outstanding, so a reader takes the 13 bins as enforced when they are declared only. - State in Section 7 and in the CM200-Minor-1 row that the eight `fcov_expectation_file` bindings are staged for the Runtime Manager with the ninth entry, and hand them over as one list; until then label the fcov-expectation leg "declared, not yet gated".

[Low][dv/auto_dv/evidence/gen_critic_response_fu2a.md:406] The CR-24-L-1 row says "gen_icache_ram.sv 836f9c2d76b8d7e2, each equal to the block's baseline field". The committed file and the retained log's baseline both read fc376b9db3ad3868; 836f9c2d… matches neither the parent commit's blob (cdfbbdaa096856f8) nor HEAD, so it is the pre-line-span-correction intermediate. - Correct the figure to fc376b9db3ad3868.

[Low][dv/auto_dv/evidence/gen_critic_response_fu2a.md:420] The CM200-Major-1 row names the fix as `scratchpad/build_identity.py`, which is not in the tree; the only committed identity tool, dv/auto_dv/tools/gen_mutant_build_identity.py, is a per-file differ, not a digest recompute. The claim is reproducible anyway (I reproduced the digest via the flow module), but the record points at an artefact no reviewer can open. - Either land the script under dv/auto_dv/tools with the gen_ prefix or say it is an uncommitted work file and give the one-line recipe (import gen_flow_util, call filelist_digest on the two lists).

[Low][dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l23_wp8_cov_reds.log:16] The GREEN control's FCOV-EXPECTATION lines ("FAIL - 5 declared bin(s) not hit: … disabled_cache, during_invalidation, masked_duplicate_copy") were produced against the group manifest this same commit deletes, and the header explains the exit code by "the group manifest". The HIT→UNHIT discrimination stands, but the run is no longer reproducible from the committed manifest home. - Name the manifest used (or retain it as the log's fixture), or note that against the entry's per-entry manifest the control would read all-hit.

[Low][dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l24_wp8_ut_muts.log:15] The unmutated "self-test: 148 cases, 0 failures" line is quoted in header prose, not retained as a root block with gate identity and local figure like the four mutated roots, so the file's own "the run's own line" convention is not applied to the baseline it rests on. - Add a GREEN root block for build L25b.

[Low][dv/auto_dv/fcov_expectations/gen_ut_lockstep_icache_ecc_data.fcov.yaml:8] Header boilerplate: "Two of those are OWED group-wide" follows a one-item exclusion list here and in _data_two, _tag_two and the base entry; in _far_data and _far_data_noprobe the listed items are not the owed ones at all. - Per-manifest wording: "of the group's two owed bins, this entry excludes …" or drop the sentence where it does not apply.

[Info][dv/auto_dv/evidence/gen_critic_response_fu2a.md:411] The row labelled CM199-M-1 has no Major counterpart in 2026-09-04-claude-diff-f0723d6d-1a7f5066.md (that artifact carries only Lows and the I-1 Info); the label follows the DV Lead's relay numbering. The RTL argument in the row is correct regardless; note the source of the numbering so the row is traceable.

**Rubrics:** rtl-purity PASS (no rtl/ change); forces-and-hier-access PASS (no forces or raw deposits added); magic-numbers PASS (the hand-typed 512 is replaced by a derivation from ibex_pkg; the `_PY` literal is rendered and twin-checked); ai-slop-comments PASS on filtered files (the new gen_icache_ram.sv comment is intent and RTL anchors; the history parenthetical is removed; the plan's "as an earlier version of this paragraph did" is a correction record in an unfiltered .md); assertion-integrity PASS (a `$fatal` guard is added; the declared bin set drops 15→13 with the two removals named, counted and owed, and `+gen_chk_all=0` appears only in evidence runs).

**Disposition of the re-review target:** CM200 Major-1, Minor-1..3, Low-1..2 and CR-24 L-1..L-3 are each resolved as the committed files show, with the identity now recomputable and reproduced here; the Minor above is a record gap on enforcement, not a defect in the evidence.

Final verdict: APPROVE-WITH-CHANGES
