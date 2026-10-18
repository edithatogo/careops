---
name: regulated-ai-assurance
description: Assess and design AI, OCR, NLP, Copilot, agent, or MCP features for CareOps with source provenance, privacy, deterministic controls, human review, fallback, and release evidence.
---

# Regulated AI assurance

Use this skill whenever a CareOps change involves OCR, NLP, an LLM, Copilot,
AI Builder, Copilot Studio, an autonomous trigger, a custom agent, agent memory,
MCP, or a local model.

## 1. State the bounded purpose

Record:

- the user problem;
- why deterministic automation alone is insufficient;
- allowed and prohibited outputs;
- information class and minimum necessary fields;
- model, provider, hosting, region, licence, and support assumptions;
- accountable business, clinical, technical, privacy, security, and records
  owners;
- ordinary non-AI fallback.

Do not begin with a model or vendor and search for a problem.

## 2. Separate source, extraction, interpretation, and decision

Represent separately:

- source document or record;
- extracted field or span;
- confidence and extraction method;
- inferred classification or summary;
- deterministic rule result;
- human review and correction;
- recommendation;
- authoritative human decision.

AI output is not source evidence, policy, verification, recommendation, or
decision merely because it is structured or confident.

## 3. Preserve provenance

For every AI run retain, as appropriate:

- source IDs and source locations or spans;
- input classification and redaction state;
- provider, model, version, prompt, skill, agent, and tool versions;
- retrieval or context sources;
- execution time;
- input and output hashes;
- confidence, uncertainty, and exceptions;
- reviewer, edits, review outcome, and time;
- publication or downstream-use status.

Never place raw sensitive prompts, outputs, documents, identities, credentials,
or tenant details in Git or broad telemetry.

## 4. Define non-delegable decisions

AI must not independently:

- verify identity, registration, qualification, or mandatory evidence;
- determine professional competence, suitability, currency, or service
  capability;
- define or alter scope of clinical practice;
- impose supervision or conditions;
- approve, refuse, suspend, restrict, reduce, revoke, or release to practise;
- decide a review, appeal, employment, disciplinary, financial, legal, or
  clinical outcome;
- publish an authoritative record;
- change production data, access, policy, workflow, or configuration.

The accountable human role, authority reference, reasons, and decision evidence
must be explicit.

## 5. Test against a simpler comparator

Compare the feature with:

- no automation;
- deterministic automation;
- rules plus human review;
- a simpler model or extraction method;
- local/private and approved cloud options where relevant.

Measure accuracy, calibration, false positives, false negatives, abstention,
human correction, time, workload, privacy, accessibility, cost, latency,
reliability, drift, and unintended burden. Use independently curated fixtures;
do not use the same model as both implementation and oracle.

## 6. Fail safely

Low confidence, missing source, model failure, tool failure, unavailable MCP,
policy conflict, stale authority, or unclear classification must:

- preserve the request and source record;
- avoid an adverse or authoritative effect;
- create a visible exception;
- route to the normal human path;
- retain enough evidence for diagnosis without disclosing unnecessary content.

## 7. Gate deployment

Require:

- approved data and records architecture;
- privacy, security, legal, human-rights, accessibility, clinical-governance,
  architecture, support, and continuity review as applicable;
- synthetic and negative-path testing;
- feature flag disabled by default;
- restricted pilot population;
- monitoring and drift review;
- rollback and model or feature exit path;
- explicit separation of repository readiness, environment deployment, pilot
  evidence, operating effectiveness, and scale approval.

For MCP or agent tools, allowlist tools and targets, use read-only or plan-only
access first, and require protected release processes for every production
write.
