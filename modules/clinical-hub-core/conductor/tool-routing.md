# Tool routing and access

## H2 native configuration —28October2026

Reuse the current private H2 exact-target binding/operation manifests and guarded
SDK reader/writers. The four fictional configuration records, type/view/field and
selected-owner form evidence are indexed in [the H2 queue](h2-native-implementation.md).
No H2 flow has been created or run. Source package preparation uses the module-local
Python3.15.1 interpreter and [`forum_native_package.py`](../scripts/forum_native_package.py);
it grants no native rights and does not run operationally in Power Automate.

For schema bootstrap, installed CLI/API semantics require NoContentType(2) plus
InternalNameHint(8), Options10, to preserve explicit internal names without linking
new fields to the default Document type. Reserved site-parent type IDs differ
from the native library-copy IDs: save absent parents, attach only selected local
copies, then read back their IDs/scope before field links. Preserve existing types,
columns, default views, files and ACL. Schema ManageLists/ManageWeb masks do not
prove file Add/Edit/ViewVersions or connector runtime rights; qualify each actual
operation and retain native readback. Owned fictional saves used exact item ETags,
native entity types, UTC dates and typed multi-choice collections. Binary reads
check actual byte hashes; a failed assertion after save never authorises resubmission.

Default item reads can omit hidden fields. Select required hidden fields explicitly
before declaring values absent or repairing a record. Use native item IDs, file
UniqueId, edit links, ETags and versions as identity evidence; generated root item
`odata.id` annotations differed in an observed unchanged roundtrip. Retain raw
responses and scope any presentation comparison rule narrowly. Do not normalize
other native identities or ignore unexpected changed data.

A native realtime subscription is not automatically a mail alert or flow listener.
H2 qualified its one exact subscription against the selected library's native
WebSocket response (ID, state, base URL/token and pinned caller parameter), plus
separate alerts/rules/assignment/approval checks. Do not allow arbitrary webhook
hosts or subscriptions based on that observation. Keep notification URLs/tokens
private and do not delete service subscriptions to obtain a passing gate.

**Check dependent tool results before any mutation.** `exec_command` can return
exit_code1 without throwing a JavaScript exception. A yielded session is not a
terminal result. The private scoped plan-check wrapper must emit its exact JSON
PASS receipt; compare the reviewed change, asset and payload before dispatch.
For example, the tested guard pattern is:

```javascript
const result = await tools.exec_command(planCheck);
if (result.exit_code !== 0 || result.session_id != null) {
  text(result);
  exit();
}
const receipt = JSON.parse(result.output);
if (receipt.status !== "PASS" ||
    receipt.change_id !== expected.change_id ||
    receipt.asset_key !== expected.asset_key ||
    receipt.payload_sha256 !== expected.payload_sha256) {
  throw new Error("Prerequisite does not match the reviewed operation");
}
// Only now dispatch the separately authorised, exact-target operation once.
```

Do not catch a prerequisite error and continue with a native/UI action.12 negative
process/receipt cases dispatched nothing, and real context/expiry refusals also
stopped before Save. A previous fictional save that ran after an ignored failure
is recorded as an incident; no prior plan was backfilled. Preserve such history.
Within journal helpers, record an existing change against its original planned
asset; never share a target-key variable with a property iteration.

Use browser tools only for actual rendered-form/interaction proof. A reconnected
browser loses tab ownership: list, reclaim the known task group and use the fresh
returned page ID, not a matching foreign/ghost tab. Check the exact form target and
server page principal (exact membership component, not a suffix match). A browser
context refusal is not native save failure; read the target before resuming any
unsubmitted case. SharePoint date displays follow regional settings: use pickers
and explicit UTC/timezone readback. Leave others' tabs, access and workflows alone.

A saved package/flow or a Connected reference still does not prove runtime, replay,
recovery, role denial or notification suppression. Complete those gates on the new
held candidate, leaving all existing flows and deferred correspondence unchanged.


## Automatic correspondence actions — 27 October 2026

