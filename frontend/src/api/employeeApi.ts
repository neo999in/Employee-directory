import { EmployeeSearchResponse } from "../types/employee";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export class ApiError extends Error {
  statusCode: number;

  constructor(message: string, statusCode: number) {
    super(message);
    this.name = "ApiError";
    this.statusCode = statusCode;
  }
}

/**
 * Centralized API client service.
 * Keeps all network requests out of UI components.
 */
export async function fetchEmployees(
  searchQuery: string = "",
  signal?: AbortSignal
): Promise<EmployeeSearchResponse> {
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
      let errorMessage = `Server error (${response.status})`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = typeof errorData.detail === "string"
            ? errorData.detail
            : JSON.stringify(errorData.detail);
        }
      } catch {
        // Fallback to response.statusText if body is not JSON
        if (response.statusText) {
          errorMessage = `${response.status} - ${response.statusText}`;
        }
      }
      throw new ApiError(errorMessage, response.status);
    }

    return (await response.json()) as EmployeeSearchResponse;
  } catch (error: unknown) {
    if (error instanceof ApiError) {
      throw error;
    }
    if (error instanceof DOMException && error.name === "AbortError") {
      throw error; // Re-throw abort to be handled by caller
    }
    // Network disconnection or CORS failure
    throw new Error(
      "Unable to connect to the backend server. Please verify the backend is running and CORS is configured."
    );
  }
}
