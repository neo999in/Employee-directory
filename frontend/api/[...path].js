// Vercel serverless proxy: forwards /api/* to the backend.
// The backend address lives in the BACKEND_URL environment variable
// (Vercel project settings), so it is never stored in the repository.
// Read-only on purpose: the frontend only ever issues GET requests.
export default async function handler(req, res) {
  const base = process.env.BACKEND_URL;
  if (!base) {
    return res.status(500).json({ detail: "BACKEND_URL is not configured." });
  }
  if (req.method !== "GET" && req.method !== "HEAD") {
    res.setHeader("Allow", "GET, HEAD");
    return res.status(405).json({ detail: "Method not allowed." });
  }

  try {
    const upstream = await fetch(base.replace(/\/+$/, "") + req.url, {
      method: req.method,
      headers: { accept: "application/json" },
      signal: AbortSignal.timeout(15000),
    });
    res.status(upstream.status);
    res.setHeader(
      "content-type",
      upstream.headers.get("content-type") || "application/json"
    );
    res.send(Buffer.from(await upstream.arrayBuffer()));
  } catch {
    res.status(502).json({ detail: "Backend unreachable." });
  }
}
