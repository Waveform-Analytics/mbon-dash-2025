import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable strict mode for better development experience
  reactStrictMode: true,
  
  // Enable image optimization for external sources if needed
  images: {
    domains: [],
  },
};

export default nextConfig;
