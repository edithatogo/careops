# RIMS exported-solution reconciliation and non-premium review — 10 November 2026

Status: source-side assessment and design; native deployment and approval remain unverified.
Owner: existing CareOps RIMS/source owner. This track extends existing RIMS migration, publication monthly monitoring, grants and study work; do not restart accepted work or introduce a second operational writer.
Baseline: user-provided unmanaged Power Platform ZIP `CHHHSRIMSPlatform_1_0_0_0 (6).zip`, SHA-256 `571aff12cf2bc0aba5065a66a6568b42b1ae0cf25e241026233a4775e6f0138f`. The 36 workflow JSON files are local input evidence, NOT an asserted deployment export or source of live tenant truth. Raw ZIP, tenant-specific strings and content must not be committed here.
Current parent main at assessment: `7de89d644b66123b47d75816dd9f5f9600e69f83`; `modules/careops-rims` remains an optional pinned submodule according to README and source registry. RIMS direct-source track `suite_rims_direct_source_20261029` is documented as pending. Both former child source repositories are archived. `research-publications` had subsequent November 2026 work; archival/source integration is not native deployment.
Evidence levels: ZIP static structure observed; repository docs inspected; no tenant readback, connection access, service runtime, reviewer UI, live published-report comparison or native flow execution performed.

## Reconciliation findings (static)
- ZIP contains 36 workflow JSON files (35 was a preliminary miscount); recurrence and manual/request trigger types exist. 33 definitions contain the text `/personal/`; distinguish resource URLs from credential/connection references before any remediation.
- Publication ingestion contains SharePoint-facing `ReviewStatus`, `ReviewNotes`, `CHHHSAffiliatedAuthors`, `AttributionEvidence` fields, but its mapped create payload sets `item/field_17` to literal `Included`. The same literal appears in PubMed and DoRA publication collection definitions. Inspect exact operation contexts to decide whether this means a default assertion, intermediate source projection, or final decision. Never interpret it as reviewer approval without provenance.
- No independently demonstrated end-to-end human review UI/workflow for both **publication relatedness** and **named-person employee status** in this package. Absence of proof in this ZIP is not proof of absence in the tenant or other repositories.
- The publication monthly repair is recorded as controlled/native repair with natural unattended scheduled success still pending (recorded next December 1 occurrence). Preserve that acceptance state. Other grants import and funding relationship tasks retain existing owners.
- None of this is authorisation to import the ZIP, activate flows, change schedules, send mail, publish reports, or modify tenant data.

## Required non-premium architecture
1. **Core**: SharePoint Lists + document libraries, Microsoft Lists browser UI, version history, standard SharePoint connectors, optional built-in list rules/notifications only where tenant eligibility is verified. Keep ordinary HTML/CSV and independently runnable source processors for offline/export fallback. Do not require Dataverse, Power BI premium/PPU, Fabric, premium HTTP/custom connectors, AI Builder, Copilot, Approvals premium, or paid third-party services for core ingestion, review, reporting or recovery. A connector's classification and licence must be qualified against actual target environment before use.
2. **Data ownership**: canonical publications register, person identity registry, organisation affiliations, source assertions, reviewer decisions, and report issue ledger linked by stable IDs. Reuse existing accepted Lists, do not create duplicates. Publication-relatedness and employment are distinct temporal assertions with different evidence and access controls.
3. **Human-in-loop**: New source discovery -> deterministic dedup -> SourceCandidate -> NeedsReview -> reviewer disposition (ConfirmedCHHHS / NotCHHHS / Uncertain / Duplicate / NeedsEvidence) -> approved projection/report. Each decision captures decision ID, assertion type, publication/person IDs, reviewer, UTC time, evidence/source snapshot hash, reason, effective date/period, and supersession link. Employment: EmployeeConfirmed / NotEmployee / Uncertain / HistoricalOrVisiting, effective-dated, with evidence type and authorised reviewer. A person can be affiliated but not employed; authorship and research collaboration are not employment proof. No automatic employment inference from domain, affiliations, DoRA/PubMed, ORCID or ROR.
4. **Safe writes**: never replace a reviewed disposition on source refresh. Separate machine suggestions, externally reported claims and reviewer-authorised decisions; pending-by-default for uncertain/no decision; explicit override event and version check for reopened decisions. Reconcile replay/duplicate events; verify state transition, concurrency/ETag, preservation of manual notes, and refusal of stale evidence before moving to approved output.
5. **Deployability**: versioned environment profile and connection-reference map, standard connector allowlist, manual setup and validation path, manifest comparing workflow IDs, triggers, connection refs, top-level action counts and hashes; tenant read-only readback is separate from source ZIP comparison. Keep all tenant personal endpoints outside source control.
6. **Interoperability**: source-qualified IDs; DOI/PMID/ORCID/ROR where supported; explicit provenance, affiliation intervals, reproducible reporting period and source query/refresh identity; CERIF/OpenAIRE/DataCite/Crossref mappings optional with source and licensing qualification. Other CareOps modules consume versioned references, not direct authoritative RIMS writes.

