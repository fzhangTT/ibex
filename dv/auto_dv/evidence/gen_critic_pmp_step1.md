# Critic verdict: pmp-step1 (four PMP covergroups, three every-seed manifests, the measured flip; LOG-096 family)

Range 2d87642..5db73d4 (full 5db73d409f76b533cfe16d000f687d62f8722bf2), named by the Orchestrator. Group commits:
218e9f3 (tb-infra-2 + DV Lead: the render, codegen fix, unit test, render log, plan overlay v2, verifier fix), 253f08e
(Test Writer: three manifests, the two test modules' bins_not_hit dicts, record Section 12), b74ca93 (runtime-2:
testlist flip, tier held), 5db73d4 (runtime-2: the 40-seed measurement block retained). Riding the range and judged
elsewhere or as records: 27212cb, 109b654 (plan touches; the PMP declaration state and CG-PMP-014 statement are read
here), 8057f49, 00c80d7, 9c3ac1b, c08d2ab (records), 298642c (register and S6), e6eb3a2 and e1bee86 (irq groups).
Artifacts at 5db73d4 (sha256 first 16 / lines):
- dv/auto_dv/env/gen_fcov_groups.svh 56dbf344f2ddb1ef / 5171; dv/auto_dv/env/gen_fcov_pkg.sv da7bb211f4bc77db / 2305;
  dv/auto_dv/tb/gen_fcov_codegen.py 9b2fe1ee48dcc287 / 242; dv/auto_dv/tb/unit/gen_ut_fcov_codegen.py a2b9ee103bde51b0 / 132;
  dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_pmp1_covergroups.log 8901217a6970479f / 128 (all identical since 218e9f3)
- dv/auto_dv/docs/gen_fcov_plan.md 33d009d695d96ba0 / 6968; dv/auto_dv/tools/gen_unbuilt_mark_check.py 67100f92db3c7b30 / 207
- dv/auto_dv/fcov_expectations/gen_test_pmp_csr_warl.fcov.yaml 7fa08b3202020283 / 443; gen_test_pmp_mseccfg.fcov.yaml
  85781936a4e4ba56 / 57; gen_test_pmp_lock.fcov.yaml 22395b0da9e21899 / 84; dv/auto_dv/tests/gen_test_pmp_csr_warl.py
  528f4578a7ad0a82 / 497; gen_test_pmp_lock.py f3d31ec0847c6d33 / 345; dv/auto_dv/evidence/gen_tdd_batch3.md
  2575386b249e105d / 495 (all identical since 253f08e)
- dv/auto_dv/flow/gen_testlist.yaml 63c0c74cc5bc76be / 2507 (identical since b74ca93)
- dv/auto_dv/evidence/gen_pmp_measurement/gen_pmp_40seed.yaml 0f1f7d1e75465688 / 51; gen_pmp_40seed_bins.txt
  ae2aa78dd82d9df2 / 1235; gen_index.md 13e7907d965cb21e / 67
Judged against: LOG-096 (d226a87) and its checklist; LOG-095; LOG-097 addendum 4 (no criterion text in the plan set);
my regen-round1 verdict M-1 condition (gen_critic_regen_round1.md, e6ed6d8); the round-2 form (463a026); DV_prompt.txt
Sections 4 and 6; docs/dv/dv_principles.md d9c27db18f511411 (read fresh; skill dv-principles-check).
Date: 2026-09-05T06:13:52Z   Role: Critic
Method: detached worktrees of 5db73d4 (the range end), 218e9f3 and 2d87642 in my scratchpad, removed after the logs were
retained under dv/auto_dv/work/critic/pmp1/ and critic/regen1/; every tool run by me on those trees (codegen --check and
unit test in both directions, gen_build_identity.py, gen_unbuilt_mark_check.py with my prose-name fixture, the manifest
renderer, the loader / selector / fcov policy, gen_covergroup_set.py); the every-seed rule re-derived by my own parser over
the retained measurement against the committed manifests; the out-tree measurement's build manifest and unmeasured merge
report read; the RTL and the sampler read at the cited lines. The range review (rev49, running) was NOT read before
Sections 1-5; Section 6 follows. Exposure: the Orchestrator's naming message summarised the group and my own conditions;
my pre-verification notes (gen_pmp1_prep_notes.md) predate it. Re-handed after a withdrawal: the first hand-off
(d30984b2ef8d72fa) carried a row L-2 stating the retained bins file lists the every-seed set only; that was my parser
matching one tag's case, not the file; corrected at 2026-09-05T06:18:34Z with the cross-check in Section 3. Re-handed a second time after the range review rev49 (fd36d17) landed: it was read
after Sections 1-5 were written and handed; its two Majors were verified by me at 2026-09-05T06:26:31Z against the sampler code and
the retained measurement and are adopted as M-1 and M-2; my Sections 1-5 had missed them (I traced the sample event and the
RTL WARL terms but not the bin classifiers against those terms). The verdict changed from APPROVE to REQUEST-CHANGES,
confined as stated at the end.

