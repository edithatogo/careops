import { Card } from './ui/card';
import { Database, Key, Link } from 'lucide-react';

export function DataModelDiagram() {
  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold">Data Model - Entity Relationship Diagram</h2>
        <p className="text-gray-600">Database structure for Power Platform / Dataverse</p>
      </div>

      <Card className="p-8 overflow-x-auto">
        <svg
          viewBox="0 0 1400 800"
          className="w-full h-auto"
          style={{ minWidth: '1000px' }}
        >
          <defs>
            {/* Relationship arrow */}
            <marker
              id="relationArrow"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="#6b7280" />
            </marker>
          </defs>

          {/* Patient Entity */}
          <g id="entity-patient">
            <rect x="50" y="50" width="280" height="280" rx="8" fill="#dbeafe" stroke="#3b82f6" strokeWidth="3" />
            <rect x="50" y="50" width="280" height="45" rx="8" fill="#3b82f6" />
            <text x="190" y="78" fontSize="18" fontWeight="bold" textAnchor="middle" fill="#fff">Patient</text>

            {/* Fields */}
            <g className="fields">
              <text x="65" y="120" fontSize="13" fontWeight="bold" fill="#1e40af">🔑 PatientID</text>
              <text x="250" y="120" fontSize="11" fill="#64748b">PK</text>

              <text x="65" y="145" fontSize="13" fill="#374151">FirstName</text>
              <text x="250" y="145" fontSize="11" fill="#64748b">Text</text>

              <text x="65" y="165" fontSize="13" fill="#374151">LastName</text>
              <text x="250" y="165" fontSize="11" fill="#64748b">Text</text>

              <text x="65" y="185" fontSize="13" fill="#374151">DateOfBirth</text>
              <text x="250" y="185" fontSize="11" fill="#64748b">Date</text>

              <text x="65" y="205" fontSize="13" fill="#374151">MedicalRecordNo</text>
              <text x="250" y="205" fontSize="11" fill="#64748b">Text</text>

              <text x="65" y="225" fontSize="13" fill="#374151">InsuranceType</text>
              <text x="250" y="225" fontSize="11" fill="#64748b">Choice</text>

              <text x="65" y="245" fontSize="13" fill="#374151">ContactPhone</text>
              <text x="250" y="245" fontSize="11" fill="#64748b">Phone</text>

              <text x="65" y="265" fontSize="13" fill="#374151">ContactEmail</text>
              <text x="250" y="265" fontSize="11" fill="#64748b">Email</text>

              <text x="65" y="285" fontSize="13" fill="#374151">Active</text>
              <text x="250" y="285" fontSize="11" fill="#64748b">Boolean</text>

              <text x="65" y="305" fontSize="13" fill="#374151">CreatedDate</text>
              <text x="250" y="305" fontSize="11" fill="#64748b">DateTime</text>
            </g>
          </g>

          {/* Costing Episode Entity */}
          <g id="entity-episode">
            <rect x="560" y="50" width="300" height="350" rx="8" fill="#f0fdf4" stroke="#22c55e" strokeWidth="3" />
            <rect x="560" y="50" width="300" height="45" rx="8" fill="#22c55e" />
            <text x="710" y="78" fontSize="18" fontWeight="bold" textAnchor="middle" fill="#fff">Costing Episode</text>

            {/* Fields */}
            <g className="fields">
              <text x="575" y="120" fontSize="13" fontWeight="bold" fill="#166534">🔑 EpisodeID</text>
              <text x="830" y="120" fontSize="11" fill="#64748b">PK</text>

              <text x="575" y="145" fontSize="13" fill="#374151">🔗 PatientID</text>
              <text x="830" y="145" fontSize="11" fill="#64748b">FK</text>

              <text x="575" y="165" fontSize="13" fill="#374151">🔗 DepartmentID</text>
              <text x="830" y="165" fontSize="11" fill="#64748b">FK</text>

              <text x="575" y="185" fontSize="13" fill="#374151">EpisodeNumber</text>
              <text x="830" y="185" fontSize="11" fill="#64748b">Text</text>

              <text x="575" y="205" fontSize="13" fill="#374151">AdmissionDate</text>
              <text x="830" y="205" fontSize="11" fill="#64748b">Date</text>

              <text x="575" y="225" fontSize="13" fill="#374151">DischargeDate</text>
              <text x="830" y="225" fontSize="11" fill="#64748b">Date</text>

              <text x="575" y="245" fontSize="13" fill="#374151">LengthOfStay</text>
              <text x="830" y="245" fontSize="11" fill="#64748b">Number</text>

              <text x="575" y="265" fontSize="13" fill="#374151">PrimaryProcedure</text>
              <text x="830" y="265" fontSize="11" fill="#64748b">Choice</text>

              <text x="575" y="285" fontSize="13" fill="#374151">TotalCost</text>
              <text x="830" y="285" fontSize="11" fill="#64748b">Currency</text>

              <text x="575" y="305" fontSize="13" fill="#374151">Status</text>
              <text x="830" y="305" fontSize="11" fill="#64748b">Choice</text>

              <text x="575" y="325" fontSize="13" fill="#374151">SubmittedBy</text>
              <text x="830" y="325" fontSize="11" fill="#64748b">User</text>

              <text x="575" y="345" fontSize="13" fill="#374151">ApprovedBy</text>
              <text x="830" y="345" fontSize="11" fill="#64748b">User</text>

              <text x="575" y="365" fontSize="13" fill="#374151">ApprovalDate</text>
              <text x="830" y="365" fontSize="11" fill="#64748b">DateTime</text>

              <text x="575" y="385" fontSize="13" fill="#374151">Notes</text>
              <text x="830" y="385" fontSize="11" fill="#64748b">Memo</text>
            </g>
          </g>

          {/* Cost Line Item Entity */}
          <g id="entity-lineitem">
            <rect x="1020" y="50" width="320" height="350" rx="8" fill="#fef3c7" stroke="#f59e0b" strokeWidth="3" />
            <rect x="1020" y="50" width="320" height="45" rx="8" fill="#f59e0b" />
            <text x="1180" y="78" fontSize="18" fontWeight="bold" textAnchor="middle" fill="#fff">Cost Line Item</text>

            {/* Fields */}
            <g className="fields">
              <text x="1035" y="120" fontSize="13" fontWeight="bold" fill="#d97706">🔑 LineItemID</text>
              <text x="1310" y="120" fontSize="11" fill="#64748b">PK</text>

              <text x="1035" y="145" fontSize="13" fill="#374151">🔗 EpisodeID</text>
              <text x="1310" y="145" fontSize="11" fill="#64748b">FK</text>

              <text x="1035" y="165" fontSize="13" fill="#374151">🔗 CostCategoryID</text>
              <text x="1310" y="165" fontSize="11" fill="#64748b">FK</text>

              <text x="1035" y="185" fontSize="13" fill="#374151">LineNumber</text>
              <text x="1310" y="185" fontSize="11" fill="#64748b">Number</text>

              <text x="1035" y="205" fontSize="13" fill="#374151">Description</text>
              <text x="1310" y="205" fontSize="11" fill="#64748b">Text</text>

              <text x="1035" y="225" fontSize="13" fill="#374151">Quantity</text>
              <text x="1310" y="225" fontSize="11" fill="#64748b">Decimal</text>

              <text x="1035" y="245" fontSize="13" fill="#374151">UnitOfMeasure</text>
              <text x="1310" y="245" fontSize="11" fill="#64748b">Text</text>

              <text x="1035" y="265" fontSize="13" fill="#374151">UnitCost</text>
              <text x="1310" y="265" fontSize="11" fill="#64748b">Currency</text>

              <text x="1035" y="285" fontSize="13" fill="#374151">ExtendedCost</text>
              <text x="1310" y="285" fontSize="11" fill="#64748b">Currency</text>

              <text x="1035" y="305" fontSize="13" fill="#374151">CostCenter</text>
              <text x="1310" y="305" fontSize="11" fill="#64748b">Text</text>

              <text x="1035" y="325" fontSize="13" fill="#374151">GLCode</text>
              <text x="1310" y="325" fontSize="11" fill="#64748b">Text</text>

              <text x="1035" y="345" fontSize="13" fill="#374151">ServiceDate</text>
              <text x="1310" y="345" fontSize="11" fill="#64748b">Date</text>

              <text x="1035" y="365" fontSize="13" fill="#374151">CreatedDate</text>
              <text x="1310" y="365" fontSize="11" fill="#64748b">DateTime</text>

              <text x="1035" y="385" fontSize="13" fill="#374151">ModifiedDate</text>
              <text x="1310" y="385" fontSize="11" fill="#64748b">DateTime</text>
            </g>
          </g>

          {/* Department Entity */}
          <g id="entity-department">
            <rect x="50" y="420" width="280" height="220" rx="8" fill="#f3e8ff" stroke="#a855f7" strokeWidth="3" />
            <rect x="50" y="420" width="280" height="45" rx="8" fill="#a855f7" />
            <text x="190" y="448" fontSize="18" fontWeight="bold" textAnchor="middle" fill="#fff">Department</text>

            {/* Fields */}
            <g className="fields">
              <text x="65" y="490" fontSize="13" fontWeight="bold" fill="#7e22ce">🔑 DepartmentID</text>
              <text x="250" y="490" fontSize="11" fill="#64748b">PK</text>

              <text x="65" y="515" fontSize="13" fill="#374151">DepartmentCode</text>
              <text x="250" y="515" fontSize="11" fill="#64748b">Text</text>

              <text x="65" y="535" fontSize="13" fill="#374151">DepartmentName</text>
              <text x="250" y="535" fontSize="11" fill="#64748b">Text</text>

              <text x="65" y="555" fontSize="13" fill="#374151">ManagerName</text>
              <text x="250" y="555" fontSize="11" fill="#64748b">Text</text>

              <text x="65" y="575" fontSize="13" fill="#374151">CostCenter</text>
              <text x="250" y="575" fontSize="11" fill="#64748b">Text</text>

              <text x="65" y="595" fontSize="13" fill="#374151">OverheadRate</text>
              <text x="250" y="595" fontSize="11" fill="#64748b">Percent</text>

              <text x="65" y="615" fontSize="13" fill="#374151">Active</text>
              <text x="250" y="615" fontSize="11" fill="#64748b">Boolean</text>
            </g>
          </g>

          {/* Cost Category Entity */}
          <g id="entity-category">
            <rect x="560" y="500" width="280" height="200" rx="8" fill="#fee2e2" stroke="#ef4444" strokeWidth="3" />
            <rect x="560" y="500" width="280" height="45" rx="8" fill="#ef4444" />
            <text x="700" y="528" fontSize="18" fontWeight="bold" textAnchor="middle" fill="#fff">Cost Category</text>

            {/* Fields */}
            <g className="fields">
              <text x="575" y="570" fontSize="13" fontWeight="bold" fill="#991b1b">🔑 CategoryID</text>
              <text x="800" y="570" fontSize="11" fill="#64748b">PK</text>

              <text x="575" y="595" fontSize="13" fill="#374151">CategoryCode</text>
              <text x="800" y="595" fontSize="11" fill="#64748b">Text</text>

              <text x="575" y="615" fontSize="13" fill="#374151">CategoryName</text>
              <text x="800" y="615" fontSize="11" fill="#64748b">Text</text>

              <text x="575" y="635" fontSize="13" fill="#374151">CategoryType</text>
              <text x="800" y="635" fontSize="11" fill="#64748b">Choice</text>

              <text x="575" y="655" fontSize="13" fill="#374151">DefaultGLCode</text>
              <text x="800" y="655" fontSize="11" fill="#64748b">Text</text>

              <text x="575" y="675" fontSize="13" fill="#374151">Active</text>
              <text x="800" y="675" fontSize="11" fill="#64748b">Boolean</text>
            </g>
          </g>

          {/* Relationships */}

          {/* Patient to Episode (1:Many) */}
          <line x1="330" y1="190" x2="560" y2="190" stroke="#6b7280" strokeWidth="2" markerEnd="url(#relationArrow)" />
          <text x="440" y="185" fontSize="12" fill="#6b7280">1</text>
          <text x="540" y="185" fontSize="12" fill="#6b7280">*</text>
          <text x="410" y="210" fontSize="11" fill="#374151" fontStyle="italic">has episodes</text>

          {/* Episode to LineItem (1:Many) */}
          <line x1="860" y1="225" x2="1020" y2="225" stroke="#6b7280" strokeWidth="2" markerEnd="url(#relationArrow)" />
          <text x="900" y="220" fontSize="12" fill="#6b7280">1</text>
          <text x="1000" y="220" fontSize="12" fill="#6b7280">*</text>
          <text x="900" y="245" fontSize="11" fill="#374151" fontStyle="italic">contains items</text>

          {/* Department to Episode (1:Many) */}
          <line x1="330" y1="530" x2="560" y2="280" stroke="#6b7280" strokeWidth="2" markerEnd="url(#relationArrow)" />
          <text x="340" y="525" fontSize="12" fill="#6b7280">1</text>
          <text x="540" y="290" fontSize="12" fill="#6b7280">*</text>
          <text x="400" y="390" fontSize="11" fill="#374151" fontStyle="italic">treats patients</text>

          {/* Category to LineItem (1:Many) */}
          <line x1="840" y1="600" x2="1180" y2="400" stroke="#6b7280" strokeWidth="2" markerEnd="url(#relationArrow)" />
          <text x="850" y="595" fontSize="12" fill="#6b7280">1</text>
          <text x="1160" y="410" fontSize="12" fill="#6b7280">*</text>
          <text x="950" y="490" fontSize="11" fill="#374151" fontStyle="italic">categorizes</text>

          {/* Legend */}
          <g id="legend" transform="translate(1020, 500)">
            <rect x="0" y="0" width="320" height="180" rx="8" fill="#f9fafb" stroke="#d1d5db" strokeWidth="2" />
            <text x="160" y="25" fontSize="14" fontWeight="bold" textAnchor="middle" fill="#374151">Notation Legend</text>

            <text x="10" y="50" fontSize="12" fontWeight="bold" fill="#374151">🔑 Primary Key (PK)</text>
            <text x="10" y="70" fontSize="12" fill="#374151">🔗 Foreign Key (FK)</text>
            <text x="10" y="90" fontSize="12" fill="#374151">1 : * = One to Many</text>

            <line x1="10" y1="105" x2="310" y2="105" stroke="#d1d5db" strokeWidth="1" />

            <text x="10" y="125" fontSize="11" fontWeight="bold" fill="#374151">Common Data Types:</text>
            <text x="10" y="142" fontSize="10" fill="#64748b">Text, Number, Currency, Date</text>
            <text x="10" y="157" fontSize="10" fill="#64748b">DateTime, Boolean, Choice, User</text>
          </g>
        </svg>
      </Card>

      {/* Additional Details */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <div className="flex items-start gap-3">
            <Database className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
            <div>
              <h4 className="font-semibold mb-2">5 Core Entities</h4>
              <p className="text-sm text-gray-600">Patient, Episode, Line Item, Department, and Cost Category tables</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-start gap-3">
            <Key className="w-6 h-6 text-purple-600 flex-shrink-0 mt-1" />
            <div>
              <h4 className="font-semibold mb-2">Relational Integrity</h4>
              <p className="text-sm text-gray-600">Foreign key relationships maintain data consistency across entities</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-start gap-3">
            <Link className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
            <div>
              <h4 className="font-semibold mb-2">Dataverse Ready</h4>
              <p className="text-sm text-gray-600">Structure aligns with Microsoft Dataverse / Common Data Model</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
