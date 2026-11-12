import { ArrowDown, Cloud, Database, Lock, Monitor, RefreshCw, Server } from "lucide-react";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";

export function IntegrationArchitecture() {
  const layers = [
    {
      title: "Identity and experience layer",
      icon: Monitor,
      tint: "bg-sky-50 border-sky-200",
      items: [
        "Model-driven app for budget buildup, review, and approval",
        "Optional canvas app for quick actions and mobile approvals",
        "Power BI reports tailored to M, S, E, and finance operations",
      ],
    },
    {
      title: "Process and orchestration layer",
      icon: RefreshCw,
      tint: "bg-violet-50 border-violet-200",
      items: [
        "Business process flow for Draft → DMS Review → Executive Approval → Finalised",
        "Server-side rules / plug-ins for cost element and FTE calculations",
        "Power Automate for notifications, escalations, extracts, and batch publication",
      ],
    },
    {
      title: "Data and content layer",
      icon: Database,
      tint: "bg-emerald-50 border-emerald-200",
      items: [
        "Dataverse tables for records, references, approvals, outputs, and role assignments",
        "SharePoint or governed document store for attachments and working papers",
        "Audit, status history, and reconciliation evidence retained with each record",
      ],
    },
    {
      title: "Integration and publication layer",
      icon: Server,
      tint: "bg-amber-50 border-amber-200",
      items: [
        "BTSExtract, FTEExtract, and ROSExtract published as governed outputs",
        "Potential downstream connections to finance, workforce, and data warehouse platforms",
        "Compatibility services preserve workbook-era code patterns during transition",
      ],
    },
    {
      title: "Platform control layer",
      icon: Lock,
      tint: "bg-slate-50 border-slate-200",
      items: [
        "Entra ID groups mapped to Dataverse teams and security roles",
        "Environment variables, DLP policies, solution pipelines, and managed solutions",
        "App visibility can also be role-mapped, mirroring the attached app-module pattern",
      ],
    },
  ];

  const designRules = [
    "Keep calculation logic server-side, not embedded in client-side forms.",
    "Treat extracts as a formal publication layer with readiness and run history.",
    "Use configuration tables for setup rather than workbook-like hidden tabs.",
    "Separate reference data updates from transactional planning activity.",
  ];

  return (
    <div className="mx-auto w-full max-w-7xl space-y-6">
      <div className="space-y-2 text-center">
        <h2 className="text-3xl font-bold text-slate-900">Target integration architecture</h2>
        <p className="mx-auto max-w-4xl text-sm text-slate-600 md:text-base">
          This architecture keeps the app simple for users while moving workbook calculations,
          approvals, and interface logic into explicit platform layers.
        </p>
      </div>

      <div className="space-y-3">
        {layers.map((layer, index) => (
          <div key={layer.title}>
            <Card className={`rounded-2xl border p-6 shadow-sm ${layer.tint}`}>
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div className="max-w-sm">
                  <div className="flex items-center gap-2">
                    <layer.icon className="h-5 w-5 text-slate-700" />
                    <h3 className="text-lg font-semibold text-slate-900">{layer.title}</h3>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-600">
                    Layer {index + 1} in the target-state stack.
                  </p>
                </div>

                <div className="grid flex-1 gap-3 md:grid-cols-3">
                  {layer.items.map((item) => (
                    <div key={item} className="rounded-2xl border border-white/70 bg-white/80 p-4">
                      <p className="text-sm leading-6 text-slate-700">{item}</p>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
            {index < layers.length - 1 && (
              <div className="flex justify-center py-2">
                <ArrowDown className="h-5 w-5 text-slate-300" />
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
          <div className="flex items-center gap-2">
            <Cloud className="h-5 w-5 text-sky-600" />
            <h3 className="text-lg font-semibold text-slate-900">Architecture rules</h3>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {designRules.map((rule) => (
              <div key={rule} className="rounded-2xl bg-slate-50 p-4">
                <p className="text-sm leading-6 text-slate-700">{rule}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900">Key technical decisions</h3>
          <div className="mt-4 flex flex-wrap gap-2">
            <Badge variant="outline">Dataverse-first</Badge>
            <Badge variant="outline">Approval-aware record states</Badge>
            <Badge variant="outline">Managed solution pipeline</Badge>
            <Badge variant="outline">Scoped access by org hierarchy</Badge>
            <Badge variant="outline">Export service for legacy parity</Badge>
          </div>
          <p className="mt-4 text-sm leading-6 text-slate-600">
            This is intentionally broader than a UI diagram. It gives delivery teams a shared view
            of where logic sits, how permissions are enforced, and how outputs leave the platform.
          </p>
        </Card>
      </div>
    </div>
  );
}
