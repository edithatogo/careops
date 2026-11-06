# SharePoint Lists + Libraries catalogue: minimum-customisation implementation plan

**Status:** design and cost model, 2026-11-06. No deployed or verified CHHHS tenant objects.  
**Canonical architecture:** [unmodified CKAN vs CareOps provider](adr-ckan-core-and-backends.md); [medallion](architecture.md). **Agent sequencing and permissions:** [coding-agent handoff](coding-agent-handoff.md). The full listed inventory is a target schema, not an instruction to create all entities on day one.

## Chosen physical architecture

- **Database:** standard SharePoint Online **Lists** for CKAN-compatible Organizations, Datasets/Packages, Resources, Groups, Tags, assignments, governance *references*, release manifests and outbox/journal. No SQLite file as a live database, no premium Dataverse/SQL, no primary PostgreSQL replacement for CKAN itself.
- **File storage:** standard SharePoint Online **Document Libraries** for uploaded objects, dictionaries, protocols, validation receipts and released products, enriched with **site columns, library views, content types, metadata and version history**.
- **Application access:** use native SharePoint Modern Lists, libraries, document forms, permissions and views as the first user interface. An SPFx 1.24.1 React web part adds a catalogue experience **only when** native forms/views cannot meet a tested user task. No CKAN UI copy.
- **Custom-code boundary:** typed provider-neutral repository/asset interfaces and thin SharePoint REST adapters; SharePoint-specific IDs, ETags, site paths, lookup structures and user fields remain inside adapter mapping. Standard Power Automate connectors for small orchestration, not heavy compute.
- **Future:** SharePoint-to-SQL Server/Dataverse provider adapter with data migration and equivalence tests; CKAN can be deployed unmodified **only with its independent PostgreSQL, Solr and Redis**. An optional custom CKAN 2.12 `file-keeper` storage adapter connects its FileStore to SharePoint Libraries; see below.

## Authoritative fields versus projections (no double-writer)

| Field/domain | Authoritative home | Projection / derived location |
| --- | --- | --- |
| DatasetID UUID, ResourceID UUID, organization, title, description, tags, licensed use, metadata revision | CKAN_Datasets, CKAN_Resources and linked SharePoint lists | Mirrored *identity and navigation only* into document-library columns |
| Actual bytes, file version, file size, file creation metadata, content hash after verified readback | SharePoint document object + validated asset receipt | CKAN_Assets list as **rebuildable cross-library index**, resource `CurrentAssetID` pointer only |
| Source HREC/SSA approvals, delegations, PPG decisions | Authoritative existing CareOps PPG/Approve/Decisions and external ERM source | CKAN_GovernanceLinks **read-only evidence reference** + last verified observation |
| Access decision/grant or revoke | Authorized governance outcome plus enforced SharePoint permission | CKAN_Entitlements read model and reconciliation journal, never grants by display badge |
| Medallion promotion, transformation provenance | CKAN_Lineage and immutable versioned release manifests | File metadata includes release reference and validation state |
| Native SharePoint person/choice/managed metadata fields | UI conveniences only | Canonical values are source-qualified text IDs and vocabulary versions |

## SharePoint Lists: minimum starter schema

| List | Purpose | Essential indexed fields |
| --- | --- | --- |
| `CKAN_Organizations` | Owned dataset organisations; **not** security tenancy | `OrganizationID` unique GUID-string, `ParentOrganizationID`, `OrgCode` |
| `CKAN_Datasets` | CKAN Package-equivalent | `DatasetID` unique, `OrganizationID`, `Slug` unique within defined namespace, `LifecycleStatus`, `AccessClass` |
| `CKAN_Resources` | CKAN Resource metadata (not library files) | `ResourceID` unique, `DatasetID`, `ResourceType`, `CurrentAssetID`, `AccessClass` |
| `CKAN_Groups`, `CKAN_DatasetGroups` | CKAN groups and many-to-many links | `GroupID`, `DatasetID`, synthetic unique composite key |
| `CKAN_Tags`, `CKAN_ResourceTags` | Faceting/taxonomy links | `TagKey`, `ResourceID`, `DatasetID` |
| `CKAN_Assets` | Rebuildable, cross-library file locator / status index | `AssetID`, `ResourceID`, `LibraryCode`, `AssetRevision` |
| `CKAN_GovernanceLinks` | Minimum evidence reference only | `GovernanceLinkID`, `DatasetID`, `ResourceID`, `EvidenceStatus` |
| `CKAN_Entitlements` | Grant/expiry/revocation reconciliation, restricted | `EntitlementID`, `ResourceID`, `PrincipalReference`, `ExpiresUTC` |
| `CKAN_Lineage`, `CKAN_ReleaseManifests` | Provenance and frozen authorised publications | `LineageEdgeID`, `ReleaseID`, `DatasetID` |
| `CKAN_CommandJournal` | Retry, rollback and cross-list write recovery | `CommandID` unique, `AggregateID`, `Status`, `RetryAfterUTC` |

