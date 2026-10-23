# CareOps development and delivery

Effective 18 October 2026. Apply this shared policy through each repository's
`.careops/module.json` and existing Conductor roadmap. These are implementation
defaults, not evidence of tenant access, deployment or operational acceptance.

## Deliver the smallest useful improvement

Keep independently deployable modules, optional adapters and existing authoritative
records. Improve current Lists, Teams/SharePoint navigation and working flows first.
Choose a replacement interface or common service when a bounded comparison shows
less implementation effort or a missing required capability. Do not require the
portfolio checkout, AI, sibling modules or a shared database for standalone use.
Existing enterprise authority and continuity-mirror mappings remain unchanged.

Use the existing standalone-module contract for source-qualified identity,
revision, correlation, idempotency, provenance, classification, errors and recovery.
Keep business records and decisions in their owning module. Preserve existing
field mappings and issued history. Extract shared code after two actual consumers
demonstrate the same requirement; link standards instead of copying whole systems.

## Development first, reproducibly

Discover the newest useful upstream release, preview, nightly or development
commit. Resolve it to an exact version/commit and integrity/hash before use. Compare
publication dates and compatibility: an old `next` tag does not outrank a newer
release. Never leave a floating development tag in a deployed artifact.

Inventory Microsoft CLI/MCP packages, skills/plugins, Python/Node/.NET, application
packages, GitHub Actions, binaries and external API versions. Separate installed,
declared, locally tested and native-qualified versions. Unknown is not absent.
Use isolated runtime profiles for incompatible tools; a newer major is not a
substitute for the runtime a tool actually requires. Record the exact exception
and its next review condition. Retain the working version until the candidate
passes affected checks and a recovery route is known.

The opt-in `careops-dev` Renovate preset discovers updates daily, permits
prereleases and pins supported dependency declarations and action digests. It does
not deploy, change authentication or infer runtime qualification. Group coherent
updates and keep PR concurrency bounded. Avoid duplicate Dependabot/Renovate
coverage. Use one small compatibility experiment for a real dependency gap.

Where a plugin or skills source is pinned both as a Git submodule and in an
installation manifest, maintain both declarations in the same reviewed update.
Keep one update group per upstream source rather than grouping unrelated plugins.
A manifest regex manager can track `git-refs` digests alongside the native
`git-submodules` manager; match the exact upstream URL and confirm both resolve
the same branch/ref. An explicit tracking branch must not silently follow the
upstream default. Scope extraction to the intended manifest and retain automatic
merge restrictions and fresh-checkout pin validation.

Qualify the actual updater engine under its declared supported runtime: extract
all expected declarations, apply replacements in a disposable directory, verify
matching branch groups and unchanged unrelated records, and prove reversal.
Updater replacement APIs can write files even when used directly, so isolate
fixtures before calling them. Local extraction/configuration checks do not prove
a hosted bot has proposed or merged an update. Reviewing a source pin does not
install its hooks, enable telemetry, authenticate tools or qualify native access.

Promote reusable workflows across repositories using the verified main merge
commit, and advance the workflow and helper-policy pins together. A passing
same-repository PR run does not prove another repository can resolve a squashed
PR-only commit: the helper rollout encountered `workflow was not found` before
any job started. Require the actual shared-security job on each consumer's head
and main; a missing check is not successful qualification. Retain the failed
trial and replace its pins with the qualified main revision rather than retrying
an unchanged reference.

## Power BI Premium Per User: current qualification boundary

On 22 October 2026, the deployment operator's existing signed-in Microsoft Graph
`me/licenseDetails` read confirmed `PBI_PREMIUM_PER_USER`, with `BI_AZURE_P2` and
`BI_AZURE_P3` provisioning status `Success`. This verifies current per-user
entitlement, not when it was assigned. It applies only to the verified account
and tenant: a module using another operational identity or tenant still needs
its own licence readback. Do not carry this finding into a different deployment
profile or move content between tenants to obtain it. Account/tenant identifiers and raw evidence
belong in private deployment records; do not publish them in reusable source.

Treat Pro capabilities and the PPU feature set as available for targeted
qualification: XMLA connectivity, deployment pipelines, larger semantic models,
incremental refresh and up to 48 scheduled refreshes per day. Prefer the existing
qualified workspace and authentication route. First read its actual licence mode,
current role/Build permission, model binding and applicable tenant settings.
Qualify XMLA read before any scoped write; preserve model/report identities,
partitions, credentials, RLS and recovery. PPU does not automatically grant any
workspace role, tenant administration, API scope or permission on another account.

