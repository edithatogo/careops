# H2 — Forum reuse and configuration plan

Prepared28October2026. **H2.1, H2.2a/b and H2.3a source-complete; H2.3b inventory/design complete with no-code qualification gaps. H2.3c source rehearsal complete with native recovery gaps. Native changes remain unselected.** H1 discovery
is closed under the user's explicit instruction, with its approval gaps retained.
Closure accepts the evidence-grounded comparison and stated limits; it does not
adopt a ToR, appoint a role, approve a reporting route or commission another forum.
Exact profiles, source papers, native bindings and evidence stay private.

## Outcome and smallest useful increment

Reuse the existing preparation, selected-source, review and calendar-comparison
capabilities for separately identified forums and occurrences. First deliver a
small validated profile/occurrence boundary and compatibility adapters with two
fictional profiles. Preserve existing entry points, identifiers, source fidelity,
manual review, human edits and one authoritative action register.

Start with identity, revision selection and isolation; then adapt only demonstrated
repeated bindings. Leave an already suitable component unchanged. Do not build a
common runtime/framework, new app, Team, register, scheduler or approval workflow.
No cross-forum referrals, correspondence changes or task synchronisation in H2.

The H2.1/H2.2a/b/H2.3a source tasks are complete; later implementation tasks remain unchecked or partial. That source increment made
no native call, change, flow invocation, email or publication. H2.3b subsequently used four read-only GETs as documented below. Native access stays
read-only until a later instruction explicitly selects the relevant native work.

## Retained H1 approval gaps

| Reference | Outstanding source/authority question | Effect on H2 |
| --- | --- | --- |
| H1-G01 | Clinical Directors adopted operating arrangements, standing role/delegation, minute approval and official records route remain unqualified; retrieved governance proposals explicitly remain drafts. | Preserve qualified existing behaviour. Model unknowns explicitly; no promotion of draft governance into a live rule. |
| H1-G02 | Medication Safety authoritative edition/roster/quorum and endorsed reporting transition remain unqualified. Same-edition content conflicts and a later review candidate are retained, with blank approval fields. | Version/effective-date and conflict cases are required. Do not pick the newest filename/upload or automatically change reporting destinations. |
| H1-G03 | CMO/EDMS Performance applicable organisational authority, role/endorsement and official records route remain unqualified. Existing divisional review and pack are evidenced. | Reuse an applicable framework/decision if qualified; do not assume a separate governing committee or require a new ToR. Preserve reporting-period versus data-extract-date distinctions. |

These gaps remain open outside the closed discovery task. They do not prevent
planning or separately selected synthetic/source work. Affected live governance
bindings require suitable current evidence or a later explicit authorised decision.
Neither a local validator nor a supplied `approved` flag establishes authority.
Other people's workflows/access and deferred correspondence follow-ups are outside
scope. H3/H4 real-forum pilots remain separately selected work.

## Source reuse inventory — observed during planning

Paths below are relative to this module. They are actual inspected source, not
assertions that a complete native graph or current runtime is present in Git.
Private planning evidence pins their source hashes; refresh only changed inputs.

