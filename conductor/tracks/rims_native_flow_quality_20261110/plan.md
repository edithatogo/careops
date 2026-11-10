# RIMS native-flow reliability, file snapshots and optional backend admission

Status: source-side design/qualification in progress; no tenant operations authorised. Owner: existing RIMS source and native owners. Continue existing RIM and RMD-05 tracks without a second scheduled writer.

## Evidence and scope
User's unmanaged RIMS export has 36 flow definitions. A recursive static audit finds five flows exceeding 120 nested actions: DoRA publication collection, Crossref notice collection, Crossref batch qualification, DataCite related-output collection and Sourcearchivecommit. Three flow paths assign source status `Included`; this is not proof of human approval. One weekly-digest test flow references Dataverse (Power Automate premium); it must not be a core runtime requirement. Existing source archive, manifest and complete-checkpoint operations must be reused.

## Phase A — Source graph and refactoring
- [ ] RFQ-01 Reconcile current live export against supplied ZIP (IDs, exact SHA, state, owners and connections). Exit: immutable native/source diff; no flow writes.
- [ ] RFQ-02 Extract all nested actions, retry policies, paging loops, `runAfter` branches, connectors, source/target references and potential premium actions. Exit: 36-flow static risk report with redacted paths.
- [ ] RFQ-03 For each of five large flows, review one minimal reusable boundary (capture, pagination, validation, commit, reporting). Propose solution-aware child flow or equivalent scopes; qualify licence, embedded connections, exact inputs/outputs and backward compatibility before changing. Exit: minimal reviewed before/after graph and rollback.
- [ ] RFQ-04 Resolve `ReviewStatus=Included` semantics in all three source create-item actions and test exclusions from final reporting without rewriting historical human decisions.

## Phase B — File-backed non-premium core
- [ ] RFQ-05 Prepare standard-library typed snapshot builder/validator (rows JSON, schema JSON, manifest, source revision, run ID, row count, hashes); tests reject partial/corrupt/unknown types. Exit: synthetic zero/one/many, nested, null and replay fixture results.
- [ ] RFQ-06 In existing solution-aware collectors, place optional standard SharePoint `Create file` stage **after** last accepted source completeness and archived-readback guard. Write immutable per-run rows.json and schema.json to a controlled library; read back; create final committed manifest/marker only once. Exit: native input/ETag/readback evidence, failure recoveries and unchanged old source archive.
- [ ] RFQ-07 Implement versioned Import-model SharePoint Folder + `Json.Document` consumer, selecting only committed, rights-approved snapshots and explicitly applying schema types. Exit: data count/key/date/decimal parity, semantic refresh and HTML/CSV fallback; source-only M text is not native acceptance.
- [ ] RFQ-08 Benchmark baseline API refresh against JSON snapshots, and optionally local SQLite/Parquet/Arrow derived copies; measure file size, elapsed refresh, peak memory and schema fidelity, do not assume faster performance. Exit: reproducible benchmarks and selected partition policy.

## Phase C — Optional services and licensing
- [ ] RFQ-09 Define core `sharepoint_json` and `local_json` backends, optional `offline_parquet`, `fabric_directlake`, `xmla`, `remote_nlp`, `copilot` adapters. All optional OFF by default; admission needs verified entitlement, capacity, DLP, connection and data release. Exit: explicit capability manifest and negative tests.
- [ ] RFQ-10 Keep mandatory solution free of *all* premium connector actions/refs, even inside disabled `If` branches. Deploy premium capabilities as separately owned optional solution(s)/workers that consume completed immutable snapshots. Core output never depends on optional adapters. Exit: exact package dependencies, core-only installation test and optional enabled/denied tests.
- [ ] RFQ-11 Implement a deployment selector: requested backend + separately qualified availability -> optional adapter; otherwise standard JSON remains authoritative. A Boolean flag is not licence proof; unknown-effect writes must be reconciled before retries. Exit: source and native contract tests.

