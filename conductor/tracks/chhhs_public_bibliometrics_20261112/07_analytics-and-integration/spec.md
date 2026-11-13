# Specification — Versioned datasets, research products and RIMS reuse

## Goal
Publish Bronze/Silver/Gold/Platinum public datasets and an inspectable data dictionary; Polars/Parquet internal analysis, CSL-JSON interoperability and safe CSV exports; dashboards reproducible without a live M365 tenant.

## Requirements

**Must:** Prefer the separate CiteLattice library for generic scientometrics after contract review, avoid coding a duplicate framework; RIMS consumer adapter read-only and optional; snapshots/release manifests and research-use disclaimers.

**Should:** retain replayable provenance, preserve data rights, integrate with existing RIMS contracts where equivalent and document divergences.

**Could:** add additional provider-supported metrics only if independently evaluated and source licensing permits.

**Won't:** assert live collection, RIMS native deployment, private employment affiliation or unverified CHHHS attribution.

## Acceptance criteria
Machine-readable validation, row and edge lineage, public data licence filtering, privacy minimisation; Power BI semantic measures/dashboard parity verified separately, not asserted by source files.

## Evidence
No implementation or hosted test evidence recorded at creation. Record exact tests, commits, source snapshots and reviewer decisions in a subsequent evidence file.
