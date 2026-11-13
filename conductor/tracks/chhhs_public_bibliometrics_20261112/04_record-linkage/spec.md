# Specification — Canonical publication identities and quality

## Goal
Deduplicate DOI/PMID/PMCID/OpenAlex IDs and robust title-year-author matching; preserve preprints, versions, errata, datasets and retractions distinctly.

## Requirements

**Must:** Use CSL-JSON as canonical exchange format, RIMS-compatible typed identifiers, immutable source assertions and confidence/evidence audit trail; review low-confidence links, provenance of replacements and temporal affiliation.

**Should:** retain replayable provenance, preserve data rights, integrate with existing RIMS contracts where equivalent and document divergences.

**Could:** add additional provider-supported metrics only if independently evaluated and source licensing permits.

**Won't:** assert live collection, RIMS native deployment, private employment affiliation or unverified CHHHS attribution.

## Acceptance criteria
Idempotence, cross-source disagreement, false merge/split, duplicate and retraction tests; unresolved records never silently promoted to confirmed CHHHS.

## Evidence
No implementation or hosted test evidence recorded at creation. Record exact tests, commits, source snapshots and reviewer decisions in a subsequent evidence file.
