# CareOps costing core

This standalone package defines a small, fictional activity-cost contract for
source-level interoperability. It uses explicit period and currency identities,
quantity/rate units, integer minor-currency units, and a rate-sensitivity
parameter. An optional aggregate provider is accepted only when its contract
version, correlation ID, idempotency key, snapshot freshness, period and
currency match. Missing or incompatible optional inputs are excluded from the
calculation and reported through `aggregateProviderStatus`; repeated identical
aggregate identities are idempotent, while conflicting duplicates are rejected.
The provider idempotency key is scoped as
`providerId:snapshotId:correlationId`, and the correlation ID must match the
scenario ID.

The calculation is `quantity × unitRateMinorUnits`, rounded to the nearest
minor unit for each activity. Sensitivity is applied to each activity amount
using basis points (`10,000` means 100%). Optional aggregates are then added to
the sensitivity-adjusted activity total. The output is deterministic and has
no clock, network, storage, ledger or native-system side effects.

Run its checks with `npm test` from this directory. CI uses the repository's
existing exact Node 26.12.0 setup. The project-owned code is covered by the
repository's Apache-2.0 licence. This package contains no Figma UI components,
images, private workbook formulas, operational records or copied third-party
source. Its fixture is synthetic and proves no business parity, finance-ledger
authority, native deployment or operational acceptance.
