# Ten-entry robustness wave at 4017573, retained

Written 2026-09-05T09:58Z by the Runtime Manager. The wave answers whether the measured entries' declared bins
hold on draws nobody has seen, and it is the measurement the Test Writer's manifest re-renders read.

The three files beside this one are BYTE-IDENTICAL to the served records under `dv/auto_dv/work/runtime/done/`,
which git does not track. No header was added, so each sha256 is re-derivable from its source.

| file | bytes | sha256 |
|---|---|---|
| `gen_wave_4017573.yaml` | 10946 | `57e756e305a6d790eebadb884a6f89d12184ec0d8d6dc561cefa9c2c52747179` |
| `gen_wave_census.txt` | 4685 | `11eaf13f51e388b38fac0ece316a6e61a24b155f7a215fc91f5e40c74d924f76` |
| `gen_wave_nothit.txt` | 3139 | `10243f2cab29bc3643c274615c82bffff2ae1412778019e8e82ad477b385fdce` |

Pinned to 40175738c709d1151a7d6a448ac46034767b7a09, head-mode mirror tree `a9176c840e23`, driver a detached
archive of that commit whose `gen_run.py` hashes to the committed blob. Out directory
`/proj_soc/user_dev/fzhang/ibex_dv_out/regress_wave_4017573`. Every run carried the fcov check INLINE, so the
declared-bin figures below are each run's own checker verdict and not a post-hoc reading. 403 runs planned, 403
run.

Seeds are FRESH BY DESIGN: each entry draws forty from its own stream keyed by the wave base and the entry name,
all 403 distinct, none colliding with the fix sweep's bit_ratified set, checked before dispatch. Re-using the fix
sweep's seeds would have re-measured what was already measured.

## Result per entry

| entry | runs | PASS | declared | at every seed | under the bar | declared cross legs | cross legs under the bar |
|---|---|---|---|---|---|---|---|
| gen_test_bit_ratified | 40 | 40 | 617 | 617 | 0 | 494 | 0 |
| gen_test_cmp_zca | 40 | 40 | 300 | 300 | 0 | 201 | 0 |
| gen_test_rst_boot | 40 | 40 | 6 | 6 | 0 | 0 | 0 |
| gen_test_pmp_csr_warl | 40 | 39 | 179 | 178 | 1 | 91 | 1 |
| gen_test_mul_mul | 40 | 38 | 338 | 336 | 2 | 289 | 2 |
| gen_test_isa_shift | 40 | 35 | 120 | 116 | 4 | 89 | 4 |
| gen_test_mul_div | 40 | 30 | 196 | 190 | 6 | 139 | 5 |
| gen_test_cmp_zcb | 40 | 22 | 96 | 87 | 9 | 61 | 6 |
| gen_test_cmp_zcmp_basic | 40 | 1 | 325 | 319 | 6 | 240 | 5 |
| gen_test_irq_basic | 40 | 21 | 0 | n/a | n/a | 0 | n/a |
| gen_test_irq_basic_red | 3 | 1 RED-OK | 0 | n/a | n/a | 0 | n/a |

THE TWO FIXED GENERATORS HOLD ON UNSEEN DRAWS. bit_ratified and cmp_zca are 40 of 40 with every declared bin at
every seed. csr_warl produced a program at all forty seeds, so the backstop closes the generator-assert class.

BINS NO READER COULD EXAMINE. The two irq entries declare no bins at all, being unmeasured with a null
`fcov_expectation_file`, so nothing can be placed under the every-seed bar for them and NO MAPPER EXISTS FOR THESE
GENERATORS. For the nine entries with manifests the inline check covers every declared bin, so the examined count
and the declared count coincide and no separate unexamined count arises.

ONE OBSERVATION FOR THE CROSS-OPERAND RULE. Of the 28 declared bins under the every-seed bar across the whole
wave, 24 are CROSS LEGS. The fragility is concentrated in crosses, which is what the rule predicts and which the
per-bin listing lets a reader check.

## The irq entry: 19 of 40 fail on mechanisms, not coverage

Kept separate because they have different owners. Run directories are in the out tree and are retained until this
block is committed.

