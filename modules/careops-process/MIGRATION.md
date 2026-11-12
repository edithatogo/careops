# Source migration to CareOps — 6 November 2026

CareOps maintains this module as ordinary source. The source provenance retains
all imported text-file hashes and the exact predecessor revision. Full legacy
refs, pending branches, non-source assets and local unpublished changes are
preserved in external private recovery bundles; no old Git history is imported.
Only root CareOps workflows execute. Nested workflows are retained as history.
Use the root Process/Approve delivery workflows and this module's existing
standalone test/build commands. Python is selected from `.python-version` in a
module-local environment. No legacy repository checkout is needed for current
source, tests or release delivery.

Outstanding Conductor tracks, native blockers and permission/email gates remain
open at their recorded scope. Moving source does not establish native acceptance.
