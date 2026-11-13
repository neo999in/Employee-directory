const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export class ApiError extends Error {
  constructor(message, statusCode, errorType, details) {
    super(message);
    this.name = "ApiError";
    this.statusCode = statusCode;
    this.errorType = errorType;
    this.details = details;
  }
}

export async function fetchEmployees(searchQuery = "", signal) {
  const params = new URLSearchParams();
  const trimmed = searchQuery.trim();
  if (trimmed) {
    params.set("search", trimmed);
  }

  const queryString = params.toString();
  const endpoint = queryString
    ? `${API_BASE_URL}/employees?${queryString}`
    : `${API_BASE_URL}/employees`;

  try {
    const response = await fetch(endpoint, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
      signal,
    });

    if (!response.ok) {
      let errorMessage = `Server responded with status ${response.status}`;
      let errorType = "SERVER_ERROR";
      let details;

      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = typeof errorData.detail === "string"
            ? errorData.detail
            : JSON.stringify(errorData.detail);
        }
        if (Array.isArray(errorData.errors)) {
          details = errorData.errors;
        }
      } catch {
        if (response.statusText) {
          errorMessage = `${response.status} - ${response.statusText}`;
        }
      }

      if (response.status === 400 || response.status === 422) {
        errorType = "VALIDATION_ERROR";
      } else if (response.status === 404) {
        errorType = "NOT_FOUND";
      } else if (response.status === 503) {
        errorType = "SERVICE_UNAVAILABLE";
      } else if (response.status >= 500) {
        errorType = "SERVER_ERROR";
      }

      throw new ApiError(errorMessage, response.status, errorType, details);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    if (error instanceof DOMException && error.name === "AbortError") {
      throw error;
    }

    throw new ApiError(
      "Unable to connect to the backend server. Please verify the backend service is running at " +
        API_BASE_URL,
      0,
      "NETWORK_ERROR"
    );
  }
}
