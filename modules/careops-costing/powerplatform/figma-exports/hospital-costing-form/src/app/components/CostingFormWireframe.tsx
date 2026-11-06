import { Card } from "./ui/card";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Separator } from "./ui/separator";
import { Badge } from "./ui/badge";
import { AlertCircle, Calculator, CheckCircle2, Save, Send } from "lucide-react";

export function CostingFormWireframe() {
  const outputs = [
    { code: "701", label: "Base salary / wages", value: "$162,840" },
    { code: "704", label: "Shift penalties", value: "$24,620" },
    { code: "716", label: "Total annual leave provision", value: "$18,460" },
    { code: "717", label: "Overtime", value: "$8,710" },
    { code: "724", label: "Superannuation", value: "$24,010" },
    { code: "820", label: "Productive FTE", value: "1.12" },
  ];

  const validations = [
    { ok: true, text: "Award / grade mapping resolved to a valid award code." },
    { ok: true, text: "Cost centre is active for the selected financial year." },
    { ok: false, text: "Rostered public holiday assumptions need confirmation." },
    { ok: false, text: "Leave relief profile is incomplete for temporary employment type." },
  ];

  const rosterRows = [
    { label: "Day", values: ["7.6", "7.6", "7.6", "7.6", "7.6", "0", "0"] },
    { label: "Afternoon", values: ["0", "0", "0", "0", "3.8", "7.6", "7.6"] },
    { label: "Night", values: ["0", "0", "0", "0", "0", "0", "0"] },
    { label: "OT hrs", values: ["0", "2", "0", "0", "0", "1.5", "0"] },
  ];

  return (
    <div className="mx-auto w-full max-w-7xl space-y-6">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h2 className="text-3xl font-bold text-slate-900">Power App form blueprint</h2>
          <p className="mt-1 max-w-4xl text-sm text-slate-600 md:text-base">
            The worksheet-style entry surface becomes a structured record with guided sections,
            scoped validation, and a live summary of key cost and FTE outputs.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge variant="outline">Status-aware fields</Badge>
          <Badge variant="outline">Server-side calculations</Badge>
          <Badge variant="outline">Extract-ready summary</Badge>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.55fr_0.85fr]">
        <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">Record</p>
              <h3 className="text-2xl font-semibold text-slate-900">
                FY26 Budget Buildup – Position 4008123
              </h3>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">Draft</Badge>
              <Badge variant="outline">Scope: Site / Directorate / Cost Centre</Badge>
            </div>
          </div>

          <Separator className="my-6" />

          <div className="space-y-8">
            <section className="space-y-4">
              <div>
                <h4 className="text-lg font-semibold text-slate-900">Organisation and position</h4>
                <p className="text-sm text-slate-600">
                  Primary replacement for the workbook’s position profile section.
                </p>
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <Label htmlFor="financialYear">Financial year</Label>
                  <Input id="financialYear" defaultValue="FY26" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="site">Site</Label>
                  <Input id="site" defaultValue="Any site (scoped by role)" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="directorate">Directorate</Label>
                  <Input id="directorate" placeholder="Clinical Operations" />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="costCentre">Cost centre</Label>
                  <Input id="costCentre" placeholder="Select active cost centre" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="project">Project</Label>
                  <Input id="project" placeholder="Optional project code" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="linkProject">Link project</Label>
                  <Input id="linkProject" placeholder="Optional linked project" />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="positionNumber">Position number</Label>
                  <Input id="positionNumber" defaultValue="4008123" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="reportingPosition">Reporting position</Label>
                  <Input id="reportingPosition" placeholder="Manager position number" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="positionTitle">Position title</Label>
                  <Input id="positionTitle" defaultValue="Registered Nurse" />
                </div>
              </div>
            </section>

            <section className="space-y-4">
              <div>
                <h4 className="text-lg font-semibold text-slate-900">Employment and award</h4>
                <p className="text-sm text-slate-600">
                  Structured lookups replace hidden workbook dependencies on awards, grade steps,
                  and employment flags.
                </p>
              </div>

              <div className="grid gap-4 md:grid-cols-4">
                <div className="space-y-2">
                  <Label>Employee type</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="FTP / PTP / FTT / CS / CON / AD / AN" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="ftp">FTP</SelectItem>
                      <SelectItem value="ptp">PTP</SelectItem>
                      <SelectItem value="ftt">FTT</SelectItem>
                      <SelectItem value="cs">CS</SelectItem>
                      <SelectItem value="con">CON</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Position grade</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select grade" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="rn-1">RN Grade 1</SelectItem>
                      <SelectItem value="rn-2">RN Grade 2</SelectItem>
                      <SelectItem value="clerical">Clerical Grade 5</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Grade year / step</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select step" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="y1">Year 1</SelectItem>
                      <SelectItem value="y2">Year 2</SelectItem>
                      <SelectItem value="y3">Year 3</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="awardCode">Award code</Label>
                  <Input id="awardCode" defaultValue="Derived from grade + step" />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="startDate">Start date</Label>
                  <Input id="startDate" type="date" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="weeks">Number of weeks</Label>
                  <Input id="weeks" defaultValue="52.18" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="fte">Position FTE</Label>
                  <Input id="fte" defaultValue="1.00" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="hours">Contracted hours</Label>
                  <Input id="hours" defaultValue="38" />
                </div>
              </div>
            </section>

            <section className="space-y-4">
              <div>
                <h4 className="text-lg font-semibold text-slate-900">Weekly roster and overtime</h4>
                <p className="text-sm text-slate-600">
                  Child tables replace wide worksheet grids while still retaining the same
                  business meaning.
                </p>
              </div>

              <div className="overflow-x-auto rounded-2xl border border-slate-200">
                <table className="min-w-full text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold text-slate-700">Pattern</th>
                      {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day) => (
                        <th key={day} className="px-3 py-3 text-center font-semibold text-slate-700">
                          {day}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {rosterRows.map((row) => (
                      <tr key={row.label} className="border-t border-slate-200">
                        <td className="px-4 py-3 font-medium text-slate-900">{row.label}</td>
                        {row.values.map((value, index) => (
                          <td key={`${row.label}-${index}`} className="px-3 py-3 text-center text-slate-600">
                            {value}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="space-y-4">
              <div>
                <h4 className="text-lg font-semibold text-slate-900">Leave and allowance assumptions</h4>
                <p className="text-sm text-slate-600">
                  Dedicated sections stop assumptions from being hidden inside hard-to-audit workbook cells.
                </p>
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <div className="rounded-2xl bg-slate-50 p-4">
                  <h5 className="font-medium text-slate-900">Leave</h5>
                  <div className="mt-3 space-y-3">
                    <Input defaultValue="Annual leave relief – 4.0 weeks" />
                    <Input defaultValue="Sick leave utilisation – 1.3 weeks" />
                    <Input defaultValue="LSL flag – >10" />
                  </div>
                </div>

                <div className="rounded-2xl bg-slate-50 p-4">
                  <h5 className="font-medium text-slate-900">Allowances</h5>
                  <div className="mt-3 space-y-3">
                    <Input defaultValue="Uniform / Laundry – $520" />
                    <Input defaultValue="On-call nurse occurrences – 26" />
                    <Input defaultValue="Manual allowance inc super – $0" />
                  </div>
                </div>

                <div className="rounded-2xl bg-slate-50 p-4">
                  <h5 className="font-medium text-slate-900">Planner notes</h5>
                  <Textarea
                    className="mt-3 min-h-[118px]"
                    defaultValue="Explain unusual roster, temporary relief assumptions, or local offsets here."
                  />
                </div>
              </div>
            </section>
          </div>

          <div className="mt-8 flex flex-wrap gap-3">
            <Button className="gap-2">
              <Save className="h-4 w-4" />
              Save draft
            </Button>
            <Button variant="outline" className="gap-2">
              <Calculator className="h-4 w-4" />
              Recalculate
            </Button>
            <Button variant="outline" className="gap-2">
              <Send className="h-4 w-4" />
              Submit to DMS
            </Button>
          </div>
        </Card>

        <div className="space-y-6">
          <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
            <div className="flex items-center gap-2">
              <Calculator className="h-5 w-5 text-violet-600" />
              <h3 className="text-lg font-semibold text-slate-900">Live output summary</h3>
            </div>
            <div className="mt-4 space-y-3">
              {outputs.map((output) => (
                <div
                  key={output.code}
                  className="flex items-center justify-between rounded-2xl border border-slate-200 p-3"
                >
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                      {output.code}
                    </p>
                    <p className="text-sm text-slate-700">{output.label}</p>
                  </div>
                  <p className="font-semibold text-slate-900">{output.value}</p>
                </div>
              ))}
            </div>
          </Card>

          <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-amber-500" />
              <h3 className="text-lg font-semibold text-slate-900">Validation summary</h3>
            </div>
            <div className="mt-4 space-y-3">
              {validations.map((validation) => (
                <div key={validation.text} className="flex items-start gap-3 rounded-2xl bg-slate-50 p-3">
                  {validation.ok ? (
                    <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0 text-emerald-500" />
                  ) : (
                    <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-amber-500" />
                  )}
                  <p className="text-sm leading-6 text-slate-600">{validation.text}</p>
                </div>
              ))}
            </div>
          </Card>

          <Card className="rounded-2xl border-slate-200 p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900">Extract readiness</h3>
            <div className="mt-4 grid gap-3">
              {[
                "BTS extract structure preserved",
                "FTE output grain aligned to productive / leave components",
                "ROS output available when roster data passes validation",
              ].map((item) => (
                <div key={item} className="flex items-start gap-2 rounded-2xl bg-emerald-50 p-3">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0 text-emerald-600" />
                  <p className="text-sm leading-6 text-slate-700">{item}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
