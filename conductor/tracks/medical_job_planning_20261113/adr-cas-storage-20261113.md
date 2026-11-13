# ADR MJP-002 — Source-only CAS protocol and storage boundary (candidate)

**Date:** 13 November 2026. **Status:** proposed, source-qualified; **NOT** an adopted CHHHS storage, industrial, identity, native connector or operational decision.

## Problem

The uploaded v0.4.2 prototype contains a four-list SharePoint compare-and-swap reference and 20 logical SharePoint Lists plus one document library. A conditional update of one PlanHead **does not** provide ACID transactions across the other Lists. A lost operation receipt can occur after the head write; a later revision may supersede that head before recovery.

## Interim decision

1. Keep the new CareOps Medical Job Planning module standalone. Retain ordinary source-level candidate logic independent of live SharePoint, Dataverse, PPG, Approve and Workforce BI.
2. Define the **single PlanHead generation update** as the linearisation point. Require an **exact observed ETag** (never `If-Match: *`) in the later native implementation. Preserve staged immutable artifacts, operations and issued history independently.
3. Use `cas_contract.py` for source-only fault-injection, conflict and replay tests. It is an **in-memory model**, explicitly not evidence of SharePoint transactionality, file durability, physical permissions, HTTP 412/429 behaviour or genuine authenticated identity.
4. Version 1 canonical payload: JSON object; recursively restricted to NFC Unicode strings, booleans, nulls, safe 53-bit integers, nested dicts/lists, depth <=32 and maximum 1 MiB. Disallow binary values, floats (including NaN/Infinity), implicit numeric coercion, non-string keys and non-normalised text. Canonicalisation uses UTF-8, sorted keys and compact separators; this is a project-specific contract, **not a claim of RFC 8785/JCS**. Hours/financial quantities are explicit decimal strings handled by separate rule validation.
5. Stage operation identity including plan, version, actor-evidence reference, expected generation and payload SHA256. Exact operation ID replay returns the same receipt; a key rebound to another actor/body/plan is refused.
6. Reconcile a crash after prepare as *not committed*, never automatically committing it. Reconcile a post-CAS receipt loss against immutable **head-version history**, not only the newest PlanHead; if a competing head committed, quarantine the orphan. In native SharePoint, actually verify whether version history and operation IDs survive policy, retention, copy, recovery and delegated ACLs.
7. No candidate can become an approved, issued or active employment plan through this protocol. Human authority requires the separately approved application, delegated role resolver and employment rule pack.

## Logical prototype storage inventory

The source's `config/data-model.json` defines the following 20 proposed Lists and one Library. This is a **source inventory**, not a provisioning instruction.

| Security cohort (prototype) | Logical collections | Review need |
|---|---|---|
| Practitioner-restricted | JP_PlanHeads; JP_Drafts; JP_PlanVersions; JP_PlanSessions; JP_AnnualisedCommitments; JP_CSTLedger; JP_ActivityObservations; JP_ApprovedPlanRecords (Library) | Practitioner rights, revisions, historic access and privacy; actual activity observations remain externally sourced/not inferred |
| Service-approver-restricted | JP_ReviewCases; JP_ReviewTasks; JP_Consultations; JP_Decisions; JP_ReviewObligations; JP_ServiceRequirements | Current service-scoped delegations, no-self-approval, consultation/dispute records, case segregation |
| Admin-restricted | JP_RoleDelegations; JP_ReviewPolicies; JP_IndustrialRules; JP_ActivityTaxonomy; JP_Operations; JP_Artifacts; JP_Notifications | Industrial rule ownership, provider authentication, service connections, records retention, technical recovery; notification sending Off by default |

**Unresolved:** 20 Lists might not be the minimum safe physical layout. Do not provision them wholesale. A physical model requires documented key uniqueness, internal columns, cross-list join cardinality, sensitivity, volume, index/pagination and SharePoint unique permission-scope growth; test >5,000 synthetic records, direct URL access and permission revocation. Where item-level unique scopes or multi-list compensation are not maintainable, evaluate site/library partitioning or an independently qualified Dataverse provider; no security downgrade to retain a non-premium label.

## Native acceptance and contracts

- Provider returns actual qualified SharePoint GET item ETag (not guessed field/version); exact `If-Match` failed writes return a clearly distinguished 412.
- POST/create uniqueness, immutable artifact content, versioned operation receipt and bounded 429 `Retry-After` retry must be reproducible across worker restart/parallelism. A failed 412 requires new review/rebase, not blind retry.
- Actual run-only Power Automate connection owner, signed-in invoker, item permissions and delegated decision principal must be reconciled server-side; `actor_evidence_ref` in the source protocol is **not authentication**.
- Publish planned versus actually observed CST in separate records and deny raw practitioner data to Workforce/Process/Costing exports without independent approval.
- No real staff records, hidden tenant settings, mass import, secret, operational export, email send or production write from this ADR.

## Evidence and outstanding acceptance

**Synthetic RED→GREEN tests:** 19 local deterministic CAS tests (plus four static storage-inventory tests), including a seeded 35-operation crash/retry schedule, including replay after a second head commit. A failing regression proved that latest-head-only reconciliation loses receipt history; version-history recovery now passes. Current-head GitHub CI and merged-main readback are separately required.

**Remaining MJP-W1/W2:** accepted canonical plan/session schemas; physical SharePoint/Dataverse comparison; production-grade durable storage; strict authenticated delegation; records and retention; property-based and mutation testing; source v0.4.2 rights/provenance reconciliation; actual native clean install, recovery, accessibility and privacy acceptance. Source logic is not operational industrial compliance evidence.
