# Specification

## Goal

Make finance reporting patterns reusable across CareOps without merging
repositories, operational data, security boundaries, or deployment ownership.

## Requirements

- generic, parameterised source and deployment configuration;
- PBIP, TMDL, and PBIR source control;
- reusable validation, reconciliation, RLS, ALM, and release evidence;
- synthetic sample data and no live environment values in Git;
- credentialing and PPG reporting only after stable operational sources,
  definitions, access, and small-cohort controls;
- no practitioner evidence, patient data, committee papers, decision reasons,
  or identifiable credentialing events in this module;
- AI-assisted model and report changes remain reviewed and source reconciled;
- polyrepo topology retained unless modules share the same deployment, owner,
  release, and security boundary.

## Acceptance criteria

- active README and track registry are organisation-neutral;
- permissive licence present;
- shared reporting boundary documented;
- live hosts, paths, database names, and gateway values are absent from active
  reusable guidance;
- source-control and live-refresh readiness are reported separately; and
- no implication that CareOps Finance is the authority for another module's
  operational or clinical data.
