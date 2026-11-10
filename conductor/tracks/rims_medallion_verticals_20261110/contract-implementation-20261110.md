# RIMS contracts and real-data utilisation — implementation & review checkpoint

Date: 10 November 2026. Existing owner: `rims_medallion_verticals_20261110`. Source review in PR #309; no tenant, registered user/staff row, or production report was accessed. Preserve earlier RIM-01–21 and RFQ-01–16 owners.

## High-priority finding

**Contract files previously existed but the runtime function outputs did not match their required properties.** For example, Bronze declared `capture_timestamp` while the historic helper emitted `captured_utc`; Silver declared `typed_attributes` and `field_lineage` while the historic helper emitted `attributes` and `lineage`. Gold and Platinum also differed in grain/row, claims and provenance fields. The older transform is not production-conformant merely because its own tests pass.

The previously downloadable local contract pack is **not byte-equivalent** to the GitHub medallion schemas. Treat the canonical reviewed GitHub branch schemas as controlling; regenerate any release pack from exact approved HEAD and compare hashes. Do not silently use the old ZIP to qualify new semantics.

## Implemented source slices
- `portfolio-scripts/rims_contract_bridge.py` constructs schema-shaped Bronze, Silver, Gold and Platinum products from synthetic permitted payloads. Requires complete pagination for Silver, carries all otherwise unmapped source fields into a retained-only Silver bucket, refuses colliding mappings, keeps Gold publication approval dependent on an independent verifier, and binds every Platinum claim to supplied evidence references. It does not authenticate reviewers or deliver reports.
- `portfolio-scripts/rims_portfolio_metrics.py` computes **descriptive** and privacy-minimised cross-domain metrics: reviewed study-to-output coverage, awarded-funding-to-study linkage, OA within assessed publications, and completed study share. Denominators, unknowns, unverified relationships and no-causal-impact caveats are explicit. A missing verifier produces no trusted outcome denominator.
- `portfolio-scripts/rims_field_coverage.py` distinguishes **field accounted for** from **field analytically utilised**, counts retained-only fields and requires a reason for exclusion. This does not establish full live-source field coverage.
- `portfolio-scripts/rims_assurance.py` no longer treats source-populated `ConfirmedCHHHS` as an approved publication without an independent review verifier. It exposes source-claimed and verified counts separately.
- `portfolio-scripts/rims_contract_gap_audit.py` enumerates the four layer contracts and six domain schemas and reports their actual structural weakness (broadly typed optional fields), native qualification false, and no demonstrated full data exploitation.
- Fictional regression tests accompany each source change. Local equivalent bridge/portfolio tests passed five tests on Python 3.13.5 with JSON Schema Draft 2020-12, against **locally reconstructed current GitHub schema shapes**; exact GitHub-head Python 3.15.1, all 24 domain-layer fixtures, CI and native service qualification remain pending.

## MoSCoW

**Must:** source-qualified schema conformance; original Bronze byte provenance; zero unexplained field loss; separate source assertion/authorised decision; typed domain facts and relationships; source-to-Gold population parity; explicit denominators and uncertainty; output RLS/rights; no premium/Copilot in core; no false claim of native acceptance.

**Should:** 24 layer/domain fixtures with null/multiple/nested/outage/revision cases; typed v2 domain contracts without breaking v1 consumers; retained-archive end-to-end field/consumer lineage; research outcome KPI catalogue; labelled semantic model, dashboard, scorecard and RDL mappings; operational comparison to last good.

**Could:** additional descriptive metrics, process mining, local BM25/NER and entity resolution, optional Parquet/SQLite/Fabric/model adapters based on measured benefit.

**Won't now:** automatically infer CHHHS employment, research impact or causality; turn on new collectors such as Trove; publish sensitive directory information; deploy premium connector/Copilot core or issue reports without approval.

## Atomic executable tasks

