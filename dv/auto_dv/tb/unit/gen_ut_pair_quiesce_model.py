#!/usr/bin/env python3
"""Model of the end-of-run pair-quiesce loop used by gen_ut_intg_store, gen_ut_lockstep and gen_ut_intg_span.

The three tests wait for the bridge's retired counter and the comparator's consumed counter to agree before
asserting equality. This file models the loop with the signal reads replaced by a scripted sample stream, so the
predicate can be judged without a simulator, and keeps the discriminating case that the earlier shape passed.

  gen_ut_pair_quiesce_model.py              print the table
  gen_ut_pair_quiesce_model.py --self-test  assert the discrimination and that the model still matches the test

Exit: 0 the model holds; 1 it does not.
"""
import pathlib, sys

BOUND = 20   # the tests' QUIESCE_CYCLES


def stream():
    """Equal at even indices, unequal at odd: no two ADJACENT equals inside the bound, and the sample just past
    the bound is equal. That is an in-flight stream, not a settled one."""
    return [(31, 31) if i % 2 == 0 else (31, 30) for i in range(BOUND + 1)]


def sampled_after_loop(samples):
    """The shape before this model existed: the loop counted equal samples, and the assertion then read a FRESH
    sample, so an exhausted loop could still be handed one equal instant."""
    settled = 0
    for i in range(BOUND):
        retired, consumed = samples[i]
        if retired == consumed:
            settled += 1
            if settled == 2:
                break
        else:
            settled = 0
    retired, consumed = samples[BOUND]
    return ("PASS" if consumed == retired else "FAIL"), retired, consumed, settled


def sampled_in_loop(samples):
    """The shape in the tests: the loop samples into the variables the assertion uses, and the gate is that the
    pair held equal across a whole cycle. Nothing is read after the loop, so the bound only decides how long to
    wait."""
    settled = 0
    retired = consumed = None
    for i in range(BOUND):
        retired, consumed = samples[i]
        if retired == consumed:
            settled += 1
            if settled == 2:
                break
        else:
            settled = 0
    return ("PASS" if settled == 2 else "FAIL"), retired, consumed, settled


def settles_when_quiet():
    """A stream that really is settled: unequal once, then equal for the rest."""
    return [(31, 30)] + [(31, 31)] * BOUND


def report():
    s = stream()
    adjacent = sum(1 for i in range(BOUND - 1) if s[i] == s[i + 1] and s[i][0] == s[i][1])
    print(f"in-flight stream: {BOUND + 1} samples, equal at even indices including the one past the bound; "
          f"adjacent equal pairs inside the bound: {adjacent}")
    out = {}
    for name, fn in (("sampled after the loop", sampled_after_loop), ("sampled in the loop", sampled_in_loop)):
        v, r, c, st = fn(s)
        out[name] = v
        print(f"  {name:24s} verdict={v}  retired={r} consumed={c} settled={st}")
    q = settles_when_quiet()
    v, r, c, st = sampled_in_loop(q)
    print(f"settled stream: unequal once then equal; sampled in the loop verdict={v} retired={r} consumed={c} "
          f"settled={st}")
    out["settled stream"] = v
    return out


def self_test():
    out = report()
    fails = []
    if (out["sampled after the loop"], out["sampled in the loop"]) != ("PASS", "FAIL"):
        fails.append("the in-flight stream no longer discriminates the two shapes")
    if out["settled stream"] != "PASS":
        fails.append("a genuinely settled stream must pass")
    src = (pathlib.Path(__file__).resolve().parents[2] / "gen_tb/gen_tests/gen_ut_intg_store.py").read_text()
    for needle in ("QUIESCE_CYCLES = 20", "settled = 0", "if settled == 2:", "assert settled == 2"):
        if needle not in src:
            fails.append(f"gen_ut_intg_store.py no longer contains {needle!r}: this model may be stale")
    for f in fails:
        print(f"SELF-TEST FAIL: {f}")
    print("SELF-TEST PASS" if not fails else "SELF-TEST FAILED")
    return 1 if fails else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        sys.exit(self_test())
    report()
