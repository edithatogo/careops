# Restricted-source handling — medical job planning

## Hard repository boundary

This module **must not track** original job-planning work instructions, personal staff plans, local PPG drafts, confidential historical comparators, their extracted text/tables/images, document metadata, staff identifiers, individual hours/rosters or raw Google Drive exports. These belong only in an approved access-controlled corporate or local reference store. No identifiable or reconstructable content may be used in public prompts, code comments, screenshots, source maps, test fixtures, issue bodies, CI artifacts, release ZIPs or commit history.

The module's `.gitignore` blocks office/PDF types and local restricted-reference folders, but ignore rules are **not a DLP guarantee** (tracked files and renamed content can still leak). Required fail-closed controls before merge: staged-file extension/path audit; content/identifier/PII scans with false-positive review; gitleaks; asset/binary inspection; PR/commit diff review; repository/history scan if leakage is suspected. Never place source hashes of individual personal files in an unrestricted public manifest where linkability could disclose workforce information.

Only commit **abstracted** process steps, class-neutral data contracts, business rule IDs requiring independently sourced authority, versioned taxonomy codes with generic descriptions, and fictional synthetic samples unrelated to any named clinician. Keep citation/source accessions in the approved restricted register (not GitHub), and use an opaque internal authority key at runtime only after access-controlled source verification.

## Design-only use

- Draft local work instruction: candidate policy/process requirements; authority **unapproved/unverified**.
- Individual clinical job-plan example: identifies needed schedule flexibility and exception categories, not a seed dataset.
- Historical comparators: confirm reusable design patterns, not governing Queensland industrial rules.
- Review of these records does **not** authorize seeding a Power App or SharePoint tenant with their personal data.
- Application data classification/retention, telemetry and accessibility remain controlled by CHHHS decisions.

## Remediation if discovered

Stop pushing and distributing; remove in the active PR; assess whether history rewrite, credential rotation, notification and private-security response are required with authorised owner. Do not assume a deletion commit alone removes data from Git history. Preserve an incident receipt in the approved restricted process, never paste the sensitive source back into a GitHub issue.
