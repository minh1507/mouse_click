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

// Sample path analysis data
const samplePathAnalyses = [
  { id: 1, name: 'Weekly Path Analysis', dateRange: 'May 1-7, 2023', createdAt: '2023-05-08' },
  { id: 2, name: 'Monthly Path Analysis', dateRange: 'April 2023', createdAt: '2023-05-01' },
  { id: 3, name: 'Checkout Funnel Paths', dateRange: 'May 1-14, 2023', createdAt: '2023-05-15' },
];

// Sample path data
const samplePathData = [
  { path: ['/', '/products', '/products/1', '/cart', '/checkout'], count: 156 },
  { path: ['/', '/about', '/contact'], count: 89 },
  { path: ['/', '/products', '/products/2', '/products/1', '/cart'], count: 72 },
  { path: ['/', '/products', '/cart', '/checkout', '/thank-you'], count: 65 },
  { path: ['/', '/login', '/dashboard'], count: 58 },
];

export default function PathAnalysis() {
  const [selectedAnalysis, setSelectedAnalysis] = useState<number | null>(null);
  
  const renderPathAnalysis = () => {
    if (!selectedAnalysis) return null;
    
    // Calculate total visits for percentage
    const totalVisits = samplePathData.reduce((sum, item) => sum + item.count, 0);
    
    return (
      <div className="mt-4 space-y-6">
        <div>
          <h3 className="text-lg font-medium mb-2">Top User Paths</h3>
          <div className="space-y-4">
            {samplePathData.map((item, index) => {
              const percentage = (item.count / totalVisits * 100).toFixed(1);
              
              return (
                <div key={index} className="border rounded-md p-4">
                  <div className="flex justify-between mb-2">
                    <div className="font-medium">Path #{index + 1}</div>
                    <div className="text-sm">{item.count} sessions ({percentage}%)</div>
                  </div>
                  <div className="flex items-center space-x-2 overflow-x-auto pb-2">
                    {item.path.map((step, stepIndex) => (
                      <React.Fragment key={stepIndex}>
                        {stepIndex > 0 && (
                          <div className="text-muted-foreground">→</div>
                        )}
                        <div className="px-3 py-1 bg-secondary rounded-md text-sm whitespace-nowrap">
                          {step}
                        </div>
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        
        <div className="flex justify-end">
          <Button onClick={() => setSelectedAnalysis(null)}>
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
          <CardTitle>Path Analysis</CardTitle>
          <CardDescription>
            Analyze user navigation paths across your site
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!selectedAnalysis ? (
            <>
              <div className="mb-6 flex items-end gap-4">
                <div className="grid w-full max-w-sm items-center gap-1.5">
                  <Label htmlFor="path-search">Search Analyses</Label>
                  <Input 
                    id="path-search" 
                    placeholder="Search by name..." 
                  />
                </div>
                <Button>Create New Analysis</Button>
              </div>
              
              <div className="space-y-4">
                {samplePathAnalyses.map((analysis) => (
                  <div 
                    key={analysis.id}
                    className="flex items-center justify-between p-4 rounded-md border border-border hover:bg-secondary cursor-pointer"
                    onClick={() => setSelectedAnalysis(analysis.id)}
                  >
                    <div>
                      <h3 className="font-medium">{analysis.name}</h3>
                      <div className="text-sm text-muted-foreground">
                        Date Range: {analysis.dateRange} · Created: {analysis.createdAt}
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
            renderPathAnalysis()
          )}
        </CardContent>
      </Card>
    </div>
  );
} 