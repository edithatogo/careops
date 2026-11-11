---
name: careops-power-platform
description: Implement and qualify CareOps Workforce Power Apps, SharePoint Standard connector, Power Automate and optional Dataverse with Microsoft skills. For job-planning app work, prefer this router and its pinned upstream plugin installation instructions.
---
# CareOps Power Platform engineering

## Source of truth

Work in `modules/careops-workforce-app` for the operational medical job-planning app; Conductor lives in `modules/careops-workforce/conductor`. **Never move the job-planning app back under PPG.** Consult existing transaction/versioning contracts before changing behavior.

## Mandatory workflow

1. Check `docs/development/power-platform-agent-skills.md` for verified upstream sources, pinned audit commits and executable installation commands.
2. Install foundation `canvas-apps@power-platform-skills` before `powercat-canvas-apps@power-cat-skills`. For flow authoring install `power-automate@power-platform-skills`. Dataverse skills are **optional** and must not shift the baseline from SharePoint Standard to Dataverse without an approved architecture change.
3. Read the currently installed plugin skill and official Microsoft platform documentation rather than inferring unsupported Power Fx controls, connector action names or solution formats. Power CAT complements, not replaces, Canvas authoring.
4. Preserve non-premium / non-Copilot baseline: Canvas App + SharePoint (Standard connector) + standard cloud flows, least privilege, service-group separation and versioned policy authorities.
5. Write synthetic tests before changing behavior; validate Power Fx, flow definition, CAS/ETag, replay, unique keys, effective-dated rules, dual-role permissions, export ACLs and portal accessibility.
6. Never commit source drafts, individual clinician job plans, extracts, personal identifiers, tenant settings, connection tokens, confidential exports or non-fictional fixtures.
7. GitHub source/CI, actual Power Apps Studio authorship, imported solution, authenticated cloud execution and production acceptance are **separate evidence gates**. Report each truthfully; do not present a template or scaffold as an imported app.
8. For SharePoint REST conditional writes require exact `If-Match` and handle 412/429, retries and crash recovery; multi-list operations are not ACID.
9. Do not run upstream `curl | node` or third-party installation scripts without review. Pin third-party sources, review dependencies and store only safe configuration in Git.

## Recommended plugin routing

- Power Fx / Canvas and Studio work: Microsoft `canvas-apps` (requires .NET 10, Studio coauthoring/app opened). Power CAT `powercat-canvas-apps` is an extension.
- Standard SharePoint flow design, connection references, retry/recovery: Microsoft `power-automate`; optionally read the pinned Wals-pro Power Automate reference skills (third-party).
- Dataverse administrative/solution topics: Microsoft `dataverse`, optional and not a baseline runtime dependency.
- Production approvals, HR/IR delegated decision and employee records require tenant-side verified identities, adopted sources and audited operational permissions.

If an installed plugin isn't available, use the local source and tests, explicitly record the missing authoring connection and never fabricate a native import receipt.
