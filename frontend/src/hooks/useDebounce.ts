import { useState, useEffect } from "react";

/**
 * Custom hook to debounce any fast-changing value.
 * Delays updating the returned value until `delay` milliseconds
 * have elapsed since the last time the input value changed.
 *
 * @param value The value to debounce (e.g. search input text)
 * @param delay Milliseconds to wait before updating (default 300ms)
 * @returns The debounced value
 */
export function useDebounce<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
