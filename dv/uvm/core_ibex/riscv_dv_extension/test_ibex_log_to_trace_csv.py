#!/usr/bin/env python3
# Copyright lowRISC contributors.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0
"""Unit tests for check_ibex_uvm_log's pass/fail log classifier.

Run (from a venv with cocotb/pathlib3x installed, e.g. `source ci/env.sh`
first, from anywhere):

    python3 -m unittest dv/uvm/core_ibex/riscv_dv_extension/test_ibex_log_to_trace_csv.py
"""

import os
import sys
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS_DIR = os.path.join(os.path.dirname(_HERE), 'scripts')
sys.path.insert(0, _HERE)
sys.path.insert(0, _SCRIPTS_DIR)

from ibex_log_to_trace_csv import check_ibex_uvm_log  # noqa: E402
from test_run_result import Failure_Modes  # noqa: E402


def _check(lines):
    """Write `lines` to a temp file and run check_ibex_uvm_log on it."""
    with tempfile.NamedTemporaryFile('w', suffix='.log', delete=False) as f:
        f.write('\n'.join(lines) + '\n')
        path = f.name
    try:
        return check_ibex_uvm_log(path)
    finally:
        os.remove(path)


class TestCheckIbexUvmLog(unittest.TestCase):

    def test_cocotb_benign_banner_is_not_a_failure(self):
        # Regression case: cocotb's own startup banner mentions
        # "AssertionError" in prose; must not be flagged as an error.
        passed, log_out, mode = _check([
            '0.00ns INFO     cocotb.regression   pytest not found, '
            'install it to enable better AssertionError messages',
            '--- RISC-V UVM TEST PASSED ---',
        ])
        self.assertTrue(passed)
        self.assertEqual(log_out, [])
        self.assertEqual(mode, Failure_Modes.NONE)

    def test_python_module_not_found_is_a_failure(self):
        passed, _, mode = _check([
            "ModuleNotFoundError: No module named 'dv.cocotb.does_not_exist'",
        ])
        self.assertFalse(passed)
        self.assertEqual(mode, Failure_Modes.LOG_ERROR)

    def test_vcs_error_dash_bracket_is_a_failure(self):
        # docs/dv/evidence/ws1-cov-summary.txt: a real VCS failure format
        # with no trailing colon -- must still be caught.
        passed, _, mode = _check([
            'Error-[FCIBH] Illegal bin hit',
        ])
        self.assertFalse(passed)
        self.assertEqual(mode, Failure_Modes.LOG_ERROR)

    def test_uvm_error_is_a_failure(self):
        passed, _, mode = _check([
            'UVM_ERROR some/path.sv(10) @ 0: reporter [ID] something bad',
        ])
        self.assertFalse(passed)
        self.assertEqual(mode, Failure_Modes.LOG_ERROR)

    def test_clean_pass_is_a_pass(self):
        passed, log_out, mode = _check([
            'UVM_INFO some/path.sv(10) @ 0: reporter [ID] all good',
            '--- RISC-V UVM TEST PASSED ---',
        ])
        self.assertTrue(passed)
        self.assertEqual(log_out, [])
        self.assertEqual(mode, Failure_Modes.NONE)


if __name__ == '__main__':
    unittest.main()
