import './globals.css';
import {Inter} from 'next/font/google';
import Header from '@/components/header/Header';

const inter = Inter({subsets: ['latin']});

export default function RootLayout({
                                       children,
                                   }: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
        <body className={`${inter.className} flex flex-col min-h-screen m-0`}>
        <Header/>

        <main className="flex-1">{children}</main>
        </body>
        </html>
    );
}
