from datetime import date
from typing import List

from pydantic import BaseModel, ConfigDict


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    department: str
    designation: str
    date_of_joining: date


class EmployeeSearchResponse(BaseModel):
    count: int  # total number of matches
    employees: List[EmployeeResponse]
