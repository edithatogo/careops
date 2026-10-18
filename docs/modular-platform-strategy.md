# Modular platform strategy

## Decision

CareOps will remain a modular polyrepo portfolio. Existing repositories are the
implementation units; the parent `careops` repository is the control plane for
shared standards, contracts, dependency pins, portfolio assurance, and
organisation-specific deployment profiles.

This is faster than creating a replacement repository because the existing
modules already contain tested workflow, governance, process, analytics, and
ALM patterns. It is safer than merging everything because the modules have
different release cadences, platform dependencies, data boundaries, and
operational owners.

## Module responsibilities

| Module | Owns | Does not own |
| --- | --- | --- |
| Approve | Intake, validation, routing, delegation, escalation, human decision capture | Clinical judgement, committee authority, source records |
| Decisions | Governance bodies, ToR, meetings, quorum, conflicts, recommendations, decisions, actions | Practitioner evidence repository, policy interpretation |
| Process | Privacy-minimised events, conformance, variants, delay and rework analysis | Operational case management or automated workflow mutation |
| Incidents | Safety analytics and reusable Power BI/ALM patterns | Credentialing case records |
| Costing | Cost, effort, capacity release and benefits | Operational finance ledger |
| Finance | Governed finance migration and reporting patterns | Clinical decision making |

## Shared contracts

The parent repository should progressively hold or index only the stable
cross-module contracts:

- identifiers and correlation IDs;
- capability and feature manifests;
- event and audit envelopes;
- policy/source assertion metadata;
- human-review and decision-authority requirements;
- privacy classifications;
- deployment profile schemas; and
- release compatibility matrices.

A module may implement a contract without sharing its database or internal
schema. Integration is by stable ID and explicit API, event, or file contract.

## MVP and incremental release pattern

Each deployment profile uses the same release sequence:

### Release 0: foundation

- synthetic fixtures only;
- deterministic validation and fail-closed rules;
- complete audit trail;
- feature flags disabled by default;
- no production writes;
- no autonomous AI decisions.

### Release 1: bounded MVP

- one high-volume, lower-complexity pathway;
- one accountable owner and one operational team;
- manual source-system confirmation;
- human approval at every material decision;
- baseline measures for time, touches, quality, exceptions, and staff effort.

### Release 2: silent assurance

- retrospective or prospective shadow operation;
- compare required evidence, timing, routing, and decisions;
- measure false positives, false negatives, rework, and user burden;
- no effect on practitioner, patient, employment, or service rights.

### Release 3: limited integration

- approved system writes only;
- least-privilege connections;
- explicit release-to-practise and expiry controls;
- rollback, continuity, support, and reconciliation evidence.

### Subsequent releases

Capabilities are added as small packs, for example:

- advanced evidence extraction;
- additional professional streams;
- temporary and mutual-recognition pathways;
- committee automation;
- operational dashboards;
- process mining;
- policy change detection; and
- controlled agent assistance.

Each pack has an owner, threat model, acceptance tests, training, feature flag,
rollback, and measurable benefit. A failed pack can be disabled without
removing the core service.

## AI and agentic boundary

AI is optional assistance, not the decision authority. Appropriate uses include
classification, OCR, extraction, reconciliation, summarisation, drafting,
policy-change triage, exception grouping, test generation, and code review.

AI must not independently:

- verify identity or registration;
- certify mandatory evidence;
- determine competence or suitability;
- decide scope of clinical practice;
- approve, refuse, suspend, reduce, or revoke authority;
- determine an appeal or review; or
- publish an authoritative record.

Every AI run must retain provider/model, prompt or agent version, source IDs,
input and output hashes where appropriate, confidence, exceptions, reviewer,
and review outcome. Failure or low confidence returns to the normal human path.

## When to reconsider a monorepo

A monorepo becomes preferable only when all of the following are substantially
true:

- modules are routinely changed in the same pull request;
- they share one release cadence and deployment pipeline;
- they have the same security and publication boundary;
- one team owns and supports them;
- independent versioning creates more coordination cost than value; and
- repository size and tool performance remain manageable.

Until then, a polyrepo with a lightweight control plane gives faster bounded
releases, clearer ownership, safer rollback, and better reuse.
