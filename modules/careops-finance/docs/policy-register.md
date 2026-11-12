# NSW Health Policy Register

This register lists the public policy, governance, and manual-level sources that are directly relevant to the finance analytics system. It is a working reference only and does not replace the underlying source documents.

## Core Public Sources

| Topic | Source | Why it matters |
| --- | --- | --- |
| Performance framework | `https://www.health.nsw.gov.au/performance/pages/frameworks.aspx` | Sets the role of Service Agreements and KPI reporting in NSW Health performance management. |
| ISLHD governance entry point | `https://www.islhd.health.nsw.gov.au/about-us/governance` | Public hub for the current service agreement, KPI supplements, and budget documents. |
| ISLHD 2025-29 Service Agreement | `https://www.islhd.health.nsw.gov.au/sites/default/files/Governance/Executed-Illawarra_Shoalhaven_Local_Health_District_2025-29_Service_Agreement.PDF` | Establishes district obligations, governance, reporting, and performance expectations. |
| Funding and performance supplement | `https://www.islhd.health.nsw.gov.au/sites/default/files/Governance/Executed-Illawarra_Shoalhaven_Local_Health_District_2025-26_Funding_and_Performance_Supplement.PDF` | Defines the current budget and performance delivery contract. |
| KPI supplement part A | `https://www.islhd.health.nsw.gov.au/sites/default/files/Governance/Part_A-KPI_Data_Supplement_2025-26.pdf` | Contains KPI definitions, thresholds, owners, and frequency metadata. |
| KPI supplement part B | `https://www.islhd.health.nsw.gov.au/sites/default/files/Governance/Part_B-2025-26_Other_Measures-Data_Supplement.pdf` | Contains the other measures and target metadata used alongside the KPI supplement. |
| Budget allocation notices | `https://www.islhd.health.nsw.gov.au/sites/default/files/Governance/Budget_2025-26/ISLHD_Budget_Notice_2025-26.pdf` and `https://www.islhd.health.nsw.gov.au/sites/default/files/Governance/Budget_2025-26/Corporate_Budget_Notice_2025-26.pdf` | Provide the public budget context for district and corporate functions. |
| Procurement policy | `https://www1.health.nsw.gov.au/pds/ActivePDSDocuments/PD2024_044.pdf` | Relevant to procurement savings, sourcing, and spend controls. |
| Clinical governance policy | `https://www1.health.nsw.gov.au/pds/ActivePDSDocuments/PD2024_010.pdf` | Relevant to safety, quality, and governance-aligned reporting. |
| Financial requirements and conditions of subsidy | NSW Health public finance guidance | Relevant to funding conditions, subsidy handling, and financial reporting discipline. |
| Accounting and audit guidance | NSW Health public accounting/audit manuals and determinations | Relevant to ledger definitions, auditability, and standard finance controls. |
| Delegations and authority guidance | NSW Health public delegation guidance | Relevant to approval thresholds, purchasing authority, and governance reporting. |

## Intranet-Only Sources

| Source | Status | Notes |
| --- | --- | --- |
| ISLHD Finance and Corporate Services intranet page | Blocked from CLI | Authentication error from `Invoke-WebRequest`. Treat as an authenticated-browser or manual export source only. |
| Local policy/procedure/guideline library behind the intranet page | Not yet inventoried | Once access is available, inventory metadata only first. Do not copy protected documents into git. |

## Working Rules

- Use the public sources above to anchor the finance roadmap and KPI catalogue.
- Use intranet-only material only when the user can confirm permitted access and export handling.
- Keep policy text, PDFs, and other protected documents out of git unless they are public and explicitly needed for source control.
- Translate the policy requirements into model metadata, target logic, or operational checklists rather than embedding policy prose in reports.
