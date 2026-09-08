# TDD transcript: the gen_ut_intg_span arming-count knob (bug candidate B16)

Component: `dv/auto_dv/gen_tb/gen_tests/gen_ut_intg_span.py` and the knob's source of record
`dv/auto_dv/tb/gen_tb_knobs.yaml` with the three files `dv/auto_dv/tb/gen_knobs_codegen.py` renders from it
(`dv/auto_dv/tb/gen_tb_pkg.sv`, `dv/auto_dv/tb/gen_env_cfg_knobs.svh`, `dv/auto_dv/gen_tb/gen_knobs.py`).
Purpose: the bug log's B16 entry asks for "a count knob for the arming in the cocotb module ... count 1 arms the
first access only" so the directed variant of `gen_intg_span_directed.S` can corrupt the FIRST bus word of the
misaligned load and nothing else. Owner: tb-infra. Written 2026-09-08T02:13:21Z.

Build: local `gen_tb_local.sh compile`, sources sha256 first-16 `047718cec02eec6a`, vcs exit 0, out tree
`dv/auto_dv/out_b16knob2` (a fresh directory, the knob set having changed). Program: `gen_program.py --seed 1
--directed dv/auto_dv/stim/gen_directed/gen_intg_span_directed.S --gcc-opts=-Idv/auto_dv/tests/gen_programs`,
entry 0x80000080, 160 words, crc32 0xb01e45ca. Runs through `gen_run_fixture.sh`; every verdict below is
`dv/auto_dv/flow/gen_verdict.py`'s own `decide`, never a grep of this record's.

## 1. What the knob is, and what it is not

One plusarg, `+gen_ut_intg_span_arm_count` (int, default 2). The module sent one bridge command whose single
constant `SPAN_WORDS = 2` set BOTH the armed address range and the arming count in `arg3[31:8]`. The bridge
command already carried a count field (`dv/auto_dv/env/gen_env_pkg.sv:131`, the driver's
`gen_agents_pkg.sv:209-222`), so no SV rule changes: the knob separates the count from the range. The range
still spans both of the load's words at every count, so the count alone decides how many of the load's accesses
are corrupted.

The module's own expectations are NOT changed and do not accommodate count 1. At count 1 the DUT still writes
the destination register, which IS B16, so the module's `assert sup` fails on purpose; the carrying testlist
entry is test-writer's `expected_fail: true` one. The committed `gen_ut_intg_span` entry passes no plusarg
and is unaffected.

## 2. The census that proves the knob reached the driver

The data-bus driver echoes the count it received (`gen_agents_pkg.sv:214`, `[GEN_BUS_ARM] dbus: armed kind 2
for N accesses in [lo, hi]`). That line, not the module's own log line, is the census: it is written on the SV
side after the value crossed the bridge. At count 1 it reads 1 in all eight seeds and at the default it reads 2
in all eight. The driver's end-of-run `injected_intg` total is present only in the passing runs: the cocotb
assertion ends a count-1 test before the UVM report phase, so that total is absent there and the
`[GEN_BUS_ARM]` echo is the count-1 census.

## 3. Red and green at seed 1, with the flow's verdicts

| run | plusargs beyond the fixture's | driver armed | suppressed records | uvm errors | cocotb | verdict |
|---|---|---|---|---|---|---|
| c2_seed1 (the default) | none | 2 | 1 | 0 | PASS 1 FAIL 0 | PASS, no collected failure mechanism |
| c1_seed1 (the knob) | `+gen_ut_intg_span_arm_count=1` | 1 | 0 | 21 crash_dump, 1 isa_rd | PASS 0 FAIL 1 | FAIL, uvm_error at sim.log:34 (isa_rd) |

The red's isa_rd line, from the retained log:

```
UVM_ERROR dv/auto_dv/env/gen_rvfi_pkg.sv(260) @ 55500: uvm_test_top.env.sb [isa_rd] rd model=x11/22221111 dut=x11/22220111 (order=8 pc=80000118 insn=00252583 trap=0 intr=0 rd=x11/22220111 mem=800002e2 w0000 r1111 mode=3 cyc=50)
```

