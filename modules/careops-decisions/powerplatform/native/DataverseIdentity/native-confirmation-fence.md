# Stabilise the original confirmation within the native recording transaction

25 September 2026. N03.04-N03.06 source after Decisions#47 at
f4e21fa0589497281ff43efad8f4885af9bcc8c9. No tenant was changed.

NativeConfirmationFence.Acquire performs the actual SDK pattern for protecting the
original source interval: read through the existing verified caller service, issue
one UpdateRequest changing ONLY the technical fence token with IfRowVersionMatches,
then re-read and verify original content/currentness. It requires the direct
recording pipeline and an ambient transaction; context/caller/record identities
must match before source work starts. It never creates a new human confirmation,
changes clinical content, sends a message or invokes an elevated connection.

The write is conditional on the first observed native version. A prior withdrawal
or other competing change causes the update to fail, with no blind retry. After
update, the source must have a different native version, the exact written token,
the same full original decision digest, policy/pathway and confirmation/currentness
instants. The actual source reader rechecks creator, actor, record and state.
Synchronous extensions cannot silently change original evidence during this update.
Native failures and altered sources escape as a generic exception; they must abort
the encompassing transaction, not trigger a compensating write or repeated decision.

Microsoft documents that record updates take write locks held until transaction
completion, and SDK operations from a synchronous plugin share the transaction.
That is the intended native basis for this fence, not a claim that a fake service
implements database isolation. Native table concurrency support, field/row update
permissions, real competing transactions, blocking and rollback remain required
sandbox evidence. No detached web API call or connection may replace the supplied
native service, and no lock lasts beyond the current request/transaction.

## Integration and workload boundaries

Use after binding the direct native caller and before the final decision save.
Keep subsequent authority/source validation and journal/event operations in the
same short native transaction. Do not call the fence from a historical receipt
read, render path, background retry or while a person is thinking in the UI.
The token is a transport marker, not a secret, permission, lease or clinician task.
Metadata and returned snapshots do not prove the caller remains in a transaction.
A host must not catch an acquisition failure and continue to the writer.

This guards ONE confirmation source only. Released delegations, role occupancy,
approved outcome/ownership policies and other mutable authoritative records need
their own consistent version/locking strategy. Use an agreed lock order and bounded
native operations; do not add long network/agent calls inside the critical section.
The full protected host still must compose these controls. This slice does not
register an endpoint or independently authorise the HumanConfirmedJournal core.

Original source capture and immutability/direct-Create controls remain prerequisites;
a fence cannot authenticate an already forged record. Correct source/team permissions
must allow only the controlled technical token update, not arbitrary evidence edits.
Native expiry checks still apply before journal staging. The administrative on-behalf
path, actual signed CHHHS instruments and operational acceptance remain open.

Tests exercise the actual source reader, CallerResolver, UpdateRequest and original
codec under synthetic SDK services. They verify exact patch/version/service binding,
intervening version failure, post-update evidence changes, native errors, wrong
contexts and input mutation. Fake changes are deliberately NOT called proof of
native rollback or cross-thread serialisation. All existing dependencies, tests,
warning and coverage gates remain; no local .NET or native tenant pass is claimed.
No-admin M365/browser pilots remain independent. No new clinician queue, app ID,
privilege, real record, clinical scope, paid service or CGov change occurred.

Primary Microsoft sources checked 25 September 2026:
- https://learn.microsoft.com/en-us/power-apps/developer/data-platform/scalable-customization-design/database-transactions
- https://learn.microsoft.com/en-us/power-apps/developer/data-platform/optimistic-concurrency
- https://learn.microsoft.com/en-us/power-apps/developer/data-platform/scalable-customization-design/transaction-design-patterns
