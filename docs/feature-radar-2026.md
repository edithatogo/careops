# CareOps feature radar — 2026

Last reviewed: 2026-10-22 (earlier entries retain their historical scope)

This radar separates reusable product capability from deployment approval.
Availability in a Microsoft or GitHub product does not establish that a feature
is licensed, enabled, secure, supported, or appropriate for a particular health
service, information class, or decision.

## Delivery priority — 18 October 2026

Apply [development-first delivery](development-and-delivery.md) before historical
stable-only or optional-only framing. The next improvement should remove a real
implementation delay. Reuse current entry points first; evaluate Code Apps when
navigation or exception handling needs more. Trial native YAML/Git integration
only where the environment/repository binding topology permits it. Prefer current
qualified FlowAgent/PAC/M365 routes to repeated browser authoring. Use Process
Intelligence on a fictional/minimised case to compare delay and rework after a
working event path exists, rather than making analytics a runtime dependency.

SharePoint structured document generation is the preferred first experiment for
structured reports, agendas/minutes and policy outputs across modules. Qualify
each document shape and retain working outputs until parity/recovery. Preview
availability, credits, licences, access and actual output remain separate facts.
Human-in-loop connector previews, agent runtimes and channel agents are evaluated
only for a concrete gap, with actual channel support and business authority
preserved. No new service, purchase or consent is implied.

## Verified Power BI PPU route — 22 October 2026

