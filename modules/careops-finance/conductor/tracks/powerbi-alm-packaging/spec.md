# Power BI ALM Packaging

## Objective

Make the Power BI project ready for a private GitHub repo and later ALM deployment without deploying in the short term.

## Requirements

- Keep `.accdb`, `.pbix`, `.pbit`, extracts, profiles, lock files, and credentials out of git.
- Keep each standalone dashboard's semantic model source in TMDL or compatible PBIP/PbixProj format.
- Keep deployment profiles disabled until tenant, workspace, and service principal details are confirmed.
- Add validation for script syntax, data-ignore behavior, Power BI CLI readiness, and deployment manifest sanity.
- Document push instructions for the private `careops-finance` GitHub repo.

## Acceptance Criteria

- `git status --ignored` confirms data is ignored.
- `scripts/Invoke-Validation.ps1` passes locally and in GitHub Actions.
- Deployment manifest uses environment variables for secrets and disabled placeholder workspaces.
- README explains the no-data-in-git policy and later deployment path.
- Separate dashboard folders can be deployed independently or merged later through a shared semantic model path.