All IDs above are domain-controlled **single-line text UUIDs**. Use SharePoint `ID` only as a physical locator. Store `SchemaVersion`, `Revision`, `SourceQualifiedID`, `CreatedUTC`, `ObservedUTC` as appropriate. Use string versioned vocabulary codes in domain contracts, even when Choice, Person or managed metadata fields help the editing experience. Avoid transactional assumptions across lists. SharePoint ETags/If-Match support optimistic concurrency for single resources; a journal/outbox and reconciler handle cross-list writes.

## Document libraries and reusable site columns

For synthetic/non-identifiable pilot data, provision separate libraries `CKAN_Bronze`, `CKAN_Silver`, `CKAN_Gold`, `CKAN_Platinum`; optionally `CKAN_SupportingDocuments`. **Access class, not the medallion layer, controls security.** Sensitive content remains in approved restricted sources, with only a sanitised pointer in the catalogue unless specifically authorised.

| Reusable site column (internal name) | SharePoint type | Canonical meaning |
| --- | --- | --- |
| `CKAN_DatasetID` | Single line text, indexed | Parent dataset stable ID (copied from `CKAN_Datasets`) |
| `CKAN_ResourceID` | Single line text, indexed | Parent resource stable ID |
| `CKAN_AssetID` | Single line text, unique/indexed where feasible | Immutable file-asset identity, not filename/path |
| `CKAN_MedallionLayer` | Choice, optional convenience | bronze/silver/gold/platinum; also in canonical metadata |
| `CKAN_ArtifactKind` | Choice | original-extract, dictionary, specification, validation-report, analytic-aggregate, approved-release |
| `CKAN_SourceQualifiedID` | Single line text | Source identifier and version |
| `CKAN_SchemaVersion` | Single line text | Versioned input/metadata schema |
| `CKAN_ContentSHA256` | Single line text | SHA-256 computed and re-verified by trusted approved processing, **not** automatically by SharePoint |
| `CKAN_Classification` | Choice/display | Controlled classification; actual permission enforcement is separate |
| `CKAN_ValidationStatus` | Choice/display | quarantine, pending, accepted, rejected |
| `CKAN_ReleaseID` | Single line text, indexed | Immutable release manifest foreign key |
| `CKAN_GovernanceRef` | Single line text | Verified external approval reference, not authority itself |
| `CKAN_ReceivedUTC` | Date/time | Received timestamp |
| `CKAN_ProvenanceURI` | Hyperlink or single-line text | Reviewable source evidence |
| `CKAN_StorageRevision` | Single line text | Current file version in library; physical adapter only |

SharePoint standard columns `Created`, `Modified`, `Created By`, `Modified By`, `Version` and Content Type are already available and should not be recreated. Site columns and content types should be reused across libraries. Canonical interoperability does not inherit the vendor-specific column types.

Recommended **content types:** `CKAN Source Extract`, `CKAN Data Dictionary`, `CKAN Clinical Protocol`, `CKAN Validation Receipt`, `CKAN Published Data Product`, `CKAN Release Manifest`. Apply allowed types and required columns per library. **Document Sets** are optional only for related document bundles, not as substitutes for dataset/resource relational lists.

## Native SharePoint capabilities to use first

1. **Indexed list/library columns and filtered/grouped views**; default views by organisation, clinical domain, lifecycle, medallion layer, access class, custodian. 5,000 is a query threshold, not a list capacity cap; avoid large unindexed queries, excessive lookups, and per-file unique permission scopes.
2. **Modern library forms, site content types, required fields, default column values, JSON column/view formatting** for status and navigation. Formatting never confers access.
3. **Version history, draft visibility, content approval, checkout only when necessary**; content approval is not ethics/delegation approval. Remember version retention can delete historical versions; preserve mandated records and approved artefacts separately.
4. **Permission-managed libraries/sites and standard SharePoint groups**, not record-by-record broken inheritance for every clinical resource. Rights must be independently checked on physical files; Power BI entitlement remains separate.
5. **Standard Power Automate SharePoint trigger/actions**, `Send an HTTP request to SharePoint` only for supported SharePoint REST operations, create-only event logging and short idempotent flows; no premium arbitrary HTTP/Graph actions. Avoid recursion on metadata-change triggers.
6. **SharePoint Search and site pages** for broader discovery; indexing is eventually consistent. Prefer indexed list queries for exact transactional reads.
7. **Document Sets and metadata navigation** only if site configuration supports them and their value exceeds their governance/performance cost.
8. **Built-in Office document preview/co-authoring** for protocols and data dictionaries; for fixed evidence snapshots publish an immutable copy rather than coauthor in an approved revision.
9. **Optional SPFx list view command set or form customiser** for actions current SharePoint forms cannot do, after validating actual tenant deployment rights. No custom React page required on day one.

