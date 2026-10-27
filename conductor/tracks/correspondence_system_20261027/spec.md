# Correspondence system continuity specification

## Purpose

Reuse the existing correspondence log and CMO/EDMS channel as a system. Correspondence remains authoritative in the log; selected tasks live in Basic Planner with reciprocal links. Do not manage individual correspondence as part of setup or create a parallel register.

## Recovered baseline

The [published source](https://github.com/edithatogo/careops/pull/216) retains capture, source identity, duplicate/replay handling, technical receipts, selected manual linked actions, reciprocal links and partial-save recovery. Module contract/operator/readiness documents are already present; preserve their history. Native review/channel/health surfaces and access observations are recorded separately in the retained private checkpoint, not re-certified here.

## Role and permission contract

- CMO and ESO use the authorised correspondence pages, log and the existing Basic Planner plan. The ESO's log ownership is a private user-confirmed fact, not a new permission grant performed by recovery.
- ESO linked-action rights are run-only (CanView), never CanEdit/co-owner. Preserve existing flow maintainers. Navigation tabs do not grant target access.
- A personal Basic plan needs native sharing into a suitable group limited to the two authorised operators. Do not use a broad parent Team or migrate task identities blindly. Existing sharing-notification approval is person/scope-specific and remains private.
- Use CLI-first exact-target qualification and the retained VS Code workload auth recipe. A Graph Tasks scope gap does not invalidate a separately qualified standard connector. Password/MFA is a real human boundary. No new consent or client switching to defeat denial.

## System boundaries

Existing intake is unchanged. Standard connectors only; no Premium, Copilot or paid feature. Task completion never closes correspondence. Public content uses generic roles and placeholders; person names, native IDs, enterprise addresses, deployment bindings and operational evidence remain private. Source work, native save, runtime proof and operational acceptance are distinct.

## Next increment

[Automatic task creation and completion reflection](../correspondence_planner_automation_20261027/index.md) now has source/stopped preparation verified under later user implementation authority. Activation remains held. The restoration request alone granted neither implementation nor activation. Other optional features remain deferred.
