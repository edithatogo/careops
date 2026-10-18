# Specification

Reconcile the corrupted or duplicate Power Automate flow records against source-controlled contracts and the live tenant without changing live data until an approved owner path exists.

## Acceptance criteria

- Every candidate flow has a stable identity, owner, connection state, enabled state, and source-control mapping.
- Disabled or connectionless duplicates are either safely removed through an approved path or recorded as a documented tenant blocker.
- The canonical flow contract has no automatic email, preserves auditability, and fails closed on invalid configuration.
- Any live test uses a synthetic, non-confidential fixture and does not alter existing submissions.
