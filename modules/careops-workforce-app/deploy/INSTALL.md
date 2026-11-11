# Controlled development deployment checklist

1. Provision authorised *development* SharePoint site, restricted identities and groups, records/retention settings, DLP. No real staff data in development.
2. On tenant with approved PnP.PowerShell app, run `provision-lists.ps1 -SiteUrl ... -ClientId ... -WhatIf` then remove `-WhatIf` after explicit administrator review. Set list and library ACL; list creation alone gives no confidentiality.
3. Review effective-dated medical job planning industrial rules and permissions with Medical Workforce/HR-IR; assign versioned authority and policy owners.
4. Create a Canvas App in a development Solution from Power Apps Studio; use included nine `.pa.yaml` screens as design specifications, **not direct-import source**. Export authoritative `.pa.yaml` via Power Platform Git Integration.
5. Author solution-aware Power Automate actions from the flow catalogue; replace each inert Compose placeholder with a real authenticated SharePoint REST action, ETag CAS, retry and checked permission/delegation enforcement. Disable all live flows until the integration test suite passes.
6. Configure connection references in flows, SharePoint data source environment variables, runtime connection ownership and deployment settings. Never embed tenant URL, list GUIDs, tokens or personal records in repository source.
7. Run Power Platform Solution Checker, import/unimport/rollback in a clean authorised development environment, and compare active plan under concurrent writes/replays. Verify historical documents and direct-list URL access cannot bypass role restrictions.
8. Export unmanaged development and managed promotion Solution ZIP through supported Microsoft Power Platform tooling. Do not build a faux ZIP manually.
9. Validate accessibility and clinician/approver workflow, HR-IR authority, records/legal-hold, privacy, support and rollback before pilot.

**No step above has been performed against a CHHHS tenant by this source bundle.**
