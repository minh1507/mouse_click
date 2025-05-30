import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="mb-12 text-center">
        <h1 className="text-4xl font-bold mb-4">Mouse Tracking Analysis</h1>
        <p className="text-xl text-muted-foreground max-w-2xl">
          A comprehensive platform for tracking and analyzing user mouse behavior
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl w-full">
        <Card>
          <CardHeader>
            <CardTitle>Website Thu thập</CardTitle>
            <CardDescription>
              Tích hợp thư viện JavaScript tracker để thu thập dữ liệu hành vi người dùng
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p>
              Tích hợp dễ dàng với website của bạn thông qua đoạn mã JavaScript đơn giản. 
              Thu thập dữ liệu về các sự kiện mouse click, mouse move, scroll và nhiều hơn nữa.
            </p>
          </CardContent>
          <CardFooter>
            <Link href="/tracking-demo" className="w-full">
              <Button className="w-full">Xem Demo</Button>
            </Link>
          </CardFooter>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Website Admin</CardTitle>
            <CardDescription>
              Dashboard quản trị và phân tích dữ liệu
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p>
              Phân tích hành vi người dùng thông qua các biểu đồ heatmap, phân tích đường dẫn,
              phân tích phiên, và nhiều tính năng phân tích nâng cao khác.
            </p>
          </CardContent>
          <CardFooter>
            <Link href="/dashboard" className="w-full">
              <Button className="w-full">Đến Dashboard</Button>
            </Link>
          </CardFooter>
        </Card>
      </div>
    </main>
  )
} 