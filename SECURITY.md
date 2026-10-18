# Security policy

This repository must not contain patient, employee, applicant, clinical,
workforce, operational, authentication, tenant-secret, or other confidential
information.

Report suspected exposure privately to the repository owner. Do not create a
public issue containing sensitive evidence. Rotate exposed credentials through
the relevant service owner and remove sensitive history using an approved
incident process rather than an ad-hoc force push.

Every component must enable the maximum security controls available to the
current account and host, subject to tenant policy and without requiring new
administrative authority.

CI uses full parent-history secret detection, source-boundary checks, bounded
configuration fuzzing, hash-locked dependency auditing, workflow syntax/security
analysis, PR dependency review and CodeQL. Public checks use read-only tokens;
only CodeQL's job may upload security results. No pull_request_target execution,
private submodule checkout or tenant credential is required. The stable Security
gate fails when any of its required security jobs does not succeed.
