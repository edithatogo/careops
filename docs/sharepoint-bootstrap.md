# SharePoint Lists setup and read-only archives

## What exists and what this adds

The suite already contains Approve's list contract in
`careops-approve/config/sharepoint-lists.example.json`, Clinical Hub's additive
metadata planner in `modules/clinical-hub-core/scripts/forum_native_schema.py`,
and the catalogue's typed physical design in
`portfolio/careops-catalogue-sharepoint.v1.json`. These are useful foundations;
none is a universal, tenant-qualified installer for the whole suite.

`portfolio-scripts/standard_bootstrap.py` now compiles the catalogue design into
a Microsoft site script, a desired inventory, a human-readable CSV column
dictionary and a plan of remaining native checks. It is offline and standard
library only. The catalogue is the first supported adapter. Other modules are
not silently installed or falsely marked provisionable.

## Generate the package

From the repository root, select the exact Python pin and one module:

```sh
uv venv --python 3.15.1 .venv-careops
.venv-careops/bin/python --version
.venv-careops/bin/python portfolio-scripts/standard_bootstrap.py \
  --module careops-catalogue --output .local/catalogue-setup-001
```

The tool refuses an existing output directory. Choose a fresh numbered directory
for each candidate; retain the selected package privately with its exact source
revision. No selected modules produces an empty plan, never an implicit full-suite
installation. No credentials, site URL, premium licence or Copilot are needed to
generate it. There is deliberately no `--apply` switch.

Generated resources are `Catalogue_Datasets`, `Catalogue_Resources` and
`Catalogue_Assets`, with typed fields, fixed field identities, shared site columns,
document content types and a basic paged metadata view. The built-in Title field
is retained and its settings must be checked. The proposed filtered views, native
forms, permissions, retention, versioning and source-to-file validation are listed
as follow-up; generation does not claim to configure them.

## Two native setup routes

**Site owner route:** create the selected empty Lists/library through SharePoint,
using `columns.csv` as the field/type/choice/index checklist. Reuse an approved
existing template/List where suitable. Check the generated plan and actual access.
Do not treat an Excel/CSV import's inferred types as the declared schema. If the
manual route creates different native field identities, record them; do not later
apply a generated script on top and assume those identities match.

**Administrator template route:** an already-authorised SharePoint administrator
registers the reviewed `site-script.json` with `Add-SPOSiteScript`, creates the
selected site design with `Add-SPOSiteDesign`, and applies it to the approved
test site with `Invoke-SPOSiteDesign` (or the supported queued application route
where size limits require it). Select the site's actual web template; no tenant
wide default or hub association is requested. These commands belong to SharePoint
Online Management Shell, not PAC. Registering a template can make subsequent
site-owner setup simpler through the organisation's site-template picker.

Use the [Microsoft cmdlet reference](https://learn.microsoft.com/en-us/sharepoint/dev/declarative-customization/site-design-powershell)
and [site-script schema](https://learn.microsoft.com/en-us/sharepoint/dev/declarative-customization/site-design-json-schema).
The generator emits only supported additive verbs. Fixed IDs make candidate output
stable; native idempotence still needs a test. No native deployment was performed
by this source change.

## Existing sites and safe reapplication

For a new package without readback the plan is explicitly `new-empty-scope-only`.
For an existing scope, export/read the actual selected resource schema through an
already-qualified read route and normalise it to `desired-inventory.json`'s shape.
Then supply it as `--existing-inventory /private/path/observed-inventory.json`.
Include the siteColumns and contentTypes sections: selected List fields alone
cannot establish shared site-schema compatibility. This compares field identity,
type, choice/default, required, unique and index
settings, rejects duplicate names and refuses conflicts. Do not substitute the
desired inventory itself for an actual native observation.

An existing mismatch requires an explicit migration or adapter. Do not drop and
recreate populated Lists, coerce field types, regenerate domain UUIDs or replace
current field GUIDs to obtain a green result. Unselected resources are untouched.
Native application can partly succeed: read back what exists before recovery,
preserve user-created records and retry only the understood remaining operation.

The first native qualification should prove creation, find/edit/link, unauthorised
read/write denial, duplicate-ID rejection, partial-apply recovery, reapply, withdrawal,
and UUID-preserving export/import using fictional entries. Record one receipt
with exact source/schema and resource identities; keep private bindings outside Git.

## Reusable resource abstraction

Use a small resource descriptor: logical module/resource key, schema version,
stable field identities, types/defaults/indexes, access class, retention role,
source owner, optional views/forms and dependencies. Physical site/list IDs and
connections belong in a private binding profile. Derive setup, manual checklists,
readback comparison, fictional fixtures and export schema from the same descriptor.

Next adapters should translate Approve's existing list contract and the Improvement
PR's templates, then Clinical Hub's qualified metadata model. Preserve semantic
rules such as request visibility, one-final-decision and immutable routing snapshot;
creating columns does not implement these. Do not replace the existing generators
with a generic engine until their preservation tests pass.

## Maintain an archive in parallel?

Yes: maintain a **read-only, versioned snapshot/recovery export**, never a second
editable copy of the register. The selected List remains the operational authority.
Use native version history and organisation-approved backup/retention alongside
the portable snapshot. A CSV export alone is not a full SharePoint backup.

| Snapshot part | Required information |
| --- | --- |
| Manifest | Export ID, schema version, source IDs, watermark, start/end time, coverage and consistency limits |
| Records | Stable domain UUID, native item ID, revision/ETag, modified time, source-qualified links and deletion/tombstone state |
| Schema | Types, choices, field identities and rules needed to interpret the rows |
| Files | Attachment/resource identity, version, length and digest; explicit missing-file failures |
| Access/recovery | Classification, permitted audience, retention, restore map and last fictional restore result |

Export JSON/CSV for portability; add Parquet only where analytical scale warrants
it. An immutable manifest identifies the exact record/file set. Use delta exports
plus periodic full reconciliation to discover deletions and missed updates; choose
frequency from recovery objectives rather than an arbitrary daily requirement.
An interrupted export is incomplete until validated. Multi-list exports are not
atomic: reconcile versions or record that consistency boundary explicitly.

Keep operational snapshots encrypted and access-controlled in approved private
storage, with short necessary retention and tested restoration. Never commit
patient/practitioner records, private dataset metadata, file bytes, signed sharing
URLs or tenant bindings to GitHub/GitLab. Source control holds schemas, exporters,
fictional fixtures and recovery instructions. Restrict restore writes and preserve
original domain IDs while mapping any new native IDs. The exporter and restore
automation are roadmap work; this change supplies the contract and setup generator.
