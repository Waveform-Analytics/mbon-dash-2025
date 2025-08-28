/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    optimizePackageImports: ['@observablehq/plot', 'd3']
  },
  poweredByHeader: false,
  reactStrictMode: true,
  
  // Development proxy to bypass CORS
  async rewrites() {
    // Only proxy in development
    if (process.env.NODE_ENV !== 'development') {
      return [];
    }
    
    return [
      {
        source: '/api/cdn/:path*',
        destination: 'https://pub-71436b8d94864ba1ace2ef29fa28f0f1.r2.dev/:path*',
      },
    ]
  },
  
  // Security headers configuration
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin'
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=(self)'
          },
          {
            key: 'Content-Security-Policy',
            value: `
              default-src 'self';
              script-src 'self' 'unsafe-eval' 'unsafe-inline' https://api.mapbox.com;
              style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://api.mapbox.com;
              font-src 'self' data: https://fonts.gstatic.com;
              img-src 'self' data: blob: https://*.mapbox.com https://*.r2.dev;
              connect-src 'self' https://*.mapbox.com https://*.r2.dev https://api.mapbox.com https://waveformdata.work;
              worker-src 'self' blob:;
              frame-src 'none';
              object-src 'none';
              base-uri 'self';
              form-action 'self';
              frame-ancestors 'none';
              upgrade-insecure-requests;
            `.replace(/\s+/g, ' ').trim()
          }
        ]
      }
    ]
  },
  
  webpack: (config) => {
    // Ensure CSS is properly processed
    const rules = config.module.rules
      .find((rule) => typeof rule.oneOf === 'object')
      .oneOf.filter((rule) => Array.isArray(rule.use));
    
    if (rules) {
      rules.forEach((rule) => {
        rule.use.forEach((moduleLoader) => {
          if (
            moduleLoader.loader?.includes('css-loader') &&
            !moduleLoader.loader?.includes('postcss-loader')
          ) {
            moduleLoader.options.importLoaders = 1;
          }
        });
      });
    }
    
    return config
  }
}

module.exports = nextConfig