| Existing component | Classification and reuse | Narrow future change / boundary |
| --- | --- | --- |
| `scripts/preparation_cycle.py` | Shared pure carry-forward logic already accepts maintained `control_keys`; preserves unresolved preparation and resets reviewed controls. | Supply profile-selected controls. Keep its no-assignment/no-clinical-action boundary; no rewrite if existing injection suffices. |
| `scripts/f06_selected_agenda.py` | Existing selected-source adapter: occurrence selection file, native source/version pins, register identities and retained legacy route. | Resolve profile/occurrence into its existing inputs; preserve exact canonical graph guards and legacy branch. Maker-owned selection files do not become operator JSON editing. |
| `scripts/f06_word_template.py`, `scripts/f06_agenda_document.ts`, `scripts/build_word_documents.py` | Maintained template/source-authoring and selected native-renderer helpers. | Keep template-specific agenda differences. Local helpers are not a replacement operational runtime or proof that a native renderer is permitted. |
| `scripts/f07_operator_inputs.py` | Exact observed paper/version choice and source-binding adapter. | Reuse known choice pattern for selected references; no broad path, unreviewed paper or inferred meeting association. |
| `scripts/f12_configuration.py` | Existing strict baseline/selection validator, 21 comparison fields, UTC requirements and 2000 UTF-16-unit text limit. | Keep the legacy schema/limit unchanged. A new profile is not packed into the existing small baseline variable. H1 inventory metadata is not a fully qualified F12 baseline. |
| `scripts/f12_environment_bindings.py`, `scripts/f12_operator_inputs.py` | Technical environment bindings versus manual operator selection are already separate. | Retain defaults/bindings as deployment configuration. Do not overwrite shared environment values to switch concurrent forums/occurrences. |
| `scripts/f12_portable_definition.py`, `scripts/f12_comparator_binding.py`, `scripts/meeting_calendar_compare.py` | Guarded source/comparator adapters and pure drift semantics. | Preserve stable identity, complete-window/paging checks, UTC/local-time distinction, original occurrence, cancellation and manual reconciliation. No calendar edits. |
| `scripts/meeting_commit_preview.py`, `scripts/optional_pack_provider.py` | Pure preview, identity/replay/recovery and source-history patterns. | Reuse relevant checks; previews remain proposals. Do not introduce a parallel persistence/action register or infer actual authority from supplied metadata. |
| `scripts/flow_definition.py`, `.careops/flows.json` | Existing comparison and canonical native-flow/source-artifact catalogue. | Preserve canonical flow identities and exact reference shapes. Update only affected source pins after later source changes; no copied tenant graphs in public Git. |
| [Library columns and maintained Word route](library-column-word-route.md), [document cases](document-cases.md) | Working Standard SharePoint/manual Word fallback, selected source/template/output revisions and edit preservation. | Default to this route while optional generation remains unqualified. Metadata updates do not refresh visible Word narrative. |

A retained F08 attempt documents a prohibited Office Script renderer operation and
unproved output/recovery. A plan mentioning conditional forms or two fictional
meetings is not evidence that those native cases passed. Reuse only actually
passed evidence at its scope. Do not retry the prohibited operation, switch action
versions/environments to evade it, add Premium Word actions or introduce Copilot.
Evaluate the preferred SharePoint structured-document route through existing
capability evidence first; where the needed behaviour is unqualified/unavailable,
retain the maintained Word/manual route without purchasing or changing policy.

## Proposed minimal contract — design, not an implemented schema

| Layer | Minimum information | Authority and isolation rule |
| --- | --- | --- |
| Versioned forum profile | `schema_version`, stable `forum_ref`, `profile_revision`, effective interval, purpose, control keys/agenda sections, enabled capabilities, role/approval/records source references and qualification state. | Display names are not identities. Unknown/draft/conflicting governance is explicit. Effective intervals cannot overlap ambiguously; no silently selected latest revision. |
| Occurrence snapshot | `forum_ref`, `occurrence_ref`, selected profile revision, existing calendar/event/series/original-occurrence references, current/original start and timezone, organiser, exception/cancellation state and source snapshot time. | Snapshot is immutable for an operation. Organiser is not chair. Preserve moved occurrences and cancelled state; missing rule/metadata remains unverified. |
| Selected sources/output provenance | Original file/record IDs, native version/ETag/hash where required, document edition/approval evidence, template version, included/excluded records, output purpose/revision and prior-output reference. | Native file version, document edition, approval and reporting/extract periods are separate. Recheck drift before using a selection; never overwrite human corrections or issued history. |
| Environment binding | Existing site/library/list IDs, canonical flow alias/native mapping, technical parameter names, actual connection-reference identities and permitted destinations. | Private maker-owned deployment data. Same-client authentication and actual target permissions remain separate from connector runtime rights. No tokens/credentials in a profile or source. |
| Per-operation identity | Stable forum + occurrence + output purpose/revision and selected input revisions, with existing recovery history. | Identical request can reuse a verified result; changed input under the same identity is conflict/reconciliation. No shared mutable last-forum/current-occurrence variable. |

