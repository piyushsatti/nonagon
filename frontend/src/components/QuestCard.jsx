import { Link } from "react-router-dom";

const DEFAULT_QUEST_IMAGE = "/quest-fallback.jpg";

function formatDate(dateString) {
  if (!dateString) return "TBD";
  return new Date(dateString).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
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
      "bg-emerald-100/70 text-emerald-800 border border-emerald-200/70",
    CANCELLED: "bg-rose-100/70 text-rose-800 border border-rose-200/70",
  };

  return (
    <span
      className={`px-2 py-0.5 rounded-full text-xs font-medium shadow-inner ${
        colors[status] || "bg-gray-100 text-gray-700"
      }`}
    >
      {status?.replace("_", " ")}
    </span>
  );
}

export default function QuestCard({ quest, guildId = "demo" }) {
  const signupCount = quest.signups?.length || 0;
  const selectedCount = quest.signups?.filter((s) => s.selected).length || 0;

  const handleImageError = (e) => {
    if (e.target.src !== DEFAULT_QUEST_IMAGE) {
      e.target.src = DEFAULT_QUEST_IMAGE;
    }
  };

  return (
    <div className="parchment-card group rounded-xl overflow-hidden hover:ring-2 hover:ring-[color:var(--accent-2)]/50 motion-safe:animate-pinIn even:motion-safe:animate-paperFloat transition-transform duration-200 ease-out motion-safe:hover:-translate-y-1 motion-safe:hover:-rotate-1 motion-reduce:transform-none">
      <div className="h-32 bg-[color:var(--board-ink)]/15 overflow-hidden">
        <img
          src={quest.imageUrl || DEFAULT_QUEST_IMAGE}
          alt={quest.title || "Quest image"}
          className="w-full h-full object-cover"
          onError={handleImageError}
        />
      </div>

      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-semibold text-[color:var(--board-ink)] line-clamp-1 font-display">
            {quest.title || "Untitled Quest"}
          </h3>
          <StatusBadge status={quest.status} />
        </div>

        <p className="text-sm text-[color:var(--board-ink)]/80 line-clamp-2 mb-3">
          {quest.description || "No description provided."}
        </p>

        <div className="space-y-2 text-sm">
          <div className="flex items-center text-[color:var(--board-ink)]/80">
            <svg
              className="w-4 h-4 mr-2 text-[color:var(--accent-2)]/70"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            {formatDate(quest.startingAt)}
          </div>

          {quest.durationHours && (
            <div className="flex items-center text-[color:var(--board-ink)]/80">
              <svg
                className="w-4 h-4 mr-2 text-[color:var(--accent-2)]/70"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              {quest.durationHours} hours
            </div>
          )}

          <div className="flex items-center text-[color:var(--board-ink)]/80">
            <svg
              className="w-4 h-4 mr-2 text-[color:var(--accent-2)]/70"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
              />
            </svg>
            {selectedCount} selected / {signupCount} signups
          </div>
        </div>

        {quest.isSignupOpen && (
          <div className="mt-3 pt-3 border-t border-[color:var(--note-border)]">
            <span className="text-xs font-medium text-emerald-700">
              ✓ Signups Open
            </span>
          </div>
        )}

        <div className="mt-3 pt-3 border-t border-[color:var(--note-border)] flex items-center justify-between">
          <span className="text-xs text-[color:var(--board-ink)]/60">
            ID: {quest.questId}
          </span>
          <Link
            to={`/guild/${guildId}/quests/${quest.questId}`}
            className="px-3 py-1.5 bg-[color:var(--accent)] text-[color:var(--note-bg)] text-xs font-semibold rounded-lg shadow-pin hover:bg-[color:var(--accent)]/90 transition-colors"
          >
            View
          </Link>
        </div>
      </div>
    </div>
  );
}
