# Source integration and SharePoint CAS qualification — 11 November 2026

**Status:** reference protocol implemented, locally tested; **real SharePoint/Power Automate commissioning is pending**.

## Integrated source

- Implementation: [SharePoint adapter](../../../../careops-workforce-app/sharepoint/sharepoint_adapter.py)
- Synthetic tests: [transaction and recovery](../../../../careops-workforce-app/sharepoint/tests/test_adapter.py) and [REST action contracts](../../../../careops-workforce-app/sharepoint/tests/test_sharepoint_rest.py)
- [Schema and native flow specification](../../../../careops-workforce-app/sharepoint/FLOW-CONTRACT.md) and [logical SharePoint lists](../../../../careops-workforce-app/sharepoint/sharepoint-schema.json)
- [CI workflow](../../../../../.github/workflows/workforce-jobplan-sharepoint.yml)

**Local verification:** 19 Python stdlib unittest scenarios PASS, including restart/replay, crash after CAS before receipt, prepared-operation replay, stale generation, self-approval, cross-service access rejection, no wildcard ETag, future-effective activation, plan-history continuity, unique review obligation and REST conditional request construction. Branch-aware `coverage` locally measured 87% for the Python adapter (217 statements; 12 statements missed; branch coverage included). Source compilation succeeded. No client/patient data or original work instructions are in the implementation.

**GitHub CI limitation:** At commit `724f7846eebd978b5e55930fc7dc726f54198140`, the two new matrix jobs failed within seconds without receiving runners (empty runner_name, zero steps), and logs were unavailable. Multiple unrelated existing repo workflows exhibited the same pattern. This does **not** establish an application code failure or a passing CI run. Verify organisation runner/usage/configuration and rerun exact-head checks once runners become available; do not bypass branch protection.

## Protocol — exact bounds

One PlanHead list item is the atomic `If-Match` update. Other list writes (Operation, immutable staged Artifact, ReviewObligation) are **not atomically committed together**; the staged operation receipt and previous-operation reconciliation are a recoverable saga. The local SQLite simulator persists across process restarts and models unique indexed Key and ETag CAS semantics; it is **not a SharePoint or identity-security simulation**. `SharePointRestStore` emits real SharePoint REST requests through an injected transport appropriate for standard `Send an HTTP request to SharePoint` flow action. It does not execute Python in Power Automate.

The reference demonstrates only single approver decisions, not Clinical Director → officer consultation → HR/IR validation → delegated approval. `Principal` roles are synthetic; real identity/delegations must be server resolved and enforced by SharePoint ACL and trusted flows. No native site, DLP, records, retention, ETag conflict or app solution import qualified.

## Qualification matrix

| Work item | State | Evidence/gap |
|---|---|---|
| JP-VC01 source integration | **source committed; local test pass; CI blocked** | Python adapter + tests in separate workforce app module, preserving Workforce PBIP source-lock |
| JP-VC02 authenticated permission/industrial eligibility | **not implemented** | only synthetic `Principal` contract and SoD gate |
| JP-VC03 SharePoint CAS/replay protocol | **source-level candidate implemented** | conditional REST mapping + durable local simulator; live tenant qualification outstanding |
| JP-VC04 review/temporal migration | **partial** | unique obligations and future activation, but no full effective-dated rule migration |
| JP-VC05 ACL/history retention/access | **not qualified** | no real SharePoint restricted site / personal data |
| JP-VC06 deployable flows/app/clean import | **not implemented** | no solution ZIP or Power Platform tenant import |
| G2–G5 | **open** | cannot claim production transactionality or safety |

## Next steps

1. Qualify a CHHHS development tenant, sharepoint list unique Key/ETag/limits and service-owned connection identity.
2. Provision restricted list schema and immutable artifact document-library model with appropriate ACLs and records/retention rules.
3. Author solution-aware Power Automate flows implementing the source protocol, tenant-authenticated roles, proper HR/IR multi-gate review, source effective dates and error recovery.
4. Add concurrency/restart/throttling/permission tests in tenant; assess data-scale limits and ability to remove/restore access to historical versions.
5. Package unmanaged development solution, run clean import/reimport and exact-head CI. Only then claim functional native deployment.

**Confidentiality:** only synthetic source and generic instructions have been committed. The supplied individual job plans and CHHHS draft work instruction remain outside Git.
