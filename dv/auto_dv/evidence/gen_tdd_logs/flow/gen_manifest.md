# Retained logs of the Runtime flow (owner: runtime)

Each row is a byte copy of the work-tree artifact in the source column (md5 of the copy, equal to the source at copy time); the
work-tree paths under dv/auto_dv/work/runtime/ are gitignored. gen_gate_rule_red.log is the TDD red of the build-input gate
(dv/auto_dv/docs/gen_build_input_gate_rule.md): both flow self-tests run with the gate cases in place and no implementation, the
NameError (gen_flow_util, classify_delta) and the TypeError (gen_serve_requests, case 12) they died with, and rc=1 each.

| evidence path | source | bytes | md5 |
|---|---|---|---|
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_gate_rule_red.log | dv/auto_dv/work/runtime/gate_rule_red.log | 926 | 78b72aae6509d2776a43c9314808b01b |
