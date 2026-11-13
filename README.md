# Employee Directory

Internal tool to search and view employees by name or department. Built with React (Vite) and FastAPI.

## Tech Stack

- Frontend: React 18, JavaScript (JSX), Vite
- Backend: Python 3.12, FastAPI, SQLAlchemy 2
- Database: SQLite (default, zero configuration) or MySQL

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+

### 1. Backend

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

The database automatically initializes and populates 20 seed records on first launch.

- API base URL: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173` in your browser.

## Project Structure

```text
Employee/
|-- backend/
|   |-- app/
|   |   |-- core/          # database engine, session factory, settings
|   |   |-- models/        # SQLAlchemy ORM models with indexes
|   |   |-- repositories/  # database queries and data access layer
|   |   |-- routers/       # route handlers and query validation
|   |   |-- schemas/       # pydantic request/response models
|   |   |-- services/      # business logic
|   |   |-- main.py        # application entry, CORS, lifespan
|   |   `-- seed.py        # initial dataset
|   |-- tests/             # pytest test suite
|   |-- requirements.txt
|   `-- .env.example
|-- frontend/
|   |-- src/
|   |   |-- api/           # API client and typed error handling
|   |   |-- components/    # SearchBar, EmployeeCard, EmployeeList, ErrorBoundary
|   |   |-- hooks/         # useDebounce, useEmployeeSearch
|   |   |-- App.jsx
|   |   `-- main.jsx
|   |-- package.json
|   `-- .env.example
`-- README.md
```

## Architecture and Design Decisions

### Backend Layering

Code is organized in four distinct tiers to keep responsibilities separate:

1. Routers (`app/routers/`): Parse HTTP requests, validate query parameters via FastAPI/Pydantic, and return status codes. No business logic or database queries live here.
2. Services (`app/services/`): Handle application rules, string sanitization, and workflow orchestration.
3. Repositories (`app/repositories/`): The only layer that executes SQL. Contains all SQLAlchemy queries, pagination, and count operations.
4. Schemas (`app/schemas/`): Pydantic models for validation and serialization.

### Database Selection

The prompt specifies "Preferably MySQL". This project defaults to SQLite via SQLAlchemy:
- Zero installation overhead: works immediately for evaluation without running external database services.
- Standard SQL schema: switching to MySQL requires only changing `DATABASE_URL` in `backend/.env`:
  ```env
  DATABASE_URL=mysql+pymysql://user:password@localhost:3306/employee_directory
  ```
- Connection pooling (`pool_pre_ping`, `pool_size`, `pool_recycle`) is already configured in `app/core/database.py` for MySQL and PostgreSQL.

### Search Performance

1. Frontend Debouncing:
   - Keystrokes are buffered with a 300ms debounce window (`useDebounce.js`).
   - Typing "Rah" triggers a single request once typing pauses, rather than 3 individual requests.
   - Pending in-flight requests are automatically canceled using `AbortController` if the user continues typing.

2. Database Querying:
   - The `name` and `department` columns carry B-tree indexes (`models/employee.py`).
   - Search uses `ILIKE` patterns across indexed fields.
   - Total count queries use `func.count(Employee.id)` directly in SQL rather than loading records into application memory.
   - Pagination parameters (`limit` and `offset`) prevent large payload transfers.

## API Reference

### `GET /api/employees`

Search or list employees.

Parameters:
- `search` (optional string, max 100): Filter by name or department.
- `limit` (optional int, 1-100, default 50): Number of records per page.
- `offset` (optional int, default 0): Number of records to skip.

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
    },
    {
      "id": 3,
      "name": "Rahul Verma",
      "email": "rahul.verma@company.com",
      "department": "Product",
      "designation": "Principal Product Manager",
      "date_of_joining": "2022-01-10"
    }
  ]
}
```

Error Status Codes:
- `400 Bad Request`: Empty or whitespace-only search string.
- `422 Unprocessable Entity`: Invalid query parameter types or out-of-range bounds.
- `503 Service Unavailable`: Database operational error.

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```
