# Specification: excluded Power Automate remediation

## Scope

- Recover useful intent from the corrupted overdue-escalation flow without
  trusting its definition.
- Replace invalid SharePoint and Teams parameters in cloned patterns using
  tenant-owned connection references.
- Preserve native Teams Approvals as the authoritative record while using
  adaptive cards only for email-free presentation.
- Reassess calendar and intranet automation only when they serve an approved
  decision and a valid machine/connection exists.
- Keep co-owner sharing disabled unless the environment permits a private,
  least-privilege configuration.

## Acceptance criteria

- No repair mutates the historical source flow.
- Replacements have explicit tests, rollback, no-email behavior, and owner-only
  visibility.
- Corrupted or unavailable source assets are represented by sanitized issues.
- Desktop/intranet work remains blocked until a machine is registered.
