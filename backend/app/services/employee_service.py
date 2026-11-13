from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import InvalidSearchQueryError
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeSearchResponse


class EmployeeService:
    """Business logic layer. Knows nothing about HTTP or SQL."""

    def __init__(self, db: Session):
        self.repository = EmployeeRepository(db)

    def search_employees(self, search: Optional[str], limit: int, offset: int) -> EmployeeSearchResponse:
        if search is not None:
            search = search.strip()
            if not search:
                raise InvalidSearchQueryError("Search query cannot be empty.")

        return EmployeeSearchResponse(
            count=self.repository.count(search),
            employees=self.repository.search(search, limit, offset),
        )
