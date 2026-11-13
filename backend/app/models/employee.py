from sqlalchemy import Column, Integer, String, Date, Index
from app.core.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(150), nullable=False, unique=True, index=True)
    department = Column(String(100), nullable=False, index=True)
    designation = Column(String(100), nullable=False)
    date_of_joining = Column(Date, nullable=False)

    # Composite index for search by both department and name if needed
    __table_args__ = (
        Index("idx_department_name", "department", "name"),
    )

    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.name}', department='{self.department}')>"
