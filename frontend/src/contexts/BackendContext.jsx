import React, { createContext, useContext, useState } from "react";

const BackendContext = createContext();

export function BackendProvider({ children }) {
  const [isBackendAvailable, setIsBackendAvailable] = useState(true);

  return (
    <BackendContext.Provider
      value={{ isBackendAvailable, setIsBackendAvailable }}
    >
      {children}
    </BackendContext.Provider>
  );
}

export function useBackend() {
  const context = useContext(BackendContext);
  if (!context) {
    throw new Error("useBackend must be used within BackendProvider");
  }
  return context;
}
