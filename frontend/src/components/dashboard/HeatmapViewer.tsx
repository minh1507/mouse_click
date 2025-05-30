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

// Sample heatmap data (in a real app, this would come from an API)
const sampleHeatmaps = [
  { id: 1, name: 'Homepage Click Heatmap', type: 'click', url: '/', createdAt: '2023-05-10' },
  { id: 2, name: 'Product Page Click Heatmap', type: 'click', url: '/products', createdAt: '2023-05-09' },
  { id: 3, name: 'Homepage Movement Heatmap', type: 'move', url: '/', createdAt: '2023-05-08' },
];

export default function HeatmapViewer() {
  const [selectedHeatmap, setSelectedHeatmap] = useState<number | null>(null);
  
  // Mock heatmap data generation (this would be real data in production)
  const generateMockHeatmapData = (width: number, height: number) => {
    const gridSize = 10;
    const cols = Math.floor(width / gridSize);
    const rows = Math.floor(height / gridSize);
    
    // Create a grid with random values
    const grid = Array(rows).fill(0).map(() => 
      Array(cols).fill(0).map(() => Math.floor(Math.random() * 20))
    );
    
    return { grid, gridSize, cols, rows };
  };
  
  const renderHeatmap = () => {
    if (!selectedHeatmap) return null;
    
    const width = 800;
    const height = 600;
    const { grid, gridSize, cols, rows } = generateMockHeatmapData(width, height);
    
    // Find max value for color scaling
    const maxValue = Math.max(...grid.flatMap(row => row));
    
    return (
      <div className="mt-4">
        <div className="bg-white rounded-md p-4 overflow-auto">
          <div 
            className="relative border border-gray-200"
            style={{ width: `${width}px`, height: `${height}px` }}
          >
            {grid.map((row, rowIndex) => 
              row.map((value, colIndex) => {
                // Calculate opacity based on value
                const opacity = value / maxValue;
                
                return (
                  <div
                    key={`${rowIndex}-${colIndex}`}
                    style={{
                      position: 'absolute',
                      left: colIndex * gridSize,
                      top: rowIndex * gridSize,
                      width: `${gridSize}px`,
                      height: `${gridSize}px`,
                      backgroundColor: 'red',
                      opacity: opacity,
                    }}
                  />
                );
              })
            )}
          </div>
        </div>
        
        <div className="mt-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-4 w-20 bg-gradient-to-r from-transparent to-red-500"></div>
            <span className="text-sm">Intensity</span>
          </div>
          <Button onClick={() => setSelectedHeatmap(null)}>
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
          <CardTitle>Heatmap Analysis</CardTitle>
          <CardDescription>
            Visualize user interaction patterns with heatmaps
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!selectedHeatmap ? (
            <>
              <div className="mb-6 flex items-end gap-4">
                <div className="grid w-full max-w-sm items-center gap-1.5">
                  <Label htmlFor="heatmap-search">Search Heatmaps</Label>
                  <Input 
                    id="heatmap-search" 
                    placeholder="Search by name or URL..." 
                  />
                </div>
                <Button>Create New Heatmap</Button>
              </div>
              
              <div className="space-y-4">
                {sampleHeatmaps.map((heatmap) => (
                  <div 
                    key={heatmap.id}
                    className="flex items-center justify-between p-4 rounded-md border border-border hover:bg-secondary cursor-pointer"
                    onClick={() => setSelectedHeatmap(heatmap.id)}
                  >
                    <div>
                      <h3 className="font-medium">{heatmap.name}</h3>
                      <div className="text-sm text-muted-foreground">
                        URL: {heatmap.url} · Type: {heatmap.type} · Created: {heatmap.createdAt}
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
            renderHeatmap()
          )}
        </CardContent>
      </Card>
    </div>
  );
} 