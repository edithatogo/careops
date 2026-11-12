# Shared Power BI Assets

Use this folder for reusable model assets that both dashboards can consume later.

- `m/` - shared Power Query parameters, reusable query contracts, and normalisation helpers.
- `model-tmdl/` - shared semantic model TMDL if the project moves to a shared dataset.

Do not put dashboard-specific pages, visuals, or one-off measures here.

Do not populate `model-tmdl/` from standalone dashboard exports. It is reserved for a later shared semantic model only after SQL validation and the merge-readiness gates in `docs/shared-model-merge-readiness.md` pass.

See [docs/shared-semantic-model.md](../../../docs/shared-semantic-model.md) for the canonical contract.
