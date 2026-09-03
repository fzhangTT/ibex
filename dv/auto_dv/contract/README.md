# dv/auto_dv contract

All generated DV work lands under `dv/auto_dv/**` and nowhere else. Namespace rule: tests,
covergroups, and TB modules carry the `gen_` prefix, and generated covergroups live in their own
namespace — never added into another covergroup. The landing check on the receiving branch
enforces this mechanically: work outside `dv/auto_dv/**`, or without the prefix, does not land.

Standing homes under this tree: review artifacts in `dv/auto_dv/reviews/`, mutation records in
`dv/auto_dv/mutations/`, fcov-expectation manifests in `dv/auto_dv/fcov_expectations/`, evidence
excerpts in `dv/auto_dv/evidence/`.
