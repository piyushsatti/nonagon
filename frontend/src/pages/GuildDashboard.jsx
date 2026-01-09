import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import {
  fetchAllLookups,
  fetchUsersByGuild,
  fetchRecentQuests,
  fetchCharactersByGuild,
  fetchSummariesByGuild,
  fetchActivityStats,
} from "../api/graphql";
import UserCard from "../components/UserCard";
import QuestCard from "../components/QuestCard";
import CharacterCard from "../components/CharacterCard";
import SummaryCard from "../components/SummaryCard";
import LookupCard from "../components/LookupCard";
import EmptyState from "../components/EmptyState";
import Loading from "../components/Loading";

function Section({ title, children, count, viewAllLink }) {
  return (
    <section className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold font-display text-[color:var(--board-ink)]">
          {title}
        </h2>
        <div className="flex items-center gap-3">
          <span className="text-sm text-[color:var(--board-ink)]/70">
            {count} items
          </span>
          {viewAllLink && (
            <Link
              to={viewAllLink}
              className="text-sm text-[color:var(--accent)] hover:text-[color:var(--accent-2)] font-medium"
            >
              View all →
            </Link>
          )}
        </div>
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
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);

      try {
        // Fetch all data from GraphQL API
        const [users, quests, characters, summaries, lookups, activityStats] =
          await Promise.all([
            fetchUsersByGuild(guildId),
            fetchRecentQuests(guildId, 20),
            fetchCharactersByGuild(guildId),
            fetchSummariesByGuild(guildId),
            fetchAllLookups(guildId),
            fetchActivityStats(guildId),
          ]);

        setData({
          users: users || [],
          quests: quests || [],
          characters: characters || [],
          summaries: summaries || [],
          lookups: lookups || [],
        });
        setStats(activityStats);
        setLoading(false);
      } catch (err) {
        console.error("Failed to fetch data:", err);
        setError(`Failed to load data: ${err.message}`);
        setLoading(false);
      }
    }

    loadData();
  }, [guildId]);

  if (loading) {
    return <Loading message="Loading guild data..." />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 text-[color:var(--board-ink)] transition-colors duration-200">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-display font-bold mb-2 drop-shadow-sm">
          Dashboard
        </h1>
        <p className="text-[color:var(--board-ink)]/80">
          Overview of your guild's activity
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-[color:var(--note-bg)]/80 border border-[color:var(--note-border)] rounded-lg shadow-parchment">
          <p className="text-[color:var(--accent)]">{error}</p>
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="parchment-card rounded-lg p-4">
          <div className="text-2xl font-bold">
            {stats?.totalQuests ?? data.quests.length}
          </div>
          <div className="text-sm text-[color:var(--board-ink)]/70">Quests</div>
        </div>
        <div className="parchment-card rounded-lg p-4">
          <div className="text-2xl font-bold">
            {stats?.totalCharacters ?? data.characters.length}
          </div>
          <div className="text-sm text-[color:var(--board-ink)]/70">
            Characters
          </div>
        </div>
        <div className="parchment-card rounded-lg p-4">
          <div className="text-2xl font-bold">
            {stats?.totalSummaries ?? data.summaries.length}
          </div>
          <div className="text-sm text-[color:var(--board-ink)]/70">
            Summaries
          </div>
        </div>
        <div className="parchment-card rounded-lg p-4">
          <div className="text-2xl font-bold">
            {stats?.activeUsers ?? data.users.length}
          </div>
          <div className="text-sm text-[color:var(--board-ink)]/70">
            Active Users
          </div>
        </div>
      </div>

      {/* Activity Stats */}
      {stats && (
        <div className="bg-gradient-to-r from-[color:var(--accent)] to-[color:var(--accent-2)] rounded-lg p-6 mb-8 text-[color:var(--note-bg)] shadow-parchment">
          <h2 className="text-xl font-bold mb-4 font-display">Guild Activity</h2>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <div className="text-3xl font-bold">
                {stats.totalMessages?.toLocaleString() ?? 0}
              </div>
              <div className="text-[color:var(--note-bg)]/80">
                Total Messages
              </div>
            </div>
            <div>
              <div className="text-3xl font-bold">
                {stats.totalReactions?.toLocaleString() ?? 0}
              </div>
              <div className="text-[color:var(--note-bg)]/80">
                Total Reactions
              </div>
            </div>
            <div>
              <div className="text-3xl font-bold">
                {Math.round(stats.totalVoiceHours ?? 0)}h
              </div>
              <div className="text-[color:var(--note-bg)]/80">Voice Time</div>
            </div>
          </div>
        </div>
      )}

      {/* Quests Section */}
      <Section
        title="Quests"
        count={data.quests.length}
        viewAllLink={`/guild/${guildId}/quests`}
      >
        {data.quests.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.quests.slice(0, 3).map((quest) => (
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
      <Section
        title="Characters"
        count={data.characters.length}
        viewAllLink={`/guild/${guildId}/characters`}
      >
        {data.characters.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.characters.slice(0, 4).map((character) => (
              <CharacterCard
                key={character.characterId}
                character={character}
              />
            ))}
          </div>
        ) : (
          <EmptyState
            title="No characters found"
            message="There are no characters in this guild yet."
          />
        )}
      </Section>

      {/* Summaries Section */}
      <Section
        title="Summaries"
        count={data.summaries.length}
        viewAllLink={`/guild/${guildId}/summaries`}
      >
        {data.summaries.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.summaries.slice(0, 4).map((summary) => (
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

      {/* Users Section */}
      <Section title="Users" count={data.users.length}>
        {data.users.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.users.slice(0, 6).map((user) => (
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

      {/* Lookups Section */}
      <Section title="Lookups" count={data.lookups.length}>
        {data.lookups.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.lookups.slice(0, 6).map((lookup) => (
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
    </div>
  );
}
