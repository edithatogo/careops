# Simplified implementation plan

1. Finish the existing preparation → agenda/papers → minutes → actions route.
   Reuse working records and flows. Use existing SharePoint library columns and
   maintained Word templates with manual narrative/revisions, assuming no Copilot
   or Premium connectors; follow [the selected route](library-column-word-route.md).
2. Use an existing meeting entry point and preparation/follow-up views. Build a
   Power Apps interface only where the current surface leaves a concrete gap.
3. Preserve agenda IDs, paper links, decisions, conditions and actions across the
   cycle. Keep decisions in minutes and one authoritative action register.
4. Reuse selected CareOps Decisions patterns: meeting-series defaults, agenda
   sections, optional attendance/conflicts/quorum and appropriate record states.
   Do not import its entire architecture or force a Dataverse migration.
5. Defer identity synchronisation, service accounts, enterprise pipelines,
   transcription/AI and duplicate task trackers unless separately needed.

Each selected slice: implement, inspect saved configuration and actual output,
verify affected failure/recovery behaviour, record once and close technical scope.
Representative fictional inputs are sufficient. Real-register cutover or sending
records is a separate operation, not a universal software-completion gate.

Delivery lessons: use narrow source-to-output increments, stable identities,
whitelisted updates and commit-last checkpoints. Close a bounded working capability
without waiting for optional extensions. Retain native statuses in the private
operational workspace; never claim deployment from local source tests.

## Modular suite evolution — 18 October 2026

Use [the ordered low-hanging-fruit queue](suite-delivery.md) for development-first
dependency alignment, optional interoperability and structured-document improvements.
Preserve current work and historical completion evidence; these improvements do
not reopen completed MVPs or establish native deployment/operational acceptance.
