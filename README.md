# 🏢 Employee Directory Search System

A high-performance, full-stack internal tool designed to search and view company employees by name or department. Built with **React + TypeScript (Vite)** on the frontend and **Python + FastAPI + SQLAlchemy** on the backend.

---

## 📋 Table of Contents
- [Architecture Overview](#-architecture-overview)
- [Project Structure](#-project-structure)
- [Requirements Fulfilled](#-requirements-fulfilled)
- [Setup & Run Instructions](#-setup--run-instructions)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#1-backend-setup-fastapi)
  - [Frontend Setup](#2-frontend-setup-react--vite)
- [Database Choice & Schema](#-database-choice--schema)
- [Search Performance Optimization](#-search-performance-optimization-conceptually--practically)
- [API Reference](#-api-reference)
- [Testing & Verification](#-testing--verification)

---

## 🏛️ Architecture Overview

The system adheres strictly to **Clean Layered Architecture** with unidirectional dependency flow:

```
[ React + Vite Client ]
       │  (Controlled & Debounced HTTP Requests with AbortSignal)
       ▼
[ FastAPI Routers ] (Request validation, status codes, query parsing)
       │
       ▼
[ Service Layer ] (Business logic, query trimming, orchestration)
       │
       ▼
[ Repository Layer ] (Data access, SQLAlchemy queries, indexing, pagination)
       │
       ▼
[ Database ] (SQLite / MySQL with B-tree indexed name & department)
```

- **Separation of Concerns:** Route handlers contain zero business logic or SQL queries. Components contain no direct `fetch` calls.
- **State Management:** Handled cleanly through custom hooks (`useEmployeeSearch`, `useDebounce`).
- **Resilience:** Centralized error handling, request cancellation for in-flight requests, and user-friendly error banners.

---

## 📂 Project Structure

```text
Employee/
├── README.md                      # Comprehensive project documentation
├── .gitignore                     # Git ignore rules for Python & Node
├── .env.example                   # Root environment configuration template
│
├── backend/                       # Python + FastAPI Backend
│   ├── .env.example               # Backend env variable template
│   ├── requirements.txt           # Python dependencies
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_employees.py      # Automated API test suite (pytest)
│   └── app/
│       ├── __init__.py
│       ├── main.py                # FastAPI entry point, CORS, lifespan & error handlers
│       ├── seed.py                # Database seeder with 20 realistic employee records
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py          # Pydantic Settings management
│       │   └── database.py        # SQLAlchemy engine, session maker, connection pooling
│       ├── models/
│       │   ├── __init__.py
│       │   └── employee.py        # Employee DB entity with indexed search columns
│       ├── schemas/
│       │   ├── __init__.py
│       │   └── employee.py        # Pydantic v2 schemas for request validation & serialization
│       ├── repositories/
│       │   ├── __init__.py
│       │   └── employee_repository.py  # Data access layer (all DB queries)
│       ├── services/
│       │   ├── __init__.py
│       │   └── employee_service.py     # Business logic & query sanitation
│       └── routers/
│           ├── __init__.py
│           └── employees.py       # API endpoints, query validation, HTTP codes
│
└── frontend/                      # React + TypeScript + Vite Frontend
    ├── .env.example               # Frontend env variable template
    ├── package.json               # Node dependencies & build scripts
    ├── tsconfig.json              # TypeScript configuration
    ├── vite.config.ts             # Vite build & dev server config
    ├── index.html                 # HTML entry point
    └── src/
        ├── main.tsx               # React root renderer
        ├── App.tsx                # Main view orchestrating search & list
        ├── App.css                # Polished, responsive component styling
        ├── index.css              # Global styles & design tokens
        ├── types/
        │   └── employee.ts        # TypeScript interfaces matching backend models
        ├── api/
        │   └── employeeApi.ts     # Dedicated API layer with AbortController support
        ├── hooks/
        │   ├── useDebounce.ts     # Custom hook to prevent rapid-fire API calls
        │   └── useEmployeeSearch.ts  # Custom hook encapsulating search state & lifecycle
        └── components/
            ├── SearchBar.tsx      # Reusable search input with status & clear button
            ├── EmployeeCard.tsx   # Reusable employee card with matching highlights
            └── EmployeeList.tsx   # State-driven renderer (loading, results, empty, error)
```

---

## ✅ Requirements Fulfilled

| Requirement Area | Specification | Implementation in this Project |
| :--- | :--- | :--- |
| **Frontend Task 1** | Controlled, debounced search (typing "Rah" must not trigger 3 calls) | `useDebounce` hook (300ms delay) + `AbortController` canceling outdated in-flight requests. |
| **Frontend Task 2** | Clear API state handling (Loading, Results, Not Found, Error) | `EmployeeList.tsx` renders dedicated, accessible UI for each state with retry & clear options. |
| **Frontend Task 3** | Reusable components & separation of API logic | Modular components (`SearchBar`, `EmployeeCard`, `EmployeeList`), `employeeApi.ts` centralized client, custom hooks. |
| **Frontend Task 4** | Environment configuration (no hardcoded URLs) | `VITE_API_BASE_URL` loaded via `.env` file across environments. |
| **Backend Task 1** | Database design & connection | SQLAlchemy declarative model, B-tree indexes, safe engine pooling with graceful session release (`yield db`). |
| **Backend Task 2** | Search API (`GET /employees?search=rahul`) | Case-insensitive `ILIKE` pattern across `name` and `department`, paginated (`limit`, `offset`), sorted. |
| **Backend Task 3** | Validation & error handling | Pydantic v2 schemas, FastAPI `Query` constraints (e.g. whitespace-only validation returning 400, invalid params returning 422, DB failure returning 503). |
| **Backend Task 4** | Clean Architecture (Routers -> Services -> Repositories) | Distinct Router, Service, and Repository layers. Easily extensible (includes `POST /employees` and `GET /employees/{id}`). |

---

## 🚀 Setup & Run Instructions

### Prerequisites
- **Python**: 3.10+ (tested on Python 3.12)
- **Node.js**: 18+ (tested on Node.js 20 LTS)

---

### 1. Backend Setup (FastAPI)

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment** (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   # Copy example env
   cp .env.example .env
   ```
   *(Default configuration uses SQLite database `employees.db` out of the box).*

5. **Start the backend server**:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```
   > 💡 *On startup, the application automatically initializes database tables and seeds 20 realistic employee records if empty.*

6. **Verify backend**:
   - Health check: [http://localhost:8000/health](http://localhost:8000/health)
   - Interactive Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 2. Frontend Setup (React + Vite)

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment variables**:
   ```bash
   # Copy example env
   cp .env.example .env
   ```
   Ensure `VITE_API_BASE_URL=http://localhost:8000/api` is present.

4. **Start Vite development server**:
   ```bash
   npm run dev
   ```

5. **Open in browser**:
   Navigate to [http://localhost:5173](http://localhost:5173).

---

## 🗄️ Database Choice & Schema

### Database Choice Rationale
The assignment states: *"Preferably MySQL"*. This solution implements a **database-agnostic architecture via SQLAlchemy ORM**:
- **Default (Zero-Friction): SQLite (`sqlite:///./employees.db`)**
  - **Zero installation dependency**: Runs anywhere with zero external daemon requirements.
  - **Identical SQL semantics**: Uses standard ANSI SQL data types and index creation.
  - Perfect for immediate evaluation, CI/CD pipelines, and local development.
- **Production MySQL Compatibility:**
  To switch to MySQL, simply update `.env`:
  ```env
  DATABASE_URL=mysql+pymysql://username:password@localhost:3306/employee_db
  ```
  The connection engine in `app/core/database.py` includes production connection pooling (`pool_pre_ping=True`, `pool_size=10`, `pool_recycle=3600`) when running against MySQL/PostgreSQL.

### Database Schema

| Column | Type | Constraints | Index | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment | Yes | Unique employee identifier |
| `name` | `VARCHAR(100)` | NOT NULL | **Yes** | Full name of the employee |
| `email` | `VARCHAR(150)` | NOT NULL, UNIQUE | Yes | Unique corporate email |
| `department` | `VARCHAR(100)` | NOT NULL | **Yes** | Department (e.g., Engineering, HR) |
| `designation` | `VARCHAR(100)` | NOT NULL | No | Job role / title |
| `date_of_joining` | `DATE` | NOT NULL | No | Date joined company |

- **Composite Index:** An index `idx_department_name` on `(department, name)` is also declared to optimize joint or grouped lookups.

---

## ⚡ Search Performance Optimization (Conceptually & Practically)

### 1. Controlled Frontend Debouncing (Eliminating Redundant Calls)
- **Problem:** In a naive implementation, typing `"Rahul"` triggers 5 separate network requests (`"R"`, `"Ra"`, `"Rah"`, `"Rahu"`, `"Rahul"`). This floods the network and database with obsolete queries.
- **Solution:** `useDebounce` delays dispatching the API call until the user pauses typing for 300ms. Typing `"Rahul"` in normal cadence issues **exactly 1 API call**.
- **Request Cancellation via `AbortController`:** If a previous request is still in-flight when a new search query is issued, the previous request is immediately aborted via browser `AbortSignal`, preventing race conditions where stale data overwrites fresh data.

### 2. Database Indexing & Query Strategy
- **Index-Powered Lookups:** Both `name` and `department` columns have B-tree indexes.
- **Optimized COUNT queries:** Total count calculation uses `func.count(Employee.id)` directly in SQL rather than loading records into memory and running `len()`.
- **Targeted Pagination:** Queries enforce `limit` (default 50, max 100) and `offset` to avoid transferring massive payloads across the wire as the employee table grows to tens of thousands of rows.
- **Projection & Row Sizing:** All fields returned are bounded in size with appropriate column limits (`VARCHAR(100)`).

---

## 🔌 API Reference

### `GET /api/employees`
Search and list employees.

**Query Parameters:**
| Parameter | Type | Required | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `search` | string | No | Search query for name or department (1-100 chars) | `rahul` |
| `limit` | integer | No | Maximum records to return (1-100, default 50) | `10` |
| `offset` | integer | No | Pagination offset (default 0) | `0` |

**Success Response (200 OK):**
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

### Validation & Error Responses:
- **`400 Bad Request`**: Sent if `search` contains only whitespace characters.
- **`422 Unprocessable Entity`**: Sent if `limit` or `offset` are invalid types or violate boundary constraints.
- **`503 Service Unavailable`**: Sent if the database connection fails.

---

## 🧪 Testing & Verification

### Running Automated Backend Tests
Run the pytest test suite:
```bash
cd backend
python -m pytest tests/ -v
```

Tests cover:
- Health check endpoint verification
- Retrieving all employees
- Search by name (e.g. `"rahul"`)
- Search by department (e.g. `"Engineering"`)
- Search case-insensitivity
- Empty/whitespace query validation (`400 Bad Request`)
- Invalid query parameters (`422 Unprocessable Entity`)
- Pagination limits
- Single employee retrieval & `404 Not Found` handling
- Extensible employee creation (`POST /api/employees`)
