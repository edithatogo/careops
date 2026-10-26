# Implementation plan

## Tranche 1: portfolio foundation

- [x] Confirm the polyrepo control-plane decision.
- [x] Replace the organisation-specific `careops-approve` submodule URL.
- [x] Expand the module catalog.
- [x] Add the CHHHS deployment profile.
- [x] Add permissive licensing for the parent repository.
- [x] Add platform-architect and assurance-reviewer agent profiles.

## Tranche 2: core module capability packs

- [ ] `careops-approve`: add a feature-flagged credentialing intake and routing
  contract, generic roles, deterministic quality checks, and human-decision
  controls.
- [ ] `careops-decisions`: add credentialing committee, recommendation,
  delegated-decision, conditions, review, and appeal extensions.
- [ ] `careops-process`: add credentialing objects, events, privacy-minimised
  projection, and conformance metrics.

## Tranche 3: supporting modules

- [ ] `careops-costing`: add a credentialing workload and capacity-release model.
- [ ] `careops-incidents`: add a controlled interface for relevant safety signals
  without copying incident narratives into credentialing analytics.
- [ ] `careops-finance`: retain its reporting and ALM patterns as optional shared
  implementation guidance.

## Tranche 4: organisation pilot

- [ ] Map current jurisdictional and local requirements to stable rule identifiers.
- [ ] Build synthetic credentialing fixtures and negative-path tests.
- [ ] Select one bounded MVP pathway.
- [ ] Establish baseline time, touch, quality, exception, and effort measures.
- [ ] Complete privacy, cyber, records, clinical-governance, architecture,
  accessibility, licensing, and support reviews.
- [ ] Run retrospective and prospective silent-mode evaluation.
- [ ] Seek a separate decision before production writes or CGOV replacement.

## Release discipline

Each capability pack must include:

- owner and module boundary;
- source and authority mapping;
- data classification;
- deterministic checks;
- human decision gate;
- AI provenance and fallback where applicable;
- synthetic, negative-path, and regression tests;
- deployment and licence implications;
- feature flag and rollback;
- support and continuity arrangements; and
- measures of benefit and unintended burden.
