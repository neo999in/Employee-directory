// The ONLY file that calls the backend.
// The base URL comes from the environment (frontend/.env) - never hardcoded.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function fetchEmployees(search, signal) {
  if (!API_BASE_URL) {
    throw new Error("VITE_API_BASE_URL is not set. Add it to frontend/.env and restart.");
  }

  const params = new URLSearchParams();
  if (search.trim()) params.set("search", search.trim());

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
