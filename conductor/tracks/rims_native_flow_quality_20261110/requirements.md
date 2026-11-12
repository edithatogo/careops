# Requirements and MoSCoW — RIMS native-flow quality

All requirements need the testable evidence below. Statuses mean **source verified**, **native pending**, or **not implemented**; documentation alone is not a pass.

| ID | MoSCoW | Requirement and executable acceptance | Status |
| --- | --- | --- | --- |
| RQ-01 | Must | Inspect every flow and nested branch in exported source with a deterministic SHA-bound manifest; refuse duplicate JSON keys and malformed WDL dependencies. | source implemented |
| RQ-02 | Must | Identify every HTTP, Dataverse, unknown connector and inactive-branch premium candidate; core-only admission fails closed on unqualified flow. | source implemented |
| RQ-03 | Must | Never publish raw personal paths, tenant URLs, connection payloads, identities or secrets in source audit artifacts. | source implemented |
| RQ-04 | Must | Retain existing source archive/readback checks; append one optional, gated typed JSON snapshot path after independently qualified completed source. | native pending |
| RQ-05 | Must | Snapshot has source/run/revision, typed schema and stage/commit markers; incomplete/partial/changed data never promoted; replay is idempotent and reversible. | partial source, native pending |
| RQ-06 | Must | Separate publication source status `Included` from verified human adjudication and issued-report eligibility; preserve historical decisions. | native pending |
| RQ-07 | Must | Power Platform connection references and environment variables are solution-aware; no hard-coded personal endpoint in approved deployable candidate. | native pending |
| RQ-08 | Must | No premium, Copilot or Dataverse action/dependency in mandatory core, including disabled conditions; mandatory core works without optional packages. | source admission, native pending |
| RQ-09 | Must | No automated email or report circulation without explicit human approval of audience, content, attachments and send scope. | control defined, native pending |
| RQ-10 | Must | Full current-head mandatory CI and separate native acceptance before merge/cutover; no bypass of blocked host checks. | pending |
| RQ-11 | Should | Shared, versioned source-to-Silver-to-Gold field lineage with complete source field inventory and explicit exclusions. | partial source |
| RQ-12 | Should | Native Flow Checker, Solution Checker, PAC unpack/pack roundtrip, mocked action output tests, controlled replay and Playwright UI where relevant. | plan only |
| RQ-13 | Should | SharePoint JSON Import and typed CSV/HTML fallback, with source/period count parity and measured refresh performance. | plan only |
| RQ-14 | Should | Redacted run receipts, throttling/backoff and duplicate-retry/failed-source recovery metrics; no extra scheduler. | partial source |
| RQ-15 | Could | Optional local SQLite cache (schema metadata, immutable files, tested) and optional Parquet conversion with benchmark. | SQLite source partial; Parquet pending |
| RQ-16 | Could | Independently deployed Fabric/Direct Lake, XMLA, remote NLP and Copilot add-ons where separately licensed and explicitly approved. | contracts only |
| RQ-17 | Won't now | Activate Trove, NIH, or additional collectors before existing sources are fully leveraged and their fields accounted for. | deferred |
| RQ-18 | Won't now | Bulk rewrite all 36 flows, move approved native resources or replace existing source archive merely to simplify action counts. | excluded |

## Per-flow MoSCoW
**Must:** classify actions/connectors and connection identities; protect source snapshots, typed fields, review decisions, completeness and recovery.  
**Should:** reduce duplicated loops by extracting solution-aware child flows with parity tests; surface meaningful codes and diagnostics.  
**Could:** use optional Parquet or advanced analytic adapters after benchmark and permission checks.  
**Won't now:** native writes, new source acquisition, premium dependency in the core, unapproved delivery.

## Exit checklist for an agent
For each RQ: exact source SHA, linked RFQ task, input evidence, code/model diff, one positive + two negative synthetic tests, native qualification marker where required, reviewer findings and fix receipt, and status. Never mark native as complete from a static source test.
