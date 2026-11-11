# Ordered executable implementation, source first

Current selected branch: `feat/ppg-assurance-coverage-20261111`. Technical-only scope; no live tenant, policy approval, accreditation authority, privileged connector, email or external sharing. Existing Conductor tracks for currency, clinical registries and native source keep ownership. Work in bounded reviewed increments.

## PA-00 Source reconciliation and authority model
- [x] PA-00.01 Inventory existing PPG accreditation, policy currency, observation, external catalogue, standard and source ownership code; identify duplicates to avoid
- [ ] PA-00.02 Build executable versioned source-type and normative-force contract and negative fixtures (HSD vs guideline, internal vs externally issued)
- [ ] PA-00.03 Add exact publisher/document/edition/capture/currentness bindings for reviewed authority records; restrict raw external text by licence
- [ ] PA-00.04 Define explicit local adoption and supersession state/actor authority, effective period and service scope; test policy-body preservation

## PA-01 Cross-scheme scoped applicability and version transitions
- [ ] PA-01.01 Validate NSQHS v2 action sources, workbook/advisory editions and granular status in existing framework graph without duplicating the corpus
- [ ] PA-01.02 Register v3 consultation separately as draft candidate and implement edition-to-edition change proposals only, no automatic obligation
- [ ] PA-01.03 Add reviewed ANZCA, RACP and RACS scheme/source **candidate metadata**, explicitly unverified until original source captured and approved
- [ ] PA-01.04 Implement service/site/training-setting/post/specialty context fixtures, effective dates, conflicts and absent-scope negative tests

## PA-02 Read-only assurance and implementation evidence
- [x] PA-02.01 Add an offline requirement-by-scope assurance coverage projection, reusing the v1 accreditation graph rather than a new register
- [ ] PA-02.02 Execute the source projection tests on canonical Python 3.15.1; complete missing/equivocal/changed-edition adversarial cases and CI coverage
- [ ] PA-02.03 Reconcile existing indicator/observation evidence to implementation-control lifecycle without treating observed counts as compliance
- [ ] PA-02.04 Add proposed/reviewed/expired/missing evidence states, owner/action routing and source-specific observation limitations (no universal score)
- [ ] PA-02.05 Produce source-only report package and contract for native SharePoint list views; real data stays private

## PA-03 Monitoring and governed human review
- [ ] PA-03.01 Generate bounded source-change/expiry/authority-diff candidates from existing `ppg_source_surveillance` and `ppg_policy_currency` outputs
- [ ] PA-03.02 Add pending applicability, implementation, evidence and assessment review queues with opaque owner refs and due dates, preserving old decisions
- [ ] PA-03.03 Reconcile clinical governance committee records through optional Decisions/Clinical Hub links; no second authority
- [ ] PA-03.04 Build no-AI deterministic control monitoring and optional model candidate workflow, with explicit human dispositions

## PA-04 Power Platform ALM and assurance reporting
- [ ] PA-04.01 Generate versioned non-premium SharePoint list/library metadata and standard-connector flow source for the existing PPG app
- [ ] PA-04.02 Add Power Platform solution graph/connection reference validation and pack/unpack parity tests for exact source version
- [ ] PA-04.03 Extend selected PBIP/TMDL model contracts for multi-scheme site readiness with unknown counts, policy status and evidence freshness
- [ ] PA-04.04 Qualify native deployment, RBAC, screenreader/browser journeys, readback, retry/rollback and export with tenant owners (cannot close in GitHub alone)

## PA-05 Source quality, privacy and acceptance
- [ ] PA-05.01 Add property-based and metamorphic graph invariants; no inferred accreditation rating or transfer after changing order, scope or edition
- [ ] PA-05.02 Test full original document metadata/byte provenance, URLs/licences and unapproved-source exclusion
- [ ] PA-05.03 Run module affected and full tests, Gitleaks, publisher content guard, packaging and source CI on exact PR head
- [ ] PA-05.04 Merge only after all required hosted checks pass; source-only success is not native or accreditation acceptance

## Current qualification

The first PA-02.01 projection and 12 synthetic tests have been authored/committed. **No canonical local Python 3.15.1 test execution or hosted current-head CI is claimed.** The existing graph source and accreditation human decisions remain unchanged. Other boxes remain open. Documentation and candidate-source URLs do not authenticate external editions.


---

## Additional source slice — authority, adoption, currency and review queue

Under PA-00/01, version- and scope-bound policy source-force candidate classifications and human adoption events are now modeled in `ppg_obligation_application.py`. Under PA-02/03, `ppg_evidence_currency.py` projects explicit review-window states and `ppg_assurance_bundle.py` generates deterministic, non-operative review candidates across the same graph version. Their tests are written and committed.

**Do not interpret these as completed operational requirements:** source capture authority, actual evidence bytes, control implementation, trained assessor decisions and native publication remain unqualified. The reviewed source inventory contains the new implementation/test files. Full Python 3.15.1 module tests and protected GitHub Actions are still pending. This incremental implementation does not alter previously approved operative PPGs or issue any tasks.