| runs | mechanism |
|---|---|
| 13 | the irq_entry CHECKER fires, `gen_checkers_pkg.sv:133`: "lines 00001 raised at cycle 44238 (order 1381) not taken within 17 records (now order 1400, mie 7fff0888 mstatus 00000088)". CORRIGENDUM 2026-09-05T10:30Z, one row, superseding the reading first written here. THE FIRST READING WAS WRONG: it said mie bit 0 is clear while the raised line is bit 0, so the checker required a line the enable mask does not enable, and called it checker-versus-stimulus. The raised lines were ENABLED, and that holds across two different fires: the Test Writer read a run whose fires name fast lines 16 and 10 at mie bits 29 and 23, and the Runtime Manager decoded a run whose fire names line 0 at bit 3, with identical mie 0x7fff0888 and mstatus 0x88. THE CHECKER FIRES CORRECTLY. THE CAUSE IS A CHECKER DEFECT, tb-infra-2's, fix queued: the interrupt was legitimately masked for the whole of a previous handler, a 17-instruction handler from entry to return inclusive plus a two-instruction vector stub, so 19 masked records against a 17-record bound, and the measured raise-to-fire deltas are 18 to 23 with 19 dominating. The checker restarts its expectation's bound under the NMI and debug masks and does NOT restart it under the global enable, which appears only in the fire condition at expiry, so a line masked for an entire handler accrues bound and the fire then samples MIE after the mret has restored it. Both other candidate gates were measured ABSENT from the emitted program by the Test Writer: no compressed instructions, so no expansion commit phase, and no debug or step state. The original error was reading a line bitmap and a raw enable word in the same numbering without tracing the index-to-bit mapping. FIRE POPULATION, stated precisely because several counts here are close together. Of the 40 gen_test_irq_basic runs, 21 PASS, 13 fail with the checker as the verdict's reason, 5 fail on a protocol property and 1 on the harness timeout. FOURTEEN of the 40 CONTAIN at least one checker fire: the 13 plus gen_test_irq_basic_1207954461, which failed first on a property and carries fires further down its log. The two gen_test_irq_basic_red runs also contain fires, so SIXTEEN runs across the entry family fire at all. THE RATE IS NOT UNIFORM AND IS UNEXPLAINED: gen_test_irq_basic_1207954461 fires 258 times where the other fifteen fire between 1 and 17. That is a named fact for the checker-fix record. COUNT, AND A DISAGREEMENT NOW CLOSED. The fire count is 334 across those 16 runs, 330 in the 14 gen_test_irq_basic runs and 4 in the 2 red runs. Method, the Test Writer's and re-derived here by the Runtime Manager rather than adopted: count lines matching "(order N) not taken within 17 records (now order M" in each run's sim.log. An earlier Runtime Manager figure of 343 counted every line mentioning the id; the 9 extra are UVM end-of-simulation per-id tally lines of the form "[irq_entry]     6", which carry no delta and are not fires. Both counts were correct for what they counted and the fire count is 334. One sub-count is corrected: the 330 fall in FOURTEEN gen_test_irq_basic runs, not thirteen. WHY THE TALLY LINE IS ABSENT FROM SEVEN OF THE SIXTEEN, measured rather than assumed. It was suggested that a UVM quit count cuts the report phase short. It does not: no log contains a quit-count line, and one of the seven fires only once, which no quit count would reach. The discriminator is simpler and exact: the seven runs missing the tally have NO "UVM Report Summary" section at all, and the nine that carry a tally all have one. The run ended before the report phase emitted its summary. So a reader counting tally lines would UNDERCOUNT, missing seven runs entirely including the 258-fire outlier, which is why the fire count above is taken from the fire lines and not from the tallies. RETENTION GAP, recorded as the Runtime Manager's own. These runs retain NOTHING per-record: every result.yaml records export_file null and export_rows_observed null and no run directory holds a trace file, because the export sink was never enabled by its plusarg (gen_tb_pkg.sv:36). A run that fires a checker sixteen times in forty and keeps no record stream forces every investigation to reconstruct arithmetic from message text; it cost the Test Writer a program count and tb-infra-2 two exchanges on this item. The flow change, defaulting the export on for measured entries or at least for entries carrying a fire check, is on the Runtime Manager's list. |
| 3 | `sva_rvfi_irq_valid_exclusive` ONLY. Already ruled AT THIS COMMIT: the committed ruling says it fires legitimately and the PROPERTY must change, not the stimulus, and the property has not changed since. Known-wrong property, not a new finding. |
| 2 | the ruled property PLUS three UNRULED ibus properties: `sva_ibus_gnt_only_with_req`, `sva_ibus_outstanding_max`, `sva_ibus_rvalid_outstanding`. The ruled one fires first, the ibus ones tens of MICROseconds later (47.73 us in gen_test_irq_basic_165313640, 26.59 us in gen_test_irq_basic_1207954461, at 10 ps ticks). NOT called a cascade and NOT called independent. For rtl-arch and tb-infra-2. |
| 1 | a HARNESS timeout, classified and named below. |

THE ONE HARNESS FAILURE, named as asked. Run directory
`/proj_soc/user_dev/fzhang/ibex_dv_out/regress_wave_4017573/runs/gen_test_irq_basic_1800473338`. The failure is
`GEN_TEST: stimulus() did not finish after the end of test (SimTimeoutError)` at `gen_test_template.py:482`, with
zero UVM errors, `$finish` reached, no pass marker, and a simulation that ran to 1123735 ns against a typical
65420 ns. A fixed cocotb timeout in the stimulus path at this seed: seed-dependent harness, not a design finding,
and the class that can kill a measured round.

THE RED FIXTURE IS RED-OK AT 1 OF 3. The other two failed for an undeclared reason and the reason is the SAME
irq_entry checker fire, so the fixture's designed failure is MASKED rather than absent.

## The 46 stimulus-class not_hit shapes

Undeclared, so no coverage check mentions them; read per seed from each run's own report with the reviewed parser.
23 of bit_ratified's 24 and 21 of cmp_zca's 22 are hit at EVERY one of the forty seeds, so the re-render may
declare those 44. The two never hit are `gen_bit_sbit_cg.cp_binv_twice.yes` and
`gen_cmp_imm_edges_cg.cp_cj_off.self`. This reproduces the Critic's measurement independently, by a different
route and on different seeds, and names the same two.

`cp_binv_twice.yes` reads 0 of 40 here BY CONSTRUCTION: the wave was deliberately not re-pinned for the
binv-pair fix, so its bin is measured by the separate post-fix block instead.
