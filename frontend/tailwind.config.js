/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
      },
      colors: {
        canvas: "var(--canvas)",
        panel: "var(--panel)",
        accent: "#f97316",
        alert: "#ef4444",
        safe: "#22c55e",
        info: "#38bdf8",
      },
      boxShadow: {
        glow: "0 0 40px rgba(249, 115, 22, 0.25)",
        "glow-light": "0 0 20px rgba(249, 115, 22, 0.15)",
        "hover-dark": "0 12px 24px rgba(0, 0, 0, 0.4)",
        "hover-light": "0 8px 16px rgba(0, 0, 0, 0.1)",
      },
      keyframes: {
        floatIn: {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        floatIn: "floatIn 500ms ease forwards",
      },
      transitionProperty: {
        "transform-shadow": "transform, box-shadow, background-color",
      },
    },
  },
  plugins: [],
};
