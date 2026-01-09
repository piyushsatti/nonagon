import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import {
  fetchSummary,
  fetchQuest,
  fetchCharacter,
  fetchUser,
} from "../api/graphql";
import Loading from "../components/Loading";

const DEFAULT_SUMMARY_IMAGE = "/summary-default.svg";

function formatDate(dateString) {
  if (!dateString) return "N/A";
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function KindBadge({ kind }) {
  const isPlayer = kind === "PLAYER";
  return (
    <span
      className={`px-3 py-1 rounded-full text-sm font-medium ${
        isPlayer ? "bg-blue-100 text-blue-700" : "bg-purple-100 text-purple-700"
      }`}
    >
      {kind}
    </span>
  );
}

function StatusBadge({ status }) {
  const isPosted = status === "POSTED";
  return (
    <span
      className={`px-3 py-1 rounded-full text-sm font-medium ${
        isPosted ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
      }`}
    >
      {status}
    </span>
  );
}

export default function SummaryDetailPage() {
  const { id: guildId, summaryId } = useParams();
  const [summary, setSummary] = useState(null);
  const [quest, setQuest] = useState(null);
  const [character, setCharacter] = useState(null);
  const [author, setAuthor] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);

      try {
        const foundSummary = await fetchSummary(guildId, summaryId);

        if (!foundSummary) {
          setError("Summary not found");
          setLoading(false);
          return;
        }

        setSummary(foundSummary);

        // Fetch related entities in parallel
        const promises = [];

        if (foundSummary.questId) {
          promises.push(
            fetchQuest(guildId, foundSummary.questId).then((q) => setQuest(q))
          );
        }

        if (foundSummary.characterId) {
          promises.push(
            fetchCharacter(guildId, foundSummary.characterId).then((c) =>
              setCharacter(c)
            )
          );
        }

        if (foundSummary.authorId) {
          promises.push(
            fetchUser(guildId, foundSummary.authorId).then((u) => setAuthor(u))
          );
        }

        await Promise.all(promises);
        setLoading(false);
      } catch (err) {
        console.error("Failed to fetch summary:", err);
        setError(`Failed to load summary: ${err.message}`);
        setLoading(false);
      }
    }

    loadData();
  }, [guildId, summaryId]);

  if (loading) {
    return <Loading message="Loading summary..." />;
  }

  if (error || !summary) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg text-center">
          <p className="text-red-700 mb-4">{error || "Summary not found"}</p>
          <Link
            to={`/guild/${guildId}/summaries`}
            className="text-indigo-600 hover:underline"
          >
            ← Back to Summaries
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Back Link */}
      <Link
        to={`/guild/${guildId}/summaries`}
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
        Back to Summaries
      </Link>

      {/* Hero Image */}
      <div className="h-48 md:h-64 bg-purple-50 rounded-xl overflow-hidden mb-6">
        <img
          src={DEFAULT_SUMMARY_IMAGE}
          alt="Summary"
          className="w-full h-full object-cover"
        />
      </div>

      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {summary.title || "Untitled Summary"}
          </h1>
          <div className="text-sm text-gray-500">ID: {summary.summaryId}</div>
        </div>
        <div className="flex gap-2">
          <KindBadge kind={summary.kind} />
          <StatusBadge status={summary.status} />
        </div>
      </div>

      {/* Meta Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500 mb-1">Author</div>
          <div className="font-semibold text-gray-900">
            {author
              ? `User ${summary.authorId.replace("user-", "")}`
              : summary.authorId || "Unknown"}
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500 mb-1">Created</div>
          <div className="font-semibold text-gray-900">
            {formatDate(summary.createdOn)}
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500 mb-1">Last Edited</div>
          <div className="font-semibold text-gray-900">
            {summary.lastEditedAt ? formatDate(summary.lastEditedAt) : "Never"}
          </div>
        </div>
      </div>

      {/* Related Links */}
      <div className="flex flex-wrap gap-4 mb-8">
        {quest && (
          <Link
            to={`/guild/${guildId}/quests/${quest.questId}`}
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
                d="M9 5l7 7-7 7"
              />
            </svg>
            Quest: {quest.title}
          </Link>
        )}
        {character && (
          <Link
            to={`/guild/${guildId}/characters/${character.characterId}`}
            className="inline-flex items-center gap-2 px-4 py-2 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition"
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
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
            Character: {character.name}
          </Link>
        )}
      </div>

      {/* Content */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Content</h2>
        <div className="prose prose-gray max-w-none">
          <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
            {summary.description || "No content provided."}
          </p>
        </div>
      </div>
    </div>
  );
}
