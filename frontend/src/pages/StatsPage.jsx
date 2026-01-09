import React, { useState, useEffect, useMemo } from "react";
import { useParams } from "react-router-dom";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { getAllDummyData } from "../data/dummy";

const COLORS = [
  "#6366F1",
  "#8B5CF6",
  "#EC4899",
  "#14B8A6",
  "#F59E0B",
  "#EF4444",
];

function StatCard({ title, value, subtitle, icon, trend }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className="text-2xl">{icon}</div>
      </div>
      {trend && (
        <div
          className={`mt-3 text-sm ${
            trend > 0 ? "text-green-600" : "text-red-600"
          }`}
        >
          {trend > 0 ? "↑" : "↓"} {Math.abs(trend)}% from last month
        </div>
      )}
    </div>
  );
}

function LeaderboardTable({ title, data, columns }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900">{title}</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Rank
              </th>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase"
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.slice(0, 10).map((item, index) => (
              <tr key={index} className={index < 3 ? "bg-indigo-50/50" : ""}>
                <td className="px-4 py-3 text-sm">
                  <span
                    className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold ${
                      index === 0
                        ? "bg-yellow-100 text-yellow-700"
                        : index === 1
                        ? "bg-gray-100 text-gray-700"
                        : index === 2
                        ? "bg-orange-100 text-orange-700"
                        : "text-gray-500"
                    }`}
                  >
                    {index + 1}
                  </span>
                </td>
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-3 text-sm text-gray-900">
                    {col.render
                      ? col.render(item[col.key], item)
                      : item[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function StatsPage() {
  const { id: guildId } = useParams();

  const [data, setData] = useState({
    users: [],
    quests: [],
    characters: [],
    summaries: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);

      try {
        const dummyData = getAllDummyData();
        setData(dummyData);
        setLoading(false);
      } catch (err) {
        console.error("Failed to fetch data:", err);
        setError(`Failed to load stats: ${err.message}`);
        setLoading(false);
      }
    }

    loadData();
  }, [guildId]);

  // Computed statistics
  const stats = useMemo(() => {
    const { users, quests, characters, summaries } = data;

    // Quest stats
    const completedQuests = quests.filter(
      (q) => q.status === "COMPLETED"
    ).length;
    const activeQuests = quests.filter((q) =>
      ["ANNOUNCED", "SIGNUP_CLOSED"].includes(q.status)
    ).length;

    // Character stats
    const activeCharacters = characters.filter(
      (c) => c.status === "ACTIVE"
    ).length;

    // User stats
    const totalMessages = users.reduce(
      (sum, u) => sum + (u.messagesCountTotal || 0),
      0
    );
    const totalVoiceHours = users.reduce(
      (sum, u) => sum + (u.voiceTotalTimeSpent || 0) / 3600,
      0
    );

    // Quest status distribution
    const questStatusData = [
      {
        name: "Completed",
        value: quests.filter((q) => q.status === "COMPLETED").length,
      },
      {
        name: "Active",
        value: quests.filter((q) => q.status === "ANNOUNCED").length,
      },
      {
        name: "Draft",
        value: quests.filter((q) => q.status === "DRAFT").length,
      },
      {
        name: "Cancelled",
        value: quests.filter((q) => q.status === "CANCELLED").length,
      },
    ].filter((d) => d.value > 0);

    // Summary kind distribution
    const summaryKindData = [
      {
        name: "Player",
        value: summaries.filter((s) => s.kind === "PLAYER").length,
      },
      {
        name: "Referee",
        value: summaries.filter((s) => s.kind === "REFEREE").length,
      },
    ].filter((d) => d.value > 0);

    // Top players by quests
    const playersWithQuests = characters
      .filter((c) => c.questsPlayed > 0)
      .sort((a, b) => b.questsPlayed - a.questsPlayed);

    // Top users by activity (messages)
    const usersByMessages = [...users].sort(
      (a, b) => (b.messagesCountTotal || 0) - (a.messagesCountTotal || 0)
    );

    // Monthly data for charts (prefer dummy-provided, fallback to mock)
    const monthlyActivity = data.monthlyActivity || [
      { month: "Sep", quests: 3, summaries: 6, newCharacters: 2 },
      { month: "Oct", quests: 4, summaries: 5, newCharacters: 1 },
      { month: "Nov", quests: 6, summaries: 9, newCharacters: 3 },
      { month: "Dec", quests: 8, summaries: 12, newCharacters: 4 },
      { month: "Jan", quests: 3, summaries: 4, newCharacters: 1 },
    ];

    return {
      totalUsers: users.length,
      totalQuests: quests.length,
      completedQuests,
      activeQuests,
      totalCharacters: characters.length,
      activeCharacters,
      totalSummaries: summaries.length,
      totalMessages,
      totalVoiceHours: Math.round(totalVoiceHours),
      questStatusData,
      summaryKindData,
      playersWithQuests,
      usersByMessages,
      monthlyActivity,
    };
  }, [data]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading statistics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Server Statistics
        </h1>
        <p className="text-gray-600">
          Overview of guild activity, player engagement, and adventure progress.
        </p>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard title="Total Users" value={stats.totalUsers} icon="👥" />
        <StatCard
          title="Active Characters"
          value={stats.activeCharacters}
          subtitle={`${stats.totalCharacters} total`}
          icon="🧙"
        />
        <StatCard
          title="Quests Completed"
          value={stats.completedQuests}
          subtitle={`${stats.activeQuests} active`}
          icon="⚔️"
        />
        <StatCard
          title="Summaries Written"
          value={stats.totalSummaries}
          icon="📜"
        />
      </div>

      {/* Engagement Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
        <StatCard
          title="Total Messages"
          value={stats.totalMessages.toLocaleString()}
          icon="💬"
        />
        <StatCard
          title="Voice Hours"
          value={stats.totalVoiceHours.toLocaleString()}
          icon="🎙️"
        />
        <StatCard title="Total Quests" value={stats.totalQuests} icon="📋" />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Monthly Activity Chart */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Monthly Activity</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={stats.monthlyActivity}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="month" stroke="#6B7280" fontSize={12} />
              <YAxis stroke="#6B7280" fontSize={12} />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="quests"
                stroke="#6366F1"
                strokeWidth={2}
                name="Quests"
              />
              <Line
                type="monotone"
                dataKey="summaries"
                stroke="#8B5CF6"
                strokeWidth={2}
                name="Summaries"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Quest Status Pie Chart */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">
            Quest Status Distribution
          </h3>
          {stats.questStatusData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={stats.questStatusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {stats.questStatusData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-gray-500">
              No quest data available
            </div>
          )}
        </div>
      </div>

      {/* Bar Chart Row */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-8">
        <h3 className="font-semibold text-gray-900 mb-4">
          New Characters by Month
        </h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={stats.monthlyActivity}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="month" stroke="#6B7280" fontSize={12} />
            <YAxis stroke="#6B7280" fontSize={12} />
            <Tooltip />
            <Bar
              dataKey="newCharacters"
              fill="#14B8A6"
              radius={[4, 4, 0, 0]}
              name="New Characters"
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Leaderboards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Characters by Quests */}
        <LeaderboardTable
          title="🏆 Most Active Characters"
          data={stats.playersWithQuests}
          columns={[
            { key: "name", label: "Character" },
            {
              key: "questsPlayed",
              label: "Quests",
              render: (val) => (
                <span className="font-semibold text-indigo-600">{val}</span>
              ),
            },
            {
              key: "summariesWritten",
              label: "Summaries",
              render: (val) => val || 0,
            },
          ]}
        />

        {/* Top Users by Messages */}
        <LeaderboardTable
          title="💬 Most Active Users"
          data={stats.usersByMessages}
          columns={[
            {
              key: "userId",
              label: "User",
              render: (val) => val.replace("user-", "User "),
            },
            {
              key: "messagesCountTotal",
              label: "Messages",
              render: (val) => (
                <span className="font-semibold text-indigo-600">
                  {(val || 0).toLocaleString()}
                </span>
              ),
            },
            {
              key: "reactionsGiven",
              label: "Reactions",
              render: (val) => val || 0,
            },
          ]}
        />
      </div>
    </div>
  );
}
