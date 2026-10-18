# Credentialing coordinated-release automation

Status: repository implementation; review-only candidate generation

## Purpose

Reduce manual pinning errors across the modular CareOps repositories while preserving the distinction between a discovered repository head, a validated candidate and an approved coordinated release.

## Implemented

- reviewed registry of participating public repositories and refs;
- immutable `git ls-remote` resolution without credentials or shell interpolation;
- public HTTPS GitHub allowlist;
- stable module identifiers and required-MVP module checks;
- optional comparison with the previous release manifest;
- explicit list of changed modules;
- all promotion gates default to false;
- production writes remain false;
- deterministic candidate and SHA-256 receipt;
- network-free fail-closed unit tests; and
- scheduled or manually dispatched candidate generation with reviewable artifacts.

## Promotion sequence

```mermaid
flowchart LR
    A[Resolve reviewed public refs] --> B[Candidate: not validated]
    B --> C[Immutable checkout]
    C --> D[Cross-module contract tests]
    D --> E[Synthetic positive and negative pathways]
    E --> F[Source currentness and rights review]
    F --> G[Human release approval]
    G --> H[Versioned coordinated release]
```

The automation stops at the candidate. It does not update the release manifest, merge a pull request, deploy Power Platform, publish data or enable a production integration.

## Evidence ceiling

A generated candidate records repository heads at an observation time. It does not establish that those heads are compatible, safe, approved, deployed or operating effectively. Promotion requires the existing cross-module harness, source and rights review, and an accountable human release decision.
