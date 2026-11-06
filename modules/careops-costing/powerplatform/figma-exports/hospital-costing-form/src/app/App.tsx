import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Badge } from "./components/ui/badge";
import { WorkflowDiagram } from "./components/WorkflowDiagram";
import { CostingFormWireframe } from "./components/CostingFormWireframe";
import { BPMNDiagram } from "./components/BPMNDiagram";
import { DataModelDiagram } from "./components/DataModelDiagram";
import { DashboardView } from "./components/DashboardView";
import { ExcelMigrationMap } from "./components/ExcelMigrationMap";
import { IntegrationArchitecture } from "./components/IntegrationArchitecture";
import { SecurityPermissionsDiagram } from "./components/SecurityPermissionsDiagram";
import { DeliveryRoadmap } from "./components/DeliveryRoadmap";
import {
  FileText,
  GitFork,
  Network,
  Database,
  BarChart3,
  FileSpreadsheet,
  Share2,
  Lock,
  Rocket,
} from "lucide-react";

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8">
      <div className="mx-auto max-w-7xl space-y-8">
        <div className="space-y-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div className="space-y-2">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
                Power Platform design pack
              </p>
              <h1 className="text-3xl font-bold tracking-tight text-slate-900 md:text-4xl">
                NSW Health Budget Buildup Tool (BBT)
              </h1>
              <p className="max-w-4xl text-sm text-slate-600 md:text-base">
                Advanced diagrams translating the Excel-based NSW Health BBT into a governed
                Power Platform solution, preserving workbook logic, extract compatibility, and
                role-based approvals for M, S, and E users.
              </p>
            </div>

            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">Workbook-driven</Badge>
              <Badge variant="outline">Dataverse target state</Badge>
              <Badge variant="outline">BTS / FTE / ROS compatible</Badge>
              <Badge variant="outline">M / S / E approval model</Badge>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                Workbook anchors
              </p>
              <p className="mt-2 text-sm text-slate-700">
                SWInput, SWSetup, SWNotes, NSWHFormulas, Summ, SWBrief, BTSExtract, FTEExtract,
                and ROSExtract.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                Key target outputs
              </p>
              <p className="mt-2 text-sm text-slate-700">
                Cost elements 701–724 and 728, control lines 732 / 734 / 738 / 743, and FTE
                outputs including 820 Productive FTE.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                Helpful additions
              </p>
              <p className="mt-2 text-sm text-slate-700">
                Added dedicated security, delivery, and ALM views so the page is useful for
                build planning, permissions, testing, and cutover.
              </p>
            </div>
          </div>
        </div>

        <Tabs defaultValue="workflow" className="w-full">
          <div className="overflow-x-auto pb-2">
            <TabsList className="mb-4 min-w-max gap-1">
              <TabsTrigger value="workflow" className="flex-none gap-2 px-3">
                <GitFork className="h-4 w-4" />
                Workflow
              </TabsTrigger>
              <TabsTrigger value="bpmn" className="flex-none gap-2 px-3">
                <Network className="h-4 w-4" />
                Approval BPMN
              </TabsTrigger>
              <TabsTrigger value="wireframe" className="flex-none gap-2 px-3">
                <FileText className="h-4 w-4" />
                Form blueprint
              </TabsTrigger>
              <TabsTrigger value="datamodel" className="flex-none gap-2 px-3">
                <Database className="h-4 w-4" />
                Data model
              </TabsTrigger>
              <TabsTrigger value="dashboard" className="flex-none gap-2 px-3">
                <BarChart3 className="h-4 w-4" />
                Dashboard
              </TabsTrigger>
              <TabsTrigger value="migration" className="flex-none gap-2 px-3">
                <FileSpreadsheet className="h-4 w-4" />
                Workbook map
              </TabsTrigger>
              <TabsTrigger value="architecture" className="flex-none gap-2 px-3">
                <Share2 className="h-4 w-4" />
                Architecture
              </TabsTrigger>
              <TabsTrigger value="security" className="flex-none gap-2 px-3">
                <Lock className="h-4 w-4" />
                Security
              </TabsTrigger>
              <TabsTrigger value="delivery" className="flex-none gap-2 px-3">
                <Rocket className="h-4 w-4" />
                Delivery & ALM
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="workflow">
            <WorkflowDiagram />
          </TabsContent>

          <TabsContent value="bpmn">
            <BPMNDiagram />
          </TabsContent>

          <TabsContent value="wireframe">
            <CostingFormWireframe />
          </TabsContent>

          <TabsContent value="datamodel">
            <DataModelDiagram />
          </TabsContent>

          <TabsContent value="dashboard">
            <DashboardView />
          </TabsContent>

          <TabsContent value="migration">
            <ExcelMigrationMap />
          </TabsContent>

          <TabsContent value="architecture">
            <IntegrationArchitecture />
          </TabsContent>

          <TabsContent value="security">
            <SecurityPermissionsDiagram />
          </TabsContent>

          <TabsContent value="delivery">
            <DeliveryRoadmap />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
