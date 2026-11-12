# Executable source migration queue

Baseline reviewed 8 November 2026. This is the implementation queue for reusable
source consolidation, excluding `careops-sim`. It does not authorise a tenant
cutover or transfer private operational data/history into the source repository.
Use existing module tracks; the coordinating track links them instead of creating
duplicate delivery records.

## Destination and sequence

| Order / task | Inputs | Destination and disposition | Completion test |
| --- | --- | --- | --- |
| M0 Reconcile current source | Root/module docs, profiles, Conductor and PR queue | CareOps maintained source; standard profile and logical hierarchy | Source locations agree; premium work remains selectable; unrelated module absence is tested |
| M1 Improvement | PR 243 | `modules/careops-improvement`, after review and conflict resolution | Existing tests plus standard-profile contract; native Lists separately qualified |
| M2 RIMS | `careops-rims` **and** `research-publications` | Ordinary source at `modules/careops-rims`; retire the gitlink only in the admitted import | Both inputs' unique functionality accounted for, standalone tests and source gates pass |
| M3 Workload/costing | Private `hwcc`, maintained Costing | Reuse reviewed rules, requirements and portable calculation fixtures in Costing | Feature/parity matrix maps every retained rule to a test or explicit deferred item |
| M4 Legacy migration | `nsw-health-mscg-powerplatform` (default branch `master`) | Optional `modules/careops-legacy-migration`, subject to source admission | Portable mapping/cutover helpers work without connecting to a legacy system |
| M5 MCHS interface | `mchs` (default branch `master`) Power Platform tree/contracts | Versioned CareOps adapter/resources; MCHS retains calculation/runtime authority | Standard file route passes; optional service/custom-connector route independently qualified |
| M6 Retained archives | Archived predecessors and private recovery stores | Read-only recovery/provenance references, no blanket re-import | Every unique reusable item has keep/import/defer/discard reason; no lost private recovery source |

Work can proceed on independent rows, but archive a predecessor only after its
replacement's required source checks and recovery references are recorded. One
module's optional adapter must not hold another module's release.

## Common procedure for each row

The implementation owner executes this sequence in an authenticated private
workspace. One migration ledger holds the outputs; link it from the module track.

1. **Pin inputs.** Read repository visibility, default branch, archived state,
   current SHA, licence/NOTICE, AGENTS and open PRs. Record repository identity as
   well as name, because renamed slugs can redirect. Freeze the source selection
   for this candidate; later upstream changes become a separate delta.
2. **Create an isolated branch.** Start from current CareOps main, keep the source
   checkouts outside the worktree's tracked source, and initialise only the selected
   optional dependency. For example:

   ```sh
   git fetch origin main
   git worktree add -b integrate/rims-source ../careops-rims-integration origin/main
   git clone --filter=blob:none https://github.com/edithatogo/careops-rims.git .local/rims-source
   git clone --filter=blob:none https://github.com/edithatogo/research-publications.git .local/publications-source
   git -C .local/rims-source rev-parse HEAD
   git -C .local/publications-source rev-parse HEAD
   ```

   These are source Git commands, not tenant CLI commands. Use the established
   credential manager; never embed tokens in URLs or source. Replace example
   working directories with the approved private workspace if required.
3. **Inventory and classify.** Compare path/content hashes and semantic behaviour.
   Classify each item as reusable source, fictional fixture, licence/provenance,
   private binding, operational material, generated output or historical evidence.
   Build an explicit reviewed import allowlist. Inspect document/archive contents
   and metadata; filenames and `.gitignore` do not establish confidentiality.
4. **Resolve overlap before import.** For duplicate implementations choose one
   maintained owner. Preserve unique behaviour with tests and compatibility adapters.
   Use a three-way comparison for divergent files; do not overwrite current main
   with an older PR or predecessor's whole file. Keep runtime and tool versions
   aligned to the selected qualified profile.
5. **Import reviewed ordinary files.** Preserve attribution and independent licence
   terms. Record source repository, exact commit, path mapping, exclusions and file
   hashes in the module's provenance. Do not merge private Git history. Remove a
   gitlink and its `.gitmodules` entry only in the same candidate that replaces it.
6. **Reconcile the suite atomically.** Update `portfolio/repos.json`, delivery/ALM
   catalogues where applicable, `PUBLIC_SOURCE_FILES.json`, capability selection,
   README/module entry points, migration/provenance and the existing Conductor track.
   Replace predecessor issue/release links with CareOps locations while preserving
   historical receipts. Do not mark live commissioning complete.
7. **Qualify the exact candidate.** Run the source project's maintained tests using
   the exact pinned runtime/locks, then standalone/missing-provider contracts and
   parent source/privacy/security checks. Test the selected standard path with every
   premium adapter absent. Record command, selected source and actual result once.
   At integration/release, run the required full applicable gates, including protected
   current-head checks. A partial checkout or billing refusal is not a passed gate.
8. **Merge, verify, then retire.** Use normal protected merge. Read back the resulting
   main tree and provenance, perform the bounded post-merge source checks, and retain
   the private recovery source. Only then mark the predecessor read-only/archived
   and add a maintenance pointer. Native systems and their owners remain unchanged.

Rollback before merge is branch abandonment. After merge, use a reviewed revert
of the source/provenance/registry change, retaining the recorded prior pin and
private recovery checkout. Do not undo native records as a source rollback.

## M2: RIMS and research-publications

