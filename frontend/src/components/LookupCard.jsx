function formatDate(dateString) {
  if (!dateString) return "N/A";
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export default function LookupCard({ lookup }) {
  return (
    <div className="parchment-card rounded-xl p-4 hover:ring-2 hover:ring-[color:var(--accent-2)]/50 transition-transform duration-200 ease-out motion-safe:animate-pinIn motion-safe:hover:-translate-y-1 motion-safe:hover:-rotate-1 motion-reduce:transform-none">
      <div className="flex items-start justify-between gap-2 mb-2">
        <h3 className="font-semibold text-[color:var(--board-ink)] font-display">
          {lookup.name}
        </h3>
      </div>

      <p className="text-sm text-[color:var(--board-ink)]/80 line-clamp-3 mb-3">
        {lookup.description || "No description."}
      </p>

      {lookup.url && (
        <a
          href={lookup.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-[color:var(--accent)] hover:text-[color:var(--accent-2)] underline-offset-2 hover:underline"
        >
          View Source →
        </a>
      )}

      <div className="mt-3 pt-3 border-t border-[color:var(--note-border)] text-xs text-[color:var(--board-ink)]/60 flex justify-between">
        <span>Created: {formatDate(lookup.createdAt)}</span>
        {lookup.updatedAt && (
          <span>Updated: {formatDate(lookup.updatedAt)}</span>
        )}
      </div>
    </div>
  );
}