Use the [stopped-worker implementation and recovery guide](correspondence-automation.md)
and current COR-16 track before interpreting older plan-only checkpoints below.
The new source compiler reuses the manual identity/claim/recovery graph. Source
tests and stopped native configuration are verified; no worker runtime or activation
is established. Both enable flags remain false. Existing intake/manual flows and
manual run-only ACL remain unchanged; no new flow-editing audience was granted.

Reuse the private correspondence workload binding and retained VS Code Toolkit
client through the guarded CLI SDK. Selected flow-management expiry was renewed
with the existing same-client MSAL form_post recipe and signed-in work account,
then the affected exact target was verified. No password, MFA, consent, new client,
token transfer or cache reset was needed. Native owner Planner sign-in is now
usable; the plan remains personal/private, so do not repeat the old password
blocker without a new challenge or infer that ESO access was granted.

Native preparation uses exact manifests, prospective journal validation, one
transport attempt, Stopped/disabled flow creation, and independent full definition,
reference, state, owner and zero-run readback. Add optional fields without opting
in existing records, and stage nondefault views alongside the current working
views. Metadata-free SharePoint view creation uses a plain ViewFields array;
ordered field readback requires the ViewFields navigation endpoint. A failed local
readback assertion after save is not permission to create the view again.

ParseJson supports secure inputs for this contract; secure outputs were explicitly
rejected natively. Project only percentComplete into that parser; retain supported
GetTask input/output protection. Preserve the rejection and actual effect readback.
The existing source reader remains GET-only; this implementation's private exact
manifest adapter has separately scoped mutation authority, not a universal writer.

The supported native Repair tips off menu disabled only the new stopped worker's
repair emails, with independent flowFailureAlertSubscribed=false readback. The
known ignored generic PATCH is not a suppression route. Provider weekly digest
preferences remain separate/unverified. Do not start/invoke the worker under the
activation hold, send a test email, change the original intake or claim runtime
success from native save/Flow checker. Fictional runtime/recovery, version-date
qualification and intended-role rollout remain explicit subsequent gates.

## Correspondence solution: execution map — 26 October 2026

### Native preparation route and permissions

For an authorised native preparation, use the private Conductor's current
`correspondence-native-preparation-20261026` operation manifests and receipts.
The installed M365 CLI SDK adapter uses the retained account/client/tenant,
explicit SharePoint or Flow-management audience, and existing client-owned cache.
It permits one exact method/URL/body, disables redirects, refuses transport replay,
and requires a prospective journal plan immediately before each mutation. The
GET-only public reader below does not gain write or renewal privileges.

List creation requires site-level ManageLists; modifying an existing list's schema
uses that list's permissions. Do not infer one from the other or change client to
retry a denied operation. Technical receipts can use another existing authorised
private site, with an explicit separate receipt-site binding. Never widen sharing.
Flow-management configuration save rights and Connected connection metadata do not
prove connector runtime writes. Require full native definition/connection/state
readback and retain raw receipts. Native services can add connector authentication
annotations and an evaluated recurrence; enumerate exact additions and confirm the
latter equals submitted recurrence rather than silently ignoring arbitrary fields.

Prepare with state Stopped, CaptureEnabled=false and a future CaptureStartUtc.
The caller must separately authorise runtime/activation scope; no start, trigger,
run, email, new connection, permission or consent operation is implied. Source-key
constraints must first be tested with fictional isolated records. Rejected writes
need independent readback before another operation. Current actual IDs/status and
working helper paths live only in the private Conductor record.

### Saved working views and read-only filter checks

Use the [operator guide](correspondence-operations.md) and current private Conductor
for exact view IDs and consumed manifests. Read existing fields/Choice values and
all current views before selecting CAML; the Progress display field can have an
internal name such as Completed. Preserve original default and hidden/form views.
Use installed CLI `spo list view add` semantics through the qualified exact-target
adapter: POST `/views/add`, explicit fields/query, PersonalView=false,
SetAsDefaultView=false and bounded paging. Applicable existing-list ManageLists
and a write-capable token are required; no permission expansion follows.

