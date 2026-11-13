# Registration assurance — pre-deployment clinical safety case v0.1

**Status:** hazard-analysis baseline; controls are requirements, not proof of native efficacy. **Clinical accountable owner and operational risk acceptance:** not yet appointed. **Product owner:** CareOps credentialing governance. No clinical or workforce decision is automated.

## Safety boundary and primary claim

**Claim RA-SC1:** A source-level registration observation must neither create unjustified assurance of clinical entitlement nor produce a materially adverse decision without independent source qualification and accountable human governance. Registration is only one input to credentialing, and credentialing is distinct from approved SoCP and facility capability.

**Safety argument:** source-capability qualification → exact registration identity → lossless current source mapping and time provenance → deterministically segregated factual observation and uncertainty → human verification/escalation → optional Decisions-owned, separately authorised governance workflow. Each boundary requires negative tests and actual native security/recovery evidence before operational use.

| Hazard | Risk mechanism | Preventive and detective controls | Acceptance evidence | Escalation / owner |
| --- | --- | --- | --- | --- |
| RA-H01 False reassurance | Autocomplete absence, positive suggestion, truncated search, stale PIE update, a mock or name-only match treated as verified registration | Enforce provider evidence ceiling; exact regulator+registration identifier; source as-of age; no live source on failure; consumer refuses mock/discovery status | Homonym, five-result omission, blocked 403/429, mock registered, stale and duplicated-origin tests; production source round-trip | Credentialing service owner, technical source owner |
| RA-H02 False adverse finding | Incorrectly joined person, expiry treated as cancellation, translated native category loses restriction, historical status replay | Lossless native categories/restrictions; source conflict queue; no automatic SoCP/roster/HR action; case/version checks; independent verification for material adverse signal | Expired but still registered, non-practising, provisional/limited, restrictions, reinstatement, mismatched profession, concurrent reviewer tests | Credentialing delegate and appropriate professional peer |
| RA-H03 Failure to detect/escalate | Missing eligible VMO/locum/contractor, off-watch rural service, blocked provider, no accountable owner | Authoritative engagement denominator reconciliation; active/unmatched/stale/ambiguous cases; explicit queue owner/deadline; channel-independent manual escalation | Facility/profession/engagement-type coverage reconciliation, process/event timing and alert-delivery readback | Credentialing/workforce operational owner |
| RA-H04 Exposure of sensitive practitioner information | Source payloads or conditions copied into public Git, SharePoint link, dashboards, logging, mistaken email | Minimal references, classed records, provider-use rights, RBAC and direct API/doc access tests, no unapproved sends, retention/hold | Zero unapproved payloads in artifacts/logs; denied direct-link access; source rights checked | Information custodian/privacy officer |
| RA-H05 Missing/incorrect operating context | Registration exists but facility service capability, supervision/endorsement, specific SoCP or engagement no longer supports practice | Explicit separation of registration facts, professional-standing assessment, employment/engagement and Decisions-owned SoCP; clinical peer review | Cross-facility/regional scope, changed supervision, new procedure, lost engagement, revoked condition tests | Authorised local SoCP governance owner |
| RA-H06 Operational recovery fault | Older restored observations overwrite newer checks; duplicate alerts; unavailable tenant or provider creates false all-clear | Append-only provenance and version checks, durable outbox, restore quarantine, readback and manual fallback | Older-after-newer replay, duplicate events, ambiguous send, backup restore and cross-component reconciliation | Native platform/service owner |

## Safety design constraints

1. A green source result **never** means `practice_authorised=true`. Only the existing governed SoCP decision path may establish practice authority.
2. A changed adverse regulator signal is **priority for human confirmation**, not a delegated decision. Local incident/urgent escalation rules govern time sensitivity.
3. Registration categories are multidimensional: general, specialist, limited, provisional, non-practising, conditions, restrictions, undertakings, supervision and specialty/endorsement records can coexist or conflict. Preserve original source vocabulary and valid dates; unsupported meanings remain unresolved.
4. A PIE refresh age (published approximately 24 hours) and public-register update age (approximately 15 minutes) are different. Success at a polling interval is not a real-time regulator guarantee. Serious time-sensitive concerns use a separately approved current-register verification route.
5. Emergency/manual fallback must remain independent of Power BI, Agents, and the polling service. Never depend on a second SharePoint practitioner register.
6. Reviewer disposition history is preserved when new evidence arrives; unchanged replays are idempotent and only material evidence changes reopen downstream cases.

## Predeployment safety assurance and human factors

Before G2, complete an approved risk assessment and table of controls with a named owner, actual protected source access/rights, direct API/record permissions, case priority routing, source freshness targets, reviewer training, human-factors usability and recovery testing. Before G3, independently test rare but clinically important adverse cases; measure missed events and false escalations, case-review latency, coverage gaps, practical operator burden and remaining high-risk scenarios. Do not claim zero false negatives from a small sample; report denominator and confidence bounds. Operating sign-off is required separately from CI and source test success.

### References

- Queensland HSD QH-HSD-034: https://www.health.qld.gov.au/system-governance/policies-standards/health-service-directives/credentialing-and-defining-the-scope-of-clinical-practice
- Australian Commission NSQHS Clinical Governance Standard, Actions 1.23 and 1.24: https://www.safetyandquality.gov.au/national-standards/nsqhs-standards/clinical-governance-standard
- May 2026 guidance: https://www.safetyandquality.gov.au/resources/credentialing-and-defining-scope-practice-guidance-health-services-and-clinicians
- AHPRA PIE FAQ (freshness): https://www.ahpra.gov.au/Registration/Employer-Services/External-data-exchange-services/Practitioner-information-exchange/PIE-FAQ
