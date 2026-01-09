import React, {
  useState,
  useEffect,
  useMemo,
  useCallback,
  useRef,
} from "react";
import { useParams } from "react-router-dom";
import InfiniteScroll from "react-infinite-scroll-component";
import ForceGraph2D from "react-force-graph-2d";
import { fetchSummariesByGuild, fetchRecentQuests } from "../api/graphql";
import SummaryCard from "../components/SummaryCard";
import EmptyState from "../components/EmptyState";
import Loading from "../components/Loading";

const ITEMS_PER_PAGE = 12;

function formatDate(dateString) {
  if (!dateString) return "N/A";
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export default function SummariesPage() {
  const { id: guildId } = useParams();
  const graphRef = useRef();

  const [allSummaries, setAllSummaries] = useState([]);
  const [allQuests, setAllQuests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // View mode: 'list' or 'graph'
  const [viewMode, setViewMode] = useState("list");

  // Filter state
  const [kindFilter, setKindFilter] = useState("ALL"); // ALL, PLAYER, REFEREE

  // Pagination state for list view
  const [displayedSummaries, setDisplayedSummaries] = useState([]);
  const [hasMore, setHasMore] = useState(true);

  // Selected summary in graph view
  const [selectedSummary, setSelectedSummary] = useState(null);

  // Sort and filter summaries
  const filteredSummaries = useMemo(() => {
    let filtered = [...allSummaries];

    if (kindFilter !== "ALL") {
      filtered = filtered.filter((s) => s.kind === kindFilter);
    }

    // Sort by createdOn date (newest first for list view)
    return filtered.sort(
      (a, b) => new Date(b.createdOn) - new Date(a.createdOn)
    );
  }, [allSummaries, kindFilter]);

  // Build graph data for visualization
  const graphData = useMemo(() => {
    if (filteredSummaries.length === 0) {
      return { nodes: [], links: [] };
    }

    // Sort by time for graph (oldest to newest, left to right)
    const sortedByTime = [...filteredSummaries].sort(
      (a, b) => new Date(a.createdOn) - new Date(b.createdOn)
    );

    // Create nodes with x position based on time
    const timeRange = {
      min: new Date(sortedByTime[0].createdOn).getTime(),
      max: new Date(sortedByTime[sortedByTime.length - 1].createdOn).getTime(),
    };
    const timeSpan = timeRange.max - timeRange.min || 1;

    // Group summaries by quest for vertical positioning
    const questGroups = {};
    sortedByTime.forEach((summary) => {
      const questId = summary.questId || "no-quest";
      if (!questGroups[questId]) {
        questGroups[questId] = [];
      }
      questGroups[questId].push(summary);
    });

    const questIds = Object.keys(questGroups);

    // Card dimensions for layout
    const cardWidth = 180;
    const cardHeight = 70;
    const horizontalGap = 60;
    const verticalGap = 40;

    const nodes = sortedByTime.map((summary, index) => {
      const time = new Date(summary.createdOn).getTime();
      // Spread nodes more horizontally based on index
      const xPos = index * (cardWidth + horizontalGap);

      const questId = summary.questId || "no-quest";
      const questIndex = questIds.indexOf(questId);
      const yPos = questIndex * (cardHeight + verticalGap);

      return {
        id: summary.summaryId,
        title: summary.title,
        kind: summary.kind,
        questId: summary.questId,
        createdOn: summary.createdOn,
        summary: summary,
        x: xPos,
        y: yPos,
        fx: xPos, // Fix x position
        fy: yPos, // Fix y position too for clean layout
      };
    });

    // Create links between summaries of the same quest (chronological)
    const links = [];
    Object.values(questGroups).forEach((group) => {
      if (group.length > 1) {
        // Sort group by time
        const sorted = group.sort(
          (a, b) => new Date(a.createdOn) - new Date(b.createdOn)
        );
        for (let i = 0; i < sorted.length - 1; i++) {
          links.push({
            source: sorted[i].summaryId,
            target: sorted[i + 1].summaryId,
            questId: sorted[i].questId,
          });
        }
      }
    });

    return { nodes, links };
  }, [filteredSummaries]);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);

      try {
        const [summaries, quests] = await Promise.all([
          fetchSummariesByGuild(guildId),
          fetchRecentQuests(guildId, 100),
        ]);
        setAllSummaries(summaries || []);
        setAllQuests(quests || []);
        setLoading(false);
      } catch (err) {
        console.error("Failed to fetch summaries:", err);
        setError(`Failed to load summaries: ${err.message}`);
        setLoading(false);
      }
    }

    loadData();
  }, [guildId]);

  // Initialize displayed summaries when data or filter changes
  useEffect(() => {
    if (filteredSummaries.length > 0) {
      setDisplayedSummaries(filteredSummaries.slice(0, ITEMS_PER_PAGE));
      setHasMore(filteredSummaries.length > ITEMS_PER_PAGE);
    } else {
      setDisplayedSummaries([]);
      setHasMore(false);
    }
  }, [filteredSummaries]);

  const fetchMoreSummaries = () => {
    const currentLength = displayedSummaries.length;
    const nextBatch = filteredSummaries.slice(
      currentLength,
      currentLength + ITEMS_PER_PAGE
    );

    setDisplayedSummaries((prev) => [...prev, ...nextBatch]);
    setHasMore(currentLength + nextBatch.length < filteredSummaries.length);
  };

  // Graph node rendering - Mini card style
  const nodeCanvasObject = useCallback(
    (node, ctx, globalScale) => {
      const isSelected = selectedSummary?.summaryId === node.id;

      // Card dimensions
      const cardWidth = 160;
      const cardHeight = 60;
      const cornerRadius = 6;
      const x = node.x - cardWidth / 2;
      const y = node.y - cardHeight / 2;

      // Draw card shadow
      ctx.shadowColor = "rgba(0, 0, 0, 0.1)";
      ctx.shadowBlur = 8;
      ctx.shadowOffsetX = 0;
      ctx.shadowOffsetY = 2;

      // Draw card background
      ctx.beginPath();
      ctx.roundRect(x, y, cardWidth, cardHeight, cornerRadius);
      ctx.fillStyle = "#FFFFFF";
      ctx.fill();

      // Reset shadow
      ctx.shadowColor = "transparent";
      ctx.shadowBlur = 0;
      ctx.shadowOffsetX = 0;
      ctx.shadowOffsetY = 0;

      // Draw border
      ctx.strokeStyle = isSelected ? "#6366F1" : "#E5E7EB";
      ctx.lineWidth = isSelected ? 2 : 1;
      ctx.stroke();

      // Draw colored left accent bar
      const accentColor = node.kind === "PLAYER" ? "#3B82F6" : "#8B5CF6";
      ctx.beginPath();
      ctx.roundRect(x, y, 4, cardHeight, [cornerRadius, 0, 0, cornerRadius]);
      ctx.fillStyle = accentColor;
      ctx.fill();

      // Draw title text
      const title = node.title?.substring(0, 18) || "Untitled";
      const displayTitle = title.length >= 18 ? title + "..." : title;
      ctx.font = "bold 11px -apple-system, BlinkMacSystemFont, sans-serif";
      ctx.fillStyle = "#111827";
      ctx.textAlign = "left";
      ctx.textBaseline = "top";
      ctx.fillText(displayTitle, x + 12, y + 10);

      // Draw kind badge
      const kindText = node.kind === "PLAYER" ? "Player" : "Referee";
      ctx.font = "9px -apple-system, BlinkMacSystemFont, sans-serif";
      ctx.fillStyle = accentColor;
      ctx.fillText(kindText, x + 12, y + 28);

      // Draw date
      const date = formatDate(node.createdOn);
      ctx.font = "9px -apple-system, BlinkMacSystemFont, sans-serif";
      ctx.fillStyle = "#6B7280";
      ctx.fillText(date, x + 12, y + 42);
    },
    [selectedSummary]
  );

  // Custom pointer area for card-shaped nodes
  const nodePointerAreaPaint = useCallback((node, color, ctx) => {
    const cardWidth = 160;
    const cardHeight = 60;
    ctx.fillStyle = color;
    ctx.fillRect(
      node.x - cardWidth / 2,
      node.y - cardHeight / 2,
      cardWidth,
      cardHeight
    );
  }, []);

  const handleNodeClick = useCallback((node) => {
    setSelectedSummary(node.summary);
  }, []);

  if (loading) {
    return <Loading message="Loading summaries..." />;
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8 text-[color:var(--board-ink)]">
        <div className="p-4 bg-[color:var(--note-bg)]/80 border border-[color:var(--note-border)] rounded-lg shadow-parchment">
          <p className="text-[color:var(--accent)]">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 text-[color:var(--board-ink)] transition-colors duration-200">
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-4xl font-display font-bold mb-2 drop-shadow-sm">
          Adventure Summaries
        </h1>
        <p className="text-[color:var(--board-ink)]/80">
          Player and referee write-ups of completed adventures, sorted by date.
        </p>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        {/* Filter */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-[color:var(--board-ink)]/80">
            Filter:
          </span>
          <div className="flex rounded-lg border border-[color:var(--note-border)] overflow-hidden bg-[color:var(--note-bg)]/60">
            {["ALL", "PLAYER", "REFEREE"].map((kind) => (
              <button
                key={kind}
                onClick={() => setKindFilter(kind)}
                className={`px-3 py-1.5 text-sm font-medium transition ${
                  kindFilter === kind
                    ? "bg-[color:var(--accent)] text-[color:var(--note-bg)]"
                    : "text-[color:var(--board-ink)]/80 hover:bg-[color:var(--note-bg)]"
                }`}
              >
                {kind === "ALL"
                  ? "All"
                  : kind.charAt(0) + kind.slice(1).toLowerCase()}
              </button>
            ))}
          </div>
        </div>

        {/* View Toggle */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-[color:var(--board-ink)]/80">View:</span>
          <div className="flex rounded-lg border border-[color:var(--note-border)] overflow-hidden bg-[color:var(--note-bg)]/60">
            <button
              onClick={() => setViewMode("list")}
              className={`px-3 py-1.5 text-sm font-medium transition flex items-center gap-1 ${
                viewMode === "list"
                  ? "bg-[color:var(--accent)] text-[color:var(--note-bg)]"
                  : "text-[color:var(--board-ink)]/80 hover:bg-[color:var(--note-bg)]"
              }`}
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 10h16M4 14h16M4 18h16"
                />
              </svg>
              List
            </button>
            <button
              onClick={() => setViewMode("graph")}
              className={`px-3 py-1.5 text-sm font-medium transition flex items-center gap-1 ${
                viewMode === "graph"
                  ? "bg-[color:var(--accent)] text-[color:var(--note-bg)]"
                  : "text-[color:var(--board-ink)]/80 hover:bg-[color:var(--note-bg)]"
              }`}
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                />
              </svg>
              Graph
            </button>
          </div>
        </div>

        {/* Count */}
        <span className="px-3 py-1 bg-[color:var(--note-bg)]/80 text-[color:var(--board-ink)] rounded-full text-sm font-medium border border-[color:var(--note-border)] shadow-inner">
          {filteredSummaries.length} summaries
        </span>
      </div>

      {/* List View */}
      {viewMode === "list" && (
        <>
          {filteredSummaries.length > 0 ? (
            <InfiniteScroll
              dataLength={displayedSummaries.length}
              next={fetchMoreSummaries}
              hasMore={hasMore}
              loader={
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[color:var(--accent)]"></div>
                </div>
              }
              endMessage={
                <p className="text-center text-[color:var(--board-ink)]/70 py-8">
                  You've seen all {filteredSummaries.length} summaries
                </p>
              }
            >
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {displayedSummaries.map((summary) => (
                  <SummaryCard key={summary.summaryId} summary={summary} />
                ))}
              </div>
            </InfiniteScroll>
          ) : (
            <EmptyState
              title="No summaries found"
              message="Adventure summaries will appear here once they're written."
            />
          )}
        </>
      )}

      {/* Graph View */}
      {viewMode === "graph" && (
        <div className="parchment-card rounded-lg overflow-hidden">
          {/* Graph Legend */}
          <div className="px-4 py-3 border-b border-[color:var(--note-border)] flex flex-wrap items-center gap-6 text-sm">
            <span className="text-[color:var(--board-ink)]/80 font-medium">
              Legend:
            </span>
            <div className="flex items-center gap-2">
              <div className="w-1 h-4 rounded-sm bg-[color:var(--accent-2)]"></div>
              <span className="text-[color:var(--board-ink)]/80">Player Summary</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-1 h-4 rounded-sm bg-[color:var(--accent)]/80"></div>
              <span className="text-[color:var(--board-ink)]/80">Referee Summary</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-0.5 bg-[color:var(--board-ink)]/40"></div>
              <span className="text-[color:var(--board-ink)]/80">Same Quest</span>
            </div>
            <span className="ml-auto text-[color:var(--board-ink)]/60 text-xs">
              Scroll to pan • Pinch/scroll to zoom
            </span>
          </div>

          {/* Graph Container */}
          <div className="relative overflow-auto" style={{ height: "500px" }}>
            {graphData.nodes.length > 0 ? (
              <ForceGraph2D
                ref={graphRef}
                graphData={graphData}
                nodeCanvasObject={nodeCanvasObject}
                nodePointerAreaPaint={nodePointerAreaPaint}
                onNodeClick={handleNodeClick}
                linkColor={() => "rgba(201, 162, 74, 0.55)"}
                linkWidth={2}
                linkDirectionalArrowLength={0}
                linkCurvature={0}
                enableNodeDrag={false}
                enableZoomInteraction={true}
                enablePanInteraction={true}
                cooldownTicks={0}
                d3AlphaDecay={1}
                d3VelocityDecay={1}
                minZoom={0.3}
                maxZoom={2}
                width={
                  typeof window !== "undefined"
                    ? Math.min(window.innerWidth - 64, 1280 - 32)
                    : 800
                }
                height={500}
              />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center">
                <EmptyState
                  title="No summaries to visualize"
                  message="Create some adventure summaries to see them on the graph."
                />
              </div>
            )}
          </div>

          {/* Selected Summary Panel */}
          {selectedSummary && (
            <div className="border-t border-[color:var(--note-border)] p-4 bg-[color:var(--note-bg)]/70">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium border ${
                        selectedSummary.kind === "PLAYER"
                          ? "bg-[color:var(--accent-2)]/25 text-[color:var(--accent)] border-[color:var(--accent-2)]/60"
                          : "bg-[color:var(--note-bg)] text-[color:var(--board-ink)] border-[color:var(--note-border)]"
                      }`}
                    >
                      {selectedSummary.kind}
                    </span>
                    <span className="text-sm text-[color:var(--board-ink)]/70">
                      {formatDate(selectedSummary.createdOn)}
                    </span>
                  </div>
                  <h3 className="font-semibold font-display mb-1">
                    {selectedSummary.title || "Untitled Summary"}
                  </h3>
                  <p className="text-sm text-[color:var(--board-ink)]/80 line-clamp-2">
                    {selectedSummary.description}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedSummary(null)}
                  className="text-[color:var(--board-ink)]/50 hover:text-[color:var(--board-ink)] transition"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
