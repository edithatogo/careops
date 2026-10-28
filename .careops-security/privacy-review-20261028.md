# CareOps privacy review — 28 October 2026

Status readback: 2026-10-28T13:26:00+00:00. Scope: all13 CareOps-named repositories,12 active and1 archived. Encryption is excluded.

## Result and remaining gates

All8 public repositories have the reviewed source fixes and expanded privacy guard merged through their protected checks. The5 private repositories have concrete draft changes. Private current default branches are **not claimed remediated**: hosted execution is refused by account billing/spending limits, and archived Incidents retains its archived state and protected merge requirement. No protection was disabled or bypassed.

No confirmed patient-record disclosure or live service credential was identified in the reviewed source. This is a bounded source/content assessment, not an anonymity, privacy-compliance or publication certificate. Existing private native target bindings remain private and unchanged.

The private CareOps parent retains older exact module pins. These were inspected rather than assumed to equal child main: selected Process/RIMS/Sim views still contain workstation breadcrumbs; selected Finance/Decisions views also retain older Windows breadcrumbs. Pin promotion remains under existing source owners and suite qualification. Upstream/third-party repositories are not cleared as independent projects by this13-repository review.

## Genuine current-source findings

- **Process:** two public documents exposed a home/mount or local authentication-profile location. Replaced with portable/private inputs. The documented private-profile example now refuses an absent/missing directory before changing the CLI profile selection; fictional PowerShell checks prove prior selection is preserved on refusal. No login/native request.
- **RIMS:** two public planning documents exposed local mount links. Replaced with portable source links or private-workspace placeholders.
- **Sim:** redacted maintainer prefixes in238 text files and4 compressed evidence copies; removed2 old local advisory lease tokens.133 binary approvals bind exact reviewed hashes. The derivative-copy manifest preserves original/current file and changed-member digests. Historical SHA256SUMS refer to originals, not edited copies; redaction is not new execution proof. Originals are retained privately and history is untouched.
- **Finance/Decisions:** removed Windows workstation breadcrumbs from Finance documentation (private/public) and three Decisions documents per edition. Both Decisions sample packs use a Secretariat role in place of one incidental first name; their declared synthetic provenance is retained.
- **Private Costing:** removed two account-address breadcrumbs and two Windows source-path breadcrumbs. Two external XLSM originals contained editor/saved-directory metadata and additional third-party paths in VBA/cell strings. Removed them from the current candidate tree and retained unchanged originals under the ignored private reference directory and private review originals, with SHA256 identities. No active script/workflow depends on their former root paths. Extracted analysis and attribution are preserved; no compiled VBA rewrite or public-dataset approval.
- **Private Decisions:** removed six embedded account-address literals. The settings tool requires the existing approved identity through a private input, and refuses absent/disconnected approved connections rather than selecting another account. Isolated AST-based PowerShell tests execute only the pure selector, never the native-reading script body.
- **Archived Incidents:** prepared removal of three Windows breadcrumbs, including the Power BI source parameter default. Its original private parameter is preserved; no deployed report/model/refresh was changed. Corrected a historical claim that hashing alone proves anonymity. Existing source-boundary and model-structure checks pass locally. The repo was temporarily reopened to create a draft source PR, then independently verified private and archived again.

## False positives and exact review records

The original unfiltered current-snapshot Gitleaks pass produced107 occurrences:105 benign identifier/digest/prose cases and2 unnecessary historical local capability fields that were redacted. These are occurrences, not unique secrets or people. The machine-readable false-positive ledger contains paths, original lines, full blob hashes and reasons, with matched values omitted.

- **Decisions,42 per copy:** terms-of-reference, meeting and relational record keys. Seed packs declare synthetic records, use role mailboxes on example.invalid and placeholder integrations. Reviewed decisions/minutes/actions identify themselves as demonstration material.
- **PPG:** two deterministic identity-resolution example digests. Its negative content detector contains regex control text, not an actual workstation location; the existing exact control-source hash exception is retained.
- **Process:** four alerts match retention/disposal prose. The workflow diagram is labelled synthetic, visually reviewed, and has no text/EXIF PNG metadata; chunk CRCs validate.
- **RIMS:** synthetic canonical-key digests and crosswalk relationship labels. Its filesystem detector regex is control code, not a personal path.
- **CareOps:** the isolated-writer fixture asset label is a test identifier, not service authentication.
- **Sim:** source/API hashes and synthetic case labels are not credentials. Two local lease values were removed rather than ignored. Six hosted-runner-only path artifacts describe disposable CI, not the maintainer workstation.
- **External documents:** the generated Costing dictionary and two UI source archives were inspected offline. The archived Incidents DOCX is a blank external publisher template; legitimate creator/copyright provenance remains. Separate rights/private status are not publication approval.

