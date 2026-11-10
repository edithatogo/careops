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
