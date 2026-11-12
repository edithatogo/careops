# Executable plan — Citation, coauthorship and institutional networks

- [ ] Inspect upstream RIMS/source contracts and freeze public-only boundaries and fixtures relevant to this track.
- [ ] Write precise typed schemas and provider/source mapping with provenance and missing-data semantics.
- [ ] Implement a minimal end-to-end fixture example before widening scope.
- [ ] Implement remaining adapters/analyses with failure and edge-case handling.
- [ ] Add deterministic unit, property and metamorphic tests and golden snapshots as applicable.
- [ ] Validate scientific correctness, provider rights, deduplication/attribution risk and time-vintage effects.
- [ ] Execute targeted checks and hosted CI; record exact evidence and failures.
- [ ] Independent Conductor review; resolve issues; reconcile linked RIMS contracts and consumer dependencies.
- [ ] Produce source-qualified handoff, review acceptance and close only with independent reproducible evidence.

## Exit
Known small-graph fixtures verify edge direction, deduplication, self-citations, time windows, isolated nodes, fractional weights, missing-reference bias and stability.

## 13 November 2026 source implementation evidence

- [x] Retrieve 222 previously missing candidate citing works, 6,325 raw references, 40 within-union directed edges.
- [x] Compute 2,196-edge full 2,280-candidate graph, endpoint/duplicate/self checks, 1,268 isolated, 1,406 weak components.
- [x] Implement source-only stdlib graph auditing CLI and 5 synthetic tests (local pass), plus full-data regression test (hosted run pending).
- [x] Retrieve OpenAlex Cairns Hospital co-affiliation groups for 2015–2021 and 2022–2026 with explicit denominators and nonexclusive counts.
- [ ] Review institutional eligibility, validate author/institution networks and source publication dates, benchmark methods against CiteLattice, and run source-level acceptance on current GitHub head.

