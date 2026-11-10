# Preliminary source-publication sensitivity assessment

11 November 2026. **Recommendation: keep the CareOps repository private until the explicit publication gates below are verified.** No visibility settings or historic branches were changed during this review.

## Reviewed evidence

- Current repository API reports `visibility=private`; `main` is a source-composition repository with thousands of tracked source and document files and optional pinned submodule references.
- `PUBLIC_SOURCE_FILES.json` and `portfolio-scripts/validate_public_source.py` implement a reviewed, strict tracked-file list, reject mismatches, inappropriate symlinks/binaries and selected private-location/account patterns. This is a valuable publishing control but is **not a universal content, document-metadata, Git-history or issue/PR audit**.
- `.careops-security/privacy-review-20261028.md` records previously remediated local path and account breadcrumbs across component sources, reviewed binary exceptions and outstanding private-repository qualification. Do not assume old audited submodule versions or archived histories match current source.
- Current source contains organisationally specific deployment-profile references, internal-system descriptions and substantial native architecture/operating instructions. The fact that no raw clinical record is intended in Git does not prove all operational metadata is suitable for open publication.
- GitHub issue/PR descriptions, comments, check artifacts, workflow logs, releases, tags, branch history and commit author metadata would be exposed by changing visibility; a source-file allowlist does not review them. This repository has a long history of PRs and issues and unqualified private-host runs.
- Optional pinned submodules have independent visibility and their own history/licence/privacy boundaries. A public parent Gitlink must not imply a public submodule or distribute its source.
- Third-party material, templates, binaries, datasets, office files and exported platform artifacts need individual redistribution/licence/provenance review. Apache-2.0 project code does not automatically license externally acquired artifacts.

## Required publication gates (all presently unverified)

1. Freeze a candidate exact SHA and enumerate **all reachable refs**, tags and Git objects (not only the working tree), plus Git LFS and release artifacts. Scan full history for secrets, account identifiers, private URLs, local paths, document metadata, sensitive personal/operational content and embedded Office/archive binaries. Include verified false-positive review.
2. Review GitHub issues, PR text/comments/reviews, workflow annotations/logs/artifacts, wiki/Projects and commit metadata for confidentiality, consent, identity and operational-security exposure. Exclude or sanitize them in a separate clean publication repository when necessary.
3. Verify each source/module/submodule licence, generated file, third-party template and redistribution permission. Verify no operational data, private bindings, credentials, live patient/personnel identifiers or authenticator cache is included.
4. Run actual source/privacy/secret/SAST gates at the frozen candidate revision and independently inspect parser/exclusion limits. Resolve fail-closed gaps; never reinterpret billing-blocked runs as passes.
5. Test public **fresh clone** without access to private dependencies, ensure standalone module installs and documentation do not expose private infrastructure, and verify public artifacts/receipts.
6. Have the source and records/IP owners approve the **specific sanitized publication candidate**. Do not equate repository administrator permission with information-owner or third-party redistribution rights.

## Safer publishing method

Prepare a **separate, history-free public source distribution** from an admitted exact SHA, retaining only reviewed project-owned files, licences and synthetic examples, with new CI and provenance. Keep the live private project, issues, operational docs, native bindings, old commits, and third-party archives private. A private repository is not unsafe merely because it remains private; public visibility should not be used to work around hosted CI billing or artifact-signing limitations.

## Assessment limit

This was a bounded review of policies, source inventories, representative files, source search patterns and PR/issue metadata. It was **not** a comprehensive byte-for-byte scan of all Git objects, issue comments, embedded binaries or old private submodule histories. No specific credential or patient-data disclosure is established by this review. Do not assert a publication certificate.
