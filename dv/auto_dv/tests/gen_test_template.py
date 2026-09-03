"""gen_test_template: the test template of the generated TB, built from the TB as built (bridge fields
of gen_bridge_if, GenBridge/GenHandles/GenImage, the rendered gen_knobs.py, the step-2b command
dispatcher). A real test subclasses GenTest, fills the four hooks and wraps `run()` in one
@cocotb.test(); it never touches a DUT signal or a hierarchical path (gen_handles.py is the only one).

Run order (fixed; a test changes it only by overriding a hook):
  1. setup: bridge start (alive, listener, stim_active), image read-back through MEM_PEEK against
     Python's own parse of the .vmem (C3.3 backdoor rule), layer 2 (regime knobs the test lets vary
     are drawn from RANDOM_SEED and applied by REGIME_SET while the core is held; pinned knobs are
     left to their command-line value), layer 3 (the schedule derived from the seed or consumed
     from +gen_regime_sched), then FETCH_EN releases the core. Requires +gen_fetch_en_at_reset=0.
  2. stimulus(): the test's body (bridge commands, thresholds, waits); the schedule runner applies
     the remaining phases at their cycle or retirement triggers concurrently.
  3. wait for the program's end of test (tohost or the EOT register, the evt_eot_seen edge).
  4. fire_check(): per-seed asserted observables; every failure is collected and raised in one
     AssertionError (the fire-check is the test's own failure mechanism, DV_prompt Section 5).
  5. declare_bins() is logged (GEN_TEST_BINS) and must equal the fcov manifest when the test declares bins.
  6. finish: checks first, then the witness epilogue (COV_WITNESS for the passed fire_tp_* checks whose
     cycle-level clause was TRUE, ids from the entry's witness_ids), then the finish handshake
     (TB_CONTRACT Section 2), then PASS_MARKER.

Skeleton of a real test (copy into dv/auto_dv/tests/gen_test_<area>_<topic>.py):

    import cocotb
    from dv.auto_dv.tests.gen_test_template import GenTest

    class MyTest(GenTest):
        name = "gen_test_<area>_<topic>"
        schedulable = GenTest.schedulable        # or a subset such as gen_test_lib.TIMING_ONLY_KNOBS
        async def stimulus(self):
            pass                                  # bridge commands / thresholds for the scenario
        def fire_check(self):
            self.check("fire_tp_<area>_<nnn>", <observable>, "<what was expected>")
        def declare_bins(self):
            return []                             # gen_<feature>_cg.<cp>.<bin> tokens, same as the manifest

    @cocotb.test()
    async def gen_test_<area>_<topic>(dut):
        await MyTest(dut).run()

MODULE=dv.auto_dv.tests.gen_test_<area>_<topic>, TOPLEVEL=gen_tb_top, RANDOM_SEED=+ntb_random_seed.
"""
import os
from collections import namedtuple

import cocotb
from cocotb.triggers import Edge, Event, First, Lock, with_timeout

from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_image import GenImage
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS
from dv.auto_dv.tests import gen_test_lib as lib

CheckResult = namedtuple("CheckResult", "what ok detail cycle_clause_true")


