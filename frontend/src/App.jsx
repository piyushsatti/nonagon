import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import GuildDashboard from './pages/GuildDashboard';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/guild/:id" element={<GuildDashboard />} />
    </Routes>
  );
}
