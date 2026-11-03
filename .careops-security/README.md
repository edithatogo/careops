# Privacy protection

CareOps must remain PRIVATE. The installed local pre-push gate checks the exact
approved destination and current GitHub visibility before Git transfers commits.
If identity, visibility, scanner, model, history or scan scope cannot be verified,
the push is blocked. A failed local notification never permits a push.

## Existing protections remain

Gitleaks 8.30.1 still scans secrets and exact outgoing ranges, with only the
existing reviewed historical fingerprints. Inline exemptions remain disabled.
The original document/binary, private-directory, inventory and size checks remain
in the legacy chain. Document approval still requires the exact path, SHA-256 and
substantive inspection reason in policy.json; changed bytes invalidate approval.
Presidio does not parse approved Office files, PDFs, images or archives. Inspect
hidden sheets, tracked edits, metadata and embedded objects before approval.
Submodules require their own gates; a gitlink is not recursively inspected.

## New offline text gate

The same Presidio worker is used locally and in CI. It scans changed text blobs,
filenames and commit messages across every selected intermediate commit. Adding
personal text and deleting it before the tip does not evade the scan. The index
or working copy cannot replace outgoing committed bytes. Repeated blob identities
are deduplicated; limits and unsupported modes fail closed, never truncate silently.

Local selection excludes only branch tips actually advertised by the approved
remote whose objects exist locally. A new branch does not automatically approve
its content. Existing Gitleaks/document history checks remain conservative for a
new remote ref. Non-branch pushes need separate review and are currently refused.
CI uses the exact PR/push commit range; manual dispatch requires an explicit base.

The worker uses the normal packaged English spaCy model, validates dependency
Python/version metadata and a model-content fingerprint, and prohibits network
connections. Its email recognizer uses the bundled public-suffix list without
fetching it. A model cannot download itself during a push. Detection includes
names, email, phones, payment/identifier categories and additive labelled birth,
TFN and Medicare patterns. Labelled patterns do not prove checksum validity or
complete unlabelled identifier coverage. Other languages, confidential non-PII
facts, author/ref metadata and non-Git uploads still need explicit local review.
This is defence in depth, not a guarantee that every disclosure is detected.

## Qualified runtime and setup

Use a verified checkout-local Python 3.15.1 virtual environment. The newest
released analyzer whose declared Python range admits 3.15 is 2.2.359. Releases
2.2.360–362 exclude 3.14+, and 2.2.363–366 exclude 3.15. Analyzer2.2.366 also pins
preshed below3.0.14. Do not override these constraints, downgrade Python, substitute
regex-only scanning, or skip the packaged tokenizer. The qualified combination is
analyzer2.2.359, spaCy3.8.18, preshed3.0.15, NumPy2.5.4 and en_core_web_sm3.8.0.
The exact model wheel hash and complete dependency hashes are locked.

From the actual checkout, create only an absent environment; never replace one
under a running operation:

```sh
uv venv --python 3.15.1 .venv-careops-presidio
uv pip sync --python .venv-careops-presidio/bin/python --require-hashes .careops-security/requirements-presidio.lock
.venv-careops-presidio/bin/python -I .careops-security/qualify_presidio.py
```

The lock records the independently qualified dependency snapshot. Re-resolution
or upgrades require their own metadata, audit and offline model qualification;
an old lock is not authority to override new incompatibilities. The official
model/package licences remain their own; no model or dependency code is vendored.

A plain clone can retain the existing guarded install.sh procedure after creating
its checkout-local privacy runtime. The actual managed installation in this
working estate instead has core.hooksPath in the Git common directory. Run:

```sh
.venv-careops-privacy-hooks/bin/python -I .careops-security/install_managed.py
```

That reviewed installer snapshots the guard/policy, preserves the existing
managed dispatcher and hook chain, refuses changed ownership, records preimages,
and atomically updates the real hook files with readback. It also withholds raw
legacy pre-commit diagnostics. It never changes private remote visibility or
credentials. Each linked checkout needs its own qualified scanner environment;
missing environments block pushes without replacing existing runtimes. Do not
assume changing the tracked hook alone updates an installed managed hook.

## Review a blocked push

Diagnostics contain fixed refusal messages, opaque identities and aggregate
status only. No matched strings, snippets, raw filenames, remote URLs, third-party
tracebacks, raw scanner output, PR comments or uploaded scan artifacts are emitted.
On macOS an actual refusal also attempts one generic local owner notification.
There is no email, webhook, subscription or remote alert. Offline/unavailable
visibility or notification paths never turn into permission to upload.

1. Stop the transfer and inspect the selected source locally.
2. Remove genuine private data; private repository visibility does not approve it.
3. For a demonstrable technical or synthetic false positive only, review that exact
   blob and finding. presidio-reviewed-findings.json binds the policy hash, opaque
   path/blob identity, blob SHA-256, entity, span and value hash, with a substantive
   reason and reviewer. A changed byte, path, span, entity or policy invalidates it.
   No blanket directory exemption or historical automatic baseline is permitted.
   These text reviews do not grant document approval or authorise sensitive data.
4. Re-run only the affected gate; keep normal hooks and required protected checks.

The installed guard uses its reviewed snapshot rather than trusting an outgoing
change to its own scanner or policy. Integrate and install an updated reviewed
snapshot deliberately. Existing legacy findings stay blocked unless specifically
reviewed under their original rules. Source/PR review is still required for gate,
policy, inventory, dependency and workflow changes.

CI is a backstop after upload, not a substitute for local prevention. It uses only
read-only GitHub credentials, no admin token, and cannot make a repository private.
If the destination unexpectedly becomes public, local pushes are refused rather
than silently changing settings. No hook can prevent deliberate hook bypass,
direct API uploads or already-distributed copies; agents must not use such routes
to evade review. Exposed credentials need revocation, not just a private setting.

Upstream: [Presidio analyzer](https://presidio.dataprivacystack.org/analyzer/),
[spaCy model releases](https://github.com/explosion/spacy-models/releases).
