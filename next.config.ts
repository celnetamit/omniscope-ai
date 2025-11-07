import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  reactStrictMode: true,
  eslint: {
    ignoreDuringBuilds: true,
  },
  output: 'standalone',
  serverExternalPackages: ['@prisma/client'],
  images: {
    domains: ['omini.panoptical.org', 'bepy.panoptical.org'],
  },
};

export default nextConfig;
