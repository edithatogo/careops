# Plan

## Phase 1 — Inventory

- [ ] P1.1 Inventory every active Python surface and distinguish historical/version-test fixtures.
- [ ] P1.2 Verify repo-local interpreter version and safe environment handover.
- [ ] P1.3 Review phase evidence and checkpoint under the repo workflow.

## Phase 2 — Qualification

- [x] P2.1 Reuse [merged migration](https://github.com/edithatogo/careops-costing-public/pull/11) without repeating unchanged tests.
- [ ] P2.2 Close remaining runtime, lock, dependency and current setup-document gaps with focused checks.
- [ ] P2.3 Verify phase evidence and checkpoint.

## Phase 3 — Integration

- [ ] P3.1 Run affected structure/privacy checks and exact-head required checks; merge eligible work and verify main.
- [ ] P3.2 Audit every acceptance requirement and explicit external blocker.
- [ ] P3.3 Record actual goal-tool result; close only when full evidence supports completion.

## Current boundary

A track or prompt is not an armed goal or completed runtime migration. Shared chat goal creation was rejected due to its unfinished goal.

## Helper-environment increment

The four Source CI Python job definitions now use the existing qualified setup-uv action
for repository-local activation and exact interpreter/prefix verification. The
shared security job retains its independently qualified immutable helper policy.
The four tracked Python files and active workflow invocations were inventoried;
no application dependencies or native bindings change.

Local Python 3.15.1 checks exercise fresh creation and refusal of existing files,
directories, dangling symlinks, wrong versions/prefixes and ambient interpreters.
Caller-module shadowing is excluded during verification. Existing package parity
and command-selection regressions pass. Hosted Windows package/comparison and
Linux attestation executions remain required before merge and main qualification.

Inventory also identified the Node canary's receipt-only OS-Python provider.
Retain its setup-failure recovery purpose as an explicit scoped exception under
the user's latest-qualified policy; capture actual version/executable and keep
application build/runtime qualification separate. Frontend regression execution
now uses the selected repository-local interpreter as well.
