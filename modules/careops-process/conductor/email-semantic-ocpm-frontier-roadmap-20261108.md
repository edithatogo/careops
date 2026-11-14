# Email-derived object-centric process intelligence: frontier roadmap
**Planning baseline:** 2026-11-08  
**Canonical source:** `edithatogo/careops/modules/careops-process`  
**Status:** proposed architecture and executable backlog; not production implemented or tenant-authorised.

## Scope and boundaries
- Model communication as an observed, immutable event stream first; enrich with inferred work objects/events in a distinct second stage. Never rewrite Stage 1 observations.
- Keep processing, business decisions, authority/approval, and workflow action separate. Email text reporting a decision is not evidence that the decision was validly made.
- Require no Fabric capacity, premium Power Automate licence, tenant-wide permission, LLM, hosted GPU, graph database, or bespoke UI in the baseline. Every one is an optional provider behind feature flags and contracts.
- Keep the generic process-intelligence core independent of credentialing, policies, committees and other domain packs. Keep CareOps Decisions authoritative for governed decision events and Kairos/careops-sim optional consumers.
- Existing Outlook acquisition and live-governance tasks remain with [#171](https://github.com/edithatogo/careops/issues/171), [#172](https://github.com/edithatogo/careops/issues/172), [#173](https://github.com/edithatogo/careops/issues/173), [#174](https://github.com/edithatogo/careops/issues/174); CI/security owner with [#167](https://github.com/edithatogo/careops/issues/167), [#168](https://github.com/edithatogo/careops/issues/168) and [#170](https://github.com/edithatogo/careops/issues/170). Never portray hypothetical/synthetic source events as live facts.

## Target interfaces and event semantics
**Stage 1: immutable communication acquisition.** Source adapters (authorized Outlook standard connector, optional Microsoft Graph, imported RFC 5322 EML/MBOX, future MSG/PST) emit canonical `MessageObserved` facts, source coverage manifests, and distinct `Message`, `Conversation`, `Mailbox`, `PersonIdentity`, `Attachment`, `DocumentVersion` objects. Track `sent_at`, `received_at`, `observed_at`, source and stable source identifiers, mailbox-specific duplicate views, provenance, retention and permission scope. No NLP requirement. For imported files, qualify [Stalwart mail-parser](https://github.com/stalwartlabs/mail-parser) first and [mail-threading](https://docs.rs/mail-threading/latest/mail_threading/) as RFC references-based fallback. Prefer source-native thread IDs when trustworthy. Do not equate forwarded/replied headers with an independent work-item case.
**Stage 2: separately authorised content enrichment.** Temporary, access-governed content readers may process email bodies, quoted chains, attachments, office documents and supported OCR outputs. Distinguish `Claim`, `Request`, `Commitment`, `ProposedDecision`, `DecisionCommunicated`, `VerifiedDecision`, `Task`, `Deadline`, `Document`, `ActorRole`, `BusinessEvent`, `UnresolvedReference`. Annotate assertion time versus claimed event time, tense, negation, uncertainty/modality, author versus actor, extraction method/model version, corpus position (protected source span), source hash, confidence and adjudication status. Treat LLM extraction as untrusted inference; reconcile against authoritative system facts when available.
**Interchange.** Maintain `OCEL 2.0` JSON/XML/SQLite interoperability (including E2O/O2O qualifiers and typed attributes), projection into case-centric XES/Parquet without losing canonical object-centric representation, and an independent richer provenance/evidence graph. Preserve clear `observed / asserted / inferred / corroborated / disputed / rejected` states. A graph link may be plausible without qualifying as an observed event. Version and replay all transformations.

## Standard/ontology contracts
- OCEL 2.0 for process event interchange; IEEE XES for case-based interoperability.
- W3C PROV-O (Entity/Activity/Agent, source and derivation) for provenance; Schema.org EmailMessage/Message/Action/Person/CreativeWork for communication semantics; W3C ORG for organisations, posts and memberships.
- BPMN 2.0 and DMN for reference workflows/decisions; W3C OWL-Time for intervals, SKOS for activity taxonomy and SHACL/JSON Schema for contract validation.
- RFC 5322, MIME, Message-ID/References/In-Reply-To; Microsoft Graph identifiers/delta scope when approved.
- Optional FHIR Workflow for healthcare domain events; do not turn a generic task contract into an implicit clinical record.
Publish versioned crosswalks, source URLs, licence provenance, mapping tests, round-trip guarantees and rejected/unsupported mappings. Fabric Ontology imports only a subset of RDF/OWL and its Graph is a labelled property graph: map explicitly, never claim lossless RDF semantics.

## Mining-engine strategy
Default: qualify Rust4PM `process_mining` (MIT/Apache-2.0) as Rust-native engine, with pinned version and a stable engine adapter interface for import/export, DFG/OCDFG, Alpha+++, Petri nets, variant alignment, token replay, OC-DECLARE, and basic statistics. Preserve the established Python/Polars API using `r4pm` bindings where parity holds.
Retain current deterministic `careops_process.mine` outputs as baseline/reference until replacements pass existing tests. PM4Py is **optional and licence-gated** (AGPL/commercial review), used only in separately qualified research/advanced lanes and for benchmarking; never a default runtime dependency. Compare additional PM4Py capabilities before porting: Inductive/Heuristics mining, soundness, process-tree transformations, extensive organisational mining, resource profiles, process performance, alignments, simulation and predictive monitoring. Contribute suitable generic implementations upstream instead of accumulating custom untested engine code. Benchmark with version-pinned synthetic/OCEL reference corpora for semantic equivalence, runtime, peak RSS, scaling and deterministic replay.

## Evidence graph / GraphRAG
Build an engine-neutral, bitemporal evidence graph with typed event, object, agent, message, claim, source span, document version, relationship and decision nodes; edge qualifiers, permissions, validity and system-observation times; conflict and alternative-hypothesis links. Support deterministic traversals and typed queries before generative retrieval.
Optional adapters: Microsoft GraphRAG for local/global/DRIFT retrieval, and Fabric Graph/Fabric IQ Ontology/Data Agent for approved enterprise materialisation and NL2GQL. Fabric remains an optional managed provider; Power BI consumes governed event and graph-derived **tabular** projections, rather than serving as the graph/GraphRAG engine. GraphRAG results are answers/hypotheses with citations and explicit abstentions, not process facts or decisions.
Evaluate no-RAG, vector-only, graph-only, graph+vector and full GraphRAG against adjudicated cross-thread questions (evidence retrieval, entity disambiguation, temporal questions, contradiction detection, grounded process-family reconstruction). Compare recall/precision, false-link rate, faithfulness, cost and query latency.

## Fluent 2 frontend constraint
Prefer native Power Apps **modern Fluent 2 controls** and model-driven UI; avoid building a custom React shell for ordinary forms/queues. For a genuinely missing custom view, use `@fluentui/react-components` v9 (React) and PCF React platform libraries with qualified platform-supported versions, theme tokens, accessibility and dark/high-contrast themes. Existing graph/OCEL viewer engine may be embedded only as a specialised visualisation component, with Fluent 2 controls for buttons/forms/navigation. Do not introduce Fluent v8, handcrafted controls or unmanaged CSS design tokens. Power BI uses native report visuals; use a graph provider for traversals. Add static dependency checks plus snapshot/a11y and keyboard navigation checks for any created frontend. The present source shows no standalone React app to migrate: audit native Canvas/Teams assets before claiming Fluent 2 conformance.

## Ordered independent work packages and acceptance
**P0 — Baseline/contract reconciliation (first).**
- Inventory current code, contracts, generated Power Platform assets, live/open issues, ontology semantics, feature/licence status, existing tests, UI presence, data source capabilities.
- Freeze current fixtures and expected outputs; map historical standalone repo to active `careops` module and avoid opening duplicate live-ingestion tasks.
- Acceptance: machine-readable capability/coverage matrix with `implemented / partially implemented / experimental / not implemented / deployment-gated`; no false claims of live completion.

**P1 — Stage 1 email portability and OCEL interoperability.**
- Add versioned source adapter interface; qualify `mail-parser`, RFC threading fallback, attachment metadata and multi-mailbox dedup, clock/order/duplicate variants, source coverage and reconciliation.
- Export/import standard OCEL 2.0 and projection into XES with round trips and independent parser cross-check.
- Acceptance: 100% preservation of adjudicated synthetic event identities/relations, deterministic replay, no restricted bytes in analytical outputs, explicit incomplete-source flags, fuzz/property tests for malformed email and missing headers.

**P2 — Rust4PM engine qualification and parity.**
- Compare all used current algorithms and optional PM4Py modules; implement adapter; version pin and isolated CI; focus on reducing duplicate hand-coded algorithms.
- Acceptance: parity within specified per-metric tolerances, lossless cross-language identities, benchmark receipts on mixed small/large logs, controlled fallback and licensing gates.

**P3 — Stage 2 governed semantic extraction.**
- Add transient content boundary with classification and approved source scope, malware/zip-bomb protection, Office/PDF/text/HTML extraction via maintained libraries, safe quoted-text handling, signature separation, document-version clustering, language detection and optional OCR.
- Develop rules + traditional NLP baseline, optional local-model pipeline, constrained typed output, temporality/negation/agent-role/commitment extraction, model provenance and reviewer correction.
- Acceptance: entity/activity/request/decision precision-recall against independently adjudicated test corpora; source-span citation and non-invention checks; deterministic reject/abstain path, prompt-injection tests, deletion/retention and replay tests.

**P4 — Cross-source object linking and process discovery.**
- Build typed identity resolution with aliases, organisational roles over time, authoritative record links, uncertainty and negative/conflicting relationships; review queue for merges/splits.
- Add organisational mining, handoff/rework, interrupted work, SLA/business-hours handling, unknown start/end, concept drift, variants, concurrency, pathway compliance and missing-data sensitivity.
- Acceptance: calibrated link confidence, false-positive ceilings, independently verifiable process outputs and explicit distinction between observation, causal hypothesis and governance authority.

**P5 — Optional evidence graph and retrieval.**
- Implement local graph adapter and temporal/provenance queries before GraphRAG; run benchmark against simpler text/graph retrieval.
- Acceptance: no uncited material claims, protected source access remains enforced after traversals, contradicted evidence shown, dynamic graph updates/retractions tested; GraphRAG is only activated on measured value.

**P6 — Fluent 2 UX / reporting / optional Fabric.**
- Inventory actual native UIs; replace any obsolete Fluent v8/custom controls with native modern controls; add only minimal v9 PCF for features absent from native controls. Publish versioned analytical projections for Power BI.
- Optional Fabric adapters for Ontology/Graph/Data Agent and OneLake, with explicit licence/preview/location/permission gating and loss-aware ontology mappings.
- Acceptance: zero unapproved custom UI controls, WCAG-oriented a11y and responsive checks, no fabric/premium dependency for baseline, no production-availability claim based on source tests.

**P7 — Research/validation and frontier extensions.**
- Independent email/process corpora (e.g., public Enron plus synthetic/adjudicated cross-system cases), record linkage drift, model calibration and abstention, temporal/historical graph queries, concept drift, uncertainty-aware conformance, social/organisational mining safeguards, operational simulation input for optional Kairos.
- Compare traditional NLP, small local models, frontier LLM and graph-assisted pipelines; blinded adjudication, ablations, provenance-grounded retrieval and repeatable benchmarks. Document ethical restrictions on workforce inference.
- Acceptance: reproducible report with datasets/licences, code, fairness/error stratification, cost and privacy/security evaluation, defensible publication contribution not premised on unsupported frontier claims.

## Security, operational and governance guardrails
- No real mailbox/attachment/record ingest, direct tenant changes, email sends, CI secrets or external-model processing from this roadmap. Every non-synthetic run requires authorised scope, retained private controls, classification, minimisation, purpose-limited access, retention/deletion and actual source-owner decisions.
- Treat email/attachments as **untrusted instructions and potential malware**, never agent/system prompts. Network egress and model-provider routing default off; require redaction or approved local processing as selected.
- Do not persist raw message bodies, personally identifying addresses, clinical information or credentials in GitHub, CI logs, source-controlled fixtures or public issue commentary.
- Distinguish event observed time, claimed occurrence time, validity time, processing time and retention status. Object history and human correction must never silently rewrite previous observed facts.
- Organisations, workloads and people are not interchangeable analytical units: prevent personal performance scoring or inappropriate employment profiling by default. Re-identification and group-size suppression need explicit governance.
- CI: SBOM/licence checking, dependency audit, malicious attachment/parsing fuzz tests, unsafe deserialization/prompt-injection tests, equivalence/property and fault-injection tests, least-privilege source gating, reproducible benchmark fixture hashes.
- No module should require another CareOps module to run: all sibling integrations use optional versioned contracts.

## Recommended dependency references (qualify versions and terms at implementation)
- [Rust4PM](https://rust4pm.aarkue.eu/) / [process_mining crate](https://docs.rs/process_mining/); [PM4Py feature matrix](https://processintelligence.solutions/pm4py/features/).
- [Stalwart mail-parser](https://docs.rs/mail-parser/); [mail-threading](https://docs.rs/mail-threading/); [mailbox-parser](https://github.com/yagaltd/mailbox-parser) as import candidate.
- [OCEL standard](https://www.ocel-standard.org/); [PROV-O](https://www.w3.org/TR/prov-o/); [Schema.org EmailMessage](https://schema.org/EmailMessage); [W3C ORG](https://www.w3.org/TR/vocab-org/).
- [Microsoft GraphRAG](https://microsoft.github.io/graphrag/); [Fabric Graph](https://learn.microsoft.com/en-us/fabric/graph/overview); [Fabric Ontology](https://learn.microsoft.com/en-us/fabric/iq/ontology/overview); [Power Apps modern controls](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/modern-controls/overview-modern-controls); [Fluent 2](https://fluent2.microsoft.design/get-started/develop).

**This file is a proposal and implementation task list only.** Its existence is not proof that any code was changed, dependency qualified, UI converted, tenant deployed, or live event acquired.