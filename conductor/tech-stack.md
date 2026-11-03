# Technology stack

- Ordinary source modules where explicitly migrated (Incidents first), with Git submodules/catalogue for remaining independently versioned components.
- PRIVATE GitHub parent hosting; independent child destinations retain their separately qualified visibility and publication policies. Enterprise deployment authority is private-profile supplied where configured. Source publication does not migrate enterprise/native systems.
- Qualified offline Presidio in checkout-local Python 3.15.1, with locked dependencies and packaged English model; installed managed pre-push guards preserve Gitleaks and exact document approvals. Same worker passed PR240 privacy CI; source merge and broader repository/upload coverage remain open in the [privacy continuation](tracks/suite_ci_delivery_20261018/privacy-rollout-20261103.md).
- GitHub Actions for continuity-host validation and permitted automation.
- Credentialing production target: full Dataverse in an approved dedicated Managed Environment; model-driven Power Apps, solution-aware Power Automate, Entra identity and controlled SharePoint evidence libraries.
- Native Dataverse backup plus separately governed SharePoint recovery; no personal OneDrive or editable Lists mirror as database backup.
- Copilot Studio/AI Builder as optional bounded assistance, never decision authority or a required core dependency.
- Each core module independently installable; cross-module adapters are optional solution packages. Shared environments do not create fault isolation.
- SQLite credentialing persistence is synthetic test-only, not a production option. Qualify real Dataverse security/concurrency/recovery separately.
- Native Teams/Outlook notifications and Power BI where they remove work; neither replaces the authoritative case or decision record.
- Power BI and pm4py for authorised de-identified or synthetic analytical evidence.
- Power Automate Desktop only as a separately approved legacy-integration last resort.

See [native platform decision](../docs/credentialing/native-microsoft-platform.md),
[standalone contract](../docs/standalone-module-contract.md), and
[target manifest](../portfolio/native-credentialing-target.json).
