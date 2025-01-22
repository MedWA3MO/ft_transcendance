/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  async rewrites() {
    return [
      {
        source: '/backend/:path*',
        destination: 'https://ft-transcendance-wjhi.onrender.com/:path*',
      },
    ];
  },
};

export default nextConfig;