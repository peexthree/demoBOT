/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'eidos-bg': '#020304',
        'eidos-surface': '#0a0d14',
        'eidos-cyan': '#66FCF1',
        'eidos-cyan-dim': 'rgba(102, 252, 241, 0.2)',
        'eidos-gray': '#45A29E',
        'eidos-text': '#C5C6C7',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      backgroundImage: {
        'cyber-gradient': 'linear-gradient(135deg, #0a0d14 0%, #020304 100%)',
      },
      animation: {
        'glitch': 'glitch 1s linear infinite',
        'scanline': 'scanline 2s linear infinite',
      },
      keyframes: {
        glitch: {
          '2%, 64%': { transform: 'translate(2px,0) skew(0deg)' },
          '4%, 60%': { transform: 'translate(-2px,0) skew(0deg)' },
          '62%': { transform: 'translate(0,0) skew(5deg)' },
        },
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        }
      }
    },
  },
  plugins: [],
}