## CKAN 2.12 file-keeper: precise plan, no unsupported backend claims

### Current supported capability

CKAN FileStore uses Python `file-keeper`, with configurable named storages. Native CKAN provides local filesystem, and `ckanext-file-keeper-cloud` supports **Azure Blob, AWS S3, Google Cloud Storage and Libcloud**. It does **not** currently advertise a SharePoint Document Library adapter. **Azure Blob is not SharePoint Online**. CKAN's native FileStore and PostgreSQL catalogue are separate, as is the CKAN DataStore. Use CKAN's official source without patches.

### Preferred low-development order

**MVP:** no Python server or FileKeeper adapter. SharePoint libraries store files, `CKAN_Resources` tracks them, and a link to SharePoint (with actual permissions) permits CKAN-style resource discovery. This satisfies the SharePoint-only operational constraint.

**Portability contract now:** design `AssetStore` with operations `put/stream/readMetadata/version/removeOrTombstone/reconcile` and capability flags `streaming/partialRange/versioning/permanentLink/signedLink/atomicPut/delete`. Its TypeScript SharePoint adapter is used by SPFx. Do **not** import Python `file-keeper` into SPFx.

**Future CKAN-native PoC:** create separate `ckanext-careops-sharepoint-storage` as an **external CKAN extension**, implementing `file-keeper` `Storage` / `SettingsFactory` / `UploaderFactory` / `ReaderFactory` / `ManagerFactory`. The adapter maps file location to stable SharePoint `AssetID` and library item, streams bytes, checks hashes, manages version and deletion semantics, and exposes private-resource download correctly. Use CKAN's `file_create` tracking API; do not bypass its file records or authorisation. CKAN itself remains unmodified.

**Security gate:** CKAN Python storage service needs an approved identity with SharePoint read/write privileges and a hosted runtime. A site-owner browser cookie alone is not a general unattended server credential. Entra application registration/delegated credentials and hosting approval may be needed. Separate this **future** admission from the zero-admin SharePoint MVP. Do not manufacture permanent public SharePoint links for private resources.

**PoC conformance matrix:** upload/download/stream large file; storage metadata, checksum, content type; version collision and concurrency; auth deny; private link expiry; nested paths; failure/retry; rate limit; delete/tombstone; Site Collections/files/versions; CKAN 2.12.1 upgrade fixture; no CKAN upstream patch.

**Alternative if native CKAN is later mandatory:** use direct controlled external SharePoint links initially. This requires substantially less development than a custom storage adapter, but CKAN does not then own the upload lifecycle.

## Minimise development and improve maintainability

* First prove a **no-SPFx** experience with SharePoint native Lists/Libraries, site pages and standard Power Automate; build only the missing user journeys later.
* Reuse existing CareOps-Approve, PPG, Decisions and RIMS **authorities** through versioned references. Do not copy their data or create another approval flow.
* Reuse Microsoft-provided SPFx 1.24.1 scaffolds and official React/Fluent UI versions; avoid modifying upstream packages. Test isolated dependency-update canaries and committed npm lockfiles.
* Reuse CKAN upstream, and later documented CKAN extensions `ckanext-scheming`, `ckanext-dcat`, `ckanext-harvest`, `ckanext-xloader` **only after** matching-version compatibility tests. Do not port CKAN internals into SharePoint or imply a CKAN server is presently deployed.
* Use declarative **site provisioning definitions** and source-controlled mapping contracts, not manual recreation or an invented universal SQL layer.
* Publish/validate a small cross-backend conformance suite for canonical IDs, CRUD, filters, permissions, ETag conflicts, migration export, release and rollback. Future Dataverse or SQL Server adapters are tested to the same interface.
* Keep Power BI PPU, Fabric/OneLake, Dataverse Premium, Syntex, Copilot and paid connectors deferred.