That line also identifies WHICH access the single corruption hit, which is the knob's whole point. The load's
merged word is `{word[buf+4][15:0], word[buf][31:16]}` = 0x22221111 on the clean image, and the DUT wrote
0x22220111: the difference is bit 12 of the merged word, which is bit 28 of the word at `buf`. So the one
armed corruption landed on the FIRST of the load's two bus accesses, as the bug log's B16 precondition asks.

## 4. The evidence set could have failed

If the knob did not reach the arming, a count-1 run would be indistinguishable from a default run: the driver
would echo 2, two corruptions would be injected, the load's write would be suppressed and the run would PASS.
It does not. The default's own eight runs are the control in the other direction: they must reproduce today's
behaviour exactly, and they do (driver armed 2, injected_intg 2, one suppressed record, zero UVM errors, PASS,
eight of eight), so a knob that silently changed the default would have shown here.

## 5. Sixteen runs, eight seeds at each count

Retained as `gen_fu_l64_b16_sweep16.log`, produced by the census script over the run directories.

| arm count | seeds | driver armed | suppressed records | no-suppress assertion | verdict |
|---|---|---|---|---|---|
| 1 | 1..8 | 1 in 8 of 8 | 0 in 8 of 8 | fires in 8 of 8 | FAIL in 8 of 8 |
| 2 (default) | 1..8 | 2 in 8 of 8 | 1 in 8 of 8 | never | PASS in 8 of 8 |

## 6. Which failure mechanism a count-1 run raises is SEED DEPENDENT, and one of the two is not

The isa_rd miss appears in 2 of the 8 count-1 seeds (1 and 5). The reason is derivable: the driver flips one bit
of the 39-bit SECDED-encoded response word, uniformly over all 39 positions
(`gen_agents_pkg.sv:338`, `data_w = $bits(vif.rdata)` = 39), and the misaligned `lw a1, 2(a0)` merges only
the UPPER half-word of the first bus word into its result. So the flip changes the value the core writes only
when it lands in one of those 16 positions; a flip in the lower half-word or in the 7 check bits leaves the
merged data equal to the model's and raises no rd miss. The seed-independent mechanism is the module's own
assertion, which fires in 8 of 8: `GEN_UT_INTG_SPAN: no record with rf_wr_suppress`. A test that rests on
isa_rd alone would pass on six of these eight seeds.

THE 16 IS OFFSET-SPECIFIC and must not be read as a property of the first-beat class (rtl-arch, after this
record was handed). The value-changing positions are the ones the offset merges in, so their number is the
width of the first-beat slice the offset selects: 24 at offset 1, 16 at offset 2, which is this program's
effective address, and 8 at offset 3 (`rtl/ibex_load_store_unit.sv:91`, `:235`, `:272-274`). The harmless
positions are therefore the seven check bits AND the unmerged half, not the check bits alone. The conclusion
does not change and is the durable part: the register value is not a reliable witness for this class at any
offset, because a data-bit corruption in the unmerged half is as invisible in the register as a check-bit one.

## 7. A TB defect the count-1 runs expose (reported, not fixed here)

Every count-1 run raises 20 or 21 `crash_dump` errors of one shape:

```
UVM_ERROR dv/auto_dv/env/gen_checkers_pkg.sv(467) @ 75500: uvm_test_top.env.misc_mon [crash_dump] crash_dump exception_pc/exception_addr 00000000/800002e2 at order 9: model mepc/mtval 00000000/800002e0, previous 00000000/800002e0, next 00000000/800002e0
```

The DUT's mirror is right: for a misaligned load whose FIRST word carried the corruption the internal NMI's
mtval is the access address 0x800002e2, not the announced word address 0x800002e0
(`rtl/ibex_controller.sv:416`, `rtl/ibex_load_store_unit.sv:258`). The scoreboard knows that rule and applies
it, but only inside the block guarded by `t.ext_rf_wr_suppress` (`dv/auto_dv/env/gen_rvfi_pkg.sv:485-498`, the correction itself at `:493`),
so with the flag clear the model keeps the announced word address and the crash_dump rule fires once per
following record until the window drains. This is a TB gap, not a second DUT finding, and it is NOT fixed in
this landing: the correction cannot simply move out of that block because the announcement is consumed there by
`take_intg_word` as part of the T-183 gate's accounting, so the fix needs a peek instead of a take and a
judgement change carries its own trust triad. Reported to the Orchestrator and the DV Lead for the TB defect
register.

