/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable static export for Render static site deployment
  output: 'export',
  
  // Disable image optimization for static export
  images: {
    unoptimized: true
  },
  
  // Base path for proper routing
  basePath: '',
  
  // Trailing slash for better static hosting
  trailingSlash: true,
  
  // Disable server-side features for static export
  experimental: {
    esmExternals: 'loose'
  }
}

module.exports = nextConfig