Read back ordered fields and all selected settings. SharePoint can change XML
self-closing whitespace; compare canonical XML structure, retain raw inputs/outputs
and never create another view solely to fix a local string-equality assertion.
SharePoint POST `/GetItems` with CAML is a read-only query: qualify an exact bounded
ID-only body separately from configuration writes, and compare its IDs against an
independent OData filter. Do not treat every POST as a record write, or allow arbitrary
POSTs because GetItems is read-only. Preserve IDs/GUIDs/versions/Modified values and
all earlier view settings in before/after readback. Flow-state GET verifies the
held gate; working-view setup needs no flow start or invocation. UI rendering and
operator acceptance are separate from saved configuration/filter qualification.

### Qualified correspondence reader — local source and bounded native reads

Use [correspondence_cli_read.mjs](../scripts/correspondence_cli_read.mjs) for
named GET operations only. It reuses the installed M365 CLI SDK, verifies private
SDK/client/account/tenant/connection/resource pins, rejects interactive or alternate
credential paths, locks local execution, disables redirects and blocks a second
transport attempt. Raw results stay in the ignored private workspace with mode0600.
There is no write, renewal, activation, invocation or email-send mode.

```sh
node --test modules/clinical-hub-core/tests/test_correspondence_cli_read.mjs
node modules/clinical-hub-core/scripts/correspondence_cli_read.mjs '<private-binding.json>' '<reviewed-read-name>' '<new-private-output.json>'
```

Paths above are relative to the CareOps parent. Bindings must live under the
module's ignored `.private-workspace` real path; outputs require an existing
private parent directory and a new filename. The private record identifies the
reviewed binding and permitted named reads. Do not invent additional endpoints
or replace an existing receipt. After an interrupted run, inspect the local lock's
PID/ownership rather than deleting a live lock. This lock serializes this reader;
it does not control other repositories' processes sharing the CLI cache.

Six offline Node tests pass, including identity/expiry drift, forbidden credential
paths, exact-target GET enforcement, redirects and transport failure cleanup.
Bounded native identity, register metadata/schema/views/permissions and owned-probe
definition reads succeeded; direct personal Inbox metadata returned403. This is
partial access qualification, not mailbox capture or mutation/runtime qualification.
No flow ran. Private evidence distinguishes the exact successes and failure.

Archived-workflow review confirmed that mailbox reads previously succeeded
through CLI management of an existing Office 365 Outlook connector while direct
Graph mail remained403. That connector adapter is the preferred mailbox reuse
route; direct Graph mail is not an MVP requirement. Toolkit-compatible sign-in
authenticates management; the connector retains its own mailbox authorisation.
The Agents Toolkit development CLI and the separate Microsoft 365 MCP client
must not be confused with this route. An explicitly authorised single GET-only
probe run subsequently succeeded for mail/folder/rule/category/calendar metadata.
An independent read verified Stopped with unchanged definition and connections.
This freshly qualifies bounded connector reads; intake triggers/writes remain
unverified. Further changes/runs require their selected scope. During cleanup,
eject only the adapter's own Axios interceptor: clearing all interceptors removes
the SDK JSON parser. Reconcile an existing stop by GET; do not replay the run.

The installed SDK maps the Flow endpoint `https://api.flow.microsoft.com` to token
audience `https://management.azure.com/`. Pin both explicitly for that read; the
reader does not acquire a different client or infer invocation permission. The
first locally rejected audience attempt is retained privately. Endpoint origin
and token audience are distinct, documented mappings; never guess an audience.

