# Organisation deployment profile

This example adapts the organisation-neutral CareOps modules for a health service.
The retained directory name is a historical link identity, not a default tenant or
organisation binding. It contains design and configuration intent only. It must not contain practitioner, patient, workforce,
committee, credential, tenant, or production data.

## Initial use cases

1. Medical and dental credentialing and scope of clinical practice (SoCP).
2. Credentialing committee governance, recommendations, delegated decisions,
   conditions, expiry, review, and appeal.
3. Clinical and medical policy, procedure, and guideline assurance.
4. Process conformance, workload, delay, rework, and quality reporting.

## Authority boundary

The controlling authority remains the applicable current legislation, health-system
instruments, local policy and procedures, current delegations, approved
committee terms of reference, and accountable human decision makers.

Reusable module code must not embed jurisdiction-specific legal or clinical
conclusions. The deployment overlay should map each deterministic rule to a current
source, effective period, reviewer, and stable identifier. Proposed AI mappings
remain non-controlling until approved by an authorised human reviewer.

## Credentialing module composition

- `careops-approve`: intake, completeness checks, evidence requests, routing,
  reminders, escalation, and auditable human decision capture.
- `careops-decisions`: committee mandate, membership, quorum, conflicts,
  recommendation, reasons, delegated decision, minutes, and actions.
- `careops-process`: privacy-minimised event projection and conformance analysis.
- `careops-costing`: baseline effort, cost, capacity release, and benefits.
- `careops-incidents`: reporting and assurance patterns where safety information
  is lawfully and appropriately linked.

## Pilot sequence

### Phase 0: synthetic validation

- synthetic practitioners, documents, committees, decisions, and events;
- deterministic rules and policy traceability;
- no production connections;
- security, privacy, records, clinical-governance, and accessibility review.

### Phase 1: retrospective silent study

- approved de-identified or minimised historical cases;
- no source-system writes;
- compare completeness, pathway, timing, exceptions, and required controls;
- do not use AI output as evidence of identity, registration, competence, or
  authority.

### Phase 2: prospective silent mode

- run beside the current process;
- no effect on current approvals or practitioner rights;
- measure time, manual touches, rework, false alerts, missed requirements,
  committee preparation, and staff experience.

### Phase 3: limited integration

- only after explicit approval and acceptance evidence;
- least-privilege connections and approved records locations;
- clear source of truth and reconciliation;
- rollback and continuity controls;
- human decision and release-to-practise gates remain mandatory.

## MVP recommendation

Begin with one bounded pathway such as routine medical and dental renewal and
expiry assurance. Add changed SoCP or mutual recognition only after the first
pathway demonstrates reliable policy mapping, evidence validation, auditability,
and measurable workload reduction.

The discovery and pilot must remain separate from the independent credentialing
audit. Audit findings may inform priorities and reusable control definitions,
but the digital service must not pre-empt or constrain independent audit
conclusions.
