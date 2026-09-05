# gen_fu_cycle_slot_service: the script behind COMMAND 1 of the retained log

COMPANION to gen_fu_cycle_slot_service.log, which is retained and not reopened. That log's
COMMAND 1 line names a script that was NOT kept when the run was made. This file carries the
script text so the log names its own instrument.

PROVENANCE, stated plainly rather than implied: the text below is a RECONSTRUCTION written
after the fact. Its output was diffed against the five result lines the log retains and is
identical to them, and it exits 0. That is why those lines are unchanged and why this file
sits beside the log instead of inside it.

THE FIVE LINES IT REPRODUCES, quoted from the log:

    RED (the shared slot as it behaves today) then GREEN (CycleWaiters):
      shared slot (today)    armed=85     far_asleep_at_near_hit=False near_woke=True  far_woke_at_own=False
      CycleWaiters           armed=85     far_asleep_at_near_hit=True  near_woke=True  far_woke_at_own=True
      naive passes all three: False   <- must be False, this is the red
      CycleWaiters passes all three: True   <- must be True

HOW TO RUN IT: from the clone root with PYTHONPATH unset,

    python3 gen_fu_cycle_slot_service_script.py     # the text below, saved under that name

THE SCRIPT, verbatim:

```python
"""Red/green for the bridge cycle-slot policy: one shared slot against lib.CycleWaiters.

Two waiters, a near target and a far one, registered far first. The bridge has ONE cycle-threshold
slot, so the question is what each policy arms and which waiter a hit wakes:

  armed                   the target the slot carries after both waiters registered
  far_asleep_at_near_hit  the far waiter is NOT woken by the near waiter's hit
  near_woke               the near waiter is woken by its own hit
  far_woke_at_own         the far waiter is woken when its own target is reached

The naive policy is the code as it behaved before the service: a caller writes the slot itself, so
the last writer owns it and every waiter treats any hit as its own. It must fail at least one of
the three; that failure is the red.

Run from the clone root with PYTHONPATH unset.
"""
import sys

NEAR, FAR = 85, 11664


class NaiveSlot:
    """One target register plus a wake-everyone hit, which is the pre-service behaviour."""

    def __init__(self):
        self.target = None
        self.waiters = []

    def add(self, target, key):
        self.waiters.append((target, key))
        self.target = target        # the caller writes the slot: the last writer owns it

    def hit(self, cycle):
        if self.target != cycle:
            return []
        woken = [k for _, k in self.waiters]   # every waiter reads the one hit as its own
        self.waiters = []
        self.target = None
        return woken


def probe(slot, add, armed, hit):
    far, near = "far", "near"
    add(slot, FAR, far)
    add(slot, NEAR, near)
    a = armed(slot)
    woken_near = hit(slot, NEAR)
    woken_far = hit(slot, FAR)
    return {"armed": a,
            "far_asleep_at_near_hit": far not in woken_near,
            "near_woke": near in woken_near,
            "far_woke_at_own": far in woken_far}


def main():
    sys.path.insert(0, ".")
    from dv.auto_dv.tests import gen_test_lib as lib

    naive = probe(NaiveSlot(), lambda s, t, k: s.add(t, k), lambda s: s.target,
                  lambda s, c: s.hit(c))
    served = probe(lib.CycleWaiters(), lambda s, t, k: s.add(t, k), lambda s: s.armed_target(),
                   lambda s, c: s.on_hit(c))

    print("RED (the shared slot as it behaves today) then GREEN (CycleWaiters):")
    for label, r in (("shared slot (today)", naive), ("CycleWaiters       ", served)):
        print("  %s    armed=%-6d far_asleep_at_near_hit=%-5s near_woke=%-5s far_woke_at_own=%s"
              % (label, r["armed"], r["far_asleep_at_near_hit"], r["near_woke"], r["far_woke_at_own"]))
    ok_naive = all(naive[k] for k in ("far_asleep_at_near_hit", "near_woke", "far_woke_at_own"))
    ok_served = all(served[k] for k in ("far_asleep_at_near_hit", "near_woke", "far_woke_at_own"))
    print("  naive passes all three: %s   <- must be False, this is the red" % ok_naive)
    print("  CycleWaiters passes all three: %s   <- must be True" % ok_served)
    return 0 if (not ok_naive and ok_served) else 1


if __name__ == "__main__":
    sys.exit(main())
```