The operator's current PPU assignment is verified; evaluate its XMLA/model ALM,
Power BI deployment-pipeline and refresh capabilities against existing targets.
Use the [shared PPU qualification boundary](development-and-delivery.md#power-bi-premium-per-user-current-qualification-boundary)
for per-lane next actions, role/settings checks, consumer licensing, unsupported
Export-to-file REST use and separate Fabric/Copilot prerequisites. This supersedes
licence-only uncertainty for that operator, without asserting a new assignment
date, workspace permissions or Power Automate/document-production entitlement.

## Adopt now in the repositories

### GitHub Copilot custom agents

Use repository-scoped custom agents for bounded roles such as platform
architecture, implementation, testing, privacy, security, records, and
independent assurance. Agents should have disjoint responsibilities and the
minimum tools required. Write-capable work remains pull-request based and
subject to ordinary validation and human review.

Source: <https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents>

### GitHub Copilot Agent Skills

Store repeatable project methods under `.github/skills/<skill>/SKILL.md`.
Skills should encode modular release, policy traceability, regulated-AI review,
privacy, test, deployment, and rollback methods rather than organisation- or
case-specific facts.

Source: <https://docs.github.com/en/copilot/concepts/agents/about-agent-skills>

### Deterministic validation before AI

Use schemas, rules, state machines, tests, and explicit human decision gates for
identity, dates, mandatory evidence, authority, delegation, expiry,
recommendation, decision, communication, release, and reconciliation. AI may
assist around these controls but cannot replace them.

### Feature-flagged capability packs

Deliver each feature as a disabled-by-default pack with an owner, dependency
contract, information classification, tests, human fallback, deployment gate,
metrics, support model, and rollback. Begin with one routine renewal pathway and
add changed scope, mutual recognition, temporary pathways, committee
automation, process assurance, and reporting as later packs.

## Evaluate during discovery or synthetic pilot

### AI Builder document processing and generative extraction

Evaluate layout-aware document processing for classification and extraction of
credential types, dates, scope identifiers, qualifications, and evidence
metadata. Compare trained document models with generative extraction for the
actual forms and scans. Every extracted field should retain its source document,
location or span, confidence, model/version, and human verification state.

Sources:
- <https://learn.microsoft.com/en-us/ai-builder/form-processing-model-overview>
- <https://learn.microsoft.com/en-us/ai-builder/prebuilt-document-processing>

### Power Apps human-review workbench

Use a role-specific review surface for uncertain OCR, missing information,
contradictions, proposed mappings, AI drafts, and reconciliation exceptions.
The human reviewer must be able to accept, correct, reject, and record reasons
without editing raw system logs.

Reference architecture: <https://learn.microsoft.com/en-us/power-platform/architecture/reference-architectures/ai-document-processing>

### Business approvals templates

Evaluate the preview business approvals templates when requirements justify
reusable multi-stage approval, delegation, conditional routing, central
administration, and analytics. Do not add their Dataverse, custom connector,
licensing, deployment, and support footprint to a simple MVP unless they provide
clear net value over native Teams Approvals and the existing CareOps contracts.

Source: <https://learn.microsoft.com/en-us/power-automate/guidance/business-approvals-templates/introduction>

### Power Platform and Dataverse MCP servers

Evaluate MCP only for approved development and assurance tasks, initially
read-only and non-production. Allowlist tools and environments, use least-
privilege identities, retain tool-call evidence, and prohibit access to live
practitioner or patient material unless separately approved. MCP can improve
solution inspection and agent-assisted development, but it must not become an
uncontrolled route around Power Platform, data, or deployment governance.

Sources:
- <https://learn.microsoft.com/en-us/power-platform/admin/power-platform-mcp-server>
- <https://learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-mcp>

### Power Automate Process Mining and object-centric models

Compare the managed Process Mining capability with `careops-process`. The
managed product may offer faster tenant-native discovery and dashboards;
CareOps provides portable OCEL contracts, stronger source control, explicit
privacy minimisation, and custom conformance tests. Use a small synthetic or
minimised corpus before choosing one or a hybrid.

Sources:
- <https://learn.microsoft.com/en-us/power-automate/process-mining-overview>
- <https://learn.microsoft.com/en-us/power-automate/process-mining-object-centric>

### Automation Center

Use Automation Center for flow health, queue and execution monitoring where it
adds operational value. Do not confuse flow reliability with clinical or policy
conformance. The CareOps assurance layer still needs domain-specific controls,
source reconciliation, and operating-effectiveness measures.

Source: <https://learn.microsoft.com/en-us/power-automate/automation-center-overview>

### Copilot Studio event-triggered agents

Evaluate event triggers for low-risk, reversible activities such as reminding an
owner, assembling an exception digest, opening a review task, or proposing a
response. Do not use an autonomous trigger to approve, refuse, impose a
condition, alter scope, change an authoritative register, or send sensitive
content broadly. Confirm whose credentials the trigger uses and how activity is
reviewed and disabled.

Source: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-trigger-event>

### Power Apps plans and plan designer

Use plan designer as a discovery and scaffold accelerator for data models,
requirements, user journeys, and app/flow candidates. Treat generated artifacts
as drafts to be reconciled with the CareOps domain contracts and current policy,
not as the architecture or authority by default.

Sources:
- <https://learn.microsoft.com/en-us/power-apps/maker/plan-designer/plan-designer>
- <https://learn.microsoft.com/en-us/power-platform/release-plan/2025wave1/power-apps/use-existing-apps-plan-designer>

### Copilot Memory

Evaluate repository memory for transient coding conventions, build commands, and
non-sensitive architectural facts. Do not rely on it for controlling policy,
delegations, current operational configuration, case facts, or information that
must be versioned and formally reviewed. The repository remains the source of
truth.

Source: <https://docs.github.com/en/copilot/concepts/agents/copilot-memory>

### Local or private models

Benchmark approved local or private models for OCR correction, classification,
redaction proposals, summarisation, and policy comparison where data sensitivity
or cost favours local processing. Promotion requires accuracy, calibration,
security, patching, model provenance, hardware, support, monitoring, and human-
review evidence. A local model is not automatically safer or more accurate.

## Defer from the MVP

### Autonomous clinical or credentialing agents

Do not deploy agents that determine competence, professional suitability,
service capability, scope, conditions, supervision, approval, refusal,
restriction, suspension, revocation, review, appeal, or release to practise.
These remain accountable human decisions.

### Computer-use or desktop automation as the target architecture

Desktop automation may be a short-lived, supervised bridge where no supported
interface exists. It is too dependent on screens, timing, sessions, and local
configuration to be the preferred target for an authoritative credentialing
service. Require explicit machine registration, least privilege, observation,
reconciliation, failure recovery, and an exit date.

### Production agent writes through MCP

Do not permit a general coding or assistant agent to alter production Dataverse,
Power Platform solutions, authoritative registers, records, permissions, or
workflows. Production changes use approved release artifacts, protected
environments, named reviewers, reconciliation, and rollback.

## Promotion test

A feature moves from evaluate to adopt only when there is evidence of:

1. a clear problem and accountable owner;
2. compatibility with current authority and human decision rights;
3. minimum necessary data and approved records handling;
4. measurable improvement over the simpler alternative;
5. synthetic and negative-path validation;
6. accessibility, privacy, security, support, continuity, and cost acceptability;
7. a normal non-AI or manual fallback;
8. feature flag, rollback, and exit path; and
9. operating-effectiveness and unintended-burden monitoring.
