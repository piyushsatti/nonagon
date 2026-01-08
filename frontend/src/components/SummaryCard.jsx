function formatDate(dateString) {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function KindBadge({ kind }) {
  const isPlayer = kind === 'PLAYER';
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
      isPlayer ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'
    }`}>
      {kind}
    </span>
  );
}

function StatusBadge({ status }) {
  const isPosted = status === 'POSTED';
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
      isPosted ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
    }`}>
      {status}
    </span>
  );
}

export default function SummaryCard({ summary }) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-2 mb-2">
        <h3 className="font-semibold text-gray-900 line-clamp-1">
          {summary.title || 'Untitled Summary'}
        </h3>
        <div className="flex gap-1 flex-shrink-0">
          <KindBadge kind={summary.kind} />
          <StatusBadge status={summary.status} />
        </div>
      </div>
      
      <p className="text-sm text-gray-600 line-clamp-3 mb-3">
        {summary.description || 'No content.'}
      </p>
      
      <div className="space-y-1 text-xs text-gray-500">
        {summary.questId && (
          <div>
            <span className="text-gray-400">Quest:</span> {summary.questId}
          </div>
        )}
        {summary.characterId && (
          <div>
            <span className="text-gray-400">Character:</span> {summary.characterId}
          </div>
        )}
        {summary.authorId && (
          <div>
            <span className="text-gray-400">Author:</span> {summary.authorId}
          </div>
        )}
      </div>
      
      <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-400 flex justify-between">
        <span>Created: {formatDate(summary.createdOn)}</span>
        {summary.lastEditedAt && (
          <span>Edited: {formatDate(summary.lastEditedAt)}</span>
        )}
      </div>
    </div>
  );
}
