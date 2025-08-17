/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/*.html',
    './apps/**/*.py',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#e14eca',
        info: '#1d8cf8',
        success: '#00f2c3',
        danger: '#fd5d93',
        warning: '#ff8d72',
        bg: {
          DEFAULT: '#0b0d13',
          muted: '#131722',
        },
      },
      fontFamily: {
        sans: ['Poppins', 'ui-sans-serif', 'system-ui', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 10px 30px rgba(0,0,0,0.25)',
      },
      backgroundImage: {
        'hero-gradient': 'linear-gradient(135deg, #ec4899 0%, #8b5cf6 50%, #4f46e5 100%)',
      },
    },
  },
  plugins: [],
};