## Implementation queue (small, reversible tracks)
- [ ] **RIM-01 P0** Reconcile solution ZIP components and hashes against current RIMS source and optional CareOps pin, identifying exact matches, missing and newer artifacts. Inspect native tenant inventory read-only when authorised; never guess deployed parity.
- [ ] **RIM-02 P0** Inspect `ReviewStatus=Included` in all three source paths: find exact action conditions and replays; add synthetic regression fixtures to ensure candidates never silently become human-approved and reviewed states survive reingestion.
- [ ] **RIM-03 P0** Reconcile existing publication-relatedness/author/person Lists and native review screens/flows against the two-decision contract; document current UI and precise missing fields/controls without replacing existing reviewed registers.
- [ ] **RIM-04 P0** Add offline contract checker/test fixtures for publication, person, organisation, assertion, decision and issued report inputs. Include disagreement, duplicate DOI/PMID, name collisions, ex-employee, visiting clinician, no affiliation, stale evidence, ambiguous organisation, reviewer concurrence and decision supersession.
- [ ] **RIM-05 P1** Build an optional, offline review-queue export/import (CSV/JSON with schema, hash and dry-run refusal) that generates SharePoint-List-compatible candidate fields; only approved adjudications enter reports. No live data, automation or user-notification path from tests.
- [ ] **RIM-06 P1** Make CI statically inspect exported flow definitions for prohibited premium connector dependency, accidental tenant bindings, `Included` defaults without review provenance, missing connection-ref manifests and excessive flow complexity. Report-only warnings first; enforce after real baselines are classified.
- [ ] **RIM-07 P1** Reuse retained qualified DoRA/PubMed/Crossref/DataCite/ROR/ARC/NHMRC/MRFF/NIH source archives and review outputs for deterministic, source-hash-bound offline replay, trend/research network outputs and incremental change detection. Data under restricted rights stays private and is never redistributed.
- [ ] **RIM-08 P1** Reconcile the existing direct-source-migration Conductor track, historical archived child repos and current integrated-source decision; preserve signed source, attribution, recovery and independently runnable module contract.
- [ ] **RIM-09 P1** Introduce non-premium List/library provision scripts, documented columns/indexes/views/versioning and permissions with explicit dry-run; Microsoft Lists reviewer views for NeedsReview, Conflicted, Uncertain, EmployeeEvidenceNeeded, Accepted, Excluded and Reopened.
- [ ] **RIM-10 P1** Preserve natural monthly exporter/observer acceptance state; do not mark complete before correlated scheduled evidence. Reuse RMD-05 and existing owner; no new recurrence.
- [ ] **RIM-11 P2** Optional scientific intelligence: verified funding matching, studies/researchers/outputs portfolio indicators, FAIR metadata and knowledge-graph projections. Deterministic evidence first; all AI, premium reporting or external graph engines are optional consumers only.

