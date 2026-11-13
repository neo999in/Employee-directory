def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_all_employees(client):
    response = client.get("/api/employees")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 20
    assert len(data["employees"]) <= 50


def test_search_by_name(client):
    # Backend task 2 example: GET /employees?search=rahul
    response = client.get("/api/employees?search=rahul")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 2
    for emp in data["employees"]:
        assert emp["name"].lower().startswith("rahul") or emp["department"].lower().startswith("rahul")


def test_search_is_case_insensitive(client):
    lower = client.get("/api/employees?search=rah").json()
    upper = client.get("/api/employees?search=RAH").json()
    assert lower["count"] == upper["count"] >= 2


def test_search_by_department(client):
    response = client.get("/api/employees?search=Engineering")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
    for emp in data["employees"]:
        assert emp["department"].lower().startswith("engineering") or emp["name"].lower().startswith("engineering")


def test_search_is_prefix_only(client):
    # "ahul" is inside "Rahul" but not a prefix -> no match (index-friendly prefix search)
    response = client.get("/api/employees?search=ahul")
    assert response.status_code == 200
    assert response.json()["count"] == 0


def test_search_wildcards_are_literal(client):
    # '%' and '_' must not act as LIKE wildcards
    assert client.get("/api/employees?search=%25").json()["count"] == 0
    assert client.get("/api/employees?search=_").json()["count"] == 0


def test_search_non_existent(client):
    response = client.get("/api/employees?search=nonexistentterm12345")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["employees"] == []


def test_search_whitespace_validation(client):
    response = client.get("/api/employees?search=   ")
    assert response.status_code == 400
    assert "detail" in response.json()


def test_empty_string_search_validation(client):
    res = client.get("/api/employees?search=")
    assert res.status_code == 400
    assert "Search query cannot be empty" in res.json()["detail"]


def test_search_too_long(client):
    res = client.get("/api/employees?search=" + "a" * 101)
    assert res.status_code == 422


def test_pagination_limit(client):
    response = client.get("/api/employees?limit=5")
    assert response.status_code == 200
    assert len(response.json()["employees"]) == 5


def test_invalid_query_params(client):
    response = client.get("/api/employees?limit=abc")
    assert response.status_code == 422
    assert "errors" in response.json()


def test_boundary_pagination_errors(client):
    assert client.get("/api/employees?limit=0").status_code == 422
    assert client.get("/api/employees?limit=101").status_code == 422
    assert client.get("/api/employees?offset=-5").status_code == 422


def test_get_single_employee_and_404(client):
    first_id = client.get("/api/employees?limit=1").json()["employees"][0]["id"]

    res = client.get(f"/api/employees/{first_id}")
    assert res.status_code == 200
    assert res.json()["id"] == first_id

    not_found = client.get("/api/employees/999999")
    assert not_found.status_code == 404
    assert "not found" in not_found.json()["detail"]


def test_create_employee_validation_errors(client):
    invalid_email = {
        "name": "Invalid Email User",
        "email": "not-an-email",
        "department": "QA",
        "designation": "Tester",
        "date_of_joining": "2024-01-01",
    }
    assert client.post("/api/employees", json=invalid_email).status_code == 422

    missing_field = {"name": "Missing Dept User", "email": "valid.email@company.com"}
    assert client.post("/api/employees", json=missing_field).status_code == 422


def test_create_employee_and_duplicate(client):
    payload = {
        "name": "Test Integration User",
        "email": "test.integration@company.com",
        "department": "Engineering",
        "designation": "QA Tester",
        "date_of_joining": "2024-01-15",
    }
    assert client.post("/api/employees", json=payload).status_code == 201
    dup = client.post("/api/employees", json=payload)
    assert dup.status_code == 409
    assert "already exists" in dup.json()["detail"]


def test_database_failure_returns_503(client, monkeypatch):
    from sqlalchemy.exc import OperationalError

    from app.repositories.employee_repository import EmployeeRepository

    def boom(*args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    monkeypatch.setattr(EmployeeRepository, "get_all", boom)
    res = client.get("/api/employees")
    assert res.status_code == 503
    assert "unavailable" in res.json()["detail"]
