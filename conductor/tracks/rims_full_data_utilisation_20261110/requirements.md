# Maximal retained-data utilisation — MoSCoW

| ID | Priority | Requirement | Acceptance |
| --- | --- | --- | --- |
| MX-01 | Must | Inventory all 17 currently catalogued sources and source-qualified accepted/archive scope | Every source classified as historically accepted, incomplete, unverified, or deferred; no claim of current parity |
| MX-02 | Must | Reuse original accepted raw bytes, typed source chunks and provider-specific Field evidence | Independently pinned source receipts, not a new acquisition |
| MX-03 | Must | Profile **all observed nested paths** and record missing/null/empty/type counts | Exact source counts with 0/1/many synthetic tests; no raw record output |
| MX-04 | Must | Retain rights-permitted field values in Bronze/Silver, and refuse unexplained field drops | All observed paths classified mapped / retained-only / excluded-with-reason / unassessed |
| MX-05 | Must | Verify each claimed downstream consumer against exact semantic/visual/RDL/scorecard identity and version | Source mapping claims not marked native-verified without model readback |
| MX-06 | Must | Preserve publication attribution, effective-dated affiliations and human-reviewed award/study relationships | No source claim silently becomes employee/award/CHHHS approved |
| MX-07 | Must | Keep source/population denominators, unknowns and difference between missing vs negative | All metrics show denominator and unknown bucket; avoid sum of source-specific citation counts |
| MX-08 | Must | Protect privacy/rights and no premium/Copilot mandatory core | No private record values in Git; standard JSON/SharePoint/HTML core |
| MX-09 | Must | Reuse existing 23 Power BI indicators and accepted 1,344 record output, preventing regressions | Native key/date/measure/visual/scorecard/paginated parity |
| MX-10 | Must | No new source until all retained-source coverage gaps classified | Trove and future sources remain roadmap-only |
| MX-11 | Should | Provide source-by-source field quality, nullability and schema-drift reports | Versioned profile with revision, replay and expected path deltas |
| MX-12 | Should | Add source-qualified research products for texts, grants, authorship, collaborations, studies and organisations | Evidence-backed measures and approval-gated link outputs |
| MX-13 | Should | Join existing source representations to medallion and Power BI without re-acquisition | Byte digests, source→Silver→Gold→consumer lineage matched |
| MX-14 | Should | Provide a single field-coverage and unused-data dashboard | Domain/source rollup of captured, mapped, retained, excluded and unassessed |
| MX-15 | Could | Local BM25/NER, topic classification, offline SQLite/Parquet and graphs | Comparative evaluation and no premium requirement |
| MX-16 | Won't now | Treat all fields as equally useful, copy all to one flat dashboard or invent research impact | Deliberately excluded |
| MX-17 | Won't now | Rebuild existing accepted native 23-metric reporting or create another source writer | Preserve owner and accepted scope |

## Full-value source products — additional MoSCoW acceptance

| ID | MoSCoW | Requirement | Executable acceptance |
| --- | --- | --- | --- |
| MX-18 | Must | Preserve every retained permitted nested JSON attribute, scalar/null, array index and original-source byte fingerprint | `test_rims_json_occurrences.py` passes source-sha, duplicate, scalar/null/empty and 25-index roundtrip tests |
| MX-19 | Must | Produce typed domain candidates only using independently reviewed source-qualified field maps | `test_rims_source_products.py` refuses wrong provider, invalid DOI, duplicated targets and repeated scalar cardinality |
| MX-20 | Must | Reuse complete accepted private batches and receipts without creating alternative collectors | `test_rims_batch_products.py` refuses incomplete source, orphan, duplicated, wrong SHA/base64 and never authorises report release |
| MX-21 | Must | Keep 17-source registry exhaustive and refuse new unqualified source maps | `test_rims_existing_source_maps.py` covers all 17 and requires native-unverified candidate status |
| MX-22 | Must | Preserve the accepted 23-indicator Power BI reporting baseline and compare actual native model fields before any remapping | Archived 51 Publication/32 GrantsRegistry model columns recorded; live visuals, scorecard and RDL remain pending |
| MX-23 | Should | Produce a usable non-premium stakeholder view of source-field accounting | `test_rims_coverage_report.py` validates totals, escaping, missing denominators and never claims actual analytical utilisation |
| MX-24 | Should | Account for fields retained-but-unmapped, separately from the fields consumed by a verified Gold business product | All source semantic paths preserved in private products; actual source-to-Gold mapping pending private/native receipt |
| MX-25 | Must | Apply rights, privacy, exact monetary precision, access and downstream release controls | Original byte authority retained; no floating-point award valuation; explicit human approval, private rights and native gates |
