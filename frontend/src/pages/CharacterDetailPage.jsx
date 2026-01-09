import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import {
  fetchCharacter,
  fetchUser,
  fetchRecentQuests,
  fetchSummariesByGuild,
} from "../api/graphql";
import Loading from "../components/Loading";

const DEFAULT_PLACEHOLDER = "/placeholder.svg";

function formatDate(dateString) {
  if (!dateString) return "Never";
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function StatusBadge({ status }) {
  const isActive = status === "ACTIVE";
  return (
    <span
      className={`px-3 py-1 rounded-full text-sm font-medium ${
        isActive ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"
      }`}
    >
      {status}
    </span>
  );
}

function TagBadge({ tag }) {
  return (
    <span className="px-3 py-1 bg-indigo-50 text-indigo-600 rounded-full text-sm">
      {tag}
    </span>
  );
}

export default function CharacterDetailPage() {
  const { id: guildId, characterId } = useParams();
  const [character, setCharacter] = useState(null);
  const [owner, setOwner] = useState(null);
  const [relatedQuests, setRelatedQuests] = useState([]);
  const [relatedSummaries, setRelatedSummaries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);

      try {
        const foundChar = await fetchCharacter(guildId, characterId);

        if (!foundChar) {
          setError("Character not found");
          setLoading(false);
          return;
        }

        setCharacter(foundChar);

        // Fetch related data in parallel
        const promises = [];

        // Fetch owner
        if (foundChar.ownerId) {
          promises.push(
            fetchUser(guildId, foundChar.ownerId).then((u) => setOwner(u))
          );
        }

        // Fetch quests to find those with this character
        promises.push(
          fetchRecentQuests(guildId, 100).then((quests) => {
            const questsWithChar = (quests || []).filter((q) =>
              q.signups?.some((s) => s.characterId === characterId)
            );
            setRelatedQuests(questsWithChar);
          })
        );

        // Fetch summaries for this character
        promises.push(
          fetchSummariesByGuild(guildId).then((summaries) => {
            const summariesForChar = (summaries || []).filter(
              (s) => s.characterId === characterId
            );
            setRelatedSummaries(summariesForChar);
          })
        );

        await Promise.all(promises);
        setLoading(false);
      } catch (err) {
        console.error("Failed to fetch character:", err);
        setError(`Failed to load character: ${err.message}`);
        setLoading(false);
      }
    }

    loadData();
  }, [guildId, characterId]);

  const handleImageError = (e) => {
    if (e.target.src !== DEFAULT_PLACEHOLDER) {
      e.target.src = DEFAULT_PLACEHOLDER;
    }
  };

  if (loading) {
    return <Loading message="Loading character..." />;
  }

  if (error || !character) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg text-center">
          <p className="text-red-700 mb-4">{error || "Character not found"}</p>
          <Link
            to={`/guild/${guildId}/characters`}
            className="text-indigo-600 hover:underline"
          >
            ← Back to Characters
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Back Link */}
      <Link
        to={`/guild/${guildId}/characters`}
        className="inline-flex items-center text-sm text-gray-600 hover:text-indigo-600 mb-6"
      >
        <svg
          className="w-4 h-4 mr-1"
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
        Back to Characters
      </Link>

      {/* Hero Section */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden mb-8">
        <div className="md:flex">
          {/* Character Art */}
          <div className="md:w-1/3 h-64 md:h-auto bg-gray-100">
            {character.artLink ? (
              <img
                src={character.artLink}
                alt={character.name}
                className="w-full h-full object-cover"
                onError={handleImageError}
              />
            ) : (
              <div className="w-full h-full bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center">
                <span className="text-6xl font-bold text-indigo-300">
                  {character.name?.charAt(0) || "?"}
                </span>
              </div>
            )}
          </div>

          {/* Character Info */}
          <div className="md:w-2/3 p-6">
            <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-1">
                  {character.name}
                </h1>
                <div className="text-sm text-gray-500">
                  ID: {character.characterId}
                </div>
              </div>
              <StatusBadge status={character.status} />
            </div>

            {/* Tags */}
            {character.tags?.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {character.tags.map((tag) => (
                  <TagBadge key={tag} tag={tag} />
                ))}
              </div>
            )}

            {/* Description */}
            <p className="text-gray-700 mb-4">
              {character.description || "No description provided."}
            </p>

            {/* Notes */}
            {character.notes && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-4">
                <div className="text-xs text-amber-600 font-medium mb-1">
                  Notes
                </div>
                <p className="text-sm text-amber-800">{character.notes}</p>
              </div>
            )}

            {/* Owner */}
            {owner && (
              <div className="text-sm text-gray-600">
                Played by:{" "}
                <span className="font-medium">
                  User {character.ownerId.replace("user-", "")}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div className="text-3xl font-bold text-indigo-600">
            {character.questsPlayed || 0}
          </div>
          <div className="text-sm text-gray-500">Quests Played</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div className="text-3xl font-bold text-purple-600">
            {character.summariesWritten || 0}
          </div>
          <div className="text-sm text-gray-500">Summaries Written</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div className="text-sm font-medium text-gray-900">
            {formatDate(character.createdAt)}
          </div>
          <div className="text-sm text-gray-500">Created</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div className="text-sm font-medium text-gray-900">
            {formatDate(character.lastPlayedAt)}
          </div>
          <div className="text-sm text-gray-500">Last Played</div>
        </div>
      </div>

      {/* External Links */}
      {(character.ddbLink ||
        character.tokenLink ||
        character.characterThreadLink) && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            External Links
          </h2>
          <div className="flex flex-wrap gap-3">
            {character.ddbLink && (
              <a
                href={character.ddbLink}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                  />
                </svg>
                D&D Beyond
              </a>
            )}
            {character.tokenLink && (
              <a
                href={character.tokenLink}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                Token Image
              </a>
            )}
            {character.characterThreadLink && (
              <a
                href={character.characterThreadLink}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 transition"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
                Discord Thread
              </a>
            )}
          </div>
        </div>
      )}

      {/* Related Quests */}
      {relatedQuests.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Quest History ({relatedQuests.length})
          </h2>
          <div className="space-y-3">
            {relatedQuests.map((quest) => (
              <Link
                key={quest.questId}
                to={`/guild/${guildId}/quests/${quest.questId}`}
                className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900">
                    {quest.title}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      quest.status === "COMPLETED"
                        ? "bg-green-100 text-green-700"
                        : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {quest.status}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Related Summaries */}
      {relatedSummaries.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Summaries ({relatedSummaries.length})
          </h2>
          <div className="space-y-3">
            {relatedSummaries.map((summary) => (
              <Link
                key={summary.summaryId}
                to={`/guild/${guildId}/summaries/${summary.summaryId}`}
                className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900">
                    {summary.title}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      summary.kind === "PLAYER"
                        ? "bg-blue-100 text-blue-700"
                        : "bg-purple-100 text-purple-700"
                    }`}
                  >
                    {summary.kind}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
