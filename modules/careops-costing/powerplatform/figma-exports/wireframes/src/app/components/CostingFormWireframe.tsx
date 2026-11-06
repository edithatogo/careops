import { useState } from 'react';
import { Card } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Separator } from './ui/separator';
import { Badge } from './ui/badge';
import { Calculator, Save, Send, Plus, Trash2 } from 'lucide-react';

interface CostItem {
  id: string;
  category: string;
  description: string;
  quantity: number;
  unitCost: number;
}

export function CostingFormWireframe() {
  const [costItems, setCostItems] = useState<CostItem[]>([
    { id: '1', category: '', description: '', quantity: 1, unitCost: 0 }
  ]);

  const addCostItem = () => {
    setCostItems([
      ...costItems,
      { id: Date.now().toString(), category: '', description: '', quantity: 1, unitCost: 0 }
    ]);
  };

  const removeCostItem = (id: string) => {
    setCostItems(costItems.filter(item => item.id !== id));
  };

  const totalCost = costItems.reduce((sum, item) => sum + (item.quantity * item.unitCost), 0);

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Hospital Costing Form</h2>
          <p className="text-gray-600 mt-1">Enter patient treatment costs and resource allocation</p>
        </div>
        <Badge variant="outline" className="text-sm">Draft</Badge>
      </div>

      <Card className="p-6">
        {/* Patient & Episode Information */}
        <div className="space-y-6">
          <div>
            <h3 className="text-xl font-semibold mb-4">Patient & Episode Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="patientId">Patient ID *</Label>
                <Input id="patientId" placeholder="P-12345" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="episodeId">Episode ID</Label>
                <Input id="episodeId" placeholder="EP-2026-001" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="admissionDate">Admission Date *</Label>
                <Input id="admissionDate" type="date" />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="department">Department *</Label>
                <Select>
                  <SelectTrigger id="department">
                    <SelectValue placeholder="Select department" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="emergency">Emergency</SelectItem>
                    <SelectItem value="surgery">Surgery</SelectItem>
                    <SelectItem value="cardiology">Cardiology</SelectItem>
                    <SelectItem value="orthopedics">Orthopedics</SelectItem>
                    <SelectItem value="radiology">Radiology</SelectItem>
                    <SelectItem value="icu">ICU</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="procedure">Primary Procedure *</Label>
                <Select>
                  <SelectTrigger id="procedure">
                    <SelectValue placeholder="Select procedure" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="consultation">Consultation</SelectItem>
                    <SelectItem value="minor-surgery">Minor Surgery</SelectItem>
                    <SelectItem value="major-surgery">Major Surgery</SelectItem>
                    <SelectItem value="diagnostic">Diagnostic</SelectItem>
                    <SelectItem value="therapy">Therapy</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="lengthOfStay">Length of Stay (days)</Label>
                <Input id="lengthOfStay" type="number" placeholder="0" min="0" />
              </div>
            </div>
          </div>

          <Separator />

          {/* Cost Items Section */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold">Cost Items</h3>
              <Button onClick={addCostItem} variant="outline" size="sm">
                <Plus className="w-4 h-4 mr-2" />
                Add Cost Item
              </Button>
            </div>

            <div className="space-y-3">
              {costItems.map((item, index) => (
                <Card key={item.id} className="p-4 bg-gray-50">
                  <div className="grid grid-cols-1 md:grid-cols-5 gap-3 items-end">
                    <div className="space-y-2">
                      <Label htmlFor={`category-${item.id}`}>Cost Category</Label>
                      <Select>
                        <SelectTrigger id={`category-${item.id}`}>
                          <SelectValue placeholder="Select" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="labor">Labor</SelectItem>
                          <SelectItem value="materials">Materials</SelectItem>
                          <SelectItem value="equipment">Equipment</SelectItem>
                          <SelectItem value="pharmacy">Pharmacy</SelectItem>
                          <SelectItem value="overhead">Overhead</SelectItem>
                          <SelectItem value="other">Other</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2 md:col-span-2">
                      <Label htmlFor={`description-${item.id}`}>Description</Label>
                      <Input
                        id={`description-${item.id}`}
                        placeholder="e.g., Surgical supplies, Nurse hours"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor={`quantity-${item.id}`}>Quantity</Label>
                      <Input
                        id={`quantity-${item.id}`}
                        type="number"
                        placeholder="1"
                        min="0"
                        step="0.01"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor={`unitCost-${item.id}`}>Unit Cost ($)</Label>
                      <Input
                        id={`unitCost-${item.id}`}
                        type="number"
                        placeholder="0.00"
                        min="0"
                        step="0.01"
                      />
                    </div>

                    {costItems.length > 1 && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => removeCostItem(item.id)}
                        className="self-end"
                      >
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </Button>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          </div>

          <Separator />

          {/* Additional Information */}
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Additional Information</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="insuranceType">Insurance Type</Label>
                <Select>
                  <SelectTrigger id="insuranceType">
                    <SelectValue placeholder="Select insurance" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="private">Private Insurance</SelectItem>
                    <SelectItem value="medicare">Medicare</SelectItem>
                    <SelectItem value="medicaid">Medicaid</SelectItem>
                    <SelectItem value="self-pay">Self-Pay</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="costCenter">Cost Center</Label>
                <Input id="costCenter" placeholder="CC-001" />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Notes / Comments</Label>
              <Textarea
                id="notes"
                placeholder="Add any additional notes or comments about this costing..."
                rows={3}
              />
            </div>
          </div>

          <Separator />

          {/* Cost Summary */}
          <div className="bg-blue-50 p-6 rounded-lg border-2 border-blue-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold flex items-center gap-2">
                <Calculator className="w-5 h-5" />
                Cost Summary
              </h3>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Subtotal (Direct Costs):</span>
                <span className="font-medium">${totalCost.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Overhead Allocation (15%):</span>
                <span className="font-medium">${(totalCost * 0.15).toFixed(2)}</span>
              </div>
              <Separator />
              <div className="flex justify-between text-lg font-bold">
                <span>Total Estimated Cost:</span>
                <span className="text-blue-600">${(totalCost * 1.15).toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 justify-end pt-4">
            <Button variant="outline">
              Cancel
            </Button>
            <Button variant="outline">
              <Save className="w-4 h-4 mr-2" />
              Save Draft
            </Button>
            <Button>
              <Send className="w-4 h-4 mr-2" />
              Submit for Approval
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
