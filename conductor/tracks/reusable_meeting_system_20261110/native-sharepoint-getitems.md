# Native Standard SharePoint GetItems adapter — 11 November 2026

## Selected implementation

Source: \`modules/clinical-hub-core/scripts/sharepoint_decisions_flow.py\`.
Contract tests: \`modules/clinical-hub-core/tests/test_sharepoint_decisions_flow.py\`.

\`build(config)\` emits **a real Power Automate Workflow Definition Language source candidate**, with one manually triggered, Stopped flow, disabled \`ReadEnabled\` parameter, and an \`OpenApiConnection\` action using:

- API: \`/providers/Microsoft.PowerApps/apis/shared_sharepointonline\`
- Operation: **\`GetItems\`**, not generic HTTP
- Parameters: \`dataset\` (selected HTTPS SharePoint site), \`table\` (exact List GUID), \`view\` (selected view GUID), \`$orderby\` (\`ID asc\`)
- Native pagination: \`runtimeConfiguration.paginationPolicy.minimumItemCount\`, bounded to the config's maximum.
- One embedded **existing** SharePoint connection reference, never created by the compiler.

The source graph guards the disabled state, missing/empty result shape, exact pagination threshold, any reported continuation, missing required fields, missing ETag and nonpositive ID, then uses WDL \`Query\` and \`Select\` to produce a **review-only** metadata projection. The flow has no record writes, mail, assignment, timer, AI Builder, Copilot, Dataverse, generic HTTP, custom connector or scheduled activation. It remains Stopped and disabled until separately qualified.

### Inputs

The private deployment profile must provide exactly \`site_url\`, \`list_id\`, \`view_id\`, \`connection_name\`, \`fields\` and \`max_items\`. All 11 logical columns require **explicit, unique native internal-name bindings**. They are never inferred from display names or file names. ID and ETag are system properties. A mapped \`OData__UIVersionString\` is only accepted under its exact expected technical name. The source contains no real site, connection or List identity.

**Native compatibility must be checked** against an actual accepted \`GetItems\` action from the selected environment before importing. Microsoft's public connector documentation confirms operation ID and parameter keys, but not the exact dynamic column schema of the user's List. Do not invent missing fields, patch the live List automatically or use a separate OAuth client to work around a denial.

### Commissioning and evidence

1. Read back the intended SharePoint List GUID, owner, permissions, versioning setting, internal column names and exact selected view.
2. Inspect an existing accepted Standard SharePoint \`GetItems\` action and the connection reference in this environment, including pagination policy and saved WDL format. Compare the generated source with that accepted native shape; do not guess unknown properties.
3. In a qualified maker/solution context, pack the stopped flow with PAC and preserve existing solution/connection owners. Import only as a separately authorised, initially Stopped candidate. **No import, tenant write or activation occurred in this source change.**
4. With a fictional two-forum register and approved native operator path, run bounded read tests for zero, one, multiple, threshold minus one, exactly threshold and over threshold rows; check enabled/disabled behaviour, output fields, native metadata and fail-closed limits. Validate actual SharePoint pagination behavior rather than treating WDL config alone as proof. An exact threshold-sized result deliberately fails.
5. Compare the native read projection with \`sharepoint_decisions_reader.py\` and \`meeting_register_projection.py\` using independently retained source/version evidence. Prove both logical composite IDs and physical SharePoint List item IDs are unique, and preserve the distinct reported-complete/resolved states.
6. Verify operator access, no-email/no-write effects, throttling and recovery. Preserve the Stopped/manual fallback and source preimage. Document the exact accepted template/solution source and native receipts privately.

**Status:** source candidate only. No native flow save/run, connector permissions, response shape, solution pack, current-head hosted tests or operational release claimed. The existing H2 native access limitations and GitHub Actions capacity/review gates remain separate.

### Sources

- [SharePoint connector / Get items](https://learn.microsoft.com/en-us/connectors/sharepointonline/#get-items)
- [Working with Get items](https://learn.microsoft.com/en-us/sharepoint/dev/business-apps/power-automate/guidance/working-with-get-items-and-get-files)
- [Native pagination policy](https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-exceed-default-page-size-with-pagination)
- [Workflow expression functions](https://learn.microsoft.com/en-us/azure/logic-apps/expression-functions-reference)
