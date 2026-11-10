# EF-00 — open pull-request qualification snapshot

**Observed on 11 November 2026.** Source `main` at `7de89d644b66123b47d75816dd9f5f9600e69f83`. GitHub connector could read PR metadata and commit check-run summaries but **not current branch-protection rules** (403 permissions). No privileged merge bypass is authorised. This is not a complete GitHub Actions annotation audit; `failure` below means GitHub marked the check failed, not proof its test steps executed.

| PRs | Latest observed check status | Additional state |
| --- | --- | --- |
| #313 #312 #311 #310 #309 | All observed current-head checks are failed or skipped | Mergeable flag does **not** mean protected checks passed |
| #308 | Failed/skipped | Draft |
| #306 #300 #299 #277 #217 | Failed/skipped | Dependency or source-pin updates retain original qualification |
| #305 #304 | Failed/skipped | Conflicts |
| #303 | Failed/skipped | AI adapter remains optional |
| #244 #243 #242 #241 #240 | Mix of old successful checks with recent failed/skipped checks | Conflicts; historical green checks are not current-head qualification |

**Total inspected: 19 open PRs. Verified safe protected merges: 0.** Source `main` remains unchanged. A latest selected workflow sample showed failure in seconds and no executed steps; #301 documents billing refusal. This supports suspicion of a service-wide execution problem but does **not** prove every failure is billing-only; record `unverified` until actual job annotations, logs, and runner execution can be read. Do not rerun an unchanged failed job repeatedly while the underlying spending restriction persists.

Current delivery priorities: (1) Restore hosted job execution without changing gate/protection requirements; (2) independently validate exact-head runs; (3) reconcile conflicts and stale dependency proposals; (4) merge one small, qualified PR at a time; (5) verify the resulting `main` commit. Keep PR #313 and all other current candidates unmerged until this becomes possible.

For programmatic, **offline** classification, use the new `portfolio-scripts/engineering_frontier.py checks` command with a locally retained sanitized GitHub snapshot. It does not acquire a privileged token or claim branch protection acceptance.
