from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.employee import Employee

class EmployeeRepository:
    """
    Data Access Layer (Repository) for Employee entities.
    Encapsulates all database query logic, indexing optimizations, and pagination.
    """

    def __init__(self, db: Session):
        self.db = db

    def search(self, query: str, limit: int = 50, offset: int = 0) -> List[Employee]:
        """
        Search employees matching name OR department using case-insensitive LIKE pattern.
        Utilizes DB indexes on `name` and `department`.
        Limits columns and limits rows fetched to prevent unnecessary data transfer.
        """
        search_pattern = f"%{query}%"
        return (
            self.db.query(Employee)
            .filter(
                or_(
                    Employee.name.ilike(search_pattern),
                    Employee.department.ilike(search_pattern),
                )
            )
            .order_by(Employee.name.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count_search(self, query: str) -> int:
        """
        Efficiently counts total matching employees for pagination metadata.
        Uses SQL COUNT without loading full model objects into memory.
        """
        search_pattern = f"%{query}%"
        return (
            self.db.query(func.count(Employee.id))
            .filter(
                or_(
                    Employee.name.ilike(search_pattern),
                    Employee.department.ilike(search_pattern),
                )
            )
            .scalar() or 0
        )

    def get_all(self, limit: int = 50, offset: int = 0) -> List[Employee]:
        """
        Fetches paginated list of all employees.
        """
        return (
            self.db.query(Employee)
            .order_by(Employee.name.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count_all(self) -> int:
        """
        Counts total number of employees in the table.
        """
        return self.db.query(func.count(Employee.id)).scalar() or 0

    def get_by_id(self, employee_id: int) -> Optional[Employee]:
        """
        Fetch a single employee by primary key.
        """
        return self.db.query(Employee).filter(Employee.id == employee_id).first()

    def get_by_email(self, email: str) -> Optional[Employee]:
        """
        Fetch employee by unique email.
        """
        return self.db.query(Employee).filter(Employee.email == email).first()

    def create(self, employee: Employee) -> Employee:
        """
        Persists a new employee to the database.
        Demonstrates extensibility for future write endpoints.
        """
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        return employee
