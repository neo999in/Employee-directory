from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeSearchResponse
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])


def get_employee_service(db: Session = Depends(get_db)) -> EmployeeService:
    return EmployeeService(db)


@router.get("", response_model=EmployeeSearchResponse, summary="Search and list employees")
def search_employees(
    search: Optional[str] = Query(
        default=None,
        max_length=100,
        description="Matches the start of an employee's name or department (case-insensitive)",
    ),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum records to return (1-100)"),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    service: EmployeeService = Depends(get_employee_service),
):
    """
    - Omit `search` to list all employees (paginated).
    - Empty / whitespace-only `search` returns 400.
    """
    return service.search_employees(search_query=search, limit=limit, offset=offset)


@router.get("/{employee_id}", response_model=EmployeeResponse, summary="Get employee by ID")
def get_employee_by_id(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
):
    return service.get_employee_by_id(employee_id)


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new employee",
)
def create_employee(
    data: EmployeeCreate,
    service: EmployeeService = Depends(get_employee_service),
):
    return service.create_employee(data)
