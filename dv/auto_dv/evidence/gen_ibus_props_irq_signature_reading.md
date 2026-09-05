# The three ibus property firings that follow the ruled exclusivity property: an RTL/TB reading

Owner: rtl-arch, 2026-09-05, at the Orchestrator's request after runtime-2's 403-run wave regression
on commit 4017573. Question asked: can the ibus firings be a consequence of the exclusivity
property's condition, or are they a separate protocol observation, and what would settle it.
No RTL change and no exclusion follows from this reading. Citations are to commit 4017573, the tree
those runs were built from, and were checked against that commit rather than against HEAD.

## 1. Answer in one paragraph

The three ibus firings are ONE observation, not three, and they are NOT a consequence of the
exclusivity property's condition. Two of the three are mechanically downstream of the first inside the
testbench's own counter, which is proved from the logs without a wave. The exclusivity property is not
sufficient for them: it fires in 8 of the 403 runs and the ibus signature appears in 2. What the two
share is a plausible provoking condition, the interrupt and NMI traffic that drains the fetch
pipeline, not a causal chain from one property to the other. A property is an observer; it cannot
cause a bus event. What the logs cannot settle is whether the single root event is a testbench
grant-decision artefact or a core protocol violation, and that needs one wave.

## 2. What the three properties actually assert (4017573)

    dv/auto_dv/tb/gen_protocol_props.sv:183  `P_ASSERT(ibus, sva_ibus_gnt_only_with_req,  instr_gnt_i |-> instr_req_o)          // TB
    dv/auto_dv/tb/gen_protocol_props.sv:184  `P_ASSERT(ibus, sva_ibus_rvalid_outstanding, instr_rvalid_i |-> ibus_outstanding > 0) // TB
    dv/auto_dv/tb/gen_protocol_props.sv:185  `P_ASSERT(ibus, sva_ibus_outstanding_max,    ibus_outstanding <= IBUS_MAX_OUTSTANDING) // DUT (bound 8)

All three are evaluated under the macro's guard `disable iff (!rst_ni || !en_ibus)` (:111). Two are
TB obligations by their own annotation; the third is annotated DUT.

The third does not read a DUT signal. It reads the TESTBENCH's counter, updated at
dv/auto_dv/tb/gen_protocol_props.sv:128 as

    ibus_outstanding <= ibus_outstanding + (instr_req_o & instr_gnt_i) - instr_rvalid_i;

`ibus_outstanding` is declared `int unsigned` (:122). So a response with the counter at zero does not
saturate, it WRAPS to 4294967295, and the bound-8 property then fires every cycle until the counter is
brought back under eight. The file already anticipates the neighbouring case in words at :119-120:
"a response in its own grant cycle sees outstanding == 0 and fails the TB obligation".

## 3. The evidence in the two runs, measured

Runs, under /proj_soc/user_dev/fzhang/ibex_dv_out/regress_wave_4017573/runs/:
gen_test_irq_basic_165313640 and gen_test_irq_basic_1207954461. Times are the UVM log's 10 ps ticks;
one cycle is 1000 ticks.

| run | property | firings | first at |
|---|---|---|---|
| 165313640 | sva_rvfi_irq_valid_exclusive | 2 | 13565500 |
| 165313640 | sva_ibus_gnt_only_with_req | 1 | 18338500 (cycle 18334) |
| 165313640 | sva_ibus_rvalid_outstanding | 8 | 18349500 (cycle 18345) |
| 165313640 | sva_ibus_outstanding_max | 280 | 18350500 (cycle 18346) |
| 1207954461 | sva_rvfi_irq_valid_exclusive | 3 | 6591500 |
| 1207954461 | sva_ibus_gnt_only_with_req | 1 | 9250500 |
| 1207954461 | sva_ibus_rvalid_outstanding | 70199 | 15158500 |
| 1207954461 | sva_ibus_outstanding_max | 449948 | 26503500 |

Three readings follow from those numbers alone.

The bound-8 firing is the counter wrapping, not a bus event. In 165313640 its first firing is at cycle
18346 and the first response-without-outstanding is at cycle 18345: EXACTLY one cycle, which is the
counter's own update delay. Its 280 firings against the other's 8 is the every-cycle flood that a
wrapped unsigned counter produces.

The response-without-outstanding firing does NOT always wrap the counter. In 1207954461 it fires 70199
times from cycle 15158 while the bound-8 property stays silent until 26503, eleven million ticks later.
That is the same-cycle case the file names at :119-120: with a grant and its response in one cycle the
expression is 0 + 1 - 1 = 0, so the obligation fails while the counter never wraps. The bound-8 flood
starts only when a response finally arrives without a same-cycle grant.

The grant-without-request firing is first of the three IBUS properties in BOTH runs and fires
exactly ONCE in each. In 165313640 it
precedes the other two by 11 and 12 cycles.

So the signature reduces to one root event per run, a grant asserted in a cycle whose request is low,
followed by a queued response the counter never accounted for, followed by the counter wrapping.

## 4. Why it is not a consequence of the exclusivity condition

The exclusivity property fires in 8 of the 403 runs; the ibus signature appears in 2. Six runs
therefore satisfy the exclusivity condition and produce no ibus firing at all, so that condition is not
sufficient. The gaps are also large: 4773 cycles in 165313640 and 2659 cycles in 1207954461 between
the first exclusivity firing and the first ibus firing. (Those are tens of MICROseconds at this
timescale, not milliseconds.)

More fundamentally, a property is an observer. `rvfi_ext_irq_valid |-> !rvfi_valid` reads two RVFI
ports; it drives nothing and cannot make a grant appear. The only honest form of the question is
whether the STATE the exclusivity property happens to observe also provokes the bus event, and the
answer available from the logs is that it is neither necessary nor sufficient, only correlated in two
runs out of eight.

What is plausible, and is a shared cause rather than a chain: the interrupt and NMI traffic drains the
fetch pipeline, and the core's request is combinational, `assign instr_req = ((~icache_enable_i |
branch_i) & lookup_grant_ic0) | (|fill_ext_req);` at rtl/ibex_icache.sv:1030-1031, with the fill
buffers marked stale on a branch at :741. An interrupt entry is a branch, so a drain can drop the
request within a cycle.

## 5. The one thing the logs cannot settle, and the wave that would

At the pin, "a grant with the request low" has two very different causes and the logs cannot separate
them.

Either the core deasserted its request before the grant, which the clone's own interface reference
forbids in prose: `instr_req_o` "must stay high until `instr_gnt_i` is high for one cycle"
(doc/03_reference/instruction_fetch.rst:53-54). That would be a core protocol finding.

Or the request was high at the accepting edge and the property saw an instant where it had already
moved. That is a testbench decision-instant question, and the driver's shape at 4017573 makes it live:
the loop waits on `@(negedge vif.clk)` (dv/auto_dv/env/gen_agents_pkg.sv:265) and asserts
`vif.gnt = 1'b1` at :313, still on that falling edge, while the accepting-edge fix moved only the
address capture, `@(posedge vif.clk)` at :320 followed by `p.addr = vif.addr` at :321. So the grant
DECISION is still taken half a cycle before the edge at which this property is evaluated.

