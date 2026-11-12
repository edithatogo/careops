# CareOps Finance — public source

This is a clean-history, source-only publication. It includes reusable report
source, synthetic samples and offline validation. It excludes the private
repository history, issues, operational records and live infrastructure bindings.
Historical planning text is source context, not proof of a public deployment.
Keep tenant settings and actual finance/workforce data outside this repository.


CareOps Finance is an organisation-neutral, source-controlled migration and
analytics module for converting legacy finance-reporting databases and files
into governed Power BI reports and semantic models.

The module is a supporting CareOps capability. It does not manage credentialing
cases or make clinical, workforce, employment, or financial-authorisation
decisions. Its reusable contribution to the wider CareOps platform is the
reporting, data-contract, validation, ALM, deployment, and reconciliation
pattern.

## Architecture

- Keep source systems and audience-specific reports separate while definitions
  are still changing.
- Promote only proven common dimensions, measures, date logic, and security into
  a shared semantic layer.
- Prefer thin reports or composite models over premature physical consolidation.
- Use PBIP, TMDL, and PBIR source formats.
- Parameterise data sources, workspaces, gateways, identities, and connections.
- Keep raw databases, extracts, credentials, internal hosts, network paths, and
  environment settings outside Git.
- Use synthetic or approved sample data for source-control and validation.

## Repository layout

- `config/`: environment-neutral source and model contracts.
- `scripts/`: repeatable inventory, extraction, transformation, and validation.
- `src/powerbi/`: report projects, semantic models, M templates, TMDL, PBIR, and
  deployment manifests.
- `docs/`: migration, source, ALM, acceptance, and operational decisions.
- `conductor/`: project context and tracks.
- `data/`: local-only raw sources, extracts, and profiling output; excluded from
  Git.

## Delivery sequence

1. Inventory and classify each source without moving unnecessary data.
2. Separate source-specific dashboards and lock their contracts.
3. Build source-controlled reports and semantic models with synthetic samples.
4. Define parameterised managed-source and gateway contracts.
5. Validate each report against the approved live source.
6. Complete business acceptance, security, privacy, access, refresh, and
   deployment checks.
7. Decide whether a shared semantic layer adds value after definitions are
   stable.
8. Promote immutable releases through approved environments.

## CareOps integration boundary

Other modules may reuse:

- validation and publication-boundary scripts;
- PBIP/TMDL/PBIR conventions;
- parameterised M and deployment settings;
- semantic-model, row-level-security, and acceptance patterns;
- data-quality, reconciliation, and release evidence.

Credentialing assurance data remains owned by its approved operational and
analytical systems. CareOps Finance must not ingest practitioner evidence,
committee papers, decision reasons, patient information, or identifiable
credentialing event data merely to provide a dashboard pattern.

See [`docs/careops-shared-reporting-boundary.md`](docs/careops-shared-reporting-boundary.md).

## Validation

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Invoke-CiChecks.ps1
.\scripts\Invoke-Validation.ps1 -Mode SourceControlReady
```

Live refresh and deployment validation require deployment-specific database,
schema, gateway, workspace, authentication, and credential values supplied
outside source control.

## Licence

Original material in this repository is licensed under Apache-2.0.
Third-party components retain their own terms.

## Qualified source-package candidates

The source-package workflow archives the exact tracked README, licence, Power BI
source definitions, configuration contracts, validation scripts and documentation. Raw databases, extracts and
compiled reports are excluded. The actual ZIP receives a file-level SPDX inventory;
main-only OIDC steps attest the same downloaded bytes and verify exact repository,
workflow, source and signer. Artifacts remain in this public source repository; no
release publication, dataset refresh, gateway change or deployment is performed.

A local archive/inventory check does not qualify Windows validation, Power BI
operation or hosted signing. Billing refusals mean those jobs did not execute;
all applicable hosted checks remain required before normal merge.

Public source CI and package attestations qualify this repository independently.


## Modular source delivery and ALM

Follow the shared delivery policy and ordered source/native queue in
[the module profile](.careops/module.json). Prefer exact useful development pins,
isolated qualification and retained recovery over replacing a working runtime.
Preserve existing publisher/logical names, stable IDs, connections, schedules and
current owners. Deduplicate only with component identity and dependency evidence.

Keep native exports, target bindings and operational records private. Version
external artifacts that do not belong in a Dataverse solution through their
existing deployment manifests. Record actual solution-layer and pipeline/Git
prerequisites separately from source CI; this profile configures no tenant.
SharePoint structured document generation remains the preferred route for any
selected structured report or document, subject to exact entitlement, complete
output, human-edit preservation and recovery qualification.


Public deployment examples use placeholders for all environment bindings,
including the SQL host/listener. Keep actual values in the existing private
operator profile; the public sample does not qualify target access or refresh.
This does not enable deployment or replace source/native ownership.

## Power BI PPU qualification — 22 October 2026

For the existing PBIP/TMDL/PBIR reporting work, qualify XMLA schema/model comparison, partition refresh and staged Power BI deployment only against an existing authorised workspace. Keep SQL/gateway/connection parameters private; PPU does not repair source connectivity, grant finance-record access or qualify a published report.

Follow the [shared PPU capability and permissions boundary](https://github.com/edithatogo/careops/blob/main/docs/development-and-delivery.md#power-bi-premium-per-user-current-qualification-boundary). The deployment operator's current PPU assignment is verified, but workspace mode, role/Build rights,
tenant settings, reader licensing and actual feature operation still require
exact-target evidence. XMLA and Power BI pipelines are qualification candidates;
Fabric Git/Copilot capacity and Power Automate/Word entitlement remain separate.
Do not infer support for report Export-to-file REST on PPU alone. Preserve current
source, native identities and recovery; no automatic workspace conversion,
settings change, new reporting dependency or cutover follows.

## Python helper isolation

The source-package, main attestation and coverage endpoint helpers activate
Python 3.15.1 in `.venv-finance-ci` through immutable setup-uv. Each job refuses
an existing environment and verifies the actual patch and repository-local prefix
before running helpers. The endpoint probe cannot fall back to ambient Python if
activation fails. PowerShell remains the source-validation and quality runner.

For local helper checks, use `uv venv --python 3.15.1 --no-project .venv-finance-ci`
and invoke `.venv-finance-ci/bin/python` (`Scripts/python.exe` on Windows)
explicitly. Helpers use only the standard library. Retain the existing package,
SPDX inventory and attestation gates; source qualification does not establish
report refresh, finance-data access or native deployment.

Retain [LICENSE](LICENSE) and [NOTICE](NOTICE) with project-owned source distributions.
