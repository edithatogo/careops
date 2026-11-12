# Specification — RIMS standard-connector flow admission and file-backed reporting

Status: in progress; source-only implementation and review, native use pending.
Track ID: `rims_native_flow_quality_20261110`. This supplements RIM-01–21, medallion vertical contracts and existing publication owner RMD-05; it is not a second collector, register or scheduler.

## User outcome
An independently deployable RIMS core operates using standards-based typed JSON snapshots, standard Microsoft 365/SharePoint connectors, and audited human decisions. Power BI can consume accepted snapshots without fetching every public API again. Premium/Fabric/Copilot/model adapters are separately deployed and entirely optional; their absence must not prevent collection, review or reporting.

## Observed export baseline (10 November 2026)
- Source: user-provided unmanaged `CHHHSRIMSPlatform_1_0_0_0 (6).zip`; exact input hash recorded in the previous RIMS reconciliation. Do not commit source ZIP or operational identities.
- Thirty-six workflow definitions, 2,749 nested actions, 16 flows containing HTTP actions, six containing Power BI connector references, 33 with personal-path candidates, three source assignments to `Included`.
- Static `runAfter` audit found no missing references or cycles. HTTP actions require separate premium/licence classification: **there is not yet proof that all existing source acquisition works without premium dependencies**.
- Existing source-archive flows already create files, read them back and verify a manifest; preserve those controls instead of layering duplicate writers over them.
- Source may be older than deployment; never infer current tenant flow state from this ZIP.

## Contracts and scope
1. **Flow admission:** a source-only scanner inventories action graph, connectors, HTTP and high-risk use, redacting tenant endpoints. Explicit core admission rejects unknown or premium dependencies, including inactive conditional branches. No automatic mutation.
2. **Snapshot:** source/run/period identity, rights/privacy, typed schema, immutable staging files, readback and terminal marker; incomplete snapshots and unreviewed publication statuses are never committed. Preserve source archive as native authority.
3. **Native delivery:** authorised solution-aware actions/child flows with connection references and environment variables. Use PAC solution unpack/pack/check in an approved environment, Flow Checker, controlled native run/replay and rollback before promotion.
4. **Optional adapters:** only separate optional solution packages/workers may use HTTP, Dataverse, premium Fabric/Direct Lake, XMLA, remote NLP or Copilot. No core connector dependency and no entitlement inferred from a Boolean flag. Optional offline SQLite and Parquet are downstream copies of approved snapshots.
5. **Reporting:** controlled SharePoint folder JSON Import (or offline JSON/SQLite) with deterministic type application, field labels, source/period count parity, non-premium HTML/CSV fallback. No unreviewed automatically included publication.
6. **Security and release:** no private identifiers/records in Git; least privilege, permitted retention and human approval for any sends/issued reports. Do not bypass host CI or change tenant setup to make testing easier.

## Out of scope
Installing premium licensing, invoking tenant writes, replacing authoritative Lists, starting a second source collector or extra recurrence, bypassing existing native holds, sending email, converting current Power BI models without exact readback, asserting final performance improvement from file snapshots.

## Acceptance matrix
- Source: audited 36-flow synthetic and exported ZIP manifests, no raw URLs/identifiers in outputs, deterministic tests and fail-closed core/optional boundary.
- Native: accepted original runtime baseline, supported connection refs/environment variable bindings, actual SharePoint create/readback/commit marker and rollback, same query semantics as original.
- Reporting: semantically identical source populations, types, periods and reconciliation on snapshot vs existing report with no blank or coded values introduced.
- Release: all required current-PR-head checks pass, protected merge; RMD-05 monthly scheduled delivery remains a separate observation. Never infer native success from source tests.

## Existing controlling records
- [Native flow quality plan](plan.md)
- [Medallion and six-vertical contracts](../rims_medallion_verticals_20261110/index.md)
- [Flow source reconciliation](../suite_rims_migration_20261018/export-reconciliation-20261110.md)
- [Standard connector and native ALM guide](../../../docs/rims/native-flow-integration-20261110.md)
- [Source-only storage profile](../../../portfolio/rims/platform/storage-profile.json)
