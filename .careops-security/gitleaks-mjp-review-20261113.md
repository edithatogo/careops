# Gitleaks full-history finding triage — Medical Job Planning planning PR

**Reviewed 2026-11-13.** This review concerns only 16 artificial fields in a public, fictional example.

## Finding

An unmodified Gitleaks v8.30.1 full-history scan (`gitleaks git . --log-opts=--all`) reported **16 `generic-api-key` matches** at an original proposal commit:

- Commit: `7aa66ac8a3cf28a62d9fa3b93ce1d27a9c2b3b09`
- File: `conductor/tracks/medical_job_planning_20261113/contracts/fixtures/valid-messages.json`
- Git blob SHA: `e3f375f92493a396b817f1cc10fef32a34f6cc4e`
- Lines: 8, 25, 56, 73, 104, 121, 154, 171, 201, 218, 255, 272, 305, 322, 351, 368.

**Classification:** Eight values are artificial, explicitly fictional idempotency labels; eight are placeholder organisation scope identifiers. The corresponding values, original file and source records were inspected, not inferred from the scanner's rule name alone. All eight example message records are fictional, and no live credential or service token was identified in these *specific* matched values. This is not a general declaration that every historical ref or deployment is free of secrets.

## Correction and scan policy

1. Shorten the current synthetic fixture labels so the public examples are not mistaken for API credentials; preserve distinct idempotency and stable organisation-scope semantics in the test schema.
2. Replace **only the assistant-created draft planning branch's intermediate commit history**, using a branch-head force-with-lease from the verified current SHA, with a clean commit directly on the unchanged parent `main` tree. The original historic commit remains identified above for provenance; do **not** force-rewrite `main`, another developer's branch, or private enterprise records.
3. Do **not** add global Gitleaks rule, path or token allowlists. Keep `.careops-security/gitleaks-reviewed.ignore` unchanged from `main`, and preserve the existing `--log-opts=--all` and shared source-security scans without newly accepted false-positive fingerprints.
4. Keep the new diagnostics in the privacy workflow: on failure, display only sanitised rule/path/commit/line metadata. Do not display matched values, scanner full output or JSON reports.
5. Independently verify that the **final branch's reachable history** passes both Privacy protection's full-history Gitleaks and the shared reusable-source-security's unfiltered full-history Gitleaks. Full source, secret, CI and native/operational gates remain separate.

**Status:** The branch-history replacement and new-head hosted verification are pending until their exact SHA and checks are recorded. A branch-only cleanup is not an enterprise history rewrite, credential revocation or production assurance.

## Negative regression expectations

- A new unreviewed commit with an actual-looking credential-shaped test value must still be detected: unchanged full-history scanner, unchanged privacy rule configuration and original historical reviewed-ignore file.
- Missing/invalid scan report must not silently pass; the redacted diagnostic helper cannot suppress exit code 1.
- The public-source inventory includes the new source and test files, and no private scan report/artifact is committed.
- An unrelated OSV or other security finding is not waived simply because Gitleaks is green.
