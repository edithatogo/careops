# Innovation and Improvement Register

CareOps owns the module source in this directory. The register includes a portable local SQLite implementation, JSON packet import, CSV exports, printable reports and a deployment dry run. It is designed for independent solution packaging, versioning and deployment. Cross-module links use documented identifiers. Site bindings and operational evidence stay in private storage.

Run from the CareOps checkout root using the qualified repository-local Python 3.15.1 environment. The local tools use the standard library.

```sh
mkdir -p modules/careops-improvement/.local
PYTHONPATH=modules/careops-improvement/src .venv-careops-privacy-hooks/bin/python -m careops_improvement.cli modules/careops-improvement/.local/pilot.sqlite import modules/careops-improvement/examples/packet.json
PYTHONPATH=modules/careops-improvement/src .venv-careops-privacy-hooks/bin/python -m careops_improvement.cli modules/careops-improvement/.local/pilot.sqlite report > modules/careops-improvement/.local/projection.json
.venv-careops-privacy-hooks/bin/python modules/careops-improvement/tools/report_pack.py modules/careops-improvement/.local/projection.json modules/careops-improvement/.local/pack-001 --period 2026-11
.venv-careops-privacy-hooks/bin/python modules/careops-improvement/tools/bootstrap.py modules/careops-improvement/config/resources.json modules/careops-improvement/examples/source-inventory.json
```

Report directories are immutable revisions. Their summary, CSV and printable HTML share one frozen input. The import is transactional and preserves the last good register on failure. Real database files and generated reports belong in private storage.

Run focused checks through the suite entrypoint.

```sh
PYTHONPATH=modules/careops-improvement/src .venv-careops-privacy-hooks/bin/python portfolio-scripts/run_tests.py --runner unittest --mode focused --tests-root modules/careops-improvement/tests test_store.py
.venv-careops-privacy-hooks/bin/python portfolio-scripts/run_tests.py --runner unittest --mode focused --tests-root modules/careops-improvement/tools test_bootstrap.py test_report_pack.py
```

See the [data contract](docs/data-contract.md), [federation and reporting design](docs/federation-and-reporting.md), and [deployment design](docs/deployment-design.md). Native connector binding, SharePoint provisioning, solution packaging, BI deployment, access control and refresh outcomes require separately authorised platform work. Teams is the initial collaboration entry point. External adapters are future options.

[Proposed Conductor tracks](conductor/tracks.md)

## Local platform artifacts

The [platform source index](platform/README.md) records the source and validation
boundaries for SharePoint, Teams, Power Automate and analytics.

```sh
.venv-careops-privacy-hooks/bin/python modules/careops-improvement/tools/provisioning.py dry-run
.venv-careops-privacy-hooks/bin/python modules/careops-improvement/tools/build_flows.py
.venv-careops-privacy-hooks/bin/python modules/careops-improvement/tools/build_analytics.py modules/careops-improvement/examples/packet.json modules/careops-improvement/.local/analytics
modules/careops-improvement/tools/pack_solution.sh
```

Use a fresh analytics output directory for each frozen revision. The builder
writes item definitions locally. Real source inputs and outputs stay private.