Existing execution track:
`conductor/tracks/suite_rims_direct_source_20261029/`.
Observed candidates were RIMS `8fdc68f09a2bdbb9dc1ab0bc39743e810fef6714`
and research-publications `2cbde867abf2364741996e6cb5edde63c426ca1d`.
Re-read the heads before selecting a new candidate. The old
`chhhs-research-publications` slug redirects; do not count it as a third source.

- [ ] Produce a three-column inventory: identical, divergent and unique to each
  source. The reviewed comparison had 629 shared paths (381 identical, 248 changed),
  plus 140 RIMS-only and 973 research-publications-only paths. These are source
  counts, not 973 independent features or approval for publication.
- [ ] Map publication ingestion, person/organisation attribution, duplicate handling,
  reporting and Power Platform assets to the maintained implementation.
- [ ] Separate confidential publications/author exports, identities and tenant
  bindings from reusable source; replace source fixtures only with fictional data.
- [ ] Preserve source-qualified publication/project IDs. Define optional
  `ImprovementInitiativeRef` and `DatasetRef`; test absent and stale providers.
- [ ] Align active Python instructions/locks to the suite's qualified runtime;
  replace stale 3.11+ wording after actual compatibility qualification.
- [ ] Import/reconcile, qualify and merge before archiving either active predecessor.

## M3: HWCC into Costing

- [ ] Capture HWCC's current private revision and its workbook/rule inventory.
- [ ] Build a parity table: rule/assumption -> Costing kernel or Python capacity
  model -> fictional test -> remaining native workbook/app dependency.
- [ ] Resolve the conflict between source feature-complete claims and unchecked
  residual deployment tasks. Carry both facts forward; neither proves the other.
- [ ] Import reviewed portable rules and fixtures in small slices. Keep private
  workbooks and organisational assumptions in their approved storage/profile.
- [ ] Qualify numerical parity, units, rounding, boundary inputs and reproducibility;
  do not require a new UI or premium service to reuse a calculation.

## M4: Legacy Migration

- [ ] Inventory `master`, existing cutover plans, external tool dependencies and
  original MIT/third-party notices. Do not relicense retained third-party source.
- [ ] Split generic mapping/validation/reconciliation helpers from private system
  exports, access bindings and operating records.
- [ ] Admit an optional portable toolkit only. A source import does not authorise
  CGov replacement, production writes or closure of N11.
- [ ] Keep original source/recovery references; avoid a cosmetic repository rename
  while admission and ownership are unresolved.

## M5: MCHS Power Platform integration

The upstream boundary explicitly keeps formulas, pricing-year logic and calculation
semantics outside Power Platform. Reuse `contracts/power-platform/`,
`power-platform/` and `conductor/power-platform-boundary.md` selectively.

- [ ] Pin the binding contract, capability matrix, fixture IDs and API schema.
- [ ] Define a standard input/result snapshot adapter carrying contract version,
  calculator ID, pricing year, input/output revision and reproducibility reference.
- [ ] Reuse forms, resource descriptors, reporting shapes and ALM helpers after
  source/privacy review; retain the upstream calculator and service deployment.
- [ ] Keep the existing custom connector/API integration as a **premium optional
  profile**. Do not imply that a generic HTTP or custom connector is a standard
  Power Automate route. The standard route uses approved export/import or existing
  qualified native connectors, with explicit latency/manual limitations.
- [ ] Test one fictional workload/costing exchange, unsupported year/capability,
  stale contract, unavailable service and fallback. Do not copy calculation logic
  into Power Fx or create a second engine.

## M6: archives and source reconciliation

Do not reopen archived Approve, Process, Incidents, Finance, Costing, Decisions,
Clinical Hub or PPG predecessors as active development locations. Check their
provenance and retained private work for unique reusable source only. The integrated
sources remain maintained in CareOps. Review `-public` predecessors as historical
snapshots, not automatically newer or publicly distributable code.

Keep a retirement receipt with source identity/revision, admitted counterpart,
excluded private material location class, unresolved reusable items and recovery
owner. A short manifest is sufficient; duplicate approval packs are unnecessary.

## Existing PR queue

Review each against the current main revision and current head before merging.
Keep source correction, local verification and protected merge status separate.

| PR | Required disposition |
| --- | --- |
| 303 | Inventory repair committed at `c081189b81e52bf7142287d3a1f04967a6679adf`; normal merge refused because all six required checks were failing. Verify current-head checks before merge |
| 302 | Draft PPG function-clause projection; review implementation/tests and exact privacy-control delta, then remove draft only when source-ready |
| 300, 277 | Qualify pinned action/tool updates at current head; retain existing checks and immutable pins |
| 299 | Reconcile dependency declarations **and** lockfiles; test affected front-end/process consumers |
| 244 | Three-way reconcile PPG retained-assessment tooling with later main changes; preserve private evidence boundaries |
| 243 | Admit Improvement as optional; resolve shared registry/docs conflicts without overwriting later integrations |
| 242 | Carry forward XML/subprocess hardening not already present; validate retained functionality and malicious fixtures |
| 241 | Preserve onboarding plan and register it under optional Workforce work; reconcile Conductor/inventory |
| 240 | Compare with the newer privacy implementation already on main; retain unique fixes, avoid restoring superseded controls |
| 231 | Do not merge version declarations without a matching exact hash-lock qualification |
| 217 | Excluded simulation update; leave untouched |

Issue 301 tracks the current hosted Actions refusal. PR 298's earlier one-time
local-evidence exception does not grant a standing protection bypass. Do not
weaken required checks or post fabricated success statuses to merge this queue.
