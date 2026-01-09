import React from "react";
import { Outlet } from "react-router-dom";
import Header from "./Header";
import Footer from "./Footer";
import BackendStatusBanner from "./BackendStatusBanner";
import { useBackend } from "../contexts/BackendContext";

export default function Layout() {
  const { isBackendAvailable } = useBackend();

  return (
    <div className="min-h-screen flex flex-col bg-board text-ink board-surface transition-colors duration-200">
      <Header />
      {!isBackendAvailable && <BackendStatusBanner />}
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
