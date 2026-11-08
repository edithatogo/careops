# CareOps Catalogue — CKAN-based design, SharePoint-native implementation

**Decision date:** 2026-11-06; CKAN design basis clarified 2026-11-08. **Status:** proposed source design, *not an installation, tenant authorisation or released service*.  
**Track:** [`ckan_catalogue_20261106`](../../conductor/tracks/ckan_catalogue_20261106/plan.md). CKAN remains the explicit reference model and functional blueprint; the track identifier **does not imply running CKAN**.  
**Owner:** in-tree reference-source candidate `modules/careops-catalogue` under CareOps; separate runtime, service ownership and deployment approval.

## CKAN reference model and functional baseline

**CareOps Catalogue is based on CKAN's catalogue model and core user journeys, implemented using native SharePoint Lists and Document Libraries.** This is an intentional CKAN-inspired product, not an unrelated document register with a historical CKAN label. The reference applies to the catalogue capability, not to the whole CareOps suite.

The conceptual structure is **Organisation/publisher → Dataset (Package) → Resource**, with groups and tags providing cross-cutting discovery. In CKAN, a dataset combines metadata with related resources; resources can be stored files or external links, and “package” is the API/internal term for a dataset. This is the model to retain, not CKAN's deployment stack. See the official [user guide](https://docs.ckan.org/en/latest/user-guide.html) and [API terminology](https://docs.ckan.org/en/latest/api/index.html).

### Reference-to-implementation mapping

This table records intended design, not feature parity already delivered. **M1 remains the minimum core; later rows do not become new M1 completion gates.**

| CKAN reference concept or journey | CareOps / SharePoint interpretation | Delivery boundary |
| --- | --- | --- |
| Organisation and dataset ownership | Reuse an authoritative organisation/publisher reference; add `Catalogue_Organizations` only if necessary. Keep ownership distinct from actual SharePoint permissions. | Owner metadata in M1; richer organisation mapping only when needed |
| Dataset / Package | `Catalogue_Datasets` is the catalogue entry, with a stable DatasetID, description, owner, source and lifecycle. It is not a folder or an individual document. | M1 |
| Resource belonging to a dataset | `Catalogue_Resources` preserves DatasetID and ResourceID and points to one file asset or an external resource. A dataset can have multiple related resources. | M1; existing relationship and locator validation applies |
| File upload versus external resource link | `Catalogue_Assets` holds bytes and library metadata; Resource records describe both files and links. An asset is a storage detail, not a replacement for the Resource concept. | M1; no CKAN FileStore/file-keeper dependency |
| Groups and tags | Curated thematic collections and descriptive keywords remain distinct from owning organisations and access-control groups. Reuse columns, vocabularies and views rather than require extra Lists immediately. | M2 controlled metadata; richer grouping only when justified |
| Find a dataset, inspect its metadata, then choose a resource | Dataset-centred native forms/pages and resource views, with permission-checked preview, download or external launch. Do not reduce the core to a file browser. | M1; supported native previews only |
| Search and facets | Start with indexed native views and filters; qualify unmodified PnP Modern Search only for a demonstrated advanced-discovery gap. | M1 basic discovery; M4 advanced facets |
| Metadata maintenance and controlled publishing | Preserve the intent of a maintained catalogue, using SharePoint versions and existing accountable CareOps governance. A status label is not an access grant or approval. | M1 safe editing/withdrawal; M2 stronger release evidence |
| CKAN authorisation | The design borrows the need for controlled ownership and access, not CKAN's user/role implementation. Actual SharePoint and source-system permissions remain authoritative. | Deliberate platform adaptation; never imply role equivalence |
| CKAN DataStore, Action API and extension ecosystem | These are not implemented by Lists, library storage or JSON exports. No full parity, drop-in compatibility or CKAN extension support is claimed. | Explicitly outside the delivery roadmap |

