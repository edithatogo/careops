# N02 plan: current requirements and delegations

Owner: Credentialing policy owner, to be named. In progress; source and operational gates remain distinct.

- [ ] N02.01 Obtain controlled-current CHHHS instruments and separate credentialing delegation; accept source version/effective-date and supersession evidence.
- [ ] N02.02 Recheck ACSQHC, QH directive and applicable profession sources; accept a clause/applicability crosswalk distinguishing mandatory rules from guidance.
- [ ] N02.03 Reconcile ordinary, interim, adverse, committee and appeal functions; accept each grant's position, conditions, facility/profession and authority chain.
- [ ] N02.04 Resolve EDMS/CMO title transitions against signed instruments; accept verified authority mappings, not aliases or Teams membership alone.
- [ ] N02.05 Model draft/review/release/withdrawal and effective dates in Dataverse; accept no draft, stale, future or withdrawn profile authorising an action.
- [~] N02.06 Implement restricted editing and independent exact-content approval; accept self-approval, changed-content and reused-receipt rejection tests.
- [~] N02.07 Validate role occupancy, acting arrangements, conflicts and grant conditions at decision time; accept expiry and intervening-role-change negative tests.
- [~] N02.08 Add business-calendar deadlines and path-specific durations; accept boundary/calendar tests against approved rules without AI date arithmetic.
- [ ] N02.09 Implement approved local source snapshots and change-review queue; accept safe human fallback on stale/disagreeing sources without invalidating existing scope automatically.
- [ ] N02.10 Obtain local authority-profile sign-off and maintenance ownership; accept a restricted approval receipt and review schedule before any operational enablement.

## Reviewed source delivery

N02.08 arithmetic: Decisions#14, merge ede4af4493f4e960a50656f09acc2dee5c00582f;
22 native tests passed, 41/41 lines and 52/52 branches covered. Approved local
calendars/rules and native host execution remain open.

N02.06/N02.07 native delegation predicates: Decisions#15, merge
6498e8e75080e7079d2ce91e7bd0efaa9b8b46fd; exact profile release binding,
organization/role/time/conflict/condition checks, default Unverified rather than
Permitted. Final 22 native tests, 132/132 lines and 108/108 branches. Host-resolved
facts are required; the library does not authenticate or verify signed sources.

N02.06 change preparation: Decisions#16, merge
8bf56acbc16d2add7f27f75c94e6e66a88656479; deterministic immutable before/after
fields bound to both full hashes, including removed conditions and grant changes.
Final authority suite 34 tests (12 added), 185/185 lines and 134/134 branches.
This prepares the existing configuration approval, not an extra case-review queue.
Actual Power Apps editing, protected Dataverse persistence and approval stay open.

See [completed source slices and reviewed evidence](completed-source-slices.md).
Each task needs versioned output, validation result, reviewer and date. Current
signed instruments, identities and private approval receipts stay in controlled
records, not this repository. A source slice is not an operationally complete track.
