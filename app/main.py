import os
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status, Query, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, close_pool
from app.models import EmployeeCreate, EmployeeUpdate, EmployeeResponse, DatabaseStats
import app.crud as crud

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables and seed
    try:
        init_db()
    except Exception as e:
        print(f"Warning: Database initialization encountered an issue: {e}")
    yield
    # Shutdown: Close database pool
    close_pool()

app = FastAPI(
    title="Employee Management CRUD API",
    description="Production-ready CRUD API with PostgreSQL backend and dump/restore capability",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for production and development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base path for static frontend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Mount static folder
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Frontend not found. Please visit /docs for API documentation."}

@app.get("/health", tags=["Monitoring"])
def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}

@app.get("/ready", tags=["Monitoring"])
def readiness_check():
    try:
        stats = crud.get_database_stats()
        return {"status": "ready", "database": stats}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {str(e)}"
        )

@app.get("/api/stats", response_model=DatabaseStats, tags=["System"])
def get_stats():
    try:
        return crud.get_database_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/employees", response_model=List[EmployeeResponse], tags=["Employees"])
def list_employees(
    search: Optional[str] = Query(None, description="Search by name, email, or role"),
    department: Optional[str] = Query(None, description="Filter by department"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status")
):
    try:
        return crud.get_employees(search=search, department=department, status=status_filter)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/employees/{employee_id}", response_model=EmployeeResponse, tags=["Employees"])
def get_employee(employee_id: int):
    employee = crud.get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")
    return employee

@app.post("/api/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED, tags=["Employees"])
def create_new_employee(employee: EmployeeCreate):
    existing = crud.get_employee_by_email(employee.email)
    if existing:
        raise HTTPException(status_code=400, detail=f"Employee with email '{employee.email}' already exists")
    try:
        return crud.create_employee(employee)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create employee: {str(e)}")

@app.put("/api/employees/{employee_id}", response_model=EmployeeResponse, tags=["Employees"])
def update_existing_employee(employee_id: int, employee: EmployeeUpdate):
    existing = crud.get_employee_by_id(employee_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")
    
    if employee.email and employee.email != existing["email"]:
        with_email = crud.get_employee_by_email(employee.email)
        if with_email and with_email["id"] != employee_id:
            raise HTTPException(status_code=400, detail=f"Email '{employee.email}' is already in use by another record")

    try:
        return crud.update_employee(employee_id, employee)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update employee: {str(e)}")

@app.delete("/api/employees/{employee_id}", tags=["Employees"])
def remove_employee(employee_id: int):
    existing = crud.get_employee_by_id(employee_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")
    
    deleted = crud.delete_employee(employee_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete employee")
    return {"message": f"Employee {employee_id} deleted successfully"}

@app.get("/api/backup/download", tags=["Database Backup"])
def download_database_dump():
    """Generates and serves a complete SQL dump of schema and current data."""
    try:
        sql_content = crud.export_sql_dump()
        return Response(
            content=sql_content,
            media_type="application/sql",
            headers={"Content-Disposition": "attachment; filename=devops_db_dump.sql"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dump generation failed: {str(e)}")
