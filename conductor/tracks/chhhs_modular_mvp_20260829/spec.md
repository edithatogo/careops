# Specification

## Goal

Adapt the existing CareOps repositories into a reusable, organisation-neutral
module portfolio that can support local credentialing and PPG assurance without
creating a replacement repository or embedding local policy in generic code.

## Requirements

1. Keep existing module repositories as the units of implementation and release.
2. Use `careops` as the shared portfolio control plane.
3. Remove active NSW Health authority, host, identity, and branding assumptions
   from reusable module surfaces.
4. Apply a permissive licence to original unlicensed repositories, subject to
   retained third-party terms.
5. Put organisation and jurisdiction-specific mappings in a deployment profile.
6. Deliver one bounded MVP before expanding to additional pathways or
   professional streams.
7. Add capabilities through versioned, reversible feature packs.
8. Keep AI advisory, provenance-rich, and subject to mandatory human review.
9. Keep operational, clinical, workforce, credential, and tenant data out of Git.
10. Distinguish repository completion, tenant deployment, and operating
    effectiveness.

## Acceptance criteria

- the parent topology no longer points to an organisation-specific upstream;
- the module catalog covers all current CareOps repositories;
- the organisation profile defines authority, privacy, pilot, and human-decision
  boundaries;
- a documented polyrepo decision and monorepo reconsideration gate exist;
- repository-level agent profiles reinforce modularity and assurance;
- module PRs introduce credentialing capability packs without changing current
  runtime behaviour by default;
- CI and publication boundaries remain intact; and
- each PR documents tests, deployment impact, rollback, and residual gates.
