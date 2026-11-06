# Product Context

## Product

`careops-finance` is a migration project for turning local Microsoft Access finance reporting databases into a maintainable Power BI reporting solution.

## Users

- Finance and operations users who need reliable reporting from existing Access data.
- Report developers who need a repeatable CLI workflow for inventory, extraction, model source control, and later deployment.
- Platform owners who need the project to be private-repo-ready and ALM-compatible before formal deployment starts.

## Goals

- Preserve the Access databases as raw local inputs while moving transformation and BI logic into source-controlled code.
- Inventory tables, queries, linked sources, columns, and row counts using repeatable CLI scripts.
- Extract local Access tables into reproducible, git-ignored staging outputs for Power BI development.
- Establish Power BI source folders that can accept TMDL/PBIP/pbi-tools exports once the model is created.
- Keep credentials, raw databases, and extracted data out of git.

## Non-Goals

- No production Power BI Service deployment in the short term.
- No live mutation of source Access databases.
- No committing raw finance data or generated extracts to git.

## Constraints

- Windows-first workflow.
- Microsoft ACE OLEDB provider is the preferred Access CLI bridge.
- Some Access objects may be linked tables or pass-through queries that require external credentials or network connectivity.
- Power BI source must be structured for later ALM even while local development continues.
