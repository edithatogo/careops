# CKAN catalogue track: staged execution

**State:** planning baseline, not implemented. Tasks are incomplete until linked test evidence exists. Preserve all pre-existing CareOps tracks.

- [x] **C0 — Inventory repository ownership and baseline.** Reviewed `careops`, `careops-approve`, `careops-rims`, `careops-ppg`, archived PPGWorkbench and Conductor parent submodule registration. Evidence: `docs/clinical-data-catalogue/architecture.md`; `docs/clinical-data-catalogue/platform-dependency-radar.md`.
- [x] **C1 — Propose canonical architecture and medallion contract.** Source-only proposed interface: `portfolio/careops-catalogue-contract.v1.json`. Not accepted/deployed.
- [ ] **C2 — Select/create independent catalogue source repository, after publication-boundary and licensing review.** Do not put a second module implementation into CareOps parent. Preserve polyrepo release ownership.
- [ ] **C3 — Materialise Conductor in catalogue repo as a pinned upstream gitlink** (or reuse the CareOps parent submodule if working within parent). Require `.gitmodules`, `git ls-tree` gitlink, `git submodule status`, and host-specific smoke receipts. Do not mutate upstream.
- [ ] **C4 — Initial SPFx skeleton and canonical schemas.** GA generator 1.24.1, React 18.3.1 and supported TypeScript; snapshot npm lockfile, deny premium imports, test SharePoint indexed pagination, pure adapter interfaces, and no secrets.
- [ ] **C5 — Synthetic Bronze/Silver ingestion and provenance.** Content-address/checksum preserved version, quarantine, idempotency, source removal and lineage negative cases; no raw patient records.
- [ ] **C6 — Gold deterministic aggregate and Platinum publication.** Run validation, small-cell suppression, human decision, immutable release manifest, expired authorization denial, rollback.
- [ ] **C7 — Optional CareOps versioned integration.** Implement evidence-only PPG/Approve/Decisions adapters and RIMS link-outs, with absence, change and revocation reconciliation. Do not import existing queues/registers.
- [ ] **C8 — CKAN/DCAT interoperability.** Generate fixtures/validators for CKAN action envelopes and target DCAT profile, including privacy redaction and non-claim of native CKAN API.
- [ ] **C9 — Feature-flag canaries.** Isolated prerelease SPFx CLI, new/edit panel UX and optional integrations; compare against GA output and explicitly refuse unqualified promotion.
- [ ] **C10 — Tenant admission & implementation.** Obtain site/app-catalog rights, standard connector readback, records/privacy/cyber sign-off, CHHHS governance owner, licences and production support. No source-level tests substitute for this.
- [ ] **C11 — Portfolio adoption.** Update `portfolio/repos.json`, `.gitmodules`, module catalog and compat matrix only after independent repo, provenance, secret scanning, licences, CI and rollback qualify.
- [ ] **C12 — Release review and maintenance.** Automated dependency canary, exact pins, vulnerability and licence review, forward/back migration tests, frozen evidence and clean rollback.
