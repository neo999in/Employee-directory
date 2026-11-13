import { useEffect, useState } from "react";
import { fetchEmployees } from "../api/employeeApi.js";
import { useDebounce } from "./useDebounce.js";

// All search state + API logic lives here, so the components only render.
export function useEmployeeSearch(debounceMs = 300) {
  const [searchQuery, setSearchQuery] = useState("");
  const [employees, setEmployees] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  const debouncedQuery = useDebounce(searchQuery, debounceMs);

  useEffect(() => {
    // If a newer search starts, cancel this one so old results never overwrite new ones.
    const controller = new AbortController();

    setIsLoading(true);
    setError(null);

    fetchEmployees(debouncedQuery, controller.signal)
      .then((data) => {
        setEmployees(data.employees);
        setTotalCount(data.count);
        setIsLoading(false);
      })
      .catch((err) => {
        if (err.name === "AbortError") return;
        setError(err); // err.message is shown to the user
        setEmployees([]);
        setTotalCount(0);
        setIsLoading(false);
      });

    return () => controller.abort();
  }, [debouncedQuery, retryCount]);

  const clearSearch = () => setSearchQuery("");
  const refresh = () => setRetryCount((n) => n + 1);

  return { searchQuery, setSearchQuery, employees, totalCount, isLoading, error, clearSearch, refresh };
}
