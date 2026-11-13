# W-1: pre-implementation decision and vertical-slice contract

**Status:** proposed planning gate (13 November 2026). No CHHHS industrial policy was adopted, no tenant accessed, no native action taken. All W-1 tasks remain OPEN. This track amends, not replaces, existing W0–W6; it creates no new approval board or operational authority.

## Intent and sequencing

**Before coding or importing the native solution, resolve the design decisions below.** Pure source triage, rights scanning and test reproductions may proceed without a tenant or policy owner. Native storage provisioning, workflow approval and business-rule deployment cannot proceed on assumptions. Reuse existing CareOps source protection and Conductor reviewers.

| ID | Decision / evidence package | Must-produce evidence and stop rule | Status |
|---|---|---|---|
| MJP-P01 | Current industrial instrument and applicability | Verify latest effective MOCA7 and relevant award, preserved policies, classification, contract and individual variation; separately identify SMO/RMO/MPPP/VMO and special arrangements. Do not generalise SMO CST to every medical employee. Map source, clause, effective interval, confidence, HR/IR adjudication owner and machine-rule candidates | Open |
| MJP-P02 | CST and entitlement semantics | MOCA7 cl.11.18.3–11.18.10: distinguish minimum individual 10% of contracted SMO ordinary fortnightly hours, allocated/planned CST, observed access, consultation, displaced time and recovery at an appropriate time. Note restrictions on location, second income and fatigue substitution. Treat eligibility/individual variations separately. Synthetic 0.5h tolerance, fixed review anchor and annualised modes are unapproved | Open |
| MJP-P03 | Security and physical persistence ADR | Compare SharePoint Standard versus optional Dataverse using actual permission cohorts, access-revocation latency, per-item unique permission scopes, linked record/history ACL, multi-list saga consistency, 5-year growth, list indexing/delegation, governance/licence and recovery. Recommend standard SharePoint only if testable: Microsoft recommends <5,000 unique scopes per list/library (supported maximum 50,000). Prefer inheritance and group/site-level partition where needed | Open |
| MJP-P04 | Domain schema strictness | Introduce strict input schema for boolean flags, bounded integers, fractions, times and decimal serialisation; reproduce v0.4.2 `bool("false") is True` defect in a failing test, then fix in the source-admission implementation slice; no malformed boolean strings or silently coerced numbers accepted | Open |
| MJP-P05 | Negotiation/disagreement workflow ADR | Identify negotiator, Clinical Director, workforce/industrial reviewer and authorised delegate by effective-date role; explicitly model proposed, counterproposed, agreed, conditionally agreed, disputed, escalated, returned, authorised, issued and effective; human adjudication and preserved document history | Open |
| MJP-P06 | Contract semantic invariants | Extend v1 wire schema, metric dictionary, source-qualified rule/authority references, quality as-of and population reconciliations; executable negative cases for mismatched quality counts, missing attribution, invalid timestamps, wrong service scope, suppression leakage, revoked identity and conditional-decision evidence. Schema valid alone is not acceptance | Open |
| MJP-P07 | Native identity proof and test stack | Draw trust boundaries (Canvas caller, flow-run connection owner, SharePoint principal, verified reviewer/delegate); prohibit caller-provided UPN/role from granting authority. Confirm current PAC, Solution Checker and Playwright test approach; deprecated Test Engine must not be new dependency. Prove denial using attempted spoofed caller/flow owner and direct URLs | Open |
| MJP-P08 | Activity ontology and metric ownership | Versioned activity taxonomy with orthogonal CST treatment, direct clinical care, service/site, schedule and industrial category, education, research, governance, on-call/recall, supervision, funding and source; canonical metric definitions and independent actual-vs-planned grain | Open |
| MJP-P09 | Practitioner-first UX and evaluation | One navigable draft -> negotiation/counterproposal -> review -> signed decision -> immutable record vertical slice with adverse/disagreement route; concise accessibility design and prespecified baseline for human effort, rework, errors, coverage and user trust | Open |
| MJP-P10 | Gate review and change control | Record ADRs, policy-owner/records/privacy/security/Power Platform review responsibilities, open uncertainties, design decisions, issue links and exact source/test receipts; W-1 exit only for validated local decisions, native/industrial signoff separately remains G2/G5 | Open |

## Industrial-rule evidence register: example, not an operational policy pack

