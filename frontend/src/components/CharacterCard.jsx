import { Link } from "react-router-dom";

const DEFAULT_PLACEHOLDER = "/character-fallback.jpg";

function formatDate(dateString) {
  if (!dateString) return "Never";
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function StatusBadge({ status }) {
  const isActive = status === "ACTIVE";
  return (
    <span
      className={`px-2 py-0.5 rounded-full text-xs font-medium border ${
        isActive
          ? "bg-emerald-100/80 text-emerald-800 border-emerald-200/80"
          : "bg-[color:var(--note-bg)] text-[color:var(--board-ink)]/70 border-[color:var(--note-border)]"
      }`}
    >
      {status}
    </span>
  );
}

function TagBadge({ tag }) {
  return (
    <span className="px-2 py-0.5 bg-[color:var(--accent-2)]/20 text-[color:var(--accent)] rounded text-xs border border-[color:var(--accent-2)]/40">
      {tag}
    </span>
  );
}

export default function CharacterCard({ character, guildId = "demo" }) {
  const handleImageError = (e) => {
    if (e.target.src !== DEFAULT_PLACEHOLDER) {
      e.target.src = DEFAULT_PLACEHOLDER;
    }
  };

  return (
    <div className="parchment-card rounded-xl overflow-hidden hover:ring-2 hover:ring-[color:var(--accent-2)]/50 transition-transform duration-200 ease-out motion-safe:animate-pinIn motion-safe:hover:-translate-y-1 motion-safe:hover:-rotate-1 motion-reduce:transform-none">
      <div className="flex">
        <div className="w-24 h-24 flex-shrink-0 bg-[color:var(--board-ink)]/10">
          {character.artLink ? (
            <img
              src={character.artLink}
              alt={character.name}
              className="w-full h-full object-cover"
              onError={handleImageError}
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-[color:var(--accent)]/15 to-[color:var(--accent-2)]/35 flex items-center justify-center">
              <span className="text-2xl font-bold text-[color:var(--accent)]/60">
                {character.name?.charAt(0) || "?"}
              </span>
            </div>
          )}
        </div>

        <div className="p-3 flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-semibold text-[color:var(--board-ink)] truncate font-display">
              {character.name}
            </h3>
            <StatusBadge status={character.status} />
          </div>

          <p className="text-sm text-[color:var(--board-ink)]/80 line-clamp-2 mt-1">
            {character.description || "No description."}
          </p>
        </div>
      </div>

      <div className="px-4 py-3 border-t border-[color:var(--note-border)]">
        {character.tags?.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {character.tags.map((tag) => (
              <TagBadge key={tag} tag={tag} />
            ))}
          </div>
        )}

        <div className="grid grid-cols-2 gap-2 text-xs text-[color:var(--board-ink)]/80">
          <div>
            <span className="text-[color:var(--board-ink)]/60">Quests:</span>{" "}
            {character.questsPlayed || 0}
          </div>
          <div>
            <span className="text-[color:var(--board-ink)]/60">Summaries:</span>{" "}
            {character.summariesWritten || 0}
          </div>
        </div>

        <div className="mt-2 flex items-center gap-3 text-xs">
          {character.ddbLink && (
            <a
              href={character.ddbLink}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[color:var(--accent)] hover:text-[color:var(--accent-2)] underline-offset-2 hover:underline"
            >
              D&D Beyond
            </a>
          )}
          {character.tokenLink && (
            <a
              href={character.tokenLink}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[color:var(--accent)] hover:text-[color:var(--accent-2)] underline-offset-2 hover:underline"
            >
              Token
            </a>
          )}
        </div>

        <div className="mt-2 text-xs text-[color:var(--board-ink)]/60">
          Created: {formatDate(character.createdAt)} • Last played:{" "}
          {formatDate(character.lastPlayedAt)}
        </div>

        <div className="mt-3 pt-3 border-t border-[color:var(--note-border)] flex justify-end">
          <Link
            to={`/guild/${guildId}/characters/${character.characterId}`}
            className="px-3 py-1.5 bg-[color:var(--accent)] text-[color:var(--note-bg)] text-xs font-semibold rounded-lg shadow-pin hover:bg-[color:var(--accent)]/90 transition-colors"
          >
            View
          </Link>
        </div>
      </div>
    </div>
  );
}
