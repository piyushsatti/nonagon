import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import InfiniteScroll from "react-infinite-scroll-component";
import { fetchCharactersByGuild } from "../api/graphql";
import CharacterCard from "../components/CharacterCard";
import EmptyState from "../components/EmptyState";
import Loading from "../components/Loading";

const ITEMS_PER_PAGE = 12;

export default function CharactersPage() {
  const { id: guildId } = useParams();

  const [allCharacters, setAllCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter state
  const [statusFilter, setStatusFilter] = useState("ALL"); // ALL, ACTIVE, INACTIVE
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("name"); // name, lastPlayed, questsPlayed

  // Pagination state
  const [displayedCharacters, setDisplayedCharacters] = useState([]);
  const [hasMore, setHasMore] = useState(true);

  // Filter and sort characters
  const filteredCharacters = React.useMemo(() => {
    let filtered = [...allCharacters];

    // Status filter
    if (statusFilter !== "ALL") {
      filtered = filtered.filter((c) => c.status === statusFilter);
    }

    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (c) =>
          c.name.toLowerCase().includes(query) ||
          c.description?.toLowerCase().includes(query) ||
          c.tags?.some((tag) => tag.toLowerCase().includes(query))
      );
    }

    // Sort
    switch (sortBy) {
      case "name":
        filtered.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case "lastPlayed":
        filtered.sort((a, b) => {
          if (!a.lastPlayedAt) return 1;
          if (!b.lastPlayedAt) return -1;
          return new Date(b.lastPlayedAt) - new Date(a.lastPlayedAt);
        });
        break;
      case "questsPlayed":
        filtered.sort((a, b) => (b.questsPlayed || 0) - (a.questsPlayed || 0));
        break;
      default:
        break;
    }

    return filtered;
  }, [allCharacters, statusFilter, searchQuery, sortBy]);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);

      try {
        const characters = await fetchCharactersByGuild(guildId);
        setAllCharacters(characters || []);
        setLoading(false);
      } catch (err) {
        console.error("Failed to fetch characters:", err);
        setError(`Failed to load characters: ${err.message}`);
        setLoading(false);
      }
    }

    loadData();
  }, [guildId]);

  // Initialize displayed characters when data or filters change
  useEffect(() => {
    if (filteredCharacters.length > 0) {
      setDisplayedCharacters(filteredCharacters.slice(0, ITEMS_PER_PAGE));
      setHasMore(filteredCharacters.length > ITEMS_PER_PAGE);
    } else {
      setDisplayedCharacters([]);
      setHasMore(false);
    }
  }, [filteredCharacters]);

  const fetchMoreCharacters = () => {
    const currentLength = displayedCharacters.length;
    const nextBatch = filteredCharacters.slice(
      currentLength,
      currentLength + ITEMS_PER_PAGE
    );

    setDisplayedCharacters((prev) => [...prev, ...nextBatch]);
    setHasMore(currentLength + nextBatch.length < filteredCharacters.length);
  };

  // Stats
  const activeCount = allCharacters.filter((c) => c.status === "ACTIVE").length;
  const inactiveCount = allCharacters.filter(
    (c) => c.status === "INACTIVE"
  ).length;

  if (loading) {
    return <Loading message="Loading characters..." />;
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8 text-[color:var(--board-ink)]">
        <div className="p-4 bg-[color:var(--note-bg)]/80 border border-[color:var(--note-border)] rounded-lg shadow-parchment">
          <p className="text-[color:var(--accent)]">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 text-[color:var(--board-ink)] transition-colors duration-200">
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-4xl font-display font-bold mb-2 drop-shadow-sm">
          Characters
        </h1>
        <p className="text-[color:var(--board-ink)]/80">
          Browse all characters registered in this guild.
        </p>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="parchment-card rounded-lg p-4">
          <div className="text-2xl font-bold">
            {allCharacters.length}
          </div>
          <div className="text-sm text-[color:var(--board-ink)]/70">
            Total Characters
          </div>
        </div>
        <div className="parchment-card rounded-lg p-4">
          <div className="text-2xl font-bold text-emerald-700">
            {activeCount}
          </div>
          <div className="text-sm text-[color:var(--board-ink)]/70">Active</div>
        </div>
        <div className="parchment-card rounded-lg p-4">
          <div className="text-2xl font-bold text-[color:var(--board-ink)]/60">
            {inactiveCount}
          </div>
          <div className="text-sm text-[color:var(--board-ink)]/70">
            Inactive
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-4 mb-6">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px] max-w-md">
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[color:var(--accent-2)]/70"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            type="text"
            placeholder="Search characters..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-[color:var(--note-border)] rounded-lg text-sm bg-[color:var(--note-bg)]/70 text-[color:var(--board-ink)] focus:outline-none focus:ring-2 focus:ring-[color:var(--accent-2)] focus:border-transparent transition-colors"
          />
        </div>

        {/* Status Filter */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-[color:var(--board-ink)]/80">
            Status:
          </span>
          <div className="flex rounded-lg border border-[color:var(--note-border)] overflow-hidden bg-[color:var(--note-bg)]/60">
            {["ALL", "ACTIVE", "INACTIVE"].map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`px-3 py-1.5 text-sm font-medium transition ${
                  statusFilter === status
                    ? "bg-[color:var(--accent)] text-[color:var(--note-bg)]"
                    : "text-[color:var(--board-ink)]/80 hover:bg-[color:var(--note-bg)]"
                }`}
              >
                {status === "ALL"
                  ? "All"
                  : status.charAt(0) + status.slice(1).toLowerCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Sort */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-[color:var(--board-ink)]/80">Sort:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-1.5 border border-[color:var(--note-border)] rounded-lg text-sm bg-[color:var(--note-bg)]/70 text-[color:var(--board-ink)] focus:outline-none focus:ring-2 focus:ring-[color:var(--accent-2)] transition-colors"
          >
            <option value="name">Name</option>
            <option value="lastPlayed">Last Played</option>
            <option value="questsPlayed">Quests Played</option>
          </select>
        </div>

        {/* Count */}
        <span className="px-3 py-1 bg-[color:var(--note-bg)]/80 text-[color:var(--board-ink)] rounded-full text-sm font-medium ml-auto border border-[color:var(--note-border)] shadow-inner">
          {filteredCharacters.length} characters
        </span>
      </div>

      {/* Character Grid */}
      {filteredCharacters.length > 0 ? (
        <InfiniteScroll
          dataLength={displayedCharacters.length}
          next={fetchMoreCharacters}
          hasMore={hasMore}
          loader={
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[color:var(--accent)]"></div>
            </div>
          }
          endMessage={
            <p className="text-center text-[color:var(--board-ink)]/70 py-8">
              You've seen all {filteredCharacters.length} characters
            </p>
          }
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {displayedCharacters.map((character) => (
              <CharacterCard
                key={character.characterId}
                character={character}
              />
            ))}
          </div>
        </InfiniteScroll>
      ) : (
        <EmptyState
          title="No characters found"
          message={
            searchQuery
              ? "Try adjusting your search or filters."
              : "Characters will appear here once they're created."
          }
        />
      )}
    </div>
  );
}
