# RIMS Power BI source-first coded-field remediation

Current package is **not** a live semantic-model/report update. The exported RIMS publication flow maps SharePoint physical columns field_1–field_20 to descriptive names. The archived research-publications PBIP TMDL source has descriptive Publication and GrantsRegistry columns already. Consequently, the displayed codes may be sourced from a different live model, report binding, List lookup or value dictionary. Do not destructively rename a working model based on the old ZIP.

## Exact observed source
- Archived `research-publications/powerbi/CHHHS Research Publications.SemanticModel/definition/tables/Publication.tmdl`: named Publication fields including CanonicalKey, DOI, SourceSet, AttributionEvidence and CHHHSAffiliatedAuthors.
- Archived `GrantsRegistry.tmdl`: descriptive Funder, Eligibility, Amount, Deadline, ReviewStatus, etc.
- Uploaded export has `Select_Exportable_Register_Fields` with aliases field_1–field_20.
- No complete current native dashboard, scorecard or paginated report source/readback available in this GitHub-only task.

## Exact executable tasks (RM-C13–16)
1. Freeze the current PBIX/PBIP/TMDL, report visuals, DAX, relationships, field parameter refs, scorecard goal IDs/bindings and paginated RDL/data sources, recording every file SHA and workspace/artifact identity privately.
2. Run `portfolio-scripts/rims_powerbi_binding_audit.py` on actual TMDL and export model/report/RDL source. Determine whether each code is a physical SharePoint column, semantic column name, lookup enum/choice value, or rendered measure value.
3. Align aliases with `portfolio/rims-field-aliases.json` and `field-remediation.csv`. Generate old/new reference diff and regression fixtures for null, unexpected status, duplicated labels and period reconciliation.
4. Preserve `sourceColumn` and existing SharePoint internal field names. Prefer metadata/display aliases or compatible derived dimension columns and decode lookup/choice values *without changing review authority*.
5. Update semantic-model source and test DAX, relationships, RLS, refresh and field parameter compatibility. Migrate report visual filters and bookmarks. Do not assume model field rename automatically updates visuals.
6. Independently update scorecard metrics/source bindings and paginated RDL datasets/expressions/parameters. Require render/export parity, sensible units/denominators and source sample trace.
7. Verify report and scorecard pages with the native owner; rollback if a visual, metric or RDL breaks. Only then promote.

## Acceptance
All codes visible to end users are either mapped to an actual canonical label and sensible decoded value, or explicitly presented as an unknown/needs-review state; all source models, dashboards, scorecards and paginated reports have independent acceptance receipts. **These acceptance gates have not been passed in the live platform.**
