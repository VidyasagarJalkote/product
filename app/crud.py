from typing import List, Optional, Dict, Any
from app.database import get_db
from app.models import EmployeeCreate, EmployeeUpdate
from app.config import settings

def get_employees(
    search: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    query = "SELECT id, name, email, role, department, salary, status, created_at FROM employees WHERE 1=1"
    params = []

    if search:
        query += " AND (name ILIKE %s OR email ILIKE %s OR role ILIKE %s)"
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern])

    if department:
        query += " AND department = %s"
        params.append(department)

    if status:
        query += " AND status = %s"
        params.append(status)

    query += " ORDER BY id ASC"

    with get_db() as cur:
        cur.execute(query, tuple(params))
        return cur.fetchall()

def get_employee_by_id(employee_id: int) -> Optional[Dict[str, Any]]:
    query = "SELECT id, name, email, role, department, salary, status, created_at FROM employees WHERE id = %s"
    with get_db() as cur:
        cur.execute(query, (employee_id,))
        return cur.fetchone()

def get_employee_by_email(email: str) -> Optional[Dict[str, Any]]:
    query = "SELECT id, name, email, role, department, salary, status, created_at FROM employees WHERE email = %s"
    with get_db() as cur:
        cur.execute(query, (email,))
        return cur.fetchone()

def create_employee(data: EmployeeCreate) -> Dict[str, Any]:
    query = """
        INSERT INTO employees (name, email, role, department, salary, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, name, email, role, department, salary, status, created_at
    """
    with get_db() as cur:
        cur.execute(query, (data.name, data.email, data.role, data.department, data.salary, data.status))
        return cur.fetchone()

def update_employee(employee_id: int, data: EmployeeUpdate) -> Optional[Dict[str, Any]]:
    fields = []
    values = []

    if data.name is not None:
        fields.append("name = %s")
        values.append(data.name)
    if data.email is not None:
        fields.append("email = %s")
        values.append(data.email)
    if data.role is not None:
        fields.append("role = %s")
        values.append(data.role)
    if data.department is not None:
        fields.append("department = %s")
        values.append(data.department)
    if data.salary is not None:
        fields.append("salary = %s")
        values.append(data.salary)
    if data.status is not None:
        fields.append("status = %s")
        values.append(data.status)

    if not fields:
        return get_employee_by_id(employee_id)

    values.append(employee_id)
    query = f"UPDATE employees SET {', '.join(fields)} WHERE id = %s RETURNING id, name, email, role, department, salary, status, created_at"

    with get_db() as cur:
        cur.execute(query, tuple(values))
        return cur.fetchone()

def delete_employee(employee_id: int) -> bool:
    query = "DELETE FROM employees WHERE id = %s RETURNING id"
    with get_db() as cur:
        cur.execute(query, (employee_id,))
        deleted = cur.fetchone()
        return deleted is not None

def get_database_stats() -> Dict[str, Any]:
    with get_db() as cur:
        cur.execute("SELECT count(*) as total FROM employees")
        result = cur.fetchone()
        total = result["total"] if result else 0
        return {
            "database": settings.DB_NAME,
            "host": settings.DB_HOST,
            "port": settings.DB_PORT,
            "total_records": total,
            "status": "Healthy & Connected"
        }

def export_sql_dump() -> str:
    """Generate a valid SQL dump containing DDL and current DML records."""
    lines = [
        "-- -------------------------------------------------------------",
        "-- PostgreSQL Database Dump (DevOps Practice Project)",
        f"-- Database: {settings.DB_NAME}",
        "-- Export Method: Full Schema + Data Dump",
        "-- -------------------------------------------------------------",
        "",
        "CREATE TABLE IF NOT EXISTS employees (",
        "    id SERIAL PRIMARY KEY,",
        "    name VARCHAR(100) NOT NULL,",
        "    email VARCHAR(150) UNIQUE NOT NULL,",
        "    role VARCHAR(100) NOT NULL,",
        "    department VARCHAR(100) NOT NULL,",
        "    salary NUMERIC(10, 2) NOT NULL CHECK (salary > 0),",
        "    status VARCHAR(50) DEFAULT 'Active',",
        "    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
        ");",
        "",
        "CREATE INDEX IF NOT EXISTS idx_employees_department ON employees (department);",
        "CREATE INDEX IF NOT EXISTS idx_employees_status ON employees (status);",
        ""
    ]

    records = get_employees()
    if records:
        lines.append("-- Dump Data:")
        for r in records:
            # Escape single quotes
            name = r["name"].replace("'", "''")
            email = r["email"].replace("'", "''")
            role = r["role"].replace("'", "''")
            dept = r["department"].replace("'", "''")
            salary = r["salary"]
            status = r["status"].replace("'", "''")
            lines.append(
                f"INSERT INTO employees (id, name, email, role, department, salary, status) "
                f"VALUES ({r['id']}, '{name}', '{email}', '{role}', '{dept}', {salary}, '{status}') "
                f"ON CONFLICT (id) DO UPDATE SET "
                f"name = EXCLUDED.name, email = EXCLUDED.email, role = EXCLUDED.role, "
                f"department = EXCLUDED.department, salary = EXCLUDED.salary, status = EXCLUDED.status;"
            )
        # Advance sequence to prevent primary key collision
        lines.append("")
        lines.append("SELECT setval(pg_get_serial_sequence('employees', 'id'), COALESCE(MAX(id), 1)) FROM employees;")
    
    return "\n".join(lines)
