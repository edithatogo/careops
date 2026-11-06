# CareOps

CareOps is an organisation-neutral, modular suite for administrative and clinical-governance workflows. This repository contains shared delivery controls and the module source already admitted through the source-integration programme. Other selected modules remain exact-pinned submodules until their own integration tracks are completed.

**Source integration is not operational deployment.** Each capability retains its business authority, native service owner, deployment boundaries and acceptance requirements. Operational exports, patient or practitioner records, credentials, tenant bindings, private evidence and authoritative business records do not belong in this repository.

## Start here

| Task | Read first |
| --- | --- |
| Understand the capabilities and current source locations | [Module catalog](portfolio/module-catalog.md) and [source registry](portfolio/repos.json) |
| Select the next bounded implementation task | [Suite delivery queue](conductor/suite-delivery.md), [track registry](conductor/tracks.md) and [module profile](.careops/module.json) |
| Work as a coding agent | [Agent instructions](AGENTS.md), [development and delivery standards](docs/development-and-delivery.md) and the selected module's instructions |
| Run the smallest relevant tests | [Targeted testing](docs/targeted-testing.md); retain the full release gates |
| Build the new native SharePoint catalogue | [Catalogue track](conductor/tracks/ckan_catalogue_20261106/index.md) and [core build plan](docs/clinical-data-catalogue/sharepoint-native-build-plan.md) |
| Understand source, privacy and release checks | [CI delivery contract](docs/ci-delivery-contract.md), [hosting boundary](portfolio/host-capabilities.md) and [reviewed source inventory](PUBLIC_SOURCE_FILES.json) |

Use `portfolio/repos.json` for the intended source form, `.gitmodules` and the selected commit's Git tree for the actual checkout, and the module's own track for qualification evidence. A dated historical receipt is not a replacement for current source readback.

## Architecture

