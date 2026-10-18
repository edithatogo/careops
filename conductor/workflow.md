# Portfolio workflow

1. Inventory and classify a component before publication.
2. Reject secrets, personal data, operational exports, and generated evidence.
3. Add the component as an independent repository and submodule.
4. Make GHE `origin` and private GitHub `github` for every component.
5. Validate locally, push GHE first, then push the same commit and tags to GitHub.
6. Create sanitized issues from Conductor metadata; never copy raw evidence.
7. Use protected branches, least-privilege workflows, dependency automation,
   security scanning, and reproducible release artifacts where host policy permits.
8. Record unsupported host features as explicit blockers rather than weakening controls.
9. Require the fail-closed portfolio harness before checkpointing or publication.
10. Treat harness findings as blockers; do not suppress sensors to obtain a green build.
