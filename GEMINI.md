# Gemini CLI project context

Use [AGENTS.md](AGENTS.md) as the authoritative CareOps development and publication policy. Read [Conductor context](conductor/index.md), [track registry](conductor/tracks.md), [suite delivery](conductor/suite-delivery.md), and the relevant existing module track before changing source.

The official Google Conductor plugin is an **exact-pinned submodule**, not vendored code, at `.agents/plugins/conductor`. It is not the same thing as an activated Gemini CLI extension. See [Gemini CLI setup](docs/clinical-data-catalogue/conductor-gemini-cli.md) and the optional workspace bootstrap script `scripts/setup_gemini_conductor.sh`. Never run `conductor-setup` in a way that replaces existing `conductor/` product documents or track history.

For the CHHHS virtual clinical registry programme, start with [its track](conductor/tracks/virtual_clinical_registry_20261113/index.md). Conductor requirements and plans represent source design, **not** approval to connect clinical systems, expose identifiable information, install in a Queensland Health tenant, activate alerts or conduct research. Only use synthetic examples in public Git.

Work on a feature branch; add focused checks; review proposed changes against the spec, preserved owners and security boundary; report exactly which source, local, tenant and clinical gates are verified. Do not send email or disclose sensitive data without the explicit approval required by AGENTS.md.
