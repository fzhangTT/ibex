# Cross-model review - committed diff 29d01e76..3a9ccaaf

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session e78ebd59-b9c6-4376-a76e-7813c769032d; sandbox: bubblewrap, working directory = detached read-only checkout of commit 3a9ccaaf8223e9b3f88a3f7b3d41223855b1b843 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit 3a9ccaaf8223e9b3f88a3f7b3d41223855b1b843
**Date:** 2026-09-03
**Target:** committed diff 29d01e76..3a9ccaaf (echo at raw line 1)

---

TARGET: 29d01e76e2f7fb8b20c909c6aa5235b580e62574..3a9ccaaf8223e9b3f88a3f7b3d41223855b1b843

Reviewer identity: Claude Fable 5.1 (claude-fable-5-1), Claude Code CLI, fresh session, read-only detached checkout of 3a9ccaa. Scope: the one commit 3a9ccaa (21 files: 8 modified, 13 added). Every claim below was checked by running the library at this commit, diffing the retained artifacts, or reading git history in this worktree.

## What I verified

**(1) Lint widenings, probed myself against `check_test_source` at 3a9ccaa**

- `self.cmd = f`, `self.finish = f`, `self.cmd: T = f`, `self.cmd += 1` in a method: all REFUSED with the new "rebinds the template method ... on the instance" message. `t.cmd = f` in an undecorated helper given self: REFUSED. Matches gen_t226close_lint_probe.log.
- Decorated module-level helper given self (positional and keyword), and a decorated helper reached through an undecorated helper: REFUSED as a bare-name escape. Undecorated helper control: ACCEPTED. Matches gen_t2cm88_cm89_lint_probe.log.
- Every shape the rewritten residual paragraph names as passing does pass at this commit: `b = self.bridge; b.cov_witness = None`; `_h(self.bridge)` with `def _h(b): b.cov_witness = f`; `b = t.bridge` in a helper; `setattr(t.bridge, ...)` in a helper; `self.__setattr__(...)`; `self.bridge.__setattr__(...)`; `self.bridge.cmds[0].x = 1` in a method and a helper; imported `forge(self.bridge)`; import-alias and full-dotted-path template patching at module level and inside a method; the three `self.failures` target forms. Imported `forge(self)` is refused as the paragraph says. The paragraph is true for everything it names.
- The self-test at this commit: PASS (ran it, rc=0). The API doc bullet and F_OVERRIDE agree (the self-test checks that).

**(2) Regime-check additions, probed against `check_regime_handlers_source`**

- `schedulable +=`, `program_handlers +=`, `mie_stays_zero |=`: all REFUSED. `metaclass=ABCMeta` and an arbitrary `foo=1` class keyword on the test class: REFUSED. Green control accepted. The structural red list now has fifteen entries (counted); "fifteen" in the API doc is correct.
- RAW_FAULT_PLUSARGS: the four keys exist in PLUSARGS, each mapping to a KNOB_HANDLER knob. `regime_handler_violations` with value `raw` on knob_imem_err_rate: violation without `exc`, none with it. The converse assert holds (the four bus err_rate knobs and the irq/dbg consumers are all mapped). `plus_int(raw, 0)` resolves the rendered `+gen_<name>` through PLUSARGS, so the setup() wiring is correct. The three csr_reset excerpts carry the expected plusargs in their headers, the `=50` run fails before the first fetch with the exact message, `=0` passes, and the pinned run's banner shows `pinned=knob_irq_regime`. The banner change to `pinned_all` is a superset of the old `self.pinned` (REGIME_KNOBS is all twenty knobs), so no pin is dropped.

**(3) Intermediate generators**

- Both sha256 values reproduce from the retained .py.txt files (`429fa9897e7236fa...`, `7fead94e4693c62a...`). The diffs to the committed generator are small and coherent (22 and 11 changed lines: the TOR-role candidate bound and the csr_op docstring). `7fead94e` is named independently by the retained before-fix sweep header. The reproduction log shows `7fead94e` asserting the vacuous 021 red at `--seed 35 --red` and `429fa989` aborting plan() at seed 17; seed 7 builds on both. So the reproduction log does not show the seed-7 failure, and Section 7 does not claim it does: the seed-7 failure is a sim-level `fire_tp_pmp_015 ok=False` retained in the s7 excerpt. See findings on the linkage.

