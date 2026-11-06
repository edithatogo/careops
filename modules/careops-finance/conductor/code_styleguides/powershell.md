# PowerShell Style Guide

- Prefer advanced functions with `[CmdletBinding()]` for reusable scripts.
- Use `-LiteralPath` for filesystem paths that may contain spaces.
- Keep scripts read-only against source databases unless a task explicitly requires mutation.
- Return structured JSON or objects for automation-facing commands.
- Fail fast with clear errors when providers, paths, or credentials are missing.