## Indicative engineering effort (person-days, *not* a delivery promise)

Assumes one competent Microsoft 365 developer, accessible SharePoint site owner, existing standard connector permissions, synthetic test data and no newly required external hosting. Ranges overlap only as noted; these are planning estimates, **not observed durations**.

| Increment | New engineering effort | Notes |
| --- | --- | --- |
| Permission and platform feasibility + architecture mapping | 2–4 | Check catalogue/site permissions, content types, standard triggers, app catalogue |
| Lists, libraries, reusable site columns, native views and scripted provisioning | 3–6 | Schema/fixtures, folder/library permissions and index tests |
| Canonical domain types, minimal SharePoint adapter + integration tests | 5–9 | UUIDs, paging, ETags, asset links, bounded writes |
| Synthetic medallion staging, lineage and Platinum release manifest | 5–9 | No heavy distributed compute or patient records |
| Minimal CareOps governance reference and approval-state reconciliation | 3–6 | Existing service contracts/read-only evidence; native permissions remain gated |
| Basic native SharePoint catalogue pilot + acceptance testing | 3–6 | Sample datasets, negative permission tests, accessible views |
| **Total functional SharePoint-native MVP** | **21–40 person-days** | Excludes organisational decision/sign-off lead time, licences and unknown tenant barriers |
| Optional custom SPFx portal beyond native views | **+6–12** | Only for confirmed UX/functional gaps |
| Optional real CKAN SharePoint `file-keeper` adapter PoC | **+10–20** | Separate Python extension, backend authentication, error/streaming/tests; excludes full CKAN infrastructure |
| Optional real CKAN production integration | **+10–25 or more** | PostgreSQL, Solr, Redis, hosting/operations, metadata synchronisation, security and approvals, excluding tenant lead time |
| Later Dataverse/SQL Server provider and controlled migration | **+10–25 each** | Depending on schema, permissions, volumes, licensing and migration gates |

**Absolute minimum pilot:** a subset of `CKAN_Datasets`, `CKAN_Resources`, a SharePoint document library with site columns, 3–5 native filtered views, a published form and 5–10 fictional resources. A simple demonstration of this subset could be scoped at **5–10 engineering person-days**, excluding tenant access and governance approvals. It would **not** qualify full CareOps/CKAN interoperability or clinical production readiness.

## Next planned work packages

1. **SP-01** — Qualify real CHHHS tenancy: site owner/List and Library provisioning rights, supported content types, standard flow rights, app catalogue, file permission and retention rules. No admin bypass.
2. **SP-02** — Build declarative schema + seeded fictional objects and expected column/internal name/readback checks.
3. **SP-03** — Implement canonical `Dataset/Resource/Asset` ports and SharePoint REST adapter; test paging, concurrent updates, permissions and upload/readback hashes.
4. **SP-04** — Native UX, filters, search, status views, governance reference links and short standard flow; defer custom web parts.
5. **SP-05** — Bounded Bronze→Silver→Gold→Platinum synthetic data promotion and lineage/immutable release gate; record unsupported compute explicitly.
6. **SP-06** — Repeatable acceptance: source boundary, versioning, negative entitlement, access expiration, recovery, file changes and cross-provider conformance.
7. **FK-01** — Isolated custom SharePoint `file-keeper` storage prototype after core pilot, only when native CKAN server use is selected; no upstream modification.
8. **FK-02** — Independently test CKAN backend/auth/tenant permissions, service hosting and document-library column roundtripping; make it optional behind feature flag.

## References

- CKAN FileStore: https://docs.ckan.org/en/2.12/maintaining/filestore.html
- CKAN cloud adapters: https://github.com/ckan/ckanext-file-keeper-cloud
- CKAN DataStore: https://docs.ckan.org/en/2.12/maintaining/datastore.html
- SharePoint site columns/content types: https://support.microsoft.com/en-au/sharepoint/libraries/plan-content-types-and-workflows-in-sharepoint
- Library versioning: https://support.microsoft.com/en-us/sharepoint/lists/documents-and-library/how-versioning-works-in-lists-and-libraries
- SharePoint view thresholds: https://support.microsoft.com/en-us/sharepoint/lists/data-and-lists/list-view-threshold-for-large-lists-and-libraries
- SharePoint JSON formatting: https://learn.microsoft.com/en-us/sharepoint/dev/declarative-customization/column-formatting
- SharePoint Document Sets: https://support.microsoft.com/en-au/sharepoint/libraries/introduction-to-document-sets

