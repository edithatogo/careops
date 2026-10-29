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

## Power Platform authoring assurance — 30 October 2026

Identify authoritative source and its generator, inspect the relevant schema and
accepted connector example, edit parsed JSON, run focused validation, review the
semantic delta, then pack affected solution releases. Preserve tested generators;
structural changes use parsed objects regardless of line count. Never replace a
working flow with guessed connector fields. Preserve unknown properties.

Use the installed qualified PAC/CLI route and already-exposed Power Platform MCP
tools. Tool visibility and local help do not qualify native permissions. Retain
workload identity pins, guarded M365 entry points and authentication ownership.
Use native UI only for a specific missing capability, rendering or human login.

The offline power-automate-profile.json is a project-owned structural profile,
with the source WDL URL/hash and explicit Power Automate extension limits. It is
not a full expression compiler. Reports distinguish pass/fail/unverified/
not_applicable and never imply native deployment readiness. Preserve exact
connection references; parameter names alone do not prove environment variables.

Keep native inputs, component maps and pack outputs private. Public maps use
sanitized sources only. Read relevant dependency XML; ignore-file conventions are
search hints, not confidentiality controls. Sync an active Canvas authoring
session before local edits and use its supported current source route, not the
retired experimental Canvas unpack format.

Do not add blanket pack/check runs to every edit. Pack affected solution releases
and compare unpacked source; cloud Solution Checker is a separate authorized
operation. Keep output/replay/recovery evidence separate from all local checks.
