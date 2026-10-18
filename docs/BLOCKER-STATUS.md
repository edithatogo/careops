# CareOps blocker status

Verified: 2026-07-11

This file records only capability state and next actions. It contains no tenant
identifiers, credentials, flow IDs, connection IDs, or personal data.

## Resolved with current authority

- GitHub.com Projects are available and the CareOps portfolio, repository, and approval roadmap boards exist.
- The parent and approval repositories are synchronized to NSW Health GHE and the private GitHub mirror.
- Repository harnesses and portfolio validation pass.
- The approval blueprint now covers no-email acknowledgement, restricted visibility, 14-day EDMS escalation, cancellation, immutable assignment, and idempotent finalization.
- The removable Power Automate duplicates were removed; the remaining corrupted record is documented.

## Still blocked

### GHE Projects

The authenticated GHE token has `gist`, `read:org`, `repo`, and `workflow` scopes but not `project` or `read:project`. GHE Project creation and verification therefore cannot be performed by this account.

Required action: obtain a least-privilege token or account grant with the required Project scopes, then run the existing portfolio project synchronization script.

### GHE Advanced Security

The GHE repository API reports Dependabot security updates enabled, but secret scanning, non-provider pattern scanning, push protection, and validity checks disabled.

Required action: an organisation or repository administrator must confirm entitlement and enable the applicable controls. The repositories must not claim these controls are active until the API reports them enabled.

### Microsoft 365 tenant fit and live flow

Required action: a tenant owner must confirm Teams Approvals, Forms or an approved submission surface, standard connector licensing, DLP compatibility, SharePoint retention/audit, pilot data classification, and named workflow owners.

### Corrupted M+M flow

The maker portal cannot deserialize or delete the remaining corrupted record. Required action: the flow owner or Power Automate support must remove or repair it through an approved recovery/API path. Do not retry destructive deletion through the maker UI.

### Desktop/intranet execution

Required action: register an approved desktop machine or machine group and confirm the permitted unattended/attended execution boundary before any intranet action is implemented.

## Evidence boundary

Tenant screenshots, policy exports, support correspondence, tokens, run payloads,
and live data belong in the organisation-approved evidence location, not Git.
