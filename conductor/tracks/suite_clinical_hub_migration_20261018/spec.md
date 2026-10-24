# Clinical Hub: reusable-source carryover

## Outcome

Compose `edithatogo/clinical-hub-core` into the CareOps control plane as an independently
versioned source module at `modules/clinical-hub-core`. Retain its own repository, history,
checks and release cadence. This is a pinned source reference, not a merge of
repositories or operational systems. The reusable scope is meeting preparation, agenda/paper links, reviewed carry-forward, manual minutes and action follow-up.

## Observed baseline — 18 October 2026

Public default-branch commit: `05d0e1f6f5a0495f40c516b40339c56a0b3698ae`; 69 tracked blob files observed.
Current default-branch Offline checks passed on the observed SHA. Source includes an explicit public inventory, stable Python 3.15.0 and hash-locked development dependencies. The existing implementation plan deliberately avoids a mandatory Dataverse migration.
These are planning observations, not approval of a new package or native runtime.
Refresh the default head and affected checks before implementation; never follow
an unreviewed branch or update a pin merely because it is newer.

## Ownership and boundaries

The CareOps maintainer owns parent catalog, gitlink, compatibility references and
parent CI. Existing Clinical Hub implementation owner owns child source changes and all existing native objects.
Preserve clinical-hub-core identity. Decisions is a separately versioned optional provider, not the destination for copying all meeting source. Native flows, journals and operational files stay with the private implementation owner.
Do not create another runtime, repo, chat, authoritative register or shared
business table. Keep authoritative IDs, links, human edits and unresolved states.

## Acceptance

- Exact reviewed public commit and canonical URL are recorded in catalog and
  gitlink; license/attribution is explicit. Public visibility is not a licence.
  Parent MIT terms do not relicense child code. Clarify rights before copying,
  bundling or redistributing child source; source referencing preserves its terms.
- Parent checkout works without initializing this optional module. The module's
  existing documented source checks work without any sibling or CareOps runtime.
- Trace fictional open action → reviewed carry-forward → manual minutes → follow-up; cover held/closed exclusions, unresolved concern, missing/stale paper, duplicate retry and preserved human edit. Reuse existing fixtures; implement only actual gaps.
- Optional adapters declare provider/consumer versions, source-qualified IDs,
  correlation and idempotency keys, error/stale behaviour and absence path. No
  adapter is mandatory merely to add a source pin.
- Updated gitlinks are explicit publication-inventory changes. Test clean clone,
  initialize only the selected module, and inspect actual dependencies. Retain
  previous parent revision; reversal changes only source references and CI.
- Native configuration, outputs/access and recovery require their own later
  qualification by the current owner. Source tests never close those gates.

## Verification and document outputs

Use make ci with the module's stable Python and hash-locked environment. Reuse the passed same-SHA hosted check; inspect source inventory and publication checks before materialisation. Do not install a tenant application.
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

## Superseding user direction — 24 October 2026

The user requested full source migration and synchronization into CareOps before
archiving the Clinical Hub remote. Integrate regular public source files rather
than a gitlink; retain provenance, private recovery history and external native
records. No child licence declaration exists; do not assert that parent MIT terms
relicense imported files. This replaces the earlier independent-child development
and gitlink mechanism for this module only.
