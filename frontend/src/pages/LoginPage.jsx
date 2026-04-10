import { useState, useContext } from "react";
import { login, verifyOtp } from "../services/auth";
import { ThemeContext } from "../context/ThemeContext";

function formatApiError(err, fallback) {
  const detail = err?.response?.data?.detail;

  if (!detail) {
    return fallback;
  }

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }
        if (item?.msg) {
          return item.msg;
        }
        return "Validation error";
      })
      .join(" | ");
  }

  if (typeof detail === "object" && detail.msg) {
    return detail.msg;
  }

  return fallback;
}

function LoginPage({ onAuthenticated }) {
  const { isDark, toggleTheme } = useContext(ThemeContext);
  const [email, setEmail] = useState("abhinav5911thakur@gmail.com");
  const [password, setPassword] = useState("Abhinav@1606");
  const [otp, setOtp] = useState("");
  const [otpRequired, setOtpRequired] = useState(false);
  const [error, setError] = useState("");

  const onLogin = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await login(email, password);
      if (!res.otp_required) {
        onAuthenticated(res.message);
      } else {
        setOtpRequired(true);
      }
    } catch (err) {
      setError(formatApiError(err, "Login failed"));
    }
  };

  const onVerifyOtp = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await verifyOtp(email, otp);
      onAuthenticated(res.access_token);
    } catch (err) {
      setError(formatApiError(err, "OTP verification failed"));
    }
  };

  return (
    <main className="relative min-h-screen overflow-hidden bg-canvas px-5 py-10 dark:text-white light:text-slate-900 transition-colors duration-300">
      <div className="absolute top-4 right-4">
        <button
          onClick={toggleTheme}
          className="rounded-lg border dark:border-slate-600 light:border-slate-400 px-3 py-2 text-lg transition-transform-shadow hover:-translate-y-1 hover:shadow-hover-dark dark:hover:shadow-hover-dark light:hover:shadow-hover-light"
          title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
        >
          {isDark ? "☀️" : "🌙"}
        </button>
      </div>

      <div className="pointer-events-none absolute -left-16 top-8 h-52 w-52 rounded-full dark:bg-accent/25 light:bg-accent/15 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-72 w-72 rounded-full dark:bg-info/20 light:bg-info/15 blur-3xl" />

      <section className="mx-auto max-w-md rounded-3xl border dark:border-slate-700/80 light:border-slate-300/80 dark:bg-panel/85 light:bg-white/85 p-8 dark:shadow-glow light:shadow-glow-light backdrop-blur transition-all duration-300 hover:shadow-hover-dark dark:hover:shadow-hover-dark light:hover:shadow-hover-light">
        <p className="font-mono text-xs uppercase tracking-[0.35em] text-accent">CAFW Console</p>
        <h1 className="mt-3 font-display text-3xl font-bold">Real-time Web Attack Defense</h1>

        {!otpRequired ? (
          <form className="mt-7 space-y-4" onSubmit={onLogin}>
            <input
              className="w-full rounded-xl border dark:border-slate-600 light:border-slate-300 dark:bg-slate-950/60 light:bg-slate-50/60 px-4 py-3 dark:text-white light:text-slate-900 dark:placeholder-slate-400 light:placeholder-slate-500 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-accent"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <input
              className="w-full rounded-xl border dark:border-slate-600 light:border-slate-300 dark:bg-slate-950/60 light:bg-slate-50/60 px-4 py-3 dark:text-white light:text-slate-900 dark:placeholder-slate-400 light:placeholder-slate-500 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-accent"
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button className="w-full rounded-xl bg-accent px-4 py-3 font-display font-bold dark:text-slate-950 light:text-slate-900 transition-transform-shadow hover:-translate-y-1 hover:shadow-hover-dark active:translate-y-0">
              Enter Dashboard
            </button>
          </form>
        ) : (
          <form className="mt-7 space-y-4" onSubmit={onVerifyOtp}>
            <p className="text-sm dark:text-slate-300 light:text-slate-600">OTP has been sent to your email. Enter it below.</p>
            <input
              className="w-full rounded-xl border dark:border-slate-600 light:border-slate-300 dark:bg-slate-950/60 light:bg-slate-50/60 px-4 py-3 font-mono dark:text-white light:text-slate-900 dark:placeholder-slate-400 light:placeholder-slate-500 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-accent"
              placeholder="6-digit OTP"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
            />
            <button className="w-full rounded-xl bg-info px-4 py-3 font-display font-bold dark:text-slate-950 light:text-slate-900 transition-transform-shadow hover:-translate-y-1 hover:shadow-hover-dark active:translate-y-0">
              Verify OTP
            </button>
          </form>
        )}

        {error && <p className="mt-4 text-sm text-alert">{error}</p>}
      </section>
    </main>
  );
}

export default LoginPage;
