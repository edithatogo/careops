# CHHHS public publications and bibliometrics — execution programme

Created 2026-11-12. **Status: planned; no new live collection or verified publication dataset yet.** Scope: independently reproducible public-data candidate cohort; keep RIMS production and internally adjudicated authority separate.

## Dependency graph

01 → 02 → 03 → 04 → 05/06 → 07 → 08. Track 03 may prototype fixtures alongside 02, but public attribution and review gates precede Gold publication. Existing [RIMS full-data utilisation](../rims_full_data_utilisation_20261110/index.md) and [medallion programme](../rims_medallion_verticals_20261110/index.md) remain the canonical existing-source owners.

| Track | Work package | State | Link |
|---|---|---|---|
| 01 | RIMS lineage and public-only source boundary | not_started | [spec and plan](01_rims-source-boundary/index.md) |
| 02 | CHHHS identity, historical affiliation and adjudication | not_started | [spec and plan](02_institution-attribution/index.md) |
| 03 | Reproducible public metadata discovery and enrichment | not_started | [spec and plan](03_open-data-harvest/index.md) |
| 04 | Canonical publication identities and quality | not_started | [spec and plan](04_record-linkage/index.md) |
| 05 | Publication and citation time-series products | not_started | [spec and plan](05_bibliometric-time-series/index.md) |
| 06 | Citation, coauthorship and institutional networks | not_started | [spec and plan](06_citation-and-collaboration-networks/index.md) |
| 07 | Versioned datasets, research products and RIMS reuse | not_started | [spec and plan](07_analytics-and-integration/index.md) |
| 08 | Evaluation, automation, security and scientific verification | not_started | [spec and plan](08_verification-release/index.md) |

## Data-product contract

- **Universe:** records with evidenced CHHHS or appropriately historical predecessor institutional affiliation; candidate, adjudicated and excluded populations separate. Affiliation at publication date is not proof of employment, grant ownership or CHHHS-only contribution.
- **Discovery vs reference:** public candidate discovery from PubMed, Europe PMC, OpenAlex, then provider-specific enrichment; RIMS historically accepted 1,344 is a **comparison baseline only**, not a harvest target, not an outcome and not a deduplication oracle. DoRA may be source-specific and must not be implicitly treated as unrestricted public bulk data.
- **Identity:** CSL-JSON interchange; DOI/PMID/PMCID/OpenAlex/ROR/ORCID and their provenance; preserve individual source assertions, version relations and explicit adjudication. Existing `portfolio/rims/contracts/domains/publications.schema.json` defines broad domain semantics, not a sufficiently strict public-work schema; track 04 must make exact typed contracts.
- **Medallion:** Bronze licence-permitted raw response + digest/request/observed time; Silver typed assertions and candidate links; Gold versioned, confirmed/qualified cohorts; Platinum bibliometry and graphs with explicit uncertainty and denominator definitions.
- **Citation edge:** `(citing_work_id, cited_work_id, source, observed_at, assertion_id)` directed from citing to cited; distinguish observed external nodes and missing references; never aggregate provider-specific citation counts as independent observations.
- **Temporal:** publication date precision (online/print/issue), citation snapshot date, updated date and institutional effective date are distinct; current-year provisional flag, retrospective changes, retraction/correction events and observation-lag sensitivity.
- **Reproducibility:** every release records code revision, query/filter, source version, access date, licence, cohort rule and reviewed overrides; no public Git commits of private RIMS extracts, identifying non-public human decisions or credentials.

## Initial source-to-purpose mapping

| Source | Role | Cautions |
|---|---|---|
| PubMed / NCBI E-utilities | PMID, article metadata and affiliation discovery | Affiliation completeness varies by era and author; use E-utilities conditions |
| Europe PMC | PMID/PMCID, abstracts, citations and full-text/reference metadata where allowed | Coverage of reference lists/affiliations uneven; full text has rights boundaries |
| OpenAlex | institution/ROR discovery, work/topic/authorship and citation graph | Institution matching incomplete; API limits/keys and snapshot drift |
| Crossref | DOI registration, references, licence, funding and correction relations | References may be unstructured, closed or absent; attribution not authoritative |
| Semantic Scholar | supplementary citation graph and influential-citation signals | Conditional rate limits, inconsistent coverage and model-specific metrics |
| OpenCitations | independently sourced DOI→DOI edges | Not a complete citation universe; provenance of graph release required |
| DataCite | linked datasets/software and related-identifier graph | Research outputs are not automatically journal publications |
| ROR / ORCID | organisation/person identity resolution | Do not collapse names to a single person without evidence |
| DoRA / RIMS | historical accepted comparison and optional authorised enrichment only | Never assume export licence, private data access or live source equivalence |

## MoSCoW

**Must:** open-data-only reproducibility; qualified CHHHS affiliation; source-aware stable IDs and human-review flags; rights/provenance; medallion schema; longitudinal counts; directed citation edge semantics; fixture tests; no private exports. **Should:** heterogeneous provider enrichment, collaboration and co-citation networks, fractional counting, dashboards, source-difference audit. **Could:** topic evolution, field-normalised citation comparisons with adequate reference populations, CiteLattice integration, interactive graph. **Won't yet:** claim publication census completeness, historical RIMS parity, current live deployment, author employment, causal research impact or cross-provider summation of citation counts.

## Setup / Gemini Conductor

The upstream **Gemini Conductor is already pinned** at `.agents/plugins/conductor` in `.gitmodules`. Do not vendor, duplicate or silently update upstream. On an authorised local Gemini CLI host, execute:

```sh
git submodule update --init --checkout -- .agents/plugins/conductor
git submodule status -- .agents/plugins/conductor
for skill_dir in .agents/plugins/conductor/skills/*; do
  test -f "$skill_dir/SKILL.md" || continue
  gemini skills link "$skill_dir" --scope workspace
done
gemini skills list --all
# Then /skills reload in Gemini CLI; activate setup/status/new-track in a fictional workspace first.
```

Use [existing documented admission tests](../../../docs/clinical-data-catalogue/conductor-gemini-cli.md). This GitHub source change **does not run a local Gemini CLI**; skill activation and host-side validation remain pending. The parent Conductor registry owns these tracks.

## Completion policy

Track status moves to in_progress only with implementation commits, and to completed only with tests, independent review, evidence and integration receipts. Missing API/tenant credentials must be logged as explicit blockers without faking a success. Use a review PR; no data publication or acceptance solely from documentation.
