/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#5F2CFF',
          50: '#F0EBFF',
          100: '#DDD0FF',
          200: '#B89BFF',
          300: '#9466FF',
          400: '#7949FF',
          500: '#5F2CFF',
          600: '#4A10F0',
          700: '#3A0CC0',
          800: '#2A0890',
          900: '#1A0560',
        },
        accent: {
          DEFAULT: '#02F576',
          50: '#E6FFF2',
          500: '#02F576',
          600: '#02C55E',
        },
        sidebar: {
          DEFAULT: '#1E2345',
          text: '#A0AEC0',
        },
        content: {
          bg: '#F7F8FC',
        },
        error: '#E53E3E',
        warning: '#DD6B20',
        success: '#38A169',
      },
      fontFamily: {
        montserrat: ['Montserrat', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
