# Executable implementation queue

Each task has a bounded output and an explicit closeout condition. Existing H2 and correspondence evidence remains authoritative; no duplicate committee or approval track.

| Task | Status | Output and acceptance |
| --- | --- | --- |
| RMS-01 | Complete | Reused H2 profile/occurrence resolver and recorded Decisions ownership boundaries. |
| RMS-02 | Complete — source | Deterministic no-write forum blueprint compiler with stable namespace/hash and non-premium capability restrictions. |
| RMS-03 | Complete — isolated focused | Four local multi-forum blueprint tests reported passing with Python 3.13.5; not canonical module Python 3.15.1. |
| RMS-04 | Open — protected CI | Exact-head module/parent, privacy/security/source inventory and hosted checks; merge through normal protection. |
| RMS-05a | Complete — isolated focused | Read-only shared-register projection scoped to named forums. Seven focused tests passed locally on Python 3.13, including cross-forum identity reuse, deterministic ordering, duplicate rejection, no auto-resolution and date validation. No native source access. |
| RMS-05b | Partial — source-only page contract | `sharepoint_decisions_reader.qualify_pages` validates explicitly scoped, normalised Standard-connector pages, contiguous continuation, strict fields, version/ETag, composite IDs and projection; seven isolated fictional tests pass on Python 3.13. This is **not a native connector reader**: authoritative SharePoint fetch, permission/full-pagination proof, tenant/list bindings, freshness, write/recovery and standalone provider integration remain open. |
| RMS-05c | Source implemented; not native-qualified | Generate stopped, disabled Standard SharePoint `GetItems` cloud-flow source with exact list/view/connection references, connector auto-pagination policy, bounded result/count guards, required-field refusal, WDL Select projection and no writes. `sharepoint_decisions_flow.py`; native PAC pack/connector schema and run acceptance remain open. |
| RMS-05d | Open — native | Independently verify connector metadata and selected List view/internal names, qualify real `GetItems` response and operator permissions, deploy only to a separately selected stopped qualification flow, test 0/1/2/threshold/over-threshold rows, and preserve manual fallback. |
| RMS-06 | Open | Native two-forum configuration, paper/minutes, action readback, conflicts and observed replay/recovery; no-email effect check and operator usability. |
| RMS-07 | Open | Versioned decision provenance, reviewed outcome links and supersession review; do not equate completion evidence with governance acceptance. |
| RMS-08 | Open — optional | Minimal OCEL/provenance read-only exports over approved events; no new core runtime. |
| RMS-09 | Open — evaluation | Benchmark manual vs deterministic vs optional model-assisted preparation; measure missed dissent/conditions, rework, user time and recovery. |
| RMS-10 | Open | Declarative operator setup, status manifest, repeatable native deployment and recovery. |

## Accepted source behaviour and its limits

`scripts/meeting_blueprints.py` emits the forum catalog without writes.
`scripts/meeting_register_projection.py` accepts a **caller-supplied** scoped metadata snapshot, rejects unknown forums/duplicate record identity/unknown fields and computes stable per-forum read-only action/decision counts. Its status counts are descriptive: supplied `resolved` plus evidence reference is **not** independently proved accepted closure. No operational data, connector runtime, record creation or durable storage was added.

Only isolated component test evidence exists for the new projection. Real SharePoint List pagination, authorization, source/policy validity, actual register freshness, write/retry and live usability remain outside this source slice. The full module/parent suites and hosted CI have not been executed on this current branch head. Any GitHub Actions billing/capacity refusal must be reported as **unexecuted**, not successful.

**Known external blockers:** GitHub Actions account issue #301; H2 native browser/Invoker runtime and recovery acceptance; existing H1 governance-source adoption gaps. No failed or unavailable operation should be bypassed by changing application identities or using premium fallbacks.

## 11 November continuation — SharePoint read-admission slice

