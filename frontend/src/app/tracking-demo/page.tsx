import { Metadata } from 'next'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import TrackerInitializer from '@/components/tracking/TrackerInitializer'

export const metadata: Metadata = {
  title: 'Tracking Demo | Mouse Tracking Analysis',
  description: 'Demo page to showcase mouse behavior tracking capabilities',
}

export default function TrackingDemoPage() {
  return (
    <>
      <TrackerInitializer />
      <main className="flex min-h-screen flex-col p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Tracking Demo</h1>
          <p className="text-muted-foreground max-w-2xl">
            This page demonstrates mouse tracking capabilities. As you interact with elements 
            on this page, your mouse movements, clicks, and other interactions are being tracked.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          <Card>
            <CardHeader>
              <CardTitle>Interactive Form</CardTitle>
              <CardDescription>Fill out this form to see tracking in action</CardDescription>
            </CardHeader>
            <CardContent>
              <form className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input id="name" placeholder="Your name" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" placeholder="Your email" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="message">Message</Label>
                  <textarea 
                    id="message" 
                    className="min-h-[100px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                    placeholder="Your message"
                  />
                </div>
              </form>
            </CardContent>
            <CardFooter>
              <Button className="w-full">Submit Form</Button>
            </CardFooter>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Interactive Elements</CardTitle>
              <CardDescription>Click on these elements to generate tracking events</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-4">
                <Button variant="default">Primary Button</Button>
                <Button variant="secondary">Secondary Button</Button>
                <Button variant="outline">Outline Button</Button>
                <Button variant="destructive">Destructive Button</Button>
              </div>
              <div className="flex flex-col gap-2">
                <div className="flex items-center gap-2">
                  <input type="checkbox" id="checkbox1" className="h-4 w-4" />
                  <Label htmlFor="checkbox1">Checkbox Option 1</Label>
                </div>
                <div className="flex items-center gap-2">
                  <input type="checkbox" id="checkbox2" className="h-4 w-4" />
                  <Label htmlFor="checkbox2">Checkbox Option 2</Label>
                </div>
                <div className="flex items-center gap-2">
                  <input type="radio" name="radio" id="radio1" className="h-4 w-4" />
                  <Label htmlFor="radio1">Radio Option 1</Label>
                </div>
                <div className="flex items-center gap-2">
                  <input type="radio" name="radio" id="radio2" className="h-4 w-4" />
                  <Label htmlFor="radio2">Radio Option 2</Label>
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Link href="/tracking-demo/page2" className="w-full">
                <Button variant="outline" className="w-full">Go to Next Page</Button>
              </Link>
            </CardFooter>
          </Card>
        </div>
        
        <div className="w-full max-w-5xl mx-auto bg-secondary p-8 rounded-lg mb-12">
          <h2 className="text-2xl font-bold mb-4">Interactive Area</h2>
          <p className="mb-4">
            Move your mouse around this area to generate mouse movement tracking data.
            Click anywhere in this area to generate click tracking data.
          </p>
          <div className="h-64 bg-card rounded-lg flex items-center justify-center border-2 border-dashed border-muted-foreground">
            <p className="text-muted-foreground">Click or move in this area</p>
          </div>
        </div>
        
        <div className="text-center">
          <Link href="/dashboard">
            <Button size="lg">View Tracking Data in Dashboard</Button>
          </Link>
        </div>
      </main>
    </>
  )
} 