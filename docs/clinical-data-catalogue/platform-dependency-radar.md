# CareOps Catalogue — Microsoft 365 feature radar and dependency policy

**Assessment date:** 2026-11-06. **Status:** candidate features, not evidence of account/tenant entitlement.  
**Default product:** native SharePoint Lists/Libraries, content types and site columns, modern pages and forms, standard SharePoint connectors, with **no custom SPFx app or CKAN software stack**. No Copilot, premium feature or paid connector is a dependency. Review feature status/version at the time of actual pilot admission.

## The minimum supported core (implement M1 before enhancement work)

| Capability | Native first choice | Why it is suitable |
| --- | --- | --- |
| Metadata and relationships | Two SharePoint Lists `Catalogue_Datasets`, `Catalogue_Resources`; stable source-qualified UUIDs; indexed and filtered views | Operationally small, predictable, user-accessible |
| Documents and data products | `Catalogue_Assets` Library; library/site columns, content types, version history and preview | No custom file service; Office co-authoring and native access |
| Registration and edits | Microsoft Lists forms, SharePoint native list form configuration, default values, required columns | No application hosting or React dependencies |
| Catalogue front page | Modern Site Pages with List/Library, Quick Links and Highlighted Content web parts | Microsoft-managed components, accessible navigation |
| Discovery | Native list filters and SharePoint search initially | Low maintenance; test async index freshness and permission trimming |
| Display | JSON column/view formatting for static links, status display and simple action buttons | Configuration, not arbitrary script execution or access control |
| Simple notifications | SharePoint List rules; targeted standard SharePoint Power Automate if needed | Avoid duplicate flow engine; choose a stable service owner |
| Governance evidence | Stable URL/ID references to existing Approve, Decisions, PPG and other authorities | Does not create a duplicate clinical decision master |
| Release/quality | Versioned metadata, exact reviewed artefact and publication record, owner attestation | Human gate; no implicit approval or invented audit |
| Repeatable setup | Declarative site/library/list manifest, approved CLI/PnP provisioning and readback | Configuration as code; no custom user-facing application |

Supported modern SharePoint architecture recommends site columns/content types and rollup web parts to support navigation across sites. JSON formatting modifies **presentation only** and cannot implement authorization.

## Short horizon: after M1 works (M2; qualified standard features)

| Opportunity | Benefit | Trigger / qualification |
| --- | --- | --- |
| Managed metadata/Term Store | Common clinical domains, synonyms, dataset types, controlled source vocabularies | Existing approved term set and ability to manage/reuse; preserve stable external code/version |
| Content Type Gallery / reusable site types | Consistent protocols, dictionaries, reports, validation receipts | Reuse existing types first; global publication may need tenant roles |
| Document Sets | Group associated document bundles under shared metadata | Only when real group-of-documents task proves benefit; does not replace relational dataset/resource lists |
| Native Lists forms and conditional logic | Simplifies registration, feedback and owner review | Test actual support, permissions and anonymous/share link behaviour in target environment |
| Retention, version restoration, information classification | Assurance and source recovery | Existing organisation policy; no claim that default version history is an immutable retention system |
| Teams channel Lists tabs / Quick Links and Planner references | Clinician/custodian access to catalogue and existing tasks | No duplicated Planner task or approval authority; confirm Teams permissions |
| Schema drift and missing metadata reports | Early data quality alerts without a new service | Scheduled bounded standard flow or source-only CI check; measure false alerts and rework |
| Metadata completeness and data-product scorecards | Stewardship and content quality | Use simple SharePoint views/calculated presentation; not clinical risk-score automation |

## Medium horizon: benefit-gated optional enhancements (M3/M4)

| Opportunity | Evidence / current status | Requirement and boundary |
| --- | --- | --- |
| **PnP Modern Search** (candidate 4.25.0) | Active upstream v4 released 17 Sep 2026 with refiners, result templates, verticals and improvements | Use **unmodified upstream** package; needs approved app catalogue, possible API consent, mapped refinable managed properties and version/security/rollback tests. Not mandatory. |
| Search-schema enrichment/acronyms/bookmarks | Native Microsoft Search features | Information-architecture/ownership approval, search lag and access trimming tested |
| Cross-site SharePoint discovery | Modern pages and Highlighted Content links across permitted sites | Explicit site/member permissions; authoritatively link, do not copy governed files |
| Optional read-only source metadata feeds | CareOps module source-qualified references and lineage | Each module owner agrees contract; avoid extra warehouse, raw records or hidden synchronisation jobs |
| Standard Power Automate reconciliation | Version/expiry reminders, source-link checks, orphan resource reporting | Only proven task; proper idempotence, retries, service-owned connections and no premium connector |
| Optional graph/tree visualisation via existing list links | Relationships between data products, reports, controlled documents and governance | Start with table/views; no bespoke UI until a measurable graph-navigation need |
| Source-controlled provisioning and drift diff | Reproducible deployment and updates | PnP.PowerShell / CLI for M365 only with already consented app and rights; not a privilege bypass |
| Metadata exports (DCAT, JSON/CSV) | External interoperability without CKAN server | Implement per actual harvesting/export consumer; validate selected profile and privacy redaction |
| Existing Power BI outputs, if separately licensed | Surface approved aggregate report **links**, not new analytics engine | Verify each user's access/licence/RLS and data classification; PPU not in baseline |

