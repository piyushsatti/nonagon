function formatDate(dateString) {
  if (!dateString) return 'Never';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function StatusBadge({ status }) {
  const isActive = status === 'ACTIVE';
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
      isActive ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
    }`}>
      {status}
    </span>
  );
}

function TagBadge({ tag }) {
  return (
    <span className="px-2 py-0.5 bg-indigo-50 text-indigo-600 rounded text-xs">
      {tag}
    </span>
  );
}

export default function CharacterCard({ character }) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
      <div className="flex">
        {character.artLink ? (
          <div className="w-24 h-24 flex-shrink-0 bg-gray-200">
            <img 
              src={character.artLink} 
              alt={character.name}
              className="w-full h-full object-cover"
              onError={(e) => e.target.style.display = 'none'}
            />
          </div>
        ) : (
          <div className="w-24 h-24 flex-shrink-0 bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center">
            <span className="text-2xl font-bold text-indigo-300">
              {character.name?.charAt(0) || '?'}
            </span>
          </div>
        )}
        
        <div className="p-3 flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-semibold text-gray-900 truncate">
              {character.name}
            </h3>
            <StatusBadge status={character.status} />
          </div>
          
          <p className="text-sm text-gray-600 line-clamp-2 mt-1">
            {character.description || 'No description.'}
          </p>
        </div>
      </div>
      
      <div className="px-4 py-3 border-t border-gray-100">
        {character.tags?.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {character.tags.map((tag) => (
              <TagBadge key={tag} tag={tag} />
            ))}
          </div>
        )}
        
        <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
          <div>
            <span className="text-gray-400">Quests:</span> {character.questsPlayed || 0}
          </div>
          <div>
            <span className="text-gray-400">Summaries:</span> {character.summariesWritten || 0}
          </div>
        </div>
        
        <div className="mt-2 flex items-center gap-3 text-xs">
          {character.ddbLink && (
            <a 
              href={character.ddbLink} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              D&D Beyond
            </a>
          )}
          {character.tokenLink && (
            <a 
              href={character.tokenLink} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              Token
            </a>
          )}
        </div>
        
        <div className="mt-2 text-xs text-gray-400">
          Created: {formatDate(character.createdAt)} • Last played: {formatDate(character.lastPlayedAt)}
        </div>
      </div>
    </div>
  );
}
