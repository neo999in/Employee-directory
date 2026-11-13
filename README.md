# Employee Directory

A small internal tool to search employees by **name** or **department**.

- **Frontend:** React + Vite
- **Backend:** Python + FastAPI (SQLAlchemy)
- **Database:** MySQL

## How it works (in one picture)

```text
Browser (React)                          Backend (FastAPI)                    MySQL
SearchBar -> useEmployeeSearch -> api ── GET /api/employees?search=rah ──> router -> service -> repository ──> employees table
             (debounce + cancel)                                           (HTTP)    (rules)   (SQL only)
```

## Setup

### 1. Database

```bash
mysql -u root -p < backend/schema.sql
```

Creates the `employee_directory` database and the `employees` table.

### 2. Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate     Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # put your MySQL user/password in DATABASE_URL
uvicorn app.main:app --reload --port 8000
```

On first start, 20 sample employees are added. API docs: http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env              # VITE_API_BASE_URL=http://localhost:8000/api
npm run dev
```

Open http://localhost:5173

### Tests

```bash
cd backend
python -m pytest tests -v
```

The tests use a temporary SQLite file, so they don't need MySQL.

## Project structure

```text
backend/app/
  routers/employees.py              HTTP layer: reads query params, calls the service
  services/employee_service.py      business rules (e.g. "search can't be empty")
  repositories/employee_repository.py  the only place with database queries
  models/employee.py                employees table (SQLAlchemy)
  schemas/employee.py               response shape (Pydantic)
  core/config.py                    settings from environment variables
  core/database.py                  connection pool + one session per request
  core/exceptions.py                turns errors into clear JSON + status codes
  seed.py                           sample data
backend/schema.sql                  MySQL table definition

frontend/src/
  api/employeeApi.js                the only file that calls the backend
  hooks/useDebounce.js              waits until the user stops typing
  hooks/useEmployeeSearch.js        search state + API calls (loading / error / results)
  components/SearchBar.jsx          input box (spinner while loading, clear button)
  components/EmployeeList.jsx       shows loading (skeletons) / error / empty / results (grid or table)
  components/EmployeeCard.jsx       one employee card (search match highlighted)
  components/ErrorBoundary.jsx      catches unexpected UI crashes
  App.jsx                           navbar (count, grid/list toggle, dark mode) + search + list
```

## Database choice

**MySQL**, as the assignment prefers it, and the data is a simple, structured table.

The `employees` table (`backend/schema.sql`) has:

- `id` as the primary key, `email` as `UNIQUE`
- **indexes on `name` and `department`**, the two columns we search
- the `utf8mb4_unicode_ci` collation, so searches ignore case without needing `LOWER()`

**How we connect** (`backend/app/core/database.py`): a SQLAlchemy engine with a **connection pool**,
and **one session per request**.

Why this approach is suitable:

- **Fast:** connections are reused instead of reconnecting on every request.
- **Scalable:** the pool limits how many connections we open, so MySQL isn't overloaded under heavy traffic.
- **Reliable:** `pool_pre_ping` and `pool_recycle` replace dead or old connections automatically.
- **Safe:** queries are parameterized, which prevents SQL injection, and the credentials are only in `.env`.

## How search performance is optimized

**Frontend: fewer requests**

1. **Debounce (300 ms):** a request is sent only after the user stops typing.
   Typing "Rah" sends **1** request, not 3.
2. **Cancel old requests:** if a new search starts, the old request is aborted (`AbortController`),
   so slow, outdated responses can't overwrite newer results.
3. Old results stay on screen while new ones load, so the list doesn't flicker. Skeleton cards show only when there are no results on screen yet.

**Backend: cheaper queries**

1. **Indexed prefix search:** `WHERE name LIKE 'rah%' OR department LIKE 'rah%'`.
   With no `%` at the start, MySQL can use the index and doesn't need to scan the whole table, so search stays fast as the table grows.
   (`'%rah%'` would force a full table scan.)
2. **Only the data we need:** results are paginated (`limit` is at most 100, `offset`), and the total is counted with `COUNT()` in SQL.
3. User input such as `%` or `_` is escaped, so it can't turn into a slow wildcard search.

Trade-off: "Rah" finds "Rahul Sharma", but "Sharma" does not, because it isn't at the start.
If that's needed later, the next step is a MySQL `FULLTEXT` index.

## API

`GET /api/employees?search=rahul&limit=50&offset=0`

| Param | Rules |
|---|---|
| `search` | optional, 1–100 characters; matches the start of the name or department |
| `limit` | 1–100, default 50 |
| `offset` | 0 or more, default 0 |

```json
{ "count": 2, "employees": [ { "id": 1, "name": "Rahul Sharma", "email": "rahul.sharma@company.com",
  "department": "Engineering", "designation": "Staff Software Engineer", "date_of_joining": "2021-03-15" } ] }
```

Errors always come back as `{ "detail": "message" }`:

| Status | When |
|---|---|
| 400 | `search` is empty or only spaces |
| 422 | invalid parameters (e.g. `limit=abc`, `limit=500`) |
| 503 | the database can't be reached |
| 500 | any other database error (internal details are not shown) |

## Configuration

Nothing is hardcoded. Each app reads a `.env` file; copy the `.env.example` files to create them.

| Variable | App | Purpose |
|---|---|---|
| `DATABASE_URL` | backend | MySQL connection string |
| `CORS_ORIGINS` | backend | frontend URL(s) allowed to call the API |
| `VITE_API_BASE_URL` | frontend | backend API URL |
| `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_RECYCLE_SECONDS` | backend | optional: connection pool tuning |
| `SEED_ON_STARTUP` | backend | optional: add sample data when the table is empty (default `true`) |

To run in another environment (dev, staging, prod), change these values. No code changes are needed.

## Extending

To add a feature such as "create employee", add one method in each layer:
`repository.create()` → `service.create_employee()` → a `POST` route in the router.
Nothing else has to change.

## Assignment checklist

| Requirement | Where |
|---|---|
| FE1: debounced, controlled search | `hooks/useDebounce.js`, `hooks/useEmployeeSearch.js` (debounce + abort) |
| FE2: loading / results / no results / error | `components/EmployeeList.jsx` |
| FE3: reusable components, no API logic in UI | `SearchBar`, `EmployeeCard`, `EmployeeList`; API calls are only in `api/` + `hooks/` |
| FE4: API URL from env | `VITE_API_BASE_URL` in `api/employeeApi.js` |
| BE1: MySQL table + safe, scalable connection | `schema.sql`, `core/database.py` |
| BE2: efficient `GET /employees?search=` | `repositories/employee_repository.py` (indexed prefix search, pagination) |
| BE3: validation + clear errors | `routers/employees.py` (param rules), `core/exceptions.py` (400/422/503/500) |
| BE4: routers / services / repository | `routers/`, `services/`, `repositories/` |
