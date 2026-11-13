import { useState, useEffect, useCallback, useRef } from "react";
import { fetchEmployees, ApiError } from "../api/employeeApi.js";
import { useDebounce } from "./useDebounce.js";

export function useEmployeeSearch(debounceDelayMs = 300) {
  const [searchQuery, setSearchQuery] = useState("");
  const [employees, setEmployees] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const debouncedQuery = useDebounce(searchQuery, debounceDelayMs);
  const abortControllerRef = useRef(null);

  const loadEmployees = useCallback(async (query) => {
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
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") {
        return;
      }
      if (err instanceof ApiError) {
        setError(err);
      } else if (err instanceof Error) {
        setError(new ApiError(err.message, 0, "UNKNOWN_ERROR"));
      } else {
        setError(new ApiError("An unexpected error occurred while fetching employees.", 0, "UNKNOWN_ERROR"));
      }
      setEmployees([]);
      setTotalCount(0);
    } finally {
      if (abortControllerRef.current === controller) {
        setIsLoading(false);
      }
    }
  }, []);

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
