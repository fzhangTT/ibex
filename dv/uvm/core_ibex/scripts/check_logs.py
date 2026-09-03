#!/usr/bin/env python3
"""
Collect all the logfiles for a single test, and check for errors.

Pass/fail criteria is determined by any errors found.
"""

# Copyright lowRISC contributors.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import argparse
import subprocess
import sys
import pathlib3x as pathlib

from metadata import RegressionMetadata
from test_entry import read_test_dot_seed
from test_run_result import TestRunResult, Failure_Modes

from spike_log_to_trace_csv import process_spike_sim_log  # type: ignore
from ibex_log_to_trace_csv import (process_ibex_sim_log,  # type: ignore
                                   check_ibex_uvm_log)

import logging
logger = logging.getLogger(__name__)


def compare_test_run(trr: TestRunResult) -> TestRunResult:
    """Compare results for a single run of a single test.

    Use any log-processing scripts available to check for errors.
    """

    # If the test is already marked as TIMEOUT before we check the logs, it must
    # have been killed at a process-level in the run_rtl stage.
    # Don't check the logs at all in this case.
    if (trr.failure_mode == Failure_Modes.TIMEOUT):
        trr.passed = False
        return trr

    # Process the Ibex trace to create a .csv
    # The format is suitable for ingestion by riscv-dv coverage collection
    try:
        logger.debug(f"About to do Log processing: {trr.rtl_trace}")
        process_ibex_sim_log(trr.rtl_trace, trr.dir_test/'rtl_trace.csv')
    except (OSError, RuntimeError) as e:
        trr.passed = False
        trr.failure_mode = Failure_Modes.FILE_ERROR
        trr.failure_message = f"[FAILED]: Processing the ibex trace failed: {e}\n"
        return trr

    # Process the test's UVM log.
    # Report a failure if an issue is seen.
    try:
        logger.debug(f"About to do simulation log processing: {trr.rtl_log}")
        uvm_pass, uvm_log_lines, uvm_failure_mode = check_ibex_uvm_log(trr.rtl_log)
    except IOError as e:
        trr.passed = False
        trr.failure_mode = Failure_Modes.FILE_ERROR
        trr.failure_message = f"[FAILED] Could not open simulation log: {e}\n"
        return trr
    if not uvm_pass:
        # Something was found in the logfile that means we mark this test as failed.
        trr.failure_mode = uvm_failure_mode
        if uvm_failure_mode == Failure_Modes.TIMEOUT:
            # If timeout is detected in the log, it means we ended via the wall-clock
            # timeout within the simulator. This is a graceful timeout, keep coverage etc.
            trr.failure_message = "[FAILURE] Simulation ended gracefully due to timeout " \
                                 f"[{trr.timeout_s}s].\n"
        else:
            # Some other error was detected, UVM_FAILED/fatal etc.
            trr.failure_message = f"\n[FAILED]: error seen in '{trr.rtl_log.name}'\n"
        if uvm_log_lines:
            trr.failure_message += \
                "---------------*LOG-EXTRACT*----------------\n" + \
                "\n".join(uvm_log_lines) + "\n" + \
                "--------------------------------------------\n"
        return trr

    # If we got this far then the test has passed.
    trr.passed = True
    return trr


def check_fcov_expectations(md: RegressionMetadata, trr: TestRunResult) -> TestRunResult:
    """Enforce the test's declared-coverage manifest (dv_principles.md §6, triad rule 3).

    A manifest at fcov_expectations/<testname>.fcov.yaml declares bins the test must
    hit; a declared-but-unhit bin (or an unverifiable query) fails the test with the
    distinct FCOV_EXPECTATION mode. No manifest, or COV disabled, is a no-op.
    """
    manifest = md.ibex_dv_root / 'fcov_expectations' / f'{trr.testname}.fcov.yaml'
    if not md.cov or not manifest.is_file():
        return trr
    checker = md.ibex_dv_root.parents[2] / 'ci' / 'check_fcov_expectations.py'
    cp = subprocess.run(
        [sys.executable, str(checker),
         '--manifest', str(manifest),
         '--vdb', str(md.dir_shared_cov / 'test.vdb'),
         '--cm-name', f'test_{trr.testname}_{trr.seed}'],
        capture_output=True, text=True)
    if cp.returncode != 0:
        trr.passed = False
        trr.failure_mode = Failure_Modes.FCOV_EXPECTATION
        trr.failure_message = ("[FAILED]: declared functional-coverage expectation not met\n"
                               + cp.stdout + cp.stderr)
    elif trr.failure_mode == Failure_Modes.FCOV_EXPECTATION:
        # A rerun reloads the previous trr.yaml; clear a stale verdict we now supersede.
        trr.failure_mode = Failure_Modes.NONE
        trr.failure_message = None
    return trr


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir-metadata',
                        type=pathlib.Path, required=True)
    parser.add_argument('--test-dot-seed',
                        type=read_test_dot_seed, required=True)

    args = parser.parse_args()
    tds = args.test_dot_seed

    trr = TestRunResult.construct_from_metadata_dir(args.dir_metadata, f"{tds[0]}.{tds[1]}")

    trr = compare_test_run(trr)
    if trr.passed:
        md = RegressionMetadata.construct_from_metadata_dir(args.dir_metadata)
        trr = check_fcov_expectations(md, trr)
    trr.export(write_yaml=True)

    # Always return 0 (success), even if the test failed. We've successfully
    # generated a comparison log either way and we don't want to stop Make from
    # gathering them all up for us.
    return 0


if __name__ == '__main__':
    sys.exit(_main())
