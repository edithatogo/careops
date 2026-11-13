# Specification — CHHHS identity, historical affiliation and adjudication

## Goal
Build alias/effective-date dictionary for Cairns and Hinterland Hospital and Health Service, former names, hospitals, author-affiliation variants, ROR IDs and institution merges. Reject geographic keyword-only attribution.

## Requirements

**Must:** Triangulate institution IDs, explicitly printed affiliations, author metadata and publication-year institutional structure; maintain inclusion tiers confirmed/probable/uncertain/excluded, provenance and review queue.

**Should:** retain replayable provenance, preserve data rights, integrate with existing RIMS contracts where equivalent and document divergences.

**Could:** add additional provider-supported metrics only if independently evaluated and source licensing permits.

**Won't:** assert live collection, RIMS native deployment, private employment affiliation or unverified CHHHS attribution.

## Acceptance criteria
Every included work has at least one auditable institutional affiliation assertion and observation date; false positives and ambiguities tested; publication vs individual employment distinguished.

## Evidence
No implementation or hosted test evidence recorded at creation. Record exact tests, commits, source snapshots and reviewer decisions in a subsequent evidence file.

## Historical alias discovery receipt — 12 November 2026

Cairns Base Hospital is a confirmed historical name for Cairns Hospital (renamed in 2013); the ROR entity (029s9j634) is identical across the historical/current names. The dedicated historical OpenAlex search returned 950 work-ID candidates (1957–2026), of which 940 were already in the modern Cairns Hospital institutional search; ten were not. In a record-level check of those ten, **only one** included the exact historical hospital name in its returned author affiliations; nine remain unresolved, not included. PubMed exact-phrase search returned 377 and all 377 IDs were already covered by the broader PubMed regional search. Source records and matching are retained in [the discovery union](../../../../portfolio/rims/public-sources/openalex-chhhs-discovery-union-20261112/manifest.json), [the alias map](../../../../portfolio/rims/maps/chhhs-publication-affiliation-aliases.json) and [quality exceptions](../../../../portfolio/rims/public-sources/openalex-chhhs-discovery-union-20261112/quality-exceptions.json).

**False-positive control:** OpenAlex fuzzy raw-affiliation search for `Mareeba Hospital` returned 1925 and 1926 works actually affiliated with *Mareeba Babies' Hospital in Adelaide*, not Far North Queensland. These are explicitly flagged as non-local matches and cannot be used to claim CHHHS research activity in 1925. Names should be validated against source-text evidence and location.
