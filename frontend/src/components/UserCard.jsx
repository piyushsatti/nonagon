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
    MEMBER: 'bg-gray-100 text-gray-700',
    PLAYER: 'bg-blue-100 text-blue-700',
    REFEREE: 'bg-purple-100 text-purple-700',
  };
  
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[role] || 'bg-gray-100 text-gray-700'}`}>
      {role}
    </span>
  );
}

export default function UserCard({ user }) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-semibold text-gray-900 text-sm">
            {user.discordId ? `Discord: ${user.discordId.slice(0, 8)}...` : user.userId}
          </h3>
          <p className="text-xs text-gray-500">ID: {user.userId}</p>
        </div>
        {user.hasServerTag && (
          <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs">
            Server Tag
          </span>
        )}
      </div>
      
      <div className="flex flex-wrap gap-1 mb-3">
        {user.roles?.map((role) => (
          <RoleBadge key={role} role={role} />
        ))}
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
        <div>
          <span className="text-gray-400">Messages:</span> {user.messagesCountTotal || 0}
        </div>
        <div>
          <span className="text-gray-400">Voice:</span> {formatDuration(user.voiceTotalTimeSpent)}
        </div>
        <div>
          <span className="text-gray-400">Reactions Given:</span> {user.reactionsGiven || 0}
        </div>
        <div>
          <span className="text-gray-400">Reactions Got:</span> {user.reactionsReceived || 0}
        </div>
      </div>
      
      <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500">
        <div className="flex justify-between">
          <span>Joined: {formatDate(user.joinedAt)}</span>
          <span>Active: {formatDate(user.lastActiveAt)}</span>
        </div>
      </div>
      
      {user.dmOptIn && (
        <div className="mt-2">
          <span className="text-xs text-blue-600">✓ DM Opt-in</span>
        </div>
      )}
    </div>
  );
}
