import { AlertCircle, ArrowRight, CheckCircle2, Key, Lock, Users } from "lucide-react";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";

export function SecurityPermissionsDiagram() {
  const roleCards = [
    {
      role: "M",
      title: "Workforce admin",
      scope: "Create, edit, calculate, and submit records within assigned scope.",
      tint: "bg-sky-50 border-sky-200",
    },
    {
      role: "S",
      title: "DMS approver",
      scope: "Review, comment, return, and approve at DMS stage.",
      tint: "bg-amber-50 border-amber-200",
    },
    {
      role: "E",
      title: "Executive approver",
      scope: "Provide final approval, rejection, and publication sign-off.",
      tint: "bg-emerald-50 border-emerald-200",
    },
  ];

  const assignments = [
    {
      assignmentId: "A001",
      roleToken: "M",
      scope: "Site: Any / Directorate: Any / Cost Centre: blank",
      note: "Development seed permission for workforce admins",
    },
    {
      assignmentId: "A002",
      roleToken: "S",
      scope: "Site: Any / Directorate: Any / Cost Centre: blank",
      note: "Development seed permission for DMS approvers",
    },
    {
      assignmentId: "A003",
      roleToken: "E",
      scope: "Site: Any / Directorate: Any / Cost Centre: blank",
      note: "Development seed permission for executive approvers",
    },
  ];

  const permissions = [
    {
      action: "Create and edit draft records",
      M: true,
      S: false,
      E: false,
      Admin: true,
    },
    {
      action: "Run calculations and validations",
      M: true,
      S: true,
      E: true,
      Admin: true,
    },
    {
      action: "Submit to DMS review",
      M: true,
      S: false,
      E: false,
      Admin: true,
    },
    {
      action: "Return for rework at DMS stage",
      M: false,
      S: true,
      E: false,
      Admin: true,
    },
    {
      action: "Approve at DMS stage",
      M: false,
      S: true,
      E: false,
      Admin: true,
    },
    {
      action: "Final approve or reject",
      M: false,
      S: false,
      E: true,
      Admin: true,
    },
    {
      action: "Maintain reference data / role assignments",
      M: false,
      S: false,
      E: false,
      Admin: true,
    },
  ];

  const implementationNotes = [
    "Entra ID group membership should map users into Dataverse owner/access teams.",
    "RoleAssignment rows hold scope fields such as site, directorate, and cost centre.",
    "Business process stage plus workflow status should lock or unlock fields appropriately.",
    "App-module visibility can also be role-mapped, following the attached module pattern.",
  ];

  return (
    <div className="mx-auto w-full max-w-7xl space-y-6">
      <div className="space-y-2 text-center">
        <h2 className="text-3xl font-bold text-slate-900">Security and permissions model</h2>
        <p className="mx-auto max-w-4xl text-sm text-slate-600 md:text-base">
          The workbook had informal control boundaries. The platform design turns those into explicit
          app visibility, team membership, scoped data access, and stage-based permissions.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-[1fr_auto_1fr_auto_1fr_auto_1fr]">
        <Card className="rounded-2xl border-slate-200 p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-sky-600" />
            <h3 className="font-semibold text-slate-900">Entra groups</h3>
          </div>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            Source of truth for workforce admin, DMS approver, and executive approver memberships.
          </p>
        </Card>

        <div className="hidden items-center justify-center md:flex">
          <ArrowRight className="h-5 w-5 text-slate-300" />
        </div>

        <Card className="rounded-2xl border-slate-200 p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <Key className="h-5 w-5 text-violet-600" />
            <h3 className="font-semibold text-slate-900">RoleAssignment rows</h3>
          </div>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            Store role token plus scope fields like site, directorate, and cost centre.
          </p>
        </Card>

        <div className="hidden items-center justify-center md:flex">
          <ArrowRight className="h-5 w-5 text-slate-300" />
        </div>

        <Card className="rounded-2xl border-slate-200 p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <Lock className="h-5 w-5 text-amber-600" />
            <h3 className="font-semibold text-slate-900">Dataverse roles / teams</h3>
          </div>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            Control record creation, read scope, update rights, and approval privileges.
          </p>
        </Card>

        <div className="hidden items-center justify-center md:flex">
          <ArrowRight className="h-5 w-5 text-slate-300" />
        </div>

        <Card className="rounded-2xl border-slate-200 p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-emerald-600" />
            <h3 className="font-semibold text-slate-900">Workflow enforcement</h3>
          </div>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            Stage transitions, field locks, notifications, and audit trail are applied automatically.
          </p>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {roleCards.map((card) => (
          <Card key={card.role} className={`rounded-2xl border p-5 shadow-sm ${card.tint}`}>
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-xl font-bold text-slate-900">
                {card.role}
              </div>
              <div>
                <p className="text-lg font-semibold text-slate-900">{card.title}</p>
                <p className="text-sm text-slate-600">{card.scope}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">Seed role assignments from attachment</h3>
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left">
                <th className="px-3 py-3 font-semibold text-slate-700">Assignment</th>
                <th className="px-3 py-3 font-semibold text-slate-700">Role token</th>
                <th className="px-3 py-3 font-semibold text-slate-700">Scope</th>
                <th className="px-3 py-3 font-semibold text-slate-700">Note</th>
              </tr>
            </thead>
            <tbody>
              {assignments.map((assignment) => (
                <tr key={assignment.assignmentId} className="border-b border-slate-100">
                  <td className="px-3 py-4 text-slate-800">{assignment.assignmentId}</td>
                  <td className="px-3 py-4">
                    <Badge variant="outline">{assignment.roleToken}</Badge>
                  </td>
                  <td className="px-3 py-4 text-slate-600">{assignment.scope}</td>
                  <td className="px-3 py-4 text-slate-600">{assignment.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900">Permission matrix</h3>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-left">
                  <th className="px-3 py-3 font-semibold text-slate-700">Action</th>
                  {["M", "S", "E", "Platform admin"].map((col) => (
                    <th key={col} className="px-3 py-3 text-center font-semibold text-slate-700">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {permissions.map((permission) => (
                  <tr key={permission.action} className="border-b border-slate-100">
                    <td className="px-3 py-4 text-slate-700">{permission.action}</td>
                    {[permission.M, permission.S, permission.E, permission.Admin].map((allowed, index) => (
                      <td key={`${permission.action}-${index}`} className="px-3 py-4 text-center">
                        {allowed ? (
                          <CheckCircle2 className="mx-auto h-4 w-4 text-emerald-600" />
                        ) : (
                          <AlertCircle className="mx-auto h-4 w-4 text-slate-300" />
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900">Implementation notes</h3>
          <div className="mt-4 space-y-3">
            {implementationNotes.map((note) => (
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
