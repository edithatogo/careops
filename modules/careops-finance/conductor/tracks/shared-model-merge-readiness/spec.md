# Shared Model Merge Readiness

## Objective

Decide whether the completed VMO Finance and Medical Staff dashboards should remain standalone, become thin reports over a shared semantic model, or use another combined model pattern.

## Deliverables

- Decision framework covering comparison matrix, decision criteria, prerequisites, risk register, and follow-up track trigger.
- Current recommendation documented before dashboard completion so the team has a stable default until validation is possible.
- Gate sequence covering source-control export readiness, SQL contract validation, standalone refresh, model comparison, and ownership/ALM acceptance.
- Candidate register for shared dimensions and measures with current promote/defer/reject disposition.
- Post-SQL-validation evidence checklist that states exactly what must be captured before a merge recommendation.
- Final merge decision deferred until both standalone dashboards are built and validated.

## Requirements

- Compare the completed dashboard models for shared dimensions, measures, and refresh dependencies.
- Identify shared date, cost-centre, organisational, and financial definitions that are stable enough to promote.
- Assess refresh coupling risk if the dashboards are merged.
- Recommend one target architecture: separate reports, shared semantic model with thin reports, composite model, or combined executive report.
- Do not merge models until both standalone dashboards are validated.
- Treat standalone PBIR/TMDL exports as comparison inputs, not as proof that a shared model is ready.
- Require SQL validation evidence before exporting or implementing any shared model TMDL.

## Acceptance Criteria

- Merge-readiness decision document exists.
- Shared definitions are listed with owners and source contracts.
- Risks and tradeoffs are documented.
- Decision gates and post-SQL-validation evidence requirements are explicit enough for another worker to execute.
- Shared dimension and measure candidates have current disposition.
- If a merge is recommended, the follow-up implementation track is created.
- If no merge is recommended, the standalone operating model is documented.
