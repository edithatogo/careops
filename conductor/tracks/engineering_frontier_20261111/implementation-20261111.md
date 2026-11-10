# EF-00 through EF-03 — source implementation checkpoint

Date: 11 November 2026. Branch: `codex/engineering-frontier-20261111`; PR #313. Exact final head must be re-read when changes stop.

## Executable source added

- `portfolio-scripts/engineering_frontier.py`: stdlib-only, read-only offline preflight.
  - Selects the current checked-out revision with exact 40-character SHA and a stable task ID.
  - Resolves ownership against the **committed** `portfolio/repos.json` registry, refusing unknown modules and optional uninitialised submodules.
  - Uses committed Git tree/blob identities instead of copying files from working directories; returns content-free SHA256 context references and refuse unsafe/untracked/symlinked paths.
  - Refuses cross-module scope, duplicate requests, stale HEAD and arbitrary tool operations. `guard_tool` is a **pure preflight policy check**, not a security boundary around GitHub, Power Platform, other MCP tools or shell access.
  - Identifies the focused parent regression target only; defers other module test selection rather than inferring unverified commands.
  - Classifies provided exact-head CI check facts, leaving actual branch protection and native access unqualified. No API authentication, network, deployment, package build, side effects or email.
- `portfolio-scripts/checks/test_engineering_frontier.py`: independent synthetic Git repository fixtures for source identity, module ownership, stale/dirty registry, bad paths, optional modules, tool-denial, untrusted text retention and required-check integrity.

## Source-only commands

```sh
# Only after selecting the repository-local Python 3.15.1 environment
python portfolio-scripts/engineering_frontier.py packet \
  --task-id EF-02.02 \
  --source-sha "$(git rev-parse HEAD)" \
  --changed portfolio-scripts/engineering_frontier.py

python portfolio-scripts/run_tests.py \
  --runner unittest --mode focused \
  --tests-root portfolio-scripts/checks test_engineering_frontier.py

# Snapshot input is a locally assembled non-sensitive JSON object:
# {"head_sha":"<sha>","required":["Security gate"],"checks":[...]}
python portfolio-scripts/engineering_frontier.py checks --input .local/current-head-checks.json
```

The `checks` command is not a native GitHub API client; it only validates a supplied JSON snapshot and always returns `protected_merge_qualified: false` because passing check-runs alone is insufficient. Actual protected merge also requires current policy, correct base, approvals, non-conflicting head and GitHub's merge decision.

## Qualification ledger

| Scope | Status | Rationale |
| --- | --- | --- |
| Source files created, committed, and read back | verified | Github connector exact branch reads and SHA receipts |
| Source inventory and Conductor links | verified at source shape | Sorted unique inventory, explicit paths and updated indices |
| Test fixture design and RED baseline | created, not executed | Missing preflight module before implementation; no independently executed RED command |
| Python 3.15.1 focused tests | **unverified** | No qualified repository-local Python 3.15.1 execution available in this connector session |
| Hosted exact-head CI | **blocked / unqualified** | Existing GitHub Actions jobs fail almost immediately without usable executed-step evidence; refer to #301 |
| Tool enforcement, agent integration, full routing and module runners | **not implemented** | Pure policy/preflight functions do not mediate live agent tool invocations |
| Power Platform / Fabric deployment and production effects | **not attempted** | Outside source-only scope |

## EF scope reconciliation

- **EF-00.01:** inspection of 19 open PRs completed as a point-in-time manual triage, but automatic executable full snapshot acquisition and native policy readback are still open.
- **EF-01.01/03:** partial factual harness inventory and correction of outdated topology guidance; task-benchmark corpus and source-drift audit remain open.
- **EF-02.01/02:** synthetic negative fixtures and first source-bound content-free packet implementation written; tests have not been executed against the canonical pin.
- **EF-02.03/04/05:** only the small pure permission preflight is implemented. Do not claim actual external tool mediation, sandboxing or agent integration.
- **EF-03.01/04:** minimal deterministic parent test selection and check-status receipt written. No unified runner, cross-module selection, cache, mutation, repair or independent verification is implemented.
- **EF-03.02/03/05:** open.

No EF task is marked fully complete without executable verification. Preserve all existing CI/security gates and native owners.
