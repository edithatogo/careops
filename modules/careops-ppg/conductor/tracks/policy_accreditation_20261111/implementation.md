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


## Non-premium SharePoint schema source — 11 November 2026

An additive `config/assurance-sharepoint-registers-v1.json` defines **three source-only** standard SharePoint Lists: source-force reviews, local edition-adoption events and evidence review receipts. Their keys reference the existing PPG framework and evidence identities; they do not duplicate policy bodies, external source documents, accreditation decisions or existing standards register rows.

`scripts/ppg_assurance_sharepoint.py` validates source-only/non-premium/no-deployment flags, the exact `shared_sharepointonline` connector, unique/required primary keys, safe field names and types, reviewed choice vocabularies and exclusion of patient identifiers, raw source text, credentials and manufactured compliance/rating fields. It generates deterministic `schemaXml` field definitions, **without authenticating or provisioning** a SharePoint site. The source contract uses standard Text, Choice and DateTime columns and carries its own SHA-256 identity.

`tests/test_assurance_sharepoint_contract.py` adds ten synthetic checks for source shape, primitive types, choice vocabularies, privacy refusals, XML parsing, repeated identity, mandatory unique keys and intentional absence of premium functionality or accreditation decision fields.

**Native qualification remains open:** actual list identities, content types, access control, standard-connector service behaviour, conditional writes, versions, pagination, recovery and licence/permission rights require a separately qualified development environment. The source can be checked in GitHub without an active M365 tenant, but this is not an installed list or a newly authorised source of clinical decisions.


## Current-head CI-driven remediation and main reconciliation

Hosted GitHub Actions resumed real execution. A PPG candidate head ran **1,512 Python domain tests** on Python 3.15.1 but exposed **two failures and four errors**: four invalid-scope negative-test calls omitted their required `as_of`; the create-only CLI fixture passed a wrapper `{graph,package}` rather than the actual graph; and duplicate SharePoint list source records were rejected by a generic list-count precheck before the more specific duplicate-identity test. All three underlying test/validation defects were corrected. This is **not a claim of a passing full suite** until the revised exact head executes.

A portable-source job also rejected three organisation-specific literals in the README, design and source-candidate configuration. Rather than weakening the existing source guard, the jurisdictional directive access candidate was moved to `profiles/chhhs/ppg-reference-sources.example.json`, while the reusable PPG source retains generic public publisher candidates only. The portable-content and privacy jobs subsequently passed on the corrected intermediate head; they must be rechecked on the final head.

The branch was first reconciled against `main` `69734c2`, preserving concurrent Decisions/Clinical Hub work. After another owner merged RIMS PR #309 into `main` `6155519`, the PPG branch received a second **non-forced, two-parent merge commit** `5c7884e` retaining the merged RIMS Conductor/data/CI source. Its reviewed parent source inventory now includes **4,373** entries, of which 18 paths are newly introduced by this PPG programme.

The PPG XML field-source generator was changed to escaped string generation rather than importing an XML parser for output-only work; SharePoint choice vocabularies are checked against the executable adoption contract. No source-security exemption, privacy guard weakening, live tenant change, external accreditation submission, email or repository visibility mutation occurred.

**Acceptance boundary:** New Python/domain, package, privacy, source-security and parent CI jobs must all pass on the *current PR head*. Native SharePoint list provision, permissions, conditional updates, source capture, application evidence and college accreditation remain independently held. No Conductor track is archived or marked production-qualified.