## Phase D — Platform-specific testing and release
- [ ] RFQ-12 Run `pac solution unpack/pack`, `pac solution check` / Power Apps Solution Checker where environment access is qualified; guard connection references, environment variables and flow state. Exit: solution checker report and source/package round-trip.
- [ ] RFQ-13 Use Flow Checker, manual Test Flow, mocked action static results and controlled replay in an authorised test environment; record run IDs, ETags and recovery. Exit: selected native positive and negative run evidence.
- [ ] RFQ-14 Use maintained Power Platform Playwright samples for any native Lists/Power Apps reviewer UI, never deprecated Power Apps Test Engine; keep test identities and tokens in approved secrets. Exit: UI readback and review-action test.
- [ ] RFQ-15 Integrate source-only tests into CI with read-only permissions and pinned actions. Full milestone includes secret/privacy checks and all existing required checks; no bypass for billing/host failures.
- [ ] RFQ-16 Protected merge, controlled native cutover and independent scheduled RMD-05 monthly observation remain separate gates. No email, production mutation, subscriptions, tenant connection or additional recurrence authorised by this track.

## Native insertion points from the supplied ZIP
- DoRA publication collector: after `Verify_manifest` and `Verify_complete_checkpoint`.
- Crossref notice collector: after `Verify_manifest` and `Save_completion`.
- Sourcearchivecommit: after `Verify_commit_readback` and `Require_archive_persisted`.
- ResearchersExport: after `Verify_manifest`, with restricted privacy profile.
- PublicationsRegisterexport: `Export_Run` boundary, only after equality with live source.
- Testweeklydigest: `Filter_digest_eligible_records` boundary; no unapproved email/Dataverse path.

## Native ALM, not Python-only
Export current solution -> `pac solution unpack` -> edit solution-aware flows in approved maker environment/controlled source with connection references and environment variables -> pack/check -> test import -> run native failures and recovery -> managed downstream release. Python helpers describe and verify file output, but do not substitute for Power Automate file actions or native acceptance.

Official guidance: https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/test-cloud-flows ; https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/solution ; https://learn.microsoft.com/en-us/power-platform/developer/playwright-samples/overview ; https://learn.microsoft.com/en-us/power-query/connectors/json ; https://learn.microsoft.com/en-us/power-query/connectors/parquet

## Source implementation checkpoint — 10 November 2026

The existing PR now includes:
- `portfolio-scripts/rims_platform_capability.py`: external-admission-gated backend selection; absent/denied optional features fall back to `sharepoint_json`; a Boolean flag never qualifies a premium licence.
- `portfolio-scripts/rims_file_snapshot.py`: pure typed JSON rows/JSON Schema/manifest builder with staged hashes, source/run identities and readback refusal. **It does not write to SharePoint or create a native completion marker**.
- `portfolio-scripts/rims_sqlite_cache.py`: optional standard-library local SQLite STRICT materialisation with schema metadata and overwrite refusal; requires a caller-supplied authoritative-commit verifier; does not call Power Automate.
- Fictional tests for capability isolation, types, partial/changed source, readback and cache denial, and a pinned read-only source-only CI workflow `rims-platform-contracts.yml`.
- A separately generated 36-flow risk report from the user's supplied ZIP found five workflows exceeding 120 recursively traversed actions, three explicit Included assignments, one Dataverse connector reference in a test flow, and 33 instances of personal-path text requiring classification. It is not the current live tenant.

Remaining native work is **RFQ-01 through RFQ-04, RFQ-06 through RFQ-08, RFQ-10 through RFQ-13 and RFQ-16**. The source slices for RFQ-05, RFQ-09 and RFQ-14 are partially implemented, but full release/hosted and native acceptance remains false until real tests and exact readback are supplied.

The companion downloadable local source package contains the deeper 36-flow audit, 13 locally passing synthetic tests, native workflow mapping and example typed JSON snapshots. Files committed in this PR are a smaller reusable subset and must be independently qualified on the exact PR head.
