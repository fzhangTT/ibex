# Cross-model review - committed diff 99cba0e3..ac5853eb

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session c8e73784-031c-42b1-9305-0476aee3f02d; sandbox: bubblewrap, working directory = detached read-only checkout of commit ac5853eb0fe34eccbc48757dd8299ba7a143bd4e (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit ac5853eb0fe34eccbc48757dd8299ba7a143bd4e
**Date:** 2026-09-03
**Target:** committed diff 99cba0e3..ac5853eb (echo at raw line 1)

---

TARGET: 99cba0e3650997813671f1d3f6b3fcbe5c6d4aca..ac5853eb0fe34eccbc48757dd8299ba7a143bd4e

Reviewer: Claude Fable 5.1 (claude-fable-5-1), fresh session, detached read-only checkout of ac5853e. Scope: the six-file diff of the range; the lint probed by executing `check_test_source` at ac5853e and, for the red-before reproduction, the 99cba0e library loaded from `git show` (sha256 925c8f43af2d21c4... matches the log header).

**Verified (no finding)**

- Red-before log: the 99cba0e library accepts `def _h(t): t.bridge.cov_witness = _f` called with self and refuses `t.bridge = None` in the same helper with the exact message the log records. Manifest row bytes (393) and md5 (e46b65c2...) match the committed file.
- At ac5853e the helper branch refuses the chain shape, deeper chains (`t.bridge.h.b`), AugAssign and AnnAssign targets, the helper-to-helper fixpoint (`_h(t)` into `_g(u)`), keyword binding (`_h(t=self)`), and parameters named `self` or read through a template-owned attribute. Both refusal messages carry the new "an attribute reached through a template-owned name is read-only for a test" sentence.
- Parameter aliased to a local (`b = t`), a nested def called with `t`, a walrus, a module-level lambda called with self, and a lambda inside a helper are all refused by the escape rule.
- The four chain writes the old residual paragraph listed (`self.schedule.phases`, `self.h.b.evt_eot_seen.value`, `self.bridge.cmd`, `self.log.info`) are refused at this commit; `for/with/*self.failures`, import-alias and dotted-path patching, exec and importlib, `b = [self.bridge][0]` and a helper returning `self.bridge` pass as listed.
- `gen_test_lib.py --self-test` PASS at ac5853e with the repo root on PYTHONPATH (the API doc bullet list equals `REFUSED_FORMS` verbatim by the self-test's assert). The five fixtures gen_ut_witness_ok/_foreign/_notable/_noid/_othergroup exist under gen_fixtures; the base fixture replaces `bridge.cov_witness` with a recorder, as the doc now says.
- CM85 rows match the diff. Files are ASCII and gen_-prefixed; the one added code comment is intent-only with no log or review id. Rubrics: rtl-purity, forces, magic-numbers, assertion-integrity, ai-slop all PASS (no rtl, no pokes, no constants, no assertion removed or weakened).

**Findings**

- [medium][dv/auto_dv/docs/gen_test_template_api.md:270] The new parenthetical says "`b = self.bridge` is refused as an escape". It is not: `b = self.bridge` followed by `b.cov_witness = None` is ACCEPTED at ac5853e (the escape rule covers the bare test object and the verdict-record attributes, not `bridge`). The paragraph rewritten to remove false refusal claims (CM85-M-1) now carries a new one - state that an alias of a template-owned attribute passes (or drop the parenthetical), and add a red/green pair to the self-test for whatever the sentence ends up claiming.
- [medium][dv/auto_dv/tests/gen_test_lib.py:531] A decorated module-level helper evades every helper check: `helpers` (line 465) includes decorated functions, so `_h(self)` is not an escape, while `helper_defs` (line 531) excludes them, so the body is never walked. `@deco def _h(t): t.bridge = None`, `t._results.append(1)` and `t.bridge.cov_witness = 1` are all ACCEPTED when called with self (also at 99cba0e, so pre-existing, but it makes F_HELPER's sentence and "refuses exactly these" false) - make the escape rule's helper set equal to `helper_defs` so self passed to a decorated function is an escape (the cocotb entry is never called with self), with a red source.
- [low][dv/auto_dv/tests/gen_test_lib.py:563] The rebinding of CM85-M-2 survives one transformation away: `def _h(b): b.cov_witness = _f` called as `_h(self.bridge)`, `b = t.bridge; b.cov_witness = 1` inside a helper, and `setattr(t.bridge, 'cov_witness', 1)` inside a helper are ACCEPTED, while the class-side `setattr(self.bridge, ...)` is refused at line 618. None of these shapes is named in the residual paragraph - either list them there as passing (minimal, frozen-list compatible) or bind a parameter passed `self.<template_attr>` as template-owned-rooted and refuse `setattr` in helpers as methods do.
- [low][dv/auto_dv/docs/gen_test_template_api.md:271] "helpers in other modules" is listed as a passing shape, but `forge(self)` with an imported `forge` is REFUSED as an escape; only `forge(self.bridge)` passes. Pre-existing wording kept in a paragraph now claiming to list only shapes that pass - qualify it ("given an attribute rather than the test object").
- [info][dv/auto_dv/docs/gen_test_template_api.md:270] "string-built names" is vague: `setattr(self, 'bri' + 'dge', ...)` and non-literal `getattr` are refused; what passes is the dunder call (`self.__setattr__('bridge', None)`, `self.bridge.__setattr__(...)`) and the subscript-in-chain write (`self.bridge.cmds[0].x = 1`, also in helpers). Naming the shapes that actually pass would make the paragraph checkable.

Final verdict: APPROVE-WITH-CHANGES
