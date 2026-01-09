import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import {
  fetchQuest,
  fetchUsersByGuild,
  fetchCharactersByGuild,
} from "../api/graphql";
import Loading from "../components/Loading";

const DEFAULT_QUEST_IMAGE = "/quest-fallback.jpg";

function formatDate(dateString, includeTime = false) {
  if (!dateString) return "TBD";
  const options = {
    year: "numeric",
    month: "long",
    day: "numeric",
    ...(includeTime && { hour: "2-digit", minute: "2-digit" }),
  };
  return new Date(dateString).toLocaleDateString("en-US", options);
}

function StatusBadge({ status }) {
  const colors = {
    DRAFT:
      "bg-[color:var(--note-bg)] text-[color:var(--board-ink)] border border-[color:var(--note-border)]",
    ANNOUNCED:
      "bg-[color:var(--accent-2)]/25 text-[color:var(--accent)] border border-[color:var(--accent-2)]/60",
    SIGNUP_CLOSED:
      "bg-[color:var(--accent)]/15 text-[color:var(--accent)] border border-[color:var(--accent-2)]/60",
    COMPLETED:
      "bg-emerald-100/80 text-emerald-800 border border-emerald-200/80",
    CANCELLED: "bg-rose-100/70 text-rose-800 border border-rose-200/70",
  };

  return (
    <span
      className={`px-3 py-1 rounded-full text-sm font-medium shadow-inner ${
        colors[status] || "bg-gray-100 text-gray-700"
      }`}
    >
      {status?.replace("_", " ")}
    </span>
  );
}

