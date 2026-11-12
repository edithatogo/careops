# CHHHS public metadata bibliometrics — architecture decision

See [Conductor implementation programme](../../conductor/tracks/chhhs_public_bibliometrics_20261112/index.md).

This is a **parallel open-data research product**, not a replacement for RIMS's accepted register, producer flow or native Power Platform solution. Reuse publication, people, organisation and funding semantics from `portfolio/rims/contracts/domains/`, the existing provider-adoption catalogue, review/decision semantics and medallion vocabulary. Do not duplicate or modify the 17-source existing-data pipeline in order to harvest from the public internet.

Proposed layers: public metadata harvest → licence-aware immutable Bronze → typed, source-qualified Silver → CHHHS-attributed adjudicated Gold → bibliometric time series and directed source-qualified citation/coauthor networks in Platinum. Consumed source fields are provider-qualified; historic affiliation evidence and publication-time institutional identity must be retained. Citation edges require observation timestamps and provider attribution. Use source-specific metrics and versions; no additive cross-provider counts.

The repository already pins Gemini Conductor as a Git submodule; actual skill activation requires the local Gemini CLI. Source-level track setup is complete when merged, but data acquisition, collection, model evaluation, release and CI acceptance are separate forthcoming tasks.
