/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        syra: {
          bg: "#FFF7FB",
          sidebar: "#FCEEF5",
          primary: "#E879A9",
          primaryHover: "#D66395",
          lavender: "#A78BFA",
          lavenderHover: "#906EE8",
          text: "#302536",
          muted: "#887887",
          border: "#F1DCE8",
          card: "#FFFFFF",
          cardHover: "#FAF3F7"
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
