# Local analytics source

The generator accepts a full register packet or a frozen initiative projection.
It builds an initiative dimension and snapshot, event, decision, observation and
adoption facts, with five relationships and seven measures. Provided source
arrays derive counts per initiative. Missing source arrays remain unknown.

The PBIR report includes Overview and Scorecard pages. The RDL uses an MSOLAP
data source with explicit endpoint/catalog parameters, a DAX dataset and a
repeating tablix. Its period parameter labels the selected frozen snapshot.
Live period filtering and refresh binding require their own deployment design.
Each Fabric item has its own Base64 definition payload and release-index entry.

Generate local artifacts from the CareOps checkout root:

```sh
.venv-careops-privacy-hooks/bin/python modules/careops-improvement/tools/build_analytics.py modules/careops-improvement/examples/packet.json modules/careops-improvement/.local/analytics
```

For schema validation, create an isolated Python 3.15.1 environment and use the
hash-locked validation dependencies. Schema copies are cached privately, with
upstream URLs and exact digests in schema-sources.json.

```sh
uv venv --python .venv-careops-privacy-hooks/bin/python modules/careops-improvement/.local/validation/venv
modules/careops-improvement/.local/validation/venv/bin/python --version
uv pip install --python modules/careops-improvement/.local/validation/venv/bin/python --require-hashes -r modules/careops-improvement/platform/analytics/validation-requirements.lock
.venv-careops-privacy-hooks/bin/python modules/careops-improvement/tools/cache_schemas.py
modules/careops-improvement/.local/validation/venv/bin/python portfolio-scripts/run_tests.py --runner unittest --mode focused --tests-root modules/careops-improvement/tools test_analytics.py
```

Local evidence includes the metadata/page/report JSON schema checks, Microsoft
RDL XSD validation, model deserialization through Microsoft Tabular Object Model,
and payload byte round trips. This does not evaluate DAX or M expressions on an
Analysis Services engine. Native rendering, permissions, refresh and RDL query
execution remain unverified.

Source format references are maintained by Microsoft.

- https://learn.microsoft.com/power-bi/developer/projects/projects-dataset
- https://learn.microsoft.com/rest/api/fabric/articles/item-management/definitions/report-definition
- https://learn.microsoft.com/rest/api/fabric/articles/item-management/definitions/paginatedreport-definition
- https://github.com/microsoft/RdlMigration
