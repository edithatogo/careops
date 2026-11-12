# Contributing

## Branch and quality guard

- Keep changes in topic branches from `main`.
- Run the repo quality gate before opening a PR:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\Invoke-CiChecks.ps1
```

## Scope rules

- Keep raw `.accdb`, credentials, and environment files out of version control.
- Do not bypass branch protections; updates to `main` are by PR path with passing checks.
- Keep PR descriptions short and include validation mode outputs.

## PR merge policy

- No CODEOWNERS/team gates are required for this solo-maintainer repository.
- Merge is allowed once all required checks are green.
