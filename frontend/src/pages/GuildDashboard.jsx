import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchAllLookups } from '../api/graphql';
import { getAllDummyData } from '../data/dummy';
import UserCard from '../components/UserCard';
import QuestCard from '../components/QuestCard';
import CharacterCard from '../components/CharacterCard';
import SummaryCard from '../components/SummaryCard';
import LookupCard from '../components/LookupCard';
import EmptyState from '../components/EmptyState';

function Section({ title, children, count }) {
  return (
    <section className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900">{title}</h2>
        <span className="text-sm text-gray-500">{count} items</span>
      </div>
      {children}
    </section>
  );
}

export default function GuildDashboard() {
  const { id: guildId } = useParams();
  
  const [data, setData] = useState({
    users: [],
    quests: [],
    characters: [],
    summaries: [],
    lookups: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [useDemo, setUseDemo] = useState(false);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);
      
      // Check if using demo mode
      if (guildId === 'demo') {
        setData(getAllDummyData());
        setUseDemo(true);
        setLoading(false);
        return;
      }
      
      try {
        // Try to fetch from GraphQL API
        const lookups = await fetchAllLookups(guildId);
        setData(prev => ({ ...prev, lookups: lookups || [] }));
        
        // Note: The GraphQL API doesn't have list queries for users, quests, characters, summaries
        // In a real app, you'd add those queries. For now, we show empty state for those.
        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch data:', err);
        setError(`Failed to load data: ${err.message}`);
        setLoading(false);
      }
    }
    
    loadData();
  }, [guildId]);

  const loadDemoData = () => {
    setData(getAllDummyData());
    setUseDemo(true);
    setError(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading guild data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <Link to="/" className="text-sm text-blue-600 hover:underline mb-1 block">
                ← Back to Home
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">
                Guild Dashboard
              </h1>
              <p className="text-sm text-gray-500">
                Guild ID: {guildId} {useDemo && <span className="text-orange-500">(Demo Data)</span>}
              </p>
            </div>
            {!useDemo && (
              <button
                onClick={loadDemoData}
                className="px-4 py-2 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition text-sm font-medium"
              >
                Load Demo Data
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
            <button
              onClick={loadDemoData}
              className="mt-2 text-sm text-red-600 hover:underline"
            >
              Load demo data instead
            </button>
          </div>
        )}

        {/* Quests Section */}
        <Section title="Quests" count={data.quests.length}>
          {data.quests.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.quests.map((quest) => (
                <QuestCard key={quest.questId} quest={quest} />
              ))}
            </div>
          ) : (
            <EmptyState 
              title="No quests found" 
              message="There are no quests in this guild yet." 
            />
          )}
        </Section>

        {/* Characters Section */}
        <Section title="Characters" count={data.characters.length}>
          {data.characters.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.characters.map((character) => (
                <CharacterCard key={character.characterId} character={character} />
              ))}
            </div>
          ) : (
            <EmptyState 
              title="No characters found" 
              message="There are no characters in this guild yet." 
            />
          )}
        </Section>

        {/* Users Section */}
        <Section title="Users" count={data.users.length}>
          {data.users.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.users.map((user) => (
                <UserCard key={user.userId} user={user} />
              ))}
            </div>
          ) : (
            <EmptyState 
              title="No users found" 
              message="There are no users in this guild yet." 
            />
          )}
        </Section>

        {/* Summaries Section */}
        <Section title="Summaries" count={data.summaries.length}>
          {data.summaries.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.summaries.map((summary) => (
                <SummaryCard key={summary.summaryId} summary={summary} />
              ))}
            </div>
          ) : (
            <EmptyState 
              title="No summaries found" 
              message="There are no summaries in this guild yet." 
            />
          )}
        </Section>

        {/* Lookups Section */}
        <Section title="Lookups" count={data.lookups.length}>
          {data.lookups.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.lookups.map((lookup) => (
                <LookupCard key={lookup.name} lookup={lookup} />
              ))}
            </div>
          ) : (
            <EmptyState 
              title="No lookups found" 
              message="There are no lookup entries in this guild yet." 
            />
          )}
        </Section>
      </main>
    </div>
  );
}
