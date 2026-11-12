# PPG policy, external authority and accreditation assurance

Status **in progress — portable source tranche only**, 11 November 2026. Existing PPGWorkbench is the canonical policy-management implementation; do not create a duplicate service or override its native authors. All inputs/outputs are source-only fictional; external authority capture and tenant acceptance require separate proof.

- [MoSCoW requirements](requirements.md)
- [Architecture and contracts](design.md)
- [Executable work packages and dependencies](plan.md)
- [Current source validation and limitations](implementation.md)

Existing source to **reuse**: policy editions, identity and source-update tools, `ppg_source_surveillance`, `ppg_standards_contract`, `ppg_accreditation_contract`, `ppg_accreditation_decisions`, `ppg_accreditation_quality_example`, indicator-source bindings, external-catalogue and native qualification tools. Preserve their schema IDs and versioning. No wholesale rewrite of installed workflows.

**Terminology:** The commission is the Australian Commission on Safety and Quality in Health Care (**ACSQHC**), and the national hospital accreditation framework is **NSQHS**. The operative 2nd edition and the draft 3rd edition must have separate edition identities. No draft or mapped source can automatically create an operative obligation.

**Non-premium-first:** source and contracts function offline; the deployment core may use SharePoint Lists, Libraries, version history and standard connectors. Full Dataverse/Fabric/AI and paid integrations are optional feature packs, not prerequisites. Git does not store private operational policy text, licences, authored records or real accreditation evidence.

External accreditation bodies issue their own findings and conditions. Internal readiness, policy approval, a requirement mapping, observed clinical implementation and external accreditation are independent.


## Source additions (not native deployment)

- [Obligation classifications and local policy adoption](../../../scripts/ppg_obligation_application.py)
- [Evidence review-window projection](../../../scripts/ppg_evidence_currency.py)
- [Unified read-only assurance packet](../../../scripts/ppg_assurance_bundle.py)
- [Standard-connector SharePoint list source contract](../../../config/assurance-sharepoint-registers-v1.json)
- [Offline field-definition validator](../../../scripts/ppg_assurance_sharepoint.py)

The new work is additive to existing standards, scheme adoption, policy currency and internal PPG review flows. No inferred legal force, accredited decision, approval or native write follows from these components.
