"""Non-premium offline RIMS field-accounting report, source-only and sanitised.

Displays domain totals, no private source values or field paths. Native Power BI
visual use is NOT inferred from declared mappings; no emails or network calls.
"""
from __future__ import annotations
from html import escape


class CoverageReportError(ValueError):
    pass


def _nonnegative(value):
    return type(value) is int and value >= 0


def render_html(rollup):
    if not isinstance(rollup, dict) or rollup.get('schema')!='careops-rims.existing-source-coverage-rollup/1':
        raise CoverageReportError('unsupported source coverage contract')
    if rollup.get('full_field_utilisation_proven') is not False or rollup.get('native_model_parity_proven') is not False:
        raise CoverageReportError('native completeness claim cannot be displayed without independent acceptance')
    domains=rollup.get('domain_summaries')
    if not isinstance(domains,list):raise CoverageReportError('domain totals missing')
    rows=[];seen=set()
    for data in sorted(domains,key=lambda v:str(v.get('domain',''))):
        if not isinstance(data,dict):raise CoverageReportError('invalid domain row')
        name=data.get('domain')
        if not isinstance(name,str) or not name or name in seen:
            raise CoverageReportError('domain identity invalid/duplicate')
        seen.add(name)
        keys=('fields_observed','mapped_to_consumer','retained_only','excluded_with_reason','unassessed')
        if any(not _nonnegative(data.get(k)) for k in keys):
            raise CoverageReportError('invalid domain totals')
        n,used,retained,excluded,unassessed=(data[k] for k in keys)
        if n!=used+retained+excluded+unassessed:
            raise CoverageReportError('counts do not reconcile')
        accounted=(n-unassessed)/n if n else None
        mapped=used/n if n else None
        fmt=lambda v:'Not assessed' if v is None else f'{v*100:.1f}%'
        rows.append('<tr>'+'<td>'+escape(name)+'</td>'+''.join(
            '<td>'+str(x)+'</td>' for x in (n,used,retained,excluded,unassessed))+
            '<td>'+fmt(accounted)+'</td><td>'+fmt(mapped)+'</td></tr>')
    body=''.join(rows) if rows else '<tr><td colspan="8">No assessed domain profiles</td></tr>'
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
      "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
      "<title>RIMS source field coverage</title>"
      "<style>body{font:16px system-ui;max-width:1100px;margin:2rem auto;padding:1rem}"
      "table{border-collapse:collapse;width:100%}th,td{padding:.65rem;border:1px solid #aaa;text-align:left}"
      "thead{background:#eee}caption{text-align:left;font-weight:600;margin:1rem 0}"
      "p{line-height:1.5}td:nth-child(n+2){font-variant-numeric:tabular-nums}</style></head>"
      "<body><h1>RIMS existing-source field coverage</h1>"
      "<p><strong>Source-only:</strong> mapped fields are declared consumer links, "
      "not verified analytical utilisation. A field can be accounted for without "
      "being used. Source completeness, current freshness, Power BI parity and "
      "rights remain independently unverified.</p>"
      "<table><caption>Declared consumer mappings and field accounting by domain</caption>"
      "<thead><tr><th>Domain</th><th>Observed paths</th><th>Mapped</th>"
      "<th>Retained only</th><th>Rights-excluded</th><th>Unassessed</th>"
      "<th>Accounted for</th><th>Declared consumer mappings</th></tr></thead>"
      "<tbody>"+body+"</tbody></table>"
      "<p>No personal records, source text or detailed field paths are included. "
      "Review even aggregated figures for disclosure risk before sharing.</p>"
      "</body></html>")
