# Python 3.15 migration and qualification plan

## Phase 1 — Inventory and preservation

- [ ] P1.1 Enumerate active Python invocations, envs, CI, containers, helpers and setup instructions; separate deliberate historical/version-test literals.
- [ ] P1.2 Record explicit repo-local interpreter version and safe terminal handover evidence.
- [ ] P1.3 Verify phase evidence and checkpoint using the repository workflow.

## Phase 2 — Reuse migration and close gaps

- [x] P2.1 Retain merged [runtime qualification](https://github.com/edithatogo/careops/pull/111) as prior completed evidence.
- [ ] P2.2 Test only remaining gaps, align stale setup/technology guidance and qualify supported dependency incompatibilities.
- [ ] P2.3 Verify affected structure, privacy and behavioral checks; checkpoint without weakening gates.

## Phase 3 — Integration and completion audit

- [ ] P3.1 Verify current-head required checks, merge eligible changes and verify main.
- [ ] P3.2 Account for all acceptance requirements and remaining external blockers; native acceptance stays separate.
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
