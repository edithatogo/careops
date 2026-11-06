# CKAN catalogue track: staged execution

**State:** planning baseline, not implemented. Tasks are incomplete until linked test evidence exists. Preserve all pre-existing CareOps tracks.

## Coding-agent execution gate

**Before any C2–C16 or SP-01–SP-06 implementation**, follow [the coding-agent handoff](../../../docs/clinical-data-catalogue/coding-agent-handoff.md):

- [ ] **AG-00 — Source/roadmap/PR reconciliation.** Existing family ownership, approved source boundaries, active modules and Conductor pin audited; evidence and no-duplicate matrix saved.
- [ ] **AG-01 — Local CLI and toolchain inventory.** Exact installed versions, trust/skill activation, clean checkout, source-only test harness, no tenant bindings.
- [ ] **AG-02 — Auth and permissions read-only preflight.** Approved CHHHS site and approved Entra client, scopes and account permission readback, with private receipts; if blocked, record permission request and do offline tests.
- [ ] **AG-03 — Canonical domain and fictional fixtures.** SharePoint-neutral IDs, schemas and mock provider, runnable contract tests; independent of AG-02.
- [ ] **AG-04 — Small approved pilot provisioning.** **Only** 3 Lists (Organizations/Datasets/Resources) + 1 PilotAssets Library; shared columns, indexed views, protected resource and idempotent rollback, following signed non-production access.
- [ ] **AG-05 — Minimal SharePoint adapter.** ETag revision, pagination, idempotency, bytes and negative permission tests.
- [ ] **AG-06 — Native SharePoint UI usability test.** Prove user discovery/edit/download task before any SPFx investment.
- [ ] **AG-07/08 — Governance and medallion expansion.** Preserve external decision authorities, lineage, revocation, disclosure controls and published releases.
- [ ] **AG-10 — Operational acceptance and staged pilot.** Clinical, records, cyber, privacy and support controls verified; do not infer deployment from code tests.

**AG-09 SPFx, FK-01 FileKeeper and MIG-01 future providers are optional non-blocking branches.** Any missing site-right, client app, licensing, or connector permission is a **stop condition**, not permission to bypass organisational controls. CI artifact-storage quota is an infrastructure finding, not a valid test suppression.


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

## Minimal-development SharePoint/CKAN FileKeeper work packages

- [ ] **SP-01 — Verify CHHHS site owner, Lists/Libraries, standard connectors, records, access and app catalogue rights; capture readback and refusals**
- [ ] **SP-02 — Provision Lists, Libraries, site columns/content types and indexed default views from `portfolio/careops-catalogue-sharepoint.v1.json`; use fictional seeded resources and readback validation**
- [ ] **SP-03 — Implement thin typed SharePoint `CatalogueRepository` and `AssetRepository` using supported REST/ETags, pagination, asset checksums and idempotent journal**
- [ ] **SP-04 — Deliver native list/library discovery, metadata editing, resource links, approvals references and standard flows; only introduce SPFx when a tested task cannot be met with native views**
- [ ] **SP-05 — Implement synthetic medallion lineage, validation and authorised Platinum release manifest; no bulk clinical or heavy compute processing**
- [ ] **SP-06 — Complete source, access denial, version restore, cross-provider contract and rollback conformance evidence**
- [ ] **FK-01 — Prototype Python `ckanext-careops-sharepoint-storage` implementing CKAN 2.12 `file-keeper` factories against a fictional/approved SharePoint test site; no upstream patch**
- [ ] **FK-02 — Only if native CKAN chosen: qualify identity, server hosting, permission isolation, upload/download/streaming, 2.12 compatibility and operations**

Estimated functional native SharePoint MVP **21–40 engineering person-days** (source planning estimate), with SPFx **+6–12** and custom CKAN FileKeeper adapter **+10–20** separately. A small native-views demo can be narrower (5–10 days). Refer to [scope/assumptions](../../../docs/clinical-data-catalogue/sharepoint-native-build-plan.md).
