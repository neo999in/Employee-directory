// The ONLY file that calls the backend.
// The base URL comes from the environment (frontend/.env) - never hardcoded.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const MIN_SEARCH_LENGTH = 2;

export async function fetchEmployees(search, signal) {
  if (!API_BASE_URL) {
    throw new Error("VITE_API_BASE_URL is not set. Add it to frontend/.env and restart.");
  }

  const params = new URLSearchParams();
  // The backend needs at least 2 characters; with 0-1 typed we just show the full list.
  if (search.trim().length >= MIN_SEARCH_LENGTH) params.set("search", search.trim());

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/employees?${params}`, { signal });
  } catch (err) {
    if (err.name === "AbortError") throw err; // request was cancelled on purpose
    const networkError = new Error("Cannot reach the server. Please check that the backend is running.");
    networkError.errorType = "NETWORK_ERROR"; // lets the UI show "Connection error"
    throw networkError;
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    // The backend always sends a readable message in "detail".
    throw new Error(data.detail || `Request failed (${response.status})`);
  }
  return data; // { count, employees }
}
