# Specification: maximal portfolio governance

## Requirements

- Maintain a private `careops` portfolio repository with independent subrepos.
- Make GHE primary and mirror every commit and tag to private GitHub.
- Prevent confidential, personal, tenant, clinical, workforce, and operational
  information from entering any repository.
- Convert sanitized Conductor history into repository issues and close completed
  historical work.
- Create a project for each repository and one overarching portfolio project.
- Maximize quality, security, dependency management, CI/CD, releases, rules,
  environments, and available GHE advanced or preview features without requiring
  additional authority.
- Preserve a complete GitHub continuity copy if GHE access is lost.
- Evaluate Power BI and local `pm4py` work against decision value and data safety.

## Non-goals

- Publishing raw historical evidence or tenant exports.
- Enabling features that require unavailable administrator rights.
- Using public repositories or public Projects.