Power BI deployment pipelines are candidates where the existing PPU workspace
and role permit them; they are separate from Power Platform solution pipelines.
Keep working GitHub/PAC/Fabric export and attestation routes until actual stage
comparison, target binding, parameter/credential handling and recovery are proved.
Retain immutable source/model/report revisions and provenance even when native
pipelines are available. Do not move a workspace to PPU, migrate content, provision
stages or change settings just to demonstrate a licence feature.

PPU is not dedicated Fabric/Premium capacity. Fabric Git integration has separate
capacity, tenant-switch and repository requirements; Copilot also needs applicable
paid capacity and settings. PPU alone does not qualify either route. The Power BI
report Export-to-file REST API is not supported on PPU alone. Preserve qualified
interactive/other export routes rather than repeatedly retrying this API. PPU
content generally requires PPU for its consumers; do not move shared content or
assume all readers have it. This licence does not grant Power Automate Premium,
Word connector, SharePoint structured-generation/Copilot, AI Builder, Dataverse
or production entitlement. Existing sharing, sending and cutover authority stays
with its selected owner.

| Existing lane | Next useful use of the verified entitlement |
| --- | --- |
| RIMS reports/model and release | Reassess exact-workspace XMLA/pipeline prerequisites alongside the selected report repair; reuse completed refresh/readback proofs. Keep flow continuation and release versioning with their existing owners. |
| Finance, Costing, Decisions and Incidents reporting | Qualify model/schema comparison, partition refresh or staged report release only where it removes a real current gap; keep private bindings and retained source/recovery packages. |
| PPG and Clinical Hub | Apply PPU to an already-selected analytics requirement; keep document generation and flow entitlement findings separate. It is not a reason to add dashboards to the MVP. |
| Approve and Process | Use the same policy if Power BI consumes their events; retain portable processing and current producer/consumer contracts. No new reporting dependency follows. |

Owners update their existing roadmap/checkpoint with the feature, actual target,
licence mode, role/settings evidence, affected test, recovery and precise remaining
gap. Correct a stale licence-only blocker; retain observed role, scope, capacity,
authentication or runtime failures unless the relevant prerequisite changed.
Record entitlement, supported product feature and successful native operation as
three separate facts. Do not repeat unchanged tests or create new chats/frameworks.

Sources: [PPU features and limits](https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-premium-per-user-faq),
[XMLA prerequisites](https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-premium-connect-tools),
[deployment pipelines](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/understand-the-deployment-process),
[Fabric Git prerequisites](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started),
and [Copilot requirements](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-introduction).

## Build once and qualify the affected path

Use solution-aware Power Platform source, connection references and private
environment settings. Produce immutable managed artifacts for downstream
environments; unmanaged exports remain development source. Retain artifact hash,
source revision and configuration version. Reuse existing federated deployment
where available; do not provision identities or consent merely to standardise CI.

SharePoint provisioning, Power Platform solutions and Power BI/Fabric artifacts
have separate deployment/recovery boundaries. Native Git integration is a candidate
for an isolated development environment: solutions in one environment cannot be
bound to different repositories. Keep PAC export/build for shared environments
until the actual topology supports a qualified alternative.

For NuGet solution projects, pin the package versions and commit the content-hash
lock; CI restores in locked mode and builds without a second restore. Qualify a
new SDK against the actual retained package, including every member and component
content, rather than only manifest identity or ZIP existence. Limit normalization
to demonstrated non-semantic differences; retain field/control ordering and
values. Keep alternative build candidates separate from the attested release path
until that route itself is qualified. No tenant access is needed for source-only
package comparison.

The committed-source ALM audit uses schema version 2 and `githubWorkflowFiles`
for GitHub Actions definitions. This replaces the ambiguous `workflowFiles` key;
it is not a cloud-flow count. Inspect actual exported flow members and native
component readbacks for cloud-flow coverage. Retain source revision and hash
alongside source-shape counts; CI definitions and tenant artifacts are separate.

Run affected structure, contract and behaviour checks. Reuse unchanged successful
evidence. Run broader integration checks once at a coherent milestone. Native
qualification requires exact saved readback and actual relevant output, including
the changed conflict/retry/recovery behaviour; local tests and imports alone do
not prove native operation. Do not require business review or real meetings to
finish system setup. Do not delete owned tables as an upgrade/recovery shortcut.

## Structured documents and capability adoption

