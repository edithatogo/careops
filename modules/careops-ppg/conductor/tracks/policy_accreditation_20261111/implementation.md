# Current bounded implementation evidence — 11 November 2026

Source scope: `modules/careops-ppg/scripts/ppg_assurance_coverage.py` and `tests/test_assurance_coverage_projection.py`, operating on existing `ppg_accreditation_contract.validate_graph`. This is a **read-only data projection**, with no new authoritative table or native client.

The projection enumerates explicitly selected requirement kinds and framework editions for one existing review context and scope. It reports no assessment, unknown applicability, nonoperative framework, proposed/unreviewed supporting mappings and explicitly recorded human review, while holding `accreditationStatus=null`, `sourceBytesVerified=false`, and `nativeWrites=0`. The result never converts policy presence into implementation or accreditation evidence, never transfers recognition through a crosswalk and never supplies a universal readiness score.

Test cases authored: missing vs unknown applicability; proposed mapping; reviewed mapping and human assessment; recorded non-applicability; draft edition exclusion; absent/wrong context and scope; duplicate assessment; crosswalk no-transfer; deterministic result without raw evidence text; invalid dates. Data uses the fictional second-example graph only.

**Executed checks:** Source retrieved and reconciled through GitHub; full Python 3.15.1 affected suite and GitHub Actions have **not** been run in this source-writing session. Native SharePoint/Dataverse/Fabric qualification and access to external original editions are explicitly false/unverified.

To qualify the code in a current 3.15.1 checkout:
```sh
.venv/bin/python scripts/run_portable_tests.py --python-only test_assurance_coverage_projection
.venv/bin/python scripts/run_portable_tests.py
.venv/bin/python scripts/check_portable_content.py
```
Run root parent source/privacy checks and inspect exact PR head before merge. No tenant operations, real policy content, email, source acquisition or accreditation submission is authorised here.

## Private result handling

The CLI now creates a **new** output using `O_CREAT|O_EXCL`, `O_NOFOLLOW` when supported and mode `0600`. It refuses existing output files and preserves prior review results instead of overwriting history. A synthetic subprocess test for private file mode and non-overwrite behaviour was added. Source-only tests are **authored but not executed on canonical Python 3.15.1** in this connected-GitHub session.
