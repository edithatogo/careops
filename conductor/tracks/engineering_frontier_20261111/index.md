# CareOps technical engineering frontier

Status: **planned; not implemented or qualified**. Created 11 November 2026 on a source-only proposal branch. Owner: CareOps parent engineering; existing module maintainers own their own source and native qualification.

This track covers **technical platform development only**: agent harness/context engineering, executable quality, privacy, security, supply-chain controls, deterministic workflow automation, developer experience and reproducible performance/recovery. Do not make organisational impact, research publications, productivity claims or live business rollout prerequisites.

- [MoSCoW requirements](requirements.md)
- [Architecture and reuse](design.md)
- [Executable work and dependencies](plan.md)
- [Acceptance and evidence contracts](contracts.md)
- Existing delivery [CI track](../suite_ci_delivery_20261018/index.md), [native N01–N12](../../native-m365-roadmap.md), [module profile](../../../.careops/module.json) and [source delivery contract](../../../docs/ci-delivery-contract.md) remain authoritative within their scopes.

**Boundary:** The cross-cutting track coordinates shared engineering contracts, not another runtime, mandatory database, tenant, paid service, approver or agent framework. Existing standard-Microsoft-365 / Copilot-off pathways remain the baseline; premium features and all AI/model providers remain opt-in. Use existing AGENTS.md, .github/agents, .github/skills, harness, security workflows, Conductor and child-module test runners; replace only on demonstrated necessity.

**Current evidence:** parent `main` revision `7de89d644b66123b47d75816dd9f5f9600e69f83` (8 November 2026). On 11 November, relevant open PRs include #312 (reusable meetings), #309 (RIMS), #311 (Presidio/Gitleaks) and #308 (Process). Workflow runs at inspected PR heads report failures and skipped jobs, often with no executed steps; #301 records hosted Actions/billing unavailability. Do not treat planned checks, earlier successful heads, unexecuted runs or local validations as current-head hosted qualification.

**Release rule:** Do not merge this work or other PRs by bypassing existing protected checks. Restoration of hosted execution and exact-head checks is the first integration gate. A PR for these planning documents is not an engineering achievement in itself; finish each work package with code, negative tests and source-appropriate evidence.

**Priority sequence:** restore trusted CI; measure current harness; implement context/task contracts and mediated tools; extend adversarial quality/security; automate reproducible artefacts, safe native ALM and measurable technical regressions. Each package may be delivered independently by one maintainer or coding agent.

## 11 November technical source checkpoint

- [Source implementation and honest qualification](implementation-20261111.md)
- [Open-PR CI reconciliation](ci-reconciliation-20261111.md)
- [Pre-publication sensitivity gates](publication-sensitivity-20261111.md)
- [Power Platform, Dataverse and Fabric technical ALM assessment](../../../docs/platform-native-ci-frontier-20261111.md)

New executable source: [offline engineering preflight](../../../portfolio-scripts/engineering_frontier.py), with [synthetic negative tests](../../../portfolio-scripts/checks/test_engineering_frontier.py). These source artifacts do **not** create a host-enforced agent sandbox, authorize tenant writes or establish full EF-00–03 completion.

## Current integration increment

- [Read-only CI collector and Linux sandbox implementation](isolation-collector-20261111.md)
- [Read-only CI collection source](../../../portfolio-scripts/frontier_ci_collect.py)
- [Linux fail-closed isolation source](../../../portfolio-scripts/frontier_isolation.py)

These changes extend EF-00/EF-03 **source scope only**. Host-enforced broad tool permissions and successful canonical hosted execution are not claimed.
