# AHPRA registration assurance → CareOps — Conductor integration track

**Status:** Source-contract design and partial independently authored synthetic reference implementation; not native-deployed or operationally authorised.  
**Created:** 13 November 2026. **Track ID:** `REGASSURE-20261113`.  
**Source:** user-supplied AHPRA registration monitoring v3.1 archive (67 files; internal package only).  
**Destination:** active `edithatogo/careops`, not a new independent repository.

## Objective

Admit and refactor only the useful capabilities of the three overlapping AHPRA monitoring prototype generations into an **optional, standalone registration assurance capability** with a bounded, separately deployable interface to the existing CareOps Decisions credentialing register. Preserve regulator source uncertainty, independent human verification and Decisions-owned authority. No source import or tenant change is authorised by this planning track.

## Contract set

- [Normative versioned integration contract](../../../docs/credentialing/registration-assurance-integration-contract.md)
- [JSON Schema: RegistrationObservation 1.0.0 design envelope](registration-observation.schema.json)
- [MoSCoW requirements and negative acceptance tests](requirements.md)
- [Architecture, source-to-target mapping and typed state model](design.md)
- [Task-executable Conductor delivery plan](plan.md)
- [Source-admission decision (ADR RA-001)](source-admission-decision.md)
- [Clinical safety case and hazard controls](clinical-safety-case.md)
- [Engagement coverage, accreditation mapping and evaluation](engagement-coverage-and-evaluation.md)
- [Source-only synthetic reference module](../../../modules/careops-registration-assurance/README.md)

## Current state / blockers

The prototype uses an undocumented public autocomplete endpoint that is **not** an official registration-verification API; it returns suggestions with a five-result limit. Its PIE assumption of JSON/OAuth2 and API alerts is not substantiated by the publicly available PIE specification: the published FAQ documents XML responses, while the PIE information sheet describes Alerts as browser-only. No official credentials, contracted API documentation, organisation acceptance or permitted automation route is present. The archive has no licence file; source reuse terms must be established before public-code admission. Four validators previously failed to run outside the author's path layout; reproduce and repair with an exact manifest before relying on their claims. This is a design and admission assessment, not a credentialing go-live claim.

## CareOps reconciliation

- `conductor/tracks/native_09_adapters_20260923/plan.md` **N09.04**: approved Ahpra/CGov/Workforce source and interface qualification; this track supplies detailed obligations.
- `conductor/tracks/native_03_register_20260923/plan.md` **N03**: practitioner/register record ownership, versioning, native write boundaries remain unchanged.
- `conductor/tracks/native_05_checks_20260923/` and N07: optional resumable worker and workbench, without new approval authority.
- `docs/credentialing/native-microsoft-platform.md`: selected Dataverse credentialing implementation and SharePoint evidence boundary.
- `docs/standalone-module-contract.md`: self-contained core, optional versioned adapters, no parent runtime or sibling dependency.
- `docs/credentialing/next-implementation-backlog.md`: read-only discovery and silent evaluation before operational decisions.
- `AGENTS.md` and shared CI delivery contract: exact-source provenance, public-source inventory, no unapproved emails and protected merge rules.

**Milestones:** G0 contract/source safety → G1 synthetic source implementation → G2 authorised native silent evaluation → G3 explicit operational commissioning. Future Workforce/PPG/Process/RIMS links remain optional; proposals do not establish installed data sharing.

## First runnable thin slice

A local source-only engine consumes synthetic registration numbers and qualified mock/manual observations, produces the versioned observation envelope and explicit uncertain/adverse review candidates, then replays duplicates/out-of-order/blocked results **without** creating or changing a practitioner master or sending any email. Validate the machine schema, fixture invariants, privacy/secret guard and source admission before introducing a live provider.

## Non-goals and disclosure

No live AHPRA scraping, PIE login, private practitioner record transfer, production scheduled polls, staff-facing alerts, licensing purchase, tenant API activation, roster change, automatic scope restriction, adverse HR action, or auto-merge bypass. The original ZIP, credentials, contact details and operational verification evidence remain outside public Git. Native and operational status must always be reported separately from source-contract completion.

## 13 November pre-integration hardening — source-only work

The original package remains **not admitted**. The new author-written pure source model implements selected, synthetic portions of RA-T07–RA-T10: provider-capability ceiling, immutable-source comparison semantics, temporal checks, registration-category review and engagement watch coverage. It has no provider transport, real identity agreement enforcement, persistent history, managed solution, exact-head test receipt or native operational authority. A Python 3.15.1 GitHub workflow is proposed alongside the source module; locally generated synthetic tests are not acceptance of the hosted run.

Additional design controls: [source admission](source-admission-decision.md), [safety case](clinical-safety-case.md), [coverage and evaluation](engagement-coverage-and-evaluation.md), schema version 1.1 and [amendment mapping below](plan.md#preintegration-acceptance-amendments). These are part of existing RA-T tasks, not a parallel programme.

## Partial source-implementation evidence — 13 November 2026

A bounded in-tree synthetic module now has explicit [provenance and no-import claims](../../../modules/careops-registration-assurance/SOURCE_PROVENANCE.json), [standalone profile](../../../modules/careops-registration-assurance/.careops/module.json) and [implementation guide](../../../modules/careops-registration-assurance/README.md). Source includes normalised evidence classification and in-memory replay, a **trusted-input-only** provider policy gate, versioned human review transitions, a bounded lease/job/outbox reference and engagement monitoring coverage. Source logic cannot contact AHPRA, access Dataverse or Microsoft, send notifications or alter a practitioner's credentialing/SoCP.

The 87-test original synthetic source suite passed on the preceding merged head; the new deterministic core adds 34 authored regression tests covering source admission, exact identity, version CAS, append-only history, recovery and failure injection. The combined **121/121 synthetic module tests passed** under GitHub Python 3.15.1 on the verified source head before final documentation reconciliation. Protected current-head security/privacy checks and merge status must be recorded separately; no native operational qualification is inferred. G1 reference implementation is **partial**, with no real provider transport, protected persistence, source admission or operational verification. RA-T17–RA-T26 remain external/native/pilot gated.

### Deterministic offline core (proposed implementation)

See [core contract](../../../modules/careops-registration-assurance/docs/deterministic-core-contract.md) and [module README](../../../modules/careops-registration-assurance/README.md). The new strict source logic is recorded in the parent Conductor track, but **no native Dataverse/PIE implementation or clinical commissioning** is asserted. The SQLite test backend is restricted to reserved fictional watch and practitioner identifiers.