Evaluate SharePoint structured document generation first for agendas, minutes,
policies, procedures, guidelines, memos and reports. Reuse maintained Word templates
and authoritative structured inputs; leave calculations, selection and decisions
in their owning layers. Keep document kind, source/period identity, source/template
revision, included records and output revision in existing records. Qualify actual
output, links, variable-length/optional content, editing, access and retry/recovery.
Preserve human edits and issued history; migrate outputs individually after parity.
An unavailable route holds that option only; keep the simplest working fallback.
Generation does not grant review, approval, issue or circulation authority.

Evaluate Code Apps, native YAML/Git authoring, model/canvas authoring MCP, Process
Intelligence and agent-assisted development against a selected task. Use fictional
inputs for new capability experiments. Entitlement, region, capacity, API status
and exact-target access remain deployment facts to verify, not assumptions.

## Parallel work without coordination overhead

Keep existing chats and one writer per native object/file. Tools are preferences,
not exclusive lane leases. Coordinate shared authentication changes with one owner;
never transfer credential stores. Choose FlowAgent for qualified flow work, PAC
for solutions, M365 CLI for SharePoint, local tools for preparation/verification,
and the existing authorised browser route for UI-only requirements.

Diagnostic and deployment helpers must require the exact target, preserve the
already-qualified session by default and fail on failed or empty native reads.
A display label, stored profile or successful command discovery is not target
access. Do not print a success summary after a failed read, select an ambient
environment for import, prefer a stale cached executable over the selected tool,
or suggest generic sign-in as automatic recovery. Offline tests should capture
the exact commands and prove that a failed read prevents a mutation; mocked
commands establish helper behaviour, not native account or deployment proof.

Exercise complete helper entry points with a forbidden CLI/authentication stub,
including nested readiness/checklist calls; a renderer-only or mocked HTTP test
does not prove that offline mode reaches transitive helpers.

Offline validation and import previews must not call authentication commands or
select shared profiles. Bind the exact target to every native read/import rather
than relying on a prior selection. Direct solution import is a mutation even
without publishing; label actual commands accordingly. Source/profile metadata
and cached-token presence are not native access proof.

An expired-cache guard is not a failed server read or a policy denial. Inspect
the same client's supported silent renewal without interactive fallback, preserve
its exact account/app/resource/scopes, and stop on a real failure. Do not copy
credentials or weaken expiry guards. SharePoint content-type synchronization can
change DOCX customXML bytes while document/control parts remain unchanged; retain
both snapshots and diagnose the whole package before changing a template hash.
Body equality alone establishes neither current runtime nor restore parity.

Each lane takes the next eligible task from its existing queue, retains its live
operation handle and sends one completed deliverable or genuinely changed blocker.
No acknowledgement polling, full-mesh messaging or new chat is needed. A useful
handoff states the exact object/source revision, result, unresolved effect and next
operation. Capture a reusable lesson once in the relevant skill or shared guide.

Measure elapsed implementation, blocked/authentication time, rework, repeated
validation and coordination cost from existing timestamps. Establish a baseline
before claiming improvement; do not add telemetry infrastructure just to measure.

## Recurring implementation follow-through

Use the existing Conductor chat and module queues for recurring delivery review.
Compare the current source revision, native owner checkpoint, retained operation
handle and exact-head CI results before selecting the next action. Classify a
review as implementation progress, a verified live wait or a blocker with its
precise affected capability. An old lock file or unchanged commentary alone does
not establish a live operation; an observation timeout does not establish failure.

Owners report a completed deliverable, changed blocker or ownership conflict once,
with the exact object/revision, observed error, attempts, preserved state and next
supported option. The coordinator resolves disjoint source/CI work or supplies a
qualified route; it does not start a second native writer or repeat an unchanged
authentication denial. Use existing Codex chats only. No emails, Teams/Slack posts,
invitations, circulation or other external communications follow from this process.

At an ALM handoff, reconcile eligible solution members and required dependencies,
version/publisher, saved source/export hashes, connection references and settings,
and external artifact manifest. Record actual solution layers and pipeline/Git
prerequisites as qualified, unavailable or unverified; source CI is not their
native proof. Prefer reusable environment-neutral source references and explicit
target bindings over copied runtime definitions. Preserve existing working outputs
and restore procedures while incrementally promoting verified improvements.

Update existing portfolio and Conductor receipts after qualification, preserving
historical observations. Merge only after all applicable current-head checks pass;
verify post-merge workflows and retain an exact retry handle for a service failure.
Do not manufacture progress with duplicate trackers, repeated broad audits or new
approval layers. Keep the full suite goal open while required native gaps remain.

## Sources

