export default function EmptyState({ title, message }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 bg-[color:var(--note-bg)]/80 rounded-lg border-2 border-dashed border-[color:var(--note-border)] shadow-parchment transition-colors duration-200">
      <svg
        className="w-12 h-12 text-[color:var(--accent-2)] mb-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
        />
      </svg>
      <h3 className="text-lg font-semibold font-display text-[color:var(--board-ink)] mb-1">
        {title}
      </h3>
      <p className="text-sm text-[color:var(--board-ink)]/70">{message}</p>
    </div>
  );
}
