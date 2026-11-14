# CareOps Workforce — medical job planning (offline source bundle)

**Status: local source prototype, NOT an importable or published Power Platform application.**

This bundle extends the SharePoint conditional-write protocol with job-plan calculation tests, a four-stage review transition engine, nine Power Apps UI screen *specifications*, ten workflow-definition *scaffolds*, a role/permission model and a deterministic synthetic local lifecycle demonstration. No confidential draft work instructions, practitioner schedules or staff IDs are present.

## Offline tests

```bash
PYTHONPATH=.:sharepoint python -m unittest discover -s tests -v
PYTHONPATH=.:sharepoint python -m unittest discover -s sharepoint/tests -v
PYTHONPATH=.:sharepoint python tools/demo.py
python tools/qualify.py
```

## Non-premium system design

SharePoint Standard connector, indexed unique-key lists and a restricted document library; role-controlled Canvas UI; solution-aware Power Automate cloud flows; standard M365 user/Outlook/Teams connectors as approved. The `sharepoint` Python adapter specifies SharePoint REST ETag compare-and-swap with a persistent local SQLite test double. It is not a SharePoint-hosted Python service. An authorised flow must reconstruct these operations using `Send an HTTP request to SharePoint` and resolve actor identity from an authenticated source; never trust caller-supplied approver identity.

## What is ready for a maker

- `canvas/Src/*.pa.yaml` — **editable review specifications only**, not a valid `.msapp` or a Studio-originated YAML serialization. The current Microsoft `pa.yaml` format is not a direct standalone import mechanism. Recreate or incorporate the controls into an authorised Canvas App in Studio, then let Git Integration export authoritative source.
- `flows/*.workflow.json` — syntactically valid WDL skeletons with **inert Compose steps** and `binding-required` markers. They are explicit implementation checklists, not functional or deployable approval flows. Do not enable them as live flows.
- `domain.py`, `sharepoint/flow_state.py` — independently testable business/workflow rules with synthetic employment rules; no live industrial-policy authority inferred.
- `sharepoint/sharepoint_adapter.py` — reference commit protocol + live REST transport adapter; not deployable Python runtime.
- `deploy/` — source installation guidance and provisioning requirements.

**Honest limit:** generating a legitimate managed/unmanaged solution ZIP requires a Studio-authoritative app, flows, connection references, environment-variable values and actual component IDs from an authorised Power Platform development environment. The repo and package do not fabricate these. Nor is list security achievable simply by hiding controls on a screen. Test the ACLs at the actual SharePoint URL and item/library endpoints.

No production use until CHHHS approves the governing work instruction/industrial interpretation, delegated authority matrix, identity/permissions, records retention, tenant DLP/licensing, and a clean native import+failure test. Never put confidential documents or clinician plans into Git, logs or CI artifacts.

## Offline implementation increment — 11 November 2026

`workflow_runtime.py` is an executable, **locally transactional SQLite simulator** for the
entire four-gate review route. It has effective-dated practitioner/approver/clinical
leadership/medical-workforce role grants; strict no-self-approval; immutable submitted
candidate JSON; deterministic SHA-256; idempotent operation IDs persisted across
process restarts; explicit return/reject; future-effective activation; historical
version indexes; rule-edition review obligations; human no-change attestation; and
role-scoped practitioner/approver dashboard projections.

`workflow_runtime.py` is deliberately **not** the production SharePoint store: it
uses SQLite `BEGIN IMMEDIATE` to provide a serialisable offline oracle. Live
SharePoint must use the separately specified compensating operation/ETag saga,
a trusted identity and delegation resolver, source-approved industrial rules,
real ACLs, and native solution-aware Power Automate flows. No user-supplied CST
rate or synthetic actor grants establish legal compliance in production.

Synthetic tests include concurrent duplicate and competing submissions, replay
across restart, stale generations, time-bound roles, calendar month boundaries,
effective-dated policy editions, altered requests sharing operation IDs, confidential
history access, and final activation. The local full lifecycle demonstration is
`python tools/demo_runtime.py`.

To run every available offline check:

```bash
bash tools/check_all.sh
```

To build a **source archive, not a Power Platform solution ZIP**:

```bash
python tools/build_release.py /mnt/data/CHHHS_Workforce_Offline_Source_v0.4.zip
```

The archive manifest records SHA-256 for each source file and explicitly declares
native Power Platform import and tenant qualification *unverified*.

## Agent skills and tenant gap

The repository agent plugin setup is described in
`../../docs/development/power-platform-agent-skills.md` when copied into the full
CareOps monorepo. GitHub/Copilot/Claude plugin settings do not install plugins in
ChatGPT. Use the Dataverse skills already accessible in ChatGPT only for relevant
solution/Dataverse work; the baseline remains standard SharePoint and Power Automate.

**Remaining locally feasible:** full native Power Fx rendering requires authoritative
Studio-origin app source; unsupported `.pa.yaml` must be tested in Studio before a
real `.msapp` can be built. WDL scaffolds must be replaced by solution-aware flows
bound to actual SharePoint connector connections. Their source and tests can still
be iteratively authored offline, but not truly qualified without the tenant.

### SharePoint Standard connector action prototype (source-only)

`flows/blueprints/sharepoint-cas-action-pair.json` contains concrete connector
`HttpRequest` action mappings for REST GET and ETag-conditional `MERGE` on
`JP_PlanHeads` (`shared_sharepointonline`, standard SharePoint connector). This
replaces neither the ten disabled flow specifications nor the permissioned
multi-list compensation workflow. It is an *unbound action template* without
connection references, tenant-specific list IDs, or an authenticated server-side
actor resolver. Do not enable it as an approval writer in production.

The local 54-test suite includes native-action shape/ETag checks, parallel
submission conflicts, review-rule migration boundaries, history access and
four-stage decisions. The **full Microsoft Power Platform/Power CAT plugin
catalogues** are registered separately in the CareOps repository's agent
settings; no ChatGPT installation of Canvas/Power Automate authoring is claimed.

## Native read-only flow candidates and role-safe Canvas specs (12 Nov 2026)

Three additional [native WDL monitoring candidates](flows/native-candidates/README.md) contain concrete SharePoint Standard `HttpRequest` GET actions for operation-status, due-obligation and plan-head connectivity monitoring. They are **separate** from the ten disabled privileged flow scaffolds and are **not imported or operational**; first-page count limits, DLP, connection mapping, schedules and list permissions require tenant qualification.

The `canvas/Src/` files remain **review-only specifications**, not Studio-originated import-ready `.pa.yaml`. Home navigation now defaults role hints to false, and the draft-save button explicitly discloses that persistence is unbound. A trusted role projection and server-side authorisation, not Power Apps visibility or `User().Email`, must govern actual data access.

Run `python -m unittest discover -s tests -p 'test_native_flow_candidates.py' -v` and `python -m unittest discover -s tests -p 'test_canvas_role_hints.py' -v` for specific source checks, or `bash tools/check_all.sh` after installing PyYAML for the complete local bundle. Committed tests have not yet obtained a passing exact-head GitHub Actions run. Source checks are not Studio validation, functional cloud execution or a solution import receipt.
