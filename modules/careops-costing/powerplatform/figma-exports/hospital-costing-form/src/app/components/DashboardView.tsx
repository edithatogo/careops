import { AlertCircle, BarChart3, CheckCircle2, DollarSign, Users } from "lucide-react";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";

function HorizontalBars({
  items,
  suffix = "",
}: {
  items: Array<{ label: string; value: number; note?: string }>;
  suffix?: string;
}) {
  const max = Math.max(...items.map((item) => item.value));

  return (
    <div className="space-y-4">
      {items.map((item) => (
        <div key={item.label} className="space-y-1">
          <div className="flex items-center justify-between gap-4 text-sm">
            <div>
              <p className="font-medium text-slate-900">{item.label}</p>
              {item.note && <p className="text-xs text-slate-500">{item.note}</p>}
            </div>
            <p className="font-semibold text-slate-700">
              {item.value}
              {suffix}
            </p>
          </div>
          <div className="h-2 rounded-full bg-slate-100">
            <div
              className="h-2 rounded-full bg-violet-500"
              style={{ width: `${(item.value / max) * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

export function DashboardView() {
  const kpis = [
    {
      title: "Annual salary & wages",
      value: "$54.8m",
      note: "Illustrative sample metric for design purposes",
      icon: DollarSign,
      tint: "bg-sky-50 text-sky-700",
    },
    {
      title: "Productive FTE",
      value: "612.4",
      note: "Target 820-derived workforce view",
      icon: Users,
      tint: "bg-violet-50 text-violet-700",
    },
    {
      title: "Finalised submissions",
      value: "37",
      note: "Approved by DMS and executive",
      icon: CheckCircle2,
      tint: "bg-emerald-50 text-emerald-700",
    },
    {
      title: "Exceptions to review",
      value: "6",
      note: "Validation or reconciliation issues",
      icon: AlertCircle,
      tint: "bg-amber-50 text-amber-700",
    },
  ];

  const costElements = [
    { label: "701 Base", value: 34.2, note: "$m" },
    { label: "704 Shift penalties", value: 6.8, note: "$m" },
    { label: "716 Leave provision", value: 4.6, note: "$m" },
    { label: "717 Overtime", value: 2.7, note: "$m" },
    { label: "724 Superannuation", value: 4.8, note: "$m" },
    { label: "728 Special allowances", value: 1.1, note: "$m" },
  ];

  const directorates = [
    { label: "Nursing", value: 48, note: "largest annual budget" },
    { label: "Emergency", value: 22, note: "shift-intensive" },
    { label: "Medical", value: 19, note: "mixed award profile" },
    { label: "Corporate", value: 10, note: "predominantly day worker" },
  ];

  const statuses = [
    { label: "Draft", value: 28 },
    { label: "DMS Review", value: 11 },
    { label: "Exec Review", value: 4 },
    { label: "Finalised", value: 37 },
    { label: "Returned", value: 6 },
  ];

  const extractChecks = [
    { name: "BTSExtract", status: "Ready", note: "All finalised records published" },
    { name: "FTEExtract", status: "Ready", note: "820 / 822 controls balanced" },
    { name: "ROSExtract", status: "Warning", note: "2 records missing roster split" },
  ];

  return (
    <div className="mx-auto w-full max-w-7xl space-y-6">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h2 className="text-3xl font-bold text-slate-900">Operations and finance dashboard</h2>
          <p className="mt-1 max-w-4xl text-sm text-slate-600 md:text-base">
            A Power BI-style view that turns the workbook summaries into role-aware operational,
            finance, and reconciliation reporting.
          </p>
        </div>
        <Badge variant="outline">Illustrative design metrics</Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {kpis.map((kpi) => (
          <Card key={kpi.title} className="rounded-2xl border-slate-200 p-5 shadow-sm">
            <div className={`flex h-12 w-12 items-center justify-center rounded-2xl ${kpi.tint}`}>
              <kpi.icon className="h-6 w-6" />
            </div>
            <p className="mt-4 text-sm font-medium text-slate-500">{kpi.title}</p>
            <h3 className="mt-1 text-2xl font-semibold text-slate-900">{kpi.value}</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600">{kpi.note}</p>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-violet-600" />
            <h3 className="text-lg font-semibold text-slate-900">Cost element mix</h3>
          </div>
          <p className="mt-2 text-sm text-slate-600">
            Helpful for validating whether server-side calculations align to expected output patterns.
          </p>
          <div className="mt-6">
            <HorizontalBars items={costElements} suffix="m" />
          </div>
        </Card>

        <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900">Submission status by count</h3>
          <p className="mt-2 text-sm text-slate-600">
            Gives DMS and executive approvers immediate visibility into bottlenecks.
          </p>
          <div className="mt-6">
            <HorizontalBars items={statuses} />
          </div>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900">Directorate budget view</h3>
          <p className="mt-2 text-sm text-slate-600">
            A common replacement for workbook roll-ups that are difficult to interrogate.
          </p>
          <div className="mt-6">
            <HorizontalBars items={directorates} suffix="m" />
          </div>
        </Card>

        <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900">Extract health and reconciliation</h3>
          <div className="mt-4 space-y-3">
            {extractChecks.map((check) => (
              <div
                key={check.name}
                className="flex items-start justify-between gap-4 rounded-2xl border border-slate-200 p-4"
              >
                <div>
                  <p className="font-semibold text-slate-900">{check.name}</p>
                  <p className="mt-1 text-sm leading-6 text-slate-600">{check.note}</p>
                </div>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold ${
                    check.status === "Ready"
                      ? "bg-emerald-100 text-emerald-700"
                      : "bg-amber-100 text-amber-700"
                  }`}
                >
                  {check.status}
                </span>
              </div>
            ))}
          </div>

          <div className="mt-6 rounded-2xl bg-slate-50 p-4">
            <p className="text-sm leading-6 text-slate-700">
              This dashboard tab is intentionally not “just BI”. It closes the loop between
              workflow status, control totals, extract readiness, and the coded outputs that the
              old workbook already produced.
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}
