# Security Policy

## Reporting

- Report security issues as `confidential` GitHub security advisories.
- Do not post credentials, internal server names, or environment secrets in issues.
- Keep payload-only files and restricted data out of public artifacts.

## GitHub hardening

- `main` branch protections now block force pushes and branch deletion.
- Protected checks must pass before merge.
- No mandatory human approval gate is enforced in this repository.

## Sensitive artifacts

- Raw data and credentials must remain outside the repository.
- Keep `.env`, `.json` secrets, and environment bindings in operator-owned local profiles only.
