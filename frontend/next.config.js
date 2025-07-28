/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable static export for Render static site deployment
  output: 'export',
  
  // Disable image optimization for static export
  images: {
    unoptimized: true
  },
  
  // Trailing slash for better static hosting
  trailingSlash: true,
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'https://budulgpt-backend.onrender.com',
    NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME || 'BudulGPT',
    NEXT_PUBLIC_APP_DESCRIPTION: process.env.NEXT_PUBLIC_APP_DESCRIPTION || 'The OpenAI for the Islamic World'
  }
}

module.exports = nextConfig