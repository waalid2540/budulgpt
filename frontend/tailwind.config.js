/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        arabic: ['var(--font-amiri)', 'serif'],
        amiri: ['var(--font-amiri)', 'serif'],
      },
      colors: {
        'islamic-green': {
          50: '#f0f9f5',
          100: '#dcf2e7',
          200: '#bbe5d1',
          300: '#8bd4b2',
          400: '#52bf8e',
          500: '#2da76f',
          600: '#1e8a5a',
          700: '#196f4a',
          800: '#17593d',
          900: '#0d4f3c',
        },
        'islamic-gold': {
          50: '#fdfcf0',
          100: '#faf7dc',
          200: '#f5eeb8',
          300: '#ede089',
          400: '#e3cd58',
          500: '#d4b943',
          600: '#c9b037',
          700: '#a8912f',
          800: '#8a762a',
          900: '#756427',
        },
      },
      backgroundImage: {
        'islamic-gradient': 'linear-gradient(135deg, #f0f9f5 0%, #ffffff 50%, #fdfcf0 100%)',
        'islamic-gradient-dark': 'linear-gradient(135deg, #17593d 0%, #0d4f3c 100%)',
        'islamic-pattern': `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%230d4f3c' fill-opacity='0.03'%3E%3Cpath d='M30 30l15-15v10l5-5v10l-10-10v5l-10-10z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
      },
      boxShadow: {
        'islamic': '0 4px 6px -1px rgba(13, 79, 60, 0.1), 0 2px 4px -1px rgba(13, 79, 60, 0.06)',
        'islamic-lg': '0 10px 15px -3px rgba(13, 79, 60, 0.1), 0 4px 6px -2px rgba(13, 79, 60, 0.05)',
        'islamic-xl': '0 20px 25px -5px rgba(13, 79, 60, 0.1), 0 10px 10px -5px rgba(13, 79, 60, 0.04)',
      },
      animation: {
        'fade-in': 'fadeIn 0.6s ease-out forwards',
        'slide-up': 'slideUp 0.6s ease-out forwards',
        'scale-in': 'scaleIn 0.4s ease-out forwards',
        'spin-islamic': 'spinIslamic 1s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(40px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.9)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        spinIslamic: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
      },
      screens: {
        'xs': '475px',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      borderRadius: {
        '4xl': '2rem',
        '5xl': '2.5rem',
      },
      maxWidth: {
        '8xl': '88rem',
        '9xl': '96rem',
      },
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '0.75rem' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
        '7xl': ['4.5rem', { lineHeight: '1' }],
        '8xl': ['6rem', { lineHeight: '1' }],
        '9xl': ['8rem', { lineHeight: '1' }],
      },
      letterSpacing: {
        'tighter': '-0.05em',
        'wider': '0.05em',
        'widest': '0.1em',
      },
      lineHeight: {
        '3': '.75rem',
        '4': '1rem',
        '11': '2.75rem',
        '12': '3rem',
        '13': '3.25rem',
        '14': '3.5rem',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/aspect-ratio'),
  ],
}