The closing full-index audit has11 strict review flags:6 hosted-runner text artifacts,1 detector regex,1 synthetic diagram and3 private document/archive files. Every exact hash matches the manual/deep review. The reviewed-flags ledger records the reason; no flag remains unclassified. These indicators remain visible in strict full audits instead of becoming global path/rule exceptions. Future byte changes require review.

Private CI accepts only exact immutable historical Gitleaks fingerprints:1 CareOps fixture label and42 Decisions record-label occurrences. Complete-history scans pass with those reviewed inputs. Identical source bytes in fresh temporary-Git commits are rejected (1 and40 findings respectively), demonstrating that new commits are not exempt. Staged scanning remains unfiltered. Actionlint1.7.12 and Zizmor1.31.1 passed the changed workflows.

## Verification

- Actual repo-local Python3.15.1:13 focused privacy tests in each of12 active repositories. Independent Windows review passed37 probes, including spaced names, bare/quoted roots, legacy profile folders and JSON escaping.
- Installed the corrected guard atomically into21 existing shared hook stores, retaining prior code backups and installation journals.18 installer/fallback/guard tests pass. All63 real pre-commit runs pass; all63 indexes and HEADs stayed unchanged during the run. 62 runs had no staged files; staged success alone is not dataset clearance.
- Independent logical decoding validated120 standalone Arrow/Parquet files (744 rows) plus726 archived files (5,865 rows): all columns/schema metadata, no privacy-pattern hits or decode failures. Existing qualified Python3.15.1/PyArrow26.0.0 was reused.
- PowerShell contracts/connection refusal cases, RIMS source/docs checks, Process strict Ruff, Sim context/task checks, staged Gitleaks and whitespace checks pass locally where affected. All required current-head public hosted checks passed before merge. Private refusal is not executed test success/failure.
- An unoptimised Sim all-files CLI attempt timed out and is not counted as a pass. A complete synchronous index-blob audit using the unchanged actual findings function completed for all12 active candidates; its11 review indicators were classified by exact hashes. No source/index/native binding was changed by the audit.
- No new library was installed or added. Existing Gitleaks, standard-library ZIP/XML/tar tooling, PowerShell and the qualified PyArrow reader were sufficient.

## Remediation PR readback

