import React from "react";
import { Employee } from "../types/employee";

interface EmployeeCardProps {
  employee: Employee;
  highlightText?: string;
}

/**
 * Helper to highlight matching substrings in text.
 */
function highlightMatch(text: string, query?: string): React.ReactNode {
  if (!query || !query.trim()) return text;
  const trimmed = query.trim();
  const regex = new RegExp(`(${trimmed.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
  const parts = text.split(regex);

  return parts.map((part, i) =>
    regex.test(part) ? (
      <mark key={i} className="highlight">
        {part}
      </mark>
    ) : (
      part
    )
  );
}

function formatDate(dateString: string): string {
  try {
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return dateString;
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return dateString;
  }
}

export const EmployeeCard: React.FC<EmployeeCardProps> = ({ employee, highlightText }) => {
  // Generate a consistent avatar color based on department or initials
  const initials = employee.name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .substring(0, 2)
    .toUpperCase();

  return (
    <article className="employee-card" aria-labelledby={`emp-name-${employee.id}`}>
      <div className="card-header">
        <div className="avatar" aria-hidden="true">
          {initials}
        </div>
        <div className="header-details">
          <h3 id={`emp-name-${employee.id}`} className="employee-name">
            {highlightMatch(employee.name, highlightText)}
          </h3>
          <span className="designation">{employee.designation}</span>
        </div>
      </div>

      <div className="card-body">
        <div className="card-row">
          <span className="row-label">Department</span>
          <span className="department-badge">
            {highlightMatch(employee.department, highlightText)}
          </span>
        </div>

        <div className="card-row">
          <span className="row-label">Email</span>
          <a
            href={`mailto:${employee.email}`}
            className="employee-email"
            title={`Email ${employee.name}`}
          >
            {employee.email}
          </a>
        </div>

        <div className="card-row">
          <span className="row-label">Joined</span>
          <span className="join-date">{formatDate(employee.date_of_joining)}</span>
        </div>
      </div>

      <div className="card-footer">
        <span className="employee-id">ID: #{employee.id}</span>
      </div>
    </article>
  );
};