The permission distinction is grounded in CKAN's [authorisation model](https://docs.ckan.org/en/latest/maintaining/authorization.html). Its [DataStore](https://docs.ckan.org/en/latest/maintaining/datastore.html) is a structured-data query service, separate from whole-file storage; neither capability should be inferred from similarly named CareOps metadata.

**CareOps-specific additions:** PPG/Approve/Decisions evidence links, clinical stewardship, cross-module discovery and Bronze/Silver/Gold/Platinum provenance/publication stages are our adaptations. They are not claimed as CKAN core conventions. Optional DCAT exports are a separate standards mapping, not evidence of CKAN API compatibility.

**Instruction for maintainers and coding agents:** use CKAN as the reference for catalogue vocabulary, information architecture and user journeys. Record each material difference as a SharePoint adaptation, CareOps addition or deliberate omission, with its milestone and reason. The selected scope and commissioning gates control delivery; this mapping neither mandates every CKAN feature nor authorises a runtime, UI clone, dependency or source-code import. Reference documentation may describe development versions; it is not a selected software dependency. Any later reuse of upstream code would require a separate licence/provenance review.

## Architecture decision — core before layering

Use SharePoint Online as the **application platform** for this CKAN-inspired catalogue rather than CKAN as an application whose database must be replaced. Reuse **native modern SharePoint Lists, Libraries, forms, site pages, views, permissions and standard Power Automate**. No bespoke SPFx React app, native CKAN stack, `file-keeper` adapter, custom middle-tier web service or CKAN Action API is in the roadmap.

**Metadata store:** proposed `Catalogue_Datasets` List and `Catalogue_Resources` List, with stable `DatasetID`/`ResourceID` UUID strings, source reference, revision and permission classification. Use an existing authoritative organisation taxonomy rather than create a separate register; `Catalogue_Organizations` is conditional.

**File store:** `Catalogue_Assets` Library with document/site columns for `DatasetID`, `ResourceID`, `AssetID`, file type, origin/version, information classification, provenance and approved state. The library is authoritative for bytes and physical file versions; the Resource List is authoritative for abstract resource metadata. Mirrored IDs are joins, **not second writers**. Content types, version history, metadata defaults and library security operate natively.

**Presentation:** one SharePoint modern site page with List and Library web parts, native Microsoft Lists registration form, indexed filtered views, metadata and built-in preview. Optional PnP Modern Search only after a demonstrated need for facets, a permitted app catalogue and version/security qualification. Search indexes are asynchronous and never access control.

**Orchestration:** SharePoint list rules and standard Power Automate actions, introduced only to remove a measured manual step. Existing CareOps Approve/Decisions/PPG and relevant external authorities remain the owners of approvals and delegations. Do not create a new approval registry.

**Portability:** stable identifiers, source-qualified versioned data contracts and independent snapshot/export tests keep a later SQL Server/Dataverse provider switch possible. **No speculative replacement database or provider implementation is needed now.** Future migration still requires a new storage adapter, security translation, data reconciliation, testing and cutover.

The [physical inventory](../../portfolio/careops-catalogue-sharepoint.v1.json) is a **proposed schema** and not a mandate to provision every entity. Naming was changed from historical `CKAN_*` plans before any native deployment. The earlier [CKAN backend ADR](adr-ckan-core-and-backends.md) is **superseded for current roadmap** and retained only for architectural history. That supersession rejects the runtime approach, not CKAN as the catalogue's design basis.

## Capabilities gained by not running CKAN

