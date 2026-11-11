# CareOps shared reporting boundary

## Purpose

CareOps Finance supplies reusable Power BI, semantic-model, source-control,
validation, ALM, and deployment patterns to the wider CareOps portfolio. It does
not become the central data warehouse or authoritative reporting repository for
all modules.

## Reusable assets

Other modules may adapt:

- PBIP, TMDL, and PBIR project structures;
- parameterised source and gateway contracts;
- deployment settings and immutable release patterns;
- schema, model, relationship, measure, and report validation;
- role and row-level-security design patterns;
- source-to-report reconciliation and acceptance evidence;
- synthetic sample data and fixture-switch patterns;
- publication-boundary, secret, and environment guards.

Reuse should occur through shared standards, templates, libraries, or versioned
contracts. Copying a complete finance report or semantic model into another
module is not the default.

## Credentialing and PPG assurance

Credentialing dashboards should initially use operational Dataverse views or an
approved source-specific model. Power BI becomes appropriate after:

- the operational source and security model are stable;
- data definitions and identifiers are agreed;
- small-cohort and sensitive-field controls are tested;
- workspace, publication, certification, access, refresh, and support ownership
  are established; and
- source-to-dashboard reconciliation is repeatable.

The finance module may contribute dashboard and ALM patterns, but must not
receive raw credentials, CVs, referee reports, patient information, committee
papers, decision reasons, investigation content, or individual risk scores.

A credentialing semantic model should use privacy-minimised, role-scoped facts
and dimensions. Wider aggregate reporting is permitted only where individuals
and sensitive cases cannot be inferred.

## Modular topology

Finance is maintained as ordinary source at `modules/careops-finance` in CareOps.
It remains an optional standalone capability with independent source-system, data,
gateway, workspace, release and support ownership. Share versioned interfaces and
patterns; source consolidation does not create one deployment or data warehouse.

## AI and Copilot

AI may assist with model documentation, DAX or M drafting, metadata
classification, test generation, anomaly explanation, and report descriptions.
It must not:

- infer financial or clinical facts not present in the source;
- bypass row-level security or publish restricted data;
- change measures, source mappings, access, or reports without review;
- become the decision authority; or
- expose source data or environment details in prompts, logs, or Git.

Every AI-assisted change requires normal code review, source reconciliation,
model validation, and business acceptance.
