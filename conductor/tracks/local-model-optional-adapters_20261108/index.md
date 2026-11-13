# Optional local-model adapter and qualification gates — 8 November 2026

**Status: proposed source-level design only.** This is not tenant deployment, clinical authorisation, case processing or reclassification of the independent module owners. Reuse N06 optional agents and N09 optional adapters. The `models_lang` catalogue/evaluation harness provides source-qualified model evidence; native CareOps services remain authoritative for records, decisions, delegations and retention.

## Boundaries

- Local inference is **disabled by default**. All model-assisted artefacts are labelled draft; no autonomous clinical, medicolegal, credentialing, executive, committee or legal determination. Do not write outputs into authoritative systems without an accountable human action.
- Source repositories contain only schemas, synthetic fixtures and redacted qualification metadata, never patient/practitioner/incident records, extracts, findings or sensitive aggregates. Preserve `careops-incidents` publication boundary.
- Deployment permits only approved local endpoint identities, encrypted transport when appropriate, allowlisted network routes, disabled external-provider fallback, controlled model installation and no telemetry/logging of prompts or source documents. Network egress denial is testable, not a prompt instruction.

## Contract and first thin slice

1. Establish `ModelQualificationRef` containing candidate HF ID, exact revision, build/quantisation, runtime and device identifiers, benchmark version, licence decision, expiration/revalidation and product-local approval. Import a versioned `models_lang` result, not a mutable 'latest' alias.
2. Define `InferenceRequest` with pseudonymous source spans, minimum-required fields, purpose, sensitivity, jurisdiction, permitted use, timeout and rollback/error semantics. Add schema-conformant `InferenceEvidence` with model revision, optional score, source-span references, missing/conflicting facts, uncertainty, human-review status and trace ID.
3. Start read-only: one synthetic incident signal triage and one synthetic committee-paper draft in isolated test doubles. No PHI, live credentials, production Dataverse write or automation activation.
4. Evaluate competing rule-only, small (Liquid/d1) and larger-reasoning configurations against independent annotated fixtures; measure omissions, false negatives, citation/span correctness, explanation unsupportedness, reviewer workload and drift. A model may be qualified for extraction but not for medical judgement.
5. Version the interface and add kill switch, timeouts, provider identity pin, no-egress proof, logs with content redaction, test failures for missing qualification and rollback test.
6. Consumer ownership: Incidents retains source and Power BI semantics; Decisions retains committee authority and drafts; PPG/Atlas owns versioned policy; clinical-hub remains native. This interface is optional and separately deployed.

## Gates

Source-interface PR may merge after synthetic contract tests, compatibility and licence checks. Live deployment additionally needs organisational information-security/privacy assessment, clinical safety review, legitimate data access, sample-based human validation, retention approval, operational observability and named accountable owner. No claimed clinical use before those gates. Link any product-specific implementation to its existing Conductor track; do not create a parallel CareOps runtime.
