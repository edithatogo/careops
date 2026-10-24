# CLI-managed Outlook connector reads

Use this route when an existing authorised Office 365 Outlook connection can read
the mailbox but the CLI's direct Microsoft Graph token lacks mail permissions.
These are separate authentication and authorisation boundaries: a direct Graph
403 does not establish that the existing Outlook connector is unavailable.

## Execution route

1. Reuse the qualified M365 CLI session, using the Microsoft 365 Agents Toolkit
   compatible public client and the CLI's own credential store. Existing local
   qualification used MSAL authorization code with PKCE, a loopback callback and
   `responseMode=form_post`, with resource `/.default` scopes and account validation
   before persistence. This is not token extraction from VS Code. Resolve exact
   parameters and bindings from private records; do not guess or cycle client IDs.
2. Read the existing isolated manual Power Automate probe, its connection
   references, state and terminal run history. Confirm current ownership and no
   operation in flight. Preserve its complete preimage. Do not change another
   lane's flow or the notification sender to perform a mailbox lookup.
3. Prepare a bounded GET-only definition using the existing `shared_office365`
   connector's `HttpRequest` action with `Uri` and `Method`. Discover the installed
   operation schema; supported Graph routes are not automatically supported by
   the connector's request broker. Use a manual Request/Button trigger, existing
   embedded connection references and required parameter declarations. Do not
   author the authentication annotation that the service injects.
4. Validate the exact final definition with the maintained operation policy.
   Review the native update diff, check for concurrent changes, save through the
   qualified management route and read back definition and bindings. For
   `m365 request` JSON bodies, specify `--content-type application/json`.
5. Invoke only within the user's current manual-run authority, through the
   authenticated management operation rather than a public callback. Narrow mail
   reads by the requested subject/date and select only necessary metadata. Do not
   request bodies or attachments unless needed and authorised. Reading must not
   mark messages read or change them.
6. Inspect each native action result and the actual returned records, not just
   top-level run success. Secure outputs may prove action success while hiding
   the records needed to establish an exact message match. Any permitted output
   inspection and local retention must be limited and private. Record pagination
   limits. Submission success alone does not prove an Inbox receipt.
7. Reconcile uncertain runs without replaying them. Restore the complete secured
   GET-only baseline and connection references; verify saved state is Stopped.
   Keep native receipts, identities, mail data and bindings outside public Git.

## Authority and evidence limits

Historical qualification on 18 October 2026 established successful native folder,
rule, category, mail-metadata and calendar-list reads. A later bounded source
search reused the route successfully. Exact evidence remains in private
operational records. Historical success is not current authentication, all-mailbox
coverage, permission for writes or standing authority to activate a flow.

The connector's credentials stay with the connector; the CLI only authenticates
management operations. Do not copy tokens/caches, seek new consent, register an
app or retry unchanged access-policy denials to reproduce this route. Missing
direct Graph mail scopes should lead to checking the existing qualified connector,
not repeated sign-ins or an assertion that all CLI mailbox access is blocked.

If workflows must remain disabled, inspect and prepare only until temporary
manual execution is explicitly within scope. Qualify platform-generated owner
failure notifications before deliberate failure tests; a GET-only action graph
does not prove that no platform email can be generated. Never send or resend a
message as a receipt check.

The historical implementation is the private Outlook workspace's
`tools/outlook/connector_session.py` gateway and operation policy. Inspect their
current contract and ownership before reuse; do not copy private bindings into a
new public helper.

References: [Office 365 Outlook connector](https://learn.microsoft.com/en-us/connectors/office365/)
and [M365 CLI request](https://pnp.github.io/cli-microsoft365/cmd/request/).
