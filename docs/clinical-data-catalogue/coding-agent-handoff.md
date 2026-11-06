# Agent execution handoff — SharePoint Lists/Libraries CKAN-compatible catalogue

**Date:** 2026-11-06. **Status:** execution-ready *plan*, not authorised production deployment. **Repository:** `edithatogo/careops`, candidate in-tree source `modules/careops-catalogue`. **Current planning PR:** #275. Use the existing CareOps Conductor submodule; do not fork CKAN, Conductor or sibling CareOps modules.

## Start here: non-negotiable sequence

1. **Read existing source and roadmap before modifying anything.** Inspect `README.md`, `docs/development-and-delivery.md`, `portfolio/module-catalog.md`, `portfolio/repos.json`, `portfolio/power-platform-alm.json`, `profiles/chhhs/README.md`, `conductor/tracks.md`, the current `conductor/tracks/ckan_catalogue_20261106/`, `docs/clinical-data-catalogue/*`, `portfolio/careops-catalogue*.json`, and ownership contracts for Approve, Decisions, PPG and RIMS. Respect other tracks; never claim that unmerged planning PR content is on `main`.
2. **Local checkout / tooling inventory** with no tenant credentials and no network writes. Record actual versions and Git commit refs, not assumed installed versions. Confirm private source and untracked data boundaries.
3. **Read-only target and auth discovery** on an explicitly permitted CHHHS test site, with an existing approved delegated CLI app, if available. No tenant IDs, source exports, access tokens, staff identities or exact site URL in public Git. Save native readback only to approved restricted records.
4. **Minimal site write gate**: only with a named CHHHS site owner/IT authorisation, create an innocuous **temporary** test list in a designated non-production site, read back internal IDs/fields/permission and remove it through an approved cleanup route. If any security or DLP permission missing, do not escalate, bypass or imply success; stay on pure offline tests and create an IT request.
5. **Canonical domain + thin SharePoint provider**, synthetic fixtures and tests. Build only `CKAN_Organizations`, `CKAN_Datasets`, `CKAN_Resources`, a `CKAN_PilotAssets` document library and shared site columns as the **first vertical slice**. The proposed full physical design includes 13 lists/five libraries, but they are *not* compulsory first-iteration objects.
6. **Native UX first**: filtered indexed list views, library columns, content types, standard web pages, read-only links. Prove what is missing before writing an SPFx shell or Power Automate orchestration. Never use URL filters, JSON column formatting or client-side state as access enforcement.
7. **Expand only after tests**: governed Bronze/Silver/Gold/Platinum artefacts, lineage, immutable approval references, fail-closed resource access, revocation and rollback.
8. **Optional** CKAN 2.12.1 `file-keeper` SharePoint adapter **after** a real CKAN runtime is authorised/provisioned with PostgreSQL, Solr, Redis and a suitable service identity. A future adapter is a standalone external extension, upstream CKAN remains unchanged.

## Critical owner/authority boundaries

| System | Authoritative content | Catalogue responsibility |
| --- | --- | --- |
| SharePoint Lists | Organisations, datasets, resource descriptions, stable IDs, link relationships | Catalogue provider backend |
| SharePoint Libraries | File bytes, native versions, physical storage and supported file-specific metadata | Asset provider, referenced by stable AssetID |
| CareOps Approve | Intake, routing, human approval workflow | Read a verified decision reference; no duplicate queue |
| CareOps Decisions | Formal committee/delegation decisions | Read a verified decision reference |
| CareOps PPG | Current controlled document lifecycle | Reference exact approved PPG version; do not recreate policy engine |
| Research ERM / HREC / SSA | Actual research ethics/governance authorities | Record externally verified approval evidence only |
| CareOps RIMS | Publication and DORA activity registries | Link to existing objects; never clone/overwrite |
| CKAN 2.12 | Official native server and file-keeper API | Optional future separate runtime, not SharePoint's primary ORM |

Keep tenant-specific configuration in a private deployment profile, not committed code. CareOps parent is the integrated **reference-source control plane**, not a mandatory shared runtime. Do not create a new standalone catalogue repo by default or change existing sibling gitlinks. Preserve each module's established roadmap and contract.

## Prerequisite toolchain — required versus conditional

