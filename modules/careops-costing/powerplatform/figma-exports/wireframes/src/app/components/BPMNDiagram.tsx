import { Card } from './ui/card';

export function BPMNDiagram() {
  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold">Hospital Costing Process - BPMN 2.0</h2>
        <p className="text-gray-600">Business Process Model and Notation Diagram</p>
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
              id="arrowhead"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="#374151" />
            </marker>

            {/* Error arrow marker */}
            <marker
              id="errorArrow"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="#dc2626" />
            </marker>
          </defs>

          {/* Swimlanes */}
          {/* Clinical Staff Lane */}
          <g id="lane-clinical">
            <rect x="0" y="0" width="1400" height="220" fill="#dbeafe" stroke="#3b82f6" strokeWidth="2" />
            <text x="20" y="110" fontSize="16" fontWeight="bold" fill="#1e40af" transform="rotate(-90 20 110)">
              Clinical Staff
            </text>
          </g>

          {/* System Lane */}
          <g id="lane-system">
            <rect x="0" y="220" width="1400" height="220" fill="#f3e8ff" stroke="#a855f7" strokeWidth="2" />
            <text x="20" y="330" fontSize="16" fontWeight="bold" fill="#7e22ce" transform="rotate(-90 20 330)">
              System (Power Platform)
            </text>
          </g>

          {/* Finance Manager Lane */}
          <g id="lane-finance">
            <rect x="0" y="440" width="1400" height="220" fill="#fef3c7" stroke="#f59e0b" strokeWidth="2" />
            <text x="20" y="550" fontSize="16" fontWeight="bold" fill="#d97706" transform="rotate(-90 20 550)">
              Finance Manager
            </text>
          </g>

          {/* BI/Reporting Lane */}
          <g id="lane-bi">
            <rect x="0" y="660" width="1400" height="220" fill="#dcfce7" stroke="#22c55e" strokeWidth="2" />
            <text x="20" y="770" fontSize="16" fontWeight="bold" fill="#16a34a" transform="rotate(-90 20 770)">
              BI & Reporting
            </text>
          </g>

          {/* BPMN Elements */}

          {/* Start Event */}
          <circle cx="100" cy="110" r="20" fill="#fff" stroke="#16a34a" strokeWidth="3" />
          <text x="100" y="155" fontSize="12" textAnchor="middle" fill="#374151">Start</text>

          {/* Task 1: Enter Patient Info */}
          <rect x="160" y="70" width="140" height="80" rx="10" fill="#fff" stroke="#374151" strokeWidth="2" />
          <text x="230" y="100" fontSize="13" fontWeight="600" textAnchor="middle" fill="#374151">Enter Patient &amp;</text>
          <text x="230" y="120" fontSize="13" fontWeight="600" textAnchor="middle" fill="#374151">Episode Info</text>

          {/* Flow 1 to 2 */}
          <line x1="120" y1="110" x2="160" y2="110" stroke="#374151" strokeWidth="2" markerEnd="url(#arrowhead)" />

          {/* Task 2: Add Cost Items */}
          <rect x="340" y="70" width="140" height="80" rx="10" fill="#fff" stroke="#374151" strokeWidth="2" />
          <text x="410" y="100" fontSize="13" fontWeight="600" textAnchor="middle" fill="#374151">Add Cost Items</text>
          <text x="410" y="120" fontSize="13" fontWeight="600" textAnchor="middle" fill="#374151">&amp; Resources</text>

          {/* Flow 2 to 3 */}
          <line x1="300" y1="110" x2="340" y2="110" stroke="#374151" strokeWidth="2" markerEnd="url(#arrowhead)" />

          {/* Gateway: Data Complete? */}
          <g id="gateway-complete">
            <path d="M 530 110 L 560 80 L 590 110 L 560 140 Z" fill="#fff" stroke="#374151" strokeWidth="2" />
            <text x="560" y="115" fontSize="20" textAnchor="middle" fill="#374151">?</text>
            <text x="560" y="165" fontSize="11" textAnchor="middle" fill="#374151">Data Complete?</text>
          </g>

          {/* Flow 3 to Gateway */}
          <line x1="480" y1="110" x2="530" y2="110" stroke="#374151" strokeWidth="2" markerEnd="url(#arrowhead)" />

          {/* Loop back - No */}
          <path d="M 560 80 L 560 40 L 410 40 L 410 70" stroke="#dc2626" strokeWidth="2" fill="none" markerEnd="url(#errorArrow)" strokeDasharray="5,5" />
          <text x="485" y="35" fontSize="11" fill="#dc2626">No</text>

          {/* Flow to System - Yes */}
          <line x1="560" y1="140" x2="560" y2="280" stroke="#374151" strokeWidth="2" markerEnd="url(#arrowhead)" />
          <text x="570" y="210" fontSize="11" fill="#374151">Yes</text>

          {/* Task 3: Validate Data */}
          <rect x="490" y="280" width="140" height="80" rx="10" fill="#fff" stroke="#374151" strokeWidth="2" />
          <text x="560" y="305" fontSize="13" fontWeight="600" textAnchor="middle" fill="#374151">Validate Data</text>
          <text x="560" y="325" fontSize="12" textAnchor="middle" fill="#666">(Rules Engine)</text>

          {/* Task 4: Calculate Costs */}
          <rect x="670" y="280" width="140" height="80" rx="10" fill="#fff" stroke="#374151" strokeWidth="2" />
          <text x="740" y="305" fontSize="13" fontWeight="600" textAnchor="middle" fill="#374151">Calculate Total</text>
          <text x="740" y="325" fontSize="13" fontWeight="600" textAnchor="middle" fill="#374151">Costs &amp; Overhead</text>

          {/* Flow 4 to 5 */}
          <line x1="630" y1="320" x2="670" y2="320" stroke="#374151" strokeWidth="2" markerEnd="url(#arrowhead)" />

          {/* Task 5: Generate Summary */}
          <rect x="850" y="280" width="140" height="80" rx="10" fill="#fff" stroke="#374151" strokeWidth="2" />
          <text x="920" y="305" fontSize="13" fontWeight="600" textAnchor="middle" fill="#374151">Generate Cost</text>
          <text x="920" y="325" fontSize="13" fontWeight="600" textAnchor="middle" fill="#374151">Summary Report</text>

          {/* Flow 5 to 6 */}
          <line x1="810" y1="320" x2="850" y2="320" stroke="#374151" strokeWidth="2" markerEnd="url(#arrowhead)" />

          {/* Flow to Finance Manager */}
          <line x1="920" y1="360" x2="920" y2="500" stroke="#374151" strokeWidth="2" markerEnd="url(#arrowhead)" />

          {/* Task 6: Review Costs */}
          <rect x="850" y="500" width="140" height="80" rx="10" fill="#fff" stroke="#374151" strokeWidth="2" />
          <text x="920" y="530" fontSize="13" fontWeight="600" textAnchor="middle" fill="#374151">Review &amp; Verify</text>
          <text x="920" y="550" fontSize="13" fontWeight="600" textAnchor="middle" fill="#374151">Cost Details</text>

          {/* Gateway: Approved? */}
          <g id="gateway-approval">
            <path d="M 1040 540 L 1070 510 L 1100 540 L 1070 570 Z" fill="#fff" stroke="#374151" strokeWidth="2" />
            <text x="1070" y="545" fontSize="20" textAnchor="middle" fill="#374151">?</text>
            <text x="1070" y="595" fontSize="11" textAnchor="middle" fill="#374151">Approved?</text>
          </g>

          {/* Flow 6 to Gateway */}
          <line x1="990" y1="540" x2="1040" y2="540" stroke="#374151" strokeWidth="2" markerEnd="url(#arrowhead)" />

          {/* Reject - Loop back */}
          <path d="M 1070 510 L 1070 470 L 410 470 L 410 150" stroke="#dc2626" strokeWidth="2" fill="none" markerEnd="url(#errorArrow)" strokeDasharray="5,5" />
          <text x="740" y="465" fontSize="11" fill="#dc2626">Needs Revision</text>

          {/* Task 7: Make Adjustments (if needed) */}
          <rect x="1000" y="620" width="140" height="60" rx="10" fill="#fff" stroke="#374151" strokeWidth="2" strokeDasharray="5,5" />
          <text x="1070" y="650" fontSize="12" textAnchor="middle" fill="#666">Make Adjustments</text>
          <text x="1070" y="665" fontSize="11" textAnchor="middle" fill="#999">(Optional)</text>

          {/* Approve - Continue */}
          <line x1="1100" y1="540" x2="1180" y2="540" stroke="#374151" strokeWidth="2" markerEnd="url(#arrowhead)" />
          <text x="1130" y="535" fontSize="11" fill="#16a34a">Approved</text>

          {/* Task 8: Finalize & Store */}
          <rect x="1180" y="280" width="140" height="80" rx="10" fill="#fff" stroke="#374151" strokeWidth="2" />
          <text x="1250" y="305" fontSize="13" fontWeight="600" textAnchor="middle" fill="#374151">Finalize &amp; Store</text>
          <text x="1250" y="325" fontSize="13" fontWeight="600" textAnchor="middle" fill="#374151">in Database</text>

          {/* Flow approved to finalize */}
          <path d="M 1180 540 L 1250 540 L 1250 360" stroke="#374151" strokeWidth="2" fill="none" markerEnd="url(#arrowhead)" />

          {/* Parallel Gateway - Split */}
          <g id="gateway-parallel-split">
            <path d="M 1250 200 L 1280 170 L 1310 200 L 1280 230 Z" fill="#fff" stroke="#374151" strokeWidth="3" />
            <text x="1280" y="210" fontSize="20" fontWeight="bold" textAnchor="middle" fill="#374151">+</text>
          </g>

          {/* Flow finalize to parallel gateway */}
          <line x1="1250" y1="280" x2="1250" y2="230" stroke="#374151" strokeWidth="2" markerEnd="url(#arrowhead)" />
          <line x1="1250" y1="230" x2="1280" y2="230" stroke="#374151" strokeWidth="2" />

          {/* Flow to BI Lane */}
          <path d="M 1280 230 L 1280 720" stroke="#374151" strokeWidth="2" fill="none" markerEnd="url(#arrowhead)" />

          {/* Task 9: Update Dashboards */}
          <rect x="1180" y="720" width="140" height="80" rx="10" fill="#fff" stroke="#374151" strokeWidth="2" />
          <text x="1250" y="745" fontSize="13" fontWeight="600" textAnchor="middle" fill="#374151">Update Power BI</text>
          <text x="1250" y="765" fontSize="13" fontWeight="600" textAnchor="middle" fill="#374151">Dashboards</text>

          {/* Flow parallel to dashboards */}
          <line x1="1280" y1="720" x2="1280" y2="760" stroke="#374151" strokeWidth="2" />
          <line x1="1280" y1="760" x2="1320" y2="760" stroke="#374151" strokeWidth="2" markerEnd="url(#arrowhead)" />

          {/* Task 10: Send Notifications */}
          <rect x="1030" y="170" width="140" height="60" rx="10" fill="#fff" stroke="#374151" strokeWidth="2" />
          <text x="1100" y="195" fontSize="13" fontWeight="600" textAnchor="middle" fill="#374151">Send Email</text>
          <text x="1100" y="213" fontSize="13" fontWeight="600" textAnchor="middle" fill="#374151">Notifications</text>

          {/* Flow to notification */}
          <path d="M 1280 200 L 1100 200" stroke="#374151" strokeWidth="2" fill="none" markerEnd="url(#arrowhead)" />

          {/* End Event */}
          <circle cx="1350" cy="760" r="20" fill="#fff" stroke="#dc2626" strokeWidth="4" />
          <circle cx="1350" cy="760" r="16" fill="#fff" stroke="#dc2626" strokeWidth="1" />
          <text x="1350" y="795" fontSize="12" textAnchor="middle" fill="#374151">End</text>

          {/* Legend */}
          <g id="legend" transform="translate(50, 820)">
            <text x="0" y="0" fontSize="14" fontWeight="bold" fill="#374151">Legend:</text>

            {/* Start/End Event */}
            <circle cx="15" cy="25" r="8" fill="#fff" stroke="#16a34a" strokeWidth="2" />
            <text x="30" y="30" fontSize="11" fill="#374151">Start Event</text>

            {/* Task */}
            <rect x="120" y="17" width="40" height="16" rx="3" fill="#fff" stroke="#374151" strokeWidth="1.5" />
            <text x="165" y="30" fontSize="11" fill="#374151">Task/Activity</text>

            {/* Gateway */}
            <path d="M 270 25 L 280 15 L 290 25 L 280 35 Z" fill="#fff" stroke="#374151" strokeWidth="1.5" />
            <text x="300" y="30" fontSize="11" fill="#374151">Gateway (Decision)</text>

            {/* Parallel Gateway */}
            <path d="M 450 25 L 460 15 L 470 25 L 460 35 Z" fill="#fff" stroke="#374151" strokeWidth="2" />
            <text x="453" y="28" fontSize="12" fontWeight="bold" fill="#374151">+</text>
            <text x="480" y="30" fontSize="11" fill="#374151">Parallel Gateway</text>

            {/* Optional Task */}
            <rect x="630" y="17" width="40" height="16" rx="3" fill="#fff" stroke="#374151" strokeWidth="1.5" strokeDasharray="2,2" />
            <text x="675" y="30" fontSize="11" fill="#374151">Optional Task</text>
          </g>
        </svg>
      </Card>

      {/* Process Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-4">
          <h3 className="font-bold text-lg mb-3">Process Overview</h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li>• <strong>Duration:</strong> Typically 10-30 minutes per case</li>
            <li>• <strong>Frequency:</strong> Per patient episode/procedure</li>
            <li>• <strong>Automation:</strong> 60% automated (calculations, validations)</li>
            <li>• <strong>Participants:</strong> 3 roles (Clinical, Finance, System)</li>
          </ul>
        </Card>

        <Card className="p-4">
          <h3 className="font-bold text-lg mb-3">Key Decision Points</h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li>• <strong>Data Completeness:</strong> All required fields entered?</li>
            <li>• <strong>Finance Approval:</strong> Costs verified and approved?</li>
            <li>• <strong>Exception Handling:</strong> Rejections loop back for revision</li>
            <li>• <strong>Parallel Processing:</strong> Notifications + BI updates</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
