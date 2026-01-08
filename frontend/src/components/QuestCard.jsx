function formatDate(dateString) {
  if (!dateString) return 'TBD';
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function StatusBadge({ status }) {
  const colors = {
    DRAFT: 'bg-gray-100 text-gray-700',
    ANNOUNCED: 'bg-blue-100 text-blue-700',
    SIGNUP_CLOSED: 'bg-yellow-100 text-yellow-700',
    COMPLETED: 'bg-green-100 text-green-700',
    CANCELLED: 'bg-red-100 text-red-700',
  };
  
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-700'}`}>
      {status?.replace('_', ' ')}
    </span>
  );
}

export default function QuestCard({ quest }) {
  const signupCount = quest.signups?.length || 0;
  const selectedCount = quest.signups?.filter(s => s.selected).length || 0;
  
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
      {quest.imageUrl && (
        <div className="h-32 bg-gray-200 overflow-hidden">
          <img 
            src={quest.imageUrl} 
            alt={quest.title} 
            className="w-full h-full object-cover"
            onError={(e) => e.target.style.display = 'none'}
          />
        </div>
      )}
      
      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-semibold text-gray-900 line-clamp-1">
            {quest.title || 'Untitled Quest'}
          </h3>
          <StatusBadge status={quest.status} />
        </div>
        
        <p className="text-sm text-gray-600 line-clamp-2 mb-3">
          {quest.description || 'No description provided.'}
        </p>
        
        <div className="space-y-2 text-sm">
          <div className="flex items-center text-gray-600">
            <svg className="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {formatDate(quest.startingAt)}
          </div>
          
          {quest.durationHours && (
            <div className="flex items-center text-gray-600">
              <svg className="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {quest.durationHours} hours
            </div>
          )}
          
          <div className="flex items-center text-gray-600">
            <svg className="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            {selectedCount} selected / {signupCount} signups
          </div>
        </div>
        
        {quest.isSignupOpen && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <span className="text-xs font-medium text-green-600">✓ Signups Open</span>
          </div>
        )}
        
        <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-400">
          ID: {quest.questId}
        </div>
      </div>
    </div>
  );
}
