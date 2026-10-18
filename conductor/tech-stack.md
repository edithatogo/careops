# Technology stack

- Ordinary source modules where explicitly migrated (Incidents first), with Git submodules/catalogue for remaining independently versioned components.
- Public GitHub source hosting; enterprise deployment authority is private-profile supplied where configured. Source publication does not migrate enterprise/native systems.
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
