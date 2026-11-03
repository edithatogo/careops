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

### Frozen monthly portfolio

Pass `--period YYYY-MM` to build_analytics.py with a complete frozen packet.
Supply the initiative roster and task inventory as they stood at the reporting
cutoff. Count events by effective time, decisions by decision time (submission
time for pending decisions), and observations by observation time in the UTC
calendar month. Undated facts cannot be assigned to the month. Missing benefit
values remain blank even when the observation itself is counted.

Registered initiatives counts distinct roster IDs. Adopted services counts
verified initiative/service pairs: repeated observations of one service on the
same initiative count once. A service adopting two different initiatives counts
twice. Zero verified adoptions means no affirmative evidence in the selected
observations. It does not imply a negative outcome. Verified spread coverage is
the number of initiatives with any verified adoption divided by the frozen
roster size. An empty denominator or unavailable adoption counts gives blank.
It is not a percentage of eligible services.

The model, PBIR and RDL use the same named measures. For offline HTML/CSV use
the generated frozen-projection.json (the same initiative rows used in the
model), with the matching period. A period build fixes the printed RDL label.

### Executive reporting

Overview shows the registered roster, tasks, recorded and pending decisions,
measured outcomes and verified initiative/service adoptions. Pending counts
pending and under-review records in the period selection. It is not an
all-time backlog. Outcome result displays the measure, value and unit for one
known result, a count for several, and Unknown when none are known.

Scorecard uses the same semantic model. Each indicator title names its owner
role, reporting period, denominator, illustrative target and preferred direction.
Activity coverage means roster initiatives with at least one task. Measured
outcome coverage counts numeric benefit observations (including zero) divided
by all benefit observations. Empty denominators yield blank. Targets and owner
roles are examples for design review.

Native dashboard tiles are a separate service step: after authorised publication
and verified model refresh, pin the selected Overview visuals to the intended
Power BI dashboard and verify the destination, tile values and viewer access.

The RDL defaults AsOfPeriod to the build month. Both its detail query and its
portfolio totals query filter the initiative dimension by the selected period.
Selecting an absent period yields no detail. The totals query uses the four
Scorecard measures at portfolio grain. The print layout allows flowing detail,
repeated headers and growing titles on landscape letter paper. The HTML pack
still builds separately. For native acceptance bind the report to its model,
export the fixture to PDF, compare the four totals, and inspect the empty and
multi-page exports for clipping, repeated headers and blank trailing pages.
