// app/about/page.tsx
'use client';

import {Info} from 'lucide-react';
import TrackerInitializer from "@/components/tracking/TrackerInitializer";

export default function About() {
    return (
        <section className="px-4 py-12 ">
            <TrackerInitializer/>
            <div className="flex justify-center mb-6">
                <Info className="w-10 h-10 text-orange-600"/>
            </div>

            <h1 className="text-4xl font-bold text-orange-600 mb-4 text-center mb-4">
                Phần mềm Mouse Tracking
            </h1>

            <p className="text-lg text-muted-foreground mb-6">
                Phần mềm Mouse Tracking giúp bạn theo dõi hành vi người dùng trên website: di chuyển chuột, click,
                scroll và tương tác tổng thể. Đây là công cụ lý tưởng để nghiên cứu trải nghiệm người dùng (UX) và tối
                ưu giao diện.
            </p>

            <ul className="text-left text-gray-700 list-disc list-inside mb-8 mx-auto space-y-2">
                <li>Thu thập dữ liệu chuột chi tiết (click, di chuyển, cuộn)</li>
                <li>Tích hợp đơn giản bằng đoạn mã JavaScript</li>
                <li>Dữ liệu được mã hóa và lưu trữ an toàn</li>
                <li>Phân tích qua dashboard trực quan (heatmap, biểu đồ, v.v.)</li>
            </ul>
        </section>
    );
}
