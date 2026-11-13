# Medical Job Planning requirements — MoSCoW

The numbering below is normative for this Conductor programme. MJP-R31–R42 incorporate the [W-1 pre-implementation decisions](pre-implementation-decisions.md); these are contractual requirements, not confirmation of local industrial adoption. Implementation tests and native evidence must trace back to requirement IDs.

| ID | Priority | Requirement and acceptance |
|---|---|---|
| MJP-R01 | Must | Independently installable and usable module; absent CareOps siblings and AI have no effect on create/revise/approve/retrieve core. |
| MJP-R02 | Must | One canonical, effective-dated distinction between practitioner, appointment, position, contract, service assignment, plan, sessions, approved version, roster and observed activity. Never infer actual work from planned sessions. |
| MJP-R03 | Must | Source-qualified identifiers; immutable submitted/approved plan payload hashes; independent effective, observed, issued and superseded timestamps; consistent UTC and CHHHS-local calendar semantics. |
| MJP-R04 | Must | Rules include dated authority, owner, version, applicable employment instrument/classification, exceptions and human override provenance; synthetic annualised hours, CST fraction, 0.5-hour tolerance and fixed review anchor are non-operative until adopted. |
| MJP-R05 | Must | Deterministic reconciliation of cycle/session hours, CST, annualised commitments, rounding/overlap, leave and part-time arrangements; reject conflicting declared totals. |
| MJP-R06 | Must | Practitioner can save and compare drafts, submit an immutable version, receive actionable review reasons, see effective state and historical versions; concurrency never silently overwrites. |
| MJP-R07 | Must | Human consultation, clinical review, workforce/industrial review and delegated approval have separately defined accountable authorities; no self-approval, stale grant, role spoofing, unauthorised bypass or automatic adverse employment decision. |
| MJP-R08 | Must | A single authoritative decision path within a module deployment; optional Approve/Decisions adapters record reviewed external authority without manufacturing a duplicate approval. |
| MJP-R09 | Must | CAS/ETag, idempotency and durable multi-list saga reconciliation; 412 conflict, duplicate trigger, 429 throttling, retry, lost connection and crash-after-head-commit are explicit negative tests. |
| MJP-R10 | Must | Least-privilege SharePoint ACLs and managed service identities enforced on physical list, item, library and direct URL/API access, not Canvas visibility or caller-supplied UPN. |
| MJP-R11 | Must | Privacy impact assessment and records retention/legal-hold decision before pilot; prohibit staff records, tenant IDs, credentials, email recipients or operational snapshots in public Git or CI artifacts. |
| MJP-R12 | Must | Editioned review schedule, no-change attestation, future-effective activation, supersession, return/reject and revoked delegation semantics; full replay and historical as-of view. |
| MJP-R13 | Must | Native solution-aware app and functional cloud flows, accepted connector mappings, connection references and environment variables; canary -> development -> test -> production with separate approvals and recovery receipts. |
| MJP-R14 | Must | Core uses standard SharePoint/M365 connectors by default; licences, solution infrastructure and DLP must be verified for each target. No hidden premium or Fabric dependency. |
| MJP-R15 | Must | Independent source gates and native runtime gates; never treat inert WDL, hand-authored Canvas specs, generated solution archives or synthetic REST tests as successful tenant execution. |
| MJP-R16 | Must | Reviewers can access only plans within current authorised service/delegation; practitioner, HR/IR, delegate, records and operator responsibilities are specified and tested for current and historical versions. |
| MJP-R17 | Must | Read-only/access-limited monitor and operator recovery queue; partial or truncated pagination, stale data or inaccessible scope must display incomplete/unverified, not zero/compliant. |
| MJP-R18 | Must | Full accessibility validation (keyboard, screen reader, contrast, focus/touch, cognitive load) and usable workflow on representative devices. |
| MJP-R19 | Must | Email/Teams delivery Off by default and fail-closed; any email delivery requires explicit human approval of exact recipients, content, attachments and scope consistent with CareOps AGENTS.md. |
| MJP-R20 | Must | Canonical generated record uses controlled Word/SharePoint document templates, maintains actual version/edition, approval evidence, checksums, issue/retention history, permissions and retrievable recovery. |
| MJP-R21 | Should | Service-level aggregate projection with role-approved small-cell suppression and data-completeness flags for Workforce BI, without raw individual plan leakage. |
| MJP-R22 | Should | Optional versioned PPG references; policy expiry or unavailable PPG fails closed for *new* operative decisions while preserving authorised read-only history. |
| MJP-R23 | Should | Optional request/result adapters with Approve; append-only event export to Process; no sibling dependency and schema negotiation/rollback tests. |
| MJP-R24 | Should | Service coverage, establishment reconciliation, cost and FTE mapping with verified authorised denominators and explicitly labelled modelling uncertainty. |
| MJP-R25 | Should | Evaluate net effort, duplicate entry, practitioner/approver usability, approval lead time, rework, CST displacement/recovery and unavailable source periods against baseline. |
| MJP-R26 | Should | Bound storage, audit growth, unique permission scopes, indexed SharePoint view patterns, partition and retention strategy proven against plausible 3–5-year scale. |
| MJP-R27 | Could | Separate optional Dataverse solution/profile if its record security, transactions or scale demonstrably justify licence/operational complexity. |
| MJP-R28 | Could | Approved de-identified or synthetic scenarios to CareOps Sim and cost-optimisation tools; never feed simulated outputs back as actual employment or rostering decisions. |
| MJP-R29 | Could | Advanced aggregate forecasting and research-grade capacity evaluation with provenance, prespecified methods and uncertainty bands. |
| MJP-R30 | Won't (core) | AI-generated approvals, employer compliance claims without industrial sign-off, premium-first redesign, public Git staff data, automatic credentialing/employment actions, source-code-only native acceptance, and automatically sent mail. |

