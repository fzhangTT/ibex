"""ctypes + DPI bridge for triggering named SV uvm_events from Python.

Hand-written, minimal version of the quasar `qsr_tb_dpi.py` generated-file pattern
(ctypes.CDLL(None, RTLD_GLOBAL) + svSetScope via svGetScopeFromName) sized for the one DPI export
this milestone needs: `export "DPI-C" task cocotb_trigger_uvm_event(string ev_name)`, declared
inside core_ibex_tb_top's own module body (see core_ibex_cocotb_dpi.svh) — hence the scope name
below matches that module's instance path exactly, with no child scope suffix.
"""

import ctypes

_DPI_SCOPE_NAME = b"core_ibex_tb_top"

# Load the simulator process's own symbol table: it already contains simv's DPI/VPI runtime
# (svGetScopeFromName/svSetScope) and the generated C stub for the SV-exported task.
ctypes.CDLL(None, mode=ctypes.RTLD_GLOBAL)
_lib = ctypes.CDLL(None)

_lib.svGetScopeFromName.argtypes = [ctypes.c_char_p]
_lib.svGetScopeFromName.restype = ctypes.c_void_p

_lib.svSetScope.argtypes = [ctypes.c_void_p]
_lib.svSetScope.restype = ctypes.c_void_p

_lib.cocotb_trigger_uvm_event.argtypes = [ctypes.c_char_p]
_lib.cocotb_trigger_uvm_event.restype = None


def trigger(ev_name: str) -> None:
    """Trigger the named global uvm_event (uvm_event_pool::get_global(ev_name).trigger())."""
    scope = _lib.svGetScopeFromName(_DPI_SCOPE_NAME)
    if not scope:
        # Plain ASCII only: cocotb's failure-logging path uses an ASCII-only stream encoder, and a
        # non-ASCII character here would crash that log call instead of reporting the real error.
        raise RuntimeError(
            f"svGetScopeFromName({_DPI_SCOPE_NAME!r}) returned NULL; DPI scope not found"
        )
    _lib.svSetScope(scope)
    _lib.cocotb_trigger_uvm_event(ev_name.encode("utf-8"))
