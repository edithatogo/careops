# CareOps: standard core and optional capabilities

Current direction, 8 November 2026. This decision supersedes the old polyrepo,
premium-first and Copilot-first setup guidance. It changes source architecture
and implementation priorities; it does not claim a new native deployment.

## Product and source boundaries

CareOps is one maintained source home with independently usable capabilities.
Source consolidation does not require one operational database, one release,
one tenant environment or installation of the whole suite. Every module and
submodule is optional. A logical parent describes product ownership, not an
installation dependency. Existing module paths remain stable during this change.

`portfolio/module-capabilities.json` records the current selection contract:
no modules enabled by default, a `standard-m365` default, explicit premium
extensions, source maturity and standard routes. `portfolio/repos.json` remains
the authority for physical source placement. Neither establishes native readiness.
The simulation module is outside this assessment and is unchanged.
Some standard routes are target designs rather than packaged native implementations;
consult each entry's `standardImplementation`. In particular, the dedicated Decisions
SharePoint register adapter and future Workforce/Interests packs remain to be built.

| Capability | Owns | Optional connections |
| --- | --- | --- |
| Approve | Requests, routing, response capture and escalation | Decisions, policy references and workforce requests |
| Decisions | Bodies, recommendations, decisions, conflicts at meetings and actions | Clinical Hub workspace, approvals and policy references |
| Clinical Hub | Optional Decisions workspace for papers, meetings, minutes, correspondence and follow-up | Can operate standalone; select an external or local decision provider |
| PPG | Policy/procedure/guideline identity, drafting, consultation, approval, issue, review and retirement | Standards mappings and accreditation evidence packs |
| Improvement | Initiatives, interventions, measures, benefits and review | RIMS research outputs, Catalogue dataset references, Costing and Process |
| RIMS | Research/publication records, attribution and reporting | Improvement initiative references and research dataset catalogue entries |
| Catalogue | Dataset descriptions, resources, ownership, access conditions and discovery | Clinical registries and every CareOps dataset; optional lineage and release ledger |
| Process, Incidents, Costing and Finance | Their existing analysis and reporting boundaries | Consume approved references or minimised snapshots |
| Interests, Workforce | Planned declaration/management of interests, credentialing administration, onboarding, job planning and outside work | Approve, Decisions, PPG and catalogue metadata |

Clinical Hub is a **logical submodule of Decisions with standalone delivery**.
Keep `modules/clinical-hub-core` until package/build/import consumers are qualified
for a physical move. One meeting, action or decision has one authoritative owner;
the workspace links to it. It must not require installing Decisions to prepare
a meeting or maintain its own bounded workflow.

PPG is the policy management system. Standards and accreditation are selectable
capabilities; routine policy work must succeed with both absent. Preserve current
source mappings and tools while consolidating duplicated utilities behind a
versioned development package only when both consumers pass their standalone tests.

Improvement, RIMS and Catalogue form a useful chain: an initiative can link to a
study or publication, which can link to datasets and resources. Their status and
authority remain distinct. Research approval is not improvement completion;
publication is not dataset release; a catalogue entry is not permission to access.

## Catalogue meaning

The catalogue is CKAN-inspired: **dataset -> one or more resources**. A clinical
registry is a dataset kind, not a separate competing catalogue. CareOps registers,
event extracts, reference datasets, analysis outputs and research datasets can
all be described. A record describes the dataset; it does not ingest patient rows.

Use stable domain UUIDs, owner/steward roles, description, purpose, schema/dictionary,
source-qualified identity, revision, coverage, access conditions and resource links.
Keep location/version bindings private. A restricted dataset may need a restricted
metadata entry as well as restricted file bytes. SharePoint permissions enforce
access; an `AccessClass` value does not. Optional lineage, vocabularies and release
manifests can follow when they solve a demonstrated requirement.

## Non-premium delivery contract

Non-premium means no additional premium dependency beyond the organisation's
held Microsoft 365 rights. It does not mean every Microsoft service is free or
every tenant permits every standard connector. Check the selected feature once,
record the result, and keep a working manual route.

| Function | Default route | Retained optional extension / limitation |
| --- | --- | --- |
| Structured records | Lists/SharePoint, native forms, typed columns, indexed views | Full Dataverse for workloads requiring its separately qualified guarantees |
| Intake | Native Lists forms or Microsoft Forms plus a standard flow | Premium apps and custom connectors only when explicitly selected |
| Routing and human responses | Standard SharePoint/Approvals actions or recorded manual response | No indefinite waiting flow; persist long-lived workflow state in the register |
| Papers, policies and letters | Maintained Word templates, library metadata and manual narrative editing | Copilot structured document generation and Word Online (Business) connector are optional |
| Follow-up tasks | Existing standard SharePoint/Basic Planner pattern | Planner premium features are a separate selection; task completion does not close the authoritative matter |
| Reporting | Native views, Excel and local/static reports | Power BI collaboration/sharing requires its own entitlement check |
| Integration | Versioned JSON/CSV/resource references and standard connector operations | Premium HTTP/custom connectors, service APIs and automation adapters |
| Assistance | Deterministic validation and human preparation | Local models, Copilot, AI Builder and other model providers are off by default |