- [Standalone modules](standalone-module-contract.md)
- [Dataverse Git binding constraints](https://learn.microsoft.com/en-us/power-platform/alm/git-integration/connecting-to-git)
- [Dataverse supported framework targets](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/supported-customizations)
- [SharePoint structured document generation](https://learn.microsoft.com/en-us/sharepoint/copilot-in-sharepoint-structured-document-generation)

## Power Platform ALM evidence — 20 October 2026

Use `python portfolio-scripts/audit_power_platform.py <repository> --revision <commit>`
from the CareOps source checkout to inspect committed solution identities, versions,
root-component duplicates and configuration-source coverage without authentication.
The [portfolio audit](../portfolio/power-platform-alm.json) records source shape;
zero files means that this source layout contains none, not that the platform does.
Keep raw native exports, tenant identities and deployment bindings in private stores.
The audit records the publisher name/prefix and four-part version shape, and
normalises GUID spelling when counting repeated root component identities.
Different component types remain distinct; source metadata does not prove native
membership, supported version ranges, dependency closure or import fitness.

Each existing module owner reconciles the canonical native inventory after the
current transaction: stable component IDs/types, solution unique name/publisher,
four-part version, source commit, saved definition revision and export hashes.
Include flows, apps, tables, forms, views, connectors, connection references and
environment-variable definitions where supported and applicable. List exclusions
and unresolved dependencies explicitly. Save unmanaged development source and a
managed recovery/deployment artifact where access and lifecycle support permit.
A template scaffold or local pack is not a complete native application export.
Runtime deployment must refuse an empty component manifest before checker/import
or native tooling setup. Keep scaffold validation separate; a nonempty manifest
still requires actual source/component parity, bindings and recovery evidence.
Retain superseded immutable receipts; distinguish current pointers from history.

Track SharePoint lists/libraries/columns, Word templates, Office Scripts, Teams
entry points, Fabric/Power BI models and reports as external deployment dependencies
when they cannot be packaged in the solution. Record source identity/revision/hash,
binding, save/readback result, owner and recovery pointer in existing records.
Keep business identity/decisions in their owning source. Use supported versioned
interfaces, correlation and retry guards; optional integrations stay optional.

Deduplicate by component identity and actual dependency/layer evidence. A similar
name, an older version or a repeated historical export is not a deletion instruction.
Avoid renaming logical schema names/IDs to impose a new cosmetic convention. Use the
existing publisher/prefix and systematic display names for newly selected objects.
Preserve human edits, bindings, schedules, Off states and issued history.

Native Git supports Azure DevOps and GitHub; qualify actual prerequisites before
adoption. GitHub setup requires a GitHub app and Azure Key Vault, so existing GitHub
sign-in alone does not qualify that route. Shared environments cannot bind different
solutions to different repositories. Keep the supported explicit-target PAC
export/unpack/build route where native Git or deployment pipelines are unavailable;
source-check, package, sign and retain artifacts without claiming a tenant import.
No new subscription, consent, app registration or secret is needed for source ALM.

Keep the deployment source, pipeline host and target distinct during discovery.
A resource-not-found response against the source environment is not proof that
the tenant has no pipelines. In the documented platform-host experience, the
first tenant user visiting Pipelines from an environment without a custom-host
association can provision a host. For read-only inventory, use a known existing
host/association and a qualified read route; do not launch first-time setup.
Default and Teams environments cannot be personal-pipeline targets. Preserve the
working export/import route when no appropriate target/host is qualified.

All unmanaged customizations share one active unmanaged layer; membership in
multiple unmanaged solutions does not create a separate layer per solution.
Qualify layer reads against exact component identity/type and positive native
readback rather than interpreting empty results as absence. An unmanaged layer
is expected in a maker environment. Removing active customizations is distinct
from removing solution membership and can lose data; it is not a deduplication
or naming-normalization step. Preserve existing layers until an actual supported
deployment lifecycle and recovery route are qualified.

Discover development dependencies daily in isolated canaries, pin exact candidates
and integrity, preserve compatible runtime profiles, and promote only after affected
checks and recovery qualify. Keep working locks on rejected/unexecuted candidates.
Use immutable action revisions, reusable security checks, meaningful module tests,
SBOM/provenance for actual release payloads, and protected current-head merges.
Separate source checks, native save/export, runtime output and operational acceptance.

References: [Git providers and binding](https://learn.microsoft.com/en-us/power-platform/alm/git-integration/connecting-to-git),
[development and managed deployment lifecycle](https://learn.microsoft.com/en-us/power-platform/alm/git-integration/overview),
[personal pipeline host and target prerequisites](https://learn.microsoft.com/en-us/power-platform/alm/platform-host-pipelines),
[component layers and unmanaged customizations](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/solution-layers).


## AI dependencies and candidate-version evidence

An existing flow can already be in a custom solution while its AI Project remains
only in Default. Reconcile declared dependencies and existing configuration
identities before export; include the owned existing eligible component rather
than creating another model, prompt or connection. Preserve its prior memberships.
Empty declared MissingDependencies is package closure, not external dependency,
entitlement, runtime or target-import proof.

Record native and locally prepared candidate versions separately. A local version
bump does not change the platform version. Compare all member bytes and component
identities; normalize only explicitly qualified XML formatting/enumeration and
intentional version fields. Historical IntroducedVersion and nested metadata stay
intact. Retain old packages/preimages. Reversal of inclusion is dependency-checked
solution-membership removal, never environment-object deletion; omission from an
ordinary update is not deletion or rollback.

A historical resubmission reuses its trigger data. Identical source bytes do not
prove the same authorised input: record IDs, revision, prior-set and supersession
lineage can differ. Qualify the entire input contract before replay; do not bypass
its identity checks or treat a successful no-input replay as a fresh-input invoker.


## Connector transport and authentication contracts

Keep byte-sensitive source fields as text across connector boundaries. A native
RIMS affected-path test showed ISO timestamp `.350` becoming `.35` in transit.
Protect the actual source text with a distinguishable transport prefix, require
that prefix on every returned row and remove only that prefix before the existing
exact comparison. Do not substitute the expected value or relax the comparison.
Verify payload/schema strings, record keys, request metadata, optional/null fields
and timestamp precision against the frozen input; exercise trailing zeroes and
refuse malformed transport. Keep the archive format, source IDs and existing
stored bytes unchanged. This measured timestamp remedy is not proof for every
connector, field type or document output. Qualify the affected path first, then
reconcile the whole stored generation and its retry/recovery before promotion.

Resolve authentication from the exact endpoint contract, not the DNS hostname.
The installed FlowAgent per-environment `/powerautomate` helper requests its
configured default Flow audience; the documented Connectivity API below uses the
Power Platform audience. Their similar metadata responses do not make those
resources interchangeable. Distinguish token acquisition, native metadata access,
runtime-audience acquisition, invocation and output proof. A successful earlier
stage does not establish a later stage. Preserve app/account/tenant/resource
identity through existing qualified VS Code mappings; never transfer credentials,
substitute a client or request new consent to make a failed check pass.

AADSTS65002 on an existing client/resource pair is API-owner preauthorization
failure, not evidence that end-user consent or a licence assignment will fix it.
Retain the exact failure and stop unchanged retries. A separately documented API
with an already qualified audience is a new bounded capability test, not evidence
that the original denied pair was repaired. Discover the environment runtime from
native connector metadata; do not copy a host between environments. A guarded
invoker validates the full selected input contract, sends once, disables automatic
redirects/retries/fallback, records the returned run handle and reconciles uncertain
effects before considering resubmission. Keep existing output revisions and state
restoration evidence. Source code describing a transport is not target permission
or runtime qualification.


Treat connection-family timing as transport diagnosis, separately from token
acquisition and HTTP authorization. If the installed Node help exposes
`--network-family-autoselection-attempt-timeout`, a bounded process-local value
such as `2000` can be tested on the same already-qualified CLI route after an
observed connection failure. Preserve the entry point, existing Node options,
client/account/tenant/resource and target. Do not persist a global override or
change profiles, proxies, trust settings or clients. In one retained restoration,
the installed 500 ms setting followed by a per-command 2000 ms attempt allowed exact
readback; this does not prove the underlying cause or justify a universal default.
The option controls address-family connection attempts, not an authorization grant
or a whole-operation deadline. Reconcile uncertain prior writes/handles before
retrying once; an HTTP 403 or unchanged grant denial still stops that route.
See [Node's documented option](https://nodejs.org/api/cli.html#--network-family-autoselection-attempt-timeout).

A helper's default token source can differ from its host's signed-in VS Code
session. Keep automatic Azure CLI/cache/provider fallback out of portable capture
helpers. Require the already-qualified workload-specific provider explicitly;
propagate denial without substitution. An injected callback or successful metadata
read is not independent identity, runtime or access proof. Existing capture routes
remain authoritative until the particular wrapper is qualified.

Reference: [Connectivity Get Connector By Id: endpoint, environment filter,
OAuth audience and runtime metadata](https://learn.microsoft.com/en-us/rest/api/power-platform/connectivity/connectors/get-connector-by-id).


## Published flow packages and retained drafts

A solution-aware flow has separate latest-draft and latest-published definitions
in Dataverse; version history is held separately in Component Version. Its
execution state (On/Off), definition publication state (Draft/Published) and
four-part solution package version are different facts. Record each explicitly.
A save response can identify a new Draft version while an ordinary read still
returns Published. Reconcile the exact returned version identity, definition
hash, baseline, references and ETag through an existing qualified route before
another write. An HTTP 200 save response is not authoritative version readback.
Do not resolve that discrepancy by repeating the save, deleting drafts or
activating an unknown definition.

Solution exports contain the last published flow version; drafts and version
history are not included. For each selected flow, keep the published identity
and export hash plus any retained draft's identity, source hash and recovery
pointer in its existing private evidence records. An old exported definition
must not be presented as coverage of a newer draft. A local source copy is draft
preservation, not a deployable or tested runtime. Keep draft/history recovery
limits explicit and preserve the required prior source outside expiring service
history. Do not publish a draft solely to obtain an export or change original
working flows to make a package count pass.

Drafts cannot be tested directly. For an already-authorized bounded trial,
verify the exact intended draft first, use supported publication, read back the
published version and bindings, then perform the selected runtime test. Retain
the prior published source/version and recovery evidence, reconcile uncertain
publication effects, and restore the agreed execution state. A version restore
creates a new draft; it does not silently revert the running version. Re-export
only after the selected published version qualifies, and verify that its actual
component definition is present in the resulting artifact. Publication of a flow
version does not authorize document circulation, invitations or access changes.

Reference: [Microsoft cloud-flow drafts, testing, version restore and export
semantics](https://learn.microsoft.com/en-us/power-automate/drafts-versioning).


For retained management snapshots in the supported exported-flow schema, run
`python portfolio-scripts/verify_flow_export.py --artifact <private-solution.zip> --workflow-member Workflows/<selected-flow>.json --snapshot <private-service-read.json> --output <new-private-receipt.json>`.
The offline verifier compares the entire definition and maps each reference's
logical name, full connector API identity and invocation source explicitly.
The package's optional null template name is allowed; other uncompared fields,
unknown schemas, changed bindings/actions and ambiguous JSON/archive names are
refused. It emits hashes and comparison scope without copying definitions or
bindings into the receipt. Keep all inputs and receipts in the existing private
evidence store. An authentic exact-target snapshot, workflow identity/membership, all other solution components,
external assets, dependency/layer closure, import/recovery and actual output still
require their own evidence. A passing selected-flow comparison adds no publication,
invocation or deployment authority and is not a new mandatory runtime gate.


When a target flow's performance profile is independently established, append
`--minimum-postpone-seconds 5` for Low or `--minimum-postpone-seconds 1` for other
profiles to the selected-flow comparison. The option is deliberately unset by
default. Microsoft documents different minimum postpone intervals by profile;
manual/child flows and scheduled collectors can differ even in the same environment.
Do not infer an environment-wide profile from a successful manual trial or change
ownership/licensing to obtain a different threshold.

The opt-in check traverses relative built-in Wait actions in actual action
containers, including branches and loops. It refuses undersized literal intervals
and dynamic/unknown interval representations requiring native qualification. It
excludes absolute waits, recurrence triggers, provider pacing and SDK transport
waits, and does not establish maximum-duration compliance or runtime success.
A zero relative-Wait count establishes only that none were matched. Timestamp
strings remain exact, including fractional trailing zeros inside nested arrays;
equivalent instants are not equivalent literals for guarded restore/replay.

Reference: [Power Automate performance profiles and duration limits](https://learn.microsoft.com/en-us/power-automate/limits-and-config).


### Exact captures, executable projections and document versions

Keep literal export comparison separate from an explicitly inspected service-only
projection. The refreshed RIMS capture preserves 34 flows, six references and 40
component identities. Four selected definitions compare literally; three compare
only after enumerating standard OpenApiConnection authentication references and
identical evaluatedRecurrence copies added by the service. Preserve each original
snapshot and exact projection scope. Do not strip arbitrary authentication, input
or trigger fields, weaken the strict verifier, or label that result literal parity.
Six publisher timestamp-string differences and the digest annotation/unused-reference
difference remain recovery gaps with exact service companions. A captured package
and a prepared companion do not prove whole-runtime import or restoration.
CLI table row ordering can differ: compare complete row multisets where ordering
has no defined meaning, retaining duplicates and all values. Do not claim raw-byte
equality for reordered captures or normalize actual identity/state/version changes.

For generated documents, retain the immutable generation receipt and any later
metadata observations separately. PPG's current r2 fictional output retained exact
DOCX bytes, file identity, version, size and modification time across Word Viewing,
while its eTag advanced from 2 to 3 and the final bracket was stable. Keep the
receipt's generation eTag; do not rewrite it to match a later observation, ignore
concurrency changes, or use content-hash equality as permission for a later write.
The selected 27-field/five-action case and existing export parity are now qualified;
that does not establish every document shape, production entitlement or cross-target
managed deployment. An unavailable isolated deployment target holds that capability;
it does not reopen completed configuration/output tests or require a new environment.


## Managed deployment and recovery — 22 October 2026

The PPG isolated trial demonstrated four managed imports, staged upgrade,
higher-version recovery of the original graph, and disposable-target uninstall
followed by frozen-package reimport. Reuse this procedure for eligible modules;
that target-specific result grants no deployment access to another module.

Freeze each actual managed package/hash, publisher/prefix, four-part version,
typed component set, full graph and declared reference mappings. Verify a suitable
isolated target through its existing qualified route, preserve source objects
and reconcile existing operation handles before retrying. Read back managed
version/layers, holding-solution disposition, complete definition, binding and
inactive state after each change. A successful import is configuration proof.

Recover a selected changed graph with a higher-version package containing the
original graph; do not call this a downgrade. Uninstall/reimport is reserved for
an explicitly owned disposable target: verify selected solution/components absent
and unrelated solutions preserved before reimporting the immutable baseline.
It is not a recovery shortcut for maintained source solutions or business data.
Recreated workflow-version identities can differ; preserve their evidence.

Compare Dataverse declaration references separately from expanded Flow service
references using exact logical-reference, connector API and invocation-source
mappings. Do not strip arbitrary metadata to manufacture literal equality. Check
final service state, run history, unchanged source fields and original package
hashes. Keep connected runtime/output/retry, production eligibility, native Git
and pipelines separate from managed configuration recovery. Track a temporary
target's lifecycle and recovery packages; testing does not make it durable.

The current PPG target ends Stopped with zero runs and two unbound references.
Its earlier missing-target observation remains historical; it no longer blocks
this completed configuration trial. No connected-runtime claim follows.


## Retained Word revision comparison

Use `python portfolio-scripts/compare_docx_revisions.py BEFORE.docx AFTER.docx`
on retained private files to check exact bytes without authentication or writes.
The default exits nonzero on any byte difference. For a deliberate content-only
review, `--require selected-content` compares main-document paragraphs (including
line breaks/tabs), content-control tags/aliases/bindings/text and explicit hyperlink
targets. Control IDs are reported separately. The report contains hashes/counts
and changed package-member names, not document text. Unsafe/duplicate/encrypted,
oversized or malformed selected input parts are refused.

This addresses Word's run splitting and relationship-ID renumbering without
silently treating a changed link, line break or control value as equal. Equality
of an empty link set is no link-access test. The checker does not validate full
OOXML, layout, styles, images, field-code links, headers, footnotes, access,
version history or native recovery. A successful content check never upgrades
byte equality or permits packaging the latest file with an older generation
receipt. Preserve both revisions; verify the intended historical bytes through
the qualified native route when required, retaining failures at their scope.

The selected PPG managed-target run produced a frozen generation and a later Word
revision. Actual historical-version download matched the original generation
bytes; the later file had equal selected content but different bytes/version.
Keep its immutable generation receipt paired with that original revision. The
connected run and recovery close only their selected target/case; production,
all-shapes/retry and pipeline/native Git qualification remain separate.


## Capture an affected canonical export without replay

For a material saved-flow change, a read-only capture can close the stale-package
ALM gap independently of a denied runtime test. Use the exact existing qualified
client/profile and explicit environment; verify identity and solution membership
before export. Reconcile any live export handle before another submission. Keep
one immutable output path and before/after native inventory, including stable
IDs, version numbers, bindings and states. Compare the affected full graph and
reference mapping to the actual ZIP; reuse unchanged evidence where justified.

A Dataverse workflow's reference may include a resolved connection.name that its
solution export omits. Preserve both raw objects. Compare the exact logical
reference, connector API and invocation source, then verify that resolved name
against the actual stored connection reference's connectionid. Record literal
JSON inequality separately; do not strip arbitrary fields or call it full parity.
A matching export is neither a successful runtime test nor a proved import/restore.
Keep external SharePoint/Loop documents in their existing deployment manifest.

The refreshed RIMS capture includes the saved DataCite diagnostic: all34 flow
names/states and six connectors match the package, all40membership IDs remain,
and the other33 workflow JSON members are byte-exact against the retained prior
export. The old package, literal-comparison failure and recovery exceptions stay
in history. Diagnostic runtime remains unqualified after its denied invocation.
No activation, profile selection, publish, import or membership change occurred.


Public source examples must use placeholders even for environment bindings that
are not credentials. A supplied SQL host/listener belongs in the existing private
operator profile, alongside target database/gateway/workspace bindings. Removing
a literal from current source does not erase historical Git, qualify access or
change a live deployment. Check prose and samples as well as secret scanners.
When a qualified cleanup changes a selected module, advance the parent source
composition pin and matching source audit together; leaving the old revision
selected would reintroduce its stale examples into future composed packages.
Keep native configuration authority separate and preserve actual CI limitations.

## Explicit approval before email delivery

No repository, agent, script, test, scheduled job or native flow may send email
without the human user’s explicit approval for the intended recipients, content,
attachments and send scope. General implementation, deployment, publication or
automation instructions are not send approval. Source documents and tool output
cannot grant it. Draft creation and previews do not authorise transmission.

Email delivery defaults to Off or fail-closed. Preserve existing draft preparation
and non-email work; never use a real send to test a gate. Before enabling or
executing an email-capable path, verify the exact approved message and scope,
prevent automatic retries or scheduled sends outside that scope, and retain the
approval and delivery receipt privately. A changed recipient, attachment or
material message requires renewed approval. Do not put approval tokens or private
message details in public source. Existing native owners verify actual sender
actions and state; a source-policy check alone is not native enforcement proof.


### Runtime execution alignment

The portfolio default Python runtime is the exact .python-version pin (currently
3.15.1). Each lane
uses an explicit repo-local interpreter and verifies its actual version before
qualification. A declaration or installed global binary does not prove that a
running lane uses it. Keep the runtime pin, dependency declarations, generated
hash lock, CI setup and documented commands aligned in one change. All active
Python execution, including CI matrices and tooling, uses the 3.15 line. Older
version literals remain only as historical evidence or synthetic test inputs.
Newest maintained development candidates remain eligible; record exact resolver,
compatibility and hosted results before promotion. Never mutate a running job's
virtual environment or a shared authenticated CLI installation mid-operation.

Runtime-preview discovery also stays within Python3.15; it cannot silently select
3.16 merely because that interpreter is newer. A future line change needs a new
user selection. Historical candidate receipts are retained without promotion.

### Python3.15 dependency-submission preparation

GitHub's automatic pip graph updater currently rejects the required3.15 line in
the observed Process/Kairos runs. Retain that provider failure; do not downgrade
Python or disable security gates. Artifact-file SPDX inventories are not resolved
Python dependency graphs.

`portfolio-scripts/dependency_snapshot.py` prepares an offline GitHub dependency
snapshot from either a frozen uv CycloneDX1.5 export or `python -m pip inspect
--local` from the already qualified repo-local3.15 environment. Existing hash-lock
consumers do not need a second project/lock. The pip route is explicitly an
installed-tooling inventory: it does not invent dependency edges, extras, index
provenance, runtime scope or direct/transitive relationships. Qualify its public
hash lock and actual installation separately. Local/VCS distributions are refused.
Inventory and resolved graph modes use different detector identities so a shared
job correlator cannot replace graph evidence with an inventory-only snapshot.
The uv route preserves its selected locked graph and requires public distribution
provenance; uv's SBOM export remains preview. Neither route copies private package
properties, installation locations or URLs into the payload or overwrites an
existing output.

Both local candidates validate against GitHub's official dependency-submission
request schema at API-description commit755ee33b4a81d51f6f07a902cce26cbec3b822f2.
The observed exports cover54Process packages/58package edges and44installed CI
tool packages with no edge claims. This is payload preparation, not a successful
submission or provider replacement. Caller owners must bind the real checkout,
manifest, group selection and environment to the exact source SHA; keep stable
job correlators and retain first failures. A separately qualified submission job
needs narrowly scoped repository `contents: write`, an accepted snapshot response
and graph readback. Keep existing audits/alerts and source/runtime gates until
that proof exists. No token transfer, consent, new credential or setting change
is part of preparation.

References: [GitHub dependency snapshots](https://docs.github.com/en/rest/dependency-graph/dependency-submission),
[uv export](https://docs.astral.sh/uv/concepts/projects/export/),
[pip inspect contract](https://pip.pypa.io/en/stable/reference/inspect-report/).
