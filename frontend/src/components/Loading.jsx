import React from "react";

export default function Loading({
  message = "Loading...",
  fullScreen = false,
}) {
  const containerClass = fullScreen
    ? "min-h-screen flex items-center justify-center"
    : "min-h-[50vh] flex items-center justify-center";

  return (
    <div className={containerClass}>
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[color:var(--accent)] mx-auto mb-4"></div>
        <p className="text-[color:var(--board-ink)]/80">{message}</p>
      </div>
    </div>
  );
}
