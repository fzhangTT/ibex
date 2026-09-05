# IRQ triage evidence, retained

Written 2026-09-05T05:18:20Z by the Runtime Manager so a committed row can cite a committed path. Every file here is
BYTE-IDENTICAL to the served record it came from under `dv/auto_dv/work/runtime/done/`, which git does
not track; no header was added to any of them, so each sha256 is re-derivable from its source. This is
TRIAGE EVIDENCE: none of it is a property of any commit, none of it entered a measured merge, and no
file here carries a manifest row.

| file | bytes | sha256 | source under work/runtime/done |
|---|---|---|---|
| `gen_rtl_arch_010_served.yaml` | 1973 | `e4a8e6798cd1295ad05a92de20e45e81ad8b1f500488aede306aa13e14423885` | `rtl-arch-010.yaml` |
| `gen_rtl_arch_010_request.yaml` | 13455 | `4465f436ce60c5b434c7d935fee3c7fc73492fe7d41fc6b19a8531caa17a575c` | `rtl-arch-010.request.yaml` |
| `gen_irq_quiet_probes.yaml` | 5946 | `10a0414edb4796b961f284aa58c5909e22c6e066f4988141619827d2b62c29f4` | `gen_irq_quiet_probes.yaml` |
| `gen_irq_probe_a_direct.yaml` | 4480 | `0f6a6af1e673e25c8d1e50fe2802419231c3b4434893f4a7ad30b10eca80b018` | `gen_irq_probe_a_direct.yaml` |
| `gen_pmp_covergroup_control.yaml` | 2135 | `63dd519b2c7717756a40ce9acee0eaa6e33e84e9e3f71d25e38fff4dcd1617f6` | `gen_pmp_covergroup_control.yaml` |
| `gen_export.txt.gz` | 155526 | `3e1f03baa414b9fcaca07ffe04cb02c70a58409fbdca1c2f972b17baed080ba3` | (the wave run's export, compressed) |

## The export file

Retained compressed because the original is 1.3 MB. `gzip -n` is the recipe the round-0 archive record
already documents; site gzip is 1.9, and another version could produce different bytes.

    original            gen_export.txt, 1320756 bytes
    original sha256     77fdcd02818d2cc6316f4a764b3c18ff67c622422792c94eb92db2f89312c7ad
    original lines      29557
    retained            gen_export.txt.gz, 155526 bytes, reproducible (two passes give one digest)
    recover with        gunzip -c gen_export.txt.gz

## What each file records

| file | run directory | entry | seed | commit | purpose |
|---|---|---|---|---|---|
| `gen_rtl_arch_010_served.yaml` | `regress_irq_wave010/runs/gen_test_irq_basic_red_694904681` | gen_test_irq_basic_red | 694904681 | 07653dd873fa3dff0b18c419f9345a2e9977b993 | the -debug_access+all wave run rtl-arch read to place the order-548 divergence; FSDB, export and reproduction checks |
| `gen_rtl_arch_010_request.yaml` | (no run) | - | - | - | rtl-arch's request as filed, kept beside the served block so the acceptance conditions are readable with the result |
| `gen_irq_quiet_probes.yaml` | `regress_irq_probe_b2/runs/{ctrl,schedquiet,quietpin}_694904681` and `regress_irq_probe_b/runs/gen_test_irq_probe_quiet_694904681` | gen_test_irq_basic_red | 694904681 | 07653dd873fa3dff0b18c419f9345a2e9977b993 | the control and the three quiet probes, RE-MEASURED from the run artifacts rather than transcribed |
| `gen_irq_probe_a_direct.yaml` | `regress_irq_probe_a4/runs/local_gen_test_irq_probe_direct_694904681` | gen_test_irq_probe_direct (scratch entry) | 694904681 | none: the 07653dd mirror plus one uncommitted generator | the mtvec-direct probe; NOT pinnable, and its zero scoreboard errors are not evidence about the divergence |
| `gen_pmp_covergroup_control.yaml` | `regress_pmp_cg_control/runs/gen_test_pmp_mseccfg_1396647892` | gen_test_pmp_mseccfg | 1396647892 | 2d87642b1d36a943fc08f7cb47258310c9199e81 | the positive control for the PMP covergroup ABSENCE before the render landed: 26 covergroups, none PMP |
| `gen_export.txt.gz` | `regress_irq_wave010/runs/gen_test_irq_basic_red_694904681` | gen_test_irq_basic_red | 694904681 | 07653dd873fa3dff0b18c419f9345a2e9977b993 | the pin and ibus event rows of the wave run, read together with the FSDB |

## Out-tree artifacts these cite

The FSDB and the coverage databases stay in the out-tree and are not retained here. The wave is
`regress_irq_wave010/runs/gen_test_irq_basic_red_694904681/waves.fsdb`, 606509 bytes, covering 0 to
65420.01 ns, with its design database at `regress_irq_wave010/build/gen_tb/vcs_simv.daidir`.

One unit note carried from the served block, because it cost a wrong window once: the UVM log timestamps
are 10 ps ticks, not nanoseconds. A record logged "@ 1185500" is at 11855 ns, and the run ends at
65420 ns.
