# careops-approve implementation plan

Status: source composition and independent checkout qualified; optional scenario/interfaces remain open. Priority position: 10.
Existing Approve maintenance may proceed independently; this is not a second import.

## Phase 1: Selection and boundary

- [x] APPROVE1.1 Refresh exact default head/checks with the existing owner; record a stable selected commit and preserve in-flight work.
- [x] APPROVE1.2 This module is already materialised at careops-approve. Maintain its existing pin and existing release contracts; do not create modules/careops-approve or blindly update its version. Generic maintenance may proceed independently.
- [x] APPROVE1.3 Inspect licence/attribution, source/history/privacy and deployment dependencies. Record concrete gaps without inferring public safety from visibility or scanner success alone.
- [x] APPROVE1.4 Checkpoint: record selected standalone slice, exact inputs, ownership and source-only stop conditions here.

## Phase 2: Parent composition and standalone proof

- [x] APPROVE2.1 Validate the existing careops-approve gitlink; update it only for a separately qualified generic release need, preserving credentialing pins unchanged.
- [x] APPROVE2.2 Verify clean parent clone without optional modules and selective child initialization; retain child licence and actual private-access boundaries.
- [x] APPROVE2.3 Run existing focused source/fixture checks and parent publication/portfolio checks; record exact revision, commands and actual results. Do not claim native operation.
- [x] APPROVE2.4 Checkpoint: retain preimage parent SHA, source provenance and supported commands; preserve a failed/missing check rather than marking qualification complete.

## Phase 3: Interoperability and recovery

- [ ] APPROVE3.1 Synthetic intake/routing, duplicate request, human approval, cancellation, recovery and optional provider absence; no autonomous decision or credentialing integration change.
- [ ] APPROVE3.2 Test only selected optional interfaces with provider absent, incompatible version, stale/missing inputs and duplicate retry; preserve authoritative ownership and human edits.
- [ ] APPROVE3.3 Rehearse reverting only the source pin/catalog/CI change in a disposable clone. Native objects/data are not deleted or rolled back by a source-reference reversal.
- [ ] APPROVE3.4 Checkpoint: close only proved source scope; send one consolidated deliverable or genuine blocker to the existing owner, without acknowledgement polling or a new chat.

## Selected source and parent qualification — 25 October 2026

The existing source is `edithatogo/careops-approve`, selected at
`f71c494634a87a9b4145742011070325c9b39c99`, the same commit as its public
`main`. The CareOps parent gitlink, `.gitmodules`, `PUBLIC_SOURCE_FILES.json`,
catalog, and current public runtime compatibility declaration agree on this
pin. The public `credentialing-cross-module.yml` also retains a separate
credentialing release reference (`ec7d7230b0fae3293c7ed51e716074074f83b5bb`);
that explicitly selected integration reference is distinct and was preserved.
No source pin change was needed.

All eight check runs on the selected Approve main commit succeeded, including
repository validation, reference safety, package attestation and shared source
security. The source has an Apache-2.0 `LICENSE` and a `NOTICE` that preserves
third-party and external-source rights. Its README describes environment values,
connection references and identities as deployment configuration that must not
be committed. This qualifies the selected public source and its existing CI
receipt; it does not grant access to private deployment bindings or establish
native operation.

In a fresh public CareOps clone at `11520f5669cc2653d7ad3c84ec943642f48d9b0b`,
`pwsh -NoProfile -File portfolio-scripts/Test-Portfolio.ps1` passed with all
optional children uninitialized. Then
`git submodule update --init --checkout careops-approve` checked out only the
selected Approve commit; sibling optional modules stayed uninitialized. The
pre-existing parent checkout remains uninitialized at the Approve path. This
clone and the selected child were not modified. Future child/source updates
still require their own qualified source need. APPROVE3.1–3.4 remain open for
the optional synthetic scenario, interoperability and recovery slice.

### Existing root reference recheck — 25 October 2026

On CareOps main `4a10d636b9a69b525733e6f5dcc31d9c60156035`, the root
`careops-approve` gitlink is mode `160000` at
`f71c494634a87a9b4145742011070325c9b39c99`. `.gitmodules` identifies the
canonical `edithatogo/careops-approve` URL with updates disabled; the public
inventory, module catalog, repository catalog, ALM record and public runtime
compatibility record agree on the existing root path and source pin. The
separate credentialing release pin remains preserved. No
`modules/careops-approve` gitlink or duplicate directory is present, and the
existing child checkout remains uninitialized. This readback reconfirms the
already-qualified source reference without changing its pin or child state;
the optional source-only Approve/Decisions scenario remains a separate open
task under APPROVE3.1–3.4.
