from typing import List, Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.employee import Employee


class EmployeeRepository:
    """Database layer: the ONLY place that talks to the employees table."""

    def __init__(self, db: Session):
        self.db = db

    def _filter(self, query, search: Optional[str]):
        if not search:
            return query
        # Escape LIKE wildcards so "%" or "_" typed by the user are matched literally.
        safe = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        # Prefix match ("rah%"): no leading wildcard, so MySQL can use the
        # indexes on name / department instead of scanning the whole table.
        pattern = f"{safe}%"
        return query.filter(
            or_(
                Employee.name.like(pattern, escape="\\"),
                Employee.department.like(pattern, escape="\\"),
            )
        )

    def search(self, search: Optional[str], limit: int, offset: int) -> List[Employee]:
        query = self._filter(self.db.query(Employee), search)
        return query.order_by(Employee.name, Employee.id).offset(offset).limit(limit).all()

    def count(self, search: Optional[str]) -> int:
        return self._filter(self.db.query(func.count(Employee.id)), search).scalar()
