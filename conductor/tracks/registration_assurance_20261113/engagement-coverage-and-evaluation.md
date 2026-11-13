# Engagement coverage, accreditation and evaluation contracts

**Status:** prospective source specification; no real workforce extracts, no reporting, no regulated decision.

## 1. Engagement denominator / `EngagementCoverage`

The denominator is **all eligible active clinician engagements** in the defined service, period and profession/regulatory policy. Do not create this population from the AHPRA search results. Use authorised employment and engagements from their existing source owners and Decisions' verified practitioner references, including visiting medical officers, locums, contractors, dual-site/rotating clinicians, licensed private practitioners and applicable regional/statewide SoCP arrangements. Preserve engagement-specific rather than deduplicated headcounts: one practitioner may have multiple facility/scope engagements.

Machine fields: source-qualified `engagementRef` (stable), `watchRef` (nullable, non-authoritative), `profession`, `engagementType`, `facilityRef`, `serviceRef` (where applicable), `effectiveFrom`/`effectiveTo` with UTC time and local operational effective date, `sourceRevision`, `sourceAsOfUtc`, `regulatorRequired` (approved policy decision), `monitorEligible` (with rule), `coverageState` (`covered / unmatched / ambiguous / inactive / excluded_by_policy / source_unavailable`), `coverageReason`, `owner` and contract version. Unknowns must not silently shrink denominator. Source mappings do not establish actual employment.

Coverage measures (definition fixed in output manifest): eligible active engagement count; uniquely matched **enabled** registration-watch entries; missing/disabled/ambiguous watches; unknown registration number; profession mismatch; started-never-checked; ended-still-monitored; freshness/currency; eligible practitioner count (separate metric); by profession, facility, rural/remote site, employment type and outreach service. Each carries denominator, as-of, exclusion rule, source coverage, interpretation and privacy suppression for small cells.

## 2. Core evidence and currentness

Regulator `sourceAsOfUtc` is not `retrievedAtUtc` or local check end time. Provider success must specify what fact was confirmed, original source identity, restricted evidence reference, version of native source vocabulary, expiry or check-evidence validity, and any source-age ceiling approved per use case. PIE (approximately daily refresh) and the more current public register cannot be counted as independent regulatory authorities. A source health failure or inability to match must be represented in an **unavailable/unknown** observation, not counted as verified clean.

The review workbench must present original native category/specialty/endorsement and conditions reference, normalised mapping, actual source as-of, check age, current watch/engagement and previous approved disposition. No inferred local SoCP from general/specialist registration.

## 3. Pre-specified silent evaluation

Pre-register sample population by profession, facility, engagement type and past-status prevalence. Independently adjudicate current regulatory facts with authorised manual register checks (where permitted) and credentialing governance, blinded to experimental alert classifications where practicable. Include verified edge-case oversampling, but report deployment-weighted real-world prevalence and separate enriched-case statistics. Blind review of uncertain and negative samples to estimate missed cases, not just alert precision.

Required measures and uncertainty:
- eligible engagements / evaluated engagements / verified-source coverage; age of source;
- identity false match and unmatched rate, including denominator and missed engagement cohort;
- false-positive escalation, missed independently verified material change, sensitivity/specificity/PPV with uncertainty intervals where estimable; severe/rare event zero counts reported with appropriate bounds, not `100% sensitivity`;
- reviewer queue time and service delay; high/urgent alert acknowledgement (defined owner), manual comparator workload and repeat-review burden;
- source/tenant outages, retry/drift rate and time to reconciliation; periodic audit of non-alerted practitioners;
- licence/connector/runtime costs, marginal cost per checked engagement and per true verification, net labour time relative to manual process.

Define a prospective pass/fail threshold for each safety-critical measure with credentialing owner **before** seeing results; do not invent numerical thresholds in source code. A silent pilot cannot establish actual downstream credentialing outcomes or prove the API is contractually permitted.

## 4. Versioned accreditation and policy controls

| Source / version | Scope / relevant requirement | Evidence from monitoring | Explicit evidence ceiling |
| --- | --- | --- | --- |
| Queensland QH-HSD-034, current version checked before deployment | Credentialing, SoCP, approved local process, regional/statewide arrangements, ongoing monitoring, annual self-assessment | Coverage of required cohorts and monitored evidence, exceptions and follow-up process | Not proof of formal SoCP, local delegation, approved facilities or compliant annual statement |
| NSQHS Clinical Governance Standard, 2nd edition, Action 1.23 | Define, monitor and periodically review clinical SoCP | Versioned referral to existing Decisions/SoCP review when relevant regulatory changes arise | AHPRA fact alone does not prove actual defined scope or monitoring effectiveness |
| NSQHS Clinical Governance Standard, 2nd edition, Action 1.24 | Credentialing processes and monitoring/improvement | Checked engagement denominator, exception resolution, observed review lag and quality audit | Does not establish that credentialing was completed or effective |
| ACSQHC Credentialing and defining scope of practice guidance, May 2026 | Risk-based review, suitability, recredentialing and scope | Input evidence and documented human review trace | Guidance is not a separate machine-enforced permission to practise |
| NSQHS prospective 3rd edition | Change intelligence only until formally operative and locally adopted | Versioned draft mapping candidates, migration gap list | Draft controls cannot overwrite currently operative requirements |

The PPG owner stores source document/edition/effective/withdrawn dates and local policy adoption; a test-passing crosswalk does not assert accreditation conformance. Include source URLs, immutable captured edition digest where licensed, and source-currentness review intervals.

## 5. Chosen release architecture

The first proof is **pure synthetic/offline logic**, then an approved **manual registration verification** workflow. The selected full credentialing deployment target is a managed Dataverse solution with optional registration-assurance adapter and existing Decisions-owned practitioner master. A minimal restricted Standard-M365 manual deployment is a distinct optional profile with no automatic AHPRA HTTP ingestion; it must not silently mirror/replace or synchronise the Dataverse credentialing master. One active observation writer per deployment. The provider HTTP/Logic Apps variant is an optional licensed transport and must not compete with Power Automate as an active source record writer.

Native service owner, actual production configuration, AHPRA entitlement/rights, operator identity and cost model must be qualified before G2. No live scheduler/send is authorised by a source-only PR.
