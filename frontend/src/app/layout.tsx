import type { Metadata } from 'next'
import { Inter, Amiri } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const amiri = Amiri({ 
  subsets: ['arabic', 'latin'], 
  weight: ['400', '700'],
  variable: '--font-amiri'
})

export const metadata: Metadata = {
  title: 'Global Waqaf Tech - Digital Waqf Network for Islamic Organizations',
  description: 'Global Waqaf Tech: Multi-tenant SaaS platform empowering masajid and Islamic organizations with AI-powered tools. 20% of proceeds support selected masajid worldwide.',
  keywords: ['Global Waqaf Tech', 'Islamic SaaS', 'Masjid Management', 'Islamic AI Tools', 'Waqf Technology', 'Dua Generator', 'Islamic Stories', 'Grant Finder', 'Learning Hub', 'Social Media Studio'],
  authors: [{ name: 'Global Waqaf Tech' }],
  openGraph: {
    title: 'Global Waqaf Tech - Empowering Islamic Organizations',
    description: 'Multi-tenant platform with 7 AI-powered modules for masajid and Islamic organizations. 20% of proceeds support selected masajid operations.',
    url: 'https://globalwaqaftech.com',
    siteName: 'Global Waqaf Tech',
    images: [
      {
        url: 'https://globalwaqaftech.com/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Global Waqaf Tech - Digital Waqf Network',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Global Waqaf Tech - Empowering Islamic Organizations',
    description: 'Multi-tenant SaaS platform with AI-powered tools for masajid worldwide. 20% supports selected masajid.',
    images: ['https://globalwaqaftech.com/og-image.jpg'],
    creator: '@GlobalWaqafTech',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${amiri.variable}`}>
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#059669" />

        {/* Structured Data for Global Waqaf Tech */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "SoftwareApplication",
              "name": "Global Waqaf Tech",
              "description": "Multi-tenant SaaS platform empowering masajid and Islamic organizations with 7 AI-powered modules. 20% of proceeds support selected masajid worldwide.",
              "url": "https://globalwaqaftech.com",
              "applicationCategory": "BusinessApplication",
              "operatingSystem": "Web",
              "offers": [
                {
                  "@type": "Offer",
                  "name": "Basic Plan",
                  "price": "0",
                  "priceCurrency": "USD",
                  "description": "Free plan with limited features"
                },
                {
                  "@type": "Offer",
                  "name": "Pro Plan",
                  "price": "29",
                  "priceCurrency": "USD",
                  "priceValidUntil": "2026-12-31",
                  "description": "Pro plan with advanced features - 20% supports selected masajid"
                },
                {
                  "@type": "Offer",
                  "name": "Enterprise Plan",
                  "price": "99",
                  "priceCurrency": "USD",
                  "priceValidUntil": "2026-12-31",
                  "description": "Enterprise plan with unlimited features - 20% supports selected masajid"
                }
              ],
              "creator": {
                "@type": "Organization",
                "name": "Global Waqaf Tech",
                "url": "https://globalwaqaftech.com",
                "sameAs": [
                  "https://twitter.com/GlobalWaqafTech"
                ]
              },
              "audience": {
                "@type": "Audience",
                "audienceType": "Islamic Organizations, Masajid, Schools, Businesses",
                "geographicArea": "Worldwide"
              }
            })
          }}
        />
      </head>
      <body className={`${inter.className} bg-madina-gradient min-h-screen`}>
        <div className="flex flex-col min-h-screen">
          <main className="flex-1">
            {children}
          </main>
        </div>
        
        {/* Analytics and Marketing Scripts */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              // Google Analytics
              (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
              (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
              m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
              })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
              ga('create', 'UA-XXXXXXXX-X', 'auto');
              ga('send', 'pageview');
            `
          }}
        />
      </body>
    </html>
  )
}
