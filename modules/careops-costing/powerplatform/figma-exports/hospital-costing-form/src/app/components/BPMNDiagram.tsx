import { Fragment } from "react";
import { ArrowRight, CheckCircle2, RotateCcw } from "lucide-react";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";

type LaneRow = {
  lane: string;
  tint: string;
  cells: Array<{ title: string; text: string; state?: string } | null>;
};

export function BPMNDiagram() {
  const columns = [
    "Draft and derive",
    "Validate and calculate",
    "DMS review",
    "Executive approval",
    "Publish and monitor",
  ];

  const lanes: LaneRow[] = [
    {
      lane: "Workforce admin (M)",
      tint: "bg-sky-50 border-sky-200",
      cells: [
        {
          title: "Create or amend record",
          text: "Select cost centre, position, award, roster, leave, and allowance inputs.",
          state: "Draft",
        },
        {
          title: "Fix exceptions",
          text: "Address validation warnings, missing reference data, or incompatible combinations.",
          state: "Rework",
        },
        {
          title: "Respond to return",
          text: "Review DMS comments and update the submission when it is returned.",
          state: "Returned",
        },
        {
          title: "Await outcome",
          text: "Record is locked for final decision apart from explicit rework actions.",
        },
        {
          title: "Use finalised budget",
          text: "Consume final numbers in local planning and next-cycle amendments.",
          state: "Finalised",
        },
      ],
    },
    {
      lane: "Power Platform system",
      tint: "bg-violet-50 border-violet-200",
      cells: [
        {
          title: "Derive organisational context",
          text: "Lookup division, entity, facility, and award-driven attributes from reference tables.",
        },
        {
          title: "Run business rules",
          text: "Calculate 701–724 / 728 costs, control lines, and FTE outputs; block invalid state transitions.",
        },
        {
          title: "Start approval workflow",
          text: "Send DMS task, capture comments, and lock editable fields appropriate to stage.",
        },
        {
          title: "Promote or reject",
          text: "On approval, escalate to executive. On rejection, route back with status and commentary.",
        },
        {
          title: "Generate outputs",
          text: "Refresh summary views and publish BTS / FTE / ROS outputs after final approval.",
        },
      ],
    },
    {
      lane: "DMS approver (S)",
      tint: "bg-amber-50 border-amber-200",
      cells: [
        null,
        null,
        {
          title: "Review and decide",
          text: "Check assumptions, staffing profile, and major deltas; approve or return for rework.",
          state: "DMS review",
        },
        null,
        null,
      ],
    },
    {
      lane: "Executive approver (E)",
      tint: "bg-emerald-50 border-emerald-200",
      cells: [
        null,
        null,
        null,
        {
          title: "Final approval or rejection",
          text: "Confirm budget position and sign off the record for publication and downstream consumption.",
          state: "Executive review",
        },
        null,
      ],
    },
    {
      lane: "Reporting and interfaces",
      tint: "bg-slate-50 border-slate-200",
      cells: [
        null,
        {
          title: "Preview outputs",
          text: "Show indicative summaries and exception counts before submission where allowed.",
        },
        null,
        null,
        {
          title: "Release governed views",
          text: "Expose dashboards, extracts, and reconciliation packs with status-aware visibility.",
          state: "Published",
        },
      ],
    },
  ];

  const states = [
    { label: "Draft", tone: "bg-slate-900 text-white" },
    { label: "Submitted", tone: "bg-sky-600 text-white" },
    { label: "DMS Approved", tone: "bg-amber-500 text-white" },
    { label: "Finalised", tone: "bg-emerald-600 text-white" },
    { label: "Returned / Rejected", tone: "bg-rose-100 text-rose-700" },
  ];

  return (
    <div className="mx-auto w-full max-w-7xl space-y-6">
      <div className="space-y-2 text-center">
        <h2 className="text-3xl font-bold text-slate-900">Approval BPMN / swimlane view</h2>
        <p className="mx-auto max-w-4xl text-sm text-slate-600 md:text-base">
          This swimlane view shows how M, S, and E roles interact with the system once the workbook
          logic is translated into staged Power Platform behaviour.
        </p>
      </div>

      <Card className="overflow-x-auto rounded-2xl border-slate-200 p-4 shadow-sm md:p-6">
        <div className="grid min-w-[1120px] grid-cols-[240px_repeat(5,minmax(170px,1fr))] gap-3">
          <div />
          {columns.map((column, index) => (
            <div key={column} className="rounded-2xl bg-slate-100 p-4 text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                Stage {index + 1}
              </p>
              <h3 className="mt-1 text-sm font-semibold text-slate-900">{column}</h3>
            </div>
          ))}

          {lanes.map((lane) => (
            <Fragment key={lane.lane}>
              <div className={`flex items-center rounded-2xl border p-4 ${lane.tint}`}>
                <p className="text-sm font-semibold text-slate-900">{lane.lane}</p>
              </div>

              {lane.cells.map((cell, index) => (
                <div key={`${lane.lane}-${index}`} className="relative">
                  {cell ? (
                    <div className={`h-full rounded-2xl border p-4 ${lane.tint}`}>
                      <div className="mb-2 flex flex-wrap gap-2">
                        {cell.state && <Badge variant="outline">{cell.state}</Badge>}
                      </div>
                      <h4 className="text-sm font-semibold text-slate-900">{cell.title}</h4>
                      <p className="mt-2 text-sm leading-6 text-slate-600">{cell.text}</p>
                    </div>
                  ) : (
                    <div className="h-full rounded-2xl border border-dashed border-slate-200 bg-white/70 p-4" />
                  )}

                  {index < lane.cells.length - 1 && (
                    <ArrowRight className="absolute -right-2 top-1/2 hidden h-4 w-4 -translate-y-1/2 text-slate-300 xl:block" />
                  )}
                </div>
              ))}
            </Fragment>
          ))}
        </div>
      </Card>

      <div className="grid gap-4 xl:grid-cols-[1.5fr_1fr]">
        <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900">Return and escalation rules</h3>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl bg-amber-50 p-4">
              <div className="flex items-start gap-2">
                <RotateCcw className="mt-0.5 h-4 w-4 text-amber-600" />
                <div>
                  <p className="font-medium text-slate-900">Return to M</p>
                  <p className="mt-1 text-sm leading-6 text-slate-600">
                    S and E can return a record for rework with mandatory commentary. Only the
                    editable sections reopen; finalised outputs stay protected.
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-2xl bg-emerald-50 p-4">
              <div className="flex items-start gap-2">
                <CheckCircle2 className="mt-0.5 h-4 w-4 text-emerald-600" />
                <div>
                  <p className="font-medium text-slate-900">Promote on approval</p>
                  <p className="mt-1 text-sm leading-6 text-slate-600">
                    Once S approves, the record transitions to executive review automatically,
                    preserving the audit trail and notification history.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </Card>

        <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900">Lifecycle states</h3>
          <div className="mt-4 flex flex-wrap gap-2">
            {states.map((state) => (
              <span
                key={state.label}
                className={`rounded-full px-3 py-1 text-xs font-semibold ${state.tone}`}
              >
                {state.label}
              </span>
            ))}
          </div>
          <p className="mt-4 text-sm leading-6 text-slate-600">
            The status model is more than workflow cosmetics: it controls editability, visibility,
            notifications, and whether summary/extract outputs are advisory or publishable.
          </p>
        </Card>
      </div>
    </div>
  );
}
