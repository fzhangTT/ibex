"""gen_prog_const: the constants the per-seed program generators share (one home; dv_principles S5).

CSR addresses follow the RISC-V privileged specification CSR listing (tools/specs, machine-level CSRs, Smepmp mseccfg,
Sdtrig tselect/tdata*, debug dcsr/dpc/dscratch*) and doc/03_reference/cs_registers.rst for the Ibex custom CSRs
(cpuctrlsts 0x7c0, secureseed 0x7c1). Values: mstatus reset (cs_registers.rst: MPIE = 1, MPP = U), misa (RV32IMCB with
X for the draft extensions, cs_registers.rst), mconfigptr 0. The end-of-test codes and the build configuration name are
re-exported from their homes so a generator never re-types them."""
from dv.auto_dv.flow.gen_flow_const import BUILD_CONFIG as CONFIG_NAME  # the one home of the configuration name
from dv.auto_dv.tests.gen_test_lib import TOHOST_FAIL, TOHOST_PASS

CSR = {
    "mstatus": 0x300,
    "misa": 0x301,
    "mie": 0x304,
    "mtvec": 0x305,
    "mcounteren": 0x306,
    "menvcfg": 0x30a,
    "mstatush": 0x310,
    "menvcfgh": 0x31a,
    "mcountinhibit": 0x320,
    "mscratch": 0x340,
    "mepc": 0x341,
    "mcause": 0x342,
    "mtval": 0x343,
    "mip": 0x344,
    "mseccfg": 0x747,
    "mseccfgh": 0x757,
    "tselect": 0x7a0,
    "tdata1": 0x7a1,
    "tdata2": 0x7a2,
    "tdata3": 0x7a3,
    "mcontext": 0x7a8,
    "mscontext": 0x7aa,
    "dcsr": 0x7b0,
    "dpc": 0x7b1,
    "dscratch0": 0x7b2,
    "dscratch1": 0x7b3,
    "cpuctrlsts": 0x7c0,
    "secureseed": 0x7c1,
    "mcycle": 0xb00,
    "minstret": 0xb02,
    "mcycleh": 0xb80,
    "minstreth": 0xb82,
    "cycle": 0xc00,
    "instret": 0xc02,
    "cycleh": 0xc80,
    "instreth": 0xc82,
    "mvendorid": 0xf11,
    "marchid": 0xf12,
    "mimpid": 0xf13,
    "mhartid": 0xf14,
    "mconfigptr": 0xf15,
}
CSR.update({f"pmpcfg{i}": 0x3a0 + i for i in range(4)})
CSR.update({f"pmpaddr{i}": 0x3b0 + i for i in range(16)})

PMPCFG_BASE = 0x3a0        # pmpcfg0..3
PMPADDR_BASE = 0x3b0       # pmpaddr0..15
MHPMCOUNTER_BASE = 0xb00   # mcycle, (0xb01 unused), minstret, mhpmcounter3..31
MHPMCOUNTERH_BASE = 0xb80
HPMCOUNTER_BASE = 0xc00    # cycle, instret, hpmcounter3..31 (user-mode aliases)
MHPMEVENT_BASE = 0x320     # mcountinhibit at 0x320, mhpmevent3..31 at 0x323..0x33f

MSTATUS_RESET = 0x0000_0080
MARCHID_IBEX = 22            # RISC-V marchid registry entry of lowRISC Ibex (gen_feature_list.md Section 4.2)
MISA_VALUE = 0x4090_1104
MCONFIGPTR_VALUE = 0


def pmpcfg(i):
    return PMPCFG_BASE + i


def pmpaddr(i):
    return PMPADDR_BASE + i


def mhpmcounter(n, high=False):
    """mhpmcounter<n> (n >= 3); mcycle / minstret are n = 0 / 2."""
    return (MHPMCOUNTERH_BASE if high else MHPMCOUNTER_BASE) + n


def hpmcounter(n, high=False):
    return HPMCOUNTER_BASE + (0x80 if high else 0) + n


def mhpmevent(n):
    """mhpmevent<n> (n >= 3)."""
    return MHPMEVENT_BASE + n


def csr_hex(name):
    """CSR operand text for the assembler, e.g. 0x300."""
    return f"0x{CSR[name]:03x}"
