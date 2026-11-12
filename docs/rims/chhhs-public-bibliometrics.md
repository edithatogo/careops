# CHHHS public metadata bibliometrics — architecture decision

See [Conductor implementation programme](../../conductor/tracks/chhhs_public_bibliometrics_20261112/index.md).

This is a **parallel open-data research product**, not a replacement for RIMS's accepted register, producer flow or native Power Platform solution. Reuse publication, people, organisation and funding semantics from `portfolio/rims/contracts/domains/`, the existing provider-adoption catalogue, review/decision semantics and medallion vocabulary. Do not duplicate or modify the 17-source existing-data pipeline in order to harvest from the public internet.

Proposed layers: public metadata harvest → licence-aware immutable Bronze → typed, source-qualified Silver → CHHHS-attributed adjudicated Gold → bibliometric time series and directed source-qualified citation/coauthor networks in Platinum. Consumed source fields are provider-qualified; historic affiliation evidence and publication-time institutional identity must be retained. Citation edges require observation timestamps and provider attribution. Use source-specific metrics and versions; no additive cross-provider counts.

The repository already pins Gemini Conductor as a Git submodule; actual skill activation requires the local Gemini CLI. Source-level track setup is complete when merged, but data acquisition, collection, model evaluation, release and CI acceptance are separate forthcoming tasks.

## Symposium acceleration (12 November 2026)

See [rapid Track 00](../../conductor/tracks/chhhs_public_bibliometrics_20261112/00_rapid-symposium-intelligence/index.md). The original source documentation records 1,344 accepted publications and an 18-field bibliography but the complete labelled extract is **not stored in the accessible Git trees**. The historical `research-publications` and `careops-rims` repositories provide only a small *synthetic* CSV. This is insufficient for credible longitudinal or network analysis. Recover private retained files from the authorised custodian; otherwise build a bounded public-only cohort and label its coverage provisional. Never turn source-side 'Included' into independently reviewed CHHHS membership, nor plot fabricated network edges.
