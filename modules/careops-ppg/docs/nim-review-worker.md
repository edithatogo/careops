# Resumable NIM review worker

The CLI worker checkpoints fictional review suggestions in a private SQLite queue.
It reads the existing OpenRouter key from the environment, without copying it
into the queue, command arguments, results or logs.
It has no SharePoint connection, native mutation capability or document loader.
The existing guarded review/compiler and CLI publication route remain separate.

## Current scope

Only the four built-in fictional source/target pairs can leave the machine.
Every outbound request checks exact fixture content, model and fingerprint before
loading the key. Adding a private document to SQLite does not authorise its use;
the worker rejects it before sending. No flag enables private content.

Free-only is mandatory from 4 November 2026. New queues default to OpenRouter
`nvidia/nemotron-3.5-lightning:free`, pinned to `nvidia/nvfp4` with no fallback,
zero maximum prompt/completion price and the existing no-training/ZDR controls.
Paid OpenRouter and NVIDIA hosted routes are rejected before loading credentials
or dispatching attempts. Historical paid fingerprints/results remain readable.
There is no paid-route override.

The fixed endpoint is `https://openrouter.ai/api/v1/chat/completions`.
Before inference, fresh endpoint metadata must explicitly confirm zero prompt
and completion pricing, strict ZDR and Safety Retention false. Missing metadata
blocks inference. The free Lightning candidate currently lacks that strict-ZDR
qualification and remains stopped; free pricing alone is insufficient.
Redirects and proxy rerouting are disabled. Requests have no tools, retrieved
instructions are evidence only, and model findings never establish clinical
acceptance or current authority. Exact quoted passages and fictional expected
dispositions must pass validation before a result is marked succeeded.

## Run and interrupt

Run from the repository with its qualified Python 3.15.1 interpreter:

```sh
.venv/bin/python scripts/ppg_nim_worker.py seed --state .local/nim-worker
.venv/bin/python scripts/ppg_nim_worker.py start --state .local/nim-worker
.venv/bin/python scripts/ppg_nim_worker.py status --state .local/nim-worker
.venv/bin/python scripts/ppg_nim_worker.py pause --state .local/nim-worker
.venv/bin/python scripts/ppg_nim_worker.py resume --state .local/nim-worker
.venv/bin/python scripts/ppg_nim_worker.py stop --state .local/nim-worker
```

Select Lightning explicitly when seeding its fictional qualification:

```sh
.venv/bin/python scripts/ppg_nim_worker.py seed --state .local/nim-worker \
  --model nvidia/nemotron-3.5-lightning:free
```

`start` launches a detached local process from an immutable source snapshot,
using the selected interpreter. The computer must stay awake. `--watch` waits
for pending fictional jobs instead of exiting when the queue is empty; it makes
no inference requests while idle. Each process dispatches at most eight requests,
with at most four concurrent readers; use `--max-requests` and `--workers` to
reduce those bounds. It exits when its request budget is exhausted.

Pause or stop prevents the next batch. Already dispatched calls finish or reach
their 120-second timeout, then checkpoint individually. SIGINT/SIGTERM requests
the same graceful stop. A forced kill leaves uncertain attempts; restarting
marks them uncertain and never silently resends them. A queue lock prevents a
second worker dispatching the same jobs. Resume clears the control files; if
the process has exited, run `start` again. Completed jobs are not repeated.

Authentication/budget failures and HTTP 429/503 pause dispatch after the current batch.
Other failed responses remain visible. No failures are retried automatically.
Uncertain/failed results need explicit investigation; neither seeding nor resume
resets them. Inference success does not mean a PPG assessment was completed.

## Private-content prerequisite

Before extending this worker beyond fictional material, establish approval for
the exact endpoint/deployment, provider, document classification, retention and
data location. That later increment must bind source identities and hashes,
reuse qualified full reviews, preserve citations and uncertainty, and pass its
suggestions through the existing completion compiler and single native writer.
It must not give the model tenant credentials or direct SharePoint tools.

No private document was authorised for transmission by this implementation.
Operational state, credential locations, detailed results and receipts stay
local. Cross-tenant recovery remains removed from current scope; this worker
does not implement Power BI or any other roadmap feature.

## Qualification limits

Local checks cover fixture-only outbound enforcement, exact quotations, explicit
uncertainty, crash recovery, completed-result reuse and stop-before-dispatch.
Native qualification requires actual responses for each configured model; a
model appearing in NVIDIA's catalogue or `/v1/models` does not establish that
its inference endpoint works for the current account.

API shape: [NVIDIA chat completion reference](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-nano-30b-a3b-infer).

## Historical paid OpenRouter qualification

