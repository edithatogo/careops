# Reporting requirements — MoSCoW

| ID | Priority | Requirement / verification |
|---|---|---|
| GRA-01 | Must | A single versioned metric dictionary supplies definitions, grain, numerators, denominators, status logic, filters, timezone and missing-data rules for semantic model, PBIR dashboard and RDL report; contract mismatch blocks release. |
| GRA-02 | Must | GovernanceBody, Forum, MeetingSeries, Occurrence, ProfileRevision, MinutesRevision, Decision, Action, EvidenceRevision, OutcomeReview and ReadSnapshot identities are stable, source-qualified and independently versioned. |
| GRA-03 | Must | Explicit grains and cardinalities prevent double-counting due to agenda/paper/decision/action many-to-many relationships; no many-to-many convenience joins without reviewed bridges. |
| GRA-04 | Must | Distinguish discussion, proposed recommendation, adopted decision, commissioned action, reported completion, verified implementation and formally accepted resolution. Planner completion never implies case/matter closure. |
| GRA-05 | Must | Preserve conditions, dissent, amendments, delegation authority, source versions, exceptions, supersession and reopenings without inferred roles, dates or approvals. |
| GRA-06 | Must | Cross-forum comparisons use forum+occurrence+record source-qualified keys; a single authoritative decision/action owner, with read-only reporting projections. |
| GRA-07 | Must | Core operation requires no Power BI, Fabric, Copilot, AI Builder, Dataverse or Premium connector; reporting optional and separately licensed. |
| GRA-08 | Must | Standard SharePoint adapter and optional Dataverse adapter map to the same canonical contract, with published mappings, supported types, pagination/completeness proofs, field-version/ETag identity and reproducible refresh receipts. |
| GRA-09 | Must | Missing/unqualified source coverage, delayed extracts and access-denied records never silently contribute to complete denominators or imply zero activity. Report completeness visibly qualified at each scope. |
| GRA-10 | Must | Role/body/record classification enforced before extraction and within report access; RLS is not a substitute for source permissions. RDL exports must enforce the same effective audience and avoid leaking restricted record-level content or inferable small counts. |
| GRA-11 | Must | Dashboard and RDL consume the shared semantic model/measure definitions, with source-to-measure traceability, parity tests and no separately reimplemented KPI logic. |
| GRA-12 | Must | RDL supports forum, period, record status and report-as-of filters, versioned issue metadata, provenance appendix, unresolved/overdue actions, decisions/conditions, evidence and reviewed outcomes. Unapproved minutes are not publishable via report. |
| GRA-13 | Must | CI validates TMDL/DAX/schema and PBIR/RDL structure, KPI tests on fictional multi-forum fixtures, security/adversarial cases, model/report compatibility and exact-head inventory; distinguish source success from hosted and native release. |
| GRA-14 | Must | Model results do not assert clinical effectiveness or causal benefit from completion/status alone; evaluation requires prespecified indicators, baseline, timeframe and attributable evidence. |
| GRA-15 | Should | Cover governance configuration, scheduling, quorum, attendance, agenda/paper readiness, minutes approval, decision latency, actions, review/reopenings, provenance, outcomes, workload, exception/recovery and connector health. |
| GRA-16 | Should | Role-focused dashboard views for secretariat, chair, executive, action owner and auditor with cross-forum comparisons, selectable grain, time trends, source-readiness labels and accessible drill-through. |
| GRA-17 | Should | Paginated committee and portfolio packs render with controlled headers/footers, print/page-break tests, accurate as-of semantics, evidence links and no orphaned detail records. |
| GRA-18 | Should | Model supporting dimensions include date/timezone, body, forum, occurrence, owner/role, status, source system, report audience, policy/ToR edition and provenance/state history. |
| GRA-19 | Should | Distinguish human effort saved from work shifted downstream; capture minutes correction time, secretariat effort, duplicate entry, delay/rework and decision-to-outcome review latency. |
| GRA-20 | Should | Optional offline snapshots are immutable, versioned, checksum-verified, source-qualified and read-only; use files/CSV or approved efficient formats within held entitlements and sensitivity rules. |
| GRA-21 | Could | OCEL 2.0 read-only event export and process-mining analyses of handoffs, rework and waiting, limited to minimum-necessary approved data. |
| GRA-22 | Could | Optional locally qualified AI-derived proposals measured against a deterministic/manual baseline, never a condition for reporting or a record of authority. |
| GRA-23 | Could | Optional Dataverse/Fabric enterprise enrichment when licensed and independently qualified; maintain core parity and separate source authority. |
| GRA-24 | Won't (core) | Automatic governance decisions, unreviewed minute publication, arbitrary transcript ingestion, premium-first reporting, unrestricted personal data exports, per-forum duplicate semantic models or unvalidated inferred outcomes. |

## Explicit acceptance cases

1. Two forums have the same local action ID: no collision, and each appears exactly once within its own scope.
2. An action reported complete but not reviewed remains **unresolved**; Planner completed status cannot change it.
3. A conditional decision with dissent is superseded: maintain historical detail and link its successor without rewriting historical counts.
4. An incomplete paginated read, missing ETag, denied source or stale snapshot produces *unverified/not available*, never a zero activity count.
5. Many actions link one decision and one action appears across meetings: distinct business identities count once at the correct grain.
6. A restricted paper exists in a forum: non-authorised audiences do not see its details or a revealing low-count aggregate; RDL export matches dashboard scope.
7. Report-as-of date preceding a later correction renders only the earlier historically effective state and its recorded evidence.
8. No outcome observation exists: report *not evaluated*, never *no benefit* or *successful*.
9. CSV/SharePoint and Dataverse adapters over equivalent fictional source states yield measure parity, subject to declared feature/coverage differences.
10. Report and semantic model can be built/tested offline without real tenant connections and with no premium connector calls.
