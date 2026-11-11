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


## Additional source implementation — 11 November 2026

Three small, separately testable **read-only overlays** were added to reuse the existing accreditation graph and evidence identity rather than creating parallel policy or assessment registers.

1. `scripts/ppg_obligation_application.py` classifies source kind and **human-reviewed candidate normative force** by exact framework edition and capture, and records time-bounded local policy adoption by existing EvidenceVersionKey/ScopeKey and human DecisionRef. It rejects out-of-context profiles, incompatible guideline/mandate claims, missing review provenance, expired/overlapping adoptions, cross-scope associations and future-dated decisions. It never determines legal applicability or assigns an accreditation rating.
2. `scripts/ppg_evidence_currency.py` compares fictional, exact-version source-capture receipts with explicit observation and review-due dates. It reports review-due, within-review-window, due-date-unset and unknown, keeping `sourceBytesVerified=false` and `sourceAuthorityVerified=false`. A hash *assertion* without independently verified bytes does not upgrade the source.
3. `scripts/ppg_assurance_bundle.py` combines these with the original `ppg_assurance_coverage.py` under one graph digest, ReviewContextKey, ScopeKey, date and requirement-kind selection. It emits sorted **candidate-only** review cues rather than issuing tasks, changing policy, inferring compliance or making an external accreditation decision. Its create-only CLI writes private mode 0600 where supported and refuses prior output replacement.

Additional synthetic test files `test_obligation_application.py` (11 methods), `test_evidence_currency_projection.py` (9 methods) and `test_assurance_bundle.py` (6 methods) were authored in GitHub. Existing tests remain intact. All source functions delegate fundamental graph validation to `ppg_accreditation_contract.validate_graph`.

**Qualification:** these are committed source/test contracts, not a verified Python 3.15.1 run or current-head hosted CI. Do not close PA-00.02/04, PA-01.04, PA-02.04/05 or PA-03.02 until their complete canonical tests and required owner/native evidence pass. Source-side implementation here is partial and doesn't replace existing edition/approval producers. No real records/standards text, notification, tenant write, deployment or provider attestation occurred.

Focused runner after setting the repository-local Python 3.15.1:
```sh
.venv/bin/python scripts/run_portable_tests.py --python-only test_obligation_application test_evidence_currency_projection test_assurance_bundle test_assurance_coverage_projection
```
