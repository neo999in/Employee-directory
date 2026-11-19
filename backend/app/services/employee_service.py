from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import InvalidSearchQueryError
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeSearchResponse


MIN_SEARCH_LENGTH = 2


class EmployeeService:
    """Business logic layer. Knows nothing about HTTP or SQL."""

    def __init__(self, db: Session):
        self.repository = EmployeeRepository(db)

    def search_employees(self, search: Optional[str], limit: int, offset: int) -> EmployeeSearchResponse:
        if search is not None:
            search = search.strip()
            if not search:
                raise InvalidSearchQueryError("Search query cannot be empty.")

            if len(search) < MIN_SEARCH_LENGTH:
                raise InvalidSearchQueryError(f"Search query must be at least {MIN_SEARCH_LENGTH} characters.")

        return EmployeeSearchResponse(
            count=self.repository.count(search),
            employees=self.repository.search(search, limit, offset),
        )
