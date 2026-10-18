# N03 journal source closeout

24 September 2026. Sanitized archive of completed SOURCE deliveries only.
Full N03 remains in progress. No real tenant writes, registered write endpoint,
source/delegation approval, native rollback or operational acceptance is claimed.

## Sequence

Existing Decisions#19 was verified on main at the start of this delivery. Its
caller/read documentation was already in open CareOps#167; that PR was reviewed
and merged at 767a55460e5c6ca21b7d7079469ec195c390caa0 before this closeout.
#167 final head a81495e98b92b654c6cbdfc0050b85b6ec343371 passed Harness35884831851,
Portfolio35884832018, Pilot35884831948 and Roadmap35884831694. The older read and
identity components are not claimed as new code in this journal delivery.

## N03-W01: exact append intent

Decisions#20 merged at 4c4abc6b4954f4fa1afa75dc056be8189f6bd3b3, directly
on #19. Checked final head 973167cf9b62ea3a67dce76530b7be118b4c116e passed:
Register35949846490, Identity35949846502, Calendar35949846527,
Authority35949846604, Reference35949846529 and Validate35949846503.

Actual artifact10788396980 was downloaded and its TRX/Cobertura independently
parsed: 40/40 native register tests, zero skips;166/166 library lines and106/106
branches. SHA256 f1c6dc5f04a0c4e0b50150963dc7d9b1ebaa1a87159ff4bb44a1d99d36bff84e.

The immutable payload requires complete explicit business data, valid UTC times,
exact hashes/outcomes, bounded native row version/sequence and predecessor. It
copies mutable SDK values and rejects altered retries. Review fixed the native
primary-key column returned with a retrieved record: only a correct matching GUID
is accepted. Wrong/extra fields still fail. Added transport regression tests;
resolved the automated finding. A static-allocation warning was corrected with a
cached private allowlist rather than an analyser suppression.

## N03-W02: transaction-bound journal staging

Decisions#21 merged at acc135465bb0007f03256267c12da1628c515f98, directly
on #20. Checked final head 7a3ee98ab4fbcbe75915d6ccdbb95b0509a57260 passed:
Register35950553545, Identity35950553396, Calendar35950553394,
Authority35950553492, Reference35950553470 and Validate35950553549.

Actual artifact10788582646 was downloaded and parsed: 92/92 native register
tests (52 added), zero skips;210/210 library lines and196/196 branches.
SHA256 7e814484c59625057f901ad425dd238db7140192b7bec67c193104f31f829d27.

The adapter rejects wrong transaction/context/service identity, makes a bounded
exact-ID replay query and does not write on an existing exact receipt. New entries
check root version/sequence and same-record predecessor, create history, then
perform a conditional native update. Only latest journal fields and projection
currentness change. Errors propagate without retries or compensating writes.
StagedInTransaction expressly does not mean final commit or practice clearance.

The fake services test real SDK request objects, ordering, matching and failure
propagation. They do NOT prove Dataverse rollback, isolation, permission or
native round-trip fidelity. No new package or sibling dependency was introduced.
Source reviews are recorded on the final PR heads, not presented as independent
clinical/cyber acceptance. All existing thresholds and locked dependencies remain.

## Inventory and remaining gates

See [N03.01 reference-to-native parity inventory](native-parity-inventory.md),
including concrete gaps in recording chronology, native representation fidelity,
current-scope projection and protected identity/authority integration. The inventory
is complete as a source assessment, not a claim that runtime parity is complete.

The protected handler must bind the actual canonical human decision and current
signed authority/case/evidence, provide a caller service from the native execution
factory, prevent direct CRUD bypass and complete projection/outbox within the
transaction. Native key/index/access/rollback/concurrency/restore, approved UI,
workload and operational acceptance remain mandatory. Null or absent restriction
data never becomes inferred no restriction, and a stale projection is not an
approval or a revocation. No part of this archive may activate production.

The no-admin synthetic M365 pilot and full Dataverse production target are
unchanged. No live records, permissions, app registration, paid service, scope,
migration or CGov contract were changed. No raw excluded archive is published.
