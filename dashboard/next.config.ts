import type { NextConfig } from "next";
import * as path from "path";
import * as dotenv from "dotenv";

// Load root-level .env.local file
dotenv.config({ path: path.resolve(__dirname, '../.env.local') });

const nextConfig: NextConfig = {
  // Enable strict mode for better development experience
  reactStrictMode: true,
  
  // Enable image optimization for external sources if needed
  images: {
    domains: [],
  },
};

export default nextConfig;