## Acceptance and guardrails
- Core setup operates with documented standard-connector-only profile and no Dataverse/Fabric/PPU/Copilot dependency, without assuming user entitlement.
- Fictional data demonstrates two independent reviewer decisions, preservation of unrelated records/notes, zero automatic `Confirmed` or employment from machine observation, replay idempotence, audit lineage and reversible report exclusion/reissue.
- Static checks and offline tests in CI operate without tenant access or secrets; native acceptance requires separately authorised readback.
- Reuse existing approved source/operational owners and historic Conductor evidence. No email or Teams sends without explicit audience/content/scope approval.
- High-priority issue: `ReviewStatus=Included` may be a source-stage status rather than final publication acceptance; pin meaning before changing or migrating any field.

## Immediate next operation
Update existing publication review contracts and tests in the canonical CareOps RIMS path, after owner/head/dirty-worktree readback, then compare a controlled tenant export against the package fingerprint. Do not modify native instance from this track.


## Implemented source-side slice (PR #309, not native)
- `portfolio-scripts/rims_solution_audit.py`: offline ZIP manifest with workflow hashes, connector classifications and exact hard-coded inclusion assignment paths. No credentials, URLs or operational content are rendered; review component semantics before changing flows.
- `portfolio-scripts/rims_review_contract.py`: synthetic-data adjudication contract validating evidence fingerprint, UTC reviewer-event fields, assertion type, latest supersession, and employment effective-period presence.
- `portfolio-scripts/rims_review_queue.py`: source-snapshot-bound queue generation, stale-decision hold, CSV formula defusing and a fail-closed unverified offline mode. Its `trusted_decisions` input is an *integration test hook only*: native publication code MUST require independently authenticated decision provenance, permissions and current List version, and MUST NOT accept it from an API/CSV/CLI request or config file. This script never authenticates a reviewer and its CLI never exports approved publications.
- `portfolio-scripts/checks/test_rims_*.py`: fictional source and flow safety regressions; these do not qualify native data or deployment.
- `PUBLIC_SOURCE_FILES.json`: reviewed module helper, tests and plan explicitly inventoried.

Source-only reproducible commands, from the CareOps repository root:

```sh
python -m unittest discover -s portfolio-scripts/checks -p 'test_rims_*.py' -v
python portfolio-scripts/rims_solution_audit.py "/path/to/exported-solution.zip" > /private/path/solution-audit.json
python portfolio-scripts/rims_review_queue.py /private/path/review-envelope.json --format csv > /private/path/review-queue.csv
```

Offline queue envelope example (fictional identities only):

```json
{
  "schema": "careops-rims.review-queue/1",
  "candidates": [
    {
      "subject_id": "doi:10.0000/fictional",
      "assertion_type": "publication",
      "evidence_hash": "fictional-source-snapshot",
      "source_id": "pubmed:fictional",
      "title": "Fictional test publication"
    }
  ],
  "decisions": []
}
```

### Native Microsoft Lists contract, before activation
Reuse existing accepted authoritative publication register and fields rather than creating another register. Map existing `field_17` ReviewStatus and `field_18` ReviewNotes by stable List GUID/column internal name. Confirm exact value semantics and legacy `Included` population with native read-only inventory. Proposed additions only if not present already: `ReviewEventID`, `AssertionType`, `CandidateHash`, `EvidenceHash`, `ReviewerPrincipal`, `DecisionUTC`, `DecisionReason`, `SupersedesEventID`, `ReviewItemVersion`, `EffectiveFrom`, `EffectiveTo`. Reviewer views should expose NeedsReview, Uncertain, Conflicted, Excluded, Accepted and Reopened. HR/employment evidence requires more restrictive permissions than publication decisions; a public publication report must never expose it.