The selected source increment adds the small pure resolver
[`scripts/forum_configuration.py`](../scripts/forum_configuration.py),
[`tests/test_forum_configuration.py`](../tests/test_forum_configuration.py) and
[two explicitly fictional profiles](../tests/fixtures/forum_profiles/two_forums.json).
Existing functions accept controls/selectors but did not select a forum/revision
or reject an overlapping profile catalogue. No legacy module/schema is changed.
Do not alter existing sealed input schemas until compatibility is demonstrated.

Resolve the immutable profile/occurrence selection into existing adapter inputs.
Keep current environment parameters as technical defaults, not a multi-forum state
store. Keep the existing record/library as the source of truth; a versioned
maker-prepared reference file may be a derived selection snapshot, not another
live register. Determine exact storage mapping in H2.1 before any schema proposal.

## H2.1 source reuse and storage map: implemented scope

This source-only map completes H2.1 at the selected scope. Exact native mappings
remain private retained bindings, not a new or freshly qualified native store.
The source catalogue/legacy files are pinned in private evidence and unchanged.
Existing native schema/control limits stay explicit in H2.3b; completion of this
map does not qualify a native profile editor or current permissions.

| Value / class | Existing location or consumer | Selected source treatment |
| --- | --- | --- |
| Shared preparation logic | `preparation_cycle.validate/next_cycle`, caller's `control_keys` | Return a tuple of selected control keys. Retain the existing cycle dict schema; do not generate a new register or clinical actions. |
| Shared calendar comparison | F12 strict configuration/metadata comparison and manual operator input builder | Return only the existing five-key selection object: `window_start`, `window_end`, `subject`, `organizer`, `agenda_name`. Full 21-field baseline remains independently required; current H1 inventory is not promoted into it. |
| Forum configuration | Explicit caller-supplied versioned profiles; proposed future native mapping through existing library/form infrastructure | Exact forum/revision and non-overlapping effective interval, purpose, control/agenda keys, evidence/role references, permitted review capabilities and opaque binding/template/destination/register refs. No native persistence added. |
| Occurrence state | Explicit caller-supplied selected occurrence and source pins | Preserve occurrence/snapshot revision, current/original start, event/series identity, type/cancellation, organiser, source name/revision/hash. Current scheduled start selects the effective interval; no latest-by-title fallback. |
| Selected source lineage | F06's existing versioned library selection-file pattern and immutable source metadata pins | Canonical immutable JSON snapshot plus SHA-256, not a second live register. No file written by resolver and no F06 selection file/schema changed. H2.3a must map this snapshot to the native adapter. |
| Deployment binding | Existing F06 source-site binding, F12 baseline/selection environment parameters, full native connection references and canonical flow aliases | Resolver returns opaque references only. Actual site/list/library/flow IDs stay in private deployment bindings. Global F12 values are not switched or overwritten for each forum/run; 2000-unit legacy constraints unchanged. |
| Credentials/access | Owning CLI/connector authentication and actual object permissions | No credential field, authentication, provider, token, persistence or access check in resolver. These remain outside the profile and independently qualified at the native boundary. |
| Existing output/records | Maintained Word/manual route, canonical register and provenance/history | No template generation, body refresh, register write, issue, send, new schema/store, or change to issued history. |

### Executable source contract

`resolve(profiles, selection, observed_sources=...)` accepts only schema version1
(exact integer). References are bounded opaque IDs and display names are never
identities. See the fixture for the complete explicit input shapes; additional
fields are rejected rather than silently ignored.

- Profiles select by `forum_ref` + `profile_revision`; effective intervals are
  start-inclusive/end-exclusive, with explicit zoned times. The occurrence's
  current scheduled start must lie within its explicitly selected revision.
- `roles` contains separate chair/delegate/secretariat references and evidence
  states. Governance states are `unverified`, `draft`, `conflicting`, `recorded`.
  `recorded` requires a source reference but is still an unauthenticated input
  assertion. An `approved` flag/state is not a supported grant of authority.
- Supported capabilities are `prepare` and `compare_calendar`; requested values
  must be enabled in the selected profile. Issue/send/native-write capabilities
  are unsupported. Cancellation blocks preparation; exceptions retain original
  start and series identity. No type/lineage is reconstructed from meeting title.
