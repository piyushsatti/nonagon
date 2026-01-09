import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import InfiniteScroll from "react-infinite-scroll-component";
import { fetchRecentQuests } from "../api/graphql";
import QuestCard from "../components/QuestCard";
import EmptyState from "../components/EmptyState";
import Loading from "../components/Loading";

const ITEMS_PER_PAGE = 9;

export default function QuestsPage() {
  const { id: guildId } = useParams();

  const [allQuests, setAllQuests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Pagination state for previous quests
  const [displayedPreviousQuests, setDisplayedPreviousQuests] = useState([]);
  const [hasMore, setHasMore] = useState(true);

  // Separate active and previous quests
  const activeStatuses = ["DRAFT", "ANNOUNCED", "SIGNUP_CLOSED"];
  const activeQuests = allQuests.filter((q) =>
    activeStatuses.includes(q.status)
  );
  const previousQuests = allQuests
    .filter((q) => !activeStatuses.includes(q.status))
    .sort(
      (a, b) =>
        new Date(b.endedAt || b.startedAt || 0) -
        new Date(a.endedAt || a.startedAt || 0)
    );

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);

      try {
        const quests = await fetchRecentQuests(guildId, 100);
        setAllQuests(quests || []);
        setLoading(false);
      } catch (err) {
        console.error("Failed to fetch quests:", err);
        setError(`Failed to load quests: ${err.message}`);
        setLoading(false);
      }
    }

    loadData();
  }, [guildId]);

  // Initialize displayed previous quests when data loads
  useEffect(() => {
    if (previousQuests.length > 0) {
      setDisplayedPreviousQuests(previousQuests.slice(0, ITEMS_PER_PAGE));
      setHasMore(previousQuests.length > ITEMS_PER_PAGE);
    }
  }, [allQuests]);

  const fetchMorePreviousQuests = () => {
    const currentLength = displayedPreviousQuests.length;
    const nextBatch = previousQuests.slice(
      currentLength,
      currentLength + ITEMS_PER_PAGE
    );

    setDisplayedPreviousQuests((prev) => [...prev, ...nextBatch]);
    setHasMore(currentLength + nextBatch.length < previousQuests.length);
  };

  if (loading) {
    return <Loading message="Loading quests..." />;
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
      <div className="mb-8">
        <h1 className="text-4xl font-display font-bold mb-2 drop-shadow-sm">
          Quests
        </h1>
        <p className="text-[color:var(--board-ink)]/80">
          Browse active adventures and explore the history of completed quests.
        </p>
      </div>

      {/* Active Quests Section */}
      <section className="mb-12">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold font-display">
              Active Quests
            </h2>
            <p className="text-sm text-[color:var(--board-ink)]/70">
              Quests that are currently running or open for signup
            </p>
          </div>
          <span className="px-3 py-1 bg-[color:var(--accent-2)]/20 text-[color:var(--accent)] rounded-full text-sm font-medium shadow-inner">
            {activeQuests.length} active
          </span>
        </div>

        {activeQuests.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {activeQuests.map((quest) => (
              <QuestCard key={quest.questId} quest={quest} />
            ))}
          </div>
        ) : (
          <EmptyState
            title="No active quests"
            message="There are no quests currently running or open for signup."
          />
        )}
      </section>

      {/* Divider */}
      <div className="border-t border-[color:var(--note-border)] my-8"></div>

      {/* Previous Quests Section */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold font-display">
              Previous Quests
            </h2>
            <p className="text-sm text-[color:var(--board-ink)]/70">
              Completed and cancelled quests from the past
            </p>
          </div>
          <span className="px-3 py-1 bg-[color:var(--note-bg)]/70 text-[color:var(--board-ink)] rounded-full text-sm font-medium border border-[color:var(--note-border)] shadow-inner">
            {previousQuests.length} total
          </span>
        </div>

        {previousQuests.length > 0 ? (
          <InfiniteScroll
            dataLength={displayedPreviousQuests.length}
            next={fetchMorePreviousQuests}
            hasMore={hasMore}
            loader={
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[color:var(--accent)]"></div>
              </div>
            }
            endMessage={
              <p className="text-center text-[color:var(--board-ink)]/70 py-8">
                You've seen all {previousQuests.length} previous quests
              </p>
            }
          >
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {displayedPreviousQuests.map((quest) => (
                <QuestCard key={quest.questId} quest={quest} />
              ))}
            </div>
          </InfiniteScroll>
        ) : (
          <EmptyState
            title="No previous quests"
            message="Completed quests will appear here."
          />
        )}
      </section>
    </div>
  );
}
