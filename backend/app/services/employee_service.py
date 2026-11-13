from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.employee_repository import EmployeeRepository
from app.models.employee import Employee
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeSearchResponse,
)

class EmployeeService:
    """
    Business Logic Layer for Employee operations.
    Keeps business logic decoupled from HTTP routing and raw database queries.
    """

    def __init__(self, db: Session):
        self.repository = EmployeeRepository(db)

    def search_employees(
        self,
        search_query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> EmployeeSearchResponse:
        """
        Processes employee search requests.
        Handles query trimming and delegation to the repository.
        """
        clean_query = search_query.strip() if search_query else None

        # Check for empty string after strip (e.g. whitespace only)
        if search_query is not None and not clean_query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty or only whitespace."
            )

        if clean_query:
            employees = self.repository.search(clean_query, limit=limit, offset=offset)
            total_count = self.repository.count_search(clean_query)
        else:
            employees = self.repository.get_all(limit=limit, offset=offset)
            total_count = self.repository.count_all()

        return EmployeeSearchResponse(
            count=total_count,
            employees=[EmployeeResponse.model_validate(emp) for emp in employees]
        )

    def get_employee_by_id(self, employee_id: int) -> EmployeeResponse:
        """
        Retrieves an employee by ID or raises 404.
        """
        employee = self.repository.get_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID {employee_id} not found."
            )
        return EmployeeResponse.model_validate(employee)

    def create_employee(self, data: EmployeeCreate) -> EmployeeResponse:
        """
        Creates a new employee, enforcing business rules like unique email.
        """
        existing = self.repository.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee with email '{data.email}' already exists."
            )

        new_employee = Employee(
            name=data.name.strip(),
            email=data.email.strip().lower(),
            department=data.department.strip(),
            designation=data.designation.strip(),
            date_of_joining=data.date_of_joining
        )
        created = self.repository.create(new_employee)
        return EmployeeResponse.model_validate(created)
