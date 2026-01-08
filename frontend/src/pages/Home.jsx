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
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gradient-to-b from-gray-50 to-gray-100">
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">Nonagon</h1>
        <p className="text-lg text-gray-600 max-w-md">
          Quest management system for Discord communities
        </p>
      </div>

      <div className="w-full max-w-md">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6 text-center">
            Enter Guild Dashboard
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label 
                htmlFor="guildId" 
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Guild ID
              </label>
              <input
                type="text"
                id="guildId"
                value={guildId}
                onChange={(e) => setGuildId(e.target.value)}
                placeholder="Enter your Discord guild ID"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
              />
              <p className="text-xs text-gray-500 mt-1">
                Your Discord server ID (e.g., 123456789012345678)
              </p>
            </div>
            
            <button
              type="submit"
              disabled={!guildId.trim()}
              className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              View Dashboard
            </button>
          </form>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">or</span>
            </div>
          </div>

          <button
            onClick={goToDemo}
            className="w-full py-3 bg-orange-100 text-orange-700 rounded-lg font-medium hover:bg-orange-200 transition"
          >
            View Demo Dashboard
          </button>
          <p className="text-xs text-gray-500 mt-2 text-center">
            See the dashboard with sample data
          </p>
        </div>
      </div>

      <footer className="mt-12 text-sm text-gray-500">
        <p>View quests, characters, users, and more from your Discord server.</p>
      </footer>
    </main>
  );
}
