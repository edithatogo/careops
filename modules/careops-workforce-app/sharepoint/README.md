# CareOps Workforce — SharePoint review/versioning adapter

**Source-only, synthetically tested. Not a deployed Power Platform solution.**

A recoverable **single-plan-head compare-and-swap** protocol plus SharePoint REST mapping intended for Power Automate's *standard* SharePoint connector, with durable idempotency receipts and staged immutable artifacts. SharePoint does **not** provide multi-list ACID transactions. The SQLite fake simulates unique keys and ETags and is for tests only.

Run (Python stdlib):

```bash
cd modules/careops-workforce-app/sharepoint
python -m unittest discover -s tests -v
```

For actual Power Automate flows, implement the documented REST operations through **Send an HTTP request to SharePoint**; this Python reference cannot run natively inside a cloud flow. A trusted server-side authorisation/delegation resolver, HR/IR checks, expiry rules, proper site/list permissions and policy provenance remain required. Do not pass untrusted Power Apps actor names, roles or clock times directly to a decision. Use SharePoint unique indexes, exact `IF-MATCH` and a crash recovery/reconciliation flow. No Copilot, Dataverse or premium connectors are needed for this *proposed* persistence design; tenant licensing and supported deployment remain unverified.

The scheme supports explicit submit, single delegated approve/reject, scheduled future activation, authorised prior approved-history references, unique policy-review obligations and operation replay. Full multi-stage consultation/HR/IR and complete previous-version export are still pending.

Confidential CHHHS documents and real staff plans are excluded. See the parent [Conductor track](../../careops-workforce/conductor/tracks/chhhs_medical_job_planning_powerapp_20261111/index.md).