Do not build a new core on Dataverse for Teams: Microsoft's published retirement
path makes it unsuitable as the long-term free workaround. Preserve historical
implementations and recovery records; migration needs its own qualified plan.
Do not delete existing Dataverse, custom connector, AI or Copilot source merely
because it is not selected. Label it, isolate its installation and test its absence.

The existing full-Dataverse credentialing register remains a separate optional
implementation. Lists can support administrative intake, checklists, declarations,
reviews and document preparation. They are not automatically equivalent to the
existing atomic decision/history/outbox, privilege and recovery contract. Keep
authoritative credentialing changes on the qualified existing system until a
selected replacement demonstrates the required behaviour.

## CLI ownership: one tool per job

| Job | Route | Required for ordinary operators? |
| --- | --- | --- |
| Source, branches, PRs | Git/GitHub; `gh` only with its own repository authentication | No |
| Offline schema generation and tests | Explicit repo-local Python 3.15.1 | No |
| Lists creation without tenant administration | Native SharePoint UI using the generated column dictionary | Setup only |
| Registered SharePoint site script/template | SharePoint Online Management Shell, already-authorised administrator | No |
| Existing scoped SharePoint reads/writes | The already-qualified CLI for Microsoft 365 or PnP route for that target | No; do not introduce a second login route routinely |
| Power Platform solution pack/unpack/import/export | Qualified PAC route; each native import separately scoped | No; PAC does not provision ordinary SharePoint Lists |
| Power BI workspace/report lifecycle | Existing qualified reporting tool and entitlement | No; separate from PAC and Power Automate licensing |
| Daily workflow | Lists, Forms, SharePoint, Word and Teams surfaces | Yes, selected native surfaces only |

Tool installation, local help and authentication are separate from permission to
operate on a target. PnP or CLI for Microsoft 365 may require an Entra application
and consent; they are not prerequisites to the manual setup route. Do not switch
clients to evade a native write hold. Reuse a qualified session rather than running
multiple CLIs against the same live operation.

## Lean governance and evidence

Use one delivery record per bounded change: purpose, owner, source revision,
selected profile, affected resources, test/result references, unresolved limits,
rollback and the final disposition. Link existing evidence instead of copying it
into every module, Conductor document and release pack. Record a material result
once and reuse it while its source, configuration and scope remain unchanged.

Routine source edits and reversible offline generation proceed under the task's
standing authority. Business approval belongs at a real decision, issue, release,
access change or materially new external effect. A committee decision must not
be followed by an invented second approval simply to copy its result into a list.
Security checks remain automated and fail closed. Keep only required protected
merge gates; optional modules cannot become release gates for an unrelated module.

Separate four useful states: source prepared, source verified, native configured,
and operationally accepted. A billing refusal means **not executed**. A checksum
proves bytes, not approval. Human edits, failed checks and missing observations
remain visible. Existing email-specific approval rules continue to apply.

## Roadmap and success measures

1. **Make installation predictable:** selected-module manifest, catalogue setup
   generator, documented CLI ownership and the same schema used for setup/readback.
   Measure time from clean checkout to usable fictional List and manual effort.
2. **Close source fragmentation:** execute the source migration plan, reconcile
   research predecessors and reuse HWCC requirements. Keep MCHS calculation logic
   external. Measure duplicate implementation and drift, not number of imports.
3. **Deliver connected records:** Improvement <-> RIMS <-> Catalogue references,
   policy/version links, and Decisions/Clinical Hub ownership with missing-provider
   tests. Measure repeated entry and time to find authoritative evidence.
4. **Deliver forms as small independent packs:** declarations/management of
   interests; onboarding; outside work; job planning; then the qualified credentialing
   pathway. Each works manually before optional automation is introduced. The term
   `COO` remains unresolved; do not silently relabel it or invent its form fields.
5. **Add optional depth:** standards/accreditation, richer analytics, advanced
   search, selected premium integrations and model assistance. Promote only where
   measured benefit exceeds entitlement, maintenance and assurance cost.

Use [the executable migration plan](source-migration-plan.md),
[SharePoint setup and archives](sharepoint-bootstrap.md), and
[portable security/CI](portable-ci-and-syndication.md).

## Current platform references

- [Standard SharePoint connector](https://learn.microsoft.com/en-us/connectors/sharepointonline/)
- [Power Automate licensing](https://learn.microsoft.com/en-us/power-platform/admin/power-automate-licensing/faqs)
- [Word Online (Business) connector classification](https://learn.microsoft.com/en-us/connectors/wordonlinebusiness/)
- [Planner connector and Basic plans](https://learn.microsoft.com/en-us/connectors/planner/)
- [Power Platform changes, including Dataverse for Teams](https://learn.microsoft.com/en-us/power-platform/important-changes-coming)
- [Power BI sharing licences](https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-share-dashboards)
