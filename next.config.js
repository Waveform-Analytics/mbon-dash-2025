/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    optimizePackageImports: ['plotly.js']
  },
  webpack: (config) => {
    // Handle plotly.js
    config.resolve.alias = {
      ...config.resolve.alias,
      'plotly.js': 'plotly.js/dist/plotly.min.js'
    }
    return config
  }
}

module.exports = nextConfig