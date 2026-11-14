# Standard-connector cloud implementation and safety contract

## Existing functionality reused

- SharePoint Standard connector: **Send an HTTP request to SharePoint** for native REST list writes and ETags, plus indexed/unique list columns, native list versioning, restricted document library, managed record controls and standard event triggers.
- Solution-aware Power Automate flows: explicit-submit app trigger; scheduled policy sweep and future-effective activation; timeout/retry/catch scopes, correlation IDs, controlled digests and monitoring.
- Microsoft Entra groups / Office 365 Users and SharePoint group or item permissions: authoritative role resolver. **Do not trust Power Apps caller identity or role in a request parameter.**
- Power Apps canvas: practitioner/approver dashboards and private editable drafts; all protected state transitions are server-side.
- No Copilot/AI, premium custom connector, third-party service or premium Dataverse data model in the baseline.

## SharePoint layout

Provision four independently access-controlled lists according to `sharepoint-schema.json`, plus a records-controlled document library. Each list requires a **unique indexed Key** and plain multiline JSON Payload. The head record is the **single compare-and-swap commit point**. Multi-list operations are a *recoverable saga*, not an ACID transaction.

1. Create/read Operation receipt keyed by stable operation UUID; hash binds plan, actor, version, expected generation, exact command and payload. A reused key with different digest is rejected.
2. Retrieve PlanHead and its exact `@odata.etag`. Resolve identity, current delegation, employment instrument and service scope within the trusted flow. Check expected generation.
3. Create immutable staged Version/Decision artifact with unique operation Key, compare on replay. Do not expose staged records as approved.
4. Attempt SharePoint REST `MERGE` using `IF-MATCH: "<etag>"` on PlanHead, changing `Payload` with generation+1, last operation key and new state. HTTP 412 = concurrency conflict; **never wildcard-match or blindly retry an outdated decision**.
5. Persist committed operation receipt and outcome. If a worker crashes after step 4, the next worker reads `Head.LastOperation`, verifies the operation and finalises its receipt before advancing the head.
6. Scheduled reconciliation flags prepared operations not committed, orphan artifacts, stale role grants, failed exports and pending effective-date activations. Operator-visible resolution required when unclear.

REST action examples:

```http
GET _api/web/lists/getbytitle('JP_PlanHeads')/items?$filter=Key eq 'plan-id'
Accept: application/json;odata=nometadata

POST _api/web/lists/getbytitle('JP_PlanHeads')/items(123)
X-HTTP-Method: MERGE
IF-MATCH: "7"
Accept: application/json;odata=nometadata
Content-Type: application/json;odata=nometadata

{"Payload":"<canonical JSON state with generation + 1>"}
```

**Do not send tokens/credentials in body content.** "Send an HTTP request to SharePoint" executes using the configured approved SharePoint connection and must be limited to the site's permitted action scope.

## Qualification still required

- [ ] CHHHS development site, restricted list provisioning, service roles and DLP/licence controls.
- [ ] Native REST unique/ETag/412 readback, 429 throttling and crash-after-CAS replay under flow retries.
- [ ] Multi-stage Clinical Director, HR/IR, delegated employer decision, acting delegations and no-self-approval in server-side flow.
- [ ] Current approved industrial and review policy edition; no operative inference from draft CHHHS work instruction.
- [ ] Per-item/list/records-library confidentiality, historical access/revocation and retention/legal holds; plan-head payload scaling and archive partition strategy.
- [ ] Real solution-aware cloud flows, app environment variables, SharePoint provisioning, solution ZIP clean import, rollback, production licensing.
- [ ] Privacy-safe notification and audit trail, stage-specific failure handling, bounded concurrency, reference monitoring and security/accessibility assessment.

### Evidence ceilings

Local 19-test reference suite validates deterministic source behavior with SQLite simulation and fake REST transport. It **does not** prove cloud runtime safety, SharePoint transactionality across lists, native Power Platform import, or legal adequacy of electronic approvals.

Official references: [SharePoint connector](https://learn.microsoft.com/en-us/connectors/sharepoint/), [Power Automate SharePoint HTTP guidance](https://learn.microsoft.com/en-us/sharepoint/dev/business-apps/power-automate/guidance/working-with-send-sp-http-request), [SharePoint REST ETags](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest).
