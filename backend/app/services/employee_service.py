from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import (
    DuplicateEmployeeError,
    EmployeeNotFoundError,
    InvalidSearchQueryError,
)
from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeSearchResponse,
)


class EmployeeService:
    """
    Business logic layer. Knows nothing about HTTP: it raises domain exceptions
    (app.core.exceptions) which are mapped to status codes centrally.
    """

    def __init__(self, db: Session):
        self.repository = EmployeeRepository(db)

    def search_employees(
        self,
        search_query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> EmployeeSearchResponse:
        if search_query is None:
            employees = self.repository.get_all(limit=limit, offset=offset)
            total_count = self.repository.count_all()
        else:
            clean_query = search_query.strip()
            if not clean_query:
                raise InvalidSearchQueryError("Search query cannot be empty or only whitespace.")
            employees = self.repository.search(clean_query, limit=limit, offset=offset)
            total_count = self.repository.count_search(clean_query)

        return EmployeeSearchResponse(
            count=total_count,
            employees=[EmployeeResponse.model_validate(emp) for emp in employees],
        )

    def get_employee_by_id(self, employee_id: int) -> EmployeeResponse:
        employee = self.repository.get_by_id(employee_id)
        if not employee:
            raise EmployeeNotFoundError(f"Employee with ID {employee_id} not found.")
        return EmployeeResponse.model_validate(employee)

    def create_employee(self, data: EmployeeCreate) -> EmployeeResponse:
        if self.repository.get_by_email(data.email):
            raise DuplicateEmployeeError(f"Employee with email '{data.email}' already exists.")

        new_employee = Employee(
            name=data.name.strip(),
            email=data.email.strip().lower(),
            department=data.department.strip(),
            designation=data.designation.strip(),
            date_of_joining=data.date_of_joining,
        )
        return EmployeeResponse.model_validate(self.repository.create(new_employee))
