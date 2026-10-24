# RIMS: reusable-source carryover

## Outcome

Compose `edithatogo/careops-rims` into the CareOps control plane as an independently
versioned source module at `modules/careops-rims`. Retain its own repository, history,
checks and release cadence. This is a pinned source reference, not a merge of
repositories or operational systems. The reusable scope is portable publications contracts, source-specific ingestion/reconciliation, report preparation and selected output interfaces.

## Observed baseline — 18 October 2026

Public default-branch commit: `f9031869f4f5dda723d548c5ed821a748154cef6`; 976 tracked blob files observed.
Current default-head Public source security passed. The source snapshot is much larger and includes Power BI, Power Query, DAX, flows, templates and historical instructions. That security result does not qualify all current reporting behaviour; README identifies known historical baseline defects.
These are planning observations, not approval of a new package or native runtime.
Refresh the default head and affected checks before implementation; never follow
an unreviewed branch or update a pin merely because it is newer.

## Ownership and boundaries

The CareOps maintainer owns parent catalog, gitlink, compatibility references and
parent CI. Existing RIMS publications implementation owner owns child source changes and all existing native objects.
RIMS native solution, checkpoint and field-mapping ownership stays with the private publications lane. No intake/register duplication, unrelated enrichment, unattended circulation, model rewrite or optional API dependency is introduced.
Do not create another runtime, repo, chat, authoritative register or shared
business table. Keep authoritative IDs, links, human edits and unresolved states.

## Acceptance

- Exact reviewed public commit and canonical URL are recorded in catalog and
  gitlink; license/attribution is explicit. Public visibility is not a licence.
  Parent licence terms do not relicense child code. Clarify rights before copying,
  bundling or redistributing child source; source referencing preserves its terms.
- Parent checkout works without initializing this optional module. The module's
  existing documented source checks work without any sibling or CareOps runtime.
- Exercise fictional source-qualified publication IDs, conservative cross-source deduplication, attribution lineage, period identity, duplicate replay and one selected output. Preserve human attribution corrections, unresolved affiliation concerns and issued report revisions.
- Optional adapters declare provider/consumer versions, source-qualified IDs,
  correlation and idempotency keys, error/stale behaviour and absence path. No
  adapter is mandatory merely to add a source pin.
- Updated gitlinks are explicit publication-inventory changes. Test clean clone,
  initialize only the selected module, and inspect actual dependencies. Retain
  previous parent revision; reversal changes only source references and CI.
- Native configuration, outputs/access and recovery require their own later
  qualification by the current owner. Source tests never close those gates.

## Verification and document outputs

Select one publications-only source-to-output slice using START_HERE.md and current completion scope. Run its existing focused contract/fixture checks plus public-source checks. Inventory report/model/flow dependencies before any managed-package or report migration.
Evaluate SharePoint structured document generation first for structured output
improvements. Preserve maintained template/input versions, included IDs, generated
revision, human edits and issued history. Qualify actual availability, optional/
repeating content, output, links, access and retry before replacing a fallback.
Generation never supplies substantive review or permission to circulate.

## Out of scope

CGov mapping/replacement, credentialing contracts/data migration, N11 cutover,
private source/history or record transfer, tenant writes/auth repair, new licences,
consent, invitations, notifications and business adjudication. Existing CGov tracks
are unchanged and are not prerequisites for this track. No native migration is
implied by a source pin; source checkout rollback cannot undo a tenant write.