| Repository | PR | State | Source commit / protected merge |
| --- | --- | --- | --- |
| careops | [PR 219](https://github.com/edithatogo/careops/pull/219) | OPEN draft | `d096fadba3226813c6f33f30243314a97d835213` |
| careops-approve | [PR 96](https://github.com/edithatogo/careops-approve/pull/96) | MERGED | `e0668809d50023444f173aae5bed7c0a8e661af3` |
| careops-costing | [PR 20](https://github.com/edithatogo/careops-costing/pull/20) | OPEN draft | `7af9d522a24cf6cf6036e7d0aa526294968d2610` |
| careops-costing-public | [PR 21](https://github.com/edithatogo/careops-costing-public/pull/21) | MERGED | `5bbfd72b6577df0df956c5f313120118b3423924` |
| careops-decisions | [PR 56](https://github.com/edithatogo/careops-decisions/pull/56) | OPEN draft | `3ca0a84c3e217d16ac4b1919b5636d759746fc10` |
| careops-decisions-public | [PR 18](https://github.com/edithatogo/careops-decisions-public/pull/18) | MERGED | `723795182e557453edd98c6c70f0c69c36092b57` |
| careops-decisions-public | [PR 19](https://github.com/edithatogo/careops-decisions-public/pull/19) | MERGED | `97f354dfb3996022fa65fbd6371ba6419afaac73` |
| careops-finance | [PR 16](https://github.com/edithatogo/careops-finance/pull/16) | OPEN draft | `c033b872fe7f8dade02e3d571169cfec552b7200` |
| careops-finance-public | [PR 16](https://github.com/edithatogo/careops-finance-public/pull/16) | MERGED | `1a44d282c6d01d452d8edcb1717d7884e80f1986` |
| careops-incidents | [PR 18](https://github.com/edithatogo/careops-incidents/pull/18) | OPEN draft | `28a1692391c3c3feb9e69ff8d088e342ed8c9743` |
| careops-ppg | [PR 67](https://github.com/edithatogo/careops-ppg/pull/67) | MERGED | `18985c82127f28f873e81d665490709f9623188c` |
| careops-process | [PR 123](https://github.com/edithatogo/careops-process/pull/123) | MERGED | `e0ea1f7ce00159389345a410c69c8a57db8d6756` |
| careops-process | [PR 124](https://github.com/edithatogo/careops-process/pull/124) | MERGED | `e62b0afce856e70bbf78fecf73b1c972ca8aa4f2` |
| careops-process | [PR 125](https://github.com/edithatogo/careops-process/pull/125) | MERGED | `ada7f03f50eb20abe384a9f3da0b76eb3a3fe2f3` |
| careops-rims | [PR 37](https://github.com/edithatogo/careops-rims/pull/37) | MERGED | `f087e76346474a3a38324e5c318c005d7e6dff5e` |
| careops-rims | [PR 38](https://github.com/edithatogo/careops-rims/pull/38) | MERGED | `8164756f26a0a3388dfac5da0c507ec46b797118` |
| careops-sim | [PR 185](https://github.com/edithatogo/careops-sim/pull/185) | MERGED | `d65c94b9b655e67df8110f2db3bb173884c97ab8` |
| careops-sim | [PR 186](https://github.com/edithatogo/careops-sim/pull/186) | MERGED | `9e25ad0b8ff24b0d9c88f0043d2c7c7e66d7b304` |

The CareOps PR readback precedes the commit containing this report; Git supplies this report’s own immutable revision. No self-referential digest is implied.

## Exact original review snapshots

| Repository | Visibility | Original reviewed default head |
| --- | --- | --- |
| careops | PRIVATE | `7b28d9751f0b6b8ca86b052c2fd1c41450709167` |
| careops-approve | PUBLIC | `74433bf8a6b2b2cee53462dbaddc71aba8d0f8b4` |
| careops-costing | PRIVATE | `5a2fdfd7739fa349948506ab30762ecd459e21a1` |
| careops-costing-public | PUBLIC | `a6ced26dc164f88923dc79efdb656c295065d31d` |
| careops-decisions | PRIVATE | `f4e21fa0589497281ff43efad8f4885af9bcc8c9` |
| careops-decisions-public | PUBLIC | `a82d696896b00fe8b56c53a62871fd550dda57ef` |
| careops-finance | PRIVATE | `5fcdd09af6871d895f1adc245ab245357edafaf2` |
| careops-finance-public | PUBLIC | `801d02608b016e89b0ca385a6cb239e2ac6d25cd` |
| careops-incidents | PRIVATE | `78e297335a95728f13a8f84b9b20e4f523d1128f` |
| careops-ppg | PUBLIC | `6ffadeb27a4d9c1fd121ded70b705b0ff10d1155` |
| careops-process | PUBLIC | `c5e96e5dda566c62ab7207a9dac8a5285e75dd8b` |
| careops-rims | PUBLIC | `57a3a3af48493e13f6f79bc4b36849d465b12423` |
| careops-sim | PUBLIC | `a3c37075b1bda5499ba30102d3785fbbed08fe5b` |

PPG changed during review; its ten additional owner-guide files were separately reviewed at d7ec4da8695fe00aa0fd373e81d66ca9fcc84583. No actual account/clinical payload was identified. Closing default heads are retained in native readback and checked against the merged fixes.

## Git history — separate assessment

Fresh non-shallow clones fetched branch/tag history for all13 repositories. An explicit default-rule Gitleaks pass disabled inline/ignore-file waivers. Object-level passes inspected reachable blobs for personal home/mount paths, health-service addresses and quoted/unquoted numeric patient labels; the closing pass also checks Windows profiles. Its metadata-only per-object reports are retained privately. Pattern counts are not unique people or breaches.

Confirmed older source/workstation/account breadcrumbs remain in history; current cleanup does not erase earlier publication. Historical credential-pattern candidates reviewed here are fixture/record labels, relationships and source digests. The old local lease values remain historical. No live service credential is confirmed.

Independent Sim extension reviewed3,792 reachable objects after adding the redaction candidate:3,745 text and47 distinct binary identities. Six older research ZIP versions (183 XML/Markdown members) added no sensitive content; no additional Arrow/Parquet identities remained beyond the decoded fixtures.261 historical text blobs retain maintainer breadcrumbs. A local-only artifact candidate at7bd66a40dfe524336eae6773d3ff258bdd463f01 was independently verified as a source SHA256 matching the selected historical file, not a token. Absence from the fresh remote clone does not prove it was never published.

Earlier local-store scans cover21 stores,12 then-shallow, with104 repeated generic candidates across overlapping copies. Fresh full remote clones remove that earlier shallow limitation for fetched remote branch/tag history, not for unavailable/unreachable objects.

Excluded from complete-history claims: deleted/unreachable remote objects, hidden PR-only refs, external forks/clones, server caches, release assets and old hosted logs/artifacts. Historical external Office inputs are retained as originals; their whole historical binary contents are not certified anonymous. No history rewrite, force push, credential rotation, storage/encryption action or native deployment was performed.

Remaining implementation gates are protected private merges and owned/pinned consumer qualification. No user permission question is pending; account/archival execution limits are recorded rather than bypassed.
