# Review/versioning executable reference qualification — 11 November 2026

**Status: locally tested source-only reference; NOT integrated into GitHub or native SharePoint/Power Platform, and NOT approved for CHHHS use.**

## Implemented in a separate synthetic-only working artifact (not in repository)

A stdlib Python in-memory reference domain engine models:
- practitioner-created freely editable drafts; explicit submit creates an immutable canonical-json SHA-256 candidate and review case;
- idempotent submission and delegated decision operations, strict key replay/payload matching, stale-draft ETag guards;
- effective-dated practitioner and approver grants; service boundary, unrelated access denial and no-self-approval;
- rejected and approved snapshots with retained version sequence and approved effective date, before/after activation;
- effective-dated review rules, obligation keys, daily due sweep replay safety, due-date preservation after later policy editions and a human no-change attestation;
- authorised history view.

**Test evidence:** 10 synthetic deterministic `unittest` cases passed locally on Python 3.13, including negative cases for self-approval, expired acting delegation, cross-service access, stale edits, duplicate operations, canonicalisation/NaN rejection and delayed policy sweep. A test-first RED run failed before implementation; later a delayed policy sweep regression failed and was corrected; subsequent full suite was green. Source file and ZIP integrity checked with `compileall` and `ZipFile.testzip`. Local artifact manifest uses SHA-256. No attached source documents, real employee schedules, staff names or identifying content in the reference package.

**Critical evidence limit:** this text is a design/test receipt, **not** a claim that the implementation source has been committed to the repository, or that CI on a GitHub ref has passed. A future integration task must bring the reviewed, tested source and its tests into a suitable independent CareOps Workforce code location while avoiding modifications to the existing source-locked Workforce.pbip. The package is available as a generated user conversation artifact, not as a source repo URL.

## Source completion — bounded

| Contract | Local evidence | Native assurance |
|---|---|---|
| Draft / explicit submit / snapshot hash | Tested | Pending |
| Idempotent submission & decision | Tested in one process | Durable restart-safe ledger pending |
| Delegated approval / self-approval | Synthetic actor-tested | Entra/SharePoint and delegation readback pending |
| Effective-date activation and history | Deterministic test | Atomic SharePoint transaction & retention pending |
| Review policy version / unique due | Tested incl. late sweep | Policy authority/migration and repeated flow pending |
| No-change attestation | Synthetic test | Delegated human approval proof pending |
| Multi-stage clinical/HR/industrial review | Not implemented in reference | Pending |
| Cloud solution, Power Fx, flows, SharePoint adapter, CI | Not implemented | Pending |

## Prioritised completion

1. **JP-VC01**: integrate local reference engine + synthetic tests as source in an independent workforce app package, preserving the pre-existing PBIP source lock; run repository-native CI on exact head.
2. **JP-VC02**: implement server-enforced identity+delegation and transition policy; practitioner may save drafts but all submitted/approved state writes validate permissions, authority edition and ETag.
3. **JP-VC03**: implement transactional SharePoint persistence with durable idempotency keys, compare-and-swap, outbox and immutable snapshots; test parallel requests and restart/replay.
4. **JP-VC04**: qualify policy migrations, overlapping revisions, pending effective-date cutovers, time zones, no-change review and backfill.
5. **JP-VC05**: qualify SharePoint list and exported history ACLs, scale, retention, records holds and accessible dual-role dashboard projections.
6. **JP-VC06**: build solution-aware flows, portable import package and validate in authorised dev tenant. No production authority implied.

Until these are complete, mark **source reference tested / production implementation pending** and do not mark JP-02.6–02.9, JP-03.20–03.25 or G2–G5 complete.

## Known limitations of the reference engine

The simplified model uses an in-memory single-delegate decision rather than the full Clinical Director/HR-IR/employer multi-gate route. It is nontransactional, nonpersistent, assumes the caller is trusted to supply timestamp and actor for its in-memory tests, and does not enforce real SharePoint permissions. Future-effective approvals anchor review at future activation; the temporal interactions of interleaved approved amendments and older obligations need further implementation. The draft CHHHS job-planning instruction is not an approved current rule set.

**Security:** original Word/PDF work instructions and identifiable clinician schedules remain off Git, CI and artifacts.