export default function QuestDetailPage() {
  const { id: guildId, questId } = useParams();
  const [quest, setQuest] = useState(null);
  const [users, setUsers] = useState([]);
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);

      try {
        const [foundQuest, usersData, charsData] = await Promise.all([
          fetchQuest(guildId, questId),
          fetchUsersByGuild(guildId),
          fetchCharactersByGuild(guildId),
        ]);

        if (!foundQuest) {
          setError("Quest not found");
        } else {
          setQuest(foundQuest);
          setUsers(usersData || []);
          setCharacters(charsData || []);
        }
        setLoading(false);
      } catch (err) {
        console.error("Failed to fetch quest:", err);
        setError(`Failed to load quest: ${err.message}`);
        setLoading(false);
      }
    }

    loadData();
  }, [guildId, questId]);

  const handleImageError = (e) => {
    if (e.target.src !== DEFAULT_QUEST_IMAGE) {
      e.target.src = DEFAULT_QUEST_IMAGE;
    }
  };

  const getUserName = (userId) => {
    const user = users.find((u) => u.userId === userId);
    return user ? `User ${userId.replace("user-", "")}` : userId;
  };

  const getCharacterName = (characterId) => {
    const char = characters.find((c) => c.characterId === characterId);
    return char?.name || characterId;
  };

  if (loading) {
    return <Loading message="Loading quest..." />;
  }

  if (error || !quest) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8 text-[color:var(--board-ink)]">
        <div className="p-6 bg-[color:var(--note-bg)]/80 border border-[color:var(--note-border)] rounded-lg text-center shadow-parchment">
          <p className="text-[color:var(--accent)] mb-4">
            {error || "Quest not found"}
          </p>
          <Link
            to={`/guild/${guildId}/quests`}
            className="text-[color:var(--accent)] hover:text-[color:var(--accent-2)] underline-offset-2 hover:underline"
          >
            ← Back to Quests
          </Link>
        </div>
      </div>
    );
  }

  const signupCount = quest.signups?.length || 0;
  const selectedCount = quest.signups?.filter((s) => s.selected).length || 0;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 text-[color:var(--board-ink)] transition-colors duration-200">
      {/* Back Link */}
      <Link
        to={`/guild/${guildId}/quests`}
        className="inline-flex items-center text-sm text-[color:var(--board-ink)]/70 hover:text-[color:var(--accent)] mb-6"
      >
        <svg
          className="w-4 h-4 mr-1 text-[color:var(--accent-2)]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 19l-7-7 7-7"
          />
        </svg>
        Back to Quests
      </Link>

      {/* Hero Image */}
      <div className="h-64 md:h-80 bg-[color:var(--board-ink)]/15 rounded-xl overflow-hidden mb-6 shadow-parchment">
        <img
          src={quest.imageUrl || DEFAULT_QUEST_IMAGE}
          alt={quest.title}
          className="w-full h-full object-cover"
          onError={handleImageError}
        />
      </div>

      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-4xl font-display font-bold mb-2 drop-shadow-sm">
            {quest.title || "Untitled Quest"}
          </h1>
          <div className="flex items-center gap-3 text-sm text-[color:var(--board-ink)]/70">
            <span>ID: {quest.questId}</span>
            {quest.refereeId && (
              <span>
                Referee:{" "}
                <Link
                  to={`/guild/${guildId}`}
                  className="text-[color:var(--accent)] hover:text-[color:var(--accent-2)] underline-offset-2 hover:underline"
                >
                  {getUserName(quest.refereeId)}
                </Link>
              </span>
            )}
          </div>
        </div>
        <StatusBadge status={quest.status} />
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="parchment-card rounded-lg p-4">
          <div className="text-sm text-[color:var(--board-ink)]/70 mb-1">
            Scheduled Start
          </div>
          <div className="font-semibold">
            {formatDate(quest.startingAt, true)}
          </div>
        </div>
        <div className="parchment-card rounded-lg p-4">
          <div className="text-sm text-[color:var(--board-ink)]/70 mb-1">
            Duration
          </div>
          <div className="font-semibold">
            {quest.durationHours ? `${quest.durationHours} hours` : "TBD"}
          </div>
        </div>
        <div className="parchment-card rounded-lg p-4">
          <div className="text-sm text-[color:var(--board-ink)]/70 mb-1">
            Signups
          </div>
          <div className="font-semibold">
            {selectedCount} selected / {signupCount} total
          </div>
          {quest.isSignupOpen && (
            <span className="text-xs text-emerald-700 font-medium">
              ✓ Open for signup
            </span>
          )}
        </div>
      </div>

      {/* Description */}
      <div className="parchment-card rounded-lg p-6 mb-8">
        <h2 className="text-lg font-semibold font-display mb-3">
          Description
        </h2>
        <p className="text-[color:var(--board-ink)]/80 whitespace-pre-wrap">
          {quest.description || "No description provided."}
        </p>
      </div>

      {/* Timeline */}
      <div className="parchment-card rounded-lg p-6 mb-8">
        <h2 className="text-lg font-semibold font-display mb-4">Timeline</h2>
        <div className="space-y-3">
          {quest.announceAt && (
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-[color:var(--accent)]"></div>
              <span className="text-sm text-[color:var(--board-ink)]/80">
                Announced: {formatDate(quest.announceAt, true)}
              </span>
            </div>
          )}
          {quest.startedAt && (
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-emerald-600"></div>
              <span className="text-sm text-[color:var(--board-ink)]/80">
                Started: {formatDate(quest.startedAt, true)}
              </span>
            </div>
          )}
          {quest.endedAt && (
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-[color:var(--board-ink)]/60"></div>
              <span className="text-sm text-[color:var(--board-ink)]/80">
                Ended: {formatDate(quest.endedAt, true)}
              </span>
            </div>
          )}
          {!quest.announceAt && !quest.startedAt && !quest.endedAt && (
            <p className="text-sm text-[color:var(--board-ink)]/70">
              No timeline events yet.
            </p>
          )}
        </div>
      </div>

      {/* Signups */}
      {quest.signups && quest.signups.length > 0 && (
        <div className="parchment-card rounded-lg p-6">
          <h2 className="text-lg font-semibold font-display mb-4">
            Signups ({quest.signups.length})
          </h2>
          <div className="divide-y divide-[color:var(--note-border)]">
            {quest.signups.map((signup, index) => (
              <div
                key={index}
                className="py-3 flex items-center justify-between"
              >
                <div>
                  <Link
                    to={`/guild/${guildId}/characters/${signup.characterId}`}
                    className="font-medium text-[color:var(--accent)] hover:text-[color:var(--accent-2)] underline-offset-2 hover:underline"
                  >
                    {getCharacterName(signup.characterId)}
                  </Link>
                  <span className="text-sm text-[color:var(--board-ink)]/60 ml-2">
                    ({getUserName(signup.userId)})
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {signup.selected && (
                    <span className="px-2 py-0.5 bg-emerald-100/80 text-emerald-800 text-xs font-medium rounded-full border border-emerald-200/80">
                      Selected
                    </span>
                  )}
                  <span className="text-xs text-[color:var(--board-ink)]/60">
                    {formatDate(signup.signedUpAt)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
