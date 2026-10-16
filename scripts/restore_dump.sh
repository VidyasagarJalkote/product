#!/usr/bin/env bash
# Shell script to restore PostgreSQL database dump on Linux / EC2 / macOS
# Usage: ./scripts/restore_dump.sh [path/to/dump.sql]

set -e

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-devops_db}"
DB_USER="${DB_USER:-postgres}"
DUMP_FILE="${1:-devops_db_dump.sql}"

echo "=========================================="
echo "  Restoring PostgreSQL Database (psql)    "
echo "=========================================="
echo "Host     : $DB_HOST:$DB_PORT"
echo "Database : $DB_NAME"
echo "User     : $DB_USER"
echo "Dump File: $DUMP_FILE"

if [ ! -f "$DUMP_FILE" ]; then
    echo "[ERROR] Dump file $DUMP_FILE not found!"
    exit 1
fi

# Ensure database exists
echo "[*] Ensuring database '$DB_NAME' exists..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;"

# Restore dump
echo "[*] Restoring schema and records..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$DUMP_FILE"

echo ""
echo "[SUCCESS] Database restored successfully into '$DB_NAME'!"
