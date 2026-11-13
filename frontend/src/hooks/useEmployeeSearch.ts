import { useState, useEffect, useCallback, useRef } from "react";
import { Employee } from "../types/employee";
import { fetchEmployees, ApiError } from "../api/employeeApi";
import { useDebounce } from "./useDebounce";

export interface UseEmployeeSearchResult {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  debouncedQuery: string;
  employees: Employee[];
  totalCount: number;
  isLoading: boolean;
  error: string | null;
  clearSearch: () => void;
  refresh: () => void;
}

/**
 * Custom hook to manage employee search state, debouncing,
 * and API interactions cleanly outside of UI components.
 */
export function useEmployeeSearch(debounceDelayMs: number = 300): UseEmployeeSearchResult {
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Debounce the input query (e.g. typing "Rah" triggers 1 API request, not 3)
  const debouncedQuery = useDebounce(searchQuery, debounceDelayMs);

  // AbortController ref to cancel obsolete in-flight HTTP requests
  const abortControllerRef = useRef<AbortController | null>(null);

  const loadEmployees = useCallback(async (query: string) => {
    // Cancel previous request if still in flight
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetchEmployees(query, controller.signal);
      setEmployees(response.employees);
      setTotalCount(response.count);
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === "AbortError") {
        // Request was aborted because a newer keystroke/query took over; do not treat as error
        return;
      }
      if (err instanceof ApiError) {
        setError(err.message);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred while fetching employees.");
      }
      setEmployees([]);
      setTotalCount(0);
    } finally {
      // Only reset loading if this was the latest active request
      if (abortControllerRef.current === controller) {
        setIsLoading(false);
      }
    }
  }, []);

  // Trigger search whenever the debounced query changes
  useEffect(() => {
    loadEmployees(debouncedQuery);

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [debouncedQuery, loadEmployees]);

  const clearSearch = useCallback(() => {
    setSearchQuery("");
  }, []);

  const refresh = useCallback(() => {
    loadEmployees(debouncedQuery);
  }, [debouncedQuery, loadEmployees]);

  return {
    searchQuery,
    setSearchQuery,
    debouncedQuery,
    employees,
    totalCount,
    isLoading,
    error,
    clearSearch,
    refresh,
  };
}
