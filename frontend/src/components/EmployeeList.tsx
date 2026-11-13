import React from "react";
import { Employee } from "../types/employee";
import { EmployeeCard } from "./EmployeeCard";

interface EmployeeListProps {
  employees: Employee[];
  isLoading: boolean;
  error: string | null;
  searchQuery: string;
  onRetry?: () => void;
  onClearSearch?: () => void;
}

export const EmployeeList: React.FC<EmployeeListProps> = ({
  employees,
  isLoading,
  error,
  searchQuery,
  onRetry,
  onClearSearch,
}) => {
  // 1. Error State
  if (error) {
    return (
      <div className="state-container state-error" role="alert">
        <div className="state-icon">⚠️</div>
        <h3>Failed to Load Employees</h3>
        <p className="error-message">{error}</p>
        {onRetry && (
          <button type="button" className="retry-btn" onClick={onRetry}>
            🔄 Try Again
          </button>
        )}
      </div>
    );
  }

  // 2. Loading State (Initial or search transition)
  if (isLoading && employees.length === 0) {
    return (
      <div className="state-container state-loading" aria-live="polite">
        <div className="loader-ring"></div>
        <p className="state-title">Loading employees...</p>
        <span className="state-subtitle">Searching across departments and records</span>
      </div>
    );
  }

  // 3. No Employees Found State (Empty Result)
  if (employees.length === 0) {
    const isFiltered = Boolean(searchQuery.trim());
    return (
      <div className="state-container state-empty" role="status">
        <div className="state-icon">{isFiltered ? "🔍" : "👥"}</div>
        <h3>{isFiltered ? "No matching employees found" : "No employees in directory"}</h3>
        <p className="empty-message">
          {isFiltered ? (
            <>
              We couldn't find any employees matching <strong>"{searchQuery.trim()}"</strong> by
              name or department.
            </>
          ) : (
            "The employee directory is currently empty."
          )}
        </p>
        {isFiltered && onClearSearch && (
          <button type="button" className="clear-filter-btn" onClick={onClearSearch}>
            Clear Search
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
