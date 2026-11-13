from sqlalchemy import Column, Date, Integer, String

from app.core.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)        # indexed: searched
    email = Column(String(150), nullable=False, unique=True)
    department = Column(String(100), nullable=False, index=True)  # indexed: searched
    designation = Column(String(100), nullable=False)
    date_of_joining = Column(Date, nullable=False)

    # *_ci collation makes LIKE case-insensitive without LOWER(), so the indexes still work.
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
