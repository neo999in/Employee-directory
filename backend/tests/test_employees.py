from datetime import date

import pytest


@pytest.fixture(scope="module")
def extra_employees(client):
    from app.core.database import SessionLocal
    from app.models.employee import Employee

    rows = [
        ("Will Turner", "will.turner@company.com"),
        ("Anne-Marie Cole", "anne.cole@company.com"),
    ]
    with SessionLocal() as db:
        for name, email in rows:
            db.add(Employee(name=name, email=email, department="Support", designation="Agent", date_of_joining=date(2024, 1, 1)))
        db.commit()


def _names(response):
    return [e["name"] for e in response.json()["employees"]]


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "ok"}


def test_health_check_reports_database_down(client):
    from sqlalchemy.exc import OperationalError

    from app.core.database import get_db

    class BrokenSession:
        def execute(self, *args, **kwargs):
            raise OperationalError("SELECT 1", {}, Exception("connection refused"))

        def close(self):
            pass

    client.app.dependency_overrides[get_db] = lambda: BrokenSession()
    try:
        response = client.get("/health")
    finally:
        client.app.dependency_overrides.pop(get_db, None)
    assert response.status_code == 503
    assert response.json() == {"status": "unhealthy", "database": "unreachable"}


def test_get_all_employees(client):
    response = client.get("/api/employees")
    assert response.status_code == 200
    assert response.json()["count"] == 20
    assert len(response.json()["employees"]) == 20


def test_search_by_first_name(client):
    res = client.get("/api/employees?search=rahul")
    assert res.status_code == 200
    assert _names(res) == ["Rahul Sharma", "Rahul Verma"]


def test_search_by_last_name_finds_full_name(client):
    # The reason for FULLTEXT: "Sharma" is not at the start of "Rahul Sharma".
    assert _names(client.get("/api/employees?search=sharma")) == ["Rahul Sharma"]


def test_search_word_prefix(client):
    assert _names(client.get("/api/employees?search=shar")) == ["Rahul Sharma"]


def test_search_is_case_insensitive(client):
    assert _names(client.get("/api/employees?search=SHARMA")) == ["Rahul Sharma"]


def test_search_multiple_words_must_all_match(client):
    assert _names(client.get("/api/employees?search=rahul sharma")) == ["Rahul Sharma"]
    assert _names(client.get("/api/employees?search=sharma verma")) == []


def test_search_name_and_department_words_combine(client):
    assert _names(client.get("/api/employees?search=priya engineering")) == ["Priya Patel"]


def test_search_by_department(client):
    res = client.get("/api/employees?search=Engineering")
    assert res.status_code == 200
    assert len(res.json()["employees"]) == 5
    assert all(e["department"] == "Engineering" for e in res.json()["employees"])


def test_search_department_second_word(client):
    # "Resources" is the 2nd word of "Human Resources".
    employees = client.get("/api/employees?search=resources").json()["employees"]
    assert len(employees) == 2
    assert {e["department"] for e in employees} == {"Human Resources"}


def test_two_character_term_uses_prefix_match(client):
    # Below the FULLTEXT minimum token size (3) -> indexed prefix search on name/department.
    assert _names(client.get("/api/employees?search=Hu")) == ["Amitabh Sen", "Sneha Kulkarni"]  # dept "Human Resources"
    assert _names(client.get("/api/employees?search=ra")) == ["Rahul Sharma", "Rahul Verma"]


def test_two_character_term_is_not_a_word_search(client):
    assert _names(client.get("/api/employees?search=ha")) == []  # "Sharma" contains "ha" but doesn't start with it


def test_short_term_combined_with_long_term(client):
    assert _names(client.get("/api/employees?search=rahul sh")) == []  # no name/department *starts* with "sh"
    assert _names(client.get("/api/employees?search=rahul ra")) == ["Rahul Sharma", "Rahul Verma"]


def test_common_english_words_are_not_dropped(client, extra_employees):
    # "will" is on InnoDB's default stopword list; docker-compose turns the list off.
    assert _names(client.get("/api/employees?search=will")) == ["Will Turner"]


def test_hyphenated_names(client, extra_employees):
    assert _names(client.get("/api/employees?search=marie")) == ["Anne-Marie Cole"]


def test_boolean_operators_in_input_are_harmless(client):
    for q in ["-rahul", "+rahul*", "rahul*", '"rahul sharma"', "(rahul)", "@@", "<>~~"]:
        assert client.get("/api/employees", params={"search": q}).status_code == 200
    # "-" is stripped, not interpreted as NOT.
    assert _names(client.get("/api/employees", params={"search": "rahul -sharma"})) == ["Rahul Sharma"]


def test_search_wildcards_are_literal(client):
    assert client.get("/api/employees?search=%25%25").json()["employees"] == []
    assert client.get("/api/employees?search=__").json()["employees"] == []


def test_count_is_total_matches_not_page_size(client):
    body = client.get("/api/employees?limit=5").json()
    assert len(body["employees"]) == 5
    assert body["count"] == len(client.get("/api/employees?limit=100").json()["employees"]) > 5
    assert client.get("/api/employees?search=sharma").json()["count"] == 1


def test_pagination_pages_do_not_overlap(client):
    first = client.get("/api/employees?limit=5&offset=0").json()
    second = client.get("/api/employees?limit=5&offset=5").json()
    assert len(first["employees"]) == len(second["employees"]) == 5
    assert not {e["id"] for e in first["employees"]} & {e["id"] for e in second["employees"]}


def test_search_below_minimum_length(client):
    for q in ["a", " a "]:
        res = client.get("/api/employees", params={"search": q})
        assert res.status_code == 400
        assert "at least 2 characters" in res.json()["detail"]
    assert client.get("/api/employees?search=hr").status_code == 200


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


def test_database_failure_returns_503(client, monkeypatch):
    from sqlalchemy.exc import OperationalError

    from app.repositories.employee_repository import EmployeeRepository

    def boom(*args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    monkeypatch.setattr(EmployeeRepository, "search", boom)
    res = client.get("/api/employees")
    assert res.status_code == 503
    assert "unavailable" in res.json()["detail"]
