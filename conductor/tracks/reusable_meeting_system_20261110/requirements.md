# Requirements (MoSCoW)

| ID | Priority | Contract / acceptance |
| --- | --- | --- |
| RMS-R01 | Must | Each forum has a stable independent forum_ref, explicitly pinned revision and namespace; identical inputs produce identical outputs regardless of order. |
| RMS-R02 | Must | Many forums may share a template and one Decisions register without sharing occurrence, meeting or action identities. |
| RMS-R03 | Must | Deterministic validation/preflight, calendar comparison and carry-forward reuse existing H2 contracts; never auto-approve, issue minutes, invent owners/dates or create actions. |
| RMS-R04 | Must | Core installs without Copilot, AI Builder, premium connectors, Dataverse or custom HTTP; missing optional providers never break standalone mode. |
| RMS-R05 | Must | Actual business authority and official policy/ToR edition are verified outside draft metadata; unknown/conflicting authority holds live publication. |
| RMS-R06 | Must | Exactly one authoritative record for decisions/actions; linked Planner tasks are execution projections, not duplicate closure authority. |
| RMS-R07 | Must | Native writes only after access, version/ETag, exact target, no-email effects, replay/uncertain-result and recovery qualifications. |
| RMS-R08 | Must | Source/test artefacts contain no operational data, private tenant bindings or secrets; documents and actions require human review. |
| RMS-R09 | Must | Use existing protected CI and privacy gates; record blocked/unexecuted independently of passing tests. |
| RMS-R10 | Should | One declarative profile supports distinct agendas, roles, evidence, sources, cadence, controls and templates without copying workflows. |
| RMS-R11 | Should | One manifest and installation report distinguish source-verified, native-configured and operationally accepted for each forum. |
| RMS-R12 | Should | Optional provenance references enable retrieving the exact reasons, conditions, dissent, source versions and later outcomes. |
| RMS-R13 | Should | Repeated work, waiting and reopenings can be exported as minimised, consented object-centric event data. |
| RMS-R14 | Could | Offline signed/snapshotted read-only fallback with expiry and scoped permissions. |
| RMS-R15 | Could | Local models or Copilot draft candidates only when selected and benchmarked, never as authority. |
| RMS-R16 | Won't (core) | Automatic decisions, automatic emails, auto-issuing minutes, premium-first setup, per-forum duplicated action stores or a new hosted Python service. |


## Implementation refinement — 10 November

| ID | Priority | Contract / acceptance |
| --- | --- | --- |
| RMS-R17 | Must | Read-only cross-forum projection rejects unselected forum data, duplicate composite action IDs and malformed state/revision/date metadata. |
| RMS-R18 | Must | Reported-complete, resolved and closed governance matters retain distinct semantics; a projection cannot create a decision, approve closure, or authenticate supplied evidence. |
| RMS-R19 | Must | Native provider proves complete pagination, selected List/tenant scope, owner permission and current version/ETag before declaring the projection operational. |
| RMS-R20 | Should | Sorted deterministic projections produce reproducible hashes and no input mutation; identical local IDs remain safe across distinct forums. |
