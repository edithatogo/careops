# N09 specification

Make interoperability optional and explicit, not hidden cross-module coupling.
Each core must have a supported standalone business scenario; each adapter owns
version negotiation, minimum data, identity, delivery and reconciliation.

Owner: integration architect and each module maintainer. Do not centralise raw
case/incident/financial records to simplify integration. Acceptance: per-module
and per-enabled-adapter install/upgrade/outage/retirement results. Optional
analytics or safety interfaces must not delay an otherwise accepted core release.