This section records the earlier paid route, which cannot dispatch under the
current free-only policy. Before the free-only instruction, the authorised key
cap was saved as $2 using existing credit and all four fictional Fireworks cases
passed. Total reported inference cost was $0.000091674. No private documents
were transmitted. Subsequent calls must satisfy the free-only controls above;
the restored cap does not authorise paid inference.

The same fictional worker also supports `--transport openrouter` when seeding:

```sh
.venv/bin/python scripts/ppg_nim_worker.py seed \
  --state .local/openrouter-qualification --transport openrouter
.venv/bin/python scripts/ppg_nim_worker.py start \
  --state .local/openrouter-qualification --workers 1 --max-requests 1
```

It reads the existing `OPENROUTER_API_KEY` environment variable directly. It
never copies the secret to the queue or arguments. A configured base URL must
match `https://openrouter.ai/api/v1`; redirects and proxy routing are refused.
The OpenRouter model ID is `nvidia/nemotron-3.5-lightning`, distinct from the NIM
model ID. Jobs and fingerprints are separated by transport.

The route is pinned to `fireworks`, with fallback disabled,
`data_collection: deny`, `zdr: true`, and response caching disabled through
`X-OpenRouter-Cache: false`. Before inference it checks the current OpenRouter
ZDR endpoint list for that exact model/provider and requires
`safety_retention: false`; the metadata check is shared for at most 60 seconds
within a worker process. A successful response must identify the expected model
and Fireworks provider. HTTP 401/402/403 blocks further dispatch; the worker does
not raise spending limits, rotate credentials, relax privacy settings or switch
to a free provider to get past a failure.

These controls qualify a candidate inference route, not organisational permission
to disclose documents. OpenRouter account opt-ins, processing location and legal
retention exceptions must still be established before private use. Ordinary
inference keys may not read account guardrails. A read denial leaves those
settings unknown; it does not justify changing the account or using another key.

References: [OpenRouter ZDR](https://openrouter.ai/docs/guides/features/zdr),
[response caching](https://openrouter.ai/docs/guides/features/response-caching),
[Fireworks open-model privacy commitments](https://fireworks.ai/privacy-policy).

## Prepare the real queue locally

`scripts/ppg_assessment_queue.py` is an offline preparation command. Supply an
all-pages snapshot of incomplete native assessments, retained source indices
and the existing private review root:

```sh
.venv/bin/python scripts/ppg_assessment_queue.py \
  --snapshot .local/private-inputs/incomplete-assessments.json \
  --source-index .local/private-inputs/source-index.json \
  --reviews-root .local --output .local/private-assessment-queue
```

The snapshot contains `observedAtUtc` and `rows` with exact assessment identities,
current states and evidence manifests. Existing qualified CLI reads supply this
input; the queue builder never authenticates or makes network requests.

The builder verifies original and extracted-text hashes against native source
pins, keeps native source/evidence holds explicit, and discovers retained r42
full-review packets through their persistent UID, edition and content hashes.
Reuse also requires complete text ranges and valid passages in all four review
dimensions. Such packets still require current graph and endpoint reconciliation;
the queue does not convert a prior review into a native completion.

Readiness distinguishes reusable full reviews, other locally verified bodies,
and source/identity/evidence holds. This bounded review index does not establish
that other historical review packets are absent. Missing local pins are explicit
queue blockers, not claims that the source is unavailable everywhere.

Every real job is held with `transmissionAllowed: false` in a separate
`assessments.sqlite3`. It cannot be consumed by the fictional inference worker.
`summary.json` reports the preparation counts. Stable per-case fingerprints
prevent replay duplicates; revised inputs retain earlier packet revisions.
Completed native records are excluded, and records outside a later incomplete
snapshot are labelled explicitly rather than deleted. All packet contents and
source paths remain private; no document bodies are sent or copied into Git.


## Restore an exhausted existing OpenRouter key

Use the existing key to read `/api/v1/key` and `/api/v1/credits`. Account credit
and the key's spending cap are separate: available account credit does not reset
an exhausted key cap, and `limit_reset: null` has no scheduled reset. Keep secrets
in the existing local credential/environment source; do not paste them into chat.

An inference key cannot administer its own cap. OpenRouter's key-management
operations require a management key. If the current client receives HTTP 401 on
`/api/v1/keys`, use the signed-in account's [API key settings](https://openrouter.ai/settings/keys)
to edit the existing key to an explicitly chosen spending limit. There is no need
to replace the inference key or buy credit solely because its separate cap is
exhausted. Account sign-in and an unspecified spending allowance remain human
steps; do not create broad management credentials or rotate keys around a limit.

Restoring allowance does not override the current free-only policy. Paid
Fireworks qualification is historical; do not repeat it. Private assessment jobs
remain held until a free route meets the privacy controls and the separate
endpoint/data-scope decision is established.

[OpenRouter key update contract](https://openrouter.ai/docs/api/api-reference/api-keys/update-keys).
