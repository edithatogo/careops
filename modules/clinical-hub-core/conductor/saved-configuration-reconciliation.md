# Saved Canvas configuration reconciliation

Compare the maintained source, the current authoring snapshot and the saved app
metadata separately. Use the existing qualified CLI for metadata and SharePoint
schema reads, and the official authoring connection for the unpublished source.
Preserve native identities, raw reports and original files in the private track.

The published package is not necessarily the functional draft. Pin the published,
draft and autosaved version identifiers; do not publish to obtain an export. A
published connection manifest may omit a source added to the unpublished draft.
Record platform autosave separately: no manual Save does not prove that autosaved
metadata stayed unchanged. Reconcile final versions and source before closeout.
Use the current authoring data-source inventory and native source destination
alongside exact SharePoint list/schema readback to qualify that binding.

## Compare before repairing

Use the explicit repo-local qualified interpreter:

```sh
.venv-ci/bin/python scripts/compare_canvas_configuration.py \
  /private/source/Screen.pa.yaml /private/readback/Screen.pa.yaml \
  --report /private/evidence/new-comparison.json
```

The helper compares YAML structure and scalar types exactly. It does not discard
whitespace, quoted literals, reordered controls or missing defaults. Exit codes:
`0` exact match, `1` differences/additions, `2` unobserved properties only. The
report is create-only and may contain private configuration; never commit it.
This local comparison is not native save or runtime proof.

Review each difference against the latest native evidence and existing ownership.
If the maintained source is older than an already-qualified native repair, retain
its original and update only the stale properties. Do not push old formulas into
the app or replace a full maintained file with a sparse export. Preserve omitted
properties and report them as unobserved; do not infer their effective values.
Explain any intentionally retained immaterial difference explicitly.

## Binding and closure checks

- Resolve each current source to its existing site/list identity, not merely a
  similar display name. Check the mapped field IDs, internal names and types.
- Check lookup targets and relevant versioning, attachment, moderation and unique
  recovery-slot settings through native readback. Do not change access or schema
  just to complete a comparison.
- Compare all actual form field bindings and safety/recovery formulas. Reuse
  unchanged passed cases at their recorded scope; do not relabel them as fresh runs.
- Take a final authoring readback to detect intervening edits. Record saved-state
  evidence, remaining export limits, source repairs and native changes separately.

Keep deadlines and existing source pins unchanged unless separately selected.
Reconciliation introduces no publication, people, real records, premium connector,
workflow activation, approval request or email. Device testing and an app-level
uncertain-save trial are separate from this configuration check.