| Capability | SharePoint/CareOps-native opportunity | Why a CKAN-centred integration was harder |
| --- | --- | --- |
| Office collaboration | Co-author versioned protocols, dictionaries, reports and templates; attach metadata in the same library | Separate authentication, file lifecycle and potentially duplicate storage/permissions |
| Identity and permissions | Use existing SharePoint sites/groups/permissions for actual resource access, separated by security boundary | CKAN user/org roles and SharePoint entitlements would require continuous reconciliation |
| Governance and source-of-truth | Link PPG, Approve and Decisions evidence in their existing M365 sites without duplicating their decisions | Additional CKAN workflows and bidirectional synchronisation |
| Document lifecycle | Native content types, required columns, version history, drafts and controlled content approval (not clinical approval) | Custom storage/CKAN FileStore adapter to reproduce Office-native document behaviour |
| Search/navigation | Search across authorised SharePoint content and reuse modern pages/web parts, with optional upstream PnP Modern Search | CKAN search indexes only CKAN-registered datasets unless external harvest and identity mapping are added |
| Teams and Planner | Embed approved Lists and link existing tasks/meetings without another app host | External navigation and duplicated context |
| Reusable configuration | Declarative Lists/columns/views and standard flows, Microsoft-hosted updates | Maintain CKAN server, PostgreSQL/Solr/Redis, extension compatibility, hosting, patching |
| Cross-module discovery | One small reference catalogue spanning source-qualified data products without acting as a new central data lake | CKAN catalogue/extension model may encourage re-import and second records of authority |

Trade-offs: SharePoint is **not** CKAN DataStore, a transactionally consistent relational database, a general-purpose analytical engine or a public open-data API; nor are List versions an immutable compliance ledger. If a real user requirement for public harvesting, queryable bulk tabular datasets or very high-cardinality relationships emerges, reassess platform choice independently rather than expanding the initial SharePoint build indefinitely.

## CareOps capability integration map

**Rule:** One authoritative record per concern. Catalogue records a **discoverable pointer and approved read-model metadata**, not a duplicated data copy. All consumers are optional, no module is a prerequisite to the basic catalogue.

| CareOps capability | Authoritative owner and assets | Catalogue projection / value | Release layer / gate |
| --- | --- | --- | --- |
| **Approve** (`careops-approve`) | Requests, routing, human approval events, assignment/revocation evidence | Link to request/decision with source-qualified ID, observed state, expiry; never auto-grant | M2 evidence links, M3 versioned adapter after owner sign-off |
| **Decisions** (`careops-decisions`) | Committee mandate, formal recommendations/decisions and delegated actions | Link exact decision/version and authorising record for a resource or release | M2 read-only references; M3 reconciliation |
| **PPG** (`careops-ppg`) | Policies/procedures/guidelines, their approved versions and lifecycle | Controlled-document links, exact version and status without mirroring policy masters | M2 links; M3 provenance updates; follow existing publication route |
| **RIMS** (`careops-rims`) | Publication Registry, authors and DORA Activity Registry | Discover data dictionary, publication, report or derived output via canonical source ID and owner; never re-key/replace RIMS register | M3 metadata-only feed, use existing source receipts |
| **Clinical Hub Core** | Agendas, papers, minutes and meeting actions | Discover source-qualified meeting documents, committee research packs or approved evidence snapshots | M3, retain one meeting register; reconcile Decisions overlap |
| **Process** (`careops-process`) | Event schemas, process model and conformance evidence | Catalogue minimised event schemas, published process definitions and approved aggregate outputs | M3/M4; no raw event/person records |
| **Incidents** (`careops-incidents`) | Safety signals, controlled incidents analytics and operational source | Index only approved, suppressed aggregate indicator/report and data dictionary references | M3/M4 with privacy/clinical data owner |
| **Costing** (`careops-costing`) | Unit cost assumptions, models, outputs and benefit estimates | Discover versioned methods, model inputs/assumptions, aggregate result packages | M3 optional read-only data product |
| **Finance** (`careops-finance`) | Financial records/reporting and independently authorised semantic models | Find controlled aggregated financial/operational dashboards, definitions and publication snapshots | M3, no duplicate ledger or Power BI entitlement |
| **Sim** (`careops-sim`) | Rust/Kairos engine, scenarios, seed/configuration and simulation outputs | Catalogue synthetic scenarios, input contract and approved result artefacts; **not** run simulation | M4 only; engine stays independent |
| **Legacy Migration/CGov** | Separate migration/cutover programme and legacy system authorities | Optional inventory of datasets, maps and retained evidence during approved transition | M4; no changes to N11/cutover programme |

