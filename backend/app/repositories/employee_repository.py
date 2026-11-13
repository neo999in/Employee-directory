from typing import List, Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.employee import Employee

LIKE_ESCAPE_CHAR = "\\"


def _escape_like(value: str) -> str:
    """Escape LIKE wildcards so user input like '50%' or 'a_b' is matched literally."""
    return (
        value.replace(LIKE_ESCAPE_CHAR, LIKE_ESCAPE_CHAR * 2)
        .replace("%", LIKE_ESCAPE_CHAR + "%")
        .replace("_", LIKE_ESCAPE_CHAR + "_")
    )


class EmployeeRepository:
    """
    Data access layer: the only place that builds SQL for employees.
    """

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _search_filter(query: str):
        """
        Prefix match on name OR department: `name LIKE 'rah%'`.

        - A pattern with no leading wildcard is a range scan on the B-tree
          index, so lookups stay O(log n) as the table grows. A leading
          wildcard ('%rah%') would force a full table scan.
        - Plain LIKE (not ILIKE) is used on purpose: ILIKE compiles to
          LOWER(col) LIKE ..., and wrapping the column in a function disables
          the index. Case-insensitivity comes from the column's *_ci collation
          in MySQL (and SQLite's ASCII-case-insensitive LIKE).
        - With OR across two indexed columns MySQL can use an index_merge
          (sort_union) of idx name + idx department.
        """
        pattern = f"{_escape_like(query)}%"
        return or_(
            Employee.name.like(pattern, escape=LIKE_ESCAPE_CHAR),
            Employee.department.like(pattern, escape=LIKE_ESCAPE_CHAR),
        )

    def search(self, query: str, limit: int = 50, offset: int = 0) -> List[Employee]:
        return (
            self.db.query(Employee)
            .filter(self._search_filter(query))
            .order_by(Employee.name.asc(), Employee.id.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count_search(self, query: str) -> int:
        """COUNT in SQL, so no rows are loaded into memory just to count them."""
        return (
            self.db.query(func.count(Employee.id))
            .filter(self._search_filter(query))
            .scalar()
            or 0
        )

    def get_all(self, limit: int = 50, offset: int = 0) -> List[Employee]:
        return (
            self.db.query(Employee)
            .order_by(Employee.name.asc(), Employee.id.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count_all(self) -> int:
        return self.db.query(func.count(Employee.id)).scalar() or 0

    def get_by_id(self, employee_id: int) -> Optional[Employee]:
        return self.db.get(Employee, employee_id)

    def get_by_email(self, email: str) -> Optional[Employee]:
        return self.db.query(Employee).filter(Employee.email == email).first()

    def create(self, employee: Employee) -> Employee:
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        return employee
