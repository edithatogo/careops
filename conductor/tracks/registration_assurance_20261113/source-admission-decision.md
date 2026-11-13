# ADR RA-001 — Selective admission of AHPRA monitoring v3.1 source

**Decision:** 2026-11-13. **Status:** accepted for source-only design; package implementation not admitted. **Scope:** new CareOps registration assurance source, not regulated operational production.

## Context

The supplied 67-file archive has three overlapping prototype generations: `ahpra-monitoring-repo/`, `ahpra-getpredictions-bootstrap/` and `ahpra-watchlist-notifications/`. Four supplied validators depend on the original author's directory layout and did not run successfully during assessment. No original licence is provided. The prototypes include an undocumented five-result autocomplete source, platform-specific watchlists, both Logic Apps and Power Automate runtimes, and a proposed PIE configuration switch inconsistent with AHPRA's published XML API and browser-only Alerts details.

## Decision

**Do not bulk-import or repair all three generations.** Use a clean-room source contract and synthetic reference implementation first. Treat archive components solely as design inputs until rights and source review establish admission. For each individual admitted asset require provenance, licence/reuse, maintainer, runtime prerequisites, current tests and semantic difference from the selected CareOps capability.

| Original asset | Decision | Condition for reuse |
| --- | --- | --- |
| `test/mock-ahpra/mock_responder.py` | Reimplement or selectively reuse as synthetic fixture only | Licence + secret/data scan + no live calls + adversarial tests |
| `config/providers.json`, `docs/PIE-SWITCH.md` | Replace, not mechanically migrate | Issued PIE technical spec (actual XML/auth/fields), organisational rights and redacted source profile |
| `scripts/build_*.py`, `scripts/validate_*.py` | Selectively retain only valuable generators after native target selected | Remove absolute paths; reproducible tests; approved reuse rights |
| Existing BPMN and Mermaid documents | Reference for design comparison | Verify against new state/authority model; source attribution |
| `ahpra-getpredictions-bootstrap/*` | Reject from active monitoring runtime | Historical reference only; autocomplete cannot prove regulatory status |
| Existing Lists/Excel schemas | Reject as practitioner master | Only a monitoring-owned state model, with restricted evidence references |
| Parallel Logic Apps / Power Automate workflows | Do not commission together | Select a single writer/execution owner and separately qualify licensed optional HTTP route |
| Unapproved external live calls | Disabled | Separate AHPRA agreement, approved use and operational permission |

## Architectural decision

CareOps Decisions/credentialing remains the master of practitioner identity, professional engagement, credentialing and SoCP. Add one optional standalone `careops-registration-assurance` module for watches, source observations, job health, exception candidates and versioned review references. It has no dependency on live Decisions, RIMS, AI, a premium connector or parent runtime. The **default operational architecture** for existing full credentialing is the approved full-Dataverse/managed-solution target of `docs/credentialing/native-microsoft-platform.md`; the restricted Standard-M365/manual profile is a separate lightweight deployment, **not a second synced Dataverse practitioner master**. There is only one monitoring job/observation writer per selected deployment; HTTP/Logic Apps variants are not concurrent systems of record.

## Consequences, reversibility and release impact

- Build a small schema/assessor and source-health harness before native flow adaptation. No old workflow is deployed merely because its builder passes.
- Preserve the original ZIP privately with hash; public CareOps includes only independently authored synthetic code/contracts and source citation.
- Source admission may remain blocked without preventing synthetic and manual-path qualification.
- Do not modify current provider credentials, CGov master, roster, licensing, protections, existing migrations or email flows.
- RA-T03 is reduced to repairing **selected retained builders only** rather than all historical generators; completion requires a documented rejected-assets inventory.

## Source and regulatory references

- AHPRA PIE service: https://www.ahpra.gov.au/Registration/Employer-Services/External-data-exchange-services
- AHPRA PIE FAQ: https://www.ahpra.gov.au/Registration/Employer-Services/External-data-exchange-services/Practitioner-information-exchange/PIE-FAQ
- CareOps N03/09 and native Microsoft credentialing architecture: linked by the main track index.
