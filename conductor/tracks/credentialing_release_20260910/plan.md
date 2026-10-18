# Plan and implementation record

## Stage 1: source intelligence

- Merge the Policy Atlas credentialing collection.
- Preserve the distinction between public metadata, current authoritative source, approved local rule and individual decision.
- Pin the collection commit in CareOps.

Status: complete.

## Stage 2: module contracts

- Merge read-only legacy source observation.
- Merge intake, reconciliation and governed handoff.
- Merge committee recommendation and separate delegated decision.
- Merge privacy-minimised process assurance.
- Preserve later safety-signal and reporting modules outside the initial MVP.

Status: complete.

## Stage 3: cross-module release

- Record exact commits and contract names.
- Validate prohibited writes and human decision stages.
- Pin the Approve gitlink in the parent repository.
- Add a source release receipt.

Status: complete in this branch, subject to parent pull-request validation and merge.

## Stage 4: organisational discovery

- Confirm current CHHHS policy, procedures, delegations, committee terms and records requirements.
- Walk through routine renewal, changed scope, temporary approval, review and appeal with staff.
- Confirm the existing system's supported API, export, read view and HTML surfaces.
- Agree the minimum necessary data, pseudonymisation and silent-comparison method.
- Establish baseline quality, workload, timeliness and rework measures.

Status: not commenced. Requires CHHHS ownership and approved access.

## Stage 5: synthetic end-to-end harness

- Generate one routine-renewal case and controlled negative variants.
- Exercise Legacy Migration → Approve → Decisions → Process.
- Verify replay safety, correction, fairness, conflict, delegation, expiry and reconciliation paths.
- Produce a single human-reviewable evidence receipt.

Status: next repository increment.

## Stage 6: silent evaluation

- Use approved minimised retrospective data, then a bounded prospective silent comparison.
- Leave the current process authoritative.
- Measure false alerts, missed requirements, rework, stage time, manual touches, workload and unintended burden.

Status: separately gated.
