# Service Agreement and KPI Research

## Purpose

This note records the public service-agreement, KPI, finance, performance, policy, procedure, guideline, and governance sources that should shape the finance analytics roadmap.

It does not copy intranet-only documents, raw source data, credentials, network paths, or protected internal material into git.

## Source Status

| Source | Status | Notes |
| --- | --- | --- |
| ISLHD analytics share `//example.invalid/analytics` | Blocked from CLI | `Get-ChildItem` returned access denied at the share/root level, so no dashboard inventory could be collected from this session. |
| ISLHD public governance page | Available | Lists current service agreement, funding/performance supplement, KPI supplements, safety and quality accounts, and budget allocations. |
| ISLHD staff intranet Finance and Corporate Services URL | Blocked from CLI | `Invoke-WebRequest` failed with authentication error, including with default credentials. A separate shell probe also reported DNS/no-host resolution for the intranet URL. Needs interactive intranet session or explicit document export path. |
| NSW Health public performance framework | Available | Defines Service Agreements as a central component of performance management. |
| NSW Health public policy directives | Available | Service Agreement references clinical governance, corporate governance, procurement, subsidy conditions, and related policies. |

## Public Source Index

| Topic | Public source | Why it matters |
| --- | --- | --- |
| ISLHD governance source list | `https://www.islhd.health.nsw.gov.au/about-us/governance` | Public entry point for current ISLHD service agreement, KPI supplements, and budget allocation documents. |
| ISLHD 2025-29 Service Agreement | `https://www.islhd.health.nsw.gov.au/sites/default/files/Governance/Executed-Illawarra_Shoalhaven_Local_Health_District_2025-29_Service_Agreement.PDF` | Establishes accountability, funding support, governance, and policy obligations for ISLHD from 1 July 2025 to 30 June 2029. |
| ISLHD 2025-26 Funding and Performance Supplement | `https://www.islhd.health.nsw.gov.au/sites/default/files/Governance/Executed-Illawarra_Shoalhaven_Local_Health_District_2025-26_Funding_and_Performance_Supplement.PDF` | Contains the current year budget, purchased volumes, KPI thresholds, and performance deliverables. |
| KPI supplement part 1 | `https://www.islhd.health.nsw.gov.au/sites/default/files/Governance/Part_A-KPI_Data_Supplement_2025-26.pdf` | Contains detailed KPI definitions, data sources, target rules, owners, frequency, and representations. |
| KPI supplement part 2 | `https://www.islhd.health.nsw.gov.au/sites/default/files/Governance/Part_B-2025-26_Other_Measures-Data_Supplement.pdf` | Contains detailed improvement-measure definitions and district targets. Public search found the file, but the web fetch was inconsistent; treat as a source to revisit. |
| ISLHD budget allocation 2025-26 | `https://www.islhd.health.nsw.gov.au/sites/default/files/Governance/Budget_2025-26/ISLHD_Budget_Notice_2025-26.pdf` | Public budget-allocation source for finance model context. |
| Corporate budget allocation 2025-26 | `https://www.islhd.health.nsw.gov.au/sites/default/files/Governance/Budget_2025-26/Corporate_Budget_Notice_2025-26.pdf` | Public corporate-services budget-allocation source. |
| NSW Health Performance Framework | `https://www.health.nsw.gov.au/performance/pages/frameworks.aspx` | Defines the performance framework, use of Service Agreements, and KPI role at whole-service and facility/service levels. |
| NSW Health LHD board finance and performance page | `https://www.health.nsw.gov.au/lhd/boards/Pages/finance_performance.aspx` | Public board-facing summary for performance framework, corporate governance, and finance/performance oversight. |
| NSW Health Procurement (Goods and Services) policy | `https://www1.health.nsw.gov.au/pds/ActivePDSDocuments/PD2024_044.pdf` | Referenced by the Service Agreement; relevant to procurement savings and spend/procurement reporting. |
| NSW Health Clinical Governance in NSW policy | `https://www1.health.nsw.gov.au/pds/ActivePDSDocuments/PD2024_010.pdf` | Referenced by the Service Agreement; relevant to safety/quality and governance-aligned reporting. |

## KPI Domains to Model

The Funding and Performance Supplement groups performance around these domains:

- Patients and carers have positive experiences and outcomes that matter.
- Safe care is delivered across all settings.
- People are healthy and well.
- Our staff are engaged and well supported.
- Research and innovation, and digital advances inform service delivery.
- The health system is managed sustainably.

For the finance analytics system, the first directly relevant model domains are:

- Sustainability and financial performance.
- Purchased activity volumes and budget alignment.
- Procurement savings.
- Workforce and staff performance.
- Patient, access, and safety indicators for executive context.

