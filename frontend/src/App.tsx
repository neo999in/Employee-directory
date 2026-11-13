import React from "react";
import { useEmployeeSearch } from "./hooks/useEmployeeSearch";
import { SearchBar } from "./components/SearchBar";
import { EmployeeList } from "./components/EmployeeList";
import "./App.css";

export const App: React.FC = () => {
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

  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="header-content">
          <div className="brand">
            <span className="brand-logo" aria-hidden="true">🏢</span>
            <div>
              <h1 className="brand-title">Employee Directory</h1>
              <p className="brand-subtitle">
                Search and explore team members across all departments
              </p>
            </div>
          </div>
          <div className="header-meta">
            <span className="live-badge">Live System</span>
          </div>
        </div>
      </header>

      <main className="app-main">
        <section className="search-section" aria-label="Employee Search Controls">
          <SearchBar
            value={searchQuery}
            onChange={setSearchQuery}
            onClear={clearSearch}
            isLoading={isLoading && Boolean(searchQuery.trim())}
            totalCount={totalCount}
            placeholder="Search by name (e.g. 'Rahul') or department (e.g. 'Engineering')..."
          />
        </section>

        <section className="results-section" aria-label="Employee Directory Content">
          <EmployeeList
            employees={employees}
            isLoading={isLoading}
            error={error}
            searchQuery={searchQuery}
            onRetry={refresh}
            onClearSearch={clearSearch}
          />
        </section>
      </main>

      <footer className="app-footer">
        <p>Employee Directory System • Fast Search • Debounced API Queries</p>
      </footer>
    </div>
  );
};

export default App;
