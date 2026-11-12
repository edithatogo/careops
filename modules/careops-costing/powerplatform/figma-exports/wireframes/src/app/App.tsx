import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { WorkflowDiagram } from "./components/WorkflowDiagram";
import { CostingFormWireframe } from "./components/CostingFormWireframe";
import { BPMNDiagram } from "./components/BPMNDiagram";
import { DataModelDiagram } from "./components/DataModelDiagram";
import { DashboardView } from "./components/DashboardView";
import { ExcelMigrationMap } from "./components/ExcelMigrationMap";
import { IntegrationArchitecture } from "./components/IntegrationArchitecture";
import { FileText, GitFork, Network, Database, BarChart3, FileSpreadsheet, Share2 } from "lucide-react";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <Tabs defaultValue="workflow" className="w-full">
          <div className="overflow-x-auto pb-4">
            <TabsList className="inline-flex min-w-full md:grid md:grid-cols-7 mb-8">
              <TabsTrigger value="workflow" className="flex items-center gap-2 whitespace-nowrap">
                <GitFork className="w-4 h-4" />
                <span className="hidden sm:inline">Workflow</span>
              </TabsTrigger>
              <TabsTrigger value="bpmn" className="flex items-center gap-2 whitespace-nowrap">
                <Network className="w-4 h-4" />
                <span className="hidden sm:inline">BPMN 2.0</span>
              </TabsTrigger>
              <TabsTrigger value="wireframe" className="flex items-center gap-2 whitespace-nowrap">
                <FileText className="w-4 h-4" />
                <span className="hidden sm:inline">Form</span>
              </TabsTrigger>
              <TabsTrigger value="datamodel" className="flex items-center gap-2 whitespace-nowrap">
                <Database className="w-4 h-4" />
                <span className="hidden sm:inline">Data Model</span>
              </TabsTrigger>
              <TabsTrigger value="dashboard" className="flex items-center gap-2 whitespace-nowrap">
                <BarChart3 className="w-4 h-4" />
                <span className="hidden sm:inline">Dashboard</span>
              </TabsTrigger>
              <TabsTrigger value="migration" className="flex items-center gap-2 whitespace-nowrap">
                <FileSpreadsheet className="w-4 h-4" />
                <span className="hidden sm:inline">Migration</span>
              </TabsTrigger>
              <TabsTrigger value="architecture" className="flex items-center gap-2 whitespace-nowrap">
                <Share2 className="w-4 h-4" />
                <span className="hidden sm:inline">Architecture</span>
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
        </Tabs>
      </div>
    </div>
  );
}
