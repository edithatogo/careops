# CareOps Incidents

Canonical development source now lives in `edithatogo/careops`, under
`modules/careops-incidents`. This is ordinary source, not a submodule.
The original repository preserves historical source and excluded material. It is
verified private and archived, following successful protected-PR integration. See the existing
[Conductor migration track](../../conductor/tracks/suite_incidents_migration_20261018/plan.md).

## Source and deployment boundary

The current Power BI project, report pages, semantic model, Power Query/DAX,
surveillance and deterministic concept-staging tools are retained. The upstream
MIT [licence](LICENSE) applies. [Provenance](SOURCE_PROVENANCE.json) records the
reviewed baseline, imported files and content hashes. Historical analysis scripts,
findings, account bindings, binary template, old governance/automation setup and
Git history remain in the private archive. They were not silently relicensed or
published. A private disposition inventory accounts for every baseline path.

No data or generated outputs are included. RootDataPath is deliberately blank:
configure it only in a private deployment/work copy with a governed `data` folder.
Set authorised expected counts in ValidationTargets there; unset targets report
`Not configured`, rather than passing against historical totals. Preserve model
lineage tags, report/page/visual identities and source schema. Existing period
defaults and provisional governance thresholds are design defaults, not approved
local policy. Standards mappings are inherited design scaffolding, not compliance
certification. Native refresh, rendering, member access, privacy suppression and
clinical review remain pending; fictional tests do not establish them.

## Standalone use

Copy this module directory alone to work on its source; no other module, parent
service or private Git credential is required. Python 3.11+ staging uses only the
standard library. PowerShell 7 runs the PBIP structure checker; interactive PBIP
operation additionally requires a supported Power BI Desktop installation.

From this module directory, supply explicit private paths and analysis dates:

```bash
python3 powerbi/incidents_dashboard/scripts/build_surveillance_outputs_v1_20260429.py --source /private/input.csv --output-dir /private/revision-001 --start 2040-01-01 --end 2040-03-31
python3 powerbi/incidents_dashboard/scripts/build_health_concept_outputs_v1_20260429.py --source /private/input.csv --output-dir /private/revision-001 --start 2040-01-01 --end 2040-03-31
```

The dates above are fictional examples. Inputs use the existing incident CSV
schema; staging needs `incident_date` and optional cleaned text/cohort fields.
Output names retain the model's expected filenames. Existing output files are
refused; select a new revision directory and keep prior outputs/human edits.
Staging aggregates do not enforce small-cell disclosure controls. Store generated
files privately; import them into a private deployment copy only after its own
qualification. Keep source selection, identity, business decisions and approval
outside document generation. For maintained reports evaluate SharePoint structured
document generation first, using maintained templates and authoritative inputs;
qualify output/access/recovery before replacing a working route. No circulation
or licensing/settings change follows from this source migration.

From the CareOps root, run:

```bash
python3 portfolio-scripts/qualify_incidents.py --receipt .local/incidents-qualification.json
```

That command checks reviewed source hashes, all PBIP issue arrays and disposable
fictional staging. Public CI performs it without any private repository checkout.

## Recovery

Revert the direct-source migration PR to restore the prior private gitlink and
parent metadata together; the original repository remains accessible to existing
authorised readers after archival. Unarchive only if private source maintenance
is explicitly selected again. Full private Git mirror, verified all-ref bundle,
metadata and path-disposition inventory are retained outside public source.
Source reversal does not restore or delete native resources or operational data.
