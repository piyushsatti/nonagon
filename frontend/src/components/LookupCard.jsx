function formatDate(dateString) {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function KindBadge({ kind }) {
  const colors = {
    SPELL: 'bg-purple-100 text-purple-700',
    LOCATION: 'bg-green-100 text-green-700',
    FACTION: 'bg-orange-100 text-orange-700',
    ITEM: 'bg-yellow-100 text-yellow-700',
    NPC: 'bg-blue-100 text-blue-700',
    RULE: 'bg-red-100 text-red-700',
  };
  
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[kind] || 'bg-gray-100 text-gray-700'}`}>
      {kind}
    </span>
  );
}

export default function LookupCard({ lookup }) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-2 mb-2">
        <h3 className="font-semibold text-gray-900">
          {lookup.name}
        </h3>
        <KindBadge kind={lookup.kind} />
      </div>
      
      <p className="text-sm text-gray-600 line-clamp-3 mb-3">
        {lookup.value || 'No description.'}
      </p>
      
      {lookup.sourceUrl && (
        <a 
          href={lookup.sourceUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-blue-600 hover:underline"
        >
          View Source →
        </a>
      )}
      
      <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-400 flex justify-between">
        <span>Created: {formatDate(lookup.createdAt)}</span>
        {lookup.updatedAt && (
          <span>Updated: {formatDate(lookup.updatedAt)}</span>
        )}
      </div>
    </div>
  );
}