Create and update with ordinary SharePoint standard connector operations only, behind permission and list-version/ETag checks. Power Automate/Lists rules may notify selected reviewers only once explicitly approved; all mailing paths default Off. Never send in source tests. Existing list version history is not a substitute for a versioned decision-event ledger. Reviewer identity must come from authenticated platform context, never an editable name string.

### Acceptance blockers
1. Inspect three exact `SharePoint_Create_item` paths currently assigning `item/field_17 = Included`: Publications Register ingestion, PubMed collector and DoRA collector. Do not silently replace with `NeedsReview` until source-stage versus accepted-status semantics and downstream export filters are verified.
2. Read-only native compare against the actual solution: workflow IDs/bytes, trigger states, connection references, List GUIDs/internal columns, reviewer views and last run evidence. Export alone cannot prove deployment equivalence.
3. Verify that no unreviewed item is published, reviewer edits survive reingestion, duplicate replay does not lose audit trails, and a withdrawn approval is excluded in regenerated reporting. Publish only after native authorised evidence and report-version acceptance.

## Source implementation checkpoint — 10 November 2026

- Implemented `portfolio-scripts/rims_review_queue.py`: deterministic offline reviewer queue, stale candidate refusal, duplicate identity guards, supersession and CSV formula escaping. CLI is read-only and returns unverified `NeedsReview` records; it cannot grant report eligibility.
- Added fictional `portfolio-scripts/checks/test_rims_review_queue.py` regression cases. Source commit is not tenant acceptance or CI proof.
- Hardened `evaluate(..., verify_decision=callback)`: no caller-controlled `trusted_decisions` flag. Approvals require per-decision authorisation by an independent trusted native ledger; absent a verified callback, approved output is empty and all emitted review states are `NeedsReview`.
- Added `portfolio/rims-review-lists.schema.json` with logical source candidates, person affiliations, decisions and report issue ledger; reuse existing Lists rather than create new duplicate operational registers. Its descriptions do not provision tenant resources.
- Do not map existing `Included` values into `ConfirmedCHHHS`. The three create-item source assignments require contextual audit and tenant-side compatibility tests.
- Hosted GitHub Actions at the PR head currently fail across unrelated portfolio workflows; no merge or passing-hosted-check evidence may be claimed until host failures and genuine test issues are differentiated. Source-only dry-run tests are required before merge.
- Next native step (separate owner): read-only list/permissions/flow readback, bound reviewer form and versioned decisions, scoped release with fallback, and a natural exporter/observer verification. No Power Platform writes from this source change.

## Additional accepted tracks — 10 November 2026 (RIM-12–15)

- [ ] **RIM-12 P1 — Review queue usability**: deterministic reviewer worklists (new, conflict, stale/reopened, ageing, deferred), batch decision preflight with atomic refusal on any invalid row, explicit escalation/second-review policy, exportable audit trail, and workload/turnaround measures. Offline worklist projections must not expose private HR evidence. Native reviewer authentication and edits remain separate.
- [ ] **RIM-13 P1 — Identity resolution**: stable source-qualified DOI/PMID/ORCID/ROR and internal identities, conservative match candidates with explainable evidence, name collision/changed name/ex-employee/visitor test fixtures, effective-dated affiliations and separate employee status. Never infer employment from affiliation, name or email domain.
- [ ] **RIM-14 P1 — Reporting assurance**: deterministic period-specific reconciliation of source, unique candidate, pending, rejected, accepted, issued and withdrawn counts; source/decision/period hashes, delta against previous issued snapshot, and explicit reissue/withdrawal recommendation. No automatic issuance.
- [ ] **RIM-15 P1 — Operational observability**: tenant-free receipt summarisation (run IDs, freshness, partial pages, retries, queue age, failure class, source archive fingerprints) with bounded, redacted metadata; optional standard SharePoint List status board, no new recurring flows, email or premium telemetry.

