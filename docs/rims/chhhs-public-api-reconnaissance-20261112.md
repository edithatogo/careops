# Public bibliography API reconnaissance — 12 November 2026

**Status:** targeted live searches and first-page DOI checks completed; **not an exhaustive multi-provider harvest, not a Searchright MCP run and not automatic RIMS inclusion**. Uploaded registry is kept out of Git.

## Source observations

| Provider | Actual observation | Interpretation |
| --- | --- | --- |
| PubMed | 2026 affiliation query: 118 results, 117 matched baseline PMID; one candidate review | Prior run, source-specific |
| Europe PMC | Exact Cairns Hospital affiliation + 2026 FIRST_PDATE: 1 (PMID 41721291) | Too narrow for census |
| ROR | Cairns Hospital = https://ror.org/029s9j634; alias Cairns Base Hospital | Useful identity anchor |
| OpenAlex institution | Cairns Hospital = https://openalex.org/I2800926667; 2,093 historical works in institution metadata | Different universe from 1,344 RIMS |
| OpenAlex 2026 institute | 143 matches through 12 Nov; **first 10 DOI matches present in uploaded register** | Full 143-row extraction/reconciliation pending |
| OpenAlex generic text | 50,250 hits including news | Invalid as CHHHS publication population |
| Crossref text/affiliation | 3,580,081 reported results | Broad relevance search, not a CHHHS denominator; use DOI exact-key enrichment |
| DataCite | 78 results for creator affiliation query; collections/supplements in first five | Related outputs require version-linked deduplication |
| ORCID | 53 search hits under Cairns Hospital | Candidate people, not employment verification |
| OpenCitations | Test DOI 10.1111/1742-6723.14177 returned empty incoming edges | Missing edges do not prove uncited work |
| Semantic Scholar | Same DOI, paperId 428210803626e34cbb497012289d08756ad1e6ae; 1 citation, 20 references | Provider-specific count vintage |
| Unpaywall | Same DOI: is_oa=true, oa_status=bronze | DOI-based OA enrichment only |
| OpenAIRE | Keyword Cairns Hospital returned 795, including wrong-author-name matches | Free-text search invalid for attribution |

Source receipt links (browser runs) and full query URLs are retained in the local analytical report; do not call this a Searchright-generated evidence receipt. No cross-source sum is valid. The ROR-constrained OpenAlex filter URL trial yielded zero because its ROR value was malformed by parsing; the **resolved institution-ID query** succeeded and supersedes that failed approach.

## Next implementation gates

- [ ] Paginate all 143 OpenAlex 2026 Cairns Hospital work matches, reconcile DOI/PMID against the full source register and classify new/changed/excluded and ambiguous.
- [ ] Repeat institution-ID and effective-dated hospital/predecessor variants for all years, without conflating CHHHS-wide and Cairns Hospital-only populations.
- [ ] Enrich all registered DOI/PMID IDs through Crossref, Europe PMC, Semantic Scholar, OpenAlex, DataCite, OpenCitations and Unpaywall under rate/rights quotas; preserve source-vintage differences.
- [ ] Link ORCID/ROR and per-authorship institutional evidence with reviewer decision authority; related-data DOIs are not articles.
- [ ] Audit temporal publication online/print/index dates, duplicate DOI assertions and coverage; obtain exact source receipts and validate sampled attribution.
- [ ] Execute this through Searchright with live provider access separately: browser API probes do **not** establish Searchright execution.
