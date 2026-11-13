# Employee Directory

Internal tool to search and view employees by name or department.
React (Vite) frontend, FastAPI backend, MySQL database.

## Tech Stack

- Frontend: React 18, Vite
- Backend: Python 3.10+, FastAPI, SQLAlchemy 2, PyMySQL
- Database: MySQL 8

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- MySQL 8 running locally (or reachable over the network)

### 1. Database

```bash
mysql -u root -p < backend/schema.sql
```

This creates the `employee_directory` database and the `employees` table.
(The backend also runs `CREATE TABLE IF NOT EXISTS` on startup, so only the
database itself strictly needs to exist.)

### 2. Backend

```bash
cd backend
python -m venv venv
# Windows: .\venv\Scripts\activate    Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then fill in your MySQL user/password
python -m uvicorn app.main:app --reload --port 8000
```

On first start, 20 sample employees are seeded (disable with `SEED_ON_STARTUP=false`).

- API: `http://localhost:8000/api/employees`
- Interactive docs: `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env        # VITE_API_BASE_URL points at the backend
npm run dev
```

Open `http://localhost:5173`.

### Tests

```bash
cd backend
python -m pytest tests/ -v
```

Tests run against a temporary SQLite file (configured in `tests/conftest.py`), so they need no MySQL instance.

## Configuration

No URLs or credentials are hardcoded; everything comes from environment variables.

| Variable | Where | Purpose |
|---|---|---|
| `DATABASE_URL` | backend | SQLAlchemy URL, e.g. `mysql+pymysql://user:pass@host:3306/employee_directory?charset=utf8mb4` (required) |
| `CORS_ORIGINS` | backend | Comma-separated allowed frontend origins (required) |
| `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_RECYCLE_SECONDS` | backend | Connection pool tuning (optional) |
| `SEED_ON_STARTUP` | backend | Seed sample data when the table is empty (default `true`) |
| `VITE_API_BASE_URL` | frontend | Backend API base URL (required; the UI shows a clear error if missing) |

Different environments (dev / staging / prod) only need different `.env` values or build-time env vars; no code changes.

## Project Structure

```text
backend/
  app/
    core/          config (env settings), database (engine/pool/session), exceptions (domain errors -> HTTP)
    models/        SQLAlchemy ORM model for the employees table
    repositories/  all SQL / data access
    services/      business rules (validation, uniqueness), HTTP-agnostic
    routers/       thin HTTP layer: parse params, call service
    schemas/       Pydantic request/response models
    main.py        app wiring: CORS, exception handlers, lifespan
    seed.py        sample data
  tests/
  schema.sql       MySQL DDL
  .env.example
frontend/
  src/
    api/           API client + typed ApiError (only place that calls fetch)
    hooks/         useDebounce, useEmployeeSearch (request logic + state)
    components/    SearchBar, EmployeeCard, EmployeeList, ErrorBoundary (presentational)
  .env.example
```

## Database Choice and Connection

**MySQL** was chosen as the assignment prefers it, and because it fits the data: a single,
well-structured relational table with uniqueness constraints and indexed lookups.

Table design (`backend/schema.sql`):

- `id` INT auto-increment primary key
- `email` has a `UNIQUE` constraint (no duplicate employees, fast lookup when creating)
- B-tree indexes on `name` and `department`, the two searched columns
- `utf8mb4` + `utf8mb4_unicode_ci` collation: full Unicode names, and case-insensitive
  comparisons natively, which matters for search performance (see below)

**Connection approach** (`backend/app/core/database.py`): SQLAlchemy engine with a connection pool
and one session per request via a FastAPI dependency.

Why this is suitable:

- **Scalable**: pooled connections are reused instead of opening a new TCP + auth handshake per
  request; `pool_size` + `max_overflow` cap total connections, so traffic spikes can't exhaust
  MySQL's `max_connections`.
- **Resilient**: `pool_pre_ping` detects connections MySQL has dropped (e.g. after `wait_timeout`)
  and replaces them transparently; `pool_recycle` refreshes connections before they go stale.
- **Safe**: all queries are parameterized through the ORM (no SQL injection); credentials only
  live in `DATABASE_URL`; each request's session is always closed and returned to the pool, even on errors.

## How Search Performance Is Optimized

### Frontend: controlled requests

- **Debounce (300 ms)**: `useDebounce` waits until the user pauses typing. Typing "Rah" sends one
  request, not three.
- **Cancellation**: `useEmployeeSearch` aborts the in-flight request (`AbortController`) when a new
  one starts, so stale responses can never overwrite newer results and the browser doesn't wait on
  outdated calls.
- Previous results stay on screen while a new search loads, so the list updates smoothly instead of flashing.

### Backend: index-friendly queries

- **Prefix matching**: search uses `name LIKE 'rah%' OR department LIKE 'rah%'`.
  A pattern with no leading wildcard is a range scan on the B-tree index (O(log n)), while
  `LIKE '%rah%'` would force a full table scan that gets slower as the table grows.
  MySQL can combine both column indexes for the `OR` (index merge).
- **No functions on indexed columns**: plain `LIKE` is used instead of `ILIKE`/`LOWER(col)`, which
  would disable the index. Case-insensitivity comes from the `_ci` collation.
- **Wildcards in user input are escaped**, so typing `%` or `_` can't turn a search into a full scan.
- **Pagination** (`limit` ≤ 100, `offset`) bounds every response, and `COUNT(id)` runs in SQL rather
  than loading rows into memory.
- Each search runs two indexed queries (the page of rows + the total count). Both use the same
  index range, so the count is cheap; at very large scale the count could be made optional or
  replaced with a "has more" flag (fetch `limit + 1` rows) to save the second query.

Trade-off: prefix search matches the *start* of a name or department ("Rah" → "Rahul Sharma",
"Eng" → "Engineering") but not a word in the middle ("Sharma"). If that becomes a requirement, the
scalable next step is a MySQL `FULLTEXT` index on (`name`, `department`) queried with
`MATCH ... AGAINST` in boolean mode, rather than `%term%` scans.

## API Reference

### `GET /api/employees`

| Param | Type | Rules |
|---|---|---|
| `search` | string, optional | 1–100 chars after trimming; prefix match on name or department, case-insensitive. Omit to list all. |
| `limit` | int, optional | 1–100, default 50 |
| `offset` | int, optional | ≥ 0, default 0 |

Response `200 OK`:

```json
{
  "count": 2,
  "employees": [
    {
      "id": 1,
      "name": "Rahul Sharma",
      "email": "rahul.sharma@company.com",
      "department": "Engineering",
      "designation": "Staff Software Engineer",
      "date_of_joining": "2021-03-15"
    }
  ]
}
```

### `GET /api/employees/{id}` and `POST /api/employees`

Included to show the architecture extends cleanly (adding creation touched only the repository,
service and router, one method each).

### Errors

All errors return JSON with a `detail` message, mapped centrally in `app/core/exceptions.py`:

| Status | When |
|---|---|
| `400 Bad Request` | `search` is empty or whitespace only |
| `404 Not Found` | Employee ID does not exist |
| `409 Conflict` | Creating an employee with an existing email |
| `422 Unprocessable Entity` | Invalid/out-of-range params or body (`errors` lists each problem) |
| `503 Service Unavailable` | Database unreachable |
| `500 Internal Server Error` | Other database errors (no internal details leaked) |
