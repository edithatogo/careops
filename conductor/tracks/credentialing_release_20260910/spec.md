# Specification: credentialing MVP source-contract release

## Purpose

Publish one auditable source release that coordinates the Policy Atlas and existing CareOps modules without collapsing their ownership, data or deployment boundaries.

## Requirements

1. The source-intelligence collection must be pinned to an immutable Policy Atlas commit.
2. Each participating module must have an explicit repository, commit, capability and merge state.
3. Approve and Decisions must share the same versioned governance-packet and result contract names.
4. Legacy-system information must remain a read-only observation pending human reconciliation.
5. Process assurance must use privacy-minimised events and reject direct identity, raw evidence, free-text scope and decision reasons.
6. Credentialing-officer review, professional or service review where required, committee recommendation and delegated decision must remain human acts.
7. Recommendation and delegated decision must remain separate records.
8. The release must not enable authoritative-register, roster, identity/access or release-to-practise writes.
9. AI must remain advisory and must not establish authority, registration, qualification, competence, scope, conditions or outcome.
10. Repository, tenant, pilot, operating-effectiveness and scale status must remain distinct.
11. The materialised Approve submodule must point to the merged credentialing commit.
12. The release must preserve a clear next organisational gate rather than imply implementation completion.

## Acceptance

- Parent compatibility manifest passes Python 3.14 validation.
- Parent CareOps Approve gitlink equals the merged Approve commit.
- All mandatory child modules are recorded as merged at immutable commits.
- Policy Atlas collection is recorded at its merge commit.
- All production and effectiveness claims remain false.
- A release receipt and Conductor evidence record are present.

## Exclusions

- CHHHS policy approval or consultation completion.
- Tenant configuration or deployment.
- Live practitioner or patient data.
- Current-system access.
- Authoritative writes.
- Individual credentialing decisions.
- Claims of benefit or operating effectiveness.
