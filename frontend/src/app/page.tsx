export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-4">Nonagon</h1>
      <p className="text-lg text-gray-600">Quest management system for Discord communities</p>
      <div className="mt-8 flex gap-4">
        <a 
          href="/quests" 
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          View Quests
        </a>
        <a 
          href="/characters" 
          className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
        >
          Characters
        </a>
      </div>
    </main>
  );
}
