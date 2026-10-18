# Independently installable CareOps modules

Status: required target contract, not proof that current packages pass it.
Version: 0.1.0. Programme: edithatogo/careops#160.

## Rule

Every business module must install and deliver its documented standalone purpose
without any sibling module, the parent CareOps repository, a live Policy Atlas,
or an AI service. Platform prerequisites and optional capabilities must be
published. Standalone does not mean no Microsoft licensing or tenant setup.

Use one owning managed solution per core module and separate optional integration
solutions. No core cross-module Dataverse lookup, shared table ownership, import
or automatic cascading deletion may force a sibling installation. Reference an
external entity with a stable, source-qualified ID in the adapter contract.
Never duplicate authoritative ownership merely to remove a dependency.
Microsoft describes solution dependency and application lifecycle trade-offs:
https://learn.microsoft.com/en-us/power-platform/alm/organize-solutions

| Module | Standalone purpose | Optional interaction |
| --- | --- | --- |
| careops-approve | Intake, checks, correction routing and native human approval capture | Decisions packet/result adapter, external governance provider, Process events |
| careops-decisions | Own intake and committee/delegate workbench; optional internally owned credentialing-register pack | Approve packet import, external intake import, Process events |
| careops-process | Ingest authorised standard event/file inputs and analyse conformance | Approve/Decisions events; no dependency on operational write availability |
| careops-incidents | Its own authorised incident/safety analytics | Explicit minimum-necessary safety signal references, never raw narrative sharing by default |
| careops-costing | Its own parameter and activity inputs, workload and benefit evaluation | Authorised aggregate Process/Finance data |
| careops-finance | Its own governed finance migration/reporting capability | Optional Costing and other approved source adapters |
| careops-legacy-migration | Discovery, mapping, reconciliation and migration rehearsal for an external legacy source | Optional per-module destination adapters; no runtime migration-service dependency after cutover |

A standalone credentialing application still needs the human governance required
by its pathway. It may record verified external human decisions or use the local
approved provider; it cannot treat an absent Decisions module as permission to
skip the committee/delegate. Similarly, Decisions can accept a controlled local
case without Approve. Use an approved local rule snapshot when Policy Atlas is
unavailable, not agent-inferred policy or a bypass of currentness requirements.

## Integration contract

Adapters declare provider/consumer versions, correlation ID, source record and
revision, classification, minimum payload, purpose/consent where applicable,
idempotency key, timestamp, authority/evidence references and error semantics.
Authenticate the caller; an ID or hash is not authentication. Define compatibility
and reconciliation before enabling an adapter. Optional absence uses a documented
standalone route. An outage preserves work and reports uncertainty, not an empty
register, automatic approval or adverse practitioner result.

Use durable, bounded retry with dead-letter/recovery ownership. Only affected
downstream prerequisites wait. Analytics, AI, notifications and optional upstream
modules must not be required for core register reads. A common Dataverse
environment may be economical but shares a restore and outage boundary; separate
managed solutions alone do not provide infrastructure isolation.

## Required release evidence for every module

- Clean install on a blank approved environment with no sibling solution.
- Complete the documented standalone business scenario and accessibility tests.
- Run with AI off, optional integration absent, provider unavailable and stale data.
- Inspect solution dependencies: no undeclared sibling/table/flow requirements.
- Test supported adapter combinations and version mismatches in both directions.
- Upgrade one module while other modules stay at supported prior versions.
- Disable/uninstall an adapter without deleting authoritative records or stopping cores.
- Rehearse module retirement with export, retention and reconciliation first; never
  claim managed-solution uninstall is safe for owned tables without preservation.
- Rebuild from signed/versioned artifacts, verify access and configuration, and
  practise recovery at the actual environment boundary.
- Record owner, on-call/escalation, licences, capacity, support window and the
  existing manual task that the feature removes.

The register stays in careops-decisions ownership; no new repository is needed.
Library code can be packaged at build time, but a central runtime or mandatory
shared business solution must not silently recreate a monolith.