The wave that settles it, and nothing less will: a dump covering the cycles around the single
grant-without-request event, in 165313640 that is cycle 18334 with a margin of about fifty cycles each
side, carrying gen_tb_top.u_ibus_if.{req,gnt,rvalid,addr,outstanding}, the DUT ports
gen_tb_top.u_dut.{instr_req_o,instr_gnt_i,instr_rvalid_i,instr_addr_o}, and on the core side
if_stage_i.gen_icache.icache_i.{instr_req,fill_ext_req,fill_busy_q,fill_stale_q,branch_i}. The single
question to read off it is whether instr_req_o was high at the rising edge where the grant was
sampled. If it was, the finding is the decision instant and belongs with the driver; if it was not,
the finding is the core dropping a request before its grant and belongs to the RTL.

## 6. Whether the parked replacement property changes the picture

It does not. The replacement proposed in Section 6 of dv/auto_dv/evidence/gen_rvfi_irq_valid_exclusive_ruling.md
changes what the RVFI property asserts. It touches no bus signal, no driver and no counter, so every
firing in Section 3 would occur unchanged with the replacement in place. The only difference is that
the exclusivity firing would stop being reported, which would remove the correlation from the logs
without removing anything from the design or the testbench. That is worth stating plainly, because a
correlation that disappears when one observer is retired was never evidence of a chain.

## 7. The root event, settled by waveform (added 2026-09-05)

