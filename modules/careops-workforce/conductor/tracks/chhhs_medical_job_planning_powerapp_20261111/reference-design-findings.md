# Source-derived design findings — sanitised summary

**Classification:** Public-safe design abstractions only. **Not a source archive, policy approval or industrial legal certification.** Prepared from restricted, off-repository CHHHS draft work instructions and anonymised interpretations of individual and historical multiweek job-plan examples. The source originals, links, employee identifiers, names, actual schedules and individual allocations are **not included** in this repository. Source provenance and approved authority versions belong in CHHHS-controlled storage. Do not reconstitute individuals from this summary.

## Observed design requirements (from supplied source materials)

1. **A prospective agreement, not an attendance timesheet.** The job plan records expected clinical and nonclinical commitments, outputs and enabling resources. Actual roster and activity evidence are separate and used for variance/review, not to retrospectively legitimise excess hours.
2. **Scoped applicability and classification.** The draft encompasses permanent/temporary SMOs and some senior trainee categories, but does not indiscriminately include RMOs/VMOs; private-practice practitioners and corporate/leadership positions have tailored contracts. Treat the draft scope as unapproved and require independent class-specific instrument validation.
3. **Service-first consultation.** Initiation -> confirm industrial terms -> demand/capacity and funded establishment -> clinician self-assessment -> quantified draft -> expected outputs/resources -> documented consultation/representative option -> lawful delegated determination -> roster implementation -> exception monitoring -> formal review.
4. **Hours as the invariant.** Full-time SMO example is 80 ordinary hours/fortnight; a nominal four-hour session is an optional display unit, not a change to industrial hours. Part-time denominators differ. Fortnightly allocations of mutually exclusive ordinary-work activities must reconcile to contracted hours; on-call availability, recall, overtime, leave and professional development entitlements remain distinct.
5. **CST entitlement and recovery.** Draft cites a minimum individual 10% of contracted ordinary SMO hours/fortnight and records delayed CST with reason, displacement hours and agreed recovery. An emergency-medicine specialty provision is mentioned in the draft and must be independently verified against current instruments rather than automatically inferred.
6. **Versioned activity taxonomy.** The source uses C1–C9, S1–S8, L1–L2, T and O with planned workload evidence, leadership portfolios and required travel. One mixed session can have several work functions; for arithmetic, subdivide hours without double counting. Keep explainable mixed-session user experience without mandating minute-by-minute timesheets.
7. **Multiple cycles and annualised components.** Individual examples use five-week repeating schedules and periodic monthly activities that replace, not supplement, the allocated block. Allow arbitrary validated 1–N week cycle patterns, dated substitutions, annualised work budgets and provenance of assumptions.
8. **Capacity and output dependencies.** Outcomes need material enabling resources (clinic rooms, staffing, equipment, administrative support), safe workload ranges, exclusions and quality indicators, not crude individual throughput targets. Clinical leadership, preparation and action follow-up count when properly assigned.
9. **Exception cases.** Service cancellations, persistent excess hours, temporary vacancies, leave cover, approved flexible work, changed scope/FTE, short-term service redeployment and CST displacement each have distinct response/review rules.
10. **Cadenced assurance.** Draft describes early review after material change, service-level periodic exception monitoring and at least annual prospective individual review, separate from appraisal. These are draft proposals until adopted locally.
11. **Approval and representation.** Employee consultation/agreement is recorded separately from employer determination. Unresolved matters, representation, formal dispute route and safe interim arrangements need explicit states, no auto-approval.
12. **Structured export and checks.** Source includes multiweek tabular schedule, minimum dataset, sign-off fields and an approval checklist. Treat output as a controlled rendering of structured data, not a DOCX upload as system-of-record.

## Historical comparator insights (not CHHHS authority)

Historical neonatal and consultant examples in a separately controlled document source illustrate service-on/off patterns, acute/night/weekend duties, portfolio distribution, handover requirements, part-time FTE, multiweek schedules and locally distinct AM/PM representations. They reinforce the need for **cycle-aware scheduling**, optional session views, annualised obligations and cross-service allocations. No individual names, historic schedules or quantitative staff allocations are retained here.

## Outstanding source/authority questions

- Verify whether the draft instruction has completed consultation and adoption; it contains proposal language and incomplete approval metadata. Do **not** describe it as operative.
- Validate the current clauses/edition of MOCA7 and specific emergency-medicine entitlements, notice, overtime/disputes, as well as award/contract variations for each employee class.
- Confirm official CHHHS job-plan templates, actual approval delegations, industrial consultation/representation requirements, recordkeeping/retention and privacy classification.
- Establish permissible custody for confidential reference documents and who may view them. Never upload raw source documents to GitHub, CI artifacts, public test fixtures, pull requests, or telemetry.

## Contract implications

Keep two orthogonal models: (a) prospective position/individual plan and its immutable, approved, effective-dated revisions; (b) observed rostering/delivery evidence and exceptions. The UI should allow qualitative rationale, supported capacity ranges and a concise self-assessment, without classifying all unstructured comments as CST or generating patient/employee performance judgments.

**Synthetic-only fixture design:** independent fake 5-week rotating clinic/ward schedule; monthly governance meeting replacing a block; overlapping mixed C/S work requiring an hours split; leadership hours and 80-hour fortnight under/over reconciliation; 0.5 FTE CST threshold; one-night/week availability plus independently recorded recall; CST displacement and later make-up; acting Clinical Director approval; roster interruption; cancellation for unavailable support; high-demand ward escalation; representation/disagreement and subsequent decision.
