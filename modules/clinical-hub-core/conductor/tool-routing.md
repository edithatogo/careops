# Tool routing and access

| Work | Preferred route | Boundary |
|---|---|---|
| SharePoint records/views/files | Qualified M365 CLI | Exact account and target; conditional writes and uncertain-save reconciliation |
| Flow graph/bindings/run diagnosis | Qualified FlowAgent; retained supported CLI/API route | Compare complete saved graph/state and inspect output |
| Solution export/pack/import | PAC | Target-specific rights; no new environment or registration implied |
| Selected existing API operation | Qualified Azure CLI adapter | No new Azure service or credential transfer |
| Required sign-in/document inspection | BrowserOS Neo | Human password/MFA only when actually challenged |

Reuse successful operations from parallel projects as routing knowledge, not as
proof of permissions on a different target. Keep exact account/licence observations
private. An existing session or developer environment does not establish every
connector entitlement. Do not ask repeatedly for unchanged licence/access decisions.

PAC, M365 and Azure clients have separate auth stores. Preserve active sessions;
never reset shared authentication for routine discovery. One CLI invocation may
retry POSTs: use a qualified conditional/no-retry route where duplication matters.
Read back uncertain effects before another write. Browser sessions do not create
new permissions. Keep current working routes until a required replacement passes
its affected checks. Latest project dependencies are pinned; shared CLI upgrades
must not interrupt another operation.
