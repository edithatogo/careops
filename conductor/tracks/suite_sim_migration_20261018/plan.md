# careops-sim implementation plan

Status: optional public source composition in progress. Priority position: 9.

## Phase 1: Selection and boundary

- [x] SIM1.1 Refresh exact default head/checks with the existing owner; record a stable selected commit and preserve in-flight work.
- [x] SIM1.2 Preserve ongoing Sim work and its Rust/Kairos runtime. Select an owner-confirmed stable source revision; inspect actual upstream licence files rather than relying only on GitHub licence detection.
- [x] SIM1.3 Inspect licence/attribution, source/history/privacy and deployment dependencies. Record concrete gaps without inferring public safety from visibility or scanner success alone.
- [x] SIM1.4 Checkpoint: record selected standalone slice, exact inputs, ownership and source-only stop conditions here.

## Phase 2: Parent composition and standalone proof

- [x] SIM2.1 After review, add an optional exact source gitlink at modules/careops-sim, canonical URL and compatibility/catalog reference; update PUBLIC_SOURCE_FILES.json together.
- [x] SIM2.2 Verify clean parent clone without optional modules and selective child initialization; retain child licence and actual private-access boundaries.
- [x] SIM2.3 Run existing focused source/fixture checks and parent publication/portfolio checks; record exact revision, commands and actual results. Do not claim native operation.
- [x] SIM2.4 Checkpoint: retain preimage parent SHA, source provenance and supported commands; preserve a failed/missing check rather than marking qualification complete.

## Phase 3: Interoperability and recovery

- [ ] SIM3.1 Synthetic versioned scenario/result files, seeds, units, reproducibility and unsupported-version handling; no production event dependency or Power Platform runtime rewrite.
- [ ] SIM3.2 Test only selected optional interfaces with provider absent, incompatible version, stale/missing inputs and duplicate retry; preserve authoritative ownership and human edits.
- [x] SIM3.3 Rehearse reverting only the source pin/catalog/CI change in a disposable clone. Native objects/data are not deleted or rolled back by a source-reference reversal.
- [ ] SIM3.4 Checkpoint: close only proved source scope; send one consolidated deliverable or genuine blocker to the existing owner, without acknowledgement polling or a new chat.

## Selected source and parent candidate — 25 October 2026

The existing Sim owner merged protected public main at
`6ffd51392303cb08d249f71fbfdd8025771fcb55` (PR181). Its 16 main checks
completed successfully, including Rust 1.99.1 default tests, Linux/macOS tests,
clippy, doctest, scope, policy and shared source security. The selected Cargo
workspace is the standalone source slice; its CI runs
`cargo test --workspace --lib --bins --tests --locked` with the independently
pinned Kairos and Conductor submodules. The actual `LICENSE` contains Apache-2.0
terms, `NOTICE` retains third-party boundaries, and Cargo declares Apache-2.0.
No child source or history is copied into CareOps. The parent's selected gitlink
is optional and its exact source can be checked out with
`git submodule update --init --checkout modules/careops-sim`.

The parent preimage is `2dd1abc9f079e955c70408d48fa367bb694bd87e`.
Parent catalog, inventory, public URL and pin guard are being qualified together.
The local Sim main checkout is older than the selected protected public main and
has other active worktrees; no child worktree or runtime was changed. Versioned
scenario/result adapters remain separate future work.

The source candidate is parent commit `9be82b7b17a1d335cb495955be430eb07deb41a8`.
In a disposable `git clone --no-local --no-hardlinks` of that commit, the parent
portfolio check passed with all optional children uninitialized. Explicit
`git submodule update --init --checkout modules/careops-sim` checked out only
the selected Sim revision; sibling modules remained uninitialized. In that clone,
`git revert --no-commit 9be82b7b17a1d335cb495955be430eb07deb41a8`
restored the tracked tree exactly to the preimage `2dd1abc9f079e955c70408d48fa367bb694bd87e`
(`git diff --cached --exit-code` passed). The initialized Sim directory remained
as an untracked checkout after reversal and requires an explicit local cleanup;
no child repository or native object was changed. This proves tracked source
reversal only. Parent full and hosted checks are recorded at the suite checkpoint.

The selected child revision's 16 protected-main checks are unchanged and reused
as its standalone Rust/fixture evidence. On the parent source candidate, the
portfolio PowerShell check, `validate_public_source.py`, the focused
`test_composition_pins.py` selectors (2 tests), and full
`portfolio-scripts/checks` unittest discovery (113 tests) passed under the
verified repo-local Python 3.15.1. `qualify_incidents.py` passed its fictional
staging scope, and `build_source_release.py` produced the Incidents archive and
SBOM. These checks do not establish a native Sim runtime or operations approval.