| External authority | Eligible group / business rule candidate | Implementation caveat |
|---|---|---|
| [MOCA7 (QIRC CB/2025/128)](https://www.qirc.qld.gov.au/sites/default/files/2025-11/2025_cb128.pdf), certified 29 Oct 2025, cl. 11.18.3–5 | Individual SMO clinical support time is protected ordinary-hours time; minimum 10% of contracted ordinary hours *per fortnight*; determine duties in consultation with Clinical Director | Candidate rule `smo_cst_minimum_fraction=0.10` applies only when classification, entitlement, effective date and overrides validated. The source text also requires consultation and time at an appropriate later point when fortnightly access is not possible |
| MOCA7 cl.11.18.6–10 | Location approval, secondary-income restriction, factors for amount, and not fatigue mitigation | Model as separately reviewable non-hours conditions, not silent arithmetic tests; no assumption that compliance in all dimensions is established by a percentage |
| MOCA7 cl.11.5, 11.7–8, 11.11–17, 11.32 | Ordinary hours, extended span, roster, penalties, on-call, recall, preserved individual arrangements | Scope/eligibility and employment conditions differ; distinguish planned allocations from paid/actual hours |
| [Queensland Health current awards/agreements register](https://www.careers.health.qld.gov.au/working-for-us/awards-agreements-and-orders) | Authoritative discovery of current coverage (MOCA7, Medical Officers Award, visiting medical officer arrangements, etc.) | Recheck source and date at policy adoption, preserve exact version/hash and industrial-owner interpretation; never infer generic cross-class applicability |

**Policy-pack shape:** `authority_id`, `source_uri`, `source_digest`, `clause`, `rule_id`, `eligibility_predicate`, `effective_from/to`, `interpretation_status`, `adoption_owner`, `adoption_receipt_ref`, `calculation_version`, `negative_cases` and `superseded_by`. Status starts `reference_only/unadopted`; only reviewed and adopted rules can control decisions. A plan may remain disputed or show an evidenced shortfall without fabricated compliance.

## Storage decision record (P03)

Evaluate separately: **confidentiality**, **security isolation**, **operability**, **atomicity/reconciliation**, **licensing**, **portability** and **recoverability**. No blanket score independent of actual organisation configuration. Each candidate must demonstrate:

- A practitioner cannot access an unrelated plan through direct SharePoint/REST/file endpoints or history, including copied links.
- A Clinical Director can see only currently permitted service allocations and loses the right after delegation revocation; service-scope membership is server-qualified.
- Minimum five-year scale with >5,000 synthetic plans and representative distributions, indexed queries, all pages and source completeness; evaluate permission-scope counts separately from item counts and validate disclosure controls.
- Multiple contributors can update different drafts, while immutable approved records and CAS generations remain consistent under 412/429/5xx/crash/replay.
- Daily operations, list/library/site permissions, recovery and support licence/capacity are quantified. Dataverse is optional and separately entitled, never smuggled into standard-core dependencies.

**Decision rule:** SharePoint Standard proceeds only if critical ACL, completeness, correctness and recovery tests can be satisfied with maintainable support. Any failure requires redesign/partitioning or a documented Dataverse alternative, **not** bypassing security to retain a non-premium label.

## First vertical slice — mandatory, fictional

One synthetic SMO position and verified fictional appointment; an effective-dated MOCA7 *reference-only* rule pack; an ordinary-hours fortnight with correctly allocated CST; a negotiated counterproposal and resolved/recorded disagreement; server-side verified delegated authorisation (test identity); an immutable issued plan; exact source/effective dates and a retrievable history. Deliberately test incorrect boolean strings, two conflicting CAS writes, policy-edition changes, delegation revocation and direct-link access denial. No other CareOps module, premium connector, staff data or automatic email is required.

**Gate outcome classifications:** `accepted-source-design`, `deferred-to-native-qualification`, `blocked`, `not-applicable`. Never label source-design closure as tenant approval, verified industrial compliance or production readiness.

## Official technical references (reviewed 13 Nov 2026)

- [SharePoint unique permission scope guidance](https://learn.microsoft.com/en-us/sharepoint/manage-permission-scope) — recommendation <5,000; supported limit 50,000, and permission-inheritance trade-offs.
- [Power Apps delegation overview](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/delegation-overview) — nondelegable results default to first 500 records; current maximum configured cap varies by release, so prove completeness rather than relying on a number.
- [Power Platform Test Engine deprecation and Playwright replacement](https://learn.microsoft.com/en-us/power-platform/test-engine/playwright) — deprecated April 2026; use maintained Playwright route.
- [Power Automate run-only connections](https://learn.microsoft.com/en-us/power-automate/create-team-flows) — owner-provided connections can execute rather than the invoking user's permissions.
