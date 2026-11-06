# CKAN catalogue track: staged execution

**State:** planning baseline, not implemented. Tasks are incomplete until linked test evidence exists. Preserve all pre-existing CareOps tracks.

- [x] **C0 — Inventory repository ownership and baseline.** Reviewed `careops`, `careops-approve`, `careops-rims`, `careops-ppg`, archived PPGWorkbench and Conductor parent submodule registration. Evidence: `docs/clinical-data-catalogue/architecture.md`; `docs/clinical-data-catalogue/platform-dependency-radar.md`.
- [x] **C1 — Propose canonical architecture and medallion contract.** Source-only proposed interface: `portfolio/careops-catalogue-contract.v1.json`. Not accepted/deployed.
- [ ] **C2 — Admit planned catalogue source at `modules/careops-catalogue/` within the CareOps parent**, after publication-boundary, licensing and security review; do not default to a duplicate standalone repo. Keep sibling module native/runtime ownership and their migration tracks intact.
- [ ] **C3 — Reuse the existing CareOps parent pinned Conductor gitlink; do not create a second checkout.** Require `.gitmodules`, `git ls-tree` gitlink, `git submodule status`, and host-specific smoke receipts. Prefer the [native Gemini CLI Agent Skills linking procedure](../../../docs/clinical-data-catalogue/conductor-gemini-cli.md) without upstream edits. Do not mutate upstream.
- [ ] **C4 — Provider-neutral catalogue domain/ports, SharePoint Lists/Libraries adapter and initial SPFx skeleton.** GA generator 1.24.1, React 18.3.1 and supported TypeScript; snapshot npm lockfile, deny premium imports, test SharePoint indexed pagination, pure adapter interfaces, and no secrets.
- [ ] **C5 — Synthetic Bronze/Silver ingestion and provenance.** Content-address/checksum preserved version, quarantine, idempotency, source removal and lineage negative cases; no raw patient records.
- [ ] **C6 — Gold deterministic aggregate and Platinum publication.** Run validation, small-cell suppression, human decision, immutable release manifest, expired authorization denial, rollback.
- [ ] **C7 — Optional CareOps versioned integration.** Implement evidence-only PPG/Approve/Decisions adapters and RIMS link-outs, with absence, change and revocation reconciliation. Do not import existing queues/registers.
- [ ] **C8 — CKAN/DCAT interoperability.** Generate fixtures/validators for a scoped compatibility API and DCAT profile, including privacy redaction. Separately evaluate untouched CKAN 2.12.1 with native services and a file-keeper SharePoint Library adapter.
- [ ] **C9 — Feature-flag canaries.** Isolated prerelease SPFx CLI, new/edit panel UX and optional integrations; compare against GA output and explicitly refuse unqualified promotion.
- [ ] **C10 — Tenant admission & implementation.** Obtain site/app-catalog rights, standard connector readback, records/privacy/cyber sign-off, CHHHS governance owner, licences and production support. No source-level tests substitute for this.
- [ ] **C11 — In-tree reference-source admission.** Integrate under `modules/careops-catalogue/` only after provenance, licence, secrets, CI and rollback gates; no new `.gitmodules` submodule. Existing sibling module integration follows its own ongoing Conductor tracks.
- [ ] **C12 — Release review and maintenance.** Automated dependency canary, exact pins, vulnerability and licence review, forward/back migration tests, frozen evidence and clean rollback.

- [ ] **C13 — Provider portability:** canonical DTOs and common CRUD/query, pagination, ETag/revision, release, governance and authorization conformance suite for SharePoint and later Dataverse/SQL Server.
- [ ] **C14 — Migration rehearsal:** validate synthetic snapshot, delta journal, dual-read shadow, access equivalence, controlled cutover and rollback; libraries can remain as asset storage.
- [ ] **C15 — SQLite:** restrict to offline export/snapshot/testing with checksums; prohibit live SQLite databases on SharePoint/OneDrive sync folders.
- [ ] **C16 — Genuine CKAN optional mode:** deploy unchanged supported CKAN with PostgreSQL/Solr/Redis in isolated lab, evaluate CKAN 2.12 file-keeper storage interface and SharePoint adapter, no upstream changes.