| Task | Source-bound instruction | Exact exit | Status |
| --- | --- | --- | --- |
| RIM-CC01 | Freeze exact GitHub contracts and historic ZIP mapping; list schema-name incompatibilities | Two-version compatibility table with SHA and inverse mapping | source partial |
| RIM-CC02 | Validate one synthetic `bronze_record` against current v1 JSON Schema including array-root/null/partial | Draft202012 format checks and rights/provenance receipt | source partial |
| RIM-CC03 | Validate `silver_record` and retained-only nested source fields; reject unmapped collisions | Exact field lineage and no field loss under synthetic tests | source partial |
| RIM-CC04 | Validate `gold_record` including denied/absent/stale reviewer authorisation | Zero unverified published rows, exact source/approved/held counts | source partial |
| RIM-CC05 | Validate `platinum_record` with claim-evidence closure, limitations and release hold | Every claim has cited source evidence; no autonomous action | source partial |
| RIM-CC06 | For each of 6 domains, prepare 0/1/many synthetic records for Bronze/Silver/Gold/Platinum (24 pairs) | Domain-specific type/null/cardinality/temporal negative tests | pending |
| RIM-CC07 | Replace broadly typed domain v1 optional fields using versioned compatible, typed v2 contracts; retain unrecognised source fields in Bronze | Versioned v1→v2 conversion tests and data dictionary | pending |
| RIM-CC08 | Inventory *actual retained* providers, archive SHA/page counts/fields/rights and compare to source schema | Each acquired provider has field accounting with source version and licensing decision | pending private archive |
| RIM-CC09 | Join archive Bronze path to Silver field lineage to Gold model/sourceColumn and per-visual measures | Real field-by-field utilised/retained/excluded matrix, no unsupported percentages | pending native model |
| RIM-CC10 | Implement reviewed entity relationship linking (publication→study, award→study, people→organisation), rejecting inferred employment | Verified links and unverified held counts; no cross-organisation identity leak | source partial |
| RIM-CC11 | Validate descriptive metrics with source changes, missingness, censoring, uncertainty and period | Count/denominator parity and explicit not-causal findings | source partial |
| RIM-CC12 | Add review-queue, Gold reporting and outcome-evidence checks to actual native Lists and Power BI | Source/run/permission readback and controlled negative cases | pending tenant |
| RIM-CC13 | Run actual exact-HEAD focused tests, privacy/secret checks and current required hosted CI | Required GitHub gates genuinely pass; no billing exceptions | pending |
| RIM-CC14 | Run Conductor-review; fix all High/Critical findings and update this task register | Review evidence, fixes, current SHA and next owner | source partial |
| RIM-CC15 | Merge via protected PR, verify main and preserve separate RMD-05 monthly native acceptance | Main readback, working standalone module and no duplicate writer | pending |

## Contract-completeness review

| Contract | Declared | Executable source use | All existing data fields? | Native/business accepted? |
| --- | --- | --- | --- | --- |
| Bronze | Yes | New synthetic bridge | No measured coverage of retained sources | No |
| Silver | Yes | New synthetic bridge | Unknown; retained-only synthetic tested | No |
| Gold | Yes | New synthetic publication bridge | No verified model/source alignment | No |
| Platinum | Yes | New synthetic claims bridge | No validated clinical/economic impact | No |
| Publications | Structural, weak optional types | Partial publication review and metrics | No | No |
| People | Structural, weak optional types | Explicit identity links, no HR inference | No | No |
| Organisations | Structural, weak optional types | ROR source definitions, relationship tests partial | No | No |
| Projects & Studies | Structural, weak optional types | Preliminary study/output measures | No | No |
| Funding | Structural, weak optional types | Preliminary award/study measures | No | No |
| Shared | Structural, weak optional types | Snapshots, provenance and run receipts partial | No | No |

**Do not mark the medallion contracts or any vertical fully implemented** on the basis of these source helpers. Retained archives, actual native Lists and semantic models, authorisation, and business outcome evidence remain separate gating conditions.

## Review findings and immediate fixes

- **High**: Historic medallion runtime output failed strict v1 schema. **Fix**: additive contract-conformant bridge and test; historic interfaces left unchanged to avoid breaking consumers. Full migration still open.
- **High**: Report reconciliation counted unverified source `ConfirmedCHHHS` as approved. **Fix**: require independent verification, retain source-claimed count as separate metric.
- **Medium**: Field coverage `complete` could be mistaken for field utilisation. **Fix**: add actual utilised count and retained-only/excluded breakdown; demand exclusion rationale.
- **Medium**: Platinum could reference evidence absent from the product. **Fix**: claim evidence refs must be declared at product level.
- **High open**: Domain v1 contracts accept many semantically inappropriate primitive types and do not enforce temporal/identity/governance rules. Typed v2 work remains.
- **High open**: Source archive/data use and live four-consumer Power BI parity cannot be proven from the unmanaged flow ZIP or source code.
- **High open**: Hosted CI was previously queued/failed without runnable logs; current exact-HEAD acceptance still required. No branch protection bypass.

Review disposition: **source slices partly qualified; parent Conductor track remains in progress, not archived.**