## Coding-agent runbook: what to implement first (AG-00 through AG-10)

**This is a source-only execution order; no CHHHS native system or account has been inspected.** Work in the existing CareOps repository. Do not create a duplicate Conductor, CKAN fork or sibling approval engine. Use this alongside `conductor/tracks/ckan_catalogue_20261106/plan.md`.

### Initial dependencies and authority gate

1. **AG-00 / source and ownership:** Read `README.md`, `docs/development-and-delivery.md`, `portfolio/module-catalog.md`, `portfolio/repos.json`, `portfolio/power-platform-alm.json`, `profiles/chhhs/README.md`, `conductor/tracks.md`, catalogue ADRs/contracts and sibling Approve, Decisions, PPG and RIMS ownership. Reconcile active `main` versus open PR #275. Existing modules keep their currently approved integration/release boundaries; new catalogue code is intended in `modules/careops-catalogue/`.
2. **AG-01 / local tools:** Check Git/gh, Gemini CLI, pinned Conductor gitlink, Node 26/npm and available test tools. Record exact installed versions and source SHAs. Do not install SPFx or CKAN yet; build a clean synthetic test harness first. Use project-scoped skills rather than global changes.
3. **AG-02 / site preflight:** Obtain approval to inspect a **designated non-production CHHHS site**. Verify read/write role, approved Entra delegated client ID and consented SharePoint scopes, site/list/field permission readback, Power Automate standard connector/DLP policy and records/privacy ownership. If any element is denied or unknown, stop cloud writes and continue offline only.
4. **AG-03 / canonical schema:** Define backend-neutral `Dataset`, `Organization`, `Resource`, `Asset`, `LineageEdge`, `ReleaseManifest`, storage ports and fixtures. Use stable UUIDs, version/conflict tokens, classifications, provenance, exact failure states and no vendor data types in the domain.
5. **AG-04 / narrow provisioning:** With written authority, create **only** `CKAN_Organizations`, `CKAN_Datasets`, `CKAN_Resources` Lists and a single `CKAN_PilotAssets` Library; add shared columns and three indexed read views. Re-run in no-change mode, inspect internal field names and rollback in test site. Do not provision the full 13-List/five-Library target before that proof.
6. **AG-05 / SharePoint adapter:** Backend-neutral data contract plus thin REST provider. Test pagination, indexed filters, ETags/If-Match, idempotent writes/journal, versioned asset links, readback checksum and permission-denial handling. Cross-list writes have no atomic SQL transaction guarantee.
7. **AG-06 / user journey:** Use native SharePoint List forms, libraries, column formatting, content types and site pages for browse, metadata change and permission-protected resources. Specify user task and failed acceptance criterion before adding SPFx. Never use client-side hiding as security.
8. **AG-07/08 / governed medallion:** Read-only references to Approve/Decisions/PPG/ERM; build synthetic Bronze/Silver/Gold/Platinum promotions, lineage, suppression validation, exact human release evidence, access revocation and restoration.
9. **AG-10 / operational readiness:** Named clinical/data custodians, digital owner, records/cyber/privacy review, retention/recovery test, negative access cases and support model. Source tests are not deployment authorisation.

**Noncritical branches:** `AG-09` optional SPFx portal; `FK-01` external Python CKAN 2.12 `file-keeper` adapter and native CKAN services; `MIG-01` later Dataverse/SQL providers. None should block a useful native SharePoint MVP.

### Permissions matrix to verify before provisioning

| Need | Site/account entitlement | Separate condition | Action if absent |
| --- | --- | --- | --- |
| Read site/list/library structure | Read or site membership | An approved CLI delegated client and SharePoint read scope | Use authorised UI read-only or IT request |
| Create List, Library, site columns/content types | Site Manage Lists/Design or Full Control (verify) | CLI create-list scope documented as SharePoint delegated **AllSites.Manage**, field-add as **AllSites.Write**; consent not implied by site ownership | Test UI/standard SharePoint flow only after approval; request scoped approved app/consent |
| Manage library access | Manage Permissions/Full Control | Data owner authorises security boundary; avoid mass broken inheritance | Keep restricted and public files in separate approved libraries/sites |
| Run standard Power Automate | Permitted maker/environment and SharePoint connection | Tenant DLP, credentials/ownership, flow retry and retention | Human process until approved |
| Deploy SPFx | Already enabled site collection app catalogue and site deployment rights | If not enabled, SharePoint administrator must enable it | Native views remain MVP |
| Operate CKAN `file-keeper` | Approved hosted Python service and site file permissions | Native CKAN PostgreSQL/Solr/Redis, safe service identity, organisation-approved authentication | Defer FK-01, keep SharePoint links |

