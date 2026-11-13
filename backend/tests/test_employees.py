import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_all_employees():
    response = client.get("/api/employees")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "employees" in data
    assert data["count"] >= 20
    assert len(data["employees"]) <= 50

def test_search_by_name():
    # As explicitly listed in backend task 2 example: GET /employees?search=rahul
    response = client.get("/api/employees?search=rahul")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 2
    for emp in data["employees"]:
        match = "rahul" in emp["name"].lower() or "rahul" in emp["department"].lower()
        assert match

def test_search_by_department():
    response = client.get("/api/employees?search=Engineering")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
    for emp in data["employees"]:
        assert "engineering" in emp["department"].lower() or "engineering" in emp["name"].lower()

def test_search_non_existent():
    response = client.get("/api/employees?search=nonexistentterm12345")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert len(data["employees"]) == 0

def test_search_whitespace_validation():
    # Whitespace only should return 400 Bad Request
    response = client.get("/api/employees?search=   ")
    assert response.status_code == 400
    assert "detail" in response.json()

def test_pagination_limit():
    response = client.get("/api/employees?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["employees"]) == 5

def test_invalid_query_params():
    # Non-integer limit should trigger 422
    response = client.get("/api/employees?limit=abc")
    assert response.status_code == 422

def test_get_single_employee_and_404():
    # Fetch first employee
    list_res = client.get("/api/employees?limit=1")
    first_id = list_res.json()["employees"][0]["id"]
    
    res = client.get(f"/api/employees/{first_id}")
    assert res.status_code == 200
    assert res.json()["id"] == first_id

    # 404 test
    not_found = client.get("/api/employees/999999")
    assert not_found.status_code == 404

def test_create_employee_extensibility():
    payload = {
        "name": "Test Integration User",
        "email": "test.integration@company.com",
        "department": "Engineering",
        "designation": "QA Tester",
        "date_of_joining": "2024-01-15"
    }
    create_res = client.post("/api/employees", json=payload)
    assert create_res.status_code in (201, 409)  # 201 on first run, 409 if already exists
