from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full name of employee")
    email: str = Field(..., min_length=3, max_length=150, description="Corporate email address")
    department: str = Field(..., min_length=1, max_length=100, description="Department name")
    designation: str = Field(..., min_length=1, max_length=100, description="Job title / designation")
    date_of_joining: date = Field(..., description="Date when employee joined")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if not EMAIL_REGEX.match(clean):
            raise ValueError(f"'{v}' is not a valid email address.")
        return clean

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class EmployeeSearchResponse(BaseModel):
    count: int = Field(..., description="Total number of matching employees")
    employees: List[EmployeeResponse] = Field(default_factory=list, description="List of employees")