## 1. What the group delivers, and what each part was checked to be
- 218e9f3: gen_fcov_groups.svh gains four covergroups rendered from the plan (gen_pmp_cfg_write_cg CG-PMP-001,
  gen_pmp_addr_write_cg CG-PMP-002, gen_pmp_csr_access_cg CG-PMP-004, gen_pmp_table_state_cg CG-PMP-014; CG-PMP-003 kept
  for step 1b with its marks), sampled from one per-record entry point pmp_record(t) in gen_fcov_pkg.sv (:1774), fed by
  the RVFI monitor and reading the MODEL's PMP table through the ISA shim. The plan overlay drops the not-built tag on
  exactly 41 lines inside those four covergroups and fixes one tuple token ("written verbatim" -> "written: stored
  verbatim"); my diff 2d87642..218e9f3 counts 41 and 1, as the render log states. The codegen fix (the tuple parser cuts a
  bin's braces at the first colon-bearing part before splitting on commas) carries one unit-test case. The verifier reads
  declarations only (my regen-round1 M-1 condition).
- 253f08e: the three manifests, rendered from the plan at 27212cb, declare only bins the 40-seed measurement found hit at
  every seed of the entry (179 / 26 / 39); the test modules' change is data, the bins_not_hit dicts that give each removed
  bin its reason (csr_warl 81 entries, lock 2), no check or fire method touched (the diff has no def / class line).
- b74ca93: the three entries measured true with stem-named manifests, tier held (csr_warl smoke; mseccfg, lock
  targeted), notes cleared, seeds left at 3.
- 5db73d4: the measurement block retained byte-identical to runtime-2's served copies with an index naming the run,
  the pin 218e9f3, base seed 218090305, 120 planned / 119 ran, the WARL 39-seed denominator and the asserting seed.

## 2. The LOG-096 family checklist, item by item
1. COMPILES IN THE HEAD-MODE BUILD WITH ITS IDENTITY STATED. The measurement's own build is the head-mode mirror of
   218e9f3 (out-tree build_manifest.yaml: source_mode head, head_sha 218e9f32316c..., covergroups_declared true,
   sources_sha256 596b04c95332e2aa...); gen_build_identity.py on my worktree of 218e9f3 gives 596b04c95332e2aa, the
   value the render log states as the gate key. The unmeasured merge of that run reports the four covergroups with
   coverage (cov_unmeasured/report/groups.txt: cfg_write 153/154, addr_write 107/109, csr_access 53/66, table_state
   41/78), the positive control the retained yaml describes. At the range end the gate key is 32f878987926e4e2 because
   gen_agents_pkg.sv (e6eb3a2) and gen_checkers_pkg.sv (e1bee86) are .f-listed and changed in the irq landings; the four
   covergroup sources are byte-identical between 218e9f3 and 5db73d4 (O-1).
2. CODEGEN RENDER UP TO DATE, UNIT TEST PASSES. gen_fcov_codegen.py --check on the 5db73d4 worktree: "up to date";
   gen_ut_fcov_codegen.py: PASS (0 failures). Both directions: the same unit test file against the pre-fix codegen at
   2d87642 fails exactly one case ("a cross tuple whose prose after the colon contains a comma still parses").
3. SAMPLING POINT AND FIELD SEMANTICS STATED AND CHECKED. The render log states, per covergroup, the sample event and the
   signal source: csr_access on every retired PMP CSR instruction, trapped ones included (pmp_record :1786 samples
   before the !t.trap test); cfg_write one sample per entry byte of a retired, untrapped, non-read-only pmpcfg write
   with the attempted value from rs1_rdata or the immediate read-modify-written over the pre-state word (pmp_rmw);
   addr_write one sample per pmpaddr write with the entry's own and the next entry's cfg and RLB; table_state a whole-
   table snapshot after any PMP CSR write, deferred until a record retires before the next change. The field caveat
   that fixed the design is measured, not assumed: at the coverage subscriber the model has not executed the record
   being handled, so the write's effect is read at the NEXT record (pmp_record :1777-1783: pmp_read_now, then the pending
   write's samples and the snapshot close). Two further caveats are cited to the TB (a CSR write reaches RVFI two cycles
   after commit, gen_tb_pkg.sv:240; rvfi_mem_rmask not gated by a load, gen_rvfi_pkg.sv:550) and respected (class and op
   from the decoded instruction). RTL terms the samplers' classes rest on, read: the PMP CSR block exists under
   rtl/ibex_cs_registers.sv:1362 "if (PMPEnable) begin : g_pmp_registers"; the WARL legalisation of the written cfg byte
   at :1429 (lock = bit 7), :1433-1438 (A: 00 OFF, 01 TOR, 10 NA4 only when PMPGranularity == 0 else OFF, 11 NAPOT),
   :1441 (X), :1444-1445 (W = wdata[1] under MML, else wdata[1] & wdata[0]: W without R forced 0), :1446 (R). The
   samplers classify the ATTEMPTED word and read the post state from the model, so the DUT-versus-model agreement on
   the stored value is the lockstep's, not the covergroups'. THE CLASSIFIERS OF TWO COVERPOINTS DO NOT FOLLOW THOSE RTL
   TERMS (adopted from rev49, verified by me): CG-PMP-001 cp_outcome (:1866-1873) books an ignored_* outcome whenever
   post_b == pre_b and the RAW attempted byte differs from pre_b, without the plan's gate "L=1 before the write and
   RLB=0" and without the legalised expected byte (bits 6:5 never stored, W forced 0 when R=0 under MML=0), so a no-op
   write on an unlocked entry is booked ignored_lock; and CG-PMP-004 cp_first_after_reset (:1687-1689) is one run-wide
   flag cleared by any PMP CSR access where the plan (:2579) defines it per CSR. Item 3 FAILS for these two coverpoints
   (M-1, M-2); it holds for the sample events and the remaining fields.