Section 5 left the single grant-without-request event open between two causes and named the dump that
would decide it. That dump was run and read, and this section records the answer. It also records the
transitions themselves, because the waveforms were non-durable scratch and have been released: this
text is now the surviving evidence of what they showed.

The runs. A fresh -debug_access+all build from the same root, pinned to the same commit 4017573 as the
wave regression and differing from it only by that flag, at both seeds, 165313640 and 1207954461. The
firing totals matched the original runs in both seeds (291 and 520233), so the dump did not perturb
the behaviour. The waveforms were
`regress_ibus_wave/runs/gen_test_irq_basic_165313640/waves.fsdb` (665363 bytes, md5 049a2646bf09) and
`.../gen_test_irq_basic_1207954461/waves.fsdb` (23564419 bytes, md5 e9579d32030d); both were verified
against those figures before reading and are RELEASED SCRATCH, not retained evidence.

What the waveform shows, seed 165313640, in the FSDB's 10 ps units with the clock rising on the half
tick and falling on the tick. The grant is held high with ZERO transitions across 18330000 to
18342000, twelve cycles spanning the event. The request is high throughout that span except for a
single dip, low from the falling edge 18338000 and high again exactly at the rising edge 18338500,
which is where the property fires. At that falling edge `branch_i` goes 1 to 0 and `lookup_grant_ic0`
goes 1 to 0 while `fill_ext_req` is already 0 from 18337500, which is the whole request expression at
rtl/ibex_icache.sv:1030-1031 going false.

Seed 1207954461 is independent and identical in shape: the request low from the falling edge 9250000
to the rising edge 9250500, the same two signals collapsing at that falling edge, and there the
grant's own timing is visible, asserted at the falling edge 9249000 and deasserted at 9251000.

THE ANSWER. The request was low at the rising edge where the grant was sampled, and the core is
nonetheless clean. In both seeds the grant was already high at the rising edge BEFORE the dip, so the
request had been accepted and the obligation that
doc/03_reference/instruction_fetch.rst:53-54 states, that the request stay high until the grant is
high for one cycle, was discharged. The core then stopped requesting, which that rule permits. The
property fired because the grant OUTLIVED the request it accepted by one cycle and the half-cycle dip
landed in that extra cycle. So the root event is the grant-hold policy meeting a combinational
request, not a core protocol violation. No RTL change and no bug row against the design follows,
which is the same conclusion Section 1 reached for the signature as a whole and now rests on
measurement rather than on the two open hypotheses.

One measurement bounds it. In seed 165313640 the request toggles 217 times across the run, roughly a
hundred low periods, while sva_ibus_gnt_only_with_req fires exactly once. The grant is deasserted in
time in essentially every other case, so this is a rare alignment and not a policy that is broadly
wrong.

A hypothesis raised and refuted during the read, recorded so it is not raised again: that the grant
might be held constantly high, which would make `instr_gnt_i |-> instr_req_o` degenerate into a claim
that the core must always be requesting. It is not. The grant transitions 1357 times across that run.

What remains is not an RTL question. The property treats a held grant as implying a live request,
while the driver's grant can outlive the request it accepted, so the property and the driver's policy
disagree about what a held grant means. Which of the two should change is tb-infra-2's call.

## 8. The same run executing zeros at 0x80000022 (added 2026-09-05)

A later question about this same run, gen_test_irq_basic_1207954461, asked how the core comes to
execute an all-zero word at pc 0x80000022, whether the model or the DUT diverged first, what the
controller does with a pending enabled interrupt while trapping repeatedly, and whether the Section 7
event is causally upstream. This section answers those from the run's own log and the RTL.

### How the core reached 0x80000022: an MRET

The image covers 0x80000080 to 0x80000378 and its vmem carries one code section at word 0x20000020,
byte 0x80000080. So 0x80000022 lies BELOW the programmed region and reads as zeros; the disassembly
has no line at that address. The transition into it is an MRET:

    order=1130 pc=800001c0 insn=30200073 trap=0     0x30200073 is MRET (opcode 0x73, funct12 0x302)
    order=1131 pc=80000022 insn=00000000 trap=1

MRET takes the pc from mepc, so mepc held 0x80000022. It is therefore a return to a stale or
corrupted mepc, and none of the other candidates: not a jump into an unprogrammed region, not a
vector-table entry, and not a misaligned fetch.

