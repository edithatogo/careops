# CHHHS research bibliography — source-aware evidence and remaining implementation

Observed 12 November 2026. **Public data discovery and provisional analyses; no independently audited whole-of-HHS publication census or live Searchright MCP execution.**

## Source snapshots on PR #319

| Product | Records | Status |
| --- | ---: | --- |
| OpenAlex Cairns Hospital historical works | 2,058 | Complete paginated institution retrieval for queried ID, not whole HHS |
| OpenAlex Cairns Base Hospital raw affiliations | 950 | Complete queried pages; highly overlapping |
| OpenAlex exact HHS organisational name | 365 | Complete queried pages |
| OpenAlex selected district facilities | 190 | Complete selected phrase-search pages; not all official facilities |
| Deduplicated OpenAlex discovery union | **2,280** | Work-ID-deduplicated candidate set; includes false positives |
| Historical PubMed affiliation identifiers | **1,270** | Complete for three bounded query families; not a whole-HHS census |
| PubMed ESummary metadata | **1,270** | Records retrieved; source authority remains independent |
| OpenAlex directed reference edges | **2,156** | From 2,058 Cairns Hospital citing works; referenced targets in 2,280-work candidate union |

## Private registry reconciliation (aggregate only)

Exact DOI/PMID comparison of the user-supplied private `Publication Registry.csv` (1,662 rows, 1,359 canonical keys, 1,276 source Included): 1,213 candidate works matched Included records; 47 matched Needs Review; one matched Excluded; 1,019 OpenAlex works had no exact identifier match. This is an *identifier reconciliation*, not a new-publication acceptance decision. The private CSV, record-level adjudication and individual registry identifiers are **not committed**. See [aggregate reconciliation](../../portfolio/rims/public-sources/rims-openalex-reconciliation-20261112/aggregate.json).

The 1,213 uniquely matched Included works have an OpenAlex citation median 7, arithmetic mean 17.90, and 173 have zero observed citations, all at one provider snapshot. The internal citation graph contains 1,142 directed edges with both endpoints source-Included; note that only the Cairns Hospital indexed citing side has been collected. These measures are neither age/field normalised nor independently verified HHS impact.

## Data quality and methodological caveats

- Known false positives: search for Mareeba Hospital returned 1925 and 1926 Adelaide-based Mareeba Babies' Hospital papers. Do not call these earliest CHHHS research.
- Historical institutional transition: Cairns Base Hospital renamed Cairns Hospital on 16 July 2013; HHS as a statutory body commenced 1 July 2012. Do not retroactively label earlier institutional work as formally produced by this legal HHS.
- Registry `Included` is a source-owned field, not proof that an independent human reviewer approved the record. Retain all 82 keyed Needs Review and administrative placeholders separately.
- Search queries and OpenAlex indices have variable historical coverage, linked affiliation parsing errors and differing source freshness; no cross-provider count summation.
- Citation graph edges are provider-sourced references, not causal indicators or formal collaboration. Do not infer individual employment.

## Remaining executable tracks / verification gates

1. **Facility completion:** use the [official HHS facility catalogue](../../portfolio/rims/maps/chhhs-facility-affiliation-catalogue.json) to construct provenance-preserving searches for 27 current facilities, historical district aliases and public health services, then adjudicate actual published author affiliations. Multi-purpose/primary/community centres require bounded geographic context.
2. **Full RIMS adjudication:** establish the independent acceptance authority and reconcile the 63 source-Included records lacking OpenAlex matches; classify 1,019 unmatched discovery works as eligible, ambiguous or non-CHHHS (do not promote automatically).
3. **Citation graph coverage:** obtain the references for HHS-only and rural-facility-only citing works, then evaluate centrality/communities using established network libraries or the separately maintained CiteLattice consumer. Keep out-of-corpus references explicitly observable.
4. **Source enrichments:** complete DOI-level Crossref/Europe PMC, ORCID author identity, DataCite linked outputs, OpenCitations, Unpaywall OA, Semantic Scholar under quotas and licensing. Provider failures and dates must be versioned.
5. **Searchright runtime:** integrate real executed provider receipts only after connecting Searchright MCP and activating live provider policies; current API probes are independent runs, not Searchright native accepted execution.
6. **Quality and release:** strict ID cardinality, status source-versus-review split, retrospective version resolution, false-merge negatives, CI/hosted gate, auditable figure calculations, and per-provider rights/use acceptance.

## Reproducible local calculation

```sh
python portfolio-scripts/rims_rapid_analysis.py --registry '/secure/Publication Registry.csv' --output '/secure/chhhs-rapid-summary.json'
python -m unittest discover -s portfolio-scripts/checks -p test_rims_rapid_analysis.py
```

The source-controlled script is tenant-free and does not automatically fetch or publish private records. A provisional symposium deck was generated and visually rendered locally from the user-supplied snapshot; source release/CI and native Power BI still require separate admission.

## 13 November 2026 update

- Retrieved all 222 previously missing citing-work reference lists from the 2,280-OpenAlex-work discovery union: 6,325 reference assertions, 40 new within-union edges. Combined network: **2,196 directed edges**; 1,268 isolated nodes; 1,406 weak components; largest component 250. No duplicate, self-loop or dangling edges. [Full coverage](../../portfolio/rims/public-sources/openalex-chhhs-citation-graph-20261112/completion-manifest.json), [network summary](../../portfolio/rims/public-sources/openalex-chhhs-citation-graph-20261112/combined-network-summary.json).
- Auditable [graph CLI](../../portfolio-scripts/rims_public_graph_audit.py) and [unittest suite](../../portfolio-scripts/checks/test_rims_public_graph_audit.py) committed. Five synthetic tests passed locally; a sixth full-source integration test is pending hosted CI evidence.
- Supplementary facilities: 21 more name or historical aliases checked. 22 selected works reviewed: ten have source-level exact historical Queensland hospital affiliation evidence; seven belong to other organisations (including Aboriginal community-controlled Gurriny Yealamucka), five remain fuzzy-unresolved. [Review ledger](../../portfolio/rims/public-sources/openalex-chhhs-supplementary-facilities-20261113/affiliation-review.json). These are not human Included decisions.
- Co-affiliation: [OpenAlex groupings](../../portfolio/rims/public-sources/openalex-chhhs-coaffiliations-20261113.json) for Cairns Hospital: 681 indexed works in 2022–13 Nov 2026; James Cook University 237 (34.8%); UQ 168 (24.7%); Townsville Hospital 93 (13.7%). Co-affiliation ≠ formal collaboration, data excludes HHS-only/rural-only records.
- A revised 13-slide symposium presentation, PPTX and PDF, is available in the user's conversation and has passed rendering/overflow checks. Private RIMS source records remain outside Git.

### Still pending
Independent adjudication of 1,019 unmatched candidates and 63 Included records without matched OpenAlex work; 2026 partial-year control; remaining sources' all-ID DOI enrichment; author identity/coauthorship and reference population normalisation; Searchright MCP execution; live Power BI readback and hosted CI.

