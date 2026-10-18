# Credentialing implementation status — 10 September 2026

## Implemented in source control

- organisation-neutral CareOps modules for intake, decisions, process assurance, legacy migration, incident interfaces, costing and reporting patterns;
- coordinated credentialing release manifest and semantic cross-module contract validation;
- Policy Atlas authority profile and fail-closed source-currentness rules;
- API-first, controlled-HTML-fallback read-only legacy-system boundary;
- synthetic routine-renewal state sequence ending at `decision-recorded-not-activated`;
- separate committee recommendation and delegated decision;
- prohibition on AI credentialing decisions and production register, roster, access or release-to-practise writes in the MVP;
- deterministic aggregate capacity and benefits model with quality, burden and redeployment guardrails;
- review-only coordinated release-candidate automation;
- CHHHS current-system read-only discovery checklist and ordered implementation backlog; and
- Python 3.14 validation paths in GitHub Actions and the local `uv` qualification workflow.

## Implemented in the Policy Atlas

- national, Queensland, NSW/SCHN and Rural Generalist source metadata;
- reviewed 88-entry model-SoCP catalogue;
- public-source and local-adoption evidence ceilings;
- currentness controls where regulator, Ahpra and college sources may update asynchronously;
- read-only NSW/SCHN model-catalogue source-health monitoring; and
- public-safe Hugging Face dataset build and fixity controls.

## Not implemented or approved

- CHHHS policy or committee approval;
- confirmed current local delegations;
- live access to the end-of-life credentialing system;
- production API, export, database, HTML or desktop integration;
- migration of practitioner records;
- Power Apps, Dataverse, Power Automate, Teams or Power BI deployment in the CHHHS tenant;
- a live or silent operational pilot;
- authoritative register, roster, identity, access or release-to-practise writes;
- adoption of any external model SoCP as a CHHHS instrument;
- publication of the public-safe dataset to Hugging Face; or
- operating-effectiveness or realised-benefit findings.

## Next controlled sequence

1. Confirm the CHHHS business owner, governance route, delegations and information/records boundary.
2. Complete the read-only current-system discovery with Credentialing, Medical Workforce, Clinical Governance, Digital Health and Records Management.
3. Select the supported API, export or read-only view; use HTML extraction only where a supported interface is unavailable.
4. Establish baseline quality, workload, delay, rework, staff burden and practitioner experience.
5. Configure synthetic and minimum-necessary read-only routine-renewal observations.
6. Run retrospective and prospective silent comparisons while the current process remains authoritative.
7. Validate Rural Generalist Medicine and facility/advanced-skill modules with relevant clinicians and rural/remote services.
8. Consult all professional streams and revise the all-professions policy, common procedure and warranted profession schedules.
9. Seek separate approval for any production integration or authoritative write.
10. Evaluate quality, burden, equity, capacity released, cost, support and operating effectiveness before scale.

## Evidence boundary

Repository implementation establishes code, contracts, fixtures, source metadata and deterministic validation. It does not establish policy approval, deployment, individual credentialing decisions or operating effectiveness.
