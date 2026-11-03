# Local platform source

| Area | Local artifact | Acceptance scope |
| --- | --- | --- |
| SharePoint | [List and library schema](sharepoint/schema.json) | Typed field CAML, indexed unique source and identity keys, versioning and offline command plan |
| Teams | [Tab request](teams/tab-request.json) | Exact team/channel binding, SharePoint URL constraints and URL-safe native channel IDs |
| Power Automate | [Stopped flow candidates](automate/README.md) | Revision capture, replay, conflict and incomplete-page handling, effective and observed timestamps |
| Power BI/Fabric | tools/build_analytics.py | Star model, report source, paginated report and definition payloads from selected local inputs |
| Independent solution | [PAC source](solution/src/Other/Solution.xml) | Unique name, publisher and version; offline scaffold pack/unpack |

The Power Automate connector candidates use the OpenApiConnection export shape.
The public Logic Apps WDL schema does not describe that action type. Structural
and dependency checks cover the candidate actions. Native save/readback and
runtime remain acceptance work.

PAC packaging covers the independent solution scaffold. SharePoint, Teams and BI
are companion artifacts. Including the authored flows as solution workflow
components requires qualified component metadata and connection mapping source.

The model uses frozen local import partitions. SharePoint or Fabric refresh
binding is a deployment-specific operation. The report and RDL need native
rendering and refresh checks after deployment authority.

Narrative documents should use maintained SharePoint structured documents once
the exact availability and prerequisites are qualified. Tabular reporting uses
RDL and a locally printable HTML counterpart. Retain included record IDs, source
and template versions and output revision with issued artifacts. Preserve human
edits and issued history.
