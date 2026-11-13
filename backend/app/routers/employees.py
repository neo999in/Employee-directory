from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.employee import EmployeeSearchResponse
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("", response_model=EmployeeSearchResponse)
def search_employees(
    search: Optional[str] = Query(None, max_length=100, description="Start of a name or department"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    # The route only reads the request and delegates; no business or DB logic here.
    return EmployeeService(db).search_employees(search, limit, offset)
