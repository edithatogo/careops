import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { Database, Key, Link } from "lucide-react";

type Entity = {
  name: string;
  purpose: string;
  fields: string[];
};

export function DataModelDiagram() {
  const groups: Array<{
    title: string;
    caption: string;
    headerClass: string;
    entities: Entity[];
  }> = [
    {
      title: "Reference and configuration",
      caption: "Reusable master data and constants that replace hidden workbook lookups.",
      headerClass: "bg-sky-600",
      entities: [
        {
          name: "OrganisationUnit",
          purpose: "Site, directorate, cost centre, entity, sector, facility hierarchy.",
          fields: ["OrgUnitId (PK)", "Site", "Directorate", "CostCentre", "Project", "ActiveFrom / To"],
        },
        {
          name: "AwardRate",
          purpose: "Award code, grade step, hourly rates, leave accruals, and loading settings.",
          fields: ["AwardRateId (PK)", "AwardCode", "GradeStep", "BaseRate", "RatedRate", "AccrualProfile"],
        },
        {
          name: "PhaseCodeCalendar",
          purpose: "Financial periods, public holidays, month phasing, and extract code patterns.",
          fields: ["CalendarId (PK)", "FinancialYear", "Month", "PublicHolidayFlag", "PhaseCode", "Sequence"],
        },
        {
          name: "CostElementDefinition",
          purpose: "Definition of 701–724, 728, control lines, and FTE output categories.",
          fields: ["ElementId (PK)", "ElementCode", "OutputFamily", "MeasureType", "ExportRule"],
        },
      ],
    },
    {
      title: "Operational budgeting records",
      caption: "The central transactional model that replaces spreadsheet entry and intermediate logic.",
      headerClass: "bg-violet-600",
      entities: [
        {
          name: "BudgetBuildCycle",
          purpose: "Controls the active financial year, status windows, and reconciliation parameters.",
          fields: ["CycleId (PK)", "FinancialYear", "Status", "ParallelRunFlag", "ApprovedAt"],
        },
        {
          name: "PositionBudgetRecord",
          purpose: "Main record for organisation, position, employment, and status.",
          fields: ["RecordId (PK)", "CycleId (FK)", "OrgUnitId (FK)", "PositionNumber", "AwardRateId (FK)", "WorkflowStatus"],
        },
        {
          name: "RosterPattern",
          purpose: "Child rows for day/shift headcount, worked hours, and overtime inputs.",
          fields: ["RosterRowId (PK)", "RecordId (FK)", "PatternType", "DayOfWeek", "Hours", "Headcount"],
        },
        {
          name: "LeaveAllowanceProfile",
          purpose: "Leave relief, public holiday, LSL, on-call, manual allowance, and specialist flags.",
          fields: ["ProfileId (PK)", "RecordId (FK)", "LeaveType", "WeeksOrDays", "Value", "AppliesToRelief"],
        },
      ],
    },
    {
      title: "Governance, approval, and outputs",
      caption: "Lifecycle, audit, and published results for reports and extracts.",
      headerClass: "bg-emerald-600",
      entities: [
        {
          name: "CostElementOutput",
          purpose: "Calculated money outputs per record / element / period.",
          fields: ["OutputId (PK)", "RecordId (FK)", "ElementId (FK)", "Amount", "PhaseCode", "PublishStatus"],
        },
        {
          name: "FTEOutput",
          purpose: "Derived productive, leave, relief, and overtime FTE rows.",
          fields: ["FteOutputId (PK)", "RecordId (FK)", "OutputCode", "FteValue", "MeasureBasis", "PublishStatus"],
        },
        {
          name: "ApprovalDecision",
          purpose: "DMS and executive approvals, comments, return reasons, and timestamps.",
          fields: ["DecisionId (PK)", "RecordId (FK)", "DecisionStage", "Decision", "Comment", "Actor"],
        },
        {
          name: "RoleAssignment / ExtractBatch",
          purpose: "Scoped permissions plus final batch publication metadata for BTS / FTE / ROS outputs.",
          fields: ["AssignmentId / BatchId", "RoleToken", "ScopeFields", "BatchType", "RunAt", "RunStatus"],
        },
      ],
    },
  ];

  const relationships = [
    "BudgetBuildCycle 1 → many PositionBudgetRecord",
    "OrganisationUnit 1 → many PositionBudgetRecord",
    "AwardRate 1 → many PositionBudgetRecord",
    "PositionBudgetRecord 1 → many RosterPattern",
    "PositionBudgetRecord 1 → many LeaveAllowanceProfile",
    "PositionBudgetRecord 1 → many CostElementOutput",
    "PositionBudgetRecord 1 → many FTEOutput",
    "PositionBudgetRecord 1 → many ApprovalDecision",
  ];

  const grainNotes = [
    "CostElementOutput should publish at record + element + phase code grain to support BTSExtract parity.",
    "FTEOutput should publish productive and non-productive components separately so 820 Productive FTE remains explainable.",
    "ApprovalDecision and audit metadata should be stored outside the main record body to preserve history cleanly.",
  ];

  return (
    <div className="mx-auto w-full max-w-7xl space-y-6">
      <div className="space-y-2 text-center">
        <h2 className="text-3xl font-bold text-slate-900">Dataverse data model</h2>
        <p className="mx-auto max-w-4xl text-sm text-slate-600 md:text-base">
          The target data model separates reference data, transactional budgeting inputs, and
          published outputs so calculations are explainable and approvals can be audited cleanly.
        </p>
      </div>

      <div className="grid gap-5 xl:grid-cols-3">
        {groups.map((group) => (
          <Card key={group.title} className="overflow-hidden rounded-2xl border-slate-200 shadow-sm">
            <div className={`${group.headerClass} px-6 py-5 text-white`}>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] opacity-80">
                {group.title}
              </p>
              <p className="mt-2 text-sm leading-6 text-white/90">{group.caption}</p>
            </div>

            <div className="space-y-4 p-5">
              {group.entities.map((entity) => (
                <div key={entity.name} className="rounded-2xl border border-slate-200 bg-white p-4">
                  <div className="mb-3 flex items-center gap-2">
                    <Database className="h-4 w-4 text-slate-500" />
                    <h3 className="font-semibold text-slate-900">{entity.name}</h3>
                  </div>

                  <p className="text-sm leading-6 text-slate-600">{entity.purpose}</p>

                  <div className="mt-3 flex flex-wrap gap-2">
                    {entity.fields.map((field) => (
                      <Badge key={field} variant="outline">
                        {field}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
          <div className="flex items-center gap-2">
            <Link className="h-5 w-5 text-violet-600" />
            <h3 className="text-lg font-semibold text-slate-900">Core relationships</h3>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {relationships.map((relationship) => (
              <div key={relationship} className="rounded-2xl bg-slate-50 p-4">
                <p className="text-sm leading-6 text-slate-700">{relationship}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
          <div className="flex items-center gap-2">
            <Key className="h-5 w-5 text-sky-600" />
            <h3 className="text-lg font-semibold text-slate-900">Important grain rules</h3>
          </div>
          <div className="mt-4 space-y-3">
            {grainNotes.map((note) => (
              <div key={note} className="rounded-2xl bg-slate-50 p-4">
                <p className="text-sm leading-6 text-slate-700">{note}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
