# Python 3.15 migration and qualification plan

## Phase 1 — Inventory and preservation

- [x] P1.1 Enumerate active Python invocations, envs, CI, containers, helpers and setup instructions; separate deliberate historical/version-test literals.
- [x] P1.2 Record explicit repo-local interpreter version and safe terminal handover evidence.
- [x] P1.3 Verify phase evidence and checkpoint using the repository workflow.

## Phase 2 — Reuse migration and close gaps

- [x] P2.1 Retain merged [runtime qualification](https://github.com/edithatogo/careops/pull/111) as prior completed evidence.
- [x] P2.2 Test only remaining gaps, align stale setup/technology guidance and qualify supported dependency incompatibilities.
- [x] P2.3 Verify affected structure, privacy and behavioral checks; checkpoint without weakening gates.

## Phase 3 — Integration and completion audit

- [x] P3.1 Verify current-head required checks, merge eligible changes and verify main.
- [x] P3.2 Account for all acceptance requirements and remaining external blockers; native acceptance stays separate.
- [ ] P3.3 Record actual goal-tool status and close the track only with full evidence.

## Current evidence and limits

No additional runtime blocker inferred; perform the final full-surface audit before closeout.

Track initialization is not proof that every Python surface has migrated. The portfolio chat's goal creation was rejected due to its unfinished goal; no per-module goal was armed here.

## Targeted test execution — 23 October 2026

The parent now provides an explicit focused-test launcher and shared workflow.
Its selection regression tests cover failure-only with no full fallback,
failed-first/full coverage semantics, stepwise, explicit node/pattern selection
and invalid selectors. Optional difftest0.3.0 qualification is blocked by its
PyO3 maximum3.14 check on actual3.15.1; no compatibility override was used.
Core pytest9.1.1/rerunfailures16.7 behavior is qualified separately using fictional
local cases. This does not close remaining module/native runtime gates.

## Current surface audit and qualification — 25 October 2026

The selected CareOps parent environment `.local/ci-env/bin/python` was invoked
directly and resolved to Python 3.15.1 at
`/Volumes/PortableSSD/appdata/local-dotdir/share/uv/python/cpython-3.15.1-macos-aarch64-none/bin/python3.15`.
No environment was replaced. The read-only dependency inventory reports the
parent and integrated `modules/clinical-hub-core/.python-version` at 3.15.1.
The parent workflow inventory contains no container definition; all literal
`actions/setup-python` selectors are 3.15.1, and both matrix-based workflows
(`pilot-profiles.yml` and `native-m365-roadmap.yml`) select only 3.15.1. Current
setup guidance in the parent and Clinical Hub uses the exact 3.15.1 pin. The
3.14 reference in `docs/credentialing/implementation-status-20260910.md` is
dated historical implementation evidence; 3.11/3.14/3.15.0 values in archived
receipts and synthetic version fixtures remain historical/test inputs. Optional
module repositories were not initialized by this audit; their exact selected
pins and runtime receipts remain in their own migration tracks.

The newest merged parent is `81849d676a14f6a9c0b6009a07dba2c0dee7ea40`
(PR #152). All eight current-main workflows passed, including the Python 3.15.1
pilot preflight, domain tests, source-boundary checks, native-roadmap integrity,
configuration fuzzing/dependency audit, CodeQL and shared source security.
The exact main run IDs are `40157628884`, `40157628867`, `40157628871`,
`40157628908`, `40157628862`, `40157628927`, `40157628896` and
`40157629009`. PR #152 also passed all twelve applicable current-head checks
before merge, including the 3.15.1 pilot preflight.

Two genuine service/dependency limits remain recorded and unchanged: optional
`pytest-difftest` 0.3.0 cannot build on 3.15.1 because its PyO3 dependency
supports only through 3.14, and the Process Dependabot UV graph updater currently
supports only through 3.14. Neither was bypassed or used to justify a Python
downgrade. The unsupported plugin remains unadopted; the child updater remains
with its existing owner. These limits are not failures of the required parent
3.15.1 runtime.

This audit closes the parent and integrated-source migration phases. It does
not certify the uninitialized optional children anew or establish native runtime
acceptance. P3.3 remains open until the overall active goal reaches its final
requirement-by-requirement audit.
