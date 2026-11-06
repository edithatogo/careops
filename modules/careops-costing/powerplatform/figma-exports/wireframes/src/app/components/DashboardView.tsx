import { Card } from './ui/card';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, DollarSign, AlertCircle, Users } from 'lucide-react';
import { Badge } from './ui/badge';

export function DashboardView() {
  // Mock data
  const costByDepartment = [
    { name: 'Surgery', cost: 245000, cases: 45 },
    { name: 'Emergency', cost: 189000, cases: 120 },
    { name: 'Cardiology', cost: 167000, cases: 65 },
    { name: 'Orthopedics', cost: 134000, cases: 38 },
    { name: 'Radiology', cost: 98000, cases: 210 },
    { name: 'ICU', cost: 287000, cases: 28 },
  ];

  const costTrend = [
    { month: 'Oct', cost: 856000, budget: 900000 },
    { month: 'Nov', cost: 923000, budget: 900000 },
    { month: 'Dec', cost: 878000, budget: 900000 },
    { month: 'Jan', cost: 945000, budget: 950000 },
    { month: 'Feb', cost: 912000, budget: 950000 },
    { month: 'Mar', cost: 987000, budget: 950000 },
  ];

  const costByCategory = [
    { name: 'Labor', value: 385000, color: '#3b82f6' },
    { name: 'Materials', value: 245000, color: '#22c55e' },
    { name: 'Pharmacy', value: 198000, color: '#a855f7' },
    { name: 'Equipment', value: 134000, color: '#f59e0b' },
    { name: 'Overhead', value: 158000, color: '#ef4444' },
  ];

  const totalCost = costByCategory.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Cost Analytics Dashboard</h2>
          <p className="text-gray-600 mt-1">Power BI / Real-time Reporting View</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">Last Updated</p>
          <p className="font-semibold">March 24, 2026 - 09:45 AM</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-blue-600 mb-1">Total Costs (MTD)</p>
              <h3 className="text-3xl font-bold text-blue-900">${(totalCost / 1000).toFixed(0)}K</h3>
              <div className="flex items-center gap-1 mt-2">
                <TrendingUp className="w-4 h-4 text-green-600" />
                <span className="text-sm text-green-600 font-medium">+4.2% vs last month</span>
              </div>
            </div>
            <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-white" />
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-green-600 mb-1">Total Episodes</p>
              <h3 className="text-3xl font-bold text-green-900">506</h3>
              <div className="flex items-center gap-1 mt-2">
                <TrendingUp className="w-4 h-4 text-green-600" />
                <span className="text-sm text-green-600 font-medium">+12 this week</span>
              </div>
            </div>
            <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
              <Users className="w-6 h-6 text-white" />
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-orange-600 mb-1">Avg Cost/Episode</p>
              <h3 className="text-3xl font-bold text-orange-900">${(totalCost / 506).toFixed(0)}</h3>
              <div className="flex items-center gap-1 mt-2">
                <TrendingUp className="w-4 h-4 text-red-600" />
                <span className="text-sm text-red-600 font-medium">+2.8% vs target</span>
              </div>
            </div>
            <div className="w-12 h-12 bg-orange-500 rounded-full flex items-center justify-center">
              <BarChart className="w-6 h-6 text-white" />
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-gradient-to-br from-red-50 to-red-100 border-red-200">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-red-600 mb-1">Pending Approval</p>
              <h3 className="text-3xl font-bold text-red-900">23</h3>
              <div className="flex items-center gap-1 mt-2">
                <AlertCircle className="w-4 h-4 text-red-600" />
                <span className="text-sm text-red-600 font-medium">Requires attention</span>
              </div>
            </div>
            <div className="w-12 h-12 bg-red-500 rounded-full flex items-center justify-center">
              <AlertCircle className="w-6 h-6 text-white" />
            </div>
          </div>
        </Card>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cost Trend */}
        <Card className="p-6">
          <div className="mb-4">
            <h3 className="text-xl font-bold">Monthly Cost Trend</h3>
            <p className="text-sm text-gray-600">Actual vs Budget Comparison</p>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={costTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip
                formatter={(value: number) => `$${(value / 1000).toFixed(0)}K`}
              />
              <Legend />
              <Line type="monotone" dataKey="cost" stroke="#3b82f6" strokeWidth={3} name="Actual Cost" />
              <Line type="monotone" dataKey="budget" stroke="#22c55e" strokeWidth={2} strokeDasharray="5 5" name="Budget" />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* Cost by Category */}
        <Card className="p-6">
          <div className="mb-4">
            <h3 className="text-xl font-bold">Cost Distribution by Category</h3>
            <p className="text-sm text-gray-600">Breakdown of cost types</p>
          </div>
          <div className="flex items-center gap-6">
            <ResponsiveContainer width="50%" height={300}>
              <PieChart>
                <Pie
                  data={costByCategory}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {costByCategory.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => `$${(value / 1000).toFixed(0)}K`} />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex-1 space-y-3">
              {costByCategory.map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded" style={{ backgroundColor: item.color }} />
                    <span className="text-sm font-medium">{item.name}</span>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold">${(item.value / 1000).toFixed(0)}K</p>
                    <p className="text-xs text-gray-500">{((item.value / totalCost) * 100).toFixed(1)}%</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>

      {/* Cost by Department */}
      <Card className="p-6">
        <div className="mb-4">
          <h3 className="text-xl font-bold">Cost by Department</h3>
          <p className="text-sm text-gray-600">Total costs and case volume by department</p>
        </div>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={costByDepartment}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis yAxisId="left" orientation="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Legend />
            <Bar yAxisId="left" dataKey="cost" fill="#3b82f6" name="Total Cost ($)" />
            <Bar yAxisId="right" dataKey="cases" fill="#22c55e" name="Number of Cases" />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      {/* Recent Episodes Table */}
      <Card className="p-6">
        <div className="mb-4">
          <h3 className="text-xl font-bold">Recent Costing Episodes</h3>
          <p className="text-sm text-gray-600">Fictional demo episodes only. No real patients or operational data.</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-sm">Episode ID</th>
                <th className="text-left py-3 px-4 font-semibold text-sm">Patient</th>
                <th className="text-left py-3 px-4 font-semibold text-sm">Department</th>
                <th className="text-left py-3 px-4 font-semibold text-sm">Date</th>
                <th className="text-right py-3 px-4 font-semibold text-sm">Total Cost</th>
                <th className="text-center py-3 px-4 font-semibold text-sm">Status</th>
              </tr>
            </thead>
            <tbody>
              {[
                { id: 'EP-2026-156', patient: 'DEMO-001', dept: 'Surgery', date: '2026-03-23', cost: 12450, status: 'Pending' },
                { id: 'EP-2026-155', patient: 'DEMO-002', dept: 'Cardiology', date: '2026-03-23', cost: 8920, status: 'Approved' },
                { id: 'EP-2026-154', patient: 'DEMO-003', dept: 'Emergency', date: '2026-03-22', cost: 3250, status: 'Approved' },
                { id: 'EP-2026-153', patient: 'DEMO-004', dept: 'ICU', date: '2026-03-22', cost: 28750, status: 'Pending' },
                { id: 'EP-2026-152', patient: 'DEMO-005', dept: 'Orthopedics', date: '2026-03-21', cost: 15680, status: 'Approved' },
              ].map((row, index) => (
                <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 text-sm font-medium text-blue-600">{row.id}</td>
                  <td className="py-3 px-4 text-sm">{row.patient}</td>
                  <td className="py-3 px-4 text-sm">{row.dept}</td>
                  <td className="py-3 px-4 text-sm text-gray-600">{row.date}</td>
                  <td className="py-3 px-4 text-sm text-right font-semibold">${row.cost.toLocaleString()}</td>
                  <td className="py-3 px-4 text-center">
                    <Badge variant={row.status === 'Approved' ? 'default' : 'outline'}>
                      {row.status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