- Selected source pins contain `source_ref`, `kind`, `name`, `revision`, `sha256`.
  Source IDs are unique; claimed complete observations must match the exact pins.
  Drift, incomplete reads and ambiguous agenda selection return blockers.
  Observations are supplied claims, not proof of actual native reading/access.
- Successful result is always `review_only`, `preview_only=true`,
  `native_authority=false`, `write_proposed=false`. It supplies control keys,
  agenda sections, opaque references and the unchanged F12 selector shape when
  requested. `f12_selection_json` is the exact compact serialisation and is bounded
  using the unchanged F12 UTF-16 limit; full baseline validation remains separate.
  Invalid Unicode is rejected. Blocked results expose no adapter inputs or snapshot.
- `snapshot_json` is immutable canonical JSON of the selected profile/occurrence;
  `snapshot_sha256` binds those exact values. Derived argument copies are mutable
  copies, not authority: future adapters must verify the selected snapshot/digest
  before an operation. No replay ledger, persistent lock or operation execution
  is implemented. Same inputs are deterministic; changed input changes the digest.

The original H2.1/H2.2 increment introduced no F06/F07/F12 caller integration, UI configuration,
actual concurrent native run, target permission, source-access or governance
qualification. Those remain H2.3/4 work. Tests exercise independent calls and
threaded pure resolution, not Power Automate runtime/concurrency acceptance.

## H2.3a source compatibility adapters: implemented

[`scripts/forum_compatibility.py`](../scripts/forum_compatibility.py) wraps the
existing pure entry points. The original resolver, F06/F07/F12 builders, preparation
functions, sealed input schemas and canonical source/flow catalogue are unchanged.
No native definition, selection file, environment value or record has been saved.

Every entry point requires `snapshot_json`, an external
`expected_snapshot_sha256` pin, and explicit `observed_sources`. It verifies the
raw digest, rejects duplicate/noncanonical JSON, reruns the resolver and requires
the selected capability. Mutable derived result flags are not trusted. The external
pin and observations are still caller assertions, not authenticated native evidence.
Successful responses are always `review_only`, `preview_only=true`,
`native_authority=false`, `write_proposed=false`; refusals have no payload.

| Adapter | Existing consumer / payload | Added consistency boundary |
| --- | --- | --- |
| `preparation_inputs(..., data=...)` | `preparation_cycle.validate`; unchanged preparation dictionary and maintained control keys | Current occurrence, register reference and selected agenda/pack reference must match the pinned context. Human notes/control states are retained; missing or cross-forum controls refuse. Ordinary legacy callers remain available directly. |
| `next_preparation_inputs(..., data=..., cycle=..., previous_ref=...)` | `preparation_cycle.next_cycle`; exact legacy carry-forward output | Validate the current context first. Preserve reset of review controls and next-meeting/priority `To confirm` values; do not infer the next occurrence's profile or authority. A subsequent occurrence needs its own selection. |
| `paper_candidate(..., baseline=..., expected_baseline_sha256=..., binding=...)` | `f07_operator_inputs.build_operator_inputs`; the same source candidate as a direct legacy call | Pin the complete supplied Stopped baseline. Check forum/occurrence/deployment reference and selected document name/revision/hash, exact nonempty ETag, supported HTTPS SharePoint site and nontraversing file path. Preserve complete outer flow identity, non-definition properties, state and full references. F07 paper readiness/meeting association remains unconfirmed; no publication or save. |
| `calendar_inputs(..., baseline_text=..., binding=...)` | `f12_configuration.validate_configuration`; exact `baseline_text` and canonical `selection_text` keyword arguments, plus the legacy shape-validation report | Require the full existing 21-field baseline and unchanged UTF-16 limit. Explicit alias-to-native event/series/agenda IDs must agree with the baseline; type, cancellation, current interval and original start must agree with the selection. Do not fabricate missing metadata or unsupported single-instance lineage. Preserve raw baseline text and timezone-aware comparison. |

