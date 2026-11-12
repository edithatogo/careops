# Specification — RIMS lineage and public-only source boundary

## Goal
Inventory the pinned RIMS submodule, 17-source catalogue, existing 23 measures and publication contracts; document reused logical fields and distinct public cohort; no live tenant or private export dependency.

## Requirements

**Must:** Map source→Bronze→Silver→Gold→Platinum; produce public-only source manifest, source schemas, licence/rate-limit matrix and comparison baseline; preserve original RIMS authority.

**Should:** retain replayable provenance, preserve data rights, integrate with existing RIMS contracts where equivalent and document divergences.

**Could:** add additional provider-supported metrics only if independently evaluated and source licensing permits.

**Won't:** assert live collection, RIMS native deployment, private employment affiliation or unverified CHHHS attribution.

## Acceptance criteria
Inventory maps each source to endpoint, fields, rights and corresponding RIMS contract; historical 1,344 retained accepted register is comparator only; no new collector in existing RIMS pipeline.

## Evidence
No implementation or hosted test evidence recorded at creation. Record exact tests, commits, source snapshots and reviewer decisions in a subsequent evidence file.
