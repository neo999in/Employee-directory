import React from "react";
import { EmployeeCard, highlightMatch, formatDate } from "./EmployeeCard.jsx";

function SkeletonCard() {
  return (
    <div className="card skeleton-card" aria-hidden="true">
      <div className="card-top">
        <div className="avatar skeleton-shimmer"></div>
        <div className="card-heading" style={{ flex: 1 }}>
          <div className="sk-bar sk-title skeleton-shimmer"></div>
          <div className="sk-bar sk-sub skeleton-shimmer"></div>
        </div>
        <div className="sk-pill skeleton-shimmer"></div>
      </div>
      <div className="card-meta">
        <div className="sk-bar sk-full skeleton-shimmer"></div>
        <div className="sk-bar sk-half skeleton-shimmer"></div>
      </div>
    </div>
  );
}

function SkeletonRow() {
  return (
    <tr className="sk-row" aria-hidden="true">
      <td>
        <div className="tbl-user">
          <div className="avatar-sm skeleton-shimmer"></div>
          <div style={{ flex: 1 }}>
            <div className="sk-bar sk-title skeleton-shimmer"></div>
            <div className="sk-bar sk-sub skeleton-shimmer"></div>
          </div>
        </div>
      </td>
      <td><div className="sk-pill skeleton-shimmer"></div></td>
      <td><div className="sk-bar sk-full skeleton-shimmer"></div></td>
      <td><div className="sk-bar sk-half skeleton-shimmer"></div></td>
      <td><div className="sk-bar sk-sub skeleton-shimmer" style={{ width: "24px" }}></div></td>
    </tr>
  );
}

export function EmployeeList({
  employees = [],
  isLoading = false,
  error = null,
  searchQuery = "",
  viewMode = "grid",
  onRetry,
  onClearSearch,
}) {
  if (error) {
    return (
      <div className="alert-banner" role="alert">
        <div className="alert-icon" aria-hidden="true">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
        </div>
        <div className="alert-body">
          <span className="alert-title">
            {error.errorType === "NETWORK_ERROR" ? "Connection error" : "Failed to load"}
          </span>
          <span className="alert-desc">{error.message}</span>
        </div>
        <div className="alert-actions">
          {onRetry && (
            <button type="button" className="btn-sm" onClick={onRetry}>
              Retry
            </button>
          )}
          {searchQuery && onClearSearch && (
            <button type="button" className="btn-sm secondary" onClick={onClearSearch}>
              Clear
            </button>
          )}
        </div>
      </div>
    );
  }

  if (isLoading && employees.length === 0) {
    return viewMode === "grid" ? (
      <div className="grid">
        {Array.from({ length: 6 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    ) : (
      <div className="tbl-wrap">
        <table className="tbl">
          <thead>
            <tr>
              <th>Employee</th>
              <th>Department</th>
              <th>Email</th>
              <th>Joined</th>
              <th>ID</th>
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: 6 }).map((_, i) => (
              <SkeletonRow key={i} />
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (employees.length === 0) {
    const isFiltered = Boolean(searchQuery.trim());
    return (
      <div className="empty-box" role="status">
        <div className="empty-icon" aria-hidden="true">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            <line x1="8" y1="11" x2="14" y2="11"></line>
          </svg>
        </div>
        <p className="empty-text">
          {isFiltered ? (
            <>No results for "{searchQuery.trim()}"</>
          ) : (
            "No employees found."
          )}
        </p>
        {isFiltered && onClearSearch && (
          <button type="button" className="btn-link" onClick={onClearSearch}>
            Clear search
          </button>
        )}
      </div>
    );
  }

  return (
    <div className={`results-wrap ${isLoading ? "is-loading" : ""}`}>
      {viewMode === "grid" ? (
        <div className="grid">
          {employees.map((emp) => (
            <EmployeeCard key={emp.id} employee={emp} highlightText={searchQuery} />
          ))}
        </div>
      ) : (
        <div className="tbl-wrap">
          <table className="tbl">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Department</th>
                <th>Email</th>
                <th>Joined</th>
                <th>ID</th>
              </tr>
            </thead>
            <tbody>
              {employees.map((emp) => {
                const initials = emp.name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")
                  .slice(0, 2)
                  .toUpperCase();

                return (
                  <tr key={emp.id}>
                    <td>
                      <div className="tbl-user">
                        <div className="avatar-sm" aria-hidden="true">
                          {initials}
                        </div>
                        <div>
                          <div className="tbl-name">{highlightMatch(emp.name, searchQuery)}</div>
                          <div className="tbl-role">{emp.designation}</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="badge">
                        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                          <path d="M12 2H2v10l9.29 9.29c.94.94 2.48.94 3.42 0l6.58-6.58c.94-.94.94-2.48 0-3.42L12 2Z"></path>
                          <path d="M7 7h.01"></path>
                        </svg>
                        <span>{highlightMatch(emp.department, searchQuery)}</span>
                      </span>
                    </td>
                    <td>
                      <a href={`mailto:${emp.email}`} className="tbl-email">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                          <rect x="2" y="4" width="20" height="16" rx="2"></rect>
                          <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path>
                        </svg>
                        <span>{emp.email}</span>
                      </a>
                    </td>
                    <td>
                      <span className="tbl-cell-inline">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                          <line x1="16" y1="2" x2="16" y2="6"></line>
                          <line x1="8" y1="2" x2="8" y2="6"></line>
                          <line x1="3" y1="10" x2="21" y2="10"></line>
                        </svg>
                        <span>{formatDate(emp.date_of_joining)}</span>
                      </span>
                    </td>
                    <td className="tbl-muted tbl-mono">#{emp.id}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
