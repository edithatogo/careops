# N10 plan: mission-critical assurance

Owner: Service assurance owner, to be named. All tasks planned.

- [ ] N10.01 Complete threat model, privacy/records review and clinical hazard log; accept accountable risk owners, mitigations and release stop conditions.
- [ ] N10.02 Run native authorisation and direct-write bypass tests; accept cross-case/profession/facility, acting-role, revoked identity and privileged-user controls.
- [ ] N10.03 Configure and verify Dataverse native backup retention and pre-release backup; accept actual settings and available restore points, not a manifest assertion.
- [ ] N10.04 Restore Dataverse to an isolated approved target with required audit options; accept measured recovery, supported target/region and preserved decision history.
- [ ] N10.05 Reconcile SharePoint evidence, configuration and decision watermarks after independent restores; accept detected mismatch/rollback and no lost revocation.
- [ ] N10.06 Quarantine and re-enable flows/agents after recovery; accept no duplicate letters, replayed approvals or unintended external actions during restore.
- [ ] N10.07 Exercise tenant/identity/region/connectivity outages and read-only downtime procedure; accept stale warnings, limited data, operational ownership and approved fallback.
- [ ] N10.08 Load-test expected and stress volumes including recovery/backlog; accept measured latency/throttling/queue bounds against signed business targets.
- [ ] N10.09 Verify monitoring, audit reads/exports, retention and support alerts; accept technical faults routed to support without applicant blame or sensitive log content.
- [ ] N10.10 Obtain independent cyber/clinical and service-owner acceptance; accept zero unresolved critical release defects, funded support and evidence-based RPO/RTO conclusions.

AI-specific acceptance in N06 is additionally required only when AI is enabled.
A SharePoint extract is not a Dataverse restore and may share its outage boundary.
