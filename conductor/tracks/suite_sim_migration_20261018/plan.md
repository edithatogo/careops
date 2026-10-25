# careops-sim implementation plan

Status: optional public source composition and parent-owned synthetic interface qualification complete; engine execution and operational acceptance remain unqualified. Priority position: 9.

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

- [x] SIM3.1 Add a fictional versioned scenario and Rust-shaped run-document envelope bound to the selected Sim source revision, input digest, seed, time unit and horizon; verify deterministic result metadata and unsupported-version handling. This is source-level proof, not a CareOps-triggered engine execution.
- [x] SIM3.2 Qualify the selected parent-owned packet adapter for provider absence, incompatible contract/source, stale/missing or changed inputs and identical/conflicting duplicate retries. The adapter is read-only and does not replace result files or human edits.
- [x] SIM3.3 Rehearse reverting only the source pin/catalog/CI change in a disposable clone. Native objects/data are not deleted or rolled back by a source-reference reversal.
- [x] SIM3.4 Checkpoint: close only proved source scope; send one consolidated deliverable or genuine blocker to the existing owner, without acknowledgement polling or a new chat.

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
Parent catalog, inventory, public URL and pin guard were qualified together.
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

A separate fresh clone of the public PR branch at
`362ee199c92343f6712defa71f8f82b4db0a549f` initially had every optional
submodule uninitialized and passed the portfolio check. Selective initialization
then checked out only Sim at `6ffd51392303cb08d249f71fbfdd8025771fcb55`;
all sibling submodules stayed uninitialized. The public branch and selected Sim
source remain independently available. PR141 merged as
`f8ba732185926b8552fae89a343bbf5868b942e3`; its tree matched the reviewed
candidate and the selected Sim gitlink remained exact. All 12 executed main
checks succeeded (two conditional jobs skipped). The source scope is closed in
the parent suite plan; SIM3.1 and SIM3.2 are optional future interface tasks.

The selected child revision's 16 protected-main checks are unchanged and reused
as its standalone Rust/fixture evidence. On the parent source candidate, the
portfolio PowerShell check, `validate_public_source.py`, the focused
`test_composition_pins.py` selectors (2 tests), and full
`portfolio-scripts/checks` unittest discovery (113 tests) passed under the
verified repo-local Python 3.15.1. `qualify_incidents.py` passed its fictional
staging scope, and `build_source_release.py` produced the Incidents archive and
SBOM. These checks do not establish a native Sim runtime or operations approval.

### Selected interface audit — 25 October 2026

A read-only disposable clone of the selected public Sim source was checked out
at `6ffd51392303cb08d249f71fbfdd8025771fcb55`; public `main` matched that pin
and the checkout was clean. The source contains a dashboard scenario config with
`schema_version`, `capacity_profile_version` and `seed`, a metrics structure
that carries a seed, and an exporter that labels JSON as
`careops_ed.run_document.v1`. The dashboard runner computes its metrics with
fixed heuristic formulas; it does not invoke or adapt the Rust simulation. The
run-document payload adds a wall-clock export timestamp and the source search
found no corresponding run-document JSON Schema or focused exporter contract
tests. These adjacent version labels therefore do not prove a stable
scenario/result contract or reproducible result file.

SIM3.1 and SIM3.2 remain open. To close them, a source owner must define and
version synthetic scenario and result documents that bind the selected Rust
simulation input, seed, units, engine/source version and deterministic output;
then add tests for unsupported versions, missing/stale input, provider absence
and duplicate retry. Do not describe the existing dashboard heuristics as Rust
simulation output or add a production event dependency. The audit used only a
disposable read-only clone and made no changes to Sim, its active worktrees or
runtime.

### Rust CLI contract evidence reconciliation — 25 October 2026

Correction to the scope of the dashboard finding above: the selected Rust CLI
does provide a separate versioned scenario/run-document contract. At the exact
parent-selected child commit
`6ffd51392303cb08d249f71fbfdd8025771fcb55`, `crates/careops-ed/src/api_runner.rs`
defines `RunManifest` and `RunDocument`. The manifest records schema version,
scenario ID, input path and SHA-256, seed, time unit and horizon; the run
document labels its validation taxonomy as software verification, no clinical
validation, and synthetic provenance. Scenario validation rejects unsupported
schema versions. The focused Rust API and validation tests cover these fields,
seed override, input hashing, incompatible time units, missing input,
overwrite protection and unsupported scenario versions. The exact selected
child main CI evidence recorded above includes the locked Rust workspace test
job. The prior “no focused exporter contract tests” statement applies to the
TypeScript dashboard exporter only, not the Rust CLI.

This reconciles existing Rust evidence; it does not close SIM3.1 or SIM3.2.
The manifest does not identify the exact engine/source revision, and the
CareOps parent has not selected a consumer/provider adapter contract that binds
this Rust document to a CareOps-owned input/output. The dashboard heuristic
output remains separate and is not Rust simulation output. A selected
parent-owned adapter must define source/engine identity and exercise absent or
incompatible provider, stale or missing input and duplicate retry before either
interface task can close. Do not modify the child source, initialize its
optional nested submodules, or infer native acceptance from these source tests.

### Parent-owned synthetic interface qualification — 25 October 2026

CareOps now has a small source-side adapter at
`portfolio-scripts/sim_interop_v1.py`, an independently authored fictional
scenario input and Rust-shaped run-document packet under
`portfolio-scripts/fixtures/sim/`, and focused tests in
`portfolio-scripts/checks/test_sim_composition.py`. The packet records the
selected Sim source commit `6ffd51392303cb08d249f71fbfdd8025771fcb55`, exact
scenario input SHA-256, scenario identity, seed, time unit, horizon and
synthetic software-verification taxonomy. The adapter validates the raw input
digest and manifest consistency, emits only deterministic result metadata, and
does not write or overwrite a run document.

The verified repo-local Python 3.15.1 command
`.local/ci-env/bin/python -m unittest discover -s portfolio-scripts/checks -p 'test_sim_composition.py' -v`
passed all eight focused tests. They cover deterministic/non-mutating output,
provider absence, unsupported contract and run versions, wrong source pin,
stale/future/missing inputs, path traversal, input digest and manifest
mismatch, duplicate retry and conflict, and rejection of clinical provenance.
The selected Sim child main CI receipt above supplies the independent Rust
workspace/API/validation test evidence; the current checkout's nested Kairos
and Conductor submodules remain uninitialized and were not changed.

This closes the parent source-contract scope of SIM3.1/3.2. The adapter does
not invoke the Rust engine and its source-commit field is a checked packet
assertion, not proof of execution provenance. No production events, Power
Platform runtime, native objects or persisted results were accessed. A
CareOps-triggered Rust run, native integration and operational acceptance
remain unqualified.
