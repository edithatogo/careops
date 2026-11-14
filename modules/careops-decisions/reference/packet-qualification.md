# Standalone packet qualification and authority boundary

Status: synthetic source reference only. This increment does not alter the
existing Approve packet contract, the generic meeting-packet identity rules,
Clinical Hub records, or any native object.

`reference/packet_qualification.py` composes the existing
`reference.governance_packet.validate_packet` contract with exact source-byte
SHA-256 and contract-version checks, then evaluates one host-resolved authority
snapshot. The packet's agenda, minutes, decision and action identity semantics
remain owned by the existing validator; this module does not create another
packet model or authority register.

Only the exact `qualified` authority state, exact mapping version, non-empty
authority reference, well-formed source digest and current half-open effective
period can pass. Missing, unsupported, ambiguous-by-state, mismatched,
unverifiable, future and expired evidence remains held. In particular, strings
such as `approved`, `permitted` or `active` are not aliases for
`qualified`. The source digest is checked against the supplied snapshot bytes; it does not
authenticate the publisher or prove that the host resolved the snapshot from a
protected authoritative source.

The qualification is deliberately standalone: optional CareOps Process is not
an input and its absence does not block packet qualification. If a Process
projection is later selected, it remains a separate optional consumer and
cannot supply or upgrade authority evidence.

A qualified result means only that these synthetic source-contract predicates
passed. It does not make a recommendation, delegated decision, approval,
register update, release-to-practise determination, native permission or
deployment. Human recommendation and delegated decision remain separate acts;
the deployment-defined authoritative register and its owner remain unchanged.

Run the focused synthetic tests from the module root using the repository's
exact Python 3.15.1 interpreter:

```sh
"$REPO_PYTHON" -m unittest discover -s tests/reference -p test_packet_qualification.py -v
```

No private records, authority mappings, practitioner data, credentials,
tenant bindings, network calls, writes, messages or Process runtime are used.
