import { Card } from './ui/card';
import { ArrowRight, FileSpreadsheet, Database } from 'lucide-react';

export function ExcelMigrationMap() {
  const mappings = [
    {
      section: 'Patient Information',
      items: [
        { excel: 'Patient_ID', arrow: '→', system: 'Patient.PatientID', type: 'Text (Primary Key)', notes: 'Unique identifier' },
        { excel: 'First_Name', arrow: '→', system: 'Patient.FirstName', type: 'Text', notes: '' },
        { excel: 'Last_Name', arrow: '→', system: 'Patient.LastName', type: 'Text', notes: '' },
        { excel: 'DOB', arrow: '→', system: 'Patient.DateOfBirth', type: 'Date', notes: 'Format: YYYY-MM-DD' },
        { excel: 'MRN', arrow: '→', system: 'Patient.MedicalRecordNo', type: 'Text', notes: 'Medical Record Number' },
        { excel: 'Insurance_Type', arrow: '→', system: 'Patient.InsuranceType', type: 'Choice', notes: 'Map to choice values' },
      ]
    },
    {
      section: 'Episode Details',
      items: [
        { excel: 'Episode_Number', arrow: '→', system: 'CostingEpisode.EpisodeNumber', type: 'Text', notes: 'Auto-generated if empty' },
        { excel: 'Admission_Date', arrow: '→', system: 'CostingEpisode.AdmissionDate', type: 'Date', notes: '' },
        { excel: 'Discharge_Date', arrow: '→', system: 'CostingEpisode.DischargeDate', type: 'Date', notes: 'Optional' },
        { excel: 'LOS', arrow: '→', system: 'CostingEpisode.LengthOfStay', type: 'Number', notes: 'Calculate if missing' },
        { excel: 'Department', arrow: '→', system: 'CostingEpisode.DepartmentID', type: 'Lookup', notes: 'Map to Department table' },
        { excel: 'Procedure_Code', arrow: '→', system: 'CostingEpisode.PrimaryProcedure', type: 'Choice', notes: 'Standardize codes' },
      ]
    },
    {
      section: 'Cost Line Items',
      items: [
        { excel: 'Line_Number', arrow: '→', system: 'CostLineItem.LineNumber', type: 'Number', notes: 'Sequential numbering' },
        { excel: 'Cost_Category', arrow: '→', system: 'CostLineItem.CostCategoryID', type: 'Lookup', notes: 'Map to Cost Category' },
        { excel: 'Item_Description', arrow: '→', system: 'CostLineItem.Description', type: 'Text', notes: '' },
        { excel: 'Qty', arrow: '→', system: 'CostLineItem.Quantity', type: 'Decimal', notes: '' },
        { excel: 'Unit_Cost', arrow: '→', system: 'CostLineItem.UnitCost', type: 'Currency', notes: '' },
        { excel: 'Total', arrow: '→', system: 'CostLineItem.ExtendedCost', type: 'Currency (Calculated)', notes: 'Qty × Unit Cost' },
        { excel: 'GL_Code', arrow: '→', system: 'CostLineItem.GLCode', type: 'Text', notes: 'General Ledger Code' },
      ]
    },
    {
      section: 'Reference Data',
      items: [
        { excel: 'Dept_Code', arrow: '→', system: 'Department.DepartmentCode', type: 'Text', notes: 'One-time import' },
        { excel: 'Dept_Name', arrow: '→', system: 'Department.DepartmentName', type: 'Text', notes: '' },
        { excel: 'Cost_Center', arrow: '→', system: 'Department.CostCenter', type: 'Text', notes: '' },
        { excel: 'Overhead_%', arrow: '→', system: 'Department.OverheadRate', type: 'Percent', notes: 'Default overhead rate' },
      ]
    }
  ];

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold">Excel to Power Platform Migration Map</h2>
        <p className="text-gray-600">Field mapping and data transformation guide</p>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 bg-blue-50 border-blue-200">
          <div className="flex items-start gap-3">
            <FileSpreadsheet className="w-6 h-6 text-blue-600 flex-shrink-0" />
            <div>
              <h4 className="font-semibold text-blue-900">Source: Excel</h4>
              <p className="text-sm text-blue-700 mt-1">Existing spreadsheet columns and worksheets</p>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-purple-50 border-purple-200">
          <div className="flex items-center justify-center h-full">
            <ArrowRight className="w-12 h-12 text-purple-600" />
            <span className="ml-3 text-lg font-semibold text-purple-900">Transform & Map</span>
          </div>
        </Card>

        <Card className="p-4 bg-green-50 border-green-200">
          <div className="flex items-start gap-3">
            <Database className="w-6 h-6 text-green-600 flex-shrink-0" />
            <div>
              <h4 className="font-semibold text-green-900">Target: Dataverse</h4>
              <p className="text-sm text-green-700 mt-1">Power Platform tables and fields</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Mapping Tables */}
      {mappings.map((section, sectionIndex) => (
        <Card key={sectionIndex} className="p-6">
          <h3 className="text-xl font-bold mb-4 text-gray-900">{section.section}</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-300 bg-gray-50">
                  <th className="text-left py-3 px-4 font-semibold text-sm w-1/4">Excel Column</th>
                  <th className="text-center py-3 px-2 font-semibold text-sm w-12"></th>
                  <th className="text-left py-3 px-4 font-semibold text-sm w-1/4">System Field</th>
                  <th className="text-left py-3 px-4 font-semibold text-sm w-1/6">Data Type</th>
                  <th className="text-left py-3 px-4 font-semibold text-sm w-1/3">Migration Notes</th>
                </tr>
              </thead>
              <tbody>
                {section.items.map((item, index) => (
                  <tr key={index} className="border-b border-gray-200 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <FileSpreadsheet className="w-4 h-4 text-blue-600 flex-shrink-0" />
                        <code className="text-sm font-mono bg-blue-50 px-2 py-1 rounded text-blue-900">
                          {item.excel}
                        </code>
                      </div>
                    </td>
                    <td className="py-3 px-2 text-center">
                      <ArrowRight className="w-5 h-5 text-gray-400 mx-auto" />
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <Database className="w-4 h-4 text-green-600 flex-shrink-0" />
                        <code className="text-sm font-mono bg-green-50 px-2 py-1 rounded text-green-900">
                          {item.system}
                        </code>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-sm text-gray-700 font-medium">{item.type}</span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-sm text-gray-600">{item.notes || '—'}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ))}

      {/* Migration Strategy */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-6">
          <h3 className="text-lg font-bold mb-4">Data Transformation Rules</h3>
          <ul className="space-y-3 text-sm">
            <li className="flex items-start gap-2">
              <span className="text-blue-600 font-bold mt-0.5">1.</span>
              <div>
                <strong>Date Formats:</strong> Convert all dates to ISO 8601 format (YYYY-MM-DD)
              </div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 font-bold mt-0.5">2.</span>
              <div>
                <strong>Lookups:</strong> Replace text values with foreign key references (Department, Cost Category)
              </div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 font-bold mt-0.5">3.</span>
              <div>
                <strong>Calculations:</strong> Extended Cost = Quantity × Unit Cost (validate in migration)
              </div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 font-bold mt-0.5">4.</span>
              <div>
                <strong>Required Fields:</strong> Validate all mandatory fields before import
              </div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 font-bold mt-0.5">5.</span>
              <div>
                <strong>Duplicates:</strong> Check for duplicate Patient IDs and Episode Numbers
              </div>
            </li>
          </ul>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-bold mb-4">Migration Phases</h3>
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                1
              </div>
              <div>
                <h4 className="font-semibold text-sm">Import Reference Data</h4>
                <p className="text-sm text-gray-600">Departments, Cost Categories first</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                2
              </div>
              <div>
                <h4 className="font-semibold text-sm">Import Patient Records</h4>
                <p className="text-sm text-gray-600">Deduplicate and validate patients</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                3
              </div>
              <div>
                <h4 className="font-semibold text-sm">Import Episodes</h4>
                <p className="text-sm text-gray-600">Link to patients and departments</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                4
              </div>
              <div>
                <h4 className="font-semibold text-sm">Import Line Items</h4>
                <p className="text-sm text-gray-600">Link to episodes, validate costs</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                ✓
              </div>
              <div>
                <h4 className="font-semibold text-sm">Validate & Test</h4>
                <p className="text-sm text-gray-600">Run reports, compare totals</p>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Tools Recommendation */}
      <Card className="p-6 bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
        <h3 className="text-lg font-bold mb-3">Recommended Migration Tools</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <h4 className="font-semibold text-sm mb-2">Power Query / Dataflows</h4>
            <p className="text-sm text-gray-700">Transform and cleanse Excel data before import</p>
          </div>
          <div>
            <h4 className="font-semibold text-sm mb-2">Data Import Wizard</h4>
            <p className="text-sm text-gray-700">Built-in Dataverse import for CSV/Excel files</p>
          </div>
          <div>
            <h4 className="font-semibold text-sm mb-2">Power Automate</h4>
            <p className="text-sm text-gray-700">Automate recurring imports and validation</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
