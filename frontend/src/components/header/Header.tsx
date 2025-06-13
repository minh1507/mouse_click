'use client';

import {useRouter} from 'next/navigation';
import {Input} from '@/components/ui/input';
import {Button} from '@/components/ui/button';
import {ShoppingCart, User} from 'lucide-react';

export default function Header() {
    const router = useRouter();

    return (
        <header className="z-50 bg-white border-b shadow-sm">
            <section className="mx-auto max-w-screen-xl flex items-center justify-between px-4 lg:px-8 py-4">
                <section className="flex space-x-4">
                    <div
                        onClick={() => router.push('/')}
                        className="text-2xl font-bold text-orange-600 cursor-pointer"
                    >
                        K
                    </div>

                    {/* Navigation */}
                    <nav className="hidden sm:flex space-x-6 text-sm font-medium text-gray-700 items-center">
                        <button onClick={() => router.push('/')} className="hover:text-orange-600">
                            Trang chủ
                        </button>
                        <button onClick={() => router.push('/about')} className="hover:text-orange-600">
                            Giới thiệu
                        </button>
                    </nav>
                </section>

                <section className="flex items-center space-x-4">
                    <Input
                        placeholder="Tìm kiếm..."
                        className="w-[140px] sm:w-[180px] lg:w-[220px]"
                    />

                    <Button variant="ghost" size="icon" onClick={() => router.push('/cart')}>
                        <ShoppingCart className="h-5 w-5"/>
                    </Button>

                    <Button variant="ghost" size="icon" onClick={() => router.push('/account')}>
                        <User className="h-5 w-5"/>
                    </Button>
                </section>
            </section>
        </header>
    );
}
