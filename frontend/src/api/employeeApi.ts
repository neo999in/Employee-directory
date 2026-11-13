import { EmployeeSearchResponse } from "../types/employee";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export type ApiErrorType =
  | "NETWORK_ERROR"
  | "VALIDATION_ERROR"
  | "SERVER_ERROR"
  | "SERVICE_UNAVAILABLE"
  | "NOT_FOUND"
  | "UNKNOWN_ERROR";

export class ApiError extends Error {
  public readonly statusCode: number;
  public readonly errorType: ApiErrorType;
  public readonly details?: string[];

  constructor(
    message: string,
    statusCode: number,
    errorType: ApiErrorType,
    details?: string[]
  ) {
    super(message);
    this.name = "ApiError";
    this.statusCode = statusCode;
    this.errorType = errorType;
    this.details = details;
  }
}

/**
 * Centralized API client service.
 * Keeps all network requests out of UI components and provides robust error parsing.
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
      let errorMessage = `Server responded with status ${response.status}`;
      let errorType: ApiErrorType = "SERVER_ERROR";
      let details: string[] | undefined;

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

    return (await response.json()) as EmployeeSearchResponse;
  } catch (error: unknown) {
    if (error instanceof ApiError) {
      throw error;
    }
    if (error instanceof DOMException && error.name === "AbortError") {
      throw error;
    }

    // Network disconnection or server offline
    throw new ApiError(
      "Unable to connect to the backend server. Please verify the backend service is running at " +
        API_BASE_URL +
        " and that CORS origins are properly configured.",
      0,
      "NETWORK_ERROR"
    );
  }
}
