# RIMS relationship assurance — executable task plan

**Current status:** planning/contracts only in parent CareOps. Writing branch in `edithatogo/careops-rims` was denied (GitHub 403); RIMS module implementation not changed. No live or new source collection, native List/flow, reporting update or external share. This track defines granular tasks for Conductor implement → review → fix → evidence-qualified merge.

| Task | MoSCoW / dependency | Implementation, executable evidence and exit |
| --- | --- | --- |
| RRA-T01 Source inventory | Must / none | Compare current RIMS G06, author registry, organisation enrichment, clinical attribution and grant/award crosswalks with PR #309 source registry; pin actual accepted schema and known defects; record native source owner. |
| RRA-T02 Identity contract | Must / T01 | Define canonical source-qualified publication/author/organisation/award/project keys and alias namespace rules. Test ORCID/ROR duplication, invalid identifiers, name collision, identity-history continuity. |
| RRA-T03 Typed relation schema | Must / T02 | Versioned relationship and assertion schemas, exact predicate taxonomy, status mapping to existing RIMS ReviewStatus; machine-validate all positive/negative fictional cases. |
| RRA-T04 Evidence-origin contract | Must / T02 | Upstream-origin provenance chain; distinguish copied Crossref records in OpenAlex/OpenAIRE, ORCID/ROR identity-only and independent internal registry observations. Test two-vendor/one-origin versus two genuinely independent origins. |
| RRA-T05 Source-use qualification | Must / T01,T04 | Reuse existing 17 providers, complete retained source-field profiles and consumer mappings, then record **specific** missing field gaps before adding any API. Keep keyless/free credential constraints, licensing/terms, source freshness and partial-data states. |
| RRA-T06 Pure deterministic assessor | Must / T03–05 | Fail-closed no-I/O evaluator for proposed authorship, affiliation, partner, grant, study, output and relevance links; separate supported, held, disputed, insufficient and rejected results. Prove no name-only/employment/formal-partner/funding promotion. |
| RRA-T07 Existing grant relationship integration | Must / T03,T06 | Adapt `grants_relationships.py` without changing old relationship IDs/statuses; demonstrate exact award+funder match, relevant opportunity candidate and contradictory award sources. |
| RRA-T08 Author/institution integration | Must / T02,T06 | Integrate `author_registry.py`, `organisation_enrichment.py` and `clinical_attribution.py` as candidate producers; preserve author order/date/evidence and role distinctions, no automatic promotion from facility keyword alone. |
| RRA-T09 Review and decision ledger | Must / T03,T06 | Use existing RIMS review exception object/surface, stable case ID, explicit dispositions/authority, optimistic concurrency and changed-source replay. Human review only on genuine uncertainty/conflict. |
| RRA-T10 Selective invalidation | Must / T04,T09 | Source→assertion→relationship→consumer dependency graph; rerun changed dependencies only; test unchanged replay, corrected author/award, conflicting record, human-edit preservation and supersession. |
| RRA-T11 Native SharePoint/flow admission | Must / T07–10 | Qualify actual List/field IDs, Standard connector schema, pagination, version/ETag, one approved writer, no-mail effects and recovery. Prepare stopped candidate, pack/preserve through Power Platform mechanisms; native save/run only with existing owner/approval. |
| RRA-T12 Reporting reconciliation | Must / T10–11 | Extend accepted RIMS model/report/paginated contracts using verified relationship snapshots; test candidate versus verified counts, denominators, service vs institution, partner/funding distinctions and source freshness. No report deployment assumed. |
| RRA-T13 Adversarial testing and profiling | Must / T06–12 | Run deterministic fixtures, Hypothesis properties, metamorphic source-order/duplicate-provider tests, mutation/security/privacy/dependency tests and benchmark bounded batch size. Use pinned RIMS Python 3.15.1, exact-head CI and no private data in logs. |
| RRA-T14 Pilot and acceptance | Must / T11–13 | Two new publication cycles and bounded re-enrichment/changed-award cases; native readback/permissions, exact keys, original evidence and reviewer queue; classify passed/failed/held/unexecuted. |
| RRA-T15 Optional consumers | Should / T12 | Read-only versioned outputs to Grants, Improvement, Catalogue and Decisions review, with no new operational authority or premium dependency. |
| RRA-T16 Research evaluation | Could / T14 | Measure false matches/omissions, percentage needing review, source coverage, attribution agreement, correction time and net administrative burden versus current rules; do not claim causality without design. |

## Prescribed development sequence

1. **Reconcile first:** identify current module head, RIMS G06 ownership, PR #309's in-progress utilisation work and any concurrent author/organisation track. Never copy/integrate stale parent submodule code as though it were main.
2. **Tests first:** establish two independent providers repeating the same Crossref origin; a publication with matching service keyword but no authorship evidence; confirmed author affiliation versus employment; a topical grant match without award evidence; conflicting grant IDs; mutable author affiliation revision; previously accepted record with later correction.
3. **Implement bounded pure source logic** in existing RIMS scripts with a minimum new module; preserve canonical IDs and statuses. Use existing review queue, storage and List bindings.
4. **Review gates:** profile/usage data checks, code/security/privacy/source inventory, machine schema, property/metamorphic and quality review. Hosted CI refusal = unexecuted; protected merge requires actual required checks.
5. **Native qualification and consumers:** make no new Flow/List/scheduled operation unless current owner authorises the exact target; readback and rollback first. Update the existing semantic model/report only after exact native and analytical contract acceptance.

## Non-goals / scope safety

No automatic emails, research-performance ranking, grants application, tenant-wide directory mining, unreviewed publication inclusion, speculative partnerships or spending. Keep source-only evidence fictional and any private employer/author/award references outside Git. An optional AI model may only propose relation candidates after a measured deterministic gap and must retain the same review controls.