| MJP-R31 | Must | Under MOCA7 or other verified adopted instrument, calculate SMO CST from contracted ordinary fortnightly hours with correct classification/effective dates. Distinguish entitlement, planned allocation, observed access, interrupted/protected time and recovered time. Document location, second-income and fatigue-related restrictions for responsible interpretation; don't misapply to RMO/VMO. |
| MJP-R32 | Must | A legitimate industrial shortfall, unresolved disagreement or individual arrangement can be represented transparently without a manufactured compliant plan or forced rejection; effective-dated human adjudication and retained historical versions. |
| MJP-R33 | Must | SharePoint Standard versus optional Dataverse storage ADR before native build: actual physical ACL, permission-scope forecast, inherited permissions, indexed/fully paged reads, CAS/saga recovery, 5-year data growth, support/licence/TCO and independently verifiable restore. Security failures block the chosen option. |
| MJP-R34 | Must | All inbound session flags and temporal/numeric fields strictly validated (not truthiness or implicit coercion); literal strings `"false"` and `"true"` are rejected as Boolean values. Regression test reproduces and fixes the v0.4.2 parser defect before source adoption. |
| MJP-R35 | Must | Negotiated states and counterproposals separated from formal delegated decisions and issued plan versions. Preserve disagreement, conditions, escalation, amendment, future effect and an unambiguous single authoritative plan writer. |
| MJP-R36 | Must | Executable cross-field schema and business invariants: eligible=observed+missing when source coverage known; scope and metric grain match; suppression must null private numeric fields and envelope flags agree; effective time and as-of ordering validated; unsupported event/status permutations rejected or quarantined. |
| MJP-R37 | Must | Native flow trusts independently authenticated actor, connection identity and current delegation at the server boundary; no Power Apps supplied UPN/role, run-only flow owner connection or UI hiding constitutes authorisation. Test direct URL and revoked authority. |
| MJP-R38 | Must | First usable fictional SMO plan supports draft, negotiated amendment, local accountable human review, delegated approval, issued immutable history and an unresolved dispute without needing other CareOps modules, premium licensing, email or real staff data. |
| MJP-R39 | Should | Source-controlled, versioned activity taxonomy and metric dictionary distinguishing ordinary/on-call/recall, planned/actual, clinical/CST, funding, location, service, entitlement and source-verification status; no unowned measure transformations. |
| MJP-R40 | Should | Test stack uses maintained Playwright/PAC/Solution Checker and module calculation/parity/negative-case tests; new development must not rely on deprecated Power Platform Test Engine. Verify 500/5,000+ record query correctness and labelled partial reads. |
| MJP-R41 | Should | Preserve first-party clinician and Clinical Director experiences with accessible negotiation, counterproposal, reason-coded return, service coverage context and no conflation of individual plan validity with staffing sufficiency. |
| MJP-R42 | Should | Predefine baseline evaluation of effort, net burden, fairness, amendments, review delay, rework, security, error rates, clinical support delivery and unintended service impacts; publish uncertainty and avoid causal claims without evaluation design. |

## Release-blocking negative acceptance scenarios

1. Practitioner accesses another service's plan using a copied direct list URL or API key: deny and record controlled trace; the plan content must not leak.
2. Reviewer loses acting delegation after opening a form but before submitting: decision rejected or rerouted; no stale grant accepted.
3. Two users submit same head generation: one conditionally commits, other gets explicit conflict with no overwritten approved history.
4. Worker dies between immutable artifact write and head CAS, or between head CAS and operation receipt: bounded reconciliation reaches one correct state; ambiguous cases quarantine.
5. Same operation ID arrives with different payload/actor/command hash: reject; valid identical replay returns same outcome.
6. Policy edition changes after submission: retained policy and as-of review requirements remain explicit; no retroactive silent recalculation.
7. Annualised inclusion mode, part-time allocation or CST formula disagrees across Python, native Power Fx and flow: release blocked by fixture parity failure.
8. 5,001+ scope/query records, many role-specific ACLs, 429 retry and paged reads: never silently truncate or leak; measured performance within adopted SLO.
9. Delegated approver submits for own plan, invalid effective interval, wrong service or altered version hash: deny; no auto-approval path.
10. Module deployed without Workforce/PPG/Approve/Process: full core scenario still works using approved local policy snapshot and documented external human governance.
11. Report consumer lacks entitlement or source completeness: no worker-level export, no false zero and no mandatory dashboard dependency.
12. Unauthorised email, attachment or recipient change: no send; existing drafts and non-email business operations continue.
13. Corrupted/partial exported document: do not issue; retain approved source and reconcile; earlier issued historical copy remains retrievable.
14. Independent clean-tenant install/upgrade/uninstall/restore and previous-version recovery: no loss or reclassification of authoritative plans.
