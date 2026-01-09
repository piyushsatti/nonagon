function formatDate(dateString) {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function formatDuration(seconds) {
  if (!seconds) return '0h';
  const hours = Math.floor(seconds / 3600);
  return `${hours}h`;
}

function RoleBadge({ role }) {
  const colors = {
    MEMBER: 'bg-[color:var(--note-bg)] text-[color:var(--board-ink)]/80 border border-[color:var(--note-border)]',
    PLAYER: 'bg-[color:var(--accent-2)]/25 text-[color:var(--accent)] border border-[color:var(--accent-2)]/60',
    REFEREE: 'bg-[color:var(--accent)]/15 text-[color:var(--accent)] border border-[color:var(--accent-2)]/60',
  };
  
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[role] || 'bg-[color:var(--note-bg)] text-[color:var(--board-ink)]/80 border border-[color:var(--note-border)]'}`}>
      {role}
    </span>
  );
}

export default function UserCard({ user }) {
  return (
    <div className="parchment-card rounded-xl p-4 hover:ring-2 hover:ring-[color:var(--accent-2)]/50 transition-transform duration-200 ease-out motion-safe:animate-pinIn motion-safe:hover:-translate-y-1 motion-safe:hover:-rotate-1 motion-reduce:transform-none">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-semibold text-[color:var(--board-ink)] text-sm font-display">
            {user.discordId ? `Discord: ${user.discordId.slice(0, 8)}...` : user.userId}
          </h3>
          <p className="text-xs text-[color:var(--board-ink)]/60">ID: {user.userId}</p>
        </div>
        {user.hasServerTag && (
          <span className="px-2 py-0.5 bg-emerald-100/80 text-emerald-800 rounded text-xs border border-emerald-200/80">
            Server Tag
          </span>
        )}
      </div>
      
      <div className="flex flex-wrap gap-1 mb-3">
        {user.roles?.map((role) => (
          <RoleBadge key={role} role={role} />
        ))}
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-xs text-[color:var(--board-ink)]/80">
        <div>
          <span className="text-[color:var(--board-ink)]/60">Messages:</span> {user.messagesCountTotal || 0}
        </div>
        <div>
          <span className="text-[color:var(--board-ink)]/60">Voice:</span> {formatDuration(user.voiceTotalTimeSpent)}
        </div>
        <div>
          <span className="text-[color:var(--board-ink)]/60">Reactions Given:</span> {user.reactionsGiven || 0}
        </div>
        <div>
          <span className="text-[color:var(--board-ink)]/60">Reactions Got:</span> {user.reactionsReceived || 0}
        </div>
      </div>
      
      <div className="mt-3 pt-3 border-t border-[color:var(--note-border)] text-xs text-[color:var(--board-ink)]/70">
        <div className="flex justify-between">
          <span>Joined: {formatDate(user.joinedAt)}</span>
          <span>Active: {formatDate(user.lastActiveAt)}</span>
        </div>
      </div>
      
      {user.dmOptIn && (
        <div className="mt-2">
          <span className="text-xs text-[color:var(--accent)]">✓ DM Opt-in</span>
        </div>
      )}
    </div>
  );
}
