# H2 — Native implementation continuation

Selected28October2026. The read-only native implementation proposal is complete;
remaining implementation/review is active. Exact target IDs, connection references,
source preimages and the full proposal remain private. No native mutation or run
has yet occurred in this continuation. H1/H2-U/H2-R gaps remain open.

## Current exact-target facts

Guarded reads using the retained Toolkit workload verified the existing site and
qualification library, schema, permissions and native F06/F07/F12 definitions.
An expired SharePoint resource was renewed silently through the same verified
client/account/resource, preserving normal persistence; the original exact read
then passed. No browser login, new client/consent, cache transfer or reset.

F06/F07/F12 are Stopped. The current principal has Owner/CanEdit on the two
permission-inventoried flows, and the site/library masks include ManageLists.
These are read/permission facts, not successful save or runtime proof. Existing
SharePoint and Outlook references are Standard/Invoker; runtime rights remain
separate. Existing flows will be preserved, including their state and ACL.

The Documents library has two On/immediate/email-capable alert records and an
active push subscription. The existing Clinical Hub qualification library instead
has no matching alerts, rules or subscriptions; assignment mail and approval
workflow are off, versioning on, checkout off and only four first-party receivers.
Reuse that library; no new store, app, Team, list or action register is needed.
Legacy alert retirement announcements are not proof that a tenant record cannot
generate mail. Do not test delivery or change existing notifications to find out.

## Minimal selected implementation

- Add two list-local document content types and32 absent typed fields for profile
  revision/effective dates, controls/sections, separate role/evidence states and
  sources, template/destination/register choices, occurrence/profile/time/lineage,
  selected sources and output revision. Existing default Document fields, files,
  views, permissions and original content remain intact. Add a nondefault view.
- Use native properties/lookups for ordinary configuration. Makers own technical
  IDs and immutable configuration package qualification via existing pure code.
  SHA256 is computed upstream during maker configuration packaging, not invented
  as an unsupported native expression. Metadata/source changes require fresh
  package qualification; no ordinary JSON/GUID/code editing.
- Prepare one manual standard-connector bridge, reserved alias F16. Existing
  fixed-paper/manual trigger contracts cannot accept selected configuration
  without breaking callers. A single new logical entry point is justified, not
  one flow per forum or copied business workflow. Preserve F06/F07/F12 untouched.
  The bridge performs per-operation binding/readback and review-only preparation,
  with create-only technical receipts in the same library. No business writes,
  assignments, closure, email, scheduled intake or automatic Word renderer.
- Qualify no-email effects before any native run. Existing flows still report
  repair-alert subscriptions enabled; do not run them as failure probes. Qualify
  supported suppression for the new stopped bridge and current digest behaviour
  without changing live flows or global settings. Keep runtime held on a gap.

## Execution and acceptance queue

- [x] H2-N01 Exact-target read-only proposal, minimal diff, permissions and tests.
- [ ] H2-N02 Implement/test schema and package/native bridge source; save exact
  permitted schema and stopped candidate with full independent native readback.
- [ ] H2-N03 Qualify ordinary-user forms and bounded fictional runtime/negative/
  concurrent/replay/partial-save/history/rollback behaviour without emails.
- [ ] H2-N04 Reconcile H2-U01–05/R01–04/native H2.4b from actual proof, review using
  conductor-review, apply fixes and complete release-boundary audit.
- [ ] H2-N05 Archive the track only after complete technical native scope passes;
  retain H1 real-governance gaps and later H3/H4/correspondence follow-ups.

No native send, live-flow change, deferred correspondence work, public publication
or real forum pilot follows. Existing governance and operational ownership remain.
The broader user instruction authorises continuing H2 implementation/review after
this proposal; it does not waive permission, no-email, exact-target, runtime or
real-governance gates.

See [H2 plan](h2-forum-reuse-plan.md), [operator gaps](h2-operator-configuration.md),
[native recovery limits](h2-source-recovery.md) and
[previous source boundary](h2-release-boundary-review.md).

## Schema source implementation checkpoint

The pure `forum_native_schema.build_schema` now emits the32 additive fields and
two list-local content types for one explicit maker-selected library GUID.13
focused tests passed: no default Document/view/permission/library changes, stable
schema IDs, exact lookup target, unverified defaults, hidden technical inputs and
separate content-type links. This source plan is not native save/readback proof.
