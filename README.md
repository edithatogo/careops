# CareOps

CareOps is an organisation-neutral, modular suite for safer administrative and
clinical-governance workflows. It provides shared architecture, governance,
validation, delivery controls and deployment profiles for independently
versioned CareOps modules.

The repository is the portfolio control plane. It does **not** store operational
exports, practitioner or patient records, credentials, tenant identifiers,
secrets, production logs, generated findings or authoritative business records.

## Architecture

CareOps uses a polyrepo model:

- each module remains independently versioned, tested, licensed and deployable;
- this repository carries shared standards, integration contracts, release
  manifests, portfolio assurance and deployment profiles;
- organisation-specific rules and configuration live in profiles rather than in
  the reusable module core; and
- modules communicate through versioned contracts and stable identifiers rather
  than shared databases or copied implementation details.

This preserves a small blast radius and allows CHHHS or another organisation to
start with one bounded capability without adopting the entire portfolio.

## Modules

| Module | Primary role |
| --- | --- |
| `careops-approve` | Intake, validation, routing, human approval, delegation, escalation and decision audit |
| `careops-decisions` | Terms of reference, committees, quorum, conflicts, recommendations, decisions, minutes and actions |
| `careops-process` | Privacy-minimised event projection, conformance, delay, rework and process-improvement evidence |
| `careops-incidents` | Safety analytics and controlled signal boundaries |
| `careops-costing` | Cost, workload, capacity-release and benefits modelling |
| `careops-finance` | Governed finance reporting and reusable Power BI/ALM patterns |
| `careops-legacy-migration` | End-of-life system discovery, migration, reconciliation, cutover and decommissioning |

See [`portfolio/module-catalog.md`](portfolio/module-catalog.md) for checkout and
release status.

## CHHHS deployment profile

The initial CHHHS profile is documented in
[`profiles/chhhs/README.md`](profiles/chhhs/README.md). It adapts the generic
modules to credentialing, scope of clinical practice, committee governance and
PPG assurance while keeping Queensland and CHHHS authority separate from the
reusable code.

The coordinated draft contract is in
[`portfolio/credentialing-mvp-compatibility.json`](portfolio/credentialing-mvp-compatibility.json).
It identifies the participating module versions, boundaries, promotion gates and
status-claim limits. It is not a deployment or approval record.

## Delivery model

CareOps is delivered as small, reversible increments:

1. **MVP:** synthetic data, one bounded pathway, deterministic validation,
   human decisions and complete audit evidence.
2. **Silent pilot:** retrospective or prospective comparison with the current
   process, without changing the source system.
3. **Limited integration:** approved writes and notifications only after the
   pilot, privacy, cyber, records, clinical-governance and operational gates
   pass.
4. **Regular releases:** small capability packs behind feature flags, with
   measurable benefits and rollback evidence.
5. **Scale decision:** broader deployment only after safety, quality, workload,
   user-experience, cost and operating-effectiveness evidence supports it.

AI may extract, reconcile, summarise, draft and identify exceptions. It may not
make credentialing, scope, appeal, employment or other materially adverse human
decisions. Deterministic checks and accountable human approval remain the
controlling path.

The current adopt/evaluate/defer position for AI, agents, MCP, OCR, process
mining and Power Platform features is maintained in
[`docs/feature-radar-2026.md`](docs/feature-radar-2026.md).

## Agent support

Repository-scoped custom agents are under `.github/agents/`. Reusable Agent
Skills are under `.github/skills/`, including:

- `modular-capability-delivery`: selects the owning module and specifies a small,
  feature-flagged, reversible release; and
- `regulated-ai-assurance`: enforces source provenance, privacy, deterministic
  controls, human review, fallback and deployment evidence.

Agents and skills assist development and assurance. The repository, current
sources, approved deployment profile and accountable humans remain authoritative.

## Repository topology

`careops-approve` is currently materialised as a submodule. Other modules remain
catalogued until there is a concrete cross-module release or integration need.
The Conductor skill repository is pinned as a development submodule.

```bash
git submodule update --init --recursive
```

## Licence

Unless a module states otherwise, original material in this repository is
licensed under the MIT License. Third-party components and preserved source
artifacts retain their own terms.

## Public-source boundary

This source-only edition starts with fresh history. Earlier private history and
GitHub records remain privately archived. Deployment destinations belong in
private profiles; publication does not change their authority. Local business
document drafts, evidence receipts and workflow artifacts are excluded.

`PUBLIC_SOURCE_FILES.json` is the reviewed source inventory. Run
`python3 portfolio-scripts/validate_public_source.py` and the existing portfolio
checks before publication. An addition needs an explicit inventory update and
content review. The [hosting boundary](portfolio/host-capabilities.md) explains
which checks run automatically and which require private-module access. The
existing [suite queue](conductor/suite-delivery.md) remains the delivery plan.
