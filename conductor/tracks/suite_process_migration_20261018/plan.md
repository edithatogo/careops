# careops-process implementation plan

Status: public source composition and synthetic consumer-boundary qualification complete. Priority position: 2.
An executable Approve producer, native provider and operational acceptance remain separate.

## Phase 1: Selection and boundary

- [x] PROCESS1.1 Refresh exact default head/checks with the existing owner; record a stable selected commit and preserve in-flight work.
- [x] PROCESS1.2 Wait for the existing Process owner to select a stable completed source revision; do not pull an unfinished working branch or interrupt current work. MIT source and passing checks observed previously must be rechecked on the selected commit.
- [x] PROCESS1.3 Inspect licence/attribution, source/history/privacy and deployment dependencies. Record concrete gaps without inferring public safety from visibility or scanner success alone.
- [x] PROCESS1.4 Checkpoint: record selected standalone slice, exact inputs, ownership and source-only stop conditions here.

## Phase 2: Parent composition and standalone proof

- [x] PROCESS2.1 After review, add an optional exact source gitlink at modules/careops-process, canonical URL and compatibility/catalog reference; update PUBLIC_SOURCE_FILES.json together.
- [x] PROCESS2.2 Verify clean parent clone without optional modules and selective child initialization; retain child licence and actual private-access boundaries.
- [x] PROCESS2.3 Run existing focused source/fixture checks and parent publication/portfolio checks; record exact revision, commands and actual results. Do not claim native operation.
- [x] PROCESS2.4 Checkpoint: retain preimage parent SHA, source provenance and supported commands; preserve a failed/missing check rather than marking qualification complete.

## Phase 3: Interoperability and recovery

- [x] PROCESS3.1 Synthetic event/file ingestion with stable source IDs, duplicate/replay, tombstone, stale and absent-provider cases; no workflow or authoritative-record writes.
- [x] PROCESS3.2 Test only selected optional interfaces with provider absent, incompatible version, stale/missing inputs and duplicate retry; preserve authoritative ownership and human edits.
- [x] PROCESS3.3 Rehearse reverting only the source pin/catalog/CI change in a disposable clone. Native objects/data are not deleted or rolled back by a source-reference reversal.
- [x] PROCESS3.4 Checkpoint: close only proved source scope; send one consolidated deliverable or genuine blocker to the existing owner, without acknowledgement polling or a new chat.

## Selected optional source composition — 24 October 2026

The selected public source is Process PR104 at
`c06c49f307950b3b6e62bac713f3d7abebdb236d`; all four exact-main workflows passed.
Retain the earlier PR103 graph/consumer receipts as historical qualification. The
new range updates only the pinned Power Platform skills source; application,
contracts and runtime locks remain unchanged. Existing native owners and private
evidence are untouched. The MIT licence remains in the independent child.

- [x] Select the completed public revision, verify checks and retain source scope.
- [x] Prepare the exact optional gitlink, inventory, topology and actual consumer pin
  together; require selected source profile and parent boundary checks.
- [x] Verify parent-only clone, selective exact child initialization, all nine
  existing fictional consumer cases, current-head checks and source-only reversal.
- [x] Merge qualified source composition and verify main; native acceptance stays
  open and optional providers remain optional.

Local actual Python3.15.1 frozen noneditable consumer qualification passed all
nine existing cases and preserved the three historical contract digests. The
parent-only clone passed publication checks; selected initialization fetched the
exact Process revision without Approve, and reversing the composition restored
the preimage source tree. The paired-pin guard also refuses independently stale
consumer, inventory and topology pins, duplicate components and wrong paths.
Hosted qualification and final squash-commit reversal remain to be verified.

### Published source composition qualification

CareOps PR131 merged at `d673399e2c22580fa50d9b4f6e4ef9058d9bb5f4`.
All nine main workflows passed; the downloaded exact-main consumer receipt
contains nine passed fictional cases with producer runtime and production writes
false. The final paired-pin guard passed before consumer checkout. A fresh public
parent clone passed without optional modules; selective Process initialization
fetched the exact pin without Approve, and reverting the actual squash commit
restored its parent tree. Existing native/provider gates stay open.

### Source composition closeout — 25 October 2026

The original parent preimage is `3b16c8937e41269bb97bd015e3355c2b91b4cace`.
PR131 merged as `d673399e2c22580fa50d9b4f6e4ef9058d9bb5f4` and its
recorded clean-parent, selective-checkout, nine consumer cases and actual
source reversal close the initial source tasks above. Later reviewed promotions
selected `5c2cc222cc4cbb97e1f34bcf9f8c28404fdee8c5`, now equal in the
gitlink, public inventory, catalog, ALM/compatibility records and consumer
workflow. GitHub readback found PR131 merged, 12 successful main checks and
two conditional skips; its PR head had 13 successes and one conditional skip.
At that checkpoint, parent main `2dd1abc9f079e955c70408d48fa367bb694bd87e`
passed the portfolio and public-source checks. These were the source
receipts available at that checkpoint; the subsequent Phase 3 evidence below
closes the synthetic consumer-boundary requirements.

### Synthetic acquisition and consumer-boundary closeout — 25 October 2026

The selected child remains `5c2cc222cc4cbb97e1f34bcf9f8c28404fdee8c5`,
equal to public `main`. Its exact-main CI `Python 3.15 quality and tests`
passed the full `uv run --no-sync pytest` suite on Python 3.15.1. The relevant
existing synthetic tests cover deterministic source IDs, overlap replay,
malformed/missing data, exclusive and stale watermarks, source withdrawal
without calling a provider, idempotent monotonic checkpoints, and tombstones
that block late replay: `tests/test_acquisition.py`, `tests/test_events.py`,
`tests/test_ingest.py` and `tests/test_reliability.py`.

The existing parent `Public declared boundary and Process runtime` check also
passed against these exact pins. Its nine fictional cases exercise the real
Process consumer with the Approve producer disabled by default, incompatible
contract/ontology versions, missing input, duplicate retry, stale watermark,
conflicting edits, source isolation and private-content rejection. Its receipt
keeps `producerRuntimeQualified=false` and `productionWrites=false`. This closes
the synthetic consumer-boundary requirement while leaving any executable
producer or native runtime unqualified.

One non-required child dependency updater remains in failure. On the exact
Process main commit, run `40095095610`, check `update-uv-graph` failed because
Dependabot detected `requires-python >=3.15,<3.16` while supporting Python only
through 3.14. The required Python 3.15.1 source-quality/test workflow passed;
do not lower the project constraint to make Dependabot succeed. Resolving the
updater is child-repository CI maintenance and remains with that repository's
existing owner; track it under suite CI, separate from this source qualification.
