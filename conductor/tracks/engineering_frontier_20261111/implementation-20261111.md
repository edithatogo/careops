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

## Follow-on source increment — 11 November 2026 (gateway)

Implemented a narrow **trusted-source-only operation gateway** at `portfolio-scripts/frontier_gateway.py`; retained exact current-commit task/owner preflight in `portfolio-scripts/engineering_frontier.py`. Git's committed blob provides the read input, not the mutable working file. A packet is recomputed independently and must be byte-for-byte equivalent as a Python object; unexpected paths, changed context hashes and escalated operations are refused. Only `repo:read` and `runner:focused-test` are supported. Raw read content is returned to the trusted local caller, never in the content-free receipt; reads are capped at 128 KiB.

A focused test request now requires an explicitly trusted checkout, an allowlisted test matching an exact-source path map, a clean tracked working tree, an in-checkout Python 3.15.1 virtual environment, bounded timeout, and minimal environment. Arbitrary shell, GitHub merge, Dataverse/Fabric/Power Automate mutation, network services, credentials and email are not gateway operations. Test output is hashed into a temporary receipt, not printed. **This does not sandbox test code:** network isolation, container limits and tool access control must be supplied by an independent host. Passing `trusted_checkout=True` is an operator assertion, not a credential or a security attestation.

The prior blanket `portfolio-scripts/* → test_engineering_frontier.py` selector was reproduced as incorrect and replaced by a narrow, explicit source-to-test map; unfamiliar paths now require human/module-owner test selection. That is fail-closed selection rather than an assumed correct test.

**Executed verification:** 15 Gateway synthetic test methods passed in an isolated throwaway Git checkout using the available Python **3.13.5**, plus two focused test-selection checks following the initial demonstrated failures. They included source/tamper/refusal cases, committed read integrity, oversized/symlink and traversal refusal, dirty checkout, no arbitrary test selection, runtime validation and non-sensitive receipts. Exact committed source was authored and pushed via the GitHub connector; no canonical Python 3.15.1 environment or GitHub Actions job executed in this session. Treat the 3.13.5 tests as a portability/focused local check, **not** repository-defined 3.15.1 qualification; existing parent full-suite/security/native release gates remain outstanding.

**Workstream scope:** EF-02.01/02/03/04 partial; EF-03.01/02/04 partial. EF-02 global MCP/Power Platform tool mediation, proper OS sandboxing and EF-03 multi-module test runners, caching, repair and cross-module proof remain open. EF-00 hosted CI and protected merge remain blocked. No tasks are marked fully complete from partial tests alone.

### Reproduction (after actual Python 3.15.1 is available)

```sh
.local/ci-env/bin/python portfolio-scripts/run_tests.py --runner unittest --mode focused --tests-root portfolio-scripts/checks test_engineering_frontier.py test_frontier_gateway.py
# Full source security parent tests are separately required for integration.
.local/ci-env/bin/python -m unittest discover -s portfolio-scripts/checks -v
```

The gateway is a library, not a general CLI shell or an independently authenticated service. The source-only reading entrypoint remains `engineering_frontier.py packet`; actual `Gateway.read` returns verified committed bytes to a trusted local caller. Do not feed untrusted Github/Git submodule content into a higher-privilege agent without independent data classification and tool-boundary enforcement.

### Reviewed-publication path enforcement

The gateway now loads `PUBLIC_SOURCE_FILES.json` from the **same committed SHA** used for its packet, and refuses a tracked file that is absent from that inventory. This separates Git's tracked-file status from explicit publication admission. A synthetic RED test initially accepted the deliberately unreviewed tracked file; the subsequent fix made the same test reject it. Source admission is not equivalent to full secret scanning, binary inspection or permission to upload content to an external model.
