# Critic verdict: pass-14-rows (the CM220 rows on the exclusion README, the select report path and the selector's print)

Artifacts at 26a517a (feature group pass-14-rows, GROUP COMPLETE; range 7062428..26a517a, the parent 7062428 being
runtime-2's retained copy of the rtl-arch-009 record):
- dv/auto_dv/excl/gen_exclusions_README.md  sha256 11399c260f0d015d  338 lines (40 changed lines)
- dv/auto_dv/excl/gen_exclusions_select_report.md  364dbd9a8291a3b6  145 (line 141: the emitted path, now repo-relative)
- dv/auto_dv/excl/gen_excl_select.py  4e7ed5936d268e19  1124 (3 lines and one intent comment at the report's emitted-path line)
- unchanged and re-checked: dv/auto_dv/excl/gen_exclusions.el 91dbc8c7ff9ce60b (identical 98b643e through HEAD);
  dv/auto_dv/evidence/gen_round_0/gen_elcheck_rtl_arch_009.yaml c3f1537cf906ced4, 62 lines (7062428), byte-identical to
  dv/auto_dv/work/runtime/done/rtl-arch-009.yaml.
Judged against: my exclusion final-file verdict gen_critic_excl_final.md (9c1de66) and its rows; the CM220 rows of the
range review 3cc3c72 as they read at the range end 255dca3 (verified there in that verdict's Section 6); the commit
message of 26a517a; docs/dv/dv_principles.md d9c27db18f511411.
Date: 2026-09-05T03:01:38Z   Role: Critic
Method: detached worktree of 26a517a (removed after the logs were retained under dv/auto_dv/work/critic/pass14rows/); the
generator re-run there with the pass-14 arguments; every changed README line read against the sources it cites and
against my own urg dashboards from the exclusion verdict. Exposure, stated: the range review 156dac5 was read in full for
the regen-round1 verdict before this file was written; its pass-14-rows paragraph reports verifications and no finding.
This verdict changes no entry of the exclusion file and does not reopen the final-file verdict, which stands as ruled.

## 1. The selector change and the reproduction
gen_excl_select.py prints the emitted path repo-relative (the REPO_ROOT prefix stripped when the --out path lies under
the clone; an out-of-tree path stays absolute). The comment states intent only. Re-run on the worktree of 26a517a with
the pass-14 arguments (dump, the three pass2-4 attempts logs, --ec3-asserts gen_round_0/gen_asserts.txt --ec3-round
round_0; the selector's self-test runs on invocation): rc 0, the .el byte-identical (91dbc8c7ff9ce60b), the report
identical except line 141, which carries my scratch --out path because it lies outside the clone; with the committed
--out the same line reads "to dv/auto_dv/excl/gen_exclusions.el", the committed text. CM220 low 1 closed.

## 2. The README rows, each read at 26a517a
- :95-98 (CM220 medium 2): "Reference dump used today: the measured round_0 dump ... which pass 14 generated from"; the
  re-baseline named as the reference through pass 13 and as history. :128-130 the author pre-checks provenance split the
  same way. Closed.
- :112 (CM220 medium 1): "Class D spare-encoding arms (rows 1, 23, 33) | 3 (included since pass 14) | EC-3 fields
  filled from the round_0 assertion report"; :245 "All three are in since pass 14"; :294 F-3 "CLOSED at pass 14".
  Consistent with the file (three class-D(2b) Blocks with attempts 5408327, failures 0) and its header line 5. Closed.
- :176 (CM220 medium 3): the ASSERT row now says the report-wide summary row "DOES move for this round, 229/257 without
  the file to 229/254 with it, the same 3 objects". My plain and strict dashboards read 229/257 and 229/254. Closed.
- :208 (CM220 medium 4): the elcheck bullet cites "its record retained in this repository at
  dv/auto_dv/evidence/gen_round_0/gen_elcheck_rtl_arch_009.yaml (received 2026-09-05T01:53:02Z, finished 01:57:16Z),
  verdict PASS, urg rc 0 ... no entry rejected"; the file exists at 7062428 and equals runtime-2's served record; its
  gated rows equal mine. Closed (my excl L-3 was closed on the same fact).
- :147-160 (CM220 low 2, my excl L-2 in part): the five-class no-op join table (NO-OP 105, EFFECTIVE 84, UNRESOLVED 0 / 0,
  ANOMALY 0; 105 + 84 = 189 = the Block count). The per-entry join stays a work artefact by the README's own sentence:
  my excl L-2 (retain it or its sha256 with the regenerating command) is carried, not new.
- Not touched, still stale at 26a517a: the F-1 row (:292, "draft form: generated from the round-0 re-baseline dump") and
  the F-6 row (:297, "381 annotation groups" for a file with 495): my excl L-1, routed to rtl-arch, carried.

## 3. dv_principles.md conformance
PASS. Section 4: the touch replaces stale statements with measured ones and names the history as history; Section 5:
the one new comment states intent; Sections 1, 2 and 6 do not apply to a records touch and a print change (the selector's
self-test ran and the file reproduced).

## 4. Reconciliation with the cross-model range review
156dac5 (a341fd9bcd473ef5, APPROVE-WITH-CHANGES over three groups): its pass-14-rows paragraph verifies the .el hashes
against the README, the select report and the retained rtl-arch-009 record, the three class-D arms with EC-3 filled and
the 229/254 dashboard, and raises no pass-14-rows finding; the refusal probes it lists belong to regen-round1. Agreement.

CRITIC VERDICT: APPROVE. The pass-14-rows touch closes CM220 medium 1-4 and low 1 with statements that match the file, my
dashboards and the retained record, changes no exclusion entry, and leaves the generator reproducing the file byte for
byte. No new rows; the carried rows are my exclusion verdict's L-1 (F-1 and F-6 README rows) and L-2 (the per-entry join).