| Tool | Use | Prerequisite / qualification | Install only when needed |
| --- | --- | --- | --- |
| `git` + GitHub CLI `gh` | Git worktrees, clean branch, PRs/checks/CI evidence, upstream gitlinks | Authenticated repo rights; never push clinical data | **Now** (gh optional if agent has approved GitHub connector) |
| Gemini CLI | Coding agent, Conductor Agent Skills | Agent trust/security configuration; workspace skill-activation smoke test | **Now** if selected agent |
| Existing pinned Conductor | Spec/plan/implement/review, no upstream edits | Existing `.agents/plugins/conductor` gitlink; exact reviewed SHA | **Now** (checkout existing gitlink only) |
| Node 26 LTS + npm | Local TypeScript and later SPFx 1.24.1 | Latest qualified 26 patch; separate incompatible toolchain environments | **Now** if TS; otherwise prior to SPFx |
| `@pnp/cli-microsoft365` (`m365`) | Read-only site inspection; Lists, Libraries, site columns and content-type provisioning | **Approved existing Entra client app ID, its delegated scopes and tenant consent**, plus site rights. CLI itself grants no privileges. | **Preflight** |
| SharePoint Online UI / standard SharePoint connection | Alternative native configuration and bounded REST operations | Site owner or equivalent, applicable tenant DLP and permissions | **Preflight fallback** |
| PnP.PowerShell + PowerShell 7 | Optional provisioning alternative | Requires *registered* Entra app/client ID and needed consent. Does **not** avoid the CLI authentication barrier. | **Only if existing approved** |
| `@microsoft/generator-sharepoint@1.24.1`, Yeoman, Heft | Optional SPFx web part, Heft build/package | Node 26; exact React 18.3.1, consistent 1.24.1 MS packages, site app catalogue separately enabled | **After native UX gap established** |
| `pac` CLI / .NET 10 | Optional Power Platform solution ALM / connection-reference packaging | Approved Power Platform environment and maker/solution privileges; not needed for initial Lists/Libraries | **Later if required** |
| Python + isolated CKAN 2.12 development environment | Optional external Python `file-keeper` adapter | CKAN 2.12-supported Python (test; do **not** assume parent Python 3.15 works), native CKAN services and approved host identity | **Future CKAN track only** |
| `jq` / TypeScript test runner | JSON validation, synthetic contract and adapter tests | Local tools only; no cloud rights | **Now** when tests begin |

Official docs:
- CLI for Microsoft 365 install: https://pnp.github.io/cli-microsoft365/
- CLI login needs app ID: https://pnp.github.io/cli-microsoft365/user-guide/connecting-microsoft-365/
- CLI list add: https://pnp.github.io/cli-microsoft365/cmd/spo/list/list-add/
- CLI field add: https://pnp.github.io/cli-microsoft365/cmd/spo/field/field-add/
- PnP registered app requirement: https://pnp.github.io/powershell/articles/registerapplication
- Site app catalogue permissions: https://learn.microsoft.com/en-us/sharepoint/dev/general-development/site-collection-app-catalog
- SPFx 1.24.1 compatibility: https://learn.microsoft.com/en-us/sharepoint/dev/spfx/compatibility
- Power Platform CLI on macOS: https://learn.microsoft.com/en-us/power-platform/developer/howto/install-cli-net-tool
- CKAN file-keeper: https://docs.ckan.org/en/2.12/maintaining/filestore.html
- Gemini skills: https://geminicli.com/docs/cli/skills/

## Read-only CLI preflight (illustrative commands)

Use only an **existing authorised application ID**, authenticated by the real user in the CHHHS tenant. Do **not** invent an app registration or authenticate via another university/organisation tenant. Require site-specific explicit authorisation before making changes. Commands below are suggested and their options must be verified by `--help` on the installed version.

```sh
git status --short
git submodule status -- .agents/plugins/conductor
git ls-tree HEAD .agents/plugins/conductor
node --version
npm --version
gemini --version
m365 version

# Only with a pre-approved CHHHS Entra delegated-client application:
# export CHHHS_ENTRA_CLIENT_ID=...   # user environment / secret store, NEVER Git
# export CHHHS_TENANT_ID=...         # user environment / secret store, NEVER Git
# export CHHHS_TEST_SITE_URL=...     # private deployment binding, NEVER Git
m365 login --appId "$CHHHS_ENTRA_CLIENT_ID" --tenant "$CHHHS_TENANT_ID" --authType browser
m365 spo web get --url "$CHHHS_TEST_SITE_URL" --withPermissions
m365 spo list list --webUrl "$CHHHS_TEST_SITE_URL"
m365 spo field list --webUrl "$CHHHS_TEST_SITE_URL"
```

