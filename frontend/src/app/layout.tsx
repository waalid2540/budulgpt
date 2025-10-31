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
  title: 'MadinaGPT - Faith, Knowledge, and Guidance',
  description: 'MadinaGPT: Your Islamic AI companion for faith, knowledge, and guidance. Supporting Masjid Madina with authentic Islamic content, duas, and stories for the whole family.',
  keywords: ['MadinaGPT', 'Islamic AI', 'Madina GPT', 'Islamic ChatGPT', 'Muslim AI', 'Dua Generator', 'Islamic Stories', 'Umrah Alert', 'Masjid Madina'],
  authors: [{ name: 'MadinaGPT Team' }],
  openGraph: {
    title: 'MadinaGPT - Faith, Knowledge, and Guidance',
    description: 'Islamic AI platform supporting Masjid Madina. Chat with MadinaGPT, generate duas, create Islamic stories for kids, and more.',
    url: 'https://madinagpt.com',
    siteName: 'MadinaGPT',
    images: [
      {
        url: 'https://madinagpt.com/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'MadinaGPT - Islamic AI Platform Supporting Masjid Madina',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'MadinaGPT - Faith, Knowledge, and Guidance',
    description: 'Islamic AI platform supporting Masjid Madina with authentic Islamic content and tools.',
    images: ['https://madinagpt.com/og-image.jpg'],
    creator: '@MadinaGPT',
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

        {/* Structured Data for MadinaGPT - Islamic AI Platform */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "SoftwareApplication",
              "name": "MadinaGPT",
              "description": "MadinaGPT - Islamic AI platform supporting Masjid Madina. Faith, Knowledge, and Guidance for the Muslim community with authentic Islamic content.",
              "url": "https://madinagpt.com",
              "applicationCategory": "BusinessApplication",
              "operatingSystem": "Web",
              "offers": {
                "@type": "Offer",
                "price": "4.99",
                "priceCurrency": "USD",
                "priceValidUntil": "2026-12-31",
                "description": "Monthly unlimited subscription - 50% proceeds support Masjid Madina"
              },
              "creator": {
                "@type": "Organization",
                "name": "MadinaGPT",
                "url": "https://madinagpt.com",
                "sameAs": [
                  "https://twitter.com/MadinaGPT"
                ]
              },
              "audience": {
                "@type": "Audience",
                "audienceType": "Muslim Community",
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
