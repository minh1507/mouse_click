/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000/api/v1',
    NEXT_PUBLIC_TRACKER_API_ENDPOINT: process.env.NEXT_PUBLIC_TRACKER_API_ENDPOINT || 'http://backend:8000/api/v1/tracking/events',
    NEXT_PUBLIC_TRACKER_WS_ENDPOINT: process.env.NEXT_PUBLIC_TRACKER_WS_ENDPOINT || 'ws://backend:8000/ws/tracking'
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://backend:8000/api/:path*',
      },
      {
        source: '/api/v1/:path*',
        destination: 'http://backend:8000/api/v1/:path*',
      }
    ];
  },
}

module.exports = nextConfig 