Write operations are **not** in the preflight script. `m365 spo list add` / `m365 spo field add` are only for approved stage-specific provisioning; their documented delegated SharePoint API scopes include `AllSites.Manage` and `AllSites.Write` respectively. This is distinct from the user's **site-level** role and may require consent by administrators. Do not infer broad API scopes are granted from site ownership. For local SPFx `SPHttpClient`, the site is accessed with the signed-in user context, but SPFx deployment still needs an approved app-catalog route. For Power Automate, the standard SharePoint `Send an HTTP request to SharePoint` action is restricted to SharePoint REST endpoints.

## Gemini Conductor activation

Use existing tracked `git submodule update --init --checkout -- .agents/plugins/conductor`; verify gitlink. In the supported Gemini CLI version, link `conductor/skills/*` folders from the upstream checkout to **workspace** Agent Skills. Both the in-session `/skills link <path> --scope workspace` and the documented `gemini skills link <path>` mechanisms exist; check `gemini skills link --help` for scope. For example:

```sh
git submodule update --init --checkout -- .agents/plugins/conductor
for skill in .agents/plugins/conductor/skills/*; do
  test -f "$skill/SKILL.md" || continue
  gemini skills link "$skill" --scope workspace
done
gemini skills list --all
```

Do not execute `conductor-setup` uncritically on an already initialised parent and overwrite `conductor/product.md`, `conductor/tracks.md` or existing plans. Verify an existing-track `conductor-status` first, create or refine **only** the catalogue track, and preserve existing Conductor history. Avoid writing generated OS-specific symlinks to Git without inspection.

## Permission proof matrix (requested, observed, decision)

For each of the following, record `required`, `observed with exact readback`, `denied/unknown`, `named authoriser` and `next action`, with no credentials in public source:

1. Owner's permission to read/write a **dedicated test site**, create Lists/Libraries/site columns/content types/views and set library permissions.
2. Authentication application ID and actual delegated SharePoint scopes (read/management), user MFA/Conditional Access, tenant consent policy and allowed apps.
3. Power Automate maker environment, standard SharePoint connector DLP posture, trigger ownership, service account and connection references (no personal production automation).
4. Site collection app catalogue already enabled? If not, a SharePoint admin must enable it, or SPFx stays deferred.
5. Information class, permissible raw/extract files, records/retention/recovery, data ownership and approved processing location (no patient-level SharePoint ingest by assumption).
6. Where to store sensitive native readback/evidence privately; GitHub repo source and CI must stay synthetic and sanitised.
7. Whether existing SharePoint site or PPG/RIMS/Approve lists already serve parts of the catalogue. Prefer reusing authority IDs/views and avoid duplicate registrations.

## Work packages and dependency gates

