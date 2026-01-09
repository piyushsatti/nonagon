import React, { useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import GuildDashboard from "./pages/GuildDashboard";
import QuestsPage from "./pages/QuestsPage";
import QuestDetailPage from "./pages/QuestDetailPage";
import SummariesPage from "./pages/SummariesPage";
import SummaryDetailPage from "./pages/SummaryDetailPage";
import CharactersPage from "./pages/CharactersPage";
import CharacterDetailPage from "./pages/CharacterDetailPage";
import StatsPage from "./pages/StatsPage";
import LoginPage from "./pages/LoginPage";
import Layout from "./components/Layout";
import { BackendProvider, useBackend } from "./contexts/BackendContext";
import { setBackendStatusCallback } from "./api/graphql";

function AppRoutes() {
  const { setIsBackendAvailable } = useBackend();

  useEffect(() => {
    setBackendStatusCallback(setIsBackendAvailable);
  }, [setIsBackendAvailable]);

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/guild/:id" element={<Layout />}>
        <Route index element={<GuildDashboard />} />
        <Route path="quests" element={<QuestsPage />} />
        <Route path="quests/:questId" element={<QuestDetailPage />} />
        <Route path="summaries" element={<SummariesPage />} />
        <Route path="summaries/:summaryId" element={<SummaryDetailPage />} />
        <Route path="characters" element={<CharactersPage />} />
        <Route
          path="characters/:characterId"
          element={<CharacterDetailPage />}
        />
        <Route path="stats" element={<StatsPage />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <BackendProvider>
      <AppRoutes />
    </BackendProvider>
  );
}