### Sequencing and acceptance
1. **Immediate**: qualify PR #309 on exact head, diagnose all required check failures, fix actual source defects, protected merge. If Actions are blocked at runner setup, retain failed/not-run state rather than weakening protection.
2. **Offline source**: implement RIM-12/13/14/15 as independently testable standard-library modules with synthetic fixtures and no tenant access. Preserve source snapshots and audit append-only decisions; never auto-authorise a decision.
3. **Native integration**: read-only inventory of existing Lists, exact column/permission mapping, and scoped deployment of standard-connector reviewer UI/flows. Do not duplicate registers or activate emails.
4. **Source consolidation**: complete existing five-phase direct-source track once owner/branch/package/rollback prerequisites are qualified.
5. **Natural operations**: preserve RMD-05 monthly run acceptance as separate evidence and avoid re-running historical import owners.

All new tracks have independent negative cases and release gates; none are marked complete solely because a source helper exists.

### RIM-12–15 source checkpoint
- Added `portfolio-scripts/rims_assurance.py`: source-qualified exact identifier collision candidates (never automatic merges), metadata-only reviewer worklist ageing/conflict lanes, period-bound source/review reconciliation with snapshot hashes and reissue review flags, and redacted run receipt summaries.
- Added `portfolio-scripts/checks/test_rims_assurance.py` with fictional tests for collisions, malformed DOI, overdue review, changed report approval, orphan decision and private telemetry minimisation.
- These are **offline analytical projections**, not authoritative employment or publication approvals; `report_reconciliation` counts supplied statuses and cannot be used as an issuance gate without separately verified ledger provenance. Native access, identity authority and notifications remain excluded.
- Pending RIM-12: batch decision preflight and native reviewer workflow. Pending RIM-13: authoritative person affiliation/temporal identity reconciliation. Pending RIM-14: issued report version/withdrawal acceptance. Pending RIM-15: tenant-side run receipt capture and dashboard.

## Next implementation checkpoint — batch/reissue/native mapping (10 November 2026)

New implementation:
- `portfolio-scripts/rims_native_preflight.py` implements **atomic dry-run batch decision preflight** against source-candidate hash, List ETag, latest decision supersession, reviewer authority callback, UTC timestamp, and effective-dated employment evidence; a failed row refuses the whole batch, and output always says `write_authorised=false`. It also supplies historical affiliation as-of projections (explicitly not employment confirmation), and draft-only report issue/reissue planning after independent ledger verification. No native mutation path is implemented.
- `portfolio-scripts/rims_sharepoint_preflight.py` implements tenant-free read-only reconciliation of an owner-exported List inventory against exact physical List GUID, internal columns, versioning, restricted readers and a standard SharePoint-only connector profile. It refuses ambiguous duplicate authorities and leaves all mutations unauthorised.
- Fictional negative/regression tests added in `test_rims_native_preflight.py` and `test_rims_sharepoint_preflight.py`. Actual runtime/host verification remains a separate release gate. Keep private inventories outside Git.
- The SharePoint logical schema now references append-only decision, native ETag/readback and fail-closed reporting patterns. It deliberately does not create a new list, publish a report, modify a flow or send mail.

Task disposition:
- RIM-03, RIM-09, RIM-12: **source contracts and dry-run qualification partial**; actual existing tenant List GUIDs, permissions, forms and controlled append-only edits remain pending.
- RIM-13: **partial**; as-of dated affiliations provided, no trusted employee identity decision, HR system integration or automatic employment inference.
- RIM-14: **partial**; draft issue/reissue preflight provided, no authoritative production decision-verification adapter or issued-document acceptance.
- RIM-15: **partial**; source-only redacted summaries, no live operational run receipts.
- RIM-08 direct-source migration stays with its existing separate five-phase owner and cannot be claimed complete merely from RIMS source helper additions.

Verification sequence before claiming these done:
1. Check exact PR head and run `python -m unittest discover -s portfolio-scripts/checks -p 'test_rims_*.py' -v` in a qualified local interpreter; satisfy public-source inventory/privacy and targeted portfolio checks.
2. Qualify **all six required hosted checks** through GitHub normal protected merge; do not bypass if Actions are missing due to billing/host settings. Separate runner/setup blockers from test failures.
3. For actual native operation: authorised read-only List inventory, dry-run binding comparison, per-item permission/ETag checks, controlled standard-connector deployment, inverse/rollback, then independent report output validation. The source plan does not authorise tenant writes.