NOT CLAIMED: how mepc came to hold 0x80000022. The value is consistent with the core having trapped
at that address earlier, but this log does not show the write and it is not inferred here.

A related hazard, because it turns one bad instruction into a loop: mtvec reads 0x80000001, so the
mode is vectored with base 0x80000000, and for an EXCEPTION the RTL takes `{csr_mtvec_i[31:8], 8'h00}`
(rtl/ibex_if_stage.sv:222-224), which is 0x80000000 and also lies below the image start. An exception
therefore vectors into unprogrammed zeros as well.

### Who diverged first: the DUT

The first divergence is order 462 at 9290500, `insn model=018b1063 dut=0062a023`, pc 0x80000154. The
image holds 018b1063 at 0x80000154, the model's word, and holds the DUT's word 0062a023 at
0x80000168, twenty bytes further on. So the DUT reported a real instruction from a different address
than the pc it reported, and the model was right. 23387 instruction mismatches follow. That is the
same wrong-word-at-a-pc shape as the order-548 event of Section 7, and here it delivers zeros as well
as neighbouring words: order 1122 and order 1126 both read pc=80000300 insn=00000000 trap=1 while
orders 1123 and 1127 read the same pc with the correct eb9ff06f.

### The all-zero word is a trap, and the masking is architectural

Every one of the 6813 records at pc=80000022 carries trap=1; traps also occur at 0x80000300 (366),
0x80000244 (68) and 0x800000e4 (63). Taking a trap clears the global interrupt enable: under
`csr_save_cause_i:` (rtl/ibex_cs_registers.sv:893) the CSR block sets `mstatus_d.mie = 1'b0;` (:924)
having saved it with `mstatus_d.mpie = mstatus_q.mie;` (:926), and an MRET restores it,
`mstatus_d.mie = mstatus_q.mpie;` (:956). The controller gates regular interrupts on that bit:
`assign irq_enabled = csr_mstatus_mie_i | (priv_mode_i == PRIV_LVL_U);` (rtl/ibex_controller.sv:490),
used by `handle_irq` at :498-500 within `(irq_nm | (irq_pending_i & irq_enabled))`.

So in M-mode a held fast interrupt whose own mie bit is set is still not taken while mstatus.MIE is
clear, and every trap clears it. A repeated trap masks the interrupt for as long as the loop runs
between mrets, which is the mechanism behind the stretches of 18 to 23 records in which a held,
enabled interrupt is not taken. This is architectural behaviour and not a controller defect.

### Is the Section 7 event causally upstream? Associated, not causal

In both runs carrying the grant-without-request event the first instruction divergence follows it
closely: 9250500 to 9290500, 40 cycles, in this run; 18338500 to 18373500, 35 cycles, in
165313640. Two independent runs, same ordering, same order of magnitude.

The obvious counter-example was checked and does not weaken it. Of the 403 runs only three show any
instruction divergence. The third, 1981534788, has zero grant events and zero exclusivity firings,
and its divergence is the OPPOSITE kind: at order 812, pc 0x8000016c, the DUT reported 0000006f and
the image holds 0000006f at exactly that pc, so there the MODEL is wrong and the DUT right, with 6
mismatches rather than 23387. It is a different failure, so among DUT-side wrong-word divergences the
association with the grant event is two for two.

NOT CLAIMED: causation. Section 7 established that the grant event is the driver granting for a
request that had ALREADY been accepted, which does not obviously enqueue a phantom transaction, so no
path from it to a word delivered for the wrong address is established. Temporal precedence and a
shape match are not a mechanism.

What would settle it, and a note that is mine to carry: a wave covering the span from the grant event
to the first divergence in either grant-event run, 40 cycles in this one and 35 in 165313640, so
about fifty cycles either side covers both, reading the fetch address issued and the word returned
for every transaction in that span to see whether any response is paired with an address the core did
not request. It cannot be done from what exists: the two dumps runtime-2 made were non-durable
scratch and were deleted at my own request after the Section 7 read, which was premature by one
question. A re-dump would be runtime-2's to schedule.

## 9. The unmapped store at 9284500, and a scoping corrigendum to Section 3

Runtime-2 censused 1207954461 by first firing and reported two events ahead of the grant event. This
section records what each turned out to be. Nothing in Sections 1-8 is withdrawn.

### 9.1 The earlier exclusivity firing is already in this file

