# Ten-entry robustness wave at 4017573, retained

Written 2026-09-05T09:58Z by the Runtime Manager. The wave answers whether the measured entries' declared bins
hold on draws nobody has seen, and it is the measurement the Test Writer's manifest re-renders read.

The three files beside this one are BYTE-IDENTICAL to the served records under `dv/auto_dv/work/runtime/done/`,
which git does not track. No header was added, so each sha256 is re-derivable from its source.

| file | bytes | sha256 |
|---|---|---|
| `gen_wave_4017573.yaml` | 6793 | `e4858b6082fb9ae0aa344f6cf5fddfbe2109f51965c563d6a622a2adddca4b97` |
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
| 13 | the irq_entry CHECKER fires, `gen_checkers_pkg.sv:133`: "lines 00001 raised at cycle 44238 (order 1381) not taken within 17 records (now order 1400, mie 7fff0888 mstatus 00000088)". mie bit 0 is clear while the raised line is bit 0, so the checker requires a line the enable mask does not enable to be taken. Reads as checker-versus-stimulus; the call is the Test Writer's and tb-infra-2's. |
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
