import { Card } from './ui/card';
import { Cloud, Server, Monitor, Database, ArrowRightLeft, Lock } from 'lucide-react';

export function IntegrationArchitecture() {
  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold">Integration Architecture</h2>
        <p className="text-gray-600">System components and data flow</p>
      </div>

      <Card className="p-8 overflow-x-auto">
        <svg
          viewBox="0 0 1400 900"
          className="w-full h-auto"
          style={{ minWidth: '1000px' }}
        >
          <defs>
            {/* Arrow marker */}
            <marker
              id="integrationArrow"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="#3b82f6" />
            </marker>

            {/* Bi-directional arrow marker */}
            <marker
              id="biArrow"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="#22c55e" />
            </marker>
          </defs>

          {/* Title */}
          <text x="700" y="30" fontSize="20" fontWeight="bold" textAnchor="middle" fill="#374151">
            Hospital Costing System - Integration Architecture
          </text>

          {/* User Layer */}
          <g id="user-layer">
            <rect x="50" y="80" width="1300" height="140" rx="8" fill="#dbeafe" stroke="#3b82f6" strokeWidth="2" />
            <text x="70" y="105" fontSize="16" fontWeight="bold" fill="#1e40af">User Interface Layer</text>

            {/* Power Apps */}
            <g id="powerapps">
              <rect x="100" y="130" width="200" height="70" rx="6" fill="#fff" stroke="#3b82f6" strokeWidth="2" />
              <text x="200" y="157" fontSize="14" fontWeight="bold" textAnchor="middle" fill="#374151">Power Apps</text>
              <text x="200" y="177" fontSize="11" textAnchor="middle" fill="#6b7280">(Model-Driven)</text>
              <text x="200" y="192" fontSize="10" textAnchor="middle" fill="#9ca3af">Data Entry Forms</text>
            </g>

            {/* Canvas App */}
            <g id="canvasapp">
              <rect x="350" y="130" width="200" height="70" rx="6" fill="#fff" stroke="#3b82f6" strokeWidth="2" />
              <text x="450" y="157" fontSize="14" fontWeight="bold" textAnchor="middle" fill="#374151">Power Apps</text>
              <text x="450" y="177" fontSize="11" textAnchor="middle" fill="#6b7280">(Canvas)</text>
              <text x="450" y="192" fontSize="10" textAnchor="middle" fill="#9ca3af">Mobile Review</text>
            </g>

            {/* Power BI */}
            <g id="powerbi">
              <rect x="600" y="130" width="200" height="70" rx="6" fill="#fff" stroke="#f59e0b" strokeWidth="2" />
              <text x="700" y="157" fontSize="14" fontWeight="bold" textAnchor="middle" fill="#374151">Power BI</text>
              <text x="700" y="177" fontSize="11" textAnchor="middle" fill="#6b7280">Analytics Dashboard</text>
              <text x="700" y="192" fontSize="10" textAnchor="middle" fill="#9ca3af">Reports & Insights</text>
            </g>

            {/* SharePoint */}
            <g id="sharepoint">
              <rect x="850" y="130" width="200" height="70" rx="6" fill="#fff" stroke="#22c55e" strokeWidth="2" />
              <text x="950" y="157" fontSize="14" fontWeight="bold" textAnchor="middle" fill="#374151">SharePoint</text>
              <text x="950" y="177" fontSize="11" textAnchor="middle" fill="#6b7280">Document Library</text>
              <text x="950" y="192" fontSize="10" textAnchor="middle" fill="#9ca3af">Supporting Docs</text>
            </g>

            {/* Teams */}
            <g id="teams">
              <rect x="1100" y="130" width="200" height="70" rx="6" fill="#fff" stroke="#a855f7" strokeWidth="2" />
              <text x="1200" y="157" fontSize="14" fontWeight="bold" textAnchor="middle" fill="#374151">Microsoft Teams</text>
              <text x="1200" y="177" fontSize="11" textAnchor="middle" fill="#6b7280">Notifications</text>
              <text x="1200" y="192" fontSize="10" textAnchor="middle" fill="#9ca3af">Collaboration</text>
            </g>
          </g>

          {/* Business Logic Layer */}
          <g id="logic-layer">
            <rect x="50" y="280" width="1300" height="140" rx="8" fill="#f0fdf4" stroke="#22c55e" strokeWidth="2" />
            <text x="70" y="305" fontSize="16" fontWeight="bold" fill="#166534">Business Logic Layer</text>

            {/* Power Automate */}
            <g id="automate">
              <rect x="100" y="330" width="300" height="70" rx="6" fill="#fff" stroke="#22c55e" strokeWidth="2" />
              <text x="250" y="355" fontSize="14" fontWeight="bold" textAnchor="middle" fill="#374151">Power Automate</text>
              <text x="250" y="375" fontSize="10" textAnchor="middle" fill="#6b7280">• Approval Workflows</text>
              <text x="250" y="390" fontSize="10" textAnchor="middle" fill="#6b7280">• Notifications • Scheduling</text>
            </g>

            {/* Business Rules */}
            <g id="rules">
              <rect x="450" y="330" width="300" height="70" rx="6" fill="#fff" stroke="#22c55e" strokeWidth="2" />
              <text x="600" y="355" fontSize="14" fontWeight="bold" textAnchor="middle" fill="#374151">Business Rules Engine</text>
              <text x="600" y="375" fontSize="10" textAnchor="middle" fill="#6b7280">• Validations • Calculations</text>
              <text x="600" y="390" fontSize="10" textAnchor="middle" fill="#6b7280">• Cost Formulas</text>
            </g>

            {/* Plugins */}
            <g id="plugins">
              <rect x="800" y="330" width="300" height="70" rx="6" fill="#fff" stroke="#22c55e" strokeWidth="2" />
              <text x="950" y="355" fontSize="14" fontWeight="bold" textAnchor="middle" fill="#374151">Custom Plugins (C#)</text>
              <text x="950" y="375" fontSize="10" textAnchor="middle" fill="#6b7280">• Complex Logic</text>
              <text x="950" y="390" fontSize="10" textAnchor="middle" fill="#6b7280">• External API Integration</text>
            </g>
          </g>

          {/* Data Layer */}
          <g id="data-layer">
            <rect x="50" y="480" width="1300" height="140" rx="8" fill="#fef3c7" stroke="#f59e0b" strokeWidth="2" />
            <text x="70" y="505" fontSize="16" fontWeight="bold" fill="#d97706">Data Layer</text>

            {/* Dataverse */}
            <g id="dataverse">
              <rect x="250" y="530" width="350" height="70" rx="6" fill="#fff" stroke="#f59e0b" strokeWidth="2" />
              <text x="425" y="555" fontSize="16" fontWeight="bold" textAnchor="middle" fill="#374151">Microsoft Dataverse</text>
              <text x="425" y="575" fontSize="11" textAnchor="middle" fill="#6b7280">Core Database (CDS)</text>
              <text x="425" y="592" fontSize="10" textAnchor="middle" fill="#9ca3af">Patients • Episodes • Line Items • Departments</text>
            </g>

            {/* Azure SQL */}
            <g id="azuresql">
              <rect x="650" y="530" width="300" height="70" rx="6" fill="#fff" stroke="#3b82f6" strokeWidth="2" />
              <text x="800" y="555" fontSize="14" fontWeight="bold" textAnchor="middle" fill="#374151">Azure SQL Database</text>
              <text x="800" y="575" fontSize="11" textAnchor="middle" fill="#6b7280">Historical Archive</text>
              <text x="800" y="592" fontSize="10" textAnchor="middle" fill="#9ca3af">(Optional)</text>
            </g>

            {/* Data Lake */}
            <g id="datalake">
              <rect x="1000" y="530" width="250" height="70" rx="6" fill="#fff" stroke="#a855f7" strokeWidth="2" />
              <text x="1125" y="555" fontSize="14" fontWeight="bold" textAnchor="middle" fill="#374151">Azure Data Lake</text>
              <text x="1125" y="575" fontSize="11" textAnchor="middle" fill="#6b7280">Big Data Analytics</text>
              <text x="1125" y="592" fontSize="10" textAnchor="middle" fill="#9ca3af">(Future)</text>
            </g>
          </g>

          {/* External Systems Layer */}
          <g id="external-layer">
            <rect x="50" y="680" width="1300" height="140" rx="8" fill="#fee2e2" stroke="#ef4444" strokeWidth="2" />
            <text x="70" y="705" fontSize="16" fontWeight="bold" fill="#991b1b">External Systems</text>

            {/* Excel */}
            <g id="excel">
              <rect x="100" y="730" width="200" height="70" rx="6" fill="#fff" stroke="#22c55e" strokeWidth="2" />
              <text x="200" y="757" fontSize="14" fontWeight="bold" textAnchor="middle" fill="#374151">Excel Spreadsheets</text>
              <text x="200" y="777" fontSize="11" textAnchor="middle" fill="#6b7280">Legacy Data</text>
              <text x="200" y="792" fontSize="10" textAnchor="middle" fill="#9ca3af">One-time Import</text>
            </g>

            {/* EHR/EMR */}
            <g id="ehr">
              <rect x="350" y="730" width="200" height="70" rx="6" fill="#fff" stroke="#3b82f6" strokeWidth="2" />
              <text x="450" y="757" fontSize="14" fontWeight="bold" textAnchor="middle" fill="#374151">EHR / EMR System</text>
              <text x="450" y="777" fontSize="11" textAnchor="middle" fill="#6b7280">Patient Records</text>
              <text x="450" y="792" fontSize="10" textAnchor="middle" fill="#9ca3af">API Integration</text>
            </g>

            {/* Finance ERP */}
            <g id="erp">
              <rect x="600" y="730" width="200" height="70" rx="6" fill="#fff" stroke="#f59e0b" strokeWidth="2" />
              <text x="700" y="757" fontSize="14" fontWeight="bold" textAnchor="middle" fill="#374151">Finance ERP</text>
              <text x="700" y="777" fontSize="11" textAnchor="middle" fill="#6b7280">GL / Accounting</text>
              <text x="700" y="792" fontSize="10" textAnchor="middle" fill="#9ca3af">Batch Export</text>
            </g>

            {/* Email */}
            <g id="email">
              <rect x="850" y="730" width="200" height="70" rx="6" fill="#fff" stroke="#a855f7" strokeWidth="2" />
              <text x="950" y="757" fontSize="14" fontWeight="bold" textAnchor="middle" fill="#374151">Email (SMTP)</text>
              <text x="950" y="777" fontSize="11" textAnchor="middle" fill="#6b7280">Notifications</text>
              <text x="950" y="792" fontSize="10" textAnchor="middle" fill="#9ca3af">Office 365</text>
            </g>

            {/* Azure AD */}
            <g id="azuread">
              <rect x="1100" y="730" width="200" height="70" rx="6" fill="#fff" stroke="#ef4444" strokeWidth="2" />
              <text x="1200" y="757" fontSize="14" fontWeight="bold" textAnchor="middle" fill="#374151">Azure AD</text>
              <text x="1200" y="777" fontSize="11" textAnchor="middle" fill="#6b7280">Authentication</text>
              <text x="1200" y="792" fontSize="10" textAnchor="middle" fill="#9ca3af">SSO / Security</text>
            </g>
          </g>

          {/* Connection Lines */}
          {/* UI to Logic */}
          <line x1="200" y1="200" x2="250" y2="330" stroke="#3b82f6" strokeWidth="2" markerEnd="url(#integrationArrow)" />
          <line x1="450" y1="200" x2="250" y2="330" stroke="#3b82f6" strokeWidth="2" markerEnd="url(#integrationArrow)" />
          <line x1="700" y1="200" x2="600" y2="330" stroke="#3b82f6" strokeWidth="2" markerEnd="url(#integrationArrow)" />

          {/* Logic to Data */}
          <line x1="250" y1="400" x2="425" y2="530" stroke="#22c55e" strokeWidth="2" markerEnd="url(#biArrow)" />
          <line x1="600" y1="400" x2="425" y2="530" stroke="#22c55e" strokeWidth="2" markerEnd="url(#biArrow)" />
          <line x1="950" y1="400" x2="425" y2="530" stroke="#22c55e" strokeWidth="2" markerEnd="url(#biArrow)" />

          {/* Data to External */}
          <line x1="425" y1="600" x2="200" y2="730" stroke="#3b82f6" strokeWidth="2" strokeDasharray="5,5" />
          <line x1="425" y1="600" x2="450" y2="730" stroke="#3b82f6" strokeWidth="2" markerEnd="url(#integrationArrow)" />
          <line x1="425" y1="600" x2="700" y2="730" stroke="#3b82f6" strokeWidth="2" markerEnd="url(#integrationArrow)" />

          {/* Power Automate to Teams */}
          <line x1="400" y1="365" x2="1200" y2="200" stroke="#a855f7" strokeWidth="2" markerEnd="url(#integrationArrow)" strokeDasharray="5,5" />

          {/* Power Automate to Email */}
          <line x1="250" y1="400" x2="950" y2="730" stroke="#a855f7" strokeWidth="2" markerEnd="url(#integrationArrow)" strokeDasharray="5,5" />

          {/* Security */}
          <line x1="1200" y1="730" x2="1200" y2="200" stroke="#ef4444" strokeWidth="3" strokeDasharray="5,5" opacity="0.3" />
          <text x="1210" y="460" fontSize="11" fill="#ef4444" fontWeight="bold">Security</text>
        </svg>
      </Card>

      {/* Integration Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-6">
          <div className="flex items-start gap-3 mb-4">
            <ArrowRightLeft className="w-6 h-6 text-blue-600 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-bold">Key Integration Points</h3>
              <p className="text-sm text-gray-600">Data flow connections</p>
            </div>
          </div>
          <ul className="space-y-2 text-sm">
            <li className="flex items-start gap-2">
              <span className="text-blue-600">•</span>
              <div><strong>Excel Import:</strong> One-time migration via Data Import Wizard</div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600">•</span>
              <div><strong>EHR Integration:</strong> REST API for patient demographics</div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600">•</span>
              <div><strong>Finance ERP:</strong> Nightly batch export of cost data</div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600">•</span>
              <div><strong>Power BI:</strong> DirectQuery to Dataverse for real-time reports</div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600">•</span>
              <div><strong>Teams/Email:</strong> Notifications via Power Automate</div>
            </li>
          </ul>
        </Card>

        <Card className="p-6">
          <div className="flex items-start gap-3 mb-4">
            <Lock className="w-6 h-6 text-red-600 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-bold">Security & Compliance</h3>
              <p className="text-sm text-gray-600">Enterprise-grade protection</p>
            </div>
          </div>
          <ul className="space-y-2 text-sm">
            <li className="flex items-start gap-2">
              <span className="text-red-600">•</span>
              <div><strong>Azure AD SSO:</strong> Single sign-on for all users</div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-600">•</span>
              <div><strong>Role-Based Access:</strong> Dataverse security roles</div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-600">•</span>
              <div><strong>Data Encryption:</strong> At rest and in transit</div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-600">•</span>
              <div><strong>Audit Logging:</strong> Track all data changes</div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-600">•</span>
              <div><strong>HIPAA Compliant:</strong> Healthcare data protection</div>
            </li>
          </ul>
        </Card>
      </div>

      {/* Technology Stack */}
      <Card className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <h3 className="text-lg font-bold mb-4">Technology Stack Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="w-16 h-16 bg-blue-500 rounded-lg flex items-center justify-center mx-auto mb-2">
              <Monitor className="w-8 h-8 text-white" />
            </div>
            <p className="font-semibold text-sm">Frontend</p>
            <p className="text-xs text-gray-600">Power Apps</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-green-500 rounded-lg flex items-center justify-center mx-auto mb-2">
              <ArrowRightLeft className="w-8 h-8 text-white" />
            </div>
            <p className="font-semibold text-sm">Workflows</p>
            <p className="text-xs text-gray-600">Power Automate</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-orange-500 rounded-lg flex items-center justify-center mx-auto mb-2">
              <Database className="w-8 h-8 text-white" />
            </div>
            <p className="font-semibold text-sm">Database</p>
            <p className="text-xs text-gray-600">Dataverse</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-purple-500 rounded-lg flex items-center justify-center mx-auto mb-2">
              <Cloud className="w-8 h-8 text-white" />
            </div>
            <p className="font-semibold text-sm">Platform</p>
            <p className="text-xs text-gray-600">Azure Cloud</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