The first of the two, sva_rvfi_irq_valid_exclusive at cycle 6591.5, is the row this file's own table
already carries as 3 firings first at 6591500, and Section 4 already gives the distance as 2659
cycles in this run and 4773 in 165313640, and already argues the exclusivity condition is neither
necessary nor sufficient. No fact changes.

CORRIGENDUM to Section 3, applied in place because the wording is what caused the report and a
corrigendum 250 lines below a defective sentence does not reach the next reader of it.

Before, as committed at 9f2edda: "The grant-without-request firing is first in BOTH runs and fires
exactly ONCE in each."

After, as this commit has it: "The grant-without-request firing is first of the three IBUS properties
in BOTH runs and fires exactly ONCE in each."

The scope was always the three ibus properties, which the sentence after it fixes by naming "the
other two". Read on its own the old sentence claimed the grant firing was first of any event, which
the table two paragraphs earlier contradicts, and two readers took it that way. Only the scoping words
changed; no figure, no claim and no other sentence was touched.

THE PREFIX CHAIN BREAKS AT BYTE OFFSET 4375, the first byte that differs from the 9f2edda blob. Every
prefix anchor this file previously carried lies after that offset, so none of them holds any longer:
the 8473-byte prefix that equalled the d8afbfd blob, the 12252-byte prefix that equalled the 7a0b6de
blob, and the 17620-byte prefix that equalled the f90fa636e886 blob of Sections 1 to 8. They are
retired rather than restated, because a prefix hash that no longer reproduces is worse than no hash.
The chain re-anchors from this commit: the byte-identical region shared with 9f2edda is the first 4375
bytes, and future appends are measured against this commit's blob.

### 9.2 The unmapped store is the divergent instruction, not a precursor

The second, a single MEM_UNMAPPED write to unmapped address 0x40000000 at 9284500, is six cycles
before the first instruction divergence at 9290500. It is the same instruction seen one pipeline
stage earlier, not a separate event.

Order 462 at 9290500 is pc=80000154 with dut insn=0062a023, and that record carries mem=40000000,
with the companion isa_mem line reporting "store model=0 dut wmask=1111". 0062a023 decodes as
sw x6, 0(x5): opcode 0100011 STORE, funct3 010 SW, rs1 x5, rs2 x6, immediate zero. A full-word store
whose address is whatever x5 holds. The MEM_UNMAPPED names 0x40000000 and the RVFI record names
mem=40000000 with a full word mask. The 6000-tick separation is six cycles, the distance from the LSU
access to the RVFI retirement comparison.

So the core did not diverge because it stored to an unmapped address. It stored to an unmapped
address because it had already been handed a store where the model expected a branch. The unmapped
write is downstream of the wrong word, and it is not a second candidate mechanism for it.

Measured in two independent builds, because the census was taken on a different regression from the
one this file cites. In regress_wave_4017573 (mirror 40175738c709), this file's own run, and in
regress_chkfix (mirror 9c7f8f63957d), both lines are identical: MEM_UNMAPPED at 9284500 to
0x40000000, and order 462 at 9290500 with insn model=018b1063 dut=0062a023.

NOT CLAIMED: that x5 held 0x40000000 for any traced reason. The store's address follows from its
operand and the RVFI record states it directly; where that operand value came from is not read here.

## 10. The window from the exclusivity firing to the unmapped store, seed 1207954461

The question this answers: what happened in the 2693 cycles between the first exclusivity firing at
6591500 and the unmapped store at 9284500. Read from the surviving sim.log of the run this file
already cites, regress_wave_4017573, mirror 40175738c709, with program/prog.dis from the same run.

### 10.1 Five events, and no scoreboard mismatch

The whole span occupies sim.log lines 44 to 56 and holds exactly five TB events, in order:
sva_rvfi_irq_valid_exclusive at 6591500 (cycle 6587), the same at 6646500 (cycle 6642),
sva_ibus_gnt_only_with_req at 9250500 (cycle 9246), sva_rvfi_irq_valid_exclusive at 9253500
(cycle 9249), and MEM_UNMAPPED at 9284500. Nothing else is logged in 2693 cycles.

The third exclusivity firing at 9253500 is new to this file's records. It falls three cycles AFTER the
grant event, not before it, and 31 cycles before the divergence. Section 3's table counted three
firings for this run but gave only the first.

