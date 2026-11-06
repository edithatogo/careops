# Local clean-package qualification

Qualify a combined source candidate separately from hosted CI, native deployment
and operational acceptance. Preserve the existing working tree and deployment
bindings. Local snapshots, packages, environments and evidence are permitted;
any group or native/cloud object requires explicit human confirmation.

Use the exact `.python-version` pin (currently Python3.15.1) in a new local
virtual environment. Install the unchanged frozen `uv.lock` with its development
and build groups. Run `tests/test_source_package.py` with the locked build group:
it builds fictional sdist/wheel fixtures, rejects generated Hypothesis state and
checks that code, LICENSE and NOTICE remain present. Without the optional build
backend the archive test records a capability skip; package qualification must
install the build group and execute both cases without skipping them.

Build the actual sdist and wheel twice with the same `SOURCE_DATE_EPOCH`, exact
source bytes and backend. Compare artifact digests, inventory actual archive
contents, verify source bytes and licence/NOTICE, and reject cache, environment,
local evidence or private deployment material. Source archives explicitly exclude
`.hypothesis`; a nested cache-generated ignore file is insufficient protection.

Extract the sdist safely into a clean local directory, install the exact frozen
dependencies into a separate repo-local interpreter, then install the wheel
without dependency resolution. Test the installed wheel with source imports
disabled and prove that `careops_process.__file__` resolves to site-packages.
Run full integration/coverage, strict typing, lint, security and offline
PowerShell gates against the selected candidate. Prepare the existing immutable
graph verifier from already available local source; do not weaken that gate.

Retain source/artifact hashes, dependency lock, package inventory and exact
failure evidence. Rehearse applying/reversing any package-boundary repair over
verified preimages. Do not overwrite historical artifacts or claim hosted
checks, signed attestations, native access or operational acceptance from local
results. No tenant operation, communication, group creation or flow activation
is part of this qualification. F06/F08 and native bindings remain untouched.

The offline module dry-run test invokes `sys.executable` directly. It must not
use `uv run`, which can synchronize an environment or resolve dependencies during
a test. Four identified invariant properties retain their assertions, generated
cases and shrinking with explicit finite one-second per-example budgets; their
former implicit 200ms timing budgets proved unstable during isolated installed-
package execution. Do not globally disable deadlines or automatically retry
failures. Keep the original failures and timing diagnosis with qualification
evidence. These properties are correctness checks, not performance benchmarks.

## Local lane closeout — 27 October 2026

The user accepted local-only closeout. Fictional replay, flow-contract typing and
combined clean-package qualification are closed. Retained results: 1,755 installed-
wheel passes, 10 existing capability/platform skips, 96.24% line/92.63% branch
coverage and zero strict type errors across 153 files. Qualification artifacts
and failure records are unchanged; this is a status-only follow-up. Hosted review,
pin promotion/merge, native/operational acceptance and archival remain deferred
in the existing Process track. Any group or native/cloud object requires prior
human confirmation. No native objects, bindings, flows or permissions change.
