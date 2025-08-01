/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    optimizePackageImports: ['plotly.js']
  },
  poweredByHeader: false,
  reactStrictMode: true,
  webpack: (config) => {
    // Handle plotly.js
    config.resolve.alias = {
      ...config.resolve.alias,
      'plotly.js': 'plotly.js/dist/plotly.min.js'
    }
    
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