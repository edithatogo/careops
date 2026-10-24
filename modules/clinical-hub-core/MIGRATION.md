# Clinical Hub source migration — 24 October 2026

CareOps now owns maintained source at `modules/clinical-hub-core`. This supersedes
the earlier optional-gitlink plan and child-only canonical-development wording.
The former repository remains recovery history; do not resume development there.
`SOURCE_PROVENANCE.json` retains the exact imported revision and original hashes.
All public source files are retained, including historical workflow definitions;
only root workflows execute in CareOps. The parent Clinical Hub workflow owns
current domain tests and lock auditing. No private Git history was imported.

The uncommitted Outlook connector guide and its README link are included.
Superseded local branch commits and dependency candidates are preserved in a
verified private all-ref bundle and worktree snapshots; preservation is not
promotion. Use current main's qualified Python 3.15.1 and hash lock. Archived
child Renovate/workflow configuration remains source history; active maintenance
is configured by the parent. Source release helpers support this nested module.

## Work and evidence continuity

- All reusable scripts, schemas, Office Script fixtures, fictional tests and
  Conductor documents from the source revision are included.
- Meeting F05–F16 capability dispositions and their limits remain in the retained
  suite delivery, document, recovery and manual-route guides. Reuse passed checks;
  metadata storage alone does not prove Word-body refresh.
- DDMS saved configuration, reviewed contributions, handover, notification pilot
  and recovery remain linked from the module Conductor index. Preserve their
  recorded scope; disabled delivery does not authorise future sending.
- Full operational registry, completed/archived AVAC and Ryan development,
  on-call roadmap, native receipts, bindings, human edits and historical source
  remain in the existing external private workspace. Local ignored compatibility
  links expose that same store; it is not copied into public source or releases.
- SharePoint library columns and maintained Word templates with manual narrative
  remain the usable route. Optional structured generation/body refresh retains
  its specific prerequisite gap. D01–D12 dispositions stay in document-cases.md.

The parent migration track indexes this work rather than duplicating native
records. Source consolidation does not alter tenant objects, permissions,
authentication, operational acceptance or email authority.

## Development and recovery

From this module directory, select `.venv-ci/bin/python` matching `.python-version`,
sync `requirements-dev.lock` with hashes and run `make ci audit`. Parent inventory
validation runs from CareOps root. Run focused tests for routine changes.
For standalone use, copy this module's regular source files into a fresh Git
checkout with its own module allowlist; siblings are not required.

Rollback uses the previous CareOps revision in a disposable checkout. Keep the
original source repository, private bundle, worktree patches and private workspace;
a source rollback never restores or deletes tenant resources. Archive the old
remote only after hosted integration and a clean-clone verification pass.
