# Python 3.15 migration and qualification

## Objective

Every active Python use in careops runs on Python 3.15 at the newest qualified patch, currently 3.15.1. Cover development, build, tests, automation, CI matrices, containers and helpers.

## Requirements

- Inventory actual invocations and select an explicit repository-local interpreter; record its actual version.
- Align constraints, locks, current setup instructions and latest qualified dependencies. Remove older active default and compatibility runners; retain only immutable history and intentional version-test fixtures.
- Preserve private history, uncommitted work, native bindings and active operations. Hand over environments only at terminal points.
- Reuse completed evidence from [qualified migration](https://github.com/edithatogo/careops/pull/111); do not repeat unchanged tests or infer native acceptance from source CI.
- Keep unsupported dependency or hosted tooling behavior explicit; never weaken meaningful tests or downgrade Python to hide a blocker.

## Acceptance

Account for each active Python surface, verify actual interpreter and affected checks, qualify current-head changes and post-merge main, and record remaining external blockers accurately.

## Goal execution

Use `/goal Complete careops Python 3.15 migration and qualification against this track, preserving all acceptance and recovery requirements`. Goals belong to chat state. The shared portfolio chat already has an unfinished goal; a new goal creation was rejected on 2026-10-23. No separate goal is claimed for this module. Preserve the unfinished objective rather than falsely complete it to free the slot.

## Out of scope

No tenant, licensing, consent, production activation, circulation, email or external communication changes.
