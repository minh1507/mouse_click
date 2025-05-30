'use client';

import React, { useState } from 'react';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Bar, 
  BarChart, 
  CartesianGrid, 
  Legend, 
  ResponsiveContainer, 
  Tooltip, 
  XAxis, 
  YAxis 
} from 'recharts';

// Sample funnel analysis data
const sampleFunnels = [
  { id: 1, name: 'Purchase Funnel', dateRange: 'May 1-15, 2023', createdAt: '2023-05-16', steps: 4 },
  { id: 2, name: 'Sign-up Funnel', dateRange: 'May 1-31, 2023', createdAt: '2023-06-01', steps: 3 },
  { id: 3, name: 'Content Engagement', dateRange: 'April 15-30, 2023', createdAt: '2023-05-01', steps: 5 },
];

// Sample funnel steps data
const sampleFunnelSteps = [
  { name: 'Visit Homepage', sessionsCount: 1000, conversionRate: 100, dropOffRate: 0 },
  { name: 'View Product', sessionsCount: 650, conversionRate: 65, dropOffRate: 35 },
  { name: 'Add to Cart', sessionsCount: 420, conversionRate: 64.6, dropOffRate: 35.4 },
  { name: 'Checkout', sessionsCount: 320, conversionRate: 76.2, dropOffRate: 23.8 },
  { name: 'Purchase Complete', sessionsCount: 250, conversionRate: 78.1, dropOffRate: 21.9 },
];

export default function FunnelAnalysis() {
  const [selectedFunnel, setSelectedFunnel] = useState<number | null>(null);
  
  const renderFunnelAnalysis = () => {
    if (!selectedFunnel) return null;
    
    // Create data for the funnel chart
    const chartData = sampleFunnelSteps.map(step => ({
      name: step.name,
      sessions: step.sessionsCount
    }));
    
    // Calculate completion rate
    const completionRate = sampleFunnelSteps[sampleFunnelSteps.length - 1].sessionsCount / 
                           sampleFunnelSteps[0].sessionsCount * 100;
    
    return (
      <div className="mt-4 space-y-6">
        <div className="flex justify-between mb-2">
          <h3 className="text-lg font-medium">Funnel Steps</h3>
          <div className="text-sm font-medium">
            Completion Rate: {completionRate.toFixed(1)}%
          </div>
        </div>
        
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="name" 
                angle={-45} 
                textAnchor="end" 
                height={70} 
              />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="sessions" fill="#8884d8" name="Sessions" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        <div className="space-y-4 mt-6">
          <h3 className="text-lg font-medium">Step Details</h3>
          
          {sampleFunnelSteps.map((step, index) => (
            <div 
              key={index} 
              className="border rounded-md p-4"
            >
              <div className="flex justify-between mb-2">
                <div className="font-medium">Step {index + 1}: {step.name}</div>
                <div className="text-sm">{step.sessionsCount} sessions</div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-muted-foreground mb-1">Conversion Rate</div>
                  <div className="flex items-center">
                    <div 
                      className="h-2 bg-green-500 rounded-full mr-2" 
                      style={{ width: `${step.conversionRate}%` }}
                    ></div>
                    <span className="text-sm">{step.conversionRate.toFixed(1)}%</span>
                  </div>
                </div>
                
                {index > 0 && (
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Drop-off Rate</div>
                    <div className="flex items-center">
                      <div 
                        className="h-2 bg-red-500 rounded-full mr-2" 
                        style={{ width: `${step.dropOffRate}%` }}
                      ></div>
                      <span className="text-sm">{step.dropOffRate.toFixed(1)}%</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
        
        <div className="flex justify-end">
          <Button onClick={() => setSelectedFunnel(null)}>
            Back to List
          </Button>
        </div>
      </div>
    );
  };
  
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Funnel Analysis</CardTitle>
          <CardDescription>
            Analyze user conversion through predefined funnels
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!selectedFunnel ? (
            <>
              <div className="mb-6 flex items-end gap-4">
                <div className="grid w-full max-w-sm items-center gap-1.5">
                  <Label htmlFor="funnel-search">Search Funnels</Label>
                  <Input 
                    id="funnel-search" 
                    placeholder="Search by name..." 
                  />
                </div>
                <Button>Create New Funnel</Button>
              </div>
              
              <div className="space-y-4">
                {sampleFunnels.map((funnel) => (
                  <div 
                    key={funnel.id}
                    className="flex items-center justify-between p-4 rounded-md border border-border hover:bg-secondary cursor-pointer"
                    onClick={() => setSelectedFunnel(funnel.id)}
                  >
                    <div>
                      <h3 className="font-medium">{funnel.name}</h3>
                      <div className="text-sm text-muted-foreground">
                        Date Range: {funnel.dateRange} · {funnel.steps} steps · Created: {funnel.createdAt}
                      </div>
                    </div>
                    <Button variant="outline" size="sm">
                      View
                    </Button>
                  </div>
                ))}
              </div>
            </>
          ) : (
            renderFunnelAnalysis()
          )}
        </CardContent>
      </Card>
    </div>
  );
} 