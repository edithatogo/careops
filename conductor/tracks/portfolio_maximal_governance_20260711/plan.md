# Implementation plan

## Phase 1: Publication boundary and topology

- [x] Task: Establish the private CareOps portfolio repository
    - [x] Define deny-by-default tracked paths and confidentiality gate
    - [x] Define GHE-primary and GitHub-continuity topology
    - [x] Create private repositories and synchronize branches and tags
- [ ] Task: Inventory and classify component repositories
    - [x] Confirm `careops-approve` is an independent subrepo
    - [x] Confirm `tesl-mvp-alm` is not currently an independent Git repository
    - [ ] Promote additional components only after confidentiality review
- [ ] Task: Conductor - User Manual Verification 'Publication boundary and topology' (Protocol in workflow.md)

## Phase 2: Quality, security, and CI/CD

- [x] Task: Harden repository defaults and validation
    - [x] Add CODEOWNERS, dependency automation, minimal workflow permissions, and release validation
    - [x] Enable all currently entitled controls; do not claim unavailable GHAS features
    - [x] Record unsupported GHE controls and runner limitations
    - [x] Record current GHE Project and Advanced Security blockers with a sanitized handoff
- [x] Task: Establish continuity automation
    - [x] Push GHE first and GitHub second without destructive mirror deletion
    - [x] Verify branch equality and recoverability
- [ ] Task: Conductor - User Manual Verification 'Quality, security, and CI/CD' (Protocol in workflow.md)

## Phase 3: Traceability and portfolio planning

- [x] Task: Convert sanitized Conductor history into issues
    - [x] Create one issue per historical track in the relevant repository
    - [x] Close issues representing completed or archived work
    - [x] Link active issues to current plans without copying raw evidence
    - [x] Reconcile issue lifecycle from verified local plan/metadata state across GHE and GitHub (`b2e44dd`)
- [~] Task: Create repository and portfolio Projects
    - [x] Create a private GitHub Project for each repository
    - [x] Create an overarching private CareOps portfolio Project
    - [x] Link repository projects and issues by item-level mirroring
    - [ ] Create equivalent GHE Projects after the token receives `read:project` and `project` scopes
- [ ] Task: Conductor - User Manual Verification 'Traceability and portfolio planning' (Protocol in workflow.md)

## Phase 4: Analytics and work pipeline

- [x] Task: Assess Power BI remediation and semantic-model work
- [x] Task: Assess de-identified local `pm4py` conformance and bottleneck analysis
- [x] Task: Define a sequenced delivery pipeline from approvals to intranet execution
- [ ] Task: Conductor - User Manual Verification 'Analytics and work pipeline' (Protocol in workflow.md)