4. UNREACHABLE BINS MARKED OR EXCLUDED WITH A REASON. The render log states no bin is unreachable at this configuration
   (PMPEnable 1, 16 regions, granularity 0) and lists what no stimulus reaches today (cp_regime's sparse / dense / mml_on:
   no program-side regime; cp_dbg.d1: no debug-mode CSR access), correcting an earlier false premise on mml1 / rlb1 by
   citing the Test Writer's programs. One class is missing from that statement: two addr_write cross bins are
   unreachable by the SAMPLER'S CONSTRUCTION (L-1), and the four cr_reset_read cross bins are unreachable AS BUILT
   (M-2): the measurement shows rst_pmpcfg, rst_pmpaddr, rst_mseccfg and rst_mseccfgh at 0/N in all three entries.
5. MANIFEST CONSEQUENCE STATED. The plan at 5db73d4 (:98-107, from 109b654) says the four are built, carry no mark, and
   that CG-PMP-014 "IS DECLARED BY NO MANIFEST, by design and permanently", an expected-from-random-tests covergroup
   (its items are Phase 2 random stimulus). The three manifests declare bins on the other three covergroups only (my
   count: csr_warl 179 on cfg_write / addr_write / csr_access; mseccfg 26 on cfg_write / csr_access; lock 39 on
   addr_write / cfg_write). gen_unbuilt_mark_check.py at 5db73d4: 30 rendered, 106 marks of 1884 on 177 unbuilt, 25
   referenced manifests judged of 27, 0 declarations on an unrendered covergroup, PASS.
