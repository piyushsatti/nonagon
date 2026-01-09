import { Link } from "react-router-dom";

const DEFAULT_SUMMARY_IMAGE = "/summary-fallback.jpg";

function formatDate(dateString) {
  if (!dateString) return "N/A";
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function KindBadge({ kind }) {
  const isPlayer = kind === "PLAYER";
  return (
    <span
      className={`px-2 py-0.5 rounded-full text-xs font-medium border ${
        isPlayer
          ? "bg-[color:var(--accent-2)]/25 text-[color:var(--accent)] border-[color:var(--accent-2)]/60"
          : "bg-[color:var(--note-bg)] text-[color:var(--board-ink)] border-[color:var(--note-border)]"
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
      className={`px-2 py-0.5 rounded-full text-xs font-medium border ${
        isPosted
          ? "bg-emerald-100/80 text-emerald-800 border-emerald-200/70"
          : "bg-rose-100/70 text-rose-800 border-rose-200/70"
      }`}
    >
      {status}
    </span>
  );
}

export default function SummaryCard({ summary, guildId = "demo" }) {
  return (
    <div className="parchment-card rounded-xl overflow-hidden hover:ring-2 hover:ring-[color:var(--accent-2)]/50 transition-transform duration-200 ease-out motion-safe:animate-pinIn motion-safe:hover:-translate-y-1 motion-safe:hover:-rotate-1 motion-reduce:transform-none">
      {/* Banner Image */}
      <div className="h-24 bg-[color:var(--board-ink)]/10 overflow-hidden">
        <img
          src={DEFAULT_SUMMARY_IMAGE}
          alt="Summary"
          className="w-full h-full object-cover"
        />
      </div>

      <div className="p-4">
        <div className="flex items-start justify-between gap-2 mb-2">
          <h3 className="font-semibold text-[color:var(--board-ink)] line-clamp-1 font-display">
            {summary.title || "Untitled Summary"}
          </h3>
          <div className="flex gap-1 flex-shrink-0">
            <KindBadge kind={summary.kind} />
            <StatusBadge status={summary.status} />
          </div>
        </div>

        <p className="text-sm text-[color:var(--board-ink)]/80 line-clamp-3 mb-3">
          {summary.description || "No content."}
        </p>

        <div className="space-y-1 text-xs text-[color:var(--board-ink)]/70">
          {summary.questId && (
            <div>
              <span className="text-[color:var(--board-ink)]/60">Quest:</span>{" "}
              {summary.questId}
            </div>
          )}
          {summary.characterId && (
            <div>
              <span className="text-[color:var(--board-ink)]/60">Character:</span>{" "}
              {summary.characterId}
            </div>
          )}
          {summary.authorId && (
            <div>
              <span className="text-[color:var(--board-ink)]/60">Author:</span>{" "}
              {summary.authorId}
            </div>
          )}
        </div>

        <div className="mt-3 pt-3 border-t border-[color:var(--note-border)] flex items-center justify-between">
          <div className="text-xs text-[color:var(--board-ink)]/60">
            <span>Created: {formatDate(summary.createdOn)}</span>
            {summary.lastEditedAt && (
              <span className="ml-2">
                • Edited: {formatDate(summary.lastEditedAt)}
              </span>
            )}
          </div>
          <Link
            to={`/guild/${guildId}/summaries/${summary.summaryId}`}
            className="px-3 py-1.5 bg-[color:var(--accent)] text-[color:var(--note-bg)] text-xs font-semibold rounded-lg shadow-pin hover:bg-[color:var(--accent)]/90 transition-colors"
          >
            View
          </Link>
        </div>
      </div>
    </div>
  );
}