## Long horizon / research canaries — never on MVP critical path

| Candidate | As of 2026-11-06 | Position |
| --- | --- | --- |
| Microsoft Graph list/item delta and cross-site discovery APIs | Public APIs with distinct application/delegated permissions | Research only for incremental sync if native Search and standard SharePoint suffice no longer |
| Power Apps Code Apps | Current Microsoft docs describe hosted code-first apps and require **Power Apps Premium/pay-as-you-go/App Pass** for users; admin enablement | **Out of scope**; no bespoke code-first frontend planned |
| Microsoft Copilot in SharePoint / Copilot Components | GA rollout/preview-to-GA during Sep–Nov 2026, with licence/credits and rollout differences | **Out of scope**. Monitor possibilities for metadata curation and Q&A but never rely on it for access/clinical approval |
| SharePoint structured document generation and associated preview Power Automate actions | Template/form based feature with restrictions, entitlements and preview connectors | **Future only**; might help PPG, Hub and publication outputs if approved, never prerequisite to catalogue |
| Fabric/OneLake/Delta/Direct Lake | Premium/capacity and other security/operational prerequisites | **Out of scope**. Later lakehouse migration evaluated separately if high-volume datasets require it |
| Power BI PPU, premium Power Automate, AI Builder, Syntex, paid process mining, SharePoint Embedded | Potential capabilities with licence/admin/runtime dependencies | **Out of scope**. Consider only on independent business case |
| SPFx new CLI/new-edit panel/canvas extension previews | Developer tooling and extensibility under evolution | Monitor but **do not implement** while no bespoke SPFx is authorised |
| Enterprise agents, MCP or semantic search over resources | Microsoft and partner tooling evolving | Future read-only development/assurance experiments only, with approved connectors and human governance |

**Preview qualification:** official status and actual enablement, exact package/version, supported cloud, licensing, API scopes, security, data classification, accessibility, performance, absent-feature fallback, rollback and documented current-head test. Candidate or release announcement != permission to deploy.

## Upgrade and dependency strategy

**Minimise code rather than build broad dependency adapters.** Microsoft-maintained native Lists, Libraries, forms and pages receive platform updates without a bespoke app recompilation. Configuration changes still require a controlled promotion, validation and rollback; avoid promises of literal zero changes.

1. Keep a small versioned *declarative information architecture*: list/library IDs, column internal names, content types, views, forms and presentation templates. Verify current native state before writing.
2. Use exact stable domain IDs and source-qualified links; SharePoint item IDs, file paths and search managed property names live only in a physical mapping manifest.
3. Keep as-is upstream PnP Modern Search **optional**, pinned to a tested `.sppkg` with checksum/approved app-catalog deployment; roll forward after tests rather than copying/forking it.
4. Existing Gemini Conductor upstream submodule is pinned in the CareOps parent and remains unchanged; avoid duplicate Conductor installation.
5. No application runtime dependencies on CKAN, React, SPFx, Python FileKeeper, Dataverse, MSSQL, Graph, Copilot or Power BI for M1.
6. Test the actual SharePoint tenant for licence, site owner rights, Entra approved client and API scopes, standard connector DLP, recovery, retention, app catalogue (only if optional PnP is selected). No unapproved consent/admin bypass.
7. Use synthetic fixtures, source-boundary validators, no-change reruns, security negative tests, current-head CI and controlled rollback. Keep operational evidence outside public Git.

## Key sources

* Microsoft modern SharePoint architecture: https://learn.microsoft.com/en-us/sharepoint/information-architecture-modern-experience
* Modern lists/libraries: https://support.microsoft.com/en-us/sharepoint/data-and-lists/differences-between-modern-and-classic-experiences-for-lists-and-libraries
* Form configuration: https://learn.microsoft.com/en-us/sharepoint/dev/declarative-customization/list-form-configuration
* Column/view formatting: https://learn.microsoft.com/en-us/sharepoint/dev/declarative-customization/column-formatting
* Site provisioning guidance: https://learn.microsoft.com/en-us/sharepoint/dev/scenario-guidance/site-provisioning
* SharePoint standard connector: https://learn.microsoft.com/en-us/sharepoint/dev/business-apps/power-automate/sharepoint-connector-actions-triggers
* PnP Modern Search 4.25.0: https://github.com/microsoft-search/pnp-modern-search/releases
* PnP Modern Search install/admin gates: https://microsoft-search.github.io/pnp-modern-search/installation/
* Power Apps Code Apps license and prerequisites: https://learn.microsoft.com/en-us/power-apps/developer/code-apps/overview
* Microsoft Copilot in SharePoint rollout: https://learn.microsoft.com/en-us/sharepoint/knowledge-agent-get-started
* Structured document generation: https://learn.microsoft.com/en-us/sharepoint/copilot-in-sharepoint-structured-document-generation
