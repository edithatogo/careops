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