No scoreboard mismatch occurs anywhere in the window; the first is at 9290500, order 462. This is an
absence claim, so it carries a positive control: the scoreboard announces itself ready at time 0
(sim.log line 30, "ISA model ready: pc=80000080 mtvec=80000001") and goes on to emit 79169 isa_*
errors in the run. It was armed and it was silent. The model and the DUT therefore agreed on every
retired instruction through order 461.

### 10.2 The store's origin is the program's own end-of-test store

From program/prog.dis:

  80000154 <gen_irq_wait>:
  80000154: 018b1063   bne   s6,s8,80000154
  80000158: 017da023   sw    s7,0(s11)
  8000015c: 00000297   auipc t0,0x0
  80000160: 26428293   addi  t0,t0,612    # 800003c0 <tohost>
  80000164: 00100313   li    t1,1
  80000168: 0062a023   sw    t1,0(t0)

The word 0062a023 lives at 0x80000168 and is `sw t1,0(t0)`, the write of 1 to tohost that ends the
test. Its address operand is set by the auipc at 0x8000015c and the addi at 0x80000160 immediately
above it. The DUT executed that word at pc 0x80000154, where the image holds the spin loop the model
expected, without executing either of the two instructions that set the operand. The operand was
therefore stale, and the record states its value: order=462 pc=80000154 insn=0062a023 rd=x0/00000000
mem=40000000 w1111 r0000 mode=3 cyc=9285.

Twelve instructions in the image write t0: auipc at 80000124, addi at 80000128, ori at 8000012c, lui
at 80000134, addi at 80000138, lui at 80000140, addi at 80000144, li t0,8 at 8000014c, auipc at
8000015c, addi at 80000160, `and t0,s6,t2` at 80000178, and `csrr t0,mtval` at 8000018c. Ten write a
constant and none of those constants is 0x40000000. The only two data-dependent writes are the last
two, both inside the interrupt handler. NOT ESTABLISHED: which of them ran, or what mtval held. No
record in the window shows either, and neither is asserted here.

### 10.3 The delivered words are wrong by whole fetch beats

IC_LINE_SIZE is 64 bits (rtl/ibex_pkg.sv:402), so a line is 8 bytes and IC_LINE_BEATS is 2 (:406) of
BUS_SIZE 32 bits (:397). A beat is a 4-byte word, two per line. Each word the DUT retired in this
span is unique in the image except 00000297, which appears twice.

| order | rvfi pc  | word delivered | its address in the image | offset in beats |
|---|---|---|---|---|
| 462 | 80000154 | 0062a023 | 80000168 | +5 |
| 463 | 80000158 | 018b1063 | 80000154 | -1 |
| 464 | 80000158 | 00100313 | 80000164 | +3 |
| 465 | 8000015c | 017da023 | 80000158 | -1 |
| 466 | 80000160 | 00000297 | 8000015c | -1 |

Order 466 is the ambiguous word; its other copy is at 80000124, and that record's rd=x5/80000160
shows the auipc executed at pc 80000160, so the near copy is tabulated. Order 465 is the sharpest
single case: the pc is beat 1 of the line at 80000158 and the word delivered is beat 0 of that SAME
line. Orders 463 and 466 have the identical relationship one line back, a pc at beat 0 of a line
receiving beat 1 of the line before it. All three are a one-beat lag.

CONSISTENT WITH, not established: a fetch-path delivery fault at beat granularity. That is the shape
the grant-hold mechanism predicts, an unmatched response advancing fill_rvd_cnt_q and with it
fill_rvd_beat, flipping the output mux from fill_data_rvd on the equality to fill_data_reg on the
greater-than. The two positive offsets, +5 and +3, are NOT explained by a one-beat lag and are not
fitted to it here. Which mechanism delivered the wrong word is still open between the grant-hold path
and an incomplete capture-edge fix, and the exonerating check on the icache registers comes first.

### 10.4 What this settles

The program was not off its rails before the wrong word. The model and the DUT agreed on every
instruction through order 461; the pc at the divergence is the spin loop the program is supposed to be
in; and the register the store used held architectural state the model also held.

The unmapped store is unmapped for a mechanical reason. The DUT was handed the store word without the
two instructions that set up its address operand, so the operand was stale. It is not a runaway
program reaching an unmapped address.

No wider dump span is needed for this question. The log answered it, and the re-dump span already
requested stands unchanged.
