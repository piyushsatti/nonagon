const defaultTheme = require("tailwindcss/defaultTheme");

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,html}"],
  theme: {
    extend: {
      colors: {
        board: "var(--board-bg)",
        ink: "var(--board-ink)",
        note: "var(--note-bg)",
        "note-border": "var(--note-border)",
        accent: "var(--accent)",
        "accent-2": "var(--accent-2)",
      },
      fontFamily: {
        display: [
          '"Cinzel Decorative"',
          '"IM Fell English SC"',
          ...defaultTheme.fontFamily.serif,
        ],
        body: ['"Cormorant Garamond"', '"Source Serif 4"', ...defaultTheme.fontFamily.serif],
        sans: ['"Inter"', ...defaultTheme.fontFamily.sans],
      },
      boxShadow: {
        parchment: "0 12px 30px rgba(0,0,0,0.18), inset 0 1px 0 rgba(255,255,255,0.25)",
        "parchment-strong": "0 16px 36px rgba(0,0,0,0.24), inset 0 1px 0 rgba(255,255,255,0.28)",
        pin: "0 6px 14px rgba(0,0,0,0.35)",
      },
      keyframes: {
        flicker: {
          "0%, 100%": { opacity: 1, filter: "brightness(1)" },
          "40%": { opacity: 0.96, filter: "brightness(1.06)" },
          "55%": { opacity: 0.86, filter: "brightness(0.94)" },
          "70%": { opacity: 0.94, filter: "brightness(1.02)" },
        },
        paperFloat: {
          "0%, 100%": { transform: "translateY(0) rotate(0deg)" },
          "50%": { transform: "translateY(-4px) rotate(-0.4deg)" },
          "75%": { transform: "translateY(3px) rotate(0.35deg)" },
        },
        pinIn: {
          "0%": { opacity: 0, transform: "translateY(8px) scale(0.98)" },
          "100%": { opacity: 1, transform: "translateY(0) scale(1)" },
        },
        hoverLift: {
          from: { transform: "translateY(0) rotate(0deg)" },
          to: { transform: "translateY(-6px) rotate(-0.6deg)" },
        },
      },
      animation: {
        flicker: "flicker 4s ease-in-out infinite",
        paperFloat: "paperFloat 7s ease-in-out infinite",
        pinIn: "pinIn 0.85s ease-out both",
        hoverLift: "hoverLift 240ms ease-out forwards",
      },
    },
  },
  plugins: [],
};