## 8. A correction owed to the bug log's B16 scoping

B16's scoping paragraph (d) says "the scoreboard's T-183 gate expects no register write for a load whose
corruption the driver announced and compares the core's rd fields against no write, so the core's write raises
[isa_rd]". The gate as built is entered only when the DUT asserts `rvfi_ext_rf_wr_suppress`
(`gen_rvfi_pkg.sv:485`), so in B16's case it is never entered and it checks nothing. The isa_rd miss that the
seed-1 run does raise comes from the ordinary rd compare seeing a different data word, which Section 6 shows is
present on 2 of 8 seeds. The rule "an announced corruption of a load's word obliges a suppressed write" is not
built. That is a checker the doc-following direction of B16 needs, and it is not this landing's knob.

## 9. Waveform confirmation (LOG-103), as a pair with the default as its control

A separate waves build (`gen_build.py --build gen_tb --waves --local-cocotb`, vcs rc=0) and two
`gen_run.py --test gen_ut_intg_span --seed 1 --waves` runs, one at each arm count (run directories
`dv/auto_dv/out_b16waves/runs/l64_c1` and `l64_c2`); the FSDB path is in the retained `result.yaml` of each. The data bus was read with the fsdb-mcp-server against the build's own
`vcs_simv.daidir`; the transition tables are retained as `gen_fu_l64_b16_waveform.log`. In FSDB units of 10 ps:

| signal | count 1 (the knob) | count 2 (the control) |
|---|---|---|
| the request phase (`data_req_o`, both `data_gnt_i` pulses, `data_addr_o` 0x800002e0 then 0x800002e4) | identical | identical |
| beat 1 `data_rdata_i` at 49000 | 0x0101111111, word 0x01111111 (clean 0x11111111, bit 28 flipped) | 0x0101111111, byte-identical |
| beat 2 `data_rdata_i` | 0x5d22222222 at 54000, word 0x22222222, the CLEAN second word | 0x5d22222322 at 52000, word 0x22222322, bit 8 flipped |

So the knob removes the second injection and changes nothing else on the bus. The beat-2 instant moves by two
cycles because the extra injection consumes `$urandom` draws that the response-delay pick reads afterwards; the
request phase and both grants are unchanged. Bit 28 of the first word is bit 12 of the merged result
`{word[0x800002e4][15:0], word[0x800002e0][31:16]}`, which is the bit the count-1 run's isa_rd line reports.

## 10. Checks run on this landing

- `gen_knobs_codegen.py --check`: up to date after the render (the four rendered targets and the three
  `.svh` files it also owns).
- `dv/auto_dv/tb/unit/gen_ut_knobs_codegen.py`: PASS, 0 failures (retained as
  `gen_fu_l64_knobs_codegen_green.log`), including its own red-and-restore pass over each rendered target.
- The compile above, vcs exit 0.
- The sixteen runs of Section 5.
- `gen_comment_census.py --root dv/auto_dv/gen_tb --verbose`: the handed module carries no process id.
  Its docstring named the scoreboard's gate by an Orchestrator task id, which the code-comment rule of
  `gen_test_plan.md` Section 0 sends out at the file's next touch; it now names the gate by what it does.
  The same id stands in `gen_rvfi_pkg.sv:482`, which this landing does not touch, and is owed there.
  Five task ids remain elsewhere under `dv/auto_dv/gen_tb`, in files this landing does not hand.

## 11. Retained logs

Under `dv/auto_dv/evidence/gen_tdd_logs/lockstep/` with manifest rows in
`dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md`:
`gen_fu_l64_b16_c2_seed1_run_header.txt`, `_verdict.txt`, `_sim.log`;
`gen_fu_l64_b16_c1_seed1_run_header.txt`, `_verdict.txt`, `_sim.log`, `_stdout_excerpt.log`;
`gen_fu_l64_b16_sweep16.log`; `gen_fu_l64_knobs_codegen_green.log`;
`gen_fu_l64_b16_waveform.log`, `gen_fu_l64_b16_waves_c1_result.yaml`, `gen_fu_l64_b16_waves_c2_result.yaml`.
