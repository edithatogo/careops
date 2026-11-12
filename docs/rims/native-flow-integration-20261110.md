# Native RIMS Power Automate and Power BI implementation handoff

Status: design/source contract, **not deployed**. Refer to [16-step Conductor plan](../../conductor/tracks/rims_native_flow_quality_20261110/plan.md).

## Standard, non-premium file export

Use the *existing* source-complete and manifest-verified flow as the authoritative starting point. Create a second **derived** typed snapshot using solution-aware built-in operations and the **standard SharePoint connector**:

1. In the solution, add an optional after-commit scope (or source-qualified child flow) with inputs SourceID, RunID, SourceRevision, SchemaRevision, RowCount, JSON rows and classification. Do not introduce additional schedules, alternate status authority or unapproved sends.
2. Write uniquely named immutable `rows.json` and `schema.json` files into a controlled SharePoint document library. JSON Schema records nullable fields, field types, timestamps, exact-decimal conventions, nested structures and versions.
3. Read back both files through the existing connection reference; check source/run IDs, version, expected count, ETags and byte lengths. Hash with a separately qualified supported implementation where available; do not invent a native SHA256 expression.
4. Only after completed source validation and successful independent readback write a committed-manifest marker. Failed/partial snapshots remain staged and invisible to consumers. Unknown-effect write => read back before retry.
5. Power BI Import reads only **accepted committed snapshots** with SharePoint Folder + `Json.Document` and applies explicit types. Continue providing non-premium HTML/CSV. Validate counts, keys, freshness and durations against existing source/API model.

### Where to change existing flow graphs

- DoRA publications: preserve `Verify_manifest` / `Verify_complete_checkpoint`; snapshot after those guards.
- Crossref notices: preserve `Verify_manifest` / `Save_completion`.
- Sourcearchivecommit: preserve `Verify_commit_readback` / `Require_archive_persisted`.
- ResearchersExport: preserve `Verify_manifest`; retain restrictive person-data classification, no HR publication.
- PublicationsRegisterexport: use `Export_Run` boundary only after period/parity checks.
- Weekly digest: test output after `Filter_digest_eligible_records`, keep mail and Dataverse optional.

## File formats

**Default:** JSON plus JSON Schema plus committed manifest. The schema retains types and timestamps/decimal semantics; raw JSON is not enough for precision, dates and nullability. CSV plus a schema sidecar is acceptable as a secondary compatibility export. For fast offline point/range queries use independently built **SQLite** (define types explicitly). For analytical scans produce **Parquet** or Arrow IPC/Feather via an optional *offline* converter from committed snapshots. Native cloud flows do not supply a standard Parquet writer. Microsoft's Power Query Parquet connector primarily supports local filesystem, Azure Blob and ADLS Gen2; SharePoint binary buffering may be size-limited and should not be the mandatory core.

## Why not an `IF premium THEN` cloud flow?

Having a premium connector action inside a cloud flow can make the **flow** premium even if the action sits under an inactive branch. The base solution therefore has **zero premium connector references**. Do not wrap Fabric, Dataverse, remote model or Copilot actions inside a core flow. Use **physically separate optional solutions/workers**, each enabled through an approved environment profile. They consume already committed and rights-approved records; the core remains functional if the add-on is absent. An environment variable or local flag is a request, not a verified entitlement. Source-side resolver: `portfolio-scripts/rims_platform_capability.py`.

## Power Platform ALM acceptance

- Export current native solution and record exact component GUID/hash/status/owners. `pac solution unpack`, review diff, `pac solution pack`; use qualified `pac solution check` / Power Apps Solution Checker against the candidate where access permits.
- Rebind solution-aware **connection references** and **environment variables** in the approved test environment; enable/disable one component at a time and validate saved values (changes may require flow re-save/re-activation).
- Test with designer **Flow Checker**, **Test Flow**, static action mock outputs and controlled replay; assert repeat deliveries, null/partial pages, stale ETags, connector 429/5xx, permissions, empty batches, last-good retention and zero unapproved sends.
- For native Power Apps/Lists UI, use Microsoft's **Power Platform Playwright samples** in a gated, credentials-protected pipeline. **Power Apps Test Engine was deprecated April 2026**. Playwright UI tests are not a headless cloud-flow engine substitute.
- Source CI: stdlib tests and static connector/definition checks, plus existing secret/privacy guards. Host-required workflows must actually pass; source checks are not native deployment qualification.
- Keep native release/rollback/observation (including RMD-05 scheduled delivery) separate from local synthetic checks.

## Official documentation

- https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/solution
- https://learn.microsoft.com/en-us/power-platform/developer/playwright-samples/overview
- https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/test-cloud-flows
- https://learn.microsoft.com/en-us/power-platform/important-changes-coming
- https://learn.microsoft.com/en-us/power-apps/maker/data-platform/environmentvariables-power-automate
- https://learn.microsoft.com/en-us/power-query/connectors/json
- https://learn.microsoft.com/en-us/power-query/connectors/parquet
