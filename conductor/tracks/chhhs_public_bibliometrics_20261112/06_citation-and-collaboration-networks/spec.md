# Specification — Citation, coauthorship and institutional networks

## Goal
Materialise directed citation graph with citing/cited source provenance and unknown-outside-corpus nodes, plus undirected/coauthorship and institution collaboration weighted graphs.

## Requirements

**Must:** Compute degree/in/out, components, PageRank, centrality, communities with bounded sensitivity, bibliographic coupling and co-citation where complete reference coverage supports them; publish graph formats GraphML/Parquet and versioned semantics.

**Should:** retain replayable provenance, preserve data rights, integrate with existing RIMS contracts where equivalent and document divergences.

**Could:** add additional provider-supported metrics only if independently evaluated and source licensing permits.

**Won't:** assert live collection, RIMS native deployment, private employment affiliation or unverified CHHHS attribution.

## Acceptance criteria
Known small-graph fixtures verify edge direction, deduplication, self-citations, time windows, isolated nodes, fractional weights, missing-reference bias and stability.

## Evidence
No implementation or hosted test evidence recorded at creation. Record exact tests, commits, source snapshots and reviewer decisions in a subsequent evidence file.
