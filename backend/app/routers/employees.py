from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.core.database import get_db
from app.services.employee_service import EmployeeService
from app.schemas.employee import EmployeeResponse, EmployeeSearchResponse, EmployeeCreate

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("", response_model=EmployeeSearchResponse, summary="Search and list employees")
def search_employees(
    search: Optional[str] = Query(
        default=None,
        max_length=100,
        description="Search term matching employee name or department"
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of employee records to return (1-100)"
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip for pagination"
    ),
    db: Session = Depends(get_db)
):
    """
    Search employees by name or department.
    - If `search` parameter is omitted or empty, returns paginated list of all employees.
    - If `search` is provided, performs case-insensitive indexed search.
    - Returns structured pagination metadata (`count`) and employee list.
    """
    try:
        service = EmployeeService(db)
        return service.search_employees(search_query=search, limit=limit, offset=offset)
    except HTTPException:
        # Re-raise explicit HTTP exceptions (e.g. 400 validation error)
        raise
    except OperationalError as oe:
        # Graceful handling for database connection / query failure
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is currently unavailable. Please verify connection."
        )
    except SQLAlchemyError as se:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred while processing the request."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/{employee_id}", response_model=EmployeeResponse, summary="Get employee by ID")
def get_employee_by_id(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Fetch a single employee by their unique ID.
    """
    try:
        service = EmployeeService(db)
        return service.get_employee_by_id(employee_id)
    except HTTPException:
        raise
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving employee."
        )

@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED, summary="Create new employee")
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new employee record.
    Demonstrates clean architecture extensibility (Backend Task 4).
    """
    try:
        service = EmployeeService(db)
        return service.create_employee(data)
    except HTTPException:
        raise
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while saving employee."
        )
