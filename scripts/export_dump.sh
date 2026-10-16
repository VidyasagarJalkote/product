#!/usr/bin/env bash
# Shell script to export PostgreSQL database dump on Linux / EC2 / macOS
# Usage: ./scripts/export_dump.sh

set -e

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-devops_db}"
DB_USER="${DB_USER:-postgres}"
OUTPUT_FILE="${1:-devops_db_dump.sql}"

echo "=========================================="
echo "  Exporting PostgreSQL Database (pg_dump) "
echo "=========================================="
echo "Host     : $DB_HOST:$DB_PORT"
echo "Database : $DB_NAME"
echo "User     : $DB_USER"
echo "Output   : $OUTPUT_FILE"

# Export schema and data with DROP IF EXISTS clauses
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" --clean --if-exists -F p -f "$OUTPUT_FILE"

echo ""
echo "[SUCCESS] Dump created at $OUTPUT_FILE ($(du -h "$OUTPUT_FILE" | cut -f1))"
