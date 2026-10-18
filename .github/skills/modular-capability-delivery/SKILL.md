---
name: modular-capability-delivery
description: Plan and implement a small, reversible CareOps capability pack in the correct existing repository, starting with an MVP and preserving cross-module contracts.
---

# Modular capability delivery

Use this skill when adding or changing a CareOps feature.

## 1. Select the owning module

Assign the feature to one existing repository:

- `careops-approve`: intake, validation, routing, delegation, escalation, human approval capture;
- `careops-decisions`: committees, ToR, quorum, conflicts, recommendations, delegated decisions, minutes, actions;
- `careops-process`: privacy-minimised events, conformance, variants, delay, rework, improvement evidence;
- `careops-incidents`: incident and safety analytics with controlled signal boundaries;
- `careops-costing`: workload, costs, benefits, capacity release, economic evaluation;
- `careops-finance`: finance analytics and reusable Power BI/ALM patterns;
- `careops-legacy-migration`: legacy discovery, mapping, migration, reconciliation, cutover, decommissioning;
- `careops`: portfolio standards, deployment profiles, compatibility, cross-module release evidence.

Do not create a new repository or move modules into a monorepo unless no existing
module owns the capability and the topology gate is documented.

## 2. Define the smallest useful release

Record:

- user and problem;
- owner and support role;
- in-scope and excluded pathways;
- current source and authority references;
- information classification;
- residual human decision;
- feature flag and default state;
- dependencies and versioned interfaces;
- success and balancing measures;
- rollback and exit path.

Prefer one pathway, one team, synthetic fixtures, and no production writes for
the first release.

## 3. Specify contracts before implementation

Use stable identifiers and explicit schemas for:

- request or case;
- source and evidence references;
- workflow states and events;
- recommendation and decision records;
- errors, exceptions, corrections, and reconciliation;
- audit and provenance;
- metrics and semantic projections.

Integrate by contract rather than shared database, copied code, or implicit
field assumptions.

## 4. Build safety and quality in

Include deterministic checks, least privilege, classification, records,
accessibility, privacy, security, duplicate safety, timeout, correction,
cancellation, escalation, dead-letter, reconciliation, continuity, and rollback.

Use synthetic positive, negative, boundary, replay, failure, AI-disabled, and
AI-failure tests. A generated artifact is not deployment or operating-
effectiveness evidence.

## 5. Preserve human authority

AI and automation may prepare, validate, classify, extract, summarise, or draft.
They do not make clinical, credentialing, employment, financial, review, appeal,
or other materially adverse decisions. Record the accountable human and the
evidence of their act.

## 6. Deliver through a small pull request

The pull request must state:

- owning module and capability-pack version;
- what changed and what remains disabled;
- data, policy, licence, deployment, and support implications;
- tests and validation performed;
- residual gates;
- rollback;
- whether repository, tenant, pilot, and operating-effectiveness status changed.

Do not merge a large collection of unrelated features merely because they share
a strategic theme.

## Development and delivery alignment — 18 October 2026

Start with the owning module's `.careops/module.json`, current task and
[shared delivery policy](../../../docs/development-and-delivery.md). Choose the
first eligible low-hanging-fruit improvement; do not reopen a completed MVP.
Prefer current useful development builds resolved to exact pins and qualified in
isolation. Use maintained Word templates/SharePoint structured generation first
for structured documents, retaining human edits and working fallbacks until parity.
Keep native owners, independent installation and existing authority/mirror mappings.
Use existing queues and evidence; one terminal result or changed blocker is enough.
Update the shared lesson once after a demonstrated improvement, not after every
status turn. Technical system setup does not require real content review or use.
