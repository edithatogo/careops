# Offline build qualification and remaining work — 11 November 2026

**Scope:** CHHHS medical workforce job planning. Confidential policy draft and individual clinician plans are not repository material.

## Verified offline deliverable (conversation source artifact, not a GitHub source commit)

`CHHHS_Workforce_Offline_Source_v0.4.zip` — SHA-256
`887a2f0f2f02dc1f36de166d806c2a35f5a40ed3b51b7d8ae379240efe1f2097`;
43 source files including content-digested manifest. Local Python test commands:

```sh
cd careops-workforce-app-local
PYTHONPATH=.:sharepoint python -m unittest discover -s tests -q
PYTHONPATH=.:sharepoint python -m unittest discover -s sharepoint/tests -q
python tools/qualify.py
python tools/demo_runtime.py
python tools/build_release.py /mnt/data/CHHHS_Workforce_Offline_Source_v0.4.zip
```

**Results in the current local container:** 25 application/domain/orchestration tests passed; 25 SharePoint adapter/flow state tests passed; static source audit passed; full synthetic lifecycle demonstration passed; ZIP integrity and SHA-256 manifest verified.

## Newly implemented locally

- Offline `workflow_runtime.py`: SQLite `BEGIN IMMEDIATE` transactional reference oracle for separate clinician and approver identities, 4-stage consultation/clinical review/HR-IR/delegated sign-off, restricted user/approver dashboard projections, invalid-role/self-approval rejection, versioned due/review obligations, human no-change attestation, return/reject, future-dated activation and immutable submitted snapshots.
- True restart-persistent idempotent submissions/decisions and deterministic synthetic parallel duplicate/competing submission tests. Time-bound delegation and review-edition temporal tests.
- Fail-closed **reference-only** contractual-hour and CST arithmetic on user-provided source references: these are not authoritative policy/industrial rule verification. No live clinician files, staff identifiers or production data.
- `tools/check_all.sh`, `tools/demo_runtime.py`, `tools/build_release.py`: repeatable offline tests, simulation and source-only archive with SHA-256 inventory.
- Existing: 9 authoring **screen specifications**, 10 WDL **disabled placeholders**, SharePoint Standard connector REST contract, four-stage source transition module, and proposed SharePoint list provisioning. None is a published native Power Apps solution.

**Evidence ceiling:** the expanded local implementation is in a generated source archive, not fully pushed into GitHub. The monorepo previously contained the SharePoint adapter and contracts; some local offline components have only this generated artifact. An additional source import/commit step remains open. No exact-head GitHub CI or Power Platform tenant deployment was qualified. Do not refer to this ZIP as an importable `.msapp` or a Power Platform solution ZIP.

## Roadmap remaining locally feasible

- [ ] Bring all 43 locally generated source files into the CareOps GitHub branch, preserving individual history and confidential file exclusion; run exact-head CI and review source-lock implications.
- [ ] Replace disabled `Compose` scaffolds with solution-aware connector actions and defensive Scope/Configure run-after; do not fake a native deployment.
- [ ] Produce maker-valid Power Fx/source from a **Studio-authored** app, after available authoring MCP/PAC access; current screen YAML files are review-only.
- [ ] Add actual controlled export rendering and version diff UI bindings, role-scoped data-source integration, workflow identity/delegation resolver, privacy-safe monitoring.
- [ ] Add policy authority/source adoption and HR/IR compliance checks, full multiweek/annualised activity and cross-site resource tests.
- [ ] Implement robust SharePoint ACL/records library provisioning with signed-off tenant identities, list threshold/index testing, ETag/429 and multi-worker interruption/retry qualification.

## Tenant-dependent gates

Authentic Power Apps Studio app and `.msapp` export/import; source-aware Power Automate flow connection references and solution ZIP; SharePoint list/record permission readback; DLP/licensing; approved CHHHS policy and delegation matrix; actual service-owned identities; retention and records legal-hold, tenant concurrency/scale and failover tests; approval and live pilot.

## Skill catalogue evidence

Microsoft's official `power-platform-skills` marketplace currently publishes **11** plugins; Microsoft Power CAT publishes **14** plugins. Both full catalogues are now declared in `.github/copilot/settings.json` and `.claude/settings.json`, and the opt-in developer bootstrap invokes installation for each. Host installation is **not** verified (no Copilot/Claude or PAC CLI available in the model container). Dataverse skills are already available in ChatGPT, but GitHub/Claude plugin marketplace entries are not ChatGPT plugins. Other exact Canvas/Power Automate plugin names were not discoverable in ChatGPT's plugin directory. The SkillEra IO source remains unidentified. Least privilege and safe activation still apply before using optional plugins.

## Local v0.5 continuation — supersedes v0.4 test count

- Generated `CHHHS_Workforce_Offline_Source_v0.5.zip`, a **source ZIP, not a Power Platform solution**, SHA-256 `5b6cc86868c78dd5ea1741e33ee4ae5498510dd96ee5c6170587bf1e28b1c1dc`. It includes 46 source files, a per-file SHA-256 manifest, a synthetic demo and controlled test/build commands.
- Local execution: **29 application/domain/contract tests passed + 25 SharePoint adapter/staged-review tests passed = 54 passed**, no failed/skipped tests. `tools/qualify.py` static audit and `tools/demo_runtime.py` full synthetic lifecycle passed. Generated-archive ZIP integrity verified.
- Added one unbound SharePoint Standard connector `HttpRequest` action-pair blueprint for GET and exact-ETag MERGE on `JP_PlanHeads`; its four contract tests enforce non-wildcard matching and no tenant/credential literals. **Blueprint not a deployed, signed or safe-to-enable flow.**
- The 20 physical-list development schema and nine Canvas screen files remain design/provisioning source; ten WDL files are explicitly inert action scaffolds pending Studio/FlowAgent deployment. The new offline SQLite reference runtime is source-committed to `modules/careops-workforce-app/workflow_runtime.py`; other 45 bundle files are **not yet all imported into GitHub**.
- Microsoft marketplace configs now declare 11 Power Platform plus 14 Power CAT plugins; actual GitHub Copilot/Claude host installation not verified. Dataverse skills are visible in this ChatGPT context; Canvas/Power Automate authoring plugins are not ChatGPT-connected.
- **Unresolved:** valid importable Canvas App/solution zip, native connector operations, secure authenticated principal resolution and all tenant-side permission/records/retention acceptance, HR/IR industrial authority, real performance and recovery qualification. Github Actions still has no successful exact-head run; do not merge on this evidence alone.
