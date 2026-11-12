import { ArrowRight, CheckCircle2, FileSpreadsheet, ClipboardList, DollarSign, BarChart3, Users, AlertCircle } from 'lucide-react';
import { Card } from './ui/card';

export function WorkflowDiagram() {
  const stages = [
    {
      id: 1,
      title: 'Data Entry',
      description: 'Staff enters patient & service details',
      icon: ClipboardList,
      color: 'bg-blue-500',
      activities: ['Patient information', 'Service codes', 'Resources used']
    },
    {
      id: 2,
      title: 'Cost Calculation',
      description: 'Automatic cost computation',
      icon: DollarSign,
      color: 'bg-purple-500',
      activities: ['Labor costs', 'Material costs', 'Overhead allocation']
    },
    {
      id: 3,
      title: 'Review & Approval',
      description: 'Manager validation',
      icon: Users,
      color: 'bg-orange-500',
      activities: ['Cost verification', 'Adjustments', 'Sign-off']
    },
    {
      id: 4,
      title: 'Reporting & BI',
      description: 'Analytics & insights',
      icon: BarChart3,
      color: 'bg-green-500',
      activities: ['Dashboard views', 'Cost trends', 'Department analysis']
    }
  ];

  return (
    <div className="w-full max-w-6xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold">Hospital Costing Workflow</h2>
        <p className="text-gray-600">Excel to Power Platform Migration</p>
      </div>

      {/* Main Workflow */}
      <div className="relative">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {stages.map((stage, index) => (
            <div key={stage.id} className="relative">
              <Card className="p-6 hover:shadow-lg transition-shadow">
                <div className="flex flex-col items-center text-center space-y-4">
                  {/* Icon */}
                  <div className={`${stage.color} w-16 h-16 rounded-full flex items-center justify-center`}>
                    <stage.icon className="w-8 h-8 text-white" />
                  </div>

                  {/* Stage Number */}
                  <div className="absolute top-4 right-4 w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-sm font-bold">
                    {stage.id}
                  </div>

                  {/* Title */}
                  <h3 className="font-bold text-lg">{stage.title}</h3>

                  {/* Description */}
                  <p className="text-sm text-gray-600">{stage.description}</p>

                  {/* Activities */}
                  <ul className="space-y-1 w-full text-left text-sm">
                    {stage.activities.map((activity, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">{activity}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </Card>

              {/* Arrow between stages (desktop only) */}
              {index < stages.length - 1 && (
                <div className="hidden md:block absolute top-1/2 -right-9 transform -translate-y-1/2 z-10">
                  <ArrowRight className="w-6 h-6 text-gray-400" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Integration Points */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
        <Card className="p-4 bg-blue-50 border-blue-200">
          <div className="flex items-start gap-3">
            <FileSpreadsheet className="w-6 h-6 text-blue-600 flex-shrink-0" />
            <div>
              <h4 className="font-semibold text-blue-900">Excel Migration</h4>
              <p className="text-sm text-blue-700 mt-1">Import existing cost structures and historical data</p>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-purple-50 border-purple-200">
          <div className="flex items-start gap-3">
            <BarChart3 className="w-6 h-6 text-purple-600 flex-shrink-0" />
            <div>
              <h4 className="font-semibold text-purple-900">Power BI Integration</h4>
              <p className="text-sm text-purple-700 mt-1">Real-time dashboards and cost analytics</p>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-orange-50 border-orange-200">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-6 h-6 text-orange-600 flex-shrink-0" />
            <div>
              <h4 className="font-semibold text-orange-900">Validation Rules</h4>
              <p className="text-sm text-orange-700 mt-1">Automated checks and approval workflows</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
