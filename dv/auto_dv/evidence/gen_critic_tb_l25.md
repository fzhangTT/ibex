# Critic verdict: tb-infra landing 25, the re-review for CR-24 and CM200 (commit 1bbf0a0, diff base 59dadee), reviewed as tb_l25

Scope (the Orchestrator's): twenty files plus the deletion of gen_cg_ic_ecc_part1.fcov.yaml; the recorded re-review for gen_critic_tb_l24.md's CR-24 lows and
for the cross-model REQUEST-CHANGES rows CM200 on landing 24, also answering CM199 M-1 and I-1 as peer-doc rows. Verified rather than taken: the nine
per-entry manifests; the build identity as the flow's filelist_digest in every retained header beside the labelled local compile figure; the identity
blocks' baselines taken from the file the diff was applied to; the ablation blocks naming the kept fault; the self-test baseline and the untruncated
failure lines; the derive: on GEN_ICRAM_UNINIT_Q_DEPTH with its twin check; the RAM comment and the plan carrying the two-mechanism wording agreed with the
DV Lead; the CM200-Major-1 row stating the measured fact. The staged ninth testlist entry block is Runtime's and outside this target.

Artifacts reviewed (committed blobs at 1bbf0a0; sha256 first 16 hex):

- dv/auto_dv/tb/gen_icache_ram.sv  fc376b9db3ad3868
- dv/auto_dv/tb/gen_knobs_codegen.py  6d56a963e188c8eb
- dv/auto_dv/tb/gen_tb_knobs.yaml  de20aa18d3e186ba
- dv/auto_dv/tb/gen_tb_pkg.sv  a59dd6fe0ced0033
- dv/auto_dv/tb/gen_tb_top.sv  736a8d8099339024
- dv/auto_dv/docs/gen_wp8_part1_plan.md  ff203f76129cb978
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  2198c8c29b946f8d
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  b8c073f89d18de86
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l24_wp8_ut_muts.log  b0a27b7a91d92801
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l23_wp8_cov_reds.log  71cc558e7582a6c2
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l23_fcov_checker_cross_bins.log  2f490224bd47811f
- dv/auto_dv/fcov_expectations/gen_ut_lockstep_icache_ecc.fcov.yaml  542eb9b504f2ad71
- dv/auto_dv/fcov_expectations/gen_ut_lockstep_icache_ecc_both.fcov.yaml  1ade221a9bfc2e61
- dv/auto_dv/fcov_expectations/gen_ut_lockstep_icache_ecc_data.fcov.yaml  78ac9dc779e2d3ee
- dv/auto_dv/fcov_expectations/gen_ut_lockstep_icache_ecc_data_noprobe.fcov.yaml  ea40ba28dce695f1
- dv/auto_dv/fcov_expectations/gen_ut_lockstep_icache_ecc_data_two.fcov.yaml  ad27374b49ee618e
- dv/auto_dv/fcov_expectations/gen_ut_lockstep_icache_ecc_far_data.fcov.yaml  8a2a6e7f4e426d8b
- dv/auto_dv/fcov_expectations/gen_ut_lockstep_icache_ecc_far_data_noprobe.fcov.yaml  76749bc198dea0a7
- dv/auto_dv/fcov_expectations/gen_ut_lockstep_icache_ecc_tag_disabled.fcov.yaml  5e6f51a5e10c5f26
- dv/auto_dv/fcov_expectations/gen_ut_lockstep_icache_ecc_tag_two.fcov.yaml  3c8de0e1940eca0f
- deleted: dv/auto_dv/fcov_expectations/gen_cg_ic_ecc_part1.fcov.yaml (the group manifest)

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_critic_tb_l24.md
(3cb1c007fa396cd7) and its supplement (0d2cf52e63596418); the CM200 artifact (f0653b574d12cd65); rtl/ibex_icache.sv:499-501, :504, :507-514, :568-573, :585
(read: the tag compare with the valid bit as its top bit, tag_hit as the OR of the per-way match, the hit-data mux over the matching ways, the data
decoder over the mux output, the data term gated by tag_hit); the DV Lead's v4m (09b4536, gen_fcov_plan.md:4864 "evidence of unhit-way masking, which
holds BY CONSTRUCTION").
Method: detached git worktree of 1bbf0a0 and copies. The files list (sha256 f407d8069de4, 20 rows) equals the added-and-modified diff, the deletions
list (7d4cdd8c0af0, 1 row) equals the deleted diff, and 20 of 20 md5s (ecc4a3b53bba) verify. Gates on the worktree, all PASS: gen_knobs_codegen --check,
gen_ut_knobs_codegen 0 failures, gen_fcov_codegen --check, gen_ut_fcov_codegen 0 failures, CONST-CHECK, gen_fcov.py --validate 27 OK 0 FAIL, the flow
self-test 151 ok (the loader red of 71f207c inside it). Both identities recomputed by me with the tools' own functions: gen_flow_util.filelist_digest
over the gen_tb build's gen_rtl.f and gen_tb.f gives b48479a3bc6f1d9f over 117 sources, the value every retained header names as the gate identity; the
TB-source recipe gives f80e2c719e16b73c, the value the headers label as the local compile figure. The nine manifests parsed: test equals the file stem
for all nine, notes equal bins for all nine, the union of bins is exactly 13, every note carries a measured count of at least 30 or a structural
bound (0 notes with neither), cp_no_alert_case.during_invalidation and masked_duplicate_copy are declared nowhere, eight stems are testlist entries
(at fcov null pending Runtime's repoint) and gen_ut_lockstep_icache_ecc_tag_disabled is not in the testlist. Every identity block re-derived from
committed files alone: each baseline hash equals the 1bbf0a0 blob of its file (6 of 6 roots, 8 of 8 blocks), each logged diff applied to that blob
gives the logged mutated hash (8 of 8), each root's local compile figure equals the tree recipe with its mutated files swapped in (6 of 6, the two
ablations with both their files), and the two ablation blocks list the kept fault in application order. Each mutated root's own filelist_digest
computed with the swapped contents (they differ from the tree's, L-1). The self-test lines read as retained (L-2). The RTL lines the two-mechanism
wording cites read at source; the derive path read in the generator, the yaml, the rendered _PY twin and the gen_tb_top.sv guard. No subagent used.
EXPOSURE: none beyond the Orchestrator's message and the git log subjects. Section 6 says whether this range's cross-model artifact was read.

CRITIC VERDICT: APPROVE. Every CR-24 row and every CM200 row is answered with evidence that reproduces from the committed tree under the identity the
gate reads, the nine manifests are what the flow can check, and the plan, the comment and the notes now say what the never-written bin witnesses with
the RTL terms quoted. Two lows on the record of the identity and the baseline line, neither touching what the runs show.

## 1. What was verified

| item | as built at 1bbf0a0 | evidence (re-derived by me) |
|---|---|---|
| the nine per-entry manifests | one per WP-8 icache ECC entry, test = stem = entry name, bins the entry hits robustly (a structural bound or a measured count of at least 30 in the entry's own run, the count in each note), union 13 of the 15 part-1 bins; the two thinly hit bins owed to a seed sweep and declared nowhere; two per-entry exclusions stated in headers; the ninth entry (the cache never enabled, cp_no_alert_case.disabled_cache at 864) staged for Runtime | parsed: 9 / 9 stems equal tests, 9 / 9 notes equal bins, union 13, 0 notes without a count or a structural bound, 0 counts under 30, the two owed bins absent; the schema sweep 27 OK |
| the build identity (CM200-Major-1) | every retained header names the gate identity b48479a3bc6f1d9f (filelist_digest, 117 sources) and, labelled, the local compile figure f80e2c719e16b73c; the cross-bins log the same | both recomputed with the tools' own functions on the worktree: equal |
| the identity blocks (CR-24-L-1, L-2) | baselines from a pristine copy taken before any mutation; the ablation blocks list the kept fault and the removed cases in application order | 8 of 8 baselines equal the 1bbf0a0 blobs; 8 of 8 diffs reproduce the mutated hashes; 6 of 6 local compile figures reproduce |
| the self-test baseline and the failure lines (CR-24-L-3, CM200-Minor-2) | the catch roots carry "self-test: 148 cases, N failures" and the untruncated uvm_error lines (file, line, time, component, id, the case name, got and expected); the ablation roots carry 146 and 144 cases, 0 failures; the unmutated build's "148 cases, 0 failures" is stated in the header | the lines read; the baseline line's retention: L-2 |
| the derive twin check (CM200-Low-1) | the yaml constant uses derive: icram_lines_x_ways; the generator computes IC_SIZE_BYTES / ways / line bytes x ways from ibex_pkg; the rendered GEN_ICRAM_UNINIT_Q_DEPTH_PY = 512 sits beside the sv expression; gen_tb_top.sv compares the two at elaboration and $fatal-s on a mismatch | the diffs; 4096 / 2 / 8 x 2 = 512 |
| the never-written bin's mechanism (CR-23-L-2 re-opened site, CM199-M-1, CM200-Minor-3) | gen_icache_ram.sv comment, the plan (Sections 5 and 7) and the anti-vacuity notes carry the two exhaustive mechanisms with :499-500 (the valid bit in the compare), :504 (tag_hit = OR of the per-way match), :507-514 (the mux), :568-573 (the decoder over the mux output), :585 (the masked term); the DV Lead's v4m says the same | the five RTL spans read at source; the deleted history parenthetical (CM200-Low-2) gone |
| the response rows | CR-24 L-1..L-3 DONE (L-3 with the 148-case correction); CM199 M-1 as a peer-doc consequence, I-1 mine and closed by deletion with the root cause; CM200 Major-1 with the fact measured (the roots were fb494f4's sources; the baselines and the missing gate figure were the true defects), Minor-1 closed by deletion, Minor-2, Minor-3, Low-1, Low-2 DONE; a line-span table correcting three citations with the plan owner | read against the diffs and the tree |

## 2. Verdict per row

- CR-23-L-1 (the group manifest): CLOSED on tb-infra's side by the nine per-entry manifests and the deletion; Runtime's repoint of the entries and the
  ninth entry's block are Runtime's touch.
- CR-23-L-2 (re-opened on the comment site in the tb_l24 supplement): CLOSED; the comment carries the two mechanisms.
- CR-24-L-1: CLOSED. CR-24-L-2: CLOSED. CR-24-L-3: CLOSED with the correction that the run's own line is the 148-case total (L-2 below on its retention).
- CM200 Major-1: answered with the measured fact; Minor-1, Minor-2, Minor-3, Low-1, Low-2: answered. CM199 M-1 and I-1: answered.

## 3. Findings

### L-1 (low) [S4 record] A mutated root's "gate identity" line quotes the unmutated tree's digest

Every root block reads "gate identity: b48479a3bc6f1d9f", the digest of the unmutated tree, while a root that carries a mutation has a different
filelist_digest by construction (recomputed with the mutated contents: UNINITQ 6ce5351e5daef0bc, UNINITQ_ABL 4952cd34d2c337f6, WINSHORT 34e7dd5af004e920,
WINSHORT_ABL 3944a159f6f6e5e3, UNINITALL 0cef864e4ded9a27, UNINITDRAIN 079a2867330a422e). The blocks' baseline-plus-diff identity is complete and exact, and
the local compile figure IS per root, so nothing is misidentified; the label is. Call the line "base identity" for a mutated root, or add the root's own
digest beside it, so the two identity columns say the same kind of thing.

### L-2 (low) [S6 retention] The unmutated build's self-test line is quoted in a header, not retained in a root block

The ut_muts header states "On the unmutated build the run reports 'self-test: 148 cases, 0 failures'", but neither log's GREEN block carries that line as a
run line (the cov_reds GREEN block holds the uninit statistic and the FCOV lines only), while every mutant root carries its own "self-test: ... cases, ...
failures" line. The ablation counts (146, 144) and the catch counts (148 with 2 and 1 failures) make the baseline's arithmetic certain, so this is
retention form, not substance: add the GREEN root's line to its block.

### Informational

- I-1: the eight committed entries still read fcov_expectation_file null; the manifests exist for them and Runtime's repoint is the next flow touch. Until
  then no run checks them, which is the intended order (manifests before entries).
- I-2: the two owed bins (during_invalidation 10 / 9 / 22, masked_duplicate_copy 4 / 2 / 14 across entries) close on a seed sweep at coverage closure; the
  plan says so and declares them nowhere, which is the honest form.
- I-3: the CM200-Major-1 row records the fact as the Orchestrator and I measured it, including what was true in the reviewer's row (the pre-landing
  baselines; no gate-recomputable figure), and names the root cause (two identity functions, the wrong one quoted). The disagreement is closed on the
  record with evidence, as it should be.
- I-4: the twin check now compares rather than documents (the gen_tb_top.sv guard), which removes the cost tb-infra had disclosed in landing 24.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S6 retention and identity: every retained header carries the identity the gate recomputes,
every mutant root's identity reproduces from committed files (conforming; L-1, L-2 on labels and one line). S5 single source: the bound derived from
ibex_pkg with a compared twin (conforming). S4 honesty: the fact disagreement recorded with the measurement, the owed bins named, the exclusions stated
per entry (conforming). fcov-expectation: per-entry manifests with a note per bin and a robustness rule the notes carry (conforming). One-line verdict: PASS.

## 5. Verdict

CRITIC VERDICT: APPROVE. The REQUEST-CHANGES chain of tb_l23 is closed on the Critic's side. Lows L-1 and L-2 with tb-infra's next records touch. Rows CR-25.

## 6. The cross-model review of this range

Not read: at hand-off dv/auto_dv/reviews/2026-09-04-claude-diff-59dadee2-1bbf0a09.md was the wrapper's empty placeholder (0 lines, sha256 of the empty
input e3b0c44298fc1c14; `git log` names no commit for it): the review of 59dadee..1bbf0a0 was still running. Its rows are reconciled by the Orchestrator's
relay or in my next verdict; the tb_l23 chain closes for both sides when that review passes too.
