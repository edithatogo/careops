# Workspace Tracking

This workspace is linked to external planning/design tools at a sanitized level. Sensitive source paths, server names, credentials, raw data, local inventories, and Power BI binaries stay in the private repository or ignored local folders.

## External Links

| Tool | Purpose | Link |
| --- | --- | --- |
| Linear | Project and issue tracking for the finance analytics roadmap | https://linear.app/edithatogo/project/careops-finance-analytics-09702fc5bad2 |
| Notion | Workspace summary page under the Linear Projects database | https://www.notion.so/3578e8c3448281ae8129ffd45e46adde |
| Figma | Sanitized Power BI dashboard mock-ups | https://www.figma.com/design/6KuDidCpQnbXWbHLwHxnJJ |

## Linear Records

- `EDI-165`: Validate local Power BI sample dashboards.
- `EDI-166`: Catalogue additional finance dashboards without bulk local transfer.
- `EDI-167`: Define shared semantic model and thin-report merge gates.

## Figma Mock-Up Scope

The Figma file contains four sanitized frames:

- Executive overview mock-up.
- Operational dashboard A mock-up.
- Operational dashboard B mock-up.
- System roadmap mock-up.

The mock-up intentionally uses placeholder labels and sample numbers. It does not include internal server names, network share paths, source database names, credentials, or real finance values.

## Working Rules

- Keep implementation evidence in git.
- Keep sensitive environment details in private local files or ignored generated outputs.
- Use Linear for task-level tracking, Notion for a readable workspace landing page, and Figma for design discussion.
- Do not publish raw Access databases, PBIX/PBIT files, generated extracts, generated remote inventories, SQL details, or credentials to external tools unless explicitly approved.