Read the [current task checklist](implementation-plan.md#task-checklist--plan-only-26-october-2026)
first. Feasibility/local guard preparation and bounded reads are authorised;
native changes and activation remain on hold. The runtime must use standard connectors, no Premium
connectors, Copilot or AI Builder; no email sending and no investigation of other
people's workflows/access. The public examples below are placeholders. Resolve
actual bindings from the ignored private correspondence record, not from guesses.

| Tasks | Tool / purpose | Required qualification and current limit |
|---|---|---|
| COR-01/02 | Guarded M365 CLI `entra user list`, `spo list/field/list view`, `flow list/get` | Selected directory/register/owned-flow reads succeeded. Directory identity does not prove mailbox access; an inventory is not tenant-wide or necessarily complete. |
| COR-03 | Local schema mapping and fictional fixtures; existing native field metadata | No message content needed for contract drafting. Keep exact bindings private and legacy data intact. |
| COR-04 | Guarded M365 exact reads; shared auth recovery recipe only if expired | Verify client/account/tenant/resource, target rights and guard command coverage. Historical login and permissions are not current target proof. Resolve the local journal prerequisite before saves. |
| COR-05–08 | Qualified CLI and supported Power Automate/SharePoint APIs | Native edits need exact flow/connection/list rights, prospective journal checks, guarded submission and independent readback. Not yet qualified for correspondence writes; mailbox reads and trigger execution are also separate checks. |
| COR-09 | Qualified native invocation and saved configuration/output reads | Flow management GET does not prove invocation, connector ACL or mailbox access. No test email. No guessed callback or client switch after denial. |
| COR-10/11 | Local source/link/content checks; existing Git/GitHub delivery route when publication selected | No tenant permission required for local checks. Public push/rendered website are separate verifications; plan edits are not publication. |
| COR-12 | Existing suitable Basic Planner plan and standard Planner connector through a qualified CLI/API route | Plan access, connector identity, exact task operations and notification effects must be established. No Planner permission or write is currently proved. No premium fallback. |
| Selected solution metadata only | Extension-managed PAC | Separate environment roles and retained auth; not an automatic dependency and not a cloud-flow invocation substitute. |

### Ordered entry procedure

1. Read shared `microsoft-cli-operations` and `microsoft-365-auth` skills, including
   the latter's verified workload recovery recipe. The shared correspondence
   runbook provides cross-repository implementation pointers. No fresh login was
   obtained during correspondence discovery: an existing named CLI connection
   was reused. Historical recovery uses the same client/cache and qualified MSAL
   `form_post` callback; it does not extract VS Code credentials.
2. Locate and inspect the workload's guarded entry point and private pins. Bare
   `m365 status` and reads can initiate stock interactive login on expiry. Do not
   repeat them as the default recipe. Serialize commands sharing auth/cache state.
3. Verify the guard allows the exact command/resource. The existing RIMS guard
   supports file reads and flow get/run reads; it is not a drop-in guard for
   directory, list, Planner or arbitrary requests. This module's reader above now
   qualifies reviewed exact GETs for correspondence; mutations/invocation remain
   outside its scope. COR-04 retains the unresolved mailbox/save prerequisites. Never
   borrow another repo's private binding or bypass the allowlist.
4. Discover syntax with MCP `m365_search_commands`, then `m365_get_command_docs`.
   The wrapper's `m365_run_command` executes CLI commands but does not supply
   permissions or establish guard coverage. Use a qualified execution entry point.
5. Make a bounded read of the exact target and compare identity/binding. Persist
   necessary raw results privately; print only selected metadata. Avoid full flow
   swagger output and never print tokens or connection caches.
6. Stop unchanged denied operations. For expiry, use the one owned recovery
   procedure and verify the affected resource afterwards. For writes, auth guards
   do not replace single-submission guards, journal checks or effect reconciliation.

Argument templates to pass through a qualified guard after command-doc checks:

```text
entra user list --displayName <narrow-prefix> --properties displayName,mail,id --output json
spo list get --webUrl <saved-site> --id <saved-list-id> --output json
spo field list --webUrl <saved-site> --listId <saved-list-id> --output json
spo list view list --webUrl <saved-site> --listId <saved-list-id> --output json
flow list --environmentName <known-environment> --sharingStatus all --withSolutions --output json
flow get --environmentName <known-environment> --name <saved-flow-id> --output json
```

### Permission interpretation and known boundaries

- The directory command documents Graph User.Read.All; successful selected reads
  do not establish actual token claims, a shared mailbox or its delegation.
- SharePoint reads use their own resource token. The inspected list's effective
  rights included ManageLists; public view-add docs specify delegated AllSites.Write
  plus applicable list rights. No correspondence native write has been tested.
  Role-assignment enumeration was denied; it is not required to investigate others.
- Exact shared Inbox metadata GET returned403. This proves failure of the CLI
  route, not absence of the user's Outlook permission. Personal intake still
  needs its own route check. Do not infer Full Access or Send As.
- Selected channel metadata worked; tab scope and named-member reads did not.
  Do not infer TeamsTab.Read.All or ChannelMember.Read.All from channel read success.
- Power Apps environment listing returned AADSTS65002. This client/resource
  preauthorisation failure did not invalidate distinct successful Flow reads.
- The stopped [Outlook connector probe](outlook-connector-cli.md) has historical
  GET qualification through its own connection. Editing/enabling/running it is
  a native operation, not read-only discovery. It must not be invoked in plan mode.
- PAC's inspected version has flow-list/action/run-history commands, not a
  supported cloud-flow invocation command. Azure/FlowAgent/Microsoft 365 MCP are
  separate clients, not fallback grants or interchangeable login stores.

Developer-tool access and runtime connector licensing are different. Record exact
operation, identity, resource, result and limits privately. Never claim mailbox
access, save, runtime success or operational acceptance from a login banner.


| Work | Preferred route | Boundary |
|---|---|---|
| SharePoint records/views/files | Qualified M365 CLI | Exact account and target; conditional writes and uncertain-save reconciliation |
| Flow graph/bindings/run diagnosis | Qualified FlowAgent; retained supported CLI/API route | Compare complete saved graph/state and inspect output |
| Solution export/pack/import | PAC | Target-specific rights; no new environment or registration implied |
| Selected existing API operation | Qualified Azure CLI adapter | No new Azure service or credential transfer |
| Required sign-in/document inspection | BrowserOS Neo | Human password/MFA only when actually challenged |

Reuse successful operations from parallel projects as routing knowledge, not as
proof of permissions on a different target. Keep exact account/licence observations
private. An existing session or developer environment does not establish every
connector entitlement. Do not ask repeatedly for unchanged licence/access decisions.

PAC, M365 and Azure clients have separate auth stores. Preserve active sessions;
never reset shared authentication for routine discovery. One CLI invocation may
retry POSTs: use a qualified conditional/no-retry route where duplication matters.
Read back uncertain effects before another write. Browser sessions do not create
new permissions. Keep current working routes until a required replacement passes
its affected checks. Latest project dependencies are pinned; shared CLI upgrades
must not interrupt another operation.

## Planner connection checkpoint — 26 October 2026

The user-established Standard Planner connection is now independently verified
Connected in the selected environment. This supersedes older connection-absence
statements; exact account/environment/connection bindings remain private.
The direct Graph CLI scope limitation is separate and is not a prerequisite for
using the signed-in Standard connector. Connected metadata alone does not prove
selected-plan access or task operations.

COR-12 next steps: reuse/select a suitable Basic plan and bucket; qualify connector
reads and bounded task writes; implement explicit selected linked actions; verify
reciprocal links, one-task replay and task-created/link-save-failed recovery.
Qualify assignment/notification effects without sending unapproved email. Task
completion must not automatically close correspondence. No Premium/Copilot route.
Natural arrival/production commissioning and public-release qualification remain
separate; passed capture/recovery tests are not reopened by this sign-in.


## Qualified selected Planner actions — 26 October 2026

Use `scripts/correspondence_linked_action.py` with private exact bindings. Source
compiles a Stopped manual Button flow; deployment separately enables LinkEnabled
and starts only the owned definition. Use the existing Standard Planner and
SharePoint connections. Toolkit Graph Tasks403 is a scope-specific route gap;
it does not invalidate the signed-in Planner connector. Never cycle clients,
request new consent or reuse another person's identity to bypass it.

The native Planner interface supplies Basic-plan creation when the Standard
connector has no create-plan operation. Reuse a suitable plan where possible;
otherwise prefer a private personal Basic plan without new membership/invites.
Qualify ListMyPlans_V2, ListBuckets_V3 and actual bounded task operations separately.
A personal Basic plan can return container type unknownFutureValue and a user
container; use the retained actual binding rather than assuming it is Premium.
GroupId is a connector dropdown-resolution parameter, not proof of a group plan.

FlowAgent invoke_operation is a dynamic-value resolver, not a general-purpose
connector executor. Its operation restriction is not a tenant403. Use the owned
flow runtime for real task operations. GetTaskDetails connector references are
an array of resourceLink entries, unlike the raw Graph reference dictionary.
Verify the native source attachment and saved reciprocal task URL independently.
SharePoint field creation can derive encoded internal names from display names;
read them back and bind exactly instead of deleting/recreating or guessing.

For auth expiry use the retained VS Code Toolkit client/account/tenant/audience
with its qualified form_post adapter; private workload recipes and pins remain
under the ignored workspace. Direct extension executable invocation is supported;
VS Code window control is unnecessary. Do not copy credentials or reset shared
profiles. Check exact affected native targets after renewal.

The private `correspondence-planner-actions-20261026` pipeline records one exact
request and prospective journal per write, with no transport retry. Consumed
execute scripts are evidence, not reusable commands: use new reviewed manifests
and filenames. Reconcile uncertain submissions before any new request. Per-flow
repair alerts require the supported native menu; a generic flow PATCH200 can
ignore flowFailureAlertSubscribed. Read the actual preference back; account-wide
weekly digests remain a separate provider setting.


Correspondence Planner runtime qualification uses the retained guarded M365 CLI SDK
for exact management/readback and existing Standard connector operations for task
runtime. Keep prospective one-attempt write manifests, exact saved restoration and
private fixture bindings. Loop repetitions qualify per-record effects; flat action
summaries do not. After interrupted observation, reconcile the same run by bounded
GET-only reads. Never replay an invocation or log raw transport/auth exceptions.


For correspondence access, distinguish direct SharePoint User.Groups from the
Microsoft365 group claims used by a log's Owners/Members grants. A direct other-user
effective-permission403 can coexist with readable group-principal mapping and a
qualified exact directory membership read. Prove the complete target grant-to-group-
to-principal chain; do not infer absent access or request wider consent. Use JSON
Accept for Graph; SharePoint's odata=nometadata media parameter is incompatible with
Graph here. Preserve rejected reads and use fresh evidence names after correction.
Native Planner Share may provide the authorised sharing route when CLI group-write
scope is absent; verify exact private member/owner audience and stable plan after save.


### H2 native mapping and same-version drift

Use `scripts/forum_native_mapping.py:map_package` for maker preparation from
explicit native property reads and qualified source-kind/byte observations. It
performs no authentication, reads or saves. Required input is the selected
library/type/reference binding, current profile and occurrence rows with expanded
File metadata and explicit hidden lineage fields, exact selected source rows and
byte hashes. Include the maintained template and evidence lookups; do not fill
missing selections with guessed defaults. The output has no native/send/activation
authority. Keep local source preparation separate from a future native bridge.

A source's `UIVersionLabel` alone is insufficient freshness proof. The qualified
read sequence is exact metadata, binary byte/hash read, then exact metadata again
including File ETag and Length. The observed same-version native drift invalidated
the first pin; a newly qualified stable pin was recorded separately. Preserve the
failed receipt and original expected values. Do not rewrite old evidence, silently
normalise lengths/ETags or claim historical restore from an empty versions result.
The bounded folder query succeeded after one filtered list query returned HTTP500;
this did not require another client, broader rights or a browser.