**(4) Records against the diff and the Critic verdicts.** Shim history: `git log` on gen_isa_shim.cc gives 9e912bb as its last change, 9e912bb is an ancestor of 2ea81ac, and the minstret-delta retirement derivation enters at 3be5a34. Section 6 and the manifest row are correct; the classification log is unedited (md5 unchanged). All 13 new files have matching md5 manifest rows. CR-T226-M-1: the Critic's three injected forms are all refused now; the attribute-chain forms were closed in 5bb10e7/ac5853e and the `self.cmd = f` instance form is closed here. What remains open, and is now stated as passing in the residual paragraph: the alias shape, the three one-transformation helper shapes, the dunder calls, subscript-in-chain. See finding 3 for one method-body shape the paragraph does not name.

**(5)** No non-ASCII in added lines; every touched file carries the `gen_` prefix; new code comments are intent-only. Rubrics: ai-slop-comments PASS, rtl-purity PASS (no rtl/ files), magic-numbers PASS, forces-and-hier-access PASS, assertion-integrity PASS (only additions; the banner and F_OVERRIDE string changes weaken nothing).

## Findings

[medium][dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_b3_pmp_lock_sweep800_seeds.txt:3] The "200 random 31-bit seeds" are one seed repeated 200 times: every value on the `random_31bit` line is 255808012, which is exactly `random.Random(2026).getrandbits(31)` re-seeded per iteration. The sequential and flow-derived lists are correct (I reproduced the 200 flow-derived seeds from `derive_seeds`). So the "800-seed" sweeps (gen_b3_pmp_lock_sweep800.log and the before-fix sweep, both headed "200 random 31-bit seeds") covered 601 distinct seeds, and gen_tdd_batch3.md:190 and :282-283, plus the CR-B3v2f-L-3 row (gen_critic_response_batch3.md:89, "the 200 random.Random(2026) 31-bit ... seeds"), describe them as 800. The retention did its job by exposing this; the record must now say it. - Recommendation: state in Section 7 and the L-3 row that the random block collapsed to one seed (601 distinct seeds swept, 0 failures on the final generator still holds), and either re-run 200 genuinely distinct random seeds on the final generator or explicitly accept the reduced sweep.

[low][dv/auto_dv/tests/gen_test_lib.py:818] The class-keyword refusal runs after `if "name" not in attrs: continue`, so a metaclass on a nameless module-local base bypasses it: `class B(GenTest, metaclass=M): pass` then `class T(B): name = ...` is ACCEPTED (probed), and `check_test_source` has no keyword check either. A metaclass is inherited, so it can rewrite the rule attributes of T exactly as the message warns. The AugAssign check at :813 already runs on every class in the hierarchy. - Recommendation: apply the keyword check to every GenTest-derived class (move it above the `name` continue), and add the base-class red source.

[low][dv/auto_dv/docs/gen_test_template_api.md:249] F_OVERRIDE now says "an instance rebinding from a method or helper, e.g. self.cmd = f", but only a bare Attribute target is caught: `self.cmd, x = _f, 1`, `for self.cmd in (_f,):` and `with open(p) as self.cmd:` are all ACCEPTED (probed). The residual paragraph at :273 lists the same three target forms for `self.failures` but not for a template method, so a reader of the bullet expects them refused. - Recommendation: either unpack Tuple/Starred targets and for/with targets in the two new checks at gen_test_lib.py:559 and :598 (cheap; the shapes are enumerable) or name the template-method variants in the residual paragraph.

[low][dv/auto_dv/evidence/gen_tdd_batch3.md:277] "429fa9897e7236fa (the h13 second-pass build header)": no retained artifact names that prefix independently of this touch (grep over dv/auto_dv/evidence finds only the reproduction log, the two records and the manifest; the h13 run summary and g* excerpt headers carry sources_sha/test_sha, not the generator sha). Likewise :281 attributes the s7/s29/s35 prefix greens to "the 7fead94e generator" from run timing, while their headers name only out_head13 and a prog.vmem path. - Recommendation: retain the h13 build header line that names 429fa989 (or say it lives under the work directory and is not retained), and say the s7/s29/s35 generator attribution is by timing and build directory, not by a hash in the excerpt.

[info][dv/auto_dv/evidence/gen_critic_response_test_template.md:162] The CM88-L-2 row says the check refuses "a class keyword on a test class", which is exactly true and is the bound of the fix; the base-class gap above is not claimed closed, so this is a scope note, not a misstatement.

Final verdict: APPROVE-WITH-CHANGES
