# Junior medical onboarding specification

A medical workforce coordinator needs to know who must decide on a commencement request, what is missing, and which decision applies to the current engagement revision. The first release covers intake, manager decision, policy-dependent delegate sign-off, correction and handover to the coordinator. Readiness, credentialing, clinical privileges, training and system provisioning each require separate evidence. An approved request establishes only that its required sign-offs were obtained.

## Reuse from the five privately reviewed flow definitions

| Reference pattern | Use in the first candidate |
|---|---|
| Line manager only | Adapt the single-stage create, wait and record sequence. Resolve the approver from a trusted role map. |
| Delegate only | Reuse the same decision contract for a policy-required second signer. Model a substitute for an absent manager separately. |
| Copy of full approval process | Compare its prior-request lookup with the explicit revision link. Require a fresh decision after material changes. |
| Medical fatigue full approval | Re-read current state after a wait. Route an overdue item to the coordinator queue. |
| Workforce suite access approval | Reuse the first-submission versus resubmission distinction. Replace historical list columns, bindings and notification branches. |

The five JSON definitions supply design patterns. The app source, target list schemas, medical delegation policy, training flow and PDF dependency remain unverified. No importable onboarding solution or confirmed nursing recruitment ownership follows from those definitions.

## Information boundaries

Keep identifiable correspondence, envelope contents, source exports, routing identities and deployment values in private storage. Retain only generic request types, roles, transitions and fictional examples in the modules. Use existing evidence links with role-scoped access. The planning track has no native scope.