Source bindings are maker-supplied metadata, kept private for actual deployments.
Common binding fields are `forum_ref`, `occurrence_ref`, `binding_ref`.
Paper bindings add `source_ref`, `site`, `path`, `name`, `version`, `etag`, `sha256`;
`version` is the selected source's pinned revision, not an inferred document edition.
Calendar bindings add `event_ref`, `event_id`, `series_ref`, `series_id`,
`agenda_ref`, `agenda_id`, `agenda_revision`, `agenda_sha256`. Native IDs may use
their actual provider syntax; logical aliases stay separate. All supplied fields
are checked, with extra/unknown fields refused. These checks prove consistency,
not access, an authenticated mapping, native freshness or approval.

F06's existing selected-source/legacy branches and donor guards require no change
for this slice. This is not a new F06 selection-file format or multi-forum native
F06 runtime qualification. F07 candidate construction is a pure source operation;
ordinary-user controls, saved state and rendering remain H2.3b/H2.4 work. Source
cross-context and digest refusals do not complete H2.3c replay/native concurrency,
recovery or output-history acceptance. H1-G01–03 remain open.

## Task-level sequence

Owner for source/native preparation is the existing Clinical Hub executor. Native
object owners retain their objects. No work is assigned to another person here.

- [x] **H2.1 — Pin reuse and storage mapping before construction.**
  Inspect the named source hashes, canonical catalogue and retained native proof.
  Classify every repeated value as shared logic, forum configuration, occurrence
  state, environment binding or credential. Record exact future file/function and
  native-object scope, schema/internal-name/type mapping, approved source/template
  references, supported no-code controls, and each unchanged component. Inspect
  exact native targets read-only only where retained evidence is insufficient.
  Exit: one reviewed reuse/diff map; no new store or extraction without demonstrated need.
- [x] **H2.2a — Specify and test identity/version/authority boundaries.**
  Use two explicitly fictional profiles with different controls/agendas and a
  clearly fictional authority source. Cover missing/unknown/duplicate identity,
  ambiguous effective intervals, stale profile/source, same-name different forum,
  unqualified governance and invalid capability escalation. Assert that claims in
  ordinary inputs cannot grant native authority. No real profile values in fixtures.
- [x] **H2.2b — Implement only the validated pure profile/occurrence resolver.**
  Reuse existing configuration infrastructure; add the proposed small module only
  if H2.1 demonstrates the gap. Return existing adapter input shapes and explicit
  blockers. Keep native reads/writes/auth out of the pure resolver. Preserve legacy
  callers and F12 text/shape limits. Exit: two synthetic profile snapshots resolve
  independently; unknown authority can produce review-only preparation, never issue.
- [x] **H2.3a — Add bounded compatibility adapters.**
  Supply maintained preparation controls and selected-source references through
  existing entry points. Touch F06/F07/F12 only where the reuse map requires it;
  preserve native identity, references, existing graph guards and fallback branch.
  Tests precede each changed behaviour and prove legacy input/output equivalence.
  Do not generalise every generator or force one agenda onto every forum.
- [~] **H2.3b — Design and qualify ordinary operator configuration.**
  Inventory/design completed28October2026; native no-code qualification remains
  unpassed. See the [observed controls, conditional design and H2-U01–05 gaps](h2-operator-configuration.md). Four guarded exact GETs; no native change/run.
  Use existing List/library forms, choices/lookups or native manual inputs for
  forum/occurrence, supported role/source/template choices and effective dates.
  Makers own technical IDs, schema mapping and generated selection artefacts.
  Ordinary configurators must not edit JSON/YAML, PowerFx/M, GUIDs or flow source.
  Inventory actual controls first: Title/description-only metadata is not proof
  of a profile editor. Prefer reusing existing fields/forms; propose only required
  additive fields under separately selected schema authority, never a new app/list
  by default. If the surface cannot represent the contract, record that precise
  gap and retain manual preparation; do not declare no-code configuration passed.
- [~] **H2.3c — Prove isolation, concurrency and recovery.**
  Source-only fictional rehearsal completed28October2026; see the
  [case matrix and H2-R01–04 limits](h2-source-recovery.md). Native save/readback,
  access/audience and actual runtime concurrency remain unqualified.
  Test overlapping runs for different forums, two occurrences of one forum,
  future-effective role changes, wrong destination/audience, duplicate/replayed
  operation, changed input under one key, source drift and denied access.
  Preserve cancellation/exception/original-start semantics. Reconcile unknown save
  outcomes by exact readback; never blind retry. Verify a correction preserves
  prior source/output versions and another forum's state.
