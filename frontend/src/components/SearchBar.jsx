import React from "react";

export function SearchBar({
  value,
  onChange,
  onClear,
  isLoading = false,
  placeholder = "Search name or department...",
}) {
  return (
    <div className="search-wrap">
      <span className="search-lens" aria-hidden="true">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
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
      {isLoading ? (
        <span className="search-loader" aria-label="Loading"></span>
      ) : value && onClear ? (
        <button
          type="button"
          className="search-clear"
          onClick={onClear}
          aria-label="Clear search"
        >
          x
        </button>
      ) : null}
    </div>
  );
}
