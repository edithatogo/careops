# PGY1 portability and the PPG dataset catalogue

The PGY1 fixture describes a fictional program and term. Clinical assurance, external assessment, trainee records and formal awards require their own operational evidence.

| Example | What is reused | What is specific to the example |
|---|---|---|
| NSQHS | Framework edition, requirement, review context, evidence version, mapping and assessment | An NSQHS action and its own assessment under the accreditation scheme |
| Stroke Clinical Care Standard | The same evidence version and separate requirement judgement | A quality statement and versioned indicator observation in a cycle-free quality context |
| PMAQ PGY1 | The same evidence version in two Proposed mappings, plus a versioned fictional brief | Program and child term scopes, independent Unknown judgements, committee decision, outstanding condition and proposed change |

The PGY1 source hierarchy retains AMC Section 2, criterion 2.1 and clauses 2.1.1 and 2.1.3. Section 3 describes program and term experience. The MBA registration standard has its own source role. QH administers the local accreditation process and the PMAQ Accreditation Committee decides the external outcome. The PMAQ guide's standard ratings are Fully met, Partially met, Not met and Not applicable. They are distinct from the program decision and internal evidence judgements. The fictional change is recorded as not submitted. A completed internal action leaves its external condition outstanding.

**Publisher conflict.** The retained QH-IMP-476 v3.0 PDF records committee approval on 3 July 2025 and DDG approval on 29 October 2025. The captured resource index says “awaiting approval”. The fixture carries both assertions and excludes that standard from operative criteria. Source roles, exact capture hashes, publisher file references and clause locators accompany the fictional records. [Example and source references](../tests/fixtures/accreditation/pmaq-pgy1.json)

## Run the example

Use the maintained repo-local interpreter. Keep installation bindings, operational exports and receipts in the private workspace.

```sh
.venv/bin/python -m scripts.ppg_pmaq_portability --output .local/pgy1.json
```

For an existing installation, supply its exact retained display-name configuration through `--vocabularies .local/vocabularies.json` to reproduce the deployed profile hash. Public source references use file names and capture hashes where the deployment retains the publisher URL privately.

The package contains the framework profile, four requirement nodes, program and term contexts, two evidence versions, four mappings, two assessments, two fictional decisions and two linked events. The importer resolves lookups against the selected destination. The prerequisite shared AC-19 evidence version must exist there. Supply the qualified SharePoint adapter and a private binding with `site`, a unique `journalPrefix`, and a `targets` map of list IDs for `framework`, `requirement`, `context`, `evidence`, `mapping`, `assessment`, `decision`, `event` and the evidence `library`.

```sh
node scripts/ppg_pmaq_native.mjs .local/adapter.mjs .local/pgy1.json .local/pgy1-target.json .local/pgy1-receipt.json
```

For recovery, select separate native objects and bind the same logical keys to their destination IDs. Reuse the actual exported revision after an owner edit. A conflicting existing row stops import. Verify separate recovery, preserved version history, stale edit rejection and unchanged replay. Link each independent judgement to the shared evidence version.

## Browse and provision the dataset directory

Open **PPG Dataset Catalogue** in Site Pages or use the **Dataset directory** view of the identically named SharePoint list. The page groups links by purpose. The list retains the physical list ID, installer key where available, scope, list/library type, link and versioning setting. Include each product list or library and the directory itself. Upstream external sources are documented separately as dependencies. Privately captured responses, mail contents and dataset rows stay in their source locations.

After provisioning the product objects, run the directory companion with the private object map returned by provisioning (the map's entries contain the destination `id`). Use an account with access to the intended catalogue scope. Keep the list/page audience appropriate for the directory metadata. Existing permissions govern opening the links.

```sh
node scripts/ppg_commission_dataset_directory.mjs .local/adapter.mjs .local/object-map.json .local/directory-receipt.json --publish
```

The command adds missing entries by physical identity and verifies readback. Existing field or page conflicts require reconciliation before a changed directory is issued. The initial page is an ordinary site page. The live directory view is linked at its top.

## Release and deployment decision

The production Power Platform solution is **0.2.3.0**. The reusable whole-product workflow installer is **1.0.4**. This SharePoint companion release is **1.4.1**. The application package contains 35 workflow definitions, five connection references and nine environment-variable definitions. The SharePoint register, page, PGY1 records, source captures and templates use separate provisioning and recovery contracts. Their version histories and deployment receipts belong with the solution release manifest.

Compare both exports for ZIP integrity, solution identity, managed flag, workflow definitions, connection references and environment variables. Export packages can contain environment-specific bindings and stay private.

**Deployment decision.** Keep the current editable source solution unmanaged. Use the managed package for a separately selected downstream environment after import, connection and environment-variable binding, SharePoint provisioning, one representative run and an upgrade/recovery check there. Managed import and upgrade are unqualified at this release. Converting the existing source environment in place would put the editing and deployment roles in the same environment. This follows the RIMS release pattern of an editable source, a downstream package, a component inventory and separate evidence for external stores. [Microsoft solution lifecycle guidance](https://learn.microsoft.com/en-us/power-platform/alm/solution-concepts-alm)

External API access and licensing, unavailable publisher history and unresolved channel delivery retain their recorded limits. Power BI remains on the roadmap. Cross-tenant recovery is removed from scope.
