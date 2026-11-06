import { ArrowRight, CheckCircle2, FileSpreadsheet } from "lucide-react";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";

export function ExcelMigrationMap() {
  const mappings = [
    {
      workbook: "SWInput",
      target: "Power Apps forms + PositionBudgetRecord, RosterPattern, LeaveAllowanceProfile",
      pattern: "Break wide worksheet input into a main record plus related child rows",
      note: "Primary user-entry surface for position, award, roster, leave, and allowance assumptions.",
    },
    {
      workbook: "SWSetup + NSWHAwards + NSWHSTSRates + NSWHPayCalendar",
      target: "Configuration and reference tables",
      pattern: "Externalise rates, calendars, caps, and award attributes into governed master data",
      note: "Avoid hard-coded spreadsheet constants and let deployments promote approved setup data.",
    },
    {
      workbook: "NSWHCostCentres + NSWHProjects + NSWHBudgetClass",
      target: "Organisation and coding reference tables",
      pattern: "Lookup-driven validation and auto-derivation",
      note: "Supports derivation of Division, Sector, Facility, Entity, project, and coding outputs.",
    },
    {
      workbook: "SWNotes + NSWHFormulas",
      target: "Business rules, plug-ins, and calculated outputs",
      pattern: "Translate long formulas into explicit rule catalogue and server-side execution",
      note: "This is where 701–724 / 728 cost logic and many derived FTE behaviours move.",
    },
    {
      workbook: "Summ + SWBrief",
      target: "Summary views and Power BI semantic model",
      pattern: "Replace opaque summary sheets with drillable reporting",
      note: "Still preserve the same business totals so parallel run and sign-off are possible.",
    },
    {
      workbook: "SWExtract + BTSExtract + FTEExtract + ROSExtract",
      target: "Export service + scheduled Power Automate flows",
      pattern: "Treat extracts as governed publication artefacts",
      note: "Do not bury interface logic in BI; maintain code-compatible outbound structures.",
    },
    {
      workbook: "PCInput",
      target: "Phase-code / phasing configuration",
      pattern: "Dedicated configuration table or admin surface",
      note: "Supports phasing behaviour and coded output patterns such as PHOL_* and CALE.",
    },
  ];

  const principles = [
    "Preserve output codes and interfaces before rethinking visuals.",
    "Move constants into configuration so rule changes do not require sheet surgery.",
    "Use parallel run comparison packs to validate workbook vs platform results by element and FTE.",
    "Keep a clean audit trail for recalculation, approval, and extract publication events.",
  ];

  const parallelRun = [
    "Compare 701–724 / 728 totals by cost centre and position.",
    "Compare 732 / 734 / 738 / 743 control outputs and balancing logic.",
    "Compare 820 Productive FTE and 822 Overtime FTE before sign-off.",
    "Compare outbound BTS / FTE / ROS record counts and code patterns.",
  ];

  return (
    <div className="mx-auto w-full max-w-7xl space-y-6">
      <div className="space-y-2 text-center">
        <h2 className="text-3xl font-bold text-slate-900">Workbook-to-platform mapping</h2>
        <p className="mx-auto max-w-4xl text-sm text-slate-600 md:text-base">
          This view makes the migration strategy explicit: each workbook asset is mapped to a
          sustainable Power Platform construct rather than being recreated as a giant form.
        </p>
      </div>

      <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
        <div className="mb-4 flex items-center gap-2">
          <FileSpreadsheet className="h-5 w-5 text-sky-600" />
          <h3 className="text-lg font-semibold text-slate-900">Mapping table</h3>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left">
                <th className="px-3 py-3 font-semibold text-slate-700">Workbook sheet / asset</th>
                <th className="px-3 py-3 font-semibold text-slate-700">Target component</th>
                <th className="px-3 py-3 font-semibold text-slate-700">Migration pattern</th>
                <th className="px-3 py-3 font-semibold text-slate-700">Why it matters</th>
              </tr>
            </thead>
            <tbody>
              {mappings.map((mapping) => (
                <tr key={mapping.workbook} className="border-b border-slate-100 align-top">
                  <td className="px-3 py-4">
                    <Badge variant="outline">{mapping.workbook}</Badge>
                  </td>
                  <td className="px-3 py-4 text-slate-800">{mapping.target}</td>
                  <td className="px-3 py-4 text-slate-600">{mapping.pattern}</td>
                  <td className="px-3 py-4 text-slate-600">{mapping.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900">Migration principles</h3>
          <div className="mt-4 space-y-3">
            {principles.map((principle) => (
              <div key={principle} className="flex items-start gap-2 rounded-2xl bg-slate-50 p-4">
                <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0 text-emerald-600" />
                <p className="text-sm leading-6 text-slate-700">{principle}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900">Parallel run controls</h3>
          <div className="mt-4 space-y-3">
            {parallelRun.map((item) => (
              <div key={item} className="rounded-2xl bg-slate-50 p-4">
                <div className="flex items-start gap-2">
                  <ArrowRight className="mt-0.5 h-4 w-4 flex-shrink-0 text-violet-600" />
                  <p className="text-sm leading-6 text-slate-700">{item}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
