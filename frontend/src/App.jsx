import React, { useState, useEffect } from "react";
import { useEmployeeSearch } from "./hooks/useEmployeeSearch.js";
import { SearchBar } from "./components/SearchBar.jsx";
import { EmployeeList } from "./components/EmployeeList.jsx";
import { ErrorBoundary } from "./components/ErrorBoundary.jsx";
import "./App.css";

export function AppContent() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem("theme");
    if (saved) return saved === "dark";
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  const [viewMode, setViewMode] = useState(() => {
    const saved = localStorage.getItem("view_mode");
    return saved === "list" ? "list" : "grid";
  });

  const {
    searchQuery,
    setSearchQuery,
    employees,
    totalCount,
    isLoading,
    error,
    clearSearch,
    refresh,
  } = useEmployeeSearch(300);

  useEffect(() => {
    const theme = isDarkMode ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [isDarkMode]);

  useEffect(() => {
    localStorage.setItem("view_mode", viewMode);
  }, [viewMode]);

  return (
    <div className="layout">
      <header className="navbar">
        <div className="navbar-inner">
          <div className="brand">
            <span className="brand-icon" aria-hidden="true">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M22 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
            </span>
            <span className="brand-name">Employees</span>
            <span className="count-tag">{totalCount}</span>
          </div>

          <div className="nav-actions">
            <div className="seg-control" role="group" aria-label="View mode">
              <button
                type="button"
                className={`seg-btn ${viewMode === "grid" ? "active" : ""}`}
                onClick={() => setViewMode("grid")}
                aria-pressed={viewMode === "grid"}
                title="Grid view"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <rect x="3" y="3" width="7" height="7"></rect>
                  <rect x="14" y="3" width="7" height="7"></rect>
                  <rect x="14" y="14" width="7" height="7"></rect>
                  <rect x="3" y="14" width="7" height="7"></rect>
                </svg>
                <span>Grid</span>
              </button>
              <button
                type="button"
                className={`seg-btn ${viewMode === "list" ? "active" : ""}`}
                onClick={() => setViewMode("list")}
                aria-pressed={viewMode === "list"}
                title="List view"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <line x1="8" y1="6" x2="21" y2="6"></line>
                  <line x1="8" y1="12" x2="21" y2="12"></line>
                  <line x1="8" y1="18" x2="21" y2="18"></line>
                  <line x1="3" y1="6" x2="3.01" y2="6"></line>
                  <line x1="3" y1="12" x2="3.01" y2="12"></line>
                  <line x1="3" y1="18" x2="3.01" y2="18"></line>
                </svg>
                <span>List</span>
              </button>
            </div>

            <button
              type="button"
              className="btn-icon"
              onClick={() => setIsDarkMode((v) => !v)}
              aria-label={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
              title={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
            >
              {isDarkMode ? (
                <>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <circle cx="12" cy="12" r="5"></circle>
                    <line x1="12" y1="1" x2="12" y2="3"></line>
                    <line x1="12" y1="21" x2="12" y2="23"></line>
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                    <line x1="1" y1="12" x2="3" y2="12"></line>
                    <line x1="21" y1="12" x2="23" y2="12"></line>
                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                  </svg>
                  <span>Light</span>
                </>
              ) : (
                <>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                  </svg>
                  <span>Dark</span>
                </>
              )}
            </button>
          </div>
        </div>
      </header>

      <main className="container">
        <div className="toolbar">
          <SearchBar
            value={searchQuery}
            onChange={setSearchQuery}
            onClear={clearSearch}
            isLoading={isLoading && Boolean(searchQuery.trim())}
          />
        </div>

        <EmployeeList
          employees={employees}
          isLoading={isLoading}
          error={error}
          searchQuery={searchQuery}
          viewMode={viewMode}
          onRetry={refresh}
          onClearSearch={clearSearch}
        />
      </main>
    </div>
  );
}

export function App() {
  return (
    <ErrorBoundary>
      <AppContent />
    </ErrorBoundary>
  );
}

export default App;
