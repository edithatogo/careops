## Summary

- Related issue:
- What changed:
- Why it was changed:

## Validation

- [ ] `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\Invoke-CiChecks.ps1`
- [ ] Validate receipts and drift check artifacts captured

## Security / governance notes

- [ ] No protected source data or secrets added
- [ ] Branch protections remain as required (no force push, no deletion, required checks)

## Merge constraints

- No CODEOWNERS/team approval required for this solo-maintainer model.
- Required checks only:
  - `validate` (both modes)
  - `workflow-lint`
  - `secret scan`
  - `codeql / analyze`
  - `coverage`
