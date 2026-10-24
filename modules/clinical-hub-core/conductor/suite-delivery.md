# Modular suite delivery — 18 October 2026

Public source-only meeting development tools; private native implementation retains records and object ownership.

Apply the [shared development and delivery policy](https://github.com/edithatogo/careops/blob/main/docs/development-and-delivery.md) and
[optional standalone-module contract](https://github.com/edithatogo/careops/blob/main/docs/standalone-module-contract.md). Existing native-object/file
owners, current task selection and operational records retain precedence for
execution. This source profile does not establish target access or deployment.
The existing enterprise authority/mirror mapping is unchanged.

## Next useful improvements

The ordered cross-repository queue is in [the module profile](../.careops/module.json).
Take its first eligible task after preserving the current in-flight operation.
A completed MVP is not reopened by this queue: optional improvements follow the
selected slice and remain optional. Keep detailed progress in the existing track.
Do not create another track, chat, acceptance pack or status ledger for alignment.

Reconciled 24 October 2026 against committed source, merged qualification checks
and existing recorded native scope. These statuses describe the listed improvement,
not deployment or operational acceptance. Skip completed items; partial items need
their stated remaining scope rather than a repeat of passed work.

1. **policy — complete.** Isolated exact hash-lock resolution, preview candidates,
   audit/test qualification, baseline preservation and explicit promotion are implemented.
   Python 3.15.1 and the refreshed lock were promoted in [PR29](https://github.com/edithatogo/clinical-hub-core/pull/29);
   required shared Python policy followed in [PR30](https://github.com/edithatogo/clinical-hub-core/pull/30).
   Both merged with successful dependency-candidate, domain and source-security checks.
   Runtime discovery success is not proof that every discovered preview was executed.
   Ongoing candidate maintenance remains routine; no repeat migration is queued.
2. **documents — complete for the selected manual route.** Reuse existing
   SharePoint library columns and maintained Word templates, assuming no Copilot
   or Premium connectors. [PR52](https://github.com/edithatogo/clinical-hub-core/pull/52)
   integrated the [route and bounded qualification](library-column-word-route.md):
   representative 0/1/12-item agendas and minutes, held/closed distinctions, paper
   targets, native rendering/readback, saved/reopened corrections and a distinct
   manually reconciled revision. Existing schema, templates and file ownership
   are retained; exact evidence remains private.
   Automatic body refresh/merge, optional Copilot generation, historical-content
   recovery, exact edited-file destination collision after unlock and transport/race
   injection retain their recorded limits. Intended-role rollout and distribution
   remain separate. These limits do not reopen the bounded manual increment.
3. **adapter — complete for the selected offline contracts.** The
   [pack-provider adapter](../scripts/optional_pack_provider.py) retains its qualified
   standalone/proposal behaviour. The [action-reference adapter](../scripts/optional_action_reference.py)
   reuses F10 carry identity and reconciliation for List GUID, opaque action ID and
   meeting ID. Fictional tests cover cross-source identities, stale/unverified revisions,
   exact/changed retries, ambiguous duplicates and preserved human edits, including
   edits after a prior receipt. No provider login, source authentication, native write
   or operational acceptance is implied. Live integration remains optional.

Reconciliation verification: the explicit repo-local interpreter reported Python
3.15.1; `tests/test_ci_delivery.py` and `tests/test_optional_pack_provider.py`
passed 11 tests. This reuses merged integration/audit evidence and does not claim a
new full-suite, dependency audit, provider connection or native execution.

## Dependency and delivery defaults

Prefer the newest useful development version, resolve an exact version/commit,
and qualify affected behaviour before promotion. Retain the working version and
recovery path. Inspect actual package engines/targets; use separate Node/Python/
.NET profiles where needed. A preview tag can be older than the current release.
The portfolio baseline is dated discovery, not this repo's installed/runtime state.
Use existing CI; exact action pins and managed downstream artifacts improve
reproducibility without provisioning new identities or tenant services.

The selected Clinical Hub working route uses existing library columns and
maintained Word templates with manual narrative/revisions, assuming no Copilot
or Premium connectors. Preserve source truth, human edits and issued history;
qualify actual output and recovery before replacing a working route. Optional
structured generation can be reconsidered on changed evidence. Document production
is not content review, approval, circulation or a change of status.

Keep one writer per object and one owner per shared authentication repair. Tools
are preferences, not exclusive leases. Send a completed deliverable or changed
blocker once; no acknowledgement polling. Reuse passed evidence and run only
checks affected by the change, with broad checks at an integration milestone.

## Source CI implementation

The shared source-security workflow and runtime discovery helper are pinned together
to CareOps `d829db7aa46e3789eb1b339f1ab1ad7e5d780d49`. The shared stale-lock gate applies to `requirements-ci.txt` callers; this module
retains its existing `requirements-dev.txt`/hash-lock compatibility tests and audit.

Renovate owns this input/lock pair through its `pip-compile` manager: discover
`requirements-dev.lock`, read its explicit `uv pip compile` header and update
the input plus generated hashes together. Standalone `pip_requirements` discovery
is disabled to avoid competing input-only proposals. Regenerate using the header
command with equals-style option arguments, then qualify `make ci audit` with
the selected repo-local interpreter. Preserve the lock/input consistency gate;
a candidate-only lock cannot substitute for the committed baseline. Keep runtime
proposals in the selected Python 3.15 line; isolated previews are separate.
Domain tests, including
Hypothesis fuzzing, remain local. Renovate proposes dependency updates through PRs.
The weekly/manual canary resolves a separate exact hash lock, audits and tests it,
and retains version/digest receipts for 14 days. Runtime discovery records the frozen
Python manifest and distinguishes unavailable previews from executed tests. Neither
canary promotes a candidate automatically; promotion requires a reviewed lock/runtime
change with passing current-head checks.

The manual source-package workflow runs only on main after source/security checks.
It builds an allowlisted archive from the committed source, a matching SPDX file
SBOM, and provenance/SBOM attestations, retained as a workflow artifact for 30 days.
This is a source package, not a tenant deployment or bundled Python runtime. Verify
a downloaded archive using `gh attestation verify --repo edithatogo/clinical-hub-core`
and compare its files with the SBOM before relying on the artifact.

The optional pack-provider adapter preserves the local pack and returns a proposal
for review. Its offline tests cover absence, stale revisions, source-qualified IDs,
retry reconciliation and preserved human edits. No provider login or live integration
is implied by those tests.

Runtime finalisation executes after failed, cancelled or skipped discovery as well
as success, recording the discovery and test outcomes separately. A missing-receipt
failure probe runs against the same pinned helper and retains a distinct
`failure-probe.json`; it is a synthetic failure case, not the actual discovery
outcome. Malformed/contradictory evidence is preserved and rejected by the helper.


## Selective SharePoint library columns — 19 October 2026

User-selected implementation direction: reuse library columns for artifact identity, provenance, filtering and routing where the output already belongs in SharePoint. Reuse existing columns/content types and exact internal names before adding fields. This extends the structured-document preference; it is not proof of automatic Word-body generation.

Priority: continue the existing native column trial, then reuse its qualified metadata behaviour in F06 agenda/pack, F07 paper gathering and F08 manual minutes. Retain document/occurrence identity, source/template versions, paper links and output revision; preserve decisions, unresolved concerns, human edits and issued history.
Native owns all flow/library mutations and operational records. Platform retains template/schema preparation; Support reconciles the existing roadmap. Reuse deployment/README.md's selected route; no parallel trial or new operational file. Property storage/readback is useful independently, but the recorded stale visible Word body remains an unresolved generation limitation.

Acceptance: map each property to its existing authoritative source and verify its actual type/internal name; read back the affected saved values and file identity. Update only changed values, guard modification-trigger loops and retries, and retain a recoverable preimage. Preserve human edits, original/issued history and exact reviewed revisions. Add no duplicate register, notifications, approval workflow, permission change, licence or runtime. Avoid putting private/internal-only values into properties that may travel inside a downloaded Office file.

Metadata readback and visible body rendering are separate checks. The Clinical trial stored a changed property while Word for the web still displayed the old body value. Do not claim scalar body refresh, narrative/repeating sections or generated Word/PDF fidelity from metadata success. Qualify those behaviours only for the selected document shape; retain working/manual outputs on a specific gap. Record one result in existing evidence, not another readiness pack.

The 24 October saved-file comparison and fresh read-only Word-web view reconfirm
that exact prior failure; neither establishes a refresh pass. Automatic Word-body refresh stays
unqualified under the existing non-premium constraint. See the [current route
disposition](document-cases.md#automatic-word-body-refresh--still-unqualified-24-october-2026).
Retain manual Word/Markdown; do not reopen passed cases or substitute metadata,
conversion, locally rewritten DOCX bytes or CI results for native visible refresh.

Post-edit regeneration is a separate dependency-bound check. The 24 October
reconciliation leaves D10/D11 pending because the automatic Word-body route has
not qualified. Retain saved-edit and history evidence within its actual scope;
metadata preservation, version enumeration and earlier Developer collision/replay
checks do not establish non-premium regeneration or conflict handling.

Reference: https://learn.microsoft.com/sharepoint/dev/business-apps/power-automate/sharepoint-connector-actions-triggers

### Offline F16 deployment-settings validation

The F16 helper validates a pinned solution ZIP against exact deployment-settings
and source-settings fingerprints. It rejects membership/connector drift, source
connection reuse, incomplete values and invalid F12 configuration. Native F12
annotation transport is decoded through the existing strict helper; the original
stored JSON length is checked before decoding and reported unchanged. Local PASS
does not establish target access, resource authority, current native/export parity,
managed layers or deployment readiness. Keep actual settings and tenant readbacks
private and retain qualified baselines independently; never repin merely to clear
a drift error. Interrupted output publication preserves completed siblings and
supports exact retry without replacing competing files.

F06 output destinations need a library GUID paired with the configured SharePoint
site, separately from the source Matters List ID. Offline settings validation
accepts GUID-valued `LibraryId` declarations using the same strict checks as
`ListId`; malformed or injected REST fragments are rejected. A local parameter
candidate or valid GUID does not prove destination existence, permission, native
adoption or target binding. Read back the actual definition/value/component set
and refresh exports before establishing a recovery baseline. Preserve create-only
output writes and completed human edits during qualification.

Export validation also requires every named flow environment-variable declaration
to resolve to an exported definition of the matching String/Object type. Built-in
connection/authentication parameters remain separate. This detects a saved flow
referencing a missing solution variable even when the package and settings counts
look plausible; it does not establish the native current value or target access.


### Managed destination qualification and recovery

Use the existing pinned package and exact private settings for a selected managed
update. Preserve the target preimage, component identities, current values,
connection references and state. Reconcile the actual import job and saved native
configuration before retrying an uncertain import. A successful import alone does
not establish that connected flows can run.

Join runtime flows to solution workflows through the explicit workflow entity ID;
the runtime flow ID may differ for a previously installed component. Compare the
complete saved definitions and Invoker bindings, not names or counts alone. Keep
managed definitions and customization properties unchanged during state-only
commissioning. Verify actual runtime output and restore the selected flow Off.

For configuration recovery, a bounded conditional update, stale-version refusal
and fresh-version restoration can qualify the selected setting without destructive
solution removal. Compare the restored configuration with its preimage and account
for server-maintained version/time fields. A prior smaller managed package is not
a rollback: a normal update does not delete newly added components.

Preserve exact stored baselines during read-only runtime checks. Rendered UI text
can normalize whitespace; do not infer source drift or silently rebaseline from
that presentation. Use actual action outputs and the final native run result.
Keep all tenant values, run payloads, operational receipts and binary packages
outside this public repository. Record technical completion at its tested scope;
real-register cutover, circulation and destructive environment restore remain
separate operations.


The bounded destination commissioning has verified a normal managed import,
complete saved graph and connection-reference parity, exact configured values,
and conditional configuration recovery with stale-write refusal. A fictional
agenda run produced the inspected linked output while preserving its source
record. The read-only calendar/agenda run reported all 21 metadata checks true,
no metadata change and no proposed write; document-content equality remains
unverified. Its actual attachment payload preserved repeated whitespace that the
rendered inspection text had normalized. These results qualify those technical
behaviours only. Final native readback also verified every included flow Off,
with graph, Invoker bindings, owners, configured values and component identities
preserved. This closes the selected source-export and managed-destination technical
commissioning/configuration-recovery scope. Destructive full-environment restore,
production entitlement, real-register cutover, circulation and substantive business
acceptance are not established by these tests. The existing private operational
record retains the native evidence; no tenant payload is published here.


The direct uv release installer is tracked through the same Renovate application
using a scoped custom regex manager. It matches only UV_VERSION in the two known
candidate-workflow paths; existing dependency managers and presets are retained.
Prerelease proposals are allowed, but automatic merging is disabled. The updater
changes the proposed version, not UV_SHA256. Preserve the digest check before
extraction/execution and qualify the matching official artifact before promotion.
This adds source update discovery, not a new installer, native write or consent.

## Optional action-reference contract — 24 October 2026

Call `scripts.optional_action_reference.propose(local_rows, envelope=None,
expected_revision=..., prior=...)` with a complete scoped row snapshot. Without an
adapter envelope it returns a detached standalone snapshot. Version 1 envelopes use
exactly `contract_version`, `source_id` (List GUID), `record_id`, `meeting_id`,
`revision`, `operation_key` and `fields`. `fields` uses the existing three F10
carry fields: `Title`, `Question_x0020_or_x0020_help_x00` and `Meeting_x0020_date`.
This bounded contract proposes an existing action reference for agenda review;
it is not a generic action-register synchroniser or another action register.

Only GUIDs are canonicalised; opaque action/meeting IDs and revision tokens retain
case. The caller supplies the expected current source revision; this adapter cannot
establish that a supplied snapshot is fresh or authorised. Native identity/version/
ETag requirements and human-edit checks are delegated to the unchanged F10 helper.
Missing or ambiguous matches never authorise creation. Only `EXISTING_MATCH` returns
a detached field proposal. An exact prior receipt returns `duplicate`, while a
changed retry requires reconciliation; current row conflicts take precedence over
prior receipts. All results preserve local rows and set `write_proposed` false.
Receipts describe proposal inputs, not committed native effects. No automatic retry,
authentication, connector, workflow or downstream mutation is implemented.

Offline adapter qualification: repo-local Python 3.15.1 passed the focused adapter/
F10 selection (28 tests and four subtests). Integration milestone `make ci` passed
public-source validation and 916 tests with 13 subtests. Staged Gitleaks and diff
format checks also passed. No dependency/runtime change or native operation occurred.

### Source integration reconciled — 24 October 2026

The existing source lane completed review, affected checks and sequential
integration: [roadmap PR #31](https://github.com/edithatogo/clinical-hub-core/pull/31)
merged as `1c6bf54415c65f4df22443233515620eac1f7c5d`, followed by
[adapter/document-case PR #32](https://github.com/edithatogo/clinical-hub-core/pull/32)
as `903ac801742fe4394775eb3cf4f6f14aa0712bf9`. Both exact PR heads passed the
domain and source-security Actions checks; the second was checked again after
updating against main.

The owning lane confirmed both merges are ancestors of current main and no owned
staged, unstaged or untracked source changes remain. No duplicate implementation
PR is needed. This reconciliation changes documentation only; implementation
files and ownership are preserved. The recorded offline results do not qualify
native generation, provider integration, publication or delivery.

## Selected no-Copilot/no-Premium document increment — 24 October 2026

Follow [the library-column/manual Word route](library-column-word-route.md).
Reuse existing metadata, maintained templates and manual narrative/revision
controls; qualify fictional D01–D12 at that scope. Automatic Word refresh/merge
and Copilot licensing remain optional limitations, not blockers of this usable
manual capability. Preserve existing native/file ownership and record exact
case results once in the private minutes track.
