from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="John Doe")
    email: EmailStr = Field(..., example="john.doe@company.com")
    role: str = Field(..., min_length=2, max_length=100, example="DevOps Engineer")
    department: str = Field(..., min_length=2, max_length=100, example="DevOps & Cloud")
    salary: float = Field(..., gt=0, example=90000.0)
    status: Optional[str] = Field("Active", example="Active")

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, min_length=2, max_length=100)
    department: Optional[str] = Field(None, min_length=2, max_length=100)
    salary: Optional[float] = Field(None, gt=0)
    status: Optional[str] = None

class EmployeeResponse(EmployeeBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DatabaseStats(BaseModel):
    database: str
    host: str
    port: int
    total_records: int
    status: str
