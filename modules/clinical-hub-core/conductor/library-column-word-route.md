# Library columns and maintained Word templates

Selected working route, 24 October 2026. Assume no Copilot and no Premium
connectors. Use the existing SharePoint library, columns, templates and Standard
SharePoint operations. Copilot licensing, tenant seat discovery and Premium Word
Populate are not dependencies of this increment. Reconsider optional generation
only on changed evidence; preserve this usable route meanwhile.

## Operation

1. Select one reviewed occurrence and the exact source revisions through the
   existing preparation route. Keep agenda, paper, minutes and action identities
   distinct; use the explicit fictional mapping in tests/fixtures/document_cases/.
2. Copy the maintained Word template to a new draft identity/revision in the
   existing library. Enter variable-length agenda/minutes narrative manually from
   the reviewed structured input; retain empty standing sections as unresolved.
   Document preparation helpers are for fixture/template preparation and tests,
   not a new local operational generator.
3. Reuse actual library columns by internal name and type. The qualified schema
   includes Title (Text) and _ExtendedDescription (Note). Created, Modified and
   library version are system-managed; never write those as business revisions.
   No narrative-to-body binding has qualified. Do not create columns to satisfy
   this logical contract or guess property/control namespaces.
4. Retain document kind, occurrence, selected source IDs/revisions, template version,
   included/excluded records, output revision and prior-output link in existing
   authoritative records. Where no suitable existing column exists, preserve the
   value in the existing record and the draft's provenance block; record the gap.
   A filename/Title alone does not establish the complete provenance contract.
5. Keep papers as links, retain review holds and unresolved notes, and reconcile
   action candidates/closure-pending/accepted closure with the existing register.
   A property or document status never issues a decision or accepts closure.
6. Open in Word, inspect count/order, full long bodies, optional/standing sections,
   links and pagination. Save/reopen an intentional manual correction. Read back
   file identity, metadata and content separately. Synthetic example.test links
   establish hyperlink fidelity only, not network availability or recipient access.
7. Refresh manually into a distinct draft revision or hold for reconciliation.
   Preserve the edited original, unresolved content and issued history. Read actual
   identity/version/content after uncertain acknowledgement; no blind write retry.
   Reuse unchanged verified outputs or refuse a collision. A version listing is
   not proof of historical-content recovery.

## Capability boundary and qualification

Library-column updates have preserved saved human edits and paper links. They have
also left visible Word text stale: core Title R3 versus body R1. Treat metadata as
metadata; manually update/review the body. Do not require automatic refresh or merge
for this manual capability to be usable, and do not mark those features passed.

Use [D01–D12](document-cases.md#case-matrix) as the content and recovery expectations.
Their automatic-generation wording remains applicable only when that optional
feature is selected. For this route, D02/D03/D06 mean manually composed visible
sections/items, D10 means a separate manually reconciled revision, D11 means
create-only collision/uncertain-result reconciliation, and D12 records the known
metadata/body distinction. These adaptations do not retroactively pass the
unexecuted automatic-generation cases.

| Cases | Evidence to retain | Limit |
| --- | --- | --- |
| D01–D04 | Empty/single/12-item template copies, exact item counts/order, full last body and paper targets; saved native file/readback and Word inspection | Local DOCX structure or upload alone does not prove native rendering. |
| D05–D09 | Pinned notes, four agenda passages, missing/off-agenda notes; open and closure-pending selected, closed/held reconciled | Manual draft; no new action issuance, owner or closure. |
| D10 | Existing saved-edit/reopen evidence; original plus distinct revision and explicit reconciliation | No automatic merge claim. |
| D11 | Existing create-only replay/collision and manual recovery evidence, tied to its exact route | Developer/Premium-flow checks are not Standard Word-generation proof. |
| D12 | Existing actual property update/readback, preserved body/links/edit and stale visible bound value | Known automatic-refresh failure, accepted manual-body limitation. |

Keep exact native bindings/results in the existing private minutes track and
operational receipt. Public source contains fictional inputs and route boundaries.
Do not repeat passed cases on unchanged configuration or introduce a parallel
register, common generator, approval workflow, licence or access change.

## Delivery checks

Use repo-local Python 3.15.1. The affected preparation and fixture tests are:

```sh
.venv-ci/bin/python --version
.venv-ci/bin/python -m pytest -q tests/test_document_cases.py tests/test_prepare_meeting_draft.py tests/test_prepare_minutes_draft.py tests/test_preflight_pack.py
.venv-ci/bin/python scripts/validate_public_source.py
git diff --check
```

On 24 October 2026 the four selectors passed 124 tests. This is fictional
preparation proof, separate from the private native case results. Production
records suitability, intended-role access and distribution retain their own scope;
no sending, issuing, publication or workflow activation follows from qualification.

## Qualification result — 24 October 2026

Reuse of the existing library/schema/template was checked through the existing
qualified CLI session. Five fictional shapes were saved natively using existing agenda/minutes templates:
empty/single/12-item agendas, action carry-forward minutes and pinned narrative
minutes. Independent downloads matched all prepared body text and hyperlink targets;
Title promotion/readback passed. Word-web inspection showed agendas across one,
one and four pages, register minutes across two pages and narrative minutes on
one page. The final long paragraph appeared on agenda page four.

| Scope | Result | Boundary |
| --- | --- | --- |
| D01–D04 manual agenda variants | 0/1/12 counts/order, complete body, standing unresolved sections and corresponding paper targets preserved in native downloads and inspected Word views | Unchanged three-item baseline and live access to synthetic links are not claimed; existing real-paper access evidence stays separate. |
| D05–D09 manual minutes variants | Pinned four agenda passages/missing note/off-agenda concern and register open/closure-pending/closed/held distinctions visible; exact prepared content retained | Future/no-follow-up variants remain covered by existing local tests, not new native runs. |
| D10 manual editing | Native manual correction saved, closed, reopened and independently downloaded; separate R2 manually incorporates a distinctly identified fictional supplement, retaining the pinned baseline and correction | Manual reconciliation, no automatic regeneration/merge or silent relabelling of source revisions. |
| D11 create-only refusal | Unlocked agenda collision returned HTTP 400; UID/version/complete bytes unchanged | Edited-minutes collision returned HTTP 423 and preserved complete bytes/version; this is lock preservation, not destination-collision proof on that edited file. |
| D12 metadata/body | Live schema and existing saved Title/body/edit state reconfirmed; original failed refresh and positive metadata-preservation evidence reused | Automatic body refresh remains failed/unqualified. |

The selected minutes copies use the existing manual minutes template; earlier
agenda-template trial copies are retained as preimages, not accepted as minutes
template parity. The final narrative copy preserves the saved correction and the
separate source supplement in a distinct corrected template revision.

Exact native IDs, versions, template/input fingerprints, readbacks, render captures,
manual-revision lineage and first failures are private. The existing private track
retains untested historical-content restore and transport/race recovery limits.
No PDF, recipient-role access, automatic Word generation, flow activation, issuing
or distribution is claimed. No Copilot/Premium action, new column, permission,
licence, consent or operational-register change was used.
