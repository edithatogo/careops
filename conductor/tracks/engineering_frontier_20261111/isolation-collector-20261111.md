# EF-00 / EF-03: read-only CI collection and fail-closed Linux isolation

Date: 11 November 2026. Source branch: `codex/engineering-frontier-20261111`, PR #313. **No native Microsoft changes, account changes, public release or protected merge.**

## New working source

1. `portfolio-scripts/frontier_ci_collect.py` obtains **GET-only** authenticated GitHub evidence via a fixed `gh api --method GET` argument vector. It fetches exact-commit check-run pages, attempts real `main` required-status-check protection readback, resolves GitHub Actions jobs and originating runs to the same commit, extracts only execution status/conclusion for each step, and retains only a boolean-style billing indication. Its output is classified by `frontier_ci_evidence.py`; no raw comments, annotations, output or credential values are emitted. If a protection read is forbidden, or a job does not support step readback, the result is unqualified, never a guessed passing requirement. It does not merge PRs or apply policy.
2. `portfolio-scripts/frontier_isolation.py` builds a Linux bubblewrap (`/usr/bin/bwrap`) command with `--unshare-all` (including network namespace), a read-only repository at `/work`, readonly minimal system-library mounts, a private tmpfs, no inherited environment, and restricted Python `-I` entrypoints. `frontier_gateway.Gateway.test` invokes this for both the Python-runtime check and focused tests, without any unsandboxed fallback. A missing bwrap executable or unsupported OS is a refusal, not reduced security.
3. New synthetic tests: `test_frontier_ci_collect.py` and `test_frontier_isolation.py`, plus `test_frontier_gateway.py` denial tests. Existing parent `Security and fuzzing` workflow runs `python -m unittest discover -s portfolio-scripts/checks -v`, so they are part of the current security gate without adding a redundant workflow. The explicit changed-source target map and reviewed `PUBLIC_SOURCE_FILES.json` include the new files.

## Security boundary and limitations

- This is **not** a general agent sandbox. It isolates only the exact Python commands routed through `Gateway.test` on supported Linux hosts. GitHub, Microsoft, shells and other MCP tools remain outside its control. No delegated write, email, tenant access, network egress, or unrestricted command is implemented.
- Bubblewrap isolation depends on host kernel user-namespace support and package availability. There is no claimed runtime acceptance until it actually executes successfully on the intended CI runner. The current local container lacks `bwrap`; this legitimately blocks a live isolated test.
- A read-only repository mount is necessary but not a proof that all tracked documents are public or safe to include in an AI context. The source gateway separately requires exact inventory admission. Tests are still executable untrusted-code risk if the host OS isolation has a vulnerability; process-level limits and CI permission scopes remain mandatory.
- `gh api` uses existing user-approved authentication, does not store a token, and issues only GET requests. GitHub might restrict branch-protection/job endpoints; that is a data qualification blocker, not an invitation to bypass scopes. No API call is made on import.
- Collected statuses do not establish trusted origin until the authenticated collector itself executes with permitted access, and do not establish required branch reviews, actual deployment, or signed release. The classifier still reports `protected_merge_qualified=false`.

## Commands for selected approved environments

```sh
# Read-only CI evidence; does not alter GitHub.
python portfolio-scripts/frontier_ci_collect.py --source-sha "$(git rev-parse HEAD)"

# Local source-specific tests after creating the canonical Python 3.15.1 venv:
.local/ci-env/bin/python portfolio-scripts/run_tests.py \
  --runner unittest --mode focused --tests-root portfolio-scripts/checks \
  test_frontier_ci_collect.py test_frontier_ci_evidence.py \
  test_frontier_isolation.py test_frontier_gateway.py \
  test_engineering_frontier.py

# Then run the full security/source checks at exact PR head before any merge.
```

## Acceptance and exact remaining work

- [ ] EF-00: actually collect protected required contexts and complete job-run readback; verify all applicable current-head checks and receiving-main checks with true execution evidence. Current GitHub Actions billing/execution refusal remains in issue #301.
- [ ] EF-02: independently enforce the tool boundary for all external connectors/agent operations; this isolated Python runner is only a partial implementation.
- [ ] EF-03: execute all focused/full tests under canonical Python 3.15.1 with installed bwrap and permitted user namespaces; verify absence of host credential/file access and network egress with controlled adversarial fixtures; add CPU/memory/output quotas and job termination/recovery checks.
- [ ] Extend cross-module selection only after proven exact producer/consumer test identities. No wildcard or guessed test selection.

Source documents and tests were committed/read back through GitHub; **hosted and native tests were not completed here**. Keep all parent Conductor requirements open pending independent acceptance.