- Implemented `scripts/sharepoint_decisions_reader.py`: pure, non-writing compiler of a bounded sequence of **pre-normalised** native SharePoint page envelopes. The interface is intentionally *not* an HTTP client or Power Automate flow and has no tenant identifiers.
- Requires an exact SharePoint site/list/scope match, connected opaque cursor chain, a final complete marker, strict approved metadata columns, SharePoint item identity, version and ETag values. It reuses `meeting_register_projection.project_register` to reject invalid governance states, duplicate identities and malformed dates.
- Seven focused fictional tests passed in a local Python 3.13 environment with a small local compatibility stand-in for the existing register projection. **This does not qualify the exact GitHub module integration**. Canonical Python 3.15.1 module/parent/security CI is pending; do not claim green release.
- An opaque cursor is a **normalised token**, not the actual `@odata.nextLink` URL. Before using the code with a real connector, implement and test an admitted native response-to-envelope adapter using the exact exposed connector output contract. The normalised complete flag is caller-supplied; the compiler cannot independently establish full pagination, source authority, access permissions, freshness or ETag enforcement.
- Reconciliation decision: integrate this bounded read-admission route with PR #304's planned `standard-m365` profile **without** treating the unmerged proposed architecture as current main. Preserve native H2 gates and keep all writes held. No scope expansion to premium HTTP/custom connectors or Dataverse.

Next: normalised native binding adapter using existing standard SharePoint connector examples, synthetic end-to-end tests with the actual projection, and native exact-list readback when authorised. Add typed connection/permission receipts and a separate fail-closed write proposal route only after native proof.

### Review follow-up — malformed native list identity

A new negative test exposed that a non-string `list_id` inside an otherwise shaped page could raise `AttributeError` rather than returning a blocked read result. Added a type guard before case-normalisation and a regression test. Six focused local tests pass in the isolated Python 3.13 environment. This is not full integration evidence; canonical module tests and native connector readback still remain open.

### Physical native identity hardening — 11 November

Reject repeated native SharePoint `ID` values across different forum projections, even when logical `(forum_ref, record_id)` keys differ. This matters because one SharePoint List item must not masquerade as two independent governance records. The two-forum fictional test uses distinct physical IDs. Seven focused read-admission tests now pass locally on Python 3.13, using the earlier-mentioned compatibility stand-in for the existing projection module. Exact GitHub integration and native reading remain unverified.

## 11 November — actual Standard-connector source implementation

- `scripts/sharepoint_decisions_flow.py` now emits a **native Power Automate Workflow Definition Language** candidate using `shared_sharepointonline` `GetItems`. It is not another Python run-time adapter or a generic HTTP action. The WDL action has enabled pagination policy with conservative item threshold, a selected view, strict binding parameters, a manual trigger and explicit review-only output. The complete flow is always Stopped with `ReadEnabled=false` initially. No action writes to SharePoint, sends email, schedules a job, or invokes Copilot/AI Builder/Dataverse.
- Companion source tests `tests/test_sharepoint_decisions_flow.py` were added for expected connector shape, default stop/disable, capability restrictions and invalid bindings. **These new tests have not yet been executed on the canonical repository Python 3.15.1 runtime**, and are not proof that Power Automate accepts the generated JSON. Existing source import and connection semantics require native verification.
- Official Microsoft documentation supports `GetItems` (`dataset`, `table`, `view`, `$orderby`) and `runtimeConfiguration.paginationPolicy.minimumItemCount`. The dynamic list column fields, version and ETag output keys remain native validation prerequisites. Read [the implementation/commissioning record](native-sharepoint-getitems.md).
- Open blockers are real delegated SharePoint site/list and connection references, a verified native `GetItems` graph, PAC solution integration, scoped permission readback, native output and pagination run proof and full source/security CI. A generated WDL graph is not a saved cloud flow.

### 11 November protected-CI privacy regression

GitHub Actions became available after the repository became public. Exact-head hosted Clinical Hub Domain tests initially failed before functional tests because `validate_public_source.py` detected two realistic-looking `example.sharepoint.com` fixture URLs in `tests/test_sharepoint_decisions_flow.py` and `tests/test_sharepoint_decisions_reader.py`. Both fixtures now use the existing allowlisted **fictional** `fictional-example.sharepoint.com` host. This is a test-data correction only; native binding and real tenant identity remain absent. The original failed head does not qualify the updated branch, which requires a new full current-head hosted check suite before protected merge.
