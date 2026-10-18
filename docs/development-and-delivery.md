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

Each lane takes the next eligible task from its existing queue, retains its live
operation handle and sends one completed deliverable or genuinely changed blocker.
No acknowledgement polling, full-mesh messaging or new chat is needed. A useful
handoff states the exact object/source revision, result, unresolved effect and next
operation. Capture a reusable lesson once in the relevant skill or shared guide.

Measure elapsed implementation, blocked/authentication time, rework, repeated
validation and coordination cost from existing timestamps. Establish a baseline
before claiming improvement; do not add telemetry infrastructure just to measure.

## Sources

- [Standalone modules](standalone-module-contract.md)
- [Dataverse Git binding constraints](https://learn.microsoft.com/en-us/power-platform/alm/git-integration/connecting-to-git)
- [Dataverse supported framework targets](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/supported-customizations)
- [SharePoint structured document generation](https://learn.microsoft.com/en-us/sharepoint/copilot-in-sharepoint-structured-document-generation)
