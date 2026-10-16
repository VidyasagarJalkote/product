import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from app.config import settings

# Threaded connection pool
_db_pool = None

def get_pool():
    global _db_pool
    if _db_pool is None:
        _db_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            connect_timeout=5
        )
    return _db_pool

@contextmanager
def get_db():
    """Context manager for obtaining a database connection with dictionary cursor."""
    pool_instance = get_pool()
    conn = pool_instance.getconn()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        pool_instance.putconn(conn)

def init_db():
    """Initialize database tables and initial seed data if not present."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    schema_path = os.path.join(base_dir, "sql", "schema.sql")
    seed_path = os.path.join(base_dir, "sql", "seed.sql")

    with get_db() as cur:
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                cur.execute(f.read())
        
        if os.path.exists(seed_path):
            with open(seed_path, "r", encoding="utf-8") as f:
                cur.execute(f.read())
    print("Database schema and seed verified successfully.")

def close_pool():
    global _db_pool
    if _db_pool:
        _db_pool.closeall()
        _db_pool = None
