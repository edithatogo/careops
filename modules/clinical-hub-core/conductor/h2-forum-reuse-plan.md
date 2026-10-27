# H2 — Forum reuse and configuration plan

Prepared28October2026. **Plan only; implementation not selected.** H1 discovery
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

All future implementation tasks below remain unchecked. This planning work made
no native call, change, flow invocation, email or publication. Native access stays
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

Prefer at most one small pure validator/resolver, provisionally
`scripts/forum_configuration.py`, only if the existing functions do not already
supply that boundary. Its paired synthetic cases would be
`tests/test_forum_configuration.py` and `tests/fixtures/forum_profiles/`.
These are proposed paths; none is created or implemented by this plan.
Do not alter existing sealed input schemas until compatibility is demonstrated.

Resolve the immutable profile/occurrence selection into existing adapter inputs.
Keep current environment parameters as technical defaults, not a multi-forum state
store. Keep the existing record/library as the source of truth; a versioned
maker-prepared reference file may be a derived selection snapshot, not another
live register. Determine exact storage mapping in H2.1 before any schema proposal.

## Task-level sequence

Owner for source/native preparation is the existing Clinical Hub executor. Native
object owners retain their objects. No work is assigned to another person here.

- [ ] **H2.1 — Pin reuse and storage mapping before construction.**
  Inspect the named source hashes, canonical catalogue and retained native proof.
  Classify every repeated value as shared logic, forum configuration, occurrence
  state, environment binding or credential. Record exact future file/function and
  native-object scope, schema/internal-name/type mapping, approved source/template
  references, supported no-code controls, and each unchanged component. Inspect
  exact native targets read-only only where retained evidence is insufficient.
  Exit: one reviewed reuse/diff map; no new store or extraction without demonstrated need.
- [ ] **H2.2a — Specify and test identity/version/authority boundaries.**
  Use two explicitly fictional profiles with different controls/agendas and a
  clearly fictional authority source. Cover missing/unknown/duplicate identity,
  ambiguous effective intervals, stale profile/source, same-name different forum,
  unqualified governance and invalid capability escalation. Assert that claims in
  ordinary inputs cannot grant native authority. No real profile values in fixtures.
- [ ] **H2.2b — Implement only the validated pure profile/occurrence resolver.**
  Reuse existing configuration infrastructure; add the proposed small module only
  if H2.1 demonstrates the gap. Return existing adapter input shapes and explicit
  blockers. Keep native reads/writes/auth out of the pure resolver. Preserve legacy
  callers and F12 text/shape limits. Exit: two synthetic profile snapshots resolve
  independently; unknown authority can produce review-only preparation, never issue.
- [ ] **H2.3a — Add bounded compatibility adapters.**
  Supply maintained preparation controls and selected-source references through
  existing entry points. Touch F06/F07/F12 only where the reuse map requires it;
  preserve native identity, references, existing graph guards and fallback branch.
  Tests precede each changed behaviour and prove legacy input/output equivalence.
  Do not generalise every generator or force one agenda onto every forum.
- [ ] **H2.3b — Design and qualify ordinary operator configuration.**
  Use existing List/library forms, choices/lookups or native manual inputs for
  forum/occurrence, supported role/source/template choices and effective dates.
  Makers own technical IDs, schema mapping and generated selection artefacts.
  Ordinary configurators must not edit JSON/YAML, PowerFx/M, GUIDs or flow source.
  Inventory actual controls first: Title/description-only metadata is not proof
  of a profile editor. Prefer reusing existing fields/forms; propose only required
  additive fields under separately selected schema authority, never a new app/list
  by default. If the surface cannot represent the contract, record that precise
  gap and retain manual preparation; do not declare no-code configuration passed.
- [ ] **H2.3c — Prove isolation, concurrency and recovery.**
  Test overlapping runs for different forums, two occurrences of one forum,
  future-effective role changes, wrong destination/audience, duplicate/replayed
  operation, changed input under one key, source drift and denied access.
  Preserve cancellation/exception/original-start semantics. Reconcile unknown save
  outcomes by exact readback; never blind retry. Verify a correction preserves
  prior source/output versions and another forum's state.
- [ ] **H2.4a — Rehearse existing behaviour and manual fallback.**
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

## Handoff

The next candidate increment is H2.1 followed by H2.2a/b as a bounded source-only
implementation when selected. This plan is reviewable without another intake
question, but it does not itself select implementation or native execution.
Keep H1-G01–03 open in the existing private comparison. Keep H3/H4 pilots and all
deferred correspondence follow-ups in their existing later lanes.