## Source coverage and verticals — 10 November 2026 follow-up

Read [source-coverage-and-verticals audit](../../../docs/rims/source-coverage-and-verticals-20261110.md), [publication field aliases](../../../portfolio/rims-field-aliases.json), [provenance-labelled public API rows](../../../portfolio/rims-public-api-samples.json) and [display-only decoder](../../../portfolio-scripts/rims_field_decoder.py).

- [~] **RIM-16 P1 — Dashboard code-to-label reconciliation**: exact export `field_1`–`field_20` aliases catalogued, pure decoder and synthetic collision/unknown tests provided. Still map every displayed visual/model field to exact source and current tenant readback, including codes beyond the first twenty; preserve legacy `Included` as non-authoritative.
- [ ] **RIM-17 P1 — Source utilisation/field-lineage audit**: inventory every available retained provider payload and field path; record raw -> canonical -> SharePoint -> semantic model -> display/decision lineage, loss reasons, nested array cardinality and quality metrics, with full-sample completeness where licensed. No unsupported '100% integrated' claim.
- [ ] **RIM-18 P1 — Unified person vertical with optional MS365 directory**: read-only tenant directory availability/permissions assessment; separate Entra account ID, person ID, ORCID, author mention and HR-verified effective-dated employment. Support offline authorised export as core fallback; no premium Graph HTTP dependency.
- [ ] **RIM-19 P2 — Optional NLA Trove v3 ingestion**: request/qualify an API key outside Git, select relevant bibliographic/grey-literature zones, record schema and 2–5 actual rights-compliant test records, source snapshots and identifiers; join conservatively by source-qualified bibliographic IDs with human review. No collector, credential or live samples accepted yet.
- [~] **RIM-20 P1 — Public API source example catalogues**: one actual observed public record each for Crossref, OpenAlex, ClinicalTrials.gov, with exact endpoint/provenance and selected fields; DataCite/ROR/Trove/MS Graph are **schema-only** due inaccessible or unauthorised API responses. Acquire and qualify additional real samples for each permitted provider, without exporting private MS365/CHHHS source records.
- [ ] **RIM-21 P2 — Data quality and research outcome intelligence**: field-level quality/freshness, retraction/correction signals, open access compliance, funded project -> study/output -> impact relationships, and optional historical/grey literature coverage. No AI or premium service necessary for first deterministic projections.

No public API response or source documentation proves that a Power BI visual is fixed. New source aliases and sample fixtures are **not** native report edits. Maintain the existing RIM-12–15 evidence/status and full branch protections.

### Field-use assay implementation checkpoint

- `portfolio-scripts/rims_field_coverage.py` now compares source field-path metadata to canonical/model/dashboard/decision/retained-only/excluded projections, revealing unassessed paths and keeping native parity explicitly false. This is a *declared schema* coverage check, not a live completeness claim.
- `portfolio-scripts/checks/test_rims_field_coverage.py` adds fictional negative tests for dropped fields, duplicate source paths and invalid lineages.
- `portfolio-scripts/rims_field_decoder.py` and `portfolio/rims-field-aliases.json` provide observed physical-column aliases; `test_rims_field_decoder.py` guards collisions and unknown values. Only display values change; no direct approval status mapping.
- `portfolio/rims-public-api-samples.json` distinguishes observed public API records from schema-only pending sources. `docs/rims/source-coverage-and-verticals-20261110.md` is the cross-vertical coverage audit.
- RIM-16 and RIM-20: **source-side partial**, not native fixes. RIM-17/18/19/21 remain incomplete pending real archives, actual dashboard model and authorised tenant/Trove access. Do not mark them done from static ZIP evidence.
