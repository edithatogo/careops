# Evidence-based hardening

This issue tracks additional repository-hardening techniques beyond the baseline `validate` workflow:

- Property-based checks (`quality-hardening` workflow, `property-based` matrix entry)
- Mutation checks (`quality-hardening` workflow, `mutation` matrix entry)
- Contract checks (`quality-hardening` workflow, `contract` matrix entry)
- Metamorphic checks (`quality-hardening` workflow, `metamorphic` matrix entry)

## Required local controls

- Single-owner workflow via `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`
- Renovate-driven dependency management (`.github/renovate.json`)
- CI checks with generated drift receipts and coverage upload via OIDC

## Status check mapping

- `validate` job matrix (`RepositoryHygiene`, `SourceControlReady`)
- `workflow-lint`
- `secret scan`
- `analyze` (CodeQL)
- `coverage`
- `quality (property-based)`
- `quality (mutation)`
- `quality (contract)`
- `quality (metamorphic)`
