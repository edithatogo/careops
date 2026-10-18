# Portfolio workflow

1. Inventory and classify a component before publication.
2. Reject secrets, personal data, operational exports, and generated evidence.
3. Retain the independent repository; materialise an optional submodule only for an exact reviewed source/release need.
4. Use the canonical public source remote for this parent; supply enterprise deployment destinations through private profiles.
5. Validate and publish reviewed public source through GitHub checks; follow separately configured enterprise delivery only where applicable.
6. Create sanitized issues from Conductor metadata; never copy raw evidence.
7. Use protected branches, least-privilege workflows, dependency automation,
   security scanning, and reproducible release artifacts where host policy permits.
8. Record unsupported host features as explicit blockers rather than weakening controls.
9. Require the fail-closed portfolio harness before checkpointing or publication.
10. Treat harness findings as blockers; do not suppress sensors to obtain a green build.
