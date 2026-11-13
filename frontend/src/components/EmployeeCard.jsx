import React from "react";

export function highlightMatch(text, query) {
  if (!query || !query.trim()) return text;
  const trimmed = query.trim();
  const regex = new RegExp(`(${trimmed.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
  const parts = String(text).split(regex);

  return parts.map((part, i) =>
    regex.test(part) ? (
      <mark key={i} className="hl">
        {part}
      </mark>
    ) : (
      part
    )
  );
}

export function formatDate(dateString) {
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

export function EmployeeCard({ employee, highlightText }) {
  const initials = employee.name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <div className="card">
      <div className="card-top">
        <div className="avatar" aria-hidden="true">
          {initials}
        </div>
        <div className="card-heading">
          <h3 className="card-name">{highlightMatch(employee.name, highlightText)}</h3>
          <span className="card-title">{employee.designation}</span>
        </div>
        <span className="badge">
          <span>{highlightMatch(employee.department, highlightText)}</span>
        </span>
      </div>

      <div className="card-meta">
        <div className="meta-row">
          <span className="meta-label">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <rect x="2" y="4" width="20" height="16" rx="2"></rect>
              <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path>
            </svg>
            <span>Email</span>
          </span>
          <a href={`mailto:${employee.email}`} className="meta-link">
            {employee.email}
          </a>
        </div>
        <div className="meta-row">
          <span className="meta-label">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            <span>Joined</span>
          </span>
          <span className="meta-val">{formatDate(employee.date_of_joining)}</span>
        </div>
      </div>
    </div>
  );
}
