# careops-process: source composition, full absorption and independent delivery

## Outcome and observed baseline

Retain the independent repository and existing runtime. Purpose: Privacy-minimised event ingestion, conformance, delay and rework analytics.
Observed default-branch source on 18 October 2026: `26f5b3e94b776c04853169ba9b3c604967899b3b`.
Visibility: public. Intended parent path: `modules/careops-process`.
This is a planning baseline, not a promoted release or deployment claim.

## Updated user-selected outcome — 25 October 2026

CareOps is to become the durable home for the Process module and its remaining
work. Keep `modules/careops-process` as an optional submodule at a reviewed exact
source commit. Move the active Conductor work plan and actionable GitHub issue
backlog into CareOps, reconcile every open item to a parent-owned track or an
explicitly accepted exclusion, and complete or safely hand over all required
work before the original GitHub repository is archived. Preserve the child
repository and its independent history as the submodule source; archival is a
final handoff step, not part of source composition or an automatic side effect.

“Fully absorbed” therefore means no active Process delivery, governance,
maintenance or decision work is stranded in the original repository. It does
not mean flattening the code into the parent tree: the user selected the
submodule form. The existing track owner boundary is superseded for the
parent-owned work-tracking and archive-readiness scope; native and operational
owners remain responsible for their actual systems and approvals.

## Scope and ownership

CareOps owns parent source references, catalog and checks; the existing module
owner retains child source, native objects and operational evidence. Wait for the existing Process owner to select a stable completed source revision; do not pull an unfinished working branch or interrupt current work. MIT source and passing checks observed previously must be rechecked on the selected commit.
No child/native edits follow from this track creation. Other module owners may
continue their current work; no blanket completion dependency is imposed.

## Requirements and acceptance

- Select an exact reviewed commit and preserve its independent history, licence,
  release cadence and source/deployment ownership. Parent MIT terms do not
  relicense child contents. Resolve required redistribution rights before bundling.
- Private history, bindings, exports and business data stay private. A public
  parent never confers access to a private child. If the current repository is
  unsuitable, prepare a separately reviewed source-only publication; do not
  change visibility or publish a sensitive gitlink/history as a shortcut.
- Parent remains usable without initializing optional modules. Validate a clean
  clone and selective initialization using actually available rights. A private
  module cannot become an unconditional public CI checkout dependency.
- Reuse existing documented source checks and passed same-revision results;
  diagnose missing/failed checks and test only changed behaviour or actual gaps.
- Selected representative case: Synthetic event/file ingestion with stable source IDs, duplicate/replay, tombstone, stale and absent-provider cases; no workflow or authoritative-record writes.
- Optional adapters declare provider/consumer versions, source-qualified IDs,
  correlation/idempotency, minimum payload, stale/error behaviour and absence
  paths. No mandatory shared business table, parent service or analytics runtime.
- Record the previous parent pin/catalog/check configuration and rehearse source
  reversal in a disposable clone. Native resource/data recovery is separate.

## Outputs and qualification

Prefer SharePoint structured document generation for maintained reports or other
structured documents. Use authoritative inputs and maintained Word templates;
preserve source/template versions, included IDs, human edits, unresolved concerns
and issued history. Qualify actual output, repeating/optional content, links,
editing, access and retry/recovery before replacement. Keep a supported fallback
for a specific gap. Generation does not review, approve or circulate content.

## Out of scope

CGov, its mapping/legacy replacement and N11 cutover; credentialing-domain
migration; tenant writes, authentication/consent/licence changes, circulation,
real-content processing and business decisions. Source setup does not depend on
real operational participation or business adjudication. Keep those later
acceptance states distinct rather than claiming them complete.
