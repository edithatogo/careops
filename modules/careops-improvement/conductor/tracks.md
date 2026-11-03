# Improvement register tracks

The five tracks have a locally tested baseline at `731a004`. The 34 tests cover register behavior, platform source and packaging. Governance decisions and tenant pilot checks remain open in the individual plans.

| Track | Local baseline |
| --- | --- |
| [IIR-01 · Governance and routing](tracks/IIR-01/index.md) | Separate registration from authority to commence. |
| [IIR-02 · Initiative identity and stewardship](tracks/IIR-02/index.md) | Preserve identity across source revisions and renames. |
| [IIR-03 · Departmental federation](tracks/IIR-03/index.md) | Import packets, reconcile revisions and retain the last successful import. |
| [IIR-04 · Evaluation and reporting](tracks/IIR-04/index.md) | Generate the semantic model, report definitions and printable output. |
| [IIR-05 · Solution lifecycle and pilot](tracks/IIR-05/index.md) | Generate provisioning previews and round-trip the solution scaffold. |

## Next CLI work, in priority order

| Order | Track | Deliverable and stopping point |
| --- | --- | --- |
| 1 | IIR-03 with IIR-02 | Map one fictional Excel table, Planner export and SharePoint list export into the existing packet importer. Five linked tasks count against one initiative. Replay and rename preserve its ID. A failed feed preserves the last good record and exposes its age. |
| 2 | IIR-05 | Compare list fields, library settings and a Teams tab against a supplied target inventory. Report missing and incompatible settings separately. With the expected inventory, a second preview proposes zero changes. |
| 3 | IIR-04 | Use one frozen reporting period to compare the model's expected measures with the scorecard and printable pack. One initiative with two adopting services gives one initiative and two adoptions. An absent outcome stays unknown. |
| 4 | IIR-05 | When verified workflow metadata and connection mappings are available, pack and unpack the stopped flows with PAC. Inspect the extracted workflow components and connection references. The existing scaffold round trip is the starting point. |

Use the existing importer, provisioning planner and reporting generators as entry points. The [PPG policy currency plan](../../careops-ppg/conductor/tracks/policy_currency/plan.md) keeps replay evidence and installation details private. Apply that pattern here using fictional fixtures in Git. The parallel research repository closed a bounded source qualification at `0cdb6765` and recorded workflow evidence separately from implementation at `ce9a2150` and `62d675c5`. For each tranche, record the source commit, exact CLI check, expected and observed result, and remaining native check. Reuse that result until its inputs change.

The federation and reporting work can run in separate worktrees once the fixture contract is fixed. One integrator updates the shared track records. Tenant deployment, flow activation and pilot acceptance require their own decisions. See the [platform acceptance scope](../platform/README.md) and [analytics checks](../platform/analytics/README.md).
