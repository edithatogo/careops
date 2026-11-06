# CareOps Costing — public source

Reusable offline Power Platform packaging, generated solution bootstrap and UI
source. This clean-history publication excludes the private workbook analysis,
Word document, ZIP inputs, CSV registers, tenant bindings and operational history.
It does not establish redistribution rights for those retained private materials.

Run the existing PowerShell packaging command tests and source CI before using
an artifact. Native deployment and substantive costing parity remain separate.
The bootstrap and UI source are development candidates, not operational approval.

The [`powerplatform/costing-core`](powerplatform/costing-core/README.md) package
provides an independent fictional activity-cost calculation and optional
aggregate-provider contract. It contains no Figma UI source, private workbook
material or native binding; its calculation checks run in the existing Node
26.12.0 source-CI lane.


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

## Locked solution SDK build

The bootstrap project pins Microsoft.PowerApps.MSBuild.Solution 2.14.1 and
.NET Framework reference assemblies 1.0.3 with a committed NuGet content-hash lock.
On Windows, run `dotnet restore powerplatform/solution_bootstrap/bootstrap_solution.cdsproj --locked-mode`,
then `dotnet build powerplatform/solution_bootstrap/bootstrap_solution.cdsproj --no-restore -c Release -p:SolutionPackageType=Managed`.
Source CI compares every SDK archive member against the existing pinned PAC
package, allowing only XML formatting, top-level entity collection order and ZIP container
metadata differences. Entity identities and all nested content/order remain checked.
The SDK candidate is retained separately; the existing PAC package remains the
attested release path. Neither build authenticates to or deploys into a tenant.

## Explicit deployment targets and existing sessions

Both `pac-environment-check.ps1` and `pac-solution-deploy.ps1` require
`-EnvironmentUrl` with the exact HTTPS Dataverse root; a display label does not
select an environment. Use `-PacPath` for the already-qualified VS Code PAC
executable. The environment check performs only one explicit-target identity/read
and fails on a failed or empty response. Inspect that identity against the intended
account and tenant; a stored profile alone is not access proof.

Deployment reuses the existing session by default and never falls back to a legacy
NuGet cache or an ambient environment. Existing application authentication is used
only when its explicit federated or application credential mode is supplied;
this source support does not authorize new identities, consent or credentials.
Neither a successful read nor source CI grants deployment authority or proves
solution membership, runtime results or recovery.

## Power BI PPU qualification — 22 October 2026

Apply PPU only to an already-selected costing model/report requirement: qualify model comparison or scoped refresh before changing the workbook/report route. The outstanding federated sign-in and native solution inventory are separate gates; PPU neither renews that session nor grants the target role. Keep costing parity and UI acceptance evidence separate.

Follow the [shared PPU capability and permissions boundary](https://github.com/edithatogo/careops/blob/main/docs/development-and-delivery.md#power-bi-premium-per-user-current-qualification-boundary). The deployment operator's current PPU assignment is verified, but workspace mode, role/Build rights,
tenant settings, reader licensing and actual feature operation still require
exact-target evidence. XMLA and Power BI pipelines are qualification candidates;
Fabric Git/Copilot capacity and Power Automate/Word entitlement remain separate.
Do not infer support for report Export-to-file REST on PPU alone. Preserve current
source, native identities and recovery; no automatic workspace conversion,
settings change, new reporting dependency or cutover follows.

## Python helpers

Packaging comparison and inventory helpers use the qualified Python 3.15.1 profile.
For local checks, create `.venv-costing-ci` with
`uv venv --python 3.15.1 --no-project .venv-costing-ci`, then invoke its
`bin/python` (`Scripts/python.exe` on Windows) explicitly. For example:

```sh
.venv-costing-ci/bin/python -m unittest discover -s tests/ci -p test_solution_packages.py -v
```

Each CI helper job uses pinned setup-uv activation and actual interpreter
patch/prefix verification.
Existing environments are refused rather than cleared. Package identity,
SDK/PAC parity, inventory verification and signature gates remain mandatory;
these source checks do not deploy a solution or qualify substantive costing data.

The Node canary retains an absolute OS-Python receipt formatter so setup failures
remain reportable. This scoped compatibility exception records its actual
interpreter and performs no application build or test execution. Build-stage and
runtime evidence remain separate; an outcome receipt cannot establish runtime
qualification.

## Licence

Project-owned code is licensed under [Apache-2.0](LICENSE); retain [NOTICE](NOTICE)
with source distributions. Third-party software and external source materials
retain their own licences and attribution. This does not grant redistribution
rights to the private workbooks, documents, data or operational history excluded
from this public source.
