# Access to Power BI Migration Notes

## Source Handling

The Access files are treated as immutable raw inputs. Scripts should read from `data/raw/` and write generated outputs to `data/profile/` or `data/extracts/`, both of which are ignored by git.

## Access Object Types

Access inventory can include:

- `TABLE` - local physical tables, preferred for export.
- `VIEW` - saved queries, useful for business logic discovery.
- `LINK` - external source links; export may require network access or credentials.
- `PASS-THROUGH` - server-side SQL; document before recreating in Power Query or the source platform.
- `SYSTEM TABLE` / `ACCESS TABLE` - internal Access metadata, excluded by default.

## Conversion Strategy

1. Inventory objects and columns.
2. Identify local fact-like tables, dimensions, linked sources, and pass-through dependencies.
3. Export local tables for profiling.
4. Recreate business transformations in Power Query M or upstream SQL where appropriate.
5. Build the semantic model in Power BI Desktop.
6. Export TMDL and report source into `src/powerbi/`.
7. Add deployment profiles only after the workspace and environment names are confirmed.

## Current Known Risk

The large Medical Staff database may be slow to open for metadata enumeration. If it keeps stalling, use Microsoft Access compact/repair on a copy, or inventory it object-by-object with a longer timeout.
