import { Metadata } from 'next'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import DashboardLayout from '@/components/dashboard/DashboardLayout'
import SessionsOverview from '@/components/dashboard/SessionsOverview'
import HeatmapViewer from '@/components/dashboard/HeatmapViewer'
import PathAnalysis from '@/components/dashboard/PathAnalysis'
import FunnelAnalysis from '@/components/dashboard/FunnelAnalysis'

export const metadata: Metadata = {
  title: 'Dashboard | Mouse Tracking Analysis',
  description: 'Analytics dashboard for mouse behavior tracking data',
}

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="p-6">
        <h1 className="text-3xl font-bold mb-6">Analytics Dashboard</h1>
        
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="heatmaps">Heatmaps</TabsTrigger>
            <TabsTrigger value="paths">Path Analysis</TabsTrigger>
            <TabsTrigger value="funnels">Funnel Analysis</TabsTrigger>
          </TabsList>
          
          <TabsContent value="overview" className="mt-6">
            <SessionsOverview />
          </TabsContent>
          
          <TabsContent value="heatmaps" className="mt-6">
            <HeatmapViewer />
          </TabsContent>
          
          <TabsContent value="paths" className="mt-6">
            <PathAnalysis />
          </TabsContent>
          
          <TabsContent value="funnels" className="mt-6">
            <FunnelAnalysis />
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
} 