- [~] **H2.4a — Rehearse existing behaviour and manual fallback.**
  Source-only baseline comparison and manual-fallback rehearsal selected28October2026.
  H1-G01–03, H2-U01–05 and H2-R01–04 remain open; no native execution.
  Run affected source tests under explicit repo-local Python3.15.1. Compare agenda,
  paper order/links, minutes, dissent/conditions, action IDs and review semantics
  against the accepted existing baseline. Use documented manual Word cases where
  automatic rendering is unavailable; source or upload success is not Word output
  proof. Complete existing module/integration/public-source gates at the coherent
  source milestone. Record source-only completion separately from native readiness.
- [ ] **H2.4b — Prepare any later native candidate and rollback.**
  Only after native preparation is explicitly selected: obtain exact current
  definition/references/state/owners and terminal runs; save only permitted,
  operation-qualified targets Stopped with no send/activation. Preserve full
  rollback preimage and independently read back the exact graph, references,
  schema/fields and state. Native fictional form/output/recovery execution needs
  its own selected scope; retained renderer denial is not bypassed. Current plan
  authorises none of these writes or runs.
- [ ] **H2.4c — Review the H2 release boundary.**
  Evidence must establish preserved existing behaviour, two synthetic profiles
  without cross-routing/shared-state leakage, usable qualified configuration
  controls, and tested recovery at the claimed source/native level. Demonstrate
  restoration of any selected native change without deleting issued records.
  List unresolved capability/approval gaps explicitly. No H3/H4 real cycle,
  business adoption, wider access, production cutover or notification approval is
  inferred from an H2 source check or fictional rehearsal.

## Tools, permissions and proof

| Work | Preferred tool / required permission | Current scope or later gate |
| --- | --- | --- |
| Source/fixture inspection and pure tests | `rg`, Git, explicit module-local Python3.15.1; ordinary local file access. | Permitted planning reads now. Future source implementation only when selected; no operational local generator. |
| SharePoint source/schema/config reads | Retained guarded M365 CLI SDK GET route; same pinned workload/account/tenant/resource and exact allowed target. File/list read permission is target-specific. | Reuse existing evidence first. Schema read is not ManageLists or audience-access proof. No new login/client/consent to bypass denial. |
| Canonical flow metadata/readback | Qualified Flow-management GET adapter; exact selected flow owner/read rights and saved native identity. | Only read-only qualification now. Do not touch live correspondence or consume a stopped probe merely for inventory. |
| Environment/solution metadata if needed | Existing VS Code extension PAC workload recipe and exact selected environment read. | Qualify that operation/account/row; management metadata is not authority to use Dataverse runtime actions or introduce Premium connectors. |
| Expired Microsoft workload session | `microsoft-365-auth` retained VS Code workload recipe, normal client-owned persistence and shared auth lock. | No bare CLI auto-login, cache/token transfer, client cycling or unqualified callback. Human credential/MFA/new consent remains human. |
| Future schema or flow save | Existing operation-qualified same-client API route; actual schema/flow write permission, prospective private journal, exact manifest and one transport attempt. | Not authorised by this plan. Stopped save is still a native write; no assumed admin privilege or broad reset. |
| Future native rehearsal | Existing Standard SharePoint/Outlook connections and explicitly selected finite fictional scope; operation-specific source/destination access. | No run now. Suppress/verify relevant per-flow and account digest effects before a no-email rehearsal; avoid deliberate failures until qualified. |
| Word/form visual acceptance | Native UI only where rendering/ordinary-user controls cannot be proved by CLI. | State exact UI need, use an existing session, then return to CLI readback. Do not install a provider or grant access to complete a check. |

No Premium connector, Copilot, AI Builder, new consent, purchase, service account,
Dataverse business-data migration, child-flow extraction or external notification
is planned. Child-flow factoring is deferred unless measured duplication and
unchanged identity/invoker/licensing behaviour justify a separately selected change.

## Focused verification and contingencies

