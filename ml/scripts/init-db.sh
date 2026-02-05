#!/bin/bash
set -e

BACKUP_FILE="/docker-entrypoint-initdb.d/backup/market_schema.backup"

if [ -f "$BACKUP_FILE" ]; then
    echo "Restoring database from backup using pg_restore..."

    # Use pg_restore for custom format backups
    pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-privileges -v "$BACKUP_FILE" 2>&1 || {
        echo "Warning: pg_restore completed with some warnings (this is often normal)"
    }

    echo "Database restore completed!"
else
    echo "No backup file found at $BACKUP_FILE, starting with empty database."
fi
