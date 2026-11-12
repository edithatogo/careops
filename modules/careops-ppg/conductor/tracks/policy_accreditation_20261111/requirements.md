# MoSCoW: governance and accreditation platform

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| PA-01 | MUST | One cataloguing contract for internal PPGs and external publications/directives/standards, with stable publication and immutable edition keys | Versioned test fixtures, distinct publisher/source/owner and provenance; no duplicate authoritative copy |
| PA-02 | MUST | Explicit source hierarchy and normative force: legislation, HSD, department policy, optional guideline, accreditation requirement, local adopted document | Tests prevent a recommendation, obsolete edition or draft being silently treated as legally mandatory |
| PA-03 | MUST | Distinguish publisher authority, delegated local adoption, document approval, internal assessor and external accreditor | Separate identities and signed/recorded decisions; no inferred delegation |
| PA-04 | MUST | Keep original bytes/hash, source capture, locator and licence/access information separate from derived text and extracted propositions | Exact source/capture references; source unavailable/stale is a visible exception |
| PA-05 | MUST | Scope obligations by health service, facility, service line, specialty/training post, role, edition and effective dates | Reject invalid scope inheritance, retroactive applicability and wrong-site adoption |
| PA-06 | MUST | Reuse existing requirement hierarchy, review graph, crosswalk and evidence versions | No alternate standard/assessment register or schema fork |
| PA-07 | MUST | Model mapping, implementation evidence, internal human assessment, and external finding independently | Presence of a PPG or evidence cannot derive Met, accredited or compliance |
| PA-08 | MUST | Provide deterministic read-only per-scope assurance backlog with unknown/missing/review-required states | Synthetic tests for missing assessment, draft edition, proposed mapping and human decisions |
| PA-09 | MUST | Preserve edition and effective-period change impact, withdrawn/replaced source, downstream policy owners and human change disposition | Immutable old editions; no auto-retirement or silent new effective policy |
| PA-10 | MUST | Support NSQHS second edition and future third edition as independent scheme editions, not interchangeable requirements | Explicit edition mapping and no acceptance transfer |
| PA-11 | MUST | Support configurable college/site accreditation (ANZCA, RACP, RACS) with distinct scopes and scheme-specific rating vocabularies | No forced universal Met score or hospital-to-training-post outcome inheritance |
| PA-12 | MUST | Privacy-by-default with limited synthetic Git fixtures and read-only approval-bound external sources | No raw personal, patient, staff or accreditation evidence committed; no automatic communication |
| PA-13 | SHOULD | Source surveillance with structured change signals, version checks and accountable review queues | Stable, explainable alerts; no HTML-layout change treated as policy change automatically |
| PA-14 | SHOULD | Monitoring of implementation/controls/observations using existing observation/evidence contracts | Observation definition and period, missingness, provenance and sample; no automatic judgement |
| PA-15 | SHOULD | Accreditation readiness overview for each framework/site/service with source gaps and next actor | Unknown is visible; counts are not certification scores |
| PA-16 | SHOULD | Versioned cross-framework mapping where shared evidence genuinely supports distinct requirements | Specific relation, rationale, scope, reviewer, confidence status; never inherits approval |
| PA-17 | SHOULD | Conductor-aware change propagation to Decisions, Process, Clinical Hub, RIMS, Finance only through optional typed interfaces | Consumer absent remains valid, no copy of source records or shadow approval chain |
| PA-18 | SHOULD | Reproducible SharePoint/Power Platform provision, solution component parity, RBAC, restore and version replay | Offline source tests first, tenant readback and native permission tests separately |
| PA-19 | COULD | Cited text comparison/extraction and candidate obligation/mapping suggestions using models | Human-reviewed, provenance-bound, optional, secure, abstaining; no model-generated authority |
| PA-20 | COULD | Published standards monitor/dashboard exports and evidence pack assembly | Clear provenance, immutable evidence refs and current source edition; export is not certification |
| PA-21 | WON'T | Automatically assign accreditation ratings, attest to clinical implementation, make a legal conclusion or publish unapproved documents | Fail-closed |
| PA-22 | WON'T | Require premium connectors, a new central business database, Copilot, live tenant access or a new approval bureaucracy for the core | Independently installable standard-connector mode |

Each MUST is a code/contract and test obligation, **not** a claim this feature is currently implemented.