## Initial KPI Candidates

These public KPIs should be treated as metadata/target candidates, not as measured results until the source data is identified and permissioned.

| Candidate | Domain | Target logic | Model implication |
| --- | --- | --- | --- |
| Expenditure Matched to Budget: YTD variance - General Fund (%) | Financial management | Public NSW Health examples use on-budget/favourable with underperforming at more than 0 and up to 0.5% unfavourable, not performing above 0.5% unfavourable. | Needs budget, actual expense, financial YTD period, general fund flag. Confirm the exact ISLHD supplement wording before use. |
| Own Source Revenue Matched to Budget: YTD variance - General Fund (%) | Financial management | Public NSW Health examples use the same on-budget/favourable family with a 0.5% unfavourable threshold band. | Needs revenue budget, actual revenue, financial YTD period, general fund flag. |
| Net Cost of Service / Net Result Matched to Budget: YTD variance - General Fund (%) | Financial management | Public NSW Health examples use the same budget-variance family. | Needs expense, revenue, other-items budget, and agreed numerator/denominator version. |
| Annual Procurement Savings: % achieved against target | Procurement | Performing >= 95% of target; underperforming >= 90% and < 95%; not performing < 90%. | Needs actual procurement savings, target savings, YTD period, owner and source narrative/Oracle linkage. |
| Purchased Activity Volumes: Total NWAU variance (%) | Activity and sustainability | Public NSW Health examples use budget thresholds around +/- 1.0% and +/- 2.0%, with the exact band set in the service agreement budget supplement. | Needs purchased activity target, actual NWAU, stream/facility/service grain. |
| Public Dental Clinical Service DWAU variance (%) | Activity and sustainability | Public NSW Health examples use the same purchased-volume threshold family, but the exact band should be confirmed against the district supplement. | Needs DWAU actual and target for dental service. |
| Overall Patient Experience Index | Patient experience | Adult admitted target 8.9; ED target 8.6 with threshold bands in supplement. | Executive context; likely BHI/Patient Survey Program source, not finance source. |
| Mental Health Acute Post-Discharge follow-up within seven days (%) | Safety/community care | Target 75; not performing < 60; underperforming >= 60 and < 75; performing >= 75. | Executive context; source outside finance, but useful for system dashboard later. |
| Staff Performance Reviews within last 12 months (%) | Workforce | Target 100; performing >= 90; underperforming >= 85 and < 90; not performing < 85. | Medical Staff/workforce dashboard candidate if data source is available. |
| Recruitment average days from request to decision | Workforce | Target <= 10 business days. | Workforce operations candidate; needs recruitment process data. |

## Recommended Model Additions

Add a performance-target layer when the shared model is ready:

- `dim_KPI`
  - KPI code.
  - KPI name.
  - Strategic outcome/domain.
  - Source document.
  - Owner.
  - Frequency.
  - Unit/format.
  - Directionality.
- `dim_PerformanceBand`
  - Performing.
  - Underperforming.
  - Not performing.
  - Threshold expression text.
  - Lower/upper numeric bounds where machine-readable.
- `fact_KPIResult`
  - Period.
  - Facility/service/cost centre where applicable.
  - Actual value.
  - Target value.
  - Variance.
  - Band.
  - Source refresh timestamp.
- `fact_BudgetPerformance`
  - General fund actuals.
  - Budget.
  - YTD actual.
  - YTD budget.
  - Variance percentage.
  - Budget version.

## Dashboard Implications

- Add an executive performance page later, separate from the current local proof reports.
- Keep finance KPIs in the finance semantic layer only where the source data is finance-owned or SQL-accessible.
- Keep patient, safety, public health, research, and clinical governance KPIs as external-context candidates until their source systems are identified.
- Use the KPI supplement as the metadata source for labels, target logic, reporting frequency, owners, and source-system expectations.
- Do not scrape HIRD/intranet indicator definitions into git unless explicitly approved and confirmed as permitted.
- See [docs/policy-register.md](policy-register.md) for the public policy/manual register that now anchors the roadmap.

## Next Steps

1. Confirm whether the ISLHD intranet Finance and Corporate Services page can be accessed through an authenticated browser session.
2. If accessible, inventory only document metadata first: title, URL/path, owner, version/date, topic, and sensitivity.
3. Map intranet finance policies/procedures to the public Service Agreement obligations.
4. Convert public KPI candidates into a small source-controlled metadata table or TMDL seed only after the dashboard/report grain is agreed.
5. Decide which KPIs belong in the combined executive report versus separate thin reports.
