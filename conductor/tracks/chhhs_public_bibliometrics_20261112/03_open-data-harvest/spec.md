# Specification — Reproducible public metadata discovery and enrichment

## Goal
Discover candidate works from PubMed/NCBI E-utilities, Europe PMC and OpenAlex; enrich Crossref, DataCite, ORCID/ROR and citation sources when eligible. DoRA/RIMS private sources are not required.

## Requirements

**Must:** Provider adapters, bounded pagination, credentials by environment, retries/backoff, ETag/updated watermark when supported, content digests, snapshots, provider schema versions, deletion/merge handling and replay. Distinguish source-specific licensing and coverage.

**Should:** retain replayable provenance, preserve data rights, integrate with existing RIMS contracts where equivalent and document divergences.

**Could:** add additional provider-supported metrics only if independently evaluated and source licensing permits.

**Won't:** assert live collection, RIMS native deployment, private employment affiliation or unverified CHHHS attribution.

## Acceptance criteria
Golden provider fixtures for zero/one/many pages, errors, date windows, API drift, throttling, retries and incremental/full recomputation; publicly distributable fields only.

## Evidence
No implementation or hosted test evidence recorded at creation. Record exact tests, commits, source snapshots and reviewer decisions in a subsequent evidence file.
