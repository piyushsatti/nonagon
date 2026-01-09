import React, { useEffect, useState } from "react";
import { Link, useParams, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Header() {
  const { id: guildId } = useParams();
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();
  const [theme, setTheme] = useState(
    typeof document !== "undefined"
      ? document.documentElement.dataset.theme || "light"
      : "light"
  );

  const navItems = [
    { path: `/guild/${guildId}`, label: "Dashboard", icon: "📊" },
    { path: `/guild/${guildId}/quests`, label: "Quests", icon: "⚔️" },
    { path: `/guild/${guildId}/summaries`, label: "Summaries", icon: "📜" },
    { path: `/guild/${guildId}/characters`, label: "Characters", icon: "🧙" },
    { path: `/guild/${guildId}/stats`, label: "Stats", icon: "📈" },
  ];

  const isActive = (path) => {
    if (path === `/guild/${guildId}`) {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  const handleLogout = () => {
    logout();
  };

  const handleToggleTheme = () => {
    const next =
      typeof window !== "undefined" && typeof window.__toggleTheme === "function"
        ? window.__toggleTheme()
        : theme === "dark"
        ? "light"
        : "dark";
    if (typeof document !== "undefined") {
      document.documentElement.dataset.theme = next;
      localStorage.setItem("theme", next);
    }
    setTheme(next);
  };

  useEffect(() => {
    const current =
      typeof document !== "undefined"
        ? document.documentElement.dataset.theme || "light"
        : "light";
    setTheme(current);
  }, []);

  return (
    <header className="bg-[color:var(--note-bg)]/85 border-b border-[color:var(--note-border)] sticky top-0 z-50 backdrop-blur-md shadow-sm transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo / Brand */}
          <div className="flex items-center gap-4">
            <Link
              to="/"
              className="flex items-center gap-2 hover:opacity-80 transition"
            >
              <div className="w-10 h-10 bg-gradient-to-br from-[color:var(--accent)] to-[color:var(--accent-2)] rounded-lg flex items-center justify-center shadow-pin text-[color:var(--note-bg)]">
                <span className="font-display font-bold text-base">N</span>
              </div>
              <span className="font-display font-semibold text-[color:var(--board-ink)] text-lg sm:text-xl hidden sm:block tracking-wide">
                Nonagon
              </span>
            </Link>

            {guildId && (
              <div className="hidden md:flex items-center gap-1 text-sm text-[color:var(--board-ink)]/80">
                <span>/</span>
                <span className="text-[color:var(--board-ink)] font-medium">
                  {guildId === "demo" ? "Demo Guild" : `Guild ${guildId}`}
                </span>
              </div>
            )}
          </div>

          {/* Navigation */}
          {guildId && (
            <nav className="flex items-center gap-1">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-3 py-2 rounded-lg text-base font-medium transition border border-transparent ${
                    isActive(item.path)
                      ? "bg-[color:var(--accent-2)]/15 text-[color:var(--board-ink)] border-[color:var(--accent-2)]/30 shadow-[0_4px_10px_rgba(0,0,0,0.08)]"
                      : "text-[color:var(--board-ink)]/80 hover:text-[color:var(--board-ink)] hover:bg-[color:var(--note-bg)]/70"
                  }`}
                >
                  <span className="hidden sm:inline mr-1">{item.icon}</span>
                  <span className="hidden md:inline">{item.label}</span>
                  <span className="md:hidden">{item.icon}</span>
                </Link>
              ))}
            </nav>
          )}

          {/* Actions */}
          <div className="flex items-center gap-3">
            <button
              onClick={handleToggleTheme}
              className="px-3 py-1.5 text-sm font-medium rounded-lg border border-[color:var(--note-border)] bg-[color:var(--note-bg)]/70 text-[color:var(--board-ink)] hover:border-[color:var(--accent-2)]/60 hover:text-[color:var(--accent)] transition"
            >
              {theme === "dark" ? "Light Mode" : "Dark Mode"}
            </button>
            {guildId && (
              <Link
                to="/"
                className="text-sm text-[color:var(--board-ink)]/70 hover:text-[color:var(--board-ink)] transition"
              >
                Switch Guild
              </Link>
            )}

            {isAuthenticated ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[color:var(--accent)] to-[color:var(--accent-2)] flex items-center justify-center shadow-pin">
                    <span className="text-[color:var(--note-bg)] text-xs font-bold">
                      {user?.username?.charAt(0)?.toUpperCase() || "U"}
                    </span>
                  </div>
                  <span className="text-sm font-medium text-[color:var(--board-ink)] hidden sm:block">
                    {user?.username || "User"}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="text-sm text-[color:var(--board-ink)]/70 hover:text-[color:var(--board-ink)] transition"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="px-4 py-2 bg-[color:var(--accent)] text-[color:var(--note-bg)] text-sm font-medium rounded-lg shadow-pin hover:bg-[color:var(--accent)]/90 transition"
              >
                Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