| ID | Work | Depends on | Deliverables | Exit gate |
| --- | --- | --- | --- | --- |
| AG-00 | Source/roadmap and PR reconciliation; Conductor host setup | Existing CareOps code | Verified exact pin, overlap matrix, updated track | No duplicate module or lost history |
| AG-01 | Local developer tools and reproducibility | AG-00 | Tool lock/inventory, local smoke, no tokens in logs | Clean local setup |
| AG-02 | Read-only CHHHS site + auth/permissions feasibility | AG-01 and site authorisation | Sanitised capabilities matrix; private readback | Site, Entra app, scopes, permissions either **verified** or **blocked** |
| AG-03 | Provider-neutral CKAN-semantic DTOs and JSON Schema/fixtures | AG-00 | Dataset/Resource/Asset/Lineage DTOs and mock provider, validated interfaces | Tests pass offline; no SharePoint SDK in domain |
| AG-04 | Declarative first-slice provisioner (dry run by default) | AG-02 (for live), AG-03 | 3 Lists + 1 Library + required site columns, reversible plan | Safe create/readback/unchanged rerun/rollback |
| AG-05 | SharePoint REST provider and conformance tests | AG-03, AG-04 | Paginated CRUD, field mappings, ETags, upload, hash, fail-closed error states | Access denied & concurrency tests pass |
| AG-06 | Native SharePoint site page/forms/views | AG-04, AG-05 | Browse, filter, metadata edit, download/link with native controls | Real tasks work; no extra SPFx unless demonstrated |
| AG-07 | Governance reference integration | AG-05, agreed authority owners | Read-only Approve/Decisions/PPG/ERM pointers, no duplicate approval | Missing/expired/revoked evidence cannot grant access |
| AG-08 | Medallion expansion and publishing | AG-05, AG-07 | Stage libraries, Bronze-Silver-Gold-Platinum, provenance/release manifest | Deterministic synthetic promotion, rollback, suppression |
| AG-09 | Optional UX SPFx, versioned extension | AG-06 proven gap + enabled app catalogue | SPFx 1.24.1, React 18.3.1, accessible web part | No premium dependency, current-head tests, rollback |
| AG-10 | Operational admission and staged pilot | AG-06–08, organisation governance | Privacy/records/security/clinical acceptance, restore, support model | No clinical use until explicit approval |
| FK-01 | Optional CKAN 2.12 file-keeper adapter | Explicit native CKAN decision + approved service identity | External Python extension and mock SharePoint storage tests | No upstream patch; file security/stream/compatibility validated |
| MIG-01 | Optional Dataverse/SQL provider test | AG-03, AG-05 plus provider rights | Shadow data and conformance comparison | No simultaneous authoritative writers |

**Critical path:** AG-00 → AG-01 → AG-02 → AG-04 → AG-05 → AG-06 → AG-10. AG-03 can run in parallel with AG-02. AG-07 and AG-08 follow once metadata/resource and permission semantics are settled. FK-01, MIG-01 and AG-09 are intentionally off critical path.

## Output locations & testing discipline

- Reference implementation (after source admission): `modules/careops-catalogue/` with `src/domain`, `src/adapters/sharepoint`, `src/application`, `tests/contracts`, `tests/fixtures`, `provisioning`, `docs`, and optional `spfx`.
- Existing proposed physical manifest: `portfolio/careops-catalogue-sharepoint.v1.json`. First generate separate **exact internal-name field XML/schema** and readback validator; do not pretend this manifest is executable as written.
- Keep no host secrets, real clinical data, site UUIDs/URLs, identities, role memberships, operational approvals, clinical extracts or stored tokens in source; use private configuration outside Git and dedicated ignore rules.
- Each AG task closes with exact tests, no-premium/no-Copilot dependency check, negative authorization fixture, a CI source-boundary check, rollback evidence and an updated Conductor task. No check may be ticked complete on description alone.
- Preserve the existing `PUBLIC_SOURCE_FILES.json` review gate and existing CI; GitHub Actions artifact quota failures should be reported as infrastructure blockers, not hidden by disabling security checks.

## Effort assumptions

A narrow synthetic native-views demo (three Lists, one Library) is around **5–10 engineering person-days** if permissions and tooling are already resolved. The existing **21–40 person-day functional MVP** includes provider, governance references, synthetic medallion lineage and quality/negative tests, not administrator waiting time. Additional optional SPFx ~6–12, custom Python CKAN file-keeper ~10–20, native CKAN hosting/integration ~10–25+ and provider migration ~10–25 per provider are *rough scope estimates*, not commitments. Reassess after AG-02 and AG-04.

## First coding-agent assignment (copyable)

> Work on the CareOps catalogue Conductor track. Begin with **AG-00 and AG-01 only**, using the existing repo and pinned Conductor submodule. Reconcile the active roadmap and sibling module ownership; inspect PR #275 and current `main`. Inventory the local CLI toolchain and establish a clean, reproducible source-only test harness. Do not access CHHHS, install premium/Copilot dependencies, create an Entra app, provision Lists, deploy SPFx, initialise another Conductor copy, change sibling modules or access any clinical data. Produce the documented capability checklist, all blocked permissions, exact dependency pins, a first-vertical-slice schema and test fixtures. Commit a bounded PR with tests and rollback notes. Stop at the CHHHS read-only access gate; report precisely what an IT/site owner must authorise.
