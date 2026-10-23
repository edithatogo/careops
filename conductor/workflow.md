# Portfolio workflow

1. Inventory and classify a component before publication.
2. Reject secrets, personal data, operational exports, and generated evidence.
3. Retain independent repositories by default. Where the user selects direct-source migration, use the existing module track to review/sanitise source, preserve private recovery history, qualify and merge ordinary module files, then verify private archival of the replaced repository. Incidents is the first authorised direct-source migration.
4. Use the canonical public source remote for this parent; supply enterprise deployment destinations through private profiles.
5. Validate and publish reviewed public source through GitHub checks; follow separately configured enterprise delivery only where applicable.
6. Create sanitized issues from Conductor metadata; never copy raw evidence.
7. Use protected branches, least-privilege workflows, dependency automation,
   security scanning, and reproducible release artifacts where host policy permits.
8. Record unsupported host features as explicit blockers rather than weakening controls.
9. Require the fail-closed portfolio harness before checkpointing or publication.
10. Treat harness findings as blockers; do not suppress sensors to obtain a green build.

11. Use [targeted testing](../docs/targeted-testing.md) during edits; reserve the
    full suite for coherent integration/release milestones. Cache state is local
    acceleration, never complete acceptance evidence.