6. TRUST TRIAD UNCHANGED FOR TESTS AND CHECKERS. No checker or test check changed in the group: the test modules gained
   bins_not_hit data only; the manifests are the fcov-expectation leg and their evidence is the measurement below. The
   codegen fix is a tool change proved by its unit test in both directions. The covergroups carry no red or mutation
   proof, as LOG-096 rules.

## 3. The flip and the every-seed rule, re-derived
- Loader at 5db73d4: 105 entries; the three PMP entries measured true with manifests whose stem equals the entry name;
  tier full selects 20 entries / 56 runs, 15 measured entries / 45 runs; fcov_policy_failures on an all-PASS plan of
  that selection: none. The three manifests re-render byte-identically on the 5db73d4 worktree
  (gen_fcov_manifest.py --test-module dv/auto_dv/tests/<test>.py --test <test> --write; git status empty).
- Every-seed rule (my parser over gen_pmp_40seed_bins.txt): every declared bin is an EVERY-seed bin of its entry
  (csr_warl 179 of the entry's 215 EVERY bins over 39 seeds; mseccfg 26 of 175 over 40; lock 39 of 139 over 40); no
  removed bin is EVERY-seed; declared plus removed equals the owned set (csr_warl 179 + 78 seed-dependent + 2 stimulus
  + 1 declaration = 260; lock 39 + 2 declaration = 41; mseccfg 26, with TP-PMP-108 not built for want of a bridge reset);
  the EVERY bins not declared belong to other items or to gen_pmp_table_state_cg. The asymmetric cp_mml.mml1 and
  cp_rlb.rlb1 (18/40 for lock, 32/39 for csr_warl) are left undeclared where not every-seed, which is what the rule is
  for. The retained bins file lists all 407 family bins per entry (1221 bin lines: 529 EVERY, 374 some, 318 never,
  each with its k-of-N), so the removals are re-derivable from the commit: the csr_warl manifest's 78 seed-dependent
  reasons carry exactly the table's k/39 (78 of 78 equal, 0 mismatches), and the five declaration- or stimulus-class
  bins (three csr_warl, two lock) read never 0/N there. The 119 runs of the measurement all carry verdict FAIL on one rule ("declares N bins but has no manifest"), fired
  after sampling; the coverage is real (item 1's control) and the block says so (O-2).
- The asserting seed 230969025 (gen_pmp_csr_warl_prog.py:615 from build() :1066) is the reason the WARL denominator is 39;
  the manifests' reasons name 39. seeds_for_test derives 12 or 40 seeds for gen_test_pmp_csr_warl at base 20260904 or
  20260905 without that value (my computation with the flow's function), so round 2 as planned does not draw it; the
  generator fix belongs to the generator group.

## 4. Conformance (dv_principles.md, read fresh)
PASS. Section 1 (stimulus) is untouched by a covergroup landing; Section 2: the manifests fail through the collected
fcov mechanism and are derived from the plan's intent with the measurement deciding the per-run guarantee; Section 4:
the render log states its corrected premise and the 39-seed denominator plainly, the yaml states that every run's verdict
is FAIL and why the coverage stands anyway; Section 5: the codegen and sampler comments state intent; Section 6: the
covergroups are exempt (LOG-096), the codegen fix has its two-direction case, no checker changed. LOG-097 addendum 4:
the plan touches in the range add no criterion or gate text (my grep over the diffs).

## 5. Rows
- M-1 (Medium, environment; tb-infra-2; adopted from rev49 Major 1 and verified). gen_fcov_pkg.sv:1866-1873 classifies
  CG-PMP-001 cp_outcome by comparing the raw attempted byte with the pre byte: `if (post_b == pre_b && a_b != pre_b)` books
  ignored_mml_exec or ignored_lock with no test of pre_b[7] && !rlb, and the else branch books written when the readback
  differs from a_b & 8'hfd even though the DUT never stores bits 6:5 (rtl/ibex_cs_registers.sv:1429-1446). Measured in the
  retained block: csr_warl hits cp_outcome.ignored_lock at 39/39 seeds while cr_lock_outcome.locked_rlb0_ignored, the only
  real ignored_lock case, hits at 23/39; mseccfg hits ignored_lock at 7/40 with locked_rlb0_ignored at 0/40. Those are
  ignored_lock samples with no locked-RLB=0 write behind them: the merged report's credit on that bin is inflated (the
  honesty-over-green rule), and the plan's bin definition (:2508 "ignored_lock{unchanged: L=1 before the write and RLB=0}")
  is not what is sampled. No DECLARED manifest bin rests on a false hit: lock declares ignored_lock backed by
  locked_rlb0_ignored at 40/40; csr_warl declares written and w_dropped only; mseccfg declares ignored_mml_exec only.
  Required: compute the legalised expected byte (mask 0x9f; W &= R when MML is 0), book written / w_dropped when post
  equals it, book an ignored_* outcome only when post == pre and expected != pre, gate ignored_lock on pre_b[7] && !rlb;
  re-run the 40-seed block for CG-PMP-001 and re-render the manifests; my re-review on that landing.
- M-2 (Medium, environment and records; tb-infra-2, the DV Lead; adopted from rev49 Major 2 and verified).
  gen_fcov_pkg.sv:1687-1689: pmp_first_acc is one flag for the run, cleared at :1689 by ANY PMP CSR access; the plan
  (:2579) defines cp_first_after_reset as "no prior write to this CSR since reset" and cr_reset_read (:2584) expects the
  first read of each of four classes. As built at most one of the four cross bins can hit per run; the measurement shows
  all four at 0/N in every run of all three entries, while the render log states that none of the family's bins is
  unreachable. Required: a written flag per CSR class (or per CSR) with yes sampled on a read-only access while that
  class is unwritten; until it lands, the log and the plan name the four cross bins as unreachable by the current sampler.
- L-1 (Low, plan and environment; routed to the DV Lead and tb-infra-2). gen_pmp_addr_write_cg.cr_self_lock.locked_rlb1_written
  and cr_tor_lock.nl_tor_rlb1_written are unreachable by construction: gen_fcov_pkg.sv:1897 self_locked =
  pmp_cfg_pre[i][7] && !rlb and :1908 next_locked = pmp_cfg_pre[i+1][7] && !rlb, so a cross requiring locked with rlb1
  can never fire. The lock manifest discloses the mechanism (declaration-class), but the plan lines (gen_fcov_plan.md:
  2535-2536) carry no unreachable marker and the render log's reachability statement does not list them. The intent
  (a locked entry written under RLB = 1) IS covered by gen_pmp_cfg_write_cg.cr_lock_outcome.locked_rlb1_written, which
  the lock manifest declares. Retire or mark the two plan bins with this reason, or redefine cp_self_lock / cp_next_cfg on
  the raw lock bit if the addr_write crosses are meant to observe the bypass. Recorded disposition (Orchestrator,
  after tb-infra-2 traced the cause to the plan text: cp_self_lock and next_locked_tor are defined with RLB = 0 and
  then crossed with rlb1): both coverpoints move to the raw lock bit and the cross with cp_rlb expresses the effective
  lock, plan first, sampler after, the bins re-entering the lock manifest then; not yet landed, so the row stands.
- L-2 (Low, plan; routed to the DV Lead for form v3). The three PMP entries stay at seeds 3 at the range end while the round-2 form
  (463a026) asks twelve with its derivation; b74ca93 says nothing about seeds. State who applies the rise and when (form
  v3 at the round's commit, or runtime-2's dispatch touch), so the round-2 plan and the testlist agree before dispatch;
  the Orchestrator has routed the question to form v3.
- L-3 (Low, environment; adopted from rev49 and verified). The ignored_mml_exec predicate at :1867, a_b[7] && (a_b[2] ||
  (!a_b[0] && a_b[1])), includes RWX = 111; the RTL's is_mml_m_exec_cfg (rtl/ibex_cs_registers.sv:164-172) is true for
  lock with RWX in {001, 010, 011, 101} only, so a locked RWX = 111 row written under MML is booked ignored_mml_exec where
  the DUT writes it; the plan's cp_outcome prose carries the same mismatch. Encode the four rows; align the plan.
- L-4 (Low, environment; adopted and verified). CG-PMP-002 cp_outcome (:1900-1905) tests `pmp_addr_now[i] == pmp_wr_val`
  first, so a locked entry (RLB = 0) rewritten with its current value is booked written although the DUT ignored it.
  Decide ignored_self_lock / ignored_tor_lock from the pre-state rule and use the readback only to confirm.
- L-5 (Low, environment; adopted and verified). cp_trap.illegal (:1686) is any rvfi_trap on the record; the plan (:2578)
  says rvfi_trap with mcause 2. Check the cause or state the caveat beside the two the render log already states.
- L-6 (Low, plan; adopted). CG-PMP-014's Sample line (:2806) samples "at each regime phase start"; the sampler
  snapshots only after a PMP CSR write and never the reset-state table. Acceptable under LOG-096 while no regime exists;
  reconcile the line when the regime lands.
- O-1 (observation). The gate build identity moved from 596b04c95332e2aa (218e9f3, the measurement's build) to
  32f878987926e4e2 (5db73d4) through the irq landings' gen_agents_pkg.sv and gen_checkers_pkg.sv; the covergroup sources
  did not change; round 2's canary rebuilds at its own pin, as the render log anticipates.
- O-2 (observation). The measurement's 119 verdicts are FAIL by the "declares N bins but has no manifest" rule that fires
  after sampling; the block states this and its positive control; nothing of it entered a measured merge.
- Closed by this range: my regen-round1 M-1 condition (the verifier reads declarations only; on a fixture root from 5db73d4
  a referenced manifest declaring counts.cp_x.b fails DECL; 30 rendered equals my strict count of 30 declarations); my
  round-2 form L-1 (twelve CM223 rows landed in the response file at 27212cb).

CRITIC VERDICT: REQUEST-CHANGES, confined to the CG-PMP-001 cp_outcome and CG-PMP-004 cp_first_after_reset samplers
(M-1, M-2) and the render log's reachability statement. The render, the codegen fix (proved in both directions), the plan
overlay, the anchored verifier, the three every-seed manifests (every declared bin backed by a real hit at every seed,
every removed bin reasoned with a count the retained file confirms) and the testlist flip stand, so the measured flip may
proceed: no declared bin rests on a false hit. The two samplers book bins by a mechanism the plan excludes and report as
reachable four bins no run can hit; a covergroup family is validated by what it samples, and these two coverpoints sample
the wrong thing. Re-review on the sampler fix with a re-measured 40-seed block; L-1..L-6 are plan and environment rows.

## 6. Reconciliation with the cross-model range review
dv/auto_dv/reviews/2026-09-05-claude-diff-2d87642b-5db73d40.md at fd36d17 (e5840103bfeda23c, APPROVE-WITH-CHANGES), read at 2026-09-05T06:26:31Z
after Sections 1-5 were handed. Its two Majors are M-1 and M-2 here, each re-verified by me against gen_fcov_pkg.sv at 5db73d4,
the RTL and the retained measurement (adopted and verified). Its three Minors are L-3..L-5 and its Low is L-6 (adopted and
verified against the sampler lines, rtl/ibex_cs_registers.sv:164-172 and the plan lines :2508, :2578, :2806). Not in the
review: L-1 (the two addr_write cross bins dead by construction, unmarked in the plan) and L-2 (the seed rise). The verdict
words differ: the review's APPROVE-WITH-CHANGES and my REQUEST-CHANGES rest on the same facts; my standard treats a bin
booked by a mechanism the plan excludes as blocking for the covergroup that books it (the tb_l4 rule), while the manifests
and the flip, which no false hit touches, are not blocked.
