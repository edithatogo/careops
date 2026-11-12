# Power BI Source

This folder is reserved for source-controlled Power BI assets. The dashboards are intentionally separated so they can be built and validated independently, then merged later if the business definitions converge.

- `shared/` - shared Power Query contracts and later shared semantic-model assets.
- `dashboards/vmo-finance/` - standalone VMO Finance dashboard project.
- `dashboards/medical-staff/` - standalone Medical Staff dashboard project.
- `Deployment/` - root-level deployment notes for later ALM.

Do not commit `.pbix`, `.pbit`, raw Access files, extracted CSVs, or credentials.
