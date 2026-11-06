# Implementation plan

- [x] Add permissive licensing.
- [x] Genericise the active README and track registry.
- [x] Document the shared reporting boundary.
- [x] Register this Conductor track.
- [ ] Inventory active tracked files for internal hosts, network paths, database
  names, tenant values, and organisation-specific claims.
- [ ] Move required environment values into protected deployment settings and
  provide safe examples.
- [ ] Extract reusable PBIP/TMDL/PBIR, validation, RLS, reconciliation, and ALM
  templates without copying business data or report-specific logic.
- [ ] Define a versioned compatibility contract for other CareOps modules.
- [ ] Add synthetic credentialing assurance model fixtures only after the
  operational source and privacy model are agreed.
- [ ] Keep live source, gateway, workspace, security, and business acceptance as
  deployment-specific evidence.

## Suite CI delivery — 18 October 2026

- [x] Inventory workflow pins and retain native Power BI/PowerShell source checks.
- [x] Prepare immutable current actions and shared CareOps security adoption; preserve required check names.
- [ ] Verify full local quality gate and all four evidence techniques.
- [ ] Qualify hosted PR checks; classify billing/entitlement refusals separately.
- [ ] Add scheduled exact PowerShell development canary with integrity receipts.
- [ ] Qualify actual source package SBOM/attestations and reporting interfaces.
- [ ] Migrate required security contexts only after successful hosted qualification.

Local evidence: PowerShell 7.6.7 passes RepositoryHygiene after replacing a
Windows-only sample-table path match with separator normalization. All four
evidence techniques pass unchanged. SourceControlReady reaches its existing
Windows Registry tests and cannot complete on macOS; Windows hosted execution
remains required. No skipped registry test is recorded as passing.

19 October: PR14 now includes a weekly/manual isolated Windows PowerShell
preview canary. Resolve the greatest official non-draft preview semantically,
require its exact official archive URL and published SHA256, verify the archive
before extraction and the executable's reported version before running both
existing source modes and all four quality techniques. Preserve exact candidate
and terminal step receipts; never promote or deploy automatically. Seven local
selection/integrity/refusal cases, real read-only preview resolution, existing
RepositoryHygiene and all four quality techniques pass on PowerShell7.6.7.
Windows preview execution, hosted gates, release attestations and cross-module
compatibility remain unqualified; account billing previously prevented execution.
