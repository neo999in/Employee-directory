import { useEffect, useState } from "react";

// Returns `value` only after it has stopped changing for `delay` ms.
// Typing "Rah" quickly => one update ("Rah"), not three.
export function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer); // a new keystroke cancels the previous timer
  }, [value, delay]);

  return debounced;
}