Existing test slices include `test_preparation_cycle.py`,
`test_f06_selected_agenda.py`, `test_f06_selected_agenda_script.py`,
`test_f07_operator_inputs.py`, `test_f12_configuration.py`,
`test_f12_environment_bindings.py`, `test_f12_operator_inputs.py`,
`test_f12_portable_definition.py`, `test_f12_comparator_binding.py` and
`test_meeting_calendar_compare.py` under `tests/`. Select only affected files/nodes
during edits and reuse unchanged evidence; add the new resolver tests only when
that resolver is selected. Do not run a native mutation or email through a retry
plugin. Full integration/release gates remain required at their actual milestone.

If native read access fails, retain source-only planning and the exact scoped
condition. If a schema/control is unsupported, retain current manual preparation
and report the mapping gap. If governance conflicts, keep the existing behaviour
and disable the affected proposed capability; do not guess authority. If a source
changes, create a fresh snapshot and invalidate only dependent proposed output.
If a save is uncertain, read/reconcile it before deciding recovery. If one component
needs broad branching, narrow the contract before another forum is introduced.
No contingency changes existing invitations, access, live flows or issued records.

## H2.3a verification —28October2026

Fifty-eight fictional adapter cases passed, including whole-result legacy
equivalence, complete flow identity/reference/state preservation, exact F12 raw
baseline/21-field validation, missing metadata and cross-context/digest/source
refusals. The full offline module suite passed1153 tests; eight parent publication/
package checks, both privacy validators and the secret scan passed. Nineteen
pinned legacy/resolver files are unchanged. These source checks do not qualify
actual bindings, ordinary-user controls, native runtime/recovery or H1 approvals.

## Source verification —28October2026

Fifty new fictional resolver cases passed, including effective boundaries,
same-name forums, unsupported authority/capabilities, source drift, cancellation,
Unicode/UTF-16 limits and existing preparation/F12 compatibility. The full offline
module suite passed1095 tests; eight parent publication/package checks and both
public-source boundary validators passed. Eighteen pinned legacy source files are
unchanged. These are source checks, not native permissions, actual source freshness,
operator/UI acceptance, concurrent Power Automate operation or business approval.

## Handoff

H2.1, H2.2a/b and H2.3a are complete at source-only scope. H2.3b inventory/design
and H2.3c source rehearsal are complete at their selected scopes; native
qualification remains partial under H2-U01–05 and H2-R01–04. H2.4 remains pending
and unselected. Source results do not select later implementation, native
execution or a live forum.
Keep H1-G01–03 open in the existing private comparison. Keep H3/H4 pilots and all
deferred correspondence follow-ups in their existing later lanes.

## H2.3b inventory and design disposition:28October2026

The [operator configuration assessment](h2-operator-configuration.md) records the
current library field/form metadata and existing F07/F12 manual inputs. Four
exact-target guarded CLI GETs succeeded. Existing title/description metadata,
fixed paper choices and meeting-search fields cannot represent the whole H2
profile/occurrence contract. No native profile editor or intended-user rendering,
save or access is qualified. H2.3b remains partial under H2-U01–05; its inventory
and conditional minimal design are finished. Manual preparation is retained.

No native schema/flow/reference/state or shared setting changed; no run, email,
correspondence work or publication. H1-G01–03 remain OPEN; H2.3c/H2.4 remain
pending/unselected. A future exact schema/control diff and fictional save/UI
qualification require separately selected scope; no new app/list is proposed.

## H2.3c source rehearsal disposition:28October2026

[Source isolation/recovery rehearsal](h2-source-recovery.md) completed41 new
fictional cases and189 focused affected checks. A demonstrated result-aliasing
defect in the existing pure commit preview was fixed without changing its values,
operation keys, schema or disposition/authority checks. No persistence framework
or native bridge was added; existing resolver/adapters/catalogue are unchanged.

H2.3c remains partial for native qualification (H2-R01–04). Audience/access, atomic
reservation, actual save/readback and historical native restoration are unproved.
H1-G01–03 and H2-U01–05 remain OPEN; H2.4 pending/unselected. This source increment
made no native call, flow/configuration change/run, deferred correspondence check,
email or publication. Preserve the existing manual route and native owners.
