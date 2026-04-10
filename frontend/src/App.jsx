import { useState } from "react";
import { ThemeProvider } from "./context/ThemeContext";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";

function App() {
  const [token, setToken] = useState(localStorage.getItem("cafw_token"));

  const handleAuthenticated = (newToken) => {
    localStorage.setItem("cafw_token", newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem("cafw_token");
    setToken(null);
  };

  if (!token) {
    return (
      <ThemeProvider>
        <LoginPage onAuthenticated={handleAuthenticated} />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider>
      <DashboardPage onLogout={handleLogout} />
    </ThemeProvider>
  );
}

export default App;