**Do not put** patient records, staff identifiers, tenant IDs, real site URLs, CLI tokens, work emails or production readback in public Git. Keep private receipts in an approved restricted location and commit only sanitised pass/fail outcomes. GitHub Actions artifact storage exhaustion is an infrastructure blocker to report, not a reason to weaken checks.

### CLI/tool choices

| When | Tool | Notes |
| --- | --- | --- |
| Immediately | Git, optional `gh`, Gemini CLI and pinned Conductor | Existing `.agents/plugins/conductor`; avoid running setup over existing tracked context |
| Preflight | Node 26/npm and `@pnp/cli-microsoft365` (`m365`) | The CLI requires an existing authorised Entra application ID and user consent/scopes; not automatically usable with site access alone |
| If approved alternative | PnP.PowerShell 7 | Also requires an Entra app/client ID; does not bypass CLI consent |
| Only on SPFx decision | `@microsoft/generator-sharepoint@1.24.1`, Yeoman, Heft, React 18.3.1 | Heft replaces gulp in SPFx 1.24; use exact compatible dependencies |
| Only for Power Platform packaging | .NET 10 and `pac` | Not necessary for native Lists/Libraries MVP |
| Only for future CKAN extension | Isolated CKAN-compatible Python, file-keeper and CKAN runtime | Do not assume parent Python 3.15 compatibility with CKAN |

Run locally, before attempting any cloud activity:

```sh
git status --short
git submodule status -- .agents/plugins/conductor
git ls-tree HEAD .agents/plugins/conductor
node --version
npm --version
gemini --version
m365 version
```

With explicit approval and a **pre-existing consented** CHHHS delegated app, use the following **read-only** preflight, storing actual binding values privately:

```sh
m365 login --appId "$CHHHS_ENTRA_CLIENT_ID" --tenant "$CHHHS_TENANT_ID" --authType browser
m365 spo web get --url "$CHHHS_TEST_SITE_URL" --withPermissions
m365 spo list list --webUrl "$CHHHS_TEST_SITE_URL"
m365 spo field list --webUrl "$CHHHS_TEST_SITE_URL"
```

Provisioning commands such as `m365 spo list add --title CKAN_Organizations --baseTemplate GenericList --webUrl "$CHHHS_TEST_SITE_URL"` are **write operations** and may only be invoked after the explicit non-production stage gate, using exact installed-version `--help` checks and an idempotent provisioner. Do not accept a different organisation's app login as CHHHS authorisation.

Gemini CLI can discover upstream Conductor skills as local workspace Agent Skills. After the existing gitlink checkout, link individual upstream `skills/*` directories with supported `gemini skills link <path> --scope workspace` (verify installed CLI help) or interactive `/skills link <path> --scope workspace`; then `gemini skills list --all`, smoke-test an existing-track status operation, and verify no existing Conductor files are overwritten.

### Deliverable and acceptance map

| Stage | Output | Definition of done |
| --- | --- | --- |
| Local bootstrap | Exact tool inventory, Conductor smoke receipt, contract tests | Clean checkout, no clinical/tenant material, no new upstream forks |
| Read-only tenant feasibility | Permission/consent/DLP matrix plus private evidence | Every unknown explicitly marked, no writes |
| Approved pilot schema | 3 Lists, 1 Library, site columns and views plus dry-run rollback | Exact internal-name/readback and repeatability confirmed |
| Working vertical slice | Create/list/edit dataset, link file, deny unauthorised reads | Runnable tests and native end-user task acceptance |
| Expanded MVP | Four medallion layers, governed releases and reconciliation | Deterministic promotion, disclosure and rollback tested |

### Initial coding-agent assignment

> Work in `edithatogo/careops` on the existing CKAN catalogue Conductor track. Implement **AG-00 and AG-01** only: reconcile main and PR #275, catalogue ownership, upstream modules and Conductor pin; inventory the local CLI tools and supported versions; create backend-neutral canonical schema/fictional fixtures and a runnable source-only test plan. Do not connect to CHHHS, create new tenant apps, provision Lists, install premium/Copilot components, patch Conductor/CKAN, change sibling modules or store private records in Git. Commit a bounded PR with exact evidence, limitations, rollback notes and blocked permission requests. Stop before any cloud write.
