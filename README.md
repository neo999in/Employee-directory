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

### Option 1: Docker (Full Stack: Frontend + Backend + MySQL)

Run the entire application in Docker containers:

```bash
docker compose up --build
```

- **Frontend App:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **Interactive API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health (200 if MySQL is reachable, 503 if not)
- **MySQL Database:** `localhost:3306` (Database: `employee_directory`, User: `employee_user`, Password: `employee_pass`)

The database is automatically initialized from `backend/schema.sql` and seeded with 20 sample employees on startup. Data is persisted in a named Docker volume (`db_data`).

Useful Docker commands:
```bash
# Run in background (detached mode)
docker compose up -d

# View logs
docker compose logs -f

# Stop containers
docker compose down

# Stop and wipe database volume (fresh start)
docker compose down -v
```

#### Hot-reload for Development (Optional)
To enable live code changes without rebuilding, create a `docker-compose.override.yml`:
```yaml
services:
  backend:
    volumes:
      - ./backend/app:/app/app:ro
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

---

### Option 2: Local / Manual Setup

#### 1. Database

```bash
mysql -u root -p < backend/schema.sql
```

Creates the `employee_directory` database and the `employees` table.

#### 2. Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate     Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # put your MySQL user/password in DATABASE_URL
uvicorn app.main:app --reload --port 8000
```

On first start, 20 sample employees are added. API docs: http://localhost:8000/docs

#### 3. Frontend

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

By default the tests use a temporary SQLite file (fast, no setup), which can't run FULLTEXT.
To test against real MySQL:

```bash
docker compose -f docker-compose.test.yml up -d --wait
cd backend
MYSQL_TEST_URL="mysql+pymysql://root:test@127.0.0.1:3307/employee_test?charset=utf8mb4" python -m pytest tests -v
docker compose -f docker-compose.test.yml down
```

## Project structure

```text
backend/app/
  routers/employees.py              HTTP layer: reads query params, calls the service
  routers/health.py                 GET /health: checks the database connection
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

1. **Word search with FULLTEXT:** terms of 3+ characters use a `FULLTEXT(name, department)` index in boolean mode:
   `MATCH(name, department) AGAINST ('+sharma* +eng*' IN BOOLEAN MODE)`. Every term must start a word,
   so "Sharma" finds "Rahul Sharma" and "resources" finds "Human Resources".
2. **Indexed prefix search for short terms:** 1-2 character terms (like "HR") are below InnoDB's minimum indexed word length (3),
   so they use `name LIKE 'hr%' OR department LIKE 'hr%'` on the normal B-tree indexes. Short terms match the *start* of the name/department only.
3. **Pagination:** results are paginated (`limit` is at most 100, `offset`), and the total is counted with `COUNT()` in SQL (`count` in the response).
4. **Safe input:** the search is split into plain word tokens, so boolean operators (`+ - * " ( )`) and `%` / `_` typed by the user can't change the query.

Notes:
- The search needs at least 2 characters (shorter returns 400; the UI just shows the full list).
- Docker MySQL runs with `--innodb-ft-enable-stopword=OFF`, otherwise words like "will" are silently ignored by FULLTEXT. On your own MySQL set `innodb_ft_enable_stopword=OFF` before the index is built.
- Existing databases get the FULLTEXT index added automatically at startup (`ensure_fulltext_index`); `schema.sql` includes it for new ones.
- The SQLite used by the quick tests only emulates word-prefix matching. The real FULLTEXT queries are tested against MySQL (see Tests).

## API

`GET /api/employees?search=rahul&limit=50&offset=0`

| Param | Rules |
|---|---|
| `search` | optional, 2–100 characters; every word must start a word in the name or department (1-2 character words match the start only) |
| `limit` | 1–100, default 50 |
| `offset` | 0 or more, default 0 |

```json
{ "count": 1, "employees": [ { "id": 1, "name": "Rahul Sharma", "email": "rahul.sharma@company.com",
  "department": "Engineering", "designation": "Staff Software Engineer", "date_of_joining": "2021-03-15" } ] }
```

`GET /health` returns `200 {"status":"healthy","database":"ok"}`, or `503 {"status":"unhealthy","database":"unreachable"}` when MySQL can't be reached.

Errors always come back as `{ "detail": "message" }`:

| Status | When |
|---|---|
| 400 | `search` is empty, only spaces, or shorter than 2 characters |
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
| BE2: efficient `GET /employees?search=` | `repositories/employee_repository.py` (FULLTEXT + indexed prefix search, pagination) |
| BE3: validation + clear errors | `routers/employees.py` (param rules), `core/exceptions.py` (400/422/503/500) |
| BE4: routers / services / repository | `routers/`, `services/`, `repositories/` |
