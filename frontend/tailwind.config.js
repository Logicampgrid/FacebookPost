/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        facebook: {
          primary: '#1877F2',
          secondary: '#42A5F5',
          light: '#E3F2FD',
          dark: '#0D47A1'
        },
        gray: {
          facebook: '#F0F2F5'
        }
      },
      fontFamily: {
        'facebook': ['Helvetica Neue', 'Helvetica', 'Arial', 'sans-serif']
      },
      boxShadow: {
        'facebook': '0 2px 4px rgba(0, 0, 0, .1), 0 8px 16px rgba(0, 0, 0, .1)'
      }
    },
  },
  plugins: [],
}