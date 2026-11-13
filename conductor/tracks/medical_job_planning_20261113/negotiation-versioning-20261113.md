# Medical Job Planning — W1 immutable version and negotiation source slice

**Status (13 November 2026): source candidate only; not industrial, native or operational acceptance.** Built on the separately merged domain and archive verification slice (PR #323). Parent Conductor W0 and full W1 remain open.

## Bounded delivered scope

- `modules/careops-medical-job-planning/negotiation.py`: append-only **candidate** negotiation transcript with source-qualified plan/version keys, immutable submitted SHA-256, explicit expected generation, stable operation-id/digest replay, counterproposal, documented disagreement, escalation and return. Transition grammar deliberately **ends at** `authority_pending`, not approved/issued/active.
- `modules/careops-medical-job-planning/plan_records.py`: source-qualified `PlanVersion` reference with external employment/position/service/policy links, immutable submitted hash, half-open effective interval, UTC issued time and decision *evidence reference*. Read-only historical as-of projection reports incomplete upstream source as `unverified_incomplete_source`; overlapping issued intervals fail closed. `candidate_issued` is not an authority assertion.
- Dedicated deterministic synthetic test suites in `tests/test_mjp_negotiation.py` and `tests/test_mjp_plan_records.py`, wired into existing Python 3.15.1 module CI. Tests cover 412-analogue stale generation, conflicting operation replay, disagreements/counterproposals, rejected unverified authorisation transitions, interval boundaries, future issue dates and incomplete source.

## Security and authority boundary

A role reference, evidence key, decision label, actor identifier or a `source_read_complete` argument cannot authenticate a person or prove an authorised human determination. No native identity/SharePoint permissions are implemented. The native owner must verify source-read completeness, role/delegation, no-self-approval, exact plan hash, policy edition, access to historical documents and authoritative decision before any actual plan approval or issuance. No live personnel or tenant data is in this slice.

## Exit evidence and remaining tasks

Local deterministic tests passed before GitHub submission (9 negotiation, 8 plan-version tests); current-head GitHub Actions and merged-main readback are separately required. This is **partial MJP-101/102/106/107**, not completed G1. Next: applicable industrial-policy adoption, physical SharePoint/Dataverse security ADR, real CAS/ETag saga, consulted/conditional-agreement evidence requirements, full original ZIP admission, and native solution-aware app/flows. Optional Power BI/Costing/Process/Sim adapters remain separately qualified.

No operational action, email, entitlement grant, or CHHHS approval is authorised by this code.
