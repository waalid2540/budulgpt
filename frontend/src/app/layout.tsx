import type { Metadata } from 'next'
import { Inter, Amiri } from 'next/font/google'
import './globals.css'

// Enterprise imports
import { ThemeProvider } from 'next-themes'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const amiri = Amiri({ 
  subsets: ['arabic', 'latin'], 
  weight: ['400', '700'],
  variable: '--font-amiri'
})

export const metadata: Metadata = {
  title: 'Budul AI - The OpenAI for the Islamic World',
  description: 'Islamic artificial intelligence that serves the Muslim community with authentic, scholar-verified knowledge and creative tools. Built on the foundation of Islamic wisdom.',
  keywords: ['Islamic AI', 'Budul AI', 'Islamic GPT', 'Halal AI', 'Muslim AI', 'Islamic Technology', 'Quran AI', 'Hadith AI'],
  authors: [{ name: 'Budul AI Team' }],
  openGraph: {
    title: 'Budul AI - The OpenAI for the Islamic World',
    description: 'Islamic artificial intelligence serving 1.8 billion Muslims worldwide with authentic, scholar-verified knowledge.',
    url: 'https://budulai.com',
    siteName: 'Budul AI',
    images: [
      {
        url: 'https://budulai.com/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Budul AI - Islamic Artificial Intelligence Platform',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Budul AI - The OpenAI for the Islamic World',
    description: 'Islamic artificial intelligence serving 1.8 billion Muslims worldwide.',
    images: ['https://budulai.com/og-image.jpg'],
    creator: '@BudulAI',
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
        <meta name="theme-color" content="#0d4f3c" />
        
        {/* Structured Data for Islamic AI Platform */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "SoftwareApplication",
              "name": "Budul AI",
              "description": "Islamic artificial intelligence platform serving the Muslim community with authentic, scholar-verified knowledge and creative tools.",
              "url": "https://budulai.com",
              "applicationCategory": "BusinessApplication",
              "operatingSystem": "Web",
              "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD",
                "priceValidUntil": "2025-12-31"
              },
              "creator": {
                "@type": "Organization",
                "name": "Budul AI",
                "url": "https://budulai.com",
                "sameAs": [
                  "https://twitter.com/BudulAI",
                  "https://github.com/budul-ai"
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
      <body className={`${inter.className} bg-islamic-gradient min-h-screen`}>
        <ThemeProvider attribute="class" defaultTheme="light">
          <div className="flex flex-col min-h-screen">
            <main className="flex-1">
              {children}
            </main>
          </div>
        </ThemeProvider>
        
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
