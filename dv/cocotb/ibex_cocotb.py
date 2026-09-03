"""cocotb entry module for ibex TB integration.

This module is referenced via MODULE=dv.cocotb.ibex_cocotb in the flow.
Test selection: currently imports test_hello directly (future: COCOTB_MODULE selection per test).
"""

# Import the test directly; this makes it available to cocotb's test discovery.
from dv.cocotb.tests.test_hello import test_hello  # noqa: F401
