import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Home() {
  const [guildId, setGuildId] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (guildId.trim()) {
      navigate(`/guild/${guildId.trim()}`);
    }
  };

  const goToDemo = () => {
    navigate('/guild/demo');
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-board text-ink board-surface transition-colors duration-200">
      <div className="text-center mb-12">
        <h1 className="text-5xl font-display font-bold mb-4 drop-shadow">
          Nonagon
        </h1>
        <p className="text-lg text-[color:var(--board-ink)]/80 max-w-md">
          Quest management system for Discord communities
        </p>
      </div>

      <div className="w-full max-w-md">
        <div className="parchment-card rounded-xl p-8 motion-safe:animate-pinIn">
          <h2 className="text-xl font-semibold mb-6 text-center font-display">
            Enter Guild Dashboard
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label 
                htmlFor="guildId" 
                className="block text-sm font-medium text-[color:var(--board-ink)]/80 mb-2"
              >
                Guild ID
              </label>
              <input
                type="text"
                id="guildId"
                value={guildId}
                onChange={(e) => setGuildId(e.target.value)}
                placeholder="Enter your Discord guild ID"
                className="w-full px-4 py-3 border border-[color:var(--note-border)] rounded-lg bg-[color:var(--note-bg)]/70 text-[color:var(--board-ink)] focus:ring-2 focus:ring-[color:var(--accent-2)] focus:border-[color:var(--accent-2)] transition-colors"
              />
              <p className="text-xs text-[color:var(--board-ink)]/70 mt-1">
                Your Discord server ID (e.g., 123456789012345678)
              </p>
            </div>
            
            <button
              type="submit"
              disabled={!guildId.trim()}
              className="w-full py-3 bg-[color:var(--accent)] text-[color:var(--note-bg)] rounded-lg font-semibold hover:bg-[color:var(--accent)]/90 disabled:bg-[color:var(--note-border)] disabled:text-[color:var(--board-ink)]/60 disabled:cursor-not-allowed transition-colors shadow-pin"
            >
              View Dashboard
            </button>
          </form>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[color:var(--note-border)]"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-[color:var(--note-bg)] text-[color:var(--board-ink)]/70">
                or
              </span>
            </div>
          </div>

          <button
            onClick={goToDemo}
            className="w-full py-3 bg-[color:var(--accent-2)]/20 text-[color:var(--accent)] rounded-lg font-semibold hover:bg-[color:var(--accent-2)]/30 transition-colors"
          >
            View Demo Dashboard
          </button>
          <p className="text-xs text-[color:var(--board-ink)]/70 mt-2 text-center">
            See the dashboard with sample data
          </p>
        </div>
      </div>

      <footer className="mt-12 text-sm text-[color:var(--board-ink)]/70">
        <p>View quests, characters, users, and more from your Discord server.</p>
      </footer>
    </main>
  );
}