CareOps is consolidating reusable source into the parent repository without making the modules a single runtime. [Repository topology](#repository-topology) lists the integrated modules and the remaining optional pinned references explicitly; the registry, not a historical module count, controls current source selection.

Modules communicate through versioned contracts and stable, source-qualified identifiers, rather than a common operational database. Organisation-specific rules and private configuration stay in deployment profiles. A user can adopt one bounded capability without installing the entire family.

Each module keeps its supported build, licence/provenance, tests and deployment contract. Moving source into this repository does not authorise a tenant connection, activate an existing flow, transfer record ownership or lift a native write hold.

## The full system

| Module | Standalone purpose | Optional contribution |
| --- | --- | --- |
| `careops-approve` | Intake, checks, routing and human approval capture | Reviewed request/result handoffs with governance providers |
| `careops-decisions` | Governance bodies, recommendations, decisions and actions | Formal governance evidence for other capabilities |
| `clinical-hub-core` | Meeting preparation, papers, minutes and follow-up | Meeting evidence and actions; reconcile overlap with Decisions |
| `careops-ppg` | Policy/procedure/guideline preparation and lifecycle | Exact-version controlled-document references |
| `careops-rims` | Publication ingestion, attribution and reporting | Source-qualified publication references and approved outputs |
| `careops-process` | Minimised event/file ingestion and process analysis | Conformance, delay and rework analysis |
| `careops-incidents` | Governed safety analytics | Minimum-necessary aggregate signal references |
| `careops-costing` | Workload, capacity, cost and benefit calculations | Reproducible assumptions and aggregate results |
| `careops-finance` | Governed finance reporting and semantic models | Aggregate reporting and reusable ALM patterns |
| `careops-sim` | Independent Rust/Kairos simulation | Synthetic scenario/result interfaces; its own runtime |
| `careops-catalogue` (planned) | Native SharePoint dataset/resource discovery | Optional references to approved products; no new central runtime |

This is a capability map, not a statement that every module is deployed or interoperating in production. Clinical Hub and Decisions must retain one authoritative record for each meeting/decision concern. Analytics, simulation and AI are optional consumers, not prerequisites to ordinary administrative work.

## Carryover approach and priority

Follow the existing [suite queue](conductor/suite-delivery.md) and [module tracks](conductor/tracks.md). Use the current [topology table](#repository-topology) for source placement. Do not restart a completed migration or initialise an integrated directory as a submodule.

Further source admission must preserve attribution, history/recovery references, working runtimes, private operational ownership and exact qualification evidence. [The CI rollout matrix](portfolio/ci-rollout.json) distinguishes selected source/package receipts from remaining native checks. Repository access or source availability never grants permission to redistribute a child repository or private history.

**CGov remains separate.** The Legacy Migration and credentialing tracks, including N11 cutover, keep their own scope and authority. This catalogue/navigation work does not authorise a legacy-system replacement.

## Structured documents

Evaluate the existing structured-document route for agendas, meeting packs, policies, memos and reports before introducing another generator. Preserve source/template versions, included record identities, human edits, unresolved concerns and issued history. Verify actual output and recovery before replacing a working route.

Generation does not approve, issue or circulate a document. Product availability, licensing and tenant admission remain separate. Capability-specific exclusions still apply: the catalogue core has no premium or Copilot dependency.

## Organisation deployment profile (separate workstream)

The retained [deployment-profile example](profiles/chhhs/README.md) adapts generic capabilities without embedding organisational authority into reusable code. Its historical directory name is not a default tenant binding.

The [credentialing compatibility contract](portfolio/credentialing-mvp-compatibility.json) records participating sources and boundaries, not a deployment or business approval. Keep actual tenant identifiers, credentials and operational evidence in approved private locations.

## Delivery model

Deliver small, reversible increments: fictional-source validation, separately approved silent/limited use, and then an explicitly authorised operational release. Preserve existing owners and manual fallbacks; measure net benefit rather than treating automation counts as evidence of improvement.

AI must not make credentialing, scope, appeal, employment or other materially adverse human decisions. Deterministic checks and accountable approval remain controlling. The [feature radar](docs/feature-radar-2026.md) records candidates; announcements and previews do not establish entitlement or acceptance.

## Agent support

Read [AGENTS.md](AGENTS.md) and the selected module's instructions before changing files. Existing agents and skills live under `.github/agents/` and `.github/skills/`; the pinned upstream Conductor is a development dependency, not a second product runtime.

Reconcile the current branch, open work and source owner before selecting a task. Keep the public-source inventory explicit, dependencies pinned, tests focused during edits and complete at integration gates. Preserve native refusals, including `NATIVE_WRITE_QUALIFICATION_REQUIRED`; do not substitute another client to bypass a held operation.

Email-capable paths remain Off unless the explicit send-approval policy in `AGENTS.md` is satisfied. General implementation instructions do not approve delivery.

## Repository topology

The following source forms are reconciled against `portfolio/repos.json` and `.gitmodules` on 6 November 2026. Refresh those authorities before a later migration.

| Module | Path | Source form |
| --- | --- | --- |
| `careops-approve` | `careops-approve/` | Integrated source |
| `careops-process` | `modules/careops-process/` | Integrated source |
| `careops-ppg` | `modules/careops-ppg/` | Integrated source |
| `careops-incidents` | `modules/careops-incidents/` | Integrated source |
| `clinical-hub-core` | `modules/clinical-hub-core/` | Integrated source |
| `careops-finance` | `modules/careops-finance/` | Integrated source |
| `careops-costing` | `modules/careops-costing/` | Integrated source |
| `careops-decisions` | `modules/careops-decisions/` | Integrated source |
| `careops-rims` | `modules/careops-rims/` | Optional pinned submodule |
| `careops-sim` | `modules/careops-sim/` | Optional pinned submodule |

A normal parent checkout includes the integrated source. Do not use submodule commands for an integrated row. The catalogue remains a planned module; its design documents do not establish an implemented `modules/careops-catalogue/` directory.

Initialise only a selected, reviewed optional dependency; do not fetch the entire family by default:

```sh
# Choose only the module needed for the task.
git submodule update --init --checkout -- modules/careops-rims
git submodule update --init --checkout -- modules/careops-sim

# Development skills, only when required by the chosen agent.
git submodule update --init --checkout -- .agents/plugins/conductor
```

The explicit `--checkout` selects the committed gitlink despite the optional modules' `update = none` setting. Upstream updates require a reviewed pin change; do not replace this with `--remote` or a floating branch update. Module-specific runtimes and operational permissions remain independent.

## Licence

Project-owned source uses Apache-2.0. Preserve [LICENSE](LICENSE), [NOTICE](NOTICE), third-party notices and module provenance. Source consolidation does not relicense upstream dependencies, original documents, datasets or private evidence. Historical Incidents licensing and migration evidence remain in its [migration track](conductor/tracks/suite_incidents_migration_20261018/plan.md) and [source manifest](portfolio/incidents-source.json).

## Public-source boundary

The reviewed source boundary applies regardless of the hosting repository's current visibility. Private source history, business records, deployment bindings and native receipts stay outside this source-only tree.

`PUBLIC_SOURCE_FILES.json` lists admitted paths and reviewed gitlinks. File additions require inventory and content review; existing privacy/security checks remain mandatory. The [hosting boundary](portfolio/host-capabilities.md) explains which checks execute in public CI and which require separately authorised access. A passing source scan is not a guarantee about all confidential content, nor a native deployment approval.

## CI and security checks

The current [security workflow](.github/workflows/security.yml) uses the pinned shared source-security workflow, configuration fuzzing and source regressions, hash-lock/dependency checks, the Python/OpenGrep source-security route and a separate OSV dependency-vulnerability review. The current [privacy workflow](.github/workflows/privacy.yml) and [public-source workflow](.github/workflows/public-source.yml) retain their own gates. Older CodeQL/dependency-review receipts remain historical evidence, not instructions for today's workflow.

No scanner policy, required check, reviewed finding or branch protection is changed by this documentation reconciliation. Secret scanning and native settings require their own readback; source configuration alone cannot prove enforcement.

Use the exact `.python-version` in a repository-local environment. Do not replace an environment underneath a running job. Follow [targeted testing](docs/targeted-testing.md); for example, with an already qualified `.local/ci-env`:

```sh
.local/ci-env/bin/python --version
.local/ci-env/bin/python portfolio-scripts/run_tests.py --runner unittest --mode focused --tests-root portfolio-scripts/checks test_test_selection.py
```

That command checks the test-selection component only; it is not a full-suite result. During coherent integration/release, run all applicable parent/module/security gates and inspect the exact PR head. Billing refusals, missing prerequisites and skipped runs are not passing tests. Native access, recovery, rendering and operational acceptance require separate evidence.

The source-topology regressions in `portfolio-scripts/checks/test_integrated_module_source.py` compare current tables, delivery locations and checkout examples with the source registry and `.gitmodules`. They run in the existing parent source-regression suite; no child checkout, network request or native write is required.

## CI/CD qualification

The [suite CI/CD programme](conductor/tracks/suite_ci_delivery_20261018/index.md), [delivery contract](docs/ci-delivery-contract.md) and [rollout matrix](portfolio/ci-rollout.json) own qualification and release evidence. Canary results do not automatically promote a dependency, activate a workflow or qualify another runtime.

## Clinical Hub integrated source

Clinical Hub is maintained in [modules/clinical-hub-core](modules/clinical-hub-core/README.md). Its [migration record](modules/clinical-hub-core/MIGRATION.md) retains private continuity and provenance. Use its current module instructions; historical submodule directions do not apply to this integrated source.

## Executive correspondence

The Clinical Hub [correspondence capability](modules/clinical-hub-core/conductor/correspondence-operations.md) supports capture, human review and selected linked Basic Planner actions for generic CMO/EDMS offices. It uses standard connectors without requiring Copilot or an email-send dependency. Actual bindings and operational evidence remain private, and the repository-wide send-approval policy still applies.

## Process and Approve development

Process (`modules/careops-process/`) and Approve (`careops-approve/`) are ordinary maintained source here; predecessor repositories are recovery history, not current gitlinks. Their module-local instructions, exact runtime selection and standalone commands remain controlling. Root `process`, `process-package` and `approve*` workflows own their current delivery. Source migration did not complete their remaining native or signed-release qualification.
