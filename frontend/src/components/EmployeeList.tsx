import React, { useState } from "react";
import { Employee } from "../types/employee";
import { EmployeeCard } from "./EmployeeCard";
import { ApiError } from "../api/employeeApi";

interface EmployeeListProps {
  employees: Employee[];
  isLoading: boolean;
  error: ApiError | null;
  searchQuery: string;
  onRetry?: () => void;
  onClearSearch?: () => void;
}

/**
 * Skeleton placeholder card for loading state.
 */
const SkeletonCard: React.FC = () => (
  <div className="employee-card skeleton-card" aria-hidden="true">
    <div className="card-header">
      <div className="skeleton-avatar skeleton-pulse"></div>
      <div className="header-details" style={{ flex: 1 }}>
        <div className="skeleton-line skeleton-title skeleton-pulse"></div>
        <div className="skeleton-line skeleton-subtitle skeleton-pulse"></div>
      </div>
    </div>
    <div className="card-body">
      <div className="card-row">
        <div className="skeleton-line skeleton-label skeleton-pulse"></div>
        <div className="skeleton-badge skeleton-pulse"></div>
      </div>
      <div className="card-row">
        <div className="skeleton-line skeleton-label skeleton-pulse"></div>
        <div className="skeleton-line skeleton-value skeleton-pulse"></div>
      </div>
      <div className="card-row">
        <div className="skeleton-line skeleton-label skeleton-pulse"></div>
        <div className="skeleton-line skeleton-value skeleton-pulse"></div>
      </div>
    </div>
  </div>
);

export const EmployeeList: React.FC<EmployeeListProps> = ({
  employees,
  isLoading,
  error,
  searchQuery,
  onRetry,
  onClearSearch,
}) => {
  const [showTechnicalDetails, setShowTechnicalDetails] = useState<boolean>(false);

  // 1. Error State
  if (error) {
    const isNetwork = error.errorType === "NETWORK_ERROR";
    const isValidation = error.errorType === "VALIDATION_ERROR";
    const isDbUnavailable = error.errorType === "SERVICE_UNAVAILABLE";

    let title = "Failed to Load Employees";
    let guidance = "An unexpected error occurred while communicating with the server.";

    if (isNetwork) {
      title = "Server Connection Failed";
      guidance =
        "The application could not reach the backend API. Please verify the FastAPI service is running locally on http://127.0.0.1:8000 and that network/CORS settings allow the connection.";
    } else if (isValidation) {
      title = "Invalid Search Request";
      guidance = error.message;
    } else if (isDbUnavailable) {
      title = "Database Unavailable";
      guidance =
        "The backend is unable to connect to the database service. Please ensure the database file or server is accessible.";
    }

    return (
      <div className="state-container state-error" role="alert">
        <div className="state-icon">
          <svg
            width="44"
            height="44"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#ef4444"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
        </div>

        <h3 className="error-title">{title}</h3>
        <p className="error-message">{guidance}</p>

        {error.details && error.details.length > 0 && (
          <ul className="error-details-list">
            {error.details.map((detail, idx) => (
              <li key={idx}>{detail}</li>
            ))}
          </ul>
        )}

        <div className="error-actions">
          {onRetry && (
            <button type="button" className="retry-btn" onClick={onRetry}>
              Retry Request
            </button>
          )}
          {searchQuery && onClearSearch && (
            <button type="button" className="clear-filter-btn" onClick={onClearSearch}>
              Clear Search
            </button>
          )}
        </div>

        <div className="technical-details-toggle">
          <button
            type="button"
            className="text-toggle-btn"
            onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
          >
            {showTechnicalDetails ? "Hide Technical Details" : "Show Technical Details"}
          </button>
          {showTechnicalDetails && (
            <div className="technical-details-panel">
              <p><strong>Error Type:</strong> {error.errorType}</p>
              <p><strong>HTTP Status Code:</strong> {error.statusCode || "N/A"}</p>
              <p><strong>Raw Message:</strong> {error.message}</p>
            </div>
          )}
        </div>
      </div>
    );
  }

  // 2. Loading State (Skeleton loading view on initial load or search reset)
  if (isLoading && employees.length === 0) {
    return (
      <div className="loading-state-wrapper" aria-live="polite" aria-busy="true">
        <div className="loading-state-header">
          <span className="mini-spinner"></span>
          <span>Loading employee directory...</span>
        </div>
        <div className="employee-grid">
          {Array.from({ length: 6 }).map((_, index) => (
            <SkeletonCard key={index} />
          ))}
        </div>
      </div>
    );
  }

  // 3. Empty State A: Search query returned 0 results
  if (employees.length === 0 && searchQuery.trim()) {
    return (
      <div className="state-container state-empty" role="status">
        <div className="state-icon">
          <svg
            width="44"
            height="44"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#64748b"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            <line x1="8" y1="11" x2="14" y2="11"></line>
          </svg>
        </div>

        <h3>No Matching Employees Found</h3>
        <p className="empty-message">
          We could not find any employees matching{" "}
          <strong className="query-highlight">"{searchQuery.trim()}"</strong> across employee names
          or departments.
        </p>

        <div className="empty-suggestions">
          <p className="suggestions-title">Search suggestions:</p>
          <ul>
            <li>Check for spelling errors or accidental typos</li>
            <li>Try searching by department (e.g. Engineering, HR, Product, Marketing)</li>
            <li>Search using a shorter keyword or partial name</li>
          </ul>
        </div>

        {onClearSearch && (
          <button type="button" className="clear-filter-btn" onClick={onClearSearch}>
            Clear Search Filter
          </button>
        )}
      </div>
    );
  }

  // 3. Empty State B: Entire directory database has 0 records
  if (employees.length === 0) {
    return (
      <div className="state-container state-empty" role="status">
        <div className="state-icon">
          <svg
            width="44"
            height="44"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#94a3b8"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
        </div>

        <h3>Directory is Empty</h3>
        <p className="empty-message">
          There are currently no employee records available in the directory database.
        </p>

        {onRetry && (
          <button type="button" className="retry-btn" onClick={onRetry}>
            Refresh Directory
          </button>
        )}
      </div>
    );
  }

  // 4. Showing Results State
  return (
    <div className={`employee-list-section ${isLoading ? "is-updating" : ""}`}>
      {isLoading && (
        <div className="inline-updating-banner" aria-live="polite">
          <span className="mini-spinner"></span> Updating results...
        </div>
      )}
      <div
        className="employee-grid"
        role="region"
        aria-label="Employees Directory Results"
      >
        {employees.map((employee) => (
          <EmployeeCard
            key={employee.id}
            employee={employee}
            highlightText={searchQuery}
          />
        ))}
      </div>
    </div>
  );
};
