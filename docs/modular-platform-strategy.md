# Modular platform strategy

## Current decision — 8 November 2026

CareOps consolidates maintained reusable source into one repository while every
module remains optional and independently usable. Ordinary integrated module
source is the default for the selected consolidation programme. External sources
and exact-pinned gitlinks remain until their admission tasks are complete, or
where an independent engine such as MCHS should retain ownership.

The previous permanent-polyrepo recommendation is superseded by the user's
consolidation direction and the integrations already present. Physical source
location does not determine native record ownership, deployment or permissions.

Use [the standard-suite decision](standard-suite.md) for module responsibilities,
Clinical Hub's optional Decisions relationship, PPG's policy-management role,
the dataset catalogue, premium extensions and lean governance.
Use [the executable migration queue](source-migration-plan.md) for remaining repos.

The default selected capability uses non-premium Microsoft 365 or its existing
portable offline route. Premium/Copilot work is retained as optional source.
Modules exchange versioned references, events or files and retain manual fallback
when another provider is absent. There is no required shared operational database.

Do not infer native deployment, entitlement, business approval or clinical authority
from a source merge. Preserve current owners, private recovery references, exact
checks and explicit send-approval boundaries.
