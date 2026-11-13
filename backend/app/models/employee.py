from sqlalchemy import Column, Date, Integer, String

from app.core.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)          # idx for prefix search + ORDER BY name
    email = Column(String(150), nullable=False, unique=True)       # unique constraint is itself an index
    department = Column(String(100), nullable=False, index=True)    # idx for prefix search
    designation = Column(String(100), nullable=False)
    date_of_joining = Column(Date, nullable=False)

    # MySQL: utf8mb4 + case-insensitive collation so plain LIKE is
    # case-insensitive and can still use the indexes (see EmployeeRepository).
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.name}', department='{self.department}')>"
