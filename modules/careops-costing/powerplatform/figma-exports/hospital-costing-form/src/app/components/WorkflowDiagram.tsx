import { ArrowRight, CheckCircle2, ClipboardList, Settings, Calculator, Users, BarChart3, Lock } from "lucide-react";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";

export function WorkflowDiagram() {
  const stages = [
    {
      id: 1,
      title: "Reference and cycle setup",
      icon: Settings,
      color: "bg-sky-500",
      workbookAnchor: "SWSetup, NSWHAwards, NSWHPayCalendar, NSWWH* reference sheets",
      summary:
        "Open the budget cycle, publish current rates, phase codes, cost centres, awards, and calendar controls.",
      points: [
        "Version configuration by financial year",
        "Promote approved rates and constants into Dataverse configuration tables",
        "Lock production changes behind deployment governance",
      ],
    },
    {
      id: 2,
      title: "Position build and roster capture",
      icon: ClipboardList,
      color: "bg-indigo-500",
      workbookAnchor: "SWInput",
      summary:
        "Capture organisation, position, award, employment, roster, overtime, leave, and allowance inputs in structured forms.",
      points: [
        "Drive derived fields from selected cost centre and award",
        "Separate main record from child roster and allowance rows",
        "Support draft save, validation, and guided completion",
      ],
    },
    {
      id: 3,
      title: "Calculation and validation engine",
      icon: Calculator,
      color: "bg-violet-500",
      workbookAnchor: "SWNotes, NSWHFormulas",
      summary:
        "Translate workbook formula blocks into server-side rules, plug-ins, calculated tables, and controlled configuration.",
      points: [
        "Recreate 701–724 and 728 cost elements",
        "Convert hours, relief, and leave assumptions into FTE outputs such as 820 Productive FTE",
        "Flag missing reference data, invalid combinations, and out-of-bounds values",
      ],
    },
    {
      id: 4,
      title: "Review and approval",
      icon: Users,
      color: "bg-amber-500",
      workbookAnchor: "M / S / E permissions",
      summary:
        "Move records through draft, DMS review, executive approval, and finalisation with full audit trace.",
      points: [
        "M users create and submit",
        "S users review, return, or approve at DMS stage",
        "E users provide final approval or rejection",
      ],
    },
    {
      id: 5,
      title: "Reporting and extract publication",
      icon: BarChart3,
      color: "bg-emerald-500",
      workbookAnchor: "Summ, SWBrief, BTSExtract, FTEExtract, ROSExtract",
      summary:
        "Expose governed summaries, operational dashboards, and file/API outputs once records are finalised.",
      points: [
        "Preserve workbook-compatible coding where needed",
        "Publish finance and workforce extracts through scheduled flows",
        "Expose readiness and reconciliation status to operations",
      ],
    },
    {
      id: 6,
      title: "Security and governance overlay",
      icon: Lock,
      color: "bg-slate-600",
      workbookAnchor: "Role assignments, app visibility, audit trail",
      summary:
        "Layer scoped access, deployment controls, field locking by status, and audit evidence across the whole process.",
      points: [
        "Scope by site, directorate, and cost centre",
        "Protect approved records from informal edits",
        "Retain traceability for every recalculation and decision",
      ],
    },
  ];

  const crossCutting = [
    {
      title: "Workbook logic preserved",
      text:
        "The design keeps the workbook’s Inputs → Formulae → Outputs / Extracts pattern, but moves logic into governed application and data layers.",
    },
    {
      title: "Extract compatibility",
      text:
        "BTSExtract, FTEExtract, and ROSExtract remain first-class outputs instead of becoming an afterthought in reporting.",
    },
    {
      title: "Configuration before code",
      text:
        "Awards, rates, calendars, project mappings, and phase codes are externalised into maintainable configuration tables.",
    },
    {
      title: "Approval-aware data model",
      text:
        "The status model is embedded into the record lifecycle so calculations, field editability, and exports all respond to approval stage.",
    },
  ];

  return (
    <div className="mx-auto w-full max-w-7xl space-y-6">
      <div className="space-y-2 text-center">
        <h2 className="text-3xl font-bold text-slate-900">Target operating workflow</h2>
        <p className="mx-auto max-w-4xl text-sm text-slate-600 md:text-base">
          The future-state process is no longer a single spreadsheet interaction. It becomes a
          governed workflow that starts with controlled setup, captures structured budget inputs,
          runs repeatable calculations, and only publishes approved outputs.
        </p>
      </div>

      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {stages.map((stage, index) => (
          <div key={stage.id} className="relative">
            <Card className="h-full rounded-2xl border-slate-200 p-6 shadow-sm">
              <div className="mb-4 flex items-start justify-between gap-4">
                <div className={`flex h-14 w-14 items-center justify-center rounded-2xl ${stage.color}`}>
                  <stage.icon className="h-7 w-7 text-white" />
                </div>
                <Badge variant="outline">Step {stage.id}</Badge>
              </div>

              <div className="space-y-3">
                <div>
                  <h3 className="text-xl font-semibold text-slate-900">{stage.title}</h3>
                  <p className="mt-1 text-xs font-medium uppercase tracking-[0.14em] text-slate-500">
                    {stage.workbookAnchor}
                  </p>
                </div>

                <p className="text-sm leading-6 text-slate-600">{stage.summary}</p>

                <ul className="space-y-2 text-sm text-slate-700">
                  {stage.points.map((point) => (
                    <li key={point} className="flex items-start gap-2">
                      <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0 text-emerald-500" />
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </Card>

            {index < stages.length - 1 && (
              <div className="pointer-events-none absolute -right-2 top-1/2 hidden -translate-y-1/2 xl:block">
                <ArrowRight className="h-5 w-5 text-slate-300" />
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {crossCutting.map((item) => (
          <Card key={item.title} className="rounded-2xl border-slate-200 p-5 shadow-sm">
            <h4 className="font-semibold text-slate-900">{item.title}</h4>
            <p className="mt-2 text-sm leading-6 text-slate-600">{item.text}</p>
          </Card>
        ))}
      </div>

      <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-3xl">
            <h3 className="text-lg font-semibold text-slate-900">Design intent</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              This advanced workflow deliberately keeps the workbook’s domain semantics visible:
              position, award, relief, leave, allowance, coded outputs, and extract readiness.
              The change is not only visual modernisation; it is a shift from hidden spreadsheet
              logic to explicit application behaviour that can be tested, governed, and supported.
            </p>
          </div>
          <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">
            <p className="font-semibold text-slate-900">Key preserved output families</p>
            <p className="mt-2">701–724, 728 cost lines</p>
            <p>732 / 734 / 738 / 743 control lines</p>
            <p>820 / 822 and related FTE outputs</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
