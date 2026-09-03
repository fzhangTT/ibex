# Wave dump for debug runs (SIM_RECIPE Section 6). gen_run.py renders {tb_top} and
# {dut_instance}; SIM_DIR comes from the environment of the run.
if { [info exists ::env(VERDI_HOME)] } {
    fsdbDumpfile "$::env(SIM_DIR)/{waves_fsdb}"
    fsdbDumpvars 0 {tb_top} +all
    fsdbDumpSVA 0 {tb_top}.{dut_instance}
} else {
    dump -file "$::env(SIM_DIR)/{waves_vpd}"
    dump -add { {tb_top} } -depth 0 -aggregates -scope "."
}
run
quit
