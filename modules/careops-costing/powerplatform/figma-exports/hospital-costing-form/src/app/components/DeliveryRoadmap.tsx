import { ArrowRight, CheckCircle2, Lock, Package, Rocket } from "lucide-react";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";

export function DeliveryRoadmap() {
  const environments = [
    {
      name: "Dev",
      summary: "Rapid build, schema evolution, and seeded reference data.",
      notes: ["Unmanaged solutions", "Developer access", "Experimental config"],
    },
    {
      name: "Test",
      summary: "Automated regression, unit / integration testing, and role checks.",
      notes: ["Managed solution import", "Synthetic or masked data", "Pipeline validation"],
    },
    {
      name: "UAT",
      summary: "Parallel-run comparison against the workbook and business sign-off.",
      notes: ["Business approver access", "Reconciliation packs", "Export validation"],
    },
    {
      name: "Prod",
      summary: "Locked release path, governed configuration, and operational support.",
      notes: ["Managed-only deployment", "Service accounts", "Audit retention"],
    },
  ];

  const phases = [
    {
      title: "1. Discover and decompose",
      items: [
        "Catalogue workbook inputs, outputs, setup constants, and extract dependencies.",
        "Prioritise rules that drive 701–724 / 728 and 820 / 822 behaviours.",
      ],
    },
    {
      title: "2. Build the reference and data model",
      items: [
        "Create Dataverse tables for org hierarchy, awards, rates, cycles, records, and outputs.",
        "Seed development permissions for M, S, and E role tokens.",
      ],
    },
    {
      title: "3. Implement calculations and approvals",
      items: [
        "Translate workbook logic into plug-ins / flows with explicit rule ownership.",
        "Implement Draft → DMS Review → Executive Approval lifecycle with field locking.",
      ],
    },
    {
      title: "4. Run parallel validation",
      items: [
        "Compare platform outputs against workbook results by cost element, FTE, and extract.",
        "Resolve variances before go-live sign-off.",
      ],
    },
    {
      title: "5. Cut over and stabilise",
      items: [
        "Promote managed solution to production with support playbook and monitoring.",
        "Retain workbook as comparison artefact until confidence threshold is met.",
      ],
    },
  ];

  const readiness = [
    "Security testing proves correct scope enforcement for M, S, and E users.",
    "Reference data update process is owned and documented.",
    "BTS / FTE / ROS outputs reconcile to workbook-era expectations.",
    "Support model exists for rule changes, rates, and annual cycle rollover.",
  ];

  return (
    <div className="mx-auto w-full max-w-7xl space-y-6">
      <div className="space-y-2 text-center">
        <h2 className="text-3xl font-bold text-slate-900">Delivery roadmap and ALM</h2>
        <p className="mx-auto max-w-4xl text-sm text-slate-600 md:text-base">
          Added to make the page more delivery-ready: this shows how the solution should move
          through environments and what must be true before the workbook can be retired.
        </p>
      </div>

      <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
        <div className="flex items-center gap-2">
          <Package className="h-5 w-5 text-violet-600" />
          <h3 className="text-lg font-semibold text-slate-900">Environment path</h3>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-[repeat(4,minmax(0,1fr))]">
          {environments.map((env, index) => (
            <div key={env.name} className="relative">
              <Card className="h-full rounded-2xl border-slate-200 p-5 shadow-sm">
                <div className="flex items-center justify-between gap-2">
                  <h4 className="text-lg font-semibold text-slate-900">{env.name}</h4>
                  <Badge variant="outline">{index === environments.length - 1 ? "Live" : "Stage"}</Badge>
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-600">{env.summary}</p>
                <div className="mt-4 space-y-2">
                  {env.notes.map((note) => (
                    <div key={note} className="rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-700">
                      {note}
                    </div>
                  ))}
                </div>
              </Card>
              {index < environments.length - 1 && (
                <div className="pointer-events-none absolute -right-3 top-1/2 hidden -translate-y-1/2 lg:block">
                  <ArrowRight className="h-5 w-5 text-slate-300" />
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>

      <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
        <div className="flex items-center gap-2">
          <Rocket className="h-5 w-5 text-sky-600" />
          <h3 className="text-lg font-semibold text-slate-900">Delivery phases</h3>
        </div>

        <div className="mt-6 grid gap-4 xl:grid-cols-5">
          {phases.map((phase) => (
            <div key={phase.title} className="rounded-2xl border border-slate-200 p-4">
              <h4 className="font-semibold text-slate-900">{phase.title}</h4>
              <div className="mt-3 space-y-2">
                {phase.items.map((item) => (
                  <div key={item} className="rounded-xl bg-slate-50 p-3">
                    <p className="text-sm leading-6 text-slate-700">{item}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </Card>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
          <div className="flex items-center gap-2">
            <Lock className="h-5 w-5 text-amber-600" />
            <h3 className="text-lg font-semibold text-slate-900">Release guardrails</h3>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {[
              "Use managed solutions from Test upward.",
              "Freeze structural changes during UAT / parallel run windows.",
              "Separate reference-data admin from general planner permissions.",
              "Retain rollback plan and workbook comparison artefacts for cutover.",
            ].map((rule) => (
              <div key={rule} className="rounded-2xl bg-slate-50 p-4">
                <p className="text-sm leading-6 text-slate-700">{rule}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900">Go-live readiness</h3>
          <div className="mt-4 space-y-3">
            {readiness.map((item) => (
              <div key={item} className="flex items-start gap-2 rounded-2xl bg-emerald-50 p-4">
                <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0 text-emerald-600" />
                <p className="text-sm leading-6 text-slate-700">{item}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
