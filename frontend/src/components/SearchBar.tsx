import React from "react";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onClear?: () => void;
  isLoading?: boolean;
  totalCount?: number;
  placeholder?: string;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  value,
  onChange,
  onClear,
  isLoading = false,
  totalCount,
  placeholder = "Search employees by name or department...",
}) => {
  return (
    <div className="search-bar-container">
      <div className="search-input-wrapper">
        <span className="search-icon" aria-hidden="true">
          🔍
        </span>
        <input
          type="text"
          className="search-input"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          aria-label="Search employees"
          autoComplete="off"
          spellCheck="false"
        />
        {isLoading && (
          <div className="search-spinner" aria-label="Loading search results">
            <span className="mini-spinner"></span>
          </div>
        )}
        {!isLoading && value && onClear && (
          <button
            type="button"
            className="clear-button"
            onClick={onClear}
            aria-label="Clear search input"
            title="Clear search"
          >
            ✕
          </button>
        )}
      </div>

      <div className="search-status-bar">
        {value.trim() ? (
          <span className="search-status-text">
            Filtering for <strong className="query-highlight">"{value.trim()}"</strong>
            {typeof totalCount === "number" && (
              <span className="count-pill">
                {totalCount} {totalCount === 1 ? "employee" : "employees"} found
              </span>
            )}
          </span>
        ) : (
          <span className="search-status-text text-muted">
            {typeof totalCount === "number" && (
              <span>Showing all {totalCount} employees</span>
            )}
          </span>
        )}
      </div>
    </div>
  );
};