**Minimum interface for each optional producer:** `OwnerModule`, `SourceSystem`, `SourceQualifiedID`, `SourceRevision`, `DatasetID/ResourceID` (when useful), `ResourceType`, `Classification`, `AssetReference`, `ObservedUTC`, `ContractVersion`, `AccessStatus`. A missing or stale owner response is explicitly reported and cannot produce implied publication, approval or access.

Use **stable links** and read-only handoffs before developing automated synchronisation. Catalogue links must not bypass target-site access controls. Preserve the CareOps parent's existing independent module source/release ownership and planned integration programme; new source inclusion is not a runtime dependency or native cutover.

## Incremental capabilities and stage gates

| Stage | User-visible product | Storage and logic | What is deliberately absent |
| --- | --- | --- | --- |
| **M1 — Working core** | Create/find/edit datasets and resources, open supporting file or URL; native filters and metadata | Two Lists, one Library, content types, modern site page, fictional tests | No workflow engine, no PnP Search, no SPFx, no medallion physical zones |
| **M2 — Governed resources** | Quality/completeness and owner review, disclosure/approval links, logical medallion release markers | Reference governance links, restricted assets, deterministic checks and short standard flows only where required | No second authoritative governance register, no automatic clinical approval |
| **M3 — Network of data products** | Discover approved related products and evidence from other CareOps modules | Versioned source-qualified links/optional read-only metadata adapters and DCAT export if needed | No shared database, mandatory cross-module services or replicated records |
| **M4 — Enhanced discovery** | Faceted search/verticals, cross-site discovery, product scorecards and optional collaboration links | PnP Modern Search only if app-catalog/permissions and UX requirements warrant; stable configuration release | No paid/Copilot features as baseline |

For separate access classes or retention, physical security may require independent sites/libraries rather than a shared `Catalogue_Assets` library. A logical medallion column is **not** an information security boundary.

## Future feature radar

See [short-, medium- and long-horizon assessment](platform-dependency-radar.md). Production requires a clear user gap, licence and site/tenant authorisation, data classification, supported APIs, current-version test and rollback. Preview/dev features are never promoted simply because announced. Premium and Copilot remain **future considerations out of scope**.

## Source-only / operational gates

- Versioned provisioning manifest; dry-run, exact internal-name/index/content-type readback, safe no-change reruns and rollback, fictional data and current-head CI.
- Verify native permissions, access/denial, metadata exposure, SharePoint indexing freshness, file version retrieval, publication/withdrawal and recovery in approved environment before calling it operational.
- No unapproved raw clinical data, patient/personnel records, tenant identifiers, credentials, private site URLs or real approval decisions in public Git.
- Existing CareOps modules, delivery tracks, history, service owners and data remain unchanged. The catalogue is a **reference layer**, not their replacement.

## References

* CKAN user guide — catalogue concepts and user journeys: https://docs.ckan.org/en/latest/user-guide.html
* CKAN API terminology — dataset/package and resource: https://docs.ckan.org/en/latest/api/index.html
* CKAN authorisation — a reference, not the SharePoint permission implementation: https://docs.ckan.org/en/latest/maintaining/authorization.html
* CKAN DataStore — capability deliberately not reproduced: https://docs.ckan.org/en/latest/maintaining/datastore.html
* Microsoft SharePoint modern information architecture: https://learn.microsoft.com/en-us/sharepoint/information-architecture-modern-experience
* Modern List/Library views and metadata: https://support.microsoft.com/en-us/sharepoint/data-and-lists/differences-between-modern-and-classic-experiences-for-lists-and-libraries
* SharePoint column/view formatting: https://learn.microsoft.com/en-us/sharepoint/dev/declarative-customization/column-formatting
* Microsoft Lists form configuration: https://learn.microsoft.com/en-us/sharepoint/dev/declarative-customization/list-form-configuration
* PnP Modern Search documentation: https://microsoft-search.github.io/pnp-modern-search/
* CareOps module catalog: ../../portfolio/module-catalog.md