class GenTest:
    name = "gen_test_template"
    # Regime knobs this test DECLARES layers 2 and 3 must vary (pinned ones are removed at run time).
    # A declared knob without a REGIME_SET consumer in the build fails setup unless layers_required is
    # False (bring-up tests only, with the reason in the docstring; never a measured test).
    schedulable = lib.REGIME_KNOBS
    layers_required = True
    # Layer-3 phase count range and duration-class weights (CG-REG-007 bins k1..k5_plus, short..long).
    k_range = (1, 5)
    duration_weights = None
    # Cycle budget for the program to reach its end-of-test store; the TB's own largest default
    # budget stands in until a test knows its program better.
    program_budget_cycles = CONSTANTS["GEN_ALIVE_TIMEOUT_CYCLES_DEFAULT"]
    finish_timeout_cycles = None   # None = the rendered default of GenBridge.finish
    # Expected-fail tests name their bug id so the failing line carries it (plan Section 4 item 5).
    xfail_bug = None
    # Program report channel: a directed program stores this many result words to the EOT MMIO
    # register (GEN_MM_EOT_ADDR) before its final tohost store; each store toggles evt_eot_seen and
    # leaves its value in evt_eot_code, so Python collects them edge by edge into self.reports and
    # treats store number expected_reports + 1 as the end of test. 0 = tohost only (riscv-dv programs).
    expected_reports = 0
    plan_group = None   # test-plan group whose bins declare_bins() defaults to (None: gen_<x> of gen_test_<x>)

    def __init__(self, dut):
        self.dut = dut
        self.log = dut._log
        self.h = GenHandles(dut)
        self.bridge = GenBridge(self.h, self.log)
        self.seed = int(os.environ.get("RANDOM_SEED", "0"))
        assert self.seed > 0, "GEN_TEST: RANDOM_SEED not set (the flow exports it from the run seed)"
        image_path = lib.plus("mem_image")
        assert image_path, "GEN_TEST: +gen_mem_image is required (program image)"
        self.image = GenImage(image_path)
        self.rng = lib.sub_rng(self.seed, "test")
        self.period_ns = CONSTANTS["GEN_CLK_PERIOD_NS"]
        self.pinned = [n for n in self.schedulable if lib.knob_is_pinned(n)]
        self.unconsumed = [n for n in self.schedulable if n not in self.pinned and n not in lib.CONSUMED_KNOBS]
        self.varied = [n for n in self.schedulable if n not in self.pinned and n in lib.CONSUMED_KNOBS]
        self._applying = False
        self._drained = Event()
        self.knobs = {}
        self.schedule = None
        self.applied = []          # Phase objects applied through REGIME_SET, in order
        self.reports = []          # program report words (EOT-register stores before the final code)
        self.eot_seen = False
        self.eot_cycle = None      # bridge counts at the end-of-test store (the schedule check's reference)
        self.eot_retired = None
        self.checks = 0            # check() calls; finish() refuses a run with none (silent-pass guard)
        self.failures = []
        self.results = []          # CheckResult per check(); the witness epilogue reads cycle_clause_true from them
        self.witness_ids = lib.witness_ids_of(self.name)
        self._cmd_lock = Lock()
        self.log.info("GEN_TEST_SEED test=%s seed=%d image=%s", self.name, self.seed, image_path)

    # ---- bridge helpers -------------------------------------------------------------------------
    async def cmd(self, kind, args=(0, 0, 0, 0), timeout_cycles=200):
        """Serialized bridge command (the stimulus hook and the schedule runner share the bridge)."""
        await self._cmd_lock.acquire()
        try:
            return await self.bridge.cmd(kind, args, timeout_cycles)
        finally:
            self._cmd_lock.release()

    def cycle(self):
        return int(self.h.b.cycle_count.value)

    def retired(self):
        return int(self.h.b.evt_retired_count.value)

    def eot_count(self):
        return int(self.h.b.evt_eot_count.value)

    async def _edge_or_eot(self, sig, cycles, what):
        """Await one edge on `sig`, abandoning it when the program ends first; returns True on the edge."""
        b = self.h.b
        if self.eot_count() > 0:
            self.eot_seen = True
            return False
        try:
            fired = await with_timeout(First(Edge(sig), Edge(b.evt_eot_seen)), cycles * self.period_ns, "ns")
        except Exception as exc:  # cocotb SimTimeoutError
            raise AssertionError(f"GEN_TEST: no edge on {what} within {cycles} cycles ({type(exc).__name__})") from None
        if getattr(fired, "signal", None) is b.evt_eot_seen:
            self.eot_seen = True
            return False
        return True

    async def wait_cycles(self, count, timeout_cycles=None):
        """Arm the bridge cycle threshold at the absolute cycle `count`; False if the program ended first."""
        b = self.h.b
        b.evt_cycle_target.value = count & 0xFFFFFFFF
        b.evt_cycle_arm.value = 0 if int(b.evt_cycle_arm.value) else 1
        budget = timeout_cycles if timeout_cycles is not None else max(count - self.cycle(), 0) + 100
        hit = await self._edge_or_eot(b.evt_cycle_hit, budget, f"evt_cycle_hit for cycle {count}")
        return hit or count <= self.cycle()   # the boundary passed in the end-of-test cycle itself

    async def wait_retired(self, count, timeout_cycles):
        """Arm the bridge retirement threshold at the absolute count; False if the program ended first."""
        b = self.h.b
        b.evt_retired_target.value = count & 0xFFFFFFFF
        b.evt_retired_arm.value = 0 if int(b.evt_retired_arm.value) else 1
        hit = await self._edge_or_eot(b.evt_retired_hit, timeout_cycles, f"evt_retired_hit for {count} retirements")
        return hit or count <= self.retired()

    async def wait_event(self, name, timeout_cycles):
        """Await one edge of a monitor event bit (evt_irq_taken, evt_dbg_entered); False if the program ended first."""
        return await self._edge_or_eot(getattr(self.h.b, name), timeout_cycles, name)

    # ---- fixed phases --------------------------------------------------------------------------
    async def setup(self):
        assert lib.plus_int("fetch_en_at_reset", lib.knob_default("fetch_en_at_reset")) == 0, \
            "GEN_TEST: +gen_fetch_en_at_reset=0 is required (read-back and layer 2 precede the first fetch)"
        await self.bridge.start()
        await self.readback()
        await self.apply_layers()
        await self.cmd("FETCH_EN", (1, 0, 0, 0))
        self.log.info("GEN_TEST_RELEASE cycle=%d", self.cycle())

    async def readback(self):
        n = lib.plus_int("mem_readback_words", CONSTANTS["GEN_MEM_READBACK_WORDS_DEFAULT"])
        bad = 0
        for idx, word in self.image.sample(n, self.seed):
            got = await self.cmd("MEM_PEEK", (idx * 4, 0, 0, 0))
            if got != word:
                bad += 1
                self.log.error("GEN_TEST read-back mismatch at 0x%08x: sv 0x%08x vmem 0x%08x", idx * 4, got, word)
        assert bad == 0, f"GEN_TEST: {bad} read-back mismatches of {n} words"
        self.log.info("GEN_TEST_READBACK ok words=%d", n)

    async def apply_layers(self):
        """Layer 2 then layer 3: phase 0 of the schedule carries the layer-2 draw; a supplied
        +gen_regime_sched replaces both (architecture C9, XM-L5)."""
        if self.unconsumed:
            names = ",".join(lib.short_knob(n) for n in self.unconsumed)
            if self.layers_required:
                raise AssertionError(f"GEN_TEST_FAIL {self.name}: declared regime knobs {names} have no REGIME_SET consumer in this build "
                                     "(layers_required); a test never runs with its layers silently off")
            self.log.info("GEN_TEST_LAYERS not_applied reason=no REGIME_SET consumer for declared knobs %s (layers_required=False, bring-up only)", names)
        supplied = lib.plus("regime_sched")
        if supplied:
            self.schedule = lib.Schedule.parse(supplied)
            dropped = [p for p in self.schedule.phases if p.knob in self.pinned]
            assert not dropped, f"GEN_TEST: +gen_regime_sched names pinned knob(s) {sorted({p.knob for p in dropped})}"
        else:
            self.knobs = lib.draw_knobs(self.seed, self.varied)
            self.schedule = lib.Schedule.derive(self.seed, self.varied, self.k_range, self.duration_weights, self.knobs)
        self.log.info("GEN_TEST_KNOBS pinned=%s drawn=%s", ",".join(sorted(self.pinned)) or "-",
                      " ".join(f"{lib.short_knob(k)}={v}" for k, v in sorted(self.knobs.items())) or "-")
        self.log.info("GEN_TEST_SCHED source=%s k=%d sched=%s", self.schedule.source, self.schedule.k,
                      self.schedule.text() or "-")
        for p in [p for p in self.schedule.phases if p.kind == "c" and p.count == 0]:
            await self.apply_phase(p)

    async def apply_phase(self, p):
        await self.cmd("REGIME_SET", self.schedule.regime_set_args(p))
        p.applied_cycle = self.cycle()
        self.applied.append(p)
        self.log.info("GEN_TEST_PHASE idx=%d trigger=%s%d knob=%s value=%s cycle=%d", p.idx, p.kind, p.count,
                      lib.short_knob(p.knob), p.value, p.applied_cycle)

    async def run_schedule(self):
        """Apply the phases after phase 0 at their triggers, in trigger order, until the program ends."""
        pending = [p for p in self.schedule.phases if not (p.kind == "c" and p.count == 0)]
        pending.sort(key=lambda p: (p.count, p.idx))   # one trigger kind per schedule (lib.Schedule), so count order is time order
        i = 0
        while i < len(pending) and not self.eot_seen:
            p = pending[i]
            if p.kind == "c":
                reached = await self.wait_cycles(p.count, timeout_cycles=self.program_budget_cycles)
            else:
                reached = await self.wait_retired(p.count, timeout_cycles=self.program_budget_cycles)
            if not reached:
                break
            self._applying = True
            self._drained.clear()
            while i < len(pending) and (pending[i].kind, pending[i].count) == (p.kind, p.count):
                await self.apply_phase(pending[i])
                i += 1
            self._applying = False
            self._drained.set()

    async def stimulus(self):
        """Hook: the scenario's stimulus (bridge commands, waits). Default: the program alone."""
        return None

    async def wait_eot(self):
        """Collect expected_reports report words (one EOT-register store each), then the end-of-test
        store; every store is one awaited edge, and the store counter proves none was missed."""
        b = self.h.b
        final = self.report_count() + 1
        while self.eot_count() < final:
            seen_before = self.eot_count()
            try:
                await with_timeout(Edge(b.evt_eot_seen), self.program_budget_cycles * self.period_ns, "ns")
            except Exception as exc:
                raise AssertionError(f"GEN_TEST: end-of-test store {seen_before + 1} of {final} not seen within "
                                     f"{self.program_budget_cycles} cycles ({type(exc).__name__})") from None
            now = self.eot_count()   # read once: the assert and its message describe the same observation
            assert now == seen_before + 1, \
                f"GEN_TEST: report channel skipped a store ({seen_before} -> {now}); the program stores faster than one edge per store"
            if now < final:
                self.reports.append(int(b.evt_eot_code.value))
                self.log.info("GEN_TEST_REPORT idx=%d value=0x%08x cycle=%d", len(self.reports) - 1, self.reports[-1], self.cycle())
        self.eot_seen = True
        self.eot_cycle = self.cycle()
        self.eot_retired = self.retired()
        self.log.info("GEN_TEST_EOT code=0x%08x stores=%d reports=%d retired=%d cycle=%d", int(b.evt_eot_code.value),
                      self.eot_count(), len(self.reports), self.eot_retired, self.eot_cycle)

    def check(self, what, ok, detail, cycle_clause_true=False):
        """Record one fire-check result (failures are raised together by finish()). A fire_tp_* method passes
        cycle_clause_true=True only on the TRUE branch of its cycle-level clause, checked against the export;
        the finish() epilogue witnesses exactly those that also passed."""
        r = CheckResult(what, bool(ok), detail, bool(cycle_clause_true))
        self.checks += 1
        self.results.append(r)
        self.log.info("GEN_TEST_FIRE %s ok=%s %s%s", what, r.ok, detail, " cycle_clause_true" if r.cycle_clause_true else "")
        if not r.ok:
            self.failures.append(f"{what}: {detail}")
        return r

    def info(self, ident, detail):
        """Record an observation that is reported, never gated: the RTL outcome of an _xfail item
        (GEN_TEST_RTL_OUTCOME <Bn>) or the observation of an _info item (GEN_TEST_INFO <id>)."""
        tag = "GEN_TEST_RTL_OUTCOME" if str(ident).startswith("B") else "GEN_TEST_INFO"
        self.log.info("%s %s %s", tag, ident, detail)

    def fire_check(self):
        """Hook: per-seed asserted observables through self.check(); every item of the group has one."""
        raise NotImplementedError("GEN_TEST: fire_check() is the test's own duty")

    def declare_bins(self):
        """Hook: the bins the test intends to hit. Default: the plan's bins for `plan_group` (gen_<x> for
        gen_test_<x>) through the manifest generator's derivation, so finish() proves the rendered manifest is
        current against the plan; a test hitting a subset declares that subset."""
        return lib.plan_bins(self.name, self.plan_group)

    def report_count(self):
        """Hook: number of report words the program stores before its end-of-test store; the default is the
        class attribute, a generated program returns its plan's count for this seed."""
        return self.expected_reports

    def phase_reached(self, p):
        """A phase's trigger passed when the bridge count it names reached the boundary by the end of test."""
        return (p.kind == "c" and p.count <= self.eot_cycle) or (p.kind == "r" and p.count <= self.eot_retired)

    def schedule_check(self):
        """Every phase whose trigger boundary passed by the end of test was applied, and no phase was
        applied before its trigger. `reached` comes from the bridge counts at EOT, never from the
        runner's own bookkeeping, so a runner that stalls or dies leaves a reached-but-unapplied
        phase and the check fails. With no schedulable knob the layers are recorded as not applied
        and the check is a logged no-op, never a silent pass."""
        if not self.schedule.phases:
            self.log.info("GEN_TEST_LAYERS not_applied reason=no consumable knob varied (declared=%s, consumed=%s)",
                          ",".join(lib.short_knob(n) for n in self.schedulable) or "-",
                          ",".join(lib.short_knob(n) for n in lib.CONSUMED_KNOBS) or "-")
            return
        reached = [p for p in self.schedule.phases if self.phase_reached(p)]
        applied = set(id(p) for p in self.applied)
        missed = [p.text() for p in reached if id(p) not in applied]
        early = [p.text() for p in self.applied if p.applied_cycle is not None and p.kind == "c" and p.applied_cycle < p.count]
        self.check("fire_schedule_applied", not missed and not early and len(self.applied) == len(reached),
                   f"reached {len(reached)} of {len(self.schedule.phases)} scheduled entries by EOT (cycle {self.eot_cycle}, "
                   f"retired {self.eot_retired}), applied {len(self.applied)}"
                   + (f", missed {missed}" if missed else "") + (f", early {early}" if early else "")
                   + f" (k={self.schedule.k}, source={self.schedule.source})")

    async def finish(self):
        bins = self.declare_bins()
        self.log.info("GEN_TEST_BINS n=%d %s", len(bins), " ".join(bins) if bins else "-")
        if self.checks == 0:
            raise AssertionError(f"GEN_TEST_FAIL {self.name}: fire_check() recorded no check (a test must assert that its scenario fired)")
        if bins or lib.load_manifest_bins(self.name) is not None:
            lib.check_manifest_matches(self.name, bins)
        if self.failures:
            tag = f"GEN_TEST_XFAIL {self.xfail_bug} " if self.xfail_bug else "GEN_TEST_FAIL "
            raise AssertionError(tag + f"{self.name}: {len(self.failures)} fire-check failure(s): " + " | ".join(self.failures))
        await self.witness_epilogue()
        await self.bridge.finish(timeout_cycles=self.finish_timeout_cycles)
        self.log.info("%s %s", self.name, lib.PASS_MARKER)

    async def witness_epilogue(self):
        """COV_WITNESS <id> for exactly the passed fire_tp_* checks whose cycle-level clause was TRUE (plan v2f
        witness protocol, Critic C-1): ids must be in the entry's witness_ids, codes come from the rendered
        WITNESS_IDS table; a foreign id, a missing table or a missing command fails loud. Tests never issue it."""
        due = [r for r in self.results if r.ok and r.cycle_clause_true]
        if not due:
            return
        ids = [lib.tp_id_of(r.what) for r in due]
        foreign = [i for i in ids if i not in self.witness_ids]
        assert not foreign, f"GEN_TEST_FAIL {self.name}: witness for {foreign} outside the entry's witness_ids {list(self.witness_ids)}"
        assert "COV_WITNESS" in lib.CMD and lib.WITNESS_IDS, \
            f"GEN_TEST_FAIL {self.name}: witness protocol not rendered (CMD COV_WITNESS / WITNESS_IDS) while {ids} are due"
        for tp in ids:
            await self.cmd("COV_WITNESS", (lib.WITNESS_IDS[tp], 0, 0, 0))
            self.log.info("GEN_TEST_WITNESS id=%s code=%d", tp, lib.WITNESS_IDS[tp])

    async def run(self):
        await self.setup()
        sched_task = cocotb.start_soon(self.run_schedule())
        stim_task = cocotb.start_soon(self.stimulus())
        await self.wait_eot()
        try:
            await with_timeout(stim_task.join(), self.program_budget_cycles * self.period_ns, "ns")
        except Exception as exc:
            raise AssertionError(f"GEN_TEST: stimulus() did not finish after the end of test ({type(exc).__name__})") from None
        if self._applying:   # a boundary reached in the end-of-test cycle is still being applied
            t0 = self.cycle()
            try:
                await with_timeout(self._drained.wait(), self.program_budget_cycles * self.period_ns, "ns")
            except Exception as exc:
                raise AssertionError(f"GEN_TEST: the schedule runner did not finish its last boundary ({type(exc).__name__})") from None
            self.log.info("GEN_TEST_DRAIN waited cycles=%d for the runner's last boundary", self.cycle() - t0)
        sched_task.kill()
        self.schedule_check()
        self.fire_check()
        await self